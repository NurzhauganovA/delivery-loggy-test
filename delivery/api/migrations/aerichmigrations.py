import pathlib
import typing

import aerich
import tortoise
import tortoise.backends
import tortoise.transactions

import api


def get_versions(versions_dirname: typing.Optional[str] = None) -> list:
    if versions_dirname is None:
        versions_dirname = 'versions'

    versions_dir = pathlib.Path(__file__).parent.joinpath(versions_dirname)
    version_files = [version.name for version in versions_dir.iterdir()]
    version_files.sort(key=lambda it: int(it.split('_')[0]))
    versions = [versions_dir.joinpath(version) for version in version_files]

    return versions


async def upgrade(uri: str, app: typing.Optional[str] = None) -> None:
    if app is None:
        app = 'versions'

    options = api.conf.tortoise.dict()
    options['connections']['default'] = uri

    # Config must be provided with tz key value
    await tortoise.Tortoise.init(config=options)

    connection_name = aerich.utils.get_app_connection_name(options, app)
    for version in get_versions():
        content = aerich.utils.get_version_content_from_file(version)

        async with tortoise.transactions.in_transaction(
                connection_name,
        ) as connection:
            for query in content['upgrade']:
                await connection.execute_script(query)

            await aerich.Aerich.create(
                app=app,
                version=version,
                content=aerich.utils.get_models_describe(app),
            )


async def close_connection() -> None:
    """Closes connection given by `default` key in tortoise config."""
    await tortoise.Tortoise.close_connections()
