import asyncio
import typing

import aiohttp

from .. import enums
from .. import exceptions
from .. import models
from .. import schemas
from .. import services


async def partner_get(
    partner_id: int,
    current_user,
) -> dict:
    try:
        return await models.partner_get(partner_id)
    except models.partner.PartnerNotFound as e:
        raise exceptions.HTTPNotFoundException(str(e)) from e
    except models.partner.PartnerActionException as e:
        raise exceptions.HTTPBadRequestException(str(e)) from e


async def partner_get_list(
    current_user: schemas.UserCurrent,
    **kwargs,
) -> list:
    profile = current_user.profile

    kwargs['courier_partner_id__isnull'] = False
    if profile['profile_type'] == enums.ProfileType.MANAGER:
        kwargs['id'] = current_user.partners[0]
    else:
        kwargs['id__in'] = current_user.partners
    if profile['profile_type'] == enums.ProfileType.BRANCH_MANAGER:
        cities = [city.id for city in profile['profile_content']['cities']]
        kwargs['cities__in'] = cities
    return await models.partner_get_list(**kwargs)


async def partner_get_many(partner_id_list: typing.List[int]) -> list:
    return await models.partner_get_many(partner_id_list)


async def partner_create(
    partner: schemas.PartnerCreate,
    current_user: schemas.UserCurrent,
):
    try:
        return await models.partner_create(
            partner=partner,
            current_user=current_user,
            courier_partner_id=current_user.partners[0],
        )
    except models.PartnerActionException as e:
        raise exceptions.HTTPBadRequestException(str(e)) from e
    except (
        asyncio.TimeoutError,
        aiohttp.ClientConnectorError,
        services.dataloader.dataloader.DataloaderRemoteServiceRequestError,
    ) as e:
        raise exceptions.HTTPTemporarilyUnavailableException(str(e)) from e
    except services.dataloader.DataloaderRemoteServiceResponseError as e:
        raise exceptions.HTTPBadRequestException(
            detail=f'dataloader: {e!s}',
        )


async def partner_update(
    partner_id: int,
    default_filters: list,
    update: schemas.PartnerUpdate,
) -> dict:
    try:
        return await models.partner_update(
            partner_id=partner_id,
            default_filters=default_filters,
            update=update,
        )
    except models.PartnerNotFound as e:
        raise exceptions.HTTPNotFoundException(str(e)) from e
    except models.PartnerActionException as e:
        raise exceptions.HTTPBadRequestException(str(e)) from e


async def delivery_service_register(partner: schemas.DeliveryServiceCreate):
    try:
        return await models.delivery_service_create(partner=partner)
    except (
        models.PartnerActionException,
        models.UserAlreadyExists,
        services.dataloader.dataloader.DataloaderRemoteServiceResponseError
    ) as e:
        raise exceptions.HTTPBadRequestException(str(e)) from e
    except (
        asyncio.TimeoutError,
        aiohttp.ClientConnectorError,
        services.dataloader.dataloader.DataloaderRemoteServiceRequestError,
    ) as e:
        raise exceptions.HTTPTemporarilyUnavailableException(str(e)) from e


async def partner_delete(
    partner_id: int, current_user: schemas.UserCurrent,
) -> None:
    try:
        if partner_id not in current_user.partners:
            raise exceptions.HTTPNotFoundException(
                f'Partner with given ID: {partner_id} was not found',
            )
        await models.partner_delete(partner_id, current_user=current_user)
    except models.PartnerNotFound as e:
        raise exceptions.HTTPNotFoundException(str(e)) from e
    except models.PartnerActionException as e:
        raise exceptions.HTTPBadRequestException(str(e)) from e


async def partner_delete_many(
    partner_id_list: typing.List[int],
    current_user: schemas.UserCurrent,
) -> list:
    try:
        partner_id_list = list(
            set(partner_id_list) & set(current_user.partners))
        deleted_partners = await models.partner_get_many(partner_id_list)
        await models.partner_delete_bulk(
            partner_id_list, current_user=current_user,
        )
        return deleted_partners
    except models.PartnersCanNotBeDeleted as e:
        raise exceptions.HTTPBadRequestException(str(e)) from e


async def get_partner_cities(
    partner_id: int, country_id: int | None = None
):
    try:
        cities = await models.get_partner_cities(partner_id, country_id)
        return cities
    except models.PartnerNotFound as e:
        raise exceptions.HTTPNotFoundException(str(e)) from e


async def get_partner_countries(partner_id: int):
    try:
        countries = await models.get_partner_countries(partner_id)
        return countries
    except models.PartnerNotFound as e:
        raise exceptions.HTTPNotFoundException(str(e)) from e