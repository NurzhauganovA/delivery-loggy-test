import tortoise.transactions
from tortoise.timezone import now

from api import models
from api.enums import InitiatorType, RequestMethods, ProfileType
from api.models import fields as custom_fields

from .. import enums
from ...city.infrastructure.db_table import City

fields = tortoise.fields


class OrderChainSender(tortoise.models.Model):
    id = fields.IntField(pk=True)
    name = fields.CharField(max_length=255)
    phone_number = fields.CharField(min_length=13, max_length=255)
    email = fields.CharField(max_length=100, null=True)
    address = fields.CharField(max_length=255)
    latitude = fields.DecimalField(max_digits=10, decimal_places=8, null=True)
    longitude = fields.DecimalField(max_digits=11, decimal_places=8, null=True)
    city = fields.ForeignKeyField(
        'versions.City',
        to_field='id',
        on_delete=fields.SET_NULL,
        null=True,
    )

    class Meta:
        table = 'order_chain_sender'

    @property
    async def localtime(self):
        if not isinstance(self.city, City):
            await self.fetch_related('city')
        if self.city is None:
            return now()
        return self.city.localtime


class OrderChainReceiver(tortoise.models.Model):
    id = fields.IntField(pk=True)
    name = fields.CharField(max_length=255)
    phone_number = fields.CharField(min_length=13, max_length=255)
    email = fields.CharField(max_length=100, null=True)
    address = fields.CharField(max_length=255)
    latitude = fields.DecimalField(max_digits=10, decimal_places=8, null=True)
    longitude = fields.DecimalField(max_digits=11, decimal_places=8, null=True)
    city = fields.ForeignKeyField(
        'versions.City',
        to_field='id',
        on_delete=fields.SET_NULL,
        null=True,
    )

    class Meta:
        table = 'order_chain_receiver'

    @property
    async def localtime(self):
        if not isinstance(self.city, City):
            await self.fetch_related('city')
        if self.city is None:
            return now()
        return self.city.localtime


class OrderChain(tortoise.models.Model):
    id = fields.IntField(pk=True)
    external_id = fields.CharField(max_length=255, null=True)
    comment = fields.CharField(max_length=255, null=True)
    package_params = fields.JSONField(null=True)
    type = fields.CharEnumField(
        **enums.OrderChainType.to_kwargs(default=enums.OrderChainType.SIMPLE)
    )
    partner = fields.ForeignKeyField(
        'versions.Partner',
        to_field='id',
        on_delete=fields.CASCADE,
        null=False,
        related_name='orderchain_set',
    )
    sender = fields.ForeignKeyField(
        'versions.OrderChainSender',
        to_field='id',
        on_delete=fields.CASCADE,
        null=False,
        related_name='orderchain_set',
    )
    receiver = fields.ForeignKeyField(
        'versions.OrderChainReceiver',
        to_field='id',
        on_delete=fields.CASCADE,
        null=False,
        related_name='orderchain_set',
    )
    updated_at = fields.DatetimeField(auto_now=True)
    created_at = fields.DatetimeField(auto_now_add=True)
    fact_delivery_datetime = fields.DatetimeField(null=True)
    expected_delivery_datetime = fields.DatetimeField(null=True)
    deadline_delivery_datetime = fields.DatetimeField(null=True)
    status = fields.CharEnumField(
        **enums.OrderChainStatus.to_kwargs(default=enums.OrderChainStatus.NEW)
    )

    class Meta:
        table = 'order_chain'

    @property
    async def receiver_localtime(self):
        if not isinstance(self.receiver, OrderChainReceiver):
            await self.fetch_related('receiver')
        if self.receiver is None:
            return now()
        return await self.receiver.localtime

    @property
    async def sender_localtime(self):
        if not isinstance(self.sender, OrderChainSender):
            await self.fetch_related('sender')
        if self.sender is None:
            return now()
        return await self.receiver.localtime


class OrderChainStage(tortoise.models.Model):
    id = fields.IntField(pk=True)
    order: fields.ForeignKeyRelation['models.Order'] = fields.ForeignKeyField(
        'versions.Order',
        'order_chain_stages_set',
        on_delete=fields.CASCADE,
    )
    order_chain: fields.ForeignKeyRelation['OrderChain'] = fields.ForeignKeyField(
        'versions.OrderChain',
        'stages',
        on_delete=fields.CASCADE,
    )
    updated_at = fields.DatetimeField(auto_now=True)
    created_at = fields.DatetimeField(auto_now_add=True)
    type = fields.CharEnumField(
        **enums.StageType.to_kwargs(default=enums.StageType.ROAD)
    )
    position = fields.IntField()
    is_last = fields.BooleanField(default=False)

    class Meta:
        table = 'order_chain_stage'


class OrderChainStageSupportingDocument(tortoise.models.Model):
    order_chain_stage: fields.ForeignKeyRelation['OrderChainStage'] = fields.ForeignKeyField(
        'versions.OrderChainStage',
        'support_document_set',
        on_delete=fields.CASCADE,
    )
    document_number = fields.CharField(max_length=255)
    image = custom_fields.ImageField(upload_to='order_chain_supporting_documents')
    comment = fields.TextField(null=True)

    # type hints
    order_chain_id: int

    class Meta:
        table = 'order_chain_stage_supporting_document'


class OrderChainHistory(tortoise.Model):
    initiator_id = fields.IntField(null=True)
    initiator_type = fields.CharEnumField(
        **InitiatorType.to_kwargs(
            default=InitiatorType.USER
        )
    )
    request_method = fields.CharEnumField(**RequestMethods.to_kwargs())
    model: fields.ForeignKeyRelation['OrderChain'] = fields.ForeignKeyField(
        'versions.OrderChain',
        'history',
        on_delete=fields.CASCADE,
    )
    model_type = fields.CharField(max_length=50)
    action_data = fields.JSONField(null=True)
    created_at = fields.DatetimeField(auto_now_add=True)
    initiator_role = fields.CharEnumField(**ProfileType.to_kwargs(null=True))

    class Meta:
        table = 'order_chain_history'