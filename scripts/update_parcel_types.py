import asyncio
from sqlalchemy import select, update
from adapters.db.session import engine, Base, AsyncSessionLocal
from sqlalchemy.ext.asyncio import AsyncSession
from adapters.db.models import ParcelType
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
        
        # Обновляем существующий тип и добавляем новые (английские названия)
        if existing_types:
            # Обновляем первый тип на "Clothing"
            await session.execute(
                update(ParcelType).where(ParcelType.id == existing_types[0].id).values(name="Clothing")
            )
            logger.info("Обновлен тип ID %s на 'Clothing'", existing_types[0].id)
        
        # Добавляем недостающие типы
        new_types = [
            {"id": 2, "name": "Electronics"},
            {"id": 3, "name": "Other"},
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
