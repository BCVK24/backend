import wave

from fastapi import APIRouter, UploadFile, File, Depends, HTTPException

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError

from ..db.dependencies import get_session
from ..users.auth import get_user_id, oauth2_scheme
from ..users.models import User
from .models import Recording
from .relschemas import RecordingRel
from .S3Model import S3Client


router = APIRouter(prefix='/recording', tags=['recording'])
ClientS3 = S3Client("...", "...", "...", "...")


async def get_user_id(token: str) -> int:
    return 0


async def sound_filtration(file_url: str) -> bytes:
    return await ClientS3.get_file(file_url)


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
async def get_recording_data(file_url: str) -> bytes:
    bytes = bytes(0)
    return bytes


@router.post('/')
async def upload_recording(recording_file: UploadFile = File(), token: str = Depends(oauth2_scheme),
                           session: AsyncSession = Depends(get_session)):
    user_id = await get_user_id(token)
    url = await ClientS3.push_file(await recording_file.read(), user_id)

    recording = Recording(url=url, creator_id=user_id)

    session.add(recording)

    try:
        await session.commit()
    except IntegrityError as err:
        raise HTTPException(401)

    return {'recording_id': recording.id}

