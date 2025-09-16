import typing
import tortoise

from .. import exceptions
from .. import models
from .. import schemas
from .. import utils


fields = tortoise.fields


class InvitedUserEntityError(Exception):
    """Raises when error occurred with entity creation"""


class InvitedUserNotFound(Exception):
    """Raises when invited user is not found in db"""


class InvitedUser(tortoise.models.Model):
    phone_number = fields.CharField(max_length=13, pk=True, index=True)
    inviter = fields.ForeignKeyField(
        'versions.User',
        to_field='id',
        on_delete=fields.CASCADE,
    )
    created_at = fields.DatetimeField(auto_now_add=True)
    inviter_profile_type = fields.CharField(max_length=20, null=False, default='service_manager')

    class Meta:
        table = 'invited_user'
        ordering = ('-created_at',)


async def invited_user_create(schema: schemas.InvitedUserCreate,
                              **kwargs) -> InvitedUser:
    try:
        existing_record = await InvitedUser.filter(
            phone_number=schema.phone_number).first()
        if existing_record:
            await existing_record.delete()

        as_dict = schema.dict()

        created = await InvitedUser.create(**as_dict, **kwargs)
        return await models.invited_user_get(created.phone_number)
    except tortoise.exceptions.IntegrityError as e:
        raise InvitedUserEntityError(
            exceptions.get_exception_msg(e),
        )


async def invited_user_get(
    phone_number: str,
    as_dict: bool = True,
) -> typing.Union[dict, InvitedUser]:
    try:
        result = await InvitedUser.get(phone_number=phone_number)
        if as_dict:
            result = utils.as_dict(record=result)
            inviter = await models.user_get(with_history=False,
                                            id=result.pop('inviter_id'))

            result['inviter'] = {
                'id': inviter['id'],
                'name': f'{inviter["first_name"]} {inviter["last_name"]}',
                'profile_type': f'{result["inviter_profile_type"]}',
            }

    except tortoise.exceptions.DoesNotExist as e:
        raise InvitedUserNotFound(
            exceptions.get_exception_msg(e),
        )

    return result