import pytest
from tortoise.exceptions import DoesNotExist

from api import models
from api.domain.order import OrderTransitionError
from tests.fixtures.database import db, run_pre_start_sql_script


@pytest.mark.asyncio
async def test_changing_status(
        db,
        pre_start_sql_script,
        run_pre_start_sql_script,
        controller,
):
    await run_pre_start_sql_script(pre_start_sql_script)

    order_id = 1
    status_id = 35

    order = await models.Order.get(id=order_id)
    assert order.current_status_id != status_id

    await controller.transition_order_status(
        order_id=order_id,
        status_id=status_id,
        default_filter_args=[],
        user_id=1,
        user_profile='manager'
    )

    order = await models.Order.get(id=order_id)
    assert order.current_status_id == status_id


@pytest.mark.asyncio
async def test_changing_to_not_allowed_status(
        db,
        pre_start_sql_script,
        run_pre_start_sql_script,
        controller,
):
    await run_pre_start_sql_script(pre_start_sql_script)

    order_id = 2
    status_id = 35

    with pytest.raises(OrderTransitionError, match='Not allow transition from delivered to card_returned_to_bank'):
        await controller.transition_order_status(
            order_id=order_id,
            status_id=status_id,
            default_filter_args=[],
            user_id=1,
            user_profile='manager'
        )


@pytest.mark.asyncio
async def test_order_not_found(
        db,
        pre_start_sql_script,
        run_pre_start_sql_script,
        controller,
):
    await run_pre_start_sql_script(pre_start_sql_script)

    order_id = 777
    status_id = 35

    with pytest.raises(DoesNotExist, match='Order with given ID: 777 was not found'):
        await controller.transition_order_status(
            order_id=order_id,
            status_id=status_id,
            default_filter_args=[],
            user_id=1,
            user_profile='manager'
        )


@pytest.mark.asyncio
async def test_status_not_found(
        db,
        pre_start_sql_script,
        run_pre_start_sql_script,
        controller,
):
    await run_pre_start_sql_script(pre_start_sql_script)

    order_id = 1
    status_id = 555

    with pytest.raises(DoesNotExist, match='Status with given ID: 555 was not found'):
        await controller.transition_order_status(
            order_id=order_id,
            status_id=status_id,
            default_filter_args=[],
            user_id=1,
            user_profile='manager'
        )


@pytest.mark.asyncio
async def test_history_was_written(
        db,
        pre_start_sql_script,
        run_pre_start_sql_script,
        controller,
):
    await run_pre_start_sql_script(pre_start_sql_script)

    order_id = 1
    status_id = 35

    await controller.transition_order_status(
        order_id=order_id,
        status_id=status_id,
        default_filter_args=[],
        user_id=1,
        user_profile='manager'
    )

    history = await models.History.get(id=1)
    assert history.model_type == 'Order'
    assert history.model_id == order_id

    action_data = history.action_data.get('status_transition', {})
    assert action_data.get('from') == 'new'
    assert action_data.get('to') == 'card_returned_to_bank'

    assert history.initiator_type == 'User'
    assert history.initiator_role == 'manager'
    assert history.initiator_id == 1


@pytest.mark.asyncio
async def test_transition_to_repeatable_status(
        db,
        pre_start_sql_script,
        run_pre_start_sql_script,
        controller,
):
    await run_pre_start_sql_script(pre_start_sql_script)

    order_id = 3
    status_id = 36 # pos_terminal_registration

    order = await models.Order.get(id=order_id)
    assert order.current_status_id == status_id

    await controller.transition_order_status(
        order_id=order_id,
        status_id=status_id,
        default_filter_args=[],
        user_id=1,
        user_profile='manager'
    )

    order = await models.Order.get(id=order_id)
    assert order.current_status_id == status_id
