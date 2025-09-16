# from decimal import Decimal
#
# import pytest
#
# from api.modules.delivery_point.errors import (
#     DeliveryPointNotFoundError, DeliveryPointIntegrityError
# )
# from api.schemas import ShipmentPointFilter
# from ..actions import DeliveryPointActions
# from ..infrastructure.db_table import DeliveryPoint
# from ..schemas import DeliveryPointCreate, DeliveryPointUpdate
#
#
# @pytest.mark.asyncio
# async def test_get_delivery_point_by_id_action(
#     initialize_tests,
#     delivery_point
# ):
#     action = DeliveryPointActions()
#     delivery_point = await action.delivery_point_get([], delivery_point_id=1)
#     assert delivery_point.id == 1
#     with pytest.raises(DeliveryPointNotFoundError):
#         assert await action.delivery_point_get([], delivery_point_id=3)
#
#
# @pytest.mark.asyncio
# async def test_delivery_point_get_list_action(
#     initialize_tests,
#     delivery_point
# ):
#     action = DeliveryPointActions()
#     delivery_points = await action.delivery_point_get_list(
#         pagination_params=None,
#         default_filter_args=[],
#         filter_kwargs=ShipmentPointFilter(city_id=1)
#     )
#     assert len(delivery_points) == 1
#
#
# @pytest.mark.asyncio
# async def test_delivery_point_update_action(
#     initialize_tests,
#     delivery_point: DeliveryPoint,
# ):
#     action = DeliveryPointActions()
#     schema = DeliveryPointUpdate(
#         address="New Address121",
#         latitude=Decimal(54.123411),
#         longitude=Decimal(52.12321),
#     )
#
#     edited_delivery_point = await action.delivery_point_update(
#         update=schema, default_filter_args=[], delivery_point_id=delivery_point.id
#     )
#     assert edited_delivery_point is None
#     edited_delivery_point = await action.delivery_point_get([],
#                                                             delivery_point_id=delivery_point.id)
#     assert edited_delivery_point.id == delivery_point.id
#     assert edited_delivery_point.address != delivery_point.address
#     assert edited_delivery_point.latitude != delivery_point.latitude
#     assert edited_delivery_point.longitude != delivery_point.longitude
#
#
# @pytest.mark.asyncio
# async def test_delivery_point_create_action(
#     initialize_tests,
#     delivery_point
# ):
#     action = DeliveryPointActions()
#     schema = DeliveryPointCreate(
#         address="New Address",
#         latitude=Decimal(54.12341),
#         longitude=Decimal(52.1232),
#         order_id=1,
#     )
#     created_delivery_point = await action.delivery_point_create(schema)
#     assert created_delivery_point is None
#     created_delivery_point = await action.delivery_point_get([], delivery_point_id=2)
#     assert created_delivery_point.id == 2
#     assert created_delivery_point.address == schema.address
#     assert created_delivery_point.latitude == schema.latitude
#     assert created_delivery_point.longitude == schema.longitude
#
#     with pytest.raises(DeliveryPointIntegrityError):
#         assert await action.delivery_point_create(schema)
#
#
# @pytest.mark.asyncio
# async def test_delivery_point_bulk_create_action(
#     initialize_tests,
#     delivery_point
# ):
#     action = DeliveryPointActions()
#     schema1 = DeliveryPointCreate(
#         address="New Address",
#         latitude=Decimal(54.12341),
#         longitude=Decimal(52.1232),
#         order_id=1,
#     )
#     schema2 = DeliveryPointCreate(
#         address="New Address",
#         latitude=Decimal(54.12341),
#         longitude=Decimal(52.1232),
#         order_id=2,
#     )
#     old_delivery_points_list = await action.delivery_point_get_list(
#         pagination_params=None,
#         default_filter_args=[],
#         filter_kwargs=ShipmentPointFilter(city_id=1)
#     )
#     delivery_point_not_in_transaction = await action.delivery_point_create_in_bulk(
#         # action,
#         delivery_points=[schema1, schema2]
#     )
#     assert delivery_point_not_in_transaction is None
#     new_delivery_points_list = await action.delivery_point_get_list(
#         pagination_params=None,
#         default_filter_args=[],
#         filter_kwargs=ShipmentPointFilter(city_id=1)
#     )
#     assert len(new_delivery_points_list) - 2 == len(old_delivery_points_list)
#
#
# @pytest.mark.asyncio
# async def test_delivery_point_delete_action(
#     initialize_tests,
#     delivery_point
# ):
#     action = DeliveryPointActions()
#     delivery_point = await action.delivery_point_delete([], delivery_point_id=1)
#     assert delivery_point is None
#     with pytest.raises(DeliveryPointNotFoundError):
#         assert await action.delivery_point_delete([], delivery_point_id=1)
