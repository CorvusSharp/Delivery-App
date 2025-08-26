from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from core.db import init_db, get_db
from domain.models import ParcelType

router = APIRouter(prefix="/admin", tags=["Admin"])

@router.post("/init-db")
async def admin_init_db():
    await init_db()
    return {"detail": "Таблицы созданы"}

@router.post("/init-data")
async def admin_init_data(db: AsyncSession = Depends(get_db)):
    """Инициализация начальных данных (типы посылок)."""
    # Проверяем, есть ли уже типы посылок
    existing_types = await db.execute(text("SELECT COUNT(*) FROM parcel_types"))
    count = existing_types.scalar()
    
    if count == 0:
        # Добавляем три канонических типа посылок (english canonical names)
        types = [
            ParcelType(id=1, name="Clothing"),
            ParcelType(id=2, name="Electronics"),
            ParcelType(id=3, name="Other"),
        ]

        for parcel_type in types:
            db.add(parcel_type)

        await db.commit()
        return {"detail": f"Добавлено {len(types)} типов посылок"}
    else:
        return {"detail": f"Типы посылок уже существуют ({count} записей)"}
