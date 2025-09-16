from datetime import timedelta
from random import uniform
from typing import List

import tortoise
from api.schemas.statistics import HeatmapResponse, HeatmapResponseItem
from pydantic import parse_obj_as
from tortoise import fields
from tortoise.exceptions import DoesNotExist
from tortoise.expressions import RawSQL, Subquery, F
from tortoise.functions import Count
from tortoise.models import Model
from tortoise.transactions import in_transaction

from .. import models
from .. import schemas
from .. import enums
from ..database import database_connection

from ..enums.statistics import ProgressInterval, progress_interval_to_query_map
from ..modules.delivery_point import DeliveryPointRepository


class CourierStat(Model):
    id = fields.IntField(pk=True)
    courier: fields.ForeignKeyRelation['models.ProfileCourier'] = fields.ForeignKeyField(
        'versions.ProfileCourier',
        'statistics',
        fields.CASCADE,
    )

    reaction_time = fields.TimeDeltaField(null=True)
    completion_time = fields.TimeDeltaField(null=True)
    order_count = fields.SmallIntField(default=0)
    ranged = fields

    created_at = fields.DateField()

    # type hints
    courier_id: int

    class Meta:
        table = 'courier_statistics'
        unique_together = ('courier', 'created_at')


async def courier_stat_get(filter_string: str):
    query = f"""
    select
     courier_id,
     (extract(epoch from sum(order_count * reaction_time)) * 1000) / coalesce(sum(order_count), 1) AS "avg_reaction_time",
     (extract(epoch from sum(order_count * completion_time)) * 1000) / coalesce(sum(order_count), 1) AS "avg_completion_time",
     sum(order_count) AS "order_count"
    from courier_statistics
    {filter_string}
    group by courier_id;
    """
    async with in_transaction('default') as conn:
        count, result = await conn.execute_query(query)
        if not count:
            return {}
        return schemas.CourierStatGet(**result[0])


async def courier_progress_get(courier_id: int, default_filter_args: list,
                               filter_string: str, interval):
    try:
        await models.ProfileCourier.filter(*default_filter_args).get(id=courier_id)
    except DoesNotExist:
        raise DoesNotExist('Courier does not exist')

    interval_query = progress_interval_to_query_map[interval]
    date_manipulation_function = 'upper' if interval != ProgressInterval.DAILY else ''
    query = f"""
    select (coalesce(sum(cs.order_count * extract(epoch from cs.reaction_time)), 0)::bigint * 1000) / coalesce(sum(cs.order_count), 1)   AS "avg_reaction_time",
       (coalesce(sum(cs.order_count * extract(epoch from cs.completion_time)), 0)::bigint * 1000) / coalesce(sum(cs.order_count), 1) AS "avg_completion_time",
       coalesce(sum(cs.order_count), 0)                                          AS "order_count",
       {date_manipulation_function}({interval_query})                   AS "date"
    from {filter_string} dates
             left join courier_statistics cs on date(cs.created_at) between date(dates) and date(dates + '1 {interval}'::interval - '1 second'::interval)
             and courier_id = {courier_id}
    group by {interval_query}
    order by {interval_query};
    """
    async with in_transaction('default') as conn:
        count, result = await conn.execute_query(query)
        return parse_obj_as(List[schemas.CourierProgressGet], result)


