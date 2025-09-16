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

router = fastapi.APIRouter()


@router.get(
    '/area/list',
    summary='Get list of areas',
    response_model=typing.List[schemas.AreaGet],
    response_description='List of areas',
)
async def area_get_list(
    filter_kwargs: schemas.AreaFilter = fastapi.Depends(schemas.AreaFilter),
    _: schemas.UserCurrent = fastapi.Security(
        auth.get_current_user,
        scopes=['a:l'],
    ),
    default_filter_args: list = fastapi.Depends(dependencies.area_get_default_filter_args),
):
    """Get list of areas."""
    result = await controllers.area_get_list(
        default_filter_args=default_filter_args,
        filter_kwargs=filter_kwargs.dict(exclude_unset=True, exclude_none=True),
    )

    return JSONResponse(jsonable_encoder(result))


@router.get(
    '/area/{area_id}',
    summary='Get area',
    response_model=schemas.AreaGet,
    response_description='Area',
)
async def area_get(
    area_id: int,
    _: schemas.UserCurrent = fastapi.Security(
        auth.get_current_user,
        scopes=['a:g'],
    ),
    default_filter_args: list = fastapi.Security(dependencies.area_get_default_filter_args),
):
    """Get area with provided ID."""
    result = await controllers.area_get(
        area_id=area_id,
        default_filter_args=default_filter_args,
    )

    return JSONResponse(jsonable_encoder(result))


@router.post(
    '/area',
    summary='Create area',
    response_model=schemas.AreaGet,
    response_description='Created area',
    responses=responses.generate_responses([responses.APIResponseNotFound]),
)
async def area_create(
    _: schemas.UserCurrent = fastapi.Security(
        auth.get_current_user,
        scopes=['a:c'],
    ),
    area: schemas.AreaCreate = fastapi.Depends(dependencies.area_validate_payload),
):
    """Create area.

    Returns 404 NOT FOUND due to the following statuses:
    * `not_found`: provided area does not exist
    """
    result = await controllers.area_create(area)

    return JSONResponse(jsonable_encoder(result))


@router.put(
    '/area/{area_id}',
    summary='Update area',
    response_model=schemas.AreaGet,
    response_description='Updated area',
    responses=responses.generate_responses([responses.APIResponseNotFound]),
)
async def area_update(
    area_id: int,
    area: schemas.AreaUpdate = fastapi.Depends(dependencies.area_validate_payload),
    _: schemas.UserCurrent = fastapi.Security(
        auth.get_current_user,
        scopes=['a:u'],
    ),
    default_filter_args: list = fastapi.Security(dependencies.area_get_default_filter_args),
):
    """Update Area with provided ID.

    Returns 404 NOT FOUND due to the following statuses:
    * `not_found`: provided area not found
    """

    result = await controllers.area_update(area_id, area, default_filter_args)

    return JSONResponse(jsonable_encoder(result))


@router.delete(
    '/area/{area_id}',
    summary='Delete area',
    response_description='Area deleted successfully',
    status_code=204,
)
async def area_delete(
    area_id: int,
    _: schemas.UserCurrent = fastapi.Security(
        auth.get_current_user,
        scopes=['a:d'],
    ),
    default_filter_args: list = fastapi.Security(dependencies.area_get_default_filter_args),
):
    """Delete area with provided ID.

    Returns 404 NOT FOUND due to the following statuses:
    * `not_found`: provided area not found
    """
    await controllers.area_delete(
        area_id=area_id,
        default_filter_args=default_filter_args,
    )

    return fastapi.responses.Response(status_code=204)


@router.put(
    '/area/{area_id}/activate',
    status_code=200,
)
async def area_activate(
    area_id: int,
    _: schemas.UserCurrent = fastapi.Security(auth.get_current_user),
    default_filter_args: list = fastapi.Security(dependencies.area_get_default_filter_args),
):

    await controllers.area_activate(area_id=area_id, default_filter_args=default_filter_args)

    return fastapi.responses.Response()


@router.put(
    '/area/{area_id}/archive',
    status_code=200,
)
async def area_archive(
    area_id: int,
    _: schemas.UserCurrent = fastapi.Security(auth.get_current_user),
    default_filter_args: list = fastapi.Security(dependencies.area_get_default_filter_args),
):
    await controllers.area_archive(area_id=area_id, default_filter_args=default_filter_args)

    return fastapi.responses.Response()
