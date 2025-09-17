import loguru

from api import auth, schemas
from api.exceptions import PydanticException

from .infrastructure.db_table import OrderGroupStatus
from .schemas import OrderGroupCreateSchema, OrderGroupUpdate, OrdersIn
from api.enums import ProfileType
from api.exceptions import HTTPBadRequestException
from fastapi import Security
from tortoise.expressions import Q

from .enums import *


async def order_group_default_filter_args(
    current_user: schemas.UserCurrent = Security(auth.get_current_user)
) -> list:
    profile = current_user.profile
    profile_type = profile['profile_type']
    profile_content = profile['profile_content']
    args = []
    loguru.logger.debug(profile)
    if current_user.is_superuser:
        return args

    match profile_type:
        case ProfileType.SERVICE_MANAGER:
            args.append(Q(partner_id__in=current_user.partners))
        case ProfileType.COURIER:
            available_statuses = (
                OrderGroupStatuses.READY_FOR_PICKUP.value,
                OrderGroupStatuses.REVISE.value,
                OrderGroupStatuses.EXPORTED.value,
                OrderGroupStatuses.UNDER_REVIEW.value,
            )
            args.append(
                Q(
                    current_status__in=available_statuses,
                    courier_id=profile['id'],
                )
            )
        case ProfileType.MANAGER:
            args.append(Q(partner_id__in=current_user.partners))
        case ProfileType.SORTER:
            args.append(Q(sorter_id=profile.get('id')))
        case ProfileType.SUPERVISOR:
            args.append(
                Q(
                    partner_id__in=current_user.partners,
                    orders__city__country_id=profile_content['country_id'],
                )
            )
        case ProfileType.CALL_CENTER_MANAGER:
            args.append(
                Q(
                    partner_id__in=current_user.partners,
                    orders__city__country_id=profile_content['country_id'],
                )
            )
        case ProfileType.GENERAL_CALL_CENTER_MANAGER:
            args.append(
                Q(
                    partner_id__in=current_user.partners,
                )
            )
        case ProfileType.LOGIST:
            args.append(
                Q(
                    partner_id__in=current_user.partners,
                    orders__city__country_id=profile_content['country_id'],
                )
            )
        case ProfileType.SUPPORT:
            args.append(
                Q(
                    partner_id__in=current_user.partners,
                )
            )
        case _:
            args.append(Q(id=-9999999999))  # filter for empty list
    return args


async def order_group_change_status_validate_args(
    status: OrderGroupStatuses,
    current_user: schemas.UserCurrent = Security(auth.get_current_user)
):
    profile = current_user.profile
    profile_type = profile['profile_type']
    profile_content = profile['profile_content']
    if current_user.is_superuser:
        return status

    errors = []

    match profile_type:
        case ProfileType.SERVICE_MANAGER:
            if status not in (
                OrderGroupStatuses.COURIER_SERVICE_ACCEPTED,
                OrderGroupStatuses.COURIER_APPOINTED
            ):
                errors.append(('status', 'Service Manager cannot use this status'))
        case ProfileType.COURIER:
            if status not in (
                OrderGroupStatuses.UNDER_REVIEW,
                OrderGroupStatuses.REVISE,
                OrderGroupStatuses.EXPORTED
            ):
                errors.append(('status', 'Courier cannot use this status'))
        case ProfileType.SORTER:
            if status not in (
                OrderGroupStatuses.NEW_GROUP,
                OrderGroupStatuses.READY_FOR_PICKUP
            ):
                errors.append(('status', 'Sorter cannot use this status'))

    if errors:
        raise PydanticException(errors=errors)
    loguru.logger.debug(status)
    return status


async def order_group_validate_payload(
    order_group: OrderGroupCreateSchema | OrderGroupUpdate,
    current_user: schemas.UserCurrent = Security(auth.get_current_user),
):
    profile = current_user.profile
    if current_user.is_superuser:
        return order_group
    return order_group


async def order_group_update_validate_payload(
    order_group: OrderGroupUpdate,
    current_user: schemas.UserCurrent = Security(auth.get_current_user),
):
    return order_group


async def order_group_orders_validate_payload(
    order_group: OrdersIn,
    current_user: schemas.UserCurrent = Security(auth.get_current_user),
):
    profile = current_user.profile
    if current_user.is_superuser:
        return order_group
    return order_group


async def order_group_for_availability_for_editing(
    order_group_id: int,
) -> bool:
    current_status = await OrderGroupStatus.filter(order_group_id=order_group_id).first()

    closed_for_edit_statuses = [
        OrderGroupStatuses.REVISE.value,
        OrderGroupStatuses.EXPORTED.value,
        OrderGroupStatuses.COURIER_SERVICE_ACCEPTED.value,
    ]

    if current_status and current_status.name in closed_for_edit_statuses:
        raise HTTPBadRequestException('Can not edit order group in this status')
