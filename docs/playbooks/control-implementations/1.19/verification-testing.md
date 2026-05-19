# Control 1.19 — eDiscovery for Agent Interactions: Verification & Testing Playbook

**Control:** 1.19 — eDiscovery for Agent Interactions
**Pillar:** 1 — Security
**Audience:** AI Governance Lead, Purview eDiscovery Manager, Legal/Compliance Officer (or General Counsel delegate), Purview Compliance Admin, Microsoft 365 Records Manager, FSI Internal Audit
**Sovereign clouds:** Commercial, GCC, GCC High, DoD (per-cloud feature parity tracked in §5; 21Vianet treated as out-of-scope — see PRE-06)
**Cross-links:** 1.5 (DLP & sensitivity labels), 1.6 (DSPM for AI), 1.7 (Audit logging), 1.9 (Retention & deletion), 1.10 (Communication Compliance), 1.13 (DCA AI monitoring), 1.14 (Data minimization), 1.21 (Adversarial input logging — preserves adversarial events under hold), 1.24 (Sentinel analytics), 2.13 (Documentation & record-keeping), 4.6 (Grounding scope governance), AI IR Playbook

> **Regulatory hedging notice.** This playbook describes verification procedures intended to **support compliance with** SEC Rule 17a-4 (including the October 2022 audit-trail-alternative amendment), SEC Rule 17a-3, FINRA Rule 4511, FINRA Rule 3110, FINRA RN 24-09 / Rule 3110 (AI supervision), FINRA Rule 8210 (information requests), SOX Section 802 (anti-spoliation) and SOX Section 404 (operating effectiveness), GLBA 501(b) Safeguards Rule, FRCP Rule 37(e) (preservation of ESI), OCC Bulletin 2026-13 (formerly OCC Bulletin 2011-12) / Federal Reserve SR 26-2 (formerly SR 11-7) (model risk management — applied to AI agent records), and CFTC Regulation 1.31 (recordkeeping). Implementation **does not guarantee** legal compliance. Organizations should verify applicability with qualified counsel and confirm tenant-specific behaviour against current Microsoft Learn documentation at the cycle's `lastVerifiedUtc` date.

---

## What this playbook catches

This playbook proves that an FSI tenant can **preserve, search, review, and produce** Microsoft 365 Copilot and Microsoft Copilot Studio agent interactions through the unified Microsoft Purview eDiscovery experience in a manner that is defensible under FINRA / SEC / FRCP scrutiny. Specifically, it verifies:

1. **License & role posture** — unified eDiscovery (Premium) features, Purview Audit (Premium) retention horizon, Microsoft 365 Copilot custodian licensing, and PIM-gated `eDiscovery Administrator` role separation are in place at cycle start.
2. **Case lifecycle** — a unified eDiscovery case can be created, named per the FSI matter standard, scoped, locked, closed, and reopened, with attributable history end-to-end.
3. **Custodian & source mapping** — synthetic custodians (and their Exchange / OneDrive / SharePoint / Teams / Copilot-interactions sources) are addable, removable, and survivable across role changes — with **no real PII in test fixtures**.
4. **KeyQL search execution** — version-pinned KeyQL templates produce stable, repeatable result counts within the tenant index-lag baseline established in PRE-04.
5. **Copilot interactions location & Copilot activity condition** — both the **Copilot interactions** location (mailbox-side hidden Copilot store) and the **Copilot activity** condition card return prompt-and-response evidence where Copilot use exists; the Copilot Studio Dataverse-only transcript gap is detected and documented rather than silently ignored.
6. **Legal hold preservation including SubstrateHolds** — a hold marked active **actually** preserves the substrate-stored Copilot transcript (the most common silent-failure mode); the held content survives end-user deletion of the chat thread and is retrievable from the **SubstrateHolds** mailbox container.
7. **Review-set integrity** — review-set load reports show no item drops without justification; reviewers can tag and code but **cannot export** (separation of duties).
8. **Defensible export** — the export package contains native content + load file + metadata + chain-of-custody log; every artifact in the package carries a SHA-256 hash recorded in a manifest; the manifest is committed to immutable storage external to the live tenant before the SEC 17a-4(f) audit-trail-alternative claim is made.
9. **Audit reconciliation** — UAL events under the `Discovery` / `eDiscovery` RecordTypes (case create, hold create, search create, search export, role assignment) appear within the tenant ingestion baseline and are retained for the 6+ year FSI horizon.
10. **Negative controls** — retired classic eDiscovery cmdlets (`New-ComplianceCase`, `New-CaseHoldPolicy`, `Search-Mailbox` in eDiscovery contexts) **fail safely** post-August 2025 retirement; the `from:Copilot` keyword anti-pattern returns zero / wrong results; bulk `eDiscovery Administrator` assignment without PIM is detected.
11. **Sovereign-cloud parity & incident readiness** — Commercial / GCC / GCC High / DoD parity for the **Copilot interactions** location, conversation reconstruction, and Copilot custodian licensing is re-verified each cycle; an annual FRCP 37(e) preservation tabletop and a FINRA 8210 production drill (against the typical ~30-day examiner SLA) are signed and retained.

> **What this playbook does NOT claim.** It does **not** assert any single numeric Microsoft SLA for case provisioning, hold propagation, or KeyQL index lag — Microsoft Learn explicitly states these are eventually-consistent and can take hours; the operative threshold for any cycle is the tenant baseline measured in PRE-04 and re-asserted in AUDIT-01. It does **not** treat the `CopilotInteraction` UAL `AuditData` body as authoritative for full prompt-and-response content for legal production — UAL is the **occurrence** signal; the substrate item placed under hold is the **content** evidence, and the two streams must be reconciled by ConversationId / time-window correlation. It does **not** treat the **Copilot activity** condition card as an exhaustive AI inventory — it is an additive scope filter on a search whose primary scope is the location set. It does **not** assert that placing a hold retroactively preserves content created before the hold's effective time; a hold preserves from the moment the hold takes effect, not before. It does **not** apply to organizations on Microsoft 365 operated by 21Vianet (China), which continues to use the classic eDiscovery experience and requires a separate validator (out of scope here).

---
## 1. Cadence Matrix

Each verification family has a defined cadence per zone. **Grace windows:** monthly = 35 days, quarterly = 100 days, annual = 400 days from the previous successful cycle's `cycleCompletedUtc`. A cycle that exceeds its grace window without an `acceptedRiskUntilUtc` exception (signed by AI Governance Lead AND Legal Officer) is reported as a finding to FSI Internal Audit.

| Family | Zone 1 (Personal) | Zone 2 (Team) | Zone 3 (Enterprise / Regulated) | Owner | Reviewer |
|---|---|---|---|---|---|
| LIC — License & role posture | Quarterly | Monthly | Monthly | Purview Compliance Admin | AI Governance Lead |
| CASE — Case lifecycle | Quarterly | Quarterly | Monthly | Purview eDiscovery Manager | Legal Officer |
| CUSTODIAN — Custodian & source assignment | Quarterly | Quarterly | Monthly | Purview eDiscovery Manager | Legal Officer |
| SEARCH — KeyQL execution & determinism | Quarterly | Monthly | Monthly | Purview eDiscovery Manager | AI Governance Lead |
| COPILOT — Copilot interactions location & activity condition | Quarterly | Monthly | Monthly | Purview eDiscovery Manager | AI Governance Lead |
| HOLD — Legal hold incl. SubstrateHolds survivability | Quarterly | Monthly | Monthly | Purview eDiscovery Manager | Legal Officer |
| REVIEW — Review-set integrity & SoD | Annual | Quarterly | Quarterly | Purview eDiscovery Manager | FSI Internal Audit |
| EXPORT — Hash-chain export & immutable handoff | Annual | Quarterly | Quarterly | Purview eDiscovery Manager | Records Manager |
| AUDIT — UAL eDiscovery RecordType reconciliation | Quarterly | Monthly | Monthly | Purview Compliance Admin | FSI Internal Audit |
| NEG — Negative / anti-pattern controls | Quarterly | Quarterly | Monthly | AI Governance Lead | FSI Internal Audit |
| SOV — Sovereign-cloud parity re-check | Annual | Annual | Quarterly | AI Governance Lead | Legal Officer |
| IR — FRCP 37(e) tabletop & FINRA 8210 production drill | Annual | Annual | Annual | Legal Officer | AI Governance Lead + FSI Internal Audit |

> **Drift rule.** If any test in the COPILOT, HOLD, EXPORT, AUDIT, or NEG family fails twice in two consecutive cycles, the next cycle's cadence for that family **escalates one tier** (annual → quarterly → monthly) and remains escalated until two consecutive clean cycles, after which it returns to the matrix default.

---

## 2. Pre-flight Gates (Fail-Closed)

PRE gates run **before** any test in §4. If any PRE gate returns FAIL, the validator exits with code **2** and no §4 test results are written to the evidence pack — the cycle is halted and surfaced to the AI Governance Lead.

### PRE-01 — Required PowerShell module versions present

- **Objective.** Confirm the operator workstation has version-pinned modules so that cmdlet behaviour matches the playbook's documented expectations.
- **How to verify.** Run `Get-Module -ListAvailable` for each of: `ExchangeOnlineManagement` ≥ 3.4.0, `Microsoft.Graph.Security` ≥ 2.20.0, `PnP.PowerShell` ≥ 2.4.0, `Microsoft.Graph.Compliance` ≥ 2.20.0 (where available in target cloud). Capture `Name`, `Version`, `Path`, `RepositorySourceLocation`.
- **Evidence.** `pre-01-modules.json` listing each module with version and SHA-256 of the resolved `.psd1`.
- **Pass.** All required modules ≥ pinned minimum AND signature trusted (`Get-AuthenticodeSignature` Status = Valid for at least the primary `.psm1`).
- **Audit assertion.** "Operator environment matches the version pin published in this playbook's revision N at `lastVerifiedUtc`."

