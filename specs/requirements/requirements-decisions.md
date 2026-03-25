# Requirements: Locked MVP decisions

**Type**: requirements  
**Dependencies**: [requirements-project.md](./requirements-project.md)

**No open MVP questions**: product and technical choices for the shippable scope are decided in this document. Implementation only **writes concrete literals** (image tags, lockfile versions) where the MVP table already requires pinned semver—those are **artifacts**, not pending decisions. Post-MVP alternatives live in [FUTURE.md](../FUTURE.md).

## Decision priority

1. **Match stated requirements** in project `instructions` and **reasonable user/evaluator expectations** (correct calculator behavior, reproducible local run, clear errors, documented scripts).
2. **MVP scope**: choose the **smallest** option that satisfies (1)—fewer components, minimal config, defaults that work on a laptop/minikube. Defer non-essential polish and production hardening unless it is required to meet (1).
3. Only then optimize for implementation convenience, repo size, or internal patterns.

When options conflict, **(1) beats (2) beats (3)**. Production-oriented alternatives to each MVP choice are listed in [FUTURE.md](../FUTURE.md).

---

## Resolved (stakeholder input)

| Topic | Decision |
|-------|----------|
| Implementation language | **Python** (`temporalio`). |
| Dependency manager | **Poetry**; lockfile committed when code exists. |
| Local Kubernetes | **minikube** as the primary documented cluster (`kubectl` context). |
| Associativity | **Left-to-right for operators of the same precedence** (left-associative), including `^`. **Standard precedence**: `^` > `* /` > `+ -`. Example: `2^3^2` → `(2^3)^2` = 64. |
| Numeric model | **`decimal.Decimal`**; **quantize to 2 decimal places** with **`ROUND_UP`** on the **final workflow result** (see MVP table for intermediates). |
| Bonus autoscaling | **In scope**, priority **last** (after all P0 deliverables). |
| LLM disclosure | **Required**; canonical content in [requirements-llm-disclosure.md](./requirements-llm-disclosure.md). |

---

## Resolved (expectations-first)

| Topic | Decision | Rationale |
|-------|----------|-----------|
| Unary operators | **Unary `+` and `-`** (e.g. `-3+5`, `--3`); full grammar in MVP table below. | Calculator expectation. |
| Division by zero | **Fail the workflow** with explicit **non-retryable** application error. | Clear failure, not bogus numeric success. |
| Temporal on cluster | **Temporal runs on minikube** as part of the **documented primary deploy path** (no undocumented “install Temporal yourself” gap). | `instructions`: everything on local Kubernetes. |
| Workflow trigger | **Trigger script** on README happy path. | Meets “script to trigger a complex calculation.” |
| Health / metrics HTTP | **Single port**: `/livez`, `/readyz`, `/metrics`. **Readiness** = worker **started** run loop and **polling**. **Liveness** = process responds. | SDK upgrade enables probes via env; minimal surface. |

---

## MVP locked decisions (implementation)

These are **chosen** for the first shippable version. They **meet** `instructions` + expectations + MVP priority. **Do not** treat the “Prod alternative” column as in scope for MVP—that content belongs in [FUTURE.md](../FUTURE.md).

