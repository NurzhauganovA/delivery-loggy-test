import datetime

import fastapi
from fastapi import Depends, Body
from fastapi import Security
from loguru import logger
from tortoise import Tortoise
from tortoise.expressions import Q
from tortoise.query_utils import Prefetch

from api import exceptions
from api.dependencies.partners_ids import (
    get_freedom_bank_partner_id,
    get_pos_terminal_partner_id,
)
from .. import auth
from .. import models
from .. import schemas
from ..domain.pan import Pan
from ..enums import AddressType, OrderStatus, ProductType, PostControlType
from ..enums import OrderDeliveryStatus
from ..enums import OrderSearchType
from ..enums import OrderType
from ..enums import PostControlResolution
from ..enums import ProfileType
from ..enums import StatusSlug
from ..modules.delivery_point import DeliveryPointRepository
from ..modules.shipment_point import PartnerShipmentPoint


class OrderDefaultFilter:
    def __init__(self, prefix: str = ''):
        self.prefix = prefix

    async def __call__(
        self,
        current_user: schemas.UserCurrent = Security(auth.get_current_user),
    ):
        px = self.prefix
        profile = current_user.profile
        profile_type = profile['profile_type']
        profile_content = profile['profile_content']
        args = []
        if current_user.is_superuser:
            return args
        match profile_type:
            case ProfileType.SERVICE_MANAGER:
                shipment_points = await PartnerShipmentPoint.filter(
                    partner_id=profile_content['partner_id'],
                ).values_list('latitude', 'longitude')
                shipment_point_latitudes = [point[0] for point in shipment_points]
                shipment_point_longitudes = [point[1] for point in shipment_points]
                args.append(
                    Q(
                        Q(
                            **{f'{px}partner_id__in': current_user.partners},
                            **{f'{px}type__not': OrderType.PICKUP.value}
                        ),
                        Q(
                            **{f'{px}address_set__type': AddressType.SHIPMENT_POINT.value},
                            **{f'{px}address_set__place__latitude__in': shipment_point_latitudes},
                            **{f'{px}address_set__place__longitude__in': shipment_point_longitudes},
                            **{f'{px}type': OrderType.PICKUP.value},
                        ),
                        join_type=Q.OR,
                    ) &
                    Q(
                        Q(
                            **{f'{px}idn__isnull': True},
                        ),
                        Q(
                            **{f'{px}idn__isnull': False},
                            **{f'{px}current_status_id__not': int(OrderStatus.NEW.value)},
                        ),
                        join_type=Q.OR,
                    )
                )
            case ProfileType.BRANCH_MANAGER:
                cities = [item.id for item in profile_content['cities']]
                shipment_points = await PartnerShipmentPoint.filter(
                    partner_id=profile_content['partner_id'],
                    city_id__in=cities,
                ).values_list('latitude', 'longitude')
                shipment_point_latitudes = [point[0] for point in shipment_points]
                shipment_point_longitudes = [point[1] for point in shipment_points]
                args.append(
                    Q(
                        Q(
                            **{f'{px}partner_id__in': current_user.partners},
                            **{f'{px}city_id__in': cities},
                            **{f'{px}type__not': OrderType.PICKUP.value},
                        ),
                        Q(
                            **{f'{px}address_set__type': AddressType.SHIPMENT_POINT.value},
                            **{f'{px}address_set__place__latitude__in': shipment_point_latitudes},
                            **{f'{px}address_set__place__longitude__in': shipment_point_longitudes},
                            **{f'{px}type': OrderType.PICKUP.value},
                        ),
                        join_type=Q.OR,
                    ) &
                    Q(
                        Q(
                            **{f'{px}idn__isnull': True},
                        ),
                        Q(
                            **{f'{px}idn__isnull': False},
                            **{f'{px}current_status_id__not': int(OrderStatus.NEW.value)},
                        ),
                        join_type=Q.OR,
                    )
                )
            case ProfileType.DISPATCHER:
                args.append(
                    Q(
                        **{f'{px}partner_id__in': current_user.partners},
                        **{f'{px}type__not': OrderType.PICKUP.value},
                    ) &
                    Q(
                        Q(
                            **{f'{px}idn__isnull': True},
                        ),
                        Q(
                            **{f'{px}idn__isnull': False},
                            **{f'{px}current_status_id__not': int(OrderStatus.NEW.value)},
                        ),
                        join_type=Q.OR,
                    )
                )
            case ProfileType.COURIER:
                args.append(
                    Q(**{f'{px}courier_id': profile['id']})
                )
            case ProfileType.MANAGER:
                args.append(
                    Q(
                        **{f'{px}partner_id': profile_content['partner_id']}
                    ) &
                    Q(
                        Q(
                            **{f'{px}idn__isnull': True},
                        ),
                        Q(
                            **{f'{px}idn__isnull': False},
                            **{f'{px}current_status_id__not': int(OrderStatus.NEW.value)},
                        ),
                        join_type=Q.OR,
                    )
                )
            case ProfileType.BANK_MANAGER:
                args.append(
                    Q(
                        **{f'{px}partner_id': profile_content['partner_id']},
                        **{f'{px}idn__isnull': False},
                    )
                )
            case ProfileType.PARTNER_BRANCH_MANAGER:
                args.append(
                    Q(
                        **{f'{px}type': OrderType.PICKUP.value},
                        **{f'{px}partner_id': profile_content['partner_id']},
                        **{f'{px}idn__isnull': True},
                    )
                )
            case ProfileType.SORTER:
                args.append(
                    Q(
                        **{f'{px}partner_id__in': current_user.partners},
                        **{f'{px}has_ready_for_shipment': True},
                        **{f'{px}idn__isnull': True},
                    )
                )
            case ProfileType.SUPERVISOR:
                args.append(
                    Q(
                        **{f'{px}partner_id__in': current_user.partners},
                        **{f'{px}city__country_id': profile_content['country_id']},
                    )
                )
            case ProfileType.LOGIST:
                args.append(
                    Q(
                        **{f'{px}partner_id__in': current_user.partners},
                        **{f'{px}city__country_id': profile_content['country_id']},
                    )
                )
            case ProfileType.CALL_CENTER_MANAGER:
                args.append(
                    Q(
                        **{f'{px}partner_id__in': current_user.partners},
                        **{f'{px}city__country_id': profile_content['country_id']},
                    )
                )
            case ProfileType.GENERAL_CALL_CENTER_MANAGER:
                args.append(
                    Q(
                        **{f'{px}partner_id__in': current_user.partners},
                    )
                )
            case ProfileType.SUPPORT:
                args.append(
                    Q(
                        **{f'{px}partner_id__in': current_user.partners},
                    )
                )
            case _:
                args.append(Q(**{f'{px}id': 999_999_999}))

        return args


