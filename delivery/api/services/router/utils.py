import subprocess
import multiprocessing
import pathlib

def parse_response(resp):
    '''
    couriers:
        path(arr)
        distance, violation, time
    total_violation max_distance total_distance
    '''
    decoded = resp.decode('utf-8').split("\n\n")

    couriers = decoded[:-1]
    overall = decoded[-1]

    couriers_result = []
    for raw_courier in couriers:
        c_path_raw, c_params_raw = raw_courier.split("\n")
        if c_path_raw[-1] == " ":
            c_path_raw = c_path_raw[:-1]
        c_path = [int(p) for p in c_path_raw.split(" ")]
        distance, violation, time = c_params_raw.split(" ")
        couriers_result.append({
            'path': c_path,
            'distance': int(distance),
            'violation': int(violation),
            'time': int(time)
        })
    # minimal_distance = int(minimal_distance)
    # path_arr = [int(p) for p in path_str.split(" ") if p != ""]
    total_violation, max_distance, total_distance = overall.split(" ")

    resp_json = {
        "total_violation": int(total_violation),
        "max_distance": float(max_distance),
        "total_distance": int(total_distance),
        "couriers": couriers_result
    }
    return resp_json


def serialize_matrix(matrix):
    result_string = ""
    for row in matrix:
        for element in row:
            result_string += str(element)
            result_string += ","
        result_string = result_string[:-1] + ";"
    return result_string[:-1]


def run_subprocess(queue, command):
    # Код для запуска процесса
    output = subprocess.check_output(command)
    queue.put(output)


def distribute_orders(is_cycle: int, orders_amount: int, couriers_amount: int,
                      distance_matrix: dict, couriers_info: dict,
                      orders_info: dict, can_delivery_info: dict
                      ) -> dict:
    """
    Distance matrix size is (orders_amount + 1)X(order_amount + 1),
    because first point is initial point
    """

    assert len(distance_matrix) == orders_amount + 1, 'Invalid distance matrix size'
    assert len(orders_info) == orders_amount, 'Invalid orders info size'
    assert len(couriers_info) == couriers_amount, 'Invalid couriers info size'
    assert len(can_delivery_info) == couriers_amount, 'Invalid can deliver info size'

    orders_info.insert(0, [0, 67108864, 0, 0, -1])
    queue = multiprocessing.Queue()
    process = multiprocessing.Process(target=run_subprocess, args=(queue, [
            '/usr/app/api/services/router/algo_src.executable',
            str(is_cycle), str(orders_amount), str(couriers_amount),
            serialize_matrix(distance_matrix), serialize_matrix(couriers_info),
            serialize_matrix(orders_info), serialize_matrix(can_delivery_info)
        ]))
    # Запускаем процесс
    process.start()

    # Ждем завершения процесса
    process.join()

    # Получаем результат из очереди
    resp = queue.get()
    resp_dict = parse_response(resp)
    return resp_dict
