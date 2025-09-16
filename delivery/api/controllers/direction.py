import asyncio
import typing

import aiohttp

from .. import exceptions
from .. import enums
from .. import models
from ..services import osm


async def direction_get(**kwargs) -> typing.List[dict]:
    try:
        profile = kwargs.pop('current_user').profile
        if profile.get('profile_type') == enums.ProfileType.COURIER:
            kwargs['courier_id'] = profile['id']
            return await models.direction_get(**kwargs)

    except models.OrderNotFound as e:
        raise exceptions.HTTPBadRequestException(str(e)) from e
    except osm.OSMRemoteServiceResponseError as e:
        raise exceptions.HTTPBadRequestException(str(e)) from e
    except (
            asyncio.TimeoutError,
            aiohttp.ClientConnectorError,
            osm.OSMRemoteServiceRequestError,
    ) as e:
        raise exceptions.HTTPTemporarilyUnavailableException(str(e)) from e
    raise exceptions.HTTPBadRequestException('You are not courier!')