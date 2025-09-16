from tortoise import fields
from tortoise.exceptions import IntegrityError
from tortoise.models import Model
from .. import models, security
from ..schemas import RevokedTokenCreate


class RevokedToken(Model):
    id = fields.IntField(pk=True)
    client: fields.ForeignKeyRelation['models.User'] = fields.ForeignKeyField(
        'versions.User',
        'revoked_tokens',
        fields.CASCADE,
    )
    token = fields.CharField(max_length=4080, unique=True, index=True)
    exp = fields.DatetimeField()
    revoked_at = fields.DatetimeField(auto_now_add=True)

    # type hints
    client_id: int

    class Config:
        extra = 'forbid'

    class Meta:
        table = 'revoked_token'


async def token_revoke(token: str):
    try:
        payload = RevokedTokenCreate(token=token, **security.unsign_token(token))
        await RevokedToken.create(**payload.dict(exclude_unset=True))
    except IntegrityError:
        pass


async def token_get(token: str) -> RevokedToken | None:
    return await RevokedToken.get_or_none(token=token)
