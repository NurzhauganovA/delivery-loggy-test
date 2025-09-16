import os

import asyncio

import pytest


CUR_DIR = os.path.dirname(__file__)


@pytest.fixture(scope="session")
def event_loop(request):
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
    yield loop

    loop.close()
