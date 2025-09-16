import abc
import secrets
import typing
from datetime import datetime
from datetime import timedelta

import fastapi.security
from jose import JWTError
from jose import jwt

from .conf import conf
from . import schemas


oauth2_scheme = fastapi.security.OAuth2PasswordBearer(tokenUrl='/api/v1/token')


class InvalidToken(Exception):
    """Raises if invalid token was provided"""


def gen_random_token(nbytes: int = 64) -> str:
    """Generate URL-safe string with n bytes of randomness."""
    return secrets.token_urlsafe(nbytes)


class JWTSinger:
    def __init__(
        self,
        secret_key: str = conf.token.secret_key,
        algorithm: str = 'HS256',
    ):
        self.secret_key = secret_key
        self.algorithm = algorithm

    def encode(self, payload, exp):
        to_encode = payload.copy()
        to_encode.update({"exp": self.get_exp(exp)})

        return jwt.encode(
            to_encode,
            self.secret_key,
            algorithm=self.algorithm,
        )

    def decode(self, token, verify_exp: bool = True):
        try:
            payload = jwt.decode(
                token,
                self.secret_key,
                algorithms=[self.algorithm],
                options={
                    'verify_exp': verify_exp,
                },
            )
            return payload
        except JWTError:
            raise InvalidToken

    @staticmethod
    def get_exp(exp):
        return datetime.utcnow() + timedelta(minutes=exp)


def sign_token(
    payload: dict,
    exp: int,
) -> str:
    """Sign provided token data."""
    return JWTSinger().encode(payload, exp=exp)


def unsign_token(
    token: str,
) -> dict:
    """Unsign provided token."""
    signer = JWTSinger()
    return signer.decode(token)


def extract_client_id_from_signed_token(
    token: str,
) -> typing.Optional[int]:
    try:
        return unsign_token(token=token).get('client_id')
    except InvalidToken:
        return


def issue_access_token(
    payload: dict,
) -> schemas.AccessTokenInternal:
    signed_token = sign_token(
        payload=payload,
        exp=conf.token.access_lifetime,
    )
    return schemas.AccessTokenInternal(
        client_id=payload['client_id'],
        token=signed_token,
        token_type='bearer',
    )


def issue_refresh_token(
    payload: dict,
) -> schemas.RefreshTokenInternal:
    signed_token = sign_token(
        payload=payload,
        exp=conf.token.refresh_lifetime,
    )
    return schemas.RefreshTokenInternal(
        client_id=payload['client_id'],
        token=signed_token,
        is_revoked=False,
        token_type='bearer',
    )
