import typing
from datetime import datetime

import aiohttp.client_exceptions
from loguru import logger

from ...conf import conf
from ... import schemas
from .. import common


class GeocoderRemoteServiceRequestError(Exception):
    """Raises when remote geocoder (2gis) service cannot proceed with request."""


class GeocoderRemoteServiceResponseError(Exception):
    """Raises when remote geocoder (2gis) service returns response with `ERROR` status."""


class Geocoder(common.AsyncHTTPSession):
    async def to_string_address(self, coordinates: schemas.Coordinates) -> str:
        pass

    def to_coordinates(self, address: str) -> schemas.Coordinates:
        pass


class Geocoder2GIS(Geocoder):
    def __init__(self):
        self.url = conf.geocoder.url_2gis + '3.0/items/geocode'
        self.key = conf.geocoder.key_2gis
        super().__init__()

    async def to_string_address(self, coordinates: schemas.Coordinates) -> str:
        # TODO: Implement when needed
        pass

    async def to_coordinates(self, address: str) -> schemas.Coordinates:
        query = f"{self.url}?q={address}&fields=items.point&key={self.key}"
        resp = await self._async_session.get(query)
        data = await resp.json()
        if not data:
            resp = await self._async_session.get(query)
            data = await resp.json()
            if not data:
                raise GeocoderRemoteServiceRequestError(
                    f'Cannot send message due to status code: {resp.status_code}',
                )

        if data.get('meta').get('error'):
            raise GeocoderRemoteServiceResponseError(
                'Cannot proceed response due to remote service '
                f'internal status code: {data["meta"]["code"]}. '
                f'Message: {data["meta"]["error"]["message"]}',
            )
        coordinates = data['result']['items'][0]['point']
        return schemas.Coordinates(
            latitude=coordinates['lat'],
            longitude=coordinates['lon']
        )

    async def distance_matrix(self, data):
        query = f"{conf.geocoder.url}get_dist_matrix?key={self.key}&version=2.0"
        resp = await self._async_session.post(url=query, json=data)
        try:
            data = await resp.json()
        except aiohttp.client_exceptions.ContentTypeError:
            raise GeocoderRemoteServiceResponseError(
                'Cannot proceed response due to remote service '
                f'Status code: {resp.status}',
            )

        if not data:
            resp = await self._async_session.post(url=query, json=data)
            data = await resp.json()
            if not data:
                raise GeocoderRemoteServiceRequestError(
                    f'Cannot get distance matrix due to status code: {resp.status_code}',
                )

        return data.get('routes')


class GeocoderOSM(Geocoder):
    def __init__(self):
        self.url = conf.geocoder.url_osm
        super().__init__()

    async def to_coordinates(self, address: str) -> schemas.Coordinates:

        query = f'{self.url}?q={address}&format=json'
        resp = await self._async_session.get(query)
        data = await resp.json()

        if not data:
            resp = await self._async_session.get(query)
            data = await resp.json()
            if not data:
                raise GeocoderRemoteServiceRequestError(
                    f'Cannot send message due to status code: {resp}'
                    f'or place cannot be found',
                )
        if isinstance(data, dict) and data.get('error'):
            error = data.get('error')
            raise GeocoderRemoteServiceResponseError(
                'Cannot proceed response due to remote service '
                f'internal status code: {error["code"]}. '
                f'Message: {error["message"]}',
            )

        data = data[0]
        return schemas.Coordinates(
            latitude=f"{data['lat']:.10}",
            longitude=f"{data['lon']:.11}"
        )
