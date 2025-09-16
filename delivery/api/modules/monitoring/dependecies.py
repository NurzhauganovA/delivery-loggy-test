from api import auth, schemas
from .schemas import Geolocation, GeolocationPut
from fastapi import Security


async def geolocation_validate_payload(
    geolocation: Geolocation,
    current_user: schemas.UserCurrent = Security(auth.get_current_user),
):
    profile = current_user.profile
    profile_type = profile['profile_type']
    profile_content = profile['profile_content']
    return GeolocationPut(
        **geolocation.dict(),
        courier_partner_id=profile_content['partner_id'],
        courier_id=profile.get('id')
    )

