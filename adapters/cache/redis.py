"""
Адаптер для работы с Redis кешем.
Инфраструктурный слой - зависит от Redis.
"""
from redis import asyncio as aioredis
from core.settings import redis as redis_settings

redis = aioredis.from_url(redis_settings.url, encoding="utf-8", decode_responses=True)  
