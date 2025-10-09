from unittest.mock import patch, AsyncMock

import pytest
from tortoise.exceptions import DoesNotExist

from api import models
from api.controllers.handle_order_status_transition.handlers.pos_terminal_registration.exceptions import (
    POSTerminalRegistrationHandlerValidationError,
    POSTerminalRegistrationHandlerIntegrationError,
    NotAllowPOSTerminalRegistration,
)
from api.domain.products.pos_terminal import RegistrationStatus
from tests.fixtures.database import db, run_pre_start_sql_script


@pytest.mark.asyncio
@patch('api.models.publisher.__publish', new=AsyncMock(return_value=None))
async def test_registration_with_data(
        db,
        pre_start_sql_script,
        run_pre_start_sql_script,
        handler,
):
    await run_pre_start_sql_script(pre_start_sql_script)

    order_id = 1

    pos_terminal_registration_status = await models.Status.get(code='pos_terminal_registration')

    order = await models.Order.get(id=order_id)

    product = await models.Product.get(order_id=order_id)
    assert product.attributes.get('model') is None
    assert product.attributes.get('serial_number') is None

    await handler.handle(
        order_obj=order,
        status=pos_terminal_registration_status,
        data={
            'model': 'PAX',
            'serial_number': '999111888222777'
        }
    )

    product = await models.Product.get(order_id=order_id)
    assert product.attributes.get('model') == 'PAX'
    assert product.attributes.get('serial_number') == '999111888222777'


@pytest.mark.asyncio
@patch('api.models.publisher.__publish', new=AsyncMock(return_value=None))
async def test_registration_with_data_and_already_has_another_data(
        db,
        pre_start_sql_script,
        run_pre_start_sql_script,
        handler,
):
    await run_pre_start_sql_script(pre_start_sql_script)

    order_id = 2

    pos_terminal_registration_status = await models.Status.get(code='pos_terminal_registration')

    order = await models.Order.get(id=order_id)

    product = await models.Product.get(order_id=order_id)
    assert product.attributes.get('model') == 'SUNMI'
    assert product.attributes.get('serial_number') == '11111111222222'

    await handler.handle(
        order_obj=order,
        status=pos_terminal_registration_status,
        data={
            'model': 'PAX',
            'serial_number': '999111888222777',
        }
    )

    product = await models.Product.get(order_id=order_id)
    assert product.attributes.get('model') == 'PAX'
    assert product.attributes.get('serial_number') == '999111888222777'


@pytest.mark.asyncio
@patch('api.models.publisher.__publish', new=AsyncMock(return_value=None))
async def test_product_not_found(
        db,
        pre_start_sql_script,
        run_pre_start_sql_script,
        handler,
):
    await run_pre_start_sql_script(pre_start_sql_script)

    order_id = 5

    pos_terminal_registration_status = await models.Status.get(code='pos_terminal_registration')

    order = await models.Order.get(id=order_id)

    with pytest.raises(DoesNotExist, match='product with given order_id: 5 was not found'):
        await handler.handle(
            order_obj=order,
            status=pos_terminal_registration_status,
            data={
                'model': 'PAX',
                'serial_number': '999111888222777',
            }
        )


@pytest.mark.asyncio
@patch('api.models.publisher.__publish', new=AsyncMock(return_value=None))
async def test_product_has_wrong_type(
        db,
        pre_start_sql_script,
        run_pre_start_sql_script,
        handler,
):
    await run_pre_start_sql_script(pre_start_sql_script)

    order_id = 4

    pos_terminal_registration_status = await models.Status.get(code='pos_terminal_registration')

    order = await models.Order.get(id=order_id)

    with pytest.raises(POSTerminalRegistrationHandlerValidationError, match='product has wrong type: card, required type: pos_terminal'):
        await handler.handle(
            order_obj=order,
            status=pos_terminal_registration_status,
            data={
                'model': 'PAX',
                'serial_number': '999111888222777',
            }
        )

@pytest.mark.asyncio
@patch('api.models.publisher.__publish', new=AsyncMock(return_value=None))
async def test_not_valid_model(
        db,
        pre_start_sql_script,
        run_pre_start_sql_script,
        handler,
):
    await run_pre_start_sql_script(pre_start_sql_script)

    order_id = 4

    pos_terminal_registration_status = await models.Status.get(code='pos_terminal_registration')

    order = await models.Order.get(id=order_id)

    with pytest.raises(POSTerminalRegistrationHandlerValidationError):
        await handler.handle(
            order_obj=order,
            status=pos_terminal_registration_status,
            data={
                'model': 'TEST_MODEL',
                'serial_number': '999111888222777',
            }
        )


@pytest.mark.asyncio
@patch('api.models.publisher.__publish', new=AsyncMock(return_value=None))
async def test_not_valid_serial_number(
        db,
        pre_start_sql_script,
        run_pre_start_sql_script,
        handler,
):
    await run_pre_start_sql_script(pre_start_sql_script)

    order_id = 4

    pos_terminal_registration_status = await models.Status.get(code='pos_terminal_registration')

    order = await models.Order.get(id=order_id)

    with pytest.raises(POSTerminalRegistrationHandlerValidationError):
        await handler.handle(
            order_obj=order,
            status=pos_terminal_registration_status,
            data={
                'model': 'PAX',
                'serial_number': '',
            }
        )


