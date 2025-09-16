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
        'profile_type': 'supervisor',
        'profile_id': '1',
    }


@pytest.fixture
def expected():
    return {
        'current_page': 1,
        'items': [
            {
                'address': 'Address 1',
                'city': {'country': {'id': 1, 'name': 'Kazakhstan'},
                         'id': 1,
                         'name': 'Almaty'},
                'id': 1,
                'latitude': 73.234353,
                'longitude': 41.23523524,
                'name': 'Shipment point 1',
                'partner': {'id': 1, 'name': 'Курьерская Служба 1'}
            },
            {
                'address': 'Address 2',
                'city': {'country': {'id': 1, 'name': 'Kazakhstan'},
                         'id': 1,
                         'name': 'Almaty'},
                'id': 2,
                'latitude': 73.234353,
                'longitude': 41.23523524,
                'name': 'Shipment point 2',
                'partner': {'id': 1, 'name': 'Курьерская Служба 1'}
            },
            {
                'address': 'Address 3',
                'city': {'country': {'id': 1, 'name': 'Kazakhstan'},
                         'id': 1,
                         'name': 'Almaty'},
                'id': 3,
                'latitude': 73.234353,
                'longitude': 41.23523524,
                'name': 'Shipment point 3',
                'partner': {'id': 1, 'name': 'Курьерская Служба 1'}
            },
            {
                'address': 'Address 4',
                'city': {'country': {'id': 1, 'name': 'Kazakhstan'},
                         'id': 1,
                         'name': 'Almaty'},
                'id': 4,
                'latitude': 73.234353,
                'longitude': 41.23523524,
                'name': 'Shipment point 4',
                'partner': {'id': 1, 'name': 'Курьерская Служба 1'}
            },
            {
                'address': 'Address 5',
                'city': {'country': {'id': 1, 'name': 'Kazakhstan'},
                         'id': 1,
                         'name': 'Almaty'},
                'id': 5,
                'latitude': 73.234353,
                'longitude': 41.23523524,
                'name': 'Shipment point 5',
                'partner': {'id': 1, 'name': 'Курьерская Служба 1'}
            },
            {
                'address': 'Address 6',
                'city': {'country': {'id': 1, 'name': 'Kazakhstan'},
                         'id': 1,
                         'name': 'Almaty'},
                'id': 6,
                'latitude': 73.234353,
                'longitude': 41.23523524,
                'name': 'Shipment point 6',
                'partner': {'id': 1, 'name': 'Курьерская Служба 1'}
            }
        ],
        'total': 6,
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
        shipment_points_insert_script(),
        profile_supervisor_insert_script(),
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
           """


def profile_supervisor_insert_script() -> str:
    return """
           INSERT INTO public.profile_supervisor (id, user_id, partner_id, country_id)
           VALUES (1, 1, 1, 1);
           """


def groups_users_insert_script() -> str:
    return """
           INSERT INTO public.groups_user (user_id, groups_id, id)
           VALUES (1, 'supervisor', 1);
           """


def shipment_points_insert_script() -> str:
    return """
           INSERT INTO public.partner_shipment_point (id, name, partner_id, address, latitude, longitude, city_id)
           VALUES 
             (1, 'Shipment point 1', 1, 'Address 1', '73.234353', '41.235235235', 1),
             (2, 'Shipment point 2', 1, 'Address 2', '73.234353', '41.235235235', 1),
             (3, 'Shipment point 3', 1, 'Address 3', '73.234353', '41.235235235', 1),
             (4, 'Shipment point 4', 1, 'Address 4', '73.234353', '41.235235235', 1),
             (5, 'Shipment point 5', 1, 'Address 5', '73.234353', '41.235235235', 1),
             (6, 'Shipment point 6', 1, 'Address 6', '73.234353', '41.235235235', 1)
            ;
           """
