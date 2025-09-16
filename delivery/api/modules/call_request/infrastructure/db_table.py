from tortoise import fields
from tortoise.models import Model


class CallRequest(Model):
    phone = fields.CharField(13)
    name = fields.CharField(255)
    created_at = fields.DatetimeField(auto_now_add=True)

    # type hints
    id: int

    class Meta:
        table = 'call_requests'


class CallRequestContact(Model):
    phone = fields.CharField(13, null=True, unique=True)
    email = fields.CharField(255, null=True, unique=True)
    name = fields.CharField(255, null=True, unique=True)

    # type hints
    id: int

    class Meta:
        table = 'call_request_contacts'
