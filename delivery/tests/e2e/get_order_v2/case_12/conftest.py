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
def expected_sub_statuses() -> list:
    return [
        {
            "name": "Принят на склад отправителя",
            "created_at": "2024-02-08T06:15:00+00:00"
        },
        {
            "name": "Отправлен в г. транзит",
            "created_at": "2024-02-08T08:30:00+00:00"
        },
        {
            "name": "Принят на склад транзита",
            "created_at": "2024-02-08T10:45:00+00:00"
        }
    ]


@pytest.fixture
def pre_start_sql_script() -> str:
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
        order_statuses_insert_script(),
        courier_service_statuses_insert_script(),
    ]
    return " ".join(scripts)


def users_insert_script() -> str:
    return """
        INSERT INTO public."user" (id, phone_number, first_name, last_name, middle_name, iin, credentials, is_active, photo, personal_agreement, created_at, is_superuser, email, password) 
        VALUES (1, '+77777777777', 'Служба 1', 'Службавна 1', 'Службавна 1', null, null, true, '', null, '2023-01-13 12:08:19.000000 +00:00', false, 'test_1@gmail.com', '$2b$12$KzP.BVjQGSu4O/D9XajUP.UikCQ4SWC47mr9XMDztCroWFiHmC2zy');
    """


def partners_insert_script() -> str:
    return """
        INSERT INTO public.partner (id, name_ru, article) 
        VALUES (1, 'Курьерская Служба 1', 'ОB');
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
        INSERT INTO public.item (id, name, item_type) 
        VALUES (1, 'Тестовый товар', 'document');
    """


def item_city_insert_script() -> str:
    return """
        INSERT INTO public.item_city (city_id, item_id, id) 
        VALUES (1, 1, 1);
    """


def delivery_graphs_insert_script() -> str:
    return """
        INSERT INTO public.deliverygraph (id, graph, graph_courier) 
        VALUES (1, '[]', '[]');
    """


def delivery_points_insert_script() -> str:
    return """
        INSERT INTO public.delivery_point (id, address, latitude, longitude) 
        VALUES (1, 'Тестовый адрес', 43.16545200, 76.87401300);
    """


def areas_insert_script() -> str:
    return """
        INSERT INTO public.area (id, slug, scope, city_id, partner_id) 
        VALUES (1, 'test-area', '[]', 1, 1);
    """


def profile_couriers_insert_script() -> str:
    return """
        INSERT INTO public.profile_courier (id, city_id, user_id, partner_id) 
        VALUES (1, 1, 1, 1);
    """


def profile_courier_areas_insert_script() -> str:
    return """
        INSERT INTO public.profile_courier_area (area_id, profile_courier_id, id) 
        VALUES (1, 1, 1);
    """


def orders_insert_script() -> str:
    return """
        INSERT INTO public."order" (id, type, created_at, receiver_phone_number, city_id, item_id, partner_id, deliverygraph_id, delivery_point_id, current_status_id) 
        VALUES (1, 'planned', '2024-02-08 06:11:17.160374 +00:00', '+77781254616', 1, 1, 1, 1, 1, 37);
    """


def order_statuses_insert_script() -> str:
    """Добавляем записи в order_status - связь заказа со статусами"""
    return """
        INSERT INTO public.order_status (id, order_id, status_id, created_at) 
        VALUES 
            (1, 1, 1, '2024-02-08 06:11:17.160374 +00:00'),
            (2, 1, 37, '2024-02-08 06:12:00.000000 +00:00');
    """


def courier_service_statuses_insert_script() -> str:
    """Добавляем саб-статусы СДЕК"""
    return """
        INSERT INTO public.courier_service_status (id, order_id, status_id, code, created_at) 
        VALUES 
            (1, 1, 37, 'ACCEPTED', '2024-02-08 06:15:00.000000 +00:00'),
            (2, 1, 37, 'SENT_TO_TRANSIT', '2024-02-08 08:30:00.000000 +00:00'),
            (3, 1, 37, 'ACCEPTED_IN_TRANSIT_CITY', '2024-02-08 10:45:00.000000 +00:00');
    """