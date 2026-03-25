# Feature: Horizontal Autoscaling (Bonus)

**Type**: feature / infra  
**Priority**: P2 — **implement last** after all P0 scope (SDK, calculator, observability, baseline K8s) is complete.  
**Dependencies**: [feature-kubernetes-deployment.md](./feature-kubernetes-deployment.md), metrics from [feature-observability-graceful-shutdown.md](./feature-observability-graceful-shutdown.md)

## Description

Implement **horizontal pod autoscaling** for worker deployments. Provide a **stress test** that ramps load up and down, and a written explanation of **which metric** scales the workers, **why** that metric, and **limitations**.

## Task breakdown

Canonical tasks: [`../tasks/feature-autoscaling-bonus.tasks.md`](../tasks/feature-autoscaling-bonus.tasks.md) (stress test must capture **replica counts plus latency or CPU** evidence per **AS-04**). Planning order: [`../tasks/priority-and-dependency-order.md`](../tasks/priority-and-dependency-order.md).

## Related

- [requirements-architecture.md](../requirements/requirements-architecture.md)
- [requirements-decisions.md](../requirements/requirements-decisions.md)
