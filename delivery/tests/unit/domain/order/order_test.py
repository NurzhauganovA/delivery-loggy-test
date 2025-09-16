import pytest

from api.domain.order import Order, OrderTransitionError, OrderValidationError, DeliveryGraph


def test_create_new_order(delivery_graph):
    """Проверяем первый status у созданной заявки"""
    order = Order(delivery_graph=delivery_graph, initial_status='new')
    assert order.status == 'new'


def test_create_new_order_empty_initial_status(delivery_graph):
    """Проверяем валидацию поля initial_status"""
    with pytest.raises(OrderValidationError, match="initial_status is required"):
        Order(delivery_graph=delivery_graph, initial_status='')


def test_create_new_order_empty_delivery_graph():
    """Проверяем валидацию поля delivery_graph"""
    with pytest.raises(OrderValidationError, match="delivery_graph is required"):
        Order(delivery_graph=DeliveryGraph([]), initial_status='new')


def test_create_in_way_order(delivery_graph):
    """Проверяем первый status у созданной заявки"""
    order = Order(delivery_graph=delivery_graph, initial_status='in_way')
    assert order.status == 'in_way'


def test_order_next_transitions_success(delivery_graph):
    """Проверяем успешные переходы на следующие статусы"""
    order = Order(delivery_graph=delivery_graph, initial_status='new')
    order.transition_to('courier_assigned')
    assert order.status == 'courier_assigned'

    order = Order(delivery_graph=delivery_graph, initial_status='new')
    order.transition_to('card_returned_to_bank')
    assert order.status == 'card_returned_to_bank'


def test_order_next_transition_failure(delivery_graph):
    """Проверяем невалидный переход на неправильный статус"""
    order = Order(delivery_graph=delivery_graph, initial_status='new')
    with pytest.raises(OrderTransitionError, match="Not allow transition from new to in_way"):
        order.transition_to('in_way')


def test_order_transition_from_final_status_failure(delivery_graph):
    """Проверяем невалидный переход из финального статуса, который не имеет переходов"""
    order = Order(delivery_graph=delivery_graph, initial_status='delivered')
    with pytest.raises(OrderTransitionError, match="Not allow transition from delivered to new"):
        order.transition_to('new')
