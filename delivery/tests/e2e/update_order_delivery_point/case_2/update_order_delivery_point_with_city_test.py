import pytest
from freezegun import freeze_time

from tests.fixtures.client import client
from tests.fixtures.database import db, run_pre_start_sql_script
from tests.fixtures.token import get_access_token_v1


@pytest.mark.asyncio
@freeze_time("2025-04-14T12:00:00Z")
async def test_query_update_delivery_point(
    client,
    credentials,
    profile_data,
    profile_service_manager_data,
    get_access_token_v1,
    db,
    pre_start_sql_script,
    run_pre_start_sql_script,
):
    await run_pre_start_sql_script(pre_start_sql_script)

    access_token = await get_access_token_v1(client, credentials, profile_data)

    body = {
        "delivery_point": {
            "latitude": 12.345678,
            "longitude": 12.345678,
            "address": "Улица Пианиста, Дом Колбасиста 7"
        },
        "city_id": 2,
        "comment": "Космос подсказал что клиент находится тут"
    }

    response = await client.patch(
        url='/v2/order/1/delivery_point',
        headers={'Authorization': 'Bearer ' + access_token},
        json=body,
    )
    assert response.status_code == 200
    access_token_for_service_manager = await get_access_token_v1(client, credentials, profile_service_manager_data)
    order_v2_get_resp = await client.get(
        url='/v2/crm/order/1',
        headers={'Authorization': 'Bearer ' + access_token_for_service_manager},
    )
    assert order_v2_get_resp.status_code == 200
    response_data = order_v2_get_resp.json()
    updated_delivery_point = response_data['delivery_point']
    assert updated_delivery_point['latitude'] == 12.345678
    assert updated_delivery_point['longitude'] == 12.345678
    assert updated_delivery_point['address'] == 'Улица Пианиста, Дом Колбасиста 7'
    assert response_data['city']['id'] == 2
    assert response_data['comment'] == 'Космос подсказал что клиент находится тут'
