import datetime
import typing

from pydantic import StrictStr, StrictInt
from tortoise.contrib.pydantic import PydanticModel

from api import enums


class HistoryImage(PydanticModel):
    id: int
    image: str

class GetHistoryResponse(PydanticModel):
    initiator_type: enums.InitiatorType
    initiator_id: int
    initiator: typing.Optional[dict]
    created_at: datetime.datetime
    request_method: enums.RequestMethods
    model_type: StrictStr
    model_id: typing.Optional[StrictInt]
    action_data: typing.Optional[typing.Union[dict, str]]
    initiator_role: typing.Optional[enums.ProfileType]
    images: typing.Optional[typing.List[HistoryImage]]
    action_type: typing.Optional[enums.ActionType]
