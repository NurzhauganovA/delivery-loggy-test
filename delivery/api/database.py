# TODO: should wrap name into "" if name of UUID type
import contextlib
import typing

import asyncpg
import tortoise
import tortoise.backends.base.client
import tortoise.transactions

from .conf import conf


@contextlib.asynccontextmanager
async def database_connection(dsn: typing.Optional[str] = None) -> typing.AsyncContextManager:
    host = None
    port = None
    user = None
    password = None
    database = None

    if dsn is None:
        host = conf.postgres.host
        port = conf.postgres.port
        user = conf.postgres.user
        password = conf.postgres.password
        database = conf.postgres.database

    connection = await asyncpg.connect(
        dsn=dsn,
        host=host,
        port=port,
        user=user,
        password=password,
        database=database,
    )

    try:
        yield connection
    finally:
        await connection.close()


async def initialize(generate_safe: bool = True) -> None:
    await tortoise.Tortoise.init(config=conf.tortoise.dict())
    # await tortoise.Tortoise.generate_schemas(safe=generate_safe)


async def close_connections():
    await tortoise.Tortoise.close_connections()


async def database_exists(db_name: str) -> bool:
    async with database_connection() as connection:
        # TODO: make query for returning either True or False nor True or None.
        # Might be changed to DROP DATABASE IF EXISTS.
        value = await connection.fetchval(
            f"""SELECT True FROM pg_database WHERE datname={db_name!r};""",
        )
    if value is not None:
        return value
    return False


async def drop_database(db_name: str) -> None:
    """Don't use beyond tests and test database."""
    async with database_connection() as connection:
        await connection.execute(f"""DROP DATABASE IF EXISTS "{db_name}";""")


async def create_database(db_name: str) -> None:
    async with database_connection() as connection:
        await connection.execute(f"""CREATE DATABASE "{db_name}";""")


async def delete_table_records_by_ids(
    db_uri: str,
    tables_with_ids: typing.Optional[list],
    table_with_ids: typing.Optional[list],
) -> None:
    """Due to autoincrementation, `id` field must be reset to appropriate value.
    Interface allows to accept table, its pk ids, restart id values to exclusively delete rows.
    """
    assert tables_with_ids is not None or table_with_ids is not None

    query_list = []
    async with database_connection(dsn=db_uri) as connection:
        if tables_with_ids is not None:
            for table, id in tables_with_ids:
                # TODO: find an alternative solution to solve a bug in tests
                # when single query described instead of two appends to list.
                query_list.append(f"""DELETE FROM "{table}" WHERE id={id};""")
                query_list.append(
                    f"""ALTER TABLE "{table}" ALTER COLUMN id RESTART WITH {id};""",
                )
            await connection.execute(''.join(query_list))

        query_list.clear()

        if table_with_ids is not None:
            table, ids, restart_id = table_with_ids
            for id in ids:
                query_list.append(f"""DELETE FROM "{table}" WHERE id={id};""")
            query_list.append(
                f"""ALTER TABLE "{table}" ALTER COLUMN id RESTART WITH {restart_id};""",
            )
            await connection.execute(''.join(query_list))


async def delete_table_records(db_uri: str, tables: list) -> None:
    """While resetting the `id`, default value of 1 must be applied."""
    query_list = []
    async with database_connection(dsn=db_uri) as connection:
        for table in tables:
            query_list.append(f"""DELETE FROM "{table}";""")
            query_list.append(f"""ALTER TABLE "{table}" ALTER COLUMN id RESTART WITH 1;""")
        await connection.execute(''.join(query_list))
