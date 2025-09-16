from decimal import Decimal
from typing import Optional

import pytest

from api.adapters.pos_terminal.exceptions import BasePOSTerminalAdapterError
from api.controllers.handle_order_status_transition.handlers.pos_terminal_registration import POSTerminalRegistrationHandler
from api.controllers.handle_order_status_transition.handlers.pos_terminal_registration.protocols import POSTerminalAdapterProtocol

from tests.fixtures.default_pre_start_sql_scripts import (
    default_groups_insert_script,
    default_permissions_insert_script,
    default_groups_permissions_insert_script,
    default_countries_insert_script,
    default_cities_insert_script,
    statuses_insert_script_v2
)


@pytest.fixture
def adapter() -> POSTerminalAdapterProtocol:
    class MockClient:
        async def registrate_pos_terminal(
                self,
                serial_number: str,
                model: str,
                merchant_id: str,
                terminal_id: str,
                receiver_iin: str,
                store_name: str,
                store_address: str,
                branch_name: str,
                oked_code: str,
                mcc_code: str,
                receiver_phone_number: str,
                receiver_full_name: str,
                courier_full_name: str,
                is_installment_enabled: bool,
                request_number_ref: Optional[str],
                inventory_number: Optional[str],
                sum: Optional[Decimal],
        ) -> str:
            if serial_number == "77777":
                raise BasePOSTerminalAdapterError()

            return "OVERDRAFT-TMS25-02339"

    return MockClient()


@pytest.fixture
def handler(adapter) -> POSTerminalRegistrationHandler:
    return POSTerminalRegistrationHandler(adapter)


