import pytest
from api import models


@pytest.fixture(scope="module")
async def country(initialize_tests):
    return await models.Country.create(**{
        "id": 1,
        "name": "Kazakstan",
    })