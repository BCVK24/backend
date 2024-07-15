from celery import Celery
from ..recordings.models import Recording
from ..db.dependencies import AsyncSession, get_session

import os

celery = Celery(__name__)
celery.conf.broker_url = os.environ.get("CELERY_BROKER_URL", "redis://localhost:6379")
celery.conf.result_backend = os.environ.get("CELERY_RESULT_BACKEND", "redis://localhost:6379")


@celery.task
def get_tags(recording):
    print("aiaiaiiaiaiaiaiaiai")
    return True