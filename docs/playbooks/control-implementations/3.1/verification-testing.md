# Control 3.1 — Verification & Testing Playbook (Inventory Integrity)

**Control:** 3.1 — Agent Inventory and Metadata Management
**Pillar:** 3 — Reporting
**Audience:** Inventory Owner, AI Governance Lead, Compliance Officer, Power Platform Admin, AI Administrator, Entra Agent ID Admin, Internal Audit, Model Risk Manager
**Cloud scope:** Microsoft 365 Commercial (Global) cloud.
**Last UI verified:** May 2026

---

## Regulatory hedging notice

This playbook helps support FSI organizations in meeting expectations from FINRA Rule 4511 (books and records), FINRA RN 24-09 / Rule 3110 (generative-AI supervision), SEC Rule 17a-4(b)(4) (records retention), SOX §§302/404 (internal control over financial reporting), GLBA Safeguards Rule 501(b), FTC Safeguards Rule 16 CFR §314, OCC Bulletin 2026-13 (formerly OCC Bulletin 2011-12) / Federal Reserve SR 26-2 (formerly SR 11-7) (model risk management), CFTC Regulation 1.31, NYDFS 23 NYCRR Part 500.16 / 500.17, NIST AI RMF 1.0 GOVERN 1.6, and ISO/IEC 42001 where applicable.

A clean run of this playbook **does not guarantee legal or regulatory compliance**, does not replace independent validation, and does not substitute for written supervisory procedures. Implementation requires organization-specific risk assessment, legal review, and integration with the firm's broader compliance program. Organizations should verify current Microsoft Learn documentation, and tenant-specific entitlements at each cycle. Cadence values, SLA windows, and reconciliation thresholds in this playbook are **calibrated to the tenant baseline captured in PRE-04**; they are not portable between tenants without recalibration.

This playbook is **inventory-integrity verification**: its purpose is to verify that the authoritative agent inventory is **complete, accurate, current, owned, and reconciled** across every Microsoft discovery surface that can host an agent. Control 3.1 is the foundation control for Pillar 3 — every dashboard, every reconciliation, every examiner-facing report downstream depends on the correctness of this inventory. If the inventory is wrong, every downstream attestation built on it is wrong.

---

## Why this playbook is foundational

Pillar 3 reporting controls (3.2 Usage Analytics, 3.6 Orphaned Agent Detection, 3.8 Copilot Hub Dashboard, 3.11 Quarterly Reporting) all consume the **system of record** that Control 3.1 maintains. The reporting chain has the property that **silent omissions propagate**: an agent missing from the system of record will also be missing from every Pillar 3 dashboard, every reconciliation report, every supervisory pull, and every regulator-response evidence pack — without ever surfacing as a visible error. The downstream controls cannot detect what their input never contained.

This playbook therefore treats two failure modes as equally severe:

1. **Visible inventory inaccuracy** — a metadata field that is wrong, stale, or contradicted by the source system.
2. **Silent inventory incompleteness** — an agent that exists in a discovery surface but never appears in the system of record, or appears under a stale AgentID that breaks the join key across portals and evidence.

Both failure modes are first-class FAIL conditions. The playbook is structured so that incompleteness cannot be hidden behind accuracy: COMP-* tests run before ACC-* tests, and a COMP failure halts the cycle regardless of how clean the rest of the evidence looks.

---

## Audience and how to use this playbook

| Role | What you do here |
|---|---|
| **Inventory Owner** | Owns the cycle, runs the discovery exports, assembles the reconciliation evidence pack, and signs as **Preparer** in the three-signature chain. |
| **AI Governance Lead** | Reviews the cycle outputs against governance policy, validates the reconciliation deltas, and signs as **Validator**. |
| **Compliance Officer** | Reviews the evidence pack from a supervisory and regulatory-readiness perspective and signs as **Compliance**. |
| **Power Platform Admin** | Confirms PPAC inventory exports are complete, the 500-agent display ceiling has been bypassed via Resource Graph or PowerShell, and the 15-minute refresh cycle is accounted for. |
| **AI Administrator** | Confirms Microsoft 365 admin center Copilot agent inventory exports are complete and reconciles declarative, shared, and Microsoft-provided agents. |
| **Entra Agent ID Admin** | Confirms Entra Agent ID directory enumeration is complete and that AgentID-to-Entra-identity joins resolve. |
| **Internal Audit** | Uses the evidence pack and three-signature attestation chain as the testable artifact for SOX-style and FINRA-supervision walkthroughs and the basis for the quarterly examiner-style audit (Section 9). |
| **Model Risk Manager** | Reviews REG-* and ACC-* evidence under Fed SR 26-2 (formerly SR 11-7) / OCC Bulletin 2026-13 (formerly OCC 2011-12) model-risk inventory expectations. |

Run order each cycle: **Section 5 PRE gates → Section 7 §COMP tests → §ACC → §DRIFT → §OWN → §LIFE → §DLP → §REG → Section 8 evidence pack assembly → Section 11 attestation chain**. A blocker, a PRE failure, or any COMP-* FAIL halts the cycle.

---

## Cross-links

This playbook depends on, and is depended on by, the following framework controls and playbooks. Operators should open these alongside this document during a cycle:

- [Control 1.7 — Comprehensive Audit Logging and Compliance](../../../controls/pillar-1-security/1.7-comprehensive-audit-logging-and-compliance.md)
- [Control 1.19 — eDiscovery for Agent Interactions (verification playbook)](../1.19/verification-testing.md)
- [Control 1.21 — Adversarial Input Logging (verification playbook)](../1.21/verification-testing.md)
- [Control 2.1 — Managed Environments (verification playbook)](../2.1/verification-testing.md)
- [Control 2.5 — Testing, Validation, and QA (verification playbook)](../2.5/verification-testing.md)
- [Control 2.13 — Documentation and Record Keeping](../../../controls/pillar-2-management/2.13-documentation-and-record-keeping.md)
- [Control 3.6 — Orphaned Agent Detection and Remediation](../../../controls/pillar-3-reporting/3.6-orphaned-agent-detection-and-remediation.md)
- [Control 3.8 — Copilot Hub and Governance Dashboard](../../../controls/pillar-3-reporting/3.8-copilot-hub-and-governance-dashboard.md)
- [Control 3.11 — Quarterly Compliance Reporting](../../../controls/pillar-3-reporting/3.11-centralized-agent-inventory-enforcement.md)
- [AI Incident Response Playbook](../../incident-and-risk/ai-incident-response-playbook.md)

---

## What this playbook catches

This playbook is designed to detect defects in the **inventory program**, not in any one agent. It is built to surface:

1. **Surface drift** — an agent exists in PPAC, Entra Agent ID, or the M365 admin center but does not appear in the authoritative system of record.
2. **Stale AgentID joins** — the immutable AgentID has been regenerated, lost, or never assigned, breaking the join across portals and evidence packs.
3. **Owner-of-record divergence** — the inventory Owner field does not resolve to a current Entra identity, or the named Owner has departed and the backup Owner is also stale.
4. **Lifecycle phantoms** — agents marked Active in inventory that have been deleted at the platform layer, or agents marked Decommissioned that are still callable.
5. **Metadata drift without re-attestation** — the agent's connectors, knowledge sources, model, or DLP scope changed at the platform layer with no corresponding re-attestation in the inventory.
6. **DLP scoping gaps** — Zone 2 / Zone 3 agents with no recorded DLP policy mapping or with a DLP policy that no longer exists in Purview.
7. **Regulatory-scope under-tagging** — agents that touch FINRA Communications surfaces, SOX ICFR processes, or GLBA-covered data but are not tagged into those supervisory inventories.
8. **PPAC display-ceiling silent truncation** — tenants with more than 500 agents whose evidence pack relies on the portal view rather than Azure Resource Graph or PowerShell enumeration.
9. **Refresh-window blind spots** — agents created or modified within the trailing 15 minutes that are missing from a snapshot taken before the platform refresh completed.
10. **Tamper-prone evidence** — inventory snapshots stored without SHA-256 manifests, signature chain, or immutable retention.
11. **Reconciliation theater** — reconciliation reports that show 100% match because the comparison set was filtered to only the agents already in the system of record, not the full discovery superset.

---

## What this playbook does NOT claim

This playbook **does not** prove the absence of unknown agents in unobserved surfaces, **does not** replace human supervisory review of the inventory, **does not** guarantee legal or regulatory compliance merely because the cycle returns a clean validator result, and **does not** substitute for the firm's written supervisory procedures, model-risk inventory, or books-and-records program. A clean cycle is one defensible data point; it is not the firm's complete inventory-governance story.

A clean cycle means: across the discovery surfaces that exist as of May 2026 the system of record reconciled to those surfaces within the recorded tolerance and with traceable evidence. It does not mean the inventory is correct against future discovery surfaces, future Microsoft service rollouts, or shadow-IT channels outside the Microsoft 365 boundary.

---

## Section 1 — The 3-Signature Attestation Chain

Every inventory verification cycle terminates in a **three-signature attestation chain** with cryptographic integrity. This is the cycle's primary deliverable and the artifact handed to internal audit and external examiners.

### 1.1 Signature roles

| Signature | Role (canonical) | What this signature attests |
|---|---|---|
| **Preparer** | Inventory Owner | "I executed the COMP, ACC, DRIFT, OWN, LIFE, DLP, and REG tests as documented; I assembled the evidence pack listed in the manifest; the SHA-256 hashes in the manifest match the artifacts in the evidence store; I have not altered any source export after capture." |
| **Validator** | AI Governance Lead | "I independently re-executed at least one test from each namespace using the operator's evidence and obtained the same result; I reviewed the reconciliation deltas and confirmed each delta is either resolved, exception-tracked, or escalated; the cycle conforms to the inventory-governance policy in force at the cycle start date." |
| **Compliance** | Compliance Officer | "I reviewed the evidence pack from a supervisory and regulatory-readiness perspective; the residual gaps documented in this cycle are acceptable for the firm's current risk posture or are tracked to a dated remediation plan; this evidence pack is suitable for inclusion in the firm's books-and-records repository under the applicable retention period." |

The three roles **must** be three distinct natural persons. Role collision (the same person signing two roles) is a cycle-stopping FAIL recorded in PRE-02. A documented temporary exception for a lower-zone scope is allowed only with a co-signed expiry.

### 1.2 Hash chain across snapshots

Each cycle's evidence pack contains a `manifest.sha256` file listing one SHA-256 per artifact. The cycle attestation file (`attestation.json`) records:

