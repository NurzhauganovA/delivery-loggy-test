import typing

import pydantic
from pydantic import BaseModel
from tortoise.contrib.pydantic import PydanticModel

from api.common.schema_base import BaseOutSchema, BaseInSchema


class CountryBase(pydantic.BaseModel):
    """Country model schema"""
    name: pydantic.constr(strict=True, max_length=255, strip_whitespace=True)


class Country(CountryBase):
    pass


class CountryCreate(Country):
    pass


class CountryUpdate(Country):
    pass


class CityGet(BaseOutSchema, PydanticModel):
    id: int
    name: str | None


class CountryGet(BaseOutSchema, PydanticModel):
    id: int
    name: str | None
    cities: typing.List[CityGet]


class CountryInternal(Country):
    pass
