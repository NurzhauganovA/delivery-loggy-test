from tortoise.models import Model
from tortoise import fields

from .. import models


class Rate(Model):
    courier: fields.ForeignKeyRelation['models.ProfileCourier'] = fields.ForeignKeyField(
        'versions.ProfileCourier',
        'ratings',
    )
    value = fields.SmallIntField(default=100)
    created_at = fields.DatetimeField(auto_now_add=True)

    class Meta:
        table = 'ratings'
        ordering = ('-created_at',)


async def rate_list(courier_id: int) -> list:
    rates = await Rate.filter(courier_id=courier_id).values()
    return rates

