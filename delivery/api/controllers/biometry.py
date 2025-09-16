import asyncio

import aiohttp

from ..conf import conf
from .. import exceptions
from .. import models
from .. import schemas
from .. import services


async def profile_biometry_verify(
        user_id: int, request_body: schemas.BiometryVerifyBody,
) -> dict:
    try:
        await models.profile_biometry_verify(user_id, request_body)
    except models.ProfileNotFound as e:
        raise exceptions.HTTPNotFoundException(str(e)) from e


async def get_biometry_url(biometry_request: schemas.BiometryRequest) -> dict:
    try:
        data = await asyncio.wait_for(
            services.biometry.service.get_biometry_url(biometry_request),
            timeout=conf.biometry.timeout,
        )
        return schemas.BiometryResponse(**data)
    except services.biometry.BiometryRemoteServiceResponseError as e:
        raise exceptions.HTTPBadRequestException(str(e)) from e
    except (
            asyncio.TimeoutError,
            aiohttp.ClientConnectorError,
            services.biometry.BiometryRemoteServiceRequestError,
    ) as e:
        raise exceptions.HTTPTemporarilyUnavailableException(str(e)) from e
