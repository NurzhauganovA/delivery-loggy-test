import fastapi
from fastapi.encoders import jsonable_encoder
from starlette.responses import JSONResponse

from api import schemas, auth

from .schemas import (
    PartnerSettingGet, PartnerSettingUpdate
)
from .dependecies import (
    partner_setting_default_filter_args,
    partner_setting_validate_payload,
)

from .actions import PartnerSettingActions

router = fastapi.APIRouter()

@router.get(
    '/partner/settings/get',
    summary='Get settings',
    response_model=PartnerSettingGet,
    response_description='Get partner settings',
)
async def partner_settings_get(
    user: schemas.UserCurrent = fastapi.Security(
        auth.get_current_user,
    ),
    default_filter_args: list = fastapi.Depends(
        partner_setting_default_filter_args
    ),
) -> PartnerSettingGet:
    """Get partner settings"""
    actions = PartnerSettingActions()
    return await actions.partner_setting_get(
        partner_id=user.partners[0],
        default_filter_args=default_filter_args,
    )


@router.patch(
    '/partner/settings/patch',
    summary='Update partner settings',
    response_description='Shipment point updated',
)
async def partner_settings_partial_update(
    update: PartnerSettingUpdate = fastapi.Depends(
        partner_setting_validate_payload
    ),
    user: schemas.UserCurrent = fastapi.Security(
        auth.get_current_user,
    ),
    default_filter_args: list = fastapi.Depends(
        partner_setting_default_filter_args
    ),
) -> fastapi.Response:
    """Update partner shipment point with provided ID.

    Returns 404 NOT FOUND due to the following statuses:
    * `not_found`: provided partner not found
    """
    actions = PartnerSettingActions(current_user=user)
    result = await actions.partner_setting_update(
        partner_id=user.partners[0],
        update=update,
        default_filter_args=default_filter_args,
    )

    return JSONResponse(jsonable_encoder(result))
