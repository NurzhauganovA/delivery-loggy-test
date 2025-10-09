import json

from delivery.tests.conftest import CUR_DIR
from .query import create_insert


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


def __read_fixture(path: str, name: str) -> dict | list[dict]:
    """
    Чтение фикстуры по пути запускаемого теста из папки fixtures и по имени фикстуры

    Args:
        path: путь, где запускается тест
        name: названия файла фикстуры

    Returns:
        SQL скрипт
    """
    if not name.endswith('.json'):
        name += '.json'

    fixture_path = f'{path}/{name}'

    try:
        with open(fixture_path) as file:
            fixture = json.load(file)
    except Exception as exc:
        print(f"[ERROR] Can't load fixture {fixture_path}: {exc}")
        raise exc
    return fixture


def get_sql_script_from_fixtures(current_dir: str, fixtures: dict) -> str:
    """
    Получение SQL скрипта, который загрузит все фикстуры в бд

    Args:
        current_dir: путь, где запускается тест
        fixtures: словарь, где ключ - название таблицы, значение - название файла фикстуры

    Returns:
        SQL скрипт
    """
    scripts = []
    for table, fixture_name in fixtures.items():
        fixture_data = __read_fixture(
            path=f'{current_dir}/fixtures',
            name=fixture_name,
        )
        insert_query = create_insert(table, fixture_data)
        scripts.append(insert_query)

    return " ".join(scripts)
