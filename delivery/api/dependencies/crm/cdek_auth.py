from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from api.services.crm.cdek_auth import CDEKAuthService

security = HTTPBearer()


async def get_cdek_client(
        credentials: HTTPAuthorizationCredentials = Depends(security)
) -> dict:
    token = credentials.credentials
    payload = CDEKAuthService.verify_access_token(token)
    return payload