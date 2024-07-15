import wave

from fastapi import APIRouter, UploadFile, File, Depends, HTTPException, Form, Header

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError

from ..db.dependencies import get_session
from ..users.auth import get_current_user
from .models import Recording
from .relschemas import RecordingRel
from .S3Model import S3Client
from .schemas import RecordingRead, RecordingUpdate
from ..users.models import User

import io
import numpy as np


router = APIRouter(prefix='/recording', tags=['recording'])
ClientS3 = S3Client("...", "...", "...", "...")


def average(data, kernel_size):
    cumsum = np.cumsum(np.insert(data, 0, 0))
    return (cumsum[kernel_size:] - cumsum[:-kernel_size]) / kernel_size


def medfilt(data, kernel_size):
    result = np.zeros(len(data))
    for i in range(len(data)):
        result[i] = np.median(data[max(i - kernel_size, 0): min(i + kernel_size, len(data))])
    return result


async def sound_filtration(sound_data: bytes) -> bytes:
    with wave.open(io.BytesIO(sound_data)) as sound:
        params = sound.getparams()
        data = np.frombuffer(sound.readframes(params.nframes), dtype=np.int16)

        result = medfilt(data, 3)
        result = np.pad(result, (0, len(data) - len(result)))
        result = result.astype(np.int16)

    ret = io.BytesIO()

    with wave.open(ret, 'wb') as rt:
        rt.setparams(params)
        rt.writeframes(result.tobytes())

    ret.seek(0)

    return ret.read()


async def get_road(recording_data: bytes):

    wav_file = wave.open(io.BytesIO(recording_data), 'rb')

    signal = wav_file.readframes(-1)
    if wav_file.getsampwidth() == 1:
        signal = np.array(np.frombuffer(signal, dtype='UInt8') - 128, dtype=np.int8)
    elif wav_file.getsampwidth() == 2:
        signal = np.frombuffer(signal, dtype=np.int16)

    deinterleaved = [signal[idx::wav_file.getnchannels()] for idx in range(wav_file.getnchannels())]

    wav_file.close()

    return average(deinterleaved[0], 128).tolist()[::64]


@router.delete('/{recording_id}')
async def delete_recording(recording_id: int, user: User = Depends(get_current_user),
                           session: AsyncSession = Depends(get_session)) -> RecordingRead:
    get_rec = await session.scalar(Recording.get_by_id(recording_id))

    if not get_rec:
        raise HTTPException(404)

    if get_rec.creator_id != user.id:
        raise HTTPException(401)

    await ClientS3.delete_file(get_rec.url)

    record_return = RecordingRead.model_validate(get_rec, from_attributes=True)

    await session.delete(get_rec)
    await session.commit()

    return record_return


@router.put('/')
async def put_recording_name(recording: RecordingUpdate, user: User = Depends(get_current_user),
                             session: AsyncSession = Depends(get_session)) -> RecordingRead:
    recording_db = await session.scalar(Recording.get_by_id(recording.id))

    if not recording_db:
        raise HTTPException(404)

    if recording_db.creator_id != user.id:
        raise HTTPException(401)

    recording_db.title = recording.title

    await session.commit()

    return RecordingRead.model_validate(recording_db, from_attributes=True)


@router.get('/{recording_id}')
async def get_recording(recording_id: int, user: User = Depends(get_current_user),
                        session: AsyncSession = Depends(get_session)) -> RecordingRel:
    recording = await session.scalar(Recording.get_by_id(recording_id))

    if not recording:
        raise HTTPException(404)

    if recording.creator_id != user.id:
        raise HTTPException(401)

    return RecordingRel.model_validate(recording, from_attributes=True)


@router.post('/')
async def upload_recording(user: User = Depends(get_current_user), recording: str = Form(),
                           recording_file: UploadFile = File(), session: AsyncSession = Depends(get_session)):

    byte = await sound_filtration(await recording_file.read())

    with wave.open(io.BytesIO(byte), 'rb') as dur:
        duration = int(dur.getnframes() / float(dur.getframerate()))

    url = await ClientS3.push_file(byte, user.id)

    soundwave = str(await get_road(byte))

    recording_db = Recording(url=url, creator_id=user.id, title=recording, duration=duration, soundwave=soundwave,
                             processing=True)

    session.add(recording_db)

    try:
        await session.commit()
    except IntegrityError as err:
        raise HTTPException(401)

    return RecordingRead.model_validate(recording_db, from_attributes=True)
