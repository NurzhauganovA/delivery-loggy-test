import decimal
import typing

import pydantic

from api.common import validators


class Coordinates(pydantic.BaseModel):
    latitude: typing.Optional[decimal.Decimal]
    longitude: typing.Optional[decimal.Decimal]

    _v_lat = validators.reuse('latitude', check_fields=False)(validators.validate_latitude)
    _v_lon = validators.reuse('longitude', check_fields=False)(validators.validate_longitude)

    def to_tuple(self):
        return self.latitude, self.longitude


class PlaceBase(Coordinates):
    address: pydantic.constr(strict=True, max_length=255)
    city_id: typing.Optional[pydantic.StrictInt]


class Place(PlaceBase):
    pass


class PlaceCreate(Place):
    pass


class PlaceUpdate(Place):
    pass


class PlaceGet(Place):
    id: pydantic.StrictInt

    _v_lt = validators.reuse('latitude')(validators.validate_latitude_to_float)
    _v_ln = validators.reuse('longitude')(validators.validate_longitude_to_float)


class PlaceInternal(Place):
    pass
