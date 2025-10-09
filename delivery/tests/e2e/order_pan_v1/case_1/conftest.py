import pytest

from tests.fixtures.default_pre_start_sql_scripts import (
    default_groups_insert_script,
    default_permissions_insert_script,
    default_groups_permissions_insert_script,
    default_countries_insert_script,
    default_cities_insert_script,
    statuses_insert_script,
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
        'profile_type': 'courier',
        'profile_id': '1',
    }


@pytest.fixture
def expected():
    return {
        "actual_delivery_datetime": "2024-02-20T11:21:50.279633+00:00",
        "addresses": [
            {
                "id": 1,
                "place": {
                    "address": "Казахстан, Алматы, Алматы, Микрорайон " "Каргалы, д.25",
                    "city_id": None,
                    "id": 1,
                    "latitude": 43.165452,
                    "longitude": 76.874013,
                },
                "position": 1,
                "type": "delivery_point",
            }
        ],
        "area": None,
        "area_id": None,
        "city": {"id": 1, "name": "Almaty", "timezone": "Asia/Aqtau"},
        "city_id": 1,
        "comment": "",
        "courier": {
            "id": 1,
            "user": {
                "first_name": "Служба 1",
                "id": 1,
                "last_name": "Службавна 1",
                "middle_name": "Службавна 1",
                "phone_number": "+77777777777",
            },
        },
        "courier_id": 1,
        "created_at": "2024-02-08T06:11:17.160374+00:00",
        "created_by": "integration",
        "current_status_id": 20,
        "delivery_datetime": "2024-02-20T23:59:00+00:00",
        "delivery_point_id": 1,
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
                },
                {
                    "button_name": "Принять в работу",
                    "icon": "courier_appointed",
                    "id": 2,
                    "name": "Курьер назначен",
                    "position": 2,
                    "slug": "kurer-naznachen",
                },
                {
                    "button_name": "К клиенту",
                    "icon": "courier_accepted",
                    "id": 3,
                    "name": "Принято курьером в работу",
                    "position": 3,
                    "slug": "priniato-kurerom-v-rabotu",
                },
                {
                    "button_name": "Отправить SMS с кодом",
                    "icon": "at_client",
                    "id": 25,
                    "name": "У клиента",
                    "position": 4,
                    "slug": "u-klienta",
                },
                {
                    "button_name": "Проверить код",
                    "icon": "post_control",
                    "id": 20,
                    "name": "Код отправлен",
                    "position": 5,
                    "slug": "kod-otpravlen",
                },
                {
                    "button_name": "Сканировать карту",
                    "icon": "post_control",
                    "id": 24,
                    "name": "Сканирование карты",
                    "position": 6,
                    "slug": "skanirovanie-karty",
                },
                {
                    "button_name": "Отправить на последконтроль",
                    "icon": "post_control",
                    "id": 16,
                    "name": "Фотографирование",
                    "position": 7,
                    "slug": "fotografirovanie",
                },
                {
                    "button_name": None,
                    "icon": "post_control",
                    "id": 12,
                    "name": "Последконтроль",
                    "position": 8,
                    "slug": "posledkontrol",
                },
                {
                    "button_name": None,
                    "icon": "order_delivered",
                    "id": 7,
                    "name": "Доставлено",
                    "position": 9,
                    "slug": "dostavleno",
                },
            ],
            "id": 11,
            "name": None,
            "partner_id": None,
            "slug": None,
            "types": ["urgent", "operative", "planned"],
        },
        "has_receiver_feedback": None,
        "id": 1,
        "initial_delivery_datetime": None,
        "item": {
            "accepted_delivery_statuses": None,
            "has_postcontrol": False,
            "message_for_noncall": None,
            "name": "Базовая кредитная карта",
            'postcontrol_cancellation_configs': [],
            "postcontrol_configs": [],
            "upload_from_gallery": True,
        },
        "item_id": 1,
        "last_otp": None,
        "main_order_id": None,
        "order_chain_stages": [],
        "order_group_id": None,
        "partner": {
            "article": "ОB",
            "courier_partner_id": None,
            "id": 1,
            "name": "Курьерская Служба 1",
        },
        "partner_id": 1,
        "partner_order_id": None,
        "position": None,
        "product": {
            "attributes": {
                "input_type": "manually",
                "pan": "5269********2985",
                "pan_suffix": "2985",
            },
            "id": 1,
            "name": None,
            "type": "card",
        },
        "receiver_iin": "860824302113",
        "receiver_name": "МАТАШЕВ АКБАР МУСЛИМЖАНОВИЧ",
        "receiver_phone_number": "+77781254616",
        "revised": False,
        "shipment_point_id": None,
        "statuses": [
            {
                "created_at": "2025-07-11T00:00:00+00:00",
                "status": {
                    "icon": "order_new",
                    "id": 1,
                    "name": None,
                    "slug": "novaia-zaiavka",
                },
            },
            {
                "created_at": "2025-07-11T00:00:01+00:00",
                "status": {
                    "icon": "courier_appointed",
                    "id": 2,
                    "name": None,
                    "slug": "kurer-naznachen",
                },
            },
            {
                "created_at": "2025-07-11T00:00:02+00:00",
                "status": {
                    "icon": "courier_accepted",
                    "id": 3,
                    "name": None,
                    "slug": "priniato-kurerom-v-rabotu",
                },
            },
            {
                "created_at": "2025-07-11T00:00:03+00:00",
                "status": {
                    "icon": "at_client",
                    "id": 25,
                    "name": None,
                    "slug": "u-klienta",
                },
            },
            {
                "created_at": "2025-07-11T00:00:04+00:00",
                "status": {
                    "icon": "post_control",
                    "id": 20,
                    "name": None,
                    "slug": "kod-otpravlen",
                },
            },
        ],
        "type": "planned",
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
        users_insert_script(),
        partners_insert_script(),
        profile_couriers_insert_script(),
        groups_users_insert_script(),
        item_insert_script(),
        item_pan_validation_masks_insert_script(),
        delivery_graphs_insert_script(),
        delivery_points_insert_script(),
        orders_insert_script(),
        order_statuses_insert_script(),
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

           INSERT INTO public."user" (id, phone_number, first_name, last_name, middle_name, iin, credentials, is_active, 
                                      photo, personal_agreement, created_at, is_superuser, email, password)
           VALUES (3, '+77777777772', 'Супервайзер 1', 'Супервайзеров 1', 'Супервайзерич 1', null, null, true, '', null, 
                   '2023-01-13 12:08:19.000000 +00:00', false, 'supervisor_1@gmail.com', 
                   '$2b$12$KzP.BVjQGSu4O/D9XajUP.UikCQ4SWC47mr9XMDztCroWFiHmC2zy');

           ALTER SEQUENCE user_id_seq RESTART WITH 4;
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