### PRE-02 — Privileged role activation via PIM

- **Objective.** Confirm the operator did not hold `eDiscovery Administrator`, `eDiscovery Manager`, `Compliance Administrator`, or `Compliance Data Administrator` as a permanent assignment for the cycle.
- **How to verify.** Query Microsoft Graph `roleManagement/directory/roleAssignmentScheduleInstances` filtered by `principalId` of the operator AND role definitions matching the four privileged roles; assert `assignmentType eq 'Activated'` AND `endDateTime` ≤ 8 hours from `startDateTime`.
- **Evidence.** `pre-02-pim.json` containing the activation record IDs, role definition IDs, justification text, and ticket reference.
- **Pass.** Every privileged role exercised in this cycle is backed by a time-bound PIM activation with a ticket reference; no permanent assignment present.
- **Audit assertion.** "No standing privileged eDiscovery access; all elevation is just-in-time and ticketed (supports SOX 404 SoD and FFIEC ITRMP §III.A.4)."

### PRE-03 — License & SKU floor

- **Objective.** Confirm the tenant carries the SKUs required for unified Premium eDiscovery features used by this cycle.
- **How to verify.** Use Graph `subscribedSkus` and `assignedPlans`. Required: a SKU containing `M365_E5_COMPLIANCE` OR `EQUIVIO_ANALYTICS_FOR_OFFICE365` OR `LOCKBOX_ENTERPRISE` per Microsoft's current licensing matrix for unified eDiscovery (verify against Microsoft Learn at `lastVerifiedUtc`); Microsoft 365 Copilot license assignments for at least one custodian; Purview Audit (Premium) entitlement (`M365_AUDIT_PREMIUM` or equivalent).
- **Evidence.** `pre-03-licensing.json` with SKU IDs, service plan IDs, and per-custodian assignment counts.
- **Pass.** All three license families present AND custodians selected for the cycle have Copilot license attached.
- **Audit assertion.** "Tenant carries the entitlements that Microsoft documents as required for the unified eDiscovery features exercised in §4 of this cycle."

### PRE-04 — Tenant baseline for index lag and UAL ingestion

- **Objective.** Establish a per-tenant, per-cycle baseline for KeyQL index lag and UAL ingestion latency rather than asserting a Microsoft SLA.
- **How to verify.** Generate three synthetic Copilot interactions with a unique cycle marker (`fsi-cycle-{cycleId}`) at T0, T0+5min, T0+10min. Poll the **Copilot interactions** location search and the UAL `CopilotInteraction` event every 5 minutes for up to 4 hours. Record P50 / P95 minutes-to-discoverability for both streams.
- **Evidence.** `pre-04-baseline.json` with the three marker IDs, T0..T_found timestamps, and computed P50/P95.
- **Pass.** P95 ≤ tenant's prior 4-cycle rolling P95 + 50% drift allowance OR ≤ 240 minutes absolute, whichever is greater. (No claim is made that 240 minutes is a Microsoft SLA — it is a fail-closed ceiling.)
- **Audit assertion.** "Tenant index lag and UAL ingestion are within rolling baseline; cycle's freshness threshold for SEARCH/AUDIT tests is the measured P95."

### PRE-05 — Audit retention horizon ≥ 6 years for `Discovery` RecordType

