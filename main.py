import asyncio
from sqlalchemy import select

from backend.db.models import *
from backend.db.database import *


async def main():
    async with session_factory() as session:
        new_user = User()
        session.add(new_user)
        await session.commit()

    async with session_factory() as session:
        query = select(User)

        result = await session.scalars(query)

        print(result)


asyncio.run(main())
