import tortoise.transactions
from tortoise.timezone import now

from api import models
from api.enums import RequestMethods, ProfileType, InitiatorType
from api.modules.city.infrastructure.db_table import City

fields = tortoise.fields


class PartnerShipmentPoint(tortoise.models.Model):
    name = fields.CharField(max_length=200, null=True)
    partner = fields.ForeignKeyField(
        'versions.Partner',
        to_field='id',
        on_delete=fields.CASCADE,
        null=False,
        related_name='shipment_points',
    )
    address = fields.CharField(max_length=255)
    latitude = fields.DecimalField(max_digits=10, decimal_places=8, null=True)
    longitude = fields.DecimalField(max_digits=11, decimal_places=8, null=True)
    city = fields.ForeignKeyField(
        'versions.City',
        to_field='id',
        on_delete=fields.SET_NULL,
        null=True,
    )

    # type hints
    id: int
    partner_id: int
    city_id: int
    item_set: fields.ManyToManyRelation['models.Item']
    sorters: fields.ReverseRelation['models.ProfileSorter']

    class Meta:
        table = 'partner_shipment_point'
        unique_together = ('city_id', 'name', 'partner_id')

    @property
    async def localtime(self):
        if not isinstance(self.city, City):
            await self.fetch_related('city')
        if self.city is None:
            return now()
        return self.city.localtime


class PartnerShipmentPointHistory(tortoise.Model):
    initiator_id = fields.IntField(null=True)
    initiator_type = fields.CharEnumField(
        **InitiatorType.to_kwargs(
            default=InitiatorType.USER
        )
    )
    request_method = fields.CharEnumField(**RequestMethods.to_kwargs())
    model: fields.ForeignKeyRelation['PartnerShipmentPoint'] = fields.ForeignKeyField(
        'versions.PartnerShipmentPoint',
        'history',
        on_delete=fields.CASCADE,
    )
    model_type = fields.CharField(max_length=50)
    action_data = fields.JSONField(null=True)
    created_at = fields.DatetimeField(auto_now_add=True)
    initiator_role = fields.CharEnumField(**ProfileType.to_kwargs(null=True))

    class Meta:
        table = 'partner_shipment_point_history'
