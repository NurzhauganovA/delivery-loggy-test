from typing import Optional, List, Dict

from .exceptions import DeliveryGraphValidationError
from pydantic import BaseModel, ValidationError


class Transition(BaseModel):
    source: str
    dest: str
    trigger: str


class DeliveryGraphStep(BaseModel):
    # Точно нужны
    status: str
    transitions: List[Transition] = []

    # Есть сомнения об необходимости этих полей
    id: int
    icon: str
    slug: str
    name_en: str
    name_ru: str
    position: Optional[int] = None
    button_name: Optional[str] = None


class DeliveryGraph(list):
    def __init__(self, items: List[Dict]):
        try:
            steps = [DeliveryGraphStep.parse_obj(item) for item in items]
        except ValidationError as e:
            raise DeliveryGraphValidationError(str(e)) from e

        super().__init__(steps)

    def get_statuses(self) -> [str]:
        return [state.status for state in self if state.status]

    def get_transitions(self) -> [dict]:
        return [transition.dict() for state in self for transition in state.transitions]
