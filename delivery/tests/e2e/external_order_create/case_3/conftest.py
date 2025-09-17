import pytest

from tests.fixtures.default_pre_start_sql_scripts import (
    default_countries_insert_script,
    default_cities_insert_script,
    statuses_insert_script
)


@pytest.fixture
def body() -> str:
    json = """
        {
            "city": "Алматы",
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
            "address": "Алматы, Жибек Жолы 135",
            "latitude": 72.12332,
            "longitude": 41.232355,
            "partner_order_id": "223o486346082346074360349",
            "payload": {}
        }
    """
    return json


@pytest.fixture
def api_key() -> str:
    return "1111"


@pytest.fixture
def expected() -> dict:
    return {
        "actual_delivery_datetime": None,
        "city_id": 1,
        "partner_id": 1,
        "partner_order_id": "223o486346082346074360349",
        "main_order_id": None,
        "item_id": 1,
        "type": "planned",
        "delivery_datetime": "2025-03-13T12:22:00.350000+00:00",
        "delivery_status": {
            "status": None,
            "datetime": None,
            "comment": None,
            "reason": None,
        },
        "receiver_iin": "012345050101",
        "receiver_name": "Нурсултан Кемелович",
        "receiver_phone_number": "+77071112233",
        "client_code": None,
        "has_receiver_feedback": None,
        "comment": "sample comment",
        "area_id": None,
        "created_by": "integration",
        "order_group_id": None,
        "revised": False,
        "id": 1,
        "order_chain_stages": None,
        "initial_delivery_datetime": "2025-03-13T12:22:00.350000+00:00",
        "courier_id": None,
        "created_at": "2025-04-14T17:00:00+00:00",
        "position": None,
        "courier": None,
        "city": {"id": 1, "name": "Almaty", "timezone": "Asia/Aqtau"},
        "area": None,
        "partner": {"id": 1, "name": 'Курьерская Служба 1', "article": "ОB", "courier_partner_id": None},
        "shipment_point_id": 1,
        "delivery_point_id": 1,
        "actual_delivery_datetime": None,
        "addresses": [
            {
                "position": 0,
                "type": "shipment_point",
                "id": 1,
                "place": {
                    "id": 1,
                    "address": 'Алматы, Muratbaev Street, 182, Алмалинский район, Элитная сауна "Status"',
                    "city_id": 1,
                    "latitude": 43.2467828,
                    "longitude": 76.9200415,
                },
            },
            {
                "position": 1,
                "type": "delivery_point",
                "id": 1,
                "place": {
                    "id": 1,
                    "address": "Алматы, Жибек Жолы 135",
                    "city_id": None,
                    "latitude": 72.12332,
                    "longitude": 41.232355,
                },
            },
        ],
        "item": {
            "name": "Базовая кредитная карта",
            "has_postcontrol": False,
            "message_for_noncall": None,
            "upload_from_gallery": True,
            "postcontrol_configs": [],
            "postcontrol_cancellation_configs": [],
            "accepted_delivery_statuses": None,
        },
        "deliverygraph": {
            "id": 1,
            "name": None,
            "slug": "Podgotovka + otp + Posledkontrol",
            "types": ["urgent", "operative", "planned"],
            "graph": [
                {
                    "position": 1,
                    "id": 1,
                    "name": "Новая заявка",
                    "slug": "novaia-zaiavka",
                    "icon": "order_new",
                    "button_name": None,
                },
                {
                    "position": 2,
                    "id": 30,
                    "name": "Упаковано",
                    "slug": "upakovano",
                    "icon": "packed",
                    "button_name": None,
                },
                {
                    "position": 3,
                    "id": 31,
                    "name": "Включено в группу",
                    "slug": "vkliucheno-v-gruppu",
                    "icon": "ready-to-send",
                    "button_name": None,
                },
                {
                    "position": 4,
                    "id": 23,
                    "name": "Готово к вывозу",
                    "slug": "gotovo-k-vyvozu",
                    "icon": "ready-to-send",
                    "button_name": None,
                },
                {
                    "position": 6,
                    "id": 32,
                    "name": "На сверке",
                    "slug": "na-sverke",
                    "icon": "at_revise",
                    "button_name": None,
                },
                {
                    "position": 7,
                    "id": 28,
                    "name": "Вывезено курьером",
                    "slug": "vyvezeno-kurerom",
                    "icon": "courier_accepted",
                    "button_name": None,
                },
                {
                    "position": 8,
                    "id": 29,
                    "name": "Принято курьерской службой",
                    "slug": "priniato-kurerskoi-sluzhboi",
                    "icon": "at-the-call-point",
                    "button_name": None,
                },
                {
                    "position": 9,
                    "id": 2,
                    "name": "Курьер назначен",
                    "slug": "kurer-naznachen",
                    "icon": "courier_appointed",
                    "button_name": "Принять в работу",
                },
                {
                    "position": 10,
                    "id": 3,
                    "name": "Принято курьером в работу",
                    "slug": "priniato-kurerom-v-rabotu",
                    "icon": "courier_accepted",
                    "button_name": "К точке вывоза",
                },
                {
                    "position": 11,
                    "id": 25,
                    "name": "У клиента",
                    "slug": "u-klienta",
                    "icon": "at_client",
                    "button_name": "Отправить SMS с кодом",
                },
                {
                    "position": 12,
                    "id": 20,
                    "name": "Код отправлен",
                    "slug": "kod-otpravlen",
                    "icon": "post_control",
                    "button_name": "Проверить код",
                },
                {
                    "position": 13,
                    "id": 16,
                    "name": "Фотографирование",
                    "slug": "fotografirovanie",
                    "icon": "post_control",
                    "button_name": "Отправить на последконтроль",
                },
                {
                    "position": 14,
                    "id": 12,
                    "name": "Последконтроль",
                    "slug": "posledkontrol",
                    "icon": "post_control",
                    "button_name": None,
                },
                {
                    "position": 15,
                    "id": 7,
                    "name": "Доставлено",
                    "slug": "dostavleno",
                    "icon": "order_delivered",
                    "button_name": None,
                },
            ],
            "partner_id": None,
        },
        "statuses": [
            {
                "status": {
                    "id": 1,
                    "name": None,
                    "icon": "order_new",
                    "slug": "novaia-zaiavka",
                },
                "created_at": "2025-04-14T17:00:00+00:00",
            }
        ],
        "last_otp": None,
        "current_status_id": 1,
        "product": None,
    }