- `cycleId` — stable identifier for this cycle
- `previousCycleId` — the immediately preceding cycle for the same scope
- `previousManifestHash` — SHA-256 of the previous cycle's `manifest.sha256`
- `manifestHash` — SHA-256 of the current cycle's `manifest.sha256`
- `chainHash` — SHA-256 of the concatenation `previousManifestHash || manifestHash || cycleId`
- `signatures[]` — three signature objects (Preparer, Validator, Compliance) each with role, identity, timestamp, and signature method

The `previousManifestHash` field creates a tamper-evident hash chain across the cycle history. A break in the chain (a `previousManifestHash` value that does not match the `manifestHash` of the previous cycle) is itself an audit finding and triggers DRIFT-03 escalation.

### 1.3 Attestation note language

The Preparer attestation should include the literal language: *"This cycle was executed against the discovery surfaces and tenant entitlements available as of the cycle start date. A clean cycle does not by itself guarantee regulatory compliance, model-risk completeness, or freedom from shadow-IT inventory."* Validator and Compliance signatures should each include a reference to the policy document identifier and effective date that they are attesting against.

---


## Section 2 — License and permissions prerequisites

Re-verify SKU availability, the at-least-one-user Agent 365 license assignment prerequisite, and tenant rollout at cycle start against current Microsoft Learn licensing guidance and the tenant Message Center.

### 3.1 Required licenses

| Capability | License | Used by |
|---|---|---|
| Microsoft 365 Copilot agent surfaces | Microsoft 365 Copilot | COMP-01, ACC-01, ACC-02 |
| Power Platform agent inventory (PPAC) | Power Platform admin entitlement | COMP-01, COMP-04, DRIFT-01 |
| Entra Agent ID directory | Entra ID P1 / P2 (verify) | COMP-01, OWN-01, OWN-02 |
| Microsoft Agent 365 (where available) | At least one user assigned a qualifying Microsoft Agent 365 license or bundled entitlement | COMP-01 (additive only) |
| Purview Audit (UAL) | E5 Compliance / Purview Audit Premium | DRIFT-03, LIFE-03, REG-03 |
| Purview DLP enumeration | E5 Compliance / Purview DLP | DLP-01, DLP-02, DLP-03 |
| Microsoft Information Protection labels | E5 Compliance | ACC-03 |
| Defender for Cloud Apps | MDA license | COMP-03 (cross-source enrichment) |
| Azure Resource Graph (programmatic enumeration) | Azure entitlement | COMP-04 |

### 3.2 Required role assignments (canonical names)

| Role | Why needed |
|---|---|
| Inventory Owner | Cycle execution; Preparer signature |
| AI Governance Lead | Cycle validation; Validator signature |
| Compliance Officer | Cycle review; Compliance signature |
| Power Platform Admin | PPAC enumeration, inventory exports |
| AI Administrator | M365 admin center Copilot inventory access |
| Entra Agent ID Admin | Entra Agent ID directory enumeration |
| Entra Global Reader | Read-only attestation review |
| Purview Compliance Admin | UAL searches; DLP policy enumeration |
| Exchange Online Admin | Mailbox-grounded agent reconciliation (where applicable) |
| Entra Global Admin | Tenant-wide Agent 365 access where still required; activated via Entra PIM, time-bound, never standing |

Role separation is enforced by PRE-02. Standing privileged role overlap with Preparer / Validator / Compliance is a cycle-stopping FAIL.

---

## Section 3 — Required namespace × zone cadence matrix

| Namespace | What the family verifies | Zone 1 | Zone 2 | Zone 3 | Owner | Reviewer |
|---|---|---|---|---|---|---|
| **COMP** | Completeness across all six discovery surfaces | Quarterly | Monthly | Weekly | Inventory Owner | AI Governance Lead |
| **ACC** | Metadata accuracy vs. source-of-truth systems | Quarterly | Monthly | Weekly | Inventory Owner | AI Governance Lead |
| **DRIFT** | New / modified agent detection within zone SLA | Monthly | Weekly | Daily (automated) | Inventory Owner | Power Platform Admin |
| **OWN** | Owner / Backup Owner accountability | Quarterly | Monthly | Monthly | Inventory Owner | AI Governance Lead |
| **LIFE** | Lifecycle state integrity | Quarterly | Monthly | Monthly | Inventory Owner | Compliance Officer |
| **DLP** | DLP policy mapping completeness | Annual | Quarterly | Monthly | Purview Compliance Admin | AI Governance Lead |
| **REG** | Regulatory-scope tagging completeness | Annual | Quarterly | Quarterly | Compliance Officer | AI Governance Lead |

**Cadence rule.** Monthly cycles have a 35-day grace window, quarterly cycles have a 100-day grace window, semi-annual cycles have a 200-day grace window, and annual cycles have a 400-day grace window. A namespace that fails in two consecutive cycles automatically escalates one tier (Zone 1 → Zone 2 cadence, Zone 2 → Zone 3 cadence) until two clean cycles are observed.

---

## Section 4 — Pre-flight gates (PRE-01 through PRE-06)

All PRE gates should pass before any §7 test runs. A PRE failure halts the cycle and returns validator exit code **2**.

### PRE-01 — Inventory governance charter and metadata schema in force
- **Objective.** Confirm the organization has a current, signed inventory-governance charter that defines the canonical metadata schema (AgentID, Owner, Backup Owner, Zone, Lifecycle State, DLP Mapping, Regulatory Scope, Effective Sensitivity Label, etc.) and the reconciliation cadence.
- **How to verify.** Pull the charter document from the policy repository; confirm signatures from AI Governance Lead and Compliance Officer; confirm effective date is current and review date has not lapsed.
- **Evidence.** `pre-01-inventory-charter.json` referencing policy ID, effective date, review date, owner, sign-off roster.
- **Pass criteria.** Charter exists, is signed, has not lapsed its review date, and the metadata schema in force matches the schema this cycle is enforcing.
- **Audit assertion.** "The cycle was executed against a current, signed inventory-governance policy and against the canonical metadata schema referenced therein."

### PRE-02 — Role separation and reviewer independence
- **Objective.** Confirm the same natural person does not occupy the attestation roles of Preparer (Inventory Owner), Validator (AI Governance Lead), and Compliance (Compliance Officer); confirm any elevated admin used during the cycle is time-bound through Entra PIM.
- **How to verify.** Query Entra role assignments and the cycle approver roster; verify PIM activation history for any privileged role used; confirm co-signer requirements for any exception.
- **Evidence.** `pre-02-role-separation.json`
- **Pass criteria.** Three roles are distinct natural persons, no standing privileged overlap exists, any exception is explicit and time-limited.
- **Audit assertion.** "The verification cycle was run under segregated duties consistent with supervisory and internal-control expectations."

### PRE-03 — License and entitlement floor
- **Objective.** Confirm the tenant has the entitlements required for every discovery surface and source-of-truth system the cycle relies on (Microsoft 365 Copilot, Power Platform admin, Entra Agent ID, Purview Audit, Purview DLP, MIP, optional MDA / Agent 365).
- **How to verify.** Capture tenant SKU report, environment classification, Managed Environment status, and entitlement availability for each surface; if a surface is not yet available, record the manual fallback path.
- **Evidence.** `pre-03-licensing-and-env.json`
- **Pass criteria.** All exercised surfaces are entitled and reachable, or a compensating control is documented and tied to the relevant SOV-* test.
- **Audit assertion.** "The cycle relied only on features the tenant is entitled to use in the declared cloud."

### PRE-04 — Tenant baseline capture
- **Objective.** Establish the tenant-specific baseline for total agent count, surface-level counts, expected reconciliation tolerance, and DRIFT detection lag before the cycle's pass conditions are evaluated. The baseline is the source of all numeric thresholds in the cycle; thresholds are not portable from another tenant.
- **How to verify.** Pull trailing 90-day cycle history; calculate trend, mean, p50, p95 for the count metrics; write a baseline file with a stable `baselineId` that every test references.
- **Evidence.** `pre-04-baseline.json`
- **Pass criteria.** A current baseline exists, references at least three trailing cycles where available, and is the sole source for the numeric thresholds cited later.
- **Audit assertion.** "All numerical assertions in this cycle trace back to a documented tenant baseline rather than copied values from another tenant or an older cycle."

### PRE-05 — Snapshot freeze and refresh-window alignment
- **Objective.** Confirm the discovery snapshot used for this cycle was taken **after** the most recent platform refresh window and is frozen for the duration of the cycle. PPAC inventory has a ~15-minute refresh cadence; snapshots taken inside the refresh window can silently truncate.
- **How to verify.** Record snapshot timestamps for each surface; confirm each timestamp is at least 20 minutes after the prior write activity recorded in UAL; freeze the snapshot directory by computing SHA-256 over its contents at cycle start and again at cycle end.
- **Evidence.** `pre-05-snapshot-freeze.json`
- **Pass criteria.** Snapshot start and end SHA-256 values match (the snapshot did not mutate during the cycle), and each surface snapshot is outside the refresh window.
- **Audit assertion.** "The cycle's evidence corresponds to a stable snapshot taken outside the platform refresh window and unchanged for the cycle duration."

### PRE-06 — System-of-record reachability and write-protection
- **Objective.** Confirm the system-of-record store (SharePoint list, Dataverse table, GRC tool, or CMDB) is reachable, that the cycle has read access, and that the write-protection / version-history feature is active so that mid-cycle edits cannot mask reconciliation deltas.
- **How to verify.** Query the system-of-record schema; confirm version history or audit log is enabled; capture a read-only export with a timestamp.
- **Evidence.** `pre-06-sor-reach.json`
- **Pass criteria.** The system of record is reachable, version history / audit is enabled, and the export is timestamped and hashed.
- **Audit assertion.** "The system of record is the immutable comparison target for the cycle, with version history sufficient to support audit replay."

---

## Section 5 — Documented processing windows

This playbook does **not invent SLAs**. Where Microsoft documentation is qualitative or eventual-consistency based, the playbook says so plainly and uses the tenant-specific PRE-04 baseline as the operative threshold.

