import asyncio
import time
from typing import Optional

from adapters.db.session import init_db, sync_engine, SyncSessionLocal
from loguru import logger
from sqlalchemy.exc import OperationalError
from sqlalchemy import select


def init_parcel_types():
    """Инициализация типов посылок, если они не существуют."""
    session = SyncSessionLocal()
    try:
        from adapters.db.models import ParcelType
        
        # Проверяем, есть ли уже типы в базе
        result = session.execute(select(ParcelType))
        existing_types = result.scalars().all()
        
        if existing_types:
            logger.info("Типы посылок уже существуют в базе данных")
            return
        
        # Создаем типы посылок (английские названия как канон)
        parcel_types = [
            ParcelType(id=1, name="Clothing"),
            ParcelType(id=2, name="Electronics"),
            ParcelType(id=3, name="Other"),
        ]
        
        session.add_all(parcel_types)
        session.commit()
        
        logger.info("Созданы типы посылок:")
        for ptype in parcel_types:
            logger.info("  ID: {}, Название: {}", ptype.id, ptype.name)
            
    except Exception as e:
        logger.error("Ошибка при инициализации типов посылок: {}", str(e))
        session.rollback()
    finally:
        session.close()


def wait_for_db(timeout: int = 60, interval: float = 1.0) -> bool:
    """Wait until the database accepts connections or timeout.

    Returns True if DB is reachable within timeout, False otherwise.
    """
    deadline = time.time() + timeout
    last_exc: Optional[Exception] = None
    while time.time() < deadline:
        try:
            # Use sync_engine to attempt a simple connection
            with sync_engine.connect() as conn:  # type: ignore
                return True
        except OperationalError as e:
            last_exc = e
            logger.info("Ожидание базы данных... повтор через %s сек", interval)
            time.sleep(interval)
        except Exception as e:  # pragma: no cover - defensive
            last_exc = e
            logger.info("Ожидание базы данных: ошибка %s", e)
            time.sleep(interval)
    logger.error("Не удалось подключиться к базе данных: %s", last_exc)
    return False


if __name__ == "__main__":
    logger.info("Ожидание доступности базы данных...")
    ok = wait_for_db(timeout=60, interval=1.0)
    if not ok:
        raise SystemExit("Database is not available, aborting init")
    
    # Импорт моделей здесь гарантирует, что они зарегистрированы в Base.metadata
    # до вызова create_all()
    import adapters.db.models  # noqa: F401
    
    logger.info("Создание таблиц в базе данных...")
    asyncio.run(init_db())
    logger.info("Таблицы созданы успешно")
    
    logger.info("Инициализация базовых данных...")
    init_parcel_types()
    logger.info("Инициализация базы данных завершена успешно")
