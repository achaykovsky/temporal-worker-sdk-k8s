# Tasks: Distributed calculator workflow

**Parent spec**: [`../features/feature-distributed-calculator-workflow.md`](../features/feature-distributed-calculator-workflow.md)  
**Priority**: P0  
**Planning**: [priority-and-dependency-order.md](./priority-and-dependency-order.md)  
**Canonical requirements**: [requirements-decisions.md](../requirements/requirements-decisions.md) · [requirements-architecture.md](../requirements/requirements-architecture.md#cross-cutting-guardrails)  
**Depends on**: [feature-worker-sdk.tasks.md](./feature-worker-sdk.tasks.md), [api-workflow-activity-contracts.tasks.md](./api-workflow-activity-contracts.tasks.md).

---

## DC-01 — Lexer/tokenizer unit tests

**Description**: Tokenize numbers, operators, parentheses, unary forms per decisions doc. **Before tokenize**, reject inputs over **max length** (after ignorable whitespace strip) per [requirements-decisions.md](../requirements/requirements-decisions.md).

**Acceptance criteria**

- [x] Tests cover valid tokens and reject unknown characters with defined error type.
- **Given** stripped input longer than **4096** characters, **when** workflow/parser entry runs, **then** **non-retryable** failure (no activities scheduled).

**Dependencies**: None (parallel with SDK).  
**Effort**: 2–3h.  
**Type**: test / feature.

---

## DC-02 — Parser to AST (precedence and associativity)

**Description**: Build AST matching spec: precedence, left-associativity at each level including `^`, unary `+`/`-`. After parse, enforce **max binary operators** (512); exceed → **non-retryable** failure before scheduling activities.

**Acceptance criteria**

- [x] **Given** `1 + 5^3 * (2 - 5)`, **when** AST is evaluated logically with `Decimal` rules, **then** result matches manual calculation and final `ROUND_UP` to 2dp at workflow end only.
- [x] **Given** `2^3^2`, **when** evaluated, **then** result matches left-associative rule `(2^3)^2`.
- [x] **Given** a parsed expression with **more than 512** binary operators, **when** the workflow validates the AST, **then** **non-retryable** failure (documented message).

**Dependencies**: DC-01.  
**Effort**: 3–4h.  
**Type**: feature / test.

---

## DC-03 — Malformed input handling

**Description**: Unbalanced parens, invalid tokens; workflow fails with defined application failure (no worker crash).

**Acceptance criteria**

- [x] **Given** malformed input, **when** parse/eval runs, **then** failure is typed and message is stable enough for tests.

**Dependencies**: DC-02.  
**Effort**: 1–2h.  
**Type**: feature / test.

---

## DC-04 — Activity implementations (str Decimal wire format)

**Description**: One activity per operator; operands/results as high-precision `str`; no per-activity quantize. Apply **timeouts and retry policy** consistent with README table: **non-retryable** for domain failures (e.g. divide by zero); bounded retries for transient failures—per [requirements-decisions.md](../requirements/requirements-decisions.md) (**Temporal timeouts (MVP)**).

**Acceptance criteria**

- [x] Each operator has unit tests with `Decimal` edge cases (division by zero → workflow failure path).
- [x] README (or `docs/design.md`) lists **default activity start-to-close** and **workflow** timeouts and **retry** behavior for calculator workers.

**Dependencies**: API-02.  
**Effort**: 3–4h.  
**Type**: feature / test.

---

## DC-05 — Workflow orchestration and dispatch

**Description**: Walk AST; schedule activities on correct task queues per operator; final quantize once. Document in README that **latency and history size scale ~linearly** with binary-operator count under MVP (one activity per op).

**Acceptance criteria**

- [x] **Given** expression using `+` and `*`, **when** workflow runs, **then** `+` executes only via add worker queue and `*` via multiply queue (logs with queue labels or integration test).

**Dependencies**: DC-02, DC-04, WS-04.  
**Effort**: 4h (split if needed: DC-05a skeleton, DC-05b full AST walk).  
**Type**: feature.

---

## DC-06 — Integration test against real Temporal

**Description**: Test suite target matching MVP (e.g. minikube stack per decisions); at least one multi-operator expression succeeds.

**Acceptance criteria**

- [x] **Given** running Temporal, **when** integration tests run, **then** at least one test completes a multi-operator expression end-to-end.

**Dependencies**: DC-05; **K8-04** (and upstream K8-02…K8-03) **recommended** for README-parity integration on minikube—see [priority-and-dependency-order.md](./priority-and-dependency-order.md). Optional interim stack only if it mirrors the same contracts.  
**Effort**: 3–4h.  
**Type**: test.

---

## DC-05a / DC-05b (optional split if DC-05 > 1 day)

**DC-05a**: Workflow schedules a **fixed** small AST (hard-coded two operations) to prove queue routing.  
**DC-05b**: Replace with full AST walker.  
**Effort**: 2h + 2h.  
**Type**: feature.
