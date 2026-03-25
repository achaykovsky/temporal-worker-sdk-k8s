"""Temporal worker interceptors for structured logs and Prometheus metrics."""

from __future__ import annotations

import asyncio
import logging
import time
from datetime import datetime, timezone
from typing import Any

import temporalio.activity as activity_mod
import temporalio.workflow as workflow_mod
from temporalio.worker import (
    ActivityInboundInterceptor,
    ExecuteActivityInput,
    ExecuteWorkflowInput,
    Interceptor,
    WorkflowInboundInterceptor,
    WorkflowInterceptorClassInput,
)

from temporal_worker_sdk.config import WorkerConfig
from temporal_worker_sdk.logging_config import _payload_preview, log_context_reset, log_context_set
from temporal_worker_sdk.metrics import SdkMetrics

logger = logging.getLogger(__name__)


class ObservabilityInterceptor(Interceptor):
    """Adds activity metrics and structured logs (no raw payloads at INFO)."""

    def __init__(self, cfg: WorkerConfig, metrics: SdkMetrics) -> None:
        self._cfg = cfg
        self._metrics = metrics

    def intercept_activity(self, next: ActivityInboundInterceptor) -> ActivityInboundInterceptor:
        return _ActivityObservabilityInbound(next, self._cfg, self._metrics)

    def workflow_interceptor_class(
        self,
        input: WorkflowInterceptorClassInput,
    ) -> type[WorkflowInboundInterceptor] | None:
        _ = input
        cfg = self._cfg

        class _WorkflowObsInbound(WorkflowInboundInterceptor):
            def __init__(self, next_in: WorkflowInboundInterceptor) -> None:
                super().__init__(next_in)
                self._cfg_inner = cfg

            async def execute_workflow(self, input: ExecuteWorkflowInput) -> Any:
                wf_log = logging.getLogger("temporal_worker_sdk.workflow")
                info = workflow_mod.info()
                token = log_context_set(
                    workflow_id=info.workflow_id,
                    workflow_run_id=info.run_id,
                    workflow_type=input.type.__name__,
                )
                try:
                    wf_log.info(
                        "workflow_task_started",
                        extra={
                            "workflow_id": info.workflow_id,
                            "workflow_run_id": info.run_id,
                            "workflow_type": input.type.__name__,
                        },
                    )
                    if self._cfg_inner.log_payloads_debug and wf_log.isEnabledFor(logging.DEBUG):
                        wf_log.debug(
                            "workflow_args_preview %s",
                            _payload_preview(input.args),
                            extra={
                                "workflow_id": info.workflow_id,
                                "workflow_run_id": info.run_id,
                            },
                        )
                    return await self.next.execute_workflow(input)
                except asyncio.CancelledError:
                    raise
                except BaseException as exc:
                    wf_log.error(
                        "workflow_task_failed",
                        exc_info=exc,
                        extra={
                            "workflow_id": info.workflow_id,
                            "workflow_run_id": info.run_id,
                            "workflow_type": input.type.__name__,
                        },
                    )
                    raise
                finally:
                    log_context_reset(token)

        return _WorkflowObsInbound


class _ActivityObservabilityInbound(ActivityInboundInterceptor):
    def __init__(
        self,
        next_in: ActivityInboundInterceptor,
        cfg: WorkerConfig,
        metrics: SdkMetrics,
    ) -> None:
        super().__init__(next_in)
        self._cfg = cfg
        self._metrics = metrics

    async def execute_activity(self, input: ExecuteActivityInput) -> Any:
        info = activity_mod.info()
        activity_name = info.activity_type
        self._metrics.activity_starts.labels(activity_name).inc()

        wf_id = info.workflow_id or ""
        run_id = info.workflow_run_id or ""
        wf_type = info.workflow_type or ""
        token = log_context_set(
            workflow_id=wf_id,
            workflow_run_id=run_id,
            workflow_type=wf_type,
            activity_type=activity_name,
        )
        act_log = logging.getLogger("temporal_worker_sdk.activity")
        act_log.info(
            "activity_started",
            extra={
                "activity_type": activity_name,
                "workflow_id": wf_id,
                "workflow_run_id": run_id,
            },
        )
        if self._cfg.log_payloads_debug and act_log.isEnabledFor(logging.DEBUG):
            act_log.debug(
                "activity_args_preview %s",
                _payload_preview(input.args),
                extra={"activity_type": activity_name},
            )

        now = datetime.now(timezone.utc)
        scheduled = info.scheduled_time
        if scheduled.tzinfo is None:
            scheduled = scheduled.replace(tzinfo=timezone.utc)
        delay = (now - scheduled).total_seconds()
        if delay >= 0:
            self._metrics.activity_schedule_to_start_seconds.labels(activity_name).observe(delay)

        t0 = time.perf_counter()
        try:
            result = await self.next.execute_activity(input)
        except asyncio.CancelledError:
            self._metrics.activity_completions.labels(activity_name, "cancelled").inc()
            raise
        except BaseException:
            self._metrics.activity_completions.labels(activity_name, "failure").inc()
            act_log.exception(
                "activity_failed",
                extra={
                    "activity_type": activity_name,
                    "workflow_id": wf_id,
                    "workflow_run_id": run_id,
                },
            )
            raise
        else:
            self._metrics.activity_completions.labels(activity_name, "success").inc()
            return result
        finally:
            elapsed = time.perf_counter() - t0
            self._metrics.activity_execution_seconds.labels(activity_name).observe(elapsed)
            log_context_reset(token)
