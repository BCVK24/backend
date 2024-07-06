import wave

from fastapi import APIRouter, UploadFile, File, Depends, HTTPException, Form

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError

from ..db.dependencies import get_session
from ..users.auth import get_user_id, oauth2_scheme
from ..users.models import User
from .models import Recording
from .relschemas import RecordingRel
from .S3Model import S3Client
from .schemas import RecordingRead, RecordingCreate

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

    result = average(medfilt(data, 3), 3)
    result = np.pad(result, (0, len(data) - len(result)))
    result = result.astype(np.int16)

    return bytes(result)


@router.delete('/{recording_id}')
async def delete_recording(recording_id: int, token: str = Depends(oauth2_scheme),
                           session: AsyncSession = Depends(get_session)) -> RecordingRead:
    user_id = await get_user_id(token)

    get_rec = await session.scalar(Recording.get_by_id(recording_id))

    if not get_rec:
        raise HTTPException(404)

    await ClientS3.delete_file(get_rec.url)

    record_return = RecordingRead.model_validate(get_rec, from_attributes=True)

    await session.delete(get_rec)
    await session.commit()

    return record_return


@router.put('/')
async def put_recording_name(recording_title: str, recording_id: int, token: str = Depends(oauth2_scheme),
                        session: AsyncSession = Depends(get_session)) -> RecordingRead:
    user_id = get_user_id(token)

    recording = await session.scalar(Recording.get_by_id(recording_id))

    if not recording:
        raise HTTPException(404)

    recording.title = recording_title

    await session.commit()

    return RecordingRead.model_validate(recording, from_attributes=True)


@router.get('/{recording_id}')
async def get_recording(recording_id: int, token: str = Depends(oauth2_scheme),
                        session: AsyncSession = Depends(get_session)) -> RecordingRel:
    user_id = await get_user_id(token)

    recording = await session.scalar(Recording.get_by_id(recording_id))

    if not recording:
        raise HTTPException(404)

    if recording.creator_id != user_id:
        raise HTTPException(401)

    return RecordingRel.model_validate(recording, from_attributes=True)


@router.get('/download/{file_id}')
async def get_recording_data(file_id: int, token: str = Depends(oauth2_scheme), session: AsyncSession = Depends(get_session)):
    user_id = await get_user_id(token)

    recording = await (session.scalar(Recording.get_by_id(file_id)))

    if not recording:
        raise HTTPException(404)

    if recording.creator_id != user_id:
        raise HTTPException(401)

    return {'recording': str(await ClientS3.get_file(recording.url))}


@router.post('/')
async def upload_recording(recording: str = Form(), recording_file: UploadFile = File(),
                           token: str = Depends(oauth2_scheme), session: AsyncSession = Depends(get_session)):
    user_id = await get_user_id(token)

    url = await ClientS3.push_file(await sound_filtration(await recording_file.read()), user_id)

    recording_db = Recording(url=url, creator_id=user_id, title=recording)

    session.add(recording_db)

    try:
        await session.commit()
    except IntegrityError as err:
        raise HTTPException(401)

    return RecordingRead.model_validate(recording_db, from_attributes=True)