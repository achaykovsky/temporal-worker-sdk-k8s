"""Observability helpers and shutdown-related config (no Temporal server)."""

from __future__ import annotations

import pytest

from temporal_worker_sdk.config import ConfigError, load_worker_config
from temporal_worker_sdk.health_server import parse_bind_addr


def test_parse_bind_addr_host_port() -> None:
    assert parse_bind_addr("0.0.0.0:8080") == ("0.0.0.0", 8080)
    assert parse_bind_addr("127.0.0.1:9090") == ("127.0.0.1", 9090)


def test_load_config_shutdown_floats(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("TEMPORAL_ADDRESS", "127.0.0.1:7233")
    monkeypatch.setenv("TEMPORAL_NAMESPACE", "default")
    monkeypatch.setenv("TEMPORAL_TASK_QUEUE", "q")
    monkeypatch.setenv("TEMPORAL_WORKER_GRACEFUL_SHUTDOWN_TIMEOUT_SEC", "12.5")
    monkeypatch.setenv("TEMPORAL_WORKER_SHUTDOWN_MAX_WAIT_SEC", "200")
    cfg = load_worker_config()
    assert cfg.graceful_shutdown_timeout_sec == 12.5
    assert cfg.shutdown_max_wait_sec == 200.0


def test_load_config_shutdown_invalid_float(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("TEMPORAL_ADDRESS", "127.0.0.1:7233")
    monkeypatch.setenv("TEMPORAL_NAMESPACE", "default")
    monkeypatch.setenv("TEMPORAL_TASK_QUEUE", "q")
    monkeypatch.setenv("TEMPORAL_WORKER_SHUTDOWN_MAX_WAIT_SEC", "not-a-float")
    with pytest.raises(ConfigError):
        load_worker_config()


def test_load_config_shutdown_non_positive(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("TEMPORAL_ADDRESS", "127.0.0.1:7233")
    monkeypatch.setenv("TEMPORAL_NAMESPACE", "default")
    monkeypatch.setenv("TEMPORAL_TASK_QUEUE", "q")
    monkeypatch.setenv("TEMPORAL_WORKER_GRACEFUL_SHUTDOWN_TIMEOUT_SEC", "0")
    with pytest.raises(ConfigError):
        load_worker_config()
