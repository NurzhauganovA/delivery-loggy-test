import pytest

from api.clients.cdek import CDEKClient
from api.clients.cdek.schemas.create_order.request import CreateOrderRequest


@pytest.mark.skip(reason="Интеграционный тест")
async def test_get_location(client: CDEKClient):
    """Получение локации по координатам"""
    response = await client.get_location(
        latitude=55.755864,
        longitude=37.617698,
    )
    assert response.status_code == 200


@pytest.mark.skip(reason="Интеграционный тест")
async def test_create_order(client: CDEKClient):
    """Создание заявки в CDEK"""
    request = CreateOrderRequest.create(
        shipment_point="MSK339",
        recipient_name="ФИО Клиента",
        recipient_phone="87110457814",
        location_code=41111114,
        city="Москва",
        fias_guid="0c5b2444-70a0-4932-980c-b4dc0d3f02b5",
        latitude=55.755864,
        longitude=37.617698,
        address="улица Победы",
        package_number="1"
    )
    response = await client.create_order(
        request=request,
    )
    assert response.status_code == 202
