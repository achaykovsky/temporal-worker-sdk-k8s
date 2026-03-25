# Tasks: Local Kubernetes deployment

**Parent spec**: [`../features/feature-kubernetes-deployment.md`](../features/feature-kubernetes-deployment.md)  
**Priority**: P0  
**Planning**: [priority-and-dependency-order.md](./priority-and-dependency-order.md)  
**Canonical requirements**: [requirements-decisions.md](../requirements/requirements-decisions.md) · [requirements-architecture.md](../requirements/requirements-architecture.md#cross-cutting-guardrails)  
**Depends on**: Worker SDK env contract, container entrypoint, observability probes ([feature-worker-sdk.tasks.md](./feature-worker-sdk.tasks.md), [feature-observability-graceful-shutdown.tasks.md](./feature-observability-graceful-shutdown.tasks.md)).  
**Blocks**: Autoscaling bonus; [requirements-documentation.tasks.md](./requirements-documentation.tasks.md) (DOC-01/DOC-03 after K8-05 / K8-07).

---

## K8-01 — Multi-stage Dockerfile (non-root)

**Description**: Build worker image; non-root user; tag strategy documented for `minikube image load` (or registry). Satisfy [requirements-decisions.md](../requirements/requirements-decisions.md) **Worker Dockerfile (DevOps)** row: multi-stage, layer order, `COPY --chown` where applicable; **Docker HEALTHCHECK** optional—document choice vs K8s probes.

**Acceptance criteria**

- **Given** `docker build`, **when** image runs with same env vars as local Poetry run, **then** worker process starts and connects per README.
- [x] README states whether **`HEALTHCHECK`** is present and why (or defers to Kubernetes probes only).

**Dependencies**: WS-02, WS-05; OB-05 if probes required in image default.  
**Effort**: 2–4h.  
**Type**: infra.

---

## K8-02 — Namespace and Postgres manifests

**Description**: Namespace `temporal`; in-cluster PostgreSQL per decisions; pinned images. **DB password** (and any sensitive env) supplied via **`Secret`**, not committed cleartext—use `*.example`, `secretGenerator`, or documented `kubectl create secret`. Postgres Deployment includes **requests/limits**.

**Acceptance criteria**

- **Given** fresh cluster, **when** manifests applied in order, **then** Postgres pod becomes Ready and data volume policy documented.
- [x] No cleartext DB password in committed YAML; README explains how to create/apply the Secret locally.

**Dependencies**: K8-01 (optional parallel for YAML-only draft).  
**Effort**: 3–4h.  
**Type**: infra.

---

## K8-03 — Temporal auto-setup deployment

**Description**: `temporalio/auto-setup` (or locked equivalent) with DB env from upstream pattern; semver pinned. Deployment includes **CPU/memory requests and limits** consistent with README minikube guidance.

**Acceptance criteria**

- **Given** Postgres up, **when** Temporal manifests applied, **then** Temporal frontend reachable from cluster DNS name used by workers.
- [x] Temporal Deployment declares **requests** and **limits**.

**Dependencies**: K8-02.  
**Effort**: 2–4h.  
**Type**: infra.

---

## K8-04 — Six worker Deployments

**Description**: One Deployment per task queue (workflow + five operators); **ConfigMap** for non-sensitive Temporal address/namespace/queues; **Secret** references only for sensitive values; **CPU/memory requests and limits** on every worker pod.

**Acceptance criteria**

- **Given** Temporal up, **when** worker manifests applied, **then** six Deployments roll out and pods become Ready with readiness probes where configured.
- [x] Each worker Deployment declares **requests** and **limits**; README ties values to default minikube profile.

**Dependencies**: K8-03, OB-05, API-02 (queue names).  
**Effort**: 4h (split: K8-04a workflow worker, K8-04b operator workers).  
**Type**: infra.

---

## K8-05 — Deploy scripts (`deploy.sh` / `deploy.ps1`)

**Description**: Idempotent `kubectl apply` sequence; namespace `temporal`; non-zero exit with actionable errors.

**Acceptance criteria**

- **Given** prerequisites, **when** script runs with invalid kube context, **then** exit non-zero and stderr explains fix.
- [x] README duplicates raw `kubectl` steps for users skipping scripts.

**Dependencies**: K8-04.  
**Effort**: 2–3h.  
**Type**: infra / docs.

---

## K8-06 — Trigger script (complex expression)

**Description**: Start workflow with expression covering multiple operators, parens, exponent; print result or clear failure.

**Acceptance criteria**

- **Given** cluster up, **when** trigger script runs, **then** output is final decimal string or explicit workflow failure reason.

**Dependencies**: K8-04; client using API-01.  
**Effort**: 1–2h.  
**Type**: feature / docs.

---

## K8-07 — Troubleshooting / runbook section

**Description**: Logs, restart, connection refused, wrong namespace; **`kubectl rollout status` / `kubectl rollout undo`** for worker Deployments; **data loss** caveat if Postgres uses `emptyDir` or PVC is deleted; **`kubectl port-forward`** to **`127.0.0.1`** and short “do not expose Temporal to LAN” note; **`metrics-server`** prerequisite and install pointer when using HPA (bonus). **Pre-deploy checklist** for evaluators lives in **DOC-03** (echoes [requirements-architecture.md](../requirements/requirements-architecture.md#cross-cutting-guardrails)); keep this section focused on **Troubleshooting** to avoid duplication.

**Acceptance criteria**

- [x] README subsection “Troubleshooting” covers the bullets above in scannable form.

**Dependencies**: K8-05.  
**Effort**: 1–2h.  
**Type**: docs.

---

## K8-04a / K8-04b (optional split)

**K8-04a**: Single generic worker Deployment template + one operator; validate pattern.  
**K8-04b**: Replicate to remaining five queues.  
**Effort**: 2h + 2h.  
**Type**: infra.
