from typing import Any
from unittest.mock import Mock

import pytest
from httpx import HTTPError

from api.adapters.cdek import CDEKAdapter
from api.clients.cdek import CDEKClient


@pytest.fixture
async def client():
    class MockClient:
        async def get_location(self, latitude: float, longitude: float) -> Mock:
            mock = Mock()
            if latitude == 111:
                raise HTTPError("Just testing")
            else:
                mock.json.return_value = {
                    "code": 44,
                    "city_uuid": "01581370-81f3-4322-9a28-3418adfabd97",
                    "city": "Москва",
                    "fias_guid": "0c5b2444-70a0-4932-980c-b4dc0d3f02b5"
                }

            return mock

        async def create_order(self, request: Any) -> Mock:
            mock = Mock()
            if request.shipment_point == "111":
                raise HTTPError("Just testing")
            else:
                mock.json.return_value = {
                    "entity": {
                        "uuid": "549b1ab8-518c-42d0-a14f-57569e3e5d65"
                    },
                    "requests": [
                        {
                            "request_uuid": "a1cd3d9e-b70a-4b09-a3fd-d107b3e630c8",
                            "type": "CREATE",
                            "date_time": "2025-09-09T10:13:21+0000",
                            "state": "ACCEPTED"
                        }
                    ],
                    "related_entities": []
                }

            return mock

    return MockClient()

@pytest.fixture
def adapter(client: CDEKClient) -> CDEKAdapter:
    return CDEKAdapter(
        client=client,
    )
