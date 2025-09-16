import typing

import pydantic

from .. import enums


class CategoryBase(pydantic.BaseModel):
    name: pydantic.constr(strict=True, max_length=255)
    item_type: enums.ItemType
    value: pydantic.conint(ge=-32768, le=32767)


class Category(CategoryBase):
    pass


class CategoryCreate(Category):
    pass


class CategoryUpdate(Category):
    pass


class CategoryGet(Category):
    id: int

    class Config:
        orm_mode = True


class CategoryInternal(Category):
    partner_id: int


class CategoryIds(pydantic.BaseModel):
    items: typing.List[pydantic.StrictInt]

    class Config:
        schema_extra = {
            'example': {
                'items': [1, 2, 3],
            },
        }
