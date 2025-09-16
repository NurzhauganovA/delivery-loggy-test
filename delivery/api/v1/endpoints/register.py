import fastapi

from ... import controllers
from ... import responses
from ... import schemas


router = fastapi.APIRouter()


# @router.post(
#     '/register',
#     summary='Register owner',
#     response_description='Owner created successfully',
#     responses=responses.generate_responses(
#         [
#             responses.APIResponseTemporarilyUnavailable,
#             responses.APIResponseBadRequest,
#             responses.APIResponseCreated,
#         ],
#     ),
#     status_code=201,
# )
# async def register(owner: schemas.RegisterCreate) -> None:
#     """Register owner.
#
#     Create user, profile and send OTP. If OTP was not send due
#     to remote service error than description of the error will
#     be provided in error's response description.
#
#     Returns 400 BAD REQUEST due to the following statuses:
#     * `bad_request`: one of user already exists, profile already
#                      exists or remote OTP service returned an error
#     """
#     await controllers.register(owner)