def item_pan_validation_masks_insert_script() -> str:
    return """
        INSERT INTO "public"."item_pan_validation_mask" ("id", "mask", "item_id")
        VALUES
        (1, '526988', 1);
    """


def profile_couriers_insert_script() -> str:
    return """
           INSERT INTO public.profile_courier (id, user_id, partner_id)
           VALUES (1, 1, 1);
           """


def groups_users_insert_script() -> str:
    return """
           INSERT INTO public.groups_user (user_id, groups_id, id)
           VALUES (1, 'courier', 1);

           ALTER SEQUENCE groups_user_id_seq restart with 2;
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


def delivery_graphs_insert_script() -> str:
    return """
           INSERT INTO public.deliverygraph (id, graph, partner_id, name_ru, slug, types, graph_courier, name_en, name_zh,
                                             name_kk)
           VALUES (11,
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
                          "button_name": "К клиенту"
                        },
                        {
                          "id": 25,
                          "icon": "at_client",
                          "name": "У клиента",
                          "slug": "u-klienta",
                          "position": 4,
                          "button_name": "Отправить SMS с кодом"
                        },
                        {
                          "id": 20,
                          "icon": "post_control",
                          "name": "Код отправлен",
                          "slug": "kod-otpravlen",
                          "position": 5,
                          "button_name": "Проверить код"
                        },
                        {
                          "id": 24,
                          "icon": "post_control",
                          "name": "Сканирование карты",
                          "slug": "skanirovanie-karty",
                          "position": 6,
                          "button_name": "Сканировать карту"
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
                   null, 'Базовый', null, '{urgent,operative,planned}',
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
                          "button_name": "К клиенту"
                        },
                        {
                          "id": 25,
                          "icon": "at_client",
                          "name": "У клиента",
                          "slug": "u-klienta",
                          "position": 4,
                          "button_name": "Отправить SMS с кодом"
                        },
                        {
                          "id": 20,
                          "icon": "post_control",
                          "name": "Код отправлен",
                          "slug": "kod-otpravlen",
                          "position": 5,
                          "button_name": "Проверить код"
                        },
                        {
                          "id": 24,
                          "icon": "post_control",
                          "name": "Сканирование карты",
                          "slug": "skanirovanie-karty",
                          "position": 6,
                          "button_name": "Сканировать карту"
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
                   null, null, null); 
           """


def delivery_points_insert_script() -> str:
    return """
           INSERT INTO public.delivery_point (id, address, latitude, longitude)
           VALUES (1, 'Казахстан, Алматы, Алматы, Микрорайон Каргалы, д.25', 43.16545200, 76.87401300); 
           """


def orders_insert_script() -> str:
    return """
           INSERT INTO public."order" (id, type, created_at, delivery_datetime, delivery_status, receiver_name,
                                       receiver_iin, receiver_phone_number, comment, city_id, item_id, partner_id,
                                       partner_order_id, main_order_id, position, archived, created_by,
                                       deliverygraph_id, callbacks, initial_delivery_datetime, order_group_id, revised,
                                       allow_courier_assign, actual_delivery_datetime, current_status_id,
                                       shipment_point_id, delivery_point_id, courier_id)
           VALUES (1, 'planned', '2024-02-08 06:11:17.160374 +00:00', '2024-02-20 23:59:00.000000 +00:00',
                   '{"status": "is_delivered"}', 'МАТАШЕВ АКБАР МУСЛИМЖАНОВИЧ', '860824302113', '+77781254616', '', 1,
                   1, 1, null, null, null, false, 'integration', 11,
                   '{"set_otp": "https://business.bankffin.kz/api/loggy/callbacks/set-otp/3928b9e9-91a5-481c-88d2-9980a3f75f10?token=f0ce3fd77de24e0a9b07e7a02da2aa02", "set_pan": null, "set_status": "https://business.bankffin.kz/api/loggy/callbacks/set-status/3928b9e9-91a5-481c-88d2-9980a3f75f10?token=f0ce3fd77de24e0a9b07e7a02da2aa02"}',
                   null, null, false, true, '2024-02-20 11:21:50.279633 +00:00', 20, null, 1, 1);
               
            INSERT INTO public."order" (id, type, created_at, delivery_datetime, delivery_status, receiver_name,
                                       receiver_iin, receiver_phone_number, comment, city_id, item_id, partner_id,
                                       partner_order_id, main_order_id, position, archived, created_by,
                                       deliverygraph_id, callbacks, initial_delivery_datetime, order_group_id, revised,
                                       allow_courier_assign, actual_delivery_datetime, current_status_id,
                                       shipment_point_id, delivery_point_id, courier_id)
           VALUES (2, 'planned', '2024-02-08 06:11:17.160374 +00:00', '2024-02-20 23:59:00.000000 +00:00',
                   '{"status": "is_delivered"}', 'МАТАШЕВ АКБАР МУСЛИМЖАНОВИЧ', '860824302113', '+77781254616', '', 1,
                   1, 1, null, null, null, false, 'integration', 11,
                   '{"set_otp": "https://business.bankffin.kz/api/loggy/callbacks/set-otp/3928b9e9-91a5-481c-88d2-9980a3f75f10?token=f0ce3fd77de24e0a9b07e7a02da2aa02", "set_pan": null, "set_status": "https://business.bankffin.kz/api/loggy/callbacks/set-status/3928b9e9-91a5-481c-88d2-9980a3f75f10?token=f0ce3fd77de24e0a9b07e7a02da2aa02"}',
                   null, null, false, true, '2024-02-20 11:21:50.279633 +00:00', 20, null, 1, 1);
           """


def order_statuses_insert_script() -> str:
    return """
    INSERT INTO "public"."order.statuses" ("id", "order_id", "status_id", "created_at")
    VALUES
    (1, 1, 1, '2025-07-11T00:00:00'),
    (2, 1, 2, '2025-07-11T00:00:01'),
    (3, 1, 3, '2025-07-11T00:00:02'),
    (4, 1, 25, '2025-07-11T00:00:03'),
    (5, 1, 20, '2025-07-11T00:00:04')
    ;
    """
