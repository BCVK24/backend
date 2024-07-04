from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from .models import Tag
from .schemas import TagRead, TagUpdate
from ..db.dependencies import get_session
from ..users.auth import get_user_id, oauth2_scheme

router = APIRouter(prefix='/tag', tags=['tag'])


@router.put('/')
async def update_tag(tag: TagUpdate, token: str = Depends(oauth2_scheme),
                     session: AsyncSession = Depends(get_session)) -> TagRead:
    pass  # Update tag [start, end]


@router.delete('/{tag_id}')
async def delete_tag(tag_id: int, token: str = Depends(oauth2_scheme),
                     session: AsyncSession = Depends(get_session)) -> TagRead:
    pass  # Delete tag by id


@router.post('/')
async def create_tag(tag):
    pass
