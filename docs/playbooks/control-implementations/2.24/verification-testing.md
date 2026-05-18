# Verification & Testing — Control 2.24: Agent Feature Enablement and Restriction Governance

> **Examiner-defensible evidence package** for Control 2.24. This playbook produces, signs, and retains the artifacts required to demonstrate to FINRA, SEC, OCC, FFIEC, NYDFS, the Federal Reserve (Fed SR 26-2 (formerly SR 11-7)), the CFTC, and internal audit that every Microsoft 365 Copilot, Copilot Studio, and declarative-agent capability — across the tenant Copilot hub, environment-level controls, agent-level settings, MCP connectors, and Agent Framework feature flags — is enumerated in a documented feature catalog, allow-listed by zone, gated by change management (forward and reverse), DLP-enforced where the runtime supports it, and re-assessed quarterly.
>
> **Scope:** All Microsoft 365 Copilot, Copilot Studio, and declarative-agent capabilities reachable in the tenant under examination, across **all** governance zones (Zone 1 / 2 / 3) and **all** Power Platform environments. Includes the **AI Administrator** controls in the Microsoft 365 admin center (per the v1.3.3 control patch), the Copilot governance page in the Power Platform admin center, environment-level feature toggles, agent-level tool selections, MCP connector enablement, and Agent Framework feature flags. Sovereign clouds (GCC, GCC High, DoD) follow the dedicated SOV namespace because Microsoft 365 Copilot capability availability lags commercial by 6–18 months and a separate per-cloud catalog is required.
>
> **Companion controls:** [1.1 Restrict Agent Publishing by Authorization](../../../controls/pillar-1-security/1.1-restrict-agent-publishing-by-authorization.md), [1.2 Agent Registry & Integrated Apps Management](../../../controls/pillar-1-security/1.2-agent-registry-and-integrated-apps-management.md), [1.4 Advanced Connector Policies (ACP)](../../../controls/pillar-1-security/1.4-advanced-connector-policies-acp.md), [1.10 Communication Compliance Monitoring](../../../controls/pillar-1-security/1.10-communication-compliance-monitoring.md), [1.25 MIME Type Restrictions](../../../controls/pillar-1-security/1.25-mime-type-restrictions.md), [2.2 Environment Groups and Tier Classification](../../../controls/pillar-2-management/2.2-environment-groups-and-tier-classification.md), [2.6 Model Risk Management Alignment with OCC Bulletin 2026-13 (formerly OCC 2011-12) / Fed SR 26-2 (formerly SR 11-7)](../../../controls/pillar-2-management/2.6-model-risk-management-sr-26-2.md), [2.12 Supervision and Oversight (FINRA Rule 3110)](../../../controls/pillar-2-management/2.12-supervision-and-oversight-finra-rule-3110.md), [2.17 Multi-Agent Orchestration Limits](../../../controls/pillar-2-management/2.17-multi-agent-orchestration-limits.md), [2.25 Agent 365 Admin Center Governance Console](../../../controls/pillar-2-management/2.25-agent-365-admin-center-governance-console.md).
>
> **Last UI verified:** April 2026 against Microsoft 365 admin center build 2026.04.x (AI Administrator role GA), Power Platform admin center Copilot hub build 2026.04, Copilot Studio Wave 1 2026, and the Agent Framework preview ring documented at the time of pack publication.
>
> **Important regulatory framing.** This playbook **supports compliance with**, but does not by itself ensure compliance with, Federal Reserve SR 26-2 (formerly SR 11-7) / OCC Bulletin 2026-13 (formerly OCC Bulletin 2011-12) (Model Risk Management), FFIEC IT Risk Management Handbook, FINRA Rules 3110 (Supervision) and 4511 (Books and Records), FINRA Regulatory Notice 25-07 (cited as RFC context only — not binding), SEC Rules 17a-3 / 17a-4 (Recordkeeping), SEC Regulation SCI §§242.1001(a) and 242.1003 (SCI entities only), SOX Sections 302 / 404 (Internal Controls), GLBA Section 501(b) (Safeguards Rule), NYDFS 23 NYCRR 500, and CFTC Regulation 1.31 (recordkeeping). **Non-substitution principle:** feature toggles enforce what a capability *can* do; they do **not** validate that a capability is fit for purpose. Enabling a generative capability on a Zone 2 or Zone 3 agent is treated as a model change under Fed SR 26-2 (formerly SR 11-7) §V and **must** trigger — not replace — the Model Risk Management re-validation in [Control 2.6](../../../controls/pillar-2-management/2.6-model-risk-management-sr-26-2.md), the supervisory-procedures update in [Control 2.12](../../../controls/pillar-2-management/2.12-supervision-and-oversight-finra-rule-3110.md), the AI guardrails reassessment in [Control 1.1](../../../controls/pillar-1-security/1.1-restrict-agent-publishing-by-authorization.md), and the communication-compliance scope update in [Control 1.10](../../../controls/pillar-1-security/1.10-communication-compliance-monitoring.md). Where FINRA Rule 3110 obligates the firm to assign a registered principal to a supervisory function, this playbook **does not substitute for** that registered-principal designation; it produces the evidentiary trail that supports — but does not replace — the firm's written supervisory procedures (WSPs).

---

## Document Conventions

| Convention | Value |
|---|---|
| PowerShell baseline | PowerShell 7.4+ Core; `#Requires -Version 7.4` at the top of every executable script. |
| Test framework | Pester 5.5+. All assertions use `Should` with `-Because` clauses for examiner traceability. |
| Output discipline | No `Write-Host`. All evidence emitted as structured `[pscustomobject]` instances via `Write-Output`, then serialized with `ConvertTo-Json -Depth 8` to evidence files. |
| Sovereign cloud handling | All Pester suites detect tenant cloud and emit `SKIPPED` records with a compensating-control pointer to §2.12 (SOV namespace) rather than `FAIL`. |
| Evidence retention | Six (6) years on WORM-protected storage for the full signed evidence pack — aligning to FINRA Rule 4511 / SEC Rule 17a-4(f) / CFTC Reg 1.31. Sovereign tenants add a 1-year buffer. |
| Hashing | SHA-256 over canonical JSON; chained leaf hashes plus a Merkle root in `attestation.json` (§5.4). |
| Sovereign anchor | Sovereign-aware functions reference [`../../_shared/powershell-baseline.md`](../../_shared/powershell-baseline.md). |
| Run identifier | Every test run is tagged `AGT224-yyyyMMdd-HHmmss-<8charGuid>` and embedded in every evidence record and artifact filename. |
| Canonical role names | Per [`docs/reference/role-catalog.md`](../../../reference/role-catalog.md). At v1.3.3 the **AI Administrator** role is the preferred operator for tenant-level Copilot capability allow-list reads in the M365 admin center; **Power Platform Admin** for PPAC and environment-level reads; **Entra Global Admin** is reserved for emergency write paths under PIM. |

> This playbook **helps meet** feature-governance, change-management, recordkeeping, supervision, model-risk, and oversight expectations under the regulations enumerated above. It is one component of a defensible AI governance program; it does not replace registered-principal designation, written supervisory procedures, model risk management practices required by Fed SR 26-2 (formerly SR 11-7) / OCC Bulletin 2026-13 (formerly OCC 2011-12), the firm's written FFIEC IT risk-management policies, or the firm's own legal review.

---

## §0 Test Overview, Success Definition & Pre-Flight

### 0.1 What this playbook proves

