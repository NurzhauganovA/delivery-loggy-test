import datetime
import io
import json
import typing
from tempfile import SpooledTemporaryFile
from typing import List, Iterable
from typing import Optional
from typing import Type
from typing import Union
from zoneinfo import ZoneInfo

import loguru
from tortoise.transactions import in_transaction
import xlsxwriter
from fastapi_pagination.ext.tortoise import paginate
from loguru import logger
from pydantic import parse_obj_as
from shapely.geometry import Point
from shapely.geometry.polygon import Polygon
from starlette.datastructures import UploadFile
from tortoise import BaseDBAsyncClient
from tortoise import Model
from tortoise import fields
from tortoise import signals
from tortoise.exceptions import DoesNotExist
from tortoise.exceptions import IntegrityError
from tortoise.expressions import RawSQL
from tortoise.expressions import Subquery
from tortoise.functions import Count
from tortoise.manager import Manager
from tortoise.query_utils import Prefetch
from tortoise.queryset import Q
from tortoise.timezone import now
from tortoise.transactions import atomic

from api.modules.delivery_point.infrastructure.repository import DeliveryPointRepository
from api.modules.shipment_point.infrastructure.repository import ShipmentPointRepository
from .fields import ArrayField
from .managers import ArchiveManager
from .partner_callbacks import get_headers
from .profile import ProfileCourier
from api import exceptions, enums
from .. import common
from .. import models
from .. import redis_module
from .. import schemas
from .. import services
from ..conf import conf
from ..controllers.websocket_managers import websocket_manager
from ..enums import *
from ..enums.descriptions import delivery_status_description
from ..modules.city.infrastructure.db_table import City
from ..modules.city.infrastructure.repository import CityRepository
from ..modules.delivery_point import DeliveryPoint
from ..modules.delivery_point.schemas import DeliveryPointCreate, DeliveryPointGet
from ..modules.container import ModulesActionsDiContainer
from ..modules.order import OrderGroup
from ..modules.order_chain import OrderChainStage
from ..modules.shipment_point import PartnerShipmentPoint
from ..modules.shipment_point.errors import PartnerShipmentPointNotFoundError
from ..modules.shipment_point.schemas import PartnerShipmentPointGet
from ..schemas import UserCurrent
from ..schemas.deliverygraph import DeliveryGraphItemGet
from ..schemas.order_payload import CardPayload, POSTerminalPayload
from ..services import router, sms
from ..services.excel_loader.excel_loader import prepare_orders_for_report
from ..services.sms.notification import send_courier_assigned_notification
from ..services.sms.notification import send_feedback_link
from ..services.sms.notification import send_post_control_otp
from api.domain.pan import Pan

from api.adapters.freedom_bank_otp import FreedomBankOTPAdapter
from .publisher import publish_callback, call_task


class OrderAlreadyExists(Exception):
    """Raises if order with provided ID already exists."""


class StatusAfterError(Exception):
    """Raises if old status of order not provided in new status dependencies"""


class StatusAlreadyCurrent(Exception):
    """Raises if status with provided ID is already current."""


class OrderNotFound(common.BaseNotFoundError):
    """Raises if order with provided ID not found."""


class OrderAlreadyDelivered(Exception):
    """Raises if order with provided ID already delivered."""


class OrderAddressNotFound(Exception):
    """Raises if address with provided ID not found."""


class OrderEntitiesError(Exception):
    """Raises if error linked to order entities."""


class OrderIsNotSubjectToPostControl(Exception):
    """Raises if the order is not subject to post control"""


class OrderPostControlMaximumNumberLimitExceeded(Exception):
    """Raises when number of PostControl instances for an order exceeded
    limit"""


class OrderReceiverIINNotProvided(Exception):
    """Raises when product have a post_control status and not provides
    receiver_iin"""


class OrderSmsMaximumLimitExceeded(Exception):
    """Raises when sms sending is reached maximum."""


class OrderSmsCheckError(Exception):
    """Raises when sms code verification fails"""


class NotDistributionOrdersError(Exception):
    """Raises when not orders without courier"""


class NotDistributionCouriersError(Exception):
    """Raises when not couriers for order destribution"""


class DistanceMatrixError(Exception):
    """Raises when distance matrix are lost"""


class OrderPostponeError(Exception):
    """Raises when order postponed without delivery datetime"""


class InvalidPointCoords(Exception):
    """Raises when all polygons do not contain point"""


class OrderAlreadyHaveCourierError(Exception):
    """Raises when all polygons do not contain point"""


class Order(Model):
    id = fields.IntField(pk=True)
    city: fields.ForeignKeyNullableRelation['City'] = fields.ForeignKeyField(
        'versions.City',
        to_field='id',
        on_delete=fields.SET_NULL,
        null=True,
    )
    partner: fields.ForeignKeyRelation['models.Partner'] = fields.ForeignKeyField(
        'versions.Partner',
        to_field='id',
        on_delete=fields.RESTRICT,
        null=False,
        related_name='orders',
    )
    courier: fields.ForeignKeyNullableRelation[
        'ProfileCourier'] = fields.ForeignKeyField(
        'versions.ProfileCourier',
        to_field='id',
        on_delete=fields.SET_NULL,
        null=True,
    )
    item: fields.ForeignKeyRelation['models.Item'] = fields.ForeignKeyField(
        'versions.Item',
        to_field='id',
        on_delete=fields.CASCADE,
        null=False,
    )
    deliverygraph: fields.ForeignKeyRelation[
        'models.DeliveryGraph'
    ] = fields.ForeignKeyField(
        'versions.DeliveryGraph',
        fields.RESTRICT,
    )
    shipment_point: fields.ForeignKeyNullableRelation[
        'PartnerShipmentPoint'
    ] = fields.ForeignKeyField(
        'versions.PartnerShipmentPoint',
        'orders',
        fields.SET_NULL,
        null=True,
    )
    delivery_point: fields.ForeignKeyNullableRelation['DeliveryPoint'] = fields.ForeignKeyField(
        'versions.DeliveryPoint',
        'orders',
        fields.RESTRICT,
        null=True,
    )
    type = fields.CharEnumField(**OrderType.to_kwargs())
    created_at = fields.DatetimeField(auto_now_add=True)
    archived = fields.BooleanField(default=False)
    initial_delivery_datetime = fields.DatetimeField(null=True)
    delivery_datetime = fields.DatetimeField(null=True)
    actual_delivery_datetime = fields.DatetimeField(null=True)
    delivery_status = fields.JSONField(
        default={
            'status': None,
            'reason': None,
            'comment': None,
            'datetime': None,
        },
    )
    receiver_name = fields.CharField(max_length=255, null=True)
    receiver_iin = fields.CharField(min_length=12, max_length=12, null=True)
    receiver_phone_number = fields.CharField(min_length=13, max_length=255)
    comment = fields.CharField(max_length=255, null=True)
    position = fields.IntField(null=True)
    partner_order_id = fields.CharField(max_length=255, null=True)
    main_order = fields.ForeignKeyField(
        'versions.Order',
        to_field='id',
        on_delete=fields.CASCADE,
        null=True,
    )
    current_status: fields.ForeignKeyNullableRelation['models.Status'] = fields.ForeignKeyField(
        'versions.Status',
        to_field='id',
        on_delete=fields.SET_NULL,
        null=True
    )
    area: fields.ForeignKeyNullableRelation['models.Area'] = fields.ForeignKeyField(
        'versions.Area',
        'order_set',
        fields.RESTRICT,
        null=True,
    )
    created_by = fields.CharEnumField(
        **CreatedType.to_kwargs(default=CreatedType.SERVICE)
    )
    callbacks = fields.JSONField(default={})
    order_group = fields.ForeignKeyField(
        'versions.OrderGroup',
        to_field='id',
        on_delete=fields.CASCADE,
        null=True,
        related_name='orders',

    )
    revised = fields.BooleanField(default=False)
    allow_courier_assign = fields.BooleanField(default=True)
    idn = fields.CharField(max_length=255, null=True)
    manager = fields.CharField(max_length=255, null=True)

    # reverse relation type hints that won't touch the db.
    geolocation: fields.OneToOneNullableRelation['OrderGeolocation']
    postcontrol_set: fields.ReverseRelation['models.PostControl']
    order_chain_stages_set: fields.ReverseRelation['OrderChainStage']
    otp_set: fields.ReverseRelation['models.SMSPostControl']
    product: fields.OneToOneRelation['models.Product']
    courier_id: int
    deliverygraph_id: int
    address_set: fields.ManyToManyRelation['OrderAddress']
    shipment_point_id: int | None
    delivery_point_id: int | None
    status_set: fields.ManyToManyRelation['OrderStatuses']
    item_id: int
    main_order: Optional[int]
    order_group: Optional[int]
    partner_id: int
    city_id: int
    current_status_id: int

    all_objects = Manager()

    class Config:
        extra = 'forbid'

    class Meta:
        table = 'order'
        manager = ArchiveManager()
        ordering = ('-created_at',)
        unique_together = (
            ('partner_order_id', 'partner_id'),
        )

    async def save(
        self,
        using_db: Optional[BaseDBAsyncClient] = None,
        update_fields: Optional[Iterable[str]] = None,
        force_create: bool = False,
        force_update: bool = False,
    ) -> None:
        """
        Creates/Updates the current model object.

        :param update_fields: If provided, it should be a tuple/list of fields by name.

            This is the subset of fields that should be updated.
            If the object needs to be created ``update_fields`` will be ignored.
        :param using_db: Specific DB connection to use instead of default bound
        :param force_create: Forces creation of the record
        :param force_update: Forces updating of the record

        :raises IncompleteInstanceError: If the model is partial and the fields are not available for persistence.
        :raises IntegrityError: If the model can't be created or updated (specifically if force_create or force_update has been set)

        We overrided this method to achieve old and new state of the object, hence send respective notifications
        on model change.
        """
        save_coro = super().save(using_db, update_fields, force_create, force_update)

        if not self.id:
            self.initial_delivery_datetime = self.delivery_datetime
            result = await save_coro
            if not self.courier_id:
                return result
            await send_new_order_to_courier(self)
            return result
        if not (old_obj := await self.__class__.get_or_none(id=self.id)):
            return await save_coro

        await save_coro

        if self.courier_id and self.courier_id != old_obj.courier_id:
            await send_new_order_to_courier(self)

        if self.delivery_status != old_obj.delivery_status:
            await websocket_manager.send_message_for_managers(
                self.partner_id, {
                    'type': MessageType.DELIVERY_STATUS_UPDATE,
                    'data': {
                        'order_id': self.id,
                        'name': self.delivery_status.get('status'),
                    }
                })

    @property
    async def city_tz(self) -> ZoneInfo:
        if not isinstance(self.city, City):
            await self.fetch_related('city')
        if self.city is None:
            return ZoneInfo('UTC')
        return self.city.tz

    @property
    async def localtime(self) -> datetime.datetime:
        current_time = now()
        city_tz = await self.city_tz
        return current_time + city_tz.utcoffset(current_time)


class OrderAddress(Model):
    position = fields.SmallIntField(null=False, default=1)
    type = fields.CharEnumField(
        **AddressType.to_kwargs(
            default=AddressType.DELIVERY_POINT,
        ),
    )
    order: fields.ForeignKeyNullableRelation[
        'models.Order'] = fields.ForeignKeyField(
        'versions.Order',
        'address_set',
        on_delete=fields.CASCADE,
        null=False,
    )
    place: fields.ForeignKeyNullableRelation[
        'models.Place'] = fields.ForeignKeyField(
        'versions.Place',
        to_field='id',
        on_delete=fields.CASCADE,
    )

    # type hints
    order_id: int
    place_id: int

    class Meta:
        table = 'order.addresses'


class OrderStatuses(Model):
    id = fields.IntField(pk=True)
    created_at = fields.DatetimeField(auto_now_add=True)
    order: fields.ForeignKeyRelation['models.Order'] = fields.ForeignKeyField(
        'versions.Order',
        'status_set',
        fields.CASCADE,
    )
    status: fields.ForeignKeyRelation['models.Status'] = fields.ForeignKeyField(
        'versions.Status',
        'order_set',
        fields.RESTRICT,
    )

    # type hints
    order_id: int
    status_id: int

    class Meta:
        table = 'order.statuses'
        ordering = ('created_at',)
        unique_together = ('order', 'status')

    async def delete(
        self,
        using_db: Optional[BaseDBAsyncClient] = None,
    ) -> None:
        if self.status.name == OrderStatus.NEW:
            raise IntegrityError(
                'You cannot delete default status')
        await super().delete(using_db)


class OrderGeolocation(Model):
    order: fields.OneToOneRelation['Order'] = fields.OneToOneField(
        'versions.Order',
        'geolocation',
        fields.CASCADE,
    )
    courier: fields.ForeignKeyRelation['models.ProfileCourier'] = fields.ForeignKeyField(
        'versions.ProfileCourier',
        'deliveries',
        fields.CASCADE,
    )
    at_client_point = ArrayField(
        fields.DecimalField(max_digits=11, decimal_places=8),
        min_length=2,
        max_length=2,
        null=True,
    )
    code_sent_point = ArrayField(
        fields.DecimalField(max_digits=11, decimal_places=8),
        min_length=2,
        max_length=2,
        null=True,
    )
    distance = fields.DecimalField(10, 3, default=0)
    speed = fields.DecimalField(5, 2, default=0)
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    #  type hints:
    courier_id: int
    order_id: int

    class Meta:
        table = 'order_geolocations'


async def order_fill_old_addresses_field(order_schema: schemas.OrderGet):
    order_schema.addresses = []
    if order_schema.shipment_point_id:
        sp_repo = ShipmentPointRepository()
        s_point: PartnerShipmentPointGet = await sp_repo.get_by_id(
            [], entity_id=order_schema.shipment_point_id)
        order_schema.addresses.append(
            schemas.OrderAddressGet(
                position=0,
                type=AddressType.SHIPMENT_POINT,
                id=s_point.id,
                place=schemas.PlaceGet(
                    id=s_point.id,
                    latitude=s_point.latitude,
                    longitude=s_point.longitude,
                    address=s_point.address,
                    city_id=s_point.city.id,
                )
            )
        )
    if order_schema.delivery_point_id:
        dp_repo = DeliveryPointRepository()
        d_point: DeliveryPointGet = await dp_repo.get_by_id(
            [], entity_id=order_schema.delivery_point_id)
        order_schema.addresses.append(
            schemas.OrderAddressGet(
                position=1,
                type=AddressType.DELIVERY_POINT,
                id=d_point.id,
                place=schemas.PlaceGet(
                    id=d_point.id,
                    latitude=d_point.latitude,
                    longitude=d_point.longitude,
                    address=d_point.address,
                )
            )
        )


async def order_address_get_list(order_id: int) -> list:
    addresses = await OrderAddress.filter(order_id=order_id).prefetch_related(
        'place')
    result = []
    # TODO: Make test for 'for' loop
    for address in addresses:
        response = schemas.OrderAddressGet(
            id=address.id,
            place=address.place,
            position=address.position,
            type=address.type,
        )
        result.append(response)
    if not result:
        order_obj = await Order.get(id=order_id)
        if order_obj.shipment_point_id:
            sp_repo = ShipmentPointRepository()
            s_point: PartnerShipmentPointGet = await sp_repo.get_by_id(
                [], entity_id=order_obj.shipment_point_id)
            result.append(
                schemas.OrderAddressGet(
                    position=0,
                    type=AddressType.SHIPMENT_POINT,
                    id=s_point.id,
                    place=schemas.PlaceGet(
                        id=s_point.id,
                        latitude=s_point.latitude,
                        longitude=s_point.longitude,
                        address=s_point.address,
                        city_id=s_point.city.id,
                    )
                )
            )
        if order_obj.delivery_point_id:
            dp_repo = DeliveryPointRepository()
            d_point: DeliveryPointGet = await dp_repo.get_by_id(
                [], entity_id=order_obj.delivery_point_id)
            result.append(
                schemas.OrderAddressGet(
                    position=1,
                    type=AddressType.DELIVERY_POINT,
                    id=d_point.id,
                    place=schemas.PlaceGet(
                        id=d_point.id,
                        latitude=d_point.latitude,
                        longitude=d_point.longitude,
                        address=d_point.address,
                    )
                )
            )
    return result


