from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from .models import Tag
from .schemas import TagRead, TagUpdate, TagCreate
from ..db.dependencies import get_session

from ..users.models import User
from ..users.auth import get_current_user

from .models import TagType
from ..recordings.models import Recording


router = APIRouter(prefix='/tag', tags=['tag'])


@router.put('/')
async def update_tag(tag: TagUpdate, user: User = Depends(get_current_user),
                     session: AsyncSession = Depends(get_session)) -> TagRead:
    tag_db = await session.get(Tag, tag.id)

    if not tag_db:
        raise HTTPException(404)

    tag_db.start = tag.start
    tag_db.end = tag.end
    tag_db.description = tag.description

    await session.commit()

    return TagRead.model_validate(tag_db, from_attributes=True)


@router.delete('/{tag_id}')
async def delete_tag(tag_id: int, user: User = Depends(get_current_user),
                     session: AsyncSession = Depends(get_session)) -> TagRead:
    tag_get = await session.get(Tag, tag_id)

    if not tag_get:
        raise HTTPException(404)

    tag_return = TagRead.model_validate(tag_get, from_attributes=True)

    await session.delete(tag_get)

    await session.commit()

    return tag_return


@router.post('/')
async def create_tag(tag: TagCreate, user: User = Depends(get_current_user),
                     session: AsyncSession = Depends(get_session)) -> TagRead:
    if tag.start > tag.end:
        raise HTTPException(422)

    recording = await session.get(Recording, tag.recording_id)

    if recording.processing:
        raise HTTPException(425)

    tag_get = Tag(**tag.model_dump(), tag_type=TagType.USERTAG)

    tag_get.start = max(0, tag_get.start)
    tag_get.end = min(recording.duration, tag_get.end)

    session.add(tag_get)

    await session.commit()

    return TagRead.model_validate(tag_get, from_attributes=True)

