import asyncio
import sys

import click

import api
from api.models import Area


@click.command(
    name='areaswapcords',
    help='Create a new user in the database',
)
def area_swap_coordinates() -> None:
    async def _area_swap() -> None:
        try:
            areas = await Area.all()
            for area in areas:
                scope = area.scope
                new_scope = []
                for item in scope:
                    new_scope.append({'latitude': item['longitude'], 'longitude': item['latitude']})
                print('old = ', scope[0], 'new = ', new_scope[0])
                area.scope = new_scope
                await area.update_from_dict(dict(scope=new_scope))
                await area.save(update_fields=['scope', ])
        except Exception:
            sys.exit(1)

        click.secho('Area coordinates was swapped', fg='green')

    loop = asyncio.get_event_loop()
    loop.run_until_complete(_area_swap())


commands = click.Group('area')
commands.add_command(area_swap_coordinates)
