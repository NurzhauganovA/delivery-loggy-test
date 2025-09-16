from .. import models
from .. import schemas
from ..schemas.statistics import HeatmapResponse


async def statistics_get(filter_params, default_filter_args) -> schemas.StatisticsBase:
    return await models.statistics_get(
        filter_params=filter_params,
        default_filter_args=default_filter_args
    )


async def statistics_get_by_date(filter_params, default_filter_args) -> list:
    return await models.statistics_get_by_date(
        filter_params=filter_params,
        default_filter_args=default_filter_args
    )


async def statistics_get_by_hour(filter_params, default_filter_args) -> list:
    return await models.statistics_get_by_hour(
        filter_params=filter_params,
        default_filter_args=default_filter_args
    )


async def statistics_heatmap_get_by_date(filter_params, default_filter_args) -> HeatmapResponse:
    return await models.statistics_heatmap_get_by_date(
        filter_params=filter_params,
        default_filter_args=default_filter_args
    )


async def courier_stat_get(filter_string: str):
    return await models.courier_stat_get(
        filter_string=filter_string,
    )


async def courier_progress_get(courier_id: int, default_filter_args: list, filter_string: str, interval):
    return await models.courier_progress_get(
        courier_id=courier_id,
        default_filter_args=default_filter_args,
        filter_string=filter_string,
        interval=interval,
    )
