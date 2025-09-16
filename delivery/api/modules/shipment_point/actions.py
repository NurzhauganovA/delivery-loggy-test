from api import models, schemas
from api.enums import InitiatorType, HistoryModelName
from api.modules.shipment_point.infrastructure.repository import ShipmentPointRepository
from fastapi_pagination.bases import AbstractPage
from tortoise.transactions import atomic
from .schemas import *
from typing import List, Union

from ...common.action_base import BaseAction
from ...enums import RequestMethods


class ShipmentPointActions(BaseAction):
    def __init__(self, user=None):
        if user:
            self.user = user
        self.repo = ShipmentPointRepository()

    async def shipment_point_create(
        self, shipment_point: PartnerShipmentPointCreate,
    ) -> None:
        # place for business logic
        shipment_point = await self.repo.create(shipment_point)
        await self.save_history(
            partner_shipment_point_id=shipment_point.id,
            request_method=RequestMethods.POST,
        )

    # Because of tests failing we set connection name to 'default'.
    # Whenever you use multiple database you have to define router or to do something.
    @atomic('default')
    async def shipment_point_create_in_bulk(
        self, shipment_points: List[PartnerShipmentPointCreate],
    ) -> None:
        # place for business logic
        shipment_points = await self.repo.bulk_create(shipment_points)

        for shipment_point in shipment_points:
            await self.save_history(
                partner_shipment_point_id=shipment_point.id,
                request_method=RequestMethods.POST,
            )

    async def shipment_point_update(
        self,
        shipment_point_id: int,
        update: PartnerShipmentPointUpdate,
        default_filter_args,
    ) -> None:
        # place for business logic
        await self.repo.partial_update(
            entity_id=shipment_point_id, update_schema=update,
            default_filter_args=default_filter_args
        )
        await self.save_history(
            partner_shipment_point_id=shipment_point_id,
            request_method=RequestMethods.PATCH,
            data=update.dict(exclude_unset=True, exclude_none=True)
        )

    async def shipment_point_get(
        self,
        default_filter_args,
        shipment_point_id: int,
    ) -> Union[PartnerShipmentPointGet, dict]:
        # place for business logic
        return await self.repo.get_by_id(
            default_filter_args=default_filter_args, entity_id=shipment_point_id
        )

    async def shipment_point_get_list(
        self, pagination_params, default_filter_args, filter_kwargs
    ) -> AbstractPage[PartnerShipmentPointGet] | List[PartnerShipmentPointGet]:
        # place for business logic
        return await self.repo.get_list(
            pagination_params=pagination_params, default_filter_args=default_filter_args,
            **filter_kwargs.dict(exclude_unset=True, exclude_none=True)
        )

    async def shipment_point_delete(
        self, default_filter_args, shipment_point_id
    ):
        return await self.repo.delete(
            default_filter_args=default_filter_args, entity_id=shipment_point_id
        )

    async def save_history(self, partner_shipment_point_id, request_method, data = None):
        if not hasattr(self, 'user'):
            return

        return await models.history_create(
            schemas.HistoryCreate(
                initiator_type=InitiatorType.USER,
                initiator_id=self.user.id,
                initiator_role=self.user.profile['profile_type'],
                model_type=HistoryModelName.PARTNER_SHIPMENT_POINTS,
                model_id=partner_shipment_point_id,
                action_data=data,
                request_method=request_method,
            )
        )
