import json
from json import dumps

import aiohttp
import loguru as loguru

from .. import common
from ..common import AsyncHTTPSession
from ...conf import conf
from ... import schemas, enums, models
from aiohttp import ClientSession

class DistributionServiceError(Exception):
    ...


class DistributionService(AsyncHTTPSession):

    def __init__(self, headers=None):
        if not headers:
            headers = {
                'Content-Type': 'application/json',
                'accept': 'application/json'
            }
        super().__init__(headers=headers)

    async def distribute(self, data):
        timeout = aiohttp.ClientTimeout(total=20)

        resp = await self._async_session.post(
            url='http://algorythm-service-api:5000/api/v1/distribute/simple',
            data=json.dumps(data), timeout=timeout
        )

        resp_dict = await resp.json()
        loguru.logger.debug(resp_dict)
        await self.close()
        return resp_dict

    async def catch_errors(self, resp: dict):
        # TODO: delete device tokens if any error occurred.
        pass


async def couriers_prepare(couriers):
    result = []
    for courier in couriers:
        result.append(
            {
                "external_courier_id": courier.id,
                "speed": 30,
                "travel_distance_limit": 100000,
                "start_of_the_work_day": courier.start_work_hour,
                "end_of_the_work_day": courier.end_work_hour,
                "capacity": 10
            }
        )

async def orders_prepare(orders):
    result = []
    for order in orders:
        place = {}
        for address in await models.order_address_get_list(order.id):
            address = address.dict()
            if address['type'] == enums.AddressType.SHIPMENT_POINT:
                place = {
                    "address": address['place']['address'],
                    "latitude": address['place']['latitude'],
                    "longitude": address['place']['longitude']
                }

        if place:
            result.append(
                {
                    "id": order.id,
                    "delivery_datetime": order.delivery_datetime,
                    "place": place
                }
            )

async def get_stock_place_prepare():
    return {
        "address": "Жибек Жолы 135",
        "latitude": 43.26130,
        "longitude": 76.92920
    }