class OrderDefaultFilterV2:
    def __init__(self, prefix: str = ''):
        self.prefix = prefix

    async def __call__(
        self,
        current_user: schemas.UserCurrent = Security(auth.get_current_user),
    ):
        px = self.prefix
        profile = current_user.profile
        profile_type = profile['profile_type']
        profile_content = profile['profile_content']
        args = []
        if current_user.is_superuser:
            return args
        match profile_type:
            case ProfileType.SERVICE_MANAGER:
                shipment_points = await PartnerShipmentPoint.filter(
                    partner_id=profile_content['partner_id'],
                ).values_list('id', flat=True)
                args.append(
                    Q(
                        Q(
                            **{f'{px}partner_id__in': current_user.partners},
                            **{f'{px}type__not': OrderType.PICKUP.value}),
                        Q(
                            **{f'{px}shipment_point_id__in': shipment_points},
                            **{f'{px}type': OrderType.PICKUP.value},
                        ),
                        join_type=Q.OR,
                    ) &
                    Q(
                        Q(
                            **{f'{px}idn__isnull': True},
                        ),
                        Q(
                            **{f'{px}idn__isnull': False},
                            **{f'{px}current_status_id__not': int(OrderStatus.NEW.value)},
                        ),
                        join_type=Q.OR,
                    )
                )
            case ProfileType.BRANCH_MANAGER:
                cities = [item.id for item in profile_content['cities']]
                shipment_points = await PartnerShipmentPoint.filter(
                    partner_id=profile_content['partner_id'],
                    city_id__in=cities,
                ).values_list('id', flat=True)
                args.append(
                    Q(
                        Q(
                            **{f'{px}partner_id__in': current_user.partners},
                            **{f'{px}city_id__in': cities},
                            **{f'{px}type__not': OrderType.PICKUP.value},
                        ),
                        Q(
                            **{f'{px}address_set__type': AddressType.SHIPMENT_POINT.value},
                            **{f'{px}shipment_point_id__in': shipment_points},
                            **{f'{px}type': OrderType.PICKUP.value},
                        ),
                        join_type=Q.OR,
                    ) &
                    Q(
                        Q(
                            **{f'{px}idn__isnull': True},
                        ),
                        Q(
                            **{f'{px}idn__isnull': False},
                            **{f'{px}current_status_id__not': int(OrderStatus.NEW.value)},
                        ),
                        join_type=Q.OR,
                    )
                )
            case ProfileType.DISPATCHER:
                args.append(
                    Q(
                        **{f'{px}partner_id__in': current_user.partners},
                        **{f'{px}type__not': OrderType.PICKUP.value},
                    ) &
                    Q(
                        Q(
                            **{f'{px}idn__isnull': True},
                        ),
                        Q(
                            **{f'{px}idn__isnull': False},
                            **{f'{px}current_status_id__not': int(OrderStatus.NEW.value)},
                        ),
                        join_type=Q.OR,
                    )
                )
            case ProfileType.COURIER:
                args.append(
                    Q(**{f'{px}courier_id': profile['id']})
                )
            case ProfileType.MANAGER:
                args.append(
                    Q(
                        **{f'{px}partner_id': profile_content['partner_id']}
                    ) &
                    Q(
                        Q(
                            **{f'{px}idn__isnull': True},
                        ),
                        Q(
                            **{f'{px}idn__isnull': False},
                            **{f'{px}current_status_id__not': int(OrderStatus.NEW.value)},
                        ),
                        join_type=Q.OR,
                    )
                )
            case ProfileType.BANK_MANAGER:
                args.append(
                    Q(
                        **{f'{px}partner_id': profile_content['partner_id']},
                        **{f'{px}idn__isnull': False},
                    )
                )
            case ProfileType.PARTNER_BRANCH_MANAGER:
                args.append(
                    Q(
                        **{f'{px}type': OrderType.PICKUP.value},
                        **{f'{px}partner_id': profile_content['partner_id']},
                        **{f'{px}idn__isnull': True},
                    )
                )
            case ProfileType.SORTER:
                args.append(
                    Q(
                        **{f'{px}partner_id__in': current_user.partners},
                        **{f'{px}has_ready_for_shipment': True},
                        **{f'{px}idn__isnull': True},
                    )
                )
            case ProfileType.SUPERVISOR:
                args.append(
                    Q(
                        **{f'{px}partner_id__in': current_user.partners},
                        **{f'{px}city__country_id': profile_content['country_id']},
                    )
                )
            case ProfileType.LOGIST:
                args.append(
                    Q(
                        **{f'{px}partner_id__in': current_user.partners},
                        **{f'{px}city__country_id': profile_content['country_id']},
                    )
                )
            case ProfileType.CALL_CENTER_MANAGER:
                args.append(
                    Q(
                        **{f'{px}partner_id__in': current_user.partners},
                        **{f'{px}city__country_id': profile_content['country_id']},
                    )
                )
            case ProfileType.GENERAL_CALL_CENTER_MANAGER:
                args.append(
                    Q(
                        **{f'{px}partner_id__in': current_user.partners},
                    )
                )
            case ProfileType.SUPPORT:
                args.append(
                    Q(
                        **{f'{px}partner_id__in': current_user.partners},
                    )
                )
            case _:
                args.append(Q(**{f'{px}id': 999_999_999}))

        return args


