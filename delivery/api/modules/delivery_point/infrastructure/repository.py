from typing import Type, List

from fastapi.encoders import jsonable_encoder
from fastapi_pagination.bases import AbstractPage
from fastapi_pagination.ext.tortoise import paginate
from pydantic import parse_obj_as
from tortoise.exceptions import DoesNotExist
from tortoise.models import MODEL

from ..errors import *
from api.common.repository_base import BaseRepository, TABLE, SCHEMA, IN_SCHEMA
from ..schemas import DeliveryPointGet
from .db_table import DeliveryPoint


class DeliveryPointRepository(BaseRepository):

    @property
    def _schema(self) -> Type[SCHEMA]:
        return DeliveryPointGet

    @property
    def _table(self):
        return DeliveryPoint

    @property
    def _not_found_error(self) -> Type[DeliveryPointNotFoundError]:
        return DeliveryPointNotFoundError

    @property
    def _integrity_error(self) -> Type[DeliveryPointIntegrityError]:
        return DeliveryPointIntegrityError

    async def get_by_id(self, default_filter_args, entity_id) -> SCHEMA:
        try:
            entity = await self._table.filter(*default_filter_args).get(
                id=entity_id
            )
        except DoesNotExist:
            raise self._not_found_error(
                table=self._table.Meta.table,
                detail=f'{self._table.Meta.table} with given ID: {entity_id} was not found'
            )
        return self._schema.from_orm(entity)

    async def ensure_exist(self, default_filter_args, entity_id) -> bool:
        return await self._table.filter(*default_filter_args, id=entity_id).exists()

    async def get_list(
        self, default_filter_args, pagination_params=None, **filter_kwargs
    ) -> AbstractPage[DeliveryPointGet] | List[DeliveryPointGet]:
        qs = self._table.filter(
            *default_filter_args).filter(**filter_kwargs)
        if pagination_params:
            return await paginate(query=qs, params=pagination_params)
        delivery_points = await qs
        return parse_obj_as(List[self._schema], delivery_points)

    async def create(self, in_schema: IN_SCHEMA) -> TABLE:
        entity = await self._table.create(**jsonable_encoder(in_schema))
        return entity

    async def bulk_create(self, entities: List[IN_SCHEMA]):
        for delivery_point in entities:
            await self.create(delivery_point)
