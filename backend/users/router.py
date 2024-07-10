from fastapi import APIRouter, Depends, HTTPException, Security

from .relschemas import UserRel
from .auth import get_current_user
from .models import User
from .auth import router as auth_router


router = APIRouter(prefix='/user', tags=['user'])
router.include_router(auth_router)

@router.get('/')
async def get_user(user: User = Depends(get_current_user)) -> UserRel:
    return UserRel.model_validate(user, from_attributes=True)