async def orders_get_count(default_filter_args, filter_args) -> int:
    has_ready_for_shipment = f"order__deliverygraph.graph @? '$.slug[*] ? (@ == \"{StatusSlug.READY_FOR_SHIPMENT}\")'"

    orders = await Order.all_objects.annotate(
        has_ready_for_shipment=RawSQL(has_ready_for_shipment),
    ).filter(
        *default_filter_args,
        deliverygraph__id__isnull=False,  # needed to join deliverygraph table only.
    ).filter(*filter_args).distinct().count()

    return orders


async def order_statuses_get_count(order_default_args, order_group_default_args, profile_type):
    current_status_sql = """
            (SELECT "name" FROM "order_group_statuses" WHERE "order_group_id" = "order_group"."id" 
            ORDER BY "created_at" DESC LIMIT 1)
        """
    sts, d_sts = StatusSlug, OrderDeliveryStatus
    d_statuses_for_filter = (
        d_sts.BEING_FINALIZED.value,
        d_sts.NONCALL.value,
        d_sts.POSTPONED.value,
        d_sts.REQUESTED_TO_CANCEL.value,
        d_sts.CANCELLED.value,
        d_sts.CANCELED_AT_CLIENT.value,
        d_sts.RESCHEDULED.value,
        d_sts.IS_DELIVERED.value,
    )
    result = {status: 0 for status in d_statuses_for_filter}

    orders = Order.filter(*order_default_args)

    counts_d_status_orders = orders.annotate(
        status=RawSQL("delivery_status ->> 'status'")
    ).filter(
        status__in=d_statuses_for_filter
    ).group_by('status').annotate(count=Count('id')).values('status', 'count')

    counts_d_status_orders = await counts_d_status_orders

    for status in counts_d_status_orders:
        result[status['status']] = status['count']

    result['export_group'] = await OrderGroup.annotate(
        current_status=RawSQL(current_status_sql)
    ).filter(*order_group_default_args).distinct().count()
    result[sts.NEW] = await orders.filter(delivery_status__filter={'status__isnull': True}).count()
    result[d_sts.BEING_FINALIZED] = await orders.filter(
        delivery_status__filter={
            'status__in': (d_sts.BEING_FINALIZED.value, d_sts.BEING_FINALIZED_ON_CANCEL.value),
        },
    ).count()
    if profile_type == ProfileType.COURIER:
        result[sts.POST_CONTROL] = await orders.filter(
            current_status__slug__in=(sts.POST_CONTROL.value, sts.POST_CONTROL_BANK.value)
        ).count()
    else:
        result[sts.POST_CONTROL] = await orders.filter(
            current_status__slug=sts.POST_CONTROL.value).count()
    result[d_sts.TO_CALL_POINT] = await orders.exclude(
        current_status__slug__in=[
            sts.POST_CONTROL.value,
            sts.POST_CONTROL_BANK.value,
        ]
    ).filter(
        delivery_status__filter={'status': d_sts.TO_CALL_POINT.value}
    ).count()

    return result


async def get_current_orders_for_courier(courier_id):
    courier_obj = await models.ProfileCourier.get(id=courier_id).select_related('city')
    courier_time = await courier_obj.localtime
    return await Order.filter(
        ~Q(delivery_status__filter={
            'status': OrderDeliveryStatus.IS_DELIVERED.value}
        ),
        delivery_datetime__year=courier_time.year,
        delivery_datetime__month=courier_time.month,
        delivery_datetime__day=courier_time.day,
        courier_id=courier_id, ).order_by('-delivery_datetime')


async def order_get_list(pagination_params, default_filter_args, filter_args, profile_type: ProfileType = None):
    has_ready_for_shipment = f"order__deliverygraph.graph @? '$.slug[*] ? (@ == \"{StatusSlug.READY_FOR_SHIPMENT}\")'"

    instance_qs = Order.all_objects.annotate(
        has_ready_for_shipment=RawSQL(has_ready_for_shipment),
    ).filter(
        *default_filter_args,
        deliverygraph__id__isnull=False,  # needed to join deliverygraph table only.
    ).filter(*filter_args).order_by('-created_at').distinct()
    qs = instance_qs.prefetch_related(
        Prefetch('status_set', OrderStatuses.all().prefetch_related('status'),
                 'statuses'),
        Prefetch('address_set', OrderAddress.all().prefetch_related('place'),
                 'addresses'),
        Prefetch(
            'order_chain_stages_set', OrderChainStage.all(), 'order_chain_stages',
        ),
    ).select_related('area', 'city', 'courier__user', 'item', 'deliverygraph', 'partner',)
    paginated_result = await paginate(qs, params=pagination_params)
    for order_item in getattr(paginated_result, 'items'):
        await order_fill_old_addresses_field(order_item)
        if profile_type == ProfileType.COURIER:
            if order_item.current_status_id == int(OrderStatus.ENDED.value):
                order_item.delivery_status = {
                    'status': OrderDeliveryStatus.IS_DELIVERED.value,
                    'datetime': None,
                    'reason': None,
                    'comment': None,
                }

    return paginated_result


async def order_get_list_mobile(pagination_params, default_filter_args, filter_args):
    has_ready_for_shipment = f"order__deliverygraph.graph @? '$.slug[*] ? (@ == \"{StatusSlug.READY_FOR_SHIPMENT}\")'"

    instance_qs = Order.all_objects.annotate(
        has_ready_for_shipment=RawSQL(has_ready_for_shipment),
    ).filter(
        *default_filter_args,
        deliverygraph__id__isnull=False,  # needed to join deliverygraph table only.
    ).filter(*filter_args).order_by('-created_at').distinct()
    qs = instance_qs.prefetch_related(
        Prefetch('status_set', OrderStatuses.all().prefetch_related('status'),
                 'statuses'),
        Prefetch('address_set', OrderAddress.all().prefetch_related('place'),
                 'addresses'),
        Prefetch(
            'order_chain_stages_set', OrderChainStage.all(), 'order_chain_stages',
        ),
    ).select_related('area', 'city', 'courier__user', 'item', 'deliverygraph', 'partner', 'product')
    paginated_result = await paginate(qs, params=pagination_params)
    for order_item in getattr(paginated_result, 'items'):
        await order_fill_old_addresses_field(order_item)
        if order_item.current_status_id == int(OrderStatus.ENDED.value):
            order_item.delivery_status = {
                'status': OrderDeliveryStatus.IS_DELIVERED.value,
                'datetime': None,
                'reason': None,
                'comment': None,
            }

    return paginated_result


async def order_get_list_v2(pagination_params, default_filter_args, filter_args, profile_type: ProfileType = None):
    has_ready_for_shipment = f"order__deliverygraph.graph @? '$.slug[*] ? (@ == \"{StatusSlug.READY_FOR_SHIPMENT}\")'"
    deliverygraph_step_count = 'jsonb_array_length("order__deliverygraph"."graph")'
    current_status_position = """(jsonb_path_query_first("order__deliverygraph"."graph", '$ ? (@.id == $val)', ('{
                  "val": ' || "order"."current_status_id" || '}')::jsonb)) ->> 'position'"""

    instance_qs = Order.all_objects.annotate(
        has_ready_for_shipment=RawSQL(has_ready_for_shipment),
        deliverygraph_step_count=RawSQL(deliverygraph_step_count),
        current_status_position=RawSQL(current_status_position),
    ).filter(
        *default_filter_args,
        deliverygraph__id__isnull=False,  # needed to join deliverygraph table only.
    ).filter(*filter_args).order_by('-created_at').distinct()
    qs = instance_qs.prefetch_related(
        Prefetch('status_set', OrderStatuses.all().prefetch_related('status'),
                 'statuses'),
    ).select_related('area', 'city', 'courier__user', 'item', 'current_status',
                     'partner', 'shipment_point', 'delivery_point', 'product')
    paginated_result = await paginate(qs, params=pagination_params)

    for order_item in getattr(paginated_result, 'items'):
        if profile_type == ProfileType.COURIER:
            if order_item.current_status.id == int(OrderStatus.ENDED.value):
                order_item.delivery_status = {
                    'status': OrderDeliveryStatus.IS_DELIVERED.value,
                    'datetime': None,
                    'reason': None,
                    'comment': None,
                }

    return paginated_result


async def order_get_v2(order_id: int, default_filter_args: list = None, profile_type: ProfileType = None):
    if default_filter_args is None:
        default_filter_args = []
    has_ready_for_shipment = f"order__deliverygraph.graph @? '$.slug[*] ? (@ == \"{StatusSlug.READY_FOR_SHIPMENT}\")'"
    deliverygraph_step_count = 'jsonb_array_length("order__deliverygraph"."graph")'
    current_status_position = """(jsonb_path_query_first("order__deliverygraph"."graph", '$ ? (@.id == $val)', ('{
                      "val": ' || "order"."current_status_id" || '}')::jsonb)) ->> 'position'"""
    if profile_type == ProfileType.COURIER:
        has_ready_for_shipment = (
            f"order__deliverygraph.graph_courier @? '$.slug[*] ? (@ == \"{StatusSlug.READY_FOR_SHIPMENT}\")'"
        )
        deliverygraph_step_count = 'jsonb_array_length("order__deliverygraph"."graph_courier")'
        current_status_position = """
        (jsonb_path_query_first("order__deliverygraph"."graph_courier", '$ ? (@.id == $val)', ('{
                              "val": ' || "order"."current_status_id" || '}')::jsonb)) ->> 'position'"""
    try:
        instance_qs = Order.all_objects.annotate(
            last_otp=Subquery(
                models.SMSPostControl.filter(
                    order_id=RawSQL('"order"."id"'),
                ).order_by('-created_at').limit(1).values('created_at'),
            ),
            has_ready_for_shipment=RawSQL(has_ready_for_shipment),
            deliverygraph_step_count=RawSQL(deliverygraph_step_count),
            current_status_position=RawSQL(current_status_position),
        ).filter(
            *default_filter_args,
            deliverygraph__id__isnull=False,  # needed to join deliverygraph table only.
        ).distinct().get(id=order_id)
        statuses_args = []
        if profile_type == ProfileType.COURIER:
            order_statuses = await instance_qs.values_list('deliverygraph__graph_courier', flat=True)
            order_status_ids = [s['id'] for s in order_statuses]
            statuses_args.append(Q(
                status_id__in=order_status_ids,
            ))
        qs = instance_qs.prefetch_related(
            Prefetch('status_set', OrderStatuses.filter(*statuses_args).prefetch_related('status'),
                     'statuses'),
            Prefetch('item__postcontrol_config_set', models.PostControlConfig.filter(
                parent_config_id__isnull=True,
                type=PostControlType.POST_CONTROL.value,
            ).prefetch_related(
                Prefetch('inner_param_set', models.PostControlConfig.filter(
                    type=PostControlType.POST_CONTROL.value
                ).prefetch_related(
                    Prefetch(
                        'postcontrol_document_set',
                        models.PostControl.filter(order_id=order_id),
                        'postcontrol_documents',
                    ),
                ), 'inner_params'),
                Prefetch(
                    'postcontrol_document_set',
                    models.PostControl.filter(order_id=order_id),
                    'postcontrol_documents',
                ),
            ), 'postcontrol_configs'),
            Prefetch('item__postcontrol_config_set', models.PostControlConfig.filter(
                parent_config_id__isnull=True,
                type=PostControlType.CANCELED.value,
            ).prefetch_related(
                Prefetch('inner_param_set', models.PostControlConfig.filter(
                    type=PostControlType.CANCELED.value,
                ).prefetch_related(
                    Prefetch(
                        'postcontrol_document_set',
                        models.PostControl.filter(order_id=order_id),
                        'postcontrol_documents',
                    ),
                ), 'inner_params'),
                Prefetch(
                    'postcontrol_document_set',
                    models.PostControl.filter(order_id=order_id),
                    'postcontrol_documents',
                ),
            ), 'postcontrol_cancellation_configs'),
        ).select_related(
            'area', 'city', 'courier__user', 'item', 'deliverygraph',
            'partner', 'current_status', 'shipment_point', 'delivery_point', 'product'
        )
        order_obj = await qs

        order_obj.courier_assigned_at = None
        for status in order_obj.statuses:
            if status.status_id == 2:
                order_obj.courier_assigned_at = status.created_at
                break

        result = schemas.OrderGetV2.from_orm(order_obj)
        if profile_type == ProfileType.COURIER:
            result.deliverygraph.graph = parse_obj_as(typing.List[DeliveryGraphItemGet], order_obj.deliverygraph.graph_courier)
            if order_obj.current_status_id == int(OrderStatus.ENDED.value):
                result.delivery_status = {
                    'status': OrderDeliveryStatus.IS_DELIVERED.value,
                    'datetime': None,
                    'reason': None,
                    'comment': None,
                }
        return result

    except DoesNotExist:
        raise DoesNotExist(f'Order with provided ID: {order_id} was not found')


async def order_get_couriers_current_executable_orders(courier_id):
    orders = await Order.filter(
        courier_id=courier_id
    ).values('id')

    return [order.get('id') for order in orders]


async def order_ensure_exists(order_id: str):
    is_exists = await Order.filter(
        id=order_id
    ).exists()

    if not is_exists:
        raise models.OrderNotFound(
            table='Order',
            detail='{table} with id {entity_id} not found',
            entity_id=order_id,
        )
    return is_exists


async def check_is_delivery_points_in_polygon(order: Order,
                                              courier_partner_id: int) -> bool:
    delivery_point = await order.delivery_point

    areas = await models.Area.filter(
        partner_id=courier_partner_id, archived=False, city_id=order.city_id
    )
    for area in areas:
        polygon = [
            list(map(float, point.values()))
            for point in area.scope
        ]
        polygon = Polygon(polygon)
        point = Point(*list(map(float, (delivery_point.latitude, delivery_point.longitude))))
        if point.within(polygon):
            await order.update_from_dict({'area': area}).save(update_fields=['area_id'])
            return True
    return False


