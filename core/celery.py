from celery import Celery
from core.settings import settings

celery = Celery(
    "delivery",
    broker=settings.rabbitmq.url,
    backend=settings.celery.result_backend,   # redis://redis:6379/0
    include=["services.tasks_delivery", "services.tasks"],
)

celery.conf.update(
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],

    enable_utc=True,
    timezone=settings.celery.timezone,  # "UTC" у тебя в .env

    task_default_queue="celery",
    worker_prefetch_multiplier=1,   # честная обработка по 1 таске
    task_acks_late=True,            # ACK после выполнения
    task_reject_on_worker_lost=True,# не терять таску при крэше воркера
    task_track_started=True,        # статус STARTED (удобно для Flower)

    broker_connection_retry_on_startup=True,

    broker_heartbeat=30,            # помогает отвалам TCP
    broker_pool_limit=10,           # не раздувать коннекты

    # Результаты
    result_expires=60 * 60 * 12,    # 12 часов (подчистка результатов)

    # Beat-планировщик и расписание
    beat_scheduler="celery.beat:PersistentScheduler",
    beat_schedule={
        "update-delivery-prices-every-5min": {
            "task": "services.tasks_delivery.update_delivery_prices",
            "schedule": 300.0,
        },
    },
    # Где хранить БД планировщика (важно в Docker)
    beat_schedule_filename="/var/run/celery/celerybeat-schedule.db",
)
