import os
from unittest.mock import call

import pytest

from api.enums import OrderDeliveryStatus
from tests.fixtures.default_pre_start_sql_scripts import (
    default_groups_insert_script,
    default_permissions_insert_script,
    default_groups_permissions_insert_script,
    default_countries_insert_script,
    default_cities_insert_script,
    statuses_insert_script
)


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
def file_57_kb_png(request):
    current_dir = os.path.dirname(str(request.fspath))
    with open(f'{current_dir}/fixtures/57_kb.png', 'rb') as file:
        return ['image', (file.name, file.read(), 'image/png')]


@pytest.fixture
def file_85_kb_png(request):
    current_dir = os.path.dirname(str(request.fspath))
    with open(f'{current_dir}/fixtures/85_kb.png', 'rb') as file:
        return ['image', (file.name, file.read(), 'image/png')]


@pytest.fixture
def file_128_kb_png(request):
    current_dir = os.path.dirname(str(request.fspath))
    with open(f'{current_dir}/fixtures/128_kb.png', 'rb') as file:
        return ['image', (file.name, file.read(), 'image/png')]


@pytest.fixture
def file_151_kb_png(request):
    current_dir = os.path.dirname(str(request.fspath))
    with open(f'{current_dir}/fixtures/151_kb.png', 'rb') as file:
        return ['image', (file.name, file.read(), 'image/png')]


@pytest.fixture()
def celery_calls():
    return [
        call(
            channel='send-to-celery',
            message={
                'task_name': 'send-status',
                'kwargs': {
                    'url': 'https://example-partner.kz/api/loggy/callbacks/set-status/3928b?token=f0ce02',
                    'data': {
                        'status': OrderDeliveryStatus.IS_DELIVERED,
                        'status_datetime': '2025-07-18 11:42:00+00:00',
                        'comment': None
                    },
                    'headers': {}
                }
            }
        ),
        call(
            channel='send-to-celery',
            message={
                'task_name': 'send-photo-urls',
                'kwargs': {
                    'url': 'https://example-partner.kz/api/loggy/callbacks/set-photo/3928b?token=f0ce02',
                    'data': {
                        'files': [
                            {
                                'url': 'https://api.devloggy-1.trafficwave.kz/media/id card front.png',
                                'document_code': 'PASSPORT_PHOTO'
                            },
                            {
                                'url': 'https://api.devloggy-1.trafficwave.kz/media/id card back.png',
                                'document_code': 'PASSPORT_PHOTO'
                            },
                            {
                                'url': 'https://api.devloggy-1.trafficwave.kz/media/selfie.png',
                                'document_code': 'USER_PHOTO'
                            }
                        ]
                    },
                    'headers': {}
                }
            }
        )
    ]


@pytest.fixture
def expected():
    return [
        {
            'id': 5,
            'inner_params': [
                {
                    'document_code': None,
                    'id': 6,
                    'name': 'фото 1',
                    'postcontrol_documents': [
                        {'comment': None,
                         'id': 13,
                         'image': '/media/postcontrols/00000000-0000-0000-0000-000000000000.png',
                         'resolution': 'pending'
                         }
                    ],
                    'send': False
                },
                {
                    'document_code': None,
                    'id': 7,
                    'name': 'фото 2',
                    'postcontrol_documents': [
                        {
                            'comment': None,
                            'id': 14,
                            'image': '/media/postcontrols/00000000-0000-0000-0000-000000000001.png',
                            'resolution': 'pending'
                        }
                    ],
                    'send': False
                },
                {
                    'document_code': None,
                    'id': 8,
                    'name': 'фото 3',
                    'postcontrol_documents': [
                        {
                            'comment': None,
                            'id': 15,
                            'image': '/media/postcontrols/00000000-0000-0000-0000-000000000002.png',
                            'resolution': 'pending'
                        }
                    ],
                    'send': False
                },
                {
                    'document_code': None,
                    'id': 9,
                    'name': 'фото 4',
                    'postcontrol_documents': [
                        {
                            'comment': None,
                            'id': 16,
                            'image': '/media/postcontrols/00000000-0000-0000-0000-000000000003.png',
                            'resolution': 'pending'
                        }
                    ],
                    'send': False
                },
                {
                    'document_code': None,
                    'id': 10,
                    'name': 'фото 5',
                    'postcontrol_documents': [],
                    'send': False
                }
            ],
            'name': 'Фотографии для отмены',
            'postcontrol_documents': []
        }
    ]


