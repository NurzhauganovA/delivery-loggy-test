import decimal
import typing

import pydantic

from api.common.schema_base import BaseOutSchema, BaseInSchema
from api.common import validators


class DeliveryPointInBaseModel(BaseInSchema):
    latitude: decimal.Decimal
    longitude: decimal.Decimal
    address: pydantic.constr(strict=True, max_length=255)

    _v_lat = validators.reuse('latitude', check_fields=False)(validators.validate_latitude)
    _v_lon = validators.reuse('longitude', check_fields=False)(validators.validate_longitude)


class DeliveryPointOutBaseModel(BaseOutSchema):
    latitude: decimal.Decimal
    longitude: decimal.Decimal
    address: str


class DeliveryPointGet(DeliveryPointOutBaseModel):
    id: pydantic.StrictInt

    class Config:
        orm_mode = True


class DeliveryPointUpdate(BaseInSchema):
    latitude: typing.Optional[decimal.Decimal]
    longitude: typing.Optional[decimal.Decimal]
    address: typing.Optional[pydantic.constr(strict=True, max_length=255)]

    _v_lat = validators.reuse('latitude', check_fields=False)(validators.validate_latitude)
    _v_lon = validators.reuse('longitude', check_fields=False)(validators.validate_longitude)


class DeliveryPointCreate(DeliveryPointInBaseModel):
    pass


class DeliveryPointFilter(pydantic.BaseModel):
    order_id: int


__all__ = (
    'DeliveryPointCreate',
    'DeliveryPointFilter',
    'DeliveryPointGet',
    'DeliveryPointUpdate',
)
