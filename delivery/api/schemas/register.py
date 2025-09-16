import typing

import pydantic

from . import user
from api.common import validators


class RegisterBase(user.UserBase):
    bin: typing.Optional[pydantic.StrictStr]
    phone_number: str
    iin: typing.Optional[pydantic.StrictStr]

    _v_phn = validators.reuse('phone_number')(validators.validate_phone)
    _v_b = validators.reuse('bin')(validators.ensure_bin_is_valid)


class Register(RegisterBase):
    pass


class RegisterCreate(Register):
    pass
