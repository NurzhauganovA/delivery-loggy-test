import pydantic


class PermissionBase(pydantic.BaseModel):
    name: str
    slug: str


class Permission(pydantic.BaseModel):
    slug: str
    name: str


class PermissionList(Permission):
    pass


class PermissionGet(Permission):
    pass


class PermissionInternal(PermissionBase):
    pass
