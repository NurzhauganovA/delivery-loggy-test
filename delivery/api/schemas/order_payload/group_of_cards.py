from typing import List

from pydantic import (
    BaseModel,
    constr,
    root_validator,
)

from api.domain.pan import Pan


class CardInGroup(BaseModel):
    id: int
    pan: constr(min_length=16, max_length=16)
    iin: constr(min_length=12, max_length=12)
    fio: constr(min_length=1, max_length=100)

    @root_validator()
    def mask_pan(cls, values):
        values['pan'] = Pan(value=values['pan']).get_masked()
        return values

class GroupOfCardsPayload(BaseModel):
    __root__: List[CardInGroup]
