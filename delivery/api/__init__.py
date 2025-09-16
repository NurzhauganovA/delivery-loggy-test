import collections
import re

import asyncpg
import fastapi
import fastapi.responses
import fastapi.staticfiles
import pydantic
import stringcase
from asyncpg import UniqueViolationError, ForeignKeyViolationError
from fastapi_pagination import add_pagination
from psycopg2 import OperationalError
from starlette.middleware.cors import CORSMiddleware
from tortoise.exceptions import BaseORMException
from tortoise.exceptions import DoesNotExist

from api.exceptions import PydanticException
# noinspection PyProtectedMember
# from translator._helpers import translate_error
# from translator.base import setup
# from translator.translator import Translator
from api import exceptions
from . import common
from . import database
from . import enums
from . import executors
from . import helpers
from . import middlewares
from . import migrations
from . import models
from . import modules
from . import monitoring
from . import redis_module
from . import responses
from . import schemas
from . import services
from . import utils
from . import v1, v2
from .conf import conf
from .context_vars import locale_context
from .middlewares import RouterLoggingMiddleware, InternalServerErrorHandlingMiddleware
from api.dependencies.clients import (
    aclose_pos_terminal_client,
    aclose_freedom_bank_otp_client,
)
from api.dependencies.clients import pos_terminal_otp

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
    fastapi.staticfiles.StaticFiles(directory=conf.media.root),
    name='media',
)

app.mount(
    conf.static.url,
    fastapi.staticfiles.StaticFiles(directory=conf.static.root),
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
# app.add_middleware(
#     RouterLoggingMiddleware,
#     logger=logging.getLogger("uvicorn.error")
# )
# app.add_middleware(InternalServerErrorHandlingMiddleware)


@app.middleware('http')
def add_context_vars_middleware(request: fastapi.Request, call_next):
    locale_context.set(request.headers.get(conf.api.locale.header_name, conf.api.locale.default_locale))
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
    _: fastapi.Request,
    exc: pydantic.ValidationError,
) -> fastapi.responses.Response:
    """Handles pydantic validation errors.

    Without this handler, if query parameters are defined as pydantic model,
    a validation error would throw an internal error to client.
    """
    return fastapi.responses.JSONResponse(
        status_code=422,
        content={
            'detail': exc.errors(),
        },
    )


@app.exception_handler(common.BaseError)
async def new_db_exception_handler(
    r: fastapi.Request,
    exc: common.BaseError,
):
    class t:
        @staticmethod
        async def t(val, **kwargs):
            return val
    # if r.state.fvi_translators and r.state.fvi_translators[r.state.locale]:
    #     t = r.state.fvi_translators[r.state.locale]
    # else:
    #     t = Translator(r.state.locale, locale_path=r.state.locale_path)

    if issubclass(exc.__class__, common.BaseIntegrityError):
        try:
            detail = exc.detail
            exc_type = 'not present' if 'not present' in detail else 'already exist'
            columns, values = re.findall(r'\(([A-Za-zА-Яа-я0-9_+,:;\- ]+)\)', exc.detail)
        except ValueError:
            raise exc
        errors = []
        for field, val in zip(columns.split(', '), values.split(', ')):
            errors.append((field, await t.t(
                'value: {val} ' + exc_type,
                val=val,
            )))

        return fastapi.responses.JSONResponse(
            status_code=422,
            content={
                'detail': PydanticException(errors=errors).errors(),
            },
        )

    if issubclass(exc.__class__, common.BaseNotFoundError):
        return fastapi.responses.JSONResponse(
            status_code=404,
            content={
                'detail': await t.t(exc.detail, **exc.kwargs),
                'status': 'not-found',
                'code': exc.code,
                'model': exc.table,
            }
        )


