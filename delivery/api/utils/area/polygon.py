from shapely.geometry import(
    Point,
    Polygon,
)


async def contains_point(latitude: float, longitude: float, polygon: list[tuple]) -> bool:
    """
    Проверка на наличие точки внутри полигона

    Args:
        latitude: широта
        longitude: долгота
        polygon: точки периметра полигона
            [
                (12.3456, 23.456),
                (45.678, 56.789),
                ...
            ]

    Returns:
        Статус проверки
    """

    point = Point(latitude, longitude)
    polygon = Polygon(polygon)
    return polygon.covers(point)
