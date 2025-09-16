import fastapi

from ... import auth
from ... import controllers
from ... import schemas


router = fastapi.APIRouter()


@router.post(
    '/firebase/device',
    summary='Register FCM Device',
    status_code=201,
)
async def create_device(
        create: schemas.FCMDeviceCreate,
        current_user: schemas.UserCurrent = fastapi.Security(auth.get_current_user),
):
    """
    Registers Firebase device for with given id, type for current_user.
    """
    await controllers.device_create(create, user_id=current_user.id)
