from fastapi import HTTPException, status

from api.services.crm.cdek_auth import CDEKAuthService
from api.schemas.crm.cdek_auth import CDEKAuthRequest, CDEKAuthResponse


class CDEKAuthController:
    @staticmethod
    async def authenticate(request: CDEKAuthRequest) -> CDEKAuthResponse:
        if not CDEKAuthService.verify_secret_key(request.secret_key):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid secret key",
                headers={"WWW-Authenticate": "Bearer"},
            )

        token_data = CDEKAuthService.create_access_token()

        return CDEKAuthResponse(**token_data)

    @staticmethod
    async def verify_token(token: str) -> dict:
        return CDEKAuthService.verify_access_token(token)