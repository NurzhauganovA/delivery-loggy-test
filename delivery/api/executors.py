import asyncio
import concurrent
import enum
import logging
import typing


logger = logging.getLogger(__name__)

_executors = None


class ExecutorType(enum.Enum):
    DEFAULT = 'default'


_executor_types = {
    ExecutorType.DEFAULT: concurrent.futures.ThreadPoolExecutor,
}

_executors_kwargs = {
    ExecutorType.DEFAULT: {},
}


def _executors_get(executor_type: ExecutorType) -> concurrent.futures.ThreadPoolExecutor:
    if executor_type not in ExecutorType.__members__.values():
        raise ValueError(f'Executor type {executor_type} does not exists')

    if executor_type not in _executors:
        executor = _executor_types[executor_type]
        executor_kwargs = _executors_kwargs[executor_type]
        _executors[executor_type] = executor(**executor_kwargs)

    return _executors[executor_type]


def _executors_submit_call(
    call: typing.Callable,
    executor_type: ExecutorType,
) -> asyncio.Future:
    if _executors is None:
        raise Exception(
            f'Executors were not initialized properly. '
            f'Called with call {call} for type {executor_type!r}',
        )

    executor = _executors_get(executor_type)
    if not executor:
        raise Exception(
            f'Executor for call {call} with type ',
            f'{executor_type!r} does not exist. Probably, it was shut down.',
        )

    loop = asyncio.get_running_loop()

    return loop.run_in_executor(executor, call)


def executors_setup():
    global _executors

    if _executors is None:
        _executors = {}


def executors_shutdown():
    global _executors

    if _executors is not None:
        for executor in _executors.values():
            if isinstance(executor, concurrent.futures.ThreadPoolExecutor):
                for thread in executor._threads:
                    try:
                        thread._tstate_lock.release()
                    except Exception as e:
                        logger.info(f'Unable to stop thread: {thread} due to {e!r}')

        _executors = None


async def executors_run(
    call: typing.Callable,
    executor_type: ExecutorType = ExecutorType.DEFAULT,
) -> typing.Any:
    return await _executors_submit_call(call, executor_type)
