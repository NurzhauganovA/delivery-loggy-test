from typing import List

from .schemas import DeliveryPointCreate, DeliveryPointUpdate


async def delivery_point_default_filter_args(
) -> list:
    args = []
    return args


async def delivery_point_default_filter_args_external(
):
    return []


async def delivery_point_validate_payload(
    delivery_point: DeliveryPointCreate | DeliveryPointUpdate,
):
    return delivery_point


async def delivery_point_validate_bulk_payload(
    delivery_points: List[DeliveryPointCreate],
):
    return delivery_points
