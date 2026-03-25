# Tasks: Requirements documentation (README, design)

**Parent specs**: [requirements-deliverables.md](../requirements/requirements-deliverables.md), [requirements-architecture.md](../requirements/requirements-architecture.md)  
**Priority**: P0 (close before calling MVP “evaluator-ready”)  
**Planning**: [priority-and-dependency-order.md](./priority-and-dependency-order.md)

**Depends on**: Deploy/trigger path documented ([feature-kubernetes-deployment.tasks.md](./feature-kubernetes-deployment.tasks.md) **K8-05** minimum for a coherent README quick start). ADR can be written from specs **without** waiting on code.

**Blocks**: None; runs in parallel with late Wave 3–4 once README skeleton exists.

---

## DOC-01 — README: deliverables and guardrails link

**Description**: Satisfy [requirements-deliverables.md](../requirements/requirements-deliverables.md): structure items 1–6, plus **item 7** — link to [requirements-architecture.md](../requirements/requirements-architecture.md#cross-cutting-guardrails) (**Cross-cutting guardrails**). Include pointers to [requirements-decisions.md](../requirements/requirements-decisions.md) and [FUTURE.md](../FUTURE.md) per deliverables doc.

**Acceptance criteria**

- [x] README includes explicit link to **Cross-cutting guardrails** in requirements-architecture.
- [x] README points to **locked decisions** and **FUTURE** backlog as specified in deliverables.

**Dependencies**: K8-05 (README quick start + kubectl echo in place).  
**Effort**: 1h.  
**Type**: docs.

---

## DOC-02 — ADR or design: parse-in-workflow

**Description**: Satisfy [requirements-architecture.md](../requirements/requirements-architecture.md) acceptance: **`docs/adr/`** entry (e.g. `0001-parse-in-workflow.md`) **or** equivalent “Design” section in README/`docs/design.md` with **Context / Decision / Consequences** per `.cursor/rules/architecture.mdc`.

**Acceptance criteria**

- [x] ADR or design section states **where parsing runs**, **why**, and **rejected alternative** (parse activity) at a glance.

**Dependencies**: None (specs are the source of truth; refine after DC-05 if needed).  
**Effort**: 1–2h.  
**Type**: docs.

---

## DOC-03 — README pre-deploy checklist (minikube)

**Description**: Add a short **Pre-deploy (local)** subsection to README that mirrors the **Pre-deploy** table in [requirements-architecture.md](../requirements/requirements-architecture.md#cross-cutting-guardrails) (tests, secrets, lockfile, smoke)—scannable bullets; link to that section for full context.

**Acceptance criteria**

- [x] Checklist is scannable (bullet list); links to **Cross-cutting guardrails** for detail (no duplicate long form).

**Dependencies**: DOC-01; K8-07 (troubleshooting/runbook tone consistent).  
**Effort**: 0.5–1h.  
**Type**: docs.
