import typing
import fastapi
from tortoise.timezone import now

from api import schemas, auth, responses
from fastapi_pagination.bases import AbstractPage

from .enums import OrderGroupStatuses
from .schemas import (
    OrderGroupGet, OrderGroupFilter, OrderGroupListOrder,
    OrderGroupCreateSchema, OrderGroupUpdate, OrdersIn
)
from .dependecies import (
    order_group_validate_payload, order_group_default_filter_args,
    order_group_orders_validate_payload, order_group_update_validate_payload,
    order_group_change_status_validate_args,
    order_group_for_availability_for_editing
)
from ...dependencies import order

from .actions import OrderGroupActions
from .schemas import OrderGroupReportFilter

router = fastapi.APIRouter()


@router.post(
    '/order_group',
    summary='Create order group',
    response_description='Order group created for Partner',
)
async def order_group_create(
    order_group: OrderGroupCreateSchema = fastapi.Depends(
        order_group_validate_payload
    ),
    current_user: schemas.UserCurrent = fastapi.Security(
        auth.get_current_user,
        scopes=['og:c'],
    ),
):
    """Create order group with given ID.

    Returns 404 NOT FOUND due to the following statuses:
    * `not_found`: provided partner not found
    """
    actions = OrderGroupActions(current_user=current_user)
    await actions.create(
        order_group=order_group
    )

    return fastapi.responses.Response(status_code=201)


@router.get(
    '/order_group/list',
    summary='Get list of order groups',
    response_model=schemas.Page[OrderGroupGet],
    response_description='List of order groups',
)
async def order_group_get_list(
    filter_kwargs: OrderGroupFilter = fastapi.Depends(OrderGroupFilter),
    pagination_params: schemas.Params = fastapi.Depends(schemas.Params),
    _: schemas.UserCurrent = fastapi.Security(
        auth.get_current_user,
        scopes=['og:l'],
    ),
    default_filter_args: list = fastapi.Depends(
        order_group_default_filter_args
    ),
) -> AbstractPage[OrderGroupGet]:
    """Get list of order groups"""
    actions = OrderGroupActions()
    return await actions.get_list(
        pagination_params=pagination_params,
        default_filter_args=default_filter_args,
        filter_kwargs=filter_kwargs
    )


@router.get(
    '/order_group/report',
)
async def order_group_report(
    filters: OrderGroupReportFilter = fastapi.Depends(),
    default_filters: list = fastapi.Depends(order_group_default_filter_args),
):
    current = now()
    filename = 'Order Group Report '
    headers = {
        'Content-Disposition': f'attachment; filename="{filename} {current.date()}.xlsx"'
    }
    actions = OrderGroupActions()
    report = await actions.order_group_report(
        default_filters=default_filters,
        filters=filters.dict(exclude_unset=True, exclude_none=True),
    )
    return fastapi.responses.StreamingResponse(
        content=report,
        media_type='application/ms-excel',
        headers=headers,
    )


@router.get(
    '/order_group/{id}',
    summary='Get order group',
    response_model=OrderGroupGet,
    response_description='Order group',
)
async def order_group_get(
    id: int,
    _: schemas.UserCurrent = fastapi.Security(
        auth.get_current_user,
        scopes=['og:l'],
    ),
    default_filter_args: list = fastapi.Depends(
        order_group_default_filter_args
    ),
) -> OrderGroupGet:
    """Get order group by ID"""
    actions = OrderGroupActions()
    return await actions.get(
        default_filter_args=default_filter_args,
        order_group_id=id
    )


@router.patch(
    '/order_group/{order_group_id}',
    summary='Update order group with given ID',
    response_description='Order group updated',
    responses=responses.generate_responses(
        [
            responses.APIResponseNotFound,
            responses.APIResponseBadRequest,
        ],
    ),
)
async def order_group_partial_update(
    order_group_id: int,
    update: OrderGroupUpdate = fastapi.Depends(
        order_group_update_validate_payload
    ),
    current_user: schemas.UserCurrent = fastapi.Security(
        auth.get_current_user,
        scopes=['og:u'],
    ),
    default_filter_args: list = fastapi.Depends(
        order_group_default_filter_args
    ),
) -> fastapi.Response:
    """Update order group with provided ID.

    Returns 404 NOT FOUND due to the following statuses:
    * `not_found`: provided partner not found
    """
    actions = OrderGroupActions(current_user=current_user)
    await actions.update(
        order_group_id=order_group_id,
        update=update,
        default_filter_args=default_filter_args,
    )

    return fastapi.responses.Response(status_code=201)


