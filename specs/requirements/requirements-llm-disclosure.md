# Requirements: LLM Use Disclosure

**Type**: docs  
**Dependencies**: [requirements-deliverables.md](./requirements-deliverables.md)  
**Status**: Fill in during / after implementation. **This file is the canonical disclosure** (README may link here).

## Policy

Any substantive use of an LLM for this repository (planning, code generation, debugging, docs) must be summarized here so evaluators can reproduce context.

## Disclosure template

### Prompts

- **Planning / architecture**: (paste or summarize key prompts; redact secrets and internal URLs.)
- **Implementation**: (per area if materially different: SDK, workflow, K8s, tests.)
- **Docs / specs**: (if LLM-assisted.)

### Planning approach

- How requirements were broken down (e.g. specs-first, test-first).
- Which documents were treated as source of truth (`instructions`, `specs/`, etc.).

### Iterations

- **Approximate number of LLM-assisted iterations** (sessions or major revise cycles) for the deliverable.
- **What changed most across iterations** (e.g. probe design, queue layout, rounding rules).

### How iterations could be reduced

- Up-front decisions that would have avoided rework (e.g. fixed associativity and `Decimal` policy on day one).
- Smaller scope slices or stricter acceptance tests earlier.

## Acceptance criteria

- [ ] This file is complete before submission/review if LLMs were used.
- [ ] No secrets, credentials, or private URLs in pasted prompts.