def order_revise_default_filters(
    current_user: schemas.UserCurrent = Security(auth.get_current_user),
):
    profile = current_user.profile
    profile_type = profile['profile_type']
    args = []
    if current_user.is_superuser:
        return args
    match profile_type:
        case ProfileType.COURIER:
            args.append(Q(order_group__courier_id=profile['id']))
        case _:
            args.append(Q(id=-1))
    return args


async def order_get_filter_args(
    filter_schema: schemas.OrderFilterParams = Depends(
        schemas.OrderFilterParams,
    ),
    user: schemas.UserCurrent = fastapi.Security(
        auth.get_current_user,
        scopes=['o:l'],
    ),
):
    return await order_get_filter_args_base(filter_schema, profile_type=user.profile['profile_type'])


async def order_get_filter_args_v2(
    filter_schema: schemas.OrderFilterParams = Depends(
        schemas.OrderFilterParamsV2,
    ),
    user: schemas.UserCurrent = fastapi.Security(
        auth.get_current_user,
        scopes=['o:l'],
    ),
):
    return await order_get_filter_args_base(filter_schema, profile_type=user.profile['profile_type'])


async def order_get_filter_args_base(
    filter_schema,
    profile_type: ProfileType = None,
):
    filter_params = filter_schema.dict(exclude_unset=True, exclude_none=True)
    args = []
    if delivery_status := filter_params.pop('delivery_status', set()):
        if 'null' in delivery_status:
            delivery_status.remove('null')
            args.append(Q(delivery_status__filter={'status__isnull': True}))
        if delivery_status:
            if OrderDeliveryStatus.IS_DELIVERED in delivery_status:
                if profile_type == ProfileType.COURIER:
                    delivery_status.add(OrderDeliveryStatus.BEING_FINALIZED_AT_CS.value)
                    args.append(
                        Q(delivery_status__filter={'status__in': tuple(delivery_status)}) |
                        Q(
                            current_status_id__in=[
                                int(OrderStatus.POST_CONTROL_BANK.value),
                                int(OrderStatus.ENDED.value),
                            ],
                        )
                    )
                else:
                    args.append(Q(delivery_status__filter={'status__in': tuple(delivery_status)}))
            if OrderDeliveryStatus.BEING_FINALIZED in delivery_status:
                delivery_status.add(OrderDeliveryStatus.BEING_FINALIZED_ON_CANCEL.value)
                args.append(Q(delivery_status__filter={'status__in': tuple(delivery_status)}))
            else:
                args.append(Q(delivery_status__filter={'status__in': tuple(delivery_status)}))

    args.append(Q(archived=filter_params.pop('archived', False)))

    if exclude_order_status_ids := filter_params.pop('exclude_order_status_ids', []):
        if profile_type == ProfileType.COURIER:
            exclude_order_status_ids.append(34)

        filter_params['current_status__id__not_in'] = exclude_order_status_ids
    if current_status_slug := filter_params.pop('current_status_slug', []):
        filter_params['current_status__slug'] = current_status_slug
    if current_status_slug__in := filter_params.pop('current_status_slug__in', []):
        filter_params['current_status__slug__in'] = current_status_slug__in

    status_criteria = (
        'current_status', 'current_status__in', 'current_status__slug', 'current_status__slug__in',
    )

    if any([status in filter_params for status in status_criteria]):
        delivery_status_slugs = (
            OrderDeliveryStatus.CANCELLED.value,
            OrderDeliveryStatus.POSTPONED.value,
            OrderDeliveryStatus.NONCALL.value,
            OrderDeliveryStatus.BEING_FINALIZED.value,
        )
        args.append(
            Q(
                ~Q(delivery_status__filter={'status__in': delivery_status_slugs}),
                Q(delivery_status__filter={'status__isnull': True}),
                join_type=Q.OR,
            )
        )

    search_params = filter_params.pop('search', None)
    search_type = filter_params.pop('search_type', None)
    if search_params and search_type:
        match search_type:
            case OrderSearchType.ID:
                try:
                    int(search_params)
                except ValueError:
                    search_params = 0
                args.append(
                    Q(id=search_params),
                )
            case OrderSearchType.PHONE:
                search_params = search_params.replace(' ', '').replace('-', '')
                search_params = search_params[0:models.Order._meta.fields_map['receiver_phone_number'].max_length]
                args.append(
                    Q(receiver_phone_number=search_params),
                )
            case OrderSearchType.IIN:
                search_params = search_params.replace(' ', '').replace('-', '')
                search_params = search_params[0:models.Order._meta.fields_map['receiver_iin'].max_length]
                args.append(
                    Q(receiver_iin=search_params)
                )
            case OrderSearchType.FULL_NAME:
                args.append(
                    Q(receiver_name__icontains=search_params)
                )
            case OrderSearchType.CARD_NUMBER:
                args.append(
                    Q(product__pan_suffix=search_params)
                )

    for k, v in filter_params.items():
        args.append(Q(**{k: v}))

    return args


