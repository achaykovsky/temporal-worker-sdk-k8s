# Feature: Distributed Calculator Workflow

**Type**: feature  
**Priority**: P0  
**Dependencies**: [feature-worker-sdk.md](./feature-worker-sdk.md), [api-workflow-activity-contracts.md](./api-workflow-activity-contracts.md)

## Description

Implement a workflow that evaluates an arithmetic expression string such as `1 + 5^3 * (2 - 5)`. Each **operator type** runs on a **different worker and task queue**. The workflow orchestrates execution; parsing strategy is implementation-defined but must be correct and testable.

## Functional requirements

- Input: single string expression.
- **Size limits**: enforce [requirements-decisions.md](../requirements/requirements-decisions.md) **Expression input limits** (length after whitespace strip, max binary operators); reject with **non-retryable** workflow failure **before** scheduling activities when the implementation can determine over-limit cheaply (e.g. length); otherwise immediately after parse.
- Operators: `+`, `-`, `*`, `/`, `^`, parentheses `(` `)`.
- Precedence: standard arithmetic; exponentiation **higher** than `* /`; `* /` higher than `+ -`.
- Associativity: **left-associative at each precedence level** (left-to-right for equal precedence), **including `^`** (e.g. `2^3^2` → `(2^3)^2`). See [requirements-decisions.md](../requirements/requirements-decisions.md).
- Numeric type: **`decimal.Decimal`**; **quantize to 2 decimal places with `ROUND_UP` only on the final workflow result** (MVP). Activities use high-precision `str` on the wire—see [requirements-decisions.md](../requirements/requirements-decisions.md).
- Unary operators: **`+` / `-`** as in MVP (including repeated unary, e.g. `--3`); see [requirements-decisions.md](../requirements/requirements-decisions.md).

## Task breakdown

Canonical tasks: [`../tasks/feature-distributed-calculator-workflow.tasks.md`](../tasks/feature-distributed-calculator-workflow.tasks.md). Planning order: [`../tasks/priority-and-dependency-order.md`](../tasks/priority-and-dependency-order.md).

## Related

- [api-workflow-activity-contracts.md](./api-workflow-activity-contracts.md)
- [requirements-architecture.md](../requirements/requirements-architecture.md)
- [requirements-decisions.md](../requirements/requirements-decisions.md)
