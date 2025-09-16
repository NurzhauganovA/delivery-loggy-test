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
    return [{'button_name': None,'icon': 'order_new','id': 1,'name': 'Готово к отправке','position': 1,'slug': 'novaia-zaiavka','status': 'new','transitions': [{'dest': 'card_returned_to_bank','source': 'new','trigger': 'card_returned_to_bank'}]},{'button_name': None,'icon': 'at-the-call-point','id': 29,'name': 'Принято курьерской службой','position': 2,'slug': 'priniato-kurerskoi-sluzhboi','status': 'accepted_by_courier_service','transitions': [{'dest': 'card_returned_to_bank','source': 'accepted_by_courier_service','trigger': 'card_returned_to_bank'}]},{'button_name': 'Принять в работу','icon': 'courier_appointed','id': 2,'name': 'Курьер назначен','position': 3,'slug': 'kurer-naznachen','status': 'courier_assigned','transitions': [{'dest': 'card_returned_to_bank','source': 'courier_assigned','trigger': 'card_returned_to_bank'}]},{'button_name': 'К точке вывоза','icon': 'courier_accepted','id': 3,'name': 'Принято курьером в работу','position': 4,'slug': 'priniato-kurerom-v-rabotu','status': 'in_way','transitions': [{'dest': 'card_returned_to_bank','source': 'in_way','trigger': 'card_returned_to_bank'}]},{'button_name': 'Отправить SMS с кодом','icon': 'at_client','id': 25,'name': 'У клиента','position': 5,'slug': 'u-klienta','status': 'send_otp','transitions': [{'dest': 'card_returned_to_bank','source': 'send_otp','trigger': 'card_returned_to_bank'}]},{'button_name': 'Проверить код','icon': 'post_control','id': 20,'name': 'Код отправлен','position': 6,'slug': 'kod-otpravlen','status': 'verify_otp','transitions': [{'dest': 'card_returned_to_bank','source': 'verify_otp','trigger': 'card_returned_to_bank'}]},{'button_name': 'Отправить на последконтроль','icon': 'post_control','id': 16,'name': 'Фотографирование','position': 7,'slug': 'fotografirovanie','status': 'photo_capturing','transitions': [{'dest': 'card_returned_to_bank','source': 'photo_capturing','trigger': 'card_returned_to_bank'}]},{'button_name': None,'icon': 'post_control','id': 12,'name': 'Последконтроль','position': 8,'slug': 'posledkontrol','status': 'post_control','transitions': [{'dest': 'card_returned_to_bank','source': 'post_control','trigger': 'card_returned_to_bank'}]},{'button_name': None,'icon': 'order_delivered','id': 7,'name': 'Доставлено','position': 9,'slug': 'dostavleno','status': 'delivered','transitions': None},{'button_name': None,'icon': 'card_returned_to_bank','id': 35,'name': 'Card was returned to bank','position': 0,'slug': 'card-returned-to-bank','status': 'card_returned_to_bank','transitions': [{'dest': 'new','source': 'card_returned_to_bank','trigger': 'new'}]}]


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
        item_city_insert_script(),
        delivery_graphs_insert_script(),
        delivery_points_insert_script(),
        areas_insert_script(),
        profile_couriers_insert_script(),
        profile_courier_areas_insert_script(),
        orders_insert_script(),
        product_insert_script()
    ]

    return " ".join(scripts)


def users_insert_script() -> str:
    """
        password: test
    """
    return """
        INSERT INTO public."user" (id, phone_number, first_name, last_name, middle_name, iin, credentials, is_active, photo, personal_agreement, created_at, is_superuser, email, password) 
        VALUES (1, '+77777777777', 'Служба 1', 'Службавна 1', 'Службавна 1', null, null, true, '', null, '2023-01-13 12:08:19.000000 +00:00', false, 'test_1@gmail.com', '$2b$12$KzP.BVjQGSu4O/D9XajUP.UikCQ4SWC47mr9XMDztCroWFiHmC2zy');

        INSERT INTO public."user" (id, phone_number, first_name, last_name, middle_name, iin, credentials, is_active, photo, personal_agreement, created_at, is_superuser, email, password) 
        VALUES (2, '+77777777771', 'Курьер 1', 'Курьеров 1', 'Курьерович 1', null, null, true, '', null, '2023-01-13 12:08:19.000000 +00:00', false, 'courier_1@gmail.com', '$2b$12$KzP.BVjQGSu4O/D9XajUP.UikCQ4SWC47mr9XMDztCroWFiHmC2zy');
    """


