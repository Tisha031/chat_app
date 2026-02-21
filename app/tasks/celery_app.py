from celery import Celery
from app.core.config import settings

celery_app = Celery(
    "chat_app",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
    include=["app.tasks.notifications"]
)

celery_app.conf.update(
    task_serializer="json",
    result_serializer="json",
    timezone="UTC",
)