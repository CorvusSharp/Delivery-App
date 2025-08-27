"""
Use-cases для работы с посылками.
Оркестрирует доменную логику через порты, не зависит от конкретных реализаций.
"""
from decimal import Decimal
from loguru import logger
from functools import wraps
from typing import Dict, List, Optional, Any

from repositories.interfaces import ParcelRepository
from domain.entities.parcel import Parcel, ParcelType


# Декоратор логирования
def log_call(fn):
    @wraps(fn)
    async def wrapper(*args, **kwargs):
        logger.info(f"Call {fn.__name__}")
        return await fn(*args, **kwargs)
    return wrapper


class ParcelService:
    """Сервис use-cases для работы с посылками."""
    
    def __init__(self, repo: ParcelRepository):
        self.repo = repo

    @log_call
    async def register_parcel(self, name: str, weight: float, type_id: int, value_usd: float, session_id: str) -> Dict[str, Any]:
        """Регистрирует новую посылку и возвращает данные в виде словаря."""
        # Получаем тип посылки
        parcel_type = await self.repo.get_type_by_id(type_id)
        if not parcel_type:
            raise ValueError(f"Тип посылки с ID {type_id} не найден")
        
        # Создаем доменную сущность
        parcel = Parcel(
            id=None,
            name=name,
            weight=Decimal(str(weight)),
            type=parcel_type,
            value_usd=Decimal(str(value_usd)),
            session_id=session_id
        )
        
        # Сохраняем через репозиторий
        saved_parcel = await self.repo.save(parcel)
        
        return self._parcel_to_dict(saved_parcel)

    @log_call
    async def get_parcel(self, parcel_id: int, session_id: str) -> Dict[str, Any]:
        """Получает посылку по ID и возвращает данные в виде словаря."""
        parcel = await self.repo.get_by_id(parcel_id, session_id)
        if not parcel:
            raise ValueError("Parcel not found")
        
        return self._parcel_to_dict(parcel)

    @log_call
    async def list_parcels(self, session_id: str, type_id: Optional[int] = None, has_price: Optional[bool] = None, limit: int = 10, offset: int = 0) -> List[Dict[str, Any]]:
        """Получает список посылок и возвращает данные в виде списка словарей."""
        parcels = await self.repo.get_by_session(session_id)
        
        # Фильтрация (TODO: перенести в репозиторий)
        if type_id is not None:
            parcels = [p for p in parcels if p.type.id == type_id]
        if has_price is not None:
            if has_price:
                parcels = [p for p in parcels if p.delivery_price_rub is not None]
            else:
                parcels = [p for p in parcels if p.delivery_price_rub is None]
        
        # Пагинация (TODO: перенести в репозиторий)
        parcels = parcels[offset:offset + limit]
        
        return [self._parcel_to_dict(p) for p in parcels]

    @log_call
    async def get_types(self) -> List[Dict[str, Any]]:
        """Получает типы посылок и возвращает данные в виде списка словарей."""
        types = await self.repo.get_types()
        return [self._type_to_dict(t) for t in types]
    
    def _parcel_to_dict(self, parcel: Parcel) -> Dict[str, Any]:
        """Преобразование доменной сущности в словарь для презентационного слоя."""
        return {
            "id": parcel.id,
            "name": parcel.name,
            "weight": float(parcel.weight),
            "type": self._type_to_dict(parcel.type),
            "value_usd": float(parcel.value_usd),
            "delivery_price_rub": float(parcel.delivery_price_rub) if parcel.delivery_price_rub else None
        }
    
    def _type_to_dict(self, parcel_type: ParcelType) -> Dict[str, Any]:
        """Преобразование типа посылки в словарь."""
        return {
            "id": parcel_type.id,
            "name": parcel_type.name
        }