| Area | MVP decision | Prod alternative (see FUTURE.md) |
|------|----------------|----------------------------------|
| **Temporal packaging** | **In-cluster PostgreSQL** + **`temporalio/auto-setup`** Deployment/Service (frontend `:7233`), same namespace; deploy applies manifests in order (postgres → temporal → workers). **Image tags:** pinned **semver** (not `latest`); exact versions recorded in manifests/README when implementation lands. | Image **digests**; full Helm; HA; external managed DB; TLS. |
| **Temporal resources** | Minimal CPU/memory; **emptyDir** or small PVC; **Kubernetes namespace `temporal`** (dedicated; not `default`). Every workload **Deployment** (Postgres, Temporal, six workers) declares **CPU/memory requests and limits** in manifests; README explains minikube profile assumptions and when to raise limits. | Sized persistence, HA, backups, retention tuning. |
| **Kubernetes secrets** | **DB passwords** and other sensitive strings live in **`Secret`** (or are applied locally via `kubectl create secret`); **no** cleartext credentials in **committed** YAML. Use **`*.example`** manifests, `secretGenerator`, or documented one-liner to create secrets; ConfigMap only for non-sensitive Temporal **address/namespace** keys. | External Secrets, SealedSecrets, Vault, rotation automation. |
| **Rollback / recovery** | README **Troubleshooting** includes **`kubectl rollout status` / `kubectl rollout undo`** for worker Deployments and notes **data persistence** caveat (Postgres `emptyDir` / PVC loss on delete). | GitOps revert, canary, DR runbooks. |
| **Temporal timeouts (MVP)** | README documents **chosen defaults** for **workflow** and **activity** timeouts and **retry policies** (activity failures: division by zero / parse errors **non-retryable** per domain rules; infra timeouts retry with backoff as appropriate). Same policy family across all five activity workers unless a table justifies an exception. | Dynamic config, per-namespace policy, advanced retry tuning. |
| **`auto-setup` DB env** | Match **Temporal upstream Postgres docker-compose** for the pinned `temporalio/auto-setup` tag (e.g. **`DB=postgres12`**, **`DB_PORT=5432`**, **`POSTGRES_SEEDS`** / user / password pointing at the in-cluster Postgres `Service`). README notes values are aligned with upstream for that image version. | Custom DB topology; TLS to Postgres; external RDS. |
| **Worker image** | **One image**, **six roles** via env (`WORKER_ROLE=workflow` \| `add` \| `sub` \| `mul` \| `div` \| `pow`); each Deployment sets `TEMPORAL_TASK_QUEUE` + role. | Multi-image, hardened bases, SBOM/signing. |
| **Worker Dockerfile (DevOps)** | **Multi-stage** build; **non-root** user; order layers **dependencies before app** code; use **`COPY --chown`** (or equivalent) where the base supports it. **Health:** **Kubernetes** liveness/readiness are primary when `TEMPORAL_WORKER_HEALTH_ADDR` is set on workers. **Docker `HEALTHCHECK`:** optional for MVP—either add a check when the default CMD always exposes `/livez`, or **document omission** and rely on K8s probes. | Mandatory `HEALTHCHECK`; image scan (Trivy/Snyk) in CI; distroless/minimal base. |
| **Task queues (short names)** | Workflow queue: `calc-workflows`. Activities: `calc-add`, `calc-sub`, `calc-mul`, `calc-div`, `calc-pow`. | Prefixed queues for multi-tenant namespaces. |
| **Workflow type name** | **`CalculatorWorkflow`** (same as [api-workflow-activity-contracts.md](../features/api-workflow-activity-contracts.md); document only if renamed before release). | Versioned workflow names / `v2` types. |
| **Expression input limits** | After **ignorable whitespace** removal (per input charset rules): max **4096** characters; max **512** binary operators in the **parsed** expression. Exceeding either → **non-retryable** application failure; **reject before scheduling activities** once parse confirms size (fail fast on length before full parse if implemented). | Higher limits; streaming; batched activities; rate limits at gateway. |
| **Trigger script** | **Python** + **`temporalio`** on host + documented **`kubectl port-forward`** to Temporal frontend (`127.0.0.1` by default; document if binding elsewhere). | In-cluster Job; `temporal` CLI only; no host Python. |
| **Deploy scripts** | **`scripts/deploy.sh`** and **`scripts/deploy.ps1`**, each a **thin wrapper** around the **same** ordered **`kubectl apply`** (or equivalent) sequence against namespace **`temporal`** (create namespace if missing). **Not** per-Linux-distro variants—only POSIX vs Windows **host** shells. | Single CI pipeline; Terraform/GitOps; Helm-only with no shell wrappers. |
| **Health / metrics bind (SDK)** | Optional env **`TEMPORAL_WORKER_HEALTH_ADDR`** (e.g. `0.0.0.0:8080`). **Unset** = no HTTP server (backward compatible). Serves **`/livez`**, **`/readyz`**, **`/metrics`** on that one bind address. | Split ports; separate scrape endpoint policy. |
| **CI / automated integration** | **No** Temporal integration in CI for MVP; **local + README** path is the gate. **Recommended:** CI runs **`pytest`** (or equivalent) for **unit** tests + **`poetry check`** / lockfile sanity; optional **`pip-audit`** / **`poetry audit`** on a schedule or PR if available. | Service container / Testcontainers; full parity gates. |
| **Decimal quantize timing** | **Quantize once** at **workflow completion** (2dp `ROUND_UP`). Activities pass **high-precision** `str` decimals internally. | Quantize per operation; different rounding modes. |
| **Wire format (workflow ↔ activities)** | **`str`** encoding of `Decimal` (no `float` on the wire). | Typed payloads / protobuf; shared schema registry. |
| **Unary operators** | Support **unary `+` and `-`**, including **repeated** unary (e.g. `--3`). | Restrict grammar; stricter validation docs. |
| **Input charset** | **ASCII**; **ignore whitespace**; digits, `.`, operators, parentheses only. | Locale decimal comma, `×`, thousands separators. |
| **Exponent (`^`)** | **Integer exponent only**: after evaluating the right subtree, value must be **integral** (e.g. allow `2^(1+2)`); otherwise fail workflow. | Decimal / fractional exponents. |
| **Workflow run id** | **Random UUID** (or unique id) per trigger invocation to avoid start conflicts. | Deterministic ids for replay debugging. |
| **Repo layout** | **Single Poetry project**: `src/temporal_worker_sdk/` + `src/calculator/` (reference app using the SDK). | Split publishable package vs app; monorepo tooling. |
| **Logging** | **`logging`** to stdout; **JSON** when `LOG_JSON` truthy; no extra structured-log dep for MVP. **SDK default:** do **not** log full raw **workflow/activity arguments** (e.g. entire expression string) at INFO; use **truncated** or **hashed** payload in debug behind a flag, or omit—so adopters do not leak user input by default. | `structlog`, log shipping agents, correlation standards, DLP. |
| **Metrics** | **`prometheus_client`**; expose via **`/metrics`** on SDK health server when enabled. Low-cardinality labels only (`activity` name). **Histograms** (e.g. poll latency): use **documented** bucket boundaries; avoid excessive bucket count. | OTel traces/metrics; high-cardinality policy review. |
| **Graceful shutdown** | Use **Temporal worker `shutdown()`** with **configured graceful window** (SDK support); **SIGTERM** in container. | Stricter drain guarantees, preStop hooks tuning. |
| **Bonus (when done)** | **CPU-based HPA** on **one** activity worker Deployment + **stress script** (Python or shell) documented with **metric choice + limitations**. | KEDA / custom metrics / queue-depth scaling. |

