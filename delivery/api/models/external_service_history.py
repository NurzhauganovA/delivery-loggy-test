import tortoise.query_utils

from .. import enums
from .. import schemas
from .. import utils


fields = tortoise.fields


class ExternalServiceHistoryError(Exception):
    """
    Raises when there is an error with the ExternalServiceLogs model
    """


class ExternalServiceHistoryDoesNotExist(Exception):
    """
    Raises when an ExternalServiceLog does not exist
    """


class ExternalServiceHistory(tortoise.models.Model):
    id = fields.UUIDField(pk=True)
    service_name = fields.CharField(
        **enums.ExternalServices.to_kwargs(null=False),
        max_length=64,
    )
    url = fields.CharField(max_length=256, null=False)
    request_body = fields.JSONField(null=True)
    response_body = fields.JSONField(null=True)
    status_code = fields.IntField(null=False)
    owner = fields.ForeignKeyField(
        'versions.User',
        on_delete=fields.CASCADE,
        null=True
    )
    created_at = fields.DatetimeField(auto_now_add=True)

    class Config:
        extra = 'forbid'

    class Meta:
        table = 'external_service_history'
        ordering = ('-created_at',)

    def __str__(self):
        return ('URL: {}\n SERVICE NAME: {}\n STATUS CODE: {}\n '
                'REQ BODY: {}\n RES BODY: {}\n DATE: {}\n OWNER: {}').format(
            self.url,
            self.service_name,
            self.status_code,
            self.request_body or '',
            self.response_body or '',
            self.created_at,
            self.owner or '',
        )


async def external_service_history_create(
    create: schemas.ExternalServiceHistoryCreate,
):
    try:
        return await ExternalServiceHistory.create(**create.dict())
    except tortoise.exceptions.IntegrityError as e:
        raise ExternalServiceHistoryError(e)


@utils.as_dict(from_model=True)
async def external_service_history_get(
    service_name: enums.ExternalServices,
    status_code: int = None,
) -> ExternalServiceHistory:
    try:
        return await ExternalServiceHistory.get(
            service_name=service_name,
            status_code=status_code,
        )
    except tortoise.exceptions.DoesNotExist as e:
        raise ExternalServiceHistoryDoesNotExist(e)


async def external_service_history_get_list(**kwargs):
    try:
        return await ExternalServiceHistory.filter(**kwargs).all()
    except tortoise.exceptions.IntegrityError as e:
        raise ExternalServiceHistoryError(e)