async def external_order_default_filter_args(
    current_partner: schemas.PartnerGet = Security(
        auth.get_current_partner,
    ),
):
    args = [Q(partner_id=current_partner.id)]
    return args


async def order_validate_create_payload(
    order: schemas.OrderCreate,
    user: schemas.UserCurrent = Security(auth.get_current_user),
):
    profile_type = user.profile['profile_type']
    profile = user.profile['profile_content']
    errors = []
    partner_does_not_exist = ('partner_id', 'Partner does not exist')
    city_does_not_exist = ('city_id', 'City does not exist')
    if user.is_superuser:
        return order
    match profile_type:
        case ProfileType.SERVICE_MANAGER:
            if order.partner_id not in user.partners:
                errors.append(partner_does_not_exist)
        case ProfileType.DISPATCHER:
            dispatcher_partners = (p.id for p in profile['partners'])
            if order.partner_id not in dispatcher_partners:
                errors.append(partner_does_not_exist)
        case ProfileType.BRANCH_MANAGER:
            if order.partner_id not in user.partners:
                errors.append(partner_does_not_exist)
            if city_id := order.city_id:
                cities = (item.id for item in profile['cities'])
                if city_id not in cities:
                    errors.append(city_does_not_exist)
        case ProfileType.MANAGER:
            if order.partner_id != profile['partner_id']:
                errors.append(partner_does_not_exist)
        case ProfileType.BANK_MANAGER:
            if order.partner_id != profile['partner_id']:
                errors.append(partner_does_not_exist)
        case ProfileType.PARTNER_BRANCH_MANAGER:
            if order.partner_id != profile['partner_id']:
                errors.append(partner_does_not_exist)
            sh_p = {
                'lat': profile['shipment_point'].latitude,
                'long': profile['shipment_point'].longitude,
            }
            if addresses := order.addresses:
                dp_repo = DeliveryPointRepository()
                d_points = await dp_repo.get_list(
                    [], id__in=[adr.place_id for adr in addresses])
                if not any(dp.latitude == sh_p['lat'] and dp.longitude == sh_p['long'] for dp in d_points):
                    errors.append(('addresses', 'Address does not exist'))
    if errors:
        raise exceptions.PydanticException(errors=errors)

    return order


