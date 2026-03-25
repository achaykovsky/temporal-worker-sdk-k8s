# Feature: Local Kubernetes Deployment

**Type**: infra  
**Priority**: P0  
**Dependencies**: [feature-worker-sdk.md](./feature-worker-sdk.md), [feature-observability-graceful-shutdown.md](./feature-observability-graceful-shutdown.md) (for probes)

## Description

Run the system on a **local** Kubernetes cluster. **Primary target: minikube** (document profile, resources, and image load, e.g. `minikube image load` or registry). Optional: note **kind** compatibility without making it the default path.

**MVP:** **Kubernetes YAML manifests** + **`kubectl apply`** (via locked deploy scripts). **Helm** for the Temporal stack is **out of MVP** unless explicitly adopted—see [FUTURE.md](../FUTURE.md). Provide **deploy** and **trigger** scripts per [requirements-decisions.md](../requirements/requirements-decisions.md).

**MVP topology (locked):** namespace **`temporal`**; in-cluster **PostgreSQL** + **`temporalio/auto-setup`** for Temporal (see [requirements-decisions.md](../requirements/requirements-decisions.md)—**pinned semver tags**, **DB env** from upstream compose); then **six worker Deployments** (one workflow + five operator queues). **Deploy** = `kubectl` to minikube; **Docker** = build/load worker image—see “Deploy scripts vs Docker” in [requirements-decisions.md](../requirements/requirements-decisions.md). Prod alternatives: [FUTURE.md](../FUTURE.md).

**Ops / security (MVP):** **Secrets** for DB credentials via **`Secret`** (no committed cleartext); **requests/limits** on all Deployments per decisions; **runbook** covers **`kubectl rollout undo`**, **`metrics-server`** prerequisite if HPA is used, and safe **`kubectl port-forward`** (default `127.0.0.1`).

## Task breakdown

Canonical tasks: [`../tasks/feature-kubernetes-deployment.tasks.md`](../tasks/feature-kubernetes-deployment.tasks.md). Planning order: [`../tasks/priority-and-dependency-order.md`](../tasks/priority-and-dependency-order.md).

## Related

- [requirements-deliverables.md](../requirements/requirements-deliverables.md)
- [requirements-documentation.tasks.md](../tasks/requirements-documentation.tasks.md)
- [feature-autoscaling-bonus.md](./feature-autoscaling-bonus.md)
