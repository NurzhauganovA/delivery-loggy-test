import abc

import typing
from functools import wraps
from typing import Generic, TypeVar, Type, List

from fastapi_pagination.bases import AbstractPage
from fastapi_pagination.ext.tortoise import paginate

from fastapi.encoders import jsonable_encoder
from tortoise.exceptions import DoesNotExist, IntegrityError
from ..common import BaseIntegrityError, BaseNotFoundError
from .schema_base import BaseOutSchema, BaseInSchema

IN_SCHEMA = TypeVar("IN_SCHEMA", bound=BaseInSchema)
SCHEMA = TypeVar("SCHEMA", bound=BaseOutSchema)
TABLE = TypeVar("TABLE")


class BaseRepository(Generic[IN_SCHEMA, SCHEMA, TABLE], metaclass=abc.ABCMeta):
    @property
    @abc.abstractmethod
    def _table(self) -> Type[TABLE]:
        ...

    @property
    @abc.abstractmethod
    def _schema(self) -> Type[SCHEMA]:
        ...

    @property
    @abc.abstractmethod
    def _not_found_error(self) -> Type[BaseNotFoundError]:
        ...

    @property
    @abc.abstractmethod
    def _integrity_error(self) -> Type[BaseIntegrityError]:
        ...

    async def create(self, in_schema: IN_SCHEMA) -> TABLE:
        try:
            return await self._table.create(**jsonable_encoder(in_schema))
        except IntegrityError as e:
            raise self._integrity_error(
                table=self._table.Meta.table,
                detail=str(e)
            )

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

    async def get_list(
        self, default_filter_args, pagination_params=None, **filter_kwargs
    ) -> AbstractPage[SCHEMA] | List[SCHEMA]:
        qs = self._table.filter(
            *default_filter_args).filter(**filter_kwargs)
        if pagination_params:
            return await paginate(qs, pagination_params)
        return [self._schema.from_orm(item) for item in await qs]

    async def partial_update(
        self,
        entity_id: int,
        update_schema: BaseInSchema,
        default_filter_args,
    ) -> TABLE:
        try:
            entity = await self._table.filter(*default_filter_args).get(
                id=entity_id
            )
        except DoesNotExist:
            raise self._not_found_error(
                table=self._table.Meta.table,
                detail=f'{self._table.Meta.table} with given ID: {entity_id} was not found'
            )
        try:
            await entity.update_from_dict(
                jsonable_encoder(update_schema, exclude_unset=True)).save()

            return entity
        except IntegrityError as e:
            raise self._integrity_error(
                table=self._table.Meta.table,
                detail=str(e)
            )

    async def partial_update_from_dict(
            self,
            entity_id: int,
            update_dict: dict,
            default_filter_args,
    ) -> TABLE:
        try:
            entity = await self._table.filter(*default_filter_args).get(
                id=entity_id
            )
        except DoesNotExist:
            raise self._not_found_error(
                table=self._table.Meta.table,
                detail=f'{self._table.Meta.table} with given ID: {entity_id} was not found'
            )
        try:
            await entity.update_from_dict(update_dict).save()

            return entity
        except IntegrityError as e:
            raise self._integrity_error(
                table=self._table.Meta.table,
                detail=str(e)
            )

    async def delete(
        self,
        default_filter_args,
        entity_id: int,
    ) -> None:
        try:
            entity = await self._table.filter(*default_filter_args).get(
                id=entity_id
            )
        except DoesNotExist:
            raise self._not_found_error(
                table=self._table.Meta.table,
                detail=f'{self._table.Meta.table} with given ID: {entity_id} was not found'
            )
        await entity.delete()
