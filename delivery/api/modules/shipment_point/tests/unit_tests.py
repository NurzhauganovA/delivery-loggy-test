import pytest
from api.schemas import ShipmentPointFilter

from ..schemas import PartnerShipmentPointCreate, PartnerShipmentPointUpdate
from ..actions import ShipmentPointActions
from api.modules.shipment_point.errors import (
    PartnerShipmentPointNotFoundError, PartnerShipmentPointIntegrityError
)
from ..infrastructure.db_table import PartnerShipmentPoint


@pytest.mark.asyncio
async def test_get_shipment_point_by_id_action(
    initialize_tests,
    shipment_point
):
    action = ShipmentPointActions()
    shipment_point = await action.shipment_point_get([], shipment_point_id=1)
    assert shipment_point.id == 1
    with pytest.raises(PartnerShipmentPointNotFoundError):
        assert await action.shipment_point_get([], shipment_point_id=3)


@pytest.mark.asyncio
async def test_shipment_point_get_list_action(
    initialize_tests,
    shipment_point
):
    action = ShipmentPointActions()
    shipment_points = await action.shipment_point_get_list(
        pagination_params=None,
        default_filter_args=[],
        filter_kwargs=ShipmentPointFilter(city_id=1)
    )
    assert len(shipment_points) == 1


@pytest.mark.asyncio
async def test_shipment_point_update_action(
    initialize_tests,
    shipment_point: PartnerShipmentPoint,
):
    action = ShipmentPointActions()
    schema = PartnerShipmentPointUpdate(
        city_id=1,
        address="New Address121",
        partner_id=2,
        latitude=54.123411,
        longitude=52.12321,
        name="asfasdfff"
    )

    edited_shipment_point = await action.shipment_point_update(
        update=schema, default_filter_args=[], shipment_point_id=shipment_point.id
    )
    assert edited_shipment_point is None
    edited_shipment_point = await action.shipment_point_get([],
                                                            shipment_point_id=shipment_point.id)
    assert edited_shipment_point.id == shipment_point.id
    assert edited_shipment_point.address != shipment_point.address
    assert edited_shipment_point.partner.id == shipment_point.partner_id
    assert edited_shipment_point.city.id == shipment_point.city_id
    assert edited_shipment_point.latitude != shipment_point.latitude
    assert edited_shipment_point.longitude != shipment_point.longitude
    assert edited_shipment_point.name != shipment_point.name


@pytest.mark.asyncio
async def test_shipment_point_create_action(
    initialize_tests,
    shipment_point
):
    action = ShipmentPointActions()
    schema = PartnerShipmentPointCreate(
        city_id=1,
        address="New Address",
        partner_id=2,
        latitude=54.12341,
        longitude=52.1232,
        name="asfasdf"
    )
    created_shipment_point = await action.shipment_point_create(schema)
    assert created_shipment_point is None
    created_shipment_point = await action.shipment_point_get([], shipment_point_id=2)
    assert created_shipment_point.id == 2
    assert created_shipment_point.address == schema.address
    assert created_shipment_point.partner.id == schema.partner_id
    assert created_shipment_point.city.id == schema.city_id
    assert created_shipment_point.latitude == schema.latitude
    assert created_shipment_point.longitude == schema.longitude
    assert created_shipment_point.name == schema.name

    with pytest.raises(PartnerShipmentPointIntegrityError):
        assert await action.shipment_point_create(schema)


@pytest.mark.asyncio
async def test_shipment_point_bulk_create_action(
    initialize_tests,
    shipment_point
):
    action = ShipmentPointActions()
    schema1 = PartnerShipmentPointCreate(
        city_id=1,
        address="New Address",
        partner_id=2,
        latitude=54.12341,
        longitude=52.1232,
        name="Name1"
    )
    schema2 = PartnerShipmentPointCreate(
        city_id=1,
        address="New Address",
        partner_id=2,
        latitude=54.12341,
        longitude=52.1232,
        name="Name2"
    )
    old_shipment_points_list = await action.shipment_point_get_list(
        pagination_params=None,
        default_filter_args=[],
        filter_kwargs=ShipmentPointFilter(city_id=1)
    )
    shipment_point_not_in_transaction = await action.shipment_point_create_in_bulk(
        # action,
        shipment_points=[schema1, schema2]
    )
    assert shipment_point_not_in_transaction is None
    new_shipment_points_list = await action.shipment_point_get_list(
        pagination_params=None,
        default_filter_args=[],
        filter_kwargs=ShipmentPointFilter(city_id=1)
    )
    assert len(new_shipment_points_list) - 2 == len(old_shipment_points_list)


@pytest.mark.asyncio
async def test_shipment_point_delete_action(
    initialize_tests,
    shipment_point
):
    action = ShipmentPointActions()
    shipment_point = await action.shipment_point_delete([], shipment_point_id=1)
    assert shipment_point is None
    with pytest.raises(PartnerShipmentPointNotFoundError):
        assert await action.shipment_point_delete([], shipment_point_id=1)
