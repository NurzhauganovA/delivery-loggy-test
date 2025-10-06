from tortoise import(
    fields,
    Model,
)


class CourierServiceStatus(Model):
    id = fields.IntField(pk=True)
    order = fields.ForeignKeyField(
        model_name='versions.Order'
    )
    status = fields.CharField(
        max_length=128,
        null=False
    )
    created_at = fields.DatetimeField(auto_now_add=True)

    class Meta:
        table = 'courier_service_status'
