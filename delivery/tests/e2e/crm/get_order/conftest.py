import os

import pytest
from _pytest.fixtures import FixtureRequest

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
        "actual_delivery_datetime": "2024-02-20T11:21:50.279633+00:00",
        "area": {"id": 1, "slug": "Весь город Алматы"},
        "city": {"id": 1, "name": "Almaty", "timezone": "Asia/Aqtau"},
        "comment": None,
        "comments": [
            {
                "created_at": "2024-02-09T12:10:10+00:00",
                "id": 2,
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
                "order_id": 1,
                "text": "Все норм",
                "user_id": 2,
                "user_name": "Служба 1 Службавна 1 Службавна 1",
                "user_role": {"name": "Менеджер", "slug": "service_manager"},
            },
            {
                "created_at": "2024-02-09T10:10:10+00:00",
                "id": 1,
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
                "order_id": 1,
                "text": "Че там",
                "user_id": 1,
                "user_name": "Курьер 1 Курьеров 1 Курьерович 1",
                "user_role": {"name": "Курьер", "slug": "courier"},
            },
        ],
        "courier": {
            "id": 1,
            "user": {
                "first_name": "Курьер 1",
                "id": 2,
                "last_name": "Курьеров 1",
                "middle_name": "Курьерович 1",
                "phone_number": "+77777777771",
            },
        },
        "courier_assigned_at": "2025-02-08T07:11:17.160374+00:00",
        "created_at": "2024-02-08T06:11:17.160374+00:00",
        "created_by": "integration",
        "current_status": {
            "icon": "order_delivered",
            "id": 7,
            "name": "Delivered",
            "slug": "dostavleno",
        },
        "current_status_position": 7,
        "delivery_datetime": "2024-02-20T23:59:00+00:00",
        "delivery_point": {
            "address": "Казахстан, Алматы, Алматы, Микрорайон Каргалы, " "д.25",
            "id": 1,
            "latitude": 43.165452,
            "longitude": 76.874013,
        },
        "delivery_status": {
            "comment": None,
            "datetime": None,
            "reason": None,
            "status": "is_delivered",
        },
        "deliverygraph": {
            "graph": [
                {
                    "button_name": None,
                    "icon": "order_new",
                    "id": 1,
                    "name": "Новая заявка",
                    "position": 1,
                    "slug": "novaia-zaiavka",
                    "status": None,
                    "transitions": None,
                },
                {
                    "button_name": "Принять в работу",
                    "icon": "courier_appointed",
                    "id": 2,
                    "name": "Курьер назначен",
                    "position": 2,
                    "slug": "kurer-naznachen",
                    "status": None,
                    "transitions": None,
                },
                {
                    "button_name": "К точке доставки",
                    "icon": "courier_accepted",
                    "id": 3,
                    "name": "Принято курьером в работу",
                    "position": 3,
                    "slug": "priniato-kurerom-v-rabotu",
                    "status": None,
                    "transitions": None,
                },
                {
                    "button_name": "На точке доставки",
                    "icon": "otw_delivery_point",
                    "id": 4,
                    "name": "В пути к точке доставки",
                    "position": 4,
                    "slug": "v-puti-k-tochke-dostavki",
                    "status": None,
                    "transitions": None,
                },
                {
                    "button_name": "Контакт с получателем",
                    "icon": "on_delivery_point",
                    "id": 5,
                    "name": "На точке доставки",
                    "position": 5,
                    "slug": "na-tochke-dostavki",
                    "status": None,
                    "transitions": None,
                },
                {
                    "button_name": "Посылка передана",
                    "icon": "at_client",
                    "id": 6,
                    "name": "Контакт с получателем",
                    "position": 6,
                    "slug": "kontakt-s-poluchatelem",
                    "status": None,
                    "transitions": None,
                },
                {
                    "button_name": None,
                    "icon": "order_delivered",
                    "id": 7,
                    "name": "Доставлено",
                    "position": 7,
                    "slug": "dostavleno",
                    "status": None,
                    "transitions": None,
                },
            ]
        },
        "deliverygraph_step_count": 7,
        "id": 1,
        "idn": None,
        "initial_delivery_datetime": None,
        "item": {
            "accepted_delivery_statuses": [
                "on-the-way-to-call-point",
                "is_delivered",
                "cancelled",
                "postponed",
                "noncall",
                "rescheduled",
                "being_finalized",
                "cancelled_at_client",
                "video_check_passed",
                "video_unavailable",
                "video_postcontrol",
                "video_postcontrol_being_finalized",
                "video_check_failed",
                "sms_postcontrol",
                "sms_postcontrol_being_finalized",
                "sms_unavailable",
                "sms_failed",
            ],
            "has_postcontrol": True,
            "message_for_noncall": "Здравствуйте! Курьер не смог дозвониться до "
            "Вас. Просьба перезвонить по этому номеру",
            "name": "Базовая кредитная карта",
            "postcontrol_configs": [
                {
                    "id": 3,
                    "inner_params": [
                        {
                            "document_code": None,
                            "id": 4,
                            "name": "Послед контроль " "отмены - " "фотография 1",
                            "postcontrol_documents": [
                                {
                                    "comment": None,
                                    "id": 3,
                                    "image": "/media/postcontrols/240ec173-8c4b-4f2a-8953-e6dd997ba8c4.jpg",
                                    "resolution": "accepted",
                                }
                            ],
                            "send": False,
                        },
                        {
                            "document_code": None,
                            "id": 5,
                            "name": "Послед контроль " "отмены - " "фотография 2",
                            "postcontrol_documents": [
                                {
                                    "comment": None,
                                    "id": 4,
                                    "image": "/media/postcontrols/240ec173-8c4b-4f2a-8953-e6dd997ba8c4.jpg",
                                    "resolution": "accepted",
                                }
                            ],
                            "send": False,
                        },
                    ],
                    "name": "Послед контроль отмены",
                    "postcontrol_documents": [],
                },
                {
                    "id": 1,
                    "inner_params": [],
                    "name": "Фотография последконтроля",
                    "postcontrol_documents": [
                        {
                            "comment": None,
                            "id": 1,
                            "image": "/media/postcontrols/453cd1b1-1379-4723-ad47-bac2560394fd.jpg",
                            "resolution": "accepted",
                        }
                    ],
                },
                {
                    "id": 2,
                    "inner_params": [],
                    "name": "Фотография последконтроля 1",
                    "postcontrol_documents": [
                        {
                            "comment": None,
                            "id": 2,
                            "image": "/media/postcontrols/240ec173-8c4b-4f2a-8953-e6dd997ba8c4.jpg",
                            "resolution": "accepted",
                        }
                    ],
                },
            ],
            "upload_from_gallery": True,
        },
        "last_otp": None,
        "manager": None,
        "partner": {
            "article": "ОB",
            "courier_partner_id": None,
            "id": 1,
            "name": "Курьерская Служба 1",
        },
        "product": None,
        "receiver_iin": "860824302113",
        "receiver_name": "МАТАШЕВ АКБАР МУСЛИМЖАНОВИЧ",
        "receiver_phone_number": "+77781254616",
        "shipment_point": None,
        "statuses": [
            {
                "created_at": "2024-02-08T06:11:17.160374+00:00",
                "status": {
                    "after": None,
                    "icon": "order_new",
                    "id": 1,
                    "is_optional": False,
                    "name": "New order",
                    "partner_id": None,
                    "slug": "novaia-zaiavka",
                },
            },
            {
                "created_at": "2024-02-08T08:11:17.160374+00:00",
                "status": {
                    "after": None,
                    "icon": "courier_accepted",
                    "id": 3,
                    "is_optional": False,
                    "name": "Accepted by courier for processing",
                    "partner_id": None,
                    "slug": "priniato-kurerom-v-rabotu",
                },
            },
            {
                "created_at": "2024-02-08T09:11:17.160374+00:00",
                "status": {
                    "after": None,
                    "icon": "on_delivery_point",
                    "id": 4,
                    "is_optional": False,
                    "name": "On the way to delivery point",
                    "partner_id": None,
                    "slug": "v-puti-k-tochke-dostavki",
                },
            },
            {
                "created_at": "2025-02-08T07:11:17.160374+00:00",
                "status": {
                    "after": None,
                    "icon": "courier_appointed",
                    "id": 2,
                    "is_optional": False,
                    "name": "Courier assigned",
                    "partner_id": None,
                    "slug": "kurer-naznachen",
                },
            },
        ],
        "type": "planned",
        "courier_service": "cdek",
        "track_number": "111111111",
    }


@pytest.fixture
def fixtures()-> dict:
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
        'public."postcontrol_configs"': 'postcontrol_configs',
        'public."order.postcontrols"': 'order.postcontrols',
        'public."order_comment"': 'order_comment',
        'public."order_comment_image"': 'order_comment_image',
        'public."order.statuses"': 'order.statuses',
    }


@pytest.fixture
def pre_start_sql_script(
    request: FixtureRequest,
    fixtures: dict,
    default_pre_start_sql_script: str,
) -> str:
    """
    Сборка всех SQL запросов из json
    Склеивание с устаревшими запросами, для совместимости

    Args:
        request: глобальный объект Pytest
        fixtures: список фикстур. Парсится из словаря выше
        default_pre_start_sql_script: легаси sql запросы

    Returns:
        SQL запрос спарсенный из фикстур
    """

    current_test_sql_scripts = get_sql_script_from_fixtures(
        current_dir=os.path.dirname(str(request.fspath)),
        fixtures=fixtures,
    )

    return default_pre_start_sql_script + current_test_sql_scripts
