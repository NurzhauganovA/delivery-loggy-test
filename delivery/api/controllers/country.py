from .. import models
from .. import schemas


async def country_get(country_id: int):
    return await models.country_get(country_id)


async def country_get_list() -> list:
    return await models.country_get_list()


async def country_create(country: schemas.CountryCreate) -> dict:
    return await models.country_create(country)


async def country_update(
        country_id: int, update: schemas.CountryUpdate,
) -> dict:
    return await models.country_update(country_id, update)


async def country_delete(country_id: int) -> None:
    await models.country_delete(country_id)