def partners_insert_script() -> str:
    return """
        INSERT INTO public.partner (id, name_kk, name_ru, name_en, activity_name_ru, address, affiliated, article, identifier, is_commerce, leader_data, consent_confirmed, is_government, is_international, email, registration_date, liq_date, liq_decision_date, credentials, courier_partner_id, created_at, start_work_hour, end_work_hour, type) 
        VALUES (1, 'Курьерская Служба 1', 'Курьерская Служба 1', null, null, 'город Алматы, Алмалинский район, Проспект АБЫЛАЙ ХАНА, дом: 91', false, 'ОB', '111111111111', true, '{"iin": "721107450542", "last_name": "ИБРАГИМОВА", "first_name": "ЛЯЗЗАТ", "middle_name": "ЕРКЕНОВНА"}', null, null, false, null, '2003-07-10 00:00:00.000000 +00:00', null, null, null, null, '2022-09-21 11:10:54.873492 +00:00', null, null, 'too');
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
        INSERT INTO public.item (id, name, item_type, delivery_time, delivery_type, category_id, partner_id, is_delivery_point_exists, has_postcontrol, accepted_delivery_statuses, distribute, message_for_noncall, courier_appointed_sms_on, courier_appointed_sms, days_to_delivery) 
        VALUES (1, 'Базовая кредитная карта', 'document', '00:00', '{planned}', null, null, true, false, '{}', false, null, false, null, null);
    """


def item_city_insert_script() -> str:
    return """
        INSERT INTO public.item_city (city_id, item_id, id) 
        VALUES (1, 1, 1);
    """


