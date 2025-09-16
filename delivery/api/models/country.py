from typing import List

from pydantic import parse_obj_as
from tortoise import Model
from tortoise import fields
from tortoise.exceptions import DoesNotExist

from .. import schemas, models
from api.modules.city.infrastructure.db_table import City
from ..context_vars import locale_context
from ..schemas import CountryGet


class Country(Model):
    id = fields.IntField(pk=True)
    name_en = fields.CharField(max_length=255, unique=True, null=True)
    name_kk = fields.CharField(max_length=255, unique=True, null=True)
    name_ru = fields.CharField(max_length=255, unique=True, null=True)
    name_zh = fields.CharField(max_length=255, unique=True, null=True)

    city_set: fields.ReverseRelation['City']

    class Meta:
        table = 'country'

    @property
    def name(self):
        locale = locale_context.get()
        return getattr(self, f'name_{locale}', self.name_en)


async def country_get(country_id: int):
    qs = Country.get(id=country_id)
    try:
        instance = await qs.prefetch_related('cities')
        return CountryGet.from_orm(instance)
    except DoesNotExist:
        raise DoesNotExist(
            f'country with given ID: {country_id} was not found',
        )


async def country_get_list() -> list:
    queryset = await Country.all().order_by('id').prefetch_related(
        'cities',
    )
    result = parse_obj_as(List[schemas.CountryGet], queryset)
    return result


async def country_create(country: schemas.CountryCreate) -> dict:
    country = await Country.create(**country.dict(exclude_unset=True))
    return dict(country)


async def country_update(
    country_id: int,
    update: schemas.CountryUpdate,
) -> dict:
    country = await country_get(country_id=country_id)
    await country.update_from_dict(update.dict(exclude_unset=True)).save()

    return dict(country)


async def country_delete(country_id: int) -> None:
    country = await country_get(country_id)
    await country.delete()
