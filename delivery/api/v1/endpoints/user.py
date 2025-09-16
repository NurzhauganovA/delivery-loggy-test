# TODO: Add `current_user` whole, password and phone number update endpoints
import typing

import fastapi
import pydantic
from fastapi.encoders import jsonable_encoder
from starlette.responses import JSONResponse

from ... import auth, security
from ... import controllers
from ... import enums
from ... import responses
from ... import schemas
from api.dependencies import validate_email_for_change

router = fastapi.APIRouter()


@router.get(
    '/user/me',
    # TODO: change it to `UserCurrentGet`
    summary='Get currently authenticated user',
    response_model=schemas.UserCurrent,
    response_description='Authenticated user',
)
async def user_get_current(
    with_profile: bool = False,
    current_user: schemas.UserCurrent = fastapi.Security(auth.get_current_user),
) -> dict:
    """Get currently authenticated user."""
    return await controllers.user_get_current(current_user, with_profile)


@router.get(
    '/user/list',
    summary='Get list of users',
    response_model=schemas.Page[schemas.UserGetMultipleProfile],
    response_description='List of users',
)
async def user_get_list(
    profile_type: enums.ProfileType,
    current_user: schemas.UserCurrent = fastapi.Security(auth.get_current_user),
    area_id: int = None,
    city_id: int = None,
    invite_status: enums.InviteStatus = None,
    search_type: enums.UserSearchType = None,
    search: str = None,
    pagination_params: schemas.Params = fastapi.Depends(schemas.Params),
):
    """Get list of users."""
    result = await controllers.user_get_list(
        pagination_params=pagination_params,
        profile_type=profile_type,
        area_id=area_id,
        current_user=current_user,
        invite_status=invite_status,
        city_id=city_id,
        search_type=search_type,
        search=search
    )
    return JSONResponse(jsonable_encoder(result))


@router.post(
    '/user/send_link',
    summary='Send registration link to user by sms'
)
async def user_send_link(
    body: schemas.SendLink,
    current_user: schemas.UserCurrent = fastapi.Security(auth.get_current_user),
) -> fastapi.responses.Response:
    await controllers.user_send_link(body, current_user)
    return fastapi.responses.Response(status_code=200)


@router.get(
    '/user',
    summary='Get user',
    response_model=schemas.UserGetMultipleProfile,
    response_description='User',
    responses=responses.generate_responses([responses.APIResponseNotFound]),
)
async def user_get_by_id(
    user_id: typing.Optional[int] = None,
    phone_number: typing.Optional[str] = None,
    current_user: schemas.UserCurrent = fastapi.Security(auth.get_current_user),
) -> dict:
    """Get user with provided ID.

    Returns 404 NOT FOUND due to the following statuses:
    * `not_found`: provided user not found
    """
    kwargs = {}
    if user_id:
        kwargs['id'] = user_id
    if phone_number:
        kwargs['phone_number'] = phone_number
    return await controllers.user_get(**kwargs, current_user=current_user)


@router.post(
    '/user',
    summary='Create user',
    response_model=schemas.UserGet,
    response_description='Created user',
    responses=responses.generate_responses([responses.APIResponseBadRequest]),
)
async def user_create_auto(
    request: fastapi.Request,
    user: schemas.UserCreate,
    current_user: schemas.UserCurrent = fastapi.Security(auth.get_current_user),
) -> dict:
    """Create user.

    Returns 400 BAD REQUEST due to the following statuses:
    * `bad_request`: user already exists
    """
    return await controllers.user_create(user=user, current_user_id=current_user.id)


@router.post(
    '/user_manually',
    summary='Create user manually',
    response_model=schemas.UserGet,
    response_description='Created user',
    responses=responses.generate_responses([responses.APIResponseBadRequest]),
)
async def user_create_manually(
    request: fastapi.Request,
    user: schemas.UserCreateManually,
    current_user: schemas.UserCurrent = fastapi.Security(auth.get_current_user),
) -> dict:
    """Create user.

    Returns 400 BAD REQUEST due to the following statuses:
    * `bad_request`: user already exists
    """
    return await controllers.user_create(user, current_user.id)