# Используется только для api/v1/order/{order_id} + api/v1/order/{order_id}/pan
async def order_get_v1(order_id: int, default_filer_args: list = None,  profile_type: ProfileType = None):
    if default_filer_args is None:
        default_filer_args = []
    try:
        instance_qs = Order.all_objects.annotate(
            last_otp=Subquery(
                models.SMSPostControl.filter(
                    order_id=RawSQL('"order"."id"'),
                ).order_by('-created_at').limit(1).values('created_at'),
            ),
            has_ready_for_shipment=RawSQL(
                f"order__deliverygraph.graph @? '$.slug[*] ? (@ == \"{StatusSlug.READY_FOR_SHIPMENT}\")'"
            ),
        ).filter(
            *default_filer_args,
            deliverygraph__id__isnull=False,  # needed to join deliverygraph table only.
        ).distinct().get(id=order_id)
        statuses_args = []
        if profile_type == ProfileType.COURIER:
            order_statuses = await instance_qs.values_list('deliverygraph__graph_courier', flat=True)
            order_status_ids = [s['id'] for s in order_statuses]
            statuses_args.append(Q(
                status_id__in=order_status_ids,
            ))
        qs = instance_qs.prefetch_related(
            Prefetch('status_set', OrderStatuses.filter(*statuses_args).prefetch_related('status'),
                     'statuses'),
            Prefetch('postcontrol_set', models.PostControl.all(), 'postcontrols'),
            Prefetch(
                'order_chain_stages_set', OrderChainStage.all(), 'order_chain_stages',
            ),
            Prefetch('item__postcontrol_config_set', models.PostControlConfig.filter(
                parent_config_id__isnull=True,
                type=PostControlType.POST_CONTROL.value,
            ).prefetch_related(
                Prefetch('inner_param_set', models.PostControlConfig.filter(
                    type=PostControlType.POST_CONTROL.value,
                ).prefetch_related(
                    Prefetch(
                        'postcontrol_document_set',
                        models.PostControl.filter(order_id=order_id),
                        'postcontrol_documents',
                    ),
                ), 'inner_params'),
                Prefetch(
                    'postcontrol_document_set',
                    models.PostControl.filter(order_id=order_id),
                    'postcontrol_documents',
                ),
            ), 'postcontrol_configs'),
            Prefetch('item__postcontrol_config_set', models.PostControlConfig.filter(
                parent_config_id__isnull=True,
                type=PostControlType.CANCELED.value,
            ).prefetch_related(
                Prefetch('inner_param_set', models.PostControlConfig.filter(
                    type=PostControlType.CANCELED.value,
                ).prefetch_related(
                    Prefetch(
                        'postcontrol_document_set',
                        models.PostControl.filter(order_id=order_id),
                        'postcontrol_documents',
                    ),
                ), 'inner_params'),
                Prefetch(
                    'postcontrol_document_set',
                    models.PostControl.filter(order_id=order_id),
                    'postcontrol_documents',
                ),
            ), 'postcontrol_cancellation_configs'),
        ).select_related(
            'area', 'city', 'courier__user', 'item', 'deliverygraph', 'partner', 'product'
        )
        order_obj = await qs

        result = schemas.OrderGetV1.from_orm(order_obj)
        await order_fill_old_addresses_field(result)
        if profile_type == ProfileType.COURIER:
            result.deliverygraph.graph = parse_obj_as(typing.List[DeliveryGraphItemGet], order_obj.deliverygraph.graph_courier)
            if order_obj.current_status_id == int(OrderStatus.ENDED.value):
                result.delivery_status = {
                    'status': OrderDeliveryStatus.IS_DELIVERED.value,
                    'datetime': None,
                    'reason': None,
                    'comment': None,
                }
        return result

    except DoesNotExist:
        raise DoesNotExist(f'Order with provided ID: {order_id} was not found')


async def order_get(order_id: int, default_filer_args: list = None,  profile_type: ProfileType = None):
    if default_filer_args is None:
        default_filer_args = []
    try:
        instance_qs = Order.all_objects.annotate(
            last_otp=Subquery(
                models.SMSPostControl.filter(
                    order_id=RawSQL('"order"."id"'),
                ).order_by('-created_at').limit(1).values('created_at'),
            ),
            has_ready_for_shipment=RawSQL(
                f"order__deliverygraph.graph @? '$.slug[*] ? (@ == \"{StatusSlug.READY_FOR_SHIPMENT}\")'"
            ),
        ).filter(
            *default_filer_args,
            deliverygraph__id__isnull=False,  # needed to join deliverygraph table only.
        ).distinct().get(id=order_id)
        statuses_args = []
        if profile_type == ProfileType.COURIER:
            order_statuses = await instance_qs.values_list('deliverygraph__graph_courier', flat=True)
            order_status_ids = [s['id'] for s in order_statuses]
            statuses_args.append(Q(
                status_id__in=order_status_ids,
            ))
        qs = instance_qs.prefetch_related(
            Prefetch('status_set', OrderStatuses.filter(*statuses_args).prefetch_related('status'),
                     'statuses'),
            Prefetch('postcontrol_set', models.PostControl.all(), 'postcontrols'),
            Prefetch(
                'order_chain_stages_set', OrderChainStage.all(), 'order_chain_stages',
            ),
            Prefetch('item__postcontrol_config_set', models.PostControlConfig.filter(
                parent_config_id__isnull=True,
            ).prefetch_related(
                Prefetch('inner_param_set', models.PostControlConfig.all().prefetch_related(
                    Prefetch(
                        'postcontrol_document_set',
                        models.PostControl.filter(order_id=order_id),
                        'postcontrol_documents',
                    ),
                ), 'inner_params'),
                Prefetch(
                    'postcontrol_document_set',
                    models.PostControl.filter(order_id=order_id),
                    'postcontrol_documents',
                ),
            ), 'postcontrol_configs'),
        ).select_related(
            'area', 'city', 'courier__user', 'item', 'deliverygraph', 'partner',
        )
        order_obj = await qs

        result = schemas.OrderGet.from_orm(order_obj)
        await order_fill_old_addresses_field(result)
        if profile_type == ProfileType.COURIER:
            result.deliverygraph.graph = parse_obj_as(typing.List[DeliveryGraphItemGet], order_obj.deliverygraph.graph_courier)
            if order_obj.current_status_id == int(OrderStatus.ENDED.value):
                result.delivery_status = {
                    'status': OrderDeliveryStatus.IS_DELIVERED.value,
                    'datetime': None,
                    'reason': None,
                    'comment': None,
                }
        return result

    except DoesNotExist:
        raise common.BaseNotFoundError(
            table='Order',
            detail='{table} with provided ID: {order_id} was not found',
            order_id=order_id,
        )


async def get_shipment_point_id(
    old_addresses_schema: List[schemas.OrderAddressCreate],
) -> int | None:
    s_point = None
    for address in old_addresses_schema:
        if address.type == AddressType.SHIPMENT_POINT:
            s_point = address.place_id
    if not s_point:
        return
    sp_repo = ShipmentPointRepository()
    try:
        place_obj = await models.Place.get(id=s_point)
        shipment_point_id = await sp_repo.get_id_by_geolocations(
            latitude=place_obj.latitude,
            longitude=place_obj.longitude,
        )
    except (
        models.PlaceNotFound,
        PartnerShipmentPointNotFoundError,
    ):
        return s_point
    return shipment_point_id


async def get_delivery_point_id(
    old_addresses_schema: List[schemas.OrderAddressCreate],
) -> int | None:
    d_points = []
    for address in old_addresses_schema:
        if address.type == AddressType.DELIVERY_POINT:
            d_points.append(address)
    if not d_points:
        return
    return d_points[0].place_id


def get_minvalue(values_list):
    # get the minimum value in the list
    min_value = min(values_list)

    # return the index of minimum value
    min_index = values_list.index(min_value)
    return min_index


async def distribute_order_immediately_for_all_couriers(
    orders: List, delivery_service_partner_id
):
    area_ids = list(set([order.area_id for order in orders]))
    couriers = await models.ProfileCourier.filter(
        partner_id=delivery_service_partner_id,
        # at_work=True,
        areas__id__in=area_ids,
    ).distinct().order_by('id')
    if not couriers:
        raise models.ProfileNotFound(
            table='ProfileCourier',
            detail='Couriers for distribution current order was not found',
        )

    result = []
    algo_results = []
    courier_orders_list = []
    for courier in couriers:
        courier_orders = await get_current_orders_for_courier(courier.id)
        courier_orders.extend(orders)
        res_with_urgent = await router.run_algo(courier_orders, [courier, ])
        courier_orders_list.append(courier_orders)
        algo_results.append(res_with_urgent)
        try:
            result.append(
                res_with_urgent.get(
                    'couriers'
                )[0].get('time')
            )
        except IndexError:
            raise models.NotDistributionCouriersError(
                'Couriers for distribution current order was not found'
            )

    courier_index = get_minvalue(result)

    if courier_orders_list:
        await router.order_distribution(
            courier_orders_list[courier_index],
            [couriers[courier_index], ],
            algo_results[courier_index]
        )


async def redistribute_order_immediately_for_current_courier(orders, courier):
    if not courier:
        raise models.ProfileNotFound(
            detail='Couriers for distribution current order was not found',
            table='Order',
        )

    if orders:
        algo_result = await router.run_algo(orders, [courier, ])
        if algo_result:
            await router.order_distribution(
                orders,
                [courier, ],
                algo_result
            )


async def get_default_values(create: dict) -> dict:
    try:
        item_obj = await models.Item.get(id=create['item_id'])
    except DoesNotExist:
        raise DoesNotExist(f'Item with given ID: {create["item_id"]}')
    if create.get('product_type') != enums.ProductType.SEP_UNEMBOSSED.value:
        if item_obj.has_postcontrol and not create.get('receiver_iin'):
            raise OrderReceiverIINNotProvided(
                'You trying to create order using a product with post_control '
                "status but don't provide receiver_iin",
            )

    deliverygraph_obj = await item_obj.deliverygraph_set.filter(
        types__contains=create['type'].value,
    ).first()
    result = {
        'deliverygraph_id': deliverygraph_obj.id,
    }

    if city_id := create.get('city_id'):
        city_repo = CityRepository()
        city = await city_repo.get_by_id([], entity_id=city_id)
        result['created_at'] = city.localtime

    if not deliverygraph_obj:
        raise IntegrityError(
            f'There is no respective deliverygraph for given type',
        )

    result['allow_courier_assign'] = not any(
        [graph['slug'] == StatusSlug.ACCEPTED_BY_COURIER_SERVICE for graph in
         deliverygraph_obj.graph]
    )

    return result


@atomic()
async def order_create(
    create: schemas.OrderCreate,
    courier_service_id: int,
    user: schemas.UserCurrent = None,
):
    create_dict = create.dict(exclude_unset=True, exclude_none=True)

    addresses = create.addresses
    create_dict.pop('addresses', None)
    sp_id = await get_shipment_point_id(addresses)
    dp_id = await get_delivery_point_id(addresses)

    distribute_now = create_dict.pop('distribute_now', None)

    default_values = await get_default_values(create_dict)
    order_created = await Order.create(
        **default_values,
        **create_dict,
        shipment_point_id=sp_id,
        delivery_point_id=dp_id,
    )

    await order_update_status(order_created, OrderStatus.NEW)

    if create_dict.get('courier_id'):
        if assigned_status := await models.Status.filter(
            slug=StatusSlug.COURIER_ASSIGNED.value,
            partner_id__isnull=True,
        ).first():
            try:
                await order_update_status(order_created, assigned_status.id)
            except IntegrityError:
                pass
    if user:
        try:
            await models.history_create(
                schemas.HistoryCreate(
                    initiator_type=InitiatorType.USER,
                    initiator_id=user.id,
                    initiator_role=user.profile['profile_type'],
                    model_type=HistoryModelName.ORDER,
                    model_id=order_created.id,
                    request_method=RequestMethods.POST,
                    action_data={
                        'created_by': order_created.created_by,
                    },
                    created_at=default_values['created_at'],
                )
            )
        except models.HistoryCreationError:
            pass

    # noinspection PyTypeChecker
    await order_fill_old_addresses_field(order_created)

    await check_is_delivery_points_in_polygon(
        order_created,
        (await order_created.partner).courier_partner_id or courier_service_id,
    )
    if not distribute_now:
        return order_created

    if not order_created.area:
        raise OrderAlreadyHaveCourierError(
            'Cannot distribute order because delivery address of order is not in area'
        )

    if order_created.courier_id:
        raise OrderAlreadyHaveCourierError(
            'Order cannot be sent for immediate distribution by ' +
            'the system and be manually assigned to a specific courier'
        )
    await distribute_order_immediately_for_all_couriers(
        [order_created, ], courier_service_id
    )

    if not order_created.courier_id:
        return order_created
    orders = await get_current_orders_for_courier(order_created.courier_id)
    if len(orders) == 0:
        orders.append(order_created)
    courier = await models.ProfileCourier.filter(id=order_created.courier_id).first()
    await redistribute_order_immediately_for_current_courier(
        orders, courier
    )

    return order_created


async def order_create_v2(
    create: schemas.OrderCreateV2,
    product_payload: typing.Optional[typing.Union[CardPayload, POSTerminalPayload]],
    courier_service_id: int,
    distribute_now: bool,
    user: schemas.UserCurrent = None,
) -> int:
    create_dict = create.dict(exclude_unset=True, exclude_none=True)
    create_dict.pop('delivery_point', None)
    order_product_type = create_dict.pop('product_type', None)
    create_dict.pop('payload', None)

    default_values = await get_default_values(create_dict)

    if not create.type == OrderType.PICKUP.value:
        delivery_point_schema = create.delivery_point
        if delivery_point_schema:
            dp_repo = DeliveryPointRepository()
            dp = await dp_repo.create(delivery_point_schema)
            default_values['delivery_point_id'] = dp.id

    order_created = await Order.create(
        **default_values,
        **create_dict,
    )

    if order_product_type == enums.ProductType.POS_TERMINAL and product_payload:
        await models.Product.create(
            order_id=order_created.id,
            type='pos_terminal',
            attributes=product_payload.json()
        )

    await order_update_status(order_created, OrderStatus.NEW)

    if create_dict.get('courier_id'):
        if assigned_status := await models.Status.filter(
            slug=StatusSlug.COURIER_ASSIGNED.value,
            partner_id__isnull=True,
        ).first():
            try:
                await order_update_status(order_created, assigned_status.id)
            except IntegrityError:
                pass
    try:
        order_time = await order_created.localtime
        await models.history_create(
            schemas.HistoryCreate(
                initiator_type=InitiatorType.USER,
                initiator_id=user.id,
                initiator_role=user.profile['profile_type'],
                model_type=HistoryModelName.ORDER,
                model_id=order_created.id,
                request_method=RequestMethods.POST,
                action_data={
                    'created_by': order_created.created_by,
                },
                created_at=order_time,
            )
        )
    except models.HistoryCreationError:
        pass

    if not create.type == OrderType.PICKUP.value:
        await check_is_delivery_points_in_polygon(
            order_created,
            courier_service_id,
        )

        if not distribute_now:
            return order_created.id

        if not order_created.area:
            raise OrderAlreadyHaveCourierError(
                'Cannot distribute order because delivery address of order is not in area'
            )
        if order_created.courier_id:
            raise OrderAlreadyHaveCourierError(
                'Order cannot be sent for immediate distribution by ' +
                'the system and be manually assigned to a specific courier'
            )
        await distribute_order_immediately_for_all_couriers(
            [order_created, ], courier_service_id
        )

    if not order_created.courier_id:
        return order_created.id
    orders = await get_current_orders_for_courier(order_created.courier_id)
    if len(orders) == 0:
        orders.append(order_created)
    courier = await models.ProfileCourier.filter(id=order_created.courier_id).first()
    await redistribute_order_immediately_for_current_courier(
        orders, courier
    )

    return order_created.id


@atomic()
async def order_update(
    order_id: int,
    update: schemas.OrderUpdate,
    default_filter_args,
):
    update_dict = update.dict(exclude_unset=True)
    try:
        subquery = (f"order__deliverygraph.graph @? "
                    f"'$.slug[*] ? (@ == \"{StatusSlug.READY_FOR_SHIPMENT}\")'")
        order_qs = Order.annotate(
            has_ready_for_shipment=RawSQL(subquery)
        ).filter(
            *default_filter_args,
            deliverygraph__id__isnull=False,  # needed to join deliverygraph table only.
        ).distinct().get(id=order_id)
        order_obj = await order_qs
    except DoesNotExist as e:
        raise DoesNotExist(
            f'Order with provided ID: {order_id} was not found') from e

    await order_obj.update_from_dict(update_dict).save(
        update_fields=[i for i in update_dict.keys()],
    )


async def order_expel_courier(order_id: int, current_user: schemas.UserCurrent, default_filter_args=None):
    order_qs = Order.filter(
        *default_filter_args,
    ).distinct().get(id=order_id).select_related('city', 'courier__city')
    try:
        order_obj = await order_qs
    except DoesNotExist as e:
        raise DoesNotExist(
            f'Order with provided ID: {order_id} was not found') from e
    order_time = await order_obj.localtime
    new_status = await models.Status.get(
        slug=StatusSlug.NEW.value,
        partner_id__isnull=True,
    )
    await OrderStatuses.filter(order_id=order_id).delete()
    await OrderStatuses.create(order_id=order_id, status_id=new_status.id, created_at=order_time)
    initiator_type = 'User'
    await models.History.create(
        initiator_id=current_user.id,
        initiator_type=initiator_type,
        initiator_role=current_user.profile['profile_type'],
        request_method='PUT',
        model_type='Order',
        model_id=order_id,
        action_data={
            'message': 'status_new_due_to_courier_unlink',
        },
        created_at=order_time,
    )
    order_obj.current_status = new_status
    await order_obj.save()


