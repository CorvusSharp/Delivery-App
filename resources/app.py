from __future__ import annotations

from fastapi import FastAPI

from core.logging import setup_logging
from core.responses import add_exception_handlers
from core.settings import fastapi as fa
from core.di import container
from resources.middlewares import RequestContextMiddleware
from resources.routers import admin as admin_router
from resources.routers import health as health_router
from resources.routers import parcels as parcels_router
from resources.routers import tasks as tasks_router
from services.adapters.messaging_celery import CeleryTaskQueueAdapter


# Инициализируем логирование на уровне модуля,
# чтобы uvicorn/gunicorn воркеры унаследовали конфиг.
setup_logging()


def _register_adapters() -> None:
    """
    Регистрирует адаптеры портов в DI-контейнере.
    Делает регистрацию идемпотентной (повторные вызовы не ломают контейнер).
    """
    if not container.has("task_queue"):
        container.register("task_queue", lambda: CeleryTaskQueueAdapter())


def create_app() -> FastAPI:
    """
    Создаёт и настраивает FastAPI-приложение для службы доставки.
    Включает DI, middlewares, роутеры, обработчики ошибок и документацию.
    """
    app = FastAPI(
        title=getattr(fa, "app_title", "Delivery Service"),
        version=getattr(fa, "app_version", "0.1.0"),
        docs_url=getattr(fa, "docs_url", "/docs"),
        redoc_url=getattr(fa, "redoc_url", "/redoc"),
    )

    # DI: регистрируем адаптеры для портов
    _register_adapters()

    # Middlewares
    app.add_middleware(RequestContextMiddleware)

    # Routers
    app.include_router(health_router.router)
    app.include_router(tasks_router.router)
    app.include_router(parcels_router.router)
    app.include_router(admin_router.router)

    # Ленивая регистрация роутеров, чтобы избежать циклических импортов
    from resources.routers import admin_init as admin_init_router  # noqa: WPS433
    app.include_router(admin_init_router.router)

    from resources.routers import web as web_router  # noqa: WPS433
    app.include_router(web_router.router)

    # OpenAPI-теги (для красивой документации)
    app.openapi_tags = [
        {"name": "Health", "description": "Проверка состояния сервиса"},
        {"name": "Tasks", "description": "Тестовые Celery-задачи через порт TaskQueue"},
        {"name": "Parcels", "description": "CRUD операции с посылками"},
        {"name": "Admin", "description": "Административные операции"},
        {"name": "Web", "description": "Веб-интерфейс для работы с посылками"},
    ]

    add_exception_handlers(app)
    return app

app = create_app()

