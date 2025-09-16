import typing

from api import auth, schemas
from .schemas import PartnerShipmentPointCreate, PartnerShipmentPointUpdate
from api.enums import ProfileType
from fastapi import Security
from tortoise.expressions import Q

from api import exceptions


async def shipment_point_default_filter_args(
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
        case ProfileType.BRANCH_MANAGER:
            cities = [city.id for city in current_user.profile['profile_content']['cities']]
            args.append(Q(partner_id=profile_content.get('partner_id')))
            args.append(Q(city_id__in=cities))
        case ProfileType.MANAGER:
            args.append(Q(partner_id=profile_content.get('partner_id')))
        case ProfileType.SUPERVISOR:
            args.append(
                Q(
                    partner_id__in=current_user.partners,
                    city__country_id=profile_content['country_id'],
                )
            )
        case ProfileType.LOGIST:
            args.append(
                Q(
                    partner_id__in=current_user.partners,
                    city__country_id=profile_content['country_id'],
                )
            )
        case ProfileType.CALL_CENTER_MANAGER:
            args.append(
                Q(
                    partner_id__in=current_user.partners,
                    city__country_id=profile_content['country_id'],
                )
            )
        case ProfileType.GENERAL_CALL_CENTER_MANAGER:
            args.append(
                Q(
                    partner_id__in=current_user.partners,
                )
            )
        case ProfileType.SUPPORT:
            args.append(
                Q(
                    partner_id__in=current_user.partners,
                )
            )
        case _:
            args.append(Q(id=-999_999_999))

    return args


async def shipment_point_default_filter_args_external(
    current_partner: schemas.PartnerGet = Security(
        auth.get_current_partner,
    ),
):
    args = [Q(partner_id__in=(current_partner.id, current_partner.courier_partner_id))]
    return args


async def shipment_point_validate_payload(
    shipment_point: PartnerShipmentPointCreate | PartnerShipmentPointUpdate,
    current_user: schemas.UserCurrent = Security(auth.get_current_user),
):
    profile = current_user.profile
    profile_type = profile['profile_type']
    profile_content = profile['profile_content']
    errors = []
    if current_user.is_superuser:
        return shipment_point
    match profile_type:
        case ProfileType.SERVICE_MANAGER:
            if shipment_point.partner_id and shipment_point.partner_id not in current_user.partners:
                errors.append(('partner_id', 'Partner does not exist'))
        case ProfileType.BRANCH_MANAGER:
            if shipment_point.partner_id and shipment_point.partner_id != profile_content[
                'partner_id']:
                errors.append(('partner_id', 'Partner does not exist'))
            if shipment_point.city_id and shipment_point.city_id != profile_content['city_id']:
                errors.append(('city_id', 'City does not exist'))
    if errors:
        raise exceptions.PydanticException(errors=errors)
    return shipment_point


async def shipment_point_validate_bulk_payload(
    shipment_points: typing.List[schemas.PartnerShipmentPointCreate],
    current_user: schemas.UserCurrent = Security(auth.get_current_user),
):
    for shipment_point in shipment_points:
        await shipment_point_validate_payload(
            shipment_point=shipment_point, current_user=current_user)
    return shipment_points