async def statistics_get(filter_params, default_filter_args) -> schemas.StatisticsBase:
    orders = models.Order.all_objects.filter(*default_filter_args, **filter_params)
    statuses = ['all', 'new', 'others', 'cancelled', 'postponed', 'on-the-way-to-call-point',
                'is_delivered']
    order_status_query = f""" 
            SELECT
                COUNT(*) AS "all",
                SUM(CASE WHEN delivery_status = '{{}}' THEN 1 ELSE 0 END) AS "new",
                SUM(CASE
                    WHEN delivery_status <> '{{}}' AND delivery_status->>'status' NOT IN ('cancelled', 'postponed', 'is_delivered', 'on-the-way-to-call-point') THEN 1
                        ELSE 0
                    END) AS "others",
                SUM(CASE WHEN delivery_status->>'status' = 'cancelled' THEN 1 ELSE 0 END) AS "cancelled",
                SUM(CASE WHEN delivery_status->>'status' = 'postponed' THEN 1 ELSE 0 END) AS "postponed",
                SUM(CASE WHEN delivery_status->>'status' = 'is_delivered' THEN 1 ELSE 0 END) AS "is_delivered",
                SUM(CASE WHEN delivery_status->>'status' = 'on-the-way-to-call-point' THEN 1 ELSE 0 END) as "on-the-way-to-call-point" 
            FROM ({orders.as_query()}) AS orders
    """

    city_order_status_query = f""" 
            SELECT DISTINCT city.name AS city_name,
                COUNT(*) AS "all",
                SUM(CASE WHEN orders.delivery_status = '{{}}' AND orders.city_id=city.id THEN 1 ELSE 0 END) AS "new",
                SUM(CASE
                    WHEN orders.delivery_status <> '{{}}' AND orders.delivery_status->>'status' NOT IN ('cancelled', 'postponed', 'is_delivered', 'on-the-way-to-call-point') THEN 1
                        ELSE 0
                    END) AS "others",
                SUM(CASE WHEN orders.delivery_status->>'status' = 'cancelled' THEN 1 ELSE 0 END) AS "cancelled",
                SUM(CASE WHEN orders.delivery_status->>'status' = 'postponed' THEN 1 ELSE 0 END) AS "postponed",
                SUM(CASE WHEN orders.delivery_status->>'status' = 'is_delivered' THEN 1 ELSE 0 END) AS "is_delivered",
                SUM(CASE WHEN orders.delivery_status->>'status' = 'on-the-way-to-call-point' THEN 1 ELSE 0 END) as "on-the-way-to-call-point"
            FROM ({orders.as_query()}) as orders LEFT JOIN city on city.id=orders.city_id GROUP BY city_name ORDER BY city_name
    """

    async with tortoise.transactions.in_transaction('default') as conn:
        _, order_counts = await conn.execute_query(order_status_query)
        _, city_order_counts = await conn.execute_query(city_order_status_query)
    status_list, cities_list = [], []
    for status in statuses:
        status_list.append(
            {'name': status, 'count': order_counts[0][status] if order_counts[0][status] else 0}
        )
    for city in city_order_counts:
        city_status_list = [{'name': i, 'count': city[i]} for i in statuses]
        cities_list.append({'name': city['city_name'], 'statuses': city_status_list})
    return schemas.StatisticsBase(statuses=status_list, cities=cities_list)


async def daterange(start_date, end_date):
    dates = [start_date.strftime("%Y-%m-%d")]
    while start_date <= end_date:
        start_date += timedelta(days=1)
        dates.append(start_date.strftime("%Y-%m-%d"))
    return dates

async def statistics_get_by_date(filter_params, default_filter_args):
    created_at_range = filter_params.get('created_at__range')
    orders = models.Order.all_objects.filter(*default_filter_args, **filter_params)
    subquery = Subquery(orders.filter(delivery_status__filter={'status':'cancelled'}).values_list('id', flat=True))
    history = models.History.filter(model_id__in=subquery, model_type='Order')
    get_new_and_delivered_count = f"""
            SELECT
                DATE(os.created_at) AS status_date,
                SUM(CASE WHEN os.status_id = 1 THEN 1 ELSE 0 END) AS new, -- 1: Новая заявка
                SUM(CASE WHEN os.status_id in (7, 27) THEN 1 ELSE 0 END) AS is_delivered -- 7: Доставлено 27: Выдано 
            FROM ({orders.values('id', 'created_at', 'partner_id').as_query()}) AS o
            LEFT JOIN "order.statuses" AS os ON os.order_id = o.id AND os.status_id IN (1, 7, 27)
            WHERE os.created_at between '{created_at_range[0]}' and '{created_at_range[1]}'
            GROUP BY status_date;
            """
    get_cancelled_count = f"""
            WITH CancelledOrders AS (
            SELECT
                DATE(hs.created_at) AS status_date,
                hs.model_id,
                ROW_NUMBER() OVER (PARTITION BY hs.model_id ORDER BY hs.created_at DESC) AS row_num
            FROM ({history.as_query()}) AS hs
            )
            SELECT
                status_date,
                COUNT(*) AS cancelled
            FROM CancelledOrders
            WHERE row_num = 1
            GROUP BY status_date;
    """
    async with tortoise.transactions.in_transaction('default') as conn:
        _, new_and_delivered_count = await conn.execute_query(get_new_and_delivered_count)
        _, cancelled_count = await conn.execute_query(get_cancelled_count)

    dates = await daterange(created_at_range[0], created_at_range[1])
    result = {f'{i}': {
        'date': f'{i}', 'new': 0, 'is_delivered': 0, 'cancelled': 0
    } for i in dates}
    for date in new_and_delivered_count:
        result[str(date['status_date'])]['new'] = date['new']
        result[str(date['status_date'])]['is_delivered'] = date['is_delivered']
    for date in cancelled_count:
        result[str(date['status_date'])]['cancelled'] = date['cancelled']
    return list(result.values())


