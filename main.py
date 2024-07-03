import asyncio
from sqlalchemy import select, delete

from backend.db.models import *
from backend.db.database import *


async def main():
    async with session_factory() as session:
        query = delete(User)
        await session.execute(query)

        new_user = User()
        session.add(new_user)

        stmt = select(User)
        result = await session.scalars(stmt)
        print(result.all())

        await session.commit()


asyncio.run(main())
