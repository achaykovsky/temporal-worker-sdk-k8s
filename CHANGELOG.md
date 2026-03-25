# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and this project adheres to **semantic versioning** (`MAJOR.MINOR.PATCH`).

## Policy

- **PATCH**: bug fixes, documentation, internal refactors without behavior change.
- **MINOR**: new backward-compatible capabilities (new optional env vars, new optional APIs).
- **MAJOR**: breaking changes to required env vars, public function signatures, or default behavior.

## [0.1.0] — unreleased

### Added

- Env-driven `WorkerConfig` with validation (`load_worker_config`).
- Public entrypoints `run_worker` and `run_worker_async`.
- Documented environment variable inventory in README (aligned with [specs/requirements/requirements-decisions.md](specs/requirements/requirements-decisions.md)).
- Calculator **API contract** in `calculator.contracts` (`CalculatorWorkflow`, queues, activity names, expression limits **4096** / **512** binary ops) per [specs/features/api-workflow-activity-contracts.md](specs/features/api-workflow-activity-contracts.md); reference workflow and per-operator activities under `src/calculator/`.
- **Observability (minor):** SIGINT/SIGTERM → `worker.shutdown()` with structured logs; `TEMPORAL_WORKER_GRACEFUL_SHUTDOWN_TIMEOUT_SEC` and `TEMPORAL_WORKER_SHUTDOWN_MAX_WAIT_SEC` (exit code **124** on hard timeout); optional **`TEMPORAL_WORKER_HEALTH_ADDR`** HTTP server for `/livez`, `/readyz`, and Prometheus `/metrics` (`prometheus_client`); low-cardinality activity metrics and README probe/scrape guidance ([specs/tasks/feature-observability-graceful-shutdown.tasks.md](specs/tasks/feature-observability-graceful-shutdown.tasks.md)).
- **Autoscaling (bonus, P2):** CPU HPA manifest [`k8s/calculator-worker-add-hpa.yaml`](k8s/calculator-worker-add-hpa.yaml) for `calculator-worker-add`; optional `./scripts/deploy.sh --with-hpa` / `deploy.ps1 -ApplyHpa`; README **Autoscaling (bonus)** (metrics-server verification, metric rationale, limitations, stress parameters); stress driver [`scripts/stress_calculator_workers.py`](scripts/stress_calculator_workers.py) ([specs/tasks/feature-autoscaling-bonus.tasks.md](specs/tasks/feature-autoscaling-bonus.tasks.md)).
