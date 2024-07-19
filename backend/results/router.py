
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from .models import Result
from ..db.dependencies import get_session
from ..recordings.models import Recording
from ..recordings.router import ClientS3
from ..users.auth import get_current_user
from .relschemas import ResultRel
from .schemas import ResultRead
from ..users.models import User

from faststream.redis import RedisBroker


router = APIRouter(prefix='/result', tags=['result'])


@router.delete('/{result_id}')
async def delete_result(result_id: int, user: User = Depends(get_current_user),
                        session: AsyncSession = Depends(get_session)) -> ResultRel:
    result = await session.scalar(Result.get_by_id(result_id))

    if not result:
        raise HTTPException(404)

    if result.processing:
        raise HTTPException(425)

    await ClientS3.delete_file(result.url)

    rec_result = ResultRel.model_validate(result, from_attributes=True)

    await session.delete(result)

    await session.commit()

    return rec_result


@router.get('/{result_id}')
async def get_result(result_id: int, user: User = Depends(get_current_user),
                     session: AsyncSession = Depends(get_session)) -> ResultRel:
    query = Result.get_by_id(result_id)
    result = await session.scalar(query)

    if not result:
        raise HTTPException(404)

    return ResultRel.model_validate(result, from_attributes=True)


@router.post('/{recording_id}')
async def create_result(recording_id: int, user: User = Depends(get_current_user),
                        session: AsyncSession = Depends(get_session)) -> ResultRead:
    recording = await session.scalar(Recording.get_by_id(recording_id))

    if recording is None:
        raise HTTPException(404)

    if recording.creator_id != user.id:
        raise HTTPException(401)

    if recording.processing:
        raise HTTPException(425)

    result = Result(source_id=recording.id, url=recording.url, duration=recording.duration, processing=True)

    session.add(result)

    await session.commit()

    async with RedisBroker("redis://redis:6379/0") as reddis:
        await reddis.publish(result.id, "cut_result")

    return ResultRead.model_validate(result, from_attributes=True)