# Feature: Worker SDK

**Type**: feature  
**Priority**: P0  
**Dependencies**: Python + **Poetry**; `temporalio` (versions pinned in `pyproject.toml`; document in README).

## Description

Provide a small framework for running Temporal workers that other teams can adopt. Configuration is **environment-driven**; bootstrap is standardized and documented.

## Task breakdown

Canonical tasks (acceptance criteria, dependencies, effort): [`../tasks/feature-worker-sdk.tasks.md`](../tasks/feature-worker-sdk.tasks.md). Planning order: [`../tasks/priority-and-dependency-order.md`](../tasks/priority-and-dependency-order.md).

## Out of scope (MVP)

- Multi-namespace federation.
- Dynamic plugin loading from arbitrary JARs/Wheels.

## Related

- [feature-observability-graceful-shutdown.md](./feature-observability-graceful-shutdown.md)
- [api-workflow-activity-contracts.md](./api-workflow-activity-contracts.md)
- [requirements-decisions.md](../requirements/requirements-decisions.md)
- [requirements-project.md](../requirements/requirements-project.md)
