from fastapi import APIRouter, Depends, Query
from fastapi.encoders import jsonable_encoder
from starlette.responses import Response, JSONResponse
from .actions import *
from .schemas import *
from .dependencies import *

router = APIRouter()


@router.post(
    '/city',
    summary='Create city and return created object',
    response_description='city created',
    response_model=CityGet,
    status_code=201,
)
async def city_create(
    city: CityCreate,
    _: UserCurrent = Security(
        auth.get_current_user,
        scopes=['c:c'],
    ),
):
    """
    Create city with given payload.
    """
    actions = CityActions()
    result = await actions.city_create(
        city=city
    )

    return result


@router.get(
    '/city',
    summary='City list',
    response_description='City list',
    response_model=CityList,
    status_code=201,
)
async def city_list(
    default_filter_args: list = Depends(city_default_filter_args),
    filter_kwargs: dict = Depends(city_filter_kwargs),
    _: UserCurrent = Security(
        auth.get_current_user,
        scopes=['c:l'],
    ),
):
    """
    Get list of cities.
    """
    actions = CityActions()
    result = await actions.city_get_list(
        default_filter_args=default_filter_args,
        filter_kwargs=filter_kwargs,
    )

    return JSONResponse(jsonable_encoder(result))


@router.get(
    '/city/{city_id}',
    summary='City detail',
    response_description='City detail',
    response_model=CityGet,
    status_code=201,
)
async def city_get(
    city_id: int,
    default_filter_args: list = Depends(city_default_filter_args),
    _: UserCurrent = Security(
        auth.get_current_user,
        scopes=['c:g'],
    ),
):
    """
    Get city detail.
    """
    actions = CityActions()
    result = await actions.city_get(
        default_filter_args=default_filter_args,
        city_id=city_id,
    )

    return JSONResponse(jsonable_encoder(result))


@router.patch(
    '/city/{city_id}',
    summary='Partial update city with given ID',
    response_description='city partially updated',
    response_model=CityGet,
    status_code=200,
)
async def city_partial_update(
    city_id: int,
    update: CityPartialUpdate,
    _: UserCurrent = Security(
        auth.get_current_user,
        scopes=['c:u'],
    ),
    default_filter_args: list = Depends(
        city_default_filter_args
    ),
):
    """Partially update partner city with provided ID and return updated object.
    """
    actions = CityActions()
    result = await actions.city_update(
        city_id=city_id,
        update=update,
        default_filter_args=default_filter_args,
    )

    return result


@router.put(
    '/city/{city_id}',
    summary='Update city with given ID',
    response_description='city updated',
    response_model=CityGet,
    status_code=200,
)
async def city_update(
    city_id: int,
    update: CityUpdate,
    _: UserCurrent = Security(
        auth.get_current_user,
        scopes=['c:u'],
    ),
    default_filter_args: list = Depends(
        city_default_filter_args
    ),
):
    """Update partner city with provided ID and return updated object.
    """
    actions = CityActions()
    result = await actions.city_update(
        city_id=city_id,
        update=update,
        default_filter_args=default_filter_args,
    )

    return result


@router.delete(
    '/city/{city_id}',
    summary='Update city with given ID and return updated object',
    response_description='city updated',
    status_code=204,
)
async def city_delete(
    city_id: int,
    _: UserCurrent = Security(
        auth.get_current_user,
        scopes=['c:d'],
    ),
    default_filter_args: list = Depends(
        city_default_filter_args
    ),
) -> Response:
    """
    Update city with provided ID.
    """
    actions = CityActions()
    await actions.city_delete(
        city_id=city_id,
        default_filter_args=default_filter_args,
    )

    return Response(status_code=204)
