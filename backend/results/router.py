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

from ..sound.sound import get_road
from ..tags.models import TagType


router = APIRouter(prefix='/result', tags=['result'])


async def cut_file(recording_bytes: bytes, tags: list[Tag]) -> bytes:
    with wave.open(io.BytesIO(recording_bytes)) as sound:
        params = sound.getparams()
        audio = np.frombuffer(sound.readframes(params.nframes), dtype=np.int16)

    for tag in tags:
        if tag.tag_type == TagType.SOURCETAG:
            continue
        audio = np.delete(audio, slice(int(tag.start * params.framerate * params.sampwidth),
                                       int(tag.end * params.framerate * params.sampwidth)))

    ret = io.BytesIO()

    with wave.open(ret, 'wb') as rt:
        rt.setparams(params)
        rt.writeframes(audio.tobytes())

    ret.seek(0)

    return ret.read()


@router.delete('/{result_id}')
async def delete_result(result_id: int, user: User = Depends(get_current_user),
                        session: AsyncSession = Depends(get_session)) -> ResultRel:
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


@router.post('/{recording_id}')
async def create_result(recording_id: int, user: User = Depends(get_current_user),
                        session: AsyncSession = Depends(get_session)) -> ResultRead:
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