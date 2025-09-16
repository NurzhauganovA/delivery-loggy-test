import typing

import fastapi
from fastapi.encoders import jsonable_encoder
from starlette.responses import JSONResponse

from ... import auth
from ... import controllers
from ... import schemas


router = fastapi.APIRouter()


@router.get(
    '/category',
    summary='Get list of categories',
    response_model=typing.List[schemas.CategoryGet],
    response_description='List categories',
)
async def category_get_list(
    current_user: schemas.UserCurrent = fastapi.Security(
        auth.get_current_user,
        scopes=['ca:l'],
    ),
):
    """Get list of categories."""
    kwargs = {'partner_id': current_user.partners[0]}

    result = await controllers.category_get_list(**kwargs)
    return JSONResponse(jsonable_encoder(result))


@router.get(
    '/category/{category_id}',
    summary='Get category',
    response_model=schemas.CategoryGet,
    response_description='Category',
)
async def category_get(
    category_id: int,
    current_user: schemas.UserCurrent = fastapi.Security(
        auth.get_current_user,
        scopes=['ca:g'],
    ),
):
    """Get Category with provided ID.

    Returns 404 NOT FOUND due to the following statuses:
    * `not_found`: provided category not found
    """
    kwargs = {
        'partner_id': current_user.partners[0],
    }
    result = await controllers.category_get(category_id=category_id, **kwargs)
    return JSONResponse(jsonable_encoder(result))


@router.post(
    '/category',
    summary='Create category',
    response_model=schemas.CategoryGet,
    response_description='Created category',
)
async def category_create(
    category: schemas.CategoryCreate,
    current_user: schemas.UserCurrent = fastapi.Security(
        auth.get_current_user,
        scopes=['ca:c'],
    ),
):
    """Create category.

    Returns 400 BAD REQUEST due to the following statuses:
    * `bad_request`: entity does not exist
    """
    kwargs = {'partner_id': current_user.partners[0]}
    result = await controllers.category_create(
        category=category,
        **kwargs,
    )
    return JSONResponse(jsonable_encoder(result))


@router.put(
    '/category/{category_id}',
    summary='Update category',
    response_model=schemas.CategoryGet,
    response_description='Update category',
)
async def category_update(
    category_id: int,
    update: schemas.CategoryUpdate,
    _: schemas.UserCurrent = fastapi.Security(auth.get_current_user),
):
    """Update with provided ID.

    Returns 400 BAD REQUEST due to the following statuses:
    * `bad_request`: entity does not exist

    Returns 404 NOT FOUND due to the following statuses:
    * `not_found`: provided category not found
    """
    result = await controllers.category_update(category_id, update)
    return JSONResponse(jsonable_encoder(result))


@router.delete(
    '/category/delete_many',
    summary='Delete many categories',
    response_description='List of categories deleted successfully',
    status_code=204,
)
async def category_delete_many(
    category_ids: schemas.CategoryIds,
    _: schemas.UserCurrent = fastapi.Security(auth.get_current_user),
) -> fastapi.responses.Response:
    """Delete list of categories by provided IDs.

    Returns 404 NOT FOUND due to the following statuses:
    * `not_found`: provided category not found
    """
    await controllers.category_delete_bulk(category_ids)
    return fastapi.responses.Response(status_code=204)


@router.delete(
    '/category/{category_id}',
    summary='Delete category',
    response_description='Category deleted successfully',
    status_code=204,
)
async def category_delete(
    category_id: int,
    _: schemas.UserCurrent = fastapi.Security(auth.get_current_user),
):
    """Delete with provided ID.

    Returns 404 NOT FOUND due to the following statuses:
    * `not_found`: provided category not found
    """
    await controllers.category_delete(category_id)
    return fastapi.responses.Response(status_code=204)
