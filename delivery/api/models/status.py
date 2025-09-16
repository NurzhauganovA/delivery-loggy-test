import typing
from typing import Type, Optional

from fastapi_pagination.ext.tortoise import paginate
from pydantic import parse_obj_as
from tortoise import Model, BaseDBAsyncClient
from tortoise import fields
from tortoise.exceptions import DoesNotExist
from tortoise.signals import pre_save

from .utils import unique_slug_generator
from .. import models
from .. import schemas
from ..context_vars import locale_context


class StatusInOtherDependings(Exception):
    """Raises if status with provided ID in after field of other status."""


class Status(Model):
    id = fields.IntField(pk=True)
    code = fields.CharField(unique=True, max_length=50, null=True)
    icon = fields.CharField(max_length=50)
    name_en = fields.CharField(max_length=50, null=True)
    name_kk = fields.CharField(max_length=50, null=True)
    name_ru = fields.CharField(max_length=50, null=True)
    name_zh = fields.CharField(max_length=50, null=True)
    slug = fields.CharField(max_length=80)
    is_optional = fields.BooleanField(default=False)
    partner = fields.ForeignKeyField(
        'versions.Partner',
        to_field='id',
        related_name='statuses',
        null=True,
    )
    after = fields.JSONField(null=True)

    # type hints
    order_set: fields.ManyToManyRelation['models.Order']
    partner_id: int

    class Meta:
        unique_together = (('name', 'partner'),)
        table = 'status'

    @property
    def name(self):
        locale = locale_context.get()
        return getattr(self, f'name_{locale}', self.name_en)


async def status_get_list(pagination_params=None, **kwargs):
    qs = Status.filter(**kwargs)
    if pagination_params:
        return await paginate(qs, pagination_params)
    return parse_obj_as(typing.List[schemas.StatusGet], await qs)


async def status_get(status_id: int):
    try:
        status = await Status.get(id=status_id)
        return schemas.StatusGet.from_orm(status)
    except DoesNotExist:
        raise DoesNotExist(
            f'Status with provided ID: {status_id} was not found',
        )


async def status_get_by_slug(slug: str | typing.Any):
    status = await Status.filter(slug=slug).first()
    if status:
        return schemas.StatusGet.from_orm(status)


async def status_create(status: schemas.StatusCreate):
    status_dict = status.dict(exclude_unset=True)

    for depend_status in status.after:
        try:
            await Status.get(id=depend_status.id)
        except DoesNotExist:
            raise DoesNotExist(
                f'Dependency status with id: {depend_status.id} was not found',
            )
    result = await Status.create(**status_dict)
    return schemas.StatusGet.from_orm(result)


async def status_update(status_id: int,
                        update: schemas.StatusUpdate):
    try:
        status = await Status.get(id=status_id)
    except DoesNotExist:
        raise DoesNotExist(
            f'Status with provided ID: {status_id} was not found')

    reference = [{
        'id': status.id,
        'name': status.name,
    }]
    contains_statuses = await Status.filter(
        after__contains=reference,
    )

    await status.update_from_dict(update.dict(exclude_unset=True)).save()

    for contains_status in contains_statuses:
        for key, val in enumerate(contains_status.after):
            if val == reference[0]:
                contains_status.after[key]['name'] = update.name
                await contains_status.save(update_fields=['after'])
    await status.refresh_from_db()

    return schemas.StatusGet.from_orm(status)


async def status_delete(status_id: int, force: bool = True):
    try:
        deleting_status = await Status.get(id=status_id)
    except DoesNotExist:
        raise DoesNotExist(
            f'Status with given ID: {status_id} was not found',
        )
    if force:
        contains_statuses = await Status.filter(
            after__contains=[{
                'id': deleting_status.id,
                'name': deleting_status.name,
            }],
        ).values_list('name', flat=True)
        if contains_statuses:
            raise StatusInOtherDependings(
                'Dependent statuses with  '
                '"{}" names, exists'.format(', '.join(contains_statuses)),
            )
    await deleting_status.delete()


@pre_save(Status)
async def status_set_slug(
    _sender: Type[Status],
    instance: Status,
    _using_db: Optional[BaseDBAsyncClient],
    _update_fields,
):
    if not instance.slug:
        instance.slug = await unique_slug_generator(instance)
