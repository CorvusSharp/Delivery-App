"""
Интерфейсы репозиториев для доменного слоя.
"""
from abc import ABC, abstractmethod
from typing import List, Optional, Mapping, Any
from domain.entities.parcel import Parcel, ParcelType


class ParcelRepository(ABC):
    """Интерфейс репозитория посылок."""
    
    @abstractmethod
    async def save(self, parcel: Parcel) -> Parcel:
        """Сохранить посылку."""
        pass
    
    @abstractmethod
    async def get_by_id(self, parcel_id: int, session_id: str) -> Optional[Parcel]:
        """Получить посылку по ID и сессии."""
        pass
    
    @abstractmethod
    async def get_by_session(
        self, 
        session_id: str, 
        type_id: Optional[int] = None,
        has_price: Optional[bool] = None,
        limit: int = 10,
        offset: int = 0,
        order_by: str = "id"
    ) -> List[Parcel]:
        """Получить посылки по сессии с фильтрацией, пагинацией и сортировкой."""
        pass
    
    @abstractmethod
    async def get_types(self) -> List[ParcelType]:
        """Получить все типы посылок."""
        pass
    
    @abstractmethod
    async def get_type_by_id(self, type_id: int) -> Optional[ParcelType]:
        """Получить тип посылки по ID."""
        pass


class TaskQueuePort(ABC):
    """Интерфейс для работы с очередью задач."""
    
    @abstractmethod
    def send(self, task_name: str, payload: Mapping[str, Any], *, queue: Optional[str] = None) -> str:
        """Отправить задачу в очередь."""
        pass