async def convert_to_hour_format(hour):
    return f'{hour:02d}:00'


async def statistics_get_by_hour(filter_params, default_filter_args):
    orders = models.Order.all_objects.filter(*default_filter_args, **filter_params)
    statuses = ['new', 'is_delivered']

    query = f"""
            SELECT
                EXTRACT(HOUR FROM os.created_at AT TIME ZONE 'UTC' + INTERVAL '6 hours') AS hour,
                SUM(CASE WHEN s.slug = 'novaia-zaiavka' THEN 1 ELSE 0 END) AS new,
                SUM(CASE WHEN s.slug = 'dostavleno' THEN 1 ELSE 0 END) AS is_delivered
            FROM ({orders.as_query()}) AS o
            LEFT JOIN "order.statuses" AS os ON os.order_id = o.id
            LEFT JOIN status AS s ON os.status_id = s.id AND s.slug IN ('novaia-zaiavka', 'dostavleno')
            GROUP BY hour;
            """

    async with in_transaction("default") as tconn:
        _, new_counts = await tconn.execute_query(query)
    result = {f'{hour:02d}:00': {
        'hour': f'{hour:02d}:00', 'new': 0, 'is_delivered': 0
    } for hour in range(24)}

    for hour in new_counts:
        result_hour = await convert_to_hour_format(int(hour['hour']))
        for sts in statuses:
            result[result_hour][sts] = hour[sts]
    return list(result.values())


async def statistics_heatmap_get_by_date(filter_params, default_filter_args) -> HeatmapResponse:
    delivery_points = models.Order.all_objects.filter(
        delivery_point__latitude__isnull=False,
        delivery_point__longitude__isnull=False,
        *default_filter_args,
        **filter_params,
    ).select_related('delivery_point').annotate(
        rounded_latitude=RawSQL('round("order__delivery_point"."latitude", 2)'),
        rounded_longitude=RawSQL('round("order__delivery_point"."longitude", 2)'),
        count=Count('delivery_point__latitude'),
    ).group_by('rounded_latitude', 'rounded_longitude').values(
        'rounded_latitude',
        'rounded_longitude',
        'count',
    )

    query = f"""
                SELECT
                 count("delivery_points"."count") AS "count",
                 "delivery_points"."rounded_latitude" AS "latitude",
                 "delivery_points"."rounded_longitude" AS "longitude"
                FROM ({delivery_points.as_query()}) AS "delivery_points"
                GROUP BY
                  "delivery_points"."rounded_latitude",
                  "delivery_points"."rounded_longitude"
             """

    # noinspection PyUnusedLocal
    result_list = []
    async with database_connection() as conn:
        data = await conn.fetch(query)
        result_list = parse_obj_as(List[HeatmapResponseItem], data)

    return HeatmapResponse(
        max=dict(max(data, key=lambda x: x['count']))['count'] if data else 0,
        data=result_list
    )