@pytest.fixture
def expected_decline():
    return [
        {
            'comment': 'Fix it',
            'config_id': 2,
            'id': 1,
            'image': '/media/id card front.png',
            'order_id': 1,
            'resolution': 'declined',
            'type': 'post_control'
        },
        {
            'comment': 'Fix it',
            'config_id': 3,
            'id': 2,
            'image': '/media/id card back.png',
            'order_id': 1,
            'resolution': 'declined',
            'type': 'post_control'
        },
        {
            'comment': None,
            'config_id': 4,
            'id': 3,
            'image': '/media/selfie.png',
            'order_id': 1,
            'resolution': 'accepted',
            'type': 'post_control'
        }
    ]


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
        users_insert_script(),
        partners_insert_script(),
        profile_service_manager_insert_script(),
        groups_users_insert_script(),
        item_insert_script(),
        postcontrol_config_insert_script(),
        delivery_graphs_insert_script(),
        delivery_points_insert_script(),
        orders_insert_script(),
        order_statuses_insert_script(),
        order_postcontrol_insert_script(),
    ]

    return " ".join(scripts)


def users_insert_script() -> str:
    """
        password: test
    """
    return """
           INSERT INTO public."user" (id, phone_number, first_name, last_name, middle_name, iin, credentials, is_active,
                                      photo, personal_agreement, created_at, is_superuser, email, password)
           VALUES (1, '+77777777777', 'Служба 1', 'Службавна 1', 'Службавна 1', null, null, true, '', null,
                   '2023-01-13 12:08:19.000000 +00:00', false, 'test_1@gmail.com',
                   '$2b$12$KzP.BVjQGSu4O/D9XajUP.UikCQ4SWC47mr9XMDztCroWFiHmC2zy');

           INSERT INTO public."user" (id, phone_number, first_name, last_name, middle_name, iin, credentials, is_active,
                                      photo, personal_agreement, created_at, is_superuser, email, password)
           VALUES (2, '+77777777771', 'Курьер 1', 'Курьеров 1', 'Курьерович 1', null, null, true, '', null,
                   '2023-01-13 12:08:19.000000 +00:00', false, 'courier_1@gmail.com',
                   '$2b$12$KzP.BVjQGSu4O/D9XajUP.UikCQ4SWC47mr9XMDztCroWFiHmC2zy'); 
           """


