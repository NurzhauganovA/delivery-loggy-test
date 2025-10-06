import typing

import fastapi
from fastapi import UploadFile, File
from fastapi.encoders import jsonable_encoder
from starlette.responses import JSONResponse

from ... import auth
from ... import enums
from ... import dependencies
from ... import models
from ... import controllers
from ... import responses
from ... import schemas
from ...enums import ProfileType


router = fastapi.APIRouter()


@router.post(
    '/post-control/{order_id}',
    summary='Create a post control document',
    response_model=schemas.PostControlGet,
    response_description='Created post control document',
)
async def postcontrol_create(
    order_id: int,
    config_id: int = fastapi.Depends(dependencies.postcontrol_validate_payload),
    image: fastapi.UploadFile = fastapi.File(...),
    current_user: schemas.UserCurrent = fastapi.Security(
        auth.get_current_user,
    ),
    default_filter_args: list = fastapi.Security(dependencies.OrderDefaultFilter()),
):
    """Create post-control document."""
    result = await controllers.postcontrol_create(
        order_id=order_id,
        image=image,
        config_id=config_id,
        default_filter_args=default_filter_args,
        current_user=current_user,
    )
    return JSONResponse(jsonable_encoder(result))


@router.delete(
    '/post-control/{postcontrol_id}',
    summary='Delete post control document with given id',
)
async def postcontrol_delete(
    postcontrol_id: int,
    _: schemas.UserCurrent = fastapi.Security(
        auth.get_current_user,
    ),
    default_filter_args: list = fastapi.Security(dependencies.OrderDefaultFilter(prefix='order__'))
) -> fastapi.Response:
    await controllers.postcontrol_delete(
        postcontrol_id=postcontrol_id,
        default_filter_args=default_filter_args,
    )
    return fastapi.Response(status_code=204)


@router.get(
    '/post-control/{postcontrol_id}',
    summary='Get postcontrol object with given id',
    response_model=schemas.PostControlGet,
    responses=responses.generate_responses([responses.APIResponseNotFound]),
)
async def postcontrol_get(
    postcontrol_id: int,
    current_user: schemas.UserCurrent = fastapi.Security(
        auth.get_current_user,
        scopes=['pc:g'],
    ),
    default_filter_args: list = fastapi.Security(dependencies.OrderDefaultFilter(prefix='order__')),
) -> dict:
    return await controllers.postcontrol_get(
        postcontrol_id=postcontrol_id,
        default_filter_args=default_filter_args,
    )


@router.put(
    '/post-control/make-resolution',
    summary='Make resolution to postcontrol objects with given ids',
)
async def postcontrol_make_resolution(
    resolutions: typing.Annotated[typing.List[schemas.PostControlMakeResolution], fastapi.Depends(
        dependencies.postcontrol_make_resolution_payload,
    )] = fastapi.Body(embed=False),
    default_filter_args: list = fastapi.Depends(dependencies.OrderDefaultFilter(prefix='order__')),
    user: schemas.UserCurrent = fastapi.Security(
        auth.get_current_user,
        scopes=['pc:u'],
    ),
):
    result = await controllers.postcontrol_make_resolution(
        resolutions=resolutions,
        default_filter_args=default_filter_args,
        user=user,
    )

    return JSONResponse(jsonable_encoder(result))


@router.put(
    '/post-control/{order_id}/accept',
    summary='Accept all post control documents of order with given id',
)
async def postcontrol_accept(
    order_id: int = fastapi.Depends(dependencies.check_order_can_make_resolution),
    current_user: schemas.UserCurrent = fastapi.Security(
        auth.get_current_user,
        scopes=['pc:u'],
    ),
    default_filter_args: list = fastapi.Security(dependencies.OrderDefaultFilter()),
):
    await controllers.postcontrol_accept(
        order_id=order_id,
        current_user=current_user,
        default_filter_args=default_filter_args,
    )

    return fastapi.responses.Response(status_code=204)


@router.put(
    '/post-control/{order_id}/decline',
    summary='Decline all post control documents of order with given id',
)
async def postcontrol_decline(
    order_id: int = fastapi.Depends(dependencies.check_order_can_make_resolution),
    current_user: schemas.UserCurrent = fastapi.Security(
        auth.get_current_user,
        scopes=['pc:u'],
    ),
    default_filter_args: list = fastapi.Security(dependencies.OrderDefaultFilter()),
):
    await controllers.postcontrol_decline(
        order_id=order_id,
        default_filter_args=default_filter_args,
    )
    history_schema = schemas.HistoryCreate(
        initiator_type=enums.InitiatorType.USER,
        initiator_id=current_user.id,
        initiator_role=current_user.profile.get('profile_type'),
        request_method=enums.RequestMethods.PUT,
        model_type=enums.HistoryModelName.ORDER.value,
        model_id=order_id,
        action_data={'post-control': enums.PostControlResolution.DECLINED}
    )
    await models.history_create(history_schema)
    return fastapi.responses.Response(status_code=204)


@router.get(
    '/post-control/{order_id}/list',
    summary='Get list of post control documents by given order id, '
            'returns empty list if no records found',
    response_model=typing.List[schemas.PostControlGet],
    response_description='Fetched post control documents.'
)
async def postcontrol_get_list(
    order_id: int,
    current_user: schemas.UserCurrent = fastapi.Security(auth.get_current_user),
    default_filter_args: list = fastapi.Security(dependencies.OrderDefaultFilter(prefix='order__')),
) -> typing.List[dict]:
    return await controllers.postcontrol_get_list(
        order_id=order_id,
        default_filter_args=default_filter_args,
    )
