import json

import pytest

from api.domain.order import DeliveryGraph

__json = '''
[
	{
		"id": 1,
		"status": "new",
		"icon": "order_new",
		"slug": "novaia-zaiavka",
		"name_en": "New order",
		"name_ru": "Новая заявка",
		"position": 1,
		"button_name": null,
		"transitions": [
			{
				"trigger": "courier_assigned",
				"source": "new",
				"dest": "courier_assigned"
			},
			{
				"trigger": "card_returned_to_bank",
				"source": "new",
				"dest": "card_returned_to_bank"
			}
		]
	},
	{
		"id": 2,
		"status": "courier_assigned",
		"icon": "courier_appointed",
		"slug": "kurer-naznachen",
		"name_en": "Courier appointed",
		"name_ru": "Курьер назначен",
		"position": 2,
		"button_name": "Принять в работу",
		"transitions": [
			{
				"trigger": "in_way",
				"source": "courier_assigned",
				"dest": "in_way"
			},
			{
				"trigger": "card_returned_to_bank",
				"source": "courier_assigned",
				"dest": "card_returned_to_bank"
			}
		]
	},
	{
		"id": 3,
		"status": "in_way",
		"icon": "courier_accepted",
		"slug": "priniato-kurerom-v-rabotu",
		"name_en": "Courier accepted",
		"name_ru": "Принято курьером в работу",
		"position": 3,
		"button_name": "К клиенту",
		"transitions": [
			{
				"trigger": "send_otp",
				"source": "in_way",
				"dest": "send_otp"
			},
			{
				"trigger": "card_returned_to_bank",
				"source": "in_way",
				"dest": "card_returned_to_bank"
			}
		]
	},
	{
		"id": 25,
		"status": "send_otp",
		"icon": "at_client",
		"slug": "u-klienta",
		"name_en": "At client",
		"name_ru": "У клиента",
		"position": 4,
		"button_name": "Отправить SMS с кодом",
		"transitions": [
			{
				"trigger": "verify_otp",
				"source": "send_otp",
				"dest": "verify_otp"
			},
			{
				"trigger": "card_returned_to_bank",
				"source": "send_otp",
				"dest": "card_returned_to_bank"
			}
		]
	},
	{
		"id": 20,
		"status": "verify_otp",
		"icon": "post_control",
		"slug": "kod-otpravlen",
		"name_en": "OTP sent",
		"name_ru": "Код отправлен",
		"position": 5,
		"button_name": "Проверить код",
		"transitions": [
			{
				"trigger": "photo_capturing",
				"source": "verify_otp",
				"dest": "photo_capturing"
			},
			{
				"trigger": "card_returned_to_bank",
				"source": "verify_otp",
				"dest": "card_returned_to_bank"
			}
		]
	},
	{
		"id": 16,
		"status": "photo_capturing",
		"icon": "post_control",
		"slug": "fotografirovanie",
		"name_en": "Photo capturing",
		"name_ru": "Фотографирование",
		"position": 7,
		"button_name": "Отправить на последконтроль",
		"transitions": [
			{
				"trigger": "post_control",
				"source": "photo_capturing",
				"dest": "post_control"
			},
			{
				"trigger": "card_returned_to_bank",
				"source": "photo_capturing",
				"dest": "card_returned_to_bank"
			}
		]
	},
	{
		"id": 12,
		"status": "post_control",
		"icon": "post_control",
		"slug": "posledkontrol",
		"name_en": "Postcontrol",
		"name_ru": "Последконтроль",
		"position": 8,
		"button_name": null,
		"transitions": [
			{
				"trigger": "delivered",
				"source": "post_control",
				"dest": "delivered"
			},
			{
				"trigger": "card_returned_to_bank",
				"source": "post_control",
				"dest": "card_returned_to_bank"
			}
		]
	},
	{
		"id": 7,
		"status": "delivered",
		"icon": "order_delivered",
		"slug": "dostavleno",
		"name_en": "Delivered",
		"name_ru": "Доставлено",
		"position": 9,
		"button_name": null
	},
	{
		"id": 35,
		"status": "card_returned_to_bank",
		"icon": "card_returned_to_bank",
		"slug": "card-returned-to-bank",
		"name_en": "Card was returned to bank",
		"name_ru": "Карта возвращена в банк",
		"position": 0,
		"button_name": null,
		"transitions": [
			{
				"trigger": "new",
				"source": "card_returned_to_bank",
				"dest": "new"
			}
		]
	}
]
'''


