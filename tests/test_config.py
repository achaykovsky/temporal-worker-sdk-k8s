"""Unit tests for env-backed worker configuration (no Temporal server)."""

from __future__ import annotations

from dataclasses import FrozenInstanceError

import pytest

from temporal_worker_sdk.config import ConfigError, WorkerConfig, load_worker_config


@pytest.fixture(autouse=True)
def clear_temporal_env(monkeypatch: pytest.MonkeyPatch) -> None:
    for key in (
        "TEMPORAL_ADDRESS",
        "TEMPORAL_NAMESPACE",
        "TEMPORAL_TASK_QUEUE",
        "WORKER_ROLE",
        "TEMPORAL_IDENTITY",
        "LOG_JSON",
        "TEMPORAL_WORKER_HEALTH_ADDR",
        "TEMPORAL_WORKER_GRACEFUL_SHUTDOWN_TIMEOUT_SEC",
        "TEMPORAL_WORKER_SHUTDOWN_MAX_WAIT_SEC",
        "TEMPORAL_WORKER_LOG_PAYLOADS_DEBUG",
    ):
        monkeypatch.delenv(key, raising=False)


def test_load_config_success_all_required(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("TEMPORAL_ADDRESS", "127.0.0.1:7233")
    monkeypatch.setenv("TEMPORAL_NAMESPACE", "default")
    monkeypatch.setenv("TEMPORAL_TASK_QUEUE", "calc-add")
    monkeypatch.setenv("WORKER_ROLE", "add")
    monkeypatch.setenv("TEMPORAL_IDENTITY", "worker-test")
    monkeypatch.setenv("LOG_JSON", "true")
    monkeypatch.setenv("TEMPORAL_WORKER_HEALTH_ADDR", "0.0.0.0:8080")

    cfg = load_worker_config()
    assert cfg.temporal_address == "127.0.0.1:7233"
    assert cfg.temporal_namespace == "default"
    assert cfg.task_queue == "calc-add"
    assert cfg.worker_role == "add"
    assert cfg.temporal_identity == "worker-test"
    assert cfg.log_json is True
    assert cfg.health_bind_addr == "0.0.0.0:8080"


def test_load_config_optional_omitted(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("TEMPORAL_ADDRESS", "temporal.temporal.svc:7233")
    monkeypatch.setenv("TEMPORAL_NAMESPACE", "default")
    monkeypatch.setenv("TEMPORAL_TASK_QUEUE", "calc-workflows")

    cfg = load_worker_config()
    assert cfg.worker_role is None
    assert cfg.temporal_identity is None
    assert cfg.log_json is False
    assert cfg.health_bind_addr is None
    assert cfg.graceful_shutdown_timeout_sec == 30.0
    assert cfg.shutdown_max_wait_sec == 120.0
    assert cfg.log_payloads_debug is False


@pytest.mark.parametrize(
    "missing",
    ("TEMPORAL_ADDRESS", "TEMPORAL_NAMESPACE", "TEMPORAL_TASK_QUEUE"),
)
def test_load_config_fails_when_required_missing(
    monkeypatch: pytest.MonkeyPatch,
    missing: str,
) -> None:
    monkeypatch.setenv("TEMPORAL_ADDRESS", "127.0.0.1:7233")
    monkeypatch.setenv("TEMPORAL_NAMESPACE", "default")
    monkeypatch.setenv("TEMPORAL_TASK_QUEUE", "q")
    monkeypatch.delenv(missing, raising=False)

    with pytest.raises(ConfigError) as excinfo:
        load_worker_config()
    assert excinfo.value.missing_var == missing


@pytest.mark.parametrize(
    "var",
    ("TEMPORAL_ADDRESS", "TEMPORAL_NAMESPACE", "TEMPORAL_TASK_QUEUE"),
)
def test_load_config_fails_when_required_empty(
    monkeypatch: pytest.MonkeyPatch,
    var: str,
) -> None:
    monkeypatch.setenv("TEMPORAL_ADDRESS", "127.0.0.1:7233")
    monkeypatch.setenv("TEMPORAL_NAMESPACE", "default")
    monkeypatch.setenv("TEMPORAL_TASK_QUEUE", "q")
    monkeypatch.setenv(var, "   ")

    with pytest.raises(ConfigError) as excinfo:
        load_worker_config()
    assert excinfo.value.missing_var == var


def test_log_json_truthy_variants(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("TEMPORAL_ADDRESS", "localhost:7233")
    monkeypatch.setenv("TEMPORAL_NAMESPACE", "default")
    monkeypatch.setenv("TEMPORAL_TASK_QUEUE", "q")

    for val in ("1", "TRUE", "yes", "On"):
        monkeypatch.setenv("LOG_JSON", val)
        assert load_worker_config().log_json is True


def test_worker_config_frozen() -> None:
    cfg = WorkerConfig(
        temporal_address="a",
        temporal_namespace="n",
        task_queue="q",
        worker_role=None,
        temporal_identity=None,
        log_json=False,
        health_bind_addr=None,
        graceful_shutdown_timeout_sec=30.0,
        shutdown_max_wait_sec=120.0,
        log_payloads_debug=False,
    )
    with pytest.raises(FrozenInstanceError):
        cfg.task_queue = "other"  # type: ignore[misc]
