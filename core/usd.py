import httpx
from core.cache import redis

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
