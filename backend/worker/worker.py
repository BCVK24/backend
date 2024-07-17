import time

from faststream import FastStream
from faststream.redis import RedisBroker
from faststream import Depends

import os

from ..recordings.models import Recording
from ..db.dependencies import get_session, AsyncSession


broker = RedisBroker("redis://redis:6379/0")
app = FastStream(broker)


@broker.subscriber("get_tags")
async def get_tags(recording_id: int, session: AsyncSession = Depends(get_session)):
    recording = await session.scalar(Recording.get_by_id(recording_id))

    recording.processing = False

    await session.commit()

    print("1488")