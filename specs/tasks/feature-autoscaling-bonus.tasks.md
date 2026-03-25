# Tasks: Horizontal autoscaling (bonus)

**Parent spec**: [`../features/feature-autoscaling-bonus.md`](../features/feature-autoscaling-bonus.md)  
**Priority**: P2 — **after** all P0 task files in [priority-and-dependency-order.md](./priority-and-dependency-order.md) (including [requirements-documentation.tasks.md](./requirements-documentation.tasks.md)).  
**Planning**: [priority-and-dependency-order.md](./priority-and-dependency-order.md)  
**Canonical requirements**: [requirements-decisions.md](../requirements/requirements-decisions.md) · [requirements-architecture.md](../requirements/requirements-architecture.md#cross-cutting-guardrails) (**DevOps deferrals**)  
**Depends on**: [feature-kubernetes-deployment.tasks.md](./feature-kubernetes-deployment.tasks.md), metrics from [feature-observability-graceful-shutdown.tasks.md](./feature-observability-graceful-shutdown.tasks.md).

---

## AS-01 — Confirm metrics scrape from in-cluster Prometheus or kubelet metrics path

**Description**: Validate that the chosen HPA signal (MVP: CPU per decisions) is available; document if metrics server install is required.

**Acceptance criteria**

- [x] README or design doc states prerequisite (e.g. metrics-server) and verification command.

**Dependencies**: K8-04, OB-04/OB-05.  
**Effort**: 1–2h.  
**Type**: research / infra.

---

## AS-02 — Design write-up: metric choice and limitations

**Description**: CPU (or locked built-in) as signal; why for demo; limitations (lag, queue depth mismatch, server bottleneck, noisy neighbors).

**Acceptance criteria**

- [x] Section merged into design doc or README “Autoscaling (bonus)” with explicit limitations list.

**Dependencies**: AS-01.  
**Effort**: 1–2h.  
**Type**: docs.

---

## AS-03 — HorizontalPodAutoscaler manifest

**Description**: HPA targeting **one** activity worker Deployment; min/max replicas; CPU averageUtilization thresholds documented.

**Acceptance criteria**

- [x] **Given** elevated workflow load, **when** stress test runs for N minutes, **then** replica count rises above baseline (thresholds recorded in README). *(Cluster verification: README Autoscaling + [`k8s/calculator-worker-add-hpa.yaml`](../../k8s/calculator-worker-add-hpa.yaml) + [`scripts/stress_calculator_workers.py`](../../scripts/stress_calculator_workers.py).)*
- [x] **Given** load drops, **when** cooldown elapses, **then** behavior documented (including cluster policies that block scale-down).

**Dependencies**: AS-02.  
**Effort**: 2–3h.  
**Type**: infra.

---

## AS-04 — Stress test script or Job

**Description**: Configurable concurrency and duration; starts many calculator workflows. Capture **evidence** for the write-up: replica counts **and** at least one of **workflow completion latency** (p50/p95 or simple min/max), **worker CPU** snapshot, or **`kubectl top pods`** output—so scaling claims are data-backed, not replica-count-only.

**Acceptance criteria**

- [x] **Given** documented parameters, **when** stress test runs, **then** output includes before/after replica counts **and** at least one **latency or CPU** snapshot documented in README or design doc.

**Dependencies**: AS-03, K8-06 (trigger pattern).  
**Effort**: 2–4h.  
**Type**: test / infra.

---

## AS-05 — Wire HPA into deploy scripts (optional)

**Description**: If bonus is shipped with repo, add conditional or documented `kubectl apply` for HPA YAML.

**Acceptance criteria**

- [x] Deploy path documented: default MVP without HPA vs bonus apply.

**Dependencies**: AS-03, K8-05.  
**Effort**: 1h.  
**Type**: docs / infra.
