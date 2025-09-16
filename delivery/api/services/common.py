import functools
import json
import typing
import uuid
from json import JSONDecodeError
import loguru
import abc
from typing import Any
from typing import Optional

import aiohttp
import aiohttp.client_exceptions
import aioredis
from aiohttp.typedefs import StrOrURL

from .. import redis_module, schemas
from .. import models
from ..enums import ExternalServices


class AsyncSessionWithInitiator(aiohttp.ClientSession):

    # use this method instead of native post().
    async def recorded_post(
        self, url: StrOrURL, *, data: Any = None, initiator: int | None = None,
        max_retries: int = 2, **kwargs: Any
    ):
        """Perform HTTP POST request and record it to db."""
        retry_count = 0
        response = {}
        while retry_count < max_retries:
            try:
                retry_count += 1
                response = await self.post(url, data=data, ssl=False, **kwargs)
            except (
                aiohttp.client_exceptions.ClientError,
                aiohttp.client_exceptions.ClientConnectorError,
            ) as e:
                loguru.logger.debug(str(e))
                if retry_count < max_retries:
                    await self.record_to_db(url, data, response, initiator)
                    continue
                raise e
            else:
                break
            finally:
                await self.record_to_db(url, data, response, initiator)
        return response

    # use this method instead of native get().
    async def recorded_get(self, url, *, initiator: int | None = None,
                           max_retries: int = 2, allow_redirects: bool = True, **kwargs):
        retry_count = 0
        response = {}
        while retry_count < max_retries:
            try:
                retry_count += 1
                response = await self.get(
                    url, allow_redirects=allow_redirects,
                    ssl=False,
                    **kwargs
                )
            except (
                aiohttp.client_exceptions.ClientError,
                aiohttp.client_exceptions.ClientConnectorError,
            ) as e:
                if retry_count != max_retries:
                    continue
                raise e

            else:
                break
            finally:
                params = str(url).split('?')[-1]
                if '=' in params:
                    params = params.split('&', 2)
                    data = {key: value for key, value in
                            [param.split('=', 2) for param in params]}
                else:
                    data = {}
                await self.record_to_db(url, data, response, initiator)

        return response

    @staticmethod
    async def record_to_db(url: StrOrURL, data, response, initiator):
        if not response:
            response_body = {}
            response_status = 0
        else:
            response_status = response.status
            try:
                response_body = await response.json()
            except JSONDecodeError:
                response_body = {'data': await response.content.read()}

        if response_status not in (200, 201, 202, 204):
            loguru.logger.debug(str(response_body))

        external_service_schema = schemas.ExternalServiceHistoryCreate(
            id=uuid.uuid4(),
            service_name=ExternalServices(url.split('/')[-1]),
            url=str(url),
            request_body=data,
            response_body=response_body,
            status_code=response_status,
            owner_id=initiator,
        )

        await models.external_service_history_create(external_service_schema)


class AsyncHTTPSession:
    _session = None

    def __init__(self, headers=None):
        if headers is None:
            headers = {'Content-Type': 'application/json'}
        self.headers = headers

    @functools.cached_property
    def _async_session(self) -> AsyncSessionWithInitiator:
        if self._session is None:
            self._session = AsyncSessionWithInitiator(
                headers=self.headers,
            )
        return self._session

    async def close(self) -> None:
        if self._async_session is not None:
            await self._async_session.close()
            self._async_session = None


class RedisService:
    def __init__(self, ttl: int = 60 * 60 * 24):
        self.ttl = ttl

    @functools.cached_property
    def _redis(self) -> aioredis.client.Redis:
        return redis_module.get_connection()

    async def _put_to_redis(self, key: str, value: str, ttl: int = None) -> None:
        # Redis tries to cast input type to str implicitly
        await self._redis.set(key, value, ex=ttl or self.ttl)

    async def _get_from_redis(self, phone_number: str) -> Optional[str]:
        return await self._redis.get(phone_number)

    async def _get_keys(self, pattern: str):
        return await self._redis.keys(pattern)

    async def _get_many_from_redis(self, keys: typing.Sequence[str]):
        encoded_result = []
        result = await self._redis.mget(keys)
        for res in result:
            encoded_result.append(json.loads(res))
        return encoded_result

    async def _get_from_redis_by_key(self, pattern: str):
        return await self._redis.get(pattern)

    async def keys_matched(self, pattern: str) -> list:
        return await self._get_keys(pattern)

    async def set(self, key, value, ttl=None):
        await self._redis.set(
            key, value, ex=ttl or self.ttl
        )

    async def get(self, key) -> typing.Union[int | str]:
        return await self._redis.get(key)

    async def exists(self, key) -> int:
        return await self._redis.exists(key)

    async def delete(self, *keys) -> int:
        return await self._redis.delete(*keys)


class BaseNotificationService(AsyncHTTPSession, abc.ABC):
    def __init__(self, headers: dict = None) -> None:
        super().__init__(headers)

    @abc.abstractmethod
    def send_message(
        self, requisites: str,
        message: str, current_user: schemas.UserCurrent = None,
        subject: str = None
    ) -> None:
        ...
