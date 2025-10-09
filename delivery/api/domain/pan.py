from typing import List

from pydantic import (
    BaseModel,
    constr,
)


class Pan(BaseModel):
    value: constr(min_length=16, max_length=16)

    class Config:
        frozen = True

    def get_suffix(self) -> str:
        return self.value[-4:]

    def get_masked(self) -> str:
        return self.value[:4] + '*' * 8 + self.value[-4:]

    def is_matched_by_any_mask(self, masks: List[str]) -> bool:
        """
            Метод проверяет, входит ли хоть одна маска в значение "Номер карты".
            Если хоть одна маска входит в значение, вернется True. Иначе False.

            Args:
                masks: массив масок для валидации значения "Номер карты"

            Returns:
                флаг, вошла ли хоть одна маска в значение "Номер карты"
        """
        return any(self.value.startswith(mask) for mask in masks)
