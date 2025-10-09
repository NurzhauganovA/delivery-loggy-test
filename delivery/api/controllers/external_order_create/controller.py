from api import schemas, models, exceptions
from .check_duplicate_order import check_duplicate_partner_order
from .get_partner_id import get_partner_id
from .get_product_payload import get_product_payload
from .exceptions import ExternalOrderCreateDuplicateError


async def external_order_create(
    order: schemas.ExternalOrderCreate,
    api_key: str
) -> int:
    try:
        partner_id = await get_partner_id(api_key)

        # Пока что проверяем дубли по комбинации partner_order_id и partner_id
        if order.partner_order_id:
            await check_duplicate_partner_order(
                partner_order_id=order.partner_order_id,
                partner_id=partner_id,
            )

        product_payload = get_product_payload(
            product_type=order.product_type,
            payload=order.payload,
        )

        order_id = await models.external_order_create_v2(
            order=order,
            product_payload=product_payload,
            partner_id=partner_id,
        )

        return order_id

    except (
        models.EntityDoesNotExist,
        models.OrderEntitiesError,
        models.OrderReceiverIINNotProvided,
        models.NotDistributionOrdersError,
        models.InvalidPointCoords,
        models.PartnerNotFound,
        models.ProfileNotFound,
        models.OrderAlreadyHaveCourierError,
        models.OrderAddressNotFound,
        models.ItemNotFound,
        ExternalOrderCreateDuplicateError,
    ) as e:
        raise exceptions.HTTPBadRequestException(str(e)) from e

    except models.PublicApiTokenNotFound as e:
        raise exceptions.HTTPUnauthenticatedException(str(e)) from e


# TODO: Потом при необходимости вынести в самостоятельный контроллер
async def get_external_order(order_id: int) -> schemas.OrderGetV1:
    try:
        order = await models.get_external_order(
            order_id=order_id,
        )

        return order

    except (
        models.EntityDoesNotExist,
        models.OrderEntitiesError,
        models.OrderReceiverIINNotProvided,
        models.NotDistributionOrdersError,
        models.InvalidPointCoords,
        models.PartnerNotFound,
        models.ProfileNotFound,
        models.OrderAlreadyHaveCourierError,
        models.OrderAddressNotFound,
        models.ItemNotFound,
        ExternalOrderCreateDuplicateError,
    ) as e:
        raise exceptions.HTTPBadRequestException(str(e)) from e
