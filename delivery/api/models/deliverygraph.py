from typing import List

from pydantic import parse_obj_as
from tortoise import Model
from tortoise import fields
from tortoise.exceptions import DoesNotExist
from tortoise.expressions import Q

from .. import models
from .. import schemas
from . import fields as custom_fields
from ..context_vars import locale_context


class DeliveryGraph(Model):
    id = fields.IntField(pk=True)
    graph = fields.JSONField(null=False)
    graph_courier = fields.JSONField(null=False, default=list)
    types = custom_fields.CharArrayField(max_length=10)
    partner: fields.ForeignKeyRelation[
        'models.Partner'] = fields.ForeignKeyField(
        'versions.Partner',
        to_field='id',
        null=True,
    )
    name = fields.CharField(max_length=128)
    name_en = fields.CharField(max_length=128, null=True)
    name_kk = fields.CharField(max_length=128, null=True)
    name_ru = fields.CharField(max_length=128, null=True)
    name_zh = fields.CharField(max_length=128, null=True)
    slug = fields.CharField(max_length=80, null=True)

    # type hints
    partner_id: int

    class Meta:
        table = 'deliverygraph'

    @property
    def name(self):
        locale = locale_context.get()
        return getattr(self, f'name_{locale}', self.name_en)


async def deliverygraph_get_list(partner_id: int):
    deliverygraphs = await DeliveryGraph.filter(
        Q(
            Q(partner_id__isnull=True),
            Q(partner_id=partner_id),
            join_type=Q.OR,
        )
    ).values()

    return deliverygraphs


async def deliverygraph_get(deliverygraph_id: int, **kwargs):
    partner_id = kwargs.pop('partner_id')
    try:
        instance = await DeliveryGraph.get(
            Q(
                Q(partner_id__isnull=True),
                Q(partner_id=partner_id),
                join_type=Q.OR,
            ),
            id=deliverygraph_id,
            **kwargs,
        )
        return schemas.DeliveryGraphGet.from_orm(instance)
    except DoesNotExist:
        raise DoesNotExist(
            f'deliverygraph with given ID: {deliverygraph_id} was not found',
        )


async def deliverygraph_list_default():
    default_deliverygraphs = await DeliveryGraph.filter(partner_id__isnull=True)
    return parse_obj_as(List[schemas.DeliveryGraphGet], default_deliverygraphs)


async def deliverygraph_create(
    deliverygraph: schemas.DeliveryGraphCreate,
    **kwargs,
):
    deliverygraph = await DeliveryGraph.create(**deliverygraph.dict(exclude_unset=True), **kwargs)
    return schemas.DeliveryGraphGet.construct(**dict(deliverygraph))


async def deliverygraph_update(
    deliverygraph_id: int, update: schemas.DeliveryGraphUpdate, **kwargs,
):
    deliverygraph = await DeliveryGraph.get(id=deliverygraph_id, **kwargs)

    await deliverygraph.update_from_dict(update.dict(exclude_unset=True)).save()
    return schemas.DeliveryGraphGet.construct(**dict(deliverygraph))


async def deliverygraph_delete(deliverygraph_id: int, **kwargs):
    deliverygraph = await DeliveryGraph.get(id=deliverygraph_id, **kwargs)
    await deliverygraph.delete()
