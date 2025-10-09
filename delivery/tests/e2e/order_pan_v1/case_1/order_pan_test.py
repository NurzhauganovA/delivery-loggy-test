import pytest

from tests.fixtures.client import client
from tests.fixtures.database import db, run_pre_start_sql_script
from tests.fixtures.token import get_access_token_v1


@pytest.mark.asyncio
async def test_order_pan(
        client,
        credentials,
        profile_data,
        get_access_token_v1,
        db,
        pre_start_sql_script,
        run_pre_start_sql_script,
        expected,
):
    await run_pre_start_sql_script(pre_start_sql_script)

    access_token = await get_access_token_v1(client, credentials, profile_data)

    body = {
        'pan': '5269880012192985',
        'input_type': 'manually',
    }

    response = await client.post(
        url='/v1/order/1/pan',
        headers={'Authorization': 'Bearer ' + access_token},
        json=body,
    )
    assert response.status_code == 200
    assert response.json() == expected


@pytest.mark.asyncio
async def test_pan_is_not_matched_by_mask(
        client,
        credentials,
        profile_data,
        get_access_token_v1,
        db,
        pre_start_sql_script,
        run_pre_start_sql_script,
        expected,
):
    await run_pre_start_sql_script(pre_start_sql_script)

    access_token = await get_access_token_v1(client, credentials, profile_data)

    body = {
        'pan': '1169880012192985',
        'input_type': 'manually',
    }

    response = await client.post(
        url='/v1/order/1/pan',
        headers={'Authorization': 'Bearer ' + access_token},
        json=body,
    )
    assert response.status_code == 422
    assert response.json() == {'detail': [{'loc': ['body', 'pan'], 'msg': 'Pan is not valid', 'type': 'validation_error'}]}


@pytest.mark.asyncio
async def test_order_pan_double_request(
        client,
        credentials,
        profile_data,
        get_access_token_v1,
        db,
        pre_start_sql_script,
        run_pre_start_sql_script,
        expected,
):
    await run_pre_start_sql_script(pre_start_sql_script)

    access_token = await get_access_token_v1(client, credentials, profile_data)

    # Первый вызов, тут курьер ошибся при вводе номера карты
    response = await client.post(
        url='/v1/order/1/pan',
        headers={'Authorization': 'Bearer ' + access_token},
        json={
            'pan': '5269880042716217',
            'input_type': 'manually',
        },
    )
    assert response.status_code == 200

    # Второй вызов, тут курьер исправил ошибку
    response = await client.post(
        url='/v1/order/1/pan',
        headers={'Authorization': 'Bearer ' + access_token},
        json={
            'pan': '5269880012192985',
            'input_type': 'manually',
        },
    )
    assert response.status_code == 200
    assert response.json() == expected


@pytest.mark.asyncio
async def test_pan_already_exists_in_this_order(
        client,
        credentials,
        profile_data,
        get_access_token_v1,
        db,
        pre_start_sql_script,
        run_pre_start_sql_script,
        expected,
):
    await run_pre_start_sql_script(pre_start_sql_script)

    access_token = await get_access_token_v1(client, credentials, profile_data)

    # Первый вызов
    response = await client.post(
        url='/v1/order/1/pan',
        headers={'Authorization': 'Bearer ' + access_token},
        json={
            'pan': '5269880042716217',
            'input_type': 'manually',
        },
    )
    assert response.status_code == 200

    # Второй вызов, с тем же номером карты и по той же заявке
    response = await client.post(
        url='/v1/order/1/pan',
        headers={'Authorization': 'Bearer ' + access_token},
        json={
            'pan': '5269880042716217',
            'input_type': 'manually',
        },
    )
    assert response.status_code == 422
    assert response.json() == {'detail': [{'loc': ['body', 'pan'], 'msg': 'already linked to this order', 'type': 'validation_error'}]}


@pytest.mark.asyncio
async def test_pan_already_exists_in_another_order(
        client,
        credentials,
        profile_data,
        get_access_token_v1,
        db,
        pre_start_sql_script,
        run_pre_start_sql_script,
        expected,
):
    await run_pre_start_sql_script(pre_start_sql_script)

    access_token = await get_access_token_v1(client, credentials, profile_data)

    # Первый вызов, по заявке с id 1
    response = await client.post(
        url='/v1/order/1/pan',
        headers={'Authorization': 'Bearer ' + access_token},
        json={
            'pan': '5269880042716217',
            'input_type': 'manually',
        },
    )
    assert response.status_code == 200

    # Второй вызов, с тем же номером карты, но по заявке с id 2
    response = await client.post(
        url='/v1/order/2/pan',
        headers={'Authorization': 'Bearer ' + access_token},
        json={
            'pan': '5269880042716217',
            'input_type': 'manually',
        },
    )
    assert response.status_code == 422
    assert response.json() == {'detail': [{'loc': ['body', 'pan'], 'msg': 'already linked to another order', 'type': 'validation_error'}]}
