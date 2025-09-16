import asyncio
import typing

import aiohttp.client_exceptions

from .. import exceptions
from .. import models
from .. import schemas
from .. import services
from .. import verification


async def call_wrapper(call: typing.Callable, *args) -> dict:
    try:
        return await call(*args)
    except (
            asyncio.TimeoutError,
            verification.VerificationResourceNotAvailable,
            aiohttp.client_exceptions.ContentTypeError,
    ) as e:
        raise exceptions.HTTPTemporarilyUnavailableException(str(e)) from e
    except (
            verification.VerificationEntityNotFound,
            models.UserNotFound,
    ) as e:
        raise exceptions.HTTPNotFoundException(str(e)) from e
    except (
            services.dataloader.DataloaderRemoteServiceRequestError,
            services.dataloader.DataloaderRemoteServiceResponseError,
    ) as e:
        raise exceptions.HTTPBadRequestException(str(e)) from e
    except services.dataloader.DataloaderDontConfigured as e:
        raise exceptions.HTTPNotImplemented(str(e)) from e


async def verify_user(user: schemas.VerificationUser) -> dict:
    return await call_wrapper(verification.client.verify_user, user)


async def verify_partner(partner: schemas.VerificationPartner) -> dict:
    return await call_wrapper(verification.client.verify_partner, partner)


async def verify_courier(courier: schemas.VerificationCourier) -> dict:
    return await call_wrapper(verification.client.verify_courier, courier)
