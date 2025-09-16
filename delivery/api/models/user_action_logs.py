import json

import tortoise
import tortoise.expressions
import tortoise.query_utils

from .. import schemas
from .mixins import HistoryAbstract


fields = tortoise.fields


class UserActionLogsError(Exception):
    pass


class UserActionLogs(HistoryAbstract):
    pass


async def user_action_logs_create(
    UserActionLogsCreate: schemas.UserActionLogsCreate,
) -> None:
    try:
        UserActionLogsCreate.action_data = json.dumps(
            UserActionLogsCreate.action_data,
            indent=4,
            sort_keys=True,
            default=str,
        )
        await UserActionLogs.create(**UserActionLogsCreate.dict())
    except tortoise.exceptions.BaseORMException as e:
        raise UserActionLogsError(e)
