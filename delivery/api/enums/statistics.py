from . import descriptor


class ProgressInterval(descriptor.Descriptor):
    DAILY = 'day'
    WEEKLY = 'week'
    MONTHLY = 'month'
    QUARTERLY = 'quarter'
    YEARLY = 'year'


progress_interval_to_query_map = {
    ProgressInterval.DAILY: 'date(dates)',
    ProgressInterval.WEEKLY: """
    daterange(
        to_date(to_char(dates, 'YYYYWW'), 'YYYYWW') + 2,
        to_date(to_char(dates, 'YYYYWW'), 'YYYYWW') + 8)
    """,
    ProgressInterval.MONTHLY: """
    daterange(
        to_date(to_char(dates, 'YYYYMM'), 'YYYYMM'),
        (to_date(to_char(dates, 'YYYYMM'), 'YYYYMM') + interval '1 month')::date -1)
    """,
    ProgressInterval.QUARTERLY: """
    daterange(
        to_date(to_char(dates, 'YYYYQQ'), 'YYYYQQ'),
        (to_date(to_char(dates, 'YYYYQQ'), 'YYYYQQ') + interval '3 months')::date -1) 
    """,
    ProgressInterval.YEARLY: """
    daterange(
        to_date(to_char(dates, 'YYYY'), 'YYYY'),
        (to_date(to_char(dates, 'YYYY'), 'YYYY') + interval '1 year')::date -1) 
    """
}
