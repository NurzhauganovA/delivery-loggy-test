import pytest

import api.schemas
from api import models
from ..infrastructure.db_table import DeliveryPoint


@pytest.fixture(scope='module')
async def user() -> models.User:
    return await models.User.create(
        **{
            'id': 1,
            'first_name': 'Test',
            'last_name': 'User',
            'phone_number': '+77071112233',
        }
    )


@pytest.fixture(scope='module')
async def service_manager(user: models.User, partner: models.Partner):
    return await models.ProfileServiceManager.create(
        **{
            'user_id': user.id,
            'partner_id': partner.id,
        }
    )


@pytest.fixture(scope='module')
async def current_service_manager(user: models.User, service_manager: models.ProfileServiceManager):
    user_as_dict = await models.user_get(id=user.id, with_history=False)
    user_with_profile = await models.get_user_profile_with_info(
        profile_type='service_manager',
        profile_id=service_manager.id,
        user=user_as_dict,
    )
    return api.schemas.UserCurrent(**user_with_profile)


@pytest.fixture(scope='module')
async def delivery_point(initialize_tests) -> DeliveryPoint:
    return await DeliveryPoint.create(
        **{
            'id': 1,
            'address': 'Address 1',
            'latitude': 72.12342,
            'longitude': 54.12312,
        }
    )


#
# @pytest.fixture(scope="module")
# async def country_1(initialize_tests):
#     return await models.Country(
#         **{
#             "id": 3,
#             "name": "12313"
#         }
#     )