| Signal or operation | Documentation-safe statement | Used by |
|---|---|---|
| PPAC Inventory refresh | ~15 minutes per Microsoft Learn ([Copilot Hub docs](https://learn.microsoft.com/en-us/power-platform/admin/copilot/copilot-hub)); use this as the lower bound and capture observed lag in PRE-05 | DRIFT-01, COMP-01 |
| PPAC deleted-agent visibility | Up to 48 hours retained-visibility window per Microsoft Learn; treat as documented behavior, not as an SLA | LIFE-03 |
| M365 admin center Copilot agent inventory propagation | No universal published SLA; use tenant baseline from PRE-04 | COMP-01, DRIFT-01 |
| Entra Agent ID directory propagation | Eventually consistent per Entra documentation; use tenant baseline | COMP-01, OWN-01 |
| Purview Audit (UAL) ingestion of agent lifecycle events | Eventual consistency; Microsoft documents up to 24 hours typical latency in Commercial; use tenant baseline | DRIFT-03, LIFE-03, REG-03 |
| Purview DLP policy enumeration | Near-real-time read; record observed read latency | DLP-01, DLP-02 |
| Defender for Cloud Apps cross-source enrichment | Tenant-dependent ingestion lag; record observed | COMP-03 |
| MIP label evaluation propagation | Eventual consistency; record observed | ACC-03 |
| System-of-record write propagation | Tenant store dependent; record observed | OWN-02, LIFE-02 |

---

## Section 6 — Test catalog (23 tests across 7 namespaces)

Each test has a stable ID, one clear objective, specific preconditions, operator-runnable steps, deterministic expected behavior and pass criteria, named evidence artifacts, the failure remediation path, the cycle cadence, the named owning role, and zone applicability. The order is fixed: COMP → ACC → DRIFT → OWN → LIFE → DLP → REG → SOV.

### Namespace expansion

- **COMP** — Completeness across discovery surfaces
- **ACC** — Metadata accuracy vs. source-of-truth systems
- **DRIFT** — New / modified agent detection and re-attestation
- **OWN** — Owner / Backup Owner accountability
- **LIFE** — Lifecycle state integrity
- **DLP** — DLP policy mapping completeness
- **REG** — Regulatory-scope tagging completeness

---

### 7.COMP — Completeness across discovery surfaces

This family verifies that no agent is silently missing from the system of record. The cycle treats the **union** of all discovery surfaces as the authoritative superset; the system of record should reconcile to that superset, not the other way around. A single missing agent in this family halts the cycle.

#### 3.1-COMP-01 — Six-surface enumeration completeness

- **Objective.** Confirm that the cycle enumerated every Microsoft discovery surface that can host or register an agent in the tenant.
- **Pre-conditions.** PRE-01, PRE-03, PRE-05, PRE-06, PRE-07 PASS.
- **Steps.**
  1. Export the Microsoft 365 admin center Copilot inventory from **admin.microsoft.com → Copilot → Agents** and save as `surface-m365.csv` with capture timestamp.
  2. Export the Power Platform admin center inventory from **PPAC → Manage → Inventory** and save as `surface-ppac.csv`. If the tenant exceeds 500 agents, fall back to the Azure Resource Graph query in §3 of Control 3.1 and record the fallback in evidence.
  3. Enumerate the Entra Agent ID directory using Microsoft Graph (or the manual fallback where Graph enumeration is unavailable) and save as `surface-entra.csv`.
  4. Where available in the declared cloud, export the Microsoft Agent 365 admin-center surface as `surface-agent365.csv`. Treat as **additive** only; treat as additive only where not yet GA.
  5. Pull a Purview Audit (UAL) export of `AgentCreated`, `AgentUpdated`, `AgentDeleted` events for the trailing reconciliation window and save as `surface-ual.csv`. UAL is the audit-trail surface, not a primary discovery surface, but absence of UAL records for an agent that appears in another surface is itself a finding.
  6. Where MDA is available, export the Defender for Cloud Apps agent enrichment view as `surface-mda.csv`.
  7. Compute SHA-256 for each surface export and write into `manifest.sha256`.
- **Expected result.** Six surface exports (or five plus a documented additive-skip for Agent 365) exist with timestamps and hashes. Each surface enumeration completed without truncation warnings.
- **Pass criteria.** All required surface exports exist, are non-empty (or empty for a documented reason such as no agents in scope), are hashed, and the PPAC export shows a row count ≥ the count visible in PPAC at snapshot time (or used the Resource Graph fallback). Truncation, missing surfaces, or unfilled fallbacks are FAIL.
- **Failure remediation.** Identify the missing surface, restore access via Power Platform Admin / Entra Agent ID Admin / AI Administrator as appropriate, re-take the snapshot outside the next refresh window, and re-run the test. Do not proceed to COMP-02 with a partial surface set.
- **Evidence.** `surface-m365.csv`, `surface-ppac.csv`, `surface-entra.csv`, `surface-agent365.csv` (or skip note), `surface-ual.csv`, `surface-mda.csv` (or skip note), `manifest.sha256`.
- **Cadence.** Zone 1 quarterly · Zone 2 monthly · Zone 3 weekly.
- **Owner.** Inventory Owner.
- **Zone applicability.** All zones; Zone 3 weekly is the binding cadence for any tenant with regulated agents.

#### 3.1-COMP-02 — Cross-source reconciliation match rate

- **Objective.** Confirm that the union of all discovery surfaces reconciles to the system of record above the per-zone tolerance, using the canonical AgentID as the join key.
- **Pre-conditions.** COMP-01 PASS.
- **Steps.**
  1. Build the discovery superset by unioning the AgentID column from each surface export captured in COMP-01. Where a surface lacks a stable AgentID (e.g., M365 admin center display-name-only rows), join on Microsoft-published surrogate IDs and record the join method.
  2. Pull the system-of-record export captured in PRE-07 (`sor-export.csv`).
  3. Compute the symmetric difference: agents in the discovery superset not in the system of record (`delta-missing-from-sor.csv`) and agents in the system of record not in any discovery surface (`delta-missing-from-discovery.csv`).
  4. Compute the match rate = `|intersection| / |discovery superset|`.
  5. Compare match rate against the zone tolerance: Zone 1 ≥ 95%, Zone 2 ≥ 99%, Zone 3 ≥ 99.5% (these are floor values; the binding tolerance is the PRE-04 baseline).
- **Expected result.** Match rate at or above the zone tolerance with both delta files explicitly produced (even if empty).
- **Pass criteria.** Match rate ≥ zone tolerance AND `delta-missing-from-sor.csv` row count is zero OR every row has a tracked remediation ticket open in the system of record. A non-empty `delta-missing-from-sor.csv` with no ticket coverage is FAIL.
- **Failure remediation.** For each row in `delta-missing-from-sor.csv`, open a remediation ticket assigned to the Inventory Owner with a due date inside the zone reconciliation cadence; for each row in `delta-missing-from-discovery.csv`, escalate to Control 3.6 (Orphaned Agent Detection) for lifecycle adjudication.
- **Evidence.** `delta-missing-from-sor.csv`, `delta-missing-from-discovery.csv`, `match-rate.json`.
- **Cadence.** Zone 1 quarterly · Zone 2 monthly · Zone 3 weekly.
- **Owner.** Inventory Owner.
- **Zone applicability.** All zones.

#### 3.1-COMP-03 — Per-surface missing-from-inventory detection

- **Objective.** Confirm the cycle can detect, per discovery surface, which agents are absent from the system of record. This decomposition prevents one healthy surface from masking blindness in another.
- **Pre-conditions.** COMP-01 PASS, COMP-02 reconciliation files produced.
- **Steps.**
  1. For each of the six surface exports (M365, PPAC, Entra, Agent 365, UAL, MDA), compute the per-surface delta against the system-of-record AgentID set.
  2. Write a per-surface delta file (`delta-{surface}-missing.csv`) with AgentID, surface row metadata, and reason classification (NEW / RENAMED / STALE-JOIN / SHADOW).
  3. Aggregate counts into `delta-by-surface.json`.
- **Expected result.** Six per-surface delta files exist (or skip-noted). Aggregated counts are produced.
- **Pass criteria.** Per-surface delta count for each surface is at or below the PRE-04 baseline tolerance, OR each delta row is tracked. A surface whose delta count exceeds 2× baseline is FAIL and triggers DRIFT-01 review.
- **Failure remediation.** Inspect the surface that exceeded tolerance; identify whether the gap is a surface refresh issue, a registration-process gap, or a shadow-IT signal; route SHADOW-classified rows to Control 3.6.
- **Evidence.** `delta-{surface}-missing.csv` × 6, `delta-by-surface.json`.
- **Cadence.** Zone 1 quarterly · Zone 2 monthly · Zone 3 weekly.
- **Owner.** Inventory Owner.
- **Zone applicability.** All zones.

#### 3.1-COMP-04 — PPAC display-ceiling and large-tenant enumeration

- **Objective.** Confirm that tenants whose agent population exceeds the 500-agent PPAC display ceiling do not silently truncate the inventory through reliance on the portal view.
- **Pre-conditions.** COMP-01 PASS.
- **Steps.**
  1. Compare the PPAC portal-visible agent count to the Azure Resource Graph and PowerShell (`Get-AdminPowerApp` filtered to `appType -eq "Agent"`) enumerations of the same tenant.
  2. If portal count ≥ 500 or within 10% of 500, the cycle MUST use the Resource Graph or PowerShell enumeration as the authoritative PPAC surface and record the fallback in `comp-04-ppac-ceiling.json`.
  3. Hash the Resource Graph / PowerShell output and store in `manifest.sha256`.
- **Expected result.** A documented decision on whether the portal export is sufficient or the fallback is required, with hashed evidence either way.
- **Pass criteria.** Portal export is used only if the count is materially below the ceiling; fallback enumeration is used and hashed if at/near the ceiling. Reliance on the portal view at/near ceiling without fallback is FAIL.
- **Failure remediation.** Re-execute COMP-01 step 2 with the Resource Graph or PowerShell enumeration; restart COMP-02 from the new PPAC surface.
- **Evidence.** `comp-04-ppac-ceiling.json`, `surface-ppac-arg.csv` or `surface-ppac-ps.csv`.
- **Cadence.** Zone 1 quarterly · Zone 2 monthly · Zone 3 weekly.
- **Owner.** Power Platform Admin.
- **Zone applicability.** All zones with > 250 agents; advisory below.

---

### 7.ACC — Metadata accuracy vs. source-of-truth systems

This family verifies that the metadata fields in the system of record match the upstream source-of-truth systems. The principle: the inventory does not invent metadata — it records what authoritative systems already say.

#### 3.1-ACC-01 — Owner field resolves to a current Entra identity

- **Objective.** Confirm every system-of-record Owner and Backup Owner field resolves to a currently active Entra user, and that the resolved user's account state is consistent with active employment / engagement.
- **Pre-conditions.** COMP-02 PASS.
- **Steps.**
  1. Extract the Owner and Backup Owner UPN / objectId for every agent in the system-of-record export.
  2. Resolve each identity via Microsoft Graph (`/users/{id}`) and capture: `accountEnabled`, `userType`, `assignedLicenses`, `employeeId` (if present), and the manager link (`/users/{id}/manager`).
  3. Build `acc-01-owner-resolution.csv` with one row per agent showing the owner state and the backup owner state.
  4. Classify each row: RESOLVED-ACTIVE, RESOLVED-DISABLED, RESOLVED-GUEST, UNRESOLVED.
- **Expected result.** Every agent row has a classification value. RESOLVED-ACTIVE for both owner slots is the expected default for Zone 2 / Zone 3 agents.
- **Pass criteria.** Zone 3: 100% of Owner rows are RESOLVED-ACTIVE. Zone 2: ≥ 99% RESOLVED-ACTIVE for Owner; Backup Owner present for 100% and ≥ 95% RESOLVED-ACTIVE. Zone 1: ≥ 95% RESOLVED-ACTIVE for Owner. RESOLVED-DISABLED or UNRESOLVED rows are FAIL and route to OWN-02.
- **Failure remediation.** Open an OWN-02 reassignment workflow for each non-RESOLVED-ACTIVE row; freeze the agent at lifecycle state Active-Pending-Reassignment until reassignment closes.
- **Evidence.** `acc-01-owner-resolution.csv`, `acc-01-summary.json`.
- **Cadence.** Zone 1 quarterly · Zone 2 monthly · Zone 3 weekly.
- **Owner.** Inventory Owner.
- **Zone applicability.** All zones.

#### 3.1-ACC-02 — Lifecycle state matches deployment state

- **Objective.** Confirm the inventory Lifecycle State for every agent matches the agent's actual deployment state at the platform layer (Active in inventory ↔ deployable / callable at the platform; Decommissioned ↔ disabled or removed).
- **Pre-conditions.** COMP-01 PASS.
- **Steps.**
  1. For each agent in the system-of-record export, capture the inventory Lifecycle State value.
  2. From the per-surface exports, capture the platform-observed state (e.g., PPAC `Status`, M365 admin agent `Published` flag, Entra Agent ID `accountEnabled`, Agent 365 enabled flag where present).
  3. Build a coherence matrix `acc-02-lifecycle-coherence.csv` mapping inventory state to platform state per surface.
  4. Classify each row: COHERENT, INVENTORY-AHEAD (inventory shows decommissioned but platform shows active), PLATFORM-AHEAD (platform shows deleted but inventory shows active), or AMBIGUOUS.
- **Expected result.** COHERENT for the overwhelming majority of agents.
- **Pass criteria.** Zone 3: 100% COHERENT or actively-tracked-delta. Zone 2: ≥ 99% COHERENT. Zone 1: ≥ 95% COHERENT. Any PLATFORM-AHEAD row is a hard FAIL — an inventory record marked Active for an agent that no longer exists at the platform layer is a books-and-records integrity break.
- **Failure remediation.** PLATFORM-AHEAD rows trigger immediate LIFE-03 escalation and Control 3.6 review. INVENTORY-AHEAD rows trigger a deployment-disable workflow.
- **Evidence.** `acc-02-lifecycle-coherence.csv`, `acc-02-summary.json`.
- **Cadence.** Zone 1 quarterly · Zone 2 monthly · Zone 3 weekly.
- **Owner.** Inventory Owner.
- **Zone applicability.** All zones.

#### 3.1-ACC-03 — Effective sensitivity label matches MIP source-of-truth

- **Objective.** Confirm that for any agent grounded on labeled content or operating under MIP label inheritance, the Effective Sensitivity Label recorded in the system of record matches the highest label MIP would compute against the agent's grounding sources at cycle time.
- **Pre-conditions.** COMP-02 PASS; PRE-03 confirms MIP entitlement.
- **Steps.**
  1. For each Zone 2 / Zone 3 agent with grounding sources, enumerate the grounding source set from the inventory and from the platform.
  2. For each grounding source, query the current MIP label via Graph or the SharePoint API and capture the label name and priority.
  3. Compute the highest label across the agent's grounding set and compare to the inventory's Effective Sensitivity Label.
  4. Build `acc-03-mip-coherence.csv` and classify: MATCH, INVENTORY-LOWER (inventory under-states the label), INVENTORY-HIGHER (inventory over-states the label — acceptable but flagged), or UNRESOLVED.
- **Expected result.** MATCH or INVENTORY-HIGHER for the overwhelming majority. INVENTORY-LOWER is a sensitivity gap.
- **Pass criteria.** Zone 3: 0 INVENTORY-LOWER rows. Zone 2: ≤ baseline tolerance INVENTORY-LOWER rows, all tracked. Zone 1: advisory only.
- **Failure remediation.** INVENTORY-LOWER rows trigger an inventory metadata correction and an immediate review of any DLP scope tied to the corrected label.
- **Evidence.** `acc-03-mip-coherence.csv`, `acc-03-summary.json`.
- **Cadence.** Zone 1 advisory · Zone 2 monthly · Zone 3 weekly.
- **Owner.** Inventory Owner (with Purview Compliance Admin support).
- **Zone applicability.** Zone 2, Zone 3; advisory in Zone 1.

#### 3.1-ACC-04 — DLP policy mapping resolves to a current Purview policy

- **Objective.** Confirm every DLP Policy Mapping value in the system of record resolves to a currently-existing Purview DLP policy in the correct workload, and that the policy is in `Enabled` state.
- **Pre-conditions.** COMP-02 PASS; PRE-03 confirms Purview DLP entitlement.
- **Steps.**
  1. Extract the DLP Policy Mapping field for every agent in the system-of-record export.
  2. Enumerate Purview DLP policies via the Compliance PowerShell (`Get-DlpCompliancePolicy`) and the equivalent Power Platform DLP policy enumeration.
  3. Resolve each inventory DLP mapping against the live policy set; capture policy ID, mode (`Enable` / `TestWithNotifications` / `Disable`), and last-modified timestamp.
  4. Build `acc-04-dlp-resolution.csv` and classify: RESOLVED-ENABLED, RESOLVED-TEST, RESOLVED-DISABLED, UNRESOLVED.
- **Expected result.** RESOLVED-ENABLED for production-state Zone 2 / Zone 3 agents.
- **Pass criteria.** Zone 3: 100% RESOLVED-ENABLED. Zone 2: ≥ 99% RESOLVED-ENABLED, with the rest tracked. UNRESOLVED rows are FAIL and route to DLP-02.
- **Failure remediation.** UNRESOLVED rows trigger an immediate DLP-02 orphan-DLP workflow; RESOLVED-DISABLED rows trigger a DLP policy review.
- **Evidence.** `acc-04-dlp-resolution.csv`, `acc-04-summary.json`.
- **Cadence.** Zone 1 advisory · Zone 2 monthly · Zone 3 weekly.
- **Owner.** Purview Compliance Admin.
- **Zone applicability.** Zone 2, Zone 3.

---

### 7.DRIFT — New / modified agent detection and re-attestation

This family verifies that newly created agents are auto-discovered within the zone-defined SLA, that modifications to existing agents trigger re-attestation, and that the audit trail of metadata changes is intact.

#### 3.1-DRIFT-01 — New-agent detection within zone SLA

- **Objective.** Confirm that agents created since the previous cycle are present in the system of record within the zone-defined detection SLA.
- **Pre-conditions.** COMP-01 PASS, PRE-04 baseline established.
- **Steps.**
  1. From `surface-ual.csv`, extract `AgentCreated` (or equivalent registration) events with timestamps in the trailing reconciliation window.
  2. For each created-event AgentID, locate the corresponding system-of-record entry and compute the elapsed time between platform creation and SoR appearance.
  3. Compare elapsed time to the zone SLA: Zone 1 ≤ 30 days, Zone 2 ≤ 7 days, Zone 3 ≤ 24 hours (or the PRE-04 calibrated baseline if tighter).
  4. Build `drift-01-new-agent-detection.csv` with one row per created agent, the elapsed time, and the SLA-met flag.
- **Expected result.** Every newly-created agent in the window appears in the system of record within SLA.
- **Pass criteria.** Zone 3: 100% within SLA. Zone 2: ≥ 99% within SLA. Zone 1: ≥ 95% within SLA. Out-of-SLA rows are FAIL.
- **Failure remediation.** Investigate the registration-process gap (was the discovery feed broken? was the auto-registration workflow disabled?); reopen Control 1.2 (Agent Registry) review for the affected scope.
- **Evidence.** `drift-01-new-agent-detection.csv`, `drift-01-summary.json`.
- **Cadence.** Zone 1 monthly · Zone 2 weekly · Zone 3 daily (automated).
- **Owner.** Inventory Owner.
- **Zone applicability.** All zones.

#### 3.1-DRIFT-02 — Modified-agent re-attestation trigger

- **Objective.** Confirm that material modifications to existing agents (connector added/removed, knowledge source changed, model changed, sensitivity scope changed) trigger an inventory re-attestation event within the zone SLA.
- **Pre-conditions.** COMP-01 PASS.
- **Steps.**
  1. From `surface-ual.csv`, extract `AgentUpdated` events of material types (connector, knowledge source, model, scope) for the trailing reconciliation window.
  2. For each updated-event AgentID, query the system-of-record audit log for a corresponding re-attestation event.
  3. Compute elapsed time between platform modification and re-attestation; compare to zone SLA: Zone 1 ≤ 30 days, Zone 2 ≤ 7 days, Zone 3 ≤ 48 hours.
  4. Build `drift-02-reattestation.csv` with one row per material modification.
- **Expected result.** Every material modification triggers a re-attestation within SLA.
- **Pass criteria.** Zone 3: 100% within SLA. Zone 2: ≥ 99% within SLA. Zone 1: ≥ 95% within SLA. Modifications without any re-attestation event are FAIL and route to LIFE-03.
- **Failure remediation.** Open a re-attestation backfill workflow for each affected agent; review the Control 2.13 documentation trigger configuration.
- **Evidence.** `drift-02-reattestation.csv`, `drift-02-summary.json`.
- **Cadence.** Zone 1 monthly · Zone 2 weekly · Zone 3 daily.
- **Owner.** Inventory Owner.
- **Zone applicability.** All zones.

#### 3.1-DRIFT-03 — Metadata change audit trail integrity

- **Objective.** Confirm the audit trail of metadata changes in the system of record is complete, immutable, and chained, so that "who changed what when" is reconstructable for the books-and-records retention window.
- **Pre-conditions.** PRE-07 PASS.
- **Steps.**
  1. Pull the system-of-record version-history / audit log for the trailing reconciliation window.
  2. For each change event, capture: AgentID, field, old value, new value, change actor (Entra identity), timestamp.
  3. Cross-reference against `surface-ual.csv` for any platform events that should have produced a metadata change but did not.
  4. Recompute the cycle hash chain (see §1.2) and confirm the previous cycle's `manifestHash` equals this cycle's `previousManifestHash`.
- **Expected result.** Every metadata change has an audit row with actor and timestamp. The hash chain across cycles is unbroken.
- **Pass criteria.** No orphan changes (changes with no actor or no timestamp). No platform events missing a corresponding metadata change. Hash chain unbroken. Any chain break is FAIL and triggers an Internal Audit referral.
- **Failure remediation.** Chain breaks trigger immediate Compliance Officer review and AI Incident Response Playbook activation; orphan changes trigger system-of-record audit configuration review.
- **Evidence.** `drift-03-audit-trail.csv`, `drift-03-chain-verify.json`.
- **Cadence.** Zone 1 monthly · Zone 2 weekly · Zone 3 daily.
- **Owner.** Inventory Owner (with Internal Audit review on chain-break).
- **Zone applicability.** All zones.

---

### 7.OWN — Owner / Backup Owner accountability

This family verifies that every agent has a named, current, accountable Owner and (for Zone 2 / Zone 3) a Backup Owner; that departed-owner events trigger reassignment within SLA; and that the manager-hierarchy fallback works.

#### 3.1-OWN-01 — Every agent has a named Owner and Backup Owner per zone rules

- **Objective.** Confirm the structural ownership rule: Zone 1 requires a named Owner; Zone 2 and Zone 3 require both a named Owner and a named Backup Owner. Both must resolve to current, distinct Entra identities.
- **Pre-conditions.** ACC-01 PASS.
- **Steps.**
  1. From the system-of-record export, extract Owner and Backup Owner fields for every agent.
  2. Confirm field non-emptiness per zone rule. Confirm Owner and Backup Owner are distinct Entra identities (no self-backup).
  3. Build `own-01-ownership.csv` and classify: COMPLIANT, MISSING-OWNER, MISSING-BACKUP, SELF-BACKUP.
- **Expected result.** COMPLIANT for the overwhelming majority.
- **Pass criteria.** Zone 3: 100% COMPLIANT. Zone 2: 100% COMPLIANT. Zone 1: ≥ 99% Owner-named. Any non-COMPLIANT row is FAIL.
- **Failure remediation.** MISSING-OWNER and MISSING-BACKUP rows trigger an immediate ownership-assignment workflow; SELF-BACKUP rows trigger a backup-reassignment workflow. Agents with no resolvable owner after the SLA window route to Control 3.6.
- **Evidence.** `own-01-ownership.csv`, `own-01-summary.json`.
- **Cadence.** Zone 1 quarterly · Zone 2 monthly · Zone 3 monthly.
- **Owner.** Inventory Owner.
- **Zone applicability.** All zones.

#### 3.1-OWN-02 — Departed-owner reassignment within SLA

- **Objective.** Confirm that when an Owner or Backup Owner is detected as disabled, deleted, or off-boarded in Entra, a reassignment workflow opens and closes within the zone SLA.
- **Pre-conditions.** ACC-01 PASS.
- **Steps.**
  1. From `acc-01-owner-resolution.csv`, extract every row classified RESOLVED-DISABLED or UNRESOLVED.
  2. For each affected agent, query the reassignment ticket queue for a corresponding open or recently-closed ticket.
  3. Compute the elapsed time between the Entra disable/delete event (from UAL or Entra audit) and the ticket open / close event.
  4. Compare to zone SLA: Zone 1 ≤ 30 days, Zone 2 ≤ 14 days, Zone 3 ≤ 5 business days.
  5. Build `own-02-reassignment-sla.csv`.
- **Expected result.** Every departed-owner event has an associated reassignment ticket within SLA.
- **Pass criteria.** Zone 3: 100% within SLA, all closed or actively in-progress with documented escalation if past 50% of SLA. Zone 2: ≥ 99% within SLA. Zone 1: ≥ 95% within SLA. Out-of-SLA rows are FAIL.
- **Failure remediation.** Open backlog ticket review with the Inventory Owner; if no reassignment is feasible (the agent's business sponsor has also departed), route to Control 3.6 for orphan adjudication.
- **Evidence.** `own-02-reassignment-sla.csv`, `own-02-summary.json`.
- **Cadence.** Zone 1 quarterly · Zone 2 monthly · Zone 3 monthly.
- **Owner.** Inventory Owner.
- **Zone applicability.** All zones.

#### 3.1-OWN-03 — Manager-hierarchy fallback functional

- **Objective.** Confirm that when an agent's Owner becomes unresolvable and the Backup Owner also fails to resolve, the manager-hierarchy fallback assigns provisional ownership to the departed owner's manager (or the highest-level resolvable manager up the chain) within the SLA.
- **Pre-conditions.** OWN-01, OWN-02 evidence captured.
- **Steps.**
  1. From `own-02-reassignment-sla.csv`, extract rows where both Owner and Backup Owner were unresolvable at the same cycle.
  2. For each row, query the system of record for the provisional-owner field; verify the value is the current resolvable manager of the departed Owner per Entra `/users/{id}/manager`.
  3. Confirm the provisional-owner notification record exists in the ticketing system and that the provisional owner has acknowledged or escalated.
  4. Build `own-03-manager-fallback.csv`.
- **Expected result.** Every dual-departed agent has a provisional-owner record resolving up the manager chain.
- **Pass criteria.** Zone 3: 100% have a provisional-owner resolution and notification within 72 hours of dual departure. Zone 2: 100% within 14 days. Zone 1: 100% within 30 days. Missing fallback is FAIL and routes to Control 3.6.
- **Failure remediation.** Manual provisional-owner assignment by the AI Governance Lead; review of the manager-hierarchy automation configuration.
- **Evidence.** `own-03-manager-fallback.csv`, `own-03-summary.json`.
- **Cadence.** Zone 1 quarterly · Zone 2 monthly · Zone 3 monthly.
- **Owner.** AI Governance Lead.
- **Zone applicability.** All zones.

---

### 7.LIFE — Lifecycle state integrity

This family verifies that lifecycle states match expected behavior: agents do not languish in Draft, Decommissioned agents have retention pinned, state transitions are audited, and there are no Active-but-platform-deleted records.

#### 3.1-LIFE-01 — No agents stuck in Draft beyond threshold

- **Objective.** Confirm no agent has been in Draft state beyond the firm-defined threshold (default 30 days; tighter per zone if calibrated in PRE-04). Long-Draft agents represent stalled approvals or abandoned registrations and are an inventory hygiene signal.
- **Pre-conditions.** COMP-02 PASS.
- **Steps.**
  1. From the system-of-record export, extract every agent in Lifecycle State `Draft` together with the state-entry timestamp.
  2. Compute days-in-draft for each row.
  3. Compare to the threshold: Zone 1 ≤ 60 days, Zone 2 ≤ 30 days, Zone 3 ≤ 14 days.
  4. Build `life-01-stuck-draft.csv`.
- **Expected result.** No rows exceed the zone threshold, or every exceeding row has a tracked exception with a documented reason.
- **Pass criteria.** Zone 3: 0 unexcepted rows over threshold. Zone 2: ≤ 2 unexcepted rows over threshold. Zone 1: ≤ 5 unexcepted rows over threshold. Otherwise FAIL.
- **Failure remediation.** Long-Draft agents trigger an outreach to the named Owner; agents with no Owner response within 14 days are auto-Decommissioned per the Control 3.6 workflow.
- **Evidence.** `life-01-stuck-draft.csv`, `life-01-summary.json`.
- **Cadence.** Zone 1 quarterly · Zone 2 monthly · Zone 3 monthly.
- **Owner.** Inventory Owner.
- **Zone applicability.** All zones.

#### 3.1-LIFE-02 — Decommissioned agents have retention pin and disposition record

- **Objective.** Confirm every agent in Lifecycle State `Decommissioned` has a retention-pin record (a Purview retention label or equivalent system-of-record retention flag) and a documented disposition record so that books-and-records retention runs against the correct artifact set.
- **Pre-conditions.** COMP-01 PASS.
- **Steps.**
  1. From the system-of-record export, extract every agent in Lifecycle State `Decommissioned`.
  2. For each row, verify (a) retention pin is set with a documented retention period appropriate to the regulatory scope (e.g., SEC 17a-4 ≥ 6 years for broker-dealer communications), (b) the disposition record exists and references the decommission ticket, and (c) the platform-side state shows disabled / removed.
  3. Build `life-02-decommission.csv`.
- **Expected result.** Every Decommissioned agent has retention pin, disposition record, and platform-side disablement.
- **Pass criteria.** 100% of Decommissioned agents satisfy all three conditions across all zones. Any failure is a books-and-records integrity FAIL with mandatory Compliance Officer escalation.
- **Failure remediation.** Backfill missing retention pins and disposition records; if platform-side disablement is missing, reopen the decommission workflow and re-execute platform removal.
- **Evidence.** `life-02-decommission.csv`, `life-02-summary.json`.
- **Cadence.** Zone 1 quarterly · Zone 2 monthly · Zone 3 monthly.
- **Owner.** Compliance Officer.
- **Zone applicability.** All zones; binding rule.

#### 3.1-LIFE-03 — State transitions audited; no Active-but-platform-deleted records

- **Objective.** Confirm every lifecycle state transition is captured in the system-of-record audit log AND that there exist zero rows where the inventory state is `Active` but the platform shows the agent as deleted (the inverse of ACC-02 from a transition-history perspective).
- **Pre-conditions.** ACC-02 PASS, DRIFT-03 PASS.
- **Steps.**
  1. Cross-reference the lifecycle state-transition events in the system-of-record audit log with the platform-state events in `surface-ual.csv`.
  2. Identify any AgentID where the most-recent inventory state is `Active` and the most-recent platform event is `AgentDeleted` or equivalent.
  3. Identify any AgentID where the platform shows lifecycle change events (publish, unpublish, archive) without a corresponding system-of-record state transition entry.
  4. Build `life-03-transition-coherence.csv`.
- **Expected result.** Zero Active-but-deleted rows. Every platform lifecycle event has a matched SoR transition entry within the DRIFT-02 SLA.
- **Pass criteria.** Active-but-deleted count = 0 across all zones. Zone 3: 100% of platform lifecycle events have a matched SoR transition. Zone 2: ≥ 99%. Zone 1: ≥ 95%. Active-but-deleted is a hard FAIL.
- **Failure remediation.** Active-but-deleted rows trigger an immediate Compliance Officer review, an AI Incident Response Playbook activation, and a 7-day root-cause review covering the registration / decommission workflow integrity.
- **Evidence.** `life-03-transition-coherence.csv`, `life-03-summary.json`.
- **Cadence.** Zone 1 quarterly · Zone 2 monthly · Zone 3 monthly.
- **Owner.** Compliance Officer.
- **Zone applicability.** All zones; binding rule.

---

### 7.DLP — DLP policy mapping completeness

This family verifies that every Zone 2 / Zone 3 agent has a DLP scope assignment in the inventory; that orphaned DLP-less agents are flagged for remediation; and that DLP scope coheres with environment classification.

#### 3.1-DLP-01 — Every Zone 2 / Zone 3 agent has a DLP scope assignment

- **Objective.** Confirm structural completeness: every Zone 2 and Zone 3 agent in the system of record has a non-empty DLP Policy Mapping field that references at least one Purview DLP policy AND/OR Power Platform DLP policy.
- **Pre-conditions.** COMP-02 PASS, ACC-04 PASS.
- **Steps.**
  1. Filter the system-of-record export to Zone 2 and Zone 3 agents.
  2. For each filtered agent, confirm the DLP Policy Mapping field is non-empty and references at least one resolvable policy (per ACC-04).
  3. Build `dlp-01-scope-coverage.csv` and classify: SCOPED, SCOPE-MISSING, SCOPE-UNRESOLVED.
- **Expected result.** SCOPED for 100% of Zone 2 / Zone 3 agents.
- **Pass criteria.** Zone 3: 100% SCOPED. Zone 2: 100% SCOPED. Any SCOPE-MISSING or SCOPE-UNRESOLVED row is FAIL and routes to DLP-02.
- **Failure remediation.** Open a DLP-scoping ticket for each affected agent; pause the agent at lifecycle Active-Pending-Scope until DLP scope is assigned and reflected in inventory.
- **Evidence.** `dlp-01-scope-coverage.csv`, `dlp-01-summary.json`.
- **Cadence.** Zone 1 advisory · Zone 2 quarterly · Zone 3 monthly.
- **Owner.** Purview Compliance Admin.
- **Zone applicability.** Zone 2, Zone 3.

#### 3.1-DLP-02 — Orphaned DLP-less agents flagged for remediation

- **Objective.** Confirm that any agent flagged as SCOPE-MISSING in DLP-01 has an open remediation ticket within the zone SLA, and that the ticket queue is being worked.
- **Pre-conditions.** DLP-01 evidence available.
- **Steps.**
  1. From `dlp-01-scope-coverage.csv`, extract all SCOPE-MISSING and SCOPE-UNRESOLVED rows.
  2. For each row, query the remediation ticket queue for an open ticket; capture ticket age.
  3. Compute mean and p95 of ticket age; compare to zone SLA: Zone 2 ≤ 30 days, Zone 3 ≤ 14 days.
  4. Build `dlp-02-orphan-tickets.csv`.
- **Expected result.** Every orphaned-DLP agent has an open ticket within SLA.
- **Pass criteria.** Zone 3: 100% have ticket within SLA. Zone 2: ≥ 95% within SLA. Otherwise FAIL.
- **Failure remediation.** Backfill missing tickets and escalate aged tickets; review the auto-ticket-creation workflow.
- **Evidence.** `dlp-02-orphan-tickets.csv`, `dlp-02-summary.json`.
- **Cadence.** Zone 1 advisory · Zone 2 quarterly · Zone 3 monthly.
- **Owner.** Purview Compliance Admin.
- **Zone applicability.** Zone 2, Zone 3.

#### 3.1-DLP-03 — DLP scope coheres with environment classification

- **Objective.** Confirm the DLP scope assigned to each agent is consistent with the agent's host environment classification (Control 2.1 Managed Environments / Control 2.2 Environment Groups). A Zone 3 agent in a Production environment should not be scoped to a Test-tier DLP policy.
- **Pre-conditions.** DLP-01 PASS; environment classification export available from Control 2.1 evidence.
- **Steps.**
  1. Join the system-of-record export with the Control 2.1 environment classification by EnvironmentId.
  2. For each agent, validate that the assigned DLP policy's environment scope matches the host environment's tier (Production-tier DLP for Production environments, etc.).
  3. Build `dlp-03-scope-coherence.csv` and classify: COHERENT, MISMATCH, UNRESOLVED.
- **Expected result.** COHERENT for the overwhelming majority.
- **Pass criteria.** Zone 3: 100% COHERENT. Zone 2: ≥ 99% COHERENT. MISMATCH rows are FAIL.
- **Failure remediation.** MISMATCH rows trigger immediate DLP scope correction; chronic mismatches indicate a Control 2.1 / 2.2 configuration gap and should escalate to AI Governance Lead.
- **Evidence.** `dlp-03-scope-coherence.csv`, `dlp-03-summary.json`.
- **Cadence.** Zone 1 advisory · Zone 2 quarterly · Zone 3 monthly.
- **Owner.** Purview Compliance Admin.
- **Zone applicability.** Zone 2, Zone 3.

---

### 7.REG — Regulatory-scope tagging completeness

This family verifies that agents touching regulated processes are tagged into the corresponding supervisory inventory: FINRA Communications, SOX ICFR, GLBA / FTC Safeguards, and any firm-specific regimes (Reg BI, MNPI, NYDFS Part 500).

#### 3.1-REG-01 — FINRA Communications-scope agents flagged for supervisory review

- **Objective.** Confirm every agent that produces, drafts, or surfaces content classifiable as a "communication with the public" under FINRA Rule 2210 (with RN 24-09 for AI supervisory guidance) is tagged with the FINRA Communications regulatory-scope flag and is referenced in the supervisory review queue (Control 1.7 / supervisory archive).
- **Pre-conditions.** COMP-02 PASS; FINRA scope policy from PRE-01 charter.
- **Steps.**
  1. From the system-of-record export, identify agents whose business justification, connected actions, or output destinations match the firm's FINRA Communications inclusion rule (e.g., agents that draft client emails, generate marketing content, or surface broker-dealer correspondence).
  2. Confirm each candidate has the `RegulatoryScope.FINRA-Communications` flag set in inventory.
  3. Confirm each tagged agent has a corresponding entry in the supervisory archive / Control 1.7 audit-feed configuration.
  4. Build `reg-01-finra-communications.csv` and classify: TAGGED-AND-ARCHIVED, TAGGED-NOT-ARCHIVED, NOT-TAGGED-CANDIDATE, OUT-OF-SCOPE.
- **Expected result.** TAGGED-AND-ARCHIVED for every in-scope agent.
- **Pass criteria.** Zone 3: 100% TAGGED-AND-ARCHIVED for in-scope agents. Zone 2: 100% TAGGED-AND-ARCHIVED. NOT-TAGGED-CANDIDATE rows are FAIL and require Compliance Officer adjudication within 5 business days.
- **Failure remediation.** Backfill missing tags; if archival feed is missing, escalate to Control 1.7 owner; document any OUT-OF-SCOPE determination with Compliance Officer signature.
- **Evidence.** `reg-01-finra-communications.csv`, `reg-01-summary.json`.
- **Cadence.** Zone 1 annual · Zone 2 quarterly · Zone 3 quarterly.
- **Owner.** Compliance Officer.
- **Zone applicability.** All zones with FINRA-regulated activity.

#### 3.1-REG-02 — SOX-scope agents present in ICFR inventory

- **Objective.** Confirm every agent that influences finance, controllership, disclosure drafting, reconciliations, journal-entry workflows, or any other ICFR-relevant process is tagged with the SOX regulatory-scope flag and is present in the firm's ICFR inventory.
- **Pre-conditions.** COMP-02 PASS.
- **Steps.**
  1. Cross-reference the system-of-record export against the firm's SOX scoping inclusion rule (financial reporting connectors, GL data sources, controllership SharePoint sites, etc.).
  2. Confirm each candidate has `RegulatoryScope.SOX-ICFR` set and is present in the firm's SOX ICFR inventory (typically a GRC tool).
  3. Build `reg-02-sox-icfr.csv` and classify: ICFR-PRESENT, ICFR-MISSING, NOT-TAGGED-CANDIDATE, OUT-OF-SCOPE.
- **Expected result.** ICFR-PRESENT for every in-scope agent.
- **Pass criteria.** 100% ICFR-PRESENT for in-scope agents across Zone 2 / Zone 3. ICFR-MISSING is FAIL with mandatory escalation to the SOX program owner and AI Governance Lead.
- **Failure remediation.** Open a SOX-inventory backfill ticket; pause the agent at lifecycle Active-Pending-SOX-Review until the ICFR inventory entry exists and the SOX testing plan covers the agent.
- **Evidence.** `reg-02-sox-icfr.csv`, `reg-02-summary.json`.
- **Cadence.** Zone 1 annual · Zone 2 quarterly · Zone 3 quarterly.
- **Owner.** Compliance Officer (with SOX program owner).
- **Zone applicability.** All zones with SOX exposure.

#### 3.1-REG-03 — GLBA / FTC Safeguards / NYDFS Part 500 scope completeness

- **Objective.** Confirm every agent that accesses or processes customer information (NPI under GLBA, customer information under FTC Safeguards 16 CFR §314, or covered information under NYDFS Part 500.16 / 500.17) is tagged with the appropriate regulatory-scope flag and is recoverable for examiner pull.
- **Pre-conditions.** COMP-02 PASS, ACC-03 PASS.
- **Steps.**
  1. Identify agents whose grounding sources or connected actions touch customer NPI / covered information using the firm's data-classification taxonomy and the MIP labels resolved in ACC-03.
  2. Confirm each candidate has `RegulatoryScope.GLBA`, `RegulatoryScope.FTC-Safeguards`, and/or `RegulatoryScope.NYDFS-500` set as applicable.
  3. For NYDFS-covered entities, confirm the inventory record includes RTO/RPO, criticality tier, support expiration, and backup-compliance status per Control 3.1's NYDFS extension fields.
  4. Build `reg-03-glba-nydfs.csv`.
- **Expected result.** All in-scope agents tagged correctly with the relevant regimes; NYDFS extension fields populated for covered entities.
- **Pass criteria.** Zone 3: 100% tagged. Zone 2: 100% tagged. NYDFS extension fields 100% populated for covered entities. Otherwise FAIL.
- **Failure remediation.** Backfill regulatory-scope flags; for NYDFS extension fields, work with the entity's CISO function to populate.
- **Evidence.** `reg-03-glba-nydfs.csv`, `reg-03-summary.json`.
- **Cadence.** Zone 1 annual · Zone 2 quarterly · Zone 3 quarterly.
- **Owner.** Compliance Officer.
- **Zone applicability.** All zones with customer-information exposure.

---

## Section 7 — Reconciliation evidence pack

The reconciliation evidence pack is the deliverable assembled by the Inventory Owner each cycle and submitted to the Validator and Compliance signatures. It is the single artifact handed to internal audit and external examiners on request.

### 8.1 Pack contents (per cycle)

| Folder | Contents | Source test |
|---|---|---|
| `pre/` | All PRE-01 through PRE-07 evidence files | Section 5 |
| `surfaces/` | Six per-surface CSV exports with capture timestamps | COMP-01 |
| `deltas/` | `delta-missing-from-sor.csv`, `delta-missing-from-discovery.csv`, six per-surface delta files, `delta-by-surface.json`, `match-rate.json` | COMP-02, COMP-03 |
| `acc/` | `acc-01-owner-resolution.csv`, `acc-02-lifecycle-coherence.csv`, `acc-03-mip-coherence.csv`, `acc-04-dlp-resolution.csv` plus summaries | ACC-01..04 |
| `drift/` | `drift-01-new-agent-detection.csv`, `drift-02-reattestation.csv`, `drift-03-audit-trail.csv`, `drift-03-chain-verify.json` | DRIFT-01..03 |
| `own/` | `own-01-ownership.csv`, `own-02-reassignment-sla.csv`, `own-03-manager-fallback.csv` plus summaries | OWN-01..03 |
| `life/` | `life-01-stuck-draft.csv`, `life-02-decommission.csv`, `life-03-transition-coherence.csv` plus summaries | LIFE-01..03 |
| `dlp/` | `dlp-01-scope-coverage.csv`, `dlp-02-orphan-tickets.csv`, `dlp-03-scope-coherence.csv` plus summaries | DLP-01..03 |
| `reg/` | `reg-01-finra-communications.csv`, `reg-02-sox-icfr.csv`, `reg-03-glba-nydfs.csv` plus summaries | REG-01..03 |

| `manifest.sha256` | One SHA-256 per artifact in the pack | All |
| `attestation.json` | Three signature objects, hash chain, `cycleId`, `previousCycleId`, `previousManifestHash`, `manifestHash`, `chainHash` | Section 1 |
| `cycle-summary.md` | Human-readable cycle summary: pass/fail per test, deltas, exceptions, escalations | Cycle owner |
| `exceptions/` | One JSON file per active exception with owner, expiry, and re-test trigger | Cross-cycle |

### 8.2 Storage and retention

The evidence pack is written to a WORM-equivalent immutable store (Purview retention label with locked policy, or equivalent). Retention is the longest of:

- 7 years for FINRA Rule 4511 / SEC 17a-4(b)(4) books-and-records scope
- 7 years for SOX-tagged agents
- 6 years for GLBA / FTC Safeguards
- 3 years for the firm's NIST AI RMF inventory program baseline
- The retention period required by NYDFS Part 500 for covered entities

Each evidence pack carries a Purview retention label that pins the longest applicable period. Disposition review at end-of-retention is logged through the standard records-disposition workflow.

### 8.3 Manifest format

`manifest.sha256` is a plain-text file with one entry per artifact in the format:

```
<sha256-hex>  <relative-path-from-pack-root>
```

Hashes are computed at pack-assembly time and re-verified at Validator review and Compliance review. Hash mismatch at any stage is a cycle-stopping FAIL and triggers AI Incident Response Playbook activation.

### 8.4 Reconciliation delta narrative

In addition to machine-readable delta files, `cycle-summary.md` includes a one-paragraph narrative for each non-zero delta:

- Which surface produced the delta
- The classification breakdown (NEW / RENAMED / STALE-JOIN / SHADOW)
- The remediation tickets opened, with links
- The expected close date relative to the zone SLA
- Whether the delta is rising, falling, or stable across the trailing three cycles

The narrative is the artifact a regulator reads first; the CSVs are the artifact a regulator audits second.

---

## Section 8 — Quarterly inventory audit procedure (examiner-style)

The cycle-level evidence pack supports continuous attestation. The quarterly examiner-style audit is an additional, independent walkthrough designed to mirror what a FINRA, OCC, Federal Reserve, SEC, or internal-audit examiner would request. It is run by Internal Audit (not the Inventory Owner) using a randomized sample.

### 9.1 Sample design

| Population | Sample size (Zone 3) | Sample size (Zone 2) | Sample size (Zone 1) |
|---|---|---|---|
| Active agents | min(60, 10% of population) | min(30, 5% of population) | min(15, 2% of population) |
| Decommissioned agents (trailing 12 months) | min(15, 10%) | min(10, 5%) | min(5, 2%) |
| Newly-registered agents (trailing quarter) | 100% if ≤ 25; else min(25, 25%) | 100% if ≤ 15; else min(15, 25%) | min(10, 25%) |
| Owner-reassignment events (trailing quarter) | 100% if ≤ 10; else min(10, 50%) | 100% if ≤ 5; else min(5, 50%) | All |

Sample selection is **randomized using a published seeded PRNG** so that the sample can be reproduced for audit replay. The seed is stored in the audit pack and rotated each quarter.

### 9.2 Per-record validation steps

For each sampled agent, Internal Audit independently verifies (without relying on the Inventory Owner's prior evidence):

1. **Existence in the system of record.** AgentID resolves to a system-of-record entry.
2. **Existence in at least one discovery surface.** AgentID is present in the surface that should host it (PPAC for Power Platform agents, M365 admin center for declarative / shared agents, etc.).
3. **Owner resolution.** Owner UPN resolves to a current Entra identity; Backup Owner resolves for Zone 2 / Zone 3.
4. **Lifecycle coherence.** Inventory state matches platform-observed state.
5. **DLP scope.** Resolves to a current Purview / Power Platform DLP policy in `Enable` state for Zone 2 / Zone 3.
6. **Regulatory tags.** Inclusion or exclusion from FINRA Communications, SOX ICFR, GLBA, NYDFS Part 500 matches the firm's adjudication rule when applied to the agent's connectors and grounding sources.
8. **Audit trail.** The system-of-record audit log shows the agent's complete history of metadata changes for the trailing quarter.
9. **Evidence pack reference.** The agent appears in at least the most recent cycle's evidence pack with consistent classification.
10. **Disposition (Decommissioned only).** Retention pin set, disposition record present, platform-side disablement confirmed.

### 9.3 Findings classification

Each per-record check returns PASS, EXCEPTION (the firm has a tracked exception for this discrepancy), or FINDING (an unexpected discrepancy). Findings are classified by severity:

| Severity | Definition | Required response |
|---|---|---|
| **Critical** | Active-but-deleted, missing owner with no fallback, missing FINRA / SOX tag for in-scope agent, hash chain break | Immediate AI Incident Response Playbook activation; Compliance Officer escalation; remediation within 5 business days |
| **High** | Owner unresolved, DLP scope unresolved, lifecycle mismatch | Remediation within 14 business days; cycle-level RCA in next cycle's `cycle-summary.md` |
| **Medium** | Stale Backup Owner, Draft > threshold, missing audit-trail entry | Remediation within 30 days |
| **Low** | Cosmetic metadata staleness without regulatory implication | Bundled remediation within next cycle |

### 9.4 Audit deliverables

The quarterly audit produces:

- `q-audit-{YYYY-Qn}-sample.csv` — the sampled AgentIDs and seed
- `q-audit-{YYYY-Qn}-findings.csv` — one row per per-record check with PASS / EXCEPTION / FINDING and severity
- `q-audit-{YYYY-Qn}-narrative.md` — examiner-style narrative summarizing scope, method, results, and recommended actions
- `q-audit-{YYYY-Qn}-attestation.json` — Internal Audit signature

The quarterly audit is an input to the next continuous-cycle attestation chain. Findings are tracked to closure by the Inventory Owner under AI Governance Lead oversight.

---

## Section 9 — Annual external attestation pack

Once per year (or on examiner request), the cycle and quarterly-audit evidence is assembled into an **Annual External Attestation Pack** suitable for delivery to FINRA, OCC, Federal Reserve, SEC, NYDFS, internal audit, or external auditors under the firm's evidence-disclosure policy.

### 10.1 Pack contents

| Section | Contents |
|---|---|
| **A. Cover and scope** | Pack identifier, scope statement, regulator audience, custodian chain, redaction policy, retention period |
| **B. Inventory governance policy** | Current signed Control 3.1 charter, metadata schema, role assignments |
| **C. Cycle history** | All cycle attestation files (`attestation.json`) for the trailing 12 months, with hash-chain verification report |
| **D. Quarterly audit reports** | Four quarterly audit packs (Q1..Q4) including narratives, findings, and remediation status |
| **E. Aggregate inventory snapshot** | Year-end snapshot of the system of record with schema, row counts by zone, DLP scope distribution, regulatory-scope distribution |
| **F. Reconciliation summary** | Trend of match rate, surface delta counts, owner-reassignment SLA, lifecycle-state mix across the trailing 12 months |
| **G. Exceptions and risk acceptances** | Active exceptions with owner, expiry, and risk-acceptance signatures |
| **H. Incident references** | Cross-references to AI Incident Response Playbook activations during the year that touched inventory integrity |
| **J. Index and manifest** | Evidence index, SHA-256 manifest, custodian chain, redaction policy |
| **K. Attestation chain** | Three-signature attestation chain with cycle-history hash chain validation |

### 10.2 Evidence indexing

The pack uses a stable index format:

```
ANNUAL-{YYYY}/
  COVER.md
  INDEX.md                    # human-readable table of contents
  manifest.sha256             # SHA-256 across every artifact in the pack
  chain-verify.json           # hash-chain verification across the cycle history
  A-cover/
  B-policy/
  C-cycles/{cycleId}/         # one folder per continuous cycle
  D-audits/{YYYY-Qn}/         # one folder per quarterly audit
  E-snapshot/
  F-reconciliation/
  G-exceptions/
  H-incidents/
  I-sov-controls/
  J-index/
  K-attestation/
```

`INDEX.md` includes one line per artifact mapping pack-relative path → originating cycle / audit ID → evidence purpose.

### 10.3 Redaction policy

The pack includes both a **full** internal-audit version (no redaction) and a **regulator-disclosure** version with the firm's standard redaction rules applied:

- Owner / Backup Owner UPNs redacted to role + initials unless the regulator's disclosure scope requires identity
- Free-text business-justification fields scanned for incidental NPI / MNPI references and redacted
- Connector configuration fields containing endpoint URLs may be redacted to domain-only depending on the regulator's request scope
- The redaction map (which fields were redacted, by what rule) is itself part of the pack

Redaction is performed by the Compliance Officer with sign-off from Legal. The redacted version carries its own SHA-256 manifest distinct from the full version.

### 10.4 Custodian chain

Each pack records:

- Originating Inventory Owner (the role responsible for cycle-level evidence)
- AI Governance Lead (the role responsible for cycle validation)
- Compliance Officer (the role responsible for examination-readiness)
- Pack assembler (the named individual who assembled the annual pack)
- Custodian (the named records-management role responsible for the immutable store)
- Disclosure custodian (the named individual who released the pack to the regulator, with date and channel)

Custodian transfers are logged in `J-index/custodian-chain.json`. Each transfer entry includes the recipient identity, the transfer reason, and a SHA-256 of the version transferred, so any post-transfer modification is detectable.

### 10.5 Examiner-readiness checklist

Before any release of the pack, the Compliance Officer confirms:

1. The hash chain across the trailing 12 months of cycles is unbroken.
2. Every Critical and High finding from the four quarterly audits has a documented closure or active remediation with owner and due date.
3. Every active exception has not expired.
4. The cycle-history attestation chain is complete (no missing cycles per the cadence matrix in Section 4).
5. The redaction map is complete and Legal-signed.
6. The custodian chain is complete and signed.
7. The pack passes a SHA-256 self-verification against `manifest.sha256`.

A failed checklist item halts the release pending remediation.

---

## Section 10 — Failure escalation matrix

| Failure type | Severity | Initial responder | Escalation within | Cross-link |
|---|---|---|---|---|
| Hash chain break (DRIFT-03) | Critical | Inventory Owner | Compliance Officer + Internal Audit, immediate | [AI Incident Response Playbook](../../incident-and-risk/ai-incident-response-playbook.md) |
| Active-but-platform-deleted (LIFE-03) | Critical | Inventory Owner | Compliance Officer, immediate | [AI Incident Response Playbook](../../incident-and-risk/ai-incident-response-playbook.md) |
| Decommissioned without retention pin (LIFE-02) | Critical | Compliance Officer | Records Management + Internal Audit, 24 hours | Control 1.7, Control 2.13 |
| FINRA / SOX in-scope agent untagged (REG-01, REG-02) | Critical | Compliance Officer | AI Governance Lead + supervisory program owner, 5 business days | Control 1.7 |
| Surface enumeration truncation at PPAC ceiling (COMP-04) | High | Power Platform Admin | Inventory Owner, 24 hours | Control 3.6 |
| Match rate below zone tolerance (COMP-02) | High | Inventory Owner | AI Governance Lead, 48 hours | Control 3.6 |
| Owner unresolvable + Backup unresolvable (OWN-02, OWN-03) | High | Inventory Owner | AI Governance Lead, 5 business days | Control 3.6 |
| DLP scope missing on Zone 3 agent (DLP-01) | High | Purview Compliance Admin | AI Governance Lead, 5 business days | Control 1.7 |
| New-agent detection out-of-SLA (DRIFT-01) | Medium | Inventory Owner | Power Platform Admin, 14 days | Control 1.2 |
| Modified-agent re-attestation out-of-SLA (DRIFT-02) | Medium | Inventory Owner | AI Governance Lead, 14 days | Control 2.13 |
| Stuck-Draft beyond threshold (LIFE-01) | Medium | Inventory Owner | Agent Owner outreach, 14 days | Control 3.6 |
| MIP label inventory under-statement (ACC-03) | Medium | Inventory Owner | Purview Compliance Admin, 14 days | — |
| Cosmetic metadata staleness without regulatory implication | Low | Inventory Owner | Bundled in next cycle | — |

Critical and High failures auto-create an AI Incident Response Playbook activation record with the cycle ID and the test ID. Medium failures are tracked in the cycle's `exceptions/` folder with a remediation owner and due date. Low failures are batched into the next cycle's narrative.

---

## Section 11 — Continuous improvement and lessons-learned loop

Inventory verification is not a static program. Each cycle and each quarterly audit feeds a continuous-improvement loop maintained by the AI Governance Lead.

### 12.1 Per-cycle learning

At cycle close, the Inventory Owner adds a `lessons-learned.md` to the evidence pack capturing:

- What changed in the discovery surface set (new Microsoft preview, deprecated surface, parity update)
- What changed in the tenant footprint (new Power Platform environments, M365 license changes)
- What test took longer than expected and why
- Which remediation tickets aged out and why
- Which exception expired and what action was taken
- Recommended changes to the cycle's calibrated thresholds in the next PRE-04 baseline

### 12.2 Per-quarter learning

After the quarterly examiner-style audit, Internal Audit publishes a `q-audit-{YYYY-Qn}-recommendations.md` capturing:

- Findings clustered by root cause (e.g., "12 of 18 High findings traced to a single registration-workflow gap in environment X")
- Recommended control changes (cadence increase, threshold tightening, automation candidate)
- Recommended training or governance-policy clarifications
- Cross-control implications (e.g., recommendations that affect Control 1.2, 2.1, 3.6, 3.8)

### 12.3 Per-year learning

At the annual external attestation cycle, the AI Governance Lead and Compliance Officer publish a `annual-{YYYY}-program-review.md` capturing:

- Trend analysis on match rate, owner-resolution rate, lifecycle coherence, DLP coverage across the year
- Cross-cycle hash-chain integrity statement
- Audit findings closed vs. outstanding
- Microsoft Learn changes that materially affected the discovery surface set
- Recommended changes to the Control 3.1 charter and metadata schema for the next program year
- Recommended changes to the cadence matrix in Section 4

### 12.4 Feedback into the framework

Material learnings that affect framework controls are routed back to:

- **Control 1.2 (Agent Registry)** — registration-workflow gaps
- **Control 2.1 (Managed Environments)** — environment-classification gaps
- **Control 2.13 (Documentation and Record Keeping)** — audit-trail gaps
- **Control 3.6 (Orphaned Agent Detection)** — orphan-classification rules
- **Control 3.8 (Copilot Hub Dashboard)** — dashboard inputs
- **Control 3.3 (Compliance and Regulatory Reporting)** — reporting-data lineage
- **AI Incident Response Playbook** — incident triggers and severity calibration

The continuous-improvement loop is itself reviewed annually for effectiveness, and the annual review is included in the External Attestation Pack (Section 10).

---

## Section 12 — References

### 13.1 Microsoft Learn (current May 2026)

- [Microsoft 365 admin center — Manage Copilot agents](https://learn.microsoft.com/en-us/microsoft-365-copilot/microsoft-365-copilot-page)
- [Power Platform admin — Copilot Hub](https://learn.microsoft.com/en-us/power-platform/admin/copilot/copilot-hub)
- [Power Platform Manage Copilot agents](https://learn.microsoft.com/en-us/power-platform/admin/copilot/copilot-hub)
- [Power Platform — Get-AdminPowerApp PowerShell](https://learn.microsoft.com/en-us/powershell/module/microsoft.powerapps.administration.powershell/)
- [Microsoft Entra Agent ID overview](https://learn.microsoft.com/en-us/entra/identity/) (verify current Agent ID page at cycle start)
- [Microsoft Agent 365 admin center overview](https://learn.microsoft.com/en-us/microsoft-agent-365/) (verify current page at cycle start; enablement requires at least one user with a qualifying Microsoft Agent 365 license or bundled entitlement)
- [Microsoft Purview Audit (UAL) search](https://learn.microsoft.com/en-us/purview/audit-search)
- [Microsoft Purview Data Loss Prevention policies](https://learn.microsoft.com/en-us/purview/dlp-learn-about-dlp)
- [Microsoft Information Protection sensitivity labels](https://learn.microsoft.com/en-us/purview/sensitivity-labels)
- [Microsoft Defender for Cloud Apps — App governance](https://learn.microsoft.com/en-us/defender-cloud-apps/app-governance-manage-app-governance)
- [Azure Resource Graph queries](https://learn.microsoft.com/en-us/azure/governance/resource-graph/)
- [Microsoft Graph users API — manager link](https://learn.microsoft.com/en-us/graph/api/user-list-manager)

### 13.2 Regulatory and standards references

- **NIST AI Risk Management Framework 1.0**, GOVERN 1.6 — Mechanisms are in place to inventory AI systems and are resourced according to organizational risk priorities. https://www.nist.gov/itl/ai-risk-management-framework
- **OCC Bulletin 2026-13 (formerly OCC Bulletin 2011-12) — Updated Interagency Guidance on Model Risk Management** — Higher-risk model inventory expectations. https://www.occ.gov/news-issuances/bulletins/2026/bulletin-2026-13.html
- **Federal Reserve SR 26-2 (formerly SR 11-7) — Guidance on Model Risk Management** — Companion guidance to OCC Bulletin 2026-13 (formerly OCC 2011-12). https://www.federalreserve.gov/supervisionreg/srletters/SR2602.htm
- **FINRA RN 24-09 / Rule 3110 (March 2025)** — Generative-AI tool supervision; firms should be able to enumerate, supervise, and explain generative-AI use. https://www.finra.org/rules-guidance/notices/24-09
- **FINRA Rule 4511** — Books and records general requirements.
- **FINRA Rule 2210** — Communications with the public.
- **FINRA Rule 3110** — Supervision.
- **SEC Rule 17a-4(b)(4)** — Records to be preserved by certain exchange members, brokers, and dealers.
- **SOX Sections 302 and 404** — Internal control over financial reporting.
- **GLBA 501(b) Safeguards Rule** — Customer information safeguards.
- **FTC Safeguards Rule 16 CFR §314** — Standards for safeguarding customer information.
- **NYDFS 23 NYCRR Part 500.16 / 500.17** — Incident response, business continuity, and asset inventory requirements for covered entities.
- **CFTC Regulation 1.31** — Recordkeeping requirements.
- **ISO/IEC 42001:2023** — AI management system requirements.

### 13.3 Companion controls and playbooks

- [Control 3.1 — Agent Inventory and Metadata Management (control specification)](../../../controls/pillar-3-reporting/3.1-agent-inventory-and-metadata-management.md)
- [Control 1.2 — Agent Registry and Integrated Apps Management](../../../controls/pillar-1-security/1.2-agent-registry-and-integrated-apps-management.md)
- [Control 1.7 — Comprehensive Audit Logging and Compliance](../../../controls/pillar-1-security/1.7-comprehensive-audit-logging-and-compliance.md)
- [Control 2.1 — Managed Environments](../../../controls/pillar-2-management/2.1-managed-environments.md)
- [Control 2.13 — Documentation and Record Keeping](../../../controls/pillar-2-management/2.13-documentation-and-record-keeping.md)
- [Control 3.6 — Orphaned Agent Detection and Remediation](../../../controls/pillar-3-reporting/3.6-orphaned-agent-detection-and-remediation.md)
- [Control 3.8 — Copilot Hub and Governance Dashboard](../../../controls/pillar-3-reporting/3.8-copilot-hub-and-governance-dashboard.md)
- [Control 3.11 — Quarterly Compliance Reporting](../../../controls/pillar-3-reporting/3.11-centralized-agent-inventory-enforcement.md)
- [AI Incident Response Playbook](../../incident-and-risk/ai-incident-response-playbook.md)
- [FSI-AgentGov-Solutions — Compliance Dashboard](https://github.com/judeper/FSI-AgentGov-Solutions/tree/main/compliance-dashboard)

---

*Updated: May 2026 | Version: v1.6.2 | UI Verification Status: Current*
