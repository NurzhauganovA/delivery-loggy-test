import typing

import fastapi
from fastapi.encoders import jsonable_encoder
from starlette.responses import JSONResponse

from ... import auth
from ... import controllers
from ... import schemas


router = fastapi.APIRouter()


@router.get(
    '/country/{country_id}',
    summary='Get country',
    response_model=schemas.CountryGet,
    response_description='Country',
)
async def country_get(
    country_id: int,
    _: schemas.UserCurrent = fastapi.Security(auth.get_current_user),
):
    """Get country with provided ID."""
    result = await controllers.country_get(country_id)
    return JSONResponse(content=jsonable_encoder(result))


@router.get(
    '/country',
    summary='Get list of countries',
    response_model=typing.List[schemas.CountryGet],
    response_description='List of countries',
)
async def country_get_list(
    _: schemas.UserCurrent = fastapi.Security(auth.get_current_user),
):
    """Get list of countries."""
    result = await controllers.country_get_list()
    return JSONResponse(content=jsonable_encoder(result))


@router.post(
    '/country',
    summary='Create a country',
    response_model=schemas.CountryGet,
    response_description='Created country',
)
async def country_create(
    country: schemas.CountryCreate,
    _: schemas.UserCurrent = fastapi.Security(auth.get_current_user),
):
    """Create country.

    Returns 400 BAD REQUEST due to the following statuses:
    * `bad_request`: country already exists
    """
    result = await controllers.country_create(country)
    return JSONResponse(content=jsonable_encoder(result))


@router.put(
    '/country/{country_id}',
    summary='Update country',
    response_model=schemas.CountryGet,
    response_description='Updated country',
)
async def country_update(
    country_id: int,
    update: schemas.CountryUpdate,
    _: schemas.UserCurrent = fastapi.Security(auth.get_current_user),
):
    """Update country with provided ID.

    Returns 404 NOT FOUND due to the following statuses:
    * `not_found`: provided country not found
    """
    result = await controllers.country_update(country_id=country_id, update=update)
    return JSONResponse(content=jsonable_encoder(result))


@router.delete(
    '/country/{country_id}',
    summary='Delete country',
    response_description='Country deleted successfully',
    status_code=204,
)
async def country_delete(
        country_id: int,
        _: schemas.UserCurrent = fastapi.Security(auth.get_current_user),
):
    """Delete country with provided ID.

    Returns 404 NOT FOUND due to the following statuses:
    * `not_found`: provided country not found
    """
    await controllers.country_delete(country_id)
    return fastapi.responses.Response(status_code=204)
