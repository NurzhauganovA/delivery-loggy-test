import typing

import pydantic

from .permission import Permission


class User(pydantic.BaseModel):
    id: int
    phone_number: str


class GroupBase(pydantic.BaseModel):
    slug: str

    class Config:
        extra = 'ignore'


class GroupCreate(GroupBase):
    permissions: typing.Optional[typing.List[str]]


class Group(GroupBase):
    pass


class GroupGet(Group):
    users: typing.List[User] = []
    permissions: typing.List[Permission] = []

    class Config:
        orm_mode = True


class GroupList(Group):
    pass


class GroupInternal(Group):
    permissions: typing.List[str]
