FROM python:3.12.4-slim-bookworm as base

ARG APP_NAME
ARG BUILD_ENV
ARG APP_DIR=/app
# Value is needed to set correct environment in app
ENV BUILD_ENV ${BUILD_ENV}

WORKDIR ${APP_DIR}

# Install apt packages
RUN apt-get update && apt-get install --no-install-recommends -y \
  # dependencies for building Python packages
  build-essential \
  # psycopg dependencies
  libpq-dev

FROM base as build-stage

COPY ./backend/requirements ${APP_DIR}/requirements

FROM base as run-stage
# Python buffered output to stdout
ENV PYTHONUNBUFFERED 1
ENV PYTHONDONTWRITEBYTECODE 1

COPY --from=build-stage ${APP_DIR}/requirements ${APP_DIR}/requirements
RUN pip install --no-cache-dir -r ${APP_DIR}/requirements/${APP_NAME}.txt

COPY ./backend/docker/${APP_NAME}/entrypoint /entrypoint
RUN chmod +x /entrypoint

COPY ./backend/src ${APP_DIR}/src
COPY ./backend/.env ${APP_DIR}/.env

ENTRYPOINT ["/entrypoint"]
