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
def expected():
    return [
        {
            'city_id': 1,
            'courier_number': 0,
            'fill_color': '#ff0000',
            'fill_opacity': 0.6,
            'id': 1,
            'partner_id': 1,
            'scope': [],
            'shipment_points': [],
            'slug': 'slug_1',
            'stroke_color': '#ff0000',
            'stroke_opacity': 1.0
        },
        {
            'city_id': 1,
            'courier_number': 0,
            'fill_color': '#ff0000',
            'fill_opacity': 0.6,
            'id': 2,
            'partner_id': 1,
            'scope': [],
            'shipment_points': [],
            'slug': 'slug_2',
            'stroke_color': '#ff0000',
            'stroke_opacity': 1.0
        },
        {
            'city_id': 1,
            'courier_number': 0,
            'fill_color': '#ff0000',
            'fill_opacity': 0.6,
            'id': 3,
            'partner_id': 1,
            'scope': [],
            'shipment_points': [],
            'slug': 'slug_3',
            'stroke_color': '#ff0000',
            'stroke_opacity': 1.0
        },
        {
            'city_id': 1,
            'courier_number': 0,
            'fill_color': '#ff0000',
            'fill_opacity': 0.6,
            'id': 4,
            'partner_id': 1,
            'scope': [],
            'shipment_points': [],
            'slug': 'slug_4',
            'stroke_color': '#ff0000',
            'stroke_opacity': 1.0
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
        profile_call_center_manager_insert_script(),
        groups_users_insert_script(),
        areas_insert_script(),
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
                   '2022-09-21 11:10:54.873492 +00:00', null, null, 'too');
           """


def profile_call_center_manager_insert_script() -> str:
    return """
           INSERT INTO public.profile_call_center_manager (id, user_id, partner_id, country_id)
           VALUES (1, 1, 1, 1);
           """


def profile_courier_insert_script() -> str:
    return """
           INSERT INTO public.profile_courier (id, user_id, partner_id, city_id)
           VALUES (1, 1, 1, 1);
           """


def groups_users_insert_script() -> str:
    return """
           INSERT INTO public.groups_user (user_id, groups_id, id)
           VALUES (1, 'call_center_manager', 1);
           """


def areas_insert_script() -> str:
    return """
    INSERT INTO public.area (id, slug, partner_id, city_id, scope)
    VALUES
      (1, 'slug_1', 1, 1, '[]'),
      (2, 'slug_2', 1, 1, '[]'),
      (3, 'slug_3', 1, 1, '[]'),
      (4, 'slug_4', 1, 1, '[]')
    ;
    """