@pytest.fixture
def pre_start_sql_script() -> str:
    """Важен порядок скриптов, так как есть зависимость от внешних ключей у таблиц"""
    scripts = [
        default_countries_insert_script(),
        default_cities_insert_script(),
        statuses_insert_script(),
        partners_insert_script(),
        partner_public_api_tokens_insert_script(),
        item_insert_script(),
        item_city_insert_script(),
        delivery_graphs_insert_script(),
        item_delivery_graphs_insert_script(),
        partner_shipment_points_insert_script(),
    ]

    return " ".join(scripts)

def partners_insert_script() -> str:
    return """
        INSERT INTO public.partner (id, name_kk, name_ru, name_en, activity_name_ru, address, affiliated, article, identifier, is_commerce, leader_data, consent_confirmed, is_government, is_international, email, registration_date, liq_date, liq_decision_date, credentials, courier_partner_id, created_at, start_work_hour, end_work_hour, type) 
        VALUES (1, 'Курьерская Служба 1', 'Курьерская Служба 1', null, null, 'город Алматы, Алмалинский район, Проспект АБЫЛАЙ ХАНА, дом: 91', false, 'ОB', '111111111111', true, '{"iin": "721107450542", "last_name": "ИБРАГИМОВА", "first_name": "ЛЯЗЗАТ", "middle_name": "ЕРКЕНОВНА"}', null, null, false, null, '2003-07-10 00:00:00.000000 +00:00', null, null, null, null, '2022-09-21 11:10:54.873492 +00:00', null, null, 'too');
    """


