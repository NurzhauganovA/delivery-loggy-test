import typing

import tortoise


class ArrayField(tortoise.fields.Field):

    def __init__(
        self,
        base_field: tortoise.fields.Field,
        min_length: typing.Optional[int] = None,
        max_length: typing.Optional[int] = None,
        null: bool = False,
        default=None,
    ):
        super().__init__()
        self.base_field = base_field
        self.min_length = min_length
        self.max_length = max_length
        self.null = null
        self.default = default

    @property
    def SQL_TYPE(self):  # noqa
        return self.base_field.SQL_TYPE + f'[{self.max_length or ""}]'

    def to_db_value(self, value: list, instance: typing.Type[tortoise.models.Model]) -> list | None:
        if value is None:
            return
        if self.min_length is not None and not self.null:
            if len(value) < self.min_length:
                raise ValueError
        value = [self.base_field.to_db_value(v, instance) for v in value]
        return value

    def to_python_value(self, value: list) -> list | None:
        if value is None:
            return
        value = [self.base_field.to_python_value(v) for v in value]
        return value


class CharArrayField(tortoise.fields.Field):
    SQL_TYPE = 'varchar[]'

    def __init__(self, max_length: typing.Optional[int] = None,
                 null: bool = False,
                 default=None
                 ) -> None:
        super().__init__()
        self.max_length = max_length
        self.null = null
        self.default = default

    def to_db_value(self, value: list,
                    instance: typing.Type[tortoise.models.Model]) -> list:
        if self.max_length is not None and not self.null:
            if len(value) > self.max_length:
                raise ValueError

        return value

    def to_python_value(self, value: list) -> list:
        return value


class CharArrayEnumField(CharArrayField):
    pass
