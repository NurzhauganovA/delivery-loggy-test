import datetime
import typing
from uuid import UUID
from uuid import uuid4

import pydantic

from .. import enums


class ExternalServiceHistoryBase(pydantic.BaseModel):
    id: typing.Optional[UUID] = uuid4()
    service_name: str
    url: pydantic.StrictStr
    request_body: typing.Optional[typing.Union[dict, str, bytes]]
    response_body: typing.Optional[dict]
    status_code: int
    owner_id: typing.Optional[int]

    class Config:
        use_enum_values = True


class ExternalServiceHistoryCreate(ExternalServiceHistoryBase):
    pass


class ExternalServiceHistoryGet(ExternalServiceHistoryBase):
    created_at: datetime.datetime


class ExternalServiceHistoryGetList(pydantic.BaseModel):
    service_name: enums.ExternalServices
    status_code: int = None
