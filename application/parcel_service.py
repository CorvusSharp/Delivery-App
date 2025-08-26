from repositories.parcel import ParcelRepository
from adapters.db.models import Parcel, ParcelType
from loguru import logger
from functools import wraps
from typing import Dict, List, Optional, Any

# Декоратор логирования
def log_call(fn):
    @wraps(fn)
    async def wrapper(*args, **kwargs):
        logger.info(f"Call {fn.__name__}")
        return await fn(*args, **kwargs)
    return wrapper

class ParcelService:
    def __init__(self, repo: ParcelRepository):
        self.repo = repo

    @log_call
    async def register_parcel(self, name: str, weight: float, type_id: int, value_usd: float, session_id: str) -> Dict[str, Any]:
        """Регистрирует новую посылку и возвращает данные в виде словаря."""
        parcel = Parcel(
            name=name,
            weight=weight,
            type_id=type_id,
            value_usd=value_usd,
            session_id=session_id
        )
        parcel = await self.repo.add(parcel)
        
        return {
            "id": parcel.id,
            "name": parcel.name,
            "weight": parcel.weight,
            "type": {
                "id": parcel.type.id,
                "name": parcel.type.name
            } if parcel.type is not None else None,
            "value_usd": parcel.value_usd,
            "delivery_price_rub": parcel.delivery_price_rub
        }

    @log_call
    async def get_parcel(self, parcel_id: int, session_id: str) -> Dict[str, Any]:
        """Получает посылку по ID и возвращает данные в виде словаря."""
        parcel = await self.repo.get_by_id(parcel_id, session_id)
        if not parcel:
            raise ValueError("Parcel not found")
        
        return {
            "id": parcel.id,
            "name": parcel.name,
            "weight": parcel.weight,
            "type": {
                "id": parcel.type.id,
                "name": parcel.type.name
            } if parcel.type is not None else None,
            "value_usd": parcel.value_usd,
            "delivery_price_rub": parcel.delivery_price_rub
        }

    @log_call
    async def list_parcels(self, session_id: str, type_id: Optional[int] = None, has_price: Optional[bool] = None, limit: int = 10, offset: int = 0) -> List[Dict[str, Any]]:
        """Получает список посылок и возвращает данные в виде списка словарей."""
        parcels = await self.repo.list(session_id, type_id, has_price, limit, offset)
        return [
            {
                "id": p.id,
                "name": p.name,
                "weight": p.weight,
                "type": {
                    "id": p.type.id,
                    "name": p.type.name
                } if p.type is not None else None,
                "value_usd": p.value_usd,
                "delivery_price_rub": p.delivery_price_rub
            } for p in parcels
        ]

    @log_call
    async def get_types(self) -> List[Dict[str, Any]]:
        """Получает типы посылок и возвращает данные в виде списка словарей."""
        types = await self.repo.get_types()
        return [
            {
                "id": t.id,
                "name": t.name
            } for t in types
        ]
