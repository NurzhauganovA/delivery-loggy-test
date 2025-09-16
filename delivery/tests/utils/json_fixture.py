import json

from delivery.tests.conftest import CUR_DIR


def get_fixture(root_path: str, module: str, path: str) -> dict | list[dict]:
    """
    Получение фикстуры в формате JSON

    Args:
        root_path: корневая точка до фикстур
        module: наименование модуля тестов
        path: путь до фикстуры

    Returns:
        Загруженная фикстура
        [
            {
                "key": "value1"
            },
            {
                "key": "value2"
            },
        ]
    """

    if not path.endswith('.json'):
        path += '.json'
    fixture_path = f'{CUR_DIR}/{root_path}/{module}/fixtures/{path}'
    try:
        with open(fixture_path) as file:
            fixture = json.load(file)
    except Exception as exc:
        print(f"[ERROR] Can't load fixture {fixture_path}: {exc}")
        raise exc
    return fixture
