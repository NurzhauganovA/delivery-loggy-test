import base64
import datetime
import decimal
import re
from copy import deepcopy
from functools import reduce
from operator import add, mul
from typing import Callable
from typing import List

import pydantic
from pydantic.typing import AnyCallable


def reuse(
        *fields: str,
        pre: bool = False,
        each_item: bool = False,
        always: bool = False,
        check_fields: bool = True,
        whole: bool = None,
        allow_reuse: bool = True,
) -> Callable[[AnyCallable], classmethod]:
    def dec(f: AnyCallable) -> classmethod:
        f = deepcopy(f)
        return pydantic.validator(
            *fields, pre=pre, each_item=each_item, whole=whole,
            always=always, check_fields=check_fields, allow_reuse=allow_reuse)(f)

    return dec


def validate_iin(value):
    if value is None:
        return value
    value = value.replace(' ', '').replace('-', '')
    if not value.isdigit():
        raise ValueError('Invalid IIN')
    return value


def validate_phone(value: str) -> str:
    # if not value.startswith('+'):
    #     raise ValueError('Phone number must start with the + sign')
    # if not value[1:].isdigit():
    #     raise ValueError('Phone number must contain digits only')
    # if value[1:5] not in phone_codes:
    #     raise ValueError('Phone number is not valid')
    #
    validated_phone = re.sub('[a-zA-Zа-яА-Я_ \-()]+', '', value)
    if validated_phone is None or validated_phone == '':
        raise ValueError('Invalid format')

    return validated_phone


def validate_latitude(latitude: decimal.Decimal) -> decimal.Decimal:
    integral_part_range = range(-90, 91)
    exponent_limit_range = range(-8, 0)
    # if latitude:
    #     integral = latitude.to_integral()
    #     params = latitude.as_tuple()
    #     digits_limit = 10
    #
    #     if len(params.digits) > digits_limit:
    #         raise ValueError(
    #             'Latitude total number of digits must be '
    #             f'less than or equal to {digits_limit}',
    #         )
    #     elif integral not in integral_part_range:
    #         raise ValueError(
    #             'Latitude integral part must be greater than or equal to '
    #             f'{integral_part_range[0]} and less than or equal to {integral_part_range[-1]}',
    #         )
    #     elif params.exponent not in exponent_limit_range:
    #         raise ValueError(
    #             'Latitude number of exponent digits must be '
    #             f'greater than or equal to {-exponent_limit_range[0]} '
    #             f'and less than or equal to {-exponent_limit_range[-1]}',
    #         )

    return latitude


def validate_longitude(longitude: decimal.Decimal) -> decimal.Decimal:
    integral_part_range = range(-180, 181)
    exponent_limit_range = range(-8, 0)
    # if longitude:
    #     integral = longitude.to_integral()
    #     params = longitude.as_tuple()
    #     digits_limit = 11
    #
    #     if len(params.digits) > digits_limit:
    #         raise ValueError(
    #             f'Longitude total number of digits must be '
    #             f'less than or equal to {digits_limit}',
    #         )
    #     elif integral not in integral_part_range:
    #         raise ValueError(
    #             'Longitude integral part must be greater than or equal to '
    #             f'{integral_part_range[0]} and less than or equal to {integral_part_range[-1]}',
    #         )
    #     elif params.exponent not in exponent_limit_range:
    #         raise ValueError(
    #             'Longitude number of exponent digits must be '
    #             f'greater than or equal to {-exponent_limit_range[0]} '
    #             f'and less than or equal to {-exponent_limit_range[-1]}',
    #         )

    return longitude


def validate_latitude_to_float(latitude: decimal.Decimal) -> decimal:
    latitude = validate_latitude(latitude)
    if not latitude:
        return latitude
    return float(latitude)


def validate_longitude_to_float(longitude: decimal.Decimal) -> decimal:
    longitude = validate_longitude(longitude)
    if not longitude:
        return longitude
    return float(longitude)


def ensure_bin_is_valid(bin: str) -> str:
    if not bin:
        return

    if not bin.isdigit():
        raise ValueError('BIN must contain digits only')

    if not int(bin[4]) in (4, 5, 6):
        raise ValueError('BIN must containt the sign of company')

    return bin


def multiply(iin: str, weights: List[int]) -> int:
    result = reduce(
        add,
        map(lambda i: mul(*i), zip(map(int, iin), weights))
    )
    return result


def ensure_work_time_is_valid(work_time: str) -> str:
    if not work_time:
        return work_time

    separated_time = work_time.split(':')

    if len(separated_time) == 1:
        raise ValueError('Separator between hour and minute must be ":"')

    hour, minute = separated_time
    if not hour.isdigit():
        raise ValueError('Hour must be digit')

    if not minute.isdigit():
        raise ValueError('Minute must be digit')

    if not (int(hour) >= 0 or int(hour) <= 23):
        raise ValueError('Hour must be great than 0 and less than 23')

    if not (int(minute) >= 0 or int(minute) <= 23):
        raise ValueError('Minute must be great than 0 and less than 23')

    return work_time


def to_base64(content: bytes | None) -> bytes | None:
    if content is not None:
        content = base64.b64encode(content)

    return content


def ensure_delivery_datetime_serialized(value: str) -> datetime.datetime:
    if value and isinstance(value, str):
        value = datetime.datetime.fromisoformat(value)

    return value


def ensure_date_has_valid_type(
        date_value: datetime.datetime | str,
) -> datetime.datetime | None:
    today = str(datetime.date.today())
    result = None

    if date_value is not None:
        if isinstance(date_value, str):
            delta = len(date_value) - len(today)
            if delta > 0:
                date_value = date_value[:-delta]
            result = datetime.date.fromisoformat(date_value)

    return result
