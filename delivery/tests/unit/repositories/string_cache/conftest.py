from unittest.mock import AsyncMock

import pytest

from api.repositories.string_cache import StringCache


@pytest.fixture
def mock_redis():
    return AsyncMock()

@pytest.fixture
def cache(mock_redis):
    return StringCache(client=mock_redis)
