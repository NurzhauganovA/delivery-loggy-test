import decimal
import typing
from datetime import datetime

import pydantic
from fastapi import Query
from pydantic import conlist, Field
from tortoise.contrib.pydantic.base import PydanticModel

from api.common.schema_base import BaseOutSchema, BaseFilterSchema, BaseInSchema
from api.modules.shipment_point.schemas import CityGet
from .enums import OrderGroupStatuses


class OrderGroupStatusGet(BaseOutSchema):
    created_at: datetime | None
    name: str | None


class PartnerShipmentPointGet(BaseOutSchema):
    id: typing.Optional[int | None]
    latitude: decimal.Decimal | None
    longitude: decimal.Decimal | None
    name: str | None
    address: pydantic.constr(strict=True, max_length=255) | None
    city: CityGet | None


class OrderGet(BaseOutSchema):
    id: pydantic.StrictInt


class UserGet(BaseOutSchema):
    id: int | None
    phone_number: str | None
    first_name: str | None
    last_name: str | None


class SorterGet(BaseOutSchema):
    id: int
    user: UserGet | None


class CourierGet(BaseOutSchema):
    id: int
    user: UserGet | None


class ServiceManagerGet(BaseOutSchema):
    id: int
    user: UserGet | None


class PartnerGet(PydanticModel):
    id: int
    name: str | None


class OrderGroupFilter(BaseFilterSchema):
    id: int | None


class OrdersIn(BaseInSchema):
    orders: typing.Optional[typing.List[int]]


class OrderGroupInBaseModel(OrdersIn):
    pass

    class Config:
        orm_mode = True


class OrderGroupOutBaseModel(BaseOutSchema, PydanticModel):
    created_at: datetime
    updated_at: datetime
    id: pydantic.StrictInt
    partner: PartnerGet | None
    sorter: SorterGet | None
    courier: CourierGet | None
    accepted_by_courier_at: datetime | None
    accepted_by_manager_at: datetime | None


class OrderGroupGet(OrderGroupOutBaseModel):
    act: str | None
    courier_service_manager: ServiceManagerGet | None
    shipment_point: typing.Optional[PartnerShipmentPointGet | None]
    delivery_point: typing.Optional[PartnerShipmentPointGet | None]
    count: typing.Optional[int | None]
    statuses: typing.Optional[typing.List[OrderGroupStatusGet] | None]


class PartnerGetForOrder(PydanticModel):
    name: str
    article: str


class OrderGroupListOrder(BaseOutSchema):
    id: int
    item_name: str
    receiver_name: typing.Optional[str]
    receiver_phone_number: str
    revised: bool
    partner: PartnerGetForOrder

    class Config:
        orm_mode = True


class OrderGroupUpdate(BaseInSchema):
    shipment_point_id: typing.Optional[pydantic.StrictInt]
    delivery_point_id: typing.Optional[pydantic.StrictInt]
    sorter_id: typing.Optional[pydantic.StrictInt]
    courier_id: typing.Optional[pydantic.StrictInt]
    courier_service_manager_id: typing.Optional[pydantic.StrictInt]
    accepted_by_manager_at: typing.Optional[datetime]


class OrderGroupCreateSchema(OrderGroupInBaseModel):
    pass


class OrderGroupCreate(BaseInSchema):
    sorter_id: typing.Optional[int]
    partner_id: typing.Optional[pydantic.StrictInt]
    shipment_point_id: typing.Optional[pydantic.StrictInt]
    delivery_point_id: typing.Optional[pydantic.StrictInt]
    courier_id: typing.Optional[pydantic.StrictInt]


class OrderGroupReportFilter(BaseInSchema):
    partner_id__in: conlist(int, min_items=1, unique_items=True) | None = Field(Query(None))
    courier_id__in: conlist(int, min_items=1, unique_items=True) | None = Field(Query(None))
    sorter_id__in: conlist(int, min_items=1, unique_items=True) | None = Field(Query(None))
    shipment_point_id__in: conlist(int, min_items=1, unique_items=True) | None = Field(Query(None))
    delivery_point_id__in: conlist(int, min_items=1, unique_items=True) | None = Field(Query(None))
    status__in: conlist(OrderGroupStatuses) | None = Field(Query(None))
    created_at__gte: datetime | None
    created_at__lte: datetime | None

    class Config:
        use_enum_values = True


__all__ = (
    'OrderGroupFilter',
    'OrderGroupGet',
    'OrderGroupListOrder',
    'OrderGroupCreateSchema',
    'OrderGroupReportFilter',
    'OrderGroupUpdate',
    'OrdersIn',
    'OrderGroupCreate',
    'OrderGroupStatusGet',
)
