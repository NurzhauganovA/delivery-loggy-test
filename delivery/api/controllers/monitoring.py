import asyncio

from .. import exceptions
from .. import monitoring
from .. import schemas
from .. import models


async def monitoring_get_couriers(city_id: int) -> list:
    try:
        # TODO: set timeout and add 201 on success
        return await monitoring.get_service().get_couriers(city_id)
    except (
            asyncio.exceptions.TimeoutError,
            monitoring.MonitoringServiceUninitialized,
    ) as e:
        raise exceptions.HTTPTemporarilyUnavailableException() from e
    except monitoring.MonitoringSubscriptionsDoNotExist as e:
        raise exceptions.HTTPNotFoundException(str(e)) from e


async def monitoring_add_courier(
        courier: schemas.MonitoringCourierAdd,
) -> None:
    try:
        await monitoring.get_service().add_courier(courier)
    except monitoring.MonitoringServiceUninitialized as e:
        raise exceptions.HTTPTemporarilyUnavailableException(str(e)) from e


