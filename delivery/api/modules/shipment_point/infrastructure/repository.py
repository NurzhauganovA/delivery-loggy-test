from typing import Type, List

from fastapi_pagination.bases import AbstractPage
from fastapi_pagination.ext.tortoise import paginate
from tortoise.exceptions import DoesNotExist

from ..errors import PartnerShipmentPointNotFoundError, PartnerShipmentPointIntegrityError
from api.common.repository_base import BaseRepository, TABLE, SCHEMA, IN_SCHEMA
from ..schemas import PartnerShipmentPointGet
from .db_table import PartnerShipmentPoint


class ShipmentPointRepository(BaseRepository):

    @property
    def _schema(self) -> Type[SCHEMA]:
        return PartnerShipmentPointGet

    @property
    def _table(self) -> Type[TABLE]:
        return PartnerShipmentPoint

    @property
    def _not_found_error(self) -> Type[PartnerShipmentPointNotFoundError]:
        return PartnerShipmentPointNotFoundError

    @property
    def _integrity_error(self) -> Type[PartnerShipmentPointIntegrityError]:
        return PartnerShipmentPointIntegrityError

    async def get_by_id(self, default_filter_args, entity_id) -> SCHEMA:
        try:
            entity = await self._table.filter(*default_filter_args).get(
                id=entity_id
            ).select_related('city', 'partner', 'city__country')
        except DoesNotExist:
            raise self._not_found_error(
                table=self._table.Meta.table,
                detail=f'{self._table.Meta.table} with given ID: {entity_id} was not found'
            )
        return self._schema.from_orm(entity)

    async def ensure_exist(self, default_filter_args, entity_id) -> bool:
        return await self._table.filter(*default_filter_args, id=entity_id).exists()

    async def get_id_by_geolocations(self, latitude, longitude) -> int:
        try:
            entity = await self._table.get(
                latitude=latitude,
                longitude=longitude,
            ).only('id')
        except DoesNotExist:
            raise self._not_found_error(
                table=self._table.Meta.table,
                detail=f'{self._table.Meta.table} with given ID was not found'
            )
        return entity.id

    async def get_list(
        self, default_filter_args, pagination_params=None, **filter_kwargs
    ) -> AbstractPage[PartnerShipmentPointGet] | List[PartnerShipmentPointGet]:
        qs = self._table.filter(
            *default_filter_args).filter(**filter_kwargs).select_related(
            'city', 'partner', 'city__country',
        )
        if pagination_params:
            return await paginate(query=qs, params=pagination_params)
        return [self._schema.from_orm(item) for item in await qs]

    async def bulk_create(self, entities: List[IN_SCHEMA]):
        for shipment_point in entities:
            await self.create(shipment_point)
