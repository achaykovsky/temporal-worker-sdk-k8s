# syntax=docker/dockerfile:1
# Multi-stage worker image (K8-01). Pinned base; app runs as non-root.
# HEALTHCHECK: intentionally omitted — use Kubernetes probes on /livez and /readyz
# when TEMPORAL_WORKER_HEALTH_ADDR is set (see README).

FROM python:3.12.8-slim-bookworm AS builder

ENV POETRY_VERSION=2.1.1 \
    POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_IN_PROJECT=true \
    POETRY_CACHE_DIR=/tmp/poetry-cache

RUN pip install --no-cache-dir "poetry==${POETRY_VERSION}"

WORKDIR /app

COPY pyproject.toml poetry.lock ./
COPY src ./src

RUN poetry install --only main --no-interaction \
    && rm -rf "${POETRY_CACHE_DIR}"

FROM python:3.12.8-slim-bookworm AS runtime

RUN groupadd --system --gid 10001 worker \
    && useradd --system --uid 10001 --gid worker --no-create-home --shell /usr/sbin/nologin worker

WORKDIR /app

COPY --from=builder --chown=10001:10001 /app/.venv /app/.venv
COPY --from=builder --chown=10001:10001 /app/src /app/src

ENV PATH="/app/.venv/bin:${PATH}" \
    PYTHONUNBUFFERED=1

USER worker

CMD ["python", "-m", "calculator.worker_main"]
