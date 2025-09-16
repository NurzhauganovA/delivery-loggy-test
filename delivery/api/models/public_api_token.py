import uuid

import tortoise
from tortoise.exceptions import DoesNotExist

from .. import schemas

fields = tortoise.fields


class PublicApiTokenNotFound(Exception):
    """Raises if api token with provided ID not found."""


class PublicApiTokenAlreadyExists(Exception):
    """Raises if api token with provided token and partner id already
    exists."""


class PublicApiToken(tortoise.models.Model):
    id = fields.IntField(pk=True)
    token = fields.CharField(max_length=255)
    partner = fields.ForeignKeyField(
        'versions.Partner',
        to_field='id',
        on_delete=fields.CASCADE,
        unique=True,
    )
    created_at = fields.DatetimeField(auto_now_add=True)
    is_expires = fields.BooleanField(default=False)

    # type_hints
    partner_id: int

    class Config:
        extra = 'forbid'

    class Meta:
        table = 'partner.publicapitoken'


async def public_api_token_get(partner_id: int) -> schemas.PublicApiTokenGet:
    try:
        token = await PublicApiToken.get(partner_id=partner_id)
    except DoesNotExist:
        raise DoesNotExist(
            f'Api token with given partner_id: {partner_id} was not found',
        )
    return schemas.PublicApiTokenGet.from_orm(token)


async def public_api_token_create(
        partner_id: int,
) -> schemas.PublicApiTokenGet:
    token = await PublicApiToken.filter(partner_id=partner_id)
    if token:
        raise PublicApiTokenAlreadyExists(
            f'Api token with provided partner_id {partner_id} already exists!'
        )
    schema = {
        'partner_id': partner_id,
        'token': str(uuid.uuid4()).replace('-', ''),
    }
    api_token = await PublicApiToken.create(**schema)
    return schemas.PublicApiTokenGet.from_orm(api_token)