- **Objective.** Confirm UAL retention for eDiscovery-relevant RecordTypes meets the FSI 6-year horizon (FINRA 4511 / SEC 17a-4).
- **How to verify.** Inspect the audit retention policy (Purview portal → Audit → Audit retention policies) for a policy scoped to `RecordType` ∈ {`Discovery`, `eDiscovery`, `ComplianceDLPExchange`, `CopilotInteraction`} with `retentionDuration` ≥ `Years6` (or `TenYears` where the firm's matter book has a longer horizon).
- **Evidence.** `pre-05-audit-retention.json` exported from `Get-AuditRetentionPolicy`.
- **Pass.** A non-default retention policy exists, is enabled, and covers all four RecordTypes for at least 6 years.
- **Audit assertion.** "UAL coverage for eDiscovery operations and Copilot interactions exceeds the FINRA/SEC 6-year recordkeeping horizon."

### PRE-06 — Cloud-environment guard

- **Objective.** Refuse to run if the operator targets an unsupported cloud (21Vianet) or if the cloud cannot be unambiguously identified.
- **How to verify.** Query `Get-OrganizationConfig` for `IsTenantInGracePeriod` and the connection's `AzureADAuthorizationEndpointUri`; classify as Commercial / GCC / GCC High / DoD; HALT if endpoint resolves to `partner.microsoftonline.cn` (21Vianet) or if classification is ambiguous.
- **Evidence.** `pre-06-cloud.json` with classified cloud, endpoint URI, and tenant region.
- **Pass.** Cloud is one of {Commercial, GCC, GCC High, DoD} AND matches the cloud declared in the cycle's `manifest.tenant.cloud`.
- **Audit assertion.** "Cycle executed against the declared sovereign cloud; no cross-cloud contamination."

### PRE-07 — Synthetic-only fixture invariant

- **Objective.** Prevent leakage of real custodian PII into test fixtures.
- **How to verify.** All custodian UPNs used in §4 must match the regex `^fsi-test-[a-z0-9]{6,}@…$` AND must NOT appear in HR's authoritative employee directory; all KeyQL templates used in tests must reference only the cycle's marker tokens (`fsi-cycle-{cycleId}-*`).
- **Evidence.** `pre-07-fixtures.json` listing every custodian UPN and KeyQL template token used in the cycle, with the HR-directory cross-check result.
- **Pass.** Zero real UPNs detected; zero KeyQL templates reference real matter names or real client identifiers.
- **Audit assertion.** "Test fixtures are synthetic; no real custodian PII or live matter content was exercised in this cycle (supports GLBA 501(b) and SOX 802 anti-spoliation)."

---
## 3. Documented Processing Windows (Microsoft Learn–cited only)

The table below captures **only** Microsoft-documented behaviours. Where Microsoft Learn does not publish a numeric SLA, the column reads "no documented numeric SLA — use tenant baseline from PRE-04". **Do not invent SLAs.**

| Operation | Documented behaviour (Microsoft Learn) | Operative threshold for this cycle |
|---|---|---|
| Hold propagation to all in-scope locations | "May take up to 24 hours" — eDiscovery hold guidance | 24h ceiling; pass condition is hold confirmation observable in case detail before retry budget exhausted |
| Query-based hold cleanup of items no longer matching | Reconciled every 7–14 days | Cycle does not test removal latency directly; HOLD-04 documents acceptance |
| UAL ingestion for core services | "Within 60–90 minutes for most services" — service-class statement, NOT an SLA | Use PRE-04 measured P95 as fail-closed ceiling |
| Completed audit-search retention | Audit search results retained 30 days from completion | Evidence pack must be exported within 30 days of search completion (see EXPORT-01) |
| Classic eDiscovery (Standard / Premium) availability | Retired August 31, 2025 in Commercial / GCC / GCC High / DoD; remains for Microsoft 365 operated by 21Vianet | NEG-01 asserts the retired cmdlets fail safely |
| Copilot interactions location surface | Documented as a selectable location in unified eDiscovery search and as the **Copilot activity** condition card | COPILOT-01 / COPILOT-02 verify both surfaces |
| SubstrateHolds container | Documented as the system mailbox container that preserves Copilot prompts and responses under hold | HOLD-03 verifies survivability of held content after end-user delete |
| Copilot Studio agent transcripts persisted to Dataverse | Not natively in M365 substrate; covered by Dataverse retention, not by M365 Copilot interactions location | COPILOT-04 detects and documents the gap (cross-link 1.9) |
| eDiscovery export package contents | Native files + load file + metadata fields + chain-of-custody log per Microsoft documentation | EXPORT-02 verifies completeness; EXPORT-01 verifies hash chain |
| Audit-trail-alternative (SEC 17a-4(f) Oct-2022) | Requires WORM-like preservation with verifiable audit trail; M365 alone is not the WORM target | EXPORT-03 verifies handoff to immutable storage outside the live tenant |

> **Citation discipline.** Every row above is testable against a Microsoft Learn page reachable at the cycle's `lastVerifiedUtc`. Any behaviour not on this table that affects cycle outcome must be added in the cycle's `manifest.deviations[]` with a Learn URL and a verification timestamp; an undocumented behaviour without a deviation entry is a finding.

---

## 4. Test Catalog

35 tests across 12 namespaces. Each test uses the standard 7-field structure: **Objective**, **Preconditions**, **Steps**, **Expected**, **Pass criteria**, **Audit assertion**, **Evidence**.

### 4.1 LIC — License & Role Posture (3 tests)

#### LIC-01 — Unified eDiscovery (Premium) license attached to operating tenant

- **Objective.** Confirm the SKU floor for unified Premium eDiscovery features used downstream (review sets, predictive coding, hold notifications).
- **Preconditions.** PRE-03 PASS.
- **Steps.** (1) `Connect-MgGraph -Scopes 'Organization.Read.All','Directory.Read.All'`. (2) `Get-MgSubscribedSku | Select SkuPartNumber, ConsumedUnits, PrepaidUnits`. (3) Resolve service-plan inclusion of `LOCKBOX_ENTERPRISE` and `EQUIVIO_ANALYTICS_FOR_OFFICE365` (or successor plans per Learn at `lastVerifiedUtc`). (4) Persist result.
- **Expected.** At least one SKU containing the unified eDiscovery service plan is provisioned and `ConsumedUnits` ≥ 1.
- **Pass criteria.** SKU present AND consumed AND tenant-region matches PRE-06 cloud classification.
- **Audit assertion.** "Tenant carries the SKU Microsoft documents as required for the unified eDiscovery features exercised in this cycle."
- **Evidence.** `lic-01-skus.json`.

#### LIC-02 — Copilot license assigned to ≥1 cycle custodian

- **Objective.** Confirm the cycle's synthetic custodians actually have Copilot — without it the **Copilot interactions** location is empty by design and COPILOT tests cannot pass for that custodian.
- **Preconditions.** PRE-03 PASS, PRE-07 PASS.
- **Steps.** For each `fsi-test-*` custodian declared in the cycle manifest: `Get-MgUserLicenseDetail -UserId $upn` and assert presence of the Copilot service plan.
- **Expected.** Every cycle custodian carries Copilot.
- **Pass criteria.** 100% custodian Copilot coverage AND license activation date ≥ 24h before T0 of PRE-04 baseline.
- **Audit assertion.** "Custodians used in COPILOT-* tests had Copilot active long enough for substrate items to exist."
- **Evidence.** `lic-02-copilot-licenses.json`.

#### LIC-03 — `eDiscovery Manager` and `eDiscovery Administrator` separation

- **Objective.** Confirm SoD: no individual holds both `eDiscovery Manager` (case scope) AND `eDiscovery Administrator` (tenant-wide) by permanent assignment.
- **Preconditions.** PRE-02 PASS.
- **Steps.** Pull role membership from Purview eDiscovery permissions blade and from Graph `roleManagement/directory/roleAssignments`. Compute the intersection.
- **Expected.** Empty intersection for permanent assignments; if PIM-eligible, both roles must require independent approvals.
- **Pass criteria.** Zero permanent dual-assignees AND PIM eligibility records carry distinct approver groups.
- **Audit assertion.** "eDiscovery role separation enforced (supports SOX 404 and FINRA 3110 supervisory structure)."
- **Evidence.** `lic-03-role-separation.json`.

### 4.2 CASE — Case Lifecycle (3 tests)

#### CASE-01 — Create, name, and scope a unified eDiscovery case

- **Objective.** Confirm a case can be created via portal AND via Graph and that naming follows the FSI matter standard `FSI-{YYYY}-{MATTER-ID}-{SHORTNAME}`.
- **Preconditions.** PRE-01..03 PASS.
- **Steps.** (1) Portal: Purview → eDiscovery → New case → name `FSI-2026-CYCLE-{cycleId}-VERIFY` → set description to cycle marker → Save. (2) Graph: `New-MgSecurityCaseEdiscoveryCase -DisplayName ...`. (3) Pull case object via Graph and capture `id`, `createdDateTime`, `createdBy.user.id`.
- **Expected.** Both creation paths succeed and produce identical case attributes (modulo `id`).
- **Pass criteria.** Naming regex match AND `createdBy` resolves to the PIM-activated identity from PRE-02 AND case visible in portal blade ≤ 5 minutes.
- **Audit assertion.** "Case creation is attributable to a time-bound PIM activation and follows matter naming policy."
- **Evidence.** `case-01-create.json` (both creation paths), portal screenshot under `case-01-portal.png`.

#### CASE-02 — Lock, close, and reopen lifecycle

- **Objective.** Confirm full lifecycle transitions and that closing does not silently delete holds or review sets.
- **Preconditions.** CASE-01 PASS.
- **Steps.** Add a placeholder hold (HOLD-01 fixture) → close case via Graph → assert state `Closed` → reopen → assert state `Active` → confirm hold still present.
- **Expected.** Transitions succeed; hold survives close/reopen.
- **Pass criteria.** State transitions observed AND hold object identity preserved (same `id`, `createdDateTime`).
- **Audit assertion.** "Case closure is reversible without loss of preservation state — supports FRCP 37(e) reasonable-steps standard."
- **Evidence.** `case-02-lifecycle.json` with state-transition timestamps.

#### CASE-03 — Case history attribution

- **Objective.** Confirm every meaningful action on the case (create, hold add, search create, export) is recorded in case history with actor, timestamp, and action type.
- **Preconditions.** CASE-01..02 PASS.
- **Steps.** Pull case operations via Graph `caseOperations` collection; cross-reference with UAL `Discovery` RecordType events for the cycle window.
- **Expected.** Every Graph-side case operation has a UAL counterpart within PRE-04 P95 ingestion lag.
- **Pass criteria.** 100% reconciliation; missing events trigger fail.
- **Audit assertion.** "Case history is dual-sourced (Graph operations + UAL) — defensible under FINRA 8210 information requests."
- **Evidence.** `case-03-history.json` and `case-03-reconciliation.csv`.

### 4.3 CUSTODIAN — Custodian & Source Assignment (3 tests)

#### CUSTODIAN-01 — Add custodian + auto-discover sources

- **Objective.** Confirm a custodian can be added and Microsoft auto-discovers their Exchange mailbox, OneDrive, and Teams sources.
- **Preconditions.** CASE-01 PASS, LIC-02 PASS.
- **Steps.** Add `fsi-test-*` custodian to case via Graph; wait up to PRE-04 P95 + 30min; pull `custodian/userSources`, `custodian/siteSources`.
- **Expected.** Mailbox and OneDrive sources auto-attached; Teams sources resolvable via group membership.
- **Pass criteria.** ≥ 2 source types attached automatically AND custodian Copilot interactions location addable.
- **Audit assertion.** "Custodian-source mapping operates as documented for the cycle's cloud and license posture."
- **Evidence.** `custodian-01-sources.json`.

#### CUSTODIAN-02 — Add Copilot interactions as a custodial source

- **Objective.** Confirm the **Copilot interactions** location can be attached to a custodian and is queryable.
- **Preconditions.** CUSTODIAN-01 PASS.
- **Steps.** Via portal: custodian → Locations → check "Copilot interactions"; via Graph: confirm the source appears with `dataSourceContainerType` matching Microsoft's documented identifier at `lastVerifiedUtc`.
- **Expected.** Copilot interactions location appears alongside Exchange/OneDrive/SharePoint.
- **Pass criteria.** Source addable AND searchable in SEARCH-02.
- **Audit assertion.** "Copilot prompt/response substrate is treated as a first-class custodial source."
- **Evidence.** `custodian-02-copilot-source.json`.

#### CUSTODIAN-03 — Remove custodian without orphaning held content

- **Objective.** Confirm removing a custodian from the case does NOT release content already on hold (FRCP 37(e) sleeper risk).
- **Preconditions.** CUSTODIAN-01 PASS, HOLD-01 PASS.
- **Steps.** Add custodian to active hold → remove custodian from case → re-query hold detail → confirm previously held items remain in `SubstrateHolds` for the held-mailbox custodian.
- **Expected.** Hold survives custodian removal; only future content for the removed custodian falls out of preservation.
- **Pass criteria.** Pre-removal items remain queryable via review set after custodian removal.
- **Audit assertion.** "Custodian removal does not silently spoliate preserved content."
- **Evidence.** `custodian-03-removal.json` with pre/post item counts.

### 4.4 SEARCH — KeyQL Execution & Determinism (3 tests)

#### SEARCH-01 — Versioned KeyQL template determinism

- **Objective.** Confirm a pinned KeyQL template returns stable counts across two consecutive runs ≥ 30 minutes apart, controlling for new ingestion.
- **Preconditions.** PRE-04 baseline established.
- **Steps.** Define `keyql-templates/v1.4-cycle-marker.kql` containing `fsi-cycle-{cycleId}` only. Run search twice with ≥ 30min gap. Compute count delta.
- **Expected.** Delta ≤ items demonstrably ingested in the gap (proven by UAL `CopilotInteraction` events with cycle marker in window).
- **Pass criteria.** No unexplained drift > 0.
- **Audit assertion.** "KeyQL execution is deterministic for a frozen corpus (FINRA 4511 reproducibility)."
- **Evidence.** `search-01-determinism.json` with both runs and reconciliation.

#### SEARCH-02 — Copilot interactions location returns marker prompts

- **Objective.** Confirm the **Copilot interactions** location surfaces the synthetic prompts created in PRE-04.
- **Preconditions.** PRE-04 PASS, CUSTODIAN-02 PASS.
- **Steps.** New search → location set = `Copilot interactions` only → KeyQL `fsi-cycle-{cycleId}` → run → preview top 10 hits.
- **Expected.** All three PRE-04 marker interactions surfaced for the in-scope custodian.
- **Pass criteria.** Hit count ≥ 3 AND each hit shows prompt + response payload (not just metadata).
- **Audit assertion.** "Copilot interactions location returns content payloads, not just occurrence metadata."
- **Evidence.** `search-02-copilot-hits.json` with hit IDs and (redacted) preview hashes.

#### SEARCH-03 — KeyQL property-restriction parity

- **Objective.** Confirm `participants:`, `subject:`, `kind:` restrictions behave per Microsoft's documented KeyQL grammar at `lastVerifiedUtc`.
- **Preconditions.** SEARCH-01 PASS.
- **Steps.** Run three searches each restricting on one supported property; assert non-zero results where expected; assert zero results for negative-control restriction.
- **Expected.** Documented operators function; undocumented operators (e.g., `from:Copilot`) return nothing or error — see NEG-02.
- **Pass criteria.** All documented operators behave as documented; negative cases match NEG-02.
- **Audit assertion.** "KeyQL grammar at `lastVerifiedUtc` is operative in this tenant."
- **Evidence.** `search-03-keyql-grammar.json`.

### 4.5 COPILOT — Copilot Interactions Location & Activity Condition (4 tests)

#### COPILOT-01 — Copilot interactions location selectable in unified eDiscovery

- **Objective.** Confirm the location appears as a selectable scope in the unified eDiscovery new-search wizard.
- **Preconditions.** LIC-01 PASS, PRE-06 PASS.
- **Steps.** Portal: New search → Locations → confirm "Copilot interactions" tile present; capture screenshot with cycle marker overlay.
- **Expected.** Location selectable in current cloud per §5 sovereign matrix.
- **Pass criteria.** Tile present AND selectable AND not greyed out.
- **Audit assertion.** "UI parity for Copilot interactions location confirmed at cycle time."
- **Evidence.** `copilot-01-location.png`, `copilot-01-confirmation.json`.

#### COPILOT-02 — Copilot activity condition card returns prompt+response

- **Objective.** Confirm the **Copilot activity** condition card on a search returns prompts and responses, not just occurrence rows.
- **Preconditions.** SEARCH-02 PASS.
- **Steps.** Add condition: `Copilot activity` → constrain to cycle marker time window → run → inspect first 5 hits in preview.
- **Expected.** Each hit shows the user's prompt text AND the assistant's response text in the preview pane (subject to current Microsoft preview-rendering behaviour).
- **Pass criteria.** Prompt and response visible in ≥ 4 of 5 previews; remaining 1 explainable by truncation policy.
- **Audit assertion.** "Copilot activity condition surfaces content (prompt + response), not just signal."
- **Evidence.** `copilot-02-activity.json` with hit IDs and preview render confirmations.

#### COPILOT-03 — Prompt + response retrieval through full case → review-set lifecycle

- **Objective.** Confirm an end-to-end pipeline (custodian → location → KeyQL → review set → tagging) preserves prompt-and-response fidelity.
- **Preconditions.** COPILOT-01..02 PASS, REVIEW-01 PASS.
- **Steps.** Create review set → add SEARCH-02 results → open one item → confirm `Body` field contains both prompt and response with attribution timestamps and ConversationId.
- **Expected.** Full content retrievable; ConversationId stable across substrate item and matching UAL `CopilotInteraction` event.
- **Pass criteria.** Body completeness ≥ 99% (allowing for documented truncation of attachments) AND ConversationId reconciles to UAL.
- **Audit assertion.** "Substrate evidence (content) and UAL evidence (occurrence) reconcile by ConversationId."
- **Evidence.** `copilot-03-roundtrip.json` with ConversationId reconciliation table.

#### COPILOT-04 — Copilot Studio Dataverse-only transcript gap detection

- **Objective.** Detect and document the known gap: Copilot Studio agents that persist transcripts only to Dataverse are NOT visible via the M365 Copilot interactions location.
- **Preconditions.** Copilot Studio agent registered in the cycle inventory (cross-link 4.6).
- **Steps.** Identify any Copilot Studio agent whose transcripts persist to Dataverse only. Attempt to discover its transcripts via the Copilot interactions location and via KeyQL — both will return zero. Then verify the agent's Dataverse retention story (cross-link 1.9 retention playbook).
- **Expected.** M365 substrate yields zero hits (expected); Dataverse-side preservation is independently verified via 1.9 evidence.
- **Pass criteria.** Gap is **declared** in the cycle's `manifest.copilotStudioGapInventory[]` AND each gap has a corresponding 1.9 retention evidence reference. A silent gap (declared nowhere) is a fail.
- **Audit assertion.** "Copilot Studio Dataverse-only transcripts are scoped under Dataverse retention (1.9), not under M365 eDiscovery, and the gap is documented per cycle."
- **Evidence.** `copilot-04-studio-gap.json`.
### 4.6 HOLD — Legal Hold Including SubstrateHolds Survivability (4 tests)

#### HOLD-01 — Create case-level legal hold scoped to Copilot interactions

- **Objective.** Confirm a hold can be created with the Copilot interactions location explicitly in scope.
- **Preconditions.** CASE-01 PASS, CUSTODIAN-02 PASS.
- **Steps.** Portal: case → Holds → New hold → name `cycle-{cycleId}-hold-01` → custodians = cycle custodians → locations include Copilot interactions → save. Confirm via Graph `caseHoldPolicies`.
- **Expected.** Hold created in `On` state; `policyContent` references Copilot interactions location.
- **Pass criteria.** Hold visible in Graph AND portal AND `Status` ∈ `On`/`Pending` (Pending acceptable up to 24h per §3 ceiling).
- **Audit assertion.** "Legal hold created with explicit Copilot interactions scope."
- **Evidence.** `hold-01-create.json`, `hold-01-portal.png`.

#### HOLD-02 — Hold confirmation observable before any deletion attempt

- **Objective.** Confirm the operator can prove hold is active **before** any test that simulates user deletion (HOLD-03).
- **Preconditions.** HOLD-01 PASS.
- **Steps.** Poll hold status every 10 minutes for up to 24h (§3 ceiling); record first observation of `Status = On` AND a non-empty `affectedLocationCount`.
- **Expected.** Confirmation reached well within 24h ceiling; if not, FAIL and do not proceed to HOLD-03.
- **Pass criteria.** Confirmation observed; observation timestamp persisted as `holdConfirmedUtc`.
- **Audit assertion.** "No deletion test executed without prior hold confirmation — supports FRCP 37(e) reasonable-steps standard."
- **Evidence.** `hold-02-confirmation.json` with poll log.

#### HOLD-03 — SubstrateHolds preserves Copilot transcript across end-user deletion

- **Objective.** Prove the highest-risk silent-failure mode is closed: that a held Copilot interaction survives end-user deletion of the chat thread and is retrievable from `SubstrateHolds`.
- **Preconditions.** HOLD-02 PASS.
- **Steps.** (1) As the synthetic custodian, create a Copilot interaction with marker `fsi-cycle-{cycleId}-hold-03`. (2) Wait for ingestion within PRE-04 P95. (3) Confirm the item appears in COPILOT-02 search. (4) As the custodian, delete the chat thread from Copilot/Teams UI. (5) Wait 60 minutes. (6) Re-run COPILOT-02 search; confirm hit count unchanged. (7) Inspect `SubstrateHolds` system folder of the custodian via `Search-Mailbox`-equivalent unified eDiscovery review-set add to confirm the item physically resides in the held container.
- **Expected.** Hit count and review-set add succeed identically before and after end-user deletion.
- **Pass criteria.** Item present in `SubstrateHolds`-backed review set after deletion; hash of preserved item identical pre/post deletion.
- **Audit assertion.** "Copilot prompt/response substrate is **physically preserved** under hold and survives end-user deletion (the operative FRCP 37(e) requirement)."
- **Evidence.** `hold-03-substrate-survival.json` with pre/post hashes and review-set add transcripts.

#### HOLD-04 — Removing a hold does not retroactively spoliate

- **Objective.** Confirm that releasing a hold does not delete content; it only stops future preservation.
- **Preconditions.** HOLD-03 PASS.
- **Steps.** Release HOLD-01 → wait 60 minutes → re-run COPILOT-02 search; for items previously held that have not been actively deleted, confirm continued discoverability.
- **Expected.** Items still discoverable until any retention policy or user deletion takes effect.
- **Pass criteria.** Hold release does not cause immediate disappearance of preserved items.
- **Audit assertion.** "Hold release behaves per Microsoft's documented model — no silent retroactive purge."
- **Evidence.** `hold-04-release.json`.

### 4.7 REVIEW — Review-Set Integrity & SoD (2 tests)

#### REVIEW-01 — Review-set load report shows zero unjustified drops

- **Objective.** Confirm review-set ingestion completeness.
- **Preconditions.** SEARCH-02 PASS.
- **Steps.** Add SEARCH-02 results to review set → wait for load completion → pull load report (`reviewSet/operations`) → assert `itemsAdded` matches `itemsFromSearch` minus `itemsExcluded` and that every excluded item carries a documented exclusion reason (e.g., unsupported file type per Microsoft documentation).
- **Expected.** Conservation of items: search hits = added + excluded; no silent drops.
- **Pass criteria.** Reconciliation balanced AND any exclusion class appears in the cycle manifest's `expectedExclusions[]`.
- **Audit assertion.** "Review-set ingestion is conservation-of-items balanced."
- **Evidence.** `review-01-load-report.json`.

#### REVIEW-02 — Reviewer role cannot export

- **Objective.** Confirm SoD: a user in `Reviewer` role can tag and code but cannot trigger export.
- **Preconditions.** LIC-03 PASS.
- **Steps.** PIM-activate a synthetic test reviewer into `Reviewer` only → attempt to start an export from a review set via Graph; expect 403/AccessDenied.
- **Expected.** Export attempt rejected.
- **Pass criteria.** 403 returned AND UAL `Discovery` event records the denied attempt.
- **Audit assertion.** "Reviewer role cannot self-export — supports SOX 404 and FINRA 3110."
- **Evidence.** `review-02-sod.json`.

### 4.8 EXPORT — Hash-Chain Export & Immutable Handoff (3 tests)

#### EXPORT-01 — SHA-256 manifest covers every artifact in the export package

- **Objective.** Confirm every file in the exported package has a SHA-256 entry in a manifest, and the manifest itself is signed.
- **Preconditions.** REVIEW-01 PASS.
- **Steps.** Trigger export from review set → download package → enumerate files → recompute SHA-256 for each → compare to manifest → verify manifest signature.
- **Expected.** 100% file-to-manifest coverage; signature valid.
- **Pass criteria.** All hashes match AND manifest signature chains to a trusted enterprise signing identity (HSM-backed where available).
- **Audit assertion.** "Export package is hash-pinned and signed — supports SEC 17a-4(f) audit-trail-alternative integrity claim."
- **Evidence.** `export-01-manifest.json`, `export-01-recomputed-hashes.csv`.

#### EXPORT-02 — Native + load file + metadata + chain-of-custody log present

- **Objective.** Confirm the export package contains all four required artifact classes.
- **Preconditions.** EXPORT-01 PASS.
- **Steps.** Inventory package contents; classify each file; map to required artifact class.
- **Expected.** Native files (per Microsoft format), load file (.dat or .csv per export option), metadata fields per Microsoft schema, chain-of-custody log.
- **Pass criteria.** All four artifact classes present AND non-empty.
- **Audit assertion.** "Export package contents match Microsoft documentation for unified eDiscovery export."
- **Evidence.** `export-02-inventory.json`.

#### EXPORT-03 — Immutable storage handoff outside the live tenant

- **Objective.** Confirm the export package is committed to immutable storage **external** to the live M365 tenant before any SEC 17a-4(f) audit-trail-alternative claim is asserted.
- **Preconditions.** EXPORT-01..02 PASS.
- **Steps.** Upload package to designated immutable target (Azure Storage with time-based immutability policy locked, or equivalent WORM target). Confirm immutability policy is **locked** (not unlocked) AND retention duration ≥ FSI horizon.
- **Expected.** Immutable target acknowledges write; subsequent overwrite/delete attempts return policy-violation error.
- **Pass criteria.** Lock state is `Locked` AND attempted overwrite returns the documented immutability error.
- **Audit assertion.** "Audit-trail-alternative integrity is anchored outside the live tenant with WORM-equivalent retention."
- **Evidence.** `export-03-immutable.json` with target URI, policy state, and overwrite-attempt response.

### 4.9 AUDIT — UAL eDiscovery RecordType Reconciliation (3 tests)

#### AUDIT-01 — `Discovery` / `eDiscovery` RecordType events present for cycle operations

- **Objective.** Confirm every meaningful cycle action produced a UAL event within PRE-04 P95.
- **Preconditions.** PRE-04..05 PASS.
- **Steps.** Pull UAL events filtered by `RecordType` ∈ {`Discovery`, `eDiscovery`} for the cycle window via `Search-UnifiedAuditLog`. Reconcile event IDs to operations performed in CASE/HOLD/SEARCH/EXPORT.
- **Expected.** ≥ 1 UAL event per cycle Graph operation.
- **Pass criteria.** Reconciliation 100% within P95 + 50% drift; orphans flagged.
- **Audit assertion.** "Cycle's eDiscovery operations are independently auditable from UAL."
- **Evidence.** `audit-01-reconciliation.json`.

#### AUDIT-02 — `CopilotInteraction` UAL events present for marker prompts

- **Objective.** Confirm UAL captured the PRE-04 marker interactions and that body parsing yields ConversationId, AppHost, and (per Microsoft documentation) prompt/response telemetry sufficient for occurrence proof.
- **Preconditions.** PRE-04 PASS.
- **Steps.** `Search-UnifiedAuditLog -RecordType CopilotInteraction -StartDate ... -EndDate ...` filtered by cycle marker; parse `AuditData` JSON.
- **Expected.** All three marker events present; ConversationIds match COPILOT-03 substrate items.
- **Pass criteria.** 100% reconciliation; UAL is treated as **occurrence** evidence and the substrate item is **content** evidence (no conflation — see anti-pattern §8 row 1).
- **Audit assertion.** "Occurrence (UAL) and content (substrate) streams reconcile by ConversationId — supports FINRA 4511 dual-record defensibility."
- **Evidence.** `audit-02-copilot-ual.json`.

#### AUDIT-03 — Audit search results exported within the 30-day completed-search retention

- **Objective.** Confirm cycle exports complete within Microsoft's documented 30-day completed-audit-search retention window.
- **Preconditions.** AUDIT-01..02 PASS.
- **Steps.** Record `searchCompletedUtc` and `evidenceExportedUtc` for each cycle audit search; assert `evidenceExportedUtc - searchCompletedUtc ≤ 30 days`.
- **Expected.** All exports within window.
- **Pass criteria.** 100% within 30 days AND median ≤ 7 days.
- **Audit assertion.** "Cycle does not rely on Microsoft to retain raw search results beyond the documented 30-day post-completion window."
- **Evidence.** `audit-03-export-timing.json`.

### 4.10 NEG — Negative / Anti-Pattern Controls (3 tests)

#### NEG-01 — Retired classic eDiscovery cmdlets fail safely (post Aug-31-2025)

- **Objective.** Confirm `New-ComplianceCase`, `New-CaseHoldPolicy`, `Set-CaseHoldPolicy`, `New-ComplianceSearch`, and similar classic cmdlets either error or return clear deprecation messages in Commercial / GCC / GCC High / DoD.
- **Preconditions.** PRE-06 PASS (cloud != 21Vianet).
- **Steps.** Connect to Security & Compliance PowerShell; invoke each retired cmdlet with safe parameters; capture error stream.
- **Expected.** Each invocation either fails with deprecation/not-found error OR succeeds against an empty no-op pathway with no side effect.
- **Pass criteria.** No retired cmdlet creates new case/hold/search artifacts in the tenant.
- **Audit assertion.** "Cycle does not depend on retired classic eDiscovery surfaces."
- **Evidence.** `neg-01-retired-cmdlets.json`.

#### NEG-02 — `from:Copilot` KeyQL filter returns zero/wrong (anti-pattern detection)

- **Objective.** Confirm the common misconception — that Copilot prompts can be filtered with `from:Copilot` as if Copilot were a chat sender — is detected and rejected.
- **Preconditions.** SEARCH-01 PASS.
- **Steps.** Execute search with KeyQL `from:Copilot AND fsi-cycle-{cycleId}` against Copilot interactions location.
- **Expected.** Zero hits OR hits that do not match the cycle's known marker prompts.
- **Pass criteria.** Result demonstrably wrong AND test PASSES on the **negative** result (i.e., we are confirming the anti-pattern fails).
- **Audit assertion.** "`from:Copilot` is documented as ineffective; cycle's KeyQL templates do not rely on it."
- **Evidence.** `neg-02-from-copilot.json`.

#### NEG-03 — Bulk `eDiscovery Administrator` assignment without PIM is detected

- **Objective.** Confirm Sentinel / monitoring (cross-link 1.24) detects an attempt to grant `eDiscovery Administrator` to multiple identities without PIM.
- **Preconditions.** PRE-02 PASS, 1.24 analytics deployed.
- **Steps.** In a synthetic identity, attempt to grant `eDiscovery Administrator` permanently to two test identities via Graph; assert (a) operation either fails per Conditional Access policy OR succeeds and (b) Sentinel raises an alert within its documented detection window.
- **Expected.** Either CA blocks OR Sentinel detects.
- **Pass criteria.** At least one of the two controls (CA, Sentinel) fires.
- **Audit assertion.** "Standing-privilege escalation attempts are detected by an independent control plane."
- **Evidence.** `neg-03-detection.json`, Sentinel incident ID where applicable.

### 4.11 SOV — Sovereign-Cloud Parity Re-check (2 tests)

#### SOV-01 — Per-cloud feature parity re-asserted from Microsoft Learn

- **Objective.** Re-confirm that the Copilot interactions location, Copilot activity condition, SubstrateHolds, and unified eDiscovery export are **currently** documented as available in this cycle's cloud at `lastVerifiedUtc`.
- **Preconditions.** PRE-06 PASS.
- **Steps.** Open Microsoft Learn pages for unified eDiscovery, Copilot interactions location, and Copilot audit; record `lastVerifiedUtc` of the verification, current page version (where shown), and any per-cloud notes.
- **Expected.** Cloud parity confirmed for cycle's cloud OR a deviation is recorded.
- **Pass criteria.** Confirmation captured AND deviation list (if any) is non-silent.
- **Audit assertion.** "Sovereign-cloud parity is not assumed; it is re-verified each cycle."
- **Evidence.** `sov-01-parity.json` with Learn URLs and verification notes.

#### SOV-02 — Cycle execution against declared cloud only

- **Objective.** Confirm no test in §4 unintentionally crossed cloud boundaries (e.g., evidence pack written to Commercial Azure storage from a GCC High cycle).
- **Preconditions.** PRE-06 PASS, EXPORT-03 PASS.
- **Steps.** Inventory all evidence-pack write targets; map each to a sovereign cloud; assert all match `manifest.tenant.cloud`.
- **Expected.** All writes within the declared cloud's data-residency boundary.
- **Pass criteria.** Zero cross-cloud writes.
- **Audit assertion.** "Cycle observed sovereign-cloud data-residency for all evidence artifacts."
- **Evidence.** `sov-02-residency.json`.

### 4.12 IR — Incident Readiness Drills (2 tests)

#### IR-01 — Annual FRCP 37(e) preservation tabletop

- **Objective.** Exercise the team's ability to issue a litigation hold within hours of trigger receipt and to defend the reasonable-steps standard.
- **Preconditions.** Annual cadence; Legal Officer scheduled.
- **Steps.** Inject a simulated litigation-hold trigger memo from Legal; team executes hold creation, custodian addition, scope inclusion of Copilot interactions, and hold confirmation per HOLD-02. Capture wall-clock times and decision rationale.
- **Expected.** Hold confirmed within an internally agreed SLO (recommended ≤ 24 hours from trigger memo).
- **Pass criteria.** Confirmed AND tabletop minutes signed by Legal Officer + AI Governance Lead.
- **Audit assertion.** "Team can demonstrate FRCP 37(e) reasonable-steps preservation capability annually."
- **Evidence.** `ir-01-tabletop.json`, signed minutes PDF.

#### IR-02 — FINRA Rule 8210 ~30-day production drill

- **Objective.** Exercise end-to-end production from custodian/scope memo to immutable handoff within an internally agreed surrogate of the typical FINRA 8210 examiner timeframe.
- **Preconditions.** Annual cadence.
- **Steps.** Issue surrogate 8210-style request specifying custodians, time window, and topic; execute CASE → CUSTODIAN → SEARCH → REVIEW → EXPORT → immutable handoff. Capture wall-clock T0 → T_handoff.
- **Expected.** Production complete within internally agreed SLO (recommended ≤ 30 calendar days).
- **Pass criteria.** Within SLO AND chain-of-custody log signed.
- **Audit assertion.** "Team can demonstrate end-to-end production capability within the internally agreed FINRA 8210 surrogate window."
- **Evidence.** `ir-02-production.json`, chain-of-custody PDF.

---
## 5. Sovereign-Cloud Matrix

Each cycle re-asserts this matrix from Microsoft Learn at `lastVerifiedUtc`. Do **not** treat any cell as static between cycles.

| Capability | Commercial | GCC | GCC High | DoD | 21Vianet |
|---|---|---|---|---|---|
| Unified eDiscovery (formerly Premium) | GA | GA | GA | GA | Not available — classic only |
| Classic eDiscovery (Standard / Premium) | Retired Aug 31, 2025 | Retired Aug 31, 2025 | Retired Aug 31, 2025 | Retired Aug 31, 2025 | In use |
| Copilot interactions location | Available | Verify per cycle | Verify per cycle | Verify per cycle | N/A |
| Copilot activity condition card | Available | Verify per cycle | Verify per cycle | Verify per cycle | N/A |
| SubstrateHolds container behaviour | Documented | Verify per cycle | Verify per cycle | Verify per cycle | N/A |
| Microsoft 365 Copilot license SKU | Available | Available (per Microsoft licensing matrix) | Verify per cycle | Verify per cycle | N/A |
| Purview Audit (Premium) | Available | Available | Available | Available | Verify per cycle |
| Hash-chain export package | Available | Available | Available | Available | N/A (classic surface differs) |
| Microsoft Graph eDiscovery API | GA in v1.0 / beta per resource | Verify per cycle | Verify per cycle | Verify per cycle | N/A |
| Sentinel cross-control integration (1.24) | Available | Available | Available | Available | Out of scope |

> Cycle execution is **forbidden** in 21Vianet via this playbook (PRE-06 halts). A separate validator targeting the classic experience is out of scope here.

---

## 6. Evidence Pack

### 6.1 JSON Schema (cycle artifact)

The cycle's top-level evidence artifact is a JSON document conforming to the schema below. The schema is intentionally permissive on test field shapes (each test serializes its own evidence sub-document referenced by file path) but strict on the cycle envelope.

Use `fsi-agentgov.example` as a placeholder identifier only (placeholder — replace with your tenant) before publishing an internal schema endpoint.

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "https://fsi-agentgov.example/schemas/control-1.19/cycle-evidence.v1.4.json",
  "title": "Control 1.19 eDiscovery Cycle Evidence",
  "type": "object",
  "required": [
    "controlId", "cycleId", "playbookVersion", "cycleStartedUtc", "cycleCompletedUtc",
    "tenant", "operator", "preflightGates", "tests", "manifest", "attestation"
  ],
  "additionalProperties": false,
  "properties": {
    "controlId":        { "const": "1.19" },
    "cycleId":          { "type": "string", "pattern": "^[0-9]{4}-[0-9]{2}-[A-Z0-9]{6,12}$" },
    "playbookVersion":  { "type": "string", "pattern": "^v[0-9]+\\.[0-9]+$" },
    "cycleStartedUtc":  { "type": "string", "format": "date-time" },
    "cycleCompletedUtc":{ "type": "string", "format": "date-time" },
    "lastVerifiedUtc":  { "type": "string", "format": "date-time" },
    "tenant": {
      "type": "object",
      "required": ["tenantId", "cloud", "region"],
      "properties": {
        "tenantId": { "type": "string", "format": "uuid" },
        "cloud":    { "enum": ["Commercial", "GCC", "GCCHigh", "DoD"] },
        "region":   { "type": "string" }
      }
    },
    "operator": {
      "type": "object",
      "required": ["principalId", "pimActivationIds"],
      "properties": {
        "principalId":      { "type": "string", "format": "uuid" },
        "pimActivationIds": { "type": "array", "items": { "type": "string" }, "minItems": 1 }
      }
    },
    "preflightGates": {
      "type": "object",
      "required": ["PRE-01","PRE-02","PRE-03","PRE-04","PRE-05","PRE-06","PRE-07"],
      "additionalProperties": false,
      "patternProperties": {
        "^PRE-0[1-7]$": {
          "type": "object",
          "required": ["status", "evidenceRef"],
          "properties": {
            "status":      { "enum": ["PASS", "FAIL"] },
            "evidenceRef": { "type": "string" },
            "notes":       { "type": "string" }
          }
        }
      }
    },
    "tests": {
      "type": "array",
      "minItems": 35,
      "items": {
        "type": "object",
        "required": ["id", "namespace", "status", "evidenceRef"],
        "properties": {
          "id":          { "type": "string", "pattern": "^(LIC|CASE|CUSTODIAN|SEARCH|COPILOT|HOLD|REVIEW|EXPORT|AUDIT|NEG|SOV|IR)-[0-9]{2}$" },
          "namespace":   { "enum": ["LIC","CASE","CUSTODIAN","SEARCH","COPILOT","HOLD","REVIEW","EXPORT","AUDIT","NEG","SOV","IR"] },
          "status":      { "enum": ["PASS", "FAIL", "SKIP"] },
          "evidenceRef": { "type": "string" },
          "skipJustification": { "type": "string" },
          "acceptedRiskUntilUtc": { "type": "string", "format": "date-time" }
        },
        "allOf": [
          { "if": { "properties": { "status": { "const": "SKIP" } } },
            "then": { "required": ["skipJustification", "acceptedRiskUntilUtc"] } }
        ]
      }
    },
    "manifest": {
      "type": "object",
      "required": ["expectedExclusions", "copilotStudioGapInventory", "deviations"],
      "properties": {
        "expectedExclusions":         { "type": "array", "items": { "type": "string" } },
        "copilotStudioGapInventory":  { "type": "array", "items": { "type": "object" } },
        "deviations":                 { "type": "array", "items": { "type": "object" } }
      }
    },
    "attestation": {
      "type": "object",
      "required": ["attestationSha256", "previousCycleAttestationSha256", "signatures"],
      "properties": {
        "attestationSha256":              { "type": "string", "pattern": "^[a-f0-9]{64}$" },
        "previousCycleAttestationSha256": { "type": "string", "pattern": "^[a-f0-9]{64}$" },
        "signatures": {
          "type": "array",
          "minItems": 3,
          "items": {
            "type": "object",
            "required": ["role", "principalId", "signedUtc", "signature"],
            "properties": {
              "role":        { "enum": ["AIGovernanceLead", "LegalOfficer", "PurviewEDiscoveryManager"] },
              "principalId": { "type": "string", "format": "uuid" },
              "signedUtc":   { "type": "string", "format": "date-time" },
              "signature":   { "type": "string" }
            }
          }
        }
      }
    }
  }
}
```

### 6.2 PowerShell Validator (skeleton)

The validator returns three exit codes: **0** = all PRE and tests PASS (or SKIP with valid `acceptedRiskUntilUtc`); **1** = any test FAIL or unjustified SKIP; **2** = any PRE gate FAIL (cycle halted before §4 executed).

```powershell
#requires -Version 7.2
#requires -Modules @{ ModuleName='ExchangeOnlineManagement'; ModuleVersion='3.4.0' }
#requires -Modules @{ ModuleName='Microsoft.Graph.Security';   ModuleVersion='2.20.0' }
#requires -Modules @{ ModuleName='PnP.PowerShell';             ModuleVersion='2.4.0' }

