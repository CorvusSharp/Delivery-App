from core.celery import celery
from core.db import SyncSessionLocal
from core.usd import get_usd_rub_rate_sync
from domain.models import Parcel
from sqlalchemy import select, update
from loguru import logger

@celery.task
def update_delivery_prices():
    """Периодическая задача: рассчитать стоимость доставки для всех необработанных посылок."""
    
    # Используем синхронную сессию для Celery задач
    with SyncSessionLocal() as db:
        # Получить все посылки без delivery_price_rub
        parcels = db.execute(select(Parcel).where(Parcel.delivery_price_rub.is_(None))).scalars().all()
        if not parcels:
            logger.info("Нет посылок для расчёта стоимости доставки.")
            return
        
        # Получаем курс валют синхронно
        rate = get_usd_rub_rate_sync()
        
        for parcel in parcels:
            price = (parcel.weight * 0.5 + parcel.value_usd * 0.01) * rate
            db.execute(update(Parcel).where(Parcel.id == parcel.id).values(delivery_price_rub=price))
            logger.info(f"Рассчитана стоимость доставки для посылки {parcel.id}: {price:.2f} руб.")
        
        db.commit()
        logger.info(f"Обновлены цены для {len(parcels)} посылок")
