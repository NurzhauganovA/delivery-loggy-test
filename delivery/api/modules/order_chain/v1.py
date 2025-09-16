from typing import Optional

import fastapi
from api import auth, schemas, responses
from api.schemas import UserCurrent
from fastapi import UploadFile, Body, File

from .dependecies import (
    order_chain_create_validate_payload,
    order_chain_default_filter_args,
    order_chain_stage_default_filter_args,
    order_chain_stage_validate_payload, order_chain_update_validate_payload, order_chain_support_document_filter_args
)

from .actions import OrderChainActions
from .schemas.request_schemas import (
    OrderChainCreateModel, OrderChainGetModel, OrderChainFilterModel,
    OrderChainUpdateModel, OrderChainStageCreateModel, OrderChainStageGetModel
)

router = fastapi.APIRouter()


@router.post(
    '/order_chain',
    summary='Create order chain',
    response_description='Order chain created',
    response_model=OrderChainGetModel,
    responses=responses.generate_responses(
        [
            responses.APIResponseNotFound,
            responses.APIResponseBadRequest,
        ],
    ),
)
async def order_chain_create(
    order_chain: OrderChainCreateModel = fastapi.Depends(
        order_chain_create_validate_payload
    ),
    _: UserCurrent = fastapi.Security(
        auth.get_current_user,
        # scopes=['sp:c'],
    ),
):
    """Create order chain.

    Returns 404 NOT FOUND due to the following statuses:
    * `not_found`: provided partner not found
    """

    actions = OrderChainActions(user=_)
    order_chain_created = await actions.create_order_chain(
        order_chain=order_chain
    )

    return order_chain_created


@router.get(
    '/order_chain/list',
    summary='Get list of order chain',
    response_model=schemas.Page[OrderChainGetModel],
    response_description='List of partner shipment_points',
)
async def order_chain_get_list(
    filter_kwargs: OrderChainFilterModel = fastapi.Depends(OrderChainFilterModel),
    pagination_params: schemas.Params = fastapi.Depends(schemas.Params),
    _: UserCurrent = fastapi.Security(
        auth.get_current_user,
        # scopes=['p:l']
    ),
    default_filter_args: list = fastapi.Depends(
        order_chain_default_filter_args
    ),
):
    """Get list of order chain"""
    actions = OrderChainActions(user=_)
    return await actions.get_list_order_chain(
        pagination_params=pagination_params,
        default_filter_args=default_filter_args,
        filter_kwargs=filter_kwargs,
    )


@router.get(
    '/order_chain/{order_chain_id}',
    summary='Get order chain by id',
    response_model=OrderChainGetModel,
    response_description='Order chain',
)
async def order_chain_get(
    order_chain_id: int,
    _: UserCurrent = fastapi.Security(
        auth.get_current_user,
        # scopes=['p:l']
    ),
    default_filter_args: list = fastapi.Depends(
        order_chain_default_filter_args
    ),
) -> dict:
    """Get order chain dict"""
    actions = OrderChainActions(user=_)
    return await actions.get_one_order_chain(
        default_filter_args=default_filter_args,
        order_chain_id=order_chain_id
    )


@router.delete(
    '/order_chain/{order_chain_id}',
    summary='Delete order chain by ID',
    response_description='Order chain deleted',
    responses=responses.generate_responses(
        [
            responses.APIResponseNotFound,
            responses.APIResponseBadRequest,
        ],
    ),
)
async def order_chain_delete(
    order_chain_id: int,
    _: schemas.UserCurrent = fastapi.Security(
        auth.get_current_user,
        # scopes=['sp:u'],
    ),
    default_filter_args: list = fastapi.Depends(
        order_chain_default_filter_args
    ),
) -> fastapi.Response:
    """Update partner shipment point with provided ID.

    Returns 404 NOT FOUND due to the following statuses:
    * `not_found`: provided partner not found
    """
    actions = OrderChainActions(user=_)
    await actions.delete_order_chain(
        order_chain_id=order_chain_id,
        default_filter_args=default_filter_args,
    )

    return fastapi.responses.Response(status_code=204)

@router.delete(
    '/order_chain/{order_chain_id}/stage/{stage_id}',
    summary='Delete order chain stage by ID',
    response_description='Order chain stage was deleted',
    responses=responses.generate_responses(
        [
            responses.APIResponseNotFound,
            responses.APIResponseBadRequest,
        ],
    ),
)
async def order_chain_stage_delete(
        order_chain_id: int,
        stage_id: int,
        _: schemas.UserCurrent = fastapi.Security(
            auth.get_current_user,
            # scopes=['sp:u'],
        ),
        default_filter_args: list = fastapi.Depends(
            order_chain_stage_default_filter_args
        ),
) -> fastapi.Response:
    """Update partner shipment point with provided ID.

    Returns 404 NOT FOUND due to the following statuses:
    * `not_found`: provided partner not found
    """
    actions = OrderChainActions(user=_)
    await actions.delete_stage(
        order_chain_id=order_chain_id,
        idx=stage_id,
        default_filter_args=default_filter_args,
    )

    return fastapi.responses.Response(status_code=204)


