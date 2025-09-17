import os

import pytest


@pytest.fixture
def img_png(request):
    script_dir = os.path.dirname(os.path.abspath(__file__))
    with open(f'{script_dir}/images/img.png', 'rb') as file:
        return ['image', (file.name, file.read(), 'image/png')]
