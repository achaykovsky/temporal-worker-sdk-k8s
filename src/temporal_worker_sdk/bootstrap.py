"""Standard worker bootstrap: connect client and poll the configured task queue."""

from __future__ import annotations

import asyncio
import contextlib
import logging
import os
import signal
import threading
from collections.abc import Callable, Sequence
from datetime import timedelta

from prometheus_client import CollectorRegistry
from temporalio.client import Client
from temporalio.worker import Worker

from temporal_worker_sdk.config import WorkerConfig, load_worker_config
from temporal_worker_sdk.health_server import HealthMetricsServer
from temporal_worker_sdk.logging_config import (
    configure_worker_logging,
    safe_temporal_target_for_log,
)
from temporal_worker_sdk.metrics import build_sdk_metrics
from temporal_worker_sdk.observability_interceptor import ObservabilityInterceptor

logger = logging.getLogger(__name__)

# Documented exit code when shutdown exceeds TEMPORAL_WORKER_SHUTDOWN_MAX_WAIT_SEC.
EXIT_SHUTDOWN_HARD_TIMEOUT = 124


def run_worker(
    *,
    workflows: Sequence[type] | None = None,
    activities: Sequence[Callable] | None = None,
    config: WorkerConfig | None = None,
    client: Client | None = None,
) -> None:
    """
    Public entrypoint: load config (unless provided), connect to Temporal, run the worker.

    Pass ``workflows`` and ``activities`` for your worker role. Integration code should depend
    only on this package's documented API — not on internal module paths.

    If ``client`` is supplied (e.g. tests), it is used instead of opening a new connection.
    """
    asyncio.run(
        run_worker_async(
            workflows=workflows,
            activities=activities,
            config=config,
            client=client,
        )
    )


async def run_worker_async(
    *,
    workflows: Sequence[type] | None = None,
    activities: Sequence[Callable] | None = None,
    config: WorkerConfig | None = None,
    client: Client | None = None,
) -> None:
    """Async variant of :func:`run_worker` for callers already inside an event loop."""
    cfg = config or load_worker_config()
    if client is None:
        c = await Client.connect(
            cfg.temporal_address,
            namespace=cfg.temporal_namespace,
            identity=cfg.temporal_identity,
        )
    else:
        c = client
    await _run_with_client(cfg, c, workflows or (), activities or ())


def _install_shutdown_handlers(
    loop: asyncio.AbstractEventLoop,
    schedule_shutdown: Callable[[], None],
) -> None:
    """Register SIGINT/SIGTERM where the platform allows (see README for Windows notes)."""
    for sig in (signal.SIGINT, signal.SIGTERM):
        try:
            loop.add_signal_handler(sig, schedule_shutdown)
        except (NotImplementedError, RuntimeError, ValueError, OSError):
            try:
                signal.signal(
                    sig,
                    lambda *_args, loop_ref=loop: loop_ref.call_soon_threadsafe(schedule_shutdown),
                )
            except (ValueError, OSError):
                logger.warning(
                    "Could not register %s for graceful shutdown; use Ctrl+C or kill",
                    sig.name if hasattr(sig, "name") else sig,
                )


async def _run_with_client(
    cfg: WorkerConfig,
    client: Client,
    workflows: Sequence[type],
    activities: Sequence[Callable],
) -> None:
    configure_worker_logging(cfg)

    registry = CollectorRegistry()
    metrics_bundle = build_sdk_metrics(registry)
    obs_interceptor = ObservabilityInterceptor(cfg, metrics_bundle)

    graceful = timedelta(seconds=cfg.graceful_shutdown_timeout_sec)
    worker = Worker(
        client,
        task_queue=cfg.task_queue,
        workflows=list(workflows),
        activities=list(activities),
        graceful_shutdown_timeout=graceful,
        interceptors=[obs_interceptor],
    )

    draining = threading.Event()
    polling_started = threading.Event()

    def is_live() -> bool:
        return True

    def is_ready() -> bool:
        if draining.is_set():
            return False
        return polling_started.is_set()

    health: HealthMetricsServer | None = None
    if cfg.health_bind_addr:
        health = HealthMetricsServer(
            cfg.health_bind_addr,
            registry,
            is_live=is_live,
            is_ready=is_ready,
        )
        health.start()

    loop = asyncio.get_running_loop()
    shutdown_task: asyncio.Task[None] | None = None

    async def shutdown_worker() -> None:
        draining.set()
        logger.info(
            "shutdown_signal_received initiating_temporal_shutdown graceful_sec=%s max_wait_sec=%s",
            cfg.graceful_shutdown_timeout_sec,
            cfg.shutdown_max_wait_sec,
        )
        try:
            await asyncio.wait_for(worker.shutdown(), timeout=cfg.shutdown_max_wait_sec)
        except asyncio.TimeoutError:
            logger.error(
                "shutdown_max_wait_exceeded; exiting with code %s (activities may have been "
                "cancelled per Temporal graceful_shutdown_timeout=%ss)",
                EXIT_SHUTDOWN_HARD_TIMEOUT,
                cfg.graceful_shutdown_timeout_sec,
            )
            os._exit(EXIT_SHUTDOWN_HARD_TIMEOUT)

    def schedule_shutdown() -> None:
        nonlocal shutdown_task
        if shutdown_task is not None and not shutdown_task.done():
            return
        shutdown_task = asyncio.create_task(shutdown_worker())

    _install_shutdown_handlers(loop, schedule_shutdown)

    async def mark_polling_started() -> None:
        try:
            while not worker.is_running:
                if worker.is_shutdown:
                    return
                await asyncio.sleep(0.05)
        except asyncio.CancelledError:
            return
        if worker.is_running and not draining.is_set():
            polling_started.set()
            logger.info("worker_polling_started task_queue=%r", cfg.task_queue)

    readiness_task = asyncio.create_task(mark_polling_started())

    try:
        safe_target = safe_temporal_target_for_log(cfg.temporal_address)
        logger.info(
            "starting_temporal_worker temporal_target=%s queue=%r namespace=%r",
            safe_target,
            cfg.task_queue,
            cfg.temporal_namespace,
            extra={
                "temporal_target": safe_target,
                "task_queue": cfg.task_queue,
                "temporal_namespace": cfg.temporal_namespace,
            },
        )
        await worker.run()
    finally:
        readiness_task.cancel()
        with contextlib.suppress(asyncio.CancelledError):
            await readiness_task
        if health is not None:
            health.stop()
