# Requirements: Temporal Worker SDK + Local Kubernetes

**Source**: Project `instructions` (Infra / Platform Engineer objective).

**Goal**: Build a small Temporal-based distributed system, package it as a reusable worker SDK, and run it locally on Kubernetes. Emphasize correctness, platform thinking, and engineering quality.

**Stack (resolved)**: Python, **Poetry** (when code is added), Temporal Python SDK (`temporalio`). Local Kubernetes: **minikube**. **All MVP vs prod choices:** [requirements-decisions.md](./requirements-decisions.md); **prod backlog:** [FUTURE.md](../FUTURE.md). LLM disclosure: [requirements-llm-disclosure.md](./requirements-llm-disclosure.md).

**Repo status:** planning/specs first; implementation follows the locked MVP table in [requirements-decisions.md](./requirements-decisions.md).

## Prioritization

| ID | Requirement | Priority | Spec |
|----|-------------|----------|------|
| R1 | Worker SDK (bootstrap, env config, multi-team reuse) | P0 | [feature-worker-sdk.md](../features/feature-worker-sdk.md) |
| R1a | Workflow/activity **contracts** (queues, types, limits) | P0 | [api-workflow-activity-contracts.md](../features/api-workflow-activity-contracts.md) |
| R2 | Distributed calculator workflow (expression string, operators, queues) | P0 | [feature-distributed-calculator-workflow.md](../features/feature-distributed-calculator-workflow.md) |
| R3 | SDK upgrades: graceful shutdown, metrics, logs, liveness/readiness without breaking existing workers | P0 | [feature-observability-graceful-shutdown.md](../features/feature-observability-graceful-shutdown.md) |
| R4 | Kubernetes: **minikube**, **manifests + kubectl** (MVP), deploy + trigger scripts | P0 | [feature-kubernetes-deployment.md](../features/feature-kubernetes-deployment.md) |
| R5 | Bonus: horizontal autoscaling, stress test, metric rationale + limitations | P2 (last) | [feature-autoscaling-bonus.md](../features/feature-autoscaling-bonus.md) |

## Non-functional expectations (evaluation)

- Engineering quality: tests, structure, dependency hygiene.
- System design: clear boundaries, documented tradeoffs ([requirements-architecture.md](./requirements-architecture.md)).
- Clarity: README, design explanation, runbooks where relevant.

## Dependencies (implementation order)

Authoritative **task DAG** and waves: [priority-and-dependency-order.md](../tasks/priority-and-dependency-order.md). Summary (must not contradict that file):

1. SDK skeleton + env bootstrap ([feature-worker-sdk.md](../features/feature-worker-sdk.md)).
2. API contract types + queues ([api-workflow-activity-contracts.md](../features/api-workflow-activity-contracts.md)); then calculator workflow + activities ([feature-distributed-calculator-workflow.md](../features/feature-distributed-calculator-workflow.md)).
3. Observability + health + graceful shutdown ([feature-observability-graceful-shutdown.md](../features/feature-observability-graceful-shutdown.md)).
4. Kubernetes packaging and scripts ([feature-kubernetes-deployment.md](../features/feature-kubernetes-deployment.md)); README/deliverables closeout per [requirements-documentation.tasks.md](../tasks/requirements-documentation.tasks.md).
5. **Last**: autoscaling and stress validation ([feature-autoscaling-bonus.md](../features/feature-autoscaling-bonus.md)) after P0 is done.

## Related

- [requirements-decisions.md](./requirements-decisions.md)
- [requirements-architecture.md](./requirements-architecture.md)
- [requirements-deliverables.md](./requirements-deliverables.md)
- [requirements-llm-disclosure.md](./requirements-llm-disclosure.md)
- [priority-and-dependency-order.md](../tasks/priority-and-dependency-order.md)