[CmdletBinding()]
param(
    [Parameter(Mandatory)] [string] $CycleId,
    [Parameter(Mandatory)] [ValidateSet('Commercial','GCC','GCCHigh','DoD')] [string] $Cloud,
    [Parameter(Mandatory)] [string] $EvidenceRoot,
    [string] $PlaybookVersion = 'v1.4'
)

$ErrorActionPreference = 'Stop'
$cycle = [ordered]@{
    controlId        = '1.19'
    cycleId          = $CycleId
    playbookVersion  = $PlaybookVersion
    cycleStartedUtc  = (Get-Date).ToUniversalTime().ToString('o')
    tenant           = @{ cloud = $Cloud }
    preflightGates   = @{}
    tests            = @()
}

function Invoke-Gate {
    param([string]$Id, [scriptblock]$Body)
    Write-Host "▶ $Id"
    try {
        $result = & $Body
        $cycle.preflightGates[$Id] = @{ status = 'PASS'; evidenceRef = $result.EvidencePath }
    } catch {
        $cycle.preflightGates[$Id] = @{ status = 'FAIL'; evidenceRef = $null; notes = $_.Exception.Message }
        Write-Error "GATE FAIL: $Id — $($_.Exception.Message)"
        $cycle.cycleCompletedUtc = (Get-Date).ToUniversalTime().ToString('o')
        $cycle | ConvertTo-Json -Depth 12 | Set-Content -Path (Join-Path $EvidenceRoot 'cycle-evidence.json')
        exit 2
    }
}

