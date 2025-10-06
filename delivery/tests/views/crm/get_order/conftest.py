import pytest

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
def expected() -> dict:
    return {
        "id": 1,
        "type": "planned",
        "delivery_datetime": "2024-02-20T23:59:00+00:00",
        "delivery_status": {
            "status": "is_delivered",
            "datetime": None,
            "comment": None,
            "reason": None,
        },
        "receiver_iin": "860824302113",
        "receiver_name": "МАТАШЕВ АКБАР МУСЛИМЖАНОВИЧ",
        "receiver_phone_number": "+77781254616",
        "comment": None,
        "created_by": "integration",
        "idn": None,
        "initial_delivery_datetime": None,
        "created_at": "2024-02-08T06:11:17.160374+00:00",
        "courier": {
            "id": 1,
            "user": {
                "id": 2,
                "phone_number": "+77777777771",
                "first_name": "Курьер 1",
                "middle_name": "Курьерович 1",
                "last_name": "Курьеров 1",
            },
        },
        "city": {"id": 1, "name": "Almaty", "timezone": "Asia/Aqtau"},
        "area": {"id": 1, "slug": "Весь город Алматы"},
        "partner": {
            "id": 1,
            "name": "Курьерская Служба 1",
            "article": "ОB",
            "courier_partner_id": None,
        },
        "shipment_point": None,
        "delivery_point": {
            "id": 1,
            "latitude": 43.165452,
            "longitude": 76.874013,
            "address": "Казахстан, Алматы, Алматы, Микрорайон Каргалы, д.25",
        },
        "item": {
            "name": "Базовая кредитная карта",
            "has_postcontrol": True,
            "message_for_noncall": 'Здравствуйте! Курьер не смог дозвониться до Вас. Просьба перезвонить по этому номеру',
            "upload_from_gallery": True,
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
                                    'comment': None,
                                     'id': 3,
                                     'image': '/media/postcontrols/240ec173-8c4b-4f2a-8953-e6dd997ba8c4.jpg',
                                     'resolution': 'accepted'
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
                                    'comment': None,
                                 'id': 4,
                                 'image': '/media/postcontrols/240ec173-8c4b-4f2a-8953-e6dd997ba8c4.jpg',
                                 'resolution': 'accepted'
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
                    "name": "Фотография последконтроля",
                    "inner_params": [],
                    "postcontrol_documents": [
                        {
                            "id": 1,
                            "image": "/media/postcontrols/453cd1b1-1379-4723-ad47-bac2560394fd.jpg",
                            "resolution": "accepted",
                            "comment": None
                        }
                    ]
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
                            "comment": None
                        }
                    ]
                }
            ],
            "accepted_delivery_statuses": [
                'on-the-way-to-call-point',
                'is_delivered',
                'cancelled',
                'postponed',
                'noncall',
                'rescheduled',
                'being_finalized',
                'cancelled_at_client',
                'video_check_passed',
                'video_unavailable',
                'video_postcontrol',
                'video_postcontrol_being_finalized',
                'video_check_failed',
                'sms_postcontrol',
                'sms_postcontrol_being_finalized',
                'sms_unavailable',
                'sms_failed'
            ],
        },
        "deliverygraph_step_count": 7,
        "current_status_position": 7,
        "current_status": {
            "id": 7,
            "name": None,
            "icon": "order_delivevred",
            "slug": "dostavleno",
        },
        "manager": None,
        "product": None,
        "deliverygraph": {
            "graph": [
                {
                    "id": 1,
                    "position": 1,
                    "name": "Новая заявка",
                    "slug": "novaia-zaiavka",
                    "icon": "order_new",
                    "button_name": None,
                    "transitions": None,
                    "status": None,
                },
                {
                    "id": 2,
                    "position": 2,
                    "name": "Курьер назначен",
                    "slug": "kurer-naznachen",
                    "icon": "courier_appointed",
                    "button_name": "Принять в работу",
                    "transitions": None,
                    "status": None,
                },
                {
                    "id": 3,
                    "position": 3,
                    "name": "Принято курьером в работу",
                    "slug": "priniato-kurerom-v-rabotu",
                    "icon": "courier_accepted",
                    "button_name": "К точке доставки",
                    "transitions": None,
                    "status": None,
                },
                {
                    "id": 4,
                    "position": 4,
                    "name": "В пути к точке доставки",
                    "slug": "v-puti-k-tochke-dostavki",
                    "icon": "otw_delivery_point",
                    "button_name": "На точке доставки",
                    "transitions": None,
                    "status": None,
                },
                {
                    "id": 5,
                    "position": 5,
                    "name": "На точке доставки",
                    "slug": "na-tochke-dostavki",
                    "icon": "on_delivery_point",
                    "button_name": "Контакт с получателем",
                    "transitions": None,
                    "status": None,
                },
                {
                    "id": 6,
                    "position": 6,
                    "name": "Контакт с получателем",
                    "slug": "kontakt-s-poluchatelem",
                    "icon": "at_client",
                    "button_name": "Посылка передана",
                    "transitions": None,
                    "status": None,
                },
                {
                    "id": 7,
                    "position": 7,
                    "name": "Доставлено",
                    "slug": "dostavleno",
                    "icon": "order_delivered",
                    "button_name": None,
                    "transitions": None,
                    "status": None,
                },
            ]
        },
        "statuses": [
            {
                "created_at": "2024-02-08T06:11:17.160374+00:00",
                "status": {
                    "after": [],
                    "icon": "order_new",
                    "id": 1,
                    "is_optional": False,
                    "name": None,
                    "partner_id": None,
                    "slug": "novaia-zaiavka",
                },
            },
            {
                "created_at": "2024-02-08T08:11:17.160374+00:00",
                "status": {
                    "after": [
                        {"id": 2, "name": "Курьер назначен"},
                        {"id": 9, "name": "Подготовка к отправке"},
                    ],
                    "icon": "courier_accepted",
                    "id": 3,
                    "is_optional": False,
                    "name": None,
                    "partner_id": None,
                    "slug": "priniato-kurerom-v-rabotu",
                },
            },
            {
                "created_at": "2024-02-08T09:11:17.160374+00:00",
                "status": {
                    "after": [
                        {"id": 3, "name": "Принято курьером в работу"},
                        {"id": 11, "name": "На точке вывоза"},
                    ],
                    "icon": "otw_delivery_point",
                    "id": 4,
                    "is_optional": False,
                    "name": None,
                    "partner_id": None,
                    "slug": "v-puti-k-tochke-dostavki",
                },
            },
            {
                "created_at": "2025-02-08T07:11:17.160374+00:00",
                "status": {
                    "after": [{"id": 1, "name": "Новая заявка"}],
                    "icon": "courier_appointed",
                    "id": 2,
                    "is_optional": False,
                    "name": None,
                    "partner_id": None,
                    "slug": "kurer-naznachen",
                },
            },
        ],
        "last_otp": None,
        "actual_delivery_datetime": "2024-02-20T11:21:50.279633+00:00",
        "courier_assigned_at": "2025-02-08T07:11:17.160374+00:00",
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
        "courier_service": None,
        "track_number": None,
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
        'public."postcontrol_configs"': 'postcontrol_configs',
        'public."order.postcontrols"': 'order.postcontrols',
        'public."order_comment"': 'order_comment',
        'public."order_comment_image"': 'order_comment_image',
        'public."order.statuses"': 'order.statuses',
    }

    for table, fixture in tables_and_fixtures.items():
        fixtures = json_fixture.get_fixture(
            'views/crm',
            'get_order',
            fixture,
        )
        insert_query = query.create_insert(table, fixtures)
        scripts.append(insert_query)

    return " ".join(scripts)