def delivery_graphs_insert_script() -> str:
    return """
        INSERT INTO public.deliverygraph (id, graph, partner_id, name, slug, types, graph_courier, name_en, name_zh, name_ru, name_kk) 
        VALUES (1, '[{"button_name": null,"icon": "order_new","id": 1,"name_en": "Готово к отправке","name_ru": "Готово к отправке","position": 1,"slug": "novaia-zaiavka","status": "new","transitions": [{"dest": "card_returned_to_bank","source": "new","trigger": "card_returned_to_bank"}]},{"button_name": null,"icon": "at-the-call-point","id": 29,"name_en": "Принято курьерской службой","name_ru": "Принято курьерской службой","position": 2,"slug": "priniato-kurerskoi-sluzhboi","status": "accepted_by_courier_service","transitions": [{"dest": "card_returned_to_bank","source": "accepted_by_courier_service","trigger": "card_returned_to_bank"}]},{"button_name": "Принять в работу","icon": "courier_appointed","id": 2,"name_en": "Курьер назначен","name_ru": "Курьер назначен","position": 3,"slug": "kurer-naznachen","status": "courier_assigned","transitions": [{"dest": "card_returned_to_bank","source": "courier_assigned","trigger": "card_returned_to_bank"}]},{"button_name": "К точке вывоза","icon": "courier_accepted","id": 3,"name_en": "Принято курьером в работу","name_ru": "Принято курьером в работу","position": 4,"slug": "priniato-kurerom-v-rabotu","status": "in_way","transitions": [{"dest": "card_returned_to_bank","source": "in_way","trigger": "card_returned_to_bank"}]},{"button_name": "Отправить SMS с кодом","icon": "at_client","id": 25,"name_en": "У клиента","name_ru": "У клиента","position": 5,"slug": "u-klienta","status": "send_otp","transitions": [{"dest": "card_returned_to_bank","source": "send_otp","trigger": "card_returned_to_bank"}]},{"button_name": "Проверить код","icon": "post_control","id": 20,"name_en": "Код отправлен","name_ru": "Код отправлен","position": 6,"slug": "kod-otpravlen","status": "verify_otp","transitions": [{"dest": "card_returned_to_bank","source": "verify_otp","trigger": "card_returned_to_bank"}]},{"button_name": "Отправить на последконтроль","icon": "post_control","id": 16,"name_en": "Фотографирование","name_ru": "Фотографирование","position": 7,"slug": "fotografirovanie","status": "photo_capturing","transitions": [{"dest": "card_returned_to_bank","source": "photo_capturing","trigger": "card_returned_to_bank"}]},{"button_name": null,"icon": "post_control","id": 12,"name_en": "Последконтроль","name_ru": "Последконтроль","position": 8,"slug": "posledkontrol","status": "post_control","transitions": [{"dest": "card_returned_to_bank","source": "post_control","trigger": "card_returned_to_bank"}]},{"button_name": null,"icon": "order_delivered","id": 7,"name_en": "Доставлено","name_ru": "Доставлено","position": 9,"slug": "dostavleno","status": "delivered"},{"button_name": null,"icon": "card_returned_to_bank","id": 35,"name_en": "Card was returned to bank","name_ru": "Карта возвращена в банк","position": 0,"slug": "card-returned-to-bank","status": "card_returned_to_bank","transitions": [{"dest": "new","source": "card_returned_to_bank","trigger": "new"}]}]', null, 'Базовый', null, '{urgent,operative,planned}', '[{"button_name": null,"icon": "order_new","id": 1,"name_en": "Готово к отправке","name_ru": "Готово к отправке","position": 1,"slug": "novaia-zaiavka","status": "new","transitions": [{"dest": "card_returned_to_bank","source": "new","trigger": "card_returned_to_bank"}]},{"button_name": null,"icon": "at-the-call-point","id": 29,"name_en": "Принято курьерской службой","name_ru": "Принято курьерской службой","position": 2,"slug": "priniato-kurerskoi-sluzhboi","status": "accepted_by_courier_service","transitions": [{"dest": "card_returned_to_bank","source": "accepted_by_courier_service","trigger": "card_returned_to_bank"}]},{"button_name": "Принять в работу","icon": "courier_appointed","id": 2,"name_en": "Курьер назначен","name_ru": "Курьер назначен","position": 3,"slug": "kurer-naznachen","status": "courier_assigned","transitions": [{"dest": "card_returned_to_bank","source": "courier_assigned","trigger": "card_returned_to_bank"}]},{"button_name": "К точке вывоза","icon": "courier_accepted","id": 3,"name_en": "Принято курьером в работу","name_ru": "Принято курьером в работу","position": 4,"slug": "priniato-kurerom-v-rabotu","status": "in_way","transitions": [{"dest": "card_returned_to_bank","source": "in_way","trigger": "card_returned_to_bank"}]},{"button_name": "Отправить SMS с кодом","icon": "at_client","id": 25,"name_en": "У клиента","name_ru": "У клиента","position": 5,"slug": "u-klienta","status": "send_otp","transitions": [{"dest": "card_returned_to_bank","source": "send_otp","trigger": "card_returned_to_bank"}]},{"button_name": "Проверить код","icon": "post_control","id": 20,"name_en": "Код отправлен","name_ru": "Код отправлен","position": 6,"slug": "kod-otpravlen","status": "verify_otp","transitions": [{"dest": "card_returned_to_bank","source": "verify_otp","trigger": "card_returned_to_bank"}]},{"button_name": "Отправить на последконтроль","icon": "post_control","id": 16,"name_en": "Фотографирование","name_ru": "Фотографирование","position": 7,"slug": "fotografirovanie","status": "photo_capturing","transitions": [{"dest": "card_returned_to_bank","source": "photo_capturing","trigger": "card_returned_to_bank"}]},{"button_name": null,"icon": "post_control","id": 12,"name_en": "Последконтроль","name_ru": "Последконтроль","position": 8,"slug": "posledkontrol","status": "post_control","transitions": [{"dest": "card_returned_to_bank","source": "post_control","trigger": "card_returned_to_bank"}]},{"button_name": null,"icon": "order_delivered","id": 7,"name_en": "Доставлено","name_ru": "Доставлено","position": 9,"slug": "dostavleno","status": "delivered"},{"button_name": null,"icon": "card_returned_to_bank","id": 35,"name_en": "Card was returned to bank","name_ru": "Карта возвращена в банк","position": 0,"slug": "card-returned-to-bank","status": "card_returned_to_bank","transitions": [{"dest": "new","source": "card_returned_to_bank","trigger": "new"}]}]', null, null, null, null);
    """


