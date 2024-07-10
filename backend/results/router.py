import io
import wave

import numpy as np
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from .models import Result
from ..db.dependencies import get_session
from ..recordings.models import Recording
from ..recordings.router import ClientS3
from ..users.auth import get_current_user
from .relschemas import ResultRel
from .schemas import ResultRead
from ..tags.models import Tag
from ..users.models import User

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


async def get_road(result_data: bytes):

    wav_file = wave.open(io.BytesIO(result_data), 'rb')

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
    Js['data'] = average(deinterleaved[0], Js['samples_per_pixel']).tolist()[::Js['samples_per_pixel'] // 2]

    wav_file.close()

    return Js


@router.delete('/{result_id}')
async def delete_result(result_id: int, user: User = Depends(get_current_user),
                        session: AsyncSession = Depends(get_session)):
    result = await session.scalar(Result.get_by_id(result_id))

    if not result:
        raise HTTPException(404)

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


@router.get('/download/{result_id}')
async def get_result_data(result_id: int, user: User = Depends(get_current_user),
                          session: AsyncSession = Depends(get_session)):
    result = await session.scalar(Result.get_by_id(result_id))

    if not result:
        raise HTTPException(404)

    return {'result': str(await ClientS3.get_file(result.url))}


@router.post('/{recording_id}')
async def create_result(recording_id: int, user: User = Depends(get_current_user),
                        session: AsyncSession = Depends(get_session)):
    recording = await session.scalar(Recording.get_by_id(recording_id))

    if recording is None:
        raise HTTPException(404)

    if recording.creator_id != user.id:
        raise HTTPException(401)

    byte = await cut_file(await ClientS3.get_file(recording.url), recording.tags)

    with wave.open(io.BytesIO(byte), 'rb') as dur:
        duration = int(dur.getnframes() / float(dur.getframerate()))

    url = await ClientS3.push_file(byte, user.id)

    soundwave = str(await get_road(byte))

    result = Result(source_id=recording.id, url=url, duration=duration, soundwave=soundwave)

    session.add(result)

    await session.commit()

    return ResultRead.model_validate(result, from_attributes=True)