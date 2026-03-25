# Requirements: LLM use disclosure

**Type:** docs  
**Dependencies:** [requirements-deliverables.md](./requirements-deliverables.md)  
**Status:** Completed for submission. **Canonical detail** for evaluator questions; [README.md](../../README.md#ai-usage) has a short summary.

## Policy

Substantive use of an LLM (planning, code generation, debugging, documentation) is summarized here so reviewers can understand context. Prompts below are **themes**, not verbatim logs; redact secrets and private URLs in any paste you add later.

## Prompts

### Planning / architecture

- Align worker SDK responsibilities with Temporal Python patterns: env-based bootstrap, optional HTTP sidecar for probes and metrics, graceful shutdown on SIGTERM/SIGINT.
- Map assignment requirements (multi-queue calculator, Kubernetes, optional HPA) to a minimal manifest set and scripts.
- Resolve deterministic-workflow constraints vs parsing: document parse-in-workflow in an ADR.

### Implementation

- **SDK:** config loading, metrics registry isolation, observability interceptor, health handler behavior (ready only after polling starts; 503 when draining).
- **Calculator:** expression parser, precedence/associativity, `Decimal` string payloads, workflow orchestration per operator queue.
- **Kubernetes:** Deployments, ConfigMap, Secret workflow, HPA manifest and stress script.
- **Tests:** unit tests without Temporal; integration tests with time-skipping server.

### Docs / specs

- README readability, deliverable mapping, autoscaling explanation (metric choice, limitations), and cross-links to architecture and FUTURE backlog.

## Planning approach

- **Source of truth:** root `instructions`, then `specs/` (requirements, features, tasks). Locked behavior lives in `requirements-decisions.md`; deferred production work in `FUTURE.md`.
- **Specs-first:** decisions and contracts before broad coding; ADRs for choices that are not obvious from code alone.
- **Verification:** `pytest` for regression; manual minikube path documented for end-to-end checks.

## Iterations

- **Approximate count:** multiple conversational sessions over the lifetime of the repo; an exact tally was not recorded.
- **What changed most across iterations:** tightening env/probe contracts so existing workers need no code changes for probes; aligning calculator numeric/rounding rules with the decisions doc; consolidating Kubernetes deploy paths and HPA documentation.

## How iterations could be reduced

- **Decide early:** decimal quantization, associativity for `^`, and max input limits in one pass—avoids parser/workflow churn.
- **Freeze interfaces:** public SDK symbols and env var names before parallelizing K8s and example workers.
- **Earlier integration gates:** Temporal in CI (service container or Testcontainers) reduces late discovery of workflow or timeout issues.
- **Single deploy surface sooner:** one script or pipeline as the default, with the other as thin wrapper, to avoid duplicate drift.

## Acceptance criteria

- [x] This file is complete before submission/review when LLMs were used.
- [x] No secrets, credentials, or private URLs in pasted prompts (none included verbatim here).
