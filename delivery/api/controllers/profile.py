import typing

from .websocket_managers import websocket_manager
from .. import enums
from .. import exceptions
from .. import models
from .. import schemas


async def profile_create(
    profile: schemas.ProfileCreate,
    **kwargs,
) -> dict:
    current_user = kwargs.pop('current_user')
    try:
        partner_id = profile.profile_content.partner_id
        if partner_id not in current_user.partners:
            raise exceptions.HTTPBadRequestException(
                f'Partner with given ID: {partner_id} was not found',
            )
        profile = await models.new_profile_create(
            profile=profile, inviter_id=current_user.id, current_user=current_user)
        return profile
    except (
        models.ProfileAlreadyExists,
        models.UserNotFound,
        models.UserAlreadyExists,
    ) as e:
        raise exceptions.HTTPBadRequestException(str(e)) from e


async def profile_list(
    pagination_params,
    current_user,
    **kwargs,
) -> list:
    kwargs['filter_kwargs']['partner__id__in'] = current_user.partners
    return await models.profile_get_list(
        pagination_params,
        **kwargs,
    )


async def profile_update(
    user_id: int,
    update: typing.Union[
        schemas.ProfileUpdate,
        schemas.ProfileUpdatePatch],
    current_user,
    is_patch: bool = False,
) -> dict:
    try:
        if partner_id := update.profile_content.partner_id:
            if partner_id not in current_user.partners:
                raise exceptions.HTTPNotFoundException(
                    f'Partner with given ID: {partner_id} was not found',
                )
        profile = await models.profile_update_by_user_id(
            user_id, update, is_patch,
            partner__id__in=current_user.partners,
        )

        return profile
    except (
        models.ProfileNotFound,
        models.PartnerNotFound,
    ) as e:
        raise exceptions.HTTPNotFoundException(str(e)) from e


async def profile_update_with_profile_type_and_id(
    profile_id: int,
    update: typing.Union[
        schemas.ProfileUpdate,
        schemas.ProfileUpdatePatch],
    current_user,
) -> dict:
    try:
        if partner_id := update.profile_content.partner_id:
            if partner_id not in current_user.partners:
                raise exceptions.HTTPNotFoundException(
                    f'Partner with given ID: {partner_id} was not found',
                )
        profile = await models.profile_update_by_profile_id(
            update=update, profile_id=profile_id
        )

        return profile
    except (
        models.ProfileNotFound,
        models.PartnerNotFound,
    ) as e:
        raise exceptions.HTTPNotFoundException(str(e)) from e


async def profile_status_update(
    user_id: int,
    update: schemas.ProfileStatusUpdate,
    current_user,
) -> dict:
    try:
        if current_user.profile['profile_type'] == enums.ProfileType.COURIER:
            if update.status in [
                enums.InviteStatus.REFUSED.value,
                enums.InviteStatus.PENDING.value
            ]:
                profile = await models.profile_status_update(
                    user_id, update,
                )
            else:
                raise exceptions.HTTPUnauthorizedException(
                    'You can only change the possible statuses: pending or refused'
                )
        else:
            profile = await models.profile_status_update(
                user_id, update,
            )

        profile_content = profile.get('profile_content')
        if profile_content:
            await websocket_manager.send_message_for_managers(
                profile_content.get('partner_id'), {
                'type': enums.MessageType.COURIER_PROFILE_STATUS_UPDATE.value,
                'data': {
                    'profile': str(current_user.id),
                    'status': update.status
                }
            })

        return profile
    except (
        models.ProfileNotFound,
    ) as e:
        raise exceptions.HTTPNotFoundException(str(e)) from e
    pass


async def profile_status_update_by_courier(
    user_id: int,
    update: typing.Union[schemas.ProfileStatusUpdate],
) -> dict:
    try:
        if update.status in [
            enums.InviteStatus.REFUSED.value,
            enums.InviteStatus.PENDING.value
        ]:
            profile = await models.profile_status_update(
                user_id, update,
            )

            profile_content = profile.get('profile_content')
            if profile_content:
                await websocket_manager.send_message_for_managers(
                    profile_content.get('partner_id'), {
                        'type': enums.MessageType.COURIER_PROFILE_STATUS_UPDATE.value,
                        'data': {
                            'profile': str(user_id),
                            'status': update.status
                        }
                    })
            return profile
        else:
            raise exceptions.HTTPUnauthorizedException
    except (
        models.ProfileNotFound,
    ) as e:
        raise exceptions.HTTPNotFoundException(str(e)) from e
    except (
        models.StatusAlreadySet,
    ) as e:
        raise exceptions.HTTPBadRequestException(str(e)) from e
    pass


async def profile_own_update(
    update: typing.Union[
        schemas.ProfileUpdate, schemas.ProfileUpdatePatch],
    current_user: schemas.UserCurrent,
    is_patch: bool = False,
) -> dict:
    try:
        if partner_id := update.profile_content.partner_id:
            if partner_id not in current_user.partners:
                raise exceptions.HTTPNotFoundException(
                    f'Partner with given ID: {partner_id} was not found',
                )
        profile = await models.profile_update_by_user_id(
            user_id=current_user.id,
            update=update,
            is_patch=is_patch,
            partner__id__in=current_user.partners,
        )

        return profile
    except (
        models.ProfileNotFound,
        models.PartnerNotFound,
    ) as e:
        raise exceptions.HTTPNotFoundException(str(e)) from e


async def profile_delete(
    user_id: int, delete: schemas.ProfileDelete, current_user) -> None:
    try:
        profile = await models.profile_get(
            user_id=user_id, skip_dependency=True)
        if profile[
            'profile_content'
        ]['partner_id'] not in current_user.partners:
            raise exceptions.HTTPNotFoundException(
                f'User with given ID: {user_id} was not found',
            )
        return await models.profile_delete(user_id, delete)
    except models.ProfileNotFound as e:
        raise exceptions.HTTPNotFoundException(str(e)) from e


async def courier_list(default_filter_args, filter_args):
    return await models.courier_list(default_filter_args, filter_args)


async def courier_stats(partner_id: int, date):
    return await models.courier_stats(partner_id=partner_id, date=date)


async def courier_stats_get(user_id: int, date, partner_id: int):
    try:
        return await models.courier_stats_get(
            user_id=user_id,
            partner_id=partner_id,
            date=date,
        )
    except models.ProfileNotFound as e:
        raise exceptions.HTTPNotFoundException(str(e))


async def courier_start_work(user_id):
    return await models.courier_start_work(user_id)


async def courier_end_work(user_id):
    return await models.courier_start_work(user_id)


async def profile_send_magic_link(inviter_id, profile_type, profile_id):
    return await models.profile_send_magic_link(inviter_id, profile_type, profile_id)