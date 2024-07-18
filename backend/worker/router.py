import time
import wave
import io
from faststream.redis import RedisBroker
from faststream import FastStream
from fastapi import Depends

from ..db.database import session_factory
from ..db.dependencies import AsyncSession, get_session

from ..recordings.models import Recording
from ..results.models import Result
from ..recordings.S3Model import ClientS3

from ..sound.sound import cut_file, sound_filtration, get_road


broker = RedisBroker("redis://redis:6379/0")
app = FastStream(broker)


@broker.subscriber("cut_result")
async def cut_result(result_id: int):
    async with session_factory() as session:
        result = await session.scalar(Result.get_by_id(result_id))

        recording = result.source

        byte = await cut_file(await ClientS3.get_file(recording.url), recording.tags)

        with wave.open(io.BytesIO(byte), 'rb') as dur:
            result.duration = int(dur.getnframes() / float(dur.getframerate()))

        result.url = await ClientS3.push_file(byte, recording.creator_id)
        result.processing = False

        await session.commit()

    return {'sperma': 'vo rtu'}


@broker.subscriber("recording_compute")
async def recording_compute(recording_id: int):
    async with session_factory() as session:
        recording = await session.scalar(Recording.get_by_id(recording_id))

        byte = await ClientS3.get_file(recording.url)

        time.sleep(30)

        await ClientS3.put_file(byte, recording.url)

        recording.soundwave = str(await get_road(byte))
        recording.processing = False

        await session.commit()

    return {'porno': '1488'}