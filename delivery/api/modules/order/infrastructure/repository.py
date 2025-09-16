from typing import Type, List, Any, Dict

from fastapi.encoders import jsonable_encoder
from fastapi_pagination.bases import AbstractPage
from fastapi_pagination.ext.tortoise import paginate
from tortoise.exceptions import DoesNotExist, IntegrityError
from tortoise.expressions import Subquery, RawSQL
from tortoise.query_utils import Prefetch
from tortoise.transactions import atomic

from api import models
from api.common.repository_base import BaseRepository, TABLE, SCHEMA, IN_SCHEMA
from .db_table import OrderGroup, OrderGroupStatus
from ..errors import OrderGroupIntegrityError, OrderGroupNotFoundError
from ..schemas import OrderGroupGet
from ..schemas import OrdersIn


class OrderGroupRepository(BaseRepository):
    __current_status_sql = """
        (SELECT "name"
        FROM "order_group_statuses"
        WHERE "order_group_id" = "order_group"."id"
        ORDER BY "created_at" DESC
        LIMIT 1)
    """

    @property
    def _schema(self) -> Type[SCHEMA]:
        return OrderGroupGet

    @property
    def _table(self) -> Type[TABLE]:
        return OrderGroup

    @property
    def _not_found_error(self) -> Type[OrderGroupNotFoundError]:
        return OrderGroupNotFoundError

    @property
    def _integrity_error(self) -> Type[OrderGroupIntegrityError]:
        return OrderGroupIntegrityError

    async def create(self, in_schema: IN_SCHEMA) -> TABLE:
        try:
            dict_object = jsonable_encoder(in_schema)
            orders = dict_object.pop('orders', None)
            order_group = await self._table.create(**dict_object)
            if orders:
                fetched_orders = await models.Order.filter(id__in=orders)
                for order in fetched_orders:
                    order.order_group_id = order_group.id
                    await models.Order.bulk_update(fetched_orders, fields=('order_group_id',))
            return order_group
        except IntegrityError as e:
            raise self._integrity_error(
                table=self._table.Meta.table,
                detail=str(e)
            )

    async def get_by_id(self, default_filter_args, entity_id) -> SCHEMA:
        try:
            entity = await self._table.annotate(
                current_status=RawSQL(self.__current_status_sql),
            ).filter(*default_filter_args).get(
                id=entity_id
            ).annotate(
                count=Subquery(
                    models.Order.filter(
                        order_group_id=RawSQL('"order_group"."id"')
                    ).count()
                )).select_related(
                'partner', 'sorter__user', 'courier__user',
                'courier_service_manager__user',
                'shipment_point__partner',
                'delivery_point__partner',
                'shipment_point__city__country',
                'delivery_point__city__country'
            ).prefetch_related('statuses')
        except DoesNotExist:
            raise self._not_found_error(
                table=self._table.Meta.table,
                detail=f'{self._table.Meta.table} with given ID: {entity_id} was not found'
            )
        return self._schema.from_orm(entity)

    async def get_list(
        self, default_filter_args, pagination_params=None, **filter_kwargs
    ) -> AbstractPage[OrderGroupGet] | List[OrderGroupGet]:
        qs = self._table.annotate(
            count=Subquery(
                models.Order.filter(
                    order_group_id=RawSQL('"order_group"."id"')
                ).count()
            ),
            current_status=RawSQL(self.__current_status_sql),
        ).filter(
            *default_filter_args,
        ).filter(
            **filter_kwargs,
        ).select_related(
            'partner', 'sorter__user', 'courier__user',
            'courier_service_manager__user',
            'shipment_point__partner',
            'delivery_point__partner',
            'shipment_point__city__country',
            'delivery_point__city__country'
        ).prefetch_related('statuses').order_by('-id')
        if pagination_params:
            return await paginate(query=qs, params=pagination_params)
        return [self._schema.from_orm(item) for item in await qs]

    async def add_orders(
        self,
        orders: OrdersIn,
        entity_id: int,
        default_filter_args=None,  # noqa,pylint: disable=unused-argument
    ):
        try:
            fetched_orders = await models.Order.filter(id__in=orders.orders)
            if fetched_orders:
                for order in fetched_orders:
                    await order.update_from_dict({'order_group_id': entity_id}).save()

        except DoesNotExist:
            raise self._not_found_error(
                table=self._table.Meta.table,
                detail=f'{self._table.Meta.table} with given ID: {entity_id} was not found'
            )

    async def list_orders(
        self,
        pagination_params,
        default_filter_args,
        entity_id,
        **kwargs,
    ):
        order_group_obj = await self._table.annotate(
                current_status=RawSQL(self.__current_status_sql),
            ).filter(
            *default_filter_args,
            id=entity_id,
        ).first()
        if not order_group_obj:
            return paginate(models.Order.filter(id=-1), pagination_params)
        order_list = order_group_obj.orders.filter().annotate(
            item_name=RawSQL(
                '(select "item"."name" "item_name" from "item" where "id"="order"."item_id")'
            ),
        ).prefetch_related(
            Prefetch('partner', models.Partner.all().only(
                'id',
                'name_en',
                'name_ru',
                'name_kk',
                'name_zh',
                'article',
            ))
        ).only('id', 'receiver_name', 'receiver_phone_number', 'revised', 'partner_id')
        return await paginate(order_list, pagination_params)

    async def remove_orders(
        self,
        default_filter_args, orders: OrdersIn, entity_id: int
    ):
        try:
            await self._table.filter(*default_filter_args).get(
                id=entity_id
            )
            if orders:
                fetched_orders = await models.Order.filter(id__in=orders.orders)
                for order in fetched_orders:
                    await order.update_from_dict({'order_group_id': None}).save()
        except DoesNotExist:
            raise self._not_found_error(
                table=self._table.Meta.table,
                detail=f'{self._table.Meta.table} with given ID: {entity_id} was not found'
            )

    @atomic()
    async def change_status(
        self,
        order_group_status: str, entity_id: int, default_filter_args,
    ):
        try:
            order_group = await self._table.annotate(
                current_status=RawSQL(self.__current_status_sql),
            ).filter(*default_filter_args).get(
                id=entity_id
            ).prefetch_related('orders').select_related('delivery_point__city')
            order_g_time = await order_group.shipment_localtime
            await OrderGroupStatus.create(
                name=str(order_group_status),
                order_group=order_group,
                created_at=order_g_time,
            )
            return order_group
        except DoesNotExist:
            raise self._not_found_error(
                table=self._table.Meta.table,
                detail=f'{self._table.Meta.table} with given ID: {entity_id} was not found'
            )

    @staticmethod
    async def get_status(entity_id: int):
        return await OrderGroupStatus.filter(order_group_id=entity_id).first()

    async def get_for_act(self, default_filter_args, entity_id):
        try:
            entity = await self._table.annotate(
                current_status=RawSQL(self.__current_status_sql),
            ).filter(*default_filter_args).get(id=entity_id).select_related(
                'sorter__user',
                'courier__user',
                'shipment_point__city'
            )
        except DoesNotExist:
            raise self._not_found_error(
                table=self._table.Meta.table,
                detail=f'{self._table.Meta.table} with given ID: {entity_id} was not found',
            )
        return entity

    @staticmethod
    async def set_act(entity, path_to_file: str):
        entity.act = path_to_file
        await entity.save()

    async def get_report(self, default_filters: list, filters: dict) -> List[Dict[str, Any]]:
        order_count_subquery = RawSQL("""
            (SELECT COUNT(ID)
            FROM "order"
            WHERE order_group_id="order_group"."id")
        """)
        partner_subquery = RawSQL("""
            (SELECT "name_ru" "name_ru"
            FROM "partner"
            WHERE "id" = "order_group"."partner_id")
        """)
        shipment_point_subquery = RawSQL("""
            (SELECT "name" "name"
            FROM "partner_shipment_point"
            WHERE "id" = "order_group"."shipment_point_id")
        """)
        delivery_point_subquery = RawSQL("""
            (SELECT "name" "name"
            FROM "partner_shipment_point"
            WHERE "id" = "order_group"."delivery_point_id")
        """)
        service_manager_subquery = RawSQL("""
            (SELECT last_name || ' ' || first_name || ' ' || middle_name "full_name"
            FROM "user"
            WHERE "id" = (SELECT "id" "id"
                          FROM "profile_service_manager"
                          WHERE "id" = "order_group"."courier_service_manager_id"))
        """)
        courier_subquery = RawSQL("""
            (SELECT last_name || ' ' || first_name || ' ' || middle_name "full_name"
            FROM "user"
            WHERE "id" = (SELECT "id" "id"
                          FROM "profile_courier"
                          WHERE "id" = "order_group"."courier_id"))
        """)
        sorter_subquery = RawSQL("""
            (SELECT last_name || ' ' || first_name || ' ' || middle_name "full_name"
            FROM "user"
            WHERE "id" = (SELECT "id" "id"
                          FROM "profile_sorter"
                          WHERE "id" = "order_group"."sorter_id"))
        """)
        status_subquery = RawSQL("""
        (SELECT name FROM "order_group_statuses"
        WHERE "order_group_id"="order_group"."id" ORDER BY created_at DESC LIMIT 1)
        """)
        status_value_subquery = RawSQL("""
            (select case
                       when name = 'new_group' then
                           'Новая группа'
                       when name = 'ready_for_pickup' then
                           'Готово к вывозу'
                       when name = 'courier_appointed' then 'Курьер назначен'
                       when name = 'revise' then 'Сверка'
                       when name = 'exported' then 'Вывезено'
                       when name = 'under_revision' then 'На пересмотре'
                       when name = 'courier_service_accepted' then 'Принято курьерской службой'
                       else name
                       end
            from "order_group_statuses"
            where order_group_id = "order_group"."id"
            order by created_at desc
            limit 1)
        """)
        ready_for_pickup_subquery = RawSQL("""
            (SELECT "created_at" "created_at"
            FROM "order_group_statuses"
            WHERE "order_group_id" = "order_group"."id"
              AND "name" = 'ready_for_pickup'
            ORDER BY "created_at" DESC
            LIMIT 1)
        """)
        revise_subquery = RawSQL("""
            (SELECT "created_at" "created_at"
            FROM "order_group_statuses"
            WHERE "order_group_id" = "order_group"."id"
              AND "name" = 'revise'
            ORDER BY "created_at" DESC
            LIMIT 1)
        """)
        exported_subquery = RawSQL("""
            (SELECT "created_at" "created_at"
            FROM "order_group_statuses"
            WHERE "order_group_id" = "order_group"."id"
              AND "name" = 'exported'
            ORDER BY "created_at" DESC
            LIMIT 1)
        """)
        courier_service_accepted_subquery = RawSQL("""
            (SELECT "created_at" "created_at"
            FROM "order_group_statuses"
            WHERE "order_group_id" = "order_group"."id"
              AND "name" = 'courier_service_accepted'
            ORDER BY "created_at" DESC
            LIMIT 1)
        """)

        report_qs = OrderGroup.annotate(
            order_count=order_count_subquery,
            partner_name=partner_subquery,
            shipment_point_name=shipment_point_subquery,
            delivery_point_name=delivery_point_subquery,
            service_manager_name=service_manager_subquery,
            courier_name=courier_subquery,
            sorter_name=sorter_subquery,
            status=status_subquery,
            status_value=status_value_subquery,
            ready_for_pickup=ready_for_pickup_subquery,
            revise=revise_subquery,
            exported=exported_subquery,
            courier_service_accepted=courier_service_accepted_subquery,
        ).filter(*default_filters).filter(**filters).values(
            'id', 'created_at', 'order_count', 'partner_name', 'shipment_point_name',
            'delivery_point_name', 'service_manager_name', 'courier_name', 'sorter_name',
            'status_value', 'ready_for_pickup', 'revise', 'exported', 'courier_service_accepted',
        )
        return await report_qs
