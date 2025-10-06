from typing import Any

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
        'profile_type': 'call_center_manager',
        'profile_id': '1',
    }


@pytest.fixture
def expected() -> list[dict[str, Any]]:
    return [
        {
            'accepted_delivery_statuses': None,
            'category': None,
            'category_id': None,
            'cities': [{'id': 1, 'name': 'Almaty'},
                       {'id': 2, 'name': 'Astana'},
                       {'id': 3, 'name': 'Qaraganda'}],
            'courier_appointed_sms': None,
            'courier_appointed_sms_on': False,
            'days_to_delivery': None,
            'delivery_time': '00:00',
            'delivery_type': ['planned'],
            'deliverygraphs': [],
            'distribute': False,
            'has_postcontrol': False,
            'id': 1,
            'is_delivery_point_exists': True,
            'item_type': 'document',
            'message_for_noncall': None,
            'name': 'Базовая кредитная карта 1',
            'partner': {'id': 2, 'name': 'Партнер 1'},
            'partner_id': 2,
            'postcontrol_configs': []
        },
        {
            'accepted_delivery_statuses': None,
            'category': None,
            'category_id': None,
            'cities': [{'id': 1, 'name': 'Almaty'},
                       {'id': 2, 'name': 'Astana'},
                       {'id': 3, 'name': 'Qaraganda'}],
            'courier_appointed_sms': None,
            'courier_appointed_sms_on': False,
            'days_to_delivery': None,
            'delivery_time': '00:00',
            'delivery_type': ['planned'],
            'deliverygraphs': [],
            'distribute': False,
            'has_postcontrol': False,
            'id': 2,
            'is_delivery_point_exists': True,
            'item_type': 'document',
            'message_for_noncall': None,
            'name': 'Базовая кредитная карта 2',
            'partner': {'id': 2, 'name': 'Партнер 1'},
            'partner_id': 2,
            'postcontrol_configs': []
        },
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
        profile_call_center_manager_insert_script(),
        groups_users_insert_script(),
        item_insert_script(),
        item_city_insert_script(),
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
                   '$2b$12$KzP.BVjQGSu4O/D9XajUP.UikCQ4SWC47mr9XMDztCroWFiHmC2zy'); \
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
                   '2022-09-21 11:10:54.873492 +00:00', null, null, 'too'); \
           """


def profile_call_center_manager_insert_script() -> str:
    return """
           INSERT INTO public.profile_call_center_manager (id, user_id, partner_id, country_id)
           VALUES (1, 1, 1, 1);
           """


def groups_users_insert_script() -> str:
    return """
           INSERT INTO public.groups_user (user_id, groups_id, id)
           VALUES (1, 'call_center_manager', 1);
           """


def item_insert_script() -> str:
    return """
           INSERT INTO public.item (id, name, item_type, delivery_time, delivery_type, category_id, partner_id,
                                    is_delivery_point_exists, has_postcontrol, accepted_delivery_statuses, distribute,
                                    message_for_noncall, courier_appointed_sms_on, courier_appointed_sms,
                                    days_to_delivery)
           VALUES (1, 'Базовая кредитная карта 1', 'document', '00:00', '{planned}', null, 2, true, false, null, false,
                   null, false, null, null);
           INSERT INTO public.item (id, name, item_type, delivery_time, delivery_type, category_id, partner_id,
                                    is_delivery_point_exists, has_postcontrol, accepted_delivery_statuses, distribute,
                                    message_for_noncall, courier_appointed_sms_on, courier_appointed_sms,
                                    days_to_delivery)
           VALUES (2, 'Базовая кредитная карта 2', 'document', '00:00', '{planned}', null, 2, true, false, null, false,
                   null, false, null, null);
           INSERT INTO public.item (id, name, item_type, delivery_time, delivery_type, category_id, partner_id,
                                    is_delivery_point_exists, has_postcontrol, accepted_delivery_statuses, distribute,
                                    message_for_noncall, courier_appointed_sms_on, courier_appointed_sms,
                                    days_to_delivery)
           VALUES (3, 'Базовая кредитная карта 3', 'document', '00:00', '{planned}', null, 3, true, false, null, false,
                   null, false, null, null);
           INSERT INTO public.item (id, name, item_type, delivery_time, delivery_type, category_id, partner_id,
                                    is_delivery_point_exists, has_postcontrol, accepted_delivery_statuses, distribute,
                                    message_for_noncall, courier_appointed_sms_on, courier_appointed_sms,
                                    days_to_delivery)
           VALUES (4, 'Базовая кредитная карта 4', 'document', '00:00', '{planned}', null, 3, true, false, null, false,
                   null, false, null, null);
           INSERT INTO public.item (id, name, item_type, delivery_time, delivery_type, category_id, partner_id,
                                    is_delivery_point_exists, has_postcontrol, accepted_delivery_statuses, distribute,
                                    message_for_noncall, courier_appointed_sms_on, courier_appointed_sms,
                                    days_to_delivery)
           VALUES (5, 'Базовая кредитная карта 5', 'document', '00:00', '{planned}', null, 3, true, false, null, false,
                   null, false, null, null);
           """


def item_city_insert_script() -> str:
    return """
        INSERT INTO public.item_city (city_id, item_id, id) 
        VALUES (1, 1, 1);
        INSERT INTO public.item_city (city_id, item_id, id) 
        VALUES (2, 1, 2);
        INSERT INTO public.item_city (city_id, item_id, id) 
        VALUES (3, 1, 3);
        INSERT INTO public.item_city (city_id, item_id, id) 
        VALUES (1, 2, 4);
        INSERT INTO public.item_city (city_id, item_id, id) 
        VALUES (2, 2, 5);
        INSERT INTO public.item_city (city_id, item_id, id) 
        VALUES (3, 2, 6);
        INSERT INTO public.item_city (city_id, item_id, id) 
        VALUES (4, 3, 7);
        INSERT INTO public.item_city (city_id, item_id, id) 
        VALUES (4, 4, 8);
        INSERT INTO public.item_city (city_id, item_id, id) 
        VALUES (4, 5, 9);
    """
