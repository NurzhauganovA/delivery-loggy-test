from .. import exceptions
from .. import models
from .. import schemas


async def status_get_default():
    return await models.status_get_list(partner_id=None)


async def status_get(status_id: int):
    return await models.status_get(status_id)


async def status_get_list(pagination_params, partner_id: int):
    return await models.status_get_list(pagination_params, partner_id=partner_id)


async def status_create(status: schemas.StatusCreate):
    return await models.status_create(status)


async def status_update(status_id: int, update: schemas.StatusUpdate):
    return await models.status_update(status_id, update)


async def status_delete(status_id: int):
    try:
        await models.status_delete(status_id)
    except models.StatusInOtherDependings as e:
        raise exceptions.HTTPBadRequestException(str(e)) from e
