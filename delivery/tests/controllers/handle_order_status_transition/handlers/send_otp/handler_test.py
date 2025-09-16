from decimal import Decimal

import pytest

from api import models
from api.controllers.handle_order_status_transition.handlers import SendOTPHandler
from tests.fixtures.database import db, run_pre_start_sql_script


@pytest.mark.asyncio
async def test_send_otp_handler_by_pos_terminal_adapter(
    db,
    pre_start_sql_script,
    run_pre_start_sql_script,
    pos_terminal_otp_adapter,
):
    await run_pre_start_sql_script(pre_start_sql_script)

    handler = SendOTPHandler(
        send_otp_adapters={
            2: pos_terminal_otp_adapter,
        }
    )

    order_obj = await models.Order.get(id=2)
    status_obj = await models.Status.get(code='send_otp')

    geo_data = {
        'latitude': 45.0,
        'longitude': -122.0,
    }

    await handler.handle(order_obj=order_obj, status=status_obj, data=geo_data)

    pos_terminal_otp_adapter.send.assert_awaited_once_with(business_key='OVERDRAFT-00000000', phone_number='+77781254616')


@pytest.mark.asyncio
async def test_send_otp_handler_by_freedom_otp_adapter(
    db,
    pre_start_sql_script,
    run_pre_start_sql_script,
    freedom_bank_otp_adapter,
):
    await run_pre_start_sql_script(pre_start_sql_script)

    handler = SendOTPHandler(
        send_otp_adapters={
            1: freedom_bank_otp_adapter,
        }
    )

    order_obj = await models.Order.get(id=1)
    status_obj = await models.Status.get(code='send_otp')

    geo_data = {
        'latitude': 45.0,
        'longitude': -122.0,
    }

    await handler.handle(order_obj=order_obj, status=status_obj, data=geo_data)

    freedom_bank_otp_adapter.send.assert_awaited_once_with(partner_order_id='BFF000081')



@pytest.mark.skip(reason="Для обратной совместимости пока нет логики смены статуса у этого handler")
@pytest.mark.asyncio
async def test_change_order_status(
    db,
    pre_start_sql_script,
    run_pre_start_sql_script,
    pos_terminal_otp_adapter,
):
    await run_pre_start_sql_script(pre_start_sql_script)

    handler = SendOTPHandler(
        send_otp_adapters={
            2: pos_terminal_otp_adapter,
        }
    )

    order_obj = await models.Order.get(id=2)
    status_obj = await models.Status.get(code='send_otp')
    assert order_obj.current_status_id != status_obj.id

    geo_data = {
        'latitude': 45.0,
        'longitude': -122.0,
    }

    await handler.handle(order_obj=order_obj, status=status_obj, data=geo_data)

    order_obj = await models.Order.get(id=2)
    assert order_obj.current_status_id == status_obj.id


@pytest.mark.asyncio
async def test_save_geolocation(
    db,
    pre_start_sql_script,
    run_pre_start_sql_script,
    pos_terminal_otp_adapter,
):
    await run_pre_start_sql_script(pre_start_sql_script)

    handler = SendOTPHandler(
        send_otp_adapters={
            2: pos_terminal_otp_adapter,
        }
    )

    order_id = 2

    order_obj = await models.Order.get(id=order_id)
    status_obj = await models.Status.get(code='send_otp')

    geo_data = {
        'latitude': 45.0,
        'longitude': -122.0,
    }

    await handler.handle(order_obj=order_obj, status=status_obj, data=geo_data)

    geolocation = await models.OrderGeolocation.get(id=1)
    assert geolocation.order_id == order_id
    assert geolocation.at_client_point == [Decimal('45'), Decimal('-122')]
