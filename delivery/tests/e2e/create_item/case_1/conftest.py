import pytest

from tests.fixtures.default_pre_start_sql_scripts import (
    default_countries_insert_script,
    default_cities_insert_script,
    statuses_insert_script, default_groups_insert_script, default_permissions_insert_script,
    default_groups_permissions_insert_script
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
def create_item_body():
    return {
        'name': 'Sample test item',
        'partner_id': 1,
        'delivery_type': ['planned'],
        'deliverygraphs': [1],
        'item_type': 'document',
        'is_delivery_point_exists': True,
        'courier_appointed_sms_on': False,

    }


@pytest.fixture
def expected_default_postcontrol_cancellation_configs() -> list[dict]:
    return [
        {
            'document_code': None,
            'id': 1,
            'inner_params': [
                {
                    'document_code': None,
                    'id': 2,
                    'name': 'Фотография 1',
                    'send': False
                },
                {
                    'document_code': None,
                    'id': 3,
                    'name': 'Фотография 2',
                    'send': False
                },
                {
                    'document_code': None,
                    'id': 4,
                    'name': 'Фотография 3',
                    'send': False
                },
                {
                    'document_code': None,
                    'id': 5,
                    'name': 'Фотография 4',
                    'send': False
                },
                {
                    'document_code': None,
                    'id': 6,
                    'name': 'Фотография 5',
                    'send': False
                }
            ],
            'name': 'Послед-контроль отмены',
            'send': False
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
        profile_service_managers_insert_script(),
        groups_users_insert_script(),
        delivery_graphs_insert_script(),
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

           ALTER SEQUENCE user_id_seq RESTART WITH 2;
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

           ALTER SEQUENCE groups_user_id_seq restart with 2;
           """


def delivery_graphs_insert_script() -> str:
    return """
        INSERT INTO public.deliverygraph (id, graph, partner_id, name_ru, slug, types, graph_courier, name_en, name_zh, name_kk) 
        VALUES (1, '[{"id": 1, "icon": "order_new", "name": "Новая заявка", "slug": "novaia-zaiavka", "position": 1, "button_name": null}, {"id": 30, "icon": "packed", "name": "Упаковано", "slug": "upakovano", "position": 2, "button_name": null}, {"id": 31, "icon": "ready-to-send", "name": "Включено в группу", "slug": "vkliucheno-v-gruppu", "position": 3, "button_name": null}, {"id": 23, "icon": "ready-to-send", "name": "Готово к вывозу", "slug": "gotovo-k-vyvozu", "position": 4, "button_name": null}, {"id": 32, "icon": "at_revise", "name": "На сверке", "slug": "na-sverke", "position": 6, "button_name": null}, {"id": 28, "icon": "courier_accepted", "name": "Вывезено курьером", "slug": "vyvezeno-kurerom", "position": 7, "button_name": null}, {"id": 29, "icon": "at-the-call-point", "name": "Принято курьерской службой", "slug": "priniato-kurerskoi-sluzhboi", "position": 8, "button_name": null}, {"id": 2, "icon": "courier_appointed", "name": "Курьер назначен", "slug": "kurer-naznachen", "position": 9, "button_name": "Принять в работу"}, {"id": 3, "icon": "courier_accepted", "name": "Принято курьером в работу", "slug": "priniato-kurerom-v-rabotu", "position": 10, "button_name": "К точке вывоза"}, {"id": 25, "icon": "at_client", "name": "У клиента", "slug": "u-klienta", "position": 11, "button_name": "Отправить SMS с кодом"}, {"id": 20, "icon": "post_control", "name": "Код отправлен", "slug": "kod-otpravlen", "position": 12, "button_name": "Проверить код"}, {"id": 16, "icon": "post_control", "name": "Фотографирование", "slug": "fotografirovanie", "position": 13, "button_name": "Отправить на последконтроль"}, {"id": 12, "icon": "post_control", "name": "Последконтроль", "slug": "posledkontrol", "position": 14, "button_name": null}, {"id": 7, "icon": "order_delivered", "name": "Доставлено", "slug": "dostavleno", "position": 15, "button_name": null}]', null, 'Подготовка + otp + Последконтроль', 'Podgotovka + otp + Posledkontrol', '{urgent,operative,planned}', '[{"id": 1, "icon": "order_new", "name": "Новая заявка", "slug": "novaia-zaiavka", "position": 1, "button_name": null}, {"id": 30, "icon": "packed", "name": "Упаковано", "slug": "upakovano", "position": 2, "button_name": null}, {"id": 31, "icon": "ready-to-send", "name": "Включено в группу", "slug": "vkliucheno-v-gruppu", "position": 3, "button_name": null}, {"id": 23, "icon": "ready-to-send", "name": "Готово к вывозу", "slug": "gotovo-k-vyvozu", "position": 4, "button_name": null}, {"id": 32, "icon": "at_revise", "name": "На сверке", "slug": "na-sverke", "position": 6, "button_name": null}, {"id": 28, "icon": "courier_accepted", "name": "Вывезено курьером", "slug": "vyvezeno-kurerom", "position": 7, "button_name": null}, {"id": 29, "icon": "at-the-call-point", "name": "Принято курьерской службой", "slug": "priniato-kurerskoi-sluzhboi", "position": 8, "button_name": null}, {"id": 2, "icon": "courier_appointed", "name": "Курьер назначен", "slug": "kurer-naznachen", "position": 9, "button_name": "Принять в работу"}, {"id": 3, "icon": "courier_accepted", "name": "Принято курьером в работу", "slug": "priniato-kurerom-v-rabotu", "position": 10, "button_name": "К точке вывоза"}, {"id": 25, "icon": "at_client", "name": "У клиента", "slug": "u-klienta", "position": 11, "button_name": "Отправить SMS с кодом"}, {"id": 20, "icon": "post_control", "name": "Код отправлен", "slug": "kod-otpravlen", "position": 12, "button_name": "Проверить код"}, {"id": 16, "icon": "post_control", "name": "Фотографирование", "slug": "fotografirovanie", "position": 13, "button_name": "Отправить на последконтроль"}, {"id": 12, "icon": "post_control", "name": "Последконтроль", "slug": "posledkontrol", "position": 14, "button_name": null}, {"id": 7, "icon": "order_delivered", "name": "Доставлено", "slug": "dostavleno", "position": 15, "button_name": null}]', null, null, null);
    """
