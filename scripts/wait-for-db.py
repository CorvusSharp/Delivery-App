#!/usr/bin/env python3
"""
Простой скрипт ожидания доступности базы данных.
"""
import time
import sys
from typing import Optional
from sqlalchemy.exc import OperationalError
from sqlalchemy import text
from adapters.db.session import sync_engine
from loguru import logger


def wait_for_db(timeout: int = 60, interval: float = 1.0) -> bool:
    """
    Ожидает доступности базы данных.
    
    Returns:
        True если БД доступна в течение timeout, False иначе.
    """
    deadline = time.time() + timeout
    last_exc: Optional[Exception] = None
    
    logger.info("Ожидание доступности базы данных...")
    
    while time.time() < deadline:
        try:
            with sync_engine.connect() as conn:
                # Простая проверка подключения
                conn.execute(text("SELECT 1"))
                logger.info("База данных доступна!")
                return True
        except OperationalError as e:
            last_exc = e
            logger.debug(f"БД не готова, повтор через {interval} сек...")
            time.sleep(interval)
        except Exception as e:
            last_exc = e
            logger.warning(f"Неожиданная ошибка: {e}")
            time.sleep(interval)
    
    logger.error(f"Не удалось подключиться к базе данных за {timeout} сек: {last_exc}")
    return False


if __name__ == "__main__":
    timeout = int(sys.argv[1]) if len(sys.argv) > 1 else 60
    
    if not wait_for_db(timeout=timeout):
        sys.exit(1)
    
    logger.info("База данных готова к работе!")
