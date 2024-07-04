from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from .models import Result
from ..db.dependencies import get_session
from ..recordings.models import Recording
from ..recordings.router import sound_filtration, ClientS3
from ..users.auth import get_user_id, oauth2_scheme

router = APIRouter(prefix='/result', tags=['result'])


@router.get('/{file_id}')
async def get_file(file_id: int, token: str = Depends(oauth2_scheme)) -> str:
    return "..."


@router.post('/{recording_id}')
async def create_result(recording_id: int, token: str = Depends(oauth2_scheme),
                        session: AsyncSession = Depends(get_session)):
    user_id = await get_user_id(token)

    query = Recording.get_by_id(recording_id)
    recording = await session.scalar(query)

    if recording is None:
        raise HTTPException(404)

    if recording.creator_id != user_id:
        raise HTTPException(401)

    bytes = await sound_filtration(recording.url)
    url = await ClientS3.push_file(bytes, user_id)

    result = Result(
        source_id=recording.id,
        url=url
    )

    session.add(result)

    await session.commit()

    return {'result_id': result.id}
