import pytest

from api.controllers.crm.cdek_auth import CDEKAuthController
from api.schemas.crm.cdek_auth import CDEKAuthRequest, CDEKAuthResponse


@pytest.mark.asyncio
async def test_get_order_product():
    request = CDEKAuthRequest(
        secret_key="123456"
    )

    product = await CDEKAuthController.authenticate(
        request
    )
    print("PRODUCT:", product)


@pytest.mark.asyncio
async def test_verify_access_token_cdek():
    token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJjZGVrIiwiY2xpZW50X3R5cGUiOiJjZGVrIiwiaWF0IjoxNzU5OTMxNTc3LCJleHAiOjE3NTk5MzE2MDd9.kToDr830O9noLg3ESHNoUUJyYlaYTTV9Wlq_ywaBjes"

    product = await CDEKAuthController.verify_token(
        token
    )
    print("PRODUCT:", product)