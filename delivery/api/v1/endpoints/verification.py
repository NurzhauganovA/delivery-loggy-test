import fastapi

from ... import auth
from ... import controllers
from ... import responses
from ... import schemas


router = fastapi.APIRouter()


# TODO: remove `user` namings
@router.post(
    '/verification/user',
    summary='Get verified user',
    response_model=schemas.VerificationUserGet,
    response_description='Verified user',
    responses=responses.generate_responses(
        [
            responses.APIResponseNotFound,
            responses.APIResponseTemporarilyUnavailable,
        ],
    ),
)
async def verify_user(
    user: schemas.VerificationUser,
    current_user: schemas.UserCurrent = fastapi.Security(auth.get_current_user),
) -> dict:
    """Get verified user.

    Returns 404 NOT FOUND due to the following statuses:
    * `not_found`: provided user not found
    """
    return await controllers.verify_user(user)

# TODO: Пока что закомментил, так как для безопасности требуется закрыть
# @router.post(
#     '/verification/courier',
#     summary='Get verified courier',
#     response_description='Verified courier',
#     responses=responses.generate_responses(
#         [
#             responses.APIResponseNotFound,
#             responses.APIResponseTemporarilyUnavailable,
#         ],
#     ),
# )
# async def verify_courier(
#     courier: schemas.VerificationCourier,
# ) -> dict:
#     """Get verified courier.
#
#     Returns 404 NOT FOUND due to the following statuses:
#     * `not_found`: provided user not found
#     """
#     return await controllers.verify_courier(courier)
#
#
# @router.post(
#     '/verification/partner',
#     summary='Get a verified partner',
#     response_model=schemas.VerificationPartnerGet,
#     response_description='Verified partner',
#     responses=responses.generate_responses(
#         [
#             responses.APIResponseNotFound,
#             responses.APIResponseTemporarilyUnavailable,
#         ],
#     ),
# )
# async def verify_partner(
#     partner: schemas.VerificationPartner,
#     # current_user: schemas.UserCurrent = fastapi.Security(auth.get_current_user),
# ) -> dict:
#     """Get verified partner.
#
#     Returns 404 NOT FOUND due to the following statuses:
#     * `not_found`: provided partner not found
#     """
#     return await controllers.verify_partner(partner)