async def order_validate_create_payload_v2(
    order: schemas.OrderCreateV2 = Body(embed=True),
    user: schemas.UserCurrent = Security(auth.get_current_user),
):
    profile_type = user.profile['profile_type']
    profile = user.profile['profile_content']
    errors = []
    partner_does_not_exist = ('partner_id', 'Partner does not exist')
    city_does_not_exist = ('city_id', 'City does not exist')
    if user.is_superuser:
        return order
    match profile_type:
        case ProfileType.SERVICE_MANAGER:
            if order.partner_id not in user.partners:
                errors.append(partner_does_not_exist)
        case ProfileType.DISPATCHER:
            dispatcher_partners = (p.id for p in profile['partners'])
            if order.partner_id not in dispatcher_partners:
                errors.append(partner_does_not_exist)
        case ProfileType.BRANCH_MANAGER:
            if order.partner_id not in user.partners:
                errors.append(partner_does_not_exist)
            if city_id := order.city_id:
                cities = (item.id for item in profile['cities'])
                if city_id not in cities:
                    errors.append(city_does_not_exist)
        case ProfileType.MANAGER:
            if order.partner_id != profile['partner_id']:
                errors.append(partner_does_not_exist)
        case ProfileType.BANK_MANAGER:
            if order.partner_id != profile['partner_id']:
                errors.append(partner_does_not_exist)
        case ProfileType.PARTNER_BRANCH_MANAGER:
            if order.partner_id != profile['partner_id']:
                errors.append(partner_does_not_exist)
            sh_p = {
                'lat': profile['shipment_point'].latitude,
                'long': profile['shipment_point'].longitude,
            }
    if errors:
        raise exceptions.PydanticException(errors=errors)

    return order


