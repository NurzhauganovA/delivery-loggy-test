import typing

from pydantic import parse_obj_as
from tortoise import Model
from tortoise import fields
from tortoise.exceptions import DoesNotExist
from tortoise.exceptions import IntegrityError
from tortoise.query_utils import Prefetch
from tortoise.transactions import atomic

from . import fields as custom_fields
from .. import enums
from .. import models
from .. import schemas
from .. import utils
from ..modules.city.infrastructure.db_table import City
from ..modules.shipment_point import PartnerShipmentPoint


class ItemNotFound(Exception):
    """Raises when item not found"""


class ItemCannotBeDeleted(Exception):
    """Raises if item cannot be deleted."""


class ItemPostControlCheckFailure(Exception):
    """Raises if items fails post control check"""


class CityNotInPartnerCityException(Exception):
    """Raises if item don't present in partners city"""


class CityAlreadyInItem(Exception):
    """Raises if item already have provided city"""


class ItemCommonError(Exception):
    """Raises when item creation is failed."""


class Item(Model):
    id = fields.IntField(pk=True)
    name = fields.CharField(max_length=255)
    item_type = fields.CharEnumField(**enums.ItemType.to_kwargs())
    delivery_time = fields.CharField(max_length=5, null=True)
    upload_from_gallery = fields.BooleanField(default=True)
    partner: fields.ForeignKeyNullableRelation[
        'models.Partner'] = fields.ForeignKeyField(
        'versions.Partner',
        to_field='id',
        on_delete=fields.SET_NULL,
        null=True,
        related_name='items',
    )
    category: fields.ForeignKeyNullableRelation[
        'models.Category'
    ] = fields.ForeignKeyField(
        'versions.Category',
        to_field='id',
        on_delete=fields.SET_NULL,
        null=True,
    )
    deliverygraph_set: fields.ManyToManyRelation[
        'models.DeliveryGraph'
    ] = fields.ManyToManyField(
        'versions.DeliveryGraph',
    )
    cities: fields.ManyToManyRelation[
        'City'
    ] = fields.ManyToManyField('versions.City')
    shipment_point_set: fields.ManyToManyRelation[
        'PartnerShipmentPoint'
    ] = fields.ManyToManyField(
        'versions.PartnerShipmentPoint',
        related_name='item_set'
    )
    delivery_type = custom_fields.CharArrayField(
        max_length=7, null=True
    )
    is_delivery_point_exists = fields.BooleanField(default=True)
    has_postcontrol = fields.BooleanField(default=False)
    distribute = fields.BooleanField(default=False)
    accepted_delivery_statuses = custom_fields.CharArrayField(
        max_length=7, null=True
    )
    message_for_noncall = fields.TextField(null=True)
    courier_appointed_sms = fields.TextField(null=True)
    courier_appointed_sms_on = fields.BooleanField(default=False)
    item_identification_code = fields.CharField(
        max_length=256,
        null=True,
    )

    # reverse relation type hints that won't touch the db.
    orders: fields.ForeignKeyRelation['models.Order']
    postcontrol_config_set: fields.ReverseRelation['models.PostControlConfig']
    days_to_delivery = fields.IntField(null=True)
    partner_id: int
    category_id: int
    deliverygraph_id: int

    class Config:
        extra = 'forbid'

    class Meta:
        table = 'item'

    def __str__(self) -> str:
        return f'{self.id} - {self.name}'


async def itemshipmentpoints_create(
    itemshipmentpoints: schemas.ItemShipmentPointCreate,
    default_filter_args,
    shipment_point_kwargs,
):
    try:
        item = await Item.get(id=itemshipmentpoints.item_id, *default_filter_args)
    except DoesNotExist:
        raise DoesNotExist(
            f'Item with given ID: {itemshipmentpoints.item_id} was not found',
        )
    try:
        shipmen_point = await PartnerShipmentPoint.get(
            id=itemshipmentpoints.shipment_point_id,
            **shipment_point_kwargs,
        )
    except DoesNotExist:
        raise DoesNotExist(
            f'Shipment point with given ID {itemshipmentpoints.shipment_point_id} '
            f'was not found',
        )
    await item.shipment_point_set.add(shipmen_point)


# TODO: Apply ordering
async def item_get_list(default_filter_args, filter_args):
    result = await models.Item.filter(
        *default_filter_args, *filter_args
    ).distinct().prefetch_related(
        Prefetch('deliverygraph_set', models.DeliveryGraph.all(), 'deliverygraphs'),
        'cities',
    ).select_related('partner', 'category')

    return parse_obj_as(typing.List[schemas.ItemGet], result)