@router.patch(
    '/order_chain/{order_chain_id}',
    summary='Update order chain data ID',
    response_description='Order chain updated',
    responses=responses.generate_responses(
        [
            responses.APIResponseNotFound,
            responses.APIResponseBadRequest,
        ],
    ),
)
async def order_chain_partial_update(
    order_chain_id: int,
    update: OrderChainUpdateModel = fastapi.Depends(
        order_chain_update_validate_payload
    ),
    _: schemas.UserCurrent = fastapi.Security(
        auth.get_current_user,
        # scopes=['sp:u'],
    ),
    default_filter_args: list = fastapi.Depends(
        order_chain_default_filter_args
    ),
) -> fastapi.Response:
    """Update partner shipment point with provided ID.

    Returns 404 NOT FOUND due to the following statuses:
    * `not_found`: provided partner not found
    """
    actions = OrderChainActions(user=_)
    await actions.update_order_chain(
        order_chain_id=order_chain_id,
        update=update,
        default_filter_args=default_filter_args,
    )

    return fastapi.responses.Response(status_code=201)


@router.post(
    '/order_chain/{order_chain_id}/stage',
    summary='Add stage to order chain',
    response_description='Order stage was added',
    response_model=OrderChainStageGetModel,
    responses=responses.generate_responses(
        [
            responses.APIResponseNotFound,
            responses.APIResponseBadRequest,
        ],
    ),
)
async def order_chain_add_stage(
    order_chain_id: int,
    _: schemas.UserCurrent = fastapi.Security(
        auth.get_current_user,
        # scopes=['sp:u'],
    ),
    stage: OrderChainStageCreateModel = fastapi.Depends(
        order_chain_stage_validate_payload
    ),
    default_filter_args: list = fastapi.Depends(
        order_chain_default_filter_args
    ),
) -> OrderChainStageGetModel:
    """Create order chain.

    Returns 404 NOT FOUND due to the following statuses:
    * `not_found`: provided partner not found
    """
    actions = OrderChainActions(user=_)
    return await actions.order_chain_add_stage(
        order_chain_id=order_chain_id, stage=stage, default_filter_args=default_filter_args
    )


@router.post(
    '/order_chain/stage/support_document',
    summary='Create a order chain support document',
    response_model=OrderChainStageGetModel,
    response_description='Created post control document',
)
async def support_document_add(
    image: UploadFile = File(...),
    order_chain_stage_id: int = Body(None),
    document_number: Optional[str] = Body(None),
    comment: Optional[str] = Body(None),
    current_user: schemas.UserCurrent = fastapi.Security(
        auth.get_current_user,
    ),
):
    """Create support document."""

    actions = OrderChainActions(user=current_user)
    return await actions.create_support_document(
        image=image,
        order_chain_stage_id=order_chain_stage_id,
        document_number=document_number,
        comment=comment
    )

@router.patch(
    '/order_chain/stage/support_document/{support_document_id}',
    summary='Update a order chain support document',
    response_model=OrderChainStageGetModel,
    response_description='Created post control document',
)
async def support_document_update(
    support_document_id: int,
    image: UploadFile = File(...),
    document_number: Optional[str] = Body(None),
    comment: Optional[str] = Body(None),
    current_user: schemas.UserCurrent = fastapi.Security(
        auth.get_current_user,
    ),
    default_filter_args: list = fastapi.Depends(
        order_chain_support_document_filter_args
    ),
):
    """Create support document."""

    actions = OrderChainActions(user=current_user)
    return await actions.update_support_document(
        entity_id=support_document_id,
        image=image,
        document_number=document_number,
        comment=comment,
        default_filter_args=default_filter_args
    )



@router.delete(
    '/order_chain/stage/support_document/{support_document_id}',
    summary='Delete a post control document',
    response_description='Delete a post control document',
)
async def support_document_delete(
    support_document_id: int,
    current_user: schemas.UserCurrent = fastapi.Security(
        auth.get_current_user,
    ),
    default_filter_args: list = fastapi.Depends(
        order_chain_support_document_filter_args
    ),
):
    """Create support document."""

    actions = OrderChainActions(user=current_user)
    await actions.support_document_delete(
        idx=support_document_id,
        default_filter_args=default_filter_args
    )