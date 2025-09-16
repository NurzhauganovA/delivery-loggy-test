import math
from datetime import datetime

import numpy as np
import pytz
import tortoise

from loguru import logger

from .distribution_service import DistributionService, couriers_prepare, orders_prepare, get_stock_place_prepare
from ... import models, enums
from .utils import distribute_orders

ONE_DEGREE = math.pi / 180
TIMEZONE = pytz.timezone("Asia/Almaty")


def to_radians(degree: float) -> float:
    return ONE_DEGREE * float(degree)


def get_distance(
        lat_first: float,
        long_first: float,
        lat_second: float,
        long_second: float,
) -> int:
    if lat_first == lat_second and long_first == long_second:
        return 0
    # Convert from degree to radians
    lat_first = to_radians(lat_first)
    long_first = to_radians(long_first)

    lat_second = to_radians(lat_second)
    long_second = to_radians(long_second)

    dlat = lat_second - lat_first
    dlong = long_second - long_first

    sq_sin_dlat = pow(math.sin(dlat / 2), 2)
    sq_sin_dlong = pow(math.sin(dlong / 2), 2)
    to_root = sq_sin_dlat + math.cos(lat_first) * math.cos(
        lat_second) * sq_sin_dlong

    return int(2 * math.asin(math.sqrt(to_root)) * 6371000)


async def set_courier_to_order(orders, order_index, couriers, key_courier,
                               position_key):
    if not couriers:
        raise models.NotDistributionCouriersError('Not couriers for distribution')
    if not orders:
        raise models.NotDistributionOrdersError('Not orders for distribution')

    order_obj = orders[order_index]
    await order_obj.update_from_dict({
        'courier_id': couriers[key_courier].id,
        'position': position_key,
    }).save()

    order_statuses = await models.OrderStatuses.filter(order_id=order_obj.id)
    if len(order_statuses) == 1:
        if status := await models.Status.filter(
                partner_id__isnull=True,
                slug=enums.StatusSlug.COURIER_ASSIGNED.value,
        ).first():
            order_time = await order_obj.localtime
            await models.OrderStatuses.create(
                order_id=order_obj.id,
                status_id=status.id,
                created_at=order_time,
            )
            order_obj.current_status = status
            await order_obj.save()

    return order_obj


async def get_distance_matrix(orders):
    if not orders:
        raise models.NotDistributionOrdersError('Not orders for distribution')
    delivery_points = []
    shipment_points = []
    for order in orders:
        for address in await models.order_address_get_list(order.id):
            address = address.dict()
            if address['type'] == enums.AddressType.SHIPMENT_POINT:
                if not shipment_points:
                    shipment_points.append([address['place']['latitude'],
                                            address['place']['longitude']])

            if address['type'] == enums.AddressType.DELIVERY_POINT:
                delivery_points.append([address['place']['latitude'],
                                        address['place']['longitude']])
    if not shipment_points:
        shipment_points.append([43.26130, 76.92920])
    points = shipment_points + delivery_points
    length = len(points)
    distances = np.zeros(shape=(length, length), dtype=np.long)

    for i in range(length):
        for j in range(length):
            dist = get_distance(
                points[i][0],
                points[i][1],
                points[j][0],
                points[j][1],
            )
            distances[i][j] = dist
    return distances.tolist()


async def get_courier_info(couriers):
    if not couriers:
        raise models.NotDistributionCouriersError('Not couriers for distribution')
    couriers_info_list = []
    speed = 30.000000000
    dist_limit = 1000000000
    start_time = datetime.now().replace(hour=9, minute=1).astimezone(TIMEZONE)
    finish_time = datetime.now().replace(hour=20, minute=1).astimezone(TIMEZONE)
    for _ in couriers:
        couriers_info_list.append([
            speed,
            dist_limit,
            int(int(datetime.timestamp(start_time)) / 60),
            int(int(datetime.timestamp(finish_time)) / 60)
        ])

    return couriers_info_list


async def get_can_delivery(orders, couriers):
    can_delivery = []
    for _ in couriers:
        courier_can_delivery = [1]
        for _ in orders:
            courier_can_delivery.append(1)
        can_delivery.append(courier_can_delivery)

    return can_delivery


async def get_order_info(orders):
    orders_info_list = []
    priority = 1
    for key, order in enumerate(orders):
        localized_delivery_datetime = order.delivery_datetime.replace(
            tzinfo=pytz.utc
        ).astimezone(TIMEZONE)
        time_r = int(datetime.timestamp(localized_delivery_datetime)) // 60
        time_l = time_r - 30
        orders_info_list.append(
            [
                int(time_l),
                int(time_r),
                priority,
                0 if key == 0 else -1
            ],
        )

    return orders_info_list


async def check_orders(orders):
    for key, order in enumerate(orders):
        for address in await models.order_address_get_list(order.id):
            address = address.dict()
            if not address['place']['latitude'] or not address['place']['longitude']:
                orders.pop(key)

async def run_algo(orders, couriers) -> dict:
    await check_orders(orders)
    distance_matrix = await get_distance_matrix(orders[-15:])
    # logger.info(distance_matrix)
    couriers_info = await get_courier_info(couriers[:4])
    # logger.info(couriers_info)
    orders_info = await get_order_info(orders[-15:])
    # logger.info(orders_info)
    can_delivery = await get_can_delivery(orders[-15:], couriers[:4])
    # logger.info(can_delivery)
    # resp_json = distribute_orders(
    #     0,
    #     len(orders),
    #     len(couriers),
    #     distance_matrix,
    #     couriers_info,
    #     orders_info,
    #     can_delivery,
    # )
    # print(resp_json, 1)
    service = DistributionService()
    result = await service.distribute(dict(
        {
            "is_cycle": 0,
            "orders_amount": len(orders[:15]),
            "couriers_amount": len(couriers[:4]),
            "distance_matrix": distance_matrix,
            "couriers_info": couriers_info,
            "orders_info": orders_info,
            "can_delivery_info": can_delivery,
        }
    ))

    return result


async def order_distribution(orders: list, couriers: list, algo_result: dict = None) -> None:
    if len(orders) == 1:
        await set_courier_to_order(
            orders, 0, couriers, 0, 0,
        )
        return

    if not algo_result:
        algo_result = await run_algo(orders, couriers)
    for key_courier, result in enumerate(algo_result.get('couriers')):
        path = result.get('path')
        path.pop(0)

        for position, order_index in enumerate(path):
            try:
                await set_courier_to_order(
                    orders=orders,
                    order_index=order_index - 1,
                    couriers=couriers,
                    key_courier=key_courier,
                    position_key=position,
                )
            except IndexError as e:
                logger.info(e)
