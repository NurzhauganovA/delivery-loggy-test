import pytest
from fastapi_pagination import set_page

from api.schemas import pagination
from api.schemas.mobile import GetHistoryResponse
from tests.fixtures.default_pre_start_sql_scripts import (
    default_groups_insert_script,
    default_permissions_insert_script,
    default_groups_permissions_insert_script,
    default_countries_insert_script,
    default_cities_insert_script,
    statuses_insert_script
)
from tests.utils import json_fixture, query


@pytest.fixture
def setting_page_type() -> None:
    """fastapi_pagination под капотом при HTTP вызове сам устанавливаем тип для page"""
    set_page(pagination.Page[GetHistoryResponse])


@pytest.fixture
def expected() -> dict:
    return {
        "current_page": 1,
        "items": [
            {
                "action_data": {"id": 2, "text": "Все норм"},
                "action_type": "create_comment",
                "created_at": "2024-02-08T06:13:00.160374+00:00",
                "images": [
                    {
                        "id": 4,
                        "image": "/media/postcontrols/413b2edd-d0b9-4908-8f8e-88e6e077f50d.jpg",
                    },
                    {
                        "id": 5,
                        "image": "/media/postcontrols/413b2edd-d0b9-4908-8f8e-88e6e077f50d.jpg",
                    },
                ],
                "initiator": {
                    "first_name": "Курьер 1",
                    "id": 2,
                    "last_name": "Курьеров 1",
                    "middle_name": "Курьерович 1",
                    "profile_types": ["supervisor"],
                },
                "initiator_id": 2,
                "initiator_role": "supervisor",
                "initiator_type": "User",
                "model_id": 1,
                "model_type": "Order",
                "request_method": "POST",
            },
            {
                "action_data": {"id": 1, "text": "Че там"},
                "action_type": "create_comment",
                "created_at": "2024-02-08T06:12:00.160374+00:00",
                "images": [
                    {
                        "id": 1,
                        "image": "/media/postcontrols/413b2edd-d0b9-4908-8f8e-88e6e077f50d.jpg",
                    },
                    {
                        "id": 2,
                        "image": "/media/postcontrols/413b2edd-d0b9-4908-8f8e-88e6e077f50d.jpg",
                    },
                    {
                        "id": 3,
                        "image": "/media/postcontrols/413b2edd-d0b9-4908-8f8e-88e6e077f50d.jpg",
                    },
                ],
                "initiator": {
                    "first_name": "Курьер 1",
                    "id": 2,
                    "last_name": "Курьеров 1",
                    "middle_name": "Курьерович 1",
                    "profile_types": ["supervisor"],
                },
                "initiator_id": 2,
                "initiator_role": "supervisor",
                "initiator_type": "User",
                "model_id": 1,
                "model_type": "Order",
                "request_method": "POST",
            },
            {
                "action_data": {"created_by": "service"},
                "action_type": None,
                "created_at": "2024-02-08T06:11:17.160374+00:00",
                "images": None,
                "initiator": {
                    "first_name": "Служба 1",
                    "id": 1,
                    "last_name": "Службавна 1",
                    "middle_name": "Службавна 1",
                    "profile_types": ["service_manager"],
                },
                "initiator_id": 1,
                "initiator_role": "service_manager",
                "initiator_type": "User",
                "model_id": 1,
                "model_type": "Order",
                "request_method": "POST",
            },
        ],
        "total": 3,
        "total_pages": 1,
    }





@pytest.fixture
def pre_start_sql_script() -> str:
    """Важен порядок скриптов, так как есть зависимость от внешних ключей у таблиц"""
    scripts = [
        default_groups_insert_script(),
        default_permissions_insert_script(),
        default_groups_permissions_insert_script(),
        default_countries_insert_script(),
        default_cities_insert_script(),
        statuses_insert_script(),
    ]

    tables_and_fixtures = {
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
        'public."order_comment"': 'order_comment',
        'public."order_comment_image"': 'order_comment_image',
        'public."order.statuses"': 'order.statuses',
        'public."history"': 'history',
    }

    for table, fixture in tables_and_fixtures.items():
        fixtures = json_fixture.get_fixture(
            'views/mobile',
            'get_history_list',
            fixture,
        )
        insert_query = query.create_insert(table, fixtures)
        scripts.append(insert_query)

    return " ".join(scripts)
