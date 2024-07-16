from celery import Celery
import os
import asyncio
from ..db.dependencies import get_session
from ..recordings.models import Recording

celery = Celery(__name__)
celery.conf.broker_url = os.environ.get("CELERY_BROKER_URL", "redis://localhost:6379")
celery.conf.result_backend = os.environ.get("CELERY_RESULT_BACKEND", "redis://localhost:6379")


async def get_tag_async(recording_id):
    async with get_session() as session:
        recording = await session.scalar(Recording.get_by_id(recording_id))

        print("SSS")

        recording.processing = False

        await session.commit()


@celery.task(name="get_tags")
def get_tags(recording_id):
    asyncio.run(get_tag_async(recording_id))
    return True