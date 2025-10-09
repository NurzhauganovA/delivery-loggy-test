import os

import pytest

from tests.fixtures.default_pre_start_sql_scripts import default_pre_start_sql_script
from tests.utils import get_sql_script_from_fixtures


@pytest.fixture
def credentials() -> dict[str, str]:
    return {
        'grant_type': 'password',
        'username': '+77777777777',
        'password': 'test'
    }


@pytest.fixture
def profile_data() -> dict[str, str]:
    return {
        'profile_type': 'service_manager',
        'profile_id': '1',
    }


@pytest.fixture
def expected() -> dict:
    return {
        "name": "Базовая кредитная карта",
        "has_postcontrol": False,
        "message_for_noncall": None,
        "upload_from_gallery": True,
        "postcontrol_configs": [
            {
                "id": 3,
                "name": "Послед контроль отмены",
                "inner_params": [
                    {
                        "id": 4,
                        "name": "Послед контроль отмены - фотография 1",
                        "send": False,
                        "document_code": None,
                        "postcontrol_documents": [
                            {
                                "id": 3,
                                "image": "/media/postcontrols/240ec173-8c4b-4f2a-8953-e6dd997ba8c4.jpg",
                                "resolution": "accepted",
                                "comment": None,
                            }
                        ],
                    },
                    {
                        "id": 5,
                        "name": "Послед контроль отмены - фотография 2",
                        "send": False,
                        "document_code": None,
                        "postcontrol_documents": [
                            {
                                "id": 4,
                                "image": "/media/postcontrols/240ec173-8c4b-4f2a-8953-e6dd997ba8c4.jpg",
                                "resolution": "accepted",
                                "comment": None,
                            }
                        ],
                    },
                ],
                "postcontrol_documents": [],
            },
            {
                "id": 1,
                "name": "Фотография последконтроля",
                "inner_params": [],
                "postcontrol_documents": [
                    {
                        "id": 1,
                        "image": "/media/postcontrols/453cd1b1-1379-4723-ad47-bac2560394fd.jpg",
                        "resolution": "accepted",
                        "comment": None,
                    }
                ],
            },
            {
                "id": 2,
                "name": "Фотография последконтроля 1",
                "inner_params": [],
                "postcontrol_documents": [
                    {
                        "id": 2,
                        "image": "/media/postcontrols/240ec173-8c4b-4f2a-8953-e6dd997ba8c4.jpg",
                        "resolution": "accepted",
                        "comment": None,
                    }
                ],
            },
        ],
        "postcontrol_cancellation_configs": [],
        "accepted_delivery_statuses": [],
    }


@pytest.fixture
def fixtures() -> dict:
    return {
        'public."user"': 'user',
        'public."partner"': 'partner',
        'public."profile_service_manager"': 'profile_service_manager',
        'public."groups_user"': 'groups_user',
        'public."item"': 'item',
        'public."item_city"': 'item_city',
        'public."deliverygraph"': 'deliverygraph',
        'public."delivery_point"': 'delivery_point',
        'public."area"': 'area',
        'public."profile_courier"': 'profile_courier',
        'public."profile_courier_area"': 'profile_courier_area',
        'public."order"': 'order',
        'public."order_sms_postcontrols"': 'order_sms_postcontrols',
        'public."postcontrol_configs"': 'postcontrol_configs',
        'public."order.postcontrols"': 'order.postcontrols'
    }


@pytest.fixture
def pre_start_sql_script(request, fixtures, default_pre_start_sql_script) -> str:
    current_test_sql_scripts = get_sql_script_from_fixtures(
        current_dir=os.path.dirname(str(request.fspath)),
        fixtures=fixtures,
    )

    return default_pre_start_sql_script + current_test_sql_scripts