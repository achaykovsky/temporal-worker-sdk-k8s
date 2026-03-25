"""Environment-backed worker configuration (MVP names from requirements-decisions)."""

from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Optional


class ConfigError(ValueError):
    """Raised when required configuration is missing or invalid."""

    def __init__(self, message: str, *, missing_var: Optional[str] = None) -> None:
        super().__init__(message)
        self.missing_var = missing_var


def _truthy_env(name: str) -> bool:
    raw = os.environ.get(name)
    if raw is None:
        return False
    return raw.strip().lower() in ("1", "true", "yes", "on")


def _required_str(name: str) -> str:
    raw = os.environ.get(name)
    if raw is None:
        raise ConfigError(
            f"Required environment variable {name!r} is unset.",
            missing_var=name,
        )
    stripped = raw.strip()
    if not stripped:
        raise ConfigError(
            f"Required environment variable {name!r} is set but empty.",
            missing_var=name,
        )
    return stripped


def _optional_str(name: str) -> Optional[str]:
    raw = os.environ.get(name)
    if raw is None:
        return None
    stripped = raw.strip()
    return stripped if stripped else None


def _optional_positive_float(name: str, default: float) -> float:
    raw = os.environ.get(name)
    if raw is None:
        return default
    stripped = raw.strip()
    if not stripped:
        return default
    try:
        value = float(stripped)
    except ValueError as exc:
        raise ConfigError(
            f"Environment variable {name!r} must be a positive number, got {raw!r}.",
        ) from exc
    if value <= 0:
        raise ConfigError(
            f"Environment variable {name!r} must be positive, got {value!r}.",
        )
    return value


@dataclass(frozen=True)
class WorkerConfig:
    """Typed worker settings after env validation."""

    temporal_address: str
    temporal_namespace: str
    task_queue: str
    worker_role: Optional[str]
    temporal_identity: Optional[str]
    log_json: bool
    health_bind_addr: Optional[str]
    graceful_shutdown_timeout_sec: float
    shutdown_max_wait_sec: float
    log_payloads_debug: bool


def load_worker_config() -> WorkerConfig:
    """
    Load configuration from the process environment.

    Required (no defaults — fail fast):
    - TEMPORAL_ADDRESS: gRPC target for the Temporal frontend (MVP stack uses port 7233).
    - TEMPORAL_NAMESPACE: Temporal namespace for this worker.
    - TEMPORAL_TASK_QUEUE: Task queue this worker polls.

    Names aligned with locked MVP env in specs/requirements-decisions.md where specified;
    connection keys are the SDK contract documented in README (deploy maps ConfigMap to these).

    Optional shutdown / logging (see README):
    - TEMPORAL_WORKER_GRACEFUL_SHUTDOWN_TIMEOUT_SEC (default 30): passed to Temporal
      ``Worker(graceful_shutdown_timeout=...)`` so in-flight activities may finish within this window.
    - TEMPORAL_WORKER_SHUTDOWN_MAX_WAIT_SEC (default 120): upper bound for ``await worker.shutdown()``
      after SIGTERM/SIGINT; on breach the process logs and exits with code 124.
    - TEMPORAL_WORKER_LOG_PAYLOADS_DEBUG: when truthy, DEBUG logs may include truncated workflow/activity
      args (never at INFO by default).
    """
    temporal_address = _required_str("TEMPORAL_ADDRESS")
    temporal_namespace = _required_str("TEMPORAL_NAMESPACE")
    task_queue = _required_str("TEMPORAL_TASK_QUEUE")

    return WorkerConfig(
        temporal_address=temporal_address,
        temporal_namespace=temporal_namespace,
        task_queue=task_queue,
        worker_role=_optional_str("WORKER_ROLE"),
        temporal_identity=_optional_str("TEMPORAL_IDENTITY"),
        log_json=_truthy_env("LOG_JSON"),
        health_bind_addr=_optional_str("TEMPORAL_WORKER_HEALTH_ADDR"),
        graceful_shutdown_timeout_sec=_optional_positive_float(
            "TEMPORAL_WORKER_GRACEFUL_SHUTDOWN_TIMEOUT_SEC",
            30.0,
        ),
        shutdown_max_wait_sec=_optional_positive_float(
            "TEMPORAL_WORKER_SHUTDOWN_MAX_WAIT_SEC",
            120.0,
        ),
        log_payloads_debug=_truthy_env("TEMPORAL_WORKER_LOG_PAYLOADS_DEBUG"),
    )
