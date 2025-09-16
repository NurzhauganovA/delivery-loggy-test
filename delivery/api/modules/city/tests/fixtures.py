import pytest
from api.modules.city.infrastructure.db_table import City
from api.modules.city.schemas import CityCreate


# noinspection PyUnusedLocal
@pytest.fixture(scope="module")
async def city(initialize_tests, country):
    create_schema = CityCreate(
        **{
            "id": 1,
            "name": "Алматы",
            "country_id": country.id,
            "longitude": 54.123412,
            "latitude": 52.12344,
            "timezone": 'Almaty'
        }
    )
    return await City.create(**create_schema.dict(exclude_none=True))
