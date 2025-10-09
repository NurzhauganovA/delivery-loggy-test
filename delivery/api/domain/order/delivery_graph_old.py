from typing import (
    List,
    Dict,
    Optional,
)


def get_delivery_graph_step(graph: List[Dict], slug: str) -> Optional[Dict]:
    """
    Находит и возвращает первый шаг в графе, который соответствует заданному slug.

    Args:
        graph: Деливери граф
        slug: Идентификатор шага, сейчас временно это slug

    Returns:
        Словарь, представляющий найденный шаг, или None, если шаг не найден.
    """
    return next((step for step in graph if step.get('slug') == slug), None)
