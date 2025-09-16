import typing

import aioredis


_connection: typing.Union[aioredis.client.Redis, None] = None


class RedisConnectionDoesNotExist(Exception):
    """Raises if Redis connection was not instantiated."""


async def connect(uri: str) -> typing.Optional[aioredis.client.Redis]:
    global _connection

    if _connection is not None:
        return

    _connection = await aioredis.from_url(url=uri, decode_responses=True)
    return _connection


async def disconnect() -> None:
    global _connection

    if _connection is None:
        return

    await _connection.close()

    _connection = None


def get_connection() -> aioredis.client.Redis:
    if _connection is None:
        raise RedisConnectionDoesNotExist('Redis connection pool was not instantiated')

    return _connection
