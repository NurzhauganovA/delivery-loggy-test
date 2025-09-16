from decimal import Decimal

import pytest

from api import models
from api.controllers.handle_order_status_transition.handlers import VerifyOTPHandler
from api.controllers.handle_order_status_transition.handlers.verify_otp.exceptions import VerifyOTPValidationError
from tests.fixtures.database import db, run_pre_start_sql_script


@pytest.mark.asyncio
async def test_verify_by_pos_terminal_adapter(
    db,
    pre_start_sql_script,
    run_pre_start_sql_script,
    pos_terminal_otp_adapter,
):
    await run_pre_start_sql_script(pre_start_sql_script)

    handler = VerifyOTPHandler(
        verify_otp_adapters={
            2: pos_terminal_otp_adapter,
        }
    )

    order_obj = await models.Order.get(id=2)
    status_obj = await models.Status.get(code='verify_otp')

    data = {
        'code': '1234',
        'code_sent_point': {
            'latitude': 45.0,
            'longitude': -122.0,
        }
    }

    await handler.handle(order_obj=order_obj, status=status_obj, data=data)

    pos_terminal_otp_adapter.verify.assert_awaited_once_with(
        business_key='OVERDRAFT-00000000',
        phone_number='+77781254616',
        otp_code='1234',
        courier_full_name='Курьеров 1 Курьер 1 Курьерович 1',
    )


@pytest.mark.asyncio
async def test_verify_by_freedom_otp_adapter(
    db,
    pre_start_sql_script,
    run_pre_start_sql_script,
    freedom_bank_otp_adapter,
):
    await run_pre_start_sql_script(pre_start_sql_script)

    handler = VerifyOTPHandler(
        verify_otp_adapters={
            1: freedom_bank_otp_adapter,
        }
    )

    order_obj = await models.Order.get(id=1)
    status_obj = await models.Status.get(code='verify_otp')

    data = {
        'code': '1234',
        'code_sent_point': {
            'latitude': 45.0,
            'longitude': -122.0,
        }
    }

    await handler.handle(order_obj=order_obj, status=status_obj, data=data)

    freedom_bank_otp_adapter.verify.assert_awaited_once_with(
        partner_order_id='BFF000081',
        otp_code='1234',
    )


@pytest.mark.asyncio
async def test_change_order_status(
    db,
    pre_start_sql_script,
    run_pre_start_sql_script,
    pos_terminal_otp_adapter,
):
    await run_pre_start_sql_script(pre_start_sql_script)

    handler = VerifyOTPHandler(
        verify_otp_adapters={
            2: pos_terminal_otp_adapter,
        }
    )

    order_obj = await models.Order.get(id=2)
    status_obj = await models.Status.get(code='verify_otp')
    assert order_obj.current_status_id != status_obj.id

    data = {
        'code': '1234',
        'code_sent_point': {
            'latitude': 45.0,
            'longitude': -122.0,
        }
    }

    await handler.handle(order_obj=order_obj, status=status_obj, data=data)

    order_obj = await models.Order.get(id=2)
    next_status_obj = await models.Status.get(code='photo_capturing')
    assert order_obj.current_status_id == next_status_obj.id


@pytest.mark.asyncio
async def test_save_geolocation(
    db,
    pre_start_sql_script,
    run_pre_start_sql_script,
    pos_terminal_otp_adapter,
):
    await run_pre_start_sql_script(pre_start_sql_script)

    handler = VerifyOTPHandler(
        verify_otp_adapters={
            2: pos_terminal_otp_adapter,
        }
    )

    order_id = 2

    order_obj = await models.Order.get(id=order_id)
    status_obj = await models.Status.get(code='verify_otp')

    data = {
        'code': '1234',
        'code_sent_point': {
            'latitude': 45.0,
            'longitude': -122.0,
        }
    }

    await handler.handle(order_obj=order_obj, status=status_obj, data=data)

    geolocation = await models.OrderGeolocation.get(id=1)
    assert geolocation.order_id == order_id
    assert geolocation.code_sent_point == [Decimal('45'), Decimal('-122')]


@pytest.mark.asyncio
async def test_no_otp_code_validation_error(
    db,
    pre_start_sql_script,
    run_pre_start_sql_script,
    pos_terminal_otp_adapter,
    handler,
):
    await run_pre_start_sql_script(pre_start_sql_script)

    order_id = 2

    order_obj = await models.Order.get(id=order_id)
    status_obj = await models.Status.get(code='send_otp')

    with pytest.raises(VerifyOTPValidationError):
        await handler.handle(order_obj=order_obj, status=status_obj, data=None)

    with pytest.raises(VerifyOTPValidationError):
        await handler.handle(order_obj=order_obj, status=status_obj, data={'test': 'test'})
