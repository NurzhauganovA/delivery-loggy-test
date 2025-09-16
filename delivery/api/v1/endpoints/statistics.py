from typing import List

import fastapi

from ... import dependencies
from fastapi.encoders import jsonable_encoder
from starlette.responses import JSONResponse

from ... import auth
from ... import controllers
from ... import schemas
from ...enums import ProgressInterval

router = fastapi.APIRouter()


@router.get(
    '/statistics',
    summary='Get dashboard data',
    response_model=schemas.StatisticsBase,
    response_description='Dashboard',
)
async def statistics_get(
    filter_args: list = fastapi.Depends(dependencies.statistics_filter_args),
    default_filter_args: list = fastapi.Depends(
        dependencies.courier_statistics_default_filter_args,
    ),
    _: schemas.UserCurrent = fastapi.Security(
        auth.get_current_user,
        scopes=['s:g'],
    ),
):
    """Get dashboard data"""
    result = await controllers.statistics_get(
        filter_params=filter_args,
        default_filter_args=default_filter_args,
    )
    return JSONResponse(jsonable_encoder(result))


@router.get(
    '/statistics-by-date',
    summary='Get order statistics by datetime',
    response_description='Dashboard',
)
async def statistics_get_by_date(
    filter_args: list = fastapi.Depends(dependencies.statistics_filter_args),
    default_filter_args: list = fastapi.Depends(
        dependencies.courier_statistics_default_filter_args,
    ),
    _: schemas.UserCurrent = fastapi.Security(
        auth.get_current_user,
        scopes=['s:g'],
    ),
):
    """Get order statistics by datetime"""
    result = await controllers.statistics_get_by_date(
        filter_params=filter_args,
        default_filter_args=default_filter_args
    )
    return JSONResponse(jsonable_encoder(result))


@router.get(
    '/statistics-by-hour',
    summary='Get order statistics by hour',
    response_description='Dashboard',
)
async def statistics_get_by_hour(
    filter_args: list = fastapi.Depends(dependencies.statistics_filter_args),
    _: schemas.UserCurrent = fastapi.Security(
        auth.get_current_user,
        scopes=['s:g'],
    ),
    default_filter_args: list = fastapi.Depends(
        dependencies.courier_statistics_default_filter_args,
    ),
):
    """Get order statistics by hour"""
    result = await controllers.statistics_get_by_hour(
        filter_params=filter_args,
        default_filter_args=default_filter_args
    )
    return JSONResponse(jsonable_encoder(result))


@router.get(
    '/heatmap-by-date',
    summary='Get dashboard data by datetime filter',
    response_description='Dashboard',
)
async def heatmap_get_by_date(
    filter_args: list = fastapi.Depends(dependencies.statistics_filter_args),
    default_filter_args: list = fastapi.Depends(
        dependencies.courier_statistics_default_filter_args,
    ),
    _: schemas.UserCurrent = fastapi.Security(
        auth.get_current_user,
        scopes=['s:g'],
    ),
):
    """Get dashboard data by datetime filter"""
    result = await controllers.statistics_heatmap_get_by_date(
        filter_params=filter_args,
        default_filter_args=default_filter_args
    )
    return JSONResponse(jsonable_encoder(result))


@router.get(
    '/statistics/courier',
    response_model=schemas.CourierStatGet,
)
async def courier_stat_get(
    filter_string: str = fastapi.Depends(dependencies.resolve_courier_statistics_filter)
):
    result = await controllers.courier_stat_get(
        filter_string=filter_string,
    )
    return JSONResponse(jsonable_encoder(result))


@router.get(
    '/statistics/courier/progress',
    response_model=List[schemas.CourierProgressGet],
)
async def courier_progress_get(
    courier_id: int,
    interval: ProgressInterval,
    default_filter_args: list = fastapi.Depends(
        dependencies.courier_statistics_default_filter_args,
    ),
    filter_string: str = fastapi.Depends(dependencies.resolve_courier_progress_filter),
):
    result = await controllers.courier_progress_get(
        courier_id=courier_id,
        default_filter_args=default_filter_args,
        filter_string=filter_string,
        interval=interval,
    )
    return JSONResponse(jsonable_encoder(result))
