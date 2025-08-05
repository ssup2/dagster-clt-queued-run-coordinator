FROM python:3.11-slim

ARG DAGSTER_VERSION=1.10.5
ARG DAGSTER_MODULES_VERSION=0.26.5
ARG DAGSTER_OBSTORE_VERSION=0.2.2

RUN pip install \
    dagster==${DAGSTER_VERSION} \
    dagster-k8s==${DAGSTER_MODULES_VERSION} \
    dagster-graphql==${DAGSTER_VERSION} \
    dagster-webserver==${DAGSTER_VERSION} \
    dagster-postgres==${DAGSTER_MODULES_VERSION} \
    dagster-celery[flower,redis,kubernetes]==${DAGSTER_MODULES_VERSION} \
    dagster-celery-k8s==${DAGSTER_MODULES_VERSION} \
    dagster-obstore==${DAGSTER_OBSTORE_VERSION} \
    redis

COPY pyproject.toml README.md /opt/clt_queued_run_coordinator/
COPY src /opt/clt_queued_run_coordinator/src

RUN pip install /opt/clt_queued_run_coordinator