def delivery_points_insert_script() -> str:
    return """
        INSERT INTO public.delivery_point (id, address, latitude, longitude) 
        VALUES (1, 'Казахстан, Алматы, Алматы, Микрорайон Каргалы, д.25', 43.16545200, 76.87401300);
    """


def areas_insert_script() -> str:
    return """
        INSERT INTO public.area (id, slug, scope, city_id, partner_id, fill_opacity, stroke_color, stroke_opacity, fill_color, updated_at, archived, created_at) 
        VALUES (1, 'Весь город Алматы', '[{"latitude": 76.9571686, "longitude": 43.3116679}, {"latitude": 76.9976807, "longitude": 43.2956948}, {"latitude": 77.0660019, "longitude": 43.2386988}, {"latitude": 76.9963074, "longitude": 43.1956664}, {"latitude": 76.953392, "longitude": 43.1723757}, {"latitude": 76.8898773, "longitude": 43.1818593}, {"latitude": 76.8304825, "longitude": 43.2431453}, {"latitude": 76.8308258, "longitude": 43.2946913}, {"latitude": 76.8964005, "longitude": 43.3063678}]', 1, 1, 0.3, '#56DB40', 1, '#FF931E', '2022-12-19 09:46:50.672242 +00:00', false, '2022-12-19 09:46:14.752459 +00:00');
    """


def profile_couriers_insert_script() -> str:
    return """
        INSERT INTO public.profile_courier (id, at_work, experience_years, experience_months, start_work_hour, end_work_hour, schedule, created_at, is_identified, is_biometry_verificated, iban, item_type, transport_type, city_id, user_id, state, partner_id, status, category_id, register_with_biometry) 
        VALUES (1, false, null, null, null, null, '{monday}', '2023-05-12 07:23:44.928687 +00:00', true, false, null, null, 'car', 1, 2, null, 1, 'accepted', null, false);
    """

def profile_courier_areas_insert_script() -> str:
    return """
        INSERT INTO public.profile_courier_area (area_id, profile_courier_id, id) VALUES (1, 1, 1);
    """

def orders_insert_script() -> str:
    return """
        INSERT INTO public."order" (id, type, created_at, delivery_datetime, delivery_status, receiver_name, receiver_iin, receiver_phone_number, comment, city_id, courier_id, item_id, partner_id, partner_order_id, main_order_id, position, area_id, archived, created_by, deliverygraph_id, callbacks, initial_delivery_datetime, order_group_id, revised, allow_courier_assign, actual_delivery_datetime, current_status_id, shipment_point_id, delivery_point_id) 
        VALUES (1, 'planned', '2024-02-08 06:11:17.160374 +00:00', '2024-02-20 23:59:00.000000 +00:00', '{"status": "is_delivered"}', 'МАТАШЕВ АКБАР МУСЛИМЖАНОВИЧ', '860824302113', '+77781254616', '', 1, 1, 1, 1, null, null, null, 1, false, 'integration', 1, '{"set_otp": "https://business.bankffin.kz/api/loggy/callbacks/set-otp/3928b9e9-91a5-481c-88d2-9980a3f75f10?token=f0ce3fd77de24e0a9b07e7a02da2aa02", "set_pan": null, "set_status": "https://business.bankffin.kz/api/loggy/callbacks/set-status/3928b9e9-91a5-481c-88d2-9980a3f75f10?token=f0ce3fd77de24e0a9b07e7a02da2aa02"}', null, null, false, true, '2024-02-20 11:21:50.279633 +00:00', 7, null, 1);
    """


def product_insert_script() -> str:
    return """
        INSERT INTO "product" ("type", "attributes", "order_id")
        VALUES (
            'card',
            '{"pan": "5269********3427", "pan_suffix": "3427"}',
            1
        );
    """
