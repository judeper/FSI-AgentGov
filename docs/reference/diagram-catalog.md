# Diagram Catalog

!!! info "Audience"
    Microsoft FSI Cloud Solution Architects (CSAs), partner architects, and FSI customer architects evaluating which diagrams to drop into customer decks, examiner evidence packs, or internal briefings.

The FSI-AgentGov framework and its companion solutions repo carry roughly 75 diagrams across architecture, lifecycle, governance, evidence, and integration. This catalog organizes them by audience and use case so a CSA preparing for a customer conversation can find the right artifact in one pass.

---

## How to use this catalog

- **CAPE-alignment diagrams (v1.5.0 net-new)** are Mermaid blocks rendered in-doc. The editable `.mmd` source lives at `docs/images/diagrams/source/cape/`. Open in [mermaid.live](https://mermaid.live) to export SVG/PNG for customer decks.
- **Solutions repo diagrams** are PNG/SVG pairs published at `docs/images/diagrams/`. They originate in the [FSI-AgentGov-Solutions](https://github.com/judeper/FSI-AgentGov-Solutions) companion repo. Use them when illustrating a specific solution's architecture in a deeper engagement.
- The "Audience" column is a guide, not a gate. Most diagrams work in more than one conversation; the column lists the primary intended reader.

---

## CAPE-alignment diagrams (v1.5.0 net-new)

These five diagrams ship with v1.5.0 to help CSAs and architects translate Microsoft CAPE concepts into FSI-AgentGov framing during customer conversations.

| Diagram | Location | Audience | Use case | Format | Editable source |
|---|---|---|---|---|---|
| Pattern × Zone matrix | [microsoft-cape-crosswalk.md §3](microsoft-cape-crosswalk.md#3-pattern-zone-fit-matrix) | CSA, FSI Architect | Customer briefing: "where does each CAPE pattern fit in our zone model?" | Mermaid (in-doc) | [`docs/images/diagrams/source/cape/pattern-zone-matrix.mmd`](../images/diagrams/source/cape/pattern-zone-matrix.mmd) |
| CoE structure by pattern | [agentic-coe.md — three CoE shapes](../framework/agentic-coe.md#the-three-coe-shapes) | CIO, CSA | Executive briefing: "what CoE shape fits which pattern?" | Mermaid (in-doc) | [`docs/images/diagrams/source/cape/coe-structure-by-pattern.mmd`](../images/diagrams/source/cape/coe-structure-by-pattern.mmd) |
| Decision rights framework | [agentic-coe.md — Decision rights at a glance](../framework/agentic-coe.md#decision-rights-at-a-glance) | CIO, CCO, CRO | "Who decides what?" — central vs shared vs domain decisions, plus the non-delegable named-principal layer | Mermaid (in-doc) | [`docs/images/diagrams/source/cape/decision-rights.mmd`](../images/diagrams/source/cape/decision-rights.mmd) |
| CAPE 90-day × FSI Phase timeline | [adoption-roadmap.md — CAPE 90-day plan × FSI](../framework/adoption-roadmap.md#cape-90-day-plan-fsi-phase-0-1-timeline) | CIO, CSA | Customer briefing: "how does Microsoft's 90-day plan map to FSI's adoption phases?" | Mermaid Gantt (in-doc) | [`docs/images/diagrams/source/cape/cape-fsi-timeline.mmd`](../images/diagrams/source/cape/cape-fsi-timeline.mmd) |
| Agent lifecycle (7-stage, FSI-annotated) | [agent-lifecycle.md — top of page](../framework/agent-lifecycle.md#cape-7-stage-lifecycle-with-fsi-regulatory-hooks) | Power Platform Admin, CCO, examiner-facing reviewer | Examiner evidence: "lifecycle controls per stage with regulatory hooks (FINRA 4511, SEC 17a-4, OCC Bulletin 2026-13 (formerly OCC 2011-12))" | Mermaid (in-doc) | [`docs/images/diagrams/source/cape/agent-lifecycle-7-stage.mmd`](../images/diagrams/source/cape/agent-lifecycle-7-stage.mmd) |

---

## Solutions repo diagrams (existing)

The [FSI-AgentGov-Solutions](https://github.com/judeper/FSI-AgentGov-Solutions) companion repo publishes architecture diagrams for each live solution. Each diagram lands in the docs site as a PNG + SVG pair under `docs/images/diagrams/`. The groupings below describe what each filename family covers — refer to the source solution README for the canonical narrative.

### Governance zones and framework overview

| Filename family | What it shows | Audience | Use case |
|---|---|---|---|
| `README-three-governance-zones.{png,svg}` | The Zone 1 / Zone 2 / Zone 3 model at a glance | CIO, CSA, FSI Architect | First-pass customer briefing on the FSI zone model |
| `README-layer-3-playbooks-docsplaybooks.{png,svg}` | Three-layer architecture (Framework → Controls → Playbooks) | CSA, FSI Architect | Walking customers through how the framework is structured |
| `README-implementation-steps.{png,svg}` | Implementation step flow (cross-solution) | Power Platform Admin, FSI Architect | Onboarding briefings for newly engaged customers |
| `index-blueprint-lifecycle-phases.{png,svg}` | Blueprint lifecycle phases (cross-solution) | FSI Architect, AI Governance Lead | Aligning solution rollouts to lifecycle phases |
| `index-architecture-overview.{png,svg}` | Cross-solution architecture overview | FSI Architect | Initial architecture-level orientation |
| `index-solution-overview.{png,svg}` (and `-2`, `-3`, `-4` variants) | Per-solution overview slides | CSA, FSI Architect | Picking the right solution for a customer use case |
| `index-daily-orchestration.{png,svg}` | Daily orchestration cadence | Service Owner, AI Governance Lead | Operating-rhythm conversations |

### Control-specific visualizations

| Filename family | What it shows | Audience | Use case |
|---|---|---|---|
| `1-2-agent-registry-and-integrated-apps-management-curation-w.{png,svg}` | Control 1.2 — agent registry and integrated apps curation workflow | Power Platform Admin, AI Governance Lead | Walking through the curation workflow during a Control 1.2 implementation |
| `3-1-agent-inventory-and-metadata-management-unified-agent-vi.{png,svg}` | Control 3.1 — unified agent view (inventory + metadata) | AI Governance Lead, Power Platform Admin | Operational briefings on the agent inventory pillar |

### Agent identity and Agent 365 control plane

| Filename family | What it shows | Audience | Use case |
|---|---|---|---|
| `agent-identity-architecture-entra-agent-id-architecture-flow.{png,svg}` | Entra Agent ID architecture flow | Entra Security Admin, FSI Architect | Designing identity governance for non-human agent identities |
| `agent-identity-architecture-agent-365-control-plane-architec.{png,svg}` | Agent 365 control plane architecture | FSI Architect, AI Administrator | Architecture review for the Agent 365 control plane |
| `agent-identity-architecture-m365-admin-center-agent-settings.{png,svg}` | M365 admin center agent settings | AI Administrator, Power Platform Admin | Configuration walk-through during deployment |

### General architecture patterns

| Filename family | What it shows | Audience | Use case |
|---|---|---|---|
| `architecture-component-overview.{png,svg}` (and `-2`) | Component overviews for solution architectures | FSI Architect | Architecture review |
| `architecture-async-polling-pattern.{png,svg}` | Async polling pattern | FSI Architect, Solution Developer | Designing long-running solution flows |
| `architecture-security-model-diagram.{png,svg}` | Security model architecture | CISO, FSI Architect | Security review |
| `architecture-workflow-state-machine.{png,svg}` (and `-2`) | Workflow state machine designs | FSI Architect, Solution Developer | Designing workflow logic |

### Deployment, provisioning, rollback

| Filename family | What it shows | Audience | Use case |
|---|---|---|---|
| `deployment-guide-deployment-architecture.{png,svg}` | Deployment architecture | Power Platform Admin, FSI Architect | Production deployment planning |
| `implementation-provisioning-provisioning-architecture.{png,svg}` | Provisioning architecture | Power Platform Admin | Provisioning step-by-step |
| `implementation-provisioning-rollback-procedure.{png,svg}` | Rollback procedure | Power Platform Admin, Service Owner | Incident-response readiness |
| `implementation-guide-architecture-overview.{png,svg}` | Implementation guide overview | FSI Architect | First-pass solution implementation |

### Implementation flows

| Filename family | What it shows | Audience | Use case |
|---|---|---|---|
| `implementation-approval-approval-flow-architecture.{png,svg}` | Approval flow architecture | AI Governance Lead, Service Owner | Designing approval workflows for Zone 2 / Zone 3 |
| `implementation-copilot-intake-intake-agent-architecture.{png,svg}` | Copilot intake agent architecture | AI Governance Lead, Power Platform Admin | Standing up the agent intake pipeline (CAPE Stage 1) |

### Evidence, audit, observability

| Filename family | What it shows | Audience | Use case |
|---|---|---|---|
| `evidence-and-audit-evidence-architecture.{png,svg}` | Evidence and audit architecture | CCO, Internal Audit, AI Governance Lead | Examiner-evidence walkthroughs |
| `opentelemetry-setup-architecture.{png,svg}` | OpenTelemetry setup architecture | Sentinel Engineer, FSI Architect | Observability instrumentation planning |
| `power-bi-correlation-dataverse-tables.{png,svg}` | Power BI correlation across Dataverse tables | AI Governance Lead, Service Owner | Reporting and correlation design |

### Solutions architecture (security postures and integration)

| Filename family | What it shows | Audience | Use case |
|---|---|---|---|
| `solutions-architecture-guide-azure-key-vault-integration.{png,svg}` | Azure Key Vault integration | FSI Architect, CISO | Hardening solution secrets management |
| `solutions-architecture-guide-high-security-deployment-vnet-i.{png,svg}` | High-security deployment with VNet isolation | FSI Architect, CISO | Designing the highest-assurance solution posture |
| `solutions-architecture-guide-streaming-architecture-near-rea.{png,svg}` | Streaming / near-real-time architecture | FSI Architect, Solution Developer | Streaming-data solution patterns |
| `solutions-integration-overview.svg` | Cross-solution integration overview | FSI Architect | Multi-solution architecture conversations |
| `solutions-integration-integration-architecture.{png,svg}` | Detailed integration architecture | FSI Architect | Designing integration fan-out across solutions |

---

## How to export a Mermaid diagram for a customer deck

1. Locate the editable source — for CAPE-alignment diagrams, `docs/images/diagrams/source/cape/<diagram>.mmd`.
2. Open [mermaid.live](https://mermaid.live) and paste the file contents.
3. Use **Actions → Download SVG** (preferred for slides — vector) or **Download PNG** (preferred for embedded screenshots).
4. Or render locally with the Mermaid CLI:
   ```powershell
   npx -p @mermaid-js/mermaid-cli mmdc -i pattern-zone-matrix.mmd -o pattern-zone-matrix.svg
   ```
5. For PNG/SVG diagrams already published under `docs/images/diagrams/`, simply right-click the rendered image on the docs site and save — the SVG is the canonical editable form.

---

## Brand boundary

These diagrams visualize the FSI-AgentGov framework's mapping of Microsoft CAPE concepts (patterns, drivers, CoE shapes, the 90-day plan, the 7-stage lifecycle) to FSI-AgentGov controls and US regulatory regimes. They are **not** Microsoft-issued artifacts. Use them in customer conversations to illustrate the FSI-AgentGov framework's interpretation of how CAPE applies in US financial services. Do not represent them as Microsoft endorsement of any specific control implementation, regulatory position, or examiner outcome. Microsoft CAPE source materials carry their own canonical visualizations; this catalog supplements rather than replaces them.

---

## Related documents

- [Microsoft CAPE Crosswalk](microsoft-cape-crosswalk.md) — host of the Pattern × Zone diagram
- [Agentic CoE](../framework/agentic-coe.md) — host of the CoE structure and decision rights diagrams
- [Adoption Roadmap](../framework/adoption-roadmap.md) — host of the CAPE 90-day × FSI Phase timeline
- [Agent Lifecycle](../framework/agent-lifecycle.md) — host of the 7-stage lifecycle diagram
- [CSA Quick Reference](csa-quick-reference.md) — partner / CSA engagement summary
- [CSA Positioning Guide](csa-positioning-guide.md) — positioning for CSA conversations

---

*Updated: May 2026 | Version: v1.6.2 | Audience: CSAs, partner architects, FSI customer architects*
