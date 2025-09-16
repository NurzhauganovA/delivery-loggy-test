import tortoise.transactions

fields = tortoise.fields


class PartnerSetting(tortoise.models.Model):
    id = fields.IntField(pk=True)
    partner = fields.ForeignKeyField(
        'versions.Partner',
        on_delete=fields.CASCADE,
        related_name='settings',
        unique=True,
        null=False,
    )
    auto_item_for_order_group = fields.ForeignKeyField(
        'versions.Item',
        on_delete=fields.RESTRICT,
        null=True
    )
    default_delivery_point_for_order_group = fields.ForeignKeyField(
        'versions.PartnerShipmentPoint',
        on_delete=fields.RESTRICT,
        null=True
    )
    default_order_group_courier = fields.ForeignKeyField(
        'versions.ProfileCourier',
        on_delete=fields.SET_NULL,
        null=True
    )
    default_order_group_couriers = fields.JSONField()

    # type hints
    partner_id: int
    auto_item_for_order_group_id: int
    default_delivery_point_for_order_group_id: int
    days_to_delivery: int

    class Meta:
        table = 'partner_setting'
