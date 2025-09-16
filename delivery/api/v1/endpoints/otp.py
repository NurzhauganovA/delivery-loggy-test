import fastapi

from ... import auth
from ... import controllers
from ... import schemas


router = fastapi.APIRouter()


# TODO: change OTP code lifetime
@router.post(
    '/otp',
    summary='Create OTP code',
    response_description='OTP code successfully created',
    status_code=201,
)
async def otp_create(body: schemas.OTPCreate) -> dict:
    """Create OTP.

    If user with the phone number in `body` argument is existing,
    then OTP code will be sent to that number and stored in database.
    If service response was received with its internal error and
    status code, than BAD REQUEST error will be raised.

    Returns 400 BAD REQUEST due to the following statuses:
    * `bad_request`: remote service response error
    """
    return await controllers.otp_create(body)


@router.post(
    '/otp/validate',
    summary='Validate OTP code',
    response_description='OTP code and phone number validated successfully',
    status_code=204,
)
async def otp_validate(body: schemas.OTPGet,
                       bg_tasks: fastapi.BackgroundTasks) -> fastapi.responses.Response:
    """OTP code and phone number validate.

    If the phone number and OTP code entered the body exist in system,
    then an empty response and status 204 will be received,
    if the phone number is not found, a 400 BAD REQUEST response will be received,
    if the phone number exists but the code is incorrect,
    then a 404 NOT FOUND response will be received
    """
    await controllers.otp_validate(phone_number=body.phone_number,
                                   password=body.otp,
                                   agree=body.agree,
                                   bg_tasks=bg_tasks)
    return fastapi.responses.Response(status_code=204)


@router.post(
    '/otp/send_register_link',
    summary='Send register link',
    response_description='Register link sended',
    status_code=204,
)
async def send_register_link(
    body: schemas.Message,
    current_user: schemas.UserCurrent = fastapi.Security(auth.get_current_user),
) -> fastapi.responses.Response:
    """OTP code and phone number validate.

    If the phone number and OTP code entered the body exist in system,
    then an empty response and status 204 will be received,
    if the phone number is not found, a 400 BAD REQUEST response will be received,
    if the phone number exists but the code is incorrect,
    then a 404 NOT FOUND response will be received
    """
    await controllers.send_register_link(body, current_user)
    return fastapi.responses.Response(status_code=204)
