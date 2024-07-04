import numpy as np
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from .models import Result
from ..db.dependencies import get_session
from ..recordings.models import Recording
from ..recordings.router import ClientS3
from ..users.auth import get_user_id, oauth2_scheme
from .relschemas import ResultRel

import wave
from scipy.signal import medfilt

router = APIRouter(prefix='/result', tags=['result'])


def average(data, kernel_size):
    cumsum = np.cumsum(np.insert(data, 0, 0))
    return (cumsum[kernel_size:] - cumsum[:-kernel_size]) / kernel_size


async def sound_filtration(file_url: str) -> bytes:
    sound_data = await ClientS3.get_file(file_url)

    with wave.open(sound_data) as sound:
        params = sound.get_params()
        data = np.frombuffer(sound.get_frames(params.nframes), dtype=np.int16)

    result = average(medfilt(data, 3), 3)
    result = np.pad(result, (0, len(data) - len(result)))
    result = result.astype(np.int16)

    return bytes(result)


@router.get('/{result_id}')
async def get_result(result_id: int, token: str = Depends(oauth2_scheme),
                     session: AsyncSession = Depends(get_session)) -> ResultRel:

    user_id = get_user_id(token)

    query = Result.get_by_id(result_id)
    result = await session.scalar(query)

    if not result:
        raise HTTPException(404)

    if result.creator.id != user_id:
        raise HTTPException(401)

    return ResultRel.model_validate(result, from_attributes=True)


async def get_result_data(result_url: str):
    return await ClientS3.get_file(result_url)


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
    # WORKING WITH SOUND

    # WORKING WITH SOUND
    url = await ClientS3.push_file(bytes, user_id)

    result = Result( source_id=recording.id, url=url)

    session.add(result)

    await session.commit()

    return {'result_id': result.id}
