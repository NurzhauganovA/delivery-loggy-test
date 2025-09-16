import typing

from .. import models
from .. import schemas


async def direction_get(**kwargs) -> typing.List[dict]:
    orders = await models.Order.filter(**kwargs)
    points = []
    if not orders:
        raise models.OrderNotFound('Orders for creating directions not found!')
    for order in orders:
        order_points = await models.order_address_get_list(order.id)
        for router_point in order_points:
            points.append(schemas.DirectionGet(
                order_id=order.id,
                position=order.position,
                delivery_status=order.delivery_status,
                type=router_point.type,
                longitude=router_point.place.longitude,
                latitude=router_point.place.latitude,
                address=router_point.place.address,
                receiver_name=order.receiver_name,
                receiver_phone_number=order.receiver_phone_number,
            ).dict())

    return points
