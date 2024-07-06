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


router = APIRouter(prefix='/recording', tags=['recording'])
ClientS3 = S3Client("...", "...", "...", "...")


async def get_user_id(token: str) -> int:
    return 1


@router.delete('/{recording_id}')
async def delete_recording(recording_id: int, token: str = Depends(oauth2_scheme),
                           session: AsyncSession = Depends(get_session)) -> RecordingRead:
    user_id = await get_user_id(token)

    get_rec = await session.scalar(Recording.get_by_id(recording_id))

    if not get_rec:
        raise HTTPException(404)

    record_return = RecordingRead.model_validate(get_rec, from_attributes=True)

    await session.delete(get_rec)
    await session.commit()

    return record_return


@router.get('/{recording_id}')
async def get_recording(recording_id: int, token: str = Depends(oauth2_scheme),
                        session: AsyncSession = Depends(get_session)) -> RecordingRel:
    user_id = await get_user_id(token)

    query = Recording.get_by_id(recording_id)
    recording = await session.scalar(query)

    if recording is None:
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
    url = await ClientS3.push_file(await recording_file.read(), user_id)

    recording_db = Recording(url=url, creator_id=user_id, title=recording)

    session.add(recording_db)

    try:
        await session.commit()
    except IntegrityError as err:
        raise HTTPException(401)

    return RecordingRead.model_validate(recording_db, from_attributes=True)