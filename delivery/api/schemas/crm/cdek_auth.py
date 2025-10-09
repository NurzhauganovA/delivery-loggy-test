from pydantic import Field
from tortoise.contrib.pydantic import PydanticModel


class CDEKAuthRequest(PydanticModel):
    """Схема запроса авторизации CDEK"""
    secret_key: str = Field(..., description="Secret key для идентификации клиента CDEK")


class CDEKAuthResponse(PydanticModel):
    """Схема ответа авторизации CDEK"""
    access_token: str = Field(..., description="JWT токен доступа")
    token_type: str = Field(default="Bearer", description="Тип токена")
    expires_in: int = Field(..., description="Время жизни токена в секундах")

    class Config:
        json_schema_extra = {
            "example": {
                "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyLCJleHAiOjE1MTYyNDI2MjJ9.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c",
                "token_type": "Bearer",
                "expires_in": 3600
            }
        }
