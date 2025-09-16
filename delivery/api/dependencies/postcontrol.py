from typing import List

import fastapi

from api import schemas, exceptions, models
from api.enums import OrderStatus, PostControlType


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
    postcontrol_objects = await models.PostControl.filter(
        id__in=tuple(r.id for r in resolutions),
    )
    order_ids = [p.order_id for p in postcontrol_objects]
    if len(order_ids) == 0:
        return resolutions
    if len(set(order_ids)) > 1:
        raise exceptions.PydanticException(
            errors=(('__root__', 'Postcontrol documents must belong to one order'),)
        )

    # if all post-control documents have 'canceled' type, then there is no need to check conditions below.
    if all(p.type == PostControlType.CANCELED for p in postcontrol_objects):
        return resolutions

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