def partner_public_api_tokens_insert_script() -> str:
    return """
        INSERT INTO public."partner.publicapitoken" (id, token, created_at, is_expires, partner_id) 
        VALUES (1, '1111', '2025-05-02 10:06:29.716074 +00:00', false, 1);
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
        INSERT INTO public.deliverygraph (id, graph, partner_id, name_ru, slug, types, graph_courier, name_en, name_zh, name_kk) 
        VALUES (1, '[{"id": 1, "icon": "order_new", "name": "Новая заявка", "slug": "novaia-zaiavka", "position": 1, "button_name": null}, {"id": 30, "icon": "packed", "name": "Упаковано", "slug": "upakovano", "position": 2, "button_name": null}, {"id": 31, "icon": "ready-to-send", "name": "Включено в группу", "slug": "vkliucheno-v-gruppu", "position": 3, "button_name": null}, {"id": 23, "icon": "ready-to-send", "name": "Готово к вывозу", "slug": "gotovo-k-vyvozu", "position": 4, "button_name": null}, {"id": 32, "icon": "at_revise", "name": "На сверке", "slug": "na-sverke", "position": 6, "button_name": null}, {"id": 28, "icon": "courier_accepted", "name": "Вывезено курьером", "slug": "vyvezeno-kurerom", "position": 7, "button_name": null}, {"id": 29, "icon": "at-the-call-point", "name": "Принято курьерской службой", "slug": "priniato-kurerskoi-sluzhboi", "position": 8, "button_name": null}, {"id": 2, "icon": "courier_appointed", "name": "Курьер назначен", "slug": "kurer-naznachen", "position": 9, "button_name": "Принять в работу"}, {"id": 3, "icon": "courier_accepted", "name": "Принято курьером в работу", "slug": "priniato-kurerom-v-rabotu", "position": 10, "button_name": "К точке вывоза"}, {"id": 25, "icon": "at_client", "name": "У клиента", "slug": "u-klienta", "position": 11, "button_name": "Отправить SMS с кодом"}, {"id": 20, "icon": "post_control", "name": "Код отправлен", "slug": "kod-otpravlen", "position": 12, "button_name": "Проверить код"}, {"id": 16, "icon": "post_control", "name": "Фотографирование", "slug": "fotografirovanie", "position": 13, "button_name": "Отправить на последконтроль"}, {"id": 12, "icon": "post_control", "name": "Последконтроль", "slug": "posledkontrol", "position": 14, "button_name": null}, {"id": 7, "icon": "order_delivered", "name": "Доставлено", "slug": "dostavleno", "position": 15, "button_name": null}]', null, 'Подготовка + otp + Последконтроль', 'Podgotovka + otp + Posledkontrol', '{urgent,operative,planned}', '[{"id": 1, "icon": "order_new", "name": "Новая заявка", "slug": "novaia-zaiavka", "position": 1, "button_name": null}, {"id": 30, "icon": "packed", "name": "Упаковано", "slug": "upakovano", "position": 2, "button_name": null}, {"id": 31, "icon": "ready-to-send", "name": "Включено в группу", "slug": "vkliucheno-v-gruppu", "position": 3, "button_name": null}, {"id": 23, "icon": "ready-to-send", "name": "Готово к вывозу", "slug": "gotovo-k-vyvozu", "position": 4, "button_name": null}, {"id": 32, "icon": "at_revise", "name": "На сверке", "slug": "na-sverke", "position": 6, "button_name": null}, {"id": 28, "icon": "courier_accepted", "name": "Вывезено курьером", "slug": "vyvezeno-kurerom", "position": 7, "button_name": null}, {"id": 29, "icon": "at-the-call-point", "name": "Принято курьерской службой", "slug": "priniato-kurerskoi-sluzhboi", "position": 8, "button_name": null}, {"id": 2, "icon": "courier_appointed", "name": "Курьер назначен", "slug": "kurer-naznachen", "position": 9, "button_name": "Принять в работу"}, {"id": 3, "icon": "courier_accepted", "name": "Принято курьером в работу", "slug": "priniato-kurerom-v-rabotu", "position": 10, "button_name": "К точке вывоза"}, {"id": 25, "icon": "at_client", "name": "У клиента", "slug": "u-klienta", "position": 11, "button_name": "Отправить SMS с кодом"}, {"id": 20, "icon": "post_control", "name": "Код отправлен", "slug": "kod-otpravlen", "position": 12, "button_name": "Проверить код"}, {"id": 16, "icon": "post_control", "name": "Фотографирование", "slug": "fotografirovanie", "position": 13, "button_name": "Отправить на последконтроль"}, {"id": 12, "icon": "post_control", "name": "Последконтроль", "slug": "posledkontrol", "position": 14, "button_name": null}, {"id": 7, "icon": "order_delivered", "name": "Доставлено", "slug": "dostavleno", "position": 15, "button_name": null}]', null, null, null);
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