async def order_validate_pan(
    order_id: int,
    pan: schemas.OrderPAN,
):
    order = await models.Order.get(id=order_id)

    if not await models.PanValidationMask.filter(
        partner_id=order.partner_id,
        pan_mask__startswith=str(pan.pan)[:6]
    ).exists():
        raise exceptions.PydanticException(errors=[('pan', 'Pan is not valid')])

    # Проверим, был ли этот Номер карты уже привязан к текущей заявке
    current_product = await models.Product.get_or_none(order_id=order_id)
    if current_product and current_product.attributes.get('pan') == Pan(value=pan.pan).value:
        raise exceptions.PydanticException(errors=[('pan', 'already linked to this order')])

    # Проверим, был ли этот Номер карты уже привязан к другим заявкам
    conn = Tortoise.get_connection("default")
    result = await conn.execute_query_dict(
        """
            SELECT 1
            FROM public.product
            WHERE type = 'card'
            AND pan_suffix = $1
            AND attributes->>'pan' = $2
            AND order_id != $3
            LIMIT 1
        """,
        [
            Pan(value=pan.pan).get_suffix(),
            Pan(value=pan.pan).value,
            order_id,
        ]
    )
    if result:
        raise exceptions.PydanticException(errors=[('pan', 'already linked to another order')])

    return pan


async def get_courier_service_id(
    user: schemas.UserCurrent = Security(auth.get_current_user),
) -> int:
    partner_id = user.profile['profile_content']['partner_id']
    partner = await models.Partner.get(id=partner_id).only('courier_partner_id')
    courier_service_id = partner.courier_partner_id if partner.courier_partner_id else partner_id

    return courier_service_id


async def order_status_validate_payload(
    order_id: int,
    status_id: int,
    freedom_bank_partner_id: int = Depends(get_freedom_bank_partner_id),
    pos_terminal_partner_id: int = Depends(get_pos_terminal_partner_id),
) -> bool:
    order_obj = await models.Order.get(id=order_id).select_related('deliverygraph', 'item')
    graph = order_obj.deliverygraph.graph
    graph_statuses = tuple(g['slug'] for g in graph)
    status = await models.Status.get(id=status_id)

    status_not_belong_to_graph = 'This status does not belong to order deliverygraph'
    is_status_exist_in_graph = any(item['slug'] == status.slug for item in graph)
    if not is_status_exist_in_graph:
        raise exceptions.PydanticException(errors=[('status_id', status_not_belong_to_graph)])

    errors = []
    previous_step = 'Can not change to this status, please try previous step again'
    match status.slug:
        case StatusSlug.SMS_SENT:
            # Для Freedom Bank KZ и POS Terminal не нужно проверять ОТП
            if order_obj.partner_id not in (freedom_bank_partner_id, pos_terminal_partner_id):
                # TODO: Выглядит избыточным проверка ОТП, ведь статус SMS_SENT говорит сам за себя.
                otp_exists = await order_obj.otp_set.all().exists()
                if StatusSlug.SMS_SENT.value in graph_statuses and not otp_exists:
                    errors.append(('status_id', previous_step))
        case StatusSlug.SCAN_CARD:
            accepted_otp_exists = await order_obj.otp_set.filter(
                accepted_at__isnull=False,
            ).exists()
            if StatusSlug.SMS_SENT.value in graph_statuses and not accepted_otp_exists:
                errors.append(('status_id', previous_step))
        case StatusSlug.PHOTO_CAPTURING:
            if StatusSlug.SCAN_CARD.value in graph_statuses and not (await order_obj.product).type == ProductType.CARD.value:
                errors.append(('status_id', previous_step))
        case StatusSlug.POST_CONTROL:
            postcontrol_configs = await order_obj.item.postcontrol_config_set.filter(
                Q(parent_config_id__isnull=True, inner_param_set__isnull=True) | Q(parent_config_id__isnull=False),
                Q(type=PostControlType.POST_CONTROL.value),
            ).count()
            postcontrols = await order_obj.postcontrol_set.filter(
                type=PostControlType.POST_CONTROL.value,
            ).count()
            if postcontrol_configs != postcontrols:
                errors.append(('status_id', previous_step))
        case StatusSlug.DELIVERED:
            config_ids = await order_obj.item.postcontrol_config_set.filter(
                Q(parent_config_id__isnull=True, inner_param_set__isnull=True) | Q(parent_config_id__isnull=False),
                Q(type=PostControlType.POST_CONTROL.value),
            ).values_list('id', flat=True)
            if StatusSlug.POST_CONTROL_BANK in graph_statuses:
                if await order_obj.postcontrol_set.filter(
                    resolution=PostControlResolution.BANK_ACCEPTED,
                    config_id__in=config_ids,
                ).count() != len(config_ids):
                    errors.append(('status_id', previous_step))
            elif StatusSlug.POST_CONTROL in graph_statuses:
                if await order_obj.postcontrol_set.filter(
                    resolution__in=[PostControlResolution.ACCEPTED.value, PostControlResolution.BANK_ACCEPTED],
                    config_id__in=config_ids,
                ).count() != len(config_ids):
                    errors.append(('status_id', previous_step))
        case StatusSlug.ISSUED:
            if StatusSlug.POST_CONTROL in graph_statuses and (
                not await order_obj.postcontrol_set.filter(
                    type=PostControlType.POST_CONTROL.value,
                ).exists() or
                await order_obj.postcontrol_set.filter(
                    resolution__in=[PostControlResolution.PENDING.value, PostControlResolution.DECLINED.value],
                    type=PostControlType.POST_CONTROL.value,
                ).exists()
            ):
                errors.append(('status_id', previous_step))
    if errors:
        raise exceptions.PydanticException(errors=errors)

    return True


