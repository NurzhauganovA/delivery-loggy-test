# TODO: append OTP creation here
import asyncio
import sys

import click

import api


@click.command(
    name='create',
    help='Create a new user in the database',
)
@click.option(
    '--phone_number',
    type=str,
    prompt='Phone number',
    help='Phone number of the new user',
)
@click.option(
    '--iin',
    type=str,
    prompt='IIN',
    help='iin of the new user',
)
def user_create(
    phone_number: str,
    iin: str,
) -> None:
    async def _user_create() -> None:
        try:
            user = await api.models.user_create(
                api.schemas.UserCreate(
                    phone_number=phone_number,
                    iin=iin,
                ),
            )

            try:
                await api.verification.client.verify_user(
                    api.schemas.VerificationUser(confirmed=True, iin=iin),
                )
            except Exception:
                user.update(
                    {
                        'first_name': 'Вася',
                        'last_name': 'Петров',
                        'middle_name': 'Николаевич',
                    },
                )
                await api.models.user_update(
                    user_id=user.pop('id'),
                    update=api.schemas.UserUpdate(**user),
                )

        except api.models.UserAlreadyExists:
            click.secho(
                f'User with provided phone_number: {phone_number} already exists',
                fg='red',
            )

            sys.exit(1)

        click.secho('User was created successfully', fg='green')

    loop = asyncio.get_event_loop()
    loop.run_until_complete(_user_create())


commands = click.Group('user')
commands.add_command(user_create)
