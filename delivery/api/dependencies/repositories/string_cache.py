from api.redis_module import get_connection
from api.repositories.string_cache import StringCache

__string_cache: StringCache | None = None

async def get_string_cache() -> StringCache:
    global __string_cache
    if __string_cache is None:
        __string_cache = StringCache(
            client=get_connection()
        )

    return __string_cache
