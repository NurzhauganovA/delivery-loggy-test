from api.modules.delivery_point.infrastructure.repository import DeliveryPointRepository
from fastapi_pagination.bases import AbstractPage
from tortoise.transactions import atomic
from .schemas import *
from typing import List, Union

from ...common.action_base import BaseAction


class DeliveryPointActions(BaseAction):
    def __init__(self):
        self.repo = DeliveryPointRepository()

    async def delivery_point_create(
        self, delivery_point: DeliveryPointCreate,
    ):
        # place for business logic
        return await self.repo.create(delivery_point)

    # Because of tests failing we set connection name to 'default'.
    # Whenever you use multiple database you have to define router or to do something.
    @atomic('default')
    async def delivery_point_create_in_bulk(
        self, delivery_points: List[DeliveryPointCreate],
    ) -> None:
        # place for business logic
        await self.repo.bulk_create(delivery_points)

    async def delivery_point_update(
        self,
        delivery_point_id: int,
        update: DeliveryPointUpdate,
        default_filter_args,
    ):
        # place for business logic
        return await self.repo.partial_update(
            entity_id=delivery_point_id, update_schema=update,
            default_filter_args=default_filter_args
        )

    async def delivery_point_get(
        self,
        default_filter_args,
        delivery_point_id: int,
    ) -> Union[DeliveryPointGet, dict]:
        # place for business logic
        return await self.repo.get_by_id(
            default_filter_args=default_filter_args, entity_id=delivery_point_id
        )

    async def delivery_point_get_list(
        self, pagination_params, default_filter_args, filter_kwargs
    ) -> AbstractPage[DeliveryPointGet] | List[DeliveryPointGet]:
        # place for business logic
        return await self.repo.get_list(
            pagination_params=pagination_params, default_filter_args=default_filter_args,
            **filter_kwargs.dict(exclude_unset=True, exclude_none=True)
        )

    async def delivery_point_delete(
        self, default_filter_args, delivery_point_id
    ):
        return await self.repo.delete(
            default_filter_args=default_filter_args, entity_id=delivery_point_id
        )
