import typing

import fastapi

from ... import auth
from ... import controllers
from ... import responses
from ... import schemas


router = fastapi.APIRouter()


# @router.get(
#     '/monitoring/{city_id}',
#     summary='Get list monitored couriers',
#     response_model=typing.List[schemas.MonitoringCourierGet],
#     response_description='List of monitored couriers',
#     responses=responses.generate_responses(
#         [
#             responses.APIResponseNotFound,
#             responses.APIResponseTemporarilyUnavailable,
#         ],
#     ),
# )
# async def monitoring_get_couriers(city_id: int) -> list:
#     """Get list of monitored couriers.
#
#     Returns 404 NOT FOUND due to the following statuses:
#     * `not_found`: subscriptions to monitoring not found
#     """
#     return await controllers.monitoring_get_couriers(city_id)


# TODO: Add 201
@router.post(
    '/monitoring',
    summary='Add monitored courier',
    responses=responses.generate_responses(
        [
            responses.APIResponseTemporarilyUnavailable,
        ],
    ),
)
async def monitoring_add_courier(
    courier: schemas.MonitoringCourierAdd,
    current_user: schemas.UserCurrent = fastapi.Depends(auth.get_current_user),
) -> None:
    """Add a monitored courier."""
    await controllers.monitoring_add_courier(courier)


# @router.get(
#     '/monitoring/public/{order_id}',
#     summary="Get order for public client's monitoring",
#     response_model=schemas.OrderGet,
#     response_description='Order',
#     responses=responses.generate_responses([responses.APIResponseNotFound]),
# )
# async def monitoring_for_order(
#         order_id: int
# ) -> dict:
#     """Get order with provided ID.
#
#     Returns 404 NOT FOUND due to the following statuses:
#     * `not_found`: order not found
#     """
#     return await controllers.order_get(
#         order_id=order_id, default_filter_args=[]
#     )
