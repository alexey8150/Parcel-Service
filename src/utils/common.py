import json
import aiohttp
from contextlib import asynccontextmanager
from datetime import datetime, timedelta
from aioredis import StrictRedis
from src.config import REDIS_HOST, REDIS_PORT
from functools import wraps
from aiocache import Cache
from fastapi import HTTPException


@asynccontextmanager
async def get_redis():
    redis_client = await StrictRedis(host=REDIS_HOST, port=REDIS_PORT)
    try:
        yield redis_client
    finally:
        await redis_client.close()


async def get_usd_rate() -> float:
    async with get_redis() as redis:
        usd_rate = await redis.get("usd_rate")
        if usd_rate is None:
            async with aiohttp.ClientSession() as session:
                async with session.get('https://www.cbr-xml-daily.ru/daily_json.js') as result:
                    if result.status == 200:
                        data = await result.json(content_type=None)
                        usd_rate = data["Valute"]["USD"]["Value"]
                        ttl = get_ttl(data)
                        await redis.set("usd_rate", usd_rate, ex=ttl)
                    else:
                        raise Exception(f"Can't to get new USD rate, response status_code={result.status}")

        return float(usd_rate)


def get_ttl(data: dict) -> int:
    expiration_time = datetime.fromisoformat(data['Timestamp']) + timedelta(days=1)
    current_time = datetime.now().astimezone()
    ttl = int((expiration_time - current_time).total_seconds())
    if ttl < 0:
        ttl = 3600
    return ttl


def cache_response(ttl: int = 60, namespace: str = "main"):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            package_id = kwargs.get('package_id')

            if not package_id and args:
                package_id = args[0]

            cache_key = f"{namespace}:package:{package_id}" if package_id else f"{namespace}:package"

            cache = Cache.REDIS(endpoint=REDIS_HOST, port=REDIS_PORT, namespace=namespace)
            cached_value = await cache.get(cache_key)
            if cached_value:
                return json.loads(cached_value)

            response = await func(*args, **kwargs)

            try:
                await cache.set(cache_key, json.dumps(response), ttl=ttl)
            except Exception as e:
                raise HTTPException(status_code=500, detail=f"Error caching data: {e}")

            return response

        return wrapper

    return decorator
