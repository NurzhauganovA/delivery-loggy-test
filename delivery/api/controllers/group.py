from .. import exceptions
from .. import models
from .. import schemas


async def group_create(group: schemas.GroupCreate):
    return await models.group_create(group)


async def group_get(group_slug: str):
    return await models.group_get(group_slug)


async def group_list():
    return await models.group_list()


async def group_user_add(group_slug: str, user_id: int):
    return await models.group_user_add(group_slug, user_id)


async def group_user_remove(group_slug: str, user_id: int):
    return await models.group_user_remove(group_slug, user_id)


async def group_permission_add(group_slug: str, permission_slug: str):
    return await models.group_permission_add(group_slug, permission_slug)


async def group_permission_remove(group_slug: str, permission_slug: str):
    return await models.group_permission_remove(group_slug, permission_slug)
