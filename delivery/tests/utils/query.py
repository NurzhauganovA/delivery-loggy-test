from delivery.tests.utils import normalize


def _parse_insert_query(table: str, fixture: dict) -> str:
    """
    Парсит данные в SQL запрос

    Args:
        table: наименование таблицы
        fixture: словарь из ключей и значений фикстуры
    """

    keys = ','.join(str(key) for key in fixture.keys())
    values = ','.join(
        normalize.parse_value_to_sql(value) for value in fixture.values()
    )
    return f'INSERT INTO {table} ({keys}) VALUES({values});'


def create_insert(table: str, fixtures: dict|list[dict]) -> str:
    """
    Создаёт голый SQL INSERT запрос

    Args:
        table: наименование таблицы
        fixture: фикстура полученная из файла

    Returns:
        SQL INSERT запрос ввиде строки
            INSERT INTO test (first, second) VALUES('test1', 'test2');
    """

    final_query = ''
    if isinstance(fixtures, list):
        for fixture in fixtures:
            final_query += _parse_insert_query(table, fixture)
    else:
        final_query = _parse_insert_query(table, fixtures)
    return final_query
