from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from ..db.dependencies import get_session
from .relschemas import UserRel
from .schemas import UserRead
from .auth import get_user_id
from .models import User
from .auth import router as auth_router, oauth2_scheme


router = APIRouter(prefix='/user', tags=['user'])
router.include_router(auth_router)


@router.post('/')
async def create_user(session: AsyncSession = Depends(get_session)) -> UserRead:
    user = User()

    session.add(user)
    await session.commit()

    return UserRead.model_validate(user, from_attributes=True)


@router.get('/')
async def get_user(token: str = Depends(oauth2_scheme), session: AsyncSession = Depends(get_session)) -> UserRel:
    user_id = await get_user_id(token)

    query = User.get_by_id(user_id)

    user = await session.scalar(query)

    if user is None:
        raise HTTPException(404)

    return UserRel.model_validate(user, from_attributes=True)
