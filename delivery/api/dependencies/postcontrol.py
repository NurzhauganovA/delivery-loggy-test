from typing import List

import fastapi
from fastapi import Depends

from api import schemas, exceptions, models
from api.dependencies import OrderDefaultFilter
from api.enums import OrderDeliveryStatus, DeliveryGraphIcons, OrderStatus


async def postcontrol_validate_payload(
    config_id: int = fastapi.Body(),
) -> int:
    config = await models.PostControlConfig.get_or_none(id=config_id).prefetch_related('inner_param_set')
    if config and config.inner_param_set:
        raise exceptions.PydanticException(
            errors=(('config_id', 'This config can not accept postcontrol documents'),)
        )

    return config_id


async def postcontrol_make_resolution_payload(
    resolutions: List[schemas.PostControlMakeResolution],
):
    order_ids = await models.PostControl.filter(
        id__in=tuple(r.id for r in resolutions),
    ).values_list('order_id', flat=True)
    if len(order_ids) == 0:
        return resolutions
    if len(set(order_ids)) > 1:
        raise exceptions.PydanticException(
            errors=(('__root__', 'Postcontrol documents must belong to one order'),)
        )

    order_obj = await models.Order.get(id=order_ids[0])
    if order_obj.current_status_id not in (int(OrderStatus.POST_CONTROL), int(OrderStatus.POST_CONTROL_BANK)):
        raise exceptions.PydanticException(
            errors=(('__root__', 'Can not make resolution in this stage'),)
        )

    return resolutions


async def check_order_can_make_resolution(
    order_id: int,
):
    order_obj = await models.Order.get(id=order_id)
    if order_obj.current_status_id not in (int(OrderStatus.POST_CONTROL), int(OrderStatus.POST_CONTROL_BANK)):
        raise exceptions.PydanticException(
            ('__root__', 'Can not make resolution in this stage'),
        )

    return order_id
