import json
from datetime import datetime
from typing import Optional, Iterable

from tortoise import fields, BaseDBAsyncClient
from tortoise.models import Model
from tortoise.timezone import now

from ...shipment_point.infrastructure.db_table import PartnerShipmentPoint
from .... import redis_module
from .... import models
from ....enums import PushType
from ....models import fields as custom_fields
from ....models import mixins


async def send_new_order_group_to_courier(order_group):
    if fcmdevice_ids := await models.FCMDevice.filter(
        user__profile_courier=order_group.courier_id,
    ).values_list('id', flat=True):
        notification = {
            'title': f'Новая группа заявок',
            'body': f'На Вас назначена группа заявок № {order_group.id}',
        }
        data = {
            'title': f'Новая группа заявок',
            'description': f'На Вас назначена группа заявок № {order_group.id}',
            'id': order_group.id,
            'type': 'order_group',
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


class OrderGroup(mixins.DeleteFilesMixin, Model):
    id = fields.IntField(pk=True)
    partner = fields.ForeignKeyField(
        'versions.Partner',
        to_field='id',
        on_delete=fields.CASCADE,
        null=False,
        related_name='order_groups',
    )
    shipment_point = fields.ForeignKeyField(
        'versions.PartnerShipmentPoint',
        to_field='id',
        on_delete=fields.SET_NULL,
        null=True,
        related_name='order_groups_sp'
    )
    delivery_point = fields.ForeignKeyField(
        'versions.PartnerShipmentPoint',
        to_field='id',
        on_delete=fields.SET_NULL,
        null=True,
        related_name='order_groups_dp'
    )
    sorter = fields.ForeignKeyField(
        'versions.ProfileSorter',
        to_field='id',
        on_delete=fields.SET_NULL,
        null=True
    )
    courier = fields.ForeignKeyField(
        'versions.ProfileCourier',
        to_field='id',
        on_delete=fields.SET_NULL,
        null=True
    )
    courier_service_manager = fields.ForeignKeyField(
        'versions.ProfileServiceManager',
        to_field='id',
        on_delete=fields.SET_NULL,
        null=True
    )
    act = custom_fields.FileField(
        upload_to='order-groups/acts',
        null=True,
    )
    updated_at = fields.DatetimeField(auto_now=True)
    created_at = fields.DatetimeField(auto_now_add=True)
    accepted_by_courier_at = fields.DatetimeField(null=True)
    accepted_by_manager_at = fields.DatetimeField(null=True)

    # type hints
    id: int
    partner_id: int
    shipment_point_id: int
    delivery_point_id: int
    sorter_id: int
    courier_id: int
    courier_service_manager_id: int
    orders: fields.ReverseRelation['models.Order']

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

        We override this method to achieve old and new state of the object, hence send respective notifications
        on model change.
        """
        save_coro = super().save(using_db, update_fields, force_create, force_update)
        old_obj = await self.__class__.get_or_none(id=self.id)
        order_g_time = await self.shipment_localtime

        self.updated_at = order_g_time

        if old_obj:
            if self.courier_id != old_obj.courier_id:
                self.accepted_by_courier_at = order_g_time

            if self.courier_service_manager_id != old_obj.courier_service_manager_id:
                self.accepted_by_manager_at = order_g_time

            await save_coro
            if self.courier_id and self.courier_id != old_obj.courier_id:
                await send_new_order_group_to_courier(self)
        else:
            self.created_at = order_g_time
            await save_coro

    class Meta:
        table = 'order_group'

    @property
    async def shipment_localtime(self) -> datetime:
        if not isinstance(self.shipment_point, PartnerShipmentPoint):
            await self.fetch_related('shipment_point')
        if self.shipment_point is None:
            return now()
        return await self.shipment_point.localtime

    @property
    async def delivery_localtime(self) -> datetime:
        if not isinstance(self.delivery_point, PartnerShipmentPoint):
            await self.fetch_related('delivery_point')
        if self.delivery_point is None:
            return now()
        return await self.delivery_point.localtime


class OrderGroupStatus(Model):
    id = fields.IntField(pk=True)
    name = fields.CharField(max_length=255)
    created_at = fields.DatetimeField(auto_now_add=True)
    order_group = fields.ForeignKeyField(
        'versions.OrderGroup',
        to_field='id',
        on_delete=fields.CASCADE,
        null=True,
        related_name='statuses'
    )

    class Meta:
        table = 'order_group_statuses'
        ordering = ("-created_at", )


__all__ = (
    'OrderGroup',
    'OrderGroupStatus',
)
