from tortoise.contrib.pydantic import PydanticModel

from api.common.schema_base import BaseInSchema
from api.common.schema_base import BaseOutSchema
from api.common.validators import reuse, validate_phone


class CallRequestIn(BaseInSchema, PydanticModel):
    phone: str
    name: str

    _v_phn = reuse('phone')(validate_phone)

    class Config:
        anystr_strip_whitespace = True


class CallRequestOut(BaseOutSchema, PydanticModel):
    id: int
    phone: str
    name: str


class CallRequestCreateSchema(CallRequestIn):
    pass


class CallRequestContactIn(BaseInSchema, PydanticModel):
    phone: str | None
    email: str | None
    name: str | None

    _v_phn = reuse('phone')(validate_phone)

    class Config:
        anystr_strip_whitespace = True


class CallRequestContactOut(BaseOutSchema, PydanticModel):
    id: int
    phone: str | None
    email: str | None
    name: str | None


class CallRequestContactCreateSchema(CallRequestIn):
    pass


__all__ = (
    'CallRequestContactCreateSchema',
    'CallRequestContactIn',
    'CallRequestContactOut',
    'CallRequestCreateSchema',
    'CallRequestIn',
    'CallRequestOut',
)
