"""
Celery задачи - адаптеры для фоновой обработки.
Вызывают use-cases из application слоя.
"""
import asyncio
from loguru import logger
from decimal import Decimal

from adapters.messaging.celery_app import celery
from adapters.db.session import SyncSessionLocal
from core.usd import get_usd_rub_rate_sync
from adapters.db.models import Parcel
from sqlalchemy import select, update


@celery.task(name="tasks.ping")
def ping(session_id: str) -> str:
    """Тестовая задача ping."""
    logger.bind(session_id=session_id, request_id="-").info("CELERY: ping started")
    asyncio.run(asyncio.sleep(0.5))
    return f"pong for session {session_id}"


@celery.task
def update_delivery_prices():
    """
    Периодическая задача: рассчитать стоимость доставки для всех необработанных посылок.
    
    TODO: Переписать с использованием application use-cases вместо прямого обращения к БД.
    """
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
            # TODO: Вынести логику расчета в доменную сущность
            base_price = Decimal("100")  # базовая стоимость
            weight_price = Decimal(str(parcel.weight)) * Decimal("50")  # цена за вес
            value_price = Decimal(str(parcel.value_usd)) * Decimal(str(rate)) * Decimal("0.01")  # процент от стоимости
            
            price = base_price + weight_price + value_price
            
            db.execute(update(Parcel).where(Parcel.id == parcel.id).values(delivery_price_rub=float(price)))
            logger.info(f"Рассчитана стоимость доставки для посылки {parcel.id}: {price:.2f} руб.")
        
        db.commit()
        logger.info(f"Обновлены цены для {len(parcels)} посылок")
