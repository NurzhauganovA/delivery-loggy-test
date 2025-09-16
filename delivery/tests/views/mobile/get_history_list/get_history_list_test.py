import json

import pytest

from api.schemas import pagination
from api.schemas.mobile.get_history import HistoryFilterParams
from api.views.mobile import get_history_list
from tests.fixtures.database import db, run_pre_start_sql_script


@pytest.mark.asyncio
async def test_get_history_list(
        db,
        pre_start_sql_script,
        run_pre_start_sql_script,
        setting_page_type,
        expected,
):
    """
        Получение истории заявки для mobile
    """
    await run_pre_start_sql_script(pre_start_sql_script)

    pagination_params = pagination.Params(
        page=1,
        page_limit=10,
    )

    filter_params = HistoryFilterParams(
        model_id=1,
        model_type='Order'
    )

    result = await get_history_list(
        pagination_params=pagination_params,
        filter_params=filter_params,
    )

    assert json.loads(result.json()) == expected


@pytest.mark.asyncio
async def test_pagination(
        db,
        pre_start_sql_script,
        run_pre_start_sql_script,
        setting_page_type,
        expected,
):
    """
        Получение истории заявки с пагинацией
    """
    await run_pre_start_sql_script(pre_start_sql_script)

    pagination_params = pagination.Params(
        page=2,
        page_limit=2,
    )

    result = await get_history_list(
        pagination_params=pagination_params,
        filter_params=None,
    )


    assert len(result.items) == 2
    assert result.current_page == 2
    assert result.total_pages == 2
    assert result.total == 4


@pytest.mark.asyncio
async def test_pagination_is_none_validation_error(
        db,
        pre_start_sql_script,
        run_pre_start_sql_script,
        setting_page_type,
        expected,
):
    """
        Получение истории заявки с без пагинации
    """
    await run_pre_start_sql_script(pre_start_sql_script)

    with pytest.raises(ValueError, match='pagination_params is required'):
        await get_history_list(
            pagination_params=None,
            filter_params=None,
        )


@pytest.mark.asyncio
async def test_filter_by_model_id(
        db,
        pre_start_sql_script,
        run_pre_start_sql_script,
        setting_page_type,
        expected,
):
    await run_pre_start_sql_script(pre_start_sql_script)

    pagination_params = pagination.Params(
        page=1,
        page_limit=10,
    )

    filter_params = HistoryFilterParams(model_id=4)

    result = await get_history_list(
        pagination_params=pagination_params,
        filter_params=filter_params,
    )

    assert len(result.items) == 1
    assert result.items[0].model_id == 4


@pytest.mark.asyncio
async def test_filter_by_model_type(
        db,
        pre_start_sql_script,
        run_pre_start_sql_script,
        setting_page_type,
        expected,
):
    await run_pre_start_sql_script(pre_start_sql_script)

    pagination_params = pagination.Params(
        page=1,
        page_limit=10,
    )

    filter_params = HistoryFilterParams(model_type='Item')

    result = await get_history_list(
        pagination_params=pagination_params,
        filter_params=filter_params,
    )

    assert len(result.items) == 1
    assert result.items[0].model_type == 'Item'
