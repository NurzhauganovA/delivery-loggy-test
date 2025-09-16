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

            "product_type": "pos_terminal",

            "payload": {
                "is_installment_enabled": false,
                "company_name": "ТОО Рога и Копыта",
                "merchant_id": "1",
                "terminal_id": "1",
                "store_name": "MyMart",
                "branch_name": "Основной MyMart",
                "mcc_code": "GGG1",
                "oked_code": "QWERTY123"
            }
        }
    """
    return json


@pytest.fixture
def api_key() -> str:
    return "1111"


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