@pytest.fixture
def raw_delivery_graph() -> [dict]:
    return  json.loads(__json)


@pytest.fixture
def delivery_graph() -> DeliveryGraph:
    return  DeliveryGraph(json.loads(__json))


__json_2 = '''
[
	{
		"id": 1,
		"status": "new",
		"icon": "order_new",
		"slug": "novaia-zaiavka",
		"name_en": "New order",
		"name_ru": "Новая заявка",
		"position": 1,
		"button_name": null,
		"transitions": [
			{
				"trigger": "courier_assigned",
				"source": "new",
				"dest": "courier_assigned"
			},
			{
				"trigger": "card_returned_to_bank",
				"source": "new",
				"dest": "card_returned_to_bank"
			}
		]
	},
	{
		"id": 2,
		"icon": "courier_appointed",
		"slug": "kurer-naznachen",
		"name_en": "Courier appointed",
		"name_ru": "Курьер назначен",
		"position": 2,
		"button_name": "Принять в работу"
	},
	{
		"id": 3,
		"status": "in_way",
		"icon": "courier_accepted",
		"slug": "priniato-kurerom-v-rabotu",
		"name_en": "Courier accepted",
		"name_ru": "Принято курьером в работу",
		"position": 3,
		"button_name": "К клиенту",
		"transitions": [
			{
				"trigger": "at_client",
				"source": "in_way",
				"dest": "at_client"
			},
			{
				"trigger": "card_returned_to_bank",
				"source": "in_way",
				"dest": "card_returned_to_bank"
			}
		]
	},
	{
		"id": 25,
		"status": "at_client",
		"icon": "at_client",
		"slug": "u-klienta",
		"name_en": "At client",
		"name_ru": "У клиента",
		"position": 4,
		"button_name": "Отправить SMS с кодом",
		"transitions": [
			{
				"trigger": "otp_sent",
				"source": "at_client",
				"dest": "otp_sent"
			},
			{
				"trigger": "card_returned_to_bank",
				"source": "at_client",
				"dest": "card_returned_to_bank"
			}
		]
	},
	{
		"id": 20,
		"status": "otp_sent",
		"icon": "post_control",
		"slug": "kod-otpravlen",
		"name_en": "OTP sent",
		"name_ru": "Код отправлен",
		"position": 5,
		"button_name": "Проверить код",
		"transitions": [
			{
				"trigger": "photo_capturing",
				"source": "otp_sent",
				"dest": "photo_capturing"
			},
			{
				"trigger": "card_returned_to_bank",
				"source": "otp_sent",
				"dest": "card_returned_to_bank"
			}
		]
	},
	{
		"id": 16,
		"status": "photo_capturing",
		"icon": "post_control",
		"slug": "fotografirovanie",
		"name_en": "Photo capturing",
		"name_ru": "Фотографирование",
		"position": 7,
		"button_name": "Отправить на последконтроль",
		"transitions": [
			{
				"trigger": "post_control",
				"source": "photo_capturing",
				"dest": "post_control"
			},
			{
				"trigger": "card_returned_to_bank",
				"source": "photo_capturing",
				"dest": "card_returned_to_bank"
			}
		]
	},
	{
		"id": 12,
		"status": "post_control",
		"icon": "post_control",
		"slug": "posledkontrol",
		"name_en": "Postcontrol",
		"name_ru": "Последконтроль",
		"position": 8,
		"button_name": null,
		"transitions": [
			{
				"trigger": "delivered",
				"source": "post_control",
				"dest": "delivered"
			},
			{
				"trigger": "card_returned_to_bank",
				"source": "post_control",
				"dest": "card_returned_to_bank"
			}
		]
	},
	{
		"id": 7,
		"status": "delivered",
		"icon": "order_delivered",
		"slug": "dostavleno",
		"name_en": "Delivered",
		"name_ru": "Доставлено",
		"position": 9,
		"button_name": null
	},
	{
		"id": 35,
		"status": "card_returned_to_bank",
		"icon": "card_returned_to_bank",
		"slug": "card-returned-to-bank",
		"name_en": "Card was returned to bank",
		"name_ru": "Карта возвращена в банк",
		"position": null,
		"button_name": null,
		"transitions": [
			{
				"trigger": "new",
				"source": "card_returned_to_bank",
				"dest": "new"
			}
		]
	}
]
'''


@pytest.fixture
def raw_wrong_delivery_graph() -> list[dict]:
    return  json.loads(__json_2)
