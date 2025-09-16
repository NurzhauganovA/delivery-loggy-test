from typing import Type

from fastapi.encoders import jsonable_encoder
from tortoise.exceptions import DoesNotExist, IntegrityError
from ..errors import PartnerSettingIntegrityError, PartnerSettingPointNotFoundError
from api.common.repository_base import BaseRepository, TABLE, SCHEMA
from ..schemas import PartnerSettingUpdate, PartnerSettingGet
from .db_table import PartnerSetting


class PartnerSettingRepository(BaseRepository):

    @property
    def _schema(self) -> Type[SCHEMA]:
        return PartnerSettingGet

    @property
    def _table(self) -> Type[TABLE]:
        return PartnerSetting

    @property
    def _not_found_error(self) -> Type[PartnerSettingPointNotFoundError]:
        return PartnerSettingPointNotFoundError

    @property
    def _integrity_error(self) -> Type[PartnerSettingIntegrityError]:
        return PartnerSettingIntegrityError

    async def get_by_id(self, partner_id, default_filter_args = None) -> SCHEMA:
        # tortoise orm v0.18.1 hangs on get_or_create()
        # that's why we have to deal with get or create manually.
        # in docs, they say that this bug is fixed.
        entity = await self._table.filter(partner_id=partner_id).first().prefetch_related(
            'partner',
            'auto_item_for_order_group',
            'default_delivery_point_for_order_group__city__country',
        )
        if not entity:
            try:
                entity = await self._table.create(partner_id=partner_id)
                await entity.fetch_related(
                    'partner',
                    'auto_item_for_order_group',
                    'default_delivery_point_for_order_group__city__country',
                )
            except IntegrityError:
                raise self._integrity_error(
                    table=self._table.Meta.table,
                    detail=f'Could not create partner setting',
                )
        return self._schema.from_orm(entity)

    async def partial_update(
        self,
        partner_id: int,
        update_schema: PartnerSettingUpdate,
        default_filter_args = None,
    ) -> TABLE:
        # tortoise orm v0.18.1 hangs on get_or_create()
        # that's why we have to deal with get or create manually.
        # in docs, they say that this bug is fixed.
        entity = await self._table.filter(partner_id=partner_id).first().prefetch_related(
            'partner',
            'auto_item_for_order_group',
            'default_delivery_point_for_order_group__city__country',
        )
        if not entity:
            try:
                entity = await self._table.create(partner_id=partner_id)
            except IntegrityError as e:
                raise self._integrity_error(
                    table=self._table.Meta.table,
                    detail=str(e)
                )
        try:
            await entity.update_from_dict(
                jsonable_encoder(update_schema, exclude_unset=True)).save()
            await entity.fetch_related('partner')
            return self._schema.from_orm(entity)
        except IntegrityError as e:
            raise self._integrity_error(
                table=self._table.Meta.table,
                detail=str(e)
            )