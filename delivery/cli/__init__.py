import click

from . import fixtures
from . import otp
from . import user
from . import area


commands = click.Group()
commands.add_command(fixtures.commands)
commands.add_command(otp.commands)
commands.add_command(user.commands)
commands.add_command(area.commands)
