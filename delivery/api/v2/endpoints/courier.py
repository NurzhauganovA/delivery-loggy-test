from fastapi import APIRouter, Security

from api import schemas, auth, controllers, dependencies

router = APIRouter()

@router.post(
    '/courier/me/geolocation',
    summary='Send geolocation on courier action',
    status_code=200,
)
async def save_courier_geolocation(
    data: schemas.SaveCourierGeolocation,
    courier: schemas.UserCurrent = Security(
        auth.get_current_user,
        scopes=['gp:p'],
    ),
    default_filter_args: list = Security(dependencies.OrderDefaultFilterV2()),
):
    await controllers.save_courier_geolocation(
        courier=courier,
        data=data,
        default_filter_args=default_filter_args,
    )