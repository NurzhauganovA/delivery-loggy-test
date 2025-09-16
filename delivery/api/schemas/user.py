import typing

import pydantic

from .. import enums
from .permission import Permission
from api.common import validators


class UserBase(pydantic.BaseModel):
    phone_number: str
    email: typing.Optional[str]
    iin: typing.Optional[pydantic.constr(
        strict=True,
        min_length=12,
        max_length=12,
    )]

    _v_phn = validators.reuse('phone_number')(validators.validate_phone)

    class Config:
        extra = 'forbid'


class User(UserBase):
    first_name: typing.Optional[pydantic.constr(max_length=32)]
    last_name: typing.Optional[pydantic.constr(max_length=32)]
    middle_name: typing.Optional[pydantic.constr(max_length=32)]
    credentials: typing.Optional[typing.Dict[str, typing.Any]]

    @property
    def fullname(self) -> str:
        return f'{self.last_name or ""} {self.first_name or ""} {self.middle_name or ""}'.strip()

class UserCreate(UserBase):
    pass


class UserCreateManually(User):
    pass


class UserCreateTest(User):
    pass


class UserUpdate(pydantic.BaseModel):
    phone_number: typing.Optional[str]
    email: typing.Optional[str]
    iin: typing.Optional[pydantic.constr(
        strict=True,
        min_length=12,
        max_length=12,
    )]
    is_active: typing.Optional[pydantic.StrictBool]
    first_name: typing.Optional[pydantic.constr(max_length=32)]
    last_name: typing.Optional[pydantic.constr(max_length=32)]
    middle_name: typing.Optional[pydantic.constr(max_length=32)]
    credentials: typing.Optional[typing.Dict[str, typing.Any]]

    class Config:
        extra = 'forbid'


class UserPhoto(pydantic.BaseModel):
    photo: typing.Optional[str]

    class Config:
        extra = 'forbid'


class UserProfileBase(pydantic.BaseModel):
    id: pydantic.StrictInt
    profile_type: enums.ProfileType

    class Config:
        extra = 'forbid'


class UserProfile(UserProfileBase):
    pass


class UserGet(User):
    id: pydantic.StrictInt
    profile: typing.Optional[dict] = None
    is_active: pydantic.StrictBool = False
    photo: typing.Optional[str] = None
    invited_by: typing.Optional[dict] = None
    last_message: typing.Optional[dict] = None

    class Config:
        orm_mode = True
        extra = 'ignore'


class UserGetMultipleProfile(User):
    id: pydantic.StrictInt
    profiles: typing.Optional[typing.List[typing.Optional[dict]]] = None
    is_active: pydantic.StrictBool = False
    photo: typing.Optional[str] = None
    invited_by: typing.Optional[dict] = None
    last_message: typing.Optional[dict] = None

    class Config:
        orm_mode = True
        extra = 'ignore'


class UserCurrent(UserGet):
    is_superuser: bool = False
    has_password: bool
    partners: typing.List[int] = []
    items: typing.Optional[typing.List]
    areas: typing.Optional[typing.List]
    partner: typing.Optional[dict]
    profiles: typing.Optional[typing.List]


class UserInternal(User):
    pass


class SendLink(pydantic.BaseModel):
    phone_number: str
    link: pydantic.stricturl()

    _v_phn = validators.reuse('phone_number')(validators.validate_phone)


class SendLinkFeedback(SendLink):
    receiver_name: typing.Optional[str]


class SendLinkMonitoring(SendLink):
    receiver_name: typing.Optional[str]
    product_name: typing.Optional[str]
    partner_name: typing.Optional[str]


class UserPermission(pydantic.BaseModel):
    id: int
    permissions: typing.List[Permission]
