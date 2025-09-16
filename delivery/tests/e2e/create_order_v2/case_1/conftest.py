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
def order_create_with_pos_terminal_body() -> str:
    json = """
        {
            "distribute_now": false,
            "order": {
                "city_id": 1,
                "partner_id": 1,
                "delivery_point": {
                    "address": "Жибек Жолы 135",
                    "latitude": "42.23156000",
                    "longitude": "69.79510000"
                },
                "comment": "sample comment",
                "delivery_datetime": "2025-03-13T12:22:00.350Z",
                "item_id": 1,
                "shipment_point_id": 1,
                "receiver_name": "Нурсултан Кемелович",
                "receiver_phone_number": "+77071112233",
                "receiver_iin": "012345050101",
                "type": "planned",
                "callbacks": {
                    "set_otp": "https://bankffin.kz/api/set-opt?orderId=1234",
                    "set_pan": "https://bankffin.kz/api/set-pan?orderId=1234",
                    "set_photo_urls": "https://bankffin.kz/api/set-photo?orderId=1234"
                },
                
                "product_type": "pos_terminal",
                "payload": {
                    "is_installment_enabled": false,
                    "is_installment_limit": true,
                    "company_name": "ТОО Рога и Копыта",
                    "merchant_id": "12345678",
                    "terminal_id": "12345678",
                    "store_name": "MyMart",
                    "branch_name": "Основной MyMart",
                    "mcc_code": "GGG1",
                    "oked_code": "QWERTY123",
                    "oked_text": "OKED SAMPLE TEXT",
                    "request_number_ref": "123456789",
                    "inventory_number": "123456789",
                    "sum": 10000.1
                }
            }
        }
    """
    return json


