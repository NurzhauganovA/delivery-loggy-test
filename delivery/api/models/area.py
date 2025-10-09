from typing import List

from fastapi.encoders import jsonable_encoder
from pydantic import parse_obj_as
from tortoise import Model
from tortoise import fields
from tortoise.exceptions import DoesNotExist
from tortoise.expressions import Q
from tortoise.manager import Manager
from tortoise.transactions import atomic
from tortoise.validators import MaxValueValidator
from tortoise.validators import MinValueValidator

from .managers import ArchiveManager
from .. import enums
from .. import models
from .. import schemas


class AreaCannotBeArchived(Exception):
    """Raises if area with provided ID cannot be archived."""


class Area(Model):
    id = fields.IntField(pk=True)
    slug = fields.CharField(max_length=255, null=True)
    scope = fields.JSONField(null=False)
    fill_color = fields.CharField(max_length=15)
    fill_opacity = fields.FloatField(
        validators=[MinValueValidator(0.0), MaxValueValidator(1.0)],
    )
    stroke_color = fields.CharField(max_length=15)
    stroke_opacity = fields.FloatField(
        validators=[MinValueValidator(0.0), MaxValueValidator(1.0)],
    )
    partner = fields.ForeignKeyField(
        'versions.Partner',
        to_field='id',
        on_delete=fields.CASCADE,
        null=False,
    )
    city = fields.ForeignKeyField(
        'versions.City',
        to_field='id',
        on_delete=fields.CASCADE,
        null=False,
    )
    updated_at = fields.DatetimeField(auto_now=True)
    created_at = fields.DatetimeField(auto_now_add=True)
    archived = fields.BooleanField(default=False)

    all_objects = Manager()

    # type hints
    city_id: int
    couriers: fields.ManyToManyRelation['models.ProfileCourier']

    class Config:
        extra = 'forbid'

    class Meta:
        table = 'area'
        manager = ArchiveManager()


async def area_get(area_id: int, default_filter_args: list = None):
    if default_filter_args is None:
        default_filter_args = ()
    try:
        area = await Area.all_objects.filter(*default_filter_args).get(id=area_id)
    except DoesNotExist:
        raise DoesNotExist(
            f'area with given ID: {area_id} was not found',
        )
    return schemas.AreaGet.from_orm(area)


async def area_get_list(default_filter_args: list = None, filter_kwargs: dict = None) -> List[schemas.AreaGet]:
    if default_filter_args is None:
        default_filter_args = ()
    if filter_kwargs is None:
        filter_kwargs = {}
    archived = filter_kwargs.pop('archived', False)
    qs = Area.all_objects.filter(archived=True) if archived else Area.all()
    areas = await qs.filter(*default_filter_args).filter(**filter_kwargs)
    return parse_obj_as(List[schemas.AreaGet], areas)


async def area_create(area: schemas.AreaCreate):
    result = await Area.create(**jsonable_encoder(area))
    return schemas.AreaGet.from_orm(result)


async def area_delete(area_id: int, default_filter_args: list = None):
    if default_filter_args is None:
        default_filter_args = ()
    await Area.all_objects.filter(*default_filter_args).distinct().get(id=area_id).delete()


@atomic()
async def area_archive(area_id: int, default_filter_args: list = None):
    if default_filter_args is None:
        default_filter_args = []
    try:
        area = await Area.all_objects.filter(*default_filter_args).get(id=area_id)
    except DoesNotExist:
        raise DoesNotExist(
            'Area was not found',
        )
    if order_count := await models.Order.filter(
        # !hardcode: as of 'tortoise-orm==0.19.2' can't use __not_in with annotated fields
        Q(
          ~Q(current_status_id=enums.OrderStatus.NEW.value),
            ~Q(current_status_id=enums.OrderStatus.DELIVERED.value),
        ),
        Q(delivery_status__filter={'status': enums.OrderDeliveryStatus.CANCELLED.value}),
        Q(area_id=area_id),
    ).count():
        raise AreaCannotBeArchived(
            f'This area cannot be archived. Untie {order_count} orders first'
        )

    area.archived = True
    couriers = await area.couriers
    await area.couriers.clear()
    await area.save()

    return couriers


@atomic()
async def area_update(area_id: int, update: schemas.AreaUpdate, default_filter_args: list = None):
    if default_filter_args is None:
        default_filter_args = ()
    try:
        area = await Area.all_objects.filter(*default_filter_args).distinct().get(id=area_id)
    except DoesNotExist:
        raise DoesNotExist(
            f'area with given ID: {area_id} was not found',
        )

    await area.update_from_dict(jsonable_encoder(update)).save()
    return schemas.AreaGet.from_orm(area)


async def area_activate(area_id: int, default_filter_args: list = None):
    if default_filter_args is None:
        default_filter_args = ()
    area = await Area.all_objects.filter(*default_filter_args).get(id=area_id)
    area.archived = False
    await area.save()
