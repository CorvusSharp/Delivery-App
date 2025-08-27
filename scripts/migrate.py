#!/usr/bin/env python3
"""
Скрипт для запуска миграций Alembic.
"""
import subprocess
import sys
from loguru import logger


def run_migrations() -> bool:
    """
    Запускает миграции Alembic.
    
    Returns:
        True если миграции прошли успешно, False иначе.
    """
    try:
        logger.info("Запуск миграций Alembic...")
        
        result = subprocess.run([
            sys.executable, "-m", "alembic", "upgrade", "head"
        ], check=True, capture_output=True, text=True)
        
        logger.info("Миграции выполнены успешно")
        if result.stdout:
            logger.info(f"Вывод Alembic: {result.stdout}")
        
        return True
        
    except subprocess.CalledProcessError as e:
        logger.error(f"Ошибка выполнения миграций: {e}")
        if e.stderr:
            logger.error(f"Stderr: {e.stderr}")
        if e.stdout:
            logger.error(f"Stdout: {e.stdout}")
        return False
    except Exception as e:
        logger.error(f"Неожиданная ошибка при миграции: {e}")
        return False


if __name__ == "__main__":
    if not run_migrations():
        sys.exit(1)
    
    logger.info("Миграции завершены успешно!")
