import typing

from .. import enums
from .. import exceptions
from .. import models
from .. import schemas


async def item_get_list(default_filter_args, filter_args) -> list:
    return await models.item_get_list(default_filter_args, filter_args)


async def item_get(
    item_id: int,
    default_filter_args
):
    item = await models.item_get(item_id, default_filter_args=default_filter_args)
    return item


async def item_create(
    payload: schemas.ItemCreate,
    current_user: schemas.UserCurrent,
) -> models.Item:
    try:
        created_item = await models.item_create(
            payload=payload,
        )
        await models.history_create(
            schemas.HistoryCreate(
                initiator_type=enums.InitiatorType.USER,
                initiator_id=current_user.id,
                initiator_role=current_user.profile['profile_type'],
                model_type=enums.HistoryModelName.ITEM,
                model_id=created_item.id,
                request_method=enums.RequestMethods.POST,
            )
        )
        return created_item
    except (
        models.EntityDoesNotExist,
        models.ItemPostControlCheckFailure,
    ) as e:
        raise exceptions.HTTPBadRequestException(str(e)) from e


async def item_cities_add(item_id: int, city_id: int, default_filter_args):
    return await models.item_cities_add(item_id, city_id, default_filter_args)


async def item_shipment_points_create(
    create: schemas.ItemShipmentPointCreate,
    default_filter_args,
    shipment_point_kwargs,
):
    return await models.itemshipmentpoints_create(
        create,
        default_filter_args,
        shipment_point_kwargs,
    )


async def item_update(
    item_id: int,
    payload: typing.Union[schemas.ItemUpdate, schemas.ItemPartialUpdate],
    current_user: schemas.UserCurrent,
    default_filter_args: list = None,
) -> schemas.ItemGet:
    try:
        updated_item = await models.item_update(item_id=item_id, payload=payload, default_filter_args=default_filter_args)

        await models.history_create(
            schemas.HistoryCreate(
                initiator_type=enums.InitiatorType.USER,
                initiator_id=current_user.id,
                initiator_role=current_user.profile['profile_type'],
                model_type=enums.HistoryModelName.ITEM,
                model_id=item_id,
                request_method=enums.RequestMethods.PUT,
            )
        )

        return updated_item
    except (
        models.EntityDoesNotExist,
        models.ItemPostControlCheckFailure,
    ) as e:
        raise exceptions.HTTPNotFoundException(str(e)) from e
    except (
        models.EntityDoesNotExist,
        models.CityAlreadyInItem,
    ) as e:
        raise exceptions.HTTPBadRequestException(str(e)) from e


async def item_partial_update(
    item_id: int,
    update: schemas.ItemPartialUpdate,
    current_user: schemas.UserCurrent,
    default_filter_args: list = None,
):
    updated_item = await models.item_update(
        item_id=item_id,
        update=update,
        default_filter_args=default_filter_args,
    )

    await models.history_create(
        schemas.HistoryCreate(
            initiator_type=enums.InitiatorType.USER,
            initiator_id=current_user.id,
            initiator_role=current_user.profile['profile_type'],
            model_type=enums.HistoryModelName.ITEM,
            model_id=item_id,
            request_method=enums.RequestMethods.PUT,
        )
    )
    return updated_item


async def item_delete(item_id: int, default_filter_args) -> None:
    await models.item_delete(item_id, default_filter_args)


async def item_delete_many(
    item_ids: schemas.ItemIDsList, default_filter_args,
) -> None:
    await models.item_delete_bulk(item_ids, default_filter_args)
