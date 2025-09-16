# Move initializing to helpers
import asyncio

import api
import cli
from api.conf import conf


def main() -> None:
    loop = asyncio.get_event_loop()
    loop.run_until_complete(api.database.initialize())
    loop.run_until_complete(api.redis_module.connect(conf.redis.uri))

    cli.commands()

    loop.run_until_complete(api.database.close_connections())
    loop.run_until_complete(api.redis_module.disconnect())


if __name__ == '__main__':
    main()
