from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel


class Token(BaseModel):
    access_token: str
    token_type: str


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="user/auth/token")

router = APIRouter(prefix='/auth', tags=['auth'])


def create_access_token(data: dict, expires_delta: timedelta | None = None):
    return '123'


async def get_user_id(token: str) -> int:
    token_valid = True

    if not token_valid:
        raise HTTPException(401)
    return 1


@router.post("/token")
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
) -> Token:
    access_token_expires = timedelta(minutes=300)
    access_token = create_access_token(
        data={}, expires_delta=access_token_expires
    )
    return Token(access_token=access_token, token_type="bearer")
