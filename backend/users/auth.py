import base64
import hashlib
import hmac
import time

from fastapi import HTTPException, Depends, Security
from fastapi.security import APIKeyHeader

from sqlalchemy.ext.asyncio import AsyncSession

from .models import User

from ..db.dependencies import get_session

from ..config import settings


api_key_header = APIKeyHeader(name='Authorization')


async def get_current_user(token: str = Security(api_key_header), session: AsyncSession = Depends(get_session)) -> User:
    if not token:
        raise HTTPException(401)

    decode = base64.b64decode(token.strip("VK ") + "===").decode().replace("'", '').strip("?")

    args = dict()

    for i in decode.split('&'):
        data = i.split('=')
        args[data[0]] = data[1]

    sign_args = '&'.join([f'{i}={args[i]}' for i in args.keys() if i.startswith('vk_')])

    hashed = base64.b64encode(
       hmac.new(settings.CLIENT_SECRET.encode(), sign_args.encode(), hashlib.sha256).digest()
    ).decode().replace('+', '-').replace('/', '_').replace('=', '')

    args['sign'] = args['sign'].strip()
    hashed = hashed.strip()

    if hashed[:len(args['sign'])] != args['sign']:
        raise HTTPException(401)

    if time.time() - int(args['vk_ts']) >= 60 * 60:
        raise HTTPException(401)

    user_id = str(args['vk_user_id'])

    user = await session.scalar(User.get_by_vk_id(str(user_id)))

    if not user:
        user = User(vk_id=user_id)
        session.add(user)
        await session.commit()

        user = await session.scalar(User.get_by_vk_id(str(user_id)))

    return user
