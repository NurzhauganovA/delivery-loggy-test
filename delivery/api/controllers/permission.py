from .. import exceptions
from .. import models


async def permission_list():
    return await models.permission_list()


async def permission_get(permission_slug: str):
    return await models.permission_get(permission_slug)
