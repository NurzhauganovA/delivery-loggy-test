from contextlib import asynccontextmanager

import pytest
import pytest_asyncio
from tortoise import Tortoise

from api.migrations.aerichmigrations import upgrade


class Postgres:
    host: str = 'localhost'
    port: int = 5432
    user: str = 'myuser'
    password: str = 'mypassword'
    database: str = 'mydatabase'

    @property
    def uri(self) -> str:
        return f'postgres://{self.user}:{self.password}@{self.host}:{self.port}/{self.database}'


def get_db_config(models: [str]):
    config = {
        'connections': {
            'default': Postgres().uri,
        },
        'apps': {
            'versions': {
                'default_connection': 'default',
            },
        },
    }

    config['apps']['versions']['models'] = models
    return config


@pytest_asyncio.fixture
async def db():
    config = get_db_config(models=[
        'api.models',
        'api.modules.call_request.infrastructure.db_table',
        'api.modules.city.infrastructure.db_table',
        'api.modules.delivery_point.infrastructure.db_table',
        'api.modules.order.infrastructure.db_table',
        'api.modules.order_chain.infrastructure.db_table',
        'api.modules.partner_settings.infrastructure.db_table',
        'api.modules.shipment_point.infrastructure.db_table',
    ])

    await Tortoise.init(config=config)
    # await Tortoise.generate_schemas()
    await Tortoise.get_connection('default').execute_script(__drop_tables_script)
    # TODO: Создание таблиц через миграции работает сейчас медленно, по 5-6 сек.
    await upgrade(config['connections']['default'], 'versions')

    try:
        yield

    finally:
        await Tortoise.get_connection('default').execute_script(__drop_tables_script)
        await Tortoise.close_connections()


@pytest_asyncio.fixture()
async def run_pre_start_sql_script():
    async def wrapper(pre_start_sql_script: str):
        try:
            await Tortoise.get_connection('default').execute_script(pre_start_sql_script)
        except Exception as e:
            raise e

    return wrapper


__drop_tables_script = """
    DO $$
        DECLARE
            r RECORD;
        BEGIN
            FOR r IN (
                SELECT tablename
                FROM pg_tables
                WHERE schemaname = 'public'
                AND tablename <> 'spatial_ref_sys'
            )
            LOOP
                EXECUTE 'DROP TABLE IF EXISTS ' || quote_ident(r.tablename) || ' CASCADE';
            END LOOP;
    END $$;
"""