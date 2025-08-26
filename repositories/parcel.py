from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import joinedload
from domain.models import Parcel, ParcelType
from typing import List, Optional

class ParcelRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def add(self, parcel: Parcel) -> Parcel:
        self.db.add(parcel)
        await self.db.commit()
        await self.db.refresh(parcel)
        # Загружаем связанный тип посылки
        result = await self.db.execute(
            select(Parcel).options(joinedload(Parcel.type)).where(Parcel.id == parcel.id)
        )
        return result.scalar_one()

    async def get_by_id(self, parcel_id: int, session_id: str) -> Optional[Parcel]:
        result = await self.db.execute(
            select(Parcel).options(joinedload(Parcel.type)).where(Parcel.id == parcel_id, Parcel.session_id == session_id)
        )
        return result.scalar_one_or_none()

    async def list(self, session_id: str, type_id: Optional[int] = None, has_price: Optional[bool] = None, limit: int = 10, offset: int = 0) -> List[Parcel]:
        query = select(Parcel).options(joinedload(Parcel.type)).where(Parcel.session_id == session_id)
        if type_id:
            query = query.where(Parcel.type_id == type_id)
        if has_price is not None:
            if has_price:
                query = query.where(Parcel.delivery_price_rub.isnot(None))
            else:
                query = query.where(Parcel.delivery_price_rub.is_(None))
        query = query.offset(offset).limit(limit)
        result = await self.db.execute(query)
        return result.scalars().all()

    async def get_types(self) -> List[ParcelType]:
        result = await self.db.execute(select(ParcelType))
        return result.scalars().all()
