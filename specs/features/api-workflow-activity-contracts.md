# API: Workflow and Activity Contracts (Temporal)

**Type**: api (boundary definitions)  
**Priority**: P0  
**Dependencies**: **None** for authoring the contract. **Implementation verification** (types, queues, dispatch tests) depends on [feature-distributed-calculator-workflow.md](./feature-distributed-calculator-workflow.md) and the reference client.

## Description

Define stable **workflow input/output** and **activity signatures** for the calculator. This is the contract between client, workflow, activities, and workers. Update this spec if types change.

## Workflow

| Field | Detail |
|-------|--------|
| Name | **`CalculatorWorkflow`** (MVP; document if renamed). |
| Workflow task queue | **`calc-workflows`** (client starts workflow here). |
| Input | Single string: arithmetic expression. |
| Input limits | **Enforced in workflow** (and optionally client): max length and max binary operators per [requirements-decisions.md](../requirements/requirements-decisions.md) (**Expression input limits**); exceed → **non-retryable** application failure. |
| Output | **Final** result: `str` decimal quantized to **2 decimal places** with **`ROUND_UP`**, **or** structured workflow failure. **MVP:** quantize **once** at workflow end; activities exchange **high-precision `str`**—see [requirements-decisions.md](../requirements/requirements-decisions.md). |
| Idempotency | Client may pass workflow id; document retry policy for starts. |

**Acceptance criteria**

- [ ] Workflow name and argument types match client trigger script and tests.

## Activities (per operator)

Each activity handles **one binary operation**. **MVP:** operands and return values are **`str`** encoding of `Decimal` at **full internal precision** (no per-activity quantize); workflow applies **final** quantize—see [requirements-decisions.md](../requirements/requirements-decisions.md).

| Operator | Activity name (MVP) | Task queue (MVP) |
|----------|---------------------|------------------|
| `+` | `add` | `calc-add` |
| `-` | `subtract` | `calc-sub` |
| `*` | `multiply` | `calc-mul` |
| `/` | `divide` | `calc-div` |
| `^` | `power` | `calc-pow` |

**Normative split:** **Task queue** names are locked in [requirements-decisions.md](../requirements/requirements-decisions.md). **Activity type names** (`add`, `subtract`, …) and the operator↔queue mapping **in this table** are the API contract—keep code, tests, and README in sync with this file.

**Acceptance criteria**

- **Given** workflow code, **when** it schedules `+`, **then** only the add activity on the add queue is invoked (enforced by integration test or worker registration matrix).

## Errors

- **Domain**: division by zero, invalid parse, **input over limit** → **fail workflow** with explicit application failure (non-retryable where appropriate); document message shape. See [requirements-decisions.md](../requirements/requirements-decisions.md).
- **Infra**: activity timeout → retry policy documented; do not swallow errors without logging.

## Versioning

If workflow logic changes in a breaking way, use **Temporal workflow versioning** (patch or new workflow type) and document migration for in-flight runs.

**MVP guidance for this repo**

- **Compatible changes** (e.g. new optional query, stricter validation that still accepts all previously valid inputs, bug fixes that do not alter history for past inputs): ship as a **patch** (or minor) version of the application/SDK; use Temporal **patches** inside the workflow when the SDK requires `patched`/`deprecate_patch` style changes, per [Temporal workflow versioning](https://docs.temporal.io/workflows#versioning) docs.
- **Breaking workflow history** (different sequence of commands for the same workflow input, renamed workflow type, incompatible activity argument shapes): add a **new workflow type** (e.g. `CalculatorWorkflowV2`) or a new `@workflow.defn` name, deploy workers that register both types during migration, and point new starters at the new type. Bump **minor/major** per [CHANGELOG.md](../../CHANGELOG.md) policy.
- **Contract constants** (queue names, activity type strings, `WORKFLOW_NAME`): treated as **public API**; changing them without dual registration is **breaking** — update [api-workflow-activity-contracts.md](./api-workflow-activity-contracts.md) and [requirements-decisions.md](../requirements/requirements-decisions.md) together.

## Related

- [requirements-architecture.md](../requirements/requirements-architecture.md)
- [requirements-decisions.md](../requirements/requirements-decisions.md)
- [feature-distributed-calculator-workflow.md](./feature-distributed-calculator-workflow.md)
- Task breakdown: [`../tasks/api-workflow-activity-contracts.tasks.md`](../tasks/api-workflow-activity-contracts.tasks.md)
