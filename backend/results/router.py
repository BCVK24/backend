import io
import wave

import numpy as np
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from .models import Result
from ..db.dependencies import get_session
from ..recordings.models import Recording
from ..recordings.router import ClientS3
from ..users.auth import get_user_id, oauth2_scheme
from .relschemas import ResultRel
from .schemas import ResultRead
from ..tags.models import Tag


router = APIRouter(prefix='/result', tags=['result'])


async def cut_file(recording_bytes: bytes, tags: list[Tag]) -> bytes:
    with wave.open(io.BytesIO(recording_bytes)) as sound:
        params = sound.getparams()
        audio = np.frombuffer(sound.readframes(params.nframes), dtype=np.int16)

    for tag in tags:
        np.delete(audio, np.r_[slice(int(tag.start * params.framerate), int(tag.end * params.framerate))])

    ret = io.BytesIO()

    with wave.open(ret, 'wb') as rt:
        rt.setparams(params)
        rt.writeframes(audio.tobytes())

    return ret.read()


@router.delete('/{result_id}')
async def delete_result(resul_id: int, token: str = Depends(oauth2_scheme),
                        session: AsyncSession = Depends(get_session)):

    user_id = await get_user_id(token)

    result = await session.scalar(Result.get_by_id(resul_id))
    await ClientS3.delete_file(result.url)

    rec_result = ResultRel.model_validate(result, from_attributes=True)

    if not result:
        raise HTTPException(404)

    await session.delete(result)

    await session.commit()

    return rec_result


@router.get('/{result_id}')
async def get_result(result_id: int, token: str = Depends(oauth2_scheme),
                     session: AsyncSession = Depends(get_session)) -> ResultRel:

    user_id = await get_user_id(token)

    query = Result.get_by_id(result_id)
    result = await session.scalar(query)

    if not result:
        raise HTTPException(404)

    return ResultRel.model_validate(result, from_attributes=True)


@router.get('/download/{result_id}')
async def get_result_data(result_id: int, token: str = Depends(oauth2_scheme),
                          session: AsyncSession = Depends(get_session)):
    user_id = await get_user_id(token)

    result = await session.scalar(Result.get_by_id(result_id))

    if not result:
        raise HTTPException(404)

    return {'result': str(await ClientS3.get_file(result.url))}


@router.post('/{recording_id}')
async def create_result(recording_id: int, token: str = Depends(oauth2_scheme),
                        session: AsyncSession = Depends(get_session)):
    user_id = await get_user_id(token)

    recording = await session.scalar(Recording.get_by_id(recording_id))

    if recording is None:
        raise HTTPException(404)

    if recording.creator_id != user_id:
        raise HTTPException(401)

    byte = await ClientS3.get_file(recording.url)

    byte = await cut_file(byte, recording.tags)

    url = await ClientS3.push_file(byte, user_id)

    result = Result(source_id=recording.id, url=url)

    session.add(result)

    await session.commit()

    return ResultRead.model_validate(result, from_attributes=True)