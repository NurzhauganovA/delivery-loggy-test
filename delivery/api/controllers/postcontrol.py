import typing

from api import exceptions
from .. import models


async def postcontrol_create(order_id: int, image, config_id, default_filter_args, current_user) -> dict:
    try:
        return await models.postcontrol_create(order_id, image, config_id, default_filter_args, current_user)
    except (
            models.OrderIsNotSubjectToPostControl,
            models.OrderPostControlMaximumNumberLimitExceeded,
            models.FileValidationError
    ) as e:
        raise exceptions.HTTPBadRequestException(e)


async def postcontrol_get_list(order_id: int, default_filter_args: list = None) -> typing.List[dict]:
    return await models.postcontrol_get_list(order_id=order_id, default_filter_args=default_filter_args)


async def postcontrol_get(postcontrol_id: int, default_filter_args: list = None) -> dict:
    return await models.postcontrol_get(postcontrol_id=postcontrol_id, default_filter_args=default_filter_args)


async def postcontrol_make_resolution(resolutions, default_filter_args, user) -> dict:
    try:
        return await models.postcontrol_make_resolution(
            resolutions=resolutions,
            default_filter_args=default_filter_args,
            user=user
        )
    except (
        models.PostControlIsNotSubjectToChange,
        models.CanNotCompleteOrder,
    ) as e:
        raise exceptions.HTTPBadRequestException(e)


async def postcontrol_accept(order_id: int, current_user, default_filter_args: list = None) -> dict:
    try:
        await models.postcontrol_accept(
            order_id=order_id,
            current_user=current_user,
            default_filter_args=default_filter_args,
        )
    except (
        models.PostControlIsNotSubjectToChange,
        models.CanNotCompleteOrder,
    ) as e:
        raise exceptions.HTTPBadRequestException(e)
    except (
            models.StatusAlreadyCurrent,
            models.StatusAfterError,
    ) as e:
        raise exceptions.HTTPBadRequestException(e)


async def postcontrol_decline(order_id: int, default_filter_args: list = None) -> dict:
    try:
        return await models.postcontrol_decline(
            order_id=order_id, default_filter_args=default_filter_args)
    except models.PostControlIsNotSubjectToChange as e:
        raise exceptions.HTTPBadRequestException(e)


async def postcontrol_delete(postcontrol_id: int, default_filter_args) -> None:
    try:
        await models.postcontrol_delete(postcontrol_id, default_filter_args=default_filter_args)
    except (
            models.PostControlCanNotDelete,
            models.PostControlIsNotSubjectToDelete,
    ) as e:
        raise exceptions.HTTPBadRequestException(e)
