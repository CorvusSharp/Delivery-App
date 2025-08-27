import httpx
import redis as sync_redis
from adapters.cache.redis import redis
from core.settings import redis as redis_settings

CBR_URL = "https://www.cbr-xml-daily.ru/daily_json.js"

async def get_usd_rub_rate() -> float:
    rate = await redis.get("usd_rub_rate")
    if rate:
        return float(rate)
    async with httpx.AsyncClient() as client:
        resp = await client.get(CBR_URL)
        data = resp.json()
        rate = data["Valute"]["USD"]["Value"]
        await redis.set("usd_rub_rate", rate, ex=300)
        return float(rate)

def get_usd_rub_rate_sync() -> float:
    """Синхронная версия для использования в Celery задачах."""
    try:
        # Создаем синхронное подключение к Redis
        sync_redis_client = sync_redis.from_url(redis_settings.url)
        
        rate = sync_redis_client.get("usd_rub_rate")
        if rate:
            rate_str = rate.decode('utf-8') if isinstance(rate, bytes) else str(rate)
            return float(rate_str)
        
        # Получаем курс с сайта ЦБР
        with httpx.Client() as client:
            resp = client.get(CBR_URL)
            data = resp.json()
            rate = data["Valute"]["USD"]["Value"]
            sync_redis_client.set("usd_rub_rate", rate, ex=300)
            return float(rate)
    except Exception:
        # Если что-то пошло не так, возвращаем фиксированный курс
        return 90.0
