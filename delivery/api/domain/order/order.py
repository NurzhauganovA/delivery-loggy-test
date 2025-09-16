from transitions import Machine, MachineError

from .delivery_graph import DeliveryGraph
from .exceptions import OrderTransitionError, OrderValidationError


class Order:
    def __init__(self, delivery_graph: DeliveryGraph, initial_status: str):
        if not initial_status:
            raise OrderValidationError("initial_status is required")

        if not delivery_graph:
            raise OrderValidationError("delivery_graph is required")

        self.__state_machine: Machine = Machine(
            states=delivery_graph.get_statuses(),
            transitions=delivery_graph.get_transitions(),
            initial=initial_status,
        )

    @property
    def status(self) -> str:
        return self.__state_machine.state

    def transition_to(self, next_status: str) -> None:
        try:
            self.__state_machine.trigger(next_status)
        except MachineError as e:
            raise OrderTransitionError(f"Not allow transition from {self.status} to {next_status}") from e
        except AttributeError as e:
            raise OrderTransitionError(f"No transitions from {self.status}") from e
