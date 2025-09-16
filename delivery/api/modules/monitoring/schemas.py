import decimal
import typing

from api.common.schema_base import BaseInSchema
from api.common import validators


class Geolocation(BaseInSchema):
    latitude: typing.Optional[decimal.Decimal]
    longitude: typing.Optional[decimal.Decimal]

    _v_lat = validators.reuse('latitude', check_fields=False)(validators.validate_latitude)
    _v_lon = validators.reuse('longitude', check_fields=False)(validators.validate_longitude)


class GeolocationPut(Geolocation):
    courier_partner_id: int
    courier_id: int

__all__ = (
    'Geolocation', 'GeolocationPut'
)
