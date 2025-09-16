import typing

import pydantic


class BiometryRequest(pydantic.BaseModel):
    iin: pydantic.constr()
    phone: pydantic.constr()
    callback: pydantic.constr()
    redirect_url: pydantic.constr()


class BiometryResponse(pydantic.BaseModel):
    url: pydantic.constr()


class BiometryVerifyBody(pydantic.BaseModel):
    state: typing.Optional[str]
    success: typing.Optional[bool]
    user_photo: typing.Optional[bytes]
