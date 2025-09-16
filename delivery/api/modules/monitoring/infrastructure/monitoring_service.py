import json

from api.services.common import RedisService


class MonitoringService(RedisService):
    def _get_key(self, city_id: int, courier_id: int) -> str:
        return f'locations_{city_id}_{courier_id}'

    def _get_key_pattern(self, city_id: int) -> str:
        return f'locations_{city_id}_*'

    async def update_courier_location(self, courier_service_id, courier_id, location):
        await self._put_to_redis(key=self._get_key(courier_service_id, courier_id),
                                 value=json.dumps(
                                         {
                                             'courier_id': courier_id,
                                             'location': location,
                                             'is_active': True
                                          }
                                     )
                                 )

    async def get_locations(self, city_id):
        pattern = self._get_key_pattern(city_id)
        return await self._get_many_from_redis(await self._get_keys(pattern))

    async def get_location(self, city_id, courier_id):
        pattern = self._get_key(city_id, courier_id)
        return await self._get_from_redis_by_key(pattern)