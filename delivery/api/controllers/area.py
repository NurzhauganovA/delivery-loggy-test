import tortoise.exceptions

from .. import exceptions
from .. import models
from .. import schemas
from re import search


async def area_get(area_id: int, default_filter_args) -> dict:
    return await models.area_get(area_id=area_id, default_filter_args=default_filter_args)


async def area_get_list(default_filter_args, filter_kwargs) -> list:
    return await models.area_get_list(default_filter_args, filter_kwargs)


async def area_create(area: schemas.AreaCreate) -> dict:
    result = await models.area_create(area)
    return result


async def area_update(
    area_id: int, update: schemas.AreaUpdate, default_filter_args,
) -> dict:
    try:
        return await models.area_update(
            area_id, update, default_filter_args=default_filter_args,
        )
    except models.AreaCannotBeArchived as e:
        raise exceptions.HTTPBadRequestException(e)


async def area_delete(area_id: int, default_filter_args) -> None:
    try:
        return await models.area_delete(area_id, default_filter_args)
    except tortoise.exceptions.IntegrityError as e:
        reference_fields = ['profile_courier', 'order', 'partner.shipment_points']
        for field in reference_fields:
            if search(field, str(e)):
                raise exceptions.HTTPBadRequestException(
                    f'{field} exist in this area')
        raise exceptions.HTTPBadRequestException(str(e)) from e


async def area_activate(area_id: int, default_filter_args):
    return await models.area_activate(area_id, default_filter_args)


async def area_archive(area_id: int, default_filter_args):
    try:
        return await models.area_archive(area_id, default_filter_args)
    except models.AreaCannotBeArchived as e:
        raise exceptions.HTTPBadRequestException(e)
