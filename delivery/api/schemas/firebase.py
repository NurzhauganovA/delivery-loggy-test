from typing import Optional

from pydantic import BaseModel
from pydantic import conlist

from .. import enums


class FCMDeviceCreate(BaseModel):
    id: str
    type: enums.DeviceType

    class Config:
        use_enum_values = True


class Notification(BaseModel):
    title: Optional[str]
    body: Optional[str]


class FirebaseMessage(BaseModel):
    registration_ids: conlist(str, min_items=1)
    data: Optional[dict]
    notification: Optional[Notification]
