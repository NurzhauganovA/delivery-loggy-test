import fastapi

from ... import auth
from ... import controllers
from ... import enums
from ... import responses
from ... import schemas
from ... import utils


router = fastapi.APIRouter()

# TODO: Пока что закомментил, так как для безопасности требуется закрыть
# @router.post(
#     '/biometry/get_biometry_url',
#     summary='Get city',
#     response_model=schemas.BiometryResponse,
#     response_description='City',
# )
# async def get_biometry_url(
#     biometry_request: schemas.BiometryRequest,
# ) -> dict:
#     """Get city with provided ID."""
#     return await controllers.get_biometry_url(biometry_request)

# TODO: Пока что закомментил, так как для безопасности требуется закрыть
# @router.post(
#     '/biometry/biometry_verify_user',
#     summary='Callback function for biometry service',
#     response_description='Updated user profile',
#     responses=responses.generate_responses(
#         [
#             responses.APIResponseNotFound,
#             responses.APIResponseNoContent,
#         ],
#     ),
#     status_code=204,
# )
# async def biometry_verify(
#     user_id: int,
#     request_body: schemas.BiometryVerifyBody
# ) -> fastapi.responses.Response:
#     """Update profile with provided ID.
#
#     Returns 404 NOT FOUND due to the following statuses:
#     * `not_found`: provided profile not found
#     """
#     await controllers.profile_biometry_verify(user_id, request_body)
#     return fastapi.responses.Response(status_code=204)
#
#
# @router.post(
#     '/biometry/send_link',
#     summary='Send biometry link to user by sms'
# )
# async def user_send_link_biometry(
#     body: schemas.SendLink,
#     current_user: schemas.UserCurrent = fastapi.Security(auth.get_current_user),
# ) -> fastapi.responses.Response:
#     await utils.send_link(
#         body=body,
#         action=enums.SMSActions.BIOMETRY,
#         current_user=current_user
#     )
#     return fastapi.responses.Response(status_code=200)
