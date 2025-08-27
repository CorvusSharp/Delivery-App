"""
Реализация репозитория посылок через SQLAlchemy.
"""
from typing import List, Optional
from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.orm import joinedload
from sqlalchemy.ext.asyncio import AsyncSession

from domain.repositories.interfaces import ParcelRepository
from domain.entities.parcel import Parcel, ParcelType
from adapters.db.models import Parcel as ParcelModel, ParcelType as ParcelTypeModel


class SQLAlchemyParcelRepository(ParcelRepository):
    """Реализация репозитория посылок через SQLAlchemy."""
    
    def __init__(self, db: AsyncSession):
        self.db = db

    async def save(self, parcel: Parcel) -> Parcel:
        """Сохранить посылку (создать или обновить)."""
        if parcel.id is None:
            # Создание новой посылки
            parcel_model = ParcelModel(
                name=parcel.name,
                weight=parcel.weight,
                type_id=parcel.type.id,
                value_usd=parcel.value_usd,
                delivery_price_rub=parcel.delivery_price_rub,
                session_id=parcel.session_id
            )
            self.db.add(parcel_model)
            await self.db.commit()
            await self.db.refresh(parcel_model)
            
            # Загружаем связанный тип
            result = await self.db.execute(
                select(ParcelModel).options(joinedload(ParcelModel.type))
                .where(ParcelModel.id == parcel_model.id)
            )
            parcel_model = result.scalar_one()
            
            return self._to_domain_entity(parcel_model)
        else:
            # Обновление существующей посылки
            result = await self.db.execute(
                select(ParcelModel).where(ParcelModel.id == parcel.id)
            )
            parcel_model = result.scalar_one_or_none()
            if not parcel_model:
                raise ValueError(f"Посылка с ID {parcel.id} не найдена")
            
            parcel_model.name = parcel.name
            parcel_model.weight = parcel.weight
            parcel_model.type_id = parcel.type.id
            parcel_model.value_usd = parcel.value_usd
            parcel_model.delivery_price_rub = parcel.delivery_price_rub
            
            await self.db.commit()
            await self.db.refresh(parcel_model)
            
            # Загружаем связанный тип
            result = await self.db.execute(
                select(ParcelModel).options(joinedload(ParcelModel.type))
                .where(ParcelModel.id == parcel_model.id)
            )
            parcel_model = result.scalar_one()
            
            return self._to_domain_entity(parcel_model)

    async def get_by_id(self, parcel_id: int, session_id: str) -> Optional[Parcel]:
        """Получить посылку по ID и сессии."""
        result = await self.db.execute(
            select(ParcelModel).options(joinedload(ParcelModel.type)).where(
                ParcelModel.id == parcel_id, 
                ParcelModel.session_id == session_id
            )
        )
        parcel_model = result.scalar_one_or_none()
        return self._to_domain_entity(parcel_model) if parcel_model else None

    async def get_by_session(self, session_id: str) -> List[Parcel]:
        """Получить все посылки по сессии."""
        result = await self.db.execute(
            select(ParcelModel).options(joinedload(ParcelModel.type))
            .where(ParcelModel.session_id == session_id)
        )
        parcel_models = result.scalars().all()
        return [self._to_domain_entity(model) for model in parcel_models]

    async def get_types(self) -> List[ParcelType]:
        """Получить все типы посылок."""
        result = await self.db.execute(select(ParcelTypeModel))
        type_models = result.scalars().all()
        return [self._type_to_domain_entity(model) for model in type_models]

    async def get_type_by_id(self, type_id: int) -> Optional[ParcelType]:
        """Получить тип посылки по ID."""
        result = await self.db.execute(
            select(ParcelTypeModel).where(ParcelTypeModel.id == type_id)
        )
        type_model = result.scalar_one_or_none()
        return self._type_to_domain_entity(type_model) if type_model else None

    def _to_domain_entity(self, parcel_model: ParcelModel) -> Parcel:
        """Преобразование ORM модели в доменную сущность."""
        parcel_type = ParcelType(
            id=parcel_model.type.id,
            name=parcel_model.type.name
        )
        
        return Parcel(
            id=parcel_model.id,
            name=parcel_model.name,
            weight=Decimal(str(parcel_model.weight)),
            type=parcel_type,
            value_usd=Decimal(str(parcel_model.value_usd)),
            delivery_price_rub=Decimal(str(parcel_model.delivery_price_rub)) if parcel_model.delivery_price_rub else None,
            session_id=parcel_model.session_id
        )

    def _type_to_domain_entity(self, type_model: ParcelTypeModel) -> ParcelType:
        """Преобразование ORM модели типа в доменную сущность."""
        return ParcelType(
            id=type_model.id,
            name=type_model.name
        )