async def order_accept_cancel(
    order_obj: Order,
    user: UserCurrent,
):
    order_obj.delivery_datetime = None
    delivery_status = {
        'status': OrderDeliveryStatus.CANCELLED.value,
        'reason': order_obj.delivery_status['reason'],
        'datetime': None,
        'comment': order_obj.delivery_status['comment'],
    }
    order_obj.delivery_status = delivery_status
    await order_obj.save()

    await models.history_create(
        schemas.HistoryCreate(
            initiator_type=InitiatorType.USER,
            initiator_id=user.id,
            initiator_role=user.profile['profile_type'],
            model_type=HistoryModelName.ORDER,
            model_id=order_obj.id,
            request_method=RequestMethods.PATCH,
            action_data={
                'delivery_status': delivery_status,
            },
            created_at=await order_obj.localtime,
        )
    )

    order_time = await order_obj.localtime

    if callback_url := order_obj.callbacks.get('set_status', None):
        data = schemas.DeliveryStatusExternal(
            status=order_obj.delivery_status['status'],
            comment=order_obj.delivery_status['reason'],
            status_datetime=str(order_time)).dict()

        # В зависимости от партнера, получаем HTTP заголовки для вызова callback метода
        headers = get_headers(order_obj.partner_id)
        await publish_callback(
            task_name='send-status',
            url=callback_url,
            data=data,
            headers=headers,
        )

    # if fcmdevice_ids := await models.FCMDevice.filter(
    #     user__profile_courier=order_obj.courier_id,
    # ).values_list('id', flat=True):
    #     message_data = schemas.FirebaseMessage(
    #         registration_ids=fcmdevice_ids,
    #         notification=schemas.Notification(
    #             title='Заявка отменена',
    #             body=f'Заявка № {order_id} отменена. Откройте заявку, чтобы посмотреть причину.',
    #         ),
    #         data={
    #             'title': 'Заявка отменена',
    #             'description': 'Заявка № {order_id} отменена. Откройте заявку, чтобы посмотреть причину.',
    #             'id': order_id,
    #             'type': order_obj.type,
    #             'push_type': PushType.INFO,
    #             'delivery_status': OrderDeliveryStatus.CANCELLED.value,
    #         }
    #     )
    #     await call_task(
    #         task_name='firebase-send',
    #         data=message_data.dict(),
    #     )

    if order_obj.courier_id is None:
        return

    if not isinstance(order_obj.courier, Model):
        await order_obj.fetch_related('courier')

    courier_time = await order_obj.courier.localtime

    orders = await Order.filter(
        delivery_datetime__year=courier_time.year,
        delivery_datetime__month=courier_time.month,
        delivery_datetime__day=courier_time.day,
        courier_id=order_obj.courier_id,
    )
    if orders:
        courier = await models.ProfileCourier.filter(
            id=order_obj.courier_id).first()
        await redistribute_order_immediately_for_current_courier(
            orders, courier
        )


async def order_request_cancellation(
    order_obj: Order,
    reason: str,
    user: UserCurrent,
    comment: str | None = None,
):
    order_obj.delivery_datetime = None
    delivery_status = {
        'status': OrderDeliveryStatus.REQUESTED_TO_CANCEL.value,
        'reason': reason,
        'datetime': None,
        'comment': comment,
    }
    order_obj.delivery_status = delivery_status
    await order_obj.save()

    await models.history_create(
        schemas.HistoryCreate(
            initiator_type=InitiatorType.USER,
            initiator_id=user.id,
            initiator_role=user.profile['profile_type'],
            model_type=HistoryModelName.ORDER,
            model_id=order_obj.id,
            request_method=RequestMethods.PATCH,
            action_data={
                'delivery_status': delivery_status,
            },
            created_at=await order_obj.localtime,
        )
    )


async def order_postpone(order_id: int, until: datetime, comment: str, user: UserCurrent, default_filter_args=None):
    order_qs = Order.filter(
        *default_filter_args,
    ).distinct().get(id=order_id).select_related('city', 'courier__city')
    try:
        order_obj = await order_qs
    except DoesNotExist as e:
        raise DoesNotExist(
            f'Order with provided ID: {order_id} was not found') from e

    order_obj.delivery_datetime = until
    delivery_status = {
        'status': OrderDeliveryStatus.POSTPONED.value,
        'datetime': str(until),
        'reason': None,
        'comment': comment,
    }
    order_obj.delivery_status = delivery_status
    await order_obj.save()
    await models.history_create(
        schemas.HistoryCreate(
            initiator_type=InitiatorType.USER,
            initiator_id=user.id,
            initiator_role=user.profile['profile_type'],
            model_type=HistoryModelName.ORDER,
            model_id=order_id,
            request_method=RequestMethods.PATCH,
            action_data={
                'delivery_status': delivery_status,
            },
            created_at=await order_obj.localtime,
        )
    )

    order_time = await order_obj.localtime

    conn = redis_module.get_connection()
    if callback_url := order_obj.callbacks.get('set_status', None):
        data = schemas.DeliveryStatusExternal(
            status=order_obj.delivery_status['status'],
            status_datetime=str(order_time)).dict()

        # В зависимости от партнера, получаем HTTP заголовки для вызова callback метода
        headers = get_headers(order_obj.partner_id)
        await publish_callback(
            task_name='send-status',
            url=callback_url,
            data=data,
            headers=headers,
        )

    if fcmdevice_ids := await models.FCMDevice.filter(
        user__profile_courier=order_obj.courier_id,
    ).values_list('id', flat=True):
        message_data = schemas.FirebaseMessage(
            registration_ids=fcmdevice_ids,
            notification=schemas.Notification(
                title='Заявка отложена',
                body=f'Заявка № {order_id} отложена на {order_obj.delivery_status.get("datetime")}',
            ),
            data={
                'title': 'Заявка отложена',
                'description': f'Заявка № {order_id} отложена на {order_obj.delivery_status.get("datetime")}',
                'id': order_id,
                'type': order_obj.type,
                'push_type': PushType.INFO,
                'delivery_status': OrderDeliveryStatus.POSTPONED.value,
            }
        )
        pubsub_message = json.dumps({
            'task_name': 'firebase-send',
            'kwargs': message_data.dict(),
        })
        await conn.publish('send-to-celery', pubsub_message)

    if order_obj.courier is None:
        return
    courier_time = await order_obj.courier.localtime

    orders = await Order.filter(
        delivery_datetime__year=courier_time.year,
        delivery_datetime__month=courier_time.month,
        delivery_datetime__day=courier_time.day,
        courier_id=order_obj.courier_id,
    )
    if orders:
        courier = await models.ProfileCourier.filter(
            id=order_obj.courier_id).first()
        await redistribute_order_immediately_for_current_courier(
            orders, courier
        )


async def order_finalize_at_cs(order_id: int, comment: str, user: UserCurrent, default_filter_args=None):
    order_qs = Order.all_objects.filter(
        *default_filter_args,
    ).distinct().get(id=order_id).select_related('city', 'courier__city')
    try:
        order_obj = await order_qs
    except DoesNotExist as e:
        raise DoesNotExist(
            f'Order with provided ID: {order_id} was not found') from e

    delivery_status = {
        'status': OrderDeliveryStatus.BEING_FINALIZED_AT_CS.value,
        'datetime': None,
        'reason': None,
        'comment': comment,
    }
    order_obj.delivery_status = delivery_status
    await order_obj.save()
    await models.history_create(
        schemas.HistoryCreate(
            initiator_type=InitiatorType.USER,
            initiator_id=user.id,
            initiator_role=user.profile['profile_type'],
            model_type=HistoryModelName.ORDER,
            model_id=order_id,
            request_method=RequestMethods.PATCH,
            action_data={
                'delivery_status': delivery_status,
            },
            created_at=await order_obj.localtime,
        )
    )


async def order_noncall(order_id: int, comment: str, user: UserCurrent, default_filter_args=None):
    if default_filter_args is None:
        default_filter_args = []

    order_qs = Order.filter(
        *default_filter_args,
    ).distinct().get(id=order_id).select_related('city', 'courier__city')
    try:
        order_obj = await order_qs
    except DoesNotExist as e:
        raise DoesNotExist(
            f'Order with provided ID: {order_id} was not found') from e

    order_obj.delivery_datetime = None
    delivery_status = {
        'status': OrderDeliveryStatus.NONCALL.value,
        'datetime': None,
        'reason': None,
        'comment': comment,
    }
    order_obj.delivery_status = delivery_status
    await order_obj.save()

    await models.history_create(
        schemas.HistoryCreate(
            initiator_type=InitiatorType.USER,
            initiator_id=user.id,
            initiator_role=user.profile['profile_type'],
            model_type=HistoryModelName.ORDER,
            model_id=order_id,
            request_method=RequestMethods.PATCH,
            action_data={
                'delivery_status': delivery_status,
            },
            created_at=await order_obj.localtime,
        )
    )
    order_time = await order_obj.localtime

    if callback_url := order_obj.callbacks.get('set_status', None):
        data = schemas.DeliveryStatusExternal(
            status=order_obj.delivery_status['status'],
            status_datetime=str(order_time)).dict()

        # В зависимости от партнера, получаем HTTP заголовки для вызова callback метода
        headers = get_headers(order_obj.partner_id)
        await publish_callback(
            task_name='send-status',
            url=callback_url,
            data=data,
            headers=headers,
        )

    if fcmdevice_ids := await models.FCMDevice.filter(
        user__profile_courier=order_obj.courier_id,
    ).values_list('id', flat=True):
        message_data = schemas.FirebaseMessage(
            registration_ids=fcmdevice_ids,
            notification=schemas.Notification(
                title='Заявка в "Недозвоне"',
                body=f'Заявка № {order_id} в статусе "Недозвон". Не забудьте, позже еще раз позвонить получателю'
                ,
            ),
            data={
                'title': 'Заявка в "Недозвоне"',
                'description': f'Заявка № {order_id} в статусе "Недозвон". '
                               f'Не забудьте, позже еще раз позвонить получателю',
                'id': order_id,
                'type': order_obj.type,
                'push_type': PushType.INFO,
                'delivery_status': OrderDeliveryStatus.NONCALL.value,
            }
        )
        pubsub_message = json.dumps({
            'task_name': 'firebase-send',
            'kwargs': message_data.dict(),
        })
        await call_task(
            task_name='firebase-send',
            data=message_data.dict(),
        )

    if order_obj.courier is None:
        return
    courier_time = await order_obj.courier.localtime
    orders = await Order.filter(
        delivery_datetime__year=courier_time.year,
        delivery_datetime__month=courier_time.month,
        delivery_datetime__day=courier_time.day,
        courier_id=order_obj.courier_id,
    )
    if orders:
        courier = await models.ProfileCourier.filter(
            id=order_obj.courier_id).first()
        await redistribute_order_immediately_for_current_courier(
            orders, courier
        )


async def order_resume(
    order_id: int,
    user: UserCurrent,
    new_delivery_datetime: datetime.datetime | None,
    default_filter_args=None,
):
    order_qs = Order.filter(
        *default_filter_args,
    ).distinct().get(id=order_id).select_related('city', 'courier__city')
    try:
        order_obj = await order_qs
    except DoesNotExist as e:
        raise DoesNotExist(
            f'Order with provided ID: {order_id} was not found') from e

    if new_delivery_datetime is not None:
        order_obj.delivery_datetime = new_delivery_datetime

    if order_obj.current_status_id == int(OrderStatus.NEW.value):
        new_delivery_status = None
    elif order_obj.current_status_id == int(OrderStatus.DELIVERED.value):
        new_delivery_status = OrderDeliveryStatus.IS_DELIVERED.value
    else:
        new_delivery_status = OrderDeliveryStatus.TO_CALL_POINT.value

    delivery_status = {
        'status': new_delivery_status,
        'datetime': None,
        'reason': None,
        'comment': None,
    }
    order_obj.delivery_status = delivery_status
    await order_obj.save()

    await models.history_create(
        schemas.HistoryCreate(
            initiator_type=InitiatorType.USER,
            initiator_id=user.id,
            initiator_role=user.profile['profile_type'],
            model_type=HistoryModelName.ORDER,
            model_id=order_id,
            request_method=RequestMethods.PATCH,
            action_data={
                'delivery_status': delivery_status,
            },
            created_at=await order_obj.localtime,
        )
    )

    order_time = await order_obj.localtime

    if callback_url := order_obj.callbacks.get('set_status', None):
        data = schemas.DeliveryStatusExternal(
            status=order_obj.delivery_status['status'],
            status_datetime=str(order_time)).dict()

        # В зависимости от партнера, получаем HTTP заголовки для вызова callback метода
        headers = get_headers(order_obj.partner_id)
        await publish_callback(
            task_name='send-status',
            url=callback_url,
            data=data,
            headers=headers,
        )

    if order_obj.courier is None:
        return
    courier_time = await order_obj.courier.localtime

    orders = await Order.filter(
        delivery_datetime__year=courier_time.year,
        delivery_datetime__month=courier_time.month,
        delivery_datetime__day=courier_time.day,
        courier_id=order_obj.courier_id,
    )
    if orders:
        courier = await models.ProfileCourier.filter(
            id=order_obj.courier_id).first()
        await redistribute_order_immediately_for_current_courier(
            orders, courier
        )


async def order_restore(
    order_id: int,
    update: schemas.OrderRestore = None,
    user: schemas.UserCurrent = None,
):
    try:
        order_obj = await Order.get(id=order_id).select_related('city')
        if order_obj.delivery_status['status'] == OrderDeliveryStatus.IS_DELIVERED.value:
            raise OrderAlreadyDelivered('Order delivery_status already delivered')
        if update:
            update_dict = update.dict(exclude_unset=True)
            update_dict['order_group_id'] = None
            if 'delivery_status' in update_dict:
                delivery_status = update_dict.pop('delivery_status', {})
                new_delivery_status = {
                    'status': delivery_status.get('status'),
                    'reason': delivery_status.get('reason'),
                    'datetime': delivery_status.get('datetime'),
                    'comment': delivery_status.get('comment'),
                }
                order_obj.delivery_status = new_delivery_status
                if callback_url := order_obj.callbacks.get('set_status', None):
                    data = schemas.DeliveryStatusExternal(
                        status=new_delivery_status.get('status'),
                        comment=new_delivery_status.get('reason'),
                        status_datetime=str(await order_obj.localtime)).dict()

                    # В зависимости от партнера, получаем HTTP заголовки для вызова callback метода
                    headers = get_headers(order_obj.partner_id)
                    await publish_callback(
                        task_name='send-status',
                        url=callback_url,
                        data=data,
                        headers=headers,
                    )

            order_obj.update_from_dict(update_dict)
            await order_obj.save()
        await models.OrderStatuses.filter(order_id=order_id).delete()
        new_status = await models.Status.get(slug=StatusSlug.NEW.value)

        order_time = await order_obj.localtime
        history_created_at = order_time
        await OrderStatuses.create(order=order_obj, status=new_status, created_at=order_time)
        order_obj.current_status = new_status
        product = await models.Product.get_or_none(order_id=order_id)
        await product.delete()
        await models.SMSPostControl.filter(order_id=order_id).delete()
        await order_obj.save()

        await models.history_create(
            schemas.HistoryCreate(
                initiator_type=InitiatorType.USER,
                initiator_id=user.id if user else None,
                initiator_role=user.profile['profile_type'] if user else None,
                model_type=HistoryModelName.ORDER,
                model_id=order_id,
                request_method=RequestMethods.PATCH,
                action_data={
                    'delivery_status': {'status': 'restored'},
                    'deleted_product': product.attributes,
                },
                created_at=history_created_at,
            )
        )
    except DoesNotExist:
        raise DoesNotExist(
            f'Order with provided ID: {order_id} was not found',
        )

    await models.SMSPostControl.filter(order_id=order_id).delete()

    if not user:
        return


