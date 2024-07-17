import time

from celery import Celery
import os

from sqlalchemy.orm import Session
from ..db.database import sync_engine

from ..recordings.models import Recording


celery = Celery(__name__)
celery.conf.broker_url = os.environ.get("CELERY_BROKER_URL", "redis://localhost:6379")
celery.conf.result_backend = os.environ.get("CELERY_RESULT_BACKEND", "redis://localhost:6379")


@celery.task(name="get_tags", ignore_result=True)
def get_tags(recording_id):
    with Session(sync_engine) as session:
        recording = session.scalar(Recording.get_by_id(recording_id))
        recording.processing = False
        session.commit()
    time.sleep(30)
    return True
