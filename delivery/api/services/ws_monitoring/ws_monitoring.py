# TODO: it needs to be refactor


import json

from fastapi.encoders import jsonable_encoder

from .. import common


class MonitoringService(common.RedisService):
    def _get_key(self, courier_service_id: int, courier_id: int) -> str:
        return f'locations_{courier_service_id}_{courier_id}'

    def _get_key_pattern(self, courier_service_id: int) -> str:
        return f'locations_{courier_service_id}_*'

    async def update_courier_location(self, courier_service_id, courier_id, location):
        await self._put_to_redis(key=self._get_key(courier_service_id, courier_id),
                                 value=json.dumps(
                                         jsonable_encoder({
                                             'courier_id': courier_id,
                                             'location': location,
                                             'is_active': True
                                          })
                                     )
                                 )

    async def get_locations(self, courier_service_id):
        pattern = self._get_key_pattern(courier_service_id)
        result = await self._get_many_from_redis(await self._get_keys(pattern))
        return result

    async def get_location(self, city_id, courier_id):
        pattern = self._get_key(city_id, courier_id)
        return await self._get_from_redis_by_key(pattern)