function Invoke-Test {
    param([string]$Id, [string]$Namespace, [scriptblock]$Body)
    Write-Host "  • $Id"
    $entry = [ordered]@{ id = $Id; namespace = $Namespace }
    try {
        $result = & $Body
        $entry.status      = if ($result.Skip) { 'SKIP' } else { 'PASS' }
        $entry.evidenceRef = $result.EvidencePath
        if ($result.Skip) {
            $entry.skipJustification    = $result.SkipReason
            $entry.acceptedRiskUntilUtc = $result.AcceptedRiskUntilUtc
        }
    } catch {
        $entry.status      = 'FAIL'
        $entry.evidenceRef = $null
        $entry.notes       = $_.Exception.Message
    }
    $cycle.tests += [pscustomobject]$entry
}

# --- PRE gates (HALT on failure) ---
Invoke-Gate 'PRE-01' { Test-ModuleVersions -EvidenceRoot $EvidenceRoot }
Invoke-Gate 'PRE-02' { Test-PimActivation  -EvidenceRoot $EvidenceRoot }
Invoke-Gate 'PRE-03' { Test-LicenseFloor   -EvidenceRoot $EvidenceRoot }
Invoke-Gate 'PRE-04' { Test-TenantBaseline -EvidenceRoot $EvidenceRoot }
Invoke-Gate 'PRE-05' { Test-AuditRetention -EvidenceRoot $EvidenceRoot }
Invoke-Gate 'PRE-06' { Test-CloudGuard     -EvidenceRoot $EvidenceRoot -DeclaredCloud $Cloud }
Invoke-Gate 'PRE-07' { Test-Fixtures       -EvidenceRoot $EvidenceRoot }

