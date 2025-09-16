import io
import uuid
from pathlib import Path
from typing import List, Union

import pdfkit
import xlsxwriter
from fastapi_pagination.bases import AbstractPage
from num2words import num2words
from tortoise.expressions import Q
from tortoise.transactions import atomic

from .enums import OrderGroupStatuses
from .infrastructure.repository import OrderGroupRepository
from .schemas import (
    OrderGroupGet,
    OrderGroupCreateSchema,
    OrderGroupUpdate,
    OrdersIn,
    OrderGroupCreate
)
from ..partner_settings.actions import PartnerSettingActions
from ... import models
from ...common.action_base import BaseAction
from ...conf import conf
from ...enums import InitiatorType, RequestMethods, HistoryModelName, StatusSlug, \
    OrderDeliveryStatus, AddressType
from ...models import history_create
from ...models.order import order_status_bulk_rollback
from ...models.status import status_get_by_slug
from ...schemas import HistoryCreate


class OrderGroupActions(BaseAction):
    def __init__(self, current_user=None):
        self.user = current_user
        self.repo = OrderGroupRepository()
        self.partner_settings = PartnerSettingActions()

    async def create(
        self, order_group: OrderGroupCreateSchema,
    ) -> None:
        profile = self.user.profile['profile_content']
        partner_settings = await self.partner_settings.partner_setting_get(
            partner_id=profile['courier_partner_id'],
        )
        delivery_point_id = (
                partner_settings.default_delivery_point_for_order_group.id
                if partner_settings.default_delivery_point_for_order_group else None
            )

        create_data = OrderGroupCreate(
            sorter_id=self.user.profile['id'],
            partner_id=profile['partner_id'],
            shipment_point_id=profile['shipment_point_id'],
            delivery_point_id=delivery_point_id,
        )

        order_group_fetched = await self.repo.create(create_data)

        await self.change_status(
            order_group_id=order_group_fetched.id,
            status=OrderGroupStatuses.NEW_GROUP,
            default_filter_args=[]
        )

        if order_group.orders:
            await self.order_add(
                default_filter_args=None, order_group_id=order_group_fetched.id,
                orders=order_group
            )
        order_g_time = await order_group_fetched.shipment_localtime

        await history_create(
            HistoryCreate(
                initiator_type=InitiatorType.USER,
                initiator_id=self.user.id,
                initiator_role=self.user.profile['profile_type'],
                model_type=HistoryModelName.ORDER_GROUP,
                model_id=order_group_fetched.id,
                request_method=RequestMethods.POST,
                action_data=create_data.dict(),
                created_at=order_g_time,
            )
        )

    async def update(
        self,
        order_group_id: int,
        update: OrderGroupUpdate,
        default_filter_args,
    ) -> None:
        # place for business logic
        order_group_fetched = await self.repo.partial_update(
            entity_id=order_group_id, update_schema=update,
            default_filter_args=default_filter_args
        )

        order_g_time = await order_group_fetched.shipment_localtime

        await history_create(
            HistoryCreate(
                initiator_type=InitiatorType.USER,
                initiator_id=self.user.id,
                initiator_role=self.user.profile['profile_type'],
                model_type=HistoryModelName.ORDER_GROUP,
                model_id=order_group_fetched.id,
                request_method=RequestMethods.PATCH,
                action_data=update.dict(),
                created_at=order_g_time,
            )
        )

    async def get(
        self,
        default_filter_args,
        order_group_id: int,
    ) -> Union[OrderGroupGet, dict]:
        # place for business logic
        return await self.repo.get_by_id(
            default_filter_args=default_filter_args, entity_id=order_group_id
        )

    async def get_list(
        self, pagination_params, default_filter_args, filter_kwargs
    ) -> AbstractPage[OrderGroupGet] | List[OrderGroupGet]:
        dict_kwargs = filter_kwargs.dict()
        id_filter_param = dict_kwargs.pop('id', None)
        if id_filter_param:
            dict_kwargs['id__startswith'] = id_filter_param
        return await self.repo.get_list(
            pagination_params=pagination_params, default_filter_args=default_filter_args,
            **dict_kwargs
        )

    @atomic()
    async def order_add(
        self, default_filter_args, order_group_id, orders: OrdersIn
    ):
        o_group_status = await self.repo.get_status(entity_id=order_group_id)
        await self.repo.add_orders(
            default_filter_args=default_filter_args, entity_id=order_group_id, orders=orders
        )
        status = await status_get_by_slug(slug=StatusSlug.ACCEPT_IN_GROUP.value)
        if status:
            await models.order_status_bulk_update(order_ids=orders.orders, status_id=status.id)
        if o_group_status.name == OrderGroupStatuses.READY_FOR_PICKUP:
            status = await status_get_by_slug(slug=StatusSlug.READY_FOR_SHIPMENT.value)
            await models.order_status_bulk_update(order_ids=orders.orders, status_id=status.id)

    @atomic()
    async def order_remove(
        self, default_filter_args, order_group_id, orders: OrdersIn
    ):
        o_group_status = await self.repo.get_status(entity_id=order_group_id)
        await self.repo.remove_orders(
            default_filter_args=default_filter_args, entity_id=order_group_id, orders=orders
        )
        packed_status = await status_get_by_slug(slug=StatusSlug.PACKED.value)
        added_to_group = await status_get_by_slug(slug=StatusSlug.ACCEPT_IN_GROUP.value)
        ready_for_shipment = await status_get_by_slug(slug=StatusSlug.READY_FOR_SHIPMENT.value)
        if added_to_group:
            await order_status_bulk_rollback(
                order_ids=orders.orders, status_id=added_to_group.id, include=True
            )
        if o_group_status.name == OrderGroupStatuses.READY_FOR_PICKUP:
            if ready_for_shipment:
                await order_status_bulk_rollback(
                    order_ids=orders.orders, status_id=ready_for_shipment.id, include=True
                )
        await models.order_status_bulk_update(order_ids=orders.orders, status_id=packed_status.id)

    async def list_orders(
        self,
        pagination_params,
        default_filter_args,
        order_group_id,
        **kwargs,
    ):
        return await self.repo.list_orders(
            pagination_params=pagination_params,
            default_filter_args=default_filter_args,
            entity_id=order_group_id,
            **kwargs,
        )

    @atomic()
    async def change_status(
        self, order_group_id, status: str, default_filter_args
    ):
        profile = self.user.profile['profile_content']
        order_group = await self.repo.change_status(
            entity_id=order_group_id,
            order_group_status=status,
            default_filter_args=default_filter_args,
        )

        if status == OrderGroupStatuses.READY_FOR_PICKUP.value:
            await self.ready_for_pickup_action(order_group, default_filter_args, profile)
        if status == OrderGroupStatuses.REVISE.value:
            await self.revise_action(order_group, default_filter_args)
        if status == OrderGroupStatuses.EXPORTED.value:
            await self.exported_action(order_group)
        if status == OrderGroupStatuses.COURIER_SERVICE_ACCEPTED.value:
            await self.courier_service_accepted_action(order_group, default_filter_args, profile)
        if status == OrderGroupStatuses.UNDER_REVIEW.value:
            await self.under_review_action(order_group)

    @atomic()
    async def ready_for_pickup_action(
        self,
        order_group,
        default_filter_args,
        profile,
    ):
        if st := await status_get_by_slug(slug=StatusSlug.READY_FOR_SHIPMENT.value):
            await self.change_status_in_order_bulk(st, order_group)

        partner_settings = await self.partner_settings.partner_setting_get(
            partner_id=profile['courier_partner_id'],
        )
        shipment_point_id = profile['shipment_point_id']
        if partner_settings.default_order_group_couriers and not order_group.courier_id:
            default_courier_id = partner_settings.default_order_group_couriers.get(
                        str(shipment_point_id)
                    )
            await self.update(
                default_filter_args=default_filter_args,
                order_group_id=order_group.id,
                update=OrderGroupUpdate(courier_id=default_courier_id),
            )
        await self.change_delivery_status_in_order_group_orders(
            order_group=order_group, delivery_status=None
        )

    @atomic()
    async def revise_action(self, order_group, default_filter_args):
        order_status = await status_get_by_slug(slug=StatusSlug.AT_REVISE.value)
        await self.order_group_act(default_filter_args, order_group.id)
        await self.set_revise_state_in_orders(order_group, revise=False)
        await self.change_delivery_status_in_order_group_orders(
            order_group=order_group, delivery_status=None
        )
        if order_status:
            await self.change_status_in_order_bulk(order_status, order_group)

    @atomic()
    async def exported_action(self, order_group):
        order_status = await status_get_by_slug(slug=StatusSlug.TAKEN_OUT_BY_COURIER.value)
        if order_status:
            await self.change_status_in_order_bulk(order_status, order_group)

    @atomic()
    async def courier_service_accepted_action(self, order_group, default_filter_args, profile):
        order_status = await status_get_by_slug(
            slug=StatusSlug.ACCEPTED_BY_COURIER_SERVICE.value
        )

        partner_settings = await self.partner_settings.partner_setting_get(
            partner_id=profile['partner_id'],
        )

        partner_order_group_item = partner_settings.auto_item_for_order_group

        await self.repo.partial_update(
            entity_id=order_group.id,
            update_schema=OrderGroupUpdate(
                courier_service_manager_id=self.user.profile['id'],
            ),
            default_filter_args=default_filter_args,
        )

        if order_status:
            await self.change_status_in_order_bulk(order_status, order_group)

        if partner_order_group_item and partner_order_group_item.distribute:
            await self.order_distribute_selective_with_status_change(
                order_group=order_group
            )

    @atomic()
    async def under_review_action(self, order_group):
        if st := await status_get_by_slug(slug=StatusSlug.READY_FOR_SHIPMENT.value):
            await self.change_status_in_order_bulk(st, order_group)
            orders = await order_group.orders
            order_ids = [order.id for order in orders]

            await order_status_bulk_rollback(order_ids, st.id, include=False)
        await self.change_delivery_status_in_order_group_orders(
            order_group=order_group, delivery_status=OrderDeliveryStatus.UNDER_REVIEW
        )

    async def order_distribute_selective_with_status_change(
        self,
        order_group,
    ):
        order_status = await status_get_by_slug(
            slug=StatusSlug.COURIER_ASSIGNED.value
        )
        orders = await order_group.orders
        order_ids = [order.id for order in orders]
        await models.order_distribution_selective(
            selective_order_ids=order_ids, current_user=self.user
        )
        orders_with_couriers_id = []
        for order in orders:
            await order.refresh_from_db(fields=['courier_id'])
            if order.courier_id:
                orders_with_couriers_id.append(order.id)
        await models.order_status_bulk_update(order_ids=orders_with_couriers_id,
                                              status_id=order_status.id)

    async def set_revise_state_in_orders(self, order_group, revise=False):
        order_ids = [item.id for item in await order_group.orders]
        orders = await models.Order.filter(id__in=order_ids).select_related('city')
        for order in orders:
            updated_data = {
                'revised': False
            }
            await order.update_from_dict(updated_data).save()

            order_time = await order.localtime
            await models.history_create(
                HistoryCreate(
                    initiator_type=InitiatorType.USER,
                    initiator_id=self.user.id,
                    initiator_role=self.user.profile['profile_type'],
                    model_type=HistoryModelName.ORDER,
                    model_id=order.id,
                    request_method=RequestMethods.PATCH,
                    action_data=updated_data,
                    created_at=order_time,
                )
            )

    @staticmethod
    async def change_status_in_order_bulk(order_status, order_group):
        orders = await order_group.orders
        order_ids = [order.id for order in orders]
        await models.order_status_bulk_update(order_ids=order_ids,
                                              status_id=order_status.id)

    async def change_delivery_status_in_order_group_orders(
        self,
        order_group, delivery_status: OrderDeliveryStatus | None
    ):
        order_ids = [item.id for item in await order_group.orders]
        orders = await models.Order.filter(id__in=order_ids).select_related('city')
        for order in orders:
            new_delivery_status = {
                'status': delivery_status.value if delivery_status else None,
                'reason': None,
                'datetime': None,
                'comment': None,
            }
            order_time = await order.localtime
            order.delivery_status = new_delivery_status
            await order.save()
            await models.history_create(
                HistoryCreate(
                    initiator_type=InitiatorType.USER,
                    initiator_id=self.user.id,
                    initiator_role=self.user.profile['profile_type'],
                    model_type=HistoryModelName.ORDER,
                    model_id=order.id,
                    request_method=RequestMethods.PATCH,
                    action_data={'delivery_status': delivery_status},
                    created_at=order_time,
                )
            )

    async def order_group_act(self, default_filter_args, order_group_id):
        entity = await self.repo.get_for_act(default_filter_args, entity_id=order_group_id)

        orders = await entity.orders.all().select_related(
            'city', 'item', 'partner', 'delivery_point',
        ).order_by('id')
        row_template = """
            <tr>
            <td>{no}</td>
            <td>{id}</td>
            <td>{fullname}</td>
            <td>{city}</td>
            <td>{address}</td>
            <td>{phone}</td>
            <td>{product}</td>
        </tr>"""
        order_list = ''
        for no, order in enumerate(orders, 1):
            order_list += row_template.format(
                no=no,
                id=f'{order.partner.article}-{order.id}',
                fullname=order.receiver_name,
                city=order.city.name,
                address=order.delivery_point.address,
                phone=order.receiver_phone_number,
                product=order.item.name,
            )
        template_path = conf.static.root / 'act_template.html'
        css_path = conf.static.root / 'act_template.css'

        with open(template_path, 'r') as template:
            html_text = template.read()
            sorter = '____________________________'
            if entity.sorter:
                sorter = entity.sorter.user.fullname
            courier = '____________________________'
            if entity.courier:
                courier = entity.courier.user.fullname
            order_count = len(orders)
            order_count_words = num2words(order_count, lang='ru')
            generated = html_text.format(
                order_list=order_list,
                sorter=sorter,
                courier=courier,
                city=entity.shipment_point.city.name,
                order_count=f'{order_count} "{order_count_words}"',

            )
            file_path = Path(entity._meta.fields_map['act'].upload_to) / f'{uuid.uuid4()}.pdf'
            full_path = conf.media.root / file_path
            pdf_file = pdfkit.from_string(generated, css=css_path)
            with open(full_path, 'wb') as act_file:
                act_file.write(pdf_file)
            await self.repo.set_act(entity, str(file_path))
            return pdf_file

    async def order_group_report(self, default_filters: list, filters: dict):
        report = await self.repo.get_report(default_filters=default_filters, filters=filters)
        buffer = io.BytesIO()
        with xlsxwriter.Workbook(buffer, options={'remove_timezone': True}) as workbook:
            sheet = workbook.add_worksheet()
            datetime_format = workbook.add_format(
                {'num_format': 'dd-mm-yyyy hh:mm:ss', }
            )
            main_format = workbook.add_format(
                {'font_color': 'black'}
            )

            field_names = {
                'id': {
                    'name': 'ID',
                    'num': 0,
                    'format': main_format,
                },
                'created_at': {
                    'name': 'Дата создания',
                    'num': 1,
                    'format': datetime_format,
                },
                'order_count': {
                    'name': 'Количество заявок',
                    'num': 2,
                    'format': main_format,
                },
                'partner_name': {
                    'name': 'Партнер',
                    'num': 3,
                    'format': main_format,
                },
                'shipment_point_name': {
                    'name': 'Точка вывоза',
                    'num': 4,
                    'format': main_format,
                },
                'delivery_point_name': {
                    'name': 'Адрес доставки',
                    'num': 5,
                    'format': main_format,
                },
                'service_manager_name': {
                    'name': 'Менеджер',
                    'num': 6,
                    'format': main_format,
                },
                'courier_name': {
                    'name': 'Курьер',
                    'num': 7,
                    'format': main_format,
                },
                'sorter_name': {
                    'name': 'Сортировщик',
                    'num': 8,
                    'format': main_format,
                },
                'status_value': {
                    'name': 'Статус',
                    'num': 9,
                    'format': main_format,
                },
                'ready_for_pickup': {
                    'name': 'Готово к вывозу',
                    'num': 10,
                    'format': datetime_format,
                },
                'revise': {
                    'name': 'Сверка',
                    'num': 11,
                    'format': datetime_format,
                },
                'exported': {
                    'name': 'Вывезено',
                    'num': 12,
                    'format': datetime_format,
                },
                'courier_service_accepted': {
                    'name': 'Принято куьерской службой',
                    'num': 13,
                    'format': datetime_format,
                },
            }

            for col_num, field in enumerate(field_names.values()):
                cell_format = workbook.add_format(
                    {
                        'bold': True,
                        'font_color': 'white',
                        'bg_color': 'green',
                        'align': 'left',
                    }
                )
                sheet.write(0, col_num, field['name'])
                sheet.set_column(col_num, col_num, 10, cell_format)

                for row_number, row in enumerate(report, 1):
                    for cell_name, cell_value in row.items():
                        sheet.write(
                            row_number,
                            field_names[cell_name]['num'],
                            cell_value,
                            field_names[cell_name]['format']
                        )
            workbook.read_only_recommended()
        buffer.seek(0)
        return buffer
