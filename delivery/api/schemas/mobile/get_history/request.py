import typing

from pydantic import BaseModel

from api import enums


class HistoryFilterParams(BaseModel):
    initiator_id: typing.Optional[int]
    request_method: typing.Optional[enums.RequestMethods]
    model_type: typing.Optional[enums.HistoryModelName]
    model_id: typing.Optional[int]

    class Config:
        use_enum_values = True
