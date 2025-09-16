import json

from fastapi.encoders import jsonable_encoder
from tortoise import Model
from tortoise import fields
from tortoise.exceptions import DoesNotExist
from tortoise.expressions import Q

from api import redis_module
from api.schemas import UserCurrent


class Permission(Model):
    slug = fields.CharField(max_length=10, pk=True)
    name = fields.CharField(unique=True, max_length=255)

    class Meta:
        table = 'permissions'


async def permission_create(permission):
    instance, created = await Permission.get_or_create(
        slug=permission.slug,
        defaults=permission.dict(exclude_unset=True, exclude={'slug', }),
    )
    redis_con = await redis_module.get_connection()
    perm_cache_keys = await redis_con.keys('permissions:*')
    if perm_cache_keys:
        await redis_con.delete(*perm_cache_keys)
    return dict(instance)


async def permission_get_or_404(permission_slug: str) -> Permission:
    try:
        return await Permission.get(slug=permission_slug)
    except DoesNotExist:
        raise DoesNotExist(
            f'Permission with given slug: {permission_slug} was not found',
        )


async def permission_list():
    return await Permission.all().values()


async def permission_get(permission_slug: str):
    permission = await permission_get_or_404(permission_slug=permission_slug)
    return dict(permission)


async def permission_mine(current_user: UserCurrent) -> list:
    redis_con = redis_module.get_connection()
    user_id = current_user.id
    profile_type = current_user.profile.get('type') if current_user.profile else None
    perm_cache_key = f"permissions:user_id:{user_id}{'_profile:' + profile_type if profile_type else ''}"
    perm_cache = await redis_con.get(perm_cache_key)
    if perm_cache is not None:
        return json.loads(perm_cache)
    if not profile_type:
        perm = await Permission.filter(users=user_id).values_list('slug', flat=True)
    else:
        perm = await Permission.filter(
            Q(users=user_id) | Q(group_set__user_set=user_id, group_set__name=profile_type),
        ).values_list('slug', flat=True)
    await redis_con.set(perm_cache_key, json.dumps(jsonable_encoder(perm)))
    return perm
