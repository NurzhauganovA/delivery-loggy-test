from api import models


async def get_partner_id(api_key: str) -> int:
    token = await models.PublicApiToken.filter(token=api_key).first()
    if not token:
        raise models.PublicApiTokenNotFound('Cannot get partner with provided api key')

    return token.partner_id
