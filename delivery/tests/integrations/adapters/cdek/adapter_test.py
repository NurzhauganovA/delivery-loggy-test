import pytest
from pydantic.validators import Decimal

from api.adapters.cdek import CDEKAdapter


@pytest.mark.skip(reason="Интеграционный тест")
async def test_create_order(adapter: CDEKAdapter):
    """Создание заявки в CDEK"""
    track_number = await adapter.order_create(
        shipment_point="MSK339",
        recipient_name="ФИО Клиента",
        recipient_phone="87110457814",
        latitude=Decimal(55.755864),
        longitude=Decimal(37.617698),
        address="улица Победы",
        package_number="1"
    )

    assert track_number is not None
