import json
from typing import Any


def parse_value_to_sql(value: Any) -> Any:
    """
    Перевод Pyton значения в SQL

    Args:
        value: исходное значение
            None

    Returns:
        Значение для sql
            'null'
    """

    if isinstance(value, (dict, list)):
        value = str(json.dumps(value))
    if isinstance(value, str):
        return f"'{value}'"
    if value is None:
        return 'null'
    return str(value)
