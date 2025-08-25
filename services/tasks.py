import asyncio
from core.celery import celery
from loguru import logger

@celery.task(name="tasks.ping")
def ping(session_id: str) -> str:
    logger.bind(session_id=session_id, request_id="-").info("CELERY: ping started")
    asyncio.run(asyncio.sleep(0.5))
    return f"pong for session {session_id}"

