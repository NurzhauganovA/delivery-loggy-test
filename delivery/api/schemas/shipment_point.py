import decimal
import typing

import pydantic
from tortoise.contrib.pydantic import PydanticModel

from api.common import validators
from api.common.schema_base import BaseOutSchema


class PartnerGet(PydanticModel):
    id: pydantic.StrictInt
    name: str | None


class CountryGet(pydantic.BaseModel):
    id: pydantic.StrictInt
    name: str

    class Config:
        orm_mode = True


class CityGet(pydantic.BaseModel):
    id: pydantic.StrictInt
    name: str | None
    country: CountryGet

    class Config:
        orm_mode = True


class ShipmentPointFilter(pydantic.BaseModel):
    city_id: int | None
    partner_id: int | None


class PartnerShipmentPointInBaseModel(pydantic.BaseModel):
    latitude: decimal.Decimal
    longitude: decimal.Decimal
    name: str
    partner_id: pydantic.StrictInt
    address: pydantic.constr(strict=True, max_length=255)
    city_id: pydantic.StrictInt

    _v_lat = validators.reuse('latitude', check_fields=False)(validators.validate_latitude)
    _v_lon = validators.reuse('longitude', check_fields=False)(validators.validate_longitude)


class PartnerShipmentPointOutBaseModel(BaseOutSchema, PydanticModel):
    latitude: decimal.Decimal
    longitude: decimal.Decimal
    name: str
    partner: PartnerGet
    address: pydantic.constr(strict=True, max_length=255)
    city: CityGet


class PartnerShipmentPointGet(PartnerShipmentPointOutBaseModel):
    # history: typing.Optional[typing.List[dict]]
    id: pydantic.StrictInt

    class Config:
        orm_mode = True


class PartnerShipmentPointUpdate(pydantic.BaseModel):
    latitude: typing.Optional[decimal.Decimal]
    longitude: typing.Optional[decimal.Decimal]
    name: typing.Optional[pydantic.constr(strict=True, max_length=200)]
    partner_id: typing.Optional[pydantic.StrictInt]
    address: typing.Optional[pydantic.constr(strict=True, max_length=255)]
    city_id: typing.Optional[pydantic.StrictInt]

    _v_lat = validators.reuse('latitude', check_fields=False)(validators.validate_latitude)
    _v_lon = validators.reuse('longitude', check_fields=False)(validators.validate_longitude)


class PartnerShipmentPointCreate(PartnerShipmentPointInBaseModel):
    pass


class PartnerShipmentPointsInternal(PartnerShipmentPointCreate):
    partner_id: int