def partners_insert_script() -> str:
    return """
           INSERT INTO public.partner (id, name_kk, name_ru, name_en, activity_name_ru, address, affiliated, article,
                                       identifier, is_commerce, leader_data, consent_confirmed, is_government,
                                       is_international, email, registration_date, liq_date, liq_decision_date,
                                       credentials, courier_partner_id, created_at, start_work_hour, end_work_hour,
                                       type)
           VALUES (1, 'Курьерская Служба 1', 'Курьерская Служба 1', null, null,
                   'город Алматы, Алмалинский район, Проспект АБЫЛАЙ ХАНА, дом: 91', false, 'ОB', '111111111111', true,
                   '{"iin": "721107450542", "last_name": "ИБРАГИМОВА", "first_name": "ЛЯЗЗАТ", "middle_name": "ЕРКЕНОВНА"}',
                   null, null, false, null, '2003-07-10 00:00:00.000000 +00:00', null, null, null, null,
                   '2022-09-21 11:10:54.873492 +00:00', null, null, 'too');

           INSERT INTO public.partner (id, name_kk, name_ru, name_en, activity_name_ru, address, affiliated, article,
                                       identifier, is_commerce, leader_data, consent_confirmed, is_government,
                                       is_international, email, registration_date, liq_date, liq_decision_date,
                                       credentials, courier_partner_id, created_at, start_work_hour, end_work_hour,
                                       type)
           VALUES (2, 'Партнер 1', 'Партнер 1', null, null,
                   'город Алматы, Алмалинский район, Проспект АБЫЛАЙ ХАНА, дом: 91', false, 'ОB', '111111111112', true,
                   '{"iin": "721107450542", "last_name": "ИБРАГИМОВА", "first_name": "ЛЯЗЗАТ", "middle_name": "ЕРКЕНОВНА"}',
                   null, null, false, null, '2003-07-10 00:00:00.000000 +00:00', null, null, null, 1,
                   '2022-09-21 11:10:54.873492 +00:00', null, null, 'too');

           INSERT INTO public.partner (id, name_kk, name_ru, name_en, activity_name_ru, address, affiliated, article,
                                       identifier, is_commerce, leader_data, consent_confirmed, is_government,
                                       is_international, email, registration_date, liq_date, liq_decision_date,
                                       credentials, courier_partner_id, created_at, start_work_hour, end_work_hour,
                                       type)
           VALUES (3, 'Партнер 2', 'Партнер 2', null, null,
                   'город Алматы, Алмалинский район, Проспект АБЫЛАЙ ХАНА, дом: 91', false, 'ОB', '111111111113', true,
                   '{"iin": "721107450542", "last_name": "ИБРАГИМОВА", "first_name": "ЛЯЗЗАТ", "middle_name": "ЕРКЕНОВНА"}',
                   null, null, false, null, '2003-07-10 00:00:00.000000 +00:00', null, null, null, 1,
                   '2022-09-21 11:10:54.873492 +00:00', null, null, 'too'); 
           """


def profile_service_manager_insert_script() -> str:
    return """
           INSERT INTO public.profile_service_manager (id, user_id, partner_id)
           VALUES (1, 1, 1);
           """


def groups_users_insert_script() -> str:
    return """
           INSERT INTO public.groups_user (user_id, groups_id, id)
           VALUES (1, 'service_manager', 1);
           """


def item_insert_script() -> str:
    return """
           INSERT INTO public.item (id, name, item_type, delivery_time, delivery_type, category_id, partner_id,
                                    is_delivery_point_exists, has_postcontrol, accepted_delivery_statuses, distribute,
                                    message_for_noncall, courier_appointed_sms_on, courier_appointed_sms,
                                    days_to_delivery)
           VALUES (1, 'Базовая кредитная карта', 'document', '00:00', '{planned}', null, null, true, false, null, false,
                   null, false, null, null); 
           """


def postcontrol_config_insert_script() -> str:
    return """
        INSERT INTO "public"."postcontrol_configs"
          ("id", "item_id", "name", "send", "document_code", "parent_config_id", "type")
        VALUES
          (1, 1, 'id card', true, 'PASSPORT_PHOTO', null, 'post_control'),
          (2, 1, 'front side', true, 'PASSPORT_PHOTO', 1, 'post_control'),
          (3, 1, 'back side', true, 'PASSPORT_PHOTO', 1, 'post_control'),
          (4, 1, 'selfie', true, 'USER_PHOTO', null, 'post_control'),
          (5, 1, 'Фотографии для отмены', false, null, null, 'canceled'),
          (6, 1, 'фото 1', false, null, 5, 'canceled'),
          (7, 1, 'фото 2', false, null, 5, 'canceled'),
          (8, 1, 'фото 3', false, null, 5, 'canceled'),
          (9, 1, 'фото 4', false, null, 5, 'canceled'),
          (10, 1, 'фото 5', false, null, 5, 'canceled')
        ;
    """


