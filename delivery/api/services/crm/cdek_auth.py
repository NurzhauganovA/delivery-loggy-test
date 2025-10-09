import jwt

from datetime import datetime, timedelta
from typing import Optional

from fastapi import HTTPException, status

from api.conf import Settings


class CDEKAuthService:
    @staticmethod
    def verify_secret_key(secret_key: str) -> bool:
        return secret_key == "123456"  # Settings.cdek_auth.secret_key

    @staticmethod
    def create_access_token(client_id: str = "cdek") -> dict:
        expires_in = 30  # Settings.cdek_auth.expiration_seconds
        expire = datetime.utcnow() + timedelta(seconds=expires_in)

        payload = {
            "sub": client_id,
            "client_type": "cdek",
            "iat": datetime.utcnow(),
            "exp": expire
        }

        token = jwt.encode(
            payload,
            "123456",  # Settings.cdek_auth.secret_key
            algorithm="HS256"  # Settings.cdek_auth.algorithm
        )

        return {
            "access_token": token,
            "token_type": "Bearer",
            "expires_in": expires_in
        }

    @staticmethod
    def verify_access_token(token: str) -> dict:
        try:
            payload = jwt.decode(
                token,
                "123456",  # Settings.cdek_auth.secret_key
                algorithms=["HS256"]  # Settings.cdek_auth.algorithm
            )

            if payload.get("client_type") != "cdek":
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Неверный тип клиента",
                    headers={"WWW-Authenticate": "Bearer"},
                )

            return payload
        except jwt.ExpiredSignatureError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Токен истек",
                headers={"WWW-Authenticate": "Bearer"},
            )
        except jwt.InvalidTokenError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Неверный токен",
                headers={"WWW-Authenticate": "Bearer"},
            )
