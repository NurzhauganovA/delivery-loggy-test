from freezegun import freeze_time

from api import models
from api.controllers import save_courier_geolocation
from tests.fixtures.database import db, run_pre_start_sql_script


async def test_save_courier_geolocation(
        db,
        pre_start_sql_script,
        run_pre_start_sql_script,
        data,
        courier
):
    await run_pre_start_sql_script(pre_start_sql_script)

    await save_courier_geolocation(
        data=data,
        courier=courier,
        default_filter_args=[]
    )


@freeze_time("2025-04-14T12:00:00Z")
async def test_save_in_history(
        db,
        pre_start_sql_script,
        run_pre_start_sql_script,
        data,
        courier
):
    await run_pre_start_sql_script(pre_start_sql_script)

    await save_courier_geolocation(
        data=data,
        courier=courier,
        default_filter_args=[]
    )

    history_records = await models.History.filter(model_id=data.order_id).all()
    assert len(history_records) == 1

    history_record = history_records[0]
    assert history_record.action_type == 'save_courier_geolocation'
    assert history_record.action_data == {'coordinates': {'latitude': '123.123', 'longitude': '456.456'}}
    assert history_record.model_id == 1
    assert history_record.model_type == 'Order'
    assert history_record.created_at.strftime("%Y-%m-%d %H:%M:%S") == '2025-04-14 17:00:00'
