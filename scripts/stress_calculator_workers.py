"""
Stress-test calculator workflows for HPA validation (AS-04).

Runs concurrent workflows for a fixed duration, prints latency stats, and (if
``kubectl`` is available) snapshots Deployment replicas and optional ``kubectl top``.

Prerequisites: Temporal frontend reachable (same as trigger_calculator_workflow.py).
"""

from __future__ import annotations

import argparse
import asyncio
import math
import os
import subprocess
import sys
import time
from datetime import timedelta
from uuid import uuid4

from temporalio.client import Client

from calculator.contracts import WORKFLOW_TASK_QUEUE
from calculator.workflow import CalculatorWorkflow

# Many binary ops with + to load calc-add activity workers.
_DEFAULT_STRESS_EXPRESSION = "+".join(["3"] * 80)


def _percentile_nearest(sorted_vals: list[float], pct: float) -> float:
    if not sorted_vals:
        return float("nan")
    if pct <= 0:
        return sorted_vals[0]
    if pct >= 100:
        return sorted_vals[-1]
    idx = int(math.ceil((pct / 100.0) * len(sorted_vals)) - 1)
    idx = max(0, min(len(sorted_vals) - 1, idx))
    return sorted_vals[idx]


def _median(sorted_vals: list[float]) -> float:
    if not sorted_vals:
        return float("nan")
    n = len(sorted_vals)
    m = n // 2
    if n % 2:
        return sorted_vals[m]
    return (sorted_vals[m - 1] + sorted_vals[m]) / 2.0


def _kubectl_lines(args: list[str]) -> str | None:
    try:
        r = subprocess.run(
            ["kubectl", *args],
            capture_output=True,
            text=True,
            timeout=45,
            check=False,
        )
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return None
    if r.returncode != 0:
        return None
    return r.stdout.rstrip() or "(empty)"


def snapshot_k8s(namespace: str, deployment: str) -> dict[str, str]:
    out: dict[str, str] = {}
    spec = _kubectl_lines(
        [
            "-n",
            namespace,
            "get",
            f"deploy/{deployment}",
            "-o",
            "jsonpath={.spec.replicas}/{.status.readyReplicas}/{.status.availableReplicas}",
        ]
    )
    out["deploy_replicas_ready_available"] = spec or "(kubectl unavailable or error)"
    top = _kubectl_lines(
        [
            "-n",
            namespace,
            "top",
            "pods",
            "-l",
            f"app.kubernetes.io/component={deployment.removeprefix('calculator-worker-')}",
            "--no-headers",
        ]
    )
    if top is None:
        alt = _kubectl_lines(
            ["-n", namespace, "top", "pods", "--no-headers"]
        )
        out["kubectl_top_pods"] = (
            alt
            if alt
            else "(kubectl top unavailable — install metrics-server or wait for samples)"
        )
    else:
        out["kubectl_top_pods"] = top
    return out


def _print_snapshot(label: str, namespace: str, deployment: str) -> None:
    print(f"\n--- {label} ---")
    snap = snapshot_k8s(namespace, deployment)
    for k, v in snap.items():
        print(f"{k}: {v}")


async def _stress(
    *,
    address: str,
    expression: str,
    concurrency: int,
    duration_sec: float,
    temporal_namespace: str,
) -> tuple[list[float], int]:
    client = await Client.connect(address, namespace=temporal_namespace)
    latencies: list[float] = []
    errors = 0
    deadline = time.monotonic() + duration_sec

    async def one_run() -> None:
        nonlocal errors
        wid = f"calc-stress-{uuid4()}"
        t0 = time.perf_counter()
        try:
            await client.execute_workflow(
                CalculatorWorkflow.run,
                expression,
                id=wid,
                task_queue=WORKFLOW_TASK_QUEUE,
                result_type=str,
                execution_timeout=timedelta(minutes=15),
            )
            latencies.append(time.perf_counter() - t0)
        except Exception:
            errors += 1

    async def worker() -> None:
        while time.monotonic() < deadline:
            await one_run()

    await asyncio.gather(*(worker() for _ in range(concurrency)))
    return latencies, errors


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Stress CalculatorWorkflow for HPA / load validation."
    )
    parser.add_argument(
        "--expression",
        default=os.environ.get("CALC_EXPRESSION", _DEFAULT_STRESS_EXPRESSION).strip(),
        help="Expression to evaluate (default stresses + via many additions).",
    )
    parser.add_argument(
        "--address",
        default=os.environ.get("TEMPORAL_ADDRESS", "127.0.0.1:7233").strip(),
        help="Temporal frontend gRPC target.",
    )
    parser.add_argument(
        "--namespace",
        default=os.environ.get("TEMPORAL_NAMESPACE", "default").strip(),
        help="Temporal namespace for workflows.",
    )
    parser.add_argument(
        "--concurrency",
        type=int,
        default=int(os.environ.get("STRESS_CONCURRENCY", "12")),
        help="Parallel in-flight workflows per worker task.",
    )
    parser.add_argument(
        "--duration-sec",
        type=float,
        default=float(os.environ.get("STRESS_DURATION_SEC", "420")),
        help="Wall-clock duration to keep submitting workflows (default ~7m for HPA).",
    )
    parser.add_argument(
        "--k8s-namespace",
        default=os.environ.get("STRESS_K8S_NAMESPACE", "temporal").strip(),
        help="Kubernetes namespace for kubectl snapshots.",
    )
    parser.add_argument(
        "--k8s-deployment",
        default=os.environ.get("STRESS_K8S_DEPLOYMENT", "calculator-worker-add").strip(),
        help="Deployment name for kubectl replica snapshot.",
    )
    args = parser.parse_args()
    if args.concurrency < 1:
        print("error: --concurrency must be >= 1", file=sys.stderr)
        raise SystemExit(2)
    if args.duration_sec <= 0:
        print("error: --duration-sec must be > 0", file=sys.stderr)
        raise SystemExit(2)
    if not args.expression:
        print("error: empty expression", file=sys.stderr)
        raise SystemExit(2)

    print(
        f"stress: concurrency={args.concurrency} duration_sec={args.duration_sec} "
        f"expression_len={len(args.expression)} temporal={args.address}"
    )
    _print_snapshot("before", args.k8s_namespace, args.k8s_deployment)

    t_wall0 = time.perf_counter()
    latencies, err_count = asyncio.run(
        _stress(
            address=args.address,
            expression=args.expression,
            concurrency=args.concurrency,
            duration_sec=args.duration_sec,
            temporal_namespace=args.namespace,
        )
    )
    wall = time.perf_counter() - t_wall0

    _print_snapshot("after", args.k8s_namespace, args.k8s_deployment)

    s = sorted(latencies)
    print("\n--- results ---")
    print(f"completed_workflows: {len(latencies)}")
    print(f"errors: {err_count}")
    print(f"wall_clock_sec: {wall:.3f}")
    if s:
        print(f"latency_sec_min: {s[0]:.3f}")
        print(f"latency_sec_p50: {_median(s):.3f}")
        print(f"latency_sec_p95: {_percentile_nearest(s, 95):.3f}")
        print(f"latency_sec_max: {s[-1]:.3f}")
    else:
        print("latency_sec: (no successful completions)")


if __name__ == "__main__":
    main()
