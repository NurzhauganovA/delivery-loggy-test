from typing import Type, List

from fastapi.encoders import jsonable_encoder
from fastapi_pagination.bases import AbstractPage
from fastapi_pagination.ext.tortoise import paginate
from pydantic import parse_obj_as
from tortoise.exceptions import DoesNotExist, IntegrityError

from api.common.schema_base import BaseInSchema
from ..errors import *
from api.common.repository_base import BaseRepository, TABLE, SCHEMA, IN_SCHEMA
from ..schemas import *
from .db_table import City


class CityRepository(BaseRepository):

    @property
    def _schema(self) -> Type[SCHEMA]:
        return CityGet

    @property
    def _list_schema(self) -> Type[SCHEMA]:
        return CityList

    @property
    def _table(self):
        return City

    @property
    def _not_found_error(self) -> Type[CityNotFoundError]:
        return CityNotFoundError

    @property
    def _integrity_error(self) -> Type[CityIntegrityError]:
        return CityIntegrityError

    async def get_by_id(self, default_filter_args, entity_id) -> SCHEMA:
        try:
            entity = await self._table.filter(*default_filter_args).get(
                id=entity_id
            ).select_related('country')
        except DoesNotExist:
            raise self._not_found_error(
                table=self._table.Meta.table,
                detail='{table} with given ID: {entity_id} was not found',
                entity_id=entity_id,
            )
        return self._schema.from_orm(entity)

    async def ensure_exist(self, default_filter_args, entity_id) -> bool:
        return await self._table.filter(*default_filter_args, id=entity_id).exists()

    async def get_list(
        self, default_filter_args, pagination_params=None, **filter_kwargs
    ) -> AbstractPage[CityList] | List[CityList]:
        qs = self._table.filter(
            *default_filter_args).filter(**filter_kwargs)
        if pagination_params:
            return await paginate(query=qs, params=pagination_params)
        cities = await qs
        return parse_obj_as(List[self._list_schema], cities)

    async def create(self, in_schema: IN_SCHEMA) -> TABLE:
        try:
            entity = await self._table.create(**jsonable_encoder(in_schema))
        except IntegrityError as e:
            raise self._integrity_error(
                table=self._table.Meta.table,
                detail=str(e)
            )
        await entity.fetch_related('country')
        return entity

    async def partial_update(
        self,
        entity_id: int,
        update_schema: BaseInSchema,
        default_filter_args,
    ) -> TABLE:
        entity = await super().partial_update(
            entity_id=entity_id,
            update_schema=update_schema,
            default_filter_args=default_filter_args,
        )
        await entity.fetch_related('country')

        return entity
