from tests.fixtures.client import client
from tests.fixtures.database import db, run_pre_start_sql_script
from tests.fixtures.token import get_access_token_v1


async def test_save_courier_geolocation(
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

    response = await client.post(
        url='/v2/courier/me/geolocation',
        headers={'Authorization': 'Bearer ' + access_token},
        json={
            'latitude': 11.11,
            'longitude': 22.22,
            'order_id': 1,
        }
    )
    assert response.status_code == 200
