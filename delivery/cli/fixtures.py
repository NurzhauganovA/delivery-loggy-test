import asyncio
import io
import json
import logging
import typing

import click
import pydantic

import api


logger = logging.Logger('cli')


class CallDoesNotExist(Exception):
    """Raises if required call does not exist."""


class SchemaInternalDoesNotExist(Exception):
    """Raises if internal schema for model does not exist."""


def _get_schema_internal(name: str) -> typing.Type[pydantic.BaseModel]:
    if name.startswith('Profile'):
        name = 'Profile'

    schema = f'{name}Internal'
    for item in dir(api.schemas):
        if item == schema:
            return getattr(api.schemas, item)

    raise SchemaInternalDoesNotExist(
        f'{schema} schema for model: {name} does not exist',
    )


def _get_model_related_call(name: str) -> typing.Callable:
    if name.startswith('Profile'):
        name = 'Profile'

    call_name = f'{name.lower()}_create'
    if call_name in dir(api.models):
        return getattr(api.models, call_name)

    raise CallDoesNotExist(
        f'{call_name} does not exist in {api.models} module',
    )


def sort_fixtures_by_id(fixtures: dict) -> None:
    for table_name, entries in fixtures.items():
        if isinstance(entries, list):
            sorted_entries = sorted(entries,
                                    key=lambda item: item['id'] if item.get('id') else 0)
            fixtures.update({table_name: sorted_entries})


def _parse_fixtures(file: io._io.TextIOWrapper) -> typing.Dict:
    try:
        fixtures = json.load(file)
        sort_fixtures_by_id(fixtures)

        return fixtures
    except json.JSONDecodeError as e:
        raise click.ClickException(str(e)) from e


def _get_call_and_schema_from_table(table_name: str) -> tuple:
    exc = click.ClickException

    try:
        internal_schema = _get_schema_internal(table_name)
        call = _get_model_related_call(table_name)
    except (CallDoesNotExist, SchemaInternalDoesNotExist) as e:
        raise exc(str(e)) from e

    return internal_schema, call


async def _create_entry(
    table_name: str,
    entry: dict,
    exclude: typing.Dict[str, typing.Dict[str, str]] = None,
) -> None:
    internal_schema, call = _get_call_and_schema_from_table(table_name)

    if exclude is not None:
        excluding_table_params = exclude.get(table_name.capitalize())

        if excluding_table_params:
            await _prepare_exclude(exclude)
            key_field, values = excluding_table_params.values()

            if entry[key_field] in values:
                return

    try:
        await call(**{table_name.lower(): internal_schema(**entry)})

    # TODO: remake errors handling
    except Exception as e:
        error_class = e.__class__.__name__
        basic_errors = ('AlreadyExists', 'DoesNotExist', 'NotFound', 'ActionException')
        logger.warning(str(entry)[:140])
        logger.warning(e)
        for error in basic_errors:
            if error_class.endswith(error):
                return

        logger.warning(f'WARNING: {e}')
        logger.warning(f'table_name: {table_name.lower()}, '
                       f'schema: {internal_schema.__name__}, '
                       f'error cls: {error_class}')


def _get_model_list_call(table_name: str) -> typing.Callable:
    call_name = f'{table_name.lower()}_get_list'
    if call_name in dir(api.models):
        return getattr(api.models, call_name)

    raise CallDoesNotExist(
        f'{call_name} does not exist in {api.models} module',
    )


def _extract_values_with_key_field_from_list(key_field: str, array: list) -> list:
    return list(map(lambda item: item[key_field] if isinstance(item, dict) else getattr(item, key_field), array))


async def _prepare_exclude(exclude: dict) -> None:
    for table_name, params in exclude.items():
        objects = await _get_model_list_call(table_name)()
        params['values'] = _extract_values_with_key_field_from_list(
            params['key_field'],
            objects,
        )


async def _parse_and_create_entries(
    entries: typing.Union[dict, list],
    table_name: str,
) -> None:
    if table_name.startswith('Profile'):
        table_name = 'Profile'

    exclude_duplicates = {
        'Status': {
            'key_field': 'name',
        },
    }

    if isinstance(entries, list):
        for entry in entries:
            await _create_entry(table_name, entry, exclude_duplicates)

    else:
        await _create_entry(table_name, entries, exclude_duplicates)


async def handle_table(table_name: str, entries: typing.Union[dict, list]) -> None:
    models_module_content = dir(api.models)

    for name in models_module_content:
        attr = getattr(api.models, name)
        if hasattr(attr, 'Meta') and attr.Meta.table == table_name:
            await _parse_and_create_entries(entries, name)
            return


@click.command(
    name='load',
    help='Load fixtures from .json file',
)
@click.argument(
    'file',
    type=click.File(),
    required=True,
)
def fixtures_load(file: io._io.TextIOWrapper) -> None:
    async def _fixtures_load() -> None:
        fixtures = _parse_fixtures(file)

        for table_name, entries in fixtures.items():
            await handle_table(table_name, entries)

    loop = asyncio.get_event_loop()
    loop.run_until_complete(_fixtures_load())


commands = click.Group('fixtures')
commands.add_command(fixtures_load)
