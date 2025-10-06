from api.conf import conf

async def get_api_key() -> str:
    return conf.cdek.webhook_api_key