async def item_get(
    item_id: int,
    default_filter_args,
):
    try:
        item_obj = await Item.filter(*default_filter_args).distinct().get(id=item_id).prefetch_related(
            'cities',
            Prefetch('deliverygraph_set', models.DeliveryGraph.all(), 'deliverygraphs'),
            Prefetch(
                relation='postcontrol_config_set',
                queryset=models.PostControlConfig.filter(
                    parent_config_id__isnull=True,
                ).prefetch_related(
                    Prefetch('inner_param_set', models.PostControlConfig.all(), 'inner_params'),
                ),
                to_attr='postcontrol_configs',
            ),
        ).select_related('partner', 'category')

    except DoesNotExist:
        raise DoesNotExist(
            f'Item with provided ID: {item_id} was not found',
        )

    item = schemas.ItemGet.from_orm(item_obj)
    return item


async def item_cities_add(
    item_id: int,
    city_id: int,
    default_filter_args,
):
    try:
        item = await Item.get(id=item_id, *default_filter_args)
    except DoesNotExist:
        raise DoesNotExist(
            f'Item with given ID: {item_id} was not found',
        )
    try:
        city = await City.get(id=city_id)
    except DoesNotExist:
        raise DoesNotExist(
            'City was not found'
        )

    await item.cities.add(city)


@atomic()
async def item_create(
    payload: schemas.ItemCreate,
):
    payload_dict = payload.dict()
    deliverygraph_ids = payload_dict.pop('deliverygraphs')
    deliverygraph_types = await models.DeliveryGraph.filter(
        id__in=deliverygraph_ids,
    ).values_list('types', flat=True)
    deliverygraphs = await models.DeliveryGraph.filter(
        id__in=deliverygraph_ids,
    )
    icons = [graph['icon'] for deliverygraph in deliverygraphs for graph in
             deliverygraph.graph]
    payload_dict['has_postcontrol'] = enums.DeliveryGraphIcons.POST_CONTROL in icons
    flatten_deliverygraphs = [type for types in deliverygraph_types for type in types]
    if len(flatten_deliverygraphs) != len(set(flatten_deliverygraphs)):
        raise IntegrityError(
            f'There are more than one deliverygraph for given types',
        )

    for delivery_type in payload_dict['delivery_type']:
        if delivery_type not in flatten_deliverygraphs:
            raise IntegrityError(
                f'You should select respective deliverygraph for type: {delivery_type}',
            )

    shipment_points_ids = payload_dict.pop('shipment_points')
    shipment_points = []
    if shipment_points_ids:
        shipment_points = await PartnerShipmentPoint.filter(
            id__in=shipment_points_ids,
        )
    cities_ids = payload_dict.pop('cities', [])
    cities = await City.filter(id__in=cities_ids) if cities_ids else []
    postcontrol_configs = payload_dict.pop('postcontrol_configs', [])

    created_item = await Item.create(**payload_dict)

    await create_postcontrol_config_objects(postcontrol_configs, created_item.id)

    await created_item.deliverygraph_set.add(*deliverygraphs)
    if shipment_points:
        await created_item.shipment_point_set.add(*shipment_points)
    if cities:
        await created_item.cities.add(*cities)

    await created_item.fetch_related('category', 'partner')

    created_item.deliverygraphs = await created_item.deliverygraph_set
    await created_item.fetch_related('cities')
    created_item.postcontrol_configs = await created_item.postcontrol_config_set.filter(
        parent_config_id__isnull=True,
    ).prefetch_related(
        Prefetch(
            relation='inner_param_set',
            queryset=models.PostControlConfig.filter(parent_config_id__isnull=False),
            to_attr='inner_params',
        ),
    )
    return schemas.ItemGet.from_orm(created_item)


async def create_postcontrol_config_objects(postcontrol_configs: list, item_id: int):
    for postcontrol_config in postcontrol_configs:
        inner_params = postcontrol_config.pop('inner_params', [])
        config_obj = await models.PostControlConfig.create(item_id=item_id, **postcontrol_config)
        inner_objects = [
            models.PostControlConfig(item_id=item_id, parent_config=config_obj, **inner) for inner in inner_params
        ]
        await models.PostControlConfig.bulk_create(inner_objects, 50)


