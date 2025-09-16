import datetime
import typing

import fastapi
from fastapi.encoders import jsonable_encoder
from starlette.responses import JSONResponse

from ... import auth
from ... import controllers
from ... import dependencies
from ... import enums
from ... import responses
from ... import schemas
from ... import utils

router = fastapi.APIRouter()


@router.post(
    '/profile',
    summary='Create a user profile',
    response_model=schemas.ProfileGet,
    response_description='Created user profile',
    status_code=201,
)
async def profile_create(
    profile: schemas.ProfileCreate,
    current_user: schemas.UserCurrent = fastapi.Security(
        auth.get_current_user,
        scopes=['pf:c'],
    ),
) -> dict:
    """Create profile.

    Returns 400 BAD REQUEST due to the following statuses:
    * `bad_request`: profile already exists
    """
    return await controllers.profile_create(profile=profile, current_user=current_user)


@router.get(
    '/profile/list',
    summary='Get list of profile',
    response_model=utils.PaginationResponse[schemas.ProfileGet],
    response_description='Created user profile',
    responses=responses.generate_responses([responses.APIResponseBadRequest]),
)
async def profile_get_list(
    profile_type: enums.ProfileType = enums.ProfileType.COURIER,
    pagination_params: utils.PaginationParams = fastapi.Depends(utils.PaginationParams),
    city_id: typing.Optional[int] = None,
    is_identified: typing.Optional[bool] = None,
    is_biometry_identified: typing.Optional[bool] = None,
    user__is_active: typing.Optional[bool] = None,
    current_user: schemas.UserCurrent = fastapi.Security(
        auth.get_current_user,
        scopes=['pf:l'],
    ),
) -> list:
    """
    Get profile list.
    """
    return await controllers.profile_list(
        pagination_params,
        current_user=current_user,
        profile_type=profile_type,
        city_id=city_id,
        filter_kwargs={
            'is_biometry_identified': is_biometry_identified,
            'is_identified': is_identified,
            'user__is_active': user__is_active,
        },
    )


@router.put(
    '/profile',
    summary='Update own profile',
    response_model=schemas.ProfileGet,
    response_description='Updated user profile',
    responses=responses.generate_responses([responses.APIResponseNotFound]),
)
async def profile_own_update(
    update: schemas.ProfileUpdate,
    current_user: schemas.UserCurrent = fastapi.Security(
        auth.get_current_user,
    ),
) -> dict:
    """Update own profile with provided ID.

    Returns 404 NOT FOUND due to the following statuses:
    * `not_found`: provided profile not found
    """
    return await controllers.profile_own_update(
        update=update,
        current_user=current_user,
    )


@router.patch(
    '/profile',
    summary='Partial update own profile ',
    response_model=schemas.ProfileGet,
    response_description='Updated user profile',
    responses=responses.generate_responses([responses.APIResponseNotFound]),
)
async def profile_partial_own_update(
    update: schemas.ProfileUpdatePatch,
    current_user: schemas.UserCurrent = fastapi.Security(
        auth.get_current_user,
    ),
) -> dict:
    """Update profile with provided ID.

    Returns 404 NOT FOUND due to the following statuses:
    * `not_found`: provided profile not found
    """
    return await controllers.profile_own_update(
        update,
        is_patch=True,
        current_user=current_user,
    )


@router.get(
    '/profile/courier/list',
    response_model=schemas.CourierList,
)
async def courier_list(
    _: schemas.UserCurrent = fastapi.Security(auth.get_current_user),
    default_filter_args: list = fastapi.Depends(dependencies.get_courier_default_filter_args),
    filter_args: list = fastapi.Depends(dependencies.get_courier_filter_args),
):
    result = await controllers.courier_list(default_filter_args, filter_args=filter_args)
    return JSONResponse(jsonable_encoder(result))


@router.put(
    '/profile/courier/end-work',
    summary='Courier end work',
    status_code=200,
)
async def courier_end_work(
    current_user: schemas.UserCurrent = fastapi.Security(
        auth.get_current_user,
        scopes=['pf:ew'],
        ),
):
    await controllers.courier_end_work(current_user.id)


@router.put(
    '/profile/courier/start-work',
    summary='Courier start work',
    status_code=200,
)
async def courier_start_work(
    current_user: schemas.UserCurrent = fastapi.Security(
        auth.get_current_user,
        scopes=['pf:sw'],
        ),
):
    await controllers.courier_start_work(current_user.id)


@router.patch(
    '/profile/update_by_profile_id/{id}',
    summary='Partial update own profile ',
    response_model=schemas.ProfileGet,
    response_description='Updated user profile',
    responses=responses.generate_responses([responses.APIResponseNotFound]),
)
async def profile_partial_update_by_profile_id(
    profile_id: int,
    update: schemas.ProfileUpdatePatch,
    current_user: schemas.UserCurrent = fastapi.Security(
        auth.get_current_user,
    ),
) -> dict:
    """Update profile with provided ID.

    Returns 404 NOT FOUND due to the following statuses:
    * `not_found`: provided profile not found
    """
    return await controllers.profile_update_with_profile_type_and_id(
        profile_id=profile_id,
        update=update,
        current_user=current_user
    )


