import typing

import fastapi
from fastapi.encoders import jsonable_encoder
from starlette.responses import JSONResponse

from ... import auth
from ... import controllers
from ... import dependencies
from ... import responses
from ... import schemas


router = fastapi.APIRouter()


@router.get(
    '/partner/{partner_id}',
    summary='Get partner',
    response_model=schemas.PartnerGet,
    response_description='Partner',
)
async def partner_get(
    partner_id: int,
    current_user: schemas.UserCurrent = fastapi.Security(
        auth.get_current_user,
        scopes=['p:g']
    ),
):
    """Get partner with provided ID."""
    result = await controllers.partner_get(partner_id, current_user=current_user)
    return JSONResponse(jsonable_encoder(result))


# TODO: should be covered with perms
@router.get(
    '/partner',
    summary='Get list of partners',
    response_model=typing.List[schemas.PartnerGet],
    response_description='List of partners',
)
async def partner_get_list(
    current_user: schemas.UserCurrent = fastapi.Security(
        auth.get_current_user,
        scopes=['p:l']
    ),
):
    """Get list of partners."""
    result = await controllers.partner_get_list(current_user=current_user)
    return JSONResponse(jsonable_encoder(result))


@router.post(
    '/partner',
    summary='Create partner',
    response_model=schemas.PartnerGet,
    response_description='Created partner',
    responses=responses.generate_responses([responses.APIResponseBadRequest]),
)
async def partner_create(
    partner: schemas.PartnerCreate,
    current_user: schemas.UserCurrent = fastapi.Security(
        auth.get_current_user,
        scopes=['p:c'],
    ),
):
    """Create partner.

    Returns 400 BAD REQUEST due to the following statuses:
    * `bad_request`: provided partner already exists
    """
    result = await controllers.partner_create(
        partner=partner,
        current_user=current_user,
    )
    return JSONResponse(jsonable_encoder(result))


@router.patch(
    '/partner/{partner_id}',
    summary='Update partner',
    response_model=schemas.PartnerGet,
    response_description='Updated partner',
    responses=responses.generate_responses([responses.APIResponseNotFound]),
)
async def partner_update(
    partner_id: int,
    update: schemas.PartnerUpdate,
    current_user: schemas.UserCurrent = fastapi.Security(
        auth.get_current_user,
        scopes=['p:u'],
    ),
    default_filters: list = fastapi.Depends(dependencies.partner_default_filter_args)
) -> dict:
    """Update partner with provided ID.

    Returns 404 NOT FOUND due to the following statuses:
    * `not_found`: provided partner not found
    """
    return await controllers.partner_update(partner_id, default_filters, update)

# TODO: Пока что закомментил, так как для безопасности требуется закрыть
# @router.post(
#     '/partner/delivery-service-register',
#     summary='Registration of delivery service',
#     response_model=schemas.PartnerGet,
#     response_description='Created partner',
#     responses=responses.generate_responses([responses.APIResponseBadRequest]),
# )
# async def delivery_service_register(
#     partner: schemas.DeliveryServiceCreate,
# ):
#     """Register partner.
#
#     Returns 400 BAD REQUEST due to the following statuses:
#     * `bad_request`: provided partner already exists
#     """
#     return await controllers.delivery_service_register(partner)

@router.delete(
    '/partner/bulk',
    summary='Delete partners bulk',
    response_model=schemas.PartnerDeleteBulk,
    response_description='Partners deleted successfully',
    status_code=202,
)
async def partner_delete_bulk(
    partner_id_list: schemas.PartnerDeleteBulk,
    current_user: schemas.UserCurrent = fastapi.Security(
        auth.get_current_user,
        scopes=['sp:d'],
    ),
) -> fastapi.responses.Response:
    partners = await controllers.partner_delete_many(current_user=current_user,
                                                     **partner_id_list.dict())
    return fastapi.responses.JSONResponse({'partner_id_list': partners}, 202)


@router.delete(
    '/partner/{partner_id}',
    summary='Delete partner',
    response_description='Partner deleted successfully',
    responses=responses.generate_responses(
        [
            responses.APIResponseNotFound,
            responses.APIResponseNoContent,
        ],
    ),
    status_code=204,
)
async def partner_delete(
    partner_id: int,
    current_user: schemas.UserCurrent = fastapi.Security(
        auth.get_current_user,
        scopes=['p:d'],
    ),
) -> fastapi.Response:
    """Delete partner with provided ID.

    Returns 404 NOT FOUND due to the following statuses:
    * `not_found`: provided partner not found
    """
    await controllers.partner_delete(partner_id, current_user=current_user)
    return fastapi.responses.Response(status_code=204)
#
#
# @router.get(
#     '/partner/{partner_id}/cities',
#     summary='Get cities by partner',
#     status_code=200,
#     response_model=list[schemas.CityGet]
# )
# async def get_partner_cities(
#     partner_id: int, region_id: int | None = None, country_id: int | None = None
#     ):
#     cities = await controllers.get_partner_cities(partner_id, country_id)
#     return cities
#
#
# @router.get(
#     '/partner/{partner_id}/regions',
#     summary='Get regions by partner',
#     status_code=200,
#     response_model=list[schemas.RegionGet]
# )
# async def get_partner_regions(
#     partner_id: int, country_id: int | None = None
#     ):
#     cities = await controllers.get_partner_regions(partner_id, country_id)
#     return cities
#
#
# @router.get(
#     '/partner/{partner_id}/countries',
#     summary='Get countries by partner',
#     status_code=200,
#     response_model=list[schemas.CountryGet]
# )
# async def get_partner_countries(partner_id: int):
#     countries = await controllers.get_partner_countries(partner_id)
#     return countries
