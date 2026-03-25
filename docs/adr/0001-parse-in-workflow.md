# ADR 0001: Parse calculator expressions in the workflow

**Status:** Accepted  
**Date:** 2026-03-24  
**Spec:** [requirements-architecture.md](../../specs/requirements/requirements-architecture.md#decision-where-parsing-runs)

## Context

The reference calculator evaluates user expressions by building an AST, then scheduling one Temporal activity per binary operator on dedicated task queues. Parsing could run either **inside the workflow** (deterministic, replay-safe) or in a **dedicated activity** (heavier isolation, different versioning and determinism constraints).

Teams need a single, explicit rule so replays stay consistent and history size remains bounded by the same limits as today ([requirements-decisions.md](../../specs/requirements/requirements-decisions.md) — expression input limits).

## Decision

**Parse and build the AST inside the workflow** using only deterministic logic (`parse_calculator_expression` in `calculator.workflow`). No parse-only activity in the MVP path.

## Consequences

**Positive**

- Parsing participates in the same deterministic execution model as the rest of the workflow; replay reasoning stays local to workflow code.
- One source of truth for expression structure before activities run; fail-fast on limits before scheduling work.

**Negative**

- Parser maintenance lives in workflow-adjacent code; it must stay pure (no I/O, no nondeterministic APIs) and well-tested.

**Rejected alternative: parse activity**

- A dedicated “parse” activity would move CPU work off the workflow worker but requires **fixed workflow code / SDK versioning** and careful handling so **workflow definitions do not depend on nondeterministic or version-drifting parse behavior** across replays. Deferred unless product requirements justify the operational cost.

## References

- Implementation: [`src/calculator/workflow.py`](../../src/calculator/workflow.py)
- Contracts and limits: [`specs/features/api-workflow-activity-contracts.md`](../../specs/features/api-workflow-activity-contracts.md)
