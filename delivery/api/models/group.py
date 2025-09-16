from tortoise import Model
from tortoise import fields
from tortoise.query_utils import Prefetch
from tortoise.transactions import atomic

from .permission import Permission
from .user import User
from .. import enums
from .. import schemas


class GroupNotFound(Exception):
    """Raises if group with given ID was not found."""


class GroupAlreadyExists(Exception):
    """Raises if group with given name already exists."""


class Group(Model):
    slug = fields.CharField(max_length=40, pk=True)
    name = fields.CharField(max_length=255, unique=True, null=True)
    user_set: fields.ManyToManyRelation['User'] = fields.ManyToManyField(
        'versions.User',
        related_name='group_set',
    )
    permission_set: fields.ManyToManyRelation[
        'Permission'] = fields.ManyToManyField(
        'versions.Permission',
        related_name='group_set',
    )

    class Meta:
        table = 'groups'


@atomic()
async def group_create(group: schemas.GroupCreate):
    create_dict = group.dict(exclude_unset=True)
    permissions = set(create_dict.pop('permissions', []))
    group, created = await Group.get_or_create(**create_dict)
    old_permissions = set(await group.permission_set.all().values_list('slug', flat=True))
    if permissions != old_permissions:
        perm_objects = await Permission.filter(slug__in=permissions)
        await group.permission_set.clear()
        await group.permission_set.add(*perm_objects)

    group.permissions = await group.permission_set
    group.users = await group.user_set

    return schemas.GroupGet.from_orm(group)


async def group_list():
    return await Group.all().values()


async def group_get(group_slug: str):
    group = await Group.get(slug=group_slug).prefetch_related(
        Prefetch(
            'user_set',
            User.all(),
            'users',
        ),
        Prefetch(
            'permission_set',
            Permission.all(),
            'permissions',
        )
    )

    return schemas.GroupGet.from_orm(group)


async def group_user_add(group_slug: str, user_id: int):
    return await group_user_change(group_slug, user_id,
                                   enums.GroupAction.USER_ADD)


async def group_user_remove(group_slug: str, user_id: int):
    return await group_user_change(group_slug, user_id,
                                   enums.GroupAction.USER_REMOVE)


async def group_permission_add(group_slug: str, permission_slug: str):
    return await group_permission_change(group_slug, permission_slug,
                                         enums.GroupAction.PERM_ADD)


async def group_permission_remove(group_slug: str, permission_slug: str):
    return await group_permission_change(group_slug, permission_slug,
                                         enums.GroupAction.PERM_REMOVE)


@atomic()
async def group_permission_change(group_slug: str, permission_slug: str,
                                  action: enums.GroupAction):
    group = await Group.get(slug=group_slug)
    permission = await Permission.get(slug=permission_slug)

    if action == action.PERM_ADD:
        await group.permission_set.add(permission)
    elif action == action.PERM_REMOVE:
        await group.permission_set.remove(permission)

    group.permissions = await group.permission_set

    return schemas.GroupGet.from_orm(group)


@atomic()
async def group_user_change(group_slug: str, user_id: int,
                            action: enums.GroupAction):
    group = await Group.get(slug=group_slug)
    user = await User.get(id=user_id)

    if action.USER_ADD:
        await group.user_set.add(user)
    elif action.USER_REMOVE:
        await group.user_set.remove(user)

    group.users = await group.user_set

    return schemas.GroupGet.from_orm(group)
