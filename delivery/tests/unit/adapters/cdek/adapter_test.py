from decimal import Decimal

import pytest

from api.adapters.cdek import CDEKAdapter
from api.adapters.cdek.exceptions import (
    CDEKGetLocationError,
    CDEKValidationError,
    CDEKCreateOrderError,
)


async def test_create_order(adapter: CDEKAdapter):
    """Создание заявки"""
    track_number = await adapter.order_create(
        shipment_point="MSK339",
        recipient_name="ФИО Клиента",
        recipient_phone="87110457814",
        latitude=Decimal(55.755864),
        longitude=Decimal(37.617698),
        address="улица Победы",
        package_number="1"
    )
    assert track_number == "549b1ab8-518c-42d0-a14f-57569e3e5d65"


async def test_create_order_validation_error(adapter: CDEKAdapter):
    """Ошибка валидации"""
    with pytest.raises(CDEKValidationError):
        await adapter.order_create(
            shipment_point="",
            recipient_name="",
            recipient_phone="",
            latitude=Decimal(0),
            longitude=Decimal(0),
            address="",
            package_number=""
        )


async def test_create_order_failure(adapter: CDEKAdapter):
    """Ошибка получения локации при создании заявки"""
    with pytest.raises(CDEKCreateOrderError):
        await adapter.order_create(
            shipment_point="111",
            recipient_name="ФИО Клиента",
            recipient_phone="87110457814",
            latitude=Decimal(55.755864),
            longitude=Decimal(37.617698),
            address="улица Победы",
            package_number="1"
        )


async def test_create_order_failure_get_location(adapter: CDEKAdapter):
    """Ошибка создания заявки"""
    with pytest.raises(CDEKGetLocationError):
        await adapter.order_create(
            shipment_point="MSK339",
            recipient_name="ФИО Клиента",
            recipient_phone="87110457814",
            latitude=Decimal(111),
            longitude=Decimal(37.617698),
            address="улица Победы",
            package_number="1"
        )
