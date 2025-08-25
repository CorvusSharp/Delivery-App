from fastapi import FastAPI
from core.logging import setup_logging
from core.settings import fastapi as fa
from resources.middlewares import RequestContextMiddleware
from resources.routers import health as health_router
from resources.routers import tasks as tasks_router
from core.di import container
from services.adapters.messaging_celery import CeleryTaskQueueAdapter

# логирование
setup_logging()

def create_app() -> FastAPI:
    app = FastAPI(
        title=fa.app_title,
        version=fa.app_version,
        docs_url=fa.docs_url,
        redoc_url=fa.redoc_url,
    )
    # DI: регистрируем адаптеры для портов
    container.register("task_queue", lambda: CeleryTaskQueueAdapter())

    # middlewares
    app.add_middleware(RequestContextMiddleware)

    # routers
    app.include_router(health_router.router)
    app.include_router(tasks_router.router)

    app.openapi_tags = [
        {"name": "Health", "description": "Проверка состояния сервиса"},
        {"name": "Tasks", "description": "Тестовые Celery задачи через порт TaskQueue"},
    ]
    return app

app = create_app()