async def order_courier_assign(default_filters: list, order_id: int, courier_id: int, user: UserCurrent):
    try:
        await Order.filter(*default_filters).distinct().get(id=order_id)
        order_obj = await Order.get(id=order_id).select_related('city')
        old_courier = order_obj.courier_id
    except DoesNotExist:
        raise DoesNotExist(f'Order with given ID: {order_id} was not found')
    if not order_obj.allow_courier_assign:
        raise exceptions.HTTPBadRequestException(f'It is not allowed to assign a courier to the order')
    order_obj.courier_id = courier_id

    if order_obj.delivery_status.get('status') == enums.OrderDeliveryStatus.ADDRESS_CHANGED:
        order_obj.current_status_id = 2
        order_obj.delivery_status = {
            'status': None,
            'datetime': None,
            'comment': None,
            'reason': None,
        }

    async with in_transaction('default'):
        await order_obj.save()
        assigned_status = await models.Status.get(
            slug=StatusSlug.COURIER_ASSIGNED.value,
            partner_id__isnull=True,
        )

        await models.history_create(
            schemas.HistoryCreate(
                initiator_type=InitiatorType.USER,
                initiator_id=user.id if user else None,
                initiator_role=user.profile['profile_type'] if user else None,
                model_type=HistoryModelName.ORDER,
                model_id=order_id,
                request_method=RequestMethods.PATCH,
                action_data={
                    'courier': {
                        'old': old_courier,
                        'new': courier_id,
                    },
                },
                created_at=await order_obj.localtime,
            )
        )
    try:
        await order_update_status(order_obj, assigned_status.id)
    except (
        models.StatusAlreadyCurrent,
        models.StatusAfterError,
        IntegrityError,
    ):
        pass


async def order_revise(default_filters: list, order_id: int, revised: bool):
    try:
        order_to_revise = await Order.filter(*default_filters).distinct().get(id=order_id)
    except DoesNotExist:
        raise DoesNotExist('Order not found')
    order_to_revise.revised = revised
    await order_to_revise.save()


async def order_status_bulk_update(
    order_ids: List[int],
    status_id: Union[int, OrderStatus],
    default_filter_args: list = None,
):
    status = await models.Status.get(id=status_id)
    order_statuses = []
    order_ids_to_be_updated = []

    for order_id in order_ids:
        exists = await OrderStatuses.filter(order_id=order_id, status_id=status_id).exists()
        if not exists:
            order_obj = await Order.get(id=order_id).select_related('city')
            order_time = await order_obj.localtime
            order_statuses.append(
                OrderStatuses(order_id=order_id, status_id=status_id, created_at=order_time)
            )
            order_ids_to_be_updated.append(order_id)
    if order_statuses:
        await OrderStatuses.bulk_create(order_statuses)
        await Order.filter(id__in=order_ids_to_be_updated).update(current_status_id=status_id)
        if status.slug in (StatusSlug.POST_CONTROL, StatusSlug.DELIVERED, StatusSlug.ISSUED):
            await order_set_actual_delivery_datetime_bulk(*order_ids_to_be_updated)

    if status.slug == StatusSlug.ACCEPTED_BY_COURIER_SERVICE:
        await Order.filter(id__in=order_ids_to_be_updated).update(allow_courier_assign=True)
        current_time = now().replace(hour=23, minute=59, second=0, microsecond=0)
        delivery_time = current_time + datetime.timedelta(days=1)
        orders = await Order.select_for_update().filter(
            id__in=order_ids,
            delivery_datetime__isnull=True,
        ).prefetch_related('item')
        for order_obj in orders:
            if order_obj.item.days_to_delivery is not None:
                delivery_time = current_time + datetime.timedelta(order_obj.item.days_to_delivery)
            order_obj.delivery_datetime = delivery_time
            await order_obj.save()  # can't use bulk update with timestamp fields for now

        # can't use bulk update with timestamp fields until tortoise version>=0.19.0
        # if orders:
        #     await Order.bulk_update(orders, ['delivery_datetime'])


async def order_status_bulk_rollback(
    order_ids: List[int],
    status_id: Union[int, OrderStatus],
    include=True,
    default_filter_args: list = None,
):
    for idx in order_ids:
        query = []
        if last_order := await OrderStatuses.filter(
            order_id=idx, status_id=status_id
        ).first():
            if include:
                query.append(Q(id=last_order.id))
            query.append(Q(order_id=idx, created_at__gt=last_order.created_at))
            await OrderStatuses.filter(
                Q(
                    *query, join_type=Q.OR
                )
            ).delete()


async def order_update_status_v2(
    order_obj_or_id: int | Order,
    status_id: Union[int, OrderStatus],
    default_filter_args: list = None,
):
    status_obj = await models.Status.get(id=status_id)
    if default_filter_args is None:
        default_filter_args = []
    try:
        if isinstance(order_obj_or_id, int):
            order_obj = await Order.filter(*default_filter_args).distinct().get(
                id=order_obj_or_id,
            ).select_related('city')
        else:
            order_obj = order_obj_or_id
        if not hasattr(order_obj, 'statuses'):
            order_obj.statuses = await order_obj.status_set
    except DoesNotExist:
        raise DoesNotExist(f'Order with given ID: {order_obj_or_id} was not found')

    order_time = await order_obj.localtime

    if status_obj.slug == StatusSlug.ACCEPTED_BY_COURIER:
        order_obj.delivery_status = {
            'status': OrderDeliveryStatus.TO_CALL_POINT.value,
            'reason': None,
            'datetime': None,
            'comment': None,
        }
    if status_obj.slug == StatusSlug.DELIVERED:
        order_obj.delivery_status = {
            'status': OrderDeliveryStatus.IS_DELIVERED.value,
            'reason': None,
            'datetime': None,
            'comment': None,
        }

        if url := order_obj.callbacks.get('set_pan'):
            product = await order_obj.product
            if product is not None:
                pan = product.attributes.get('pan')
                if pan is not None:
                    data = {'pan_card': pan}
                    conn = redis_module.get_connection()
                    await conn.publish(
                        channel='send-to-celery',
                        message=json.dumps({
                            'task_name': 'send-pan',
                            'kwargs': {
                                'url': url,
                                'data': data,
                            }
                        })
                    )

        # В v2 отправлять SMS не нужно
        #
        # if url := order_obj.callbacks.get('set_otp', None):
        #     stored_otp_objects = await order_obj.otp_set.filter(accepted_at__isnull=False)
        #     if stored_otp_objects:
        #         last_otp = stored_otp_objects[0]
        #         stored_code = last_otp.otp
        #         timestamp = int(last_otp.accepted_at.strftime('%s'))
        #         data = {
        #             'url': url,
        #             'data': {
        #                 'otp': str(stored_code),
        #                 'datetime_otp': timestamp,
        #             }
        #         }
        #         conn = redis_module.get_connection()
        #         await conn.publish(
        #             channel='send-to-celery',
        #             message=json.dumps({
        #                 'task_name': 'send-otp',
        #                 'kwargs': data,
        #             })
        #         )
    if status_obj.slug == StatusSlug.ACCEPTED_BY_COURIER_SERVICE:
        order_obj.allow_courier_assign = True

    if status_obj.slug == StatusSlug.DELIVERED.value:
        link = f'https://{conf.frontend.domain}/' + conf.frontend.feedback_url
        await send_feedback_link(
            phone=order_obj.receiver_phone_number,
            link=link.format(order_obj.id),
            receiver_full_name=order_obj.receiver_name,
            related_order_id=order_obj.id
        )

    await models.OrderStatuses.create(
        order_id=order_obj.id,
        status_id=status_id,
        created_at=order_time,
    )
    order_obj.current_status = status_obj
    await order_obj.save()

    if status_obj.slug in (StatusSlug.DELIVERED, StatusSlug.ACCEPTED_BY_COURIER):
        if callback_url := order_obj.callbacks.get('set_status'):
            data = schemas.DeliveryStatusExternal(
                status=order_obj.delivery_status['status'],
                status_datetime=str(order_time)).dict()

            # В зависимости от партнера, получаем HTTP заголовки для вызова callback метода
            headers = get_headers(order_obj.partner_id)
            await publish_callback(
                task_name='send-status',
                url=callback_url,
                data=data,
                headers=headers,
            )

    if status_obj.slug in (StatusSlug.POST_CONTROL, StatusSlug.ISSUED, StatusSlug.DELIVERED):
        await order_set_actual_delivery_datetime(order_obj)

    status = await order_get_status(order_obj.id, status_id)

    await websocket_manager.send_order_status_update(
        order_id=order_obj.id, order_status=status)
    return await order_get_current_status(order_obj.id)


async def order_update_status(
    order_obj_or_id: int | Order,
    status_id: Union[int, OrderStatus],
    default_filter_args: list = None,
):
    status_obj = await models.Status.get(id=status_id)
    if default_filter_args is None:
        default_filter_args = []
    try:
        if isinstance(order_obj_or_id, int):
            order_obj = await Order.filter(*default_filter_args).distinct().get(
                id=order_obj_or_id,
            ).select_related('city')
        else:
            order_obj = order_obj_or_id
        if not hasattr(order_obj, 'statuses'):
            order_obj.statuses = await order_obj.status_set
    except DoesNotExist:
        raise DoesNotExist(f'Order with given ID: {order_obj_or_id} was not found')

    order_time = await order_obj.localtime

    if status_obj.slug == StatusSlug.ACCEPTED_BY_COURIER:
        order_obj.delivery_status = {
            'status': OrderDeliveryStatus.TO_CALL_POINT.value,
            'reason': None,
            'datetime': None,
            'comment': None,
        }
    if status_obj.slug == StatusSlug.DELIVERED:
        order_obj.delivery_status = {
            'status': OrderDeliveryStatus.IS_DELIVERED.value,
            'reason': None,
            'datetime': None,
            'comment': None,
        }

        if url := order_obj.callbacks.get('set_pan'):
            product = await order_obj.product
            if product is not None:
                pan = product.attributes.get('pan')
                if pan is not None:
                    data = {'pan_card': pan}
                    conn = redis_module.get_connection()
                    await conn.publish(
                        channel='send-to-celery',
                        message=json.dumps({
                            'task_name': 'send-pan',
                            'kwargs': {
                                'url': url,
                                'data': data,
                            }
                        })
                    )

        if url := order_obj.callbacks.get('set_otp', None):
            stored_otp_objects = await order_obj.otp_set.filter(accepted_at__isnull=False)
            if stored_otp_objects:
                last_otp = stored_otp_objects[0]
                stored_code = last_otp.otp
                timestamp = int(last_otp.accepted_at.strftime('%s'))
                data = {
                    'url': url,
                    'data': {
                        'otp': str(stored_code),
                        'datetime_otp': timestamp,
                    }
                }
                conn = redis_module.get_connection()
                await conn.publish(
                    channel='send-to-celery',
                    message=json.dumps({
                        'task_name': 'send-otp',
                        'kwargs': data,
                    })
                )
    if status_obj.slug == StatusSlug.ACCEPTED_BY_COURIER_SERVICE:
        order_obj.allow_courier_assign = True

    if status_obj.slug == StatusSlug.DELIVERED.value:
        link = f'https://{conf.frontend.domain}/' + conf.frontend.feedback_url
        await send_feedback_link(
            phone=order_obj.receiver_phone_number,
            link=link.format(order_obj.id),
            receiver_full_name=order_obj.receiver_name,
            related_order_id=order_obj.id
        )

    await models.OrderStatuses.create(
        order_id=order_obj.id,
        status_id=status_id,
        created_at=order_time,
    )
    order_obj.current_status = status_obj
    await order_obj.save()

    if status_obj.slug in (StatusSlug.DELIVERED, StatusSlug.ACCEPTED_BY_COURIER):
        if callback_url := order_obj.callbacks.get('set_status'):
            data = schemas.DeliveryStatusExternal(
                status=order_obj.delivery_status['status'],
                status_datetime=str(order_time)).dict()

            # В зависимости от партнера, получаем HTTP заголовки для вызова callback метода
            headers = get_headers(order_obj.partner_id)
            await publish_callback(
                task_name='send-status',
                url=callback_url,
                data=data,
                headers=headers,
            )

    if status_obj.slug in (StatusSlug.POST_CONTROL, StatusSlug.ISSUED, StatusSlug.DELIVERED):
        await order_set_actual_delivery_datetime(order_obj)

    status = await order_get_status(order_obj.id, status_id)

    await websocket_manager.send_order_status_update(
        order_id=order_obj.id, order_status=status)
    return await order_get_current_status(order_obj.id)


async def order_get_status(order_id: int, status_id: int) -> dict:
    order_statuses = (await Order.get(id=order_id).prefetch_related(
        Prefetch('status_set', OrderStatuses.all().prefetch_related('status'),
                 'statuses')
    )).statuses
    order_statuses = parse_obj_as(List[schemas.OrderStatusGetWithDatetime],
                                  order_statuses)
    order_statuses_ids = await OrderStatuses.filter(order_id=order_id).values_list(
        'status_id',
        flat=True)

    if int(status_id) in order_statuses_ids:
        status = next(
            filter(lambda o_status: o_status.status.id == int(status_id),
                   order_statuses))
        result = {
            'order_id': order_id,
            'status': status.status,
            'created_at': status.created_at,
        }
        return result

    raise OrderEntitiesError(
        f'Order with provided ID: {order_id} does not have provided status')


async def order_get_current_status(order_id: int,
                                   default_filter_args: list = None) -> schemas.OrderStatusGet:
    if default_filter_args is None:
        default_filter_args = []
    order_status_obj = await models.OrderStatuses.filter(
        *default_filter_args,
        order_id=order_id,
    ).distinct().order_by('-created_at').first()
    if not order_status_obj:
        raise DoesNotExist(f'Order with given ID: {order_id} was not found')
    current_status = await models.status_get(order_status_obj.status_id)
    order_obj = await models.Order.all_objects.get(id=order_id)

    return schemas.OrderStatusGet(
        order_id=order_id,
        delivery_status=order_obj.delivery_status,
        status=current_status,
        created_at=order_status_obj.created_at,
    )


async def order_import_history(**kwargs):
    current_user_id = kwargs.pop('current_user')
    user_id = current_user_id.profile['user_id']
    current_user = await models.user_get(id=user_id)
    courier_partner_id = current_user.get('partners')[0]
    kwargs['model_id'] = courier_partner_id
    kwargs['model_type'] = HistoryModelName.IMPORT_ORDER.value
    history = await models.history_get_list(**kwargs)
    return history


async def translate_delivery_status(status: str, description_statuses: dict):
    swapped_description = dict((v, k) for k, v in description_statuses.items())
    if status in swapped_description:
        status_in_rus = swapped_description[status]
        return status_in_rus


async def get_order_history(history):
    history_str = ''
    for history_item in history:
        if history_item.request_method in [RequestMethods.PUT,
                                           RequestMethods.PATCH]:
            history_time = history_item.created_at.strftime("%Y-%m-%d %H:%M:%S")
            action_data = history_item.action_data
            if action_data:
                if action_data.get('change_type') == OrderChangeAddressType.RESTORE:
                    history_str = 'Адрес изменен ({}); '.format(
                        history_time) + history_str
                if action_data.get('delivery_status', None):
                    status = action_data['delivery_status'].get('status', None)
                    status_comment = action_data['delivery_status'].get('comment', '')
                    if not status_comment:
                        status_comment = action_data['delivery_status'].get('reason', '')
                    if not status:
                        status = 'is_reset'

                    status_description, *_ = delivery_status_description.values()
                    translate_to_russ = await translate_delivery_status(status,
                                                                        status_description)
                    history_str = '{} ({}, comment: {});  '.format(translate_to_russ,
                                                                   history_time,
                                                                   status_comment) + history_str
    return history_str


