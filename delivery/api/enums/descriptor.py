import enum
import typing


Descriptor = typing.TypeVar('Descriptor')


class Descriptor(str, enum.Enum):

    def __str__(self) -> str:
        return str(self.value)

    @classmethod
    def describe(cls) -> str:
        pairs = []
        for key, value in cls.__members__.items():
            pairs.append(f'{key}: {value}')

        return ', '.join(pairs)

    @classmethod
    def to_kwargs(
        cls,
        null: bool = False,
        default: Descriptor | None = None,
    ) -> dict:
        """
        Used to pass as kwargs to CharEnumField of tortoise ORM.
        """
        return {
            'enum_type': cls,
            'description': cls.describe(),
            'default': default,
            'null': null,
        }


__all__ = (
    'Descriptor',
)
