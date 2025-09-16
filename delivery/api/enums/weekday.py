import enum


class Weekday(str, enum.Enum):
    MONDAY = 'monday'
    TUESDAY = 'tuesday'
    WEDNESDAY = 'wednesday'
    THURSDAY = 'thursday'
    FRIDAY = 'friday'
    SATURDAY = 'saturday'
    SUNDAY = 'sunday'

    def __str__(self) -> str:
        return str(self.value)

    @classmethod
    def as_list(cls, to_string: bool = False) -> list:
        call = lambda day: str(day) if to_string else day  # noqa: E731
        return [call(day) for day in cls]
