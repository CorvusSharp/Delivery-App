"""
FastAPI зависимости для внедрения сервисов.
"""
from fastapi import Request, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from adapters.db.session import get_db
from adapters.db.repositories.parcel import SQLAlchemyParcelRepository
from application.parcel_service import ParcelService
from core.di import container


def get_session_id(request: Request) -> str:
    """Получить ID сессии из состояния запроса."""
    return request.state.session_id


def get_request_id(request: Request) -> str:
    """Получить ID запроса из состояния запроса."""
    return request.state.request_id


def get_parcel_repository(db: AsyncSession = Depends(get_db)) -> SQLAlchemyParcelRepository:
    """Создать репозиторий посылок с текущей сессией БД."""
    return SQLAlchemyParcelRepository(db)


def get_parcel_service(repo: SQLAlchemyParcelRepository = Depends(get_parcel_repository)) -> ParcelService:
    """Создать сервис посылок с внедренным репозиторием."""
    return ParcelService(repo)


def get_messaging_adapter():
    """Получить адаптер для отправки сообщений."""
    return container.resolve("messaging_adapter")