@router.put(
    '/profile/{user_id}',
    summary='Update a user profile',
    response_model=schemas.ProfileGet,
    response_description='Updated user profile',
    responses=responses.generate_responses([responses.APIResponseNotFound]),
)
async def profile_update(
    user_id: int,
    update: schemas.ProfileUpdate,
    current_user: schemas.UserCurrent = fastapi.Security(
        auth.get_current_user,
        scopes=['pf:u'],
    ),
) -> dict:
    """Update profile with provided ID.

    Returns 404 NOT FOUND due to the following statuses:
    * `not_found`: provided profile not found
    """
    return await controllers.profile_update(
        user_id=user_id,
        update=update,
        current_user=current_user,
    )


@router.patch(
    '/profile/{user_id}',
    summary='Partial update a user profile ',
    response_model=schemas.ProfileGet,
    response_description='Updated user profile',
    responses=responses.generate_responses([responses.APIResponseNotFound]),
)
async def profile_partial_update(
    user_id: int,
    update: schemas.ProfileUpdatePatch,
    current_user: schemas.UserCurrent = fastapi.Security(
        auth.get_current_user,
        scopes=['pf:u'],
    ),
) -> dict:
    """Update profile with provided ID.

    Returns 404 NOT FOUND due to the following statuses:
    * `not_found`: provided profile not found
    """
    return await controllers.profile_update(
        user_id, update,
        is_patch=True,
        current_user=current_user,
    )


@router.delete(
    '/profile/{user_id}',
    summary='Delete a user profile',
    response_description='User profile deleted successfully',
    responses=responses.generate_responses(
        [
            responses.APIResponseNotFound,
            responses.APIResponseNoContent,
        ],
    ),
    status_code=204,
)
async def profile_delete(
    user_id: int,
    delete: schemas.ProfileDelete,
    current_user: schemas.UserCurrent = fastapi.Security(
        auth.get_current_user,
        scopes=['pf:d'],
    ),
) -> fastapi.responses.Response:
    """Delete profile with provided ID.

    Returns 404 NOT FOUND due to the following statuses:
    * `not_found`: provided profile not found
    """
    await controllers.profile_delete(user_id, delete, current_user)
    return fastapi.responses.Response(status_code=204)


@router.patch(
    '/profile/{user_id}/update/status',
    summary='Update courier profile status',
    response_model=schemas.ProfileGet,
    response_description='Update courier profile status',
    responses=responses.generate_responses([
        responses.APIResponseNotFound,
        responses.APIResponseNoContent,
    ], ),
)
async def profile_status_update(
    user_id: int,
    update: schemas.ProfileStatusUpdate,
    current_user: schemas.UserCurrent = fastapi.Security(auth.get_current_user),
) -> dict:
    """Update status courier profile with provided ID.

    Returns 404 NOT FOUND due to the following statuses:
    * `not_found`: provided profile not found
    """
    return await controllers.profile_status_update(
        user_id, update, current_user
    )

# TODO: Пока что закомментил, так как для безопасности требуется закрыть
# @router.patch(
#     '/profile/{user_id}/courier/update/status',
#     summary='Update courier profile status to refuse',
#     response_model=schemas.ProfileStatusUpdate,
#     response_description='Update courier profile status refuse',
#     responses=responses.generate_responses([
#         responses.APIResponseNotFound,
#         responses.APIResponseNoContent,
#     ], ),
# )
# async def profile_status_update_by_courier(
#     user_id: int,
#     update: schemas.ProfileStatusUpdate,
# ) -> dict:
#     """Update status courier profile with provided ID.
#
#     Returns 404 NOT FOUND due to the following statuses:
#     * `not_found`: provided profile not found
#     """
#     return await controllers.profile_status_update_by_courier(
#         user_id, update
#     )


@router.get(
    '/profile/courier-stats',
    summary='Get stats data of all couriers in service',
    response_model=typing.List[schemas.ProfileCourierStatsList],
)
async def courier_stats(
    date: datetime.date = None,
    current_user: schemas.UserCurrent = fastapi.Security(auth.get_current_user),
):
    return await controllers.courier_stats(
        partner_id=current_user.partners[0],
        date=date,
    )


@router.get(
    '/profile/courier-stats/{user_id}',
    summary='Get stats data of courier with given user_id',
    response_model=schemas.ProfileCourierStats,
)
async def courier_stats_get(
    user_id: int,
    date: datetime.date = None,
    current_user: schemas.UserCurrent = fastapi.Security(auth.get_current_user),
):
    return await controllers.courier_stats_get(
        user_id=user_id,
        partner_id=current_user.partners[0],
        date=date,
    )


@router.post(
    '/profile/{profile_type}/{profile_id}/send-magic-link',
    summary='Send magic link to user',
    status_code=200,
)
async def profile_send_magic_link(
    profile_type: enums.ProfileType,
    profile_id: int,
    inviter: schemas.UserCurrent = fastapi.Security(
        auth.get_current_user,
        scopes=['pf:c'],
    ),
):
    return await controllers.profile_send_magic_link(inviter.id, profile_type, profile_id)