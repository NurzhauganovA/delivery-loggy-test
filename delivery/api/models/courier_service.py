from tortoise import(
    fields,
    Model,
)


class CourierService(Model):
    id = fields.IntField(pk=True)
    courier_service = fields.CharField(
        max_length=256,
        null=True,
    )
    warehouse_id = fields.CharField(
        max_length=256,
        null=True,
    )
    city = fields.ForeignKeyField(
        'versions.City'
    )
    partner = fields.ForeignKeyField(
        'versions.Partner'
    )

    class Meta:
        table = 'courier_service'
