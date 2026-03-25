# Feature: Graceful Shutdown, Observability, Health Probes

**Type**: feature / infra  
**Priority**: P0  
**Dependencies**: [feature-worker-sdk.md](./feature-worker-sdk.md)

## Description

Upgrade the SDK with **graceful shutdown**, **basic observability** (metrics + structured logs), and **liveness/readiness** probes. Existing workers must not require code changes beyond bumping the SDK and setting env/config as documented; **no new mandatory application hooks** for probes.

## Task breakdown

Canonical tasks: [`../tasks/feature-observability-graceful-shutdown.tasks.md`](../tasks/feature-observability-graceful-shutdown.tasks.md). Planning order: [`../tasks/priority-and-dependency-order.md`](../tasks/priority-and-dependency-order.md).

## Related

- [feature-kubernetes-deployment.md](./feature-kubernetes-deployment.md)
- [requirements-decisions.md](../requirements/requirements-decisions.md)
