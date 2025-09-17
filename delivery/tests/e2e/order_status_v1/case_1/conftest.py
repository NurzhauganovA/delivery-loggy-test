import pytest

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
def expected() -> dict:
    return {
        'created_at': '2025-07-18T10:38:10.748589+00:00',
        'delivery_status': {
            'comment': None,
            'datetime': None,
            'reason': None,
            'status': 'on-the-way-to-call-point',
        },
        'order_id': 1,
        'status': {
            'after': [
                {'id': 6, 'name': 'Контакт с получателем'},
                {'id': 16, 'name': 'Фотографирование'}
            ],
            'icon': 'post_control',
            'id': 12,
            'is_optional': True,
            'name': None,
            'partner_id': None,
            'slug': 'posledkontrol'
        }
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
        profile_service_managers_insert_script(),
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


def profile_service_managers_insert_script() -> str:
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
    INSERT INTO "public"."postcontrol_configs" ("id", "item_id", "name")
    VALUES
    (1, 1, 'id card');
    """


def delivery_graphs_insert_script() -> str:
    return """
        INSERT INTO public.deliverygraph (id, graph, partner_id, name_ru, slug, types, graph_courier, name_en, name_zh, name_kk) 
        VALUES (1, '[{"id": 1, "icon": "order_new", "name": "Новая заявка", "slug": "novaia-zaiavka", "position": 1, "button_name": null}, {"id": 30, "icon": "packed", "name": "Упаковано", "slug": "upakovano", "position": 2, "button_name": null}, {"id": 31, "icon": "ready-to-send", "name": "Включено в группу", "slug": "vkliucheno-v-gruppu", "position": 3, "button_name": null}, {"id": 23, "icon": "ready-to-send", "name": "Готово к вывозу", "slug": "gotovo-k-vyvozu", "position": 4, "button_name": null}, {"id": 32, "icon": "at_revise", "name": "На сверке", "slug": "na-sverke", "position": 6, "button_name": null}, {"id": 28, "icon": "courier_accepted", "name": "Вывезено курьером", "slug": "vyvezeno-kurerom", "position": 7, "button_name": null}, {"id": 29, "icon": "at-the-call-point", "name": "Принято курьерской службой", "slug": "priniato-kurerskoi-sluzhboi", "position": 8, "button_name": null}, {"id": 2, "icon": "courier_appointed", "name": "Курьер назначен", "slug": "kurer-naznachen", "position": 9, "button_name": "Принять в работу"}, {"id": 3, "icon": "courier_accepted", "name": "Принято курьером в работу", "slug": "priniato-kurerom-v-rabotu", "position": 10, "button_name": "К точке вывоза"}, {"id": 25, "icon": "at_client", "name": "У клиента", "slug": "u-klienta", "position": 11, "button_name": "Отправить SMS с кодом"}, {"id": 20, "icon": "post_control", "name": "Код отправлен", "slug": "kod-otpravlen", "position": 12, "button_name": "Проверить код"}, {"id": 16, "icon": "post_control", "name": "Фотографирование", "slug": "fotografirovanie", "position": 13, "button_name": "Отправить на последконтроль"}, {"id": 12, "icon": "post_control", "name": "Последконтроль", "slug": "posledkontrol", "position": 14, "button_name": null}, {"id": 7, "icon": "order_delivered", "name": "Доставлено", "slug": "dostavleno", "position": 15, "button_name": null}]', null, 'Подготовка + otp + Последконтроль', 'Podgotovka + otp + Posledkontrol', '{urgent,operative,planned}', '[{"id": 1, "icon": "order_new", "name": "Новая заявка", "slug": "novaia-zaiavka", "position": 1, "button_name": null}, {"id": 30, "icon": "packed", "name": "Упаковано", "slug": "upakovano", "position": 2, "button_name": null}, {"id": 31, "icon": "ready-to-send", "name": "Включено в группу", "slug": "vkliucheno-v-gruppu", "position": 3, "button_name": null}, {"id": 23, "icon": "ready-to-send", "name": "Готово к вывозу", "slug": "gotovo-k-vyvozu", "position": 4, "button_name": null}, {"id": 32, "icon": "at_revise", "name": "На сверке", "slug": "na-sverke", "position": 6, "button_name": null}, {"id": 28, "icon": "courier_accepted", "name": "Вывезено курьером", "slug": "vyvezeno-kurerom", "position": 7, "button_name": null}, {"id": 29, "icon": "at-the-call-point", "name": "Принято курьерской службой", "slug": "priniato-kurerskoi-sluzhboi", "position": 8, "button_name": null}, {"id": 2, "icon": "courier_appointed", "name": "Курьер назначен", "slug": "kurer-naznachen", "position": 9, "button_name": "Принять в работу"}, {"id": 3, "icon": "courier_accepted", "name": "Принято курьером в работу", "slug": "priniato-kurerom-v-rabotu", "position": 10, "button_name": "К точке вывоза"}, {"id": 25, "icon": "at_client", "name": "У клиента", "slug": "u-klienta", "position": 11, "button_name": "Отправить SMS с кодом"}, {"id": 20, "icon": "post_control", "name": "Код отправлен", "slug": "kod-otpravlen", "position": 12, "button_name": "Проверить код"}, {"id": 16, "icon": "post_control", "name": "Фотографирование", "slug": "fotografirovanie", "position": 13, "button_name": "Отправить на последконтроль"}, {"id": 12, "icon": "post_control", "name": "Последконтроль", "slug": "posledkontrol", "position": 14, "button_name": null}, {"id": 7, "icon": "order_delivered", "name": "Доставлено", "slug": "dostavleno", "position": 15, "button_name": null}]', null, null, null);
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
                                       allow_courier_assign, current_status_id,
                                       shipment_point_id, delivery_point_id)
           VALUES (1, 'planned', '2024-02-08 06:11:17.160374 +00:00', '2024-02-20 23:59:00.000000 +00:00',
                   '{"status": "on-the-way-to-call-point"}', 'МАТАШЕВ АКБАР МУСЛИМЖАНОВИЧ', '860824302113', '+77781254616', '', 1,
                   1, 3, null, null, null, false, 'integration', 1,
                   '{"set_otp": "https://business.bankffin.kz/api/loggy/callbacks/set-otp/3928b9e9-91a5-481c-88d2-9980a3f75f10?token=f0ce3fd77de24e0a9b07e7a02da2aa02", "set_pan": null, "set_status": "https://business.bankffin.kz/api/loggy/callbacks/set-status/3928b9e9-91a5-481c-88d2-9980a3f75f10?token=f0ce3fd77de24e0a9b07e7a02da2aa02"}',
                   null, null, false, true, 16, null, 1),
                   (2, 'planned', '2024-02-08 06:11:17.160374 +00:00', '2024-02-20 23:59:00.000000 +00:00',
                   '{"status": "on-the-way-to-call-point"}', 'МАТАШЕВ АКБАР МУСЛИМЖАНОВИЧ', '860824302113', '+77781254616', '', 1,
                   1, 3, null, null, null, false, 'integration', 1,
                   '{"set_otp": "https://business.bankffin.kz/api/loggy/callbacks/set-otp/3928b9e9-91a5-481c-88d2-9980a3f75f10?token=f0ce3fd77de24e0a9b07e7a02da2aa02", "set_pan": null, "set_status": "https://business.bankffin.kz/api/loggy/callbacks/set-status/3928b9e9-91a5-481c-88d2-9980a3f75f10?token=f0ce3fd77de24e0a9b07e7a02da2aa02"}',
                   null, null, false, true, 16, null, 1);
           """


def order_statuses_insert_script() -> str:
    return """
    INSERT INTO "public"."order.statuses" ("id", "order_id", "status_id", "created_at")
    VALUES 
    (1, 1, 1, '2025-07-18T10:00+00'),
    (2, 1, 2, '2025-07-18T10:01+00'),
    (3, 1, 3, '2025-07-18T10:02+00'),
    (4, 1, 4, '2025-07-18T10:03+00'),
    (5, 1, 5, '2025-07-18T10:04+00'),
    (6, 1, 6, '2025-07-18T10:05+00'),
    (7, 1, 16, '2025-07-18T10:06+00'),
    
    (8, 2, 1, '2025-07-18T10:00+00'),
    (9, 2, 2, '2025-07-18T10:01+00'),
    (10, 2, 3, '2025-07-18T10:02+00'),
    (11, 2, 4, '2025-07-18T10:03+00'),
    (12, 2, 5, '2025-07-18T10:04+00'),
    (13, 2, 6, '2025-07-18T10:05+00'),
    (14, 2, 16, '2025-07-18T10:06+00');
    
    ALTER SEQUENCE "order.statuses_id_seq" RESTART WITH 15;
    """


def order_postcontrol_insert_script() -> str:
    return """
    INSERT INTO "public"."order.postcontrols" ("id", "order_id", "config_id", "image", "type")
    VALUES
    (1, 1, 1, 'sample_image.png', 'post_control'),
    (2, 2, 1, 'sample_image.png', 'post_control');
    """
