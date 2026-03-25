# Future work / production hardening

This file lists **production-oriented alternatives** to the **MVP decisions** locked in [specs/requirements-decisions.md](specs/requirements-decisions.md). MVP = expectations first, then smallest shippable path; **this backlog is explicitly out of scope** until post-MVP.

The **mapping table** below is the compact index. **Narrative sections** after it elaborate the same themes—they are **not** additional MVP requirements.

---

## How this maps to MVP

| MVP choice (specs) | Suggested prod / later evolution |
|--------------------|-----------------------------------|
| **Semver-pinned** images (no `latest`) | **Image digests** (`@sha256:…`) in manifests for reproducibility and supply-chain control. |
| PostgreSQL + `auto-setup` in-cluster | Official **Temporal Helm** chart; external **managed** PostgreSQL; **Cassandra/ES** visibility where required; upgrade/runbook discipline. |
| Minimal CPU/RAM, small/ephemeral DB | Right-sized **persistence**, **replication/HA**, **backup/restore**, **retention/archival** tuning. |
| Single container image, env-based roles | **Separate images** per component; **distroless** bases; **SBOM**, **signing**, **CVE** scanning in CI. |
| Short workflow/queue names | **Prefixed** names per team/product; **namespace** isolation strategy for shared Temporal. |
| Host Python trigger + port-forward | **Kubernetes Job** client; **`temporal` CLI** standardization; **internal** service DNS only (no host tools). |
| **`deploy.sh` + `deploy.ps1`** thin wrappers | **Single** pipeline (e.g. only GitHub Actions apply); **Terraform** / **Argo CD**; drop duplicate shell if team standardizes on one OS in CI. |
| No CI integration tests | **Temporal in CI** (service container, **Testcontainers**, shared env); **smoke** after image build; **minikube/kind** matrix. |
| Quantize **once** at workflow end | **Per-operation** quantize; **HALF_UP** / regulatory rounding; audit-friendly semantics. |
| `str` decimals on the wire | **Strongly typed** payloads; **schema registry**; avoid ad hoc string parsing at boundaries. |
| ASCII input only | **Locale** decimal comma, `×`, thousands separators; **normalization** layer. |
| Integer `^` only | **Decimal exponents**; domain limits; error messaging for overflow. |
| Random workflow run id | **Deterministic** ids for support replay (with collision policy). |
| Single Poetry package | **Publishable SDK** package + **example app** split; semver **migration** guides. |
| stdlib `logging` JSON | **structlog** / agent-friendly fields; **redaction** policies; **correlation** with trace ids. |
| `prometheus_client` only | **OpenTelemetry** traces + metrics; **dashboards**, **SLOs**, **alerts** with runbooks. |
| Basic readiness (“polling started”) | **Stronger readiness** (first successful poll/session) if SDK supports without flapping. |
| Single HTTP port for health + metrics | **Split ports** (`:8080` health, `:9090` metrics) for **NetworkPolicy** / scrape isolation. |
| CPU-only HPA (bonus) | **KEDA** / **custom metrics** (queue depth, activity latency); **multi-queue** coordinated scaling. |

---

## Temporal and data plane

- [ ] Production-grade Helm values; HA; backup/restore; versioned upgrades.
- [ ] **TLS/mTLS** (workers, clients, frontend); cert-manager / private CA.
- [ ] Dedicated namespaces/environments; RBAC; multi-cluster strategy.
- [ ] Retention, visibility store sizing, archival.

## Security and policy

- [ ] **NetworkPolicies**; egress allowlists.
- [ ] **Pod Security** (restricted, seccomp, read-only root).
- [ ] **External Secrets** / Vault; rotation; no long-lived creds in ConfigMaps.
- [ ] Image provenance, signing, minimal attack surface.

## Observability and operations

- [ ] Split health vs metrics listeners; scrape security.
- [ ] Tracing (OTel); log/trace correlation.
- [ ] Dashboards, SLOs, on-call runbooks.

## CI/CD and release

- [ ] Full integration test gate with Temporal.
- [ ] Automated local-cluster smoke (kind/minikube).
- [ ] Versioned releases for images and SDK.

## Autoscaling and capacity

- [ ] Custom metrics / KEDA beyond CPU HPA.
- [ ] Per-queue tuning from real traffic.

## SDK and packaging

- [ ] Pydantic (or similar) **settings** validation with clear errors.
- [ ] Published SDK artifact separate from demo app.

## Calculator / domain

- [ ] Locale and extended input symbols.
- [ ] Non-integer exponents if product requires.
- [ ] Rounding policy review for regulated use cases.

## Documentation

- [ ] DR and Temporal-outage playbooks for worker fleets.
- [ ] Multi-region / multi-cluster worker topology.

---

Add rows here when MVP implementation surfaces new “prod would do X” gaps; keep [specs/requirements-decisions.md](specs/requirements-decisions.md) as the single **locked MVP** source of truth.
