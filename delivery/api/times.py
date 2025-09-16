import datetime

import pytz


def utcnow() -> datetime.datetime:
    return datetime.datetime.now(tz=pytz.UTC)
