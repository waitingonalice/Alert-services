FROM python:3.12.4-slim-bookworm as base

ARG APP_SERVICE=bot
ARG BUILD_ENV=local
ARG APP_DIR=/app
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

COPY --from=build-stage ${APP_DIR}/requirements ${APP_DIR}/requirements
RUN pip install --no-cache-dir -r ${APP_DIR}/requirements/${APP_SERVICE}.txt

COPY ./backend/docker/${BUILD_ENV}/bot/entrypoint /entrypoint
RUN chmod +x /entrypoint

COPY ./backend/src ${APP_DIR}/src
COPY ./backend/.env ${APP_DIR}/.env

ENTRYPOINT ["/entrypoint"]