def delivery_graphs_insert_script() -> str:
    return """
           INSERT INTO public.deliverygraph (id, graph, partner_id, name_ru, slug, types, graph_courier, name_en, name_zh,
                                             name_kk)
           VALUES (1,
                       '[
                        {
                          "id": 1,
                          "icon": "order_new",
                          "name": "Новая заявка",
                          "slug": "novaia-zaiavka",
                          "position": 1,
                          "button_name": null
                        },
                        {
                          "id": 2,
                          "icon": "courier_appointed",
                          "name": "Курьер назначен",
                          "slug": "kurer-naznachen",
                          "position": 2,
                          "button_name": "Принять в работу"
                        },
                        {
                          "id": 3,
                          "icon": "courier_accepted",
                          "name": "Принято курьером в работу",
                          "slug": "priniato-kurerom-v-rabotu",
                          "position": 3,
                          "button_name": "К точке вывоза"
                        },
                        {
                          "id": 4,
                          "icon": "otw_delivery_point",
                          "name": "В пути к точке доставки",
                          "slug": "v-puti-k-tochke-dostavki",
                          "position": 4,
                          "button_name": "На точке доставки"
                        },
                        {
                          "id": 5,
                          "icon": "on_delivery_point",
                          "name": "На точке доставки",
                          "slug": "na-tochke-dostavki",
                          "position": 5,
                          "button_name": "Контакт с получателем"
                        },
                        {
                          "id": 6,
                          "icon": "at_client",
                          "name": "Контакт с получателем",
                          "slug": "kontakt-s-poluchatelem",
                          "position": 6,
                          "button_name": "Начать фотографирование"
                        },
                        {
                          "id": 16,
                          "icon": "post_control",
                          "name": "Фотографирование",
                          "slug": "fotografirovanie",
                          "position": 7,
                          "button_name": "Отправить на последконтроль"
                        },
                        {
                          "id": 12,
                          "icon": "post_control",
                          "name": "Последконтроль",
                          "slug": "posledkontrol",
                          "position": 8,
                          "button_name": null
                        },
                        {
                          "id": 7,
                          "icon": "order_delivered",
                          "name": "Доставлено",
                          "slug": "dostavleno",
                          "position": 9,
                          "button_name": null
                        }
                      ]',
                   null, 'Базовый', null, '{urgent,operative,planned}', '[]',
                   null, null, null); 
           """


def delivery_points_insert_script() -> str:
    return """
           INSERT INTO public.delivery_point (id, address, latitude, longitude)
           VALUES (1, 'Казахстан, Алматы, Алматы, Микрорайон Каргалы, д.25', 43.16545200, 76.87401300); 
           """


