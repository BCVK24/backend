import base64

from fastapi import HTTPException, Depends, Security
from fastapi.security import APIKeyHeader

from sqlalchemy.ext.asyncio import AsyncSession

from .models import User

from ..db.dependencies import get_session


api_key_header = APIKeyHeader(name='Authorization')


async def get_current_user(token: str = Security(api_key_header), session: AsyncSession = Depends(get_session)) -> User:
    decode = str(base64.b64decode(token.strip("VK ")))

    args = dict()

    for i in decode.split('&'):
        gay_porno_1488 = i.split('=')
        args[gay_porno_1488[0]] = gay_porno_1488[1]

    token_valid = True

    if not token_valid:
        raise HTTPException(1488)

    user_id = str(args['vk_user_id'])

    user = await session.scalar(User.get_by_vk_id(str(user_id)))

    if not user:
        user = User(vk_id=user_id)
        session.add(user)
        await session.commit()

        user = await session.scalar(User.get_by_vk_id(str(user_id)))

    return user
