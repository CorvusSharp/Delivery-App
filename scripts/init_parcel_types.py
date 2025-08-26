import asyncio
from sqlalchemy import delete
from core.db import engine, Base, AsyncSessionLocal
from sqlalchemy.ext.asyncio import AsyncSession
from domain.models import ParcelType
from loguru import logger

async def init_parcel_types():
    """Инициализация типов посылок в базе данных."""
    
    # Создаем таблицы если их нет
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    # Создаем сессию
    session = AsyncSessionLocal()
    try:
        # Удаляем старые типы
        await session.execute(delete(ParcelType))
        await session.commit()
        logger.info("Старые типы посылок удалены")
        
        # Создаем новые типы
        parcel_types = [
            ParcelType(id=1, name="одежда"),
            ParcelType(id=2, name="электроника"),
            ParcelType(id=3, name="разное"),
        ]
        
        session.add_all(parcel_types)
        await session.commit()
        logger.info("Добавлены новые типы посылок: %s", [pt.name for pt in parcel_types])
        
        # Проверяем что типы добавились
        from sqlalchemy import select
        result = await session.execute(select(ParcelType))
        types = result.scalars().all()
        
        logger.info("Типы посылок в базе:")
        for ptype in types:
            logger.info("  ID: %s, Название: %s", ptype.id, ptype.name)
    finally:
        await session.close()

if __name__ == "__main__":
    asyncio.run(init_parcel_types())