@pytest.fixture
def pre_start_sql_script() -> str:
    """Важен порядок скриптов, так как есть зависимость от внешних ключей у таблиц"""
    scripts = [
        default_groups_insert_script(),
        default_permissions_insert_script(),
        default_groups_permissions_insert_script(),
        default_countries_insert_script(),
        default_cities_insert_script(),
        statuses_insert_script_v2(),
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
        products_insert_script(),
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
        VALUES (1, '[{"id": 1,"status": "new","icon": "order_new","slug": "novaia-zaiavka","name_en": "New order","name_ru": "Новая заявка","position": 1,"button_name": null,"transitions": [{"trigger": "courier_assigned","source": "new","dest": "courier_assigned"},{"trigger": "card_returned_to_bank","source": "new","dest": "card_returned_to_bank"}]},{"id": 2,"status": "courier_assigned","icon": "courier_appointed","slug": "kurer-naznachen","name_en": "Courier appointed","name_ru": "Курьер назначен","position": 2,"button_name": "Принять в работу","transitions": [{"trigger": "in_way","source": "courier_assigned","dest": "in_way"},{"trigger": "card_returned_to_bank","source": "courier_assigned","dest": "card_returned_to_bank"}]},{"id": 3,"status": "in_way","icon": "courier_accepted","slug": "priniato-kurerom-v-rabotu","name_en": "Courier accepted","name_ru": "Принято курьером в работу","position": 3,"button_name": "К клиенту","transitions": [{"trigger": "at_client","source": "in_way","dest": "at_client"},{"trigger": "card_returned_to_bank","source": "in_way","dest": "card_returned_to_bank"}]},{"id": 25,"status": "at_client","icon": "at_client","slug": "u-klienta","name_en": "At client","name_ru": "У клиента","position": 4,"button_name": "Отправить SMS с кодом","transitions": [{"trigger": "otp_sent","source": "at_client","dest": "otp_sent"},{"trigger": "card_returned_to_bank","source": "at_client","dest": "card_returned_to_bank"}]},{"id": 20,"status": "otp_sent","icon": "post_control","slug": "kod-otpravlen","name_en": "OTP sent","name_ru": "Код отправлен","position": 5,"button_name": "Проверить код","transitions": [{"trigger": "photo_capturing","source": "otp_sent","dest": "photo_capturing"},{"trigger": "card_returned_to_bank","source": "otp_sent","dest": "card_returned_to_bank"}]},{"id": 16,"status": "photo_capturing","icon": "post_control","slug": "fotografirovanie","name_en": "Photo capturing","name_ru": "Фотографирование","position": 7,"button_name": "Отправить на последконтроль","transitions": [{"trigger": "post_control","source": "photo_capturing","dest": "post_control"},{"trigger": "card_returned_to_bank","source": "photo_capturing","dest": "card_returned_to_bank"}]},{"id": 12,"status": "post_control","icon": "post_control","slug": "posledkontrol","name_en": "Postcontrol","name_ru": "Последконтроль","position": 8,"button_name": null,"transitions": [{"trigger": "delivered","source": "post_control","dest": "delivered"},{"trigger": "card_returned_to_bank","source": "post_control","dest": "card_returned_to_bank"}]},{"id": 7,"status": "delivered","icon": "order_delivered","slug": "dostavleno","name_en": "Delivered","name_ru": "Доставлено","position": 9,"button_name": null},{"id": 35,"status": "card_returned_to_bank","icon": "card_returned_to_bank","slug": "card-returned-to-bank","name_en": "Card was returned to bank","name_ru": "Карта возвращена в банк","position": null,"button_name": null,"transitions": [{"trigger": "new","source": "card_returned_to_bank","dest": "new"}]}]', null, 'Базовый', null, '{urgent,operative,planned}', '[{"id": 1, "icon": "order_new", "name": "Новая заявка", "slug": "novaia-zaiavka", "position": 1, "button_name": null}, {"id": 2, "icon": "courier_appointed", "name": "Курьер назначен", "slug": "kurer-naznachen", "position": 2, "button_name": "Принять в работу"}, {"id": 3, "icon": "courier_accepted", "name": "Принято курьером в работу", "slug": "priniato-kurerom-v-rabotu", "position": 3, "button_name": "К точке доставки"}, {"id": 4, "icon": "otw_delivery_point", "name": "В пути к точке доставки", "slug": "v-puti-k-tochke-dostavki", "position": 4, "button_name": "На точке доставки"}, {"id": 5, "icon": "on_delivery_point", "name": "На точке доставки", "slug": "na-tochke-dostavki", "position": 5, "button_name": "Контакт с получателем"}, {"id": 6, "icon": "at_client", "name": "Контакт с получателем", "slug": "kontakt-s-poluchatelem", "position": 6, "button_name": "Посылка передана"}, {"id": 7, "icon": "order_delivered", "name": "Доставлено", "slug": "dostavleno", "position": 7, "button_name": null}]', null, null, null, null);
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
    VALUES (1, 'planned', '2024-02-08 06:11:17.160374 +00:00', '2024-02-20 23:59:00.000000 +00:00', '{"status": "is_delivered"}', 'МАТАШЕВ АКБАР МУСЛИМЖАНОВИЧ', '860824302113', '+77781254616', '', 1, 1, 1, 1, null, null, null, 1, false, 'integration', 1, '{"set_otp": "https://business.bankffin.kz/api/loggy/callbacks/set-otp/3928b9e9-91a5-481c-88d2-9980a3f75f10?token=f0ce3fd77de24e0a9b07e7a02da2aa02", "set_pan": null, "set_status": "https://business.bankffin.kz/api/loggy/callbacks/set-status/3928b9e9-91a5-481c-88d2-9980a3f75f10?token=f0ce3fd77de24e0a9b07e7a02da2aa02"}', null, null, false, true, '2024-02-20 11:21:50.279633 +00:00', 1, null, 1);
    
    INSERT INTO public."order" (id, type, created_at, delivery_datetime, delivery_status, receiver_name, receiver_iin, receiver_phone_number, comment, city_id, courier_id, item_id, partner_id, partner_order_id, main_order_id, position, area_id, archived, created_by, deliverygraph_id, callbacks, initial_delivery_datetime, order_group_id, revised, allow_courier_assign, actual_delivery_datetime, current_status_id, shipment_point_id, delivery_point_id) 
    VALUES (2, 'planned', '2024-02-08 06:11:17.160374 +00:00', '2024-02-20 23:59:00.000000 +00:00', '{"status": "is_delivered"}', 'МАТАШЕВ АКБАР МУСЛИМЖАНОВИЧ', '860824302113', '+77781254616', '', 1, 1, 1, 1, null, null, null, 1, false, 'integration', 1, '{"set_otp": "https://business.bankffin.kz/api/loggy/callbacks/set-otp/3928b9e9-91a5-481c-88d2-9980a3f75f10?token=f0ce3fd77de24e0a9b07e7a02da2aa02", "set_pan": null, "set_status": "https://business.bankffin.kz/api/loggy/callbacks/set-status/3928b9e9-91a5-481c-88d2-9980a3f75f10?token=f0ce3fd77de24e0a9b07e7a02da2aa02"}', null, null, false, true, '2024-02-20 11:21:50.279633 +00:00', 1, null, 1);
    
    INSERT INTO public."order" (id, type, created_at, delivery_datetime, delivery_status, receiver_name, receiver_iin, receiver_phone_number, comment, city_id, courier_id, item_id, partner_id, partner_order_id, main_order_id, position, area_id, archived, created_by, deliverygraph_id, callbacks, initial_delivery_datetime, order_group_id, revised, allow_courier_assign, actual_delivery_datetime, current_status_id, shipment_point_id, delivery_point_id) 
    VALUES (3, 'planned', '2024-02-08 06:11:17.160374 +00:00', '2024-02-20 23:59:00.000000 +00:00', '{"status": "is_delivered"}', 'МАТАШЕВ АКБАР МУСЛИМЖАНОВИЧ', '860824302113', '+77781254616', '', 1, 1, 1, 1, null, null, null, 1, false, 'integration', 1, '{"set_otp": "https://business.bankffin.kz/api/loggy/callbacks/set-otp/3928b9e9-91a5-481c-88d2-9980a3f75f10?token=f0ce3fd77de24e0a9b07e7a02da2aa02", "set_pan": null, "set_status": "https://business.bankffin.kz/api/loggy/callbacks/set-status/3928b9e9-91a5-481c-88d2-9980a3f75f10?token=f0ce3fd77de24e0a9b07e7a02da2aa02"}', null, null, false, true, '2024-02-20 11:21:50.279633 +00:00', 1, null, 1);
    
    INSERT INTO public."order" (id, type, created_at, delivery_datetime, delivery_status, receiver_name, receiver_iin, receiver_phone_number, comment, city_id, courier_id, item_id, partner_id, partner_order_id, main_order_id, position, area_id, archived, created_by, deliverygraph_id, callbacks, initial_delivery_datetime, order_group_id, revised, allow_courier_assign, actual_delivery_datetime, current_status_id, shipment_point_id, delivery_point_id) 
    VALUES (4, 'planned', '2024-02-08 06:11:17.160374 +00:00', '2024-02-20 23:59:00.000000 +00:00', '{"status": "is_delivered"}', 'МАТАШЕВ АКБАР МУСЛИМЖАНОВИЧ', '860824302113', '+77781254616', '', 1, 1, 1, 1, null, null, null, 1, false, 'integration', 1, '{"set_otp": "https://business.bankffin.kz/api/loggy/callbacks/set-otp/3928b9e9-91a5-481c-88d2-9980a3f75f10?token=f0ce3fd77de24e0a9b07e7a02da2aa02", "set_pan": null, "set_status": "https://business.bankffin.kz/api/loggy/callbacks/set-status/3928b9e9-91a5-481c-88d2-9980a3f75f10?token=f0ce3fd77de24e0a9b07e7a02da2aa02"}', null, null, false, true, '2024-02-20 11:21:50.279633 +00:00', 1, null, 1);
    
    INSERT INTO public."order" (id, type, created_at, delivery_datetime, delivery_status, receiver_name, receiver_iin, receiver_phone_number, comment, city_id, courier_id, item_id, partner_id, partner_order_id, main_order_id, position, area_id, archived, created_by, deliverygraph_id, callbacks, initial_delivery_datetime, order_group_id, revised, allow_courier_assign, actual_delivery_datetime, current_status_id, shipment_point_id, delivery_point_id) 
    VALUES (5, 'planned', '2024-02-08 06:11:17.160374 +00:00', '2024-02-20 23:59:00.000000 +00:00', '{"status": "is_delivered"}', 'МАТАШЕВ АКБАР МУСЛИМЖАНОВИЧ', '860824302113', '+77781254616', '', 1, 1, 1, 1, null, null, null, 1, false, 'integration', 1, '{"set_otp": "https://business.bankffin.kz/api/loggy/callbacks/set-otp/3928b9e9-91a5-481c-88d2-9980a3f75f10?token=f0ce3fd77de24e0a9b07e7a02da2aa02", "set_pan": null, "set_status": "https://business.bankffin.kz/api/loggy/callbacks/set-status/3928b9e9-91a5-481c-88d2-9980a3f75f10?token=f0ce3fd77de24e0a9b07e7a02da2aa02"}', null, null, false, true, '2024-02-20 11:21:50.279633 +00:00', 1, null, 1);
    
    """

def products_insert_script() -> str:
    return """
        INSERT INTO "product" ("type", "attributes", "order_id")
        VALUES (
            'pos_terminal',
            '{"model": null, "mcc_code": "GGG1", "oked_code": "QWERTY123", "store_name": "MyMart", "branch_name": "Основной MyMart", "merchant_id": "1", "terminal_id": "1", "company_name": "ТОО Рога и Копыта", "serial_number": null, "is_installment_enabled": false}',
            1
        ); 
        INSERT INTO "product" ("type", "attributes", "order_id")
        VALUES (
            'pos_terminal',
            '{"model": "SUNMI", "mcc_code": "GGG1", "oked_code": "QWERTY123", "store_name": "MyMart", "branch_name": "Основной MyMart", "merchant_id": "1", "terminal_id": "1", "company_name": "ТОО Рога и Копыта", "serial_number": "11111111222222", "is_installment_enabled": false, "inventory_number": "123456789", "sum": 10000.1}',
            2
        );
        INSERT INTO "product" ("type", "attributes", "order_id")
        VALUES (
            'card',
            '{"pan": "1111********2222"}',
            4
        );
        INSERT INTO "product" ("type", "attributes", "order_id")
        VALUES (
            'pos_terminal',
            '{"model": "SUNMI", "mcc_code": "GGG1", "oked_code": "QWERTY123", "store_name": "MyMart", "branch_name": "Основной MyMart", "merchant_id": "1", "terminal_id": "1", "company_name": "ТОО Рога и Копыта", "serial_number": "11111111222222", "is_installment_enabled": false, "registration_status": "COMPLETED"}',
            3
        );
    """
