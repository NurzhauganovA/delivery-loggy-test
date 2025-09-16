import os
import json
from datetime import datetime

import pytest

from api.services.excel_loader.excel_loader import(
    prepare_orders_for_report,
)
from tests.fixtures.database import(
    db,
    run_pre_start_sql_script,
)

from delivery.tests.conftest import CUR_DIR


CASES_PATH = f'{CUR_DIR}/controllers/prepare_orders_for_report/cases'


@pytest.mark.asyncio
async def test_prepare_orders_for_report_other(
    db,
    pre_start_sql_script,
    run_pre_start_sql_script,
    ):

    await run_pre_start_sql_script(pre_start_sql_script)

    path = f'{CASES_PATH}/other.json'
    with open(path) as file:
        fixture = json.load(file)
        values = fixture['values']
        columns = values['columns']
        kwargs = values['kwargs']
        current_status_created_at__range = kwargs.get('current_status__created_at__range')
        if current_status_created_at__range:
            new_create_ad = []
            for element in current_status_created_at__range:
                new_create_ad.append(
                    datetime.strptime(element, '%Y-%m-%dT%H:%M:%S')
                )
            kwargs['current_status__created_at__range'] = new_create_ad

        expected = fixture['expected']

    response = await prepare_orders_for_report(columns=columns, **kwargs)
    courier_appointed_at = datetime.strftime(response[0][-2], '%Y-%m-%d %H:%M:%S')

    assert courier_appointed_at == expected


@pytest.mark.asyncio
async def test_prepare_orders_for_report_bank_manager(
    db,
    pre_start_sql_script,
    run_pre_start_sql_script,
    ):

    await run_pre_start_sql_script(pre_start_sql_script)

    path = f'{CASES_PATH}/bank_manager.json'
    with open(path) as file:
        fixture = json.load(file)
        values = fixture['values']
        columns = values['columns']
        kwargs = values['kwargs']
        current_status_created_at__range = kwargs.get('current_status__created_at__range')
        if current_status_created_at__range:
            new_create_ad = []
            for element in current_status_created_at__range:
                new_create_ad.append(
                    datetime.strptime(element, '%Y-%m-%dT%H:%M:%S')
                )
            kwargs['current_status__created_at__range'] = new_create_ad

        expected = fixture['expected']

    response = await prepare_orders_for_report(columns=columns, **kwargs)
    courier_appointed_at = datetime.strftime(response[0][-3], '%Y-%m-%d %H:%M:%S')

    assert courier_appointed_at == expected