@app.exception_handler(BaseORMException)
@app.exception_handler(asyncpg.PostgresError)
async def db_exception_handler(
    r: fastapi.Request,
    exc: BaseORMException,
):
    class t:
        @staticmethod
        async def t(val, **kwargs):
            return val.format(**kwargs)
    # if r.state.fvi_translators and r.state.fvi_translators[r.state.locale]:
    #     t = r.state.fvi_translators[r.state.locale]
    # else:
    #     t = Translator(r.state.locale, locale_path=r.state.locale_path)

    if not isinstance(exc, DoesNotExist) and isinstance(exc.args[0], str):
        return fastapi.responses.JSONResponse(
            status_code=500,
            content={
                'detail': await t.t(exc.args[0]),
                'status': 'internal-error',
                'status_code': 500,
            }
        )
    for arg in exc.args:
        if isinstance(arg, str):
            return fastapi.responses.JSONResponse(
                status_code=404,
                content={
                    'detail': arg,
                    'status': 'not-found',
                    'status_code': 404,
                }
            )
        if isinstance(arg, UniqueViolationError):
            try:
                column, value = re.findall(r'\(([A-Za-zА-Яа-я0-9_+,:;\- ]+)\)', arg.detail)
            except ValueError:
                raise exc
            return fastapi.responses.JSONResponse(
                status_code=400,
                content={
                    'detail': await t.t(
                        '{table_name} with fields: {column} and values: {value} is already exists',
                        table_name=arg.table_name,
                        column=column,
                        value=value,
                    ),
                    'status': 'bad-request',
                    'status_code': 400,
                }
            )
        if isinstance(arg, ForeignKeyViolationError):
            if 'is still referenced' in arg.detail:
                return fastapi.responses.JSONResponse(
                    status_code=400,
                    content={
                        'detail': await t.t('Can not delete'),
                        'status': 'bad-request',
                        'status_code': 400,
                    }
                )
            try:
                column, value = re.findall(r'\(([A-Za-zА-Яа-я0-9_+,:;\- ]+)\)', arg.detail)
            except ValueError:
                raise exc
            table_name = re.findall(r'\"([A-Za-zА-Яа-я0-9_]+)\"', arg.detail)[-1]
            column = column.split('_')[-1]
            return fastapi.responses.JSONResponse(
                status_code=400,
                content={
                    'detail': await t.t(
                        '{table_name} with given {column}: {value} was not found',
                        table_name=await t.t(table_name),
                        column=await t.t(column),
                        value=value,
                    ),
                    'status': 'bad-request',
                    'status_code': 400,
                }
            )


@app.exception_handler(OperationalError)
async def db_connection_error_handler(
    r: fastapi.Request,
    exc: OperationalError,
):
    # if r.state.fvi_translators and r.state.fvi_translators[r.state.locale]:
    #     t = r.state.fvi_translators[r.state.locale]
    # else:
    #     t = Translator(r.state.locale, locale_path=r.state.locale_path)
    # detail = await translate_error(t, str(exc))
    detail = str(exc)

    return fastapi.responses.JSONResponse(
        status_code=500,
        content={
            'detail': detail,
            'status': responses.InternalErrorStatus.INTERNAL_ERROR,
            'status_code': 500,
        }
    )


@app.exception_handler(exceptions.HTTPException)
async def request_exception_handler(
    r: fastapi.Request,
    exc: exceptions.HTTPException,
):
    # if r.state.fvi_translators and r.state.fvi_translators[r.state.locale]:
    #     t = r.state.fvi_translators[r.state.locale]
    # else:
    #     t = Translator(r.state.locale, locale_path=r.state.locale_path)
    # detail = await translate_error(t, exc.detail)
    detail = exc.detail

    return fastapi.responses.JSONResponse(
        status_code=exc.status_code,
        content={
            'detail': detail,
            'status': exc.status,
            'status_code': exc.status_code,
        },
    )


@app.exception_handler(500)
async def internal_exception_handler(_: fastapi.Request, exc: Exception):
    detail = 'Internal Server Error'
    if conf.api.debug:
        detail = str(exc)
    return fastapi.responses.JSONResponse(
        status_code=500,
        content={
            'detail': detail,
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
