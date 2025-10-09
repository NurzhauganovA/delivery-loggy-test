import fastapi
from fastapi import status
from starlette.responses import JSONResponse
from fastapi.encoders import jsonable_encoder

from api.controllers.crm.cdek_auth import CDEKAuthController
from api.schemas.crm.cdek_auth import CDEKAuthResponse, CDEKAuthRequest

router = fastapi.APIRouter()


@router.post(
    '/auth-cdek',
    summary='CDEK authentication',
    response_model=CDEKAuthResponse,
    response_description='Returns JWT access token for CDEK client',
    status_code=status.HTTP_200_OK,
)
async def cdek_authenticate(
        request: CDEKAuthRequest,
):
    result = await CDEKAuthController.authenticate(request)

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content=jsonable_encoder(result)
    )