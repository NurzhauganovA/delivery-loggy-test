from .. import exceptions
from .. import models


async def device_create(create, **kwargs):
    await models.device_create(create, **kwargs)
