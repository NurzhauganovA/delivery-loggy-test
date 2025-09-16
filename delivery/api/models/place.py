# TODO: add on unique constraint error handlers
import asyncio
from typing import Union, List

import tortoise

from ..conf import conf
from .. import models
from .. import schemas
from .. import utils
from ..services import geocoder
from api.modules.delivery_point.infrastructure.repository import DeliveryPointRepository
from api.modules.delivery_point.schemas import DeliveryPointCreate


fields = tortoise.fields


class PlaceNotFound(Exception):
    """Raises if place with provided ID was not found."""


class Place(tortoise.models.Model):
    id = fields.IntField(pk=True)
    address = fields.CharField(max_length=255)
    latitude = fields.DecimalField(max_digits=10, decimal_places=8, null=True)
    longitude = fields.DecimalField(max_digits=11, decimal_places=8, null=True)
    city = fields.ForeignKeyField(
        'versions.City',
        to_field='id',
        on_delete=fields.SET_NULL,
        null=True,
    )

    class Config:
        extra = 'forbid'

    class Meta:
        table = 'place'


@utils.as_dict(from_model=True)
async def place_get_list() -> list:
    repo = DeliveryPointRepository()
    return await repo.get_list([])


@utils.as_dict(from_model=True)
async def place_get(place_id: int) -> Place:
    repo = DeliveryPointRepository()
    try:
        return await repo.get_by_id([], entity_id=place_id)
    except tortoise.exceptions.DoesNotExist as e:
        raise PlaceNotFound(
            f'Place with provided ID: {place_id} was not found') from e


@utils.as_dict(from_model=True)
async def place_create(place: schemas.PlaceCreate) -> Place:
    repo = DeliveryPointRepository()
    dp = DeliveryPointCreate(
        latitude=place.latitude,
        longitude=place.longitude,
        address=place.address,
    )
    return await repo.create(dp)


async def place_update(place_id: int, update: schemas.PlaceUpdate, **kwargs) -> dict:
    repo = DeliveryPointRepository()
    dp = DeliveryPointCreate(
        latitude=update.latitude,
        longitude=update.longitude,
        address=update.address,
    )
    try:
        await repo.partial_update(entity_id=place_id, update_schema=dp, default_filter_args=[])
    except tortoise.exceptions.DoesNotExist as e:
        raise PlaceNotFound(
            f'Place with provided ID: {place_id} was not found',
        ) from e

    try:
        if not update.latitude and not update.longitude:
            coordinates = await asyncio.wait_for(
                geocoder.service.to_coordinates(update.address),
                timeout=conf.geocoder.timeout,
            )

            update.latitude = coordinates.dict()['latitude']
            update.longitude = coordinates.dict()['longitude']
        await repo.partial_update_from_dict(entity_id=place_id, update_dict=update.dict(), default_filter_args=[])
    except tortoise.exceptions.IntegrityError as e:
        raise models.EntityDoesNotExist(
            'City with provided ID does not exist',
        ) from e

    return await repo.get_by_id([], place_id)


async def place_delete(place_id: int, **kwargs) -> None:
    repo = DeliveryPointRepository()
    try:
        await repo.delete([], place_id)
    except tortoise.exceptions.DoesNotExist as e:
        raise PlaceNotFound(
            f'Place with provided ID: {place_id} was not found',
        ) from e
