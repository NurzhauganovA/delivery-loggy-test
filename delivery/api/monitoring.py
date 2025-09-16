import asyncio
import enum
import functools
import json
import typing

import aioredis
import cacheout

from .conf import conf
from . import redis_module
from . import schemas


_service = None
_cache = cacheout.Cache()


class MonitoringServiceUninitialized(Exception):
    """Raises if Monitor service was not initialized."""


class MonitoringSubscriptionsDoNotExist(Exception):
    """Raises if there was no any subscriptions during an attempt to read messages."""


class ChannelType(str, enum.Enum):
    ORDER = 'order'
    COURIER = 'courier'


class Monitor:
    @functools.cached_property
    def _connection(self) -> aioredis.client.Redis:
        return redis_module.get_connection()

    @functools.cached_property
    def _subscription(self) -> aioredis.client.PubSub:
        return self._connection.pubsub()

    def _build_channel(self, channel_type: ChannelType, channel_id: int) -> str:
        return f'{channel_type}:{channel_id}'

    async def _receive_record(self) -> typing.Optional[dict]:
        return await self._subscription.get_message(ignore_subscribe_messages=True)

    async def close(self) -> None:
        await self._subscription.unsubscribe()
        await self._subscription.close()


class CourierMonitor(Monitor):
    def __init__(self):
        self._latest_courier_id = None
        self._lock = asyncio.Lock()

    def _filter_couriers(self, couriers: list) -> list:
        ids_to_objects = {}

        for courier in couriers:
            _id = courier['id']
            if _id not in ids_to_objects:
                ids_to_objects[_id] = courier
            else:
                if courier['ts'] > ids_to_objects[_id]['ts']:
                    ids_to_objects[_id] = courier

        try:
            return list(ids_to_objects.values())
        finally:
            couriers.clear()

    @_cache.memoize(ttl=conf.monitoring.ttl)
    async def _retrieve_filtered_couriers(self) -> list:
        """All published couriers must be filtered by `city_id` and cached at first request."""
        couriers = []

        while True:
            record = await self._receive_record()
            if isinstance(record, dict):
                if record['type'] == 'message':
                    courier = json.loads(record['data'])
                    couriers.append(courier)

                    if courier['id'] == self._latest_courier_id:
                        break

        return self._filter_couriers(couriers)

    async def get_couriers(self, city_id: int) -> list:
        """Get and return a list of couriers related to the city."""
        couriers = []
        # Prior to caching we need to make sure
        # at least 1 courier has sent metadata.
        try:
            filtered = await asyncio.wait_for(
                self._retrieve_filtered_couriers(),
                timeout=conf.monitoring.timeout,
            )
        except RuntimeError as e:
            raise MonitoringSubscriptionsDoNotExist(
                'Currently there is no existing subscriptions yet',
            ) from e

        for courier in filtered:
            if courier['city_id'] == city_id:
                couriers.append(courier)

        return couriers

    async def add_courier(self, courier: schemas.MonitoringCourierAdd) -> None:
        courier_id = courier.id

        channel = self._build_channel(ChannelType.COURIER, courier_id)
        if channel not in self._subscription.channels:
            await self._subscription.subscribe(channel)

        serialized_courier = json.dumps(courier.dict())
        await self._connection.publish(channel, serialized_courier)

        async with self._lock:
            self._latest_courier_id = courier_id


class Monitoring:
    def __init__(self) -> None:
        self._courier_monitor = CourierMonitor()

    async def terminate(self) -> None:
        await self._courier_monitor.close()

    async def add_courier(self, courier: schemas.MonitoringCourierAdd) -> None:
        await self._courier_monitor.add_courier(courier)

    async def get_couriers(self, city_id: int) -> list:
        return await self._courier_monitor.get_couriers(city_id)


def initialize() -> None:
    global _service

    if _service is not None:
        return

    _service = Monitoring()


async def shutdown() -> None:
    global _service

    if _service is None:
        return

    await _service.terminate()

    _service = None


def get_service() -> Monitoring:
    if _service is None:
        raise MonitoringServiceUninitialized('Monitor service must be initialized first')

    return _service