async def order_check_if_delivered(
    order_id: int,
):
    if await models.Order.filter(
        id=order_id,
        current_status__slug__in=[StatusSlug.ISSUED.value, StatusSlug.DELIVERED.value]
    ):
        raise exceptions.HTTPBadRequestException(
            'Already completed',
        )

    return order_id


async def order_check_for_cancel(
    order_id: int,
    reason: str = fastapi.Body(embed=True),
) -> int:
    order_obj = await models.Order.filter(
        id=order_id,
    ).select_related('current_status').first().prefetch_related(
        Prefetch('item__postcontrol_config_set', models.PostControlConfig.filter(
            parent_config_id__isnull=True,
            type=PostControlType.CANCELED.value,
        ).prefetch_related(
            Prefetch('inner_param_set', models.PostControlConfig.filter(
                type=PostControlType.CANCELED.value,
            ).prefetch_related(
                Prefetch(
                    'postcontrol_document_set',
                    models.PostControl.filter(order_id=order_id),
                    'postcontrol_documents',
                ),
            ), 'inner_params'),
            Prefetch(
                'postcontrol_document_set',
                models.PostControl.filter(order_id=order_id),
                'postcontrol_documents',
            ),
        ), 'postcontrol_cancellation_configs')
    )
    if order_obj is None:
        raise exceptions.HTTPBadRequestException(
            'Not found',
        )
    if order_obj.current_status.slug in (StatusSlug.ISSUED.value, StatusSlug.DELIVERED.value):
        raise exceptions.HTTPBadRequestException(
            'Already completed',
        )
    logger.debug(order_obj.delivery_status)
    try:
        if order_obj.delivery_status['status'] == OrderDeliveryStatus.CANCELLED.value:
            raise exceptions.HTTPBadRequestException(
                'Already cancelled',
            )
        if order_obj.delivery_status['status'] == OrderDeliveryStatus.REQUESTED_TO_CANCEL.value:
            raise exceptions.HTTPBadRequestException(
                'Already requested to cancel',
            )
    except KeyError:
        logger.debug(order_obj.id)
        logger.debug(order_obj.delivery_status)

    postcontrol_cancellation_configs = order_obj.item.postcontrol_cancellation_configs
    postcontrol_cancel_docs_exists = await models.PostControl.filter(
        order_id=order_id,
        type=PostControlType.CANCELED.value,
    ).exists()
    if reason.lower() == 'возврат по истечению срока':
        if postcontrol_cancellation_configs and not postcontrol_cancel_docs_exists:
            raise exceptions.HTTPBadRequestException(
                'At least one image is required',
            )
    else:
        if postcontrol_cancel_docs_exists:
            raise exceptions.HTTPBadRequestException(
                'Image is not allowed for this cancellation reason',
            )
    return order_id


