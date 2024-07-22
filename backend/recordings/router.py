import wave

from fastapi import APIRouter, UploadFile, File, Depends, HTTPException, Form
from faststream.redis import RedisBroker

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import contains_eager
from sqlalchemy import select

from ..db.dependencies import get_session
from ..users.auth import get_current_user
from .models import Recording
from .relschemas import RecordingRel
from .S3Model import ClientS3
from .schemas import RecordingRead, RecordingUpdate
from ..users.models import User

from ..tags.models import Tag, TagType

import io


router = APIRouter(prefix='/recording', tags=['recording'])


@router.delete('/{recording_id}')
async def delete_recording(recording_id: int, user: User = Depends(get_current_user),
                           session: AsyncSession = Depends(get_session)) -> RecordingRead:
    get_rec = await session.get(Recording, recording_id)

    if not get_rec:
        raise HTTPException(404)
    if get_rec.creator_id != user.id:
        raise HTTPException(401)
    if get_rec.processing:
        raise HTTPException(425)

    await ClientS3.delete_file(get_rec.url)

    record_return = RecordingRead.model_validate(get_rec, from_attributes=True)

    await session.delete(get_rec)
    await session.commit()

    return record_return


@router.put('/')
async def put_recording_name(recording: RecordingUpdate, user: User = Depends(get_current_user),
                             session: AsyncSession = Depends(get_session)) -> RecordingRead:
    recording_db = await session.get(Recording, recording.id)

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
    recording = await session.get(Recording, id)

    if not recording:
        raise HTTPException(404)
    if recording.creator_id != user.id:
        raise HTTPException(401)

    return RecordingRel.model_validate(recording, from_attributes=True)


@router.post('/')
async def upload_recording(user: User = Depends(get_current_user), recording: str = Form(),
                           recording_file: UploadFile = File(),
                           session: AsyncSession = Depends(get_session)) -> RecordingRead:

    byte = await recording_file.read()

    with wave.open(io.BytesIO(byte), 'rb') as dur:
         duration = int(dur.getnframes() / float(dur.getframerate()))

    url = await ClientS3.push_file(byte, user.id)

    recording_db = Recording(url=url, creator_id=user.id, title=recording, duration=duration,
                             soundwave="soundwave", processing=True)

    try:
        session.add(recording_db)

        await session.commit()
    except Exception as e:
        raise HTTPException(401)

    async with RedisBroker("redis://redis:6379/0") as reddis:
        await reddis.publish(recording_db.id, "recording_compute")

    return RecordingRead.model_validate(recording_db, from_attributes=True)


@router.post('/model_tags/{recording_id}', tags=['model tags'])
async def get_model_tags(recording_id: int, user: User = Depends(get_current_user),
                         session: AsyncSession = Depends(get_session)) -> RecordingRel:
    recording = await session.get(Recording, recording_id)

    if not recording:
        raise HTTPException(404)
    if recording.creator_id != user.id:
        raise HTTPException(401)
    if recording.processing:
        raise HTTPException(425)

    stmt = Tag.delete_model_tag_by_recording_id(recording_id)

    await session.execute(stmt)

    tag_list = await session.scalars(Tag.get_source_tag_by_recording_id(recording_id))

    for i in tag_list:
        tag_new = Tag(recording_id=recording_id, start=i.start, end=i.end, description=i.description,
                      tag_type=TagType.MODELTAG)
        session.add(tag_new)

    await session.commit()

    return RecordingRel.model_validate(recording, from_attributes=True)


@router.delete('/model_tags/{recording_id}', tags=['model tags'])
async def delete_model_tags(recording_id: int, user: User = Depends(get_current_user),
                         session: AsyncSession = Depends(get_session)) -> RecordingRel:
    recording = await session.get(Recording, recording_id)

    if not recording:
        raise HTTPException(404)
    if recording.creator_id != user.id:
        raise HTTPException(401)
    if recording.processing:
        raise HTTPException(425)

    stmt = Tag.delete_model_tag_by_recording_id(recording_id)

    await session.execute(stmt)

    await session.commit()

    return RecordingRel.model_validate(recording, from_attributes=True)