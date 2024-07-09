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

from ..recordings.router import average


router = APIRouter(prefix='/result', tags=['result'])


async def cut_file(recording_bytes: bytes, tags: list[Tag]) -> bytes:
    with wave.open(io.BytesIO(recording_bytes)) as sound:
        params = sound.getparams()
        audio = np.frombuffer(sound.readframes(params.nframes), dtype=np.int16)

    for tag in tags:
        np.delete(audio, np.r_[slice(int(tag.start * (params.framerate // 1000)), int(tag.end * (params.framerate // 1000)))])

    ret = io.BytesIO()

    with wave.open(ret, 'wb') as rt:
        rt.setparams(params)
        rt.writeframes(audio.tobytes())

    ret.seek(0)

    return ret.read()


@router.get('/GetRoad/{result_id}')
async def get_road(result_id: int, token: str = Depends(oauth2_scheme),
                   session: AsyncSession = Depends(get_session)):
    user_id = await get_user_id(token)

    result = await session.scalar(Result.get_by_id(result_id))

    wav_file = wave.open(io.BytesIO(await ClientS3.get_file(result.url)), 'rb')

    Js = {
        'version': 2,
        'channels': wav_file.getnchannels(),
        'sample_rate': wav_file.getframerate(),
        'samples_per_pixel': 128,
    }

    signal = wav_file.readframes(-1)
    if wav_file.getsampwidth() == 1:
        signal = np.array(np.frombuffer(signal, dtype='UInt8') - 128, dtype=np.int8)
        Js['bits'] = 8
        Js['length'] = 1
    elif wav_file.getsampwidth() == 2:
        signal = np.frombuffer(signal, dtype=np.int16)
        Js['bits'] = 16
        Js['length'] = 2

    deinterleaved = [signal[idx::wav_file.getnchannels()] for idx in range(wav_file.getnchannels())]

    Js['length'] = int(len(deinterleaved[0]) / Js['length'] / (Js['samples_per_pixel'] // 2))
    Js['data'] = list(average(deinterleaved[0], Js['samples_per_pixel']))[::Js['samples_per_pixel'] // 2]

    return Js


@router.delete('/{result_id}')
async def delete_result(result_id: int, token: str = Depends(oauth2_scheme),
                        session: AsyncSession = Depends(get_session)):

    user_id = await get_user_id(token)

    result = await session.scalar(Result.get_by_id(result_id))
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

    with wave.open(io.BytesIO(byte), 'rb') as dur:
        duration = int(dur.getnframes() / float(dur.getframerate()))

    url = await ClientS3.push_file(byte, user_id)

    result = Result(source_id=recording.id, url=url, duration=duration)

    session.add(result)

    await session.commit()

    return ResultRead.model_validate(result, from_attributes=True)