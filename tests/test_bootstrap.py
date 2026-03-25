"""Bootstrap uses config task queue and constructs a worker (mocked, no I/O)."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock

import pytest

from temporal_worker_sdk import bootstrap
from temporal_worker_sdk.config import WorkerConfig


@pytest.mark.asyncio
async def test_run_worker_async_polls_configured_queue(monkeypatch: pytest.MonkeyPatch) -> None:
    captured: dict[str, object] = {}

    class FakeWorker:
        def __init__(
            self,
            client: object,
            *,
            task_queue: str,
            workflows: list[object],
            activities: list[object],
            **kwargs: object,
        ) -> None:
            captured["task_queue"] = task_queue
            captured["workflows"] = workflows
            captured["activities"] = activities
            captured["worker_kwargs"] = kwargs
            self._started = False

        @property
        def is_running(self) -> bool:
            return self._started

        @property
        def is_shutdown(self) -> bool:
            return False

        async def run(self) -> None:
            self._started = True
            captured["ran"] = True

        async def shutdown(self) -> None:
            pass

    monkeypatch.setattr(bootstrap, "Worker", FakeWorker)

    cfg = WorkerConfig(
        temporal_address="127.0.0.1:7233",
        temporal_namespace="default",
        task_queue="calc-mul",
        worker_role="mul",
        temporal_identity=None,
        log_json=False,
        health_bind_addr=None,
        graceful_shutdown_timeout_sec=30.0,
        shutdown_max_wait_sec=120.0,
        log_payloads_debug=False,
    )
    fake_client = MagicMock()

    await bootstrap.run_worker_async(
        workflows=[],
        activities=[],
        config=cfg,
        client=fake_client,  # type: ignore[arg-type]
    )

    assert captured["task_queue"] == "calc-mul"
    assert captured["ran"] is True
    assert captured["workflows"] == []
    assert captured["activities"] == []
    wk = captured["worker_kwargs"]
    assert "graceful_shutdown_timeout" in wk
    assert "interceptors" in wk


@pytest.mark.asyncio
async def test_run_worker_async_connects_when_no_client(monkeypatch: pytest.MonkeyPatch) -> None:
    captured: dict[str, object] = {}

    async def fake_connect(
        address: str,
        *,
        namespace: str,
        identity: str | None,
    ) -> object:
        captured["address"] = address
        captured["namespace"] = namespace
        captured["identity"] = identity
        return MagicMock()

    class FakeWorker:
        def __init__(self, *args: object, **kwargs: object) -> None:
            self._started = False

        @property
        def is_running(self) -> bool:
            return self._started

        @property
        def is_shutdown(self) -> bool:
            return False

        async def run(self) -> None:
            self._started = True

        async def shutdown(self) -> None:
            pass

    monkeypatch.setattr(bootstrap.Client, "connect", AsyncMock(side_effect=fake_connect))
    monkeypatch.setattr(bootstrap, "Worker", FakeWorker)

    cfg = WorkerConfig(
        temporal_address="temporal:7233",
        temporal_namespace="ns1",
        task_queue="q",
        worker_role=None,
        temporal_identity="id-1",
        log_json=False,
        health_bind_addr=None,
        graceful_shutdown_timeout_sec=30.0,
        shutdown_max_wait_sec=120.0,
        log_payloads_debug=False,
    )

    await bootstrap.run_worker_async(workflows=[], activities=[], config=cfg, client=None)

    assert captured["address"] == "temporal:7233"
    assert captured["namespace"] == "ns1"
    assert captured["identity"] == "id-1"
