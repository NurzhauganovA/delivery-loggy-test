import decimal
import typing

import pydantic
from tortoise.contrib.pydantic import PydanticModel

from api.common.schema_base import BaseOutSchema, BaseFilterSchema, BaseInSchema
from api.modules.order.schemas import UserGet


class PartnerGet(PydanticModel):
    id: int
    name: str | None


class ItemGet(PydanticModel):
    id: int | None
    name: str | None
    distribute: bool | None


class CountryGet(PydanticModel):
    id: int
    name: str


class CityGet(PydanticModel):
    id: int
    name: str | None
    country: CountryGet


class PartnerSettingFilter(BaseFilterSchema):
    partner_id: int | None


class DefaultCouriers(pydantic.BaseModel):
    __root__: typing.Dict[int, int]

    def __setitem__(self, key, value):
        self.__root__[key] = value

    def __getitem__(self, item):
        return self.__root__[item]

    def get(self, key):
        try:
            return self.__root__[key]
        except KeyError:
            pass


class PartnerSettingInBaseModel(BaseInSchema):
    auto_item_for_order_group_id: int | None
    default_delivery_point_for_order_group_id: int | None
    default_order_group_couriers: DefaultCouriers | None


class ProfileCourierGet(BaseOutSchema):
    id: int | None
    user: UserGet


class PartnerShipmentPointGet(BaseOutSchema, PydanticModel):
    id: int | None
    latitude: decimal.Decimal | None
    longitude: decimal.Decimal | None
    name: str | None
    address: pydantic.constr(strict=True, max_length=255) | None
    city: CityGet | None


class PartnerSettingOutBaseModel(BaseOutSchema):
    id: int
    partner: PartnerGet | None
    auto_item_for_order_group: ItemGet | None = None
    default_delivery_point_for_order_group: PartnerShipmentPointGet | None = None
    default_order_group_couriers: None | DefaultCouriers = None


class PartnerSettingGet(PartnerSettingOutBaseModel):
    pass


class PartnerSettingUpdate(BaseInSchema):
    auto_item_for_order_group_id: typing.Optional[int | None]
    default_delivery_point_for_order_group_id: typing.Optional[int | None]
    default_order_group_couriers: DefaultCouriers | None


class PartnerSettingCreate(PartnerSettingInBaseModel):
    pass


__all__ = (
    'PartnerSettingFilter', 'PartnerSettingCreate', 'PartnerSettingUpdate',
    'PartnerSettingGet'
)