def orders_insert_script() -> str:
    return """
           INSERT INTO public."order" (
                id, type, created_at, delivery_datetime,
                delivery_status,
                receiver_name, receiver_iin, receiver_phone_number,
                city_id, item_id, partner_id, partner_order_id,
                archived, created_by, deliverygraph_id,
                callbacks,
                allow_courier_assign, actual_delivery_datetime, current_status_id, delivery_point_id
            )
           VALUES
            (
                1, 'planned', '2025-04-14T12:00:00+00:00', '2025-04-14T12:00:00+00:00',
                '{
                    "status": "on-the-way-to-call-point",
                    "datetime": null,
                    "comment": null,
                    "reason": null
                }',
                 'МАТАШЕВ АКБАР МУСЛИМЖАНОВИЧ', '860824302113', '+77781254616',
                1, 1, 3, '2151251251',
                false, 'integration', 1,
                '{
                    "set_otp": "https://example-partner.kz/api/loggy/callbacks/set-otp/3928b?token=f0ce02",
                    "set_pan": "https://example-partner.kz/api/loggy/callbacks/set-pan/3928b?token=f0ce02",
                    "set_status": "https://example-partner.kz/api/loggy/callbacks/set-status/3928b?token=f0ce02",
                    "send_photo_urls": "https://example-partner.kz/api/loggy/callbacks/set-photo/3928b?token=f0ce02"
                }',
                true, null, 12, 1
            ),
            (
                2, 'planned', '2025-04-14T12:00:00+00:00', '2025-04-14T12:00:00+00:00',
                '{
                    "status": "is_delivered",
                    "datetime": null,
                    "comment": null,
                    "reason": null
                }',
                 'МАТАШЕВ АКБАР МУСЛИМЖАНОВИЧ', '860824302113', '+77781254616',
                1, 1, 3, 'q34q34623463',
                false, 'integration', 1,
                '{
                    "set_otp": "https://example-partner.kz/api/loggy/callbacks/set-otp/3928b?token=f0ce02",
                    "set_pan": "https://example-partner.kz/api/loggy/callbacks/set-pan/3928b?token=f0ce02",
                    "set_status": "https://example-partner.kz/api/loggy/callbacks/set-status/3928b?token=f0ce02",
                    "send_photo_urls": "https://example-partner.kz/api/loggy/callbacks/set-photo/3928b?token=f0ce02"
                }',
                true, null, 7, 1
            ),
            (
                3, 'planned', '2025-04-14T12:00:00+00:00', '2025-04-14T12:00:00+00:00',
                '{
                    "status": null,
                    "datetime": null,
                    "comment": null,
                    "reason": null
                }',
                 'МАТАШЕВ АКБАР МУСЛИМЖАНОВИЧ', '860824302113', '+77781254616',
                1, 1, 3, 'aeth45hw5h',
                false, 'integration', 1,
                '{
                    "set_otp": "https://example-partner.kz/api/loggy/callbacks/set-otp/3928b?token=f0ce02",
                    "set_pan": "https://example-partner.kz/api/loggy/callbacks/set-pan/3928b?token=f0ce02",
                    "set_status": "https://example-partner.kz/api/loggy/callbacks/set-status/3928b?token=f0ce02",
                    "send_photo_urls": "https://example-partner.kz/api/loggy/callbacks/set-photo/3928b?token=f0ce02"
                }',
                true, null, 7, 1
            ),
            (
                4, 'planned', '2025-04-14T12:00:00+00:00', '2025-04-14T12:00:00+00:00',
                '{
                    "status": null,
                    "datetime": null,
                    "comment": null,
                    "reason": null
                }',
                 'МАТАШЕВ АКБАР МУСЛИМЖАНОВИЧ', '860824302113', '+77781254616',
                1, 1, 3, '3raergaf',
                false, 'integration', 1,
                '{
                    "set_otp": "https://example-partner.kz/api/loggy/callbacks/set-otp/3928b?token=f0ce02",
                    "set_pan": "https://example-partner.kz/api/loggy/callbacks/set-pan/3928b?token=f0ce02",
                    "set_status": "https://example-partner.kz/api/loggy/callbacks/set-status/3928b?token=f0ce02",
                    "send_photo_urls": "https://example-partner.kz/api/loggy/callbacks/set-photo/3928b?token=f0ce02"
                }',
                true, null, 12, 1
            ),
            (
                5, 'planned', '2025-04-14T12:00:00+00:00', '2025-04-14T12:00:00+00:00',
                '{
                    "status": null,
                    "datetime": null,
                    "comment": null,
                    "reason": null
                }',
                 'МАТАШЕВ АКБАР МУСЛИМЖАНОВИЧ', '860824302113', '+77781254616',
                1, 1, 3, 'arqwrawf',
                false, 'integration', 1,
                '{
                    "set_otp": "https://example-partner.kz/api/loggy/callbacks/set-otp/3928b?token=f0ce02",
                    "set_pan": "https://example-partner.kz/api/loggy/callbacks/set-pan/3928b?token=f0ce02",
                    "set_status": "https://example-partner.kz/api/loggy/callbacks/set-status/3928b?token=f0ce02",
                    "send_photo_urls": "https://example-partner.kz/api/loggy/callbacks/set-photo/3928b?token=f0ce02"
                }',
                true, null, 12, 1
            )
           ;
           """


