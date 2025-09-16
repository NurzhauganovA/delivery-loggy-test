from tortoise import Model
from tortoise import fields

from api import models


class DeliveryPoint(Model):
    address = fields.CharField(max_length=255)
    latitude = fields.DecimalField(max_digits=10, decimal_places=8, null=True)
    longitude = fields.DecimalField(max_digits=11, decimal_places=8, null=True)

    # type hints
    id: int
    order_id: int

    class Meta:
        table = 'delivery_point'
