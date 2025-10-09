import collections

import asyncpg
import fastapi
import pydantic
import stringcase

from starlette.middleware.base import BaseHTTPMiddleware

from fastapi.staticfiles import StaticFiles

from fastapi_pagination import add_pagination
from starlette.middleware.cors import CORSMiddleware
from tortoise import exceptions as tortoise_exceptions

from api import(
    exceptions,
    database,
    executors,
    models,
    monitoring,
    redis_module,
    services,
    v1,
    v2,
    responses,
)
from api.conf import conf
from api.context_vars import locale_context
from api.dependencies.clients import (
    aclose_pos_terminal_client,
    aclose_freedom_bank_otp_client,
    pos_terminal_otp,
)
from api.business_exceptions.base import BaseBuisnessException

from api.middlewares import(
    LogMiddleware,
)


app = fastapi.FastAPI(
    title='Globerce delivery API service',
    openapi_url='/api/v1/openapi.json' if conf.api.debug else '',
    swagger_ui_parameters={
        'docExpansion': None,
        'jsonEditor': True,
        'operationsSorter': 'alpha',
        'tagsSorter': 'alpha',
        'defaultModelsExpandDepth': -1,
        'deepLinking': True,
        'persistAuthorization': True,
        'displayOperationId': False,
        'displayRequestDuration': True,
        'tryItOutEnabled': True,
    },
)


app.mount(
    conf.media.url,
    StaticFiles(directory=conf.media.root),
    name='media',
)

app.mount(
    conf.static.url,
    StaticFiles(directory=conf.static.root),
    name='static',
)


@app.get("/api/v1/service/android", response_model=dict, tags=["service_status"])
async def android_check():
    return await models.get_last_android_version()


@app.get("/api/v1/service/health", response_model=dict, tags=["service_status"])
async def health_check():
    return {}


app.include_router(v1.api_router, prefix='/api')
app.include_router(v2.api_router, prefix='/api')


app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["X-Result", ]
)
app.add_middleware(LogMiddleware)


@app.middleware('http')
def add_context_vars_middleware(request: fastapi.Request, call_next):
    locale_context.set(
        request.headers.get(
            conf.api.locale.header_name, conf.api.locale.default_locale
        )
    )
    request.state.locale = conf.api.locale.default_locale
    return call_next(request)


@app.get('/', include_in_schema=False)
async def redirect_to_api_docs():
    return fastapi.responses.RedirectResponse(url=app.docs_url)


@app.on_event('startup')
async def startup():
    executors.executors_setup()
    monitoring.initialize()

    await database.initialize()
    await redis_module.connect(conf.redis.uri)


@app.on_event('shutdown')
async def shutdown():
    executors.executors_shutdown()

    await database.close_connections()
    await monitoring.shutdown()
    await redis_module.disconnect()
    await services.terminate_services()
    await aclose_freedom_bank_otp_client()
    await aclose_pos_terminal_client()
    await pos_terminal_otp.aclose()


@app.exception_handler(pydantic.ValidationError)
@app.exception_handler(exceptions.PydanticException)
async def query_params_validation_error_handler(
    request: fastapi.Request,
    exc: pydantic.ValidationError,
) -> fastapi.responses.Response:
    """
    Обрабатываются исключения валидации
        Кастомный чек PydanticException (легаси)
        Чеки Pydantic
    """

    return fastapi.responses.JSONResponse(
        status_code=422,
        content={
            'detail': exc.errors(),
        },
    )


@app.exception_handler(tortoise_exceptions.BaseORMException)
@app.exception_handler(asyncpg.PostgresError)
async def database_exception_handler(
    request: fastapi.Request,
    exc: tortoise_exceptions.BaseORMException,
) -> fastapi.responses.Response:
    """
    Исключения от базы
        На уровне ORM
        На уровне конектора asyncpostgre
    """

    status_code = 400
    content = {
        'detail': str(exc),
        'status': 'bad-request',
        'status_code': status_code
    }
    if isinstance(exc, tortoise_exceptions.DoesNotExist):
        status_code = 404
        content['status'] = 'not-found'
        content['status_code'] = status_code
    return fastapi.responses.JSONResponse(
        status_code=status_code,
        content=content,
    )


@app.exception_handler(exceptions.HTTPException)
async def request_exception_handler(
    request: fastapi.Request,
    exc: exceptions.HTTPException,
) -> fastapi.responses.Response:
    """
    Все кастомные исключения от HTTP
    """

    return fastapi.responses.JSONResponse(
        status_code=exc.status_code,
        content={
            'detail': str(exc),
            'status': exc.status,
            'status_code': exc.status_code,
        },
    )


@app.exception_handler(BaseBuisnessException)
async def buisness_logic_exceptions(
    request: fastapi.Request,
    exc: BaseBuisnessException,
) -> fastapi.responses.Response:
    """
    Исключения бизнес логики
    """

    return fastapi.responses.JSONResponse(
        status_code=exc.status_code,
        content={
            'detail': str(exc),
            'status': exc.status,
            'status_code': exc.status_code,
        }
    )


@app.exception_handler(Exception)
async def other_exceptions(
    request: fastapi.Request,
    exc: Exception
) -> fastapi.responses.Response:
    """
    Все остальные, необработанные исключения
    """

    return fastapi.responses.JSONResponse(
        status_code=500,
        content={
            'detail': str(exc),
            'status': responses.InternalErrorStatus.INTERNAL_ERROR,
            'status_code': 500,
        },
    )


def enrich_openapi_schema(application: fastapi.FastAPI):
    operation_ids = []
    for route in application.routes:
        if isinstance(route, fastapi.routing.APIRoute):
            route.operation_id = stringcase.camelcase(route.name)
            operation_ids.append(route.operation_id)

    non_unique_operation_ids = [
        oid
        for oid, count in collections.Counter(operation_ids).items()
        if count > 1
    ]
    if non_unique_operation_ids:
        raise Exception(
            'Non-unique endpoint operation IDs '
            f'found: {non_unique_operation_ids}',
        )


enrich_openapi_schema(app)
add_pagination(app)
