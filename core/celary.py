from celery import Celery
from core.settings import settings

celery = Celery(
    "delivery",
    broker=settings.rabbitmq.url,
    backend=settings.celery.result_backend,
)

celery.conf.update(
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    timezone=settings.celery.timezone,
    task_acks_late=True,
    worker_prefetch_multiplier=1,
)
