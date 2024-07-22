import time
import wave
import io
from faststream.redis import RedisBroker
from faststream import FastStream
from fastapi import Depends

from ..config import settings
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncAttrs

from ..tags.models import Tag, TagType

from .ML.main import asr, bert
# from .ML.utils import filter
from ..sound.sound import sound_filtration

from ..recordings.models import Recording
from ..recordings.S3Model import ClientS3

from ..sound.sound import get_road


engine = create_async_engine("postgresql+asyncpg://postgres:postgres@localhost:5432/vk-pg")
session_factory = async_sessionmaker(engine, expire_on_commit=False)

broker = RedisBroker("redis://localhost:6379")
app = FastStream(broker)


async def get_tags_from_model(recording_url, recording_id):
    tags = bert.filter(asr.forced_align(recording_url))
    async with session_factory() as session:
        for i in tags:
            if i[3]:
                tag = Tag(recording_id=recording_id, start=i[1], end=i[2], description="", tag_type=TagType.SOURCETAG)
                session.add(tag)
    await session.commit()


@broker.subscriber("recording_compute")
async def recording_compute(recording_id: int):
    async with session_factory() as session:
        recording = await session.get(Recording, recording_id)
        byte = await sound_filtration(await ClientS3.get_file(recording.url))

        time.sleep(5)

        await ClientS3.put_file(byte, recording["url"])

        #recording.soundwave = str(await get_road(byte))

        await get_tags_from_model("/home/ubuntu/backend/env/local_save/" + recording["url"], recording_id)

        recording.processing = False

        await session.commit()

    return 200