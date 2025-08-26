import asyncio
from sqlalchemy import select, update
from core.db import engine, Base, AsyncSessionLocal
from sqlalchemy.ext.asyncio import AsyncSession
from domain.models import ParcelType
from loguru import logger

async def update_parcel_types():
    """Обновление типов посылок в базе данных."""
    
    # Создаем таблицы если их нет
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    # Создаем сессию
    session = AsyncSessionLocal()
    try:
        # Проверяем существующие типы
        result = await session.execute(select(ParcelType))
        existing_types = result.scalars().all()
        
        logger.info("Существующие типы:")
        for ptype in existing_types:
            logger.info("  ID: %s, Название: %s", ptype.id, ptype.name)
        
        # Обновляем существующий тип и добавляем новые
        if existing_types:
            # Обновляем первый тип на "одежда"
            await session.execute(
                update(ParcelType).where(ParcelType.id == existing_types[0].id).values(name="одежда")
            )
            logger.info("Обновлен тип ID %s на 'одежда'", existing_types[0].id)
        
        # Добавляем недостающие типы
        new_types = [
            {"id": 2, "name": "электроника"},
            {"id": 3, "name": "разное"},
        ]
        
        for type_data in new_types:
            # Проверяем, существует ли уже тип с таким ID
            result = await session.execute(
                select(ParcelType).where(ParcelType.id == type_data["id"])
            )
            existing = result.scalar_one_or_none()
            
            if existing:
                # Обновляем существующий
                await session.execute(
                    update(ParcelType).where(ParcelType.id == type_data["id"]).values(name=type_data["name"])
                )
                logger.info("Обновлен тип ID %s на '%s'", type_data["id"], type_data["name"])
            else:
                # Добавляем новый
                new_type = ParcelType(id=type_data["id"], name=type_data["name"])
                session.add(new_type)
                logger.info("Добавлен новый тип ID %s: '%s'", type_data["id"], type_data["name"])
        
        await session.commit()
        
        # Проверяем результат
        result = await session.execute(select(ParcelType).order_by(ParcelType.id))
        types = result.scalars().all()
        
        logger.info("Итоговые типы посылок в базе:")
        for ptype in types:
            logger.info("  ID: %s, Название: %s", ptype.id, ptype.name)
            
    finally:
        await session.close()

if __name__ == "__main__":
    asyncio.run(update_parcel_types())
