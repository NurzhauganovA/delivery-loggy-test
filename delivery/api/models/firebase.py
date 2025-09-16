from tortoise import fields
from tortoise.models import Model

from .. import enums
from .. import models
from .. import schemas


class DeviceAlreadyExistError(Exception):
    """Raises when device with given id is already exist"""


class FCMDevice(Model):
    id = fields.CharField(max_length=1000, pk=True)
    type = fields.CharEnumField(**enums.DeviceType.to_kwargs())
    user: fields.ForeignKeyRelation['models.User'] = fields.ForeignKeyField(
        'versions.User',
        'fcmdevices',
    )

    # type hints
    user_id: int

    class Meta:
        table = 'firebase_devices'


async def device_create(create: schemas.FCMDeviceCreate, **kwargs):
    await FCMDevice.filter(id=create.id).delete()
    await FCMDevice.create(**create.dict(exclude_unset=True), **kwargs)


async def device_delete(**kwargs):
    await FCMDevice.filter(**kwargs).delete()
