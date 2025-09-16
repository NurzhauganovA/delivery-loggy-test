import json
import typing

import aiohttp.client_exceptions

from ... import schemas
from ...conf import conf
from .. import common


class OSMRemoteServiceRequestError(Exception):
    """Raises when remote geocoder (OSM) service cannot proceed with request."""


class OSMRemoteServiceResponseError(Exception):
    """Raises when remote geocoder (OSM) service returns response with `ERROR` status."""


class OSM(common.AsyncHTTPSession):
    def __init__(self):
        self.url = conf.osm.url
        super().__init__()

    async def direction(self, shipment_points: str):
        query = f"{self.url}route/v1/driving/{shipment_points}?overview=false&alternatives=true&steps=true"
        resp = await self._async_session.get(query)
        data = await resp.json()
        if not data or not data.get('waypoints', None):
            resp = await self._async_session.get(query)
            data = await resp.json()
            if not data:
                raise OSMRemoteServiceRequestError(
                    f'Cannot send message due to status code: {resp.status_code}',
                )

        if data and data.get('code', None) != "Ok":
            raise OSMRemoteServiceResponseError(
                'Cannot proceed response due to remote service '
                f'internal status code: {data["code"]}. '
                f'Message: {data}',
            )
        return data.get('waypoints')