---

## Spec alignment

Cross-check when this file or behavior-affecting specs change:

- [requirements-project.md](./requirements-project.md)
- [requirements-architecture.md](./requirements-architecture.md) (includes **Cross-cutting guardrails**)
- [priority-and-dependency-order.md](../tasks/priority-and-dependency-order.md) and matching `*.tasks.md` under [`specs/tasks/`](../tasks/) (**canonical** work breakdown; feature specs link here—do not duplicate task lists in `specs/features/`)
- [api-workflow-activity-contracts.md](../features/api-workflow-activity-contracts.md)
- [feature-worker-sdk.md](../features/feature-worker-sdk.md)
- [feature-distributed-calculator-workflow.md](../features/feature-distributed-calculator-workflow.md)
- [feature-observability-graceful-shutdown.md](../features/feature-observability-graceful-shutdown.md)
- [feature-kubernetes-deployment.md](../features/feature-kubernetes-deployment.md)
- [feature-autoscaling-bonus.md](../features/feature-autoscaling-bonus.md)

**Infra pins** (semver tags not `latest`, `DB=postgres12`-style env for `auto-setup`, namespace **`temporal`**) are defined only in the **MVP locked decisions** table above—no separate duplicate table.

**Quality gates:** [.cursor/rules/planning.mdc](../../.cursor/rules/planning.mdc) and [requirements-architecture.md](./requirements-architecture.md#cross-cutting-guardrails) (security, performance, DevOps, pre-deploy — aligned with specs and tasks).

---

## Deploy scripts vs Docker (clarification)

**Deploying to the cluster is not “per Linux distro.”** Scripts (or documented `kubectl`/`kustomize`/`helm` steps) talk to the **Kubernetes API** via **`kubectl`** against **minikube**. Any recent Linux/macOS/Windows environment only needs a working **`kubectl`** context pointed at minikube—not separate scripts for Ubuntu vs Fedora vs Debian.

**Docker’s role (separate):**

- **Build** the **worker application image** (`docker build`).
- **Load or push** that image so **minikube** can run it (`minikube image load …`, or registry push + pull policy).

That flow is **orthogonal** to apply order: manifests vs YAML. README may list Docker/minikube steps next to deploy steps, but **they are not duplicate “distro versions” of the same deploy.**

**Deploy scripts (see MVP table row):** **`scripts/deploy.sh`** and **`scripts/deploy.ps1`**—same `kubectl` sequence; rationale here is **host OS shell** (POSIX vs Windows), not Linux distro on cluster nodes.

README must still list the equivalent `kubectl` commands for users who skip scripts. **Post-MVP:** consolidation options in [FUTURE.md](../FUTURE.md).

---

## Implementation artifacts

Policy is **pinned semver** (see MVP table: Temporal `auto-setup`, Postgres, worker base image, Python deps). When adding `Dockerfile`, manifests, and Poetry lockfile, **record the chosen tag numbers** in those files and in README; align `temporalio/auto-setup` with **Temporal Python SDK** compatibility as needed. That is **documentation and config output**, not a spec gap.

Deploy entrypoints are **locked** above (`deploy.sh` + `deploy.ps1` + README echo of `kubectl`).

If a **new** requirement appears during coding, update this file and [FUTURE.md](../FUTURE.md) together.
