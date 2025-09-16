from .. import exceptions
from .. import models
from .. import schemas


async def transport_get(transport_id: int) -> dict:
    return await models.transport_get(transport_id)


async def transport_create(transport: schemas.TransportCreate) -> dict:
    try:
        return await models.transport_create(transport)
    except models.ProfileNotFound as e:
        raise exceptions.HTTPNotFoundException(str(e)) from e


async def transport_update(
        transport_id: int, update: schemas.TransportUpdate) -> dict:
    try:
        return await models.transport_update(transport_id, update)
    except models.TransportNotFound as e:
        raise exceptions.HTTPNotFoundException(str(e)) from e


async def transport_delete(transport_id: int) -> dict:
    try:
        return await models.transport_delete(transport_id)
    except models.TransportNotFound as e:
        raise exceptions.HTTPNotFoundException(str(e)) from e
