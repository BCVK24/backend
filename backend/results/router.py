import io

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

import wave

router = APIRouter(prefix='/result', tags=['result'])


def average(data, kernel_size):
    cumsum = np.cumsum(np.insert(data, 0, 0))
    return (cumsum[kernel_size:] - cumsum[:-kernel_size]) / kernel_size


def medfilt(data, kernel_size):
    result = np.zeros(len(data))
    for i in range(len(data)):
        result[i] = np.median(data[max(i - kernel_size, 0): min(i + kernel_size, len(data))])
    return result


async def sound_filtration(file_url: str) -> bytes:
    sound_data = await ClientS3.get_file(file_url)

    with wave.open(io.BytesIO(sound_data)) as sound:
        params = sound.getparams()
        data = np.frombuffer(sound.readframes(params.nframes), dtype=np.int16)

    result = average(medfilt(data, 3), 3)
    result = np.pad(result, (0, len(data) - len(result)))
    result = result.astype(np.int16)

    return bytes(result)


@router.delete('/{result_id}')
async def delete_result(resul_id: int, token: str = Depends(oauth2_scheme),
                        session: AsyncSession = Depends(get_session)):

    user_id = await get_user_id(token)

    result = await session.scalar(Result.get_by_id(resul_id))

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

    byte = await sound_filtration(recording.url)

    url = await ClientS3.push_file(byte, user_id)

    result = Result(source_id=recording.id, url=url)

    session.add(result)

    await session.commit()

    return ResultRead.model_validate(result, from_attributes=True)