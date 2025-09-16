import datetime
import typing

import pydantic


class PublicApiTokenBase(pydantic.BaseModel):
    token: pydantic.constr(strict=True, max_length=255)
    is_expires: typing.Optional[bool]


class PublicApiToken(PublicApiTokenBase):
    pass


class PublicApiTokenCreate(PublicApiToken):
    partner_id: int


class PublicApiTokenGet(PublicApiToken):
    id: pydantic.StrictInt
    created_at: datetime.datetime

    class Config:
        orm_mode = True


class PublicApiTokenUpdate(PublicApiTokenCreate):
    pass