# --- Tests (do not halt; record FAIL and continue) ---
Invoke-Test 'LIC-01'       'LIC'       { Test-LicUnifiedEDiscovery -EvidenceRoot $EvidenceRoot }
Invoke-Test 'LIC-02'       'LIC'       { Test-LicCopilotPerCustodian -EvidenceRoot $EvidenceRoot }
Invoke-Test 'LIC-03'       'LIC'       { Test-LicRoleSeparation -EvidenceRoot $EvidenceRoot }
Invoke-Test 'CASE-01'      'CASE'      { Test-CaseCreate -EvidenceRoot $EvidenceRoot }
Invoke-Test 'CASE-02'      'CASE'      { Test-CaseLifecycle -EvidenceRoot $EvidenceRoot }
Invoke-Test 'CASE-03'      'CASE'      { Test-CaseHistory -EvidenceRoot $EvidenceRoot }
Invoke-Test 'CUSTODIAN-01' 'CUSTODIAN' { Test-CustodianAdd -EvidenceRoot $EvidenceRoot }
Invoke-Test 'CUSTODIAN-02' 'CUSTODIAN' { Test-CustodianCopilotSource -EvidenceRoot $EvidenceRoot }
Invoke-Test 'CUSTODIAN-03' 'CUSTODIAN' { Test-CustodianRemoval -EvidenceRoot $EvidenceRoot }
Invoke-Test 'SEARCH-01'    'SEARCH'    { Test-SearchDeterminism -EvidenceRoot $EvidenceRoot }
Invoke-Test 'SEARCH-02'    'SEARCH'    { Test-SearchCopilotHits -EvidenceRoot $EvidenceRoot }
Invoke-Test 'SEARCH-03'    'SEARCH'    { Test-SearchKeyqlGrammar -EvidenceRoot $EvidenceRoot }
Invoke-Test 'COPILOT-01'   'COPILOT'   { Test-CopilotLocation -EvidenceRoot $EvidenceRoot }
Invoke-Test 'COPILOT-02'   'COPILOT'   { Test-CopilotActivity -EvidenceRoot $EvidenceRoot }
Invoke-Test 'COPILOT-03'   'COPILOT'   { Test-CopilotRoundtrip -EvidenceRoot $EvidenceRoot }
Invoke-Test 'COPILOT-04'   'COPILOT'   { Test-CopilotStudioGap -EvidenceRoot $EvidenceRoot }
Invoke-Test 'HOLD-01'      'HOLD'      { Test-HoldCreate -EvidenceRoot $EvidenceRoot }
Invoke-Test 'HOLD-02'      'HOLD'      { Test-HoldConfirmation -EvidenceRoot $EvidenceRoot }
Invoke-Test 'HOLD-03'      'HOLD'      { Test-HoldSubstrateSurvival -EvidenceRoot $EvidenceRoot }
Invoke-Test 'HOLD-04'      'HOLD'      { Test-HoldRelease -EvidenceRoot $EvidenceRoot }
Invoke-Test 'REVIEW-01'    'REVIEW'    { Test-ReviewLoadReport -EvidenceRoot $EvidenceRoot }
Invoke-Test 'REVIEW-02'    'REVIEW'    { Test-ReviewSod -EvidenceRoot $EvidenceRoot }
Invoke-Test 'EXPORT-01'    'EXPORT'    { Test-ExportManifest -EvidenceRoot $EvidenceRoot }
Invoke-Test 'EXPORT-02'    'EXPORT'    { Test-ExportInventory -EvidenceRoot $EvidenceRoot }
Invoke-Test 'EXPORT-03'    'EXPORT'    { Test-ExportImmutable -EvidenceRoot $EvidenceRoot }
Invoke-Test 'AUDIT-01'     'AUDIT'     { Test-AuditDiscoveryEvents -EvidenceRoot $EvidenceRoot }
Invoke-Test 'AUDIT-02'     'AUDIT'     { Test-AuditCopilotEvents -EvidenceRoot $EvidenceRoot }
Invoke-Test 'AUDIT-03'     'AUDIT'     { Test-AuditExportTiming -EvidenceRoot $EvidenceRoot }
Invoke-Test 'NEG-01'       'NEG'       { Test-NegRetiredCmdlets -EvidenceRoot $EvidenceRoot }
Invoke-Test 'NEG-02'       'NEG'       { Test-NegFromCopilot -EvidenceRoot $EvidenceRoot }
Invoke-Test 'NEG-03'       'NEG'       { Test-NegBulkAdminDetection -EvidenceRoot $EvidenceRoot }
Invoke-Test 'SOV-01'       'SOV'       { Test-SovParity -EvidenceRoot $EvidenceRoot }
Invoke-Test 'SOV-02'       'SOV'       { Test-SovResidency -EvidenceRoot $EvidenceRoot }
Invoke-Test 'IR-01'        'IR'        { Test-IrTabletop -EvidenceRoot $EvidenceRoot }
Invoke-Test 'IR-02'        'IR'        { Test-IrProductionDrill -EvidenceRoot $EvidenceRoot }

