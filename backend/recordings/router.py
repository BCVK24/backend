import wave

from fastapi import APIRouter, UploadFile, File, Depends, HTTPException, Form

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError

from ..db.dependencies import get_session
from ..users.auth import get_current_user
from .models import Recording
from .relschemas import RecordingRel
from .S3Model import ClientS3
from .schemas import RecordingRead, RecordingUpdate
from ..users.models import User

from ..sound.sound import sound_filtration, get_road

from ..worker.router import router as broker

import io


router = APIRouter(prefix='/recording', tags=['recording'])


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
                           recording_file: UploadFile = File(),
                           session: AsyncSession = Depends(get_session)) -> RecordingRead:

    byte = await sound_filtration(await recording_file.read())

    with wave.open(io.BytesIO(byte), 'rb') as dur:
        duration = int(dur.getnframes() / float(dur.getframerate()))

    url = await ClientS3.push_file(byte, user.id)

    soundwave = str(await get_road(byte))

    recording_db = Recording(url=url, creator_id=user.id, title=recording, duration=duration,
                             soundwave=soundwave, processing=True)

    session.add(recording_db)

    try:
        await session.commit()
    except IntegrityError as err:
        raise HTTPException(401)

    await broker.broker.publish(recording_db.id, "get_tags")

    return RecordingRead.model_validate(recording_db, from_attributes=True)
