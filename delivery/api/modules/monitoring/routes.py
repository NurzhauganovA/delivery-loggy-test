from typing import List

import fastapi
from api import schemas, auth

from .actions import GeolocationActions
from .schemas import Geolocation
from .dependecies import geolocation_validate_payload

router = fastapi.APIRouter()


@router.put(
    '/monitoring/geolocation',
    summary='Create shipment points for partner in bulk',
    response_description='Shipment points created for Partner',
)
async def geolocation_put(
    geolocation: Geolocation = fastapi.Depends(
        geolocation_validate_payload
    ),
    _: schemas.UserCurrent = fastapi.Security(
        auth.get_current_user,
        # scopes=['gp:p'],
    ),
):
    """Create shipment points for the partner with given ID.

    Returns 404 NOT FOUND due to the following statuses:
    * `not_found`: provided partner not found
    """

    actions = GeolocationActions()
    await actions.geolocation_put(geolocation, )
    return fastapi.responses.Response(status_code=201)
