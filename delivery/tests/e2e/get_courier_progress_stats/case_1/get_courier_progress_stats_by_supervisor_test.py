from datetime import datetime, timedelta

from freezegun import freeze_time
import pytest

from tests.fixtures.client import client
from tests.fixtures.database import db, run_pre_start_sql_script
from tests.fixtures.token import get_access_token_v1


@pytest.mark.asyncio
@freeze_time('2021-01-10')
async def test_get_statistics_by_supervisor(
    client,
    credentials,
    profile_data,
    get_access_token_v1,
    db,
    pre_start_sql_script,
    run_pre_start_sql_script,
):
    await run_pre_start_sql_script(pre_start_sql_script)

    access_token = await get_access_token_v1(client, credentials, profile_data)

    params = {
        'from_date': datetime.now().date() - timedelta(days=1),
        'to_date': datetime.now().date() + timedelta(days=1),
        'courier_id': 1,
        'interval': 'day',
    }

    response = await client.get(
        url='/v1/statistics/courier/progress',
        headers={'Authorization': 'Bearer ' + access_token},
        params=params,
    )
    assert response.status_code == 200
    assert response.json()

"""
OperationalError(UndefinedFunctionError('function pg_catalog.extract(unknown, bigint) does not exist'))
"""

"""
    select (coalesce(sum(cs.order_count * extract(epoch from cs.reaction_time)), 0)::bigint * 1000) / coalesce(sum(cs.order_count), 1)   AS "avg_reaction_time",
       (coalesce(sum(cs.order_count * extract(epoch from cs.completion_time)), 0)::bigint * 1000) / coalesce(sum(cs.order_count), 1) AS "avg_completion_time",
       coalesce(sum(cs.order_count), 0)                                          AS "order_count",
       (date(dates))                   AS "date"
    from generate_series('2021-01-09'::date, '2021-01-11'::date, '1 day'::interval) dates
             left join courier_statistics cs on date(cs.created_at) between date(dates) and date(dates + '1 day'::interval - '1 second'::interval)
             and courier_id = 1
    group by date(dates)
    order by date(dates);
"""