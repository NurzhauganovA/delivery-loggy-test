FROM gitlab.globerce.com:5050/delivery/delivery/python-poetry:3.10-slim-bookworm as base

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYSETUP_PATH=/opt/pysetup \
    APPLICATION_PATH=/usr/app
ENV VENV_PATH=$PYSETUP_PATH/.venv
ENV PATH=$VENV_PATH/bin:$PATH

RUN apt-get update && apt-get install -y --no-install-recommends make procps wkhtmltopdf

FROM base as builder

ENV PIP_NO_CACHE_DIR=off \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    PIP_DEFAULT_TIMEOUT=100 \
    POETRY_VIRTUALENVS_IN_PROJECT=true \
    POETRY_NO_INTERACTION=1

WORKDIR $PYSETUP_PATH

RUN rm -rf /etc/apt/sources.list
RUN touch /etc/apt/sources.list
RUN echo "deb http://deb.debian.org/debian bookworm main" >> /etc/apt/sources.list
RUN echo "deb http://deb.debian.org/debian-security bookworm-security main" >> /etc/apt/sources.list
RUN echo "deb http://deb.debian.org/debian bookworm-updates main" >> /etc/apt/sources.list

RUN apt-get -y update \
    && apt-get install -y --no-install-recommends build-essential libpq-dev curl

COPY poetry.lock pyproject.toml ./

RUN poetry install -n --no-root --only main

FROM builder as dev-builder
RUN poetry install -n --no-root

FROM base as app-base
ENV PORT=8001 \
    MEDIA_ROOT=/media
EXPOSE 5555
WORKDIR $APPLICATION_PATH
RUN mkdir -p $STATIC_ROOT $MEDIA_ROOT
COPY docker-entrypoint.sh ./
RUN chmod +x docker-entrypoint.sh

FROM app-base as development

ENV POETRY_NO_INTERACTION=1 \
    VIRTUAL_ENV=$VENV_PATH

COPY --from=dev-builder $VENV_PATH $VENV_PATH

COPY pyproject.toml poetry.lock Makefile ./
COPY api/ ./api
COPY cli/ ./cli
COPY translator/ ./translator
COPY static/ ./static

RUN poetry install -n

CMD ["./docker-entrypoint.sh"]