import typing

import pydantic
from pydantic import EmailStr

from .. import enums
from api.common import validators


class Email(pydantic.BaseModel):
    email: EmailStr


class PhoneNumber(pydantic.BaseModel):
    phone_number: str

    _v_phn = validators.reuse('phone_number')(validators.validate_phone)


class OTPBase(pydantic.BaseModel):
    credentials: Email | PhoneNumber


class OTP(OTPBase):
    otp: pydantic.constr(strict=True, min_length=4, max_length=4)
    agree: typing.Optional[bool]

    # noinspection PyMethodParameters
    @pydantic.validator('otp')
    def ensure_otp_is_valid(cls, otp: str) -> str:
        if not otp.isdigit():
            raise ValueError('OTP code must contain digits only')

        return otp


class OTPCreate(OTPBase):
    type: typing.Optional[enums.OTPType]


class Message(OTPBase):
    message: str


class OTPGet(OTP):
    pass
