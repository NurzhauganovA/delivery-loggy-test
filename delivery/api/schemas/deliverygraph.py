import typing

import pydantic
import slugify
from pydantic import validator, root_validator
from tortoise.contrib.pydantic import PydanticModel

from .. import enums
from ..common.schema_base import BaseInSchema, BaseOutSchema
from ..context_vars import locale_context


class DeliveryGraphItem(pydantic.BaseModel):
    position: pydantic.StrictInt
    id: pydantic.StrictInt
    name: pydantic.StrictStr
    slug: typing.Optional[pydantic.StrictStr]
    icon: pydantic.StrictStr
    button_name: typing.Optional[pydantic.StrictStr]  # TODO: remove optionality after migration


class DeliveryGraphItemV2(BaseOutSchema, PydanticModel):
    id: int
    position: int
    name: str | None
    slug: str | None
    icon: str
    button_name: str | None
    transitions: list | None
    status: str | None

    @root_validator(pre=True)
    def _validate_name(cls, value: dict) -> dict:
        locale = locale_context.get()
        value['name'] = value.get(f'name_{locale}', value.get('name_en', value.get('name')))
        value['button_name'] = value.get(f'button_name_{locale}', value.get('button_name_en', value.get('button_name')))
        return value


class DeliveryGraphItemGet(BaseOutSchema, PydanticModel):
    position: int
    id: int
    name: str
    slug: typing.Optional[str]
    icon: str
    button_name: typing.Optional[str]  # TODO: remove optionality after migration
    slug: typing.Optional[str]

    @root_validator(pre=True)
    def _validate_name(cls, value: dict) -> dict:
        locale = locale_context.get()
        value['name'] = value.get(f'name_{locale}', value.get('name_en', value.get('name')))
        value['button_name'] = value.get(f'button_name_{locale}', value.get('button_name_en', value.get('button_name')))
        return value


class DeliveryGraphCreate(BaseInSchema, PydanticModel):
    name: pydantic.StrictStr
    slug: typing.Optional[pydantic.StrictStr]
    graph: typing.List[DeliveryGraphItem]
    types: typing.Set[enums.OrderType]

    class Config:
        use_enum_values = True

    # noinspection PyMethodParameters
    @validator('slug')
    def set_slug(cls, slug: str, values: dict) -> str:
        if slug is None:
            return slugify.slugify(values['name'])

        return slug

    # noinspection PyMethodParameters
    @validator('graph')
    def set_slug_for_items(cls, graph_items: list) -> list:
        for item in graph_items:
            if item.slug is None:
                item.slug = slugify.slugify(item.name)

        return graph_items


class DeliveryGraphUpdate(BaseInSchema, PydanticModel):
    name: pydantic.StrictStr
    slug: typing.Optional[pydantic.StrictStr]
    graph: typing.List[DeliveryGraphItem]
    types: typing.Set[enums.OrderType]

    class Config:
        use_enum_values = True


class DeliveryGraphGet(BaseOutSchema, PydanticModel):
    id: pydantic.StrictInt
    name: str | None
    slug: typing.Optional[pydantic.StrictStr]
    types: typing.List[str]
    graph: typing.List[DeliveryGraphItemGet]
    partner_id: typing.Optional[int]


class DeliveryGraphGetV2(BaseOutSchema, PydanticModel):
    graph: typing.List[DeliveryGraphItemV2]


class DeliveryGraphInternal(BaseInSchema, PydanticModel):
    id: int
    name: pydantic.StrictStr
    slug: typing.Optional[pydantic.StrictStr]
    graph: typing.List[DeliveryGraphItem]
    partner_id: typing.Optional[int]
