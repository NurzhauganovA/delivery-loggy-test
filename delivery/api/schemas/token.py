import datetime
import typing

import pydantic
from pydantic import Extra
from tortoise.contrib.pydantic import PydanticModel


class TokenGet(pydantic.BaseModel):
    access_token: str
    refresh_token: str
    token_type: pydantic.constr(strict=True, regex='bearer')  # noqa: F821
    profiles: typing.Optional[typing.List]

    class Config:
        extra = 'forbid'


class TokenBase(pydantic.BaseModel):
    client_id: int
    token: str
    token_type: pydantic.constr(strict=True, regex='bearer')  # noqa: F821

    class Config:
        extra = 'forbid'


class TokenInternalInfo(pydantic.BaseModel):
    class Config:
        extra = 'forbid'


class AccessTokenInternal(TokenBase, TokenInternalInfo):
    class Config:
        extra = 'forbid'


class RefreshTokenInternal(TokenBase, TokenInternalInfo):
    is_revoked: bool = True
    revoked_at: typing.Optional[datetime.datetime] = None

    class Config:
        extra = 'forbid'


class RevokedTokenCreate(PydanticModel):
    client_id: int
    exp: datetime.datetime
    token: str

    class Config:
        extra = Extra.ignore