async def update_postcontrol_config_objects(postcontrol_configs: list, item_id: int):
    configs_to_keep = []
    for postcontrol_config in postcontrol_configs:
        inner_params = postcontrol_config.pop('inner_params', [])
        if config_id := postcontrol_config.get('id'):
            try:
                config_obj = await models.PostControlConfig.get(item_id=item_id, id=config_id)
                await config_obj.update_from_dict(postcontrol_config).save()
            except DoesNotExist:
                raise DoesNotExist(f'PostControl object with ID: {config_id} was not found')
        else:
            config_obj = await models.PostControlConfig.create(item_id=item_id, **postcontrol_config)
        configs_to_keep.append(config_obj.id)
        inner_params_to_keep = []
        for inner_param in inner_params:
            if param_id := inner_param.get('id'):
                try:
                    inner_object = await models.PostControlConfig.get(
                        parent_config=config_obj,
                        id=param_id,
                    )
                    await inner_object.update_from_dict(inner_param).save()
                except DoesNotExist:
                    raise DoesNotExist(f'PostControl object with ID: {param_id} was not found')
            else:
                inner_object = await models.PostControlConfig.create(
                    parent_config=config_obj,
                    item_id=config_obj.item_id,
                    **inner_param,
                )
            inner_params_to_keep.append(inner_object.id)

        # delete all configs not listed in update payload
        await models.PostControlConfig.filter(parent_config=config_obj, id__not_in=inner_params_to_keep).delete()
    await models.PostControlConfig.filter(
        item_id=item_id,
        parent_config_id__isnull=True,
        id__not_in=configs_to_keep,
    ).delete()


@atomic()
async def item_update(
    item_id: int,
    payload: schemas.ItemUpdate | schemas.ItemPartialUpdate,
    default_filter_args: list = None,
) -> schemas.ItemGet:
    if default_filter_args is None:
        default_filter_args = []
    try:
        item = await Item.get(*default_filter_args, id=item_id)
    except DoesNotExist:
        raise DoesNotExist(
            f'Item with given ID: {item_id} was not found',
        )

    payload_dict = payload.dict(exclude_unset=True)
    if deliverygraph_ids := payload_dict.pop('deliverygraphs', []):
        deliverygraph_types = await models.DeliveryGraph.filter(
            id__in=deliverygraph_ids,
        ).values_list('types', flat=True)
        deliverygraphs = await models.DeliveryGraph.filter(
            id__in=deliverygraph_ids,
        )
        icons = [graph['icon'] for deliverygraph in deliverygraphs for graph in
                 deliverygraph.graph]
        payload_dict['has_postcontrol'] = enums.DeliveryGraphIcons.POST_CONTROL in icons
        flatten_deliverygraphs = [type for types in deliverygraph_types for type in
                                  types]
        if len(flatten_deliverygraphs) != len(set(flatten_deliverygraphs)):
            raise IntegrityError(
                f'There are more than one deliverygraph for given types',
            )

        for delivery_type in payload_dict.get('delivery_type') or item.delivery_type:
            if delivery_type not in flatten_deliverygraphs:
                raise IntegrityError(
                    f'You should select respective deliverygraph '
                    f'for type: {delivery_type}',
                )
        await item.deliverygraph_set.clear()
        if deliverygraphs:
            await item.deliverygraph_set.add(*deliverygraphs)
    if shipment_point_ids := payload_dict.pop('shipment_points', None):
        shipment_points = await PartnerShipmentPoint.filter(
            id__in=shipment_point_ids,
        )
        await item.shipment_point_set.clear()
        if shipment_points:
            await item.shipment_point_set.add(*shipment_points)

    if city_ids := payload_dict.pop('cities', None):
        cities = await City.filter(id__in=city_ids)
        await item.cities.clear()
        if cities:
            await item.cities.add(*cities)

    postcontrol_configs = payload_dict.pop('postcontrol_configs', [])

    await item.update_from_dict(payload_dict).save()

    await update_postcontrol_config_objects(postcontrol_configs, item_id)

    await item.fetch_related('category', 'partner', 'cities')
    item.deliverygraphs = await item.deliverygraph_set
    item.postcontrol_configs = await models.PostControlConfig.filter(
        item_id=item_id,
        parent_config_id__isnull=True,
    ).prefetch_related(
        Prefetch(
            relation='inner_param_set',
            queryset=models.PostControlConfig.filter(
                parent_config_id__isnull=False,
                item_id=item_id,
            ),
            to_attr='inner_params',
        ),
    )

    return schemas.ItemGet.from_orm(item)


async def item_delete(item_id: int, default_filter_args) -> None:
    try:
        item = await Item.get(id=item_id, *default_filter_args)
    except DoesNotExist:
        raise DoesNotExist(
            f'Item with given ID: {item_id} was not found',
        )
    await item.delete()


async def item_delete_bulk(item_ids: schemas.ItemIDsList, default_filter_args) -> None:
    try:
        qs = Item.filter(id__in=item_ids.items, *default_filter_args)
        fetched_item_ids = await qs.values_list('id', flat=True)
        for id in item_ids.items:
            if id not in fetched_item_ids:
                raise DoesNotExist(
                    f'Item with given ID: {id} was not found',
                )
        await qs.delete()
    except IntegrityError:
        raise IntegrityError(
            'Items with provided id list cannot be deleted',
        )