@pytest.mark.asyncio
@patch('api.models.publisher.__publish', new=AsyncMock(return_value=None))
async def test_pos_terminal_registration_success(
        db,
        pre_start_sql_script,
        run_pre_start_sql_script,
        handler
):
    await run_pre_start_sql_script(pre_start_sql_script)

    order_id = 1

    pos_terminal_registration_status = await models.Status.get(code='pos_terminal_registration')

    order = await models.Order.get(id=order_id)

    await handler.handle(
        order_obj=order,
        status=pos_terminal_registration_status,
        data={
            'model': 'PAX',
            'serial_number': '999111888222777',
        }
    )

    product = await models.Product.get(order_id=order_id)
    assert product.attributes.get('business_key') == 'OVERDRAFT-TMS25-02339'


@pytest.mark.asyncio
@patch('api.models.publisher.__publish', new=AsyncMock(return_value=None))
async def test_pos_terminal_registration_failure(
        db,
        pre_start_sql_script,
        run_pre_start_sql_script,
        handler
):
    await run_pre_start_sql_script(pre_start_sql_script)

    order_id = 1

    pos_terminal_registration_status = await models.Status.get(code='pos_terminal_registration')

    order = await models.Order.get(id=order_id)

    with pytest.raises(POSTerminalRegistrationHandlerIntegrationError):
        await handler.handle(
            order_obj=order,
            status=pos_terminal_registration_status,
            data={
                'model': 'PAX',
                'serial_number': '77777',
            }
        )


@pytest.mark.asyncio
@patch('api.models.publisher.__publish', new=AsyncMock(return_value=None))
async def test_pos_terminal_registration_not_allow_error(
        db,
        pre_start_sql_script,
        run_pre_start_sql_script,
        handler
):
    await run_pre_start_sql_script(pre_start_sql_script)

    pos_terminal_registration_status = await models.Status.get(code='pos_terminal_registration')

    order = await models.Order.get(id=3)

    with pytest.raises(NotAllowPOSTerminalRegistration, match='not allowed start registration, current registration_status: COMPLETED'):
        await handler.handle(
            order_obj=order,
            status=pos_terminal_registration_status,
            data={
                'model': 'PAX',
                'serial_number': '111111',
            }
        )


@pytest.mark.asyncio
@patch('api.models.publisher.__publish', new=AsyncMock(return_value=None))
async def test_pos_terminal_registration_two_calls_in_row(
        db,
        pre_start_sql_script,
        run_pre_start_sql_script,
        handler
):
    await run_pre_start_sql_script(pre_start_sql_script)

    pos_terminal_registration_status = await models.Status.get(code='pos_terminal_registration')

    order = await models.Order.get(id=1)

    await handler.handle(
        order_obj=order,
        status=pos_terminal_registration_status,
        data={
            'model': 'PAX',
            'serial_number': '111111',
        }
    )

    with pytest.raises(NotAllowPOSTerminalRegistration, match='not allowed start registration, current registration_status: STARTED'):
        await handler.handle(
            order_obj=order,
            status=pos_terminal_registration_status,
            data={
                'model': 'PAX',
                'serial_number': '111111',
            }
        )


@pytest.mark.skip(reason="Пока нет нормальной обработки статуса CANCELED")
@patch('api.models.publisher.__publish', new=AsyncMock(return_value=None))
async def test_pos_terminal_registration_second_call_on_cancelled_status(
        db,
        pre_start_sql_script,
        run_pre_start_sql_script,
        handler
):
    await run_pre_start_sql_script(pre_start_sql_script)

    pos_terminal_registration_status = await models.Status.get(code='pos_terminal_registration')

    order = await models.Order.get(id=1)

    # Вызовем в первый раз регистрацию pos терминала
    await handler.handle(
        order_obj=order,
        status=pos_terminal_registration_status,
        data={
            'model': 'PAX',
            'serial_number': '111111',
        }
    )

    # Сделаем вид, что регистрация завершена и поставим статус CANCELED
    product = await models.Product.get(id=1)
    product.attributes['business_key'] = 'test'
    product.attributes['registration_status'] = RegistrationStatus.CANCELED
    await product.save()

    # Вызовем повторно регистрацию pos терминала
    with pytest.raises(NotAllowPOSTerminalRegistration, match='not allowed start registration, current registration_status: CANCELED'):
        await handler.handle(
            order_obj=order,
            status=pos_terminal_registration_status,
            data={
                'model': 'PAX',
                'serial_number': '111111',
            }
        )


@pytest.mark.asyncio
@patch('api.models.publisher.__publish', new=AsyncMock(return_value=None))
async def test_data_is_none(
        db,
        pre_start_sql_script,
        run_pre_start_sql_script,
        handler
):
    await run_pre_start_sql_script(pre_start_sql_script)

    pos_terminal_registration_status = await models.Status.get(code='pos_terminal_registration')

    order = await models.Order.get(id=3)

    with pytest.raises(POSTerminalRegistrationHandlerValidationError, match='data is required'):
        await handler.handle(
            order_obj=order,
            status=pos_terminal_registration_status,
            data=None
        )
