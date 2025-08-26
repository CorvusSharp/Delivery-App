from celery import Celery
from core.settings import settings

celery = Celery(
    "delivery",
    broker=settings.rabbitmq.url,
    backend=settings.celery.result_backend,
    include=['services.tasks_delivery', 'services.tasks']  # Автоимпорт задач
)

celery.conf.update(
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    timezone=settings.celery.timezone,
    task_acks_late=True,
    worker_prefetch_multiplier=1,
    beat_scheduler="celery.beat:PersistentScheduler",  # Используем встроенный планировщик
    beat_schedule={
        "update-delivery-prices-every-5min": {
            "task": "services.tasks_delivery.update_delivery_prices",
            "schedule": 300.0,  # каждые 5 минут
        },
    },
)
