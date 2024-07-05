from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from .models import Tag
from .schemas import TagRead, TagUpdate, TagCreate
from ..db.dependencies import get_session
from ..users.auth import get_user_id, oauth2_scheme

router = APIRouter(prefix='/tag', tags=['tag'])


@router.put('/')
async def update_tag(tag: TagUpdate, token: str = Depends(oauth2_scheme),
                     session: AsyncSession = Depends(get_session)) -> TagRead:
    tag_db = await session.scalar(Tag.get_by_id(tag.id))
    tag_db.start = tag.start
    tag_db.end = tag.end

    await session.commit()

    return TagRead.model_validate(tag_db, from_attributes=True)

@router.delete('/{tag_id}')
async def delete_tag(tag_id: int, token: str = Depends(oauth2_scheme),
                     session: AsyncSession = Depends(get_session)) -> TagRead:
    tag_get = await session.scalar(Tag.get_by_id(tag_id))

    if not tag_get:
        raise HTTPException(404)

    tag_return = TagRead.model_validate(tag_get, from_attributes=True)

    await session.delete(tag_get)

    await session.commit()

    return tag_return


@router.post('/')
async def create_tag(tag: TagCreate, token: str = Depends(oauth2_scheme),
                     session: AsyncSession = Depends(get_session)):
    user_id = get_user_id(token)

    tag_get = Tag(**tag.model_dump())

    session.add(tag_get)

    await session.commit()

    return TagRead.model_validate(tag_get, from_attributes=True)

