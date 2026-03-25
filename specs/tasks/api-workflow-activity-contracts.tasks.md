# Tasks: Workflow and activity contracts (API)

**Parent spec**: [`../features/api-workflow-activity-contracts.md`](../features/api-workflow-activity-contracts.md)  
**Priority**: P0  
**Planning**: [priority-and-dependency-order.md](./priority-and-dependency-order.md)  
**Canonical requirements**: [requirements-decisions.md](../requirements/requirements-decisions.md) · [requirements-architecture.md](../requirements/requirements-architecture.md#cross-cutting-guardrails)  
**Blocks**: Calculator workflow implementation and client/trigger scripts (types, names, queues).

---

## API-01 — Encode workflow contract in shared types

**Description**: Workflow name `CalculatorWorkflow`, input `str`, output `str` (final quantize per decisions), workflow task queue `calc-workflows` — as constants or Pydantic/dataclass DTOs used by client and worker. Include **constants** for **expression max length** and **max binary operators** matching [requirements-decisions.md](../requirements/requirements-decisions.md) (single source of truth for client precheck if implemented).

**Acceptance criteria**

- [x] Single source of truth for workflow name and queue string; imported by starter and worker registration.
- [x] Input/output types match spec (expression string; result string or structured failure path documented).
- [x] Limit constants match decisions doc numerically (4096 chars, 512 binary ops).

**PM validation (2026-03-23)**: `calculator.contracts` defines `WORKFLOW_NAME`, `WORKFLOW_TASK_QUEUE`, `EXPRESSION_MAX_CHARS`, `MAX_BINARY_OPERATORS_IN_EXPRESSION`; workflow docstring documents `str` I/O and final quantize; failures via `ApplicationError` (see `calculator.errors`). Starters/workers import these symbols from `calculator` / `calculator.contracts`.

**Dependencies**: WS-05 recommended (shared package layout).  
**Effort**: 2–3h.  
**Type**: feature.

---

## API-02 — Encode per-operator activity names and task queues

**Description**: Map operators `+`, `-`, `*`, `/`, `^` to activity names and queues per spec table (`add` / `calc-add`, etc.).

**Acceptance criteria**

- [x] Table in spec is reproducible as code (dict or enum) with no mismatched spelling.
- [x] README or module doc duplicates the table for operators skimming docs only.

**PM validation (2026-03-23)**: `activity_and_queue_for_binary_operator` + README **Calculator API** table mirror [api-workflow-activity-contracts.md](../features/api-workflow-activity-contracts.md).

**Dependencies**: API-01.  
**Effort**: 1–2h.  
**Type**: feature / docs.

---

## API-03 — Document error and failure shapes

**Description**: Application failures for division by zero, invalid parse, **input over limit** (length / binary-operator cap); non-retryable vs retryable; message shape for operators—aligned with [api-workflow-activity-contracts.md](../features/api-workflow-activity-contracts.md) **Errors** and [requirements-decisions.md](../requirements/requirements-decisions.md).

**Acceptance criteria**

- [x] Spec section mirrored in short “Errors” doc or docstring; links to [requirements-decisions.md](../requirements/requirements-decisions.md).
- [x] At least one unit test or workflow test asserts failure type/message for one invalid case (can land with calculator tasks if faster).

**PM validation (2026-03-23)**: Module `calculator.errors` + `tests/test_errors_and_limits.py` (length limit, invalid parse `ApplicationError.non_retryable`, message content).

**Dependencies**: API-01.  
**Effort**: 1–2h.  
**Type**: docs / test.

---

## API-04 — Registration matrix test

**Description**: Prove `+` schedules only the add activity on `calc-add` (and analogous checks or parameterized matrix).

**Acceptance criteria**

- [x] **Given** workflow code, **when** expression uses `+` and `*`, **then** tests prove dispatch targets the correct activity names/queues (integration or isolated registration test per parent spec).

**PM validation (2026-03-23)**: Parametrized routing tests in `tests/test_routing_matrix.py` (CI); `CalculatorWorkflow` + `tests/test_calculator_workflow_integration.py` exercises `1+2` / `3*4` against real activities on `calc-add` / `calc-mul` (marked `@pytest.mark.integration`, excluded from default CI per decisions).

**Dependencies**: API-02; calculator workflow dispatch — **after** DC-05 (or DC-05a routing proof).  
**Effort**: 2–4h.  
**Type**: test.

---

## API-05 — Versioning note for breaking workflow changes

**Description**: Document Temporal workflow versioning approach when logic changes incompatibly.

**Acceptance criteria**

- [x] Paragraph in spec or README points to patch vs new workflow type; owners know when to bump.

**PM validation (2026-03-23)**: **Versioning** expanded in [api-workflow-activity-contracts.md](../features/api-workflow-activity-contracts.md); README **Calculator API** links to spec + [CHANGELOG.md](../../CHANGELOG.md).

**Dependencies**: None (can parallelize).  
**Effort**: 1h.  
**Type**: docs.
