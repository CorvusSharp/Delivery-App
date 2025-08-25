from redis import asyncio as aioredis
from core.settings import settings

redis = aioredis.from_url(settings.redis.url, encoding="utf-8", decode_responses=True)