def order_statuses_insert_script() -> str:
    return """
    INSERT INTO "public"."order.statuses" ("id", "status_id", "order_id", "created_at")
    VALUES
     (1, 1, 1, '2025-04-14T12:00:00+00:00'),
     (2, 2, 1, '2025-04-14T12:00:01+00:00'),
     (3, 3, 1, '2025-04-14T12:00:02+00:00'),
     (4, 4, 1, '2025-04-14T12:00:03+00:00'),
     (5, 5, 1, '2025-04-14T12:00:04+00:00'),
     (6, 6, 1, '2025-04-14T12:00:05+00:00'),
     (7, 16, 1, '2025-04-14T12:00:06+00:00'),
     (8, 12, 1, '2025-04-14T12:00:07+00:00'),


     (9, 1, 2, '2025-04-14T12:00:00+00:00'),
     (10, 2, 2, '2025-04-14T12:00:01+00:00'),
     (11, 3, 2, '2025-04-14T12:00:02+00:00'),
     (12, 4, 2, '2025-04-14T12:00:03+00:00'),
     (13, 5, 2, '2025-04-14T12:00:04+00:00'),
     (14, 6, 2, '2025-04-14T12:00:05+00:00'),
     (15, 16, 2, '2025-04-14T12:00:06+00:00'),

     (16, 1, 3, '2025-04-14T12:00:06+00:00'),

     (17, 1, 4, '2025-04-14T12:00:00+00:00'),
     (18, 2, 4, '2025-04-14T12:00:01+00:00'),
     (19, 3, 4, '2025-04-14T12:00:02+00:00'),
     (20, 4, 4, '2025-04-14T12:00:03+00:00'),
     (21, 5, 4, '2025-04-14T12:00:04+00:00'),
     (22, 6, 4, '2025-04-14T12:00:05+00:00'),
     (23, 16, 4, '2025-04-14T12:00:06+00:00'),
     (24, 12, 4, '2025-04-14T12:00:07+00:00'),

     (25, 1, 5, '2025-04-14T12:00:00+00:00'),
     (26, 2, 5, '2025-04-14T12:00:01+00:00'),
     (27, 3, 5, '2025-04-14T12:00:02+00:00'),
     (28, 4, 5, '2025-04-14T12:00:03+00:00'),
     (29, 5, 5, '2025-04-14T12:00:04+00:00'),
     (30, 6, 5, '2025-04-14T12:00:05+00:00'),
     (31, 16, 5, '2025-04-14T12:00:06+00:00'),
     (32, 12, 5, '2025-04-14T12:00:07+00:00')
    ;

    ALTER SEQUENCE "order.statuses_id_seq" RESTART WITH 33;
    """


def order_postcontrol_insert_script() -> str:
    return """
    INSERT INTO "public"."order.postcontrols"
      ("id", "order_id", "config_id", "image", "type", "resolution")
    VALUES
      (1, 1, 2, 'id card front.png', 'post_control', 'pending'),
      (2, 1, 3, 'id card back.png', 'post_control', 'pending'),
      (3, 1, 4, 'selfie.png', 'post_control', 'pending'),
      
      
      (4, 2, 2, 'id card front.png', 'post_control', 'pending'),
      (5, 2, 3, 'id card back.png', 'post_control', 'pending'),
      (6, 2, 4, 'selfie.png', 'post_control', 'pending'),
      
      
      (7, 4, 2, 'id card front.png', 'post_control', 'pending'),
      (8, 4, 3, 'id card back.png', 'post_control', 'pending'),
      (9, 4, 4, 'selfie.png', 'post_control', 'pending'),
      
      
      (10, 5, 2, 'id card front.png', 'post_control', 'pending'),
      (11, 5, 3, 'id card back.png', 'post_control', 'pending'),
      (12, 5, 4, 'selfie.png', 'post_control', 'pending')
      
      ;
      ALTER SEQUENCE "order.postcontrols_id_seq" RESTART WITH 13;
    """
