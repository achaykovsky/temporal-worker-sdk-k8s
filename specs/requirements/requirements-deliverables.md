# Requirements: Deliverables and Disclosure

**Type**: docs / release  
**Dependencies**: [requirements-project.md](./requirements-project.md)

## Deliverables checklist

| Item | Acceptance criteria |
|------|---------------------|
| Source code | Repository builds; tests runnable via documented command; no committed secrets. |
| README | Prerequisites, install, run locally (including Kubernetes), env reference, link to design doc; link to [FUTURE.md](../FUTURE.md) for post-MVP/prod backlog. |
| Design explanation | Architecture, task queues, probes/observability, key tradeoffs ([requirements-architecture.md](./requirements-architecture.md) aligned). |
| LLM use disclosure | **Required for this project.** [requirements-llm-disclosure.md](./requirements-llm-disclosure.md) (prompts, planning approach, iterations, how to reduce). README: [AI usage](../../README.md#ai-usage). |

## README structure (minimum)

1. What the repo is (one paragraph).
2. Prerequisites (Python version, Poetry, Docker, **minikube**, `kubectl`). **MVP:** Temporal via **in-cluster manifests** + `kubectl` ([requirements-decisions.md](./requirements-decisions.md)); **Helm** for the Temporal stack is **post-MVP** unless explicitly added later ([FUTURE.md](../FUTURE.md)).
3. Quick start: apply MVP manifests / deploy scripts, then trigger a sample expression (no undocumented “install Temporal elsewhere” gap).
4. SDK usage for other teams: env vars, optional health/metrics flags.
5. Testing: unit vs integration commands.
6. **MVP note**: README or design doc points to [requirements-decisions.md](./requirements-decisions.md) for **locked MVP decisions** (expectations first, then smallest shippable path); deferred prod work lives in [FUTURE.md](../FUTURE.md).
7. **Guardrails**: README links to [requirements-architecture.md](./requirements-architecture.md#cross-cutting-guardrails) (**Cross-cutting guardrails** — pre-deploy checklist, security/performance notes) so evaluators see how MVP maps to ops and review expectations.

## Design doc location

- Preferred: `docs/design.md` **or** dedicated README section “Design”.
- Must include Mermaid or ASCII diagram consistent with [requirements-architecture.md](./requirements-architecture.md).
- **Work planning:** execution order and atomic tasks live under [`specs/tasks/`](../tasks/) ([priority-and-dependency-order.md](../tasks/priority-and-dependency-order.md)); feature specs describe *what* only and link to the matching `*.tasks.md` file.

## Acceptance criteria

- [x] A new engineer can run the calculator on local Kubernetes by following README only.
- [x] Design doc and specs do not contradict each other on queues, parsing, or probes.
- [x] [requirements-llm-disclosure.md](./requirements-llm-disclosure.md) is filled in if LLMs were used.

## Related

- [requirements-llm-disclosure.md](./requirements-llm-disclosure.md)
- [requirements-decisions.md](./requirements-decisions.md)
- [requirements-documentation.tasks.md](../tasks/requirements-documentation.tasks.md)
- [priority-and-dependency-order.md](../tasks/priority-and-dependency-order.md)
- [FUTURE.md](../FUTURE.md) (post-MVP / production backlog)