async def order_report(query: schemas.ExportExcel, profile_type, **kwargs):
    buffer = io.BytesIO()
    with xlsxwriter.Workbook(buffer, options={'remove_timezone': True}) as workbook:
        sheet = workbook.add_worksheet()
        format_datetime = workbook.add_format(
            {'num_format': 'yyyy-mm-dd hh:mm:ss', }
        )
        field_names = [
            'ID',
            'ID заявки партнера',
            'Дата создания',
            'ФИО получателя',
            'ИИН получателя',
            'Номер получателя',
            'Номер карты',
            'Тип',
            'Доставить до',
            'Исходная дата доставки',
            'Фактическая дата доставки',
            'Город',
            'Партнер',
            'Продукт',
            'Зона доставки',
            'Курьер',
            'Статус',
            'Адрес доставки',
            'История заявок',
            'Комментарии',
            'Coздавший последконтроль',
            'Принявший последконтроль',
            'Дата назначения курьера',
            'Дата текущего статуса',
            'Текущий статус',
        ]
        if profile_type == ProfileType.BANK_MANAGER:
            field_names = [
                'ID заявки',
                'ФИО',
                'Продукт',
                'IDN карты',
                'Номер телефона',
                'ИИН',
                'Адрес доставки',
                'Город доставки',
                'Страна доставки',
                'Менеджер',
                'Партнёр',
                'Дата создания',
                'Дата назначения курьера',
                'Дата доставки',
                'Статус',
            ]
        for col_num, field in enumerate(field_names):
            cell_format = workbook.add_format(
                {
                    'bold': True,
                    'font_color': 'white',
                    'bg_color': 'green',
                    'align': 'left',
                }
            )
            sheet.write(0, col_num, str(field))
            sheet.set_column(col_num, col_num, 10, cell_format)

        filter_dict = query.filtering.dict(exclude_unset=True, exclude_none=True)
        if partner_filter := filter_dict.pop('partner_id__in', None):
            if 'partner_id__in' in kwargs:
                intersection = set(partner_filter) & set(kwargs['partner_id__in'])
                kwargs['partner_id__in'] = list(intersection)
        orders = await prepare_orders_for_report(
            columns=field_names,
            **filter_dict,
            **kwargs,
        )
        for row, order in enumerate(orders, 1):
            order.append(' ')
            sheet.write_row(row=row, col=0, data=order, cell_format=format_datetime)

        workbook.read_only_recommended()
    buffer.seek(0)
    return buffer


async def order_delivered_today(courier_id: int) -> int:
    courier_obj = await ProfileCourier.get(id=courier_id)
    courier_time = await courier_obj.localtime
    return await models.OrderStatuses.filter(
        order__courier_id=courier_id,
        status_id=OrderStatus.DELIVERED.value,
        created_at__lt=courier_time,
    ).count()


async def order_average_time_deviation(courier_id: int) -> int:
    deviation = 0

    delivered_orders_query = OrderStatuses.filter(
        order__courier_id=courier_id,
        status_id=7,
    )

    delivered_orders = await delivered_orders_query.values_list(
        'order__delivery_datetime',
        'created_at',
    )

    for order in delivered_orders:
        delivery_dt, created_at = order

        if delivery_dt and created_at < delivery_dt:
            deviation += int((delivery_dt - created_at).total_seconds())

    return deviation


def order_import_get_sample(current_user):
    if current_user.profile['profile_type'] == ProfileType.MANAGER:
        return conf.static.root / 'orders_sample_manager_partner.xlsx'
    if current_user.profile['profile_type'] == ProfileType.BANK_MANAGER:
        return conf.static.root / 'orders_sample_bank_manager.xlsx'
    return conf.static.root / 'orders_sample_service_manager.xlsx'


async def order_import_from_excel(file: UploadFile, **kwargs):
    current_user = kwargs.get('current_user', None)
    processed_file, result = await services.excel_loader.service.get_models_from_excel(
        model_name='Order',
        file=file,
        current_user=current_user
    )
    resp = schemas.ImportExcelResponse(file=processed_file, result=result)
    return resp


async def order_biometry_verify(order_id, request_body):
    try:
        order_obj = await Order.get(id=order_id)
        if request_body.success:
            if status_video := await models.Status.filter(
                slug=StatusSlug.VIDEO_IDENTIFICATION.value,
                partner_id__isnull=True,
            ).first():
                try:
                    await order_update_status(order_obj, status_video.id)
                except StatusAlreadyCurrent:
                    pass
            if status_passed := await models.Status.filter(
                slug=StatusSlug.DELIVERED.value,
                partner_id__isnull=True,
            ).first():
                await order_update_status(order_obj, status_passed.id)
                order_obj.delivery_status = {
                    'status': OrderDeliveryStatus.IS_DELIVERED.value,
                    'reason': None,
                    'datetime': None,
                    'comment': None,
                }
                await order_obj.save()

        else:
            order_obj.delivery_status = {
                'status': OrderDeliveryStatus.VIDEO_CHECK_FAILED.value,
                'reason': None,
                'datetime': None,
                'comment': None,
            }
            await order_obj.save()
    except DoesNotExist:
        raise DoesNotExist(f'Order with provided ID: {order_id} was not found')


@atomic()
async def order_sms_postcontrol(
        order: Order,
        at_client_point: schemas.Coordinates,
):
    """
        Используется для всех ОСТАЛЬНЫХ партнеров. Используется НАШ ОТП сервис.
    """

    order_time = await order.localtime

    otp_code = await models.utils.create_otp()
    await models.SMSPostControl.create(
        otp=otp_code,
        order_id=order.id,
        created_at=order_time,
    )

    geolocation = await order.geolocation
    if not geolocation and order.courier_id:
        location = at_client_point.to_tuple() if at_client_point else None
        await OrderGeolocation.create(
            order_id=order.id,
            at_client_point=location,
            courier_id=order.courier_id,
            created_at=order_time,
        )

    await send_post_control_otp(
        phone=order.receiver_phone_number,
        otp_code=otp_code,
        receiver_full_name=order.receiver_name,
        related_order_id=order.id
    )


async def get_next_status_from_status(order_obj: Order, status_slug: str) -> Optional['models.Status']:
    if not isinstance(order_obj.deliverygraph, models.DeliveryGraph):
        await order_obj.fetch_related('deliverygraph')
    graph = order_obj.deliverygraph.graph
    current_status_list = list(
        filter(lambda g: g['slug'] == status_slug, graph),
    )
    if not current_status_list:
        current_status = {'position': 1}
    else:
        current_status = current_status_list[0]
    next_status = list(
        filter(lambda g: g['position'] == current_status['position'] + 1, graph),
    )
    if next_status:
        next_status_obj = await models.Status.filter(id=next_status[0]['id']).first()
        return next_status_obj

# TODO: Костыль, чтобы вернуть заявку после верефикации ОТП
async def get_order_for_order_sms_postcontrol_check(
        order_id: int,
):
    order_qs = Order.get(id=order_id).prefetch_related(
        Prefetch('status_set', OrderStatuses.all().prefetch_related('status'),
                 'statuses'),
        Prefetch('address_set', OrderAddress.all().prefetch_related('place'),
                 'addresses'),
        Prefetch('postcontrol_set', models.PostControl.all(), 'postcontrols'),
        Prefetch('item__postcontrol_config_set', models.PostControlConfig.filter(
            parent_config_id__isnull=True,
            type=PostControlType.POST_CONTROL.value,
        ).prefetch_related(
            Prefetch('inner_param_set', models.PostControlConfig.filter(
                type=PostControlType.POST_CONTROL.value,
            ).prefetch_related(
                Prefetch(
                    'postcontrol_document_set',
                    models.PostControl.filter(order_id=order_id),
                    'postcontrol_documents',
                ),
            ), 'inner_params'),
            Prefetch(
                'postcontrol_document_set',
                models.PostControl.filter(order_id=order_id),
                'postcontrol_documents',
            ),
        ), 'postcontrol_configs'),
    ).select_related('area', 'city', 'courier__user', 'item', 'deliverygraph', 'partner', 'product')

    return schemas.OrderGetV1.from_orm(await order_qs)

async def order_sms_postcontrol_check(
        order: Order,
        code,
        code_sent_point: schemas.Coordinates,
):
    order_time = await order.localtime
    stored_otp_objects = await order.otp_set
    if not stored_otp_objects:
        raise OrderSmsCheckError(
            OrderSMS.SEND_SMS,
        )
    last_otp: models.SMSPostControl = stored_otp_objects[0]
    stored_code = last_otp.otp
    async with in_transaction('default'):
        # TODO: Храним int, получаем str, привидение типов как костыль
        if str(stored_code) != code:
            last_otp.try_count += 1
            last_otp.updated_at = order_time
            await last_otp.save()

            raise OrderSmsCheckError(
                OrderSMS.NOT_MATCH,
            )

        order_qs = Order.get(id=order.id).prefetch_related(
            Prefetch('status_set', OrderStatuses.all().prefetch_related('status'),
                     'statuses'),
            Prefetch('address_set', OrderAddress.all().prefetch_related('place'),
                     'addresses'),
            Prefetch('postcontrol_set', models.PostControl.all(), 'postcontrols'),
        ).select_related('area', 'city', 'courier__user', 'item', 'deliverygraph', 'partner', 'product')

        if any(otp_object.accepted_at is not None for otp_object in stored_otp_objects):
            return schemas.OrderGetV1.from_orm(await order_qs)

        last_otp = await order.otp_set.all().first().select_for_update()
        last_otp.accepted_at = order_time
        await last_otp.save()

        geolocation = await order.geolocation
        if geolocation and code_sent_point:
            geolocation = await order.geolocation.select_for_update()
            geolocation.code_sent_point = code_sent_point.to_tuple()
            await geolocation.save()

    next_status_obj = await get_next_status_from_status(order, StatusSlug.SMS_SENT.value)
    if next_status_obj:
        try:
            await order_update_status(order, next_status_obj.id)
        except (
            StatusAfterError,
            IntegrityError,
        ):
            pass
        async with in_transaction('default'):
            order.current_status = next_status_obj
            await order.save()
            if next_status_obj.slug in (StatusSlug.ISSUED, StatusSlug.DELIVERED):
                await order_set_actual_delivery_datetime(order)
            if next_status_obj.slug == StatusSlug.DELIVERED:
                order.delivery_status = {
                    'status': OrderDeliveryStatus.IS_DELIVERED.value,
                    'reason': None,
                    'datetime': None,
                    'comment': None,
                }
                await order.save()

    return schemas.OrderGetV1.from_orm(await order_qs)


@atomic()
async def order_cancel_at_client(order_id, image, reason, current_user: schemas.UserCurrent, default_filter_args):
    try:
        order_obj = await Order.filter(*default_filter_args).distinct().get(id=order_id).select_related(
            'courier__user', 'city',
        )
    except DoesNotExist:
        raise DoesNotExist('Order could not found')
    order_obj.delivery_status = {
        'status': OrderDeliveryStatus.CANCELED_AT_CLIENT.value,
        'reason': reason,
        'datetime': None,
        'comment': None,
    }
    await order_obj.save()
    postcontrol = None
    if image is not None:
        postcontrol = await models.PostControl.create(
            order_id=order_id,
            image=image,
            type=PostControlType.CANCELED_AT_CLIENT.value,
        )

    order_time = await order_obj.localtime

    if callback_url := order_obj.callbacks.get('set_status', None):
        data = schemas.DeliveryStatusExternal(
            status=order_obj.delivery_status.get('status'),
            comment=order_obj.delivery_status.get('reason'),
            status_datetime=str(order_time),
        ).dict()

        # В зависимости от партнера, получаем HTTP заголовки для вызова callback метода
        headers = get_headers(order_obj.partner_id)
        await publish_callback(
            task_name='send-status',
            url=callback_url,
            data=data,
            headers=headers,
        )

    courier = order_obj.courier

    await models.history_create(
        schemas.HistoryCreate(
            initiator_type=InitiatorType.USER,
            initiator_id=current_user.id,
            model_type=HistoryModelName.ORDER,
            model_id=order_id,
            request_method=RequestMethods.PUT,
            initiator_role=current_user.profile['profile_type'],
            action_data={
                'delivery_status': order_obj.delivery_status,
                'postcontrol': postcontrol.image if postcontrol else None,
                'courier_id': courier.id if courier else None,
            },
            created_at=order_time,
        )
    )


@atomic()
async def order_reschedule(order_id, update, **kwargs):
    current_user_id = kwargs.pop('current_user_id')
    current_user_role = kwargs.pop('current_user_role')
    try:
        order_obj = await Order.filter(**kwargs).distinct().get(id=order_id).select_related('city')
    except DoesNotExist:
        raise DoesNotExist('Order could not found')
    order_obj.delivery_status = {
        'status': OrderDeliveryStatus.RESCHEDULED.value,
        'reason': update.reason,
        'datetime': None,
        'comment': None,
    }
    order_obj.delivery_datetime = update.delivery_datetime
    await order_obj.save()
    if callback_url := order_obj.callbacks.get('set_status', None):
        data = schemas.DeliveryStatusExternal(
            status=order_obj.delivery_status.get('status'),
            comment=order_obj.delivery_status.get('reason'),
            status_datetime=str(await order_obj.localtime)).dict()

        # В зависимости от партнера, получаем HTTP заголовки для вызова callback метода
        headers = get_headers(order_obj.partner_id)
        await publish_callback(
            task_name='send-status',
            url=callback_url,
            data=data,
            headers=headers,
        )

    order_time = await order_obj.localtime

    await models.history_create(
        schemas.HistoryCreate(
            initiator_type=InitiatorType.USER,
            initiator_role=current_user_role,
            initiator_id=current_user_id,
            model_type=HistoryModelName.ORDER,
            model_id=order_id,
            request_method=RequestMethods.PUT,
            action_data={
                'delivery_status': order_obj.delivery_status
            },
            created_at=order_time,
        )
    )


async def order_distribution_for_area(**kwargs) -> None:
    current_user = kwargs.pop('current_user')
    current_user_profile_type = current_user.profile['profile_type']
    partner_id = current_user.profile.get('profile_content').get('partner_id')
    if current_user_profile_type == ProfileType.SERVICE_MANAGER:
        filter_params = {
            'partner_id': current_user.profile.get('profile_content').get(
                'partner_id',
            ),
        }
    else:
        raise exceptions.HTTPUnauthorizedException()
    areas = await models.Area.filter(**filter_params).select_related('city')
    for area in areas:
        localtime = area.city.localtime
        partners_ids = await models.Partner.filter(
            courier_partner_id=partner_id,
        ).values_list('id', flat=True)

        orders = await Order.filter(
            courier_id__isnull=True,
            area_id=area.id,
            partner_id__in=partners_ids,
            delivery_datetime__year=localtime.year,
            delivery_datetime__month=localtime.month,
            delivery_datetime__day=localtime.day,
        ).order_by('-delivery_datetime')
        orders_filtered = []
        for order_obj in orders:
            if order_obj.delivery_status.get('status', None) not in [
                OrderDeliveryStatus.CANCELLED,
                OrderDeliveryStatus.POSTPONED,
            ]:
                orders_filtered.append(order_obj)
        couriers = await ProfileCourier.filter(
            areas__id=area.id,
            partner_id=partner_id,
            # at_work=True,
            user__is_active=True,
        )
        try:
            await router.order_distribution(orders_filtered, couriers)
        except (NotDistributionCouriersError, NotDistributionOrdersError) as e:
            logger.info(e)