@router.delete(
    '/order_group/{order_group_id}',
    summary='Delete order group with given ID',
    response_description='Order group deleted',
    responses=responses.generate_responses(
        [
            responses.APIResponseNotFound,
            responses.APIResponseBadRequest,
        ],
    ),
)
async def order_group_delete(
    order_group_id: int,
    _: schemas.UserCurrent = fastapi.Security(
        auth.get_current_user,
        scopes=['og:d'],
    ),
    default_filter_args: list = fastapi.Depends(
        order_group_default_filter_args
    ),
) -> fastapi.Response:
    """Delete order group point with provided ID.

    Returns 404 NOT FOUND due to the following statuses:
    * `not_found`: provided partner not found
    """
    actions = OrderGroupActions()
    await actions.order_group_delete(
        order_group_id=order_group_id,
        default_filter_args=default_filter_args,
    )

    return fastapi.responses.Response(status_code=204)


@router.patch(
    '/order_group/{order_group_id}/add_order',
    summary='Add orders to order group',
    response_description='Orders was added',
    responses=responses.generate_responses(
        [
            responses.APIResponseNotFound,
            responses.APIResponseBadRequest,
        ],
    ),
)
async def order_group_add_order(
    order_group_id: int,
    _: schemas.UserCurrent = fastapi.Security(
        auth.get_current_user,
        scopes=['ogo:c'],
    ),
    update: OrdersIn = fastapi.Depends(
        order_group_orders_validate_payload
    ),
    default_filter_args: list = fastapi.Depends(
        order_group_default_filter_args
    ),
    is_available_for_edit: bool = fastapi.Depends(  # noqa
        order_group_for_availability_for_editing,
    )
) -> fastapi.Response:
    """Add orders to order group.

    Returns 404 NOT FOUND due to the following statuses:
    * `not_found`: provided partner not found
    """
    actions = OrderGroupActions()
    await actions.order_add(
        orders=update,
        order_group_id=order_group_id,
        default_filter_args=default_filter_args,
    )

    return fastapi.responses.Response(status_code=204)


@router.get(
    '/order_group/{order_group_id}/orders',
    summary='List orders of group',
    response_model=schemas.Page[OrderGroupListOrder],
)
async def order_group_list_order(
    order_group_id: int,
    order_id: typing.Optional[int] = fastapi.Query(None),
    pagination_params: schemas.Params = fastapi.Depends(schemas.Params),
    _: schemas.UserCurrent = fastapi.Security(
        auth.get_current_user,
        scopes=['og:l'],
    ),
    default_filter_args: list = fastapi.Depends(
        order_group_default_filter_args
    ),
):
    actions = OrderGroupActions()
    kwargs = {}
    if order_id is not None:
        kwargs['id'] = order_id
    return await actions.list_orders(
        pagination_params=pagination_params,
        default_filter_args=default_filter_args,
        order_group_id=order_group_id,
        **kwargs,
    )


@router.patch(
    '/order_group/{order_group_id}/remove_order',
    summary='Delete orders from order group',
    response_description='Orders was deleted',
    responses=responses.generate_responses(
        [
            responses.APIResponseNotFound,
            responses.APIResponseBadRequest,
        ],
    ),
)
async def order_group_remove_order(
    order_group_id: int,
    _: schemas.UserCurrent = fastapi.Security(
        auth.get_current_user,
        scopes=['ogo:d'],
    ),
    update: OrdersIn = fastapi.Depends(
        order_group_orders_validate_payload
    ),
    default_filter_args: list = fastapi.Depends(
        order_group_default_filter_args
    ),
    is_available_for_edit: bool = fastapi.Depends(  # noqa
        order_group_for_availability_for_editing,
    )
) -> fastapi.Response:
    """Remove orders from order group.

    Returns 404 NOT FOUND due to the following statuses:
    * `not_found`: provided partner not found
    """
    actions = OrderGroupActions()
    await actions.order_remove(
        orders=update,
        order_group_id=order_group_id,
        default_filter_args=default_filter_args,
    )

    return fastapi.responses.Response(status_code=204)


@router.patch(
    '/order_group/{order_group_id}/add_status',
    summary='Add status to order group',
    response_description='Status was added',
    responses=responses.generate_responses(
        [
            responses.APIResponseNotFound,
            responses.APIResponseBadRequest,
        ],
    ),
)
async def order_group_add_status(
    order_group_id: int,
    status: OrderGroupStatuses = fastapi.Depends(
        order_group_change_status_validate_args
    ),
    user: schemas.UserCurrent = fastapi.Security(
        auth.get_current_user,
        scopes=['ogs:s'],
    ),
    default_filter_args: list = fastapi.Depends(
        order_group_default_filter_args
    ),
) -> fastapi.Response:
    """Add status to order group.

    Returns 404 NOT FOUND due to the following statuses:
    * `not_found`: provided partner not found
    """
    actions = OrderGroupActions(current_user=user)
    await actions.change_status(
        status=status,
        order_group_id=order_group_id,
        default_filter_args=default_filter_args,
    )

    return fastapi.responses.Response(status_code=204)
