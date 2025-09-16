from typing import Union

from api import auth, schemas
from api.enums import ProfileType
from fastapi import Security
from tortoise.expressions import Q

from api import exceptions

from .schemas.request_schemas import (
    OrderChainCreateModel, OrderChainUpdateModel,
    OrderChainStageCreateModel, SupportDocumentCreateModel
)


async def order_chain_default_filter_args(
    current_user: schemas.UserCurrent = Security(auth.get_current_user)
) -> list:
    profile = current_user.profile
    profile_type = profile['profile_type']
    profile_content = profile['profile_content']
    args = []
    if current_user.is_superuser:
        return args
    match profile_type:
        case ProfileType.SERVICE_MANAGER:
            args.append(Q(partner_id__in=current_user.partners))
        case _:
            args.append(Q(id=-999_999_999))

    return args


async def order_chain_support_document_filter_args(
    current_user: schemas.UserCurrent = Security(auth.get_current_user)
) -> list:
    profile = current_user.profile
    profile_type = profile['profile_type']
    profile_content = profile['profile_content']
    args = []
    if current_user.is_superuser:
        return args
    match profile_type:
        case ProfileType.SERVICE_MANAGER:
            args.append(Q(order_chain_stage__order_chain__partner_id__in=current_user.partners))
        case _:
            args.append(Q(id=-999_999_999))

    return args


async def order_chain_stage_default_filter_args(
    current_user: schemas.UserCurrent = Security(auth.get_current_user)
) -> list:
    profile = current_user.profile
    profile_type = profile['profile_type']
    profile_content = profile['profile_content']
    args = []
    if current_user.is_superuser:
        return args
    match profile_type:
        case ProfileType.SERVICE_MANAGER:
            args.append(Q(order_chain__partner__id__in=current_user.partners))
        case _:
            args.append(Q(id=-999_999_999))

    return args


async def order_chain_default_filter_args_external(
    current_partner: schemas.PartnerGet = Security(
        auth.get_current_partner,
    ),
):
    args = [Q(partner_id__in=(current_partner.id, current_partner.courier_partner_id))]
    return args


async def order_chain_create_validate_payload(
    order_chain: OrderChainCreateModel,
    current_user: schemas.UserCurrent = Security(auth.get_current_user),
):
    profile = current_user.profile
    profile_type = profile['profile_type']
    profile_content = profile['profile_content']
    errors = []
    if current_user.is_superuser:
        return order_chain
    if errors:
        raise exceptions.PydanticException(errors=errors)
    return order_chain


async def order_chain_update_validate_payload(
    order_chain: OrderChainUpdateModel,
    current_user: schemas.UserCurrent = Security(auth.get_current_user),
):
    profile = current_user.profile
    profile_type = profile['profile_type']
    profile_content = profile['profile_content']
    errors = []
    if current_user.is_superuser:
        return order_chain
    if errors:
        raise exceptions.PydanticException(errors=errors)
    return order_chain


async def order_chain_stage_validate_payload(
    stage: OrderChainStageCreateModel,
    current_user: schemas.UserCurrent = Security(auth.get_current_user),
):
    profile = current_user.profile
    profile_type = profile['profile_type']
    profile_content = profile['profile_content']
    errors = []
    if current_user.is_superuser:
        return stage
    if errors:
        raise exceptions.PydanticException(errors=errors)
    return stage