@atomic()
async def order_mass_courier_assign(
    data: schemas.OrderMassCourierAssign,
    bg,
    default_filter_args,
):
    courier = await models.profile_get_by_id(
        profile_id=data.courier_id,
        profile_type=ProfileType.COURIER,
    )
    given_order_count = len(data.orders)
    has_ready_for_shipment = f"order__deliverygraph.graph @? '$.slug[*] ? (@ == \"{StatusSlug.READY_FOR_SHIPMENT}\")'"

    orders = await models.Order.annotate(
        has_ready_for_shipment=RawSQL(has_ready_for_shipment),
    ).filter(
        *default_filter_args,
        id__in=data.orders,
        current_status__slug=StatusSlug.NEW.value,
        deliverygraph__id__isnull=False,  # needed to join deliverygraph table only.
    )
    actual_order_count = len(orders)

    if given_order_count != actual_order_count:
        raise DoesNotExist(
            'Some orders was not found',
        )

    for order_obj in orders:
        order_obj.courier_id = courier.id
        await order_obj.save(update_fields=['courier_id', ])
        await order_update_status(
            order_obj_or_id=order_obj,
            status_id=OrderStatus.COURIER_ASSIGNED,
        )

    if fcmdevice_ids := await models.FCMDevice.filter(
        user__profile_courier=courier.id,
    ).values_list('id', flat=True):
        message = schemas.FirebaseMessage(
            registration_ids=fcmdevice_ids,
            data={
                'title': f'Новые заявки',
                'description': f'На Вас назначены несколько заявок',
                'push_type': PushType.INFO,
            }
        )
        bg.add_task(services.firebase.service.send, message=message)


@atomic()
async def order_mass_status_update(
    data: schemas.OrderMassStatusUpdate, **kwargs,
):
    current_user = kwargs.pop('current_user')
    given_order_count = len(data.orders)
    qs = await models.Order.filter(
        id__in=data.orders,
        **kwargs,
    ).exclude(
        delivery_status={'status': OrderDeliveryStatus.IS_DELIVERED},
        archived=True).select_related('city')
    actual_order_count = len(qs)
    if given_order_count != actual_order_count:
        raise models.OrderNotFound(
            'Some orders was not found',
        )
    dict_delivery_status = data.delivery_status.dict()
    for order_obj in qs:
        action_data = None
        if data.delivery_status.status in [
            OrderDeliveryStatus.POSTPONED.value,
            OrderDeliveryStatus.CANCELLED.value
        ]:  # if order cancelled or postponed
            order_obj.delivery_status = data.delivery_status.dict()
            if data.delivery_datetime:
                order_obj.delivery_datetime = data.delivery_datetime
            await order_obj.save()
            action_data = {
                'delivery_status': data.delivery_status.dict(),
            }

        elif dict_delivery_status.get('status', None) is None:
            await models.order_restore(order_obj.id, schemas.OrderRestore(
                delivery_datetime=data.delivery_datetime,
                courier_id=None,
                delivery_status={
                    'status': None,
                    'reason': None,
                    'datetime': None,
                    'comment': None,
                }
            ))
            action_data = {
                'delivery_status': {'status': 'restored'},
            }
        if action_data:
            order_time = await order_obj.localtime
            await models.history_create(
                schemas.HistoryCreate(
                    initiator_type=InitiatorType.USER,
                    initiator_id=current_user.id,
                    initiator_role=current_user.profile['profile_type'],
                    model_type=HistoryModelName.ORDER,
                    model_id=order_obj.id,
                    request_method=RequestMethods.PATCH,
                    action_data=action_data,
                    created_at=order_time,
                )
            )


async def order_distribution_selective(**kwargs) -> List:
    current_user = kwargs.pop('current_user')
    selective_order_ids = kwargs.pop('selective_order_ids', None)
    partner_id = current_user.profile.get('profile_content').get('partner_id')
    filter_params = {
        'partner_id': current_user.profile['profile_content']['partner_id']
    }
    areas = await models.Area.filter(**filter_params)
    not_distributed_orders = []
    for area in areas:
        orders = await Order.filter(
            id__in=selective_order_ids, area_id=area.id
        ).order_by('-delivery_datetime')
        couriers = await ProfileCourier.filter(
            areas__id=area.id,
            partner_id=partner_id,
            # at_work=True,
            user__is_active=True,
        )
        logger.info(couriers)
        try:
            await router.order_distribution(orders, couriers)
            for courier_obj in couriers:
                courier_time = await courier_obj.localtime
                orders = await get_current_orders_for_courier(courier_obj.id)
                courier_orders = await models.Order.filter(
                    ~Q(delivery_status__filter={
                        'status': OrderDeliveryStatus.IS_DELIVERED.value}
                    ),
                    delivery_datetime__year=courier_time.year,
                    delivery_datetime__month=courier_time.month,
                    delivery_datetime__day=courier_time.day,
                    courier_id=courier_obj.id,
                )
                await redistribute_order_immediately_for_current_courier(
                    courier_orders, courier_obj,
                )
        except (NotDistributionCouriersError, NotDistributionOrdersError) as e:
            logger.info(e)
        not_distributed_orders.extend(
            [order_obj.id for order_obj in orders if order_obj.courier_id is None]
        )

    return not_distributed_orders


@atomic()
async def order_address_update(
    order_id: int,
    update: schemas.OrderAddressChange,
    current_user: schemas.UserCurrent,
):
    delivery_service_partner_id = current_user.profile.get('profile_content').get('partner_id')
    try:
        order_obj = await models.Order.get(id=order_id).prefetch_related(
            'address_set__place').select_related('city')
    except DoesNotExist:
        raise DoesNotExist(f'Order with provided ID: {order_id} was not found')
    order_addresses = await order_obj.address_set.all().values('place__id', 'place__address')
    for place_obj in update.places:
        place_dict = place_obj.dict()
        place_id = place_dict.pop('id', None)
        dp_repo, sp_repo = DeliveryPointRepository(), ShipmentPointRepository()
        place_is_sp = await sp_repo.ensure_exist([], entity_id=place_id)
        place_is_dp = await dp_repo.ensure_exist([], entity_id=place_id)

        if place_id not in [item_obj['place__id'] for item_obj in order_addresses] and not place_is_sp and not place_is_dp:
            raise models.PlaceNotFound(
                f'Place with ID {place_id} not found on current order')
        await models.place_update(place_id, schemas.PlaceUpdate(**place_dict))

    match update.change_type:
        case OrderChangeAddressType.RESTORE:
            await models.order_restore(order_id, schemas.OrderRestore(
                delivery_datetime=update.delivery_datetime, courier_id=None
            ))

        case OrderChangeAddressType.NEW_COURIER_NEW_DELIVERY_DATETIME:
            await order_obj.update_from_dict({
                'delivery_datetime': update.delivery_datetime
            })
            await distribute_order_immediately_for_all_couriers(
                [order, ], delivery_service_partner_id
            )

        case OrderChangeAddressType.NEW_COURIER_SAVE_DELIVERY_DATETIME:
            await models.order_restore(order_id)
            await distribute_order_immediately_for_all_couriers(
                [order, ], delivery_service_partner_id
            )

        case OrderChangeAddressType.SAVE_COURIER_NEW_DELIVERY_DATETIME:
            await order_obj.update_from_dict({
                'delivery_datetime': update.delivery_datetime
            })
            orders = await get_current_orders_for_courier(order_obj.courier_id)
            if not orders:
                orders.append(order_obj)
            courier = await models.ProfileCourier.filter(id=order_obj.courier_id).first()
            await redistribute_order_immediately_for_current_courier(orders, courier)

        case OrderChangeAddressType.SAVE_COURIER_SAVE_DELIVERY_DATETIME:
            orders = await get_current_orders_for_courier(order_obj.courier_id)
            if not orders:
                orders.append(order_obj)
            courier = await models.ProfileCourier.filter(id=order_obj.courier_id).first()
            await redistribute_order_immediately_for_current_courier(orders, courier)
    await check_is_delivery_points_in_polygon(
        order_obj,
        delivery_service_partner_id
    )

    order_time = await order_obj.localtime
    update_dict = update.dict()
    update_dict['old_places'] = [
        {
            key.replace('place__', ''): value for key, value in item_obj.items()
        } for item_obj in order_addresses
    ]
    await models.history_create(
        schemas.HistoryCreate(
            initiator_type=InitiatorType.USER,
            initiator_id=current_user.id,
            initiator_role=current_user.profile['profile_type'],
            model_type=HistoryModelName.ORDER,
            model_id=order_id,
            request_method=RequestMethods.PUT,
            action_data=update_dict,
            created_at=order_time,
        )
    )


@atomic()
async def order_address_update_v2(
    order_id: int,
    update: schemas.OrderAddressChangeV2,
    current_user: schemas.UserCurrent,
):

    delivery_service_partner_id = current_user.profile.get('profile_content').get('partner_id')
    try:
        order_obj = await models.Order.get(id=order_id)
    except DoesNotExist:
        raise DoesNotExist(f'Order with provided ID: {order_id} was not found')
    old_delivery_point = await order_obj.delivery_point.first().values('id', 'address')
    if city_id := update.city_id:
        order_obj.city_id = city_id
        await order_obj.save()
    dp_repo = DeliveryPointRepository()
    # noinspection PyTypeChecker
    await dp_repo.partial_update(order_obj.delivery_point_id, update.delivery_point, ())

    match update.change_type:
        case OrderChangeAddressType.RESTORE:
            await models.order_restore(
                order_id,
                schemas.OrderRestore(
                    delivery_datetime=update.delivery_datetime,
                    courier_id=None,
                ),
                user=current_user,
            )

        case OrderChangeAddressType.NEW_COURIER_NEW_DELIVERY_DATETIME:
            await order_obj.update_from_dict({
                'delivery_datetime': update.delivery_datetime
            })
            await distribute_order_immediately_for_all_couriers(
                [order_obj, ], delivery_service_partner_id
            )

        case OrderChangeAddressType.NEW_COURIER_SAVE_DELIVERY_DATETIME:
            await models.order_restore(order_id, user=current_user)
            await distribute_order_immediately_for_all_couriers(
                [order_obj, ], delivery_service_partner_id
            )

        case OrderChangeAddressType.SAVE_COURIER_NEW_DELIVERY_DATETIME:
            await order_obj.update_from_dict({
                'delivery_datetime': update.delivery_datetime
            })
            orders = await get_current_orders_for_courier(order_obj.courier_id)
            if not orders:
                orders.append(order_obj)
            courier = await models.ProfileCourier.filter(id=order_obj.courier_id).first()
            await redistribute_order_immediately_for_current_courier(orders, courier)

        case OrderChangeAddressType.SAVE_COURIER_SAVE_DELIVERY_DATETIME:
            orders = await get_current_orders_for_courier(order_obj.courier_id)
            if not orders:
                orders.append(order_obj)
            courier = await models.ProfileCourier.filter(id=order_obj.courier_id).first()
            await redistribute_order_immediately_for_current_courier(orders, courier)
    await check_is_delivery_points_in_polygon(
        order_obj,
        delivery_service_partner_id
    )

    order_time = await order_obj.localtime

    update_dict = update.dict()
    update_dict['old_delivery_point'] = old_delivery_point
    await models.history_create(
        schemas.HistoryCreate(
            initiator_type=InitiatorType.USER,
            initiator_id=current_user.id,
            initiator_role=current_user.profile['profile_type'],
            model_type=HistoryModelName.ORDER,
            model_id=order_id,
            request_method=RequestMethods.PUT,
            action_data=update_dict,
            created_at=order_time,
        )
    )
    return old_delivery_point


@atomic()
async def external_order_create_v2(
    order: schemas.ExternalOrderCreate,
    product_payload: typing.Optional[typing.Union[CardPayload, POSTerminalPayload]],
    partner_id: int,
) -> int:
    order_dict = order.dict(exclude_unset=True)
    city_name = order_dict.pop('city', None)
    if city_name:
        try:
            city = await City.get(
                Q(name_en=city_name, name_ru=city_name, name_kk=city_name, name_zh=city_name, join_type=Q.OR),
            )
            order_dict['city_id'] = city.id
        except DoesNotExist:
            raise DoesNotExist(f'City with provided name {city_name} not found')
    partner_dict = await models.partner_get(partner_id)
    order_dict['partner_id'] = partner_dict.get('id')
    order_dict['created_by'] = CreatedType.INTEGRATION

    try:
        item_obj = await models.Item.filter(
            id=order_dict.get('item_id'), partner_id=partner_id
        ).first()
        if not item_obj:
            raise models.ItemNotFound(
                f"Item with provided partner_id: "
                f"{partner_id} and item_id {order_dict.get('item_id')}"
                f", not found"
            )
        if order.product_type == enums.ProductType.SEP_UNEMBOSSED:
            client_code = product_payload.client_code
            if not client_code:
                raise ValueError(
                    'Payload client_code required for sep_unembossed product type'
                )
        else:
            if item_obj.has_postcontrol and not order_dict.get('receiver_iin'):
                raise OrderReceiverIINNotProvided(
                    'You trying to create order using a product with post_control '
                    "status but don't provide receiver_iin",
                )
        has_preparation = f"graph @? '$.slug[*] ? (@ == \"{StatusSlug.PACKED}\")'"
        deliverygraph = await item_obj.deliverygraph_set.filter(
            types__contains=order.type.value
        ).annotate(has_preparation=RawSQL(has_preparation)).first()
        if not deliverygraph:
            raise IntegrityError(
                f'There is no respective deliverygraph for given type',
            )
        order_dict['callbacks'] = order.callbacks
        dp_id = None
        if city_name:
            dp_repo = DeliveryPointRepository()
            dp_obj = await dp_repo.create(DeliveryPointCreate(
                address=order_dict.pop('address'),
                latitude=order_dict.pop('latitude'),
                longitude=order_dict.pop('longitude'),
            ))
            dp_id = dp_obj.id
        order_created = await Order.create(
            delivery_point_id=dp_id,
            **await get_default_values(order_dict),
            **order_dict,
        )

        # TODO: Сейчас параллельно тут доработки по двум продуктам, ЗП проект и Пос терминалы, + SEP неименные в будущем
        # TODO: Поэтому пока без рефакторинга, чтобы не было конфликтов

        if product_payload:
            if order.product_type == enums.ProductType.GROUP_OF_CARDS:
                await models.Product.create(
                    order_id=order_created.id,
                    type=order.product_type,
                    attributes=product_payload.json(),
                    name=order.product_name,
                )

            if order.product_type == enums.ProductType.CARD:
                pan = Pan(value=product_payload.pan)
                await models.Product.create(
                    order_id=order_created.id,
                    type='card',
                    name=order.product_name,
                    attributes={
                        "pan": pan.get_masked(),
                        "pan_suffix": pan.get_suffix(),
                    },
                    pan_suffix=pan.get_suffix(),
                )

            if order.product_type == enums.ProductType.POS_TERMINAL:
                await models.Product.create(
                    order_id=order_created.id,
                    type='pos_terminal',
                    attributes=product_payload.json()
            )

            if order.product_type == enums.ProductType.SEP_UNEMBOSSED:
                await models.Product.create(
                    order_id=order_created.id,
                    type=enums.ProductType.SEP_UNEMBOSSED.value,
                    attributes=product_payload.json()
                )

        await order_update_status(order_created, OrderStatus.NEW)
        if city_name and not order.type == OrderType.PICKUP:
            address_in_polygon = await check_is_delivery_points_in_polygon(
                order_created,
                partner_dict.get('courier_partner_id')
            )
            if item_obj.distribute is True and not deliverygraph.has_preparation:
                if address_in_polygon:
                    try:
                        await distribute_order_immediately_for_all_couriers(
                            [order_created, ], partner_dict.get('courier_partner_id')
                        )
                    except Exception as e:
                        logger.error(e)

        order_time = await order_created.localtime

        await models.history_create(
            schemas.HistoryCreate(
                initiator_type=InitiatorType.EXTERNAL_SERVICE,
                initiator_id=partner_id,
                model_type=HistoryModelName.ORDER,
                model_id=order_created.id,
                request_method=RequestMethods.POST,
                created_at=order_time,
            )
        )
        return order_created.id

    except IntegrityError as e:
        raise OrderEntitiesError(
            exceptions.get_exception_msg(e),
        ) from e