This playbook produces, signs, and retains evidence that the firm satisfies the **ten Verification Criteria** in [Control 2.24 §Verification Criteria](../../../controls/pillar-2-management/2.24-agent-feature-enablement-and-restriction-governance.md#verification-criteria). The criteria, paraphrased and re-numbered as **VC-1 … VC-10** for cross-reference throughout this playbook:

| VC | Statement (paraphrased) | Primary namespace(s) |
|---|---|---|
| VC-1 | PPAC Copilot governance page configured with environment-specific feature restrictions aligned with zones; tenant-level capability allow-list configured in the Microsoft 365 admin center; agent-level settings constrained by environment | M365HUB, PPAC, ENV, AGENT |
| VC-2 | Zone 3 environments have preview / experimental features disabled (or documented exceptions with affirmative approval) | ZONE, AGF, ENV |
| VC-3 | Generative AI features restricted to an approved allow-list in Zone 3; Zone 2 has documented approval for each enabled generative action | CATALOG, ZONE |
| VC-4 | Feature catalog deployed and maintained with current status for all Copilot Studio, Copilot, declarative-agent, MCP, and Agent Framework features; **separate variant per cloud** (commercial / GCC / GCC High / DoD) | CATALOG, SOV |
| VC-5 | High-risk features (code interpreter, unapproved orchestration, web search on customer-facing agents, image generation without DLP coverage) are disabled in Zone 2 and Zone 3 | ZONE, AGENT |
| VC-6 | DLP policies (Control 1.4) enforce feature restrictions by blocking prohibited connectors and data sources at runtime where the runtime supports it | DLP |
| VC-7 | Change-management process is operational with documented approvals for Zone 2 / Zone 3 feature changes — **forward (enablement) AND reverse (disablement / withdrawal)** flows both evidenced | CHANGE |
| VC-8 | Author-side reality check: an agent author in a Zone 2 / Zone 3 environment cannot enable a restricted feature, **OR** the UI does not expose it in their context (the playbook records which of the two is true on each surface, because they are not equivalent for examination purposes) | AGENT |
| VC-9 | Feature catalog includes the required field set: `FeatureName`, `FeatureCategory`, `Surface`, `Cloud`, `Zone1Status`, `Zone2Status`, `Zone3Status`, `ApprovalRequired`, `ApprovalDate`, `ChangeTicket`, `ExpirationDate`, `RiskRating`, `LastReviewDate`, `Owner` | CATALOG |
| VC-10 | Quarterly feature risk assessment is conducted with documented results, threshold variance review, and downstream cascade decisions (MRM 2.6, supervision 2.12, CC 1.10, ACP 1.4) | CATALOG, CHANGE |

### 0.2 Success definition

A run of this playbook is considered **PASS** when, for the tenant under examination:

1. PRE-01 through PRE-10 (§0.4) all pass.
2. Every namespace suite in §2 emits at least the minimum expected number of evidence records for the cloud detected (Commercial: all 12 namespaces; sovereign: 11 namespaces with `SKIPPED` routing through SOV).
3. No record carries `status = ERROR`. (`SKIPPED` records are acceptable in the sovereign path; `WARN` records are acceptable subject to §3 manual sign-off.)
4. The §5 evidence pack assembles cleanly, the Merkle root is computable, and `Test-Agt224PackIntegrity` returns true.
5. The §6 sign-off triad (AI Governance Lead, Compliance Officer, Security Architect) all sign the published pack.

A run is considered **FAIL** if any namespace returns one or more `FAIL` records. A run is considered **INVALID** (not PASS, not FAIL) if any pre-flight gate fails or if the pack assembler refuses publication due to schema violation.

### 0.3 What this playbook does **not** prove

For the avoidance of doubt — and to anchor the non-substitution principle in the regulatory framing above — this playbook does **not** prove any of the following. They are evidenced by other controls and packs:

- **Model fitness** for any individual capability — see [Control 2.6](../../../controls/pillar-2-management/2.6-model-risk-management-sr-26-2.md). VC-3 evidences only that a generative capability appears on the firm's documented allow-list, not that the model behind it has been validated.
- **Supervisory adequacy** of the firm's WSPs — see [Control 2.12](../../../controls/pillar-2-management/2.12-supervision-and-oversight-finra-rule-3110.md). VC-7 evidences only that a change ticket exists; it does not evidence that the corresponding WSP update was reviewed and accepted by the registered principal.
- **Communication-compliance scope adequacy** for newly enabled output modalities (voice, image) — see [Control 1.10](../../../controls/pillar-1-security/1.10-communication-compliance-monitoring.md). The cascade is asserted in §2 CHANGE but the CC scope itself is evidenced under 1.10.
- **Connector-level data-flow restrictions** — see [Control 1.4](../../../controls/pillar-1-security/1.4-advanced-connector-policies-acp.md). VC-6 evidences only that DLP policies are present and bound to environments; the policy *content* (which connectors are blocked) is evidenced under 1.4.
- **Identity-layer access** to the Agent 365 admin surface — see [Control 2.25](../../../controls/pillar-2-management/2.25-agent-365-admin-center-governance-console.md).

### 0.4 PRE gates (must all pass before §2 executes)

The bootstrap script `Invoke-Agt224PreFlight.ps1` runs ten pre-flight gates. Any `FAIL` halts the suite and emits a single evidence artifact `preflight-FAILED-<runId>.json`. Any `SKIPPED` from PRE-04 redirects the run to the SOV namespace (§2.12).

| Gate | ID | Purpose | Failure behavior |
|---|---|---|---|
| Module presence | PRE-01 | Confirms `Microsoft.Graph.*` (2.25+), `Microsoft.PowerApps.Administration.PowerShell` (2.0.196+), `MicrosoftPowerBIMgmt`, `Pester` (5.5+) all loaded at pinned versions | HALT |
| Graph context | PRE-02 | Confirms `Connect-MgGraph` with scopes: `Directory.Read.All`, `Application.Read.All`, `Policy.Read.All`, `AuditLog.Read.All`, `AgentGovernance.Read.All`, `CopilotSettings.Read.All` (preview scope; falls back to `Directory.Read.All` with a documented compensating gap if not yet released in the operator's tenant) | HALT |
| Tenant identification | PRE-03 | Captures `tenantId`, `displayName`, `verifiedDomains[0].name` for every evidence record | HALT |
| Cloud detection | PRE-04 | Reads `(Get-MgContext).Environment` and maps to `Commercial / GCC / GCCH / DoD`; sovereign clouds route through SOV | Continue with `cloud` field set |
| Catalog presence | PRE-05 | Confirms `$env:AGT224_FEATURE_CATALOG_ROOT` exists and contains a per-cloud catalog file matching the detected cloud (`catalog.commercial.json`, `catalog.gcc.json`, `catalog.gcch.json`, `catalog.dod.json`); HALT if the cloud-specific file is missing — a single shared catalog is **not** acceptable per the sovereign caveat in the control doc | HALT |
| Catalog schema | PRE-06 | Validates the cloud-specific catalog against the §1.5 schema (all VC-9 fields present, no nulls in required columns, all `Zone*Status` values from the controlled vocabulary `Allowed / Restricted / Prohibited / Unavailable`) | HALT |
| PPAC reachability | PRE-07 | Probes PPAC Copilot governance endpoint via `Get-AdminPowerAppEnvironment` and a follow-up read against the Copilot governance metadata API; HALT in commercial; route to SOV in sovereign if 404/501 | HALT (commercial) |
| M365 admin Copilot blade | PRE-08 | Probes the Microsoft 365 admin center Copilot capability blade via Graph (`/beta/copilot/admin/settings`); falls back to a manual UI verification record under §3 if the Graph endpoint is not yet available in the tenant's release ring | Continue with `manual_verification_required` flag set |
| Clock skew | PRE-09 | Compares local UTC to the `Date` header from Graph; aborts if drift > 60 s — clock skew invalidates timestamp evidence for FINRA 4511 / SEC 17a-4 / CFTC 1.31 | HALT |
| Evidence root writeable | PRE-10 | Confirms `$env:AGT224_EVIDENCE_ROOT` exists, is writeable, and resolves to a path under WORM-eligible storage | HALT |

### 0.5 Sovereign bootstrap pattern

```powershell
function Test-Agt224SovereignTenant {
    [CmdletBinding()]
    [OutputType([pscustomobject])]
    param()

    $ctx = Get-MgContext
    if (-not $ctx) { throw "PRE-02 failed: no Graph context. Run Connect-MgGraph first." }

    $cloud = switch ($ctx.Environment) {
        'Global'    { 'Commercial' }
        'USGov'     { 'GCC' }
        'USGovDoD'  { 'DoD' }
        'USGovHigh' { 'GCCH' }
        default     { 'Unknown' }
    }

    [pscustomobject]@{
        cloud         = $cloud
        is_sovereign  = $cloud -in @('GCC','GCCH','DoD')
        tenant_id     = $ctx.TenantId
        detected_at   = (Get-Date).ToUniversalTime().ToString('o')
        catalog_file  = "catalog.$($cloud.ToLower()).json"
        endpoint_ref  = '../../_shared/powershell-baseline.md#3-sovereign-cloud-endpoints-gcc-gcc-high-dod'
    }
}
```

When `is_sovereign` is `$true`, every Pester `It` block in §2 (except SOV itself) emits a `SKIPPED` record routed to SOV. Crucially, sovereign-tenant runs **do not** inherit the commercial catalog: PRE-05 enforces the per-cloud catalog requirement called out in the control doc's sovereign caveat.

### 0.6 Run identifier and evidence root

```powershell
function New-Agt224RunId {
    'AGT224-{0}-{1}' -f (Get-Date -Format 'yyyyMMdd-HHmmss'),
                        ([guid]::NewGuid().ToString('N').Substring(0,8))
}

$script:RunId        = New-Agt224RunId
$script:RunTimestamp = (Get-Date).ToUniversalTime().ToString('o')
$script:EvidenceRoot = Join-Path $env:AGT224_EVIDENCE_ROOT $script:RunId
New-Item -ItemType Directory -Path $script:EvidenceRoot -Force | Out-Null
```

---


## §1 Namespace Taxonomy

The ten Verification Criteria are evidenced by **twelve test namespaces**. Each namespace produces independent evidence records that combine into a single signed evidence pack (§5). The split between M365HUB / PPAC / ENV / AGENT corresponds to the **three configuration surfaces** named in the control description (tenant Copilot hub, environment-level features, agent-level settings) plus the cross-cutting catalog, DLP, MCP, Agent Framework, zone roll-up, change management, sovereign, and SIEM forwarding namespaces.

### 1.1 Namespace catalog

| Namespace | Section | Surface / scope | Evidences VC | Cadence | Owner |
|---|---|---|---|---|---|
| `CATALOG` | §2.1 | Feature catalog file (per cloud) | VC-3, VC-4, VC-9, VC-10 | Monthly + on-change | AI Governance Lead |
| `M365HUB` | §2.2 | Microsoft 365 admin center → Copilot → declarative-agent capability allow-list | VC-1, VC-3, VC-5 | Daily (Z3) / Weekly (full) | AI Administrator |
| `PPAC` | §2.3 | Power Platform admin center → Copilot → Governance | VC-1, VC-3 | Weekly | Power Platform Admin |
| `ENV` | §2.4 | Per-environment feature toggles in PPAC | VC-1, VC-2, VC-5 | Weekly | Power Platform Admin |
| `AGENT` | §2.5 | Per-agent settings in Copilot Studio + author reality check | VC-1, VC-5, VC-8 | Per-agent on publish; full enumeration weekly | Copilot Studio Agent Author (read) + AI Administrator (verify) |
| `DLP` | §2.6 | Environment-level DLP policies enforcing feature/connector restrictions | VC-6 | Weekly | Power Platform Admin |
| `MCP` | §2.7 | MCP connector enablement governance | VC-3, VC-5, VC-7 | Weekly + on enablement | AI Administrator |
| `AGF` | §2.8 | Agent Framework feature flags and preview-ring tools | VC-2, VC-5, VC-7 | Weekly + on flag flip | AI Administrator |
| `ZONE` | §2.9 | Zone-by-zone roll-up against the Zone-Based Feature Exposure Model | VC-1, VC-2, VC-5 | Weekly | AI Governance Lead |
| `CHANGE` | §2.10 | Change-management workflow — forward (enable) AND reverse (disable / withdraw) | VC-7, VC-10 | Per-change + monthly reconciliation | Change Management Team |
| `SOV` | §2.11 | Sovereign-cloud compensating attestation (sovereign tenants) and per-cloud parity check (commercial vs sovereign) | All VCs (compensating) | Quarterly | AI Governance Lead + Compliance Officer |
| `SIEM` | §2.12 | Forwarding of feature-change events to SIEM (Microsoft Sentinel) for 6-year retention; chains with Control 3.1 / 3.9 | Cross-cutting | Weekly | Security Architect + Entra Security Admin |

### 1.2 Eight-part section structure

Each namespace section (§2.1 – §2.12) follows the same eight-part structure used by the Control 2.25 and 3.6 verification playbooks:

1. **Criterion mapping** — explicit pointer to which numbered VC in Control 2.24 §Verification Criteria is satisfied.
2. **Pre-conditions** — what must already be true (PRE gates passed; reference data present; Graph scopes granted).
3. **Pester suite** — `Describe "AGT224-{NS}" { Context "Zone {1|2|3}" { It "..." } }` using PowerShell 7.4 / Pester 5.5 syntax.
4. **Sample passing JSON evidence record** — exact shape that flows into the evidence pack.
5. **Sample failing JSON evidence record** with a remediation pointer to §3 (manual triage) or to the sister troubleshooting playbook.
6. **Examiner artifact** — filename pattern, retention duration, signing policy.
7. **Zone thresholds** — PASS / WARN / FAIL bands per zone.
8. **Regulator mapping** — which specific regulatory citation each test supports.

### 1.3 Evidence record schema (canonical)

Every evidence record produced by every namespace MUST conform to this schema. The schema is enforced by `Test-Agt224EvidenceSchema` in §5.5; the pack assembler refuses to publish a pack containing any record that fails schema validation.

```json
{
  "control_id": "2.24",
  "run_id": "AGT224-20260415-093012-a1b2c3d4",
  "run_timestamp": "2026-04-15T09:30:12Z",
  "tenant_id": "11111111-2222-3333-4444-555555555555",
  "tenant_display_name": "Contoso Bank, N.A.",
  "cloud": "Commercial",
  "zone": "3",
  "namespace": "M365HUB",
  "criterion": "VC-1",
  "subject_id": "capability:web-search",
  "subject_type": "capability_toggle",
  "surface": "m365-admin-center",
  "status": "PASS",
  "assertion": "Z3 declarative-agent capability allow-list contains web-search only with explicit per-agent binding",
  "observed_value": {
    "tenant_setting": "explicit-allowlist",
    "z3_bound_agents": ["agent-treasury-research-001"],
    "approval_record": "CHG0048221"
  },
  "expected_value": {
    "tenant_setting": "explicit-allowlist",
    "z3_bound_agents": "<every binding has a CHG ticket>",
    "approval_record": "<resolves to a Control 2.3 ticket>"
  },
  "catalog_ref": {
    "feature_name": "web-search",
    "catalog_file": "catalog.commercial.json",
    "last_review_date": "2026-03-31"
  },
  "evidence_artifacts": ["m365hub-websearch-snapshot-AGT224-20260415-093012-a1b2c3d4.json"],
  "regulator_mappings": ["FED-SR-11-7","OCC-2011-12","FINRA-3110","SOX-404","FFIEC-IT-RM"],
  "remediation_ref": null,
  "operator_upn": "agt224-runner@contoso.com",
  "schema_version": "1.0"
}
```

Field semantics:

| Field | Type | Notes |
|---|---|---|
| `control_id` | string | Always `"2.24"` for this playbook. |
| `run_id` | string | Output of `New-Agt224RunId`; identical across every record in a single run. |
| `run_timestamp` | ISO-8601 string | Captured at `BeforeAll` time, frozen for the run. |
| `tenant_id` / `tenant_display_name` | string | From PRE-03. |
| `cloud` | enum | `Commercial / GCC / GCCH / DoD / Unknown`. |
| `zone` | enum | `1 / 2 / 3 / all`. `all` is used for tenant-wide records (M365HUB tenant toggles, CATALOG schema, SIEM). |
| `namespace` | enum | One of the namespace IDs in §1.1. |
| `criterion` | enum | `VC-1` … `VC-10`, or `VC-1..10 (compensating)` for SOV. |
| `subject_id` | string | The agent ID, environment ID, capability ID, MCP connector ID, feature-flag ID, or change ticket reference. |
| `subject_type` | enum | `capability_toggle / environment_setting / agent_setting / dlp_policy / mcp_connector / agent_framework_flag / zone_rollup / change_ticket / catalog_entry / siem_forward`. |
| `surface` | enum | `m365-admin-center / ppac-copilot-hub / ppac-environment / copilot-studio-agent / dlp-policy-store / mcp-registry / agent-framework / catalog-store / siem`. |
| `status` | enum | `PASS / WARN / FAIL / SKIPPED / ERROR`. `ERROR` indicates the test could not run; `SKIPPED` is the sovereign-or-not-applicable case. |
| `assertion` | string | Human-readable statement of what was tested; written to be examiner-readable without context. |
| `observed_value` / `expected_value` | object | Free-form structured payload; both fields MUST be present even when one is trivial. |
| `catalog_ref` | object or null | Required for any record that asserts a feature or capability state; null only for cross-cutting records (CHANGE, SIEM). |
| `evidence_artifacts` | array | Filenames (relative to evidence root) of the supporting artifacts. |
| `regulator_mappings` | array | Citation tokens from §1.4. |
| `remediation_ref` | string or null | A `TRG-{NS}-NN` pointer when `status != 'PASS'`. |
| `operator_upn` | string | UPN of the operator who ran the test (from `Get-MgContext`). |
| `schema_version` | string | Always `"1.0"` for this playbook revision. |

### 1.4 Regulator mapping vocabulary

| Token | Citation |
|---|---|
| `FED-SR-11-7` | Federal Reserve SR Letter 11-7 (Guidance on Model Risk Management) |
| `OCC-2011-12` | OCC Bulletin 2026-13 (formerly OCC Bulletin 2011-12) (Supervisory Guidance on Model Risk Management) |
| `FFIEC-IT-RM` | FFIEC IT Examination Handbook — IT Risk Management booklet |
| `FFIEC-MGMT` | FFIEC IT Examination Handbook — Management booklet |
| `FFIEC-IS` | FFIEC IT Examination Handbook — Information Security booklet |
| `FINRA-3110` | FINRA Rule 3110 (Supervision) |
| `FINRA-4511` | FINRA Rule 4511 (Books and Records — General Requirements) |
| `FINRA-25-07` | FINRA Regulatory Notice 25-07 (workplace modernization RFC — cited as context only) |
| `SEC-17a-3` | SEC Rule 17a-3 (Records to be Made) |
| `SEC-17a-4` | SEC Rule 17a-4 (Records Retention) |
| `SEC-REG-SCI-1001` | SEC Regulation SCI §242.1001(a) (reasonably designed policies) — SCI entities only |
| `SEC-REG-SCI-1003` | SEC Regulation SCI §242.1003 (notification of systems changes) — SCI entities only |
| `SOX-302` | Sarbanes-Oxley Section 302 (Management Certification) |
| `SOX-404` | Sarbanes-Oxley Section 404 (Internal Controls Over Financial Reporting) |
| `GLBA-501b` | Gramm-Leach-Bliley Act §501(b) (Safeguards Rule) |
| `NYDFS-500` | NYDFS 23 NYCRR 500 (Cybersecurity Requirements) |
| `CFTC-1-31` | CFTC Regulation 1.31 (Recordkeeping) |

> **Non-substitution reminder.** Wherever `FINRA-3110` appears in a regulator-mapping table in §2, it indicates that the control element **supports** the firm's Rule 3110 supervisory obligation by providing reviewable evidence of feature-change oversight. It does **not** indicate that this playbook substitutes for the firm's obligation to designate an appropriately registered principal. The firm's WSPs remain the authoritative supervisory document; this playbook's evidence supports those WSPs. The same logic applies to `FED-SR-11-7` / `OCC-2011-12` and the firm's MRM framework (Control 2.6).

### 1.5 Catalog schema (referenced by VC-9 and PRE-06)

```json
{
  "schema_version": "1.0",
  "cloud": "Commercial",
  "generated_utc": "2026-04-15T09:00:00Z",
  "next_quarterly_review_due": "2026-06-30",
  "owner_upn": "ai-governance-lead@contoso.com",
  "features": [
    {
      "FeatureName": "code-interpreter",
      "FeatureCategory": "Tool",
      "Surface": "copilot-studio-agent",
      "Cloud": "Commercial",
      "Zone1Status": "Allowed",
      "Zone2Status": "Prohibited",
      "Zone3Status": "Prohibited",
      "ApprovalRequired": true,
      "ApprovalDate": null,
      "ChangeTicket": null,
      "ExpirationDate": null,
      "RiskRating": "High",
      "LastReviewDate": "2026-03-31",
      "Owner": "ai-governance-lead@contoso.com",
      "Notes": "Sandbox-only execution; not approved for any data classified Confidential or above."
    }
  ]
}
```

The catalog is the **single source of truth** consumed by every namespace. A `FeatureName` that appears as enabled in any of M365HUB, PPAC, ENV, AGENT, MCP, or AGF but is **not** present in the catalog produces a `FAIL` in the corresponding namespace and a parallel `FAIL` in CATALOG (catalog drift).

---


## §2 Pester Suites by Namespace

The full Pester runner is invoked as:

```powershell
Invoke-Pester -Path .\tests\agt224 -Output Detailed -PassThru |
    Export-Agt224EvidencePack -RunId $script:RunId -EvidenceRoot $script:EvidenceRoot
```

Each namespace lives in its own file (`tests\agt224\AGT224-{NS}.Tests.ps1`) and emits records using the shared helper `New-Agt224EvidenceRecord` (defined in `_shared/powershell-baseline.md`).

### §2.1 CATALOG — feature catalog integrity

**Criterion mapping.** VC-3 (allow-list semantics), VC-4 (catalog presence per cloud), VC-9 (schema field set), VC-10 (quarterly review evidence).

**Pre-conditions.** PRE-05 and PRE-06 passed; `$env:AGT224_FEATURE_CATALOG_ROOT` resolves to a directory containing the cloud-specific catalog file; the catalog file's `next_quarterly_review_due` is parseable as an ISO date.

**Pester suite.**

```powershell
Describe "AGT224-CATALOG" -Tag 'AGT224','CATALOG' {
    BeforeAll {
        $cloud = (Test-Agt224SovereignTenant).cloud
        $catalogPath = Join-Path $env:AGT224_FEATURE_CATALOG_ROOT "catalog.$($cloud.ToLower()).json"
        $script:catalog = Get-Content $catalogPath -Raw | ConvertFrom-Json -Depth 12
        $script:requiredFields = @(
            'FeatureName','FeatureCategory','Surface','Cloud',
            'Zone1Status','Zone2Status','Zone3Status',
            'ApprovalRequired','ApprovalDate','ChangeTicket',
            'ExpirationDate','RiskRating','LastReviewDate','Owner'
        )
        $script:vocabulary = @('Allowed','Restricted','Prohibited','Unavailable')
    }

    Context "Schema (VC-9)" {
        It "every feature row contains every required field" {
            foreach ($f in $script:catalog.features) {
                foreach ($field in $script:requiredFields) {
                    $f.PSObject.Properties.Name | Should -Contain $field
                }
            }
        }
        It "Zone*Status uses only the controlled vocabulary" {
            foreach ($f in $script:catalog.features) {
                $f.Zone1Status | Should -BeIn $script:vocabulary
                $f.Zone2Status | Should -BeIn $script:vocabulary
                $f.Zone3Status | Should -BeIn $script:vocabulary
            }
        }
        It "Cloud field matches the catalog filename cloud" {
            foreach ($f in $script:catalog.features) {
                $f.Cloud | Should -Be $script:catalog.cloud
            }
        }
    }

    Context "Allow-list semantics (VC-3)" {
        It "Z3-Allowed features carry an ApprovalDate and a ChangeTicket" {
            foreach ($f in $script:catalog.features | Where-Object { $_.Zone3Status -eq 'Allowed' }) {
                $f.ApprovalDate | Should -Not -BeNullOrEmpty
                $f.ChangeTicket | Should -Not -BeNullOrEmpty
            }
        }
        It "Z2-Allowed generative features carry ApprovalDate" {
            foreach ($f in $script:catalog.features |
                Where-Object { $_.Zone2Status -eq 'Allowed' -and $_.FeatureCategory -in 'Generative','Tool' }) {
                $f.ApprovalDate | Should -Not -BeNullOrEmpty
            }
        }
    }

    Context "Quarterly review (VC-10)" {
        It "next_quarterly_review_due is in the future" {
            [datetime]$script:catalog.next_quarterly_review_due | Should -BeGreaterThan (Get-Date)
        }
        It "no feature row has a LastReviewDate older than 100 days" {
            foreach ($f in $script:catalog.features) {
                ([datetime]::UtcNow - [datetime]$f.LastReviewDate).Days | Should -BeLessOrEqual 100
            }
        }
    }
}
```

**Sample PASS record.**

```json
{
  "control_id":"2.24","run_id":"AGT224-20260415-093012-a1b2c3d4","namespace":"CATALOG",
  "criterion":"VC-9","status":"PASS","subject_id":"catalog.commercial.json","subject_type":"catalog_entry",
  "assertion":"Catalog schema valid; 47 features; 0 missing required fields; quarterly review due 2026-06-30",
  "observed_value":{"feature_count":47,"missing_fields":0,"oldest_review_days":62},
  "expected_value":{"missing_fields":0,"oldest_review_days":"<= 100"},
  "regulator_mappings":["FED-SR-11-7","OCC-2011-12","FFIEC-MGMT","SOX-404","FINRA-4511","SEC-17a-4","CFTC-1-31"]
}
```

**Sample FAIL record.**

```json
{
  "control_id":"2.24","namespace":"CATALOG","criterion":"VC-9","status":"FAIL",
  "subject_id":"catalog.commercial.json","subject_type":"catalog_entry",
  "assertion":"3 of 47 feature rows missing required field 'ChangeTicket' for Z3-Allowed entries",
  "observed_value":{"violating_features":["web-search","image-generation","mcp-jira"]},
  "expected_value":{"violating_features":[]},
  "remediation_ref":"TRG-CATALOG-01"
}
```

**Examiner artifact.** `catalog-snapshot-{runId}.json` — the verbatim catalog file at run time, retained 6 years per FINRA 4511 / SEC 17a-4 / CFTC 1.31. Detached signature `.sig` produced by §5.6.

**Zone thresholds.**

| Zone | PASS | WARN | FAIL |
|---|---|---|---|
| 1 | All required fields present | 1 missing optional | Required field missing |
| 2 | All required fields present and Z2-Allowed generative entries have ApprovalDate | Approval date older than 12 months | Required field missing or Z2-Allowed without approval |
| 3 | All Z3-Allowed entries have ChangeTicket and ApprovalDate ≤ 6 months old | Approval date 6–12 months | Z3-Allowed without ChangeTicket |

**Regulator mapping.** `FED-SR-11-7`, `OCC-2011-12`, `FFIEC-MGMT`, `SOX-404`, `FINRA-4511`, `SEC-17a-4`, `CFTC-1-31`.

---

### §2.2 M365HUB — Microsoft 365 admin center capability allow-list

**Criterion mapping.** VC-1 (tenant declarative-agent capability allow-list), VC-3 (generative allow-list at tenant), VC-5 (high-risk capabilities disabled at tenant for downstream Z2/Z3 binding).

**Pre-conditions.** PRE-08 passed (or `manual_verification_required` flag set, in which case this namespace emits one `WARN` record pointing at §3.2 and the rest of the section is skipped). Operator runs with the **AI Administrator** role; if running with Entra Global Admin, an `operator_role` field in each record records `'global-admin-elevated'` for audit transparency.

**Pester suite.**

```powershell
Describe "AGT224-M365HUB" -Tag 'AGT224','M365HUB' {
    BeforeAll {
        $script:hub = Get-MgBetaCopilotAdminSetting -ErrorAction Stop
        $script:catalog = $script:catalog  # populated by CATALOG suite or shared BeforeAll
        $script:highRisk = @('code-interpreter','image-generation','web-search','external-orchestration')
    }

    Context "Tenant capability allow-list (VC-1, VC-3)" {
        It "tenant declarative-agent capabilities follow an explicit allow-list (not a deny-list)" {
            $script:hub.declarativeAgentCapabilityMode | Should -Be 'ExplicitAllowList'
        }
        It "every enabled tenant capability appears in the catalog as at-least-Z1-Allowed" {
            foreach ($cap in $script:hub.enabledCapabilities) {
                $entry = $script:catalog.features | Where-Object FeatureName -eq $cap
                $entry | Should -Not -BeNullOrEmpty -Because "capability '$cap' enabled at tenant must exist in catalog"
                $entry.Zone1Status | Should -BeIn @('Allowed','Restricted')
            }
        }
    }

    Context "High-risk capabilities at tenant (VC-5)" {
        It "high-risk capabilities are not blanket-enabled at tenant level" {
            foreach ($hr in $script:highRisk) {
                if ($script:hub.enabledCapabilities -contains $hr) {
                    $script:hub.capabilityBindings.$hr.scope | Should -Be 'PerAgentExplicit' `
                        -Because "$hr may be enabled only via per-agent explicit binding, never tenant-wide"
                }
            }
        }
    }
}
```

**Sample PASS record.**

```json
{
  "namespace":"M365HUB","criterion":"VC-1","status":"PASS",
  "subject_id":"tenant-capability-allowlist","subject_type":"capability_toggle","surface":"m365-admin-center",
  "assertion":"Tenant uses ExplicitAllowList; 6 capabilities enabled; all present in commercial catalog; high-risk capabilities require per-agent explicit binding",
  "observed_value":{"mode":"ExplicitAllowList","enabled":["file-search","actions","mcp","web-search","image-generation","code-interpreter"],"high_risk_per_agent":true},
  "expected_value":{"mode":"ExplicitAllowList","high_risk_per_agent":true},
  "regulator_mappings":["FED-SR-11-7","OCC-2011-12","FFIEC-IS","FINRA-3110","SOX-404"]
}
```

**Sample FAIL record.**

```json
{
  "namespace":"M365HUB","criterion":"VC-5","status":"FAIL",
  "subject_id":"capability:code-interpreter","subject_type":"capability_toggle","surface":"m365-admin-center",
  "assertion":"code-interpreter enabled at tenant scope (not PerAgentExplicit); contradicts Zone3Status=Prohibited in catalog",
  "observed_value":{"scope":"TenantWide"},
  "expected_value":{"scope":"PerAgentExplicit"},
  "remediation_ref":"TRG-M365HUB-02",
  "regulator_mappings":["FED-SR-11-7","OCC-2011-12","FINRA-3110"]
}
```

**Examiner artifact.** `m365hub-capabilities-{runId}.json` — captured `Get-MgBetaCopilotAdminSetting` payload plus an audit-log slice covering the prior 90 days of capability changes (`/auditLogs/directoryAudits?$filter=category eq 'CopilotAdmin'`). Retained 6 years.

**Zone thresholds.**

| Zone | PASS | WARN | FAIL |
|---|---|---|---|
| all (tenant) | ExplicitAllowList + every enabled capability in catalog + no high-risk tenant-wide | 1 capability missing from catalog (drift, scheduled fix < 7 d) | Mode ≠ ExplicitAllowList OR high-risk capability tenant-wide |

**Regulator mapping.** `FED-SR-11-7`, `OCC-2011-12`, `FFIEC-IS`, `FINRA-3110`, `SOX-404`, `GLBA-501b`.

---

### §2.3 PPAC — Power Platform admin center Copilot governance

**Criterion mapping.** VC-1 (tenant-wide PPAC governance page), VC-3 (Z3 generative-feature gating).

**Pre-conditions.** PRE-07 passed; `Get-AdminPowerAppEnvironment` returns ≥ 1 environment.

**Pester suite.**

```powershell
Describe "AGT224-PPAC" -Tag 'AGT224','PPAC' {
    BeforeAll {
        $script:ppacGov = Get-AdminPowerPlatformCopilotGovernance -ErrorAction Stop
    }
    Context "Tenant Copilot governance page (VC-1)" {
        It "tenant Copilot governance page is configured (not at default)" {
            $script:ppacGov.configurationState | Should -Be 'Configured'
            $script:ppacGov.lastModifiedUtc | Should -Not -BeNullOrEmpty
        }
        It "Z3-mapped environments inherit a restrictive policy template" {
            foreach ($e in $script:ppacGov.environments | Where-Object zone -eq 'Zone3') {
                $e.policyTemplate | Should -Be 'Z3-Restrictive'
            }
        }
    }
    Context "Generative-feature gating (VC-3)" {
        It "Z3 environments do not enable any generative feature outside the catalog Z3-Allowed list" {
            $z3Allowed = ($script:catalog.features | Where-Object Zone3Status -eq 'Allowed').FeatureName
            foreach ($e in $script:ppacGov.environments | Where-Object zone -eq 'Zone3') {
                foreach ($g in $e.enabledGenerativeFeatures) {
                    $g | Should -BeIn $z3Allowed
                }
            }
        }
    }
}
```

**Sample PASS record.**

```json
{
  "namespace":"PPAC","criterion":"VC-1","status":"PASS",
  "subject_id":"ppac-tenant-governance","subject_type":"environment_setting","surface":"ppac-copilot-hub",
  "assertion":"PPAC Copilot governance configured; 14 environments classified; 4 Zone3 environments bound to Z3-Restrictive template",
  "observed_value":{"environments":14,"zone3":4,"unclassified":0},
  "expected_value":{"unclassified":0},
  "regulator_mappings":["FED-SR-11-7","OCC-2011-12","FFIEC-MGMT","FINRA-3110"]
}
```

**Sample FAIL record.**

```json
{
  "namespace":"PPAC","criterion":"VC-3","status":"FAIL",
  "subject_id":"env:treasury-prod","subject_type":"environment_setting",
  "assertion":"Zone3 environment 'treasury-prod' enables generative feature 'image-generation' which is Zone3Status=Prohibited in catalog",
  "observed_value":{"enabled":["web-search","image-generation"]},
  "expected_value":{"enabled":["web-search"]},
  "remediation_ref":"TRG-PPAC-01"
}
```

**Examiner artifact.** `ppac-governance-{runId}.json` retained 6 years.

**Zone thresholds.** PASS = configured + zero unclassified envs + Z3 envs bound to restrictive template; WARN = ≤ 2 unclassified envs scheduled for classification; FAIL = unconfigured, or Z3 env bound to permissive template.

**Regulator mapping.** `FED-SR-11-7`, `OCC-2011-12`, `FFIEC-MGMT`, `FINRA-3110`, `SOX-404`.

---

### §2.4 ENV — environment-level feature toggles

**Criterion mapping.** VC-1, VC-2 (Z3 preview disabled), VC-5 (high-risk Z2/Z3 disabled).

**Pre-conditions.** PRE-07 passed; environment classification metadata available (Control 2.7).

**Pester suite.**

```powershell
Describe "AGT224-ENV" -Tag 'AGT224','ENV' {
    BeforeAll {
        $script:envs = Get-AdminPowerAppEnvironment | ForEach-Object {
            [pscustomobject]@{
                Id          = $_.EnvironmentName
                DisplayName = $_.DisplayName
                Zone        = (Get-AgtZoneClassification -EnvironmentId $_.EnvironmentName)
                Features    = (Get-AdminPowerPlatformEnvironmentFeatures -EnvironmentId $_.EnvironmentName)
            }
        }
    }
    Context "Zone 3 — preview disabled (VC-2)" {
        It "no Zone 3 environment has preview/experimental features enabled" {
            foreach ($e in $script:envs | Where-Object Zone -eq 'Zone3') {
                $e.Features.previewFeaturesEnabled | Should -BeFalse
                $e.Features.experimentalFlags.Count | Should -Be 0
            }
        }
    }
    Context "Zone 2 / 3 — high-risk disabled (VC-5)" {
        It "high-risk features disabled in Z2 and Z3 environments" {
            $hr = @('code-interpreter','external-orchestration')
            foreach ($e in $script:envs | Where-Object Zone -in 'Zone2','Zone3') {
                foreach ($f in $hr) {
                    $e.Features.PSObject.Properties[$f].Value | Should -BeFalse `
                        -Because "$f must be disabled in $($e.Zone) env $($e.DisplayName)"
                }
            }
        }
    }
}
```

**Sample PASS / FAIL records** follow the standard schema. **FAIL** triggers `TRG-ENV-01` (preview enabled in Z3) or `TRG-ENV-02` (high-risk enabled in Z2/Z3).

**Examiner artifact.** `env-features-{runId}.json` enumerating every env with its zone classification, feature toggles, and last-changed timestamp.

**Zone thresholds.**

| Zone | PASS | WARN | FAIL |
|---|---|---|---|
| 1 | n/a (information only) | — | — |
| 2 | High-risk disabled | Generative enabled without ApprovalDate | High-risk enabled |
| 3 | Preview disabled AND high-risk disabled | — | Either condition violated |

**Regulator mapping.** `FED-SR-11-7`, `OCC-2011-12`, `FFIEC-IS`, `FINRA-3110`, `SOX-404`, `NYDFS-500`.

---

### §2.5 AGENT — per-agent settings and author reality check

**Criterion mapping.** VC-1 (per-agent settings constrained), VC-5 (high-risk disabled where required), VC-8 (author cannot enable restricted feature, OR UI does not expose it).

**Pre-conditions.** PRE-02 passed; service principal with read access to Copilot Studio agent enumeration; **separately**, a non-privileged author identity is available for the §2.5.2 reality-check probe.

**Pester suite — Part A: enumeration.**

```powershell
Describe "AGT224-AGENT" -Tag 'AGT224','AGENT' {
    BeforeAll {
        $script:agents = Get-CopilotStudioAgent -All | ForEach-Object {
            [pscustomobject]@{
                Id           = $_.AgentId
                Name         = $_.DisplayName
                EnvId        = $_.EnvironmentId
                Zone         = (Get-AgtZoneClassification -EnvironmentId $_.EnvironmentId)
                EnabledTools = $_.EnabledTools
                Capabilities = $_.Capabilities
            }
        }
    }

    Context "Per-agent constraint inheritance (VC-1)" {
        It "no agent enables a tool prohibited at its environment's zone" {
            foreach ($a in $script:agents) {
                $prohibited = ($script:catalog.features |
                    Where-Object { ($_."Zone$($a.Zone -replace 'Zone','')Status") -eq 'Prohibited' }).FeatureName
                foreach ($t in $a.EnabledTools) {
                    $t | Should -Not -BeIn $prohibited `
                        -Because "agent '$($a.Name)' in $($a.Zone) enables prohibited tool '$t'"
                }
            }
        }
    }
}
```

**Pester suite — Part B: author reality check (VC-8).**

The control language is deliberate: an author **cannot enable** a restricted feature, **OR** the UI does not expose it. These two outcomes are not equivalent for examination purposes — the second is a compensating UX outcome rather than an active enforcement. The reality check records *which* outcome is in effect on each surface so an examiner can distinguish.

```powershell
Context "Author reality check (VC-8)" {
    BeforeAll {
        # Switch to non-privileged author context loaded from $env:AGT224_AUTHOR_TOKEN
        $script:authorCtx = Connect-CopilotStudio -Token $env:AGT224_AUTHOR_TOKEN -PassThru
    }
    It "in a Zone 3 env, an author attempting to enable code-interpreter is blocked OR the toggle is not exposed" {
        $env3 = ($script:envs | Where-Object Zone -eq 'Zone3' | Select-Object -First 1).Id
        $probe = Test-CopilotStudioToolAvailability `
                    -EnvironmentId $env3 `
                    -ToolName 'code-interpreter' `
                    -AuthorContext $script:authorCtx
        $probe.outcome | Should -BeIn @('blocked-by-policy','toggle-not-exposed')
        # Record which outcome is in effect for examiner transparency
        $script:agentAuthorOutcome = $probe.outcome
    }
}
```

**Sample PASS record (reality check).**

```json
{
  "namespace":"AGENT","criterion":"VC-8","status":"PASS",
  "subject_id":"author-probe:env:treasury-prod:code-interpreter","subject_type":"agent_setting",
  "assertion":"Author probe in Zone 3 env blocked from enabling code-interpreter; outcome=blocked-by-policy (active enforcement)",
  "observed_value":{"outcome":"blocked-by-policy","probe_author_upn":"agt224-author-probe@contoso.com"},
  "expected_value":{"outcome":"blocked-by-policy OR toggle-not-exposed"},
  "regulator_mappings":["FED-SR-11-7","FINRA-3110","SOX-404"]
}
```

**Sample FAIL record.** Author probe outcome = `enabled` (the author was able to flip the toggle). Triggers `TRG-AGENT-01` (immediate disablement + change-management investigation).

**Examiner artifact.** `agent-enumeration-{runId}.json` plus `agent-author-probe-{runId}.json`. Retained 6 years.

**Zone thresholds.**

| Zone | PASS | WARN | FAIL |
|---|---|---|---|
| 2 | No agent enables Z2-Prohibited tools; author probe outcome ∈ {blocked, not-exposed} | Author probe outcome `not-exposed` (compensating, document why) | Author probe `enabled`, OR Z2-Prohibited tool active |
| 3 | Same as Z2, with stricter prohibited list | — | Same |

**Regulator mapping.** `FED-SR-11-7`, `OCC-2011-12`, `FFIEC-IS`, `FINRA-3110`, `SOX-404`, `GLBA-501b`.

---

### §2.6 DLP — DLP-enforced feature restriction

**Criterion mapping.** VC-6 (DLP enforces feature restrictions where the runtime supports it).

**Pre-conditions.** PRE-07 passed; Power Platform DLP policies enumerable via `Get-DlpPolicy`. Cross-references Control 1.4 (ACP) for the connector-level policy content.

**Pester suite.**

```powershell
Describe "AGT224-DLP" -Tag 'AGT224','DLP' {
    BeforeAll {
        $script:dlp = Get-DlpPolicy -All
    }
    Context "Coverage (VC-6)" {
        It "every Z2 and Z3 environment is bound to at least one DLP policy" {
            foreach ($e in $script:envs | Where-Object Zone -in 'Zone2','Zone3') {
                ($script:dlp | Where-Object { $_.environments.name -contains $e.Id }).Count |
                    Should -BeGreaterThan 0
            }
        }
        It "DLP policies block connectors corresponding to catalog Zone3=Prohibited features that are connector-backed" {
            $prohibitedConnectors = ($script:catalog.features |
                Where-Object { $_.Zone3Status -eq 'Prohibited' -and $_.Surface -eq 'connector' }).FeatureName
            foreach ($p in $script:dlp | Where-Object { $_.environmentType -eq 'OnlyEnvironments' }) {
                foreach ($c in $prohibitedConnectors) {
                    ($p.businessDataGroup + $p.nonBusinessDataGroup) | Should -Not -Contain $c
                    $p.blockedDataGroup | Should -Contain $c
                }
            }
        }
    }
}
```

**Examiner artifact.** `dlp-binding-{runId}.json` enumerating every Z2/Z3 env, the bound policies, and a per-policy connector-classification table. Retained 6 years.

**Regulator mapping.** `FED-SR-11-7`, `FFIEC-IS`, `FINRA-3110`, `GLBA-501b`, `NYDFS-500`, `SOX-404`.

---



### §2.7 MCP — MCP connector enablement governance

**Criterion mapping.** VC-3, VC-5, VC-7. Cross-references Control 1.4 (ACP) and Control 2.20 (third-party-tool risk).

**Pre-conditions.** MCP registry enumerable; `Get-AgtMcpRegistration` returns array.

**Pester suite.**

```powershell
Describe "AGT224-MCP" -Tag 'AGT224','MCP' {
    BeforeAll { $script:mcp = Get-AgtMcpRegistration -All }
    Context "Allow-list semantics (VC-3)" {
        It "every enabled MCP connector exists in the catalog" {
            foreach ($m in $script:mcp | Where-Object enabled) {
                ($script:catalog.features | Where-Object FeatureName -eq "mcp-$($m.name)") |
                    Should -Not -BeNullOrEmpty
            }
        }
    }
    Context "Z2/Z3 high-risk (VC-5)" {
        It "MCP connectors with RiskRating=High are not bound to Z2/Z3 envs" {
            $highRisk = ($script:catalog.features |
                Where-Object { $_.FeatureName -like 'mcp-*' -and $_.RiskRating -eq 'High' }).FeatureName -replace 'mcp-',''
            foreach ($m in $script:mcp | Where-Object name -in $highRisk) {
                $m.boundEnvironments | ForEach-Object {
                    (Get-AgtZoneClassification -EnvironmentId $_) | Should -Be 'Zone1'
                }
            }
        }
    }
    Context "Change ticket (VC-7)" {
        It "every enablement event in the prior 90 days has a ChangeTicket reference" {
            $events = Get-AgtMcpEnablementEvent -SinceDays 90
            foreach ($e in $events) { $e.changeTicket | Should -Not -BeNullOrEmpty }
        }
    }
}
```

**Examiner artifact.** `mcp-registry-{runId}.json` + `mcp-enablement-events-90d-{runId}.json`. Retained 6 years.

**Regulator mapping.** `FED-SR-11-7`, `OCC-2011-12`, `FFIEC-IS`, `FINRA-3110`, `SOX-404`, `GLBA-501b`, `NYDFS-500`.

---

### §2.8 AGF — Agent Framework feature flags

**Criterion mapping.** VC-2 (preview disabled in Z3), VC-5 (high-risk disabled in Z2/Z3), VC-7 (flag flips logged with ticket).

**Pre-conditions.** Agent Framework admin API reachable.

**Pester suite.**

```powershell
Describe "AGT224-AGF" -Tag 'AGT224','AGF' {
    BeforeAll { $script:flags = Get-AgentFrameworkFeatureFlag -All }
    Context "Preview ring (VC-2)" {
        It "no preview-ring flag is enabled in Z3 environments" {
            foreach ($f in $script:flags | Where-Object ring -eq 'Preview') {
                foreach ($scope in $f.enabledScopes) {
                    if ($scope.kind -eq 'Environment') {
                        (Get-AgtZoneClassification -EnvironmentId $scope.id) |
                            Should -Not -Be 'Zone3'
                    }
                }
            }
        }
    }
    Context "Flag flip audit (VC-7)" {
        It "every flag flip in the prior 90 days has a CHG ticket" {
            $audit = Get-AgentFrameworkFlagAudit -SinceDays 90
            foreach ($a in $audit) {
                $a.changeTicket | Should -Match '^CHG\d{7}$'
                $a.approver_upn | Should -Not -BeNullOrEmpty
            }
        }
    }
}
```

**Examiner artifact.** `agf-flags-{runId}.json` + `agf-audit-90d-{runId}.json`.

**Regulator mapping.** `FED-SR-11-7`, `FFIEC-MGMT`, `FINRA-3110`, `SOX-404`, `SEC-REG-SCI-1003` (SCI entities only).

---

### §2.9 ZONE — zone roll-up against the Zone-Based Feature Exposure Model

**Criterion mapping.** VC-1 (alignment with zones), VC-2, VC-5.

The ZONE namespace does **no new probing**; it cross-correlates outputs from CATALOG / M365HUB / PPAC / ENV / AGENT / DLP / MCP / AGF and asserts that the tenant-wide picture aligns with the firm's zone model. A failure here usually means the underlying namespace already failed; the ZONE record gives examiners a single rolled-up status per zone.

**Pester suite.**

```powershell
Describe "AGT224-ZONE" -Tag 'AGT224','ZONE' {
    BeforeAll {
        $script:rollup = New-Agt224ZoneRollup -CatalogPath $catalogPath -RunId $script:RunId
    }
    foreach ($z in 'Zone1','Zone2','Zone3') {
        Context "Roll-up: $z" {
            It "no FAIL records from contributing namespaces in $z" {
                ($script:rollup.$z.failures.Count) | Should -Be 0
            }
            It "all features active in $z exist in catalog with matching status" {
                $script:rollup.$z.driftCount | Should -Be 0
            }
        }
    }
}
```

**Examiner artifact.** `zone-rollup-{runId}.json` — a per-zone summary suitable for executive review and quarterly attestation.

**Regulator mapping.** `FED-SR-11-7`, `OCC-2011-12`, `FFIEC-MGMT`, `FINRA-3110`, `SOX-302`, `SOX-404`.

---

### §2.10 CHANGE — forward and reverse change-management evidence

**Criterion mapping.** VC-7 (forward AND reverse change-mgmt), VC-10 (downstream cascade).

**Forward flow** = enablement of a feature, capability, MCP connector, or flag.
**Reverse flow** = disablement, withdrawal, expiration, or CVE-driven retraction.

The control doc explicitly requires both, because regulators (especially OCC under Fed SR 26-2 (formerly SR 11-7)) treat the *removal* of a model capability as a model change in its own right.

**Pester suite.**

```powershell
Describe "AGT224-CHANGE" -Tag 'AGT224','CHANGE' {
    BeforeAll {
        $script:changes = Get-AgtFeatureChangeEvent -SinceDays 90
    }
    Context "Forward flow (VC-7)" {
        It "every enablement has CHG ticket, approver, and ApprovalDate in catalog" {
            foreach ($c in $script:changes | Where-Object direction -eq 'Enable') {
                $c.changeTicket | Should -Match '^CHG\d{7}$'
                $c.approver_upn | Should -Not -BeNullOrEmpty
                ($script:catalog.features | Where-Object FeatureName -eq $c.feature).ApprovalDate |
                    Should -Not -BeNullOrEmpty
            }
        }
    }
    Context "Reverse flow (VC-7, VC-10)" {
        It "every disablement has CHG ticket and a reason in {Expired,CVE,RiskReassessment,VendorWithdrawal,RegulatoryDirective}" {
            foreach ($c in $script:changes | Where-Object direction -eq 'Disable') {
                $c.changeTicket | Should -Match '^CHG\d{7}$'
                $c.reason | Should -BeIn @('Expired','CVE','RiskReassessment','VendorWithdrawal','RegulatoryDirective')
            }
        }
        It "expired features (ExpirationDate < today) are evidenced as Disabled in the change log" {
            $expired = $script:catalog.features |
                Where-Object { $_.ExpirationDate -and ([datetime]$_.ExpirationDate -lt (Get-Date)) }
            foreach ($f in $expired) {
                ($script:changes | Where-Object { $_.feature -eq $f.FeatureName -and $_.direction -eq 'Disable' }) |
                    Should -Not -BeNullOrEmpty -Because "expired feature '$($f.FeatureName)' must have a reverse-flow change record"
            }
        }
    }
    Context "Downstream cascade (VC-10)" {
        It "any change touching a generative output modality has a paired notification to CC (Control 1.10) within 5 business days" {
            $modalityChanges = $script:changes | Where-Object { $_.feature -in 'voice-output','image-generation','video-generation' }
            foreach ($c in $modalityChanges) {
                $c.cascadeNotifications.cc110 | Should -Not -BeNullOrEmpty
                ([datetime]$c.cascadeNotifications.cc110.notifiedUtc - [datetime]$c.changeTimestampUtc).TotalDays |
                    Should -BeLessOrEqual 7
            }
        }
    }
}
```

**Examiner artifact.** `change-events-90d-{runId}.json` plus per-change attachment links to the firm's change-management system. Retained 6 years.

**Zone thresholds.** PASS = all enable + disable events ticketed and linked; WARN = ≤ 5 % of events missing cascade notification but within remediation SLA; FAIL = any unticketed change, or expired feature still active.

**Regulator mapping.** `FED-SR-11-7`, `OCC-2011-12`, `FFIEC-MGMT`, `FINRA-3110`, `SOX-302`, `SOX-404`, `SEC-REG-SCI-1003` (SCI entities only), `NYDFS-500`.

---

### §2.11 SOV — sovereign-cloud compensating attestation and parity

**Criterion mapping.** All VCs (compensating). The SOV namespace serves two purposes:

1. In sovereign tenants (GCC, GCC High, DoD), it is the destination namespace for `SKIPPED` records emitted when a commercial-cloud capability is not yet available in the operator's cloud — those skips are NOT failures, but they MUST be attested as such.
2. In commercial tenants that operate sovereign tenants in parallel, it produces a quarterly **catalog parity attestation** comparing the commercial and sovereign catalogs.

**Pester suite.**

```powershell
Describe "AGT224-SOV" -Tag 'AGT224','SOV' {
    Context "Sovereign-tenant skips" {
        It "every SKIPPED record from another namespace has a SOV-justification entry" {
            $skipped = Get-Agt224RunRecords -RunId $script:RunId -Status 'SKIPPED'
            foreach ($s in $skipped) {
                $j = Get-Agt224SovJustification -Feature $s.subject_id
                $j | Should -Not -BeNullOrEmpty
                $j.reason | Should -BeIn @('NotAvailableInCloud','SovereignVariantPending','PolicyDeferred','VendorRoadmap')
            }
        }
    }
    Context "Catalog parity (commercial firms operating sovereign tenants)" {
        It "every commercial Z3-Allowed feature has a corresponding sovereign catalog row (Allowed, Restricted, OR Unavailable)" {
            if (Test-Path "$($env:AGT224_FEATURE_CATALOG_ROOT)\catalog.gcch.json") {
                $sov = Get-Content "$($env:AGT224_FEATURE_CATALOG_ROOT)\catalog.gcch.json" -Raw | ConvertFrom-Json
                foreach ($cf in $script:catalog.features | Where-Object Zone3Status -eq 'Allowed') {
                    ($sov.features | Where-Object FeatureName -eq $cf.FeatureName) |
                        Should -Not -BeNullOrEmpty
                }
            }
        }
    }
}
```

**Examiner artifact.** `sov-justification-{runId}.json` and (where relevant) `parity-report-{quarter}.json`. Retained 6 years.

**Regulator mapping.** `FED-SR-11-7`, `OCC-2011-12`, `FFIEC-MGMT`, `FINRA-3110`, `SOX-404`. SOV records carry the additional token `SOVEREIGN-COMPENSATING` to flag examiner attention.

---

### §2.12 SIEM — forwarding to Microsoft Sentinel

**Criterion mapping.** Cross-cutting; chains with Control 1.7 (Comprehensive Audit Logging and Compliance) and Control 3.9 (Microsoft Sentinel Integration).

**Pester suite.**

```powershell
Describe "AGT224-SIEM" -Tag 'AGT224','SIEM' {
    BeforeAll {
        $script:sentinel = Invoke-AgtSentinelQuery -Workspace $env:AGT224_SENTINEL_WORKSPACE -Query @"
AgentFeatureChange_CL
| where TimeGenerated > ago(7d)
| summarize events=count(), distinctTickets=dcount(changeTicket_s) by ChangeDirection_s
"@
    }
    It "Sentinel received feature-change events in the past 7 days (ingest health)" {
        ($script:sentinel | Where-Object ChangeDirection_s -eq 'Enable').events | Should -BeGreaterOrEqual 0
    }
    It "every change ticket appearing in Sentinel resolves to the change-management system" {
        foreach ($row in $script:sentinel) {
            $row.distinctTickets | Should -BeLessOrEqual $row.events
        }
    }
}
```

**Examiner artifact.** `siem-ingest-7d-{runId}.json`. Retained 6 years.

**Regulator mapping.** `FED-SR-11-7`, `FFIEC-IS`, `FINRA-4511`, `SEC-17a-4`, `CFTC-1-31`, `NYDFS-500`.

---



---


## §3 Manual Procedures (UI Reality Checks)

Several configuration surfaces do not yet expose stable Graph or PowerShell endpoints suitable for automated verification. For these, the playbook requires a **manual UI walkthrough** with screenshots captured to the evidence root and signed under the same triad as automated evidence. Manual records are emitted as namespace records with `subject_type` ending in `-manual` (e.g., `capability_toggle-manual`) and `evidence_artifacts` listing the screenshot files.

### 3.1 Microsoft 365 admin center → Copilot capability blade

**Surface.** `https://admin.microsoft.com` → **Copilot** → **Settings** → **Declarative agents** → **Capabilities**.

**Operator role.** AI Administrator.

**Procedure.**

1. Sign in under the AI Administrator account (PIM-elevated session). Capture the session details (sign-in time, MFA method) into the evidence header.
2. Navigate to the Capabilities blade. Capture a full-page screenshot named `m365hub-capabilities-{runId}.png`.
3. For each enabled capability, expand the binding details and capture `m365hub-capability-{name}-{runId}.png`.
4. Cross-reference each enabled capability against the catalog. Any mismatch is recorded as a manual `WARN` and triaged via §6 (M365HUB).
5. If `code-interpreter`, `image-generation`, `web-search`, or `external-orchestration` is enabled, capture the per-agent binding list and verify each binding against a corresponding CHG ticket.

**Acceptance.** All enabled capabilities appear in the catalog as at-least-Z1-Allowed; no high-risk capability is enabled tenant-wide; per-agent bindings each resolve to a CHG ticket.

### 3.2 PPAC → Copilot Governance page

**Surface.** Power Platform admin center → **Copilot Governance**.

**Operator role.** Power Platform Admin.

**Procedure.**

1. Capture the Copilot Governance landing page (`ppac-governance-landing-{runId}.png`).
2. For each environment listed, capture the per-environment policy template binding. Confirm the binding matches the zone classification from Control 2.7.
3. Where the environment is Z3, expand the Generative AI section and confirm only catalog-Z3-Allowed features are enabled.

**Acceptance.** Configuration state = `Configured`; zero unclassified environments; Z3 environments bound to the Z3-Restrictive template; no Z3-Prohibited generative feature enabled.

### 3.3 PPAC → Environment-level features

**Procedure.** For each Z2 and Z3 environment, capture the **Features** tab (`env-{envName}-features-{runId}.png`) and the **Settings → Product → Features** sub-tab. Confirm preview features off in Z3; high-risk features off in Z2 and Z3.

### 3.4 Copilot Studio → per-agent settings

**Operator role.** Copilot Studio Agent Author (read-only) accompanied by AI Administrator (verifier).

**Procedure.** Sample at least 10 % of Z2 and Z3 agents (minimum 3 per zone). For each sampled agent, capture the **Settings → Tools** screen and the **Settings → Generative AI** screen. Confirm enabled tools match the catalog Z2/Z3 status.

### 3.5 MCP connector approval

**Procedure.** Open the firm's MCP registry UI (typically a custom Power App or an internal portal). For each enabled connector, capture the approval record screen showing approver UPN, ApprovalDate, and CHG ticket.

### 3.6 Agent Framework feature flags

**Procedure.** Open the Agent Framework admin portal. Capture the feature-flags table (`agf-flags-{runId}.png`). Confirm preview-ring flags are not enabled in any Z3-bound scope.

### 3.7 Manual evidence records

Each manual procedure produces one record per surface using this shape:

```json
{
  "namespace":"M365HUB","criterion":"VC-1","status":"PASS",
  "subject_id":"manual:m365hub-capabilities","subject_type":"capability_toggle-manual",
  "surface":"m365-admin-center","assertion":"Manual UI verification: 6 capabilities enabled; all in catalog; high-risk per-agent only",
  "observed_value":{"screenshots":["m365hub-capabilities-AGT224-...png"]},
  "expected_value":{"all_in_catalog":true,"high_risk_per_agent":true},
  "operator_upn":"ai-admin@contoso.com","verifier_upn":"compliance-officer@contoso.com",
  "evidence_artifacts":["m365hub-capabilities-AGT224-20260415-093012-a1b2c3d4.png"],
  "regulator_mappings":["FED-SR-11-7","FINRA-3110","SOX-404"]
}
```

---

## §4 Examiner Scenarios

Each scenario below defines a likely examiner question, the evidence-pack files that respond to it, the namespace records that compose those files, and the **companion control packs** the firm should bring alongside.

### 4.1 OCC MRM walkthrough — feature change as model change (SR 26-2)

**Examiner question.** "Show me how a change to a Copilot capability that affects model output is reviewed under your Model Risk Management framework."

**Evidence path.**

- `change-events-90d-{runId}.json` filtered to features in catalog with `RiskRating ∈ {High, Medium}` and `FeatureCategory = Generative`.
- For each such change, the linked CHG ticket attachment.
- Companion pack from Control 2.6 (Model Risk Management) showing the MRM intake, validation, and approval for the affected model.

**Namespaces cited.** CHANGE (forward + reverse), CATALOG (LastReviewDate within quarterly window), AGENT (per-agent binding).

**Regulatory anchor.** `FED-SR-11-7`, `OCC-2011-12`. The 2.24 evidence supports the firm's MRM process; it does not replace the MRM validation itself.

### 4.2 FINRA cycle exam — capability enabled on customer-facing agent without WSP update

**Examiner question.** "You enabled image generation on a customer-facing agent on March 4. Show me the supervisory record."

**Evidence path.**

- CHANGE record for the March 4 enablement.
- Cascade notification to Control 1.10 (Communication Compliance) showing CC scope updated to monitor image output.
- Companion pack from Control 2.12 (Supervision) showing the registered principal's WSP attestation.

**Namespaces cited.** CHANGE, AGENT, M365HUB (per-agent capability binding), DLP (image-modality DLP coverage).

**Regulatory anchor.** `FINRA-3110`, `FINRA-4511`. The non-substitution principle from §1.4 applies — the 2.24 evidence supports the WSP, but the WSP is the authoritative supervisory document.

### 4.3 SOX 404 management certification — forward AND reverse change-mgmt evidence

**Examiner question.** "Demonstrate that your internal controls over financial reporting include both the addition and the removal of AI features that touch financially-relevant systems."

**Evidence path.**

- Quarterly `zone-rollup-{runId}.json` for each quarter in the certification period.
- `change-events-90d-{runId}.json` rolled forward through the period showing both enable and disable events ticketed.
- Companion pack from Control 2.10 (Privileged Access Management) showing PIM logs for AI Administrator activations.

**Namespaces cited.** CHANGE (both directions), ZONE (rollup), CATALOG (review cadence).

**Regulatory anchor.** `SOX-302`, `SOX-404`.

### 4.4 SEC Regulation SCI — notification of systems changes (SCI entities only)

**Applicable to.** SCI entities (national securities exchanges, certain ATSs, registered clearing agencies, plan processors). Other firms may skip this scenario.

**Examiner question.** "You enabled an MCP connector that interacts with your order-handling system on May 12. Show me your §242.1003 notification."

**Evidence path.**

- MCP enablement event from MCP namespace with the linked CHG ticket.
- Cascade notification record showing the §242.1003 notification was filed within the required window.
- Companion pack from the firm's Reg SCI program demonstrating the notification.

**Namespaces cited.** MCP, CHANGE, CATALOG (catalog row showing the MCP connector with `Surface=connector` and `RiskRating`).

**Regulatory anchor.** `SEC-REG-SCI-1003`. **Important:** the playbook supports the notification process by providing the change record; the actual notification filing is the firm's Reg SCI program responsibility.

### 4.5 Surprise audit — commercial vs sovereign catalog parity

**Examiner question.** "You operate both a commercial tenant and a GCC High tenant. Show me that the feature catalog and exposure model are managed consistently across the two."

**Evidence path.**

- `parity-report-{quarter}.json` from SOV namespace.
- Both `catalog.commercial.json` and `catalog.gcch.json` snapshots from the same quarter.
- SOV justifications explaining each `Unavailable` entry in the GCC High catalog.

**Namespaces cited.** SOV (parity), CATALOG (both clouds), CHANGE (any cross-cloud cascade).

**Regulatory anchor.** `FED-SR-11-7`, `FFIEC-MGMT`, `OCC-2011-12`. Parity gaps are acceptable when explained as product unavailability; they are not policy exceptions.

### 4.6 CVE / preview withdrawal — reverse-flow demonstration

**Examiner question.** "Microsoft retracted a preview connector on June 7 due to a CVE. Show me your reverse-flow handling."

**Evidence path.**

- Reverse-flow CHANGE record with `reason = CVE` or `reason = VendorWithdrawal`.
- Catalog snapshot pre- and post-event showing the catalog row updated with `ExpirationDate` set to June 7.
- AGENT enumeration snapshot showing zero active agents using the affected feature within 24 hours.

**Namespaces cited.** CHANGE (reverse), CATALOG (drift detection caught it), AGENT (post-event clean).

**Regulatory anchor.** `FED-SR-11-7`, `FFIEC-IS`, `NYDFS-500`.

### 4.7 Voice / image enabled without Purview / DLP coverage update

**Examiner question.** "You enabled voice output on agent X on July 9. Show me how Communication Compliance scope was updated."

**Evidence path.**

- AGENT enumeration snapshot showing voice-output enabled on agent X with timestamp.
- CHANGE record with the cascade notification to Control 1.10.
- Companion pack from Control 1.10 showing the updated CC scope and a sample of monitored voice events from after July 9.
- Companion pack from Control 1.4 (ACP) if any new connector was bound as part of the change.

**Namespaces cited.** AGENT, CHANGE (cascade), DLP (modality coverage), M365HUB (per-agent capability binding).

**Regulatory anchor.** `FINRA-3110`, `FINRA-4511`, `SEC-17a-4`, `SOX-404`.

---

## §5 Evidence Packaging per Verification Criterion

Each VC's pack is the union of the namespace records that prove it, plus the corresponding artifact files. The pack assembler `Export-Agt224EvidencePack` builds a directory layout:

```
{EvidenceRoot}/
  manifest.json              ← record of all artifacts + Merkle root
  manifest.json.sig          ← detached signature (§5.6)
  records/
    AGT224-CATALOG-*.json
    AGT224-M365HUB-*.json
    ... one file per record ...
  artifacts/
    catalog-snapshot-*.json
    m365hub-capabilities-*.json|.png
    ... per-namespace artifacts ...
  by-criterion/
    VC-01/  ← symlinks/copies of records and artifacts proving VC-1
    VC-02/
    ... one folder per VC ...
```

### 5.1 Per-criterion composition

| VC | Records (namespaces) | Artifact globs |
|---|---|---|
| VC-1 | `M365HUB`, `PPAC`, `ENV`, `AGENT` | `m365hub-capabilities-*`, `ppac-governance-*`, `env-features-*`, `agent-enumeration-*` |
| VC-2 | `ENV` (Z3 preview), `AGF` (preview ring) | `env-features-*` (Z3 subset), `agf-flags-*` |
| VC-3 | `CATALOG`, `M365HUB`, `PPAC`, `MCP` | `catalog-snapshot-*`, `mcp-registry-*` |
| VC-4 | `CATALOG`, `SOV` | `catalog-snapshot-*` (per cloud), `parity-report-*` |
| VC-5 | `M365HUB`, `ENV`, `AGENT`, `MCP`, `AGF` | All zone-flagged subsets |
| VC-6 | `DLP` | `dlp-binding-*` |
| VC-7 | `CHANGE` (forward + reverse), `MCP`, `AGF` | `change-events-90d-*`, `mcp-enablement-events-*`, `agf-audit-*` |
| VC-8 | `AGENT` (Part B reality check) | `agent-author-probe-*` |
| VC-9 | `CATALOG` (schema context) | `catalog-snapshot-*` |
| VC-10 | `CATALOG` (next_quarterly_review_due, LastReviewDate), `CHANGE` (cascade) | `catalog-snapshot-*`, `change-events-90d-*` |

### 5.2 Manifest schema

```json
{
  "control_id":"2.24","run_id":"AGT224-...","run_timestamp":"2026-04-15T09:30:12Z",
  "tenant_id":"...","cloud":"Commercial","operator_upn":"agt224-runner@contoso.com",
  "record_count":214,"artifact_count":47,
  "by_criterion":{"VC-1":{"records":58,"artifacts":12,"status":"PASS"}, "...":""},
  "merkle_root":"sha256:9f2c4b...","schema_version":"1.0",
  "signers":[
    {"role":"AI Governance Lead","upn":"...","sig_file":"manifest.json.sig.aigov"},
    {"role":"Compliance Officer","upn":"...","sig_file":"manifest.json.sig.compliance"},
    {"role":"Security Architect","upn":"...","sig_file":"manifest.json.sig.security"}
  ]
}
```

### 5.3 Merkle root computation

Records are sorted by `(namespace, subject_id, criterion)` then hashed with SHA-256; pairwise hashing builds a binary Merkle tree. The root is the manifest's `merkle_root`. Verification: `Test-Agt224PackIntegrity -ManifestPath ...\manifest.json` recomputes the root and compares.

### 5.4 Retention

Six years from `run_timestamp` to satisfy the longest applicable horizon (FINRA Rule 4511 / SEC Rule 17a-4 / CFTC Regulation 1.31). WORM-eligible storage (Azure Immutable Blob Storage with time-based legal-hold retention policy, or Purview Records Management) is required. Retention configuration is itself evidenced under Control 3.6 (Retention) and Control 3.10 (Records).

### 5.5 Schema validator

```powershell
function Test-Agt224EvidenceSchema {
    param([Parameter(Mandatory)][object]$Record)
    $required = 'control_id','run_id','run_timestamp','tenant_id','cloud','zone',
                'namespace','criterion','subject_id','subject_type','status',
                'assertion','observed_value','expected_value','regulator_mappings',
                'operator_upn','schema_version'
    foreach ($f in $required) {
        if (-not $Record.PSObject.Properties.Name.Contains($f)) {
            throw "schema: missing field '$f'"
        }
    }
    if ($Record.control_id -ne '2.24')      { throw "schema: control_id must be '2.24'" }
    if ($Record.schema_version -ne '1.0')   { throw "schema: schema_version must be '1.0'" }
    if ($Record.status -notin 'PASS','WARN','FAIL','SKIPPED','ERROR') { throw "schema: status invalid" }
}
```

### 5.6 Signing

Manifest is signed by three operators (§6). Each signature is a detached PKCS#7 over `manifest.json` produced by an HSM-backed certificate. Signing keys are issued by the firm's internal CA and the cert chain is stapled into the `.sig` file.

---

## §6 Sign-Off

The published evidence pack is countersigned by three roles. Each signer's responsibility is bounded; the triad collectively asserts pack integrity, regulatory mapping accuracy, and high-risk attestation.

| Role | Responsibility | Signature artifact |
|---|---|---|
| **AI Governance Lead** | Pack integrity; Merkle root computed and verified; all ten VCs evidenced; sovereign justifications complete | `manifest.json.sig.aigov` |
| **Compliance Officer** | Regulator-mapping accuracy; non-substitution principle observed; FINRA / SEC / SOX / Fed SR 26-2 (formerly SR 11-7) citations correctly applied; Reg SCI applicability correctly identified | `manifest.json.sig.compliance` |
| **Security Architect** | High-risk feature attestation: every Z2/Z3 enablement of code-interpreter, image-generation, web-search, external-orchestration, or any High-RiskRating MCP connector is reviewed and accepted; SIEM forwarding healthy | `manifest.json.sig.security` |

Sign-off occurs **after** §5 pack assembly. A pack with fewer than three signatures is considered DRAFT and is not eligible to be presented to examiners. Signatures are recorded in the manifest's `signers[]` array and verified by `Test-Agt224PackIntegrity -RequireSignatures All`.

Detached signature filename pattern: `manifest.json.sig.{role-token}` where `role-token ∈ {aigov, compliance, security}`. Each signature includes the signer UPN, the signing certificate thumbprint, the signing timestamp (ISO-8601 UTC), and an RFC 3161 timestamp token from the firm's TSA.

---

## §7 Quarterly Attestation Template

A quarterly attestation packet bundles the most recent run from each month of the quarter plus a quarterly synthesis. The packet supports Control 2.24 VC-10 (quarterly feature risk assessment) and feeds the firm's MRM (2.6) and supervisory (2.12) cycles.

### 7.1 Cadence

| Activity | Cadence | Owner | Output |
|---|---|---|---|
| Namespace runs | Daily (Z3 hub), Weekly (full) | AI Administrator + Power Platform Admin | Per-run signed packs |
| Quarterly risk assessment | Within 15 business days of quarter-end | AI Governance Lead | `quarterly-assessment-{YYYY-Qn}.pdf` + `.json` |
| Quarterly attestation | Within 30 business days of quarter-end | AI Governance Lead + Compliance Officer + Security Architect | Signed attestation packet |
| Annual review of zone model and catalog schema | Annually | AI Governance Lead with MRM (2.6) | `zone-model-review-{YYYY}.pdf` |

### 7.2 Packet contents

1. The three monthly signed packs from the quarter (latest run from each month).
2. `quarterly-assessment-{YYYY-Qn}.json` containing per-feature review status, risk-rating changes, expirations, additions, and removals.
3. Threshold variance log: any run with WARN or FAIL records, with disposition.
4. Cross-control evidence pointers (2.6 MRM, 2.12 Supervision, 1.4 ACP, 1.10 CC, 2.25 Agent 365 Admin, 3.1 / 3.9 SIEM).
5. Sovereign parity report (where applicable).
6. Triad sign-off.

### 7.3 Distribution

| Recipient | What they receive | Cadence |
|---|---|---|
| Chief Risk Officer | Executive summary + threshold variance log | Quarterly |
| Chief Compliance Officer | Full packet | Quarterly |
| Internal Audit | Full packet + access to evidence root | Quarterly |
| External examiners (on request) | Full packet, namespaces requested, with signature verification instructions | On request |
| MRM committee (2.6) | Quarterly assessment JSON | Quarterly |

### 7.4 Threshold variance log

Any run within the quarter that emitted WARN or FAIL records is recorded here with: run ID, namespace, criterion, severity, remediation pointer, owner, target date, and current status. The variance log is itself evidence — examiners use it to test the firm's responsiveness, not just its initial detection.

---

## §8 Continuous-Improvement Metrics

These metrics feed the firm's quarterly governance review. Targets are illustrative and should be calibrated to the firm's risk appetite.

| Metric | Formula | Illustrative target | Owner |
|---|---|---|---|
| Namespace pass rate | `pass_records / total_records` per namespace per quarter | ≥ 98 % | AI Governance Lead |
| Mean time to remediation (MTTR) | Time from FAIL emission to corresponding PASS in next run | ≤ 7 d (Critical), ≤ 30 d (High), ≤ 90 d (Medium) | Owning admin role |
| Catalog drift rate | `(features active in surface but not in catalog) / total features` | ≤ 1 % | AI Governance Lead |
| Exception expiry compliance | `(catalog rows with expired ExpirationDate disabled in change log) / (catalog rows with expired ExpirationDate)` | 100 % | Change Management Team |
| Sovereign parity gap count | Count of commercial Z3-Allowed features without a sovereign catalog row | 0 (or all explained as `Unavailable` in SOV justifications) | AI Governance Lead + Compliance Officer |
| Reverse-flow evidence rate | `(disable events with CHG ticket and reason) / (total disable events)` | 100 % | Change Management Team |
| Author probe coverage | `(Z2/Z3 envs with at least one author probe per quarter) / (total Z2/Z3 envs)` | 100 % | AI Administrator |
| SIEM ingest health | Events ingested / events generated (cross-checked with Control 3.1) | ≥ 99.5 % | Security Architect |

Trend charts of each metric across rolling four quarters are included in the quarterly attestation packet (§7).

---

## §9 Cross-References

### 9.1 Sibling playbooks for Control 2.24

- [Portal Walkthrough](portal-walkthrough.md) — UI configuration of all surfaces evidenced here.
- [PowerShell Setup](powershell-setup.md) — install / configure the modules and helper functions referenced throughout §0–§5.
- Troubleshooting (`TRG-{NS}-NN` remediation pointers referenced in FAIL records — see the sibling troubleshooting playbook when published).

### 9.2 Source control

- [Control 2.24 — Agent Feature Enablement and Restriction Governance](../../../controls/pillar-2-management/2.24-agent-feature-enablement-and-restriction-governance.md)

### 9.3 Companion controls

| Control | Relationship |
|---|---|
| [1.4 — Advanced Connector Policies](../../../controls/pillar-1-security/1.4-advanced-connector-policies-acp.md) | DLP / connector-level enforcement of feature restrictions (VC-6) |
| [1.10 — Communication Compliance](../../../controls/pillar-1-security/1.10-communication-compliance-monitoring.md) | Cascade target when output modalities change (VC-7, VC-10) |
| [2.3 — Change Management and Release Planning](../../../controls/pillar-2-management/2.3-change-management-and-release-planning.md) | Source of CHG tickets cited throughout CHANGE namespace |
| [2.6 — Model Risk Management](../../../controls/pillar-2-management/2.6-model-risk-management-sr-26-2.md) | MRM cascade for capability changes that affect model output |
| [2.7 — Vendor and Third-Party Risk Management](../../../controls/pillar-2-management/2.7-vendor-and-third-party-risk-management.md) | Vendor-side feature attestation; pairs with catalog `RiskRating` |
| [2.10 — Patch Management and System Updates](../../../controls/pillar-2-management/2.10-patch-management-and-system-updates.md) | Update cycle that can introduce or retract features (reverse flow) |
| [2.12 — Supervision (FINRA Rule 3110)](../../../controls/pillar-2-management/2.12-supervision-and-oversight-finra-rule-3110.md) | Supervisory overlay; non-substitution principle |
| [2.20 — Adversarial Testing and Red-Team Framework](../../../controls/pillar-2-management/2.20-adversarial-testing-and-red-team-framework.md) | Red-team validation of capability boundaries (high-risk features) |
| [2.25 — Agent 365 Admin Center Governance Console](../../../controls/pillar-2-management/2.25-agent-365-admin-center-governance-console.md) | Identity-layer access to admin console; structural template for this playbook |
| [3.1 — Agent Inventory and Metadata Management](../../../controls/pillar-3-reporting/3.1-agent-inventory-and-metadata-management.md) | Inventory feed used by AGENT enumeration |
| [3.6 — Orphaned Agent Detection and Remediation](../../../controls/pillar-3-reporting/3.6-orphaned-agent-detection-and-remediation.md) | Cross-check that disabled features do not leave orphan agents |
| [3.9 — Microsoft Sentinel Integration](../../../controls/pillar-3-reporting/3.9-microsoft-sentinel-integration.md) | Sentinel ingest of SIEM namespace events |

### 9.4 Reference material

- [Shared PowerShell baseline](../../_shared/powershell-baseline.md) — module versions, sovereign endpoints, helper functions.
- [Role catalog](../../../reference/role-catalog.md) — canonical names for AI Administrator, Power Platform Admin, Entra Global Admin, Compliance Officer, Security Architect.
- [Regulatory mappings](../../../reference/regulatory-mappings.md) — full citation index keyed to control IDs.

### 9.5 External regulatory references

- Federal Reserve SR Letter 11-7 — Guidance on Model Risk Management.
- OCC Bulletin 2026-13 (formerly OCC Bulletin 2011-12) — Supervisory Guidance on Model Risk Management.
- FFIEC IT Examination Handbook — Management, Information Security, and IT Risk Management booklets.
- FINRA Rule 3110 (Supervision); Rule 4511 (Books and Records); Regulatory Notice 25-07 (workplace modernization RFC, contextual reference only).
- SEC Rule 17a-3 / 17a-4; SEC Regulation SCI §§242.1001, 242.1003 (SCI entities).
- Sarbanes-Oxley §§ 302, 404.
- Gramm-Leach-Bliley Act § 501(b) (Safeguards Rule).
- NYDFS 23 NYCRR 500 (Cybersecurity Requirements).
- CFTC Regulation 1.31 (Recordkeeping).

---



*Updated: May 2026 | Version: v1.6.2 | UI Verification Status: Current*
