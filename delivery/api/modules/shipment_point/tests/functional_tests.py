import pytest

from api import auth
from ..v1 import router


@pytest.mark.asyncio
@pytest.mark.parametrize(
    (
        'view_name',
        'method',
        'query_params',
        'payload_path',
        'expected_response_code',
        'expected_response_path',
    ),
    (
        (
            'shipment_point_get_list',
            'get',
            {},
            None,
            200,
            'data-fixtures/shipment-point-list-response.json',
        ),
        (
            'shipment_point_get',
            'get',
            {"shipment_point_id": 1},
            None,
            200,
            'data-fixtures/shipment-point-get-response.json'
        ),
        (
            'partner_shipment_point_create',
            'post',
            {},
            'data-fixtures/shipment-point-create-payload.json',
            201,
            None,
        ),
        (
            'partner_shipment_point_bulk_create',
            'post',
            {},
            'data-fixtures/shipment-point-bulk-create-payload.json',
            201,
            None,
        ),
        (
            'partner_shipment_point_partial_update',
            'patch',
            {'shipment_point_id': 1},
            'data-fixtures/shipment-point-partial-update-payload.json',
            201,
            None,
        ),
    ),
)
async def test_shipment_point_endpoints(
    view_name, method, query_params, payload_path, expected_response_code, expected_response_path,
    initialize_tests, json_data_by_path, shipment_point, current_service_manager, client,
) -> None:
    headers = {
        'HTTP_ACCEPT_LANGUAGE': 'ru',
        'Content-Type': 'application/json',
    }
    url = router.url_path_for(view_name, **query_params)
    app = client._transport.app
    app.dependency_overrides[auth.get_current_user] = lambda: current_service_manager
    params = {
        'headers': headers,
    }
    if payload_path:
        params['json'] = json_data_by_path(payload_path)
    response = await client.request(method, url, **params)
    assert response.status_code == expected_response_code, response.json()
    if expected_response_path is not None:
        expected_response = json_data_by_path(expected_response_path)
        assert response.json() == expected_response, response.json()
