import asyncio

import click
import pydantic

import api


@click.command(
    name='create',
    help='Create otp in redis',
)
@click.option(
    '--phone_number',
    type=str,
    prompt='Phone number',
    help='Phone number of the user',
)
@click.option(
    '--otp',
    type=int,
    prompt='OTP',
    help='OTP for the new user',
)
def otp_create(phone_number: str, otp: int) -> None:
    async def _otp_create() -> None:
        try:
            api.schemas.OTPCreate(
                phone_number=phone_number,
            )
        except pydantic.ValidationError as e:
            raise click.ClickException(e.errors()[0]['msg'])

        lower_bound = 1000
        upper_bound = 10000
        if otp not in range(lower_bound, upper_bound):
            raise click.ClickException(
                f'OTP must be greater than or equal to {lower_bound} '
                f'and less than or equal to {upper_bound - 1}',
            )

        await api.redis_module.get_connection().set(phone_number, otp)
        click.secho('OTP was recorded successfully', fg='green')

    loop = asyncio.get_event_loop()
    loop.run_until_complete(_otp_create())


commands = click.Group('otp')
commands.add_command(otp_create)
