# Tasks: Worker SDK

**Parent spec**: [`../features/feature-worker-sdk.md`](../features/feature-worker-sdk.md)  
**Priority**: P0  
**Planning**: [priority-and-dependency-order.md](./priority-and-dependency-order.md)  
**Canonical requirements**: [requirements-decisions.md](../requirements/requirements-decisions.md) · [requirements-architecture.md](../requirements/requirements-architecture.md#cross-cutting-guardrails)  
**Blocks**: Observability, calculator workers, Kubernetes worker images.

---

## WS-01 — Inventory env vars and defaults

**Description**: List required vs optional variables (address, namespace, identity, logging, telemetry) and map them to names locked in [requirements-decisions.md](../requirements/requirements-decisions.md).

**Acceptance criteria**

- [x] Table in README or module doc matches decisions doc for MVP names.
- [x] Missing required vars are enumerated explicitly.

**PM validation (2026-03-23)**: README **Worker environment variables** tables list all decision-locked names (`WORKER_ROLE`, `TEMPORAL_TASK_QUEUE`, `LOG_JSON`, `TEMPORAL_WORKER_HEALTH_ADDR`) and document `TEMPORAL_ADDRESS` / `TEMPORAL_NAMESPACE` as the SDK mapping for manifest “address/namespace”. Required trio is called out explicitly.

**Dependencies**: None.  
**Effort**: 1–2h.  
**Type**: docs / research.

---

## WS-02 — Implement env loader with validation

**Description**: Parse env into a typed config; validate on startup; no silent fallbacks for required connection fields.

**Acceptance criteria**

- [x] **Given** all required vars set, **when** config is built, **then** values are available to worker bootstrap without ad hoc `os.getenv` at call sites.
- [x] **Given** a missing required connection parameter, **when** the worker starts, **then** it fails fast with an error that names the variable.

**PM validation (2026-03-23)**: `load_worker_config()` / `WorkerConfig` centralize env reads; `ConfigError.missing_var` identifies `TEMPORAL_ADDRESS`, `TEMPORAL_NAMESPACE`, or `TEMPORAL_TASK_QUEUE` on failure.

**Dependencies**: WS-01.  
**Effort**: 2–4h.  
**Type**: feature.

---

## WS-03 — Unit tests for env validation

**Description**: Tests for present/missing combinations; no real Temporal connection.

**Acceptance criteria**

- [x] At least one test per required var proving startup/config construction fails when unset.

**PM validation (2026-03-23)**: Parametrized tests cover each required var for missing and whitespace-empty cases (`tests/test_config.py`).

**Dependencies**: WS-02.  
**Effort**: 1–2h.  
**Type**: test.

---

## WS-04 — Standard worker bootstrap (register + poll)

**Description**: Single code path that accepts workflow/activity registrations and starts polling the configured task queue using SDK client options from config.

**Acceptance criteria**

- [x] **Given** valid config and registrations, **when** bootstrap runs, **then** worker polls the configured queue (smoke test or integration stub acceptable at SDK layer).

**PM validation (2026-03-23)**: `run_worker` / `run_worker_async` build `Worker(..., task_queue=cfg.task_queue, ...)` and `await worker.run()`; `tests/test_bootstrap.py` mocks `Worker` / `Client.connect` (no Temporal).

**Dependencies**: WS-02.  
**Effort**: 2–4h.  
**Type**: feature.

---

## WS-05 — Public entrypoint API

**Description**: Stable function or CLI (e.g. `run` / `start_worker`) documented as the integration surface for other teams.

**Acceptance criteria**

- [x] Minimal sample worker uses only the public API (no internal imports).
- [x] Docstring or README section lists the supported entrypoint(s).

**PM validation (2026-03-23)**: [examples/minimal_worker.py](../../examples/minimal_worker.py) imports `run_worker` from `temporal_worker_sdk`; README **Public API** lists `run_worker`, `run_worker_async`, and config symbols.

**Dependencies**: WS-04.  
**Effort**: 1–3h.  
**Type**: feature / docs.

---

## WS-06 — Semantic versioning and changelog discipline

**Description**: Ensure `CHANGELOG` or release notes process; document breaking vs additive changes policy.

**Acceptance criteria**

- [x] `CHANGELOG` or GitHub Releases notes mention probe/metrics as additive when those land (cross-link observability tasks).

**PM validation (2026-03-23)**: [CHANGELOG.md](../../CHANGELOG.md) states semver policy and that health/metrics via `TEMPORAL_WORKER_HEALTH_ADDR` are **minor** / additive, with link to observability tasks.

**Dependencies**: WS-05 (baseline package exists).  
**Effort**: 1h.  
**Type**: docs.

---

## WS-07 — CI baseline (recommended)

**Description**: Add a minimal pipeline (e.g. GitHub Actions) that runs **unit tests** (`pytest` excluding integration markers) and **`poetry check`** (or lockfile validation). Optionally run **`pip-audit`** / **`poetry audit`** on PR or weekly—per [requirements-decisions.md](../requirements/requirements-decisions.md) (**CI / automated integration**). Align with [`.cursor/rules/devops.mdc`](../../.cursor/rules/devops.mdc): fail fast, cache deps; **container image scan** (Trivy/Snyk) is **post-MVP** unless you add an optional job after `Dockerfile` exists (see **DevOps deferrals** in [requirements-architecture.md](../requirements/requirements-architecture.md#cross-cutting-guardrails)).

**Acceptance criteria**

- [x] CI config committed; main/PR runs unit tests without requiring Temporal.
- [x] README “Testing” mentions CI vs local integration.

**PM validation (2026-03-23)**: [.github/workflows/ci.yml](../../.github/workflows/ci.yml) runs `poetry check` and `pytest -m "not integration"`; README **Testing** distinguishes local vs CI and integration marker.

**Dependencies**: WS-03 (tests exist).  
**Effort**: 1–3h.  
**Type**: infra.
