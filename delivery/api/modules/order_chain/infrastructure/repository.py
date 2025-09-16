from typing import Type, List

from fastapi import UploadFile
from fastapi.encoders import jsonable_encoder
from fastapi_pagination.ext.tortoise import paginate
from tortoise.exceptions import DoesNotExist
from tortoise.exceptions import IntegrityError
from tortoise.query_utils import Prefetch

from api.models import Order
from  .. import errors
from api.common.repository_base import BaseRepository, TABLE, SCHEMA, IN_SCHEMA
from .db_table import (
    OrderChain, OrderChainStage,
    OrderChainSender, OrderChainReceiver,
    OrderChainStageSupportingDocument
)
from ..schemas.dto_schemas import (
    OrderChainGetDto, OrderChainStageGetDto,
    OrderChainReceiverGetDto, OrderChainSenderGetDto, SupportDocumentGetDto,
)
from ...city.infrastructure.repository import CityRepository


class OrderChainRepository(BaseRepository):

    @property
    def _schema(self) -> Type[SCHEMA]:
        return OrderChainGetDto

    @property
    def _table(self) -> Type[TABLE]:
        return OrderChain

    @property
    def _not_found_error(self) -> Type[errors.OrderChainNotFoundError]:
        return errors.OrderChainNotFoundError

    @property
    def _integrity_error(self) -> Type[errors.OrderChainIntegrityError]:
        return errors.OrderChainIntegrityError

    async def get_by_id(self, default_filter_args, entity_id) -> SCHEMA:
        try:

            entity = await self._table.filter(*default_filter_args).get(
                id=entity_id
            ).select_related(
                'partner', 'sender__city__country', 'receiver__city__country'
            ).prefetch_related(
                Prefetch(
                    'stages',
                    OrderChainStage.all().prefetch_related(
                        Prefetch(
                            'order',
                            Order.all_objects.all().select_related('current_status', 'courier__user'),
                            'order'
                        ),
                        Prefetch(
                            'support_document_set',
                            OrderChainStageSupportingDocument.all(),
                            'support_documents'
                        )
                    ),
                )
            )
        except DoesNotExist:
            raise self._not_found_error(
                table=self._table.Meta.table,
                detail=f'{self._table.Meta.table} with given ID: {entity_id} was not found'
            )
        return self._schema.from_orm(entity)

    async def get_list(
        self, default_filter_args, pagination_params=None, **filter_kwargs
    ):
        qs = self._table.filter(
            *default_filter_args).filter(**filter_kwargs).select_related(
            'partner', 'sender__city__country', 'receiver__city__country'
        ).prefetch_related(
                Prefetch(
                    'stages',
                    OrderChainStage.all().prefetch_related(
                        Prefetch(
                            'order',
                            Order.all_objects.all().select_related('current_status', 'courier__user'),
                            'order'
                        ),
                        Prefetch(
                            'support_document_set',
                            OrderChainStageSupportingDocument.all(),
                            'support_documents'
                        )
                    ),
                )
            ).order_by('-created_at')
        if pagination_params:
            return await paginate(query=qs, params=pagination_params)
        return [self._schema.from_orm(item) for item in await qs]

    async def create(self, in_schema: IN_SCHEMA) -> TABLE:
        try:
            city_repo = CityRepository()
            city = await city_repo.get_by_id([], in_schema['city_id'])
            return await self._table.create(
                created_at=city.localtime,
                updated_at=city.localtime,
                **jsonable_encoder(in_schema),
            )
        except IntegrityError as e:
            raise self._integrity_error(
                table=self._table.Meta.table,
                detail=str(e)
            )


class OrderChainSenderRepository(BaseRepository):

    @property
    def _schema(self) -> Type[SCHEMA]:
        return OrderChainSenderGetDto

    @property
    def _table(self) -> Type[TABLE]:
        return OrderChainSender

    @property
    def _not_found_error(self) -> Type[errors.OrderChainSenderNotFoundError]:
        return errors.OrderChainSenderNotFoundError

    @property
    def _integrity_error(self) -> Type[errors.OrderChainSenderIntegrityError]:
        return errors.OrderChainSenderIntegrityError


