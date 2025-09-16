from fastapi import Depends
from fastapi.security import OAuth2PasswordRequestFormStrict

from .. import PydanticException
from ..exceptions import HTTPNotFoundException
from ..enums import ProfileType
from ..models import profile_types_to_models


async def token_validate_payload(
    profile_type: ProfileType | None = None,
    profile_id: int | None = None,
    form_data: OAuth2PasswordRequestFormStrict = Depends(),
):
    profile_type = profile_type or form_data.client_secret
    if profile_type is not None:
        try:
            profile_type = ProfileType(profile_type)
        except ValueError as e:
            errors = (('client_secret', str(e)),)
            raise PydanticException(errors=errors)
    profile_id = profile_id or form_data.client_id

    if profile_type and profile_id:
        model = profile_types_to_models[profile_type]
        filter_params = {}
        if '@' in form_data.username:
            filter_params['user__email'] = form_data.username
        elif '+' in form_data.username:
            filter_params['user__phone_number'] = form_data.username
        if not await model.filter(id=profile_id, **filter_params).exists():
            raise HTTPNotFoundException('Profile does not exist with given parameters')
    return {
        'credential': form_data.username,
        'password': form_data.password,
        'profile_type': profile_type,
        'profile_id': profile_id,
    }


__all__ = (
    'token_validate_payload',
)
