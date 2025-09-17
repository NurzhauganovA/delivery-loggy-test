import pytest
from freezegun import freeze_time

from tests.fixtures.client import client
from tests.fixtures.database import db, run_pre_start_sql_script
from tests.fixtures.images import img_png
from tests.fixtures.token import get_access_token_v1


@pytest.mark.asyncio
@freeze_time("2025-04-14T12:00:00Z")
async def test_attach_image_to_comment(
    client,
    credentials,
    profile_data,
    get_access_token_v1,
    db,
    pre_start_sql_script,
    run_pre_start_sql_script,
    img_png,
):
    """
        Прикрепить фото к комментарию.
    """
    await run_pre_start_sql_script(pre_start_sql_script)

    access_token = await get_access_token_v1(client, credentials, profile_data)

    order_id = 1
    comment_id = 1

    response = await client.post(
        url=f'/v2/order/{order_id}/comments/{comment_id}/images',
        headers={'Authorization': 'Bearer ' + access_token},
        files=[img_png],
    )
    assert response.status_code == 201
    assert response.json() == {'id': 1}



@pytest.mark.asyncio
@freeze_time("2025-04-14T12:00:00Z")
async def test_attach_image_to_non_existing_comment(
    client,
    credentials,
    profile_data,
    get_access_token_v1,
    db,
    pre_start_sql_script,
    run_pre_start_sql_script,
    img_png,
):
    """
        Прикрепить фото к несуществующему комментарию
    """
    await run_pre_start_sql_script(pre_start_sql_script)

    access_token = await get_access_token_v1(client, credentials, profile_data)

    order_id = 1
    comment_id = 100

    response = await client.post(
        url=f'/v2/order/{order_id}/comments/{comment_id}/images',
        headers={'Authorization': 'Bearer ' + access_token},
        files=[img_png],
    )
    assert response.status_code == 404
    assert response.json() == {'detail': 'Comment does not exist', 'status': 'not-found', 'status_code': 404}
