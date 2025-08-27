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
    Использует доменную логику для расчета цен.
    """
    from decimal import Decimal
    from domain.entities.parcel import Parcel as ParcelDomain, ParcelType as ParcelTypeDomain
    
    # Используем синхронную сессию для Celery задач
    with SyncSessionLocal() as db:
        # Получить посылки без delivery_price_rub
        result = db.execute(
            select(Parcel).where(Parcel.delivery_price_rub.is_(None)).limit(100)
        )
        parcels = result.scalars().all()
        
        if not parcels:
            logger.info("Нет посылок для расчёта стоимости доставки.")
            return
        
        # Получаем курс валют синхронно
        rate = Decimal(str(get_usd_rub_rate_sync()))
        logger.info(f"Обновление цен для {len(parcels)} посылок с курсом USD: {rate}")
        
        for parcel_model in parcels:
            try:
                # Загружаем тип посылки отдельным запросом
                from adapters.db.models import ParcelType as ParcelTypeModel
                parcel_type_model = db.execute(
                    select(ParcelTypeModel).where(ParcelTypeModel.id == parcel_model.type_id)
                ).scalar_one()
                
                # Создаем доменные сущности с правильным доступом к атрибутам
                parcel_type = ParcelTypeDomain(
                    id=int(parcel_type_model.id),
                    name=str(parcel_type_model.name)
                )
                
                parcel_domain = ParcelDomain(
                    id=int(parcel_model.id),
                    name=str(parcel_model.name),
                    weight=Decimal(str(parcel_model.weight)),
                    type=parcel_type,
                    value_usd=Decimal(str(parcel_model.value_usd)),
                    delivery_price_rub=None,
                    session_id=str(parcel_model.session_id)
                )
                
                # Используем доменную логику для расчета цены
                price = parcel_domain.calculate_delivery_price(rate)
                
                # Обновляем в БД
                db.execute(
                    update(Parcel).where(Parcel.id == parcel_model.id)
                    .values(delivery_price_rub=float(price))
                )
                
                logger.info(f"Обновлена цена для посылки {parcel_model.id}: {price}")
                
            except Exception as e:
                logger.error(f"Ошибка обновления цены для посылки {parcel_model.id}: {e}")
                continue
        
        db.commit()
        logger.info(f"Обновлены цены для {len(parcels)} посылок")