class OrderChainReceiverRepository(BaseRepository):

    @property
    def _schema(self) -> Type[SCHEMA]:
        return OrderChainReceiverGetDto

    @property
    def _table(self) -> Type[TABLE]:
        return OrderChainReceiver

    @property
    def _not_found_error(self) -> Type[errors.OrderChainSenderNotFoundError]:
        return errors.OrderChainSenderNotFoundError

    @property
    def _integrity_error(self) -> Type[errors.OrderChainSenderIntegrityError]:
        return errors.OrderChainSenderIntegrityError


class OrderChainStageRepository(BaseRepository):

    @property
    def _schema(self) -> Type[SCHEMA]:
        return OrderChainStageGetDto

    @property
    def _table(self) -> Type[TABLE]:
        return OrderChainStage

    @property
    def _not_found_error(self) -> Type[errors.OrderChainStageNotFoundError]:
        return errors.OrderChainStageNotFoundError

    @property
    def _integrity_error(self) -> Type[errors.OrderChainStageIntegrityError]:
        return errors.OrderChainStageIntegrityError

    async def create(self, in_schema: IN_SCHEMA) -> TABLE:
        order_obj = await Order.get(id=in_schema['order_id']).select_related('city')
        order_time = await order_obj.localtime
        return await self._table.create(
            created_at=order_time,
            updated_at=order_time,
            **jsonable_encoder(in_schema),
        )

    async def get_by_id(self, default_filter_args, entity_id: int, **kwargs) -> SCHEMA:
        try:
            entity = await self._table.filter(*default_filter_args).get(
                id=entity_id, **kwargs
            ).select_related(
                'order__current_status', 'order__courier__user'
            ).prefetch_related(
                Prefetch(
                    'support_document_set',
                    OrderChainStageSupportingDocument.all(),
                    'support_documents'
                )
            )

        except DoesNotExist:
            raise self._not_found_error(
                table=self._table.Meta.table,
                detail=f'{self._table.Meta.table} with given ID: {entity_id} was not found'
            )

        return self._schema.from_orm(entity)

    async def delete(
        self,
        default_filter_args,
        entity_id: int,
        **kwargs,
    ) -> None:
        try:
            entity = await self._table.filter(*default_filter_args).get(
                id=entity_id, **kwargs
            )
        except DoesNotExist:
            raise self._not_found_error(
                table=self._table.Meta.table,
                detail=f'{self._table.Meta.table} with given ID: {entity_id} was not found'
            )
        await entity.delete()


class OrderChainSupportDocumentRepository(BaseRepository):

    @property
    def _schema(self) -> Type[SCHEMA]:
        return SupportDocumentGetDto

    @property
    def _table(self) -> Type[TABLE]:
        return OrderChainStageSupportingDocument

    @property
    def _not_found_error(self) -> Type[errors.OrderChainSupportDocumentNotFoundError]:
        return errors.OrderChainSupportDocumentNotFoundError

    @property
    def _integrity_error(self) -> Type[errors.OrderChainSupportDocumentIntegrityError]:
        return errors.OrderChainSupportDocumentIntegrityError

    async def create_by_params(
            self,
            image: UploadFile,
            document_number: str,
            comment: str,
            order_chain_stage_id: int,
    ) -> TABLE:
        try:
            return await self._table.create(
                image=image,
                document_number=document_number,
                comment=comment,
                order_chain_stage_id=order_chain_stage_id,
            )
        except IntegrityError as e:
            raise self._integrity_error(
                table=self._table.Meta.table,
                detail=str(e)
            )


    async def partial_update_by_params(
        self,
        entity_id: int,
        default_filter_args,
        image: UploadFile,
        document_number: str,
        comment: str,
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
            if image:
                entity.image = image
            if document_number:
                entity.document_number = document_number
            if comment:
                entity.comment = comment
            await entity.save(update_fields=['image', 'document_number', 'comment'])

            return entity
        except IntegrityError as e:
            raise self._integrity_error(
                table=self._table.Meta.table,
                detail=str(e)
            )

    async def bulk_delete(
        self,
        default_filter_args,
        ids: List
    ) -> None:
        await self._table.filter(*default_filter_args, id__in=ids).delete()

