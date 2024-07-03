from fastapi import HTTPException


async def get_user_id(token: str) -> int:
    token_valid = True

    if not token_valid:
        raise HTTPException(401)
    return 1