async def get_external_order(order_id: int) -> schemas.OrderGetV1:
    order_fetched = await Order.get(id=order_id).prefetch_related(
        Prefetch('status_set', OrderStatuses.all().prefetch_related('status'),
                 'statuses'),
        Prefetch('postcontrol_set', models.PostControl.all(), 'postcontrols'),
    ).select_related('area', 'city', 'courier__user', 'item', 'deliverygraph',
                     'partner', 'product')
    result = schemas.OrderGetV1.from_orm(order_fetched)
    await order_fill_old_addresses_field(result)

    return result


# TODO: вместо external_order_create теперь используем external_order_create_v2
# external_order_create сейчас еще где то используется, поэтому пока не удалил
@atomic()
async def external_order_create(
    order: schemas.ExternalOrderCreate,
    **kwargs,
):
    partner_id = kwargs.pop('partner_id', None)
    order_dict = order.dict(exclude_unset=True)
    city_name = order_dict.pop('city', None)
    if city_name:
        try:
            city = await City.get(
                Q(name_en=city_name, name_ru=city_name, name_kk=city_name, name_zh=city_name, join_type=Q.OR),
            )
            order_dict['city_id'] = city.id
        except DoesNotExist:
            raise DoesNotExist(f'City with provided name {city_name} not found')
    partner_dict = await models.partner_get(partner_id)
    order_dict['partner_id'] = partner_dict.get('id')
    order_dict['created_by'] = CreatedType.INTEGRATION

    try:
        item_obj = await models.Item.filter(
            id=order_dict.get('item_id'), partner_id=partner_id
        ).first()
        if not item_obj:
            raise models.ItemNotFound(
                f"Item with provided partner_id: "
                f"{partner_id} and item_id {order_dict.get('item_id')}"
                f", not found"
            )
        if order.product_type != enums.ProductType.SEP_UNEMBOSSED:
            if item_obj.has_postcontrol and not order_dict.get('receiver_iin'):
                raise OrderReceiverIINNotProvided(
                    'You trying to create order using a product with post_control '
                    "status but don't provide receiver_iin",
                )
        has_preparation = f"graph @? '$.slug[*] ? (@ == \"{StatusSlug.PACKED}\")'"
        deliverygraph = await item_obj.deliverygraph_set.filter(
            types__contains=order.type.value
        ).annotate(has_preparation=RawSQL(has_preparation)).first()
        if not deliverygraph:
            raise IntegrityError(
                f'There is no respective deliverygraph for given type',
            )
        order_dict['callbacks'] = order.callbacks
        dp_id = None
        if city_name:
            dp_repo = DeliveryPointRepository()
            dp_obj = await dp_repo.create(DeliveryPointCreate(
                address=order_dict.pop('address'),
                latitude=order_dict.pop('latitude'),
                longitude=order_dict.pop('longitude'),
            ))
            dp_id = dp_obj.id
        order_created = await Order.create(
            delivery_point_id=dp_id,
            **await get_default_values(order_dict),
            **order_dict,
        )

        # TODO: Кажется нужна логика разделения создания заявки от типа продукта
        # Если это карточный продукт и передали pan, то сохраним его
        if order.payload and order.payload.pan:
            pan = Pan(value=order.payload.pan)
            await models.PAN.create(
                order_id=order_created.id,
                pan=pan.value,
                pan_suffix=pan.get_suffix(),
            )

        await order_update_status(order_created, OrderStatus.NEW)
        if city_name and not order.type == OrderType.PICKUP:
            address_in_polygon = await check_is_delivery_points_in_polygon(
                order_created,
                partner_dict.get('courier_partner_id')
            )
            if item_obj.distribute is True and not deliverygraph.has_preparation:
                if address_in_polygon:
                    try:
                        await distribute_order_immediately_for_all_couriers(
                            [order_created, ], partner_dict.get('courier_partner_id')
                        )
                    except Exception as e:
                        logger.error(e)

        order_fetched = await Order.get(id=order_created.id).prefetch_related(
            Prefetch('status_set', OrderStatuses.all().prefetch_related('status'),
                     'statuses'),
            Prefetch('postcontrol_set', models.PostControl.all(), 'postcontrols'),
        ).select_related('area', 'city', 'courier__user', 'item', 'deliverygraph',
                         'partner')
        result = schemas.OrderGet.from_orm(order_fetched)
        await order_fill_old_addresses_field(result)

        order_time = await order_fetched.localtime

        await models.history_create(
            schemas.HistoryCreate(
                initiator_type=InitiatorType.EXTERNAL_SERVICE,
                initiator_id=partner_id,
                model_type=HistoryModelName.ORDER,
                model_id=order_created.id,
                request_method=RequestMethods.POST,
                created_at=order_time,
            )
        )
        return result

    except IntegrityError as e:
        raise OrderEntitiesError(
            exceptions.get_exception_msg(e),
        ) from e


async def order_pan(order_id: int, pan_schema: schemas.OrderPAN, default_filter_args):
    pan = Pan(value=pan_schema.pan)

    # Проверим есть ли уже созданный продукт
    current_product = await models.Product.get_or_none(order_id=order_id)

    # Если есть, то редактируем текущий продукт
    if current_product:
        current_product.attributes['pan'] = pan.value
        current_product.attributes['pan_suffix'] = pan.get_suffix()
        current_product.attributes['input_type'] = pan_schema.input_type
        current_product.pan_suffix = pan.get_suffix()
        await current_product.save()

    # Иначе, создадим новый продукт
    else:
        await models.Product.create(
            order_id=order_id,
            type='card',
            attributes={
                'pan': pan.value,
                'pan_suffix': pan.get_suffix(),
                'input_type': pan_schema.input_type,
            },
            pan_suffix=pan.get_suffix(),
        )

    order_obj = await Order.filter(
        *default_filter_args,
    ).distinct().get(id=order_id).select_related('city', 'deliverygraph')

    next_status_obj = await get_next_status_from_status(order_obj, StatusSlug.SCAN_CARD.value)
    if next_status_obj:
        try:
            async with in_transaction('default'):
                order_obj.current_status = next_status_obj
                await order_obj.save()
                await order_update_status(order_obj, next_status_obj.id)
                if next_status_obj.slug in (StatusSlug.ISSUED, StatusSlug.DELIVERED):
                    await order_set_actual_delivery_datetime(order_obj)
                if next_status_obj.slug == StatusSlug.DELIVERED:
                    order_obj.delivery_status = {
                        'status': OrderDeliveryStatus.IS_DELIVERED.value,
                        'reason': None,
                        'datetime': None,
                        'comment': None,
                    }
                    await order_obj.save()
        except (
            StatusAfterError,
            IntegrityError,
        ):
            pass
    return await order_get_v1(order_id=order_id)


async def order_pan_v2(order_id: int, pan_schema: schemas.OrderPAN, default_filter_args):
    pan = Pan(value=pan_schema.pan)

    # Проверим есть ли уже созданный продукт
    current_product = await models.Product.get_or_none(order_id=order_id)

    # Если есть, то редактируем текущий продукт
    if current_product:
        current_product.attributes['pan'] = pan.value
        current_product.attributes['pan_suffix'] = pan.get_suffix()
        current_product.attributes['input_type'] = pan_schema.input_type
        current_product.pan_suffix = pan.get_suffix()
        await current_product.save()

    # Иначе, создадим новый продукт
    else:
        await models.Product.create(
            order_id=order_id,
            type='card',
            attributes={
                'pan': pan.value,
                'pan_suffix': pan.get_suffix(),
                'input_type': pan_schema.input_type,
            },
            pan_suffix=pan.get_suffix(),
        )

    order_obj = await Order.filter(
        *default_filter_args,
    ).distinct().get(id=order_id).select_related('city', 'deliverygraph')

    next_status_obj = await get_next_status_from_status(order_obj, StatusSlug.SCAN_CARD.value)
    if next_status_obj:
        try:
            async with in_transaction('default'):
                order_obj.current_status = next_status_obj
                await order_obj.save()
                await order_update_status(order_obj, next_status_obj.id)
                if next_status_obj.slug in (StatusSlug.ISSUED, StatusSlug.DELIVERED):
                    await order_set_actual_delivery_datetime(order_obj)
                if next_status_obj.slug == StatusSlug.DELIVERED:
                    order_obj.delivery_status = {
                        'status': OrderDeliveryStatus.IS_DELIVERED.value,
                        'reason': None,
                        'datetime': None,
                        'comment': None,
                    }
                    await order_obj.save()
        except (
            StatusAfterError,
            IntegrityError,
        ):
            pass
    return await order_get_v2(order_id=order_id, profile_type=ProfileType.COURIER)


async def send_new_order_to_courier(order):
    if fcmdevice_ids := await models.FCMDevice.filter(
        user__profile_courier=order.courier_id,
    ).values_list('id', flat=True):
        notification = {
            'title': f'Новая заявка',
            'body': f'На Вас назначена заявка № {order.id}',

        }
        data = {
            'title': f'Новая заявка',
            'description': f'На Вас назначена заявка № {order.id}',
            'id': order.id,
            'type': order.type,
            'push_type': PushType.INFO.value,
        }
        task_kwargs = {
            'registration_ids': fcmdevice_ids,
            'notification': notification,
            'data': data,
        }
        conn = redis_module.get_connection()
        await conn.publish(
            channel='send-to-celery',
            message=json.dumps({
                'task_name': 'firebase-send',
                'kwargs': task_kwargs,
            })
        )


# TODO: кажется этот метод больше не нужен, как и сам ендпоинт вызывающий его
async def check_if_order_can_get_status(
    order_obj: Order,
    status_obj: 'models.Status',
) -> bool:
    graph = order_obj.deliverygraph.graph

    status_not_belong_to_graph = 'This status does not belong to order deliverygraph'
    is_status_exist_in_graph = any(i['slug'] == status_obj.slug for i in graph)
    if not is_status_exist_in_graph:
        raise exceptions.PydanticException(errors=[('status_id', status_not_belong_to_graph)])

    errors = []
    previous_step = 'Can not change to this status, please try previous step again'
    match status_obj.slug:
        case StatusSlug.SMS_SENT:
            if not await order_obj.otp_set.all().exists():
                errors.append(('status_id', previous_step))
        case StatusSlug.SCAN_CARD:
            if not await order_obj.otp_set.filter(accepted_at__isnull=False).exists():
                errors.append(('status_id', previous_step))
        case StatusSlug.PHOTO_CAPTURING:
            if not (await order_obj.product).type == ProductType.CARD.value:
                errors.append(('status_id', previous_step))
        case StatusSlug.POST_CONTROL:
            if not await order_obj.postcontrol_set.all().exists():
                errors.append(('status_id', previous_step))
        case StatusSlug.DELIVERED:
            config_ids = await order_obj.item.postcontrol_config_set.all().values_list('id', flat=True)
            if any(step['slug'] == StatusSlug.POST_CONTROL_BANK for step in graph):
                if await order_obj.postcontrol_set.filter(
                    resolution=PostControlResolution.BANK_ACCEPTED,
                    config_id__in=config_ids,
                ).count() != len(config_ids):
                    errors.append(('status_id', previous_step))
            elif any(step['slug'] == StatusSlug.POST_CONTROL for step in graph):
                if await order_obj.postcontrol_set.filter(
                    resolution__in=[PostControlResolution.ACCEPTED.value, PostControlResolution.BANK_ACCEPTED],
                    config_id__in=config_ids,
                ).count() != len(config_ids):
                    errors.append(('status_id', previous_step))
        case StatusSlug.ISSUED:
            if any(item['slug'] == StatusSlug.POST_CONTROL for item in graph) and (
                not await order_obj.postcontrol_set.all().exists() or
                await order_obj.postcontrol_set.filter(
                    resolution__in=[PostControlResolution.PENDING.value, PostControlResolution.DECLINED.value],
                ).exists()
            ):
                errors.append(('status_id', previous_step))
    if errors:
        raise exceptions.PydanticException(errors=errors)

    return True


@atomic()
async def order_change_status(default_filter_args, body):
    try:
        status_obj = await models.Status.get(id=body.status_id)
    except DoesNotExist:
        raise DoesNotExist('Status with given ID not found')

    order_statuses = []
    order_ids = []
    for order_id in body.order_id_list:
        try:
            order_obj = await Order.annotate(
                has_ready_for_shipment=RawSQL(
                    f"order__deliverygraph.graph @? '$.slug[*] ? (@ == \"{StatusSlug.READY_FOR_SHIPMENT}\")'"
                ),
            ).filter(
                *default_filter_args,
                deliverygraph__id__isnull=False,  # needed to join deliverygraph table only.
            ).get(id=order_id).select_related('city', 'deliverygraph')
            await check_if_order_can_get_status(order_obj, status_obj)
            order_ids.append(order_id)
        except DoesNotExist:
            raise DoesNotExist(f'Order with given ID: {order_id} was not found')
        order_time = await order_obj.localtime
        order_statuses.append(
            OrderStatuses(order=order_obj, status=status_obj, created_at=order_time)
        )
    await OrderStatuses.bulk_create(order_statuses, 100)
    await Order.filter(id__in=order_ids).update(current_status_id=body.status_id)


@signals.post_save(OrderStatuses)
async def order_update_delivery_status_on_status_change(
    sender: 'Type[OrderStatuses]',
    instance: OrderStatuses,
    created: bool,
    using_db: 'Optional[BaseDBAsyncClient]',
    update_fields: List[str],
):
    order: Order = await instance.order

    if str(instance.status_id) in [
        OrderStatus.DELIVERED.value, OrderStatus.ISSUED.value
    ] and created:
        order.delivery_status = {
            'status': OrderDeliveryStatus.IS_DELIVERED.value,
            'reason': None,
            'datetime': None,
            'comment': None,
        }
        await order.save(update_fields=['delivery_status'])

        try:
            order_chain_actions = ModulesActionsDiContainer().order_chain

            await order_chain_actions.set_order_chain_done(
                order=order,
            )
        except Exception as e:
            logger.info(e)

    if str(instance.status_id) in [
        OrderStatus.ACCEPTED_BY_COURIER.value
    ] and created:
        try:
            order_chain_actions = ModulesActionsDiContainer().order_chain

            await order_chain_actions.set_order_chain_in_progress(
                order=order,
            )
        except Exception as e:
            logger.info(e)

    try:
        status = await instance.status
        await websocket_manager.send_message_for_managers(
            order.partner_id, {
                'type': MessageType.ORDER_STATUS_UPDATE,
                'data': {
                    'order_id': order.id,
                    'name': status.name,
                    'slug': status.slug,
                }
            })
    except Exception as e:
        logger.info(e)


@signals.post_save(OrderStatuses)
async def order_send_notification_to_client_on_currier_assign(
    sender: 'Type[OrderStatuses]',
    instance: OrderStatuses,
    created: bool,
    using_db: 'Optional[BaseDBAsyncClient]',
    update_fields: List[str],
):
    if not created:
        return
    if instance.status_id != int(OrderStatus.COURIER_ASSIGNED):
        return
    order = await instance.order
    item = await order.item
    if item.courier_appointed_sms_on:
        await send_courier_assigned_notification(
            phone=order.receiver_phone_number,
            message=item.courier_appointed_sms,
            receiver_full_name=order.receiver_name,
            related_order_id=order.id
        )


async def order_set_actual_delivery_datetime(
    order_obj: Order,
):
    if order_obj.actual_delivery_datetime is not None:
        return
    order_time = await order_obj.localtime
    order_obj.actual_delivery_datetime = order_time
    await order_obj.save()
    return


async def order_set_actual_delivery_datetime_bulk(
    *order_ids,
):
    for order_obj in await Order.filter(
        id__in=order_ids,
        actual_delivery_datetime__isnull=True,
    ).select_related('city'):
        order_time = await order_obj.localtime
        order_obj.actual_delivery_datetime = order_time
        await order_obj.save()

