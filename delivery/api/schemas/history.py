import datetime
import json
import typing

import pydantic
from pydantic import validator

from .. import enums


class HistoryBase(pydantic.BaseModel):
    initiator_type: typing.Optional[enums.InitiatorType]
    initiator_id: int
    request_method: enums.RequestMethods
    model_type: enums.HistoryModelName
    model_id: typing.Optional[int]
    action_type: enums.ActionType | None
    action_data: typing.Optional[typing.Union[dict, str]]
    initiator_role: typing.Optional[enums.ProfileType]

    class Config:
        use_enum_values = True

    # noinspection PyMethodParameters
    @validator('action_data')
    def ensure_action_data_is_serialized(cls, value: dict) -> json:
        if not value:
            return value

        result = json.dumps(
            value,
            indent=4,
            sort_keys=True,
            default=str,
        )

        return result


class HistoryCreate(HistoryBase):
    created_at: datetime.datetime | None


class HistoryUser(pydantic.BaseModel):
    id: typing.Optional[int]
    first_name: typing.Optional[pydantic.constr(max_length=32)]
    last_name: typing.Optional[pydantic.constr(max_length=32)]
    middle_name: typing.Optional[pydantic.constr(max_length=32)]
    profile_type: typing.Optional[str]

    class Config:
        orm_mode = False


class HistoryGet(pydantic.BaseModel):
    initiator_type: enums.InitiatorType
    initiator_id: int
    initiator: typing.Optional[dict]
    created_at: datetime.datetime
    request_method: enums.RequestMethods
    model_type: pydantic.StrictStr
    model_id: typing.Optional[pydantic.StrictInt]
    action_data: typing.Optional[typing.Union[dict, str]]
    initiator_role: typing.Optional[enums.ProfileType]

    class Config:
        orm_mode = True


class HistoryFilterParams(pydantic.BaseModel):
    initiator_id: typing.Optional[int]
    request_method: typing.Optional[enums.RequestMethods]
    model_type: typing.Optional[enums.HistoryModelName]
    model_id: typing.Optional[int]
