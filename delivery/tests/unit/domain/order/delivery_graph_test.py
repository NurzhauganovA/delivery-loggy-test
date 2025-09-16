import pytest

from api.domain.order import DeliveryGraph, DeliveryGraphStep, DeliveryGraphValidationError


def test_create_delivery_graph(raw_delivery_graph: list[dict]):
    delivery_graph = DeliveryGraph(raw_delivery_graph)
    assert len(delivery_graph) == 9

    for item in delivery_graph:
        assert type(item) == DeliveryGraphStep


def test_create_delivery_graph_failure(raw_wrong_delivery_graph: list[dict]):
    with pytest.raises(DeliveryGraphValidationError):
        DeliveryGraph(raw_wrong_delivery_graph)


def test_get_states(raw_delivery_graph: list[dict]):
    delivery_graph = DeliveryGraph(raw_delivery_graph)
    assert delivery_graph.get_statuses() == [
        'new', 'courier_assigned', 'in_way',
        'send_otp', 'verify_otp', 'photo_capturing',
        'post_control', 'delivered', 'card_returned_to_bank',
    ]


def test_get_transitions(raw_delivery_graph: list[dict]):
    delivery_graph = DeliveryGraph(raw_delivery_graph)
    assert delivery_graph.get_transitions() == [
        {
            'source': 'new',
            'dest': 'courier_assigned',
            'trigger': 'courier_assigned'
        },
        {
            'source': 'new',
            'dest': 'card_returned_to_bank',
            'trigger': 'card_returned_to_bank'
        },
        {
            'source': 'courier_assigned',
            'dest': 'in_way',
            'trigger': 'in_way'
        },
        {
            'source': 'courier_assigned',
            'dest': 'card_returned_to_bank',
            'trigger': 'card_returned_to_bank'
        },
        {
            'source': 'in_way',
            'dest': 'send_otp',
            'trigger': 'send_otp'
        },
        {
            'source': 'in_way',
            'dest': 'card_returned_to_bank',
            'trigger': 'card_returned_to_bank'
        },
        {
            'source': 'send_otp',
            'dest': 'verify_otp',
            'trigger': 'verify_otp'
        },
        {
            'source': 'send_otp',
            'dest': 'card_returned_to_bank',
            'trigger': 'card_returned_to_bank'
        },
        {
            'source': 'verify_otp',
            'dest': 'photo_capturing',
            'trigger': 'photo_capturing'
        },
        {
            'source': 'verify_otp',
            'dest': 'card_returned_to_bank',
            'trigger': 'card_returned_to_bank'
        },
        {
            'source': 'photo_capturing',
            'dest': 'post_control',
            'trigger': 'post_control'
        },
        {
            'source': 'photo_capturing',
            'dest': 'card_returned_to_bank',
            'trigger': 'card_returned_to_bank'
        },
        {
            'source': 'post_control',
            'dest': 'delivered',
            'trigger': 'delivered'
        },
        {
            'source': 'post_control',
            'dest': 'card_returned_to_bank',
            'trigger': 'card_returned_to_bank'
        },
        {
            'source': 'card_returned_to_bank',
            'dest': 'new',
            'trigger': 'new'
        }
    ]