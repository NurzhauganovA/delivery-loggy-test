import asyncio

import aiohttp

from .. import exceptions
from .. import models
from .. import schemas
from .. import enums
from ..services import geocoder


async def place_get_list() -> list:
    return await models.place_get_list()


async def place_get(place_id: int, **kwargs) -> dict:
    try:
        profile = kwargs.pop('current_user').profile
        if profile['profile_type'] == enums.ProfileType.BRANCH_MANAGER:
            cities = [city.id for city in profile['profile_content']['cities']]
            kwargs['city_id__in'] = cities
        return await models.place_get(place_id, **kwargs)
    except models.PlaceNotFound as e:
        raise exceptions.HTTPNotFoundException(str(e)) from e


async def place_create(place: schemas.PlaceCreate, **kwargs):
    profile = kwargs.pop('current_user').profile
    if profile['profile_type'] == enums.ProfileType.BRANCH_MANAGER:
        if profile['profile_content']['city_id'] != place.city_id:
            raise exceptions.HTTPBadRequestException(
                f'City with given ID: {place.city_id} in request is not available',
            )
    return await models.place_create(place)


async def place_update(place_id: int, place: schemas.PlaceUpdate, **kwargs) -> dict:
    try:
        profile = kwargs.pop('current_user').profile
        if profile['profile_type'] == enums.ProfileType.BRANCH_MANAGER:
            if profile['profile_content']['city_id'] != place.city_id:
                raise exceptions.HTTPBadRequestException(
                    'Place with given ID in request is not available',
                )
            kwargs['city_id'] = profile['profile_content']['city_id']
        return await models.place_update(place_id, place, **kwargs)
    except (
            geocoder.GeocoderRemoteServiceResponseError,
            models.EntityDoesNotExist,
    ) as e:
        raise exceptions.HTTPBadRequestException(str(e)) from e
    except (
            asyncio.TimeoutError,
            aiohttp.ClientConnectorError,
            geocoder.GeocoderRemoteServiceRequestError,
    ) as e:
        raise exceptions.HTTPTemporarilyUnavailableException(str(e)) from e
    except models.PlaceNotFound as e:
        raise exceptions.HTTPNotFoundException(str(e)) from e


async def place_delete(place_id: int, **kwargs) -> None:
    try:
        profile = kwargs.pop('current_user').profile
        if profile['profile_type'] == enums.ProfileType.BRANCH_MANAGER:
            kwargs['city_id'] = profile['profile_content']['city_id']
        await models.place_delete(place_id, **kwargs)
    except models.PlaceNotFound as e:
        raise exceptions.HTTPNotFoundException(str(e)) from e
