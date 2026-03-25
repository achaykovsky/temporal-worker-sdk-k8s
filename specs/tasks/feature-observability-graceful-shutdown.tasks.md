# Tasks: Graceful shutdown, observability, health probes

**Parent spec**: [`../features/feature-observability-graceful-shutdown.md`](../features/feature-observability-graceful-shutdown.md)  
**Priority**: P0  
**Planning**: [priority-and-dependency-order.md](./priority-and-dependency-order.md)  
**Canonical requirements**: [requirements-decisions.md](../requirements/requirements-decisions.md) · [requirements-architecture.md](../requirements/requirements-architecture.md#cross-cutting-guardrails)  
**Depends on**: Worker SDK bootstrap/lifecycle ([feature-worker-sdk.tasks.md](./feature-worker-sdk.tasks.md)).  
**Blocks**: Kubernetes readiness probes; autoscaling metrics.

---

## OB-01 — Wire SIGTERM to worker shutdown path

**Description**: Hook platform signal to Temporal worker shutdown API; document timeout behavior.

**Acceptance criteria**

- [x] **Given** worker running, **when** SIGTERM (or Windows equivalent documented), **then** shutdown path is invoked (log line or metric).

**Dependencies**: WS-04.  
**Effort**: 2–3h.  
**Type**: feature.

---

## OB-02 — Drain in-flight activities with bounded timeout

**Description**: Configure max drain wait; on timeout log explicit message and exit with documented code.

**Acceptance criteria**

- [x] **Given** a long-running activity (test double or sleep activity), **when** SIGTERM and drain timeout elapses, **then** behavior matches documented policy (no silent drop without documentation). *(Temporal `graceful_shutdown_timeout` + README; hard cap exit **124** documented.)*

**Dependencies**: OB-01.  
**Effort**: 2–4h.  
**Type**: feature / test.

---

## OB-03 — Structured logging baseline

**Description**: JSON or key-value logs with worker identity, task queue, workflow/activity type when available; redact secrets. **Default:** do **not** log full raw workflow/activity **payloads** at INFO (e.g. entire calculator expression); truncation, hash, or debug-only flag per [requirements-decisions.md](../requirements/requirements-decisions.md).

**Acceptance criteria**

- [x] **Given** error path, **when** logs emitted, **then** they are machine-parseable and include correlation fields the SDK exposes (workflow id / run id if available).
- [x] No raw connection strings or tokens in log fields.
- [x] Documented behavior for payload logging (what is omitted/truncated at INFO vs DEBUG).

**Dependencies**: WS-04 (optional ordering with OB-01).  
**Effort**: 2–3h.  
**Type**: feature.

---

## OB-04 — Prometheus metrics (low cardinality)

**Description**: Expose counters/histograms for activity start/complete/error and poll latency; label set bounded and documented. **Histograms:** choose **fixed** bucket boundaries (e.g. poll latency); document them in README to avoid scrape bloat and aid comparison across runs.

**Acceptance criteria**

- [x] **Given** load, **when** `/metrics` scraped, **then** series cardinality stays bounded (no unbounded workflow-id labels).
- [x] README lists **histogram names** and **bucket boundaries** (or points to module constant).

**Dependencies**: OB-03 optional.  
**Effort**: 3–4h.  
**Type**: feature.

---

## OB-05 — Optional health + metrics HTTP server

**Description**: When `TEMPORAL_WORKER_HEALTH_ADDR` unset, no listener. When set, single bind serves `/livez`, `/readyz`, `/metrics` per decisions doc.

**Acceptance criteria**

- [x] **Given** env unset, **when** worker starts, **then** no health server listens.
- [x] **Given** env set, **when** probes hit endpoints, **then** liveness/readiness return correct HTTP status during startup, steady state, and shutdown (readiness follows MVP rule: polling started).

**Dependencies**: OB-01, OB-04 (metrics on same server).  
**Effort**: 3–4h.  
**Type**: infra / feature.

---

## OB-06 — Document probe and metrics usage for K8s

**Description**: README fragment for probe paths, ports, and scrape annotations if any.

**Acceptance criteria**

- [x] Copy-paste-ready probe snippet or table for Deployments.

**Dependencies**: OB-05.  
**Effort**: 1h.  
**Type**: docs.
