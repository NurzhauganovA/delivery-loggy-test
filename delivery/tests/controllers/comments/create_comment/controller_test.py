import pytest
from freezegun import freeze_time

from api import models
from api.controllers.comments.create_comment.controller import create_comment
from api.controllers.comments.create_comment.exceptions import CommentCreateException
from api.enums import ActionType
from tests.fixtures.database import db, run_pre_start_sql_script


@pytest.mark.asyncio
async def test_create_comment_success(
    db,
    pre_start_sql_script,
    run_pre_start_sql_script,
    user,
):
    await run_pre_start_sql_script(pre_start_sql_script)

    comment_id = await create_comment(
        comment_text='Sample comment text',
        user=user,
        order_id=1,
        order_filters=[],
    )

    assert comment_id == 1


@pytest.mark.asyncio
@freeze_time('2025-04-14T12:00:00Z')
async def test_history_was_writen_on_create_comment(
    db,
    pre_start_sql_script,
    run_pre_start_sql_script,
    user,
):
    await run_pre_start_sql_script(pre_start_sql_script)

    order_id = 1

    comment_id = await create_comment(
        comment_text='Sample comment text',
        user=user,
        order_id=order_id,
        order_filters=[],
    )

    history = await models.History.get(id=1)
    assert history.model_type == 'Order'
    assert history.model_id == order_id

    assert history.action_type == ActionType.CREATE_COMMENT

    action_data = history.action_data
    assert action_data.get('id') == comment_id
    assert action_data.get('text') == 'Sample comment text'

    assert history.initiator_type == 'User'
    assert history.initiator_role == 'service_manager'
    assert history.initiator_id == 1
    assert history.created_at.strftime('%Y-%m-%dT%H:%M:%S%z') == '2025-04-14T17:00:00+0000'


@pytest.mark.asyncio
async def test_create_comment_with_nonexisting_order(
    db,
    pre_start_sql_script,
    run_pre_start_sql_script,
    user,
):
    await run_pre_start_sql_script(pre_start_sql_script)

    with pytest.raises(CommentCreateException, match='Order does not exist'):
        await create_comment(
            comment_text='Sample comment text',
            user=user,
            order_id=100,
            order_filters=[],
        )