async def order_check_for_accept_cancel(
    order_id: int,
) -> int:
    order_obj = await models.Order.filter(
        id=order_id,
    ).select_related('current_status').first().prefetch_related(
        Prefetch('item__postcontrol_config_set', models.PostControlConfig.filter(
            parent_config_id__isnull=True,
            type=PostControlType.CANCELED.value,
        ).prefetch_related(
            Prefetch('inner_param_set', models.PostControlConfig.filter(
                type=PostControlType.CANCELED.value,
            ).prefetch_related(
                Prefetch(
                    'postcontrol_document_set',
                    models.PostControl.filter(order_id=order_id),
                    'postcontrol_documents',
                ),
            ), 'inner_params'),
            Prefetch(
                'postcontrol_document_set',
                models.PostControl.filter(order_id=order_id),
                'postcontrol_documents',
            ),
        ), 'postcontrol_cancellation_configs')
    )
    if order_obj is None:
        raise exceptions.HTTPBadRequestException(
            'Not found',
        )
    if order_obj.current_status.slug in (StatusSlug.ISSUED.value, StatusSlug.DELIVERED.value):
        raise exceptions.HTTPBadRequestException(
            'Already completed',
        )
    if order_obj.delivery_status['status'] == OrderDeliveryStatus.CANCELLED.value:
        raise exceptions.HTTPBadRequestException(
            'Already cancelled',
        )

    postcontrol_cancellation_configs = order_obj.item.postcontrol_cancellation_configs
    postcontrol_cancel_docs_exists = await models.PostControl.filter(
        order_id=order_id,
        type=PostControlType.CANCELED.value,
    ).exists()
    reason = order_obj.delivery_status['reason']
    if reason.lower() == 'возврат по истечению срока':
        if postcontrol_cancellation_configs and not postcontrol_cancel_docs_exists:
            raise exceptions.HTTPBadRequestException(
                'At least one image is required',
            )
        if postcontrol_cancellation_configs and postcontrol_cancel_docs_exists:
            postcontrol_cancel_docs_nonaccepted_exists = await models.PostControl.filter(
                order_id=order_id,
                type=PostControlType.CANCELED.value,
                resolution__not=PostControlResolution.ACCEPTED.value,
            ).exists()
            if postcontrol_cancel_docs_nonaccepted_exists:
                raise exceptions.HTTPBadRequestException(
                    'Accept all post-control images',
                )
    else:
        if postcontrol_cancel_docs_exists:
            raise exceptions.HTTPBadRequestException(
                'Image is not allowed for this cancellation reason',
            )
    return order_id


async def order_check_for_resume(
    order_id: int,
):
    order_obj = await models.Order.filter(
        id=order_id,
    ).select_related('current_status').first()
    if order_obj is None:
        raise exceptions.HTTPBadRequestException(
            'Not found',
        )
    if order_obj.delivery_status['status'] == OrderDeliveryStatus.TO_CALL_POINT:
        raise exceptions.HTTPBadRequestException(
            'Already on the way',
        )
    if order_obj.delivery_status['status'] in (OrderDeliveryStatus.CANCELLED, OrderDeliveryStatus.CANCELED_AT_CLIENT):
        raise exceptions.HTTPBadRequestException(
            'Can not resume a cancelled order'
        )

    return order_id


async def validate_delivery_datetime_for_order_resume(
    order_id: int,
    new_delivery_datetime: datetime.datetime | None = fastapi.Body(None, embed=True),
):
    order_obj = await models.Order.filter(
        id=order_id,
    ).first()
    if order_obj is None:
        raise exceptions.HTTPBadRequestException(
            'Not found',
        )
    if order_obj.delivery_status['status'] == OrderDeliveryStatus.NONCALL:
        if new_delivery_datetime is None:
            raise exceptions.PydanticException(
                errors=(
                    ('delivery_datetime', 'field required'),
                ),
            )
        return new_delivery_datetime


async def order_validate_image_for_cancel_at_client(
    image: fastapi.UploadFile = fastapi.File(None),
    current_user: schemas.UserCurrent = fastapi.Security(auth.get_current_user),
):
    profile = current_user.profile
    if not profile:
        return image
    profile_type = profile['profile_type']
    if profile_type == ProfileType.COURIER and image is None:
        raise exceptions.PydanticException(
            errors=(
                ('image', 'field required'),
            )
        )
    return image
