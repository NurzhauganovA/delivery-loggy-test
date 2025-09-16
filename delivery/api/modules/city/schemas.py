from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from tortoise.contrib.pydantic import PydanticModel
from tortoise.timezone import now

from api.common.schema_base import BaseInSchema
from api.common.schema_base import BaseOutSchema
from api.common.validators import reuse, validate_latitude, validate_longitude

import pydantic


class CountryGet(BaseOutSchema, PydanticModel):
    id: int
    name: str


class CityBase(BaseOutSchema, PydanticModel):
    name: pydantic.constr(strict=True, max_length=255)
    country_id: int
    timezone: str | None
    latitude: float | None
    longitude: float | None


class City(CityBase):
    pass


class CityBaseIn(BaseInSchema, PydanticModel):
    name: pydantic.constr(strict=True, max_length=255)
    country_id: int
    timezone: str | None
    latitude: float | None
    longitude: float | None

    _v_la = reuse('latitude')(validate_latitude)
    _v_lo = reuse('longitude')(validate_longitude)


class CityCreate(CityBaseIn):
    pass


class CityUpdate(CityBaseIn):
    pass


class CityPartialUpdate(CityBaseIn):
    name: pydantic.constr(strict=True, max_length=255)
    country_id: int | None


class CityBaseOut(BaseOutSchema, PydanticModel):
    id: int
    name: str | None = None


class CityList(CityBaseOut):
    pass


class CityGet(BaseOutSchema, PydanticModel):
    id: int
    name: str
    timezone: str | None
    latitude: float | None
    longitude: float | None
    country: CountryGet

    @property
    def offset(self):
        current_time = now()
        return self.tz.utcoffset(current_time)

    @property
    def localtime(self):
        current_time = now()
        return current_time + self.tz.utcoffset(current_time)

    @property
    def tz(self):
        try:
            return ZoneInfo(self.timezone)
        except ZoneInfoNotFoundError:
            pass
        return ZoneInfo('UTC')


class CityInternal(CityBaseIn):
    pass


class CityFilter(pydantic.BaseModel):
    country_id: int | None
    partner_id: int | None


__all__ = (
    'CityCreate',
    'CityFilter',
    'CityGet',
    'CityInternal',
    'CityList',
    'CityPartialUpdate',
    'CityUpdate',
)
