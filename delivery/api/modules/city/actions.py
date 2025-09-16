from fastapi_pagination.bases import AbstractPage
from typing import List, Union

from .infrastructure.repository import CityRepository
from .schemas import *
from ...common.action_base import BaseAction


class CityActions(BaseAction):
    def __init__(self):
        self.repo = CityRepository()

    async def city_create(
        self, city: CityCreate,
    ):
        # place for business logic
        return await self.repo.create(city)

    async def city_update(
        self,
        city_id: int,
        update: CityUpdate | CityPartialUpdate,
        default_filter_args,
    ):
        # place for business logic
        return await self.repo.partial_update(
            entity_id=city_id, update_schema=update,
            default_filter_args=default_filter_args
        )

    async def city_get(
        self,
        default_filter_args,
        city_id: int,
    ) -> Union[CityGet, dict]:
        # place for business logic
        return await self.repo.get_by_id(
            default_filter_args=default_filter_args, entity_id=city_id
        )

    async def city_get_list(
        self,
        default_filter_args,
        filter_kwargs,
        pagination_params=None,
    ) -> AbstractPage[CityList] | List[CityList]:
        # place for business logic
        return await self.repo.get_list(
            pagination_params=pagination_params, default_filter_args=default_filter_args,
            **filter_kwargs,
        )

    async def city_delete(
        self, default_filter_args, city_id
    ):
        return await self.repo.delete(
            default_filter_args=default_filter_args, entity_id=city_id
        )


__all__ = (
    'CityActions',
)