$cycle.cycleCompletedUtc = (Get-Date).ToUniversalTime().ToString('o')
$cycle | ConvertTo-Json -Depth 12 | Set-Content -Path (Join-Path $EvidenceRoot 'cycle-evidence.json')

$failed = $cycle.tests | Where-Object {
    $_.status -eq 'FAIL' -or
    ($_.status -eq 'SKIP' -and -not $_.acceptedRiskUntilUtc)
}
if ($failed) { exit 1 } else { exit 0 }
```

### 6.3 Manifest Builder

The manifest is constructed at cycle start and amended at cycle end. It is the single source of truth for *what the cycle was supposed to do*; the evidence pack is *what the cycle actually did*. They must reconcile.

```powershell
function New-CycleManifest {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory)] [string] $CycleId,
        [Parameter(Mandatory)] [ValidateSet('Commercial','GCC','GCCHigh','DoD')] [string] $Cloud,
        [Parameter(Mandatory)] [string] $TenantId,
        [Parameter(Mandatory)] [string] $PreviousCycleAttestationSha256,
        [string[]] $Custodians,
        [object[]] $CopilotStudioAgents
    )

    [ordered]@{
        controlId       = '1.19'
        cycleId         = $CycleId
        playbookVersion = 'v1.4'
        lastVerifiedUtc = (Get-Date).ToUniversalTime().ToString('o')
        tenant          = @{ tenantId = $TenantId; cloud = $Cloud }
        custodians      = $Custodians
        keyqlTemplates  = @(
            @{ name = 'cycle-marker'; path = 'keyql-templates/v1.4-cycle-marker.kql' }
        )
        expectedExclusions = @(
            'unsupported-file-type-per-microsoft-export-doc',
            'attachment-truncated-per-export-size-cap'
        )
        copilotStudioGapInventory = @($CopilotStudioAgents | ForEach-Object {
            @{ agentId = $_.Id; persistsTo = $_.Persistence; retentionEvidenceRef = $_.RetentionEvidenceRef }
        })
        deviations = @()
        previousCycleAttestationSha256 = $PreviousCycleAttestationSha256
    }
}
```

### 6.4 Artifact Catalog

Every cycle produces (at minimum) the following artifacts under `$EvidenceRoot/{cycleId}/`:

| Artifact | Path (relative to cycle root) | Producer | Required |
|---|---|---|---|
| Cycle envelope | `cycle-evidence.json` | Validator (§6.2) | Yes |
| Cycle manifest | `manifest.json` | Manifest builder (§6.3) | Yes |
| PRE-gate evidences | `preflight/pre-0{1..7}-*.json` | Gate functions | Yes |
| Test evidences | `tests/{namespace}/{id}.json` | Test functions | Yes (35) |
| Portal screenshots | `screenshots/{id}.png` | Operator | Where listed in §4 |
| KeyQL templates (frozen) | `keyql-templates/v{ver}-*.kql` | Operator | Yes |
| Export packages (raw) | `exports/{caseId}/{exportId}/...` | Export pipeline | Yes (per cycle) |
| Export manifests | `exports/{caseId}/{exportId}/manifest.sig.json` | EXPORT-01 | Yes |
| Immutable handoff receipts | `exports/{caseId}/{exportId}/immutable-receipt.json` | EXPORT-03 | Yes |
| Sentinel incident refs | `cross-controls/1.24/{incidentId}.json` | NEG-03 | If raised |
| Tabletop minutes | `ir/ir-01-tabletop.signed.pdf` | Legal Officer | Annual cycle |
| Production-drill log | `ir/ir-02-production.signed.pdf` | Legal Officer | Annual cycle |
| Attestation | `attestation.signed.json` | §7 | Yes |

### 6.5 Retention Table

| Artifact class | Minimum retention | Storage class | Rationale |
|---|---|---|---|
| `cycle-evidence.json`, `manifest.json`, `attestation.signed.json` | 7 years | Immutable (WORM-equivalent) | FINRA 4511 / SEC 17a-4 evidence of supervisory control operating effectiveness |
| Per-test evidence JSONs | 7 years | Immutable | Same |
| Export packages + manifests | 7 years (or matter-life if longer) | Immutable | SEC 17a-4(f) audit-trail-alternative anchor |
| Portal screenshots | 7 years | Immutable | Defensibility of UI-state-at-cycle-time |
| KeyQL frozen templates | 7 years | Versioned (git-ok) | Reproducibility |
| Tabletop / drill PDFs | 7 years | Immutable | FRCP 37(e) and FINRA 8210 readiness |
| Sentinel incident snapshots (NEG-03) | Per 1.24 retention | Per 1.24 | Cross-control |

---

## 7. Attestation Block

A cycle is not complete until the attestation is signed by **three** roles. The attestation is a JSON document with a stable canonicalisation, hashed with SHA-256, and the hash is recorded in the next cycle's `previousCycleAttestationSha256` to form a chain.

```json
{
  "controlId": "1.19",
  "cycleId": "2026-04-XYZ123",
  "playbookVersion": "v1.4",
  "cycleStartedUtc": "2026-04-08T13:02:11Z",
  "cycleCompletedUtc": "2026-04-08T19:47:55Z",
  "lastVerifiedUtc": "2026-04-08T13:00:00Z",
  "tenant": { "tenantId": "00000000-0000-0000-0000-000000000000", "cloud": "Commercial" },
  "summary": {
    "preflight": "ALL_PASS",
    "testsTotal": 35,
    "testsPass": 35,
    "testsFail": 0,
    "testsSkip": 0
  },
  "evidenceManifestSha256": "<sha256-of-cycle-evidence.json>",
  "exportPackageSha256s": [
    "<sha256-of-export-1>",
    "<sha256-of-export-2>"
  ],
  "previousCycleAttestationSha256": "<sha256-of-prior-attestation>",
  "attestationSha256": "<sha256-of-this-document-pre-signatures>",
  "signatures": [
    {
      "role": "AIGovernanceLead",
      "principalId": "11111111-1111-1111-1111-111111111111",
      "signedUtc": "2026-04-08T20:01:03Z",
      "signature": "<base64-detached-signature-over-attestationSha256>"
    },
    {
      "role": "LegalOfficer",
      "principalId": "22222222-2222-2222-2222-222222222222",
      "signedUtc": "2026-04-08T20:09:42Z",
      "signature": "<base64-detached-signature-over-attestationSha256>"
    },
    {
      "role": "PurviewEDiscoveryManager",
      "principalId": "33333333-3333-3333-3333-333333333333",
      "signedUtc": "2026-04-08T20:14:18Z",
      "signature": "<base64-detached-signature-over-attestationSha256>"
    }
  ],
  "statement": "We attest that the verification cycle described herein was executed by the named operator under PIM-activated privileged roles; that PRE gates 01–07 returned PASS prior to any §4 test execution; that the §4 test results recorded in cycle-evidence.json reflect the actual tenant behaviour observed at cycleCompletedUtc; that all evidence artifacts have been committed to immutable storage as required by §6.5; and that this attestation is intended to support compliance with the regulations enumerated in the playbook's hedging notice and does not guarantee legal compliance."
}
```

> **Hash-chain rule.** A cycle whose `previousCycleAttestationSha256` does not equal the prior cycle's `attestationSha256` (post-signature, computed over the same canonicalisation as the prior cycle) is treated as a chain break and reported to FSI Internal Audit.

---
## 8. Anti-Patterns

Each row pairs an anti-pattern with the test(s) that detect it. A cycle that passes §4 but fails to detect any of these is treated as a methodology gap and surfaced to AI Governance Lead for playbook revision.

| # | Anti-pattern | Why it fails defensibility | Detected by |
|---|---|---|---|
| 1 | Treating the `CopilotInteraction` UAL `AuditData` body as the authoritative full prompt-and-response payload for legal production | UAL is the **occurrence** signal; the substrate item placed under hold is the **content** evidence. Conflating the two undermines completeness arguments under FRCP 37(e) and SEC 17a-4. | AUDIT-02, COPILOT-03 |
| 2 | Producing a Copilot interaction in discovery without first verifying it resides in `SubstrateHolds` for the held custodian | A "hold" that did not actually preserve the substrate item is the most common silent-failure mode for Copilot eDiscovery. | HOLD-03 |
| 3 | Using real custodian UPNs or live matter IDs in test fixtures | Mixes test artifacts with real evidence and risks GLBA 501(b) and SOX 802 spoliation findings. | PRE-07 |
| 4 | Attempting any deletion-of-original or release-of-hold test before HOLD-02 confirmation | Risks actual spoliation if the hold was not in fact active; also breaks the FRCP 37(e) reasonable-steps narrative. | HOLD-02 (PRE-condition for HOLD-03/04) |
| 5 | Exporting from a review set without a SHA-256 manifest | Defeats the SEC 17a-4(f) audit-trail-alternative integrity claim; chain-of-custody becomes unprovable. | EXPORT-01 |
| 6 | Issuing a litigation hold to a custodian without delivering the legal hold notification | FRCP and many state-bar rules require notice; absence of notice undermines the reasonable-steps defense. | IR-01 (tabletop) |
| 7 | Granting `eDiscovery Administrator` as a permanent assignment to one or more identities | Standing tenant-wide eDiscovery power; SOX 404 and FFIEC ITRMP §III.A.4 SoD violation. | PRE-02, NEG-03 |
| 8 | Granting export permission to identities that also hold `Reviewer` role | Single-role compromise can both review and exfiltrate evidence. | LIC-03, REVIEW-02 |
| 9 | Assuming Commercial-cloud feature parity in GCC / GCC High / DoD without per-cycle re-verification | Sovereign-cloud feature surfaces drift; assumption produces false-positive PASS records. | SOV-01, PRE-06 |
| 10 | Calling retired classic eDiscovery cmdlets after Aug 31, 2025 in non-21Vianet clouds | Cycles built on retired surfaces are not reproducible and may silently fall back to no-op behaviour. | NEG-01 |
| 11 | Relying on the M365 Copilot interactions location to discover Copilot Studio agents that persist transcripts to Dataverse | These transcripts are NOT in the M365 substrate and require a separate Dataverse retention story (1.9). | COPILOT-04 |
| 12 | Claiming SEC 17a-4(f) audit-trail-alternative compliance with exports stored only in mutable tenant-internal locations | The standard requires WORM-equivalent preservation outside the live tenant. | EXPORT-03 |
| 13 | Single-administrator hold creation and confirmation (no four-eyes / Legal sign-off) | Allows a single insider to silently weaken preservation; FINRA 3110 supervisory structure failure. | LIC-03, IR-01 |
| 14 | Deleting custodian content under any retention story before confirming the matter's hold has been formally released | Spoliation risk; FRCP 37(e) sanctions. | HOLD-02, HOLD-04, cross-link 1.9 |
| 15 | Using `from:Copilot` (or similar sender-style filters) in KeyQL to find Copilot prompts | Copilot is not a chat sender; the filter returns wrong/empty results and gives a false sense of completeness. | NEG-02 |
| 16 | Relying on Content Search (find-only) for litigation events instead of creating a hold | Content Search does not preserve; matching items can be modified or deleted before export. | HOLD-01 |
| 17 | Inventing or quoting a numeric SLA for hold propagation, KeyQL index lag, or UAL ingestion | Microsoft does not publish single-number SLAs for these; assertions create misrepresentation risk. | §3, PRE-04 |
| 18 | Not capturing per-cycle Microsoft Learn `lastVerifiedUtc` for the sovereign-cloud parity claim | Without a verification timestamp, the parity claim is undated and cannot be defended a year later. | SOV-01 |

---

## 9. Cross-Links

| Reference | Why it matters here |
|---|---|
| Control 1.5 — DLP & sensitivity labels | Labels travel with substrate items; eDiscovery review sets surface label state for production decisioning. |
| Control 1.6 — DSPM for AI | DSPM AI inventory feeds candidate prompts for SEARCH-02 / COPILOT-02 sampling. |
| Control 1.7 — Audit logging | UAL is the occurrence stream reconciled in AUDIT-01..03. |
| Control 1.9 — Retention & deletion | Owns the Dataverse-side retention story for COPILOT-04 gap inventory. |
| Control 1.10 — Communication Compliance | Adjacent supervisory-review surface; cross-references suspicious Copilot interactions for hold candidates. |
| Control 1.13 — DCA AI monitoring | Provides upstream alerting that may trigger a litigation hold (IR-01 tabletop input). |
| Control 1.14 — Data minimization | Shapes which prompt/response fields are exported in EXPORT-02. |
| Control 1.21 — Adversarial input logging | Adversarial events are preserved under the same hold infrastructure exercised here. |
| Control 1.24 — Sentinel analytics | Provides NEG-03 detection of bulk privileged-role assignment. |
| Control 2.13 — Documentation & record-keeping | Owns the long-term retention catalog into which §6.5 plugs. |
| Control 4.6 — Grounding scope governance | Owns the Copilot Studio agent inventory used in COPILOT-04. |
| AI Incident Response Playbook | Defines IR-01 and IR-02 trigger memos and signed-minute templates. |

---

*Updated: May 2026 | Version: v1.6.2 | UI Verification Status: Current*
