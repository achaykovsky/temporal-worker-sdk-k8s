"""
Prometheus metrics for the worker SDK (low-cardinality labels only).

Label values are activity type names — never workflow args or free-form user strings.
"""

from __future__ import annotations

from dataclasses import dataclass

from prometheus_client import CollectorRegistry, Counter, Histogram

# Histogram bucket boundaries (documented in README; keep stable for comparable scrapes).
ACTIVITY_EXECUTION_BUCKETS = (
    0.001,
    0.005,
    0.01,
    0.025,
    0.05,
    0.1,
    0.25,
    0.5,
    1.0,
    2.5,
    5.0,
    10.0,
    30.0,
    60.0,
    120.0,
)

# Time from server schedule to activity start on this worker (queue + poll latency proxy).
ACTIVITY_SCHEDULE_TO_START_BUCKETS = (
    0.01,
    0.05,
    0.1,
    0.25,
    0.5,
    1.0,
    2.5,
    5.0,
    10.0,
    30.0,
    60.0,
    120.0,
    300.0,
    600.0,
)


@dataclass(frozen=True)
class SdkMetrics:
    activity_starts: Counter
    activity_completions: Counter
    activity_execution_seconds: Histogram
    activity_schedule_to_start_seconds: Histogram


def build_sdk_metrics(registry: CollectorRegistry) -> SdkMetrics:
    """Register SDK metrics on *registry* (use an isolated registry for tests)."""
    activity_starts = Counter(
        "temporal_worker_activity_starts_total",
        "Activity task executions started on this worker",
        ("activity",),
        registry=registry,
    )
    activity_completions = Counter(
        "temporal_worker_activity_completions_total",
        "Activity task completions",
        ("activity", "outcome"),
        registry=registry,
    )
    activity_execution_seconds = Histogram(
        "temporal_worker_activity_execution_seconds",
        "Wall time spent inside user activity callables",
        ("activity",),
        buckets=ACTIVITY_EXECUTION_BUCKETS,
        registry=registry,
    )
    activity_schedule_to_start_seconds = Histogram(
        "temporal_worker_activity_schedule_to_start_seconds",
        "Time from activity scheduled_time to execute start (poll/queue proxy)",
        ("activity",),
        buckets=ACTIVITY_SCHEDULE_TO_START_BUCKETS,
        registry=registry,
    )
    return SdkMetrics(
        activity_starts=activity_starts,
        activity_completions=activity_completions,
        activity_execution_seconds=activity_execution_seconds,
        activity_schedule_to_start_seconds=activity_schedule_to_start_seconds,
    )
