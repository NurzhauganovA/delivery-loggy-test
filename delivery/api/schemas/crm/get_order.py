import datetime
import typing

from tortoise.contrib.pydantic import PydanticModel

from api import enums
from api.enums import OrderType
from api.schemas.deliverygraph import DeliveryGraphGetV2
from api.schemas.order import (
    Courier, DeliveryStatus, Area, Partner, ShipmentPointGet, DeliveryPointGet, ItemV2, StatusGetV2, Product,
    ItemGetV2, OrderStatusGetWithDatetime, City
)


class CommentUserRole(PydanticModel):
    slug: str
    name: str


class CommentImage(PydanticModel):
    id: int
    image: str


class Comment(PydanticModel):
    id: int
    user_id: int
    order_id: int
    text: str
    user_name: str
    created_at: datetime.datetime
    user_role: CommentUserRole
    images: typing.List[CommentImage]


class GetOrderResponse(PydanticModel):
    id: int
    type: OrderType
    delivery_datetime: datetime.datetime | None
    delivery_status: DeliveryStatus | None
    receiver_iin: str | None
    receiver_name: str | None
    receiver_phone_number: str
    comment: str | None
    created_by: enums.CreatedType
    idn: str | None = None

    initial_delivery_datetime: datetime.datetime | None
    created_at: datetime.datetime
    courier: Courier | None
    city: City | None
    area: Area | None
    partner: Partner | None
    shipment_point: ShipmentPointGet | None
    delivery_point: DeliveryPointGet | None
    item: ItemV2
    deliverygraph_step_count: int = 0
    current_status_position: int | None
    current_status: StatusGetV2 | None
    manager: str | None = None
    product: Product | None = None

    item: ItemGetV2
    deliverygraph: DeliveryGraphGetV2 | None
    statuses: typing.List[OrderStatusGetWithDatetime]
    last_otp: datetime.datetime | None
    actual_delivery_datetime: datetime.datetime | None
    product: Product | None
    courier_assigned_at: datetime.datetime | None
    comments: typing.List[Comment]