@router.put(
    '/user/change-email',
    summary='Send OTP code to given email',
    response_description='User update',
)
async def change_email(
    email: pydantic.EmailStr = fastapi.Depends(validate_email_for_change),
    current_user: schemas.UserCurrent = fastapi.Security(
        auth.get_current_user,
    ),
):
    await controllers.send_email_verification_code(user_id=current_user.id, email=email)
    return fastapi.responses.JSONResponse(
        status_code=201,
        content={
            'detail': 'Verification OTP is sent',
        },
    )


@router.put(
    '/user/verify-email',
    summary='Change user email with sending OTP code',
    response_description='User update',
)
async def verify_email(
    otp: typing.Annotated[str, fastapi.Body(embed=True)],
    current_user: schemas.UserCurrent = fastapi.Security(
        auth.get_current_user,
    ),
):

    await controllers.check_email_verification_code(current_user.id, otp)
    return fastapi.responses.JSONResponse(
        status_code=201,
        content={
            'detail': 'Email was edited!',
        },
    )


@router.put(
    '/user/set-password',
    status_code=200,
)
async def set_password(
    password: typing.Annotated[pydantic.constr(min_length=6, max_length=20), fastapi.Body(embed=True)],
    email: typing.Annotated[pydantic.EmailStr | None, fastapi.Body(embed=True)] = None,
    token: str = fastapi.Security(security.oauth2_scheme),
    current_user: schemas.UserCurrent = fastapi.Security(auth.get_current_user),
):
    """
    Sets new password for logged-in user.
    Sends verification email in case new email address given.
    """
    await controllers.user_set_password(user_id=current_user.id, email=email, password=password, token=token)


@router.put(
    '/user/{user_id}',
    summary='Update user',
    response_model=schemas.UserGet,
    response_description='Updated user',
    responses=responses.generate_responses([responses.APIResponseNotFound]),
)
async def user_update(
    user_id: int,
    user: schemas.UserUpdate,
    current_user: schemas.UserCurrent = fastapi.Security(auth.get_current_user),
) -> dict:
    """Update user with provided ID.

    Returns 404 NOT FOUND due to the following statuses:
    * `not_found`: provided user not found
    """
    return await controllers.user_update(user_id, user, current_user)


@router.delete(
    '/user/{user_id}',
    summary='Delete a user',
    response_description='User deleted successfully',
    responses=responses.generate_responses(
        [
            responses.APIResponseNotFound,
            responses.APIResponseNoContent,
        ],
    ),
    status_code=204,
)
async def user_delete(
    user_id: int,
    current_user: schemas.UserCurrent = fastapi.Security(auth.get_current_user),
) -> fastapi.responses.Response:
    """Delete user with provided ID.

    Returns 404 NOT FOUND due to the following statuses:
    * `not_found`: provided user not found
    """
    await controllers.user_delete(user_id, current_user)
    return fastapi.responses.Response(status_code=204)


@router.put(
    '/user/{user_id}/photo',
    summary='Change user photo',
    response_description='User\'s photo changed successfully',
    response_model=schemas.UserPhoto,
)
async def user_change_photo(
    user_id: int,
    photo: typing.Optional[fastapi.UploadFile] = fastapi.File(None),
    current_user: schemas.UserCurrent = fastapi.Security(auth.get_current_user),
) -> None:
    """
    Change user's photo. Deletes user's current photo if no photo was given.
    """
    return await controllers.user_change_photo(user_id, photo)


@router.put(
    '/user/{user_id}/add_permission',
    summary='Add permission to user',
    response_model=schemas.UserPermission,
    response_description='User update',
)
async def user_permission_add(
    user_id: int,
    permission_slug: str,
    current_user: schemas.UserCurrent = fastapi.Security(
        auth.get_current_user,
        scopes=['pm:ua'],
    ),
):
    return await controllers.user_permission_add(user_id, permission_slug)


@router.put(
    '/user/{user_id}/remove_permission',
    summary='Remove permission from user',
    response_model=schemas.UserPermission,
    response_description='User update',
)
async def user_permission_remove(
    user_id: int,
    permission_slug: str,
    current_user: schemas.UserCurrent = fastapi.Security(
        auth.get_current_user,
        scopes=['pm:ur'],
    ),
):
    return await controllers.user_permission_remove(user_id, permission_slug)