@pytest.fixture
def expected() -> dict:
    return {
        'actual_delivery_datetime': None,
        'area': None,
        'city': {'id': 1, 'name': 'Almaty', 'timezone': 'Asia/Aqtau'},
        'comment': 'sample comment',
        'courier': None,
        'created_at': '2025-04-14T17:00:00+00:00',
        'created_by': 'service',
        'current_status': {
            'icon': 'order_new',
            'id': 1,
            'name': None,
            'slug': 'novaia-zaiavka'
        },
        'current_status_position': 1,
        'delivery_datetime': '2025-03-13T12:22:00.350000+00:00',
        'delivery_point': {
            'address': 'Жибек Жолы 135',
            'id': 1,
            'latitude': 42.23156,
            'longitude': 69.7951
        },
        'delivery_status': {
            'comment': None,
            'datetime': None,
            'reason': None,
            'status': None
        },
        'deliverygraph': {
            'graph': [
                {'button_name': None,
                 'icon': 'order_new',
                 'id': 1,
                 'name': 'Новая заявка',
                 'position': 1,
                 'slug': 'novaia-zaiavka',
                 'status': None,
                 'transitions': None},
                {'button_name': None,
                 'icon': 'packed',
                 'id': 30,
                 'name': 'Упаковано',
                 'position': 2,
                 'slug': 'upakovano',
                 'status': None,
                 'transitions': None},
                {'button_name': None,
                 'icon': 'ready-to-send',
                 'id': 31,
                 'name': 'Включено в группу',
                 'position': 3,
                 'slug': 'vkliucheno-v-gruppu',
                 'status': None,
                 'transitions': None},
                {'button_name': None,
                 'icon': 'ready-to-send',
                 'id': 23,
                 'name': 'Готово к вывозу',
                 'position': 4,
                 'slug': 'gotovo-k-vyvozu',
                 'status': None,
                 'transitions': None},
                {'button_name': None,
                 'icon': 'at_revise',
                 'id': 32,
                 'name': 'На сверке',
                 'position': 6,
                 'slug': 'na-sverke',
                 'status': None,
                 'transitions': None},
                {'button_name': None,
                 'icon': 'courier_accepted',
                 'id': 28,
                 'name': 'Вывезено курьером',
                 'position': 7,
                 'slug': 'vyvezeno-kurerom',
                 'status': None,
                 'transitions': None},
                {'button_name': None,
                 'icon': 'at-the-call-point',
                 'id': 29,
                 'name': 'Принято курьерской службой',
                 'position': 8,
                 'slug': 'priniato-kurerskoi-sluzhboi',
                 'status': None,
                 'transitions': None},
                {'button_name': 'Принять в работу',
                 'icon': 'courier_appointed',
                 'id': 2,
                 'name': 'Курьер назначен',
                 'position': 9,
                 'slug': 'kurer-naznachen',
                 'status': None,
                 'transitions': None},
                {'button_name': 'К точке вывоза',
                 'icon': 'courier_accepted',
                 'id': 3,
                 'name': 'Принято курьером в работу',
                 'position': 10,
                 'slug': 'priniato-kurerom-v-rabotu',
                 'status': None,
                 'transitions': None},
                {'button_name': 'Отправить SMS с кодом',
                 'icon': 'at_client',
                 'id': 25,
                 'name': 'У клиента',
                 'position': 11,
                 'slug': 'u-klienta',
                 'status': None,
                 'transitions': None},
                {'button_name': 'Проверить код',
                 'icon': 'post_control',
                 'id': 20,
                 'name': 'Код отправлен',
                 'position': 12,
                 'slug': 'kod-otpravlen',
                 'status': None,
                 'transitions': None},
                {'button_name': 'Отправить на последконтроль',
                 'icon': 'post_control',
                 'id': 16,
                 'name': 'Фотографирование',
                 'position': 13,
                 'slug': 'fotografirovanie',
                 'status': None,
                 'transitions': None},
                {'button_name': None,
                 'icon': 'post_control',
                 'id': 12,
                 'name': 'Последконтроль',
                 'position': 14,
                 'slug': 'posledkontrol',
                 'status': None,
                 'transitions': None},
                {'button_name': None,
                 'icon': 'order_delivered',
                 'id': 7,
                 'name': 'Доставлено',
                 'position': 15,
                 'slug': 'dostavleno',
                 'status': None,
                 'transitions': None}
            ]
        },
        'deliverygraph_step_count': 14,
        'id': 1,
        'idn': None,
        'initial_delivery_datetime': '2025-03-13T12:22:00.350000+00:00',
        'item': {
            'accepted_delivery_statuses': None,
            'has_postcontrol': False,
            'name': 'Базовая кредитная карта',
            'postcontrol_configs': [],
            'upload_from_gallery': True
        },
        'last_otp': None,
        'manager': None,
        'partner': {'article': 'ОB',
                    'courier_partner_id': None,
                    'id': 1,
                    'name': 'Курьерская Служба 1'},
        'product': {
            'attributes': {
                'branch_name': 'Основной MyMart',
                'company_name': 'ТОО Рога и Копыта',
                'is_installment_enabled': False,
                'is_installment_limit': True,
                'mcc_code': 'GGG1',
                'merchant_id': '12345678',
                'model': None,
                'oked_code': 'QWERTY123',
                'oked_text': 'OKED SAMPLE TEXT',
                'request_number_ref': '123456789',
                'serial_number': None,
                'store_name': 'MyMart',
                'terminal_id': '12345678',
                'inventory_number': '123456789',
                'sum': 10000.1
            },
            'id': 1,
            'type': 'pos_terminal'
        },
        'receiver_iin': '012345050101',
        'receiver_name': 'Нурсултан Кемелович',
        'receiver_phone_number': '+77071112233',
        'shipment_point': {
            'address': 'Алматы, Muratbaev Street, 182, Алмалинский '
                       'район, Элитная сауна "Status"',
            'latitude': 43.2467828,
            'longitude': 76.9200415,
            'name': 'Алматы, Muratbaev Street, 182, Алмалинский район, '
                    'Элитная сауна "Status"'
        },
        'statuses': [
            {
                'created_at': '2025-04-14T17:00:00+00:00',
                'status': {
                    'after': [],
                    'icon': 'order_new',
                    'id': 1,
                    'is_optional': False,
                    'name': None,
                    'partner_id': None,
                    'slug': 'novaia-zaiavka'
                }
            }
        ],
        'type': 'planned'
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
        item_city_insert_script(),
        delivery_graphs_insert_script(),
        item_delivery_graphs_insert_script(),
        partner_shipment_points_insert_script(),
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


def item_insert_script() -> str:
    return """
        INSERT INTO public.item (id, name, item_type, delivery_time, delivery_type, category_id, partner_id, is_delivery_point_exists, has_postcontrol, accepted_delivery_statuses, distribute, message_for_noncall, courier_appointed_sms_on, courier_appointed_sms, days_to_delivery) 
        VALUES (1, 'Базовая кредитная карта', 'document', '00:00', '{planned}', null, 1, true, false, null, false, null, false, null, null);
    """


def item_city_insert_script() -> str:
    return """
        INSERT INTO public.item_city (city_id, item_id, id) 
        VALUES (1, 1, 1);
    """


def delivery_graphs_insert_script() -> str:
    return """
        INSERT INTO public.deliverygraph (id, graph, partner_id, name, slug, types, graph_courier, name_en, name_zh, name_ru, name_kk) 
        VALUES (1, '[{"id": 1, "icon": "order_new", "name": "Новая заявка", "slug": "novaia-zaiavka", "position": 1, "button_name": null}, {"id": 30, "icon": "packed", "name": "Упаковано", "slug": "upakovano", "position": 2, "button_name": null}, {"id": 31, "icon": "ready-to-send", "name": "Включено в группу", "slug": "vkliucheno-v-gruppu", "position": 3, "button_name": null}, {"id": 23, "icon": "ready-to-send", "name": "Готово к вывозу", "slug": "gotovo-k-vyvozu", "position": 4, "button_name": null}, {"id": 32, "icon": "at_revise", "name": "На сверке", "slug": "na-sverke", "position": 6, "button_name": null}, {"id": 28, "icon": "courier_accepted", "name": "Вывезено курьером", "slug": "vyvezeno-kurerom", "position": 7, "button_name": null}, {"id": 29, "icon": "at-the-call-point", "name": "Принято курьерской службой", "slug": "priniato-kurerskoi-sluzhboi", "position": 8, "button_name": null}, {"id": 2, "icon": "courier_appointed", "name": "Курьер назначен", "slug": "kurer-naznachen", "position": 9, "button_name": "Принять в работу"}, {"id": 3, "icon": "courier_accepted", "name": "Принято курьером в работу", "slug": "priniato-kurerom-v-rabotu", "position": 10, "button_name": "К точке вывоза"}, {"id": 25, "icon": "at_client", "name": "У клиента", "slug": "u-klienta", "position": 11, "button_name": "Отправить SMS с кодом"}, {"id": 20, "icon": "post_control", "name": "Код отправлен", "slug": "kod-otpravlen", "position": 12, "button_name": "Проверить код"}, {"id": 16, "icon": "post_control", "name": "Фотографирование", "slug": "fotografirovanie", "position": 13, "button_name": "Отправить на последконтроль"}, {"id": 12, "icon": "post_control", "name": "Последконтроль", "slug": "posledkontrol", "position": 14, "button_name": null}, {"id": 7, "icon": "order_delivered", "name": "Доставлено", "slug": "dostavleno", "position": 15, "button_name": null}]', null, 'Подготовка + otp + Последконтроль', 'Podgotovka + otp + Posledkontrol', '{urgent,operative,planned}', '[{"id": 1, "icon": "order_new", "name": "Новая заявка", "slug": "novaia-zaiavka", "position": 1, "button_name": null}, {"id": 30, "icon": "packed", "name": "Упаковано", "slug": "upakovano", "position": 2, "button_name": null}, {"id": 31, "icon": "ready-to-send", "name": "Включено в группу", "slug": "vkliucheno-v-gruppu", "position": 3, "button_name": null}, {"id": 23, "icon": "ready-to-send", "name": "Готово к вывозу", "slug": "gotovo-k-vyvozu", "position": 4, "button_name": null}, {"id": 32, "icon": "at_revise", "name": "На сверке", "slug": "na-sverke", "position": 6, "button_name": null}, {"id": 28, "icon": "courier_accepted", "name": "Вывезено курьером", "slug": "vyvezeno-kurerom", "position": 7, "button_name": null}, {"id": 29, "icon": "at-the-call-point", "name": "Принято курьерской службой", "slug": "priniato-kurerskoi-sluzhboi", "position": 8, "button_name": null}, {"id": 2, "icon": "courier_appointed", "name": "Курьер назначен", "slug": "kurer-naznachen", "position": 9, "button_name": "Принять в работу"}, {"id": 3, "icon": "courier_accepted", "name": "Принято курьером в работу", "slug": "priniato-kurerom-v-rabotu", "position": 10, "button_name": "К точке вывоза"}, {"id": 25, "icon": "at_client", "name": "У клиента", "slug": "u-klienta", "position": 11, "button_name": "Отправить SMS с кодом"}, {"id": 20, "icon": "post_control", "name": "Код отправлен", "slug": "kod-otpravlen", "position": 12, "button_name": "Проверить код"}, {"id": 16, "icon": "post_control", "name": "Фотографирование", "slug": "fotografirovanie", "position": 13, "button_name": "Отправить на последконтроль"}, {"id": 12, "icon": "post_control", "name": "Последконтроль", "slug": "posledkontrol", "position": 14, "button_name": null}, {"id": 7, "icon": "order_delivered", "name": "Доставлено", "slug": "dostavleno", "position": 15, "button_name": null}]', null, null, null, null);
    """


def item_delivery_graphs_insert_script() -> str:
    return """
        INSERT INTO public.item_deliverygraph (deliverygraph_id, item_id, id) 
        VALUES (1, 1, 1);
    """


def partner_shipment_points_insert_script() -> str:
    return """
        INSERT INTO public.partner_shipment_point (id, name, partner_id, address, latitude, longitude, city_id) 
        VALUES (1, 'Алматы, Muratbaev Street, 182, Алмалинский район, Элитная сауна "Status"', 1, 'Алматы, Muratbaev Street, 182, Алмалинский район, Элитная сауна "Status"', 43.24678280, 76.92004150, 1);
    """
