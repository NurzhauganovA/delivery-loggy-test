import decimal
import typing

import pydantic
from api.common import validators

from api.common.schema_base import BaseOutSchema, BaseFilterSchema, BaseInSchema
from fastapi import Query
from pydantic import Field


class PartnerGet(pydantic.BaseModel):
    id: pydantic.StrictInt
    name: str | None


class CountryGet(pydantic.BaseModel):
    id: pydantic.StrictInt
    name: str

    class Config:
        orm_mode = True


class CityGet(pydantic.BaseModel):
    id: pydantic.StrictInt
    name: str
    country: CountryGet

    class Config:
        orm_mode = True


class PartnerShipmentPointFilter(BaseFilterSchema):
    city_id: int | None
    partner_id: int | None


class PartnerShipmentPointFilterV2(BaseFilterSchema):
    city_id__in: typing.List[int] | None = Field(Query(None))
    partner_id__in: typing.List[int] | None = Field(Query(None))


class PartnerShipmentPointInBaseModel(BaseInSchema):
    latitude: decimal.Decimal
    longitude: decimal.Decimal
    name: str
    partner_id: pydantic.StrictInt
    address: pydantic.constr(strict=True, max_length=255)
    city_id: pydantic.StrictInt

    _v_lat = validators.reuse('latitude', check_fields=False)(validators.validate_latitude)
    _v_lon = validators.reuse('longitude', check_fields=False)(validators.validate_longitude)


class PartnerShipmentPointOutBaseModel(BaseOutSchema):
    latitude: decimal.Decimal
    longitude: decimal.Decimal
    name: str
    partner: PartnerGet
    address: pydantic.constr(strict=True, max_length=255)
    city: CityGet
    client_link: str | None = None


class PartnerShipmentPointGet(PartnerShipmentPointOutBaseModel):
    # history: typing.Optional[typing.List[dict]]
    id: pydantic.StrictInt

    class Config:
        orm_mode = True


class PartnerShipmentPointUpdate(BaseInSchema):
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


__all__ = (
    'PartnerShipmentPointFilter',
    'PartnerShipmentPointGet',
    'PartnerShipmentPointCreate',
    'PartnerShipmentPointUpdate'
)
