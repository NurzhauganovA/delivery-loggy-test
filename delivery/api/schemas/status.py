import typing

import pydantic


class StatusChildItem(pydantic.BaseModel):
    id: pydantic.StrictInt
    name: typing.Optional[pydantic.StrictStr]


class Status(pydantic.BaseModel):
    name: pydantic.StrictStr
    is_optional: pydantic.StrictBool
    partner_id: typing.Optional[pydantic.StrictInt]
    after: typing.List[StatusChildItem]


class StatusCreate(Status):
    pass


class StatusGet(Status):
    id: pydantic.StrictInt
    slug: pydantic.StrictStr


class StatusBulkCreate(pydantic.BaseModel):
    __root__: typing.List[Status]


class StatusUpdate(Status):
    pass
