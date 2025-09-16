import datetime

import pydantic

from .. import enums
from api.common import validators


class InvitedUser(pydantic.BaseModel):
    phone_number: str
    status: enums.InviteStatus = enums.InviteStatus.INVITED
    profile_type: str

    _v_phn = validators.reuse('phone_number')(validators.validate_phone)


class InvitedUserCreate(InvitedUser):
    pass


class InvitedUserGet(InvitedUser):
    created_at: datetime.datetime
    inviter: dict

    class Config:
        orm_mode = True
