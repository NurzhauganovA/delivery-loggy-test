import pytest
from aioredis.exceptions import RedisError

from api.repositories.string_cache import (
    CacheGetValueError,
    CacheSetValueError,
)


@pytest.mark.asyncio
async def test_get(cache, mock_redis):
    mock_redis.get.return_value = "value"
    result = await cache.get("key")
    assert result == "value"
    mock_redis.get.assert_awaited_once_with("key")


@pytest.mark.asyncio
async def test_get_none(cache, mock_redis):
    mock_redis.get.return_value = None
    result = await cache.get("key")
    assert result is None


@pytest.mark.asyncio
async def test_get_raises_on_redis_error(cache, mock_redis):
    mock_redis.get.side_effect = RedisError("redis down")
    with pytest.raises(CacheGetValueError, match="can not get value from cache"):
        await cache.get("key")


@pytest.mark.asyncio
async def test_set(cache, mock_redis):
    await cache.set("key", "value", expire_in_seconds=300)
    mock_redis.set.assert_awaited_once_with("key", "value", ex=300)


@pytest.mark.asyncio
async def test_set_raises_on_redis_error(cache, mock_redis):
    mock_redis.set.side_effect = RedisError("fail")
    with pytest.raises(CacheSetValueError, match="can not set value in cache"):
        await cache.set("key", "value")
