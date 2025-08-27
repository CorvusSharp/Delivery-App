from __future__ import annotations

from fastapi import FastAPI

from core.logging import setup_logging
from core.responses import add_exception_handlers
from core.settings import fastapi as fa
from core.di import container, register_adapters
from resources.middlewares import RequestContextMiddleware
from resources.routers import admin as admin_router
from resources.routers import health as health_router
from resources.routers import parcels as parcels_router
from resources.routers import tasks as tasks_router
from resources.routers import web as web_router


# Инициализируем логирование на уровне модуля,
# чтобы uvicorn/gunicorn воркеры унаследовали конфиг.
setup_logging()

# Регистрируем адаптеры в DI контейнере
register_adapters()


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

    # Middlewares
    app.add_middleware(RequestContextMiddleware)

    # Routers
    app.include_router(health_router.router)
    app.include_router(tasks_router.router)
    app.include_router(parcels_router.router)
    app.include_router(admin_router.router)
    app.include_router(web_router.router)

    # OpenAPI-теги
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

