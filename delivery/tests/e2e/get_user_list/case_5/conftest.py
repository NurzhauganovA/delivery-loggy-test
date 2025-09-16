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
        'profile_type': 'support',
        'profile_id': '1',
    }


@pytest.fixture
def expected():
    return {
        'current_page': 1,
        'items': [
            {
                'credentials': None,
                'email': 'courier_1@gmail.com',
                'first_name': 'Курьер 1',
                'id': 2,
                'iin': None,
                'invited_by': None,
                'is_active': True,
                'last_message': None,
                'last_name': 'Курьеров 1',
                'middle_name': 'Курьерович 1',
                'phone_number': '+77777777771',
                'photo': None,
                'profiles': [
                    {
                        'id': 1,
                        'profile_content': {
                            'areas': [],
                            'at_work': False,
                            'average_time_deviation': 0,
                            'category_id': None,
                            'city': {'id': 1,
                                     'name': 'Almaty'},
                            'city_id': 1,
                            'created_at': "2025-06-03T10:00:00.000000+00:00",
                            'current_rate': 100,
                            'end_work_hour': None,
                            'experience_months': 0,
                            'experience_years': 0,
                            'iban': None,
                            'is_biometry_verificated': False,
                            'is_identified': False,
                            'item_type': None,
                            'orders_delivered_today': 0,
                            'partner_id': 1,
                            'register_with_biometry': False,
                            'schedule': None,
                            'start_work_hour': None,
                            'state': None,
                            'status': 'invited',
                            'transport_type': None},
                        'profile_type': 'courier',
                        'user_id': 2
                    }
                ]
            },
            {
                'credentials': None,
                'email': 'courier_2@gmail.com',
                'first_name': 'Курьер 2',
                'id': 3,
                'iin': None,
                'invited_by': None,
                'is_active': True,
                'last_message': None,
                'last_name': 'Курьеров 2',
                'middle_name': 'Курьерович 2',
                'phone_number': '+77777777772',
                'photo': None,
                'profiles': [
                    {
                        'id': 2,
                        'profile_content': {
                            'areas': [],
                            'at_work': False,
                            'average_time_deviation': 0,
                            'category_id': None,
                            'city': {
                                'id': 2,
                                'name': 'Astana'
                            },
                            'city_id': 2,
                            'created_at': "2025-06-03T10:00:00.000000+00:00",
                            'current_rate': 100,
                            'end_work_hour': None,
                            'experience_months': 0,
                            'experience_years': 0,
                            'iban': None,
                            'is_biometry_verificated': False,
                            'is_identified': False,
                            'item_type': None,
                            'orders_delivered_today': 0,
                            'partner_id': 1,
                            'register_with_biometry': False,
                            'schedule': None,
                            'start_work_hour': None,
                            'state': None,
                            'status': 'invited',
                            'transport_type': None},
                        'profile_type': 'courier',
                        'user_id': 3
                    }
                ]
            },
            {
                'credentials': None,
                'email': 'courier_3@gmail.com',
                'first_name': 'Курьер 3',
                'id': 4,
                'iin': None,
                'invited_by': None,
                'is_active': True,
                'last_message': None,
                'last_name': 'Курьеров 3',
                'middle_name': 'Курьерович 3',
                'phone_number': '+77777777773',
                'photo': None,
                'profiles': [
                    {
                        'id': 3,
                        'profile_content': {
                            'areas': [],
                            'at_work': False,
                            'average_time_deviation': 0,
                            'category_id': None,
                            'city': {'id': 3,
                                     'name': 'Qaraganda'},
                            'city_id': 3,
                            'created_at': "2025-06-03T10:00:00.000000+00:00",
                            'current_rate': 100,
                            'end_work_hour': None,
                            'experience_months': 0,
                            'experience_years': 0,
                            'iban': None,
                            'is_biometry_verificated': False,
                            'is_identified': False,
                            'item_type': None,
                            'orders_delivered_today': 0,
                            'partner_id': 1,
                            'register_with_biometry': False,
                            'schedule': None,
                            'start_work_hour': None,
                            'state': None,
                            'status': 'invited',
                            'transport_type': None},
                        'profile_type': 'courier',
                        'user_id': 4
                    }
                ]
            }
        ],
        'total': 3,
        'total_pages': 1
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
        profile_supports_insert_script(),
        profile_couriers_insert_script(),
        groups_users_insert_script(),
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
           VALUES (3, '+77777777772', 'Курьер 2', 'Курьеров 2', 'Курьерович 2', null, null, true, '', null,
                   '2023-01-13 12:08:19.000000 +00:00', false, 'courier_2@gmail.com',
                   '$2b$12$KzP.BVjQGSu4O/D9XajUP.UikCQ4SWC47mr9XMDztCroWFiHmC2zy');

           INSERT INTO public."user" (id, phone_number, first_name, last_name, middle_name, iin, credentials, is_active,
                                      photo, personal_agreement, created_at, is_superuser, email, password)
           VALUES (4, '+77777777773', 'Курьер 3', 'Курьеров 3', 'Курьерович 3', null, null, true, '', null,
                   '2023-01-13 12:08:19.000000 +00:00', false, 'courier_3@gmail.com',
                   '$2b$12$KzP.BVjQGSu4O/D9XajUP.UikCQ4SWC47mr9XMDztCroWFiHmC2zy');

           INSERT INTO public."user" (id, phone_number, first_name, last_name, middle_name, iin, credentials, is_active,
                                      photo, personal_agreement, created_at, is_superuser, email, password)
           VALUES (5, '+77777777774', 'Курьер 4', 'Курьеров 4', 'Курьерович 4', null, null, true, '', null,
                   '2023-01-13 12:08:19.000000 +00:00', false, 'courier_4@gmail.com',
                   '$2b$12$KzP.BVjQGSu4O/D9XajUP.UikCQ4SWC47mr9XMDztCroWFiHmC2zy');

           INSERT INTO public."user" (id, phone_number, first_name, last_name, middle_name, iin, credentials, is_active,
                                      photo, personal_agreement, created_at, is_superuser, email, password)
           VALUES (6, '+77777777775', 'Курьер 5', 'Курьеров 5', 'Курьерович 5', null, null, true, '', null,
                   '2023-01-13 12:08:19.000000 +00:00', false, 'courier_5@gmail.com',
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
                   '2022-09-21 11:10:54.873492 +00:00', null, null, 'too'); \
           """


def profile_supports_insert_script() -> str:
    return """
           INSERT INTO public.profile_support (id, user_id, partner_id)
           VALUES (1, 1, 1);
           """


def profile_couriers_insert_script() -> str:
    return """
           INSERT INTO public.profile_courier (id, user_id, partner_id, city_id)
           VALUES (1, 2, 1, 1);
           
           INSERT INTO public.profile_courier (id, user_id, partner_id, city_id)
           VALUES (2, 3, 1, 2);
           
           INSERT INTO public.profile_courier (id, user_id, partner_id, city_id)
           VALUES (3, 4, 1, 3);
           
           INSERT INTO public.profile_courier (id, user_id, partner_id, city_id)
           VALUES (4, 5, 1, 4);
           
           INSERT INTO public.profile_courier (id, user_id, partner_id, city_id)
           VALUES (5, 6, 1, 4);
           """


def groups_users_insert_script() -> str:
    return """
           INSERT INTO public.groups_user (user_id, groups_id, id)
           VALUES (1, 'support', 1);
           """
