import asyncio
import typing

import aiohttp
import uuid

from .. import exceptions
from .. import models
from .. import schemas
from .. import enums
from ..services import osm


async def external_service_history_get(id_: uuid.UUID) -> dict:
    try:
        return await models.external_service_history_get(id=id_)
    except models.ExternalServiceHistoryDoesNotExist as e:
        raise exceptions.HTTPNotFoundException(str(e)) from e


async def external_service_history_get_list(**kwargs) -> list:
    return await models.external_service_history_get_list(**kwargs)
