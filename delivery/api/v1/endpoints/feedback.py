import typing

import fastapi
from fastapi.encoders import jsonable_encoder
from starlette.responses import JSONResponse

from ... import auth
from ... import controllers
from ... import enums
from ... import schemas

router = fastapi.APIRouter()


@router.get(
    '/feedbacks',
    summary='Get list of feedbacks',
    response_model=schemas.Page[schemas.FeedbackList],
    response_description='List of feedbacks',
)
async def feedback_get_list(
    courier_id: int = None,
    status: enums.FeedbackStatus = None,
    params: schemas.Params = fastapi.Depends(schemas.Params),
    current_user: schemas.UserCurrent = fastapi.Security(
        auth.get_current_user,
        scopes=['f:l'],
    ),
):
    """Get list of feedbacks."""
    kwargs = {
        'order__partner_id__in': current_user.partners,
        'params': params,
    }
    if status:
        kwargs['status'] = status
    if courier_id:
        kwargs['order__courier_id'] = courier_id
    result = await controllers.feedback_get_list(**kwargs)
    return JSONResponse(jsonable_encoder(result))


@router.post(
    '/feedbacks/create/manager',
    summary='Create feedback by manager',
    response_model=schemas.FeedbackGet,
    response_description='Create feedback by manager',
)
async def feedback_create_manager(
    feedback: schemas.FeedbackCreateManager,
    current_user: schemas.UserCurrent = fastapi.Security(
        auth.get_current_user,
        scopes=['f:cm'],
    ),
):
    """Create feedback by manager."""
    fullname = f'{current_user.last_name or ""} ' \
               f'{current_user.first_name or ""} ' \
               f'{current_user.middle_name or ""}'
    kwargs = {
        'author_full_name': fullname.strip(),
        'author_phone': current_user.phone_number,
        'author_role': enums.AuthorsFeedback.MANAGER,
        'partner_id__in': current_user.partners,
    }
    result = await controllers.feedback_create_by_manager(feedback, **kwargs)
    return JSONResponse(jsonable_encoder(result))


@router.post(
    '/feedbacks/create/receiver',
    summary='Create feedback by receiver',
    response_model=schemas.FeedbackGet,
    response_description='Create feedback by receiver',
)
async def feedback_create_receiver(
    feedback: schemas.FeedbackCreateReceiver,
    _: None = fastapi.Security(auth.simple_auth),
):
    """Create feedback by receiver."""
    kwargs = {'author_role': enums.AuthorsFeedback.RECEIVER}
    result = await controllers.feedback_create_by_receiver(feedback, **kwargs)
    return JSONResponse(jsonable_encoder(result))


@router.put(
    '/feedbacks/{feedback_id}/update/status',
    summary='Update feedback status',
    response_model=schemas.FeedbackGet,
    response_description='Update feedback status',
)
async def feedback_update_status(
    feedback_id: int,
    update: schemas.FeedbackUpdateStatus,
    current_user: schemas.UserCurrent = fastapi.Security(
        auth.get_current_user,
        scopes=['f:u'],
    ),
) -> dict:
    """Update feedback status."""
    return await controllers.feedback_update_status(
        feedback_id=feedback_id,
        update=update,
        order__partner_id__in=current_user.partners,
    )


@router.delete(
    '/feedbacks/{feedback_id}',
    summary='Delete feedback',
    response_description='Feedback deleted successfully',
    status_code=204,
)
async def feedback_delete(
    feedback_id: int,
    current_user: schemas.UserCurrent = fastapi.Security(
        auth.get_current_user,
        scopes=['f:d'],
    ),
):
    """Delete feedback with provided ID.

    Returns 404 NOT FOUND due to the following statuses:
    * `not_found`: provided feedback not found
    """
    await controllers.feedback_delete(
        feedback_id=feedback_id,
        order__partner_id__in=current_user.partners,
    )
    return fastapi.responses.Response(status_code=204)


@router.get(
    '/feedbacks/{feedback_id}',
    summary='Get Feedback object by given ID',
    response_model=schemas.FeedbackGet,
    response_description='Detail view of feedback',
)
async def feedback_get(
    feedback_id: int,
    current_user: schemas.UserCurrent = fastapi.Security(auth.get_current_user),
):
    kwargs = {'id': feedback_id, 'order__partner_id__in': current_user.partners}
    result = await controllers.feedback_get(**kwargs)
    return JSONResponse(jsonable_encoder(result))


@router.get(
    '/feedback_reasons/{partner_id}',
    summary='Get list of feedback reasons',
    response_model=typing.List[schemas.FeedbackReasonGet],
    response_description='List of feedback reasons',
)
async def feedback_reason_get_list(
    partner_id: int,
    rate: int = None,
    _: None = fastapi.Security(auth.simple_auth),
):
    """Get list of feedback reasons."""
    kwargs = {'partner_id': partner_id}
    if rate:
        kwargs['rate'] = rate
    result = await controllers.feedback_reason_get_list(**kwargs)
    return JSONResponse(jsonable_encoder(result))


@router.post(
    '/feedback_reason',
    summary='Create feedback reason',
    response_model=schemas.FeedbackReasonGet,
    response_description='Create feedback reason',
)
async def feedback_reason_create(
    feedback_reason: schemas.FeedbackReasonCreate,
    current_user: schemas.UserCurrent = fastapi.Security(
        auth.get_current_user,
        scopes=['fr:c'],
    ),
):
    """Create feedback reason."""
    result = await controllers.feedback_reason_create(
        feedback_reason=feedback_reason,
        partner_id=current_user.partners[0],
    )
    return JSONResponse(jsonable_encoder(result))


@router.put(
    '/feedback_reason/{reason_id}',
    summary='Update feedback reason with given ID',
    response_model=schemas.FeedbackReasonGet,
    response_description='Update feedback reason',
)
async def feedback_reason_update(
    reason_id: int,
    update: schemas.FeedbackReasonUpdate,
    current_user: schemas.UserCurrent = fastapi.Security(
        auth.get_current_user,
        scopes=['fr:u'],
    ),
):
    """Update feedback reason."""
    result = await controllers.feedback_reason_update(
        reason_id=reason_id,
        update=update,
        partner_id=current_user.partners[0],
    )
    return JSONResponse(jsonable_encoder(result))


@router.delete(
    '/feedback_reasons/{feedback_reason_id}',
    summary='Delete feedback reason',
    response_description='Feedback reason deleted successfully',
    status_code=204,
)
async def feedback_reason_delete(
    feedback_reason_id: int,
    current_user: schemas.UserCurrent = fastapi.Security(
        auth.get_current_user,
        scopes=['fr:d'],
    ),
):
    """Delete feedback reasons with provided ID.

    Returns 404 NOT FOUND due to the following statuses:
    * `not_found`: provided feedback reason not found
    """
    await controllers.feedback_reason_delete(feedback_reason_id, partner_id=current_user.partners[0])
    return fastapi.responses.Response(status_code=204)
