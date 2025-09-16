import tortoise

from .. import enums
from .. import models
from .. import schemas
from .. import utils


fields = tortoise.fields


class TransportNotFound(Exception):
    """Raises if transport with provided ID not found."""


# TODO: figure out which profiles can own the transport
class Transport(tortoise.models.Model):
    id = fields.IntField(pk=True)
    courier = fields.ForeignKeyField(
        'versions.ProfileCourier',
        to_field='id',
        on_delete=fields.SET_NULL,
        null=True,
    )
    type = fields.CharEnumField(**enums.TransportType.to_kwargs())
    name = fields.CharField(max_length=64)
    plate_number = fields.CharField(max_length=32, null=True)
    fuel_consumption = fields.FloatField(null=True)
    average_speed = fields.IntField(null=True)
    payload = fields.FloatField(null=True)
    width = fields.FloatField(null=True)
    height = fields.FloatField(null=True)
    depth = fields.FloatField(null=True)
    capacity = fields.FloatField(null=True)

    class Config:
        extra = 'forbid'

    class Meta:
        table = 'transport'


@utils.as_dict()
async def transport_get(transport_id: int) -> list:
    return await Transport.filter(id=transport_id).values()


@utils.as_dict(from_model=True)
async def transport_create(transport: schemas.TransportCreate) -> list:
    try:
        return await Transport.create(**transport.dict())
    except tortoise.exceptions.IntegrityError as e:
        raise models.ProfileNotFound(
            f'Courier with provided ID: {transport.courier_id} not found',
        ) from e


async def transport_update(transport_id: int,
                           update: schemas.TransportCreate) -> dict:
    await transport_ensure_exists(transport_id)
    await Transport.filter(id=transport_id).update(**update.dict())

    return await transport_get(transport_id)


async def transport_delete(transport_id: int) -> None:
    await transport_ensure_exists(transport_id)
    await Transport.filter(id=transport_id).delete()


async def transport_ensure_exists(transport_id: int) -> None:
    transport = await transport_get(transport_id)
    if not transport:
        raise TransportNotFound(
            f'Transport with provided ID: {transport_id} not found')
