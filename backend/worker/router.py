import time
import wave
import io
from faststream.redis.fastapi import RedisRouter
from fastapi import Depends

from ..db.dependencies import AsyncSession, get_session

from ..recordings.models import Recording
from ..results.models import Result
from ..recordings.S3Model import ClientS3

from ..sound.sound import cut_file


router = RedisRouter("redis://redis:6379/0")


@router.subscriber("cut_result")
async def cut_result(result_id: int, session: AsyncSession = Depends(get_session)):

    result = await session.scalar(Result.get_by_id(result_id))

    recording = result.source

    byte = await cut_file(await ClientS3.get_file(recording.url), recording.tags)

    with wave.open(io.BytesIO(byte), 'rb') as dur:
        result.duration = int(dur.getnframes() / float(dur.getframerate()))

    result.url = await ClientS3.push_file(byte, recording.creator_id)

    result.processing = False

    await session.commit()

    return {'sperma': 'vo rtu'}


@router.subscriber("get_tags")
async def get_tags(recording_id: int, session: AsyncSession = Depends(get_session)):
    recording = await session.scalar(Recording.get_by_id(recording_id))
    time.sleep(30)

    recording.processing = False
    await session.commit()

    return {'porno': '1488'}