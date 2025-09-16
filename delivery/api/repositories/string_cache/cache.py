from aioredis.client import Redis
from aioredis.exceptions import RedisError
from loguru import logger

from .exceptions import (
    CacheGetValueError,
    CacheSetValueError,
)


class StringCache:
    def __init__(self, client: Redis):
        self.__client = client

    async def get(self, key: str) -> str | None:
        try:
            value = await self.__client.get(key)
            if value:
                logger.debug(f"cache hit, key: {key}, value: {value}")
                return value
            logger.debug(f"cache miss, key: {key}")
        except RedisError as e:
            raise CacheGetValueError("can not get value from cache") from e

    async def set(self, key: str, value: str, expire_in_seconds: int = None) -> None:
        try:
            await self.__client.set(key, value, ex=expire_in_seconds)
            logger.debug(f"cache set, key: {key}, value: {value}, ex: {expire_in_seconds}")
        except RedisError as e:
            raise CacheSetValueError("can not set value in cache") from e
