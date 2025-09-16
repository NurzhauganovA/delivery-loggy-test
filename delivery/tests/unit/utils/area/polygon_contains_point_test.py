import json
import pytest

from delivery.tests.conftest import CUR_DIR

from delivery.utils.area import polygon


FIXTURES_PATH = f'{CUR_DIR}/unit/utils/area/fixtures/'


@pytest.mark.asyncio
async def test_polygon_contains_point_true():
    expected = True
    path = f'{FIXTURES_PATH}/{expected}.json'

    with open(path) as file:
        data = json.load(file)
        data_polygon = data['polygon']
        lat = data['lat']
        lon = data['lon']

    assert await polygon.contains_point(lat, lon, data_polygon) == expected


@pytest.mark.asyncio
async def test_polygon_contains_point_false():
    expected = False
    path = f'{FIXTURES_PATH}/{expected}.json'

    with open(path) as file:
        data = json.load(file)
        data_polygon = data['polygon']
        lat = data['lat']
        lon = data['lon']

    assert await polygon.contains_point(lat, lon, data_polygon) == expected
