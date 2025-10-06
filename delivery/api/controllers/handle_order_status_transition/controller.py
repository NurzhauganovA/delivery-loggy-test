from typing import Optional, Dict
from fastapi import Depends

from tortoise.exceptions import DoesNotExist

from api import models, schemas
from api.domain.order import Order, DeliveryGraph
from api.enums import InitiatorType, HistoryModelName, RequestMethods, OrderStatusCodes
from .handler_protocol import OrderStatusTransitionHandlerProtocol
from .handlers.pos_terminal_registration.exceptions import BasePOSTerminalRegistrationHandlerError
from .exceptions import StatusHandlerExecutionError

OrderStatusTransitionHandlers = Dict[OrderStatusCodes, OrderStatusTransitionHandlerProtocol]


class OrderStatusTransitionController:
    def __init__(self, handlers: OrderStatusTransitionHandlers):
        self.__handlers = handlers

    async def transition_order_status(
        self,
        order_id: int,
        status_id: int,
        default_filter_args,
        user_id: int,
        user_profile: str,
        data: Optional[dict] = None,
    ) -> None:
        # Получаем заявку
        try:
            order_obj = await models.Order.filter(*default_filter_args).distinct().get(id=order_id)
        except DoesNotExist:
            raise DoesNotExist(f'Order with given ID: {order_id} was not found')

        # Получаем текущий и следующий статусы
        try:
            current_status = await models.Status.get(id=order_obj.current_status_id)
            next_status = await models.Status.get(id=status_id)
        except DoesNotExist:
            raise DoesNotExist(f'Status with given ID: {status_id} was not found')

        # Получаем деливери граф
        delivery_graph_obj = await order_obj.deliverygraph

        # Получаем модель деливери графа
        delivery_graph = DeliveryGraph(delivery_graph_obj.graph)

        # Получаем модель заявки
        order = Order(
            delivery_graph=delivery_graph,
            initial_status=current_status.code
        )

        # TODO: Временный костыль, нужна логика repeatable статусов в деливери графе и в доменной модели
        if next_status.code != 'pos_terminal_registration':
            # Пробуем передвинуть заявку в переданный статус
            order.transition_to(next_status.code)

        # Получим обработчик перехода на другой статус
        status_handler = self.__handlers.get(next_status.code)

        # Вызовем обработчик
        try:
            await status_handler.handle(
                order_obj=order_obj,
                status=next_status,
                data=data,
            )
        except BasePOSTerminalRegistrationHandlerError as e:
            raise StatusHandlerExecutionError(e) from e

        # Получим локальное время у заявки
        order_time = await order_obj.localtime

        # Получим локальное время у заявки
        order_time = await order_obj.localtime

        # Запишем в историю об изменении статуса
        await models.history_create(
            schemas.HistoryCreate(
                initiator_type=InitiatorType.USER,
                initiator_id=user_id,
                initiator_role=user_profile,
                model_type=HistoryModelName.ORDER,
                model_id=order_obj.id,
                request_method=RequestMethods.PUT,
                action_data={
                    'status_transition': {'from': current_status.code, 'to': next_status.code},
                },
                created_at=order_time,
            )
        )

        # TODO: Нужно перенести сохранение OrderStatuses в сами handlers, и покрыть это тестами
        # TODO: У статуса pos_terminal_registration добавляем запись о OrderStatus в самом обработчике
        if next_status.code != 'pos_terminal_registration':
            # Сохраним изменение статуса в историю статусов
            await models.OrderStatuses.create(order=order_obj, status=next_status, created_at=order_time)
