# Verification & Testing — Control 2.25: Microsoft Agent 365 Admin Center Governance Console

**Last Verified:** 2026-11-09 (live Microsoft documentation review; no tenant or UI execution).

**Execution boundary:** this is a manual evidence-verification playbook, not a shipped Pester harness. The previous suites depended on undefined `Get-Agent365*` functions and undocumented Graph contracts. The companion PowerShell adapters stop with `ManualEvidenceRequired`; that outcome blocks acceptance and is not `Clean`, `NotApplicable`, or proof of an empty tenant. The JSON below defines illustrative firm evidence records, not Microsoft API response schemas or actual passing results. Implement and independently validate any evidence assembler, signer, schema validator, or automation adapter before relying on its output.

> **Examiner-defensible evidence package** for Control 2.25. This playbook produces, signs, and retains the artifacts required to demonstrate to FINRA, SEC, OCC, FFIEC, NYDFS, and internal audit that every Microsoft 365 AI agent surfaced through the Microsoft Agent 365 Admin Center is licensed, admin-approved, owned, governance-template-bound, exception-monitored, inventory-exported, and (for the Researcher with Computer Use capability) configured per documented zone policy.
>
> **Scope:** US commercial-cloud Microsoft 365. Microsoft Agent 365 is available as a standalone subscription for eligible Microsoft 365 subscriptions and is included in Microsoft 365 E7. Copilot is not a universal prerequisite for standalone Agent 365. At least one user must have a qualifying Agent 365 license assigned to enable Agent 365. Basic registry and governance capabilities also exist in Microsoft 365 plans; verify entitlement separately for policy templates, observability, and package API access. Microsoft Agent 365 reached general availability on **May 1, 2026**.
>
> **Companion controls:** [1.2 Agent Registry & Integrated Apps Management](../../../controls/pillar-1-security/1.2-agent-registry-and-integrated-apps-management.md) feeds the OWNER and INVENTORY namespaces. [2.26 Entra Agent ID Identity Governance](../../../controls/pillar-2-management/2.26-entra-agent-id-identity-governance.md) provides the identity-layer prerequisite that 2.25 governance templates rely on for Zone 3 access-package binding. [3.9 Microsoft Sentinel Integration](../../../controls/pillar-3-reporting/3.9-microsoft-sentinel-integration.md) consumes the SIEM forwarding namespace. [3.6 Orphaned Agent Detection & Remediation](../../../controls/pillar-3-reporting/3.6-orphaned-agent-detection-and-remediation.md) consumes the OWNER namespace outputs.
>
> **Last UI verified:** Not established by this review. The previous April 2026 "post-GA" build claim was inconsistent with the May 1, 2026 GA date and is withdrawn. Capture dated tenant evidence before operational sign-off.
>
> **Important regulatory framing.** This playbook **supports compliance with**, but does not by itself confirm compliance with, FINRA Rules 3110 (Supervision) and 4511 (Books and Records), FINRA RN 24-09 / Rule 3110 (AI Tools), SEC Rules 17a-3 / 17a-4 (Recordkeeping), SOX Sections 302 / 404 (Internal Controls), GLBA Section 501(b) (Safeguards Rule), OCC Bulletin 2026-13 (formerly OCC Bulletin 2011-12) (Technology Risk Management), NYDFS 23 NYCRR 500 (Cybersecurity), and the FFIEC IT Examination Handbook. Where FINRA Rule 3110 obligates the firm to assign a registered principal to a supervisory function, the Agent 365 governance console **does not substitute for** that registered-principal designation; it produces the evidentiary trail that supports — but does not replace — the firm's written supervisory procedures (WSPs).

---

## Document Conventions

### Microsoft documentation verification ledger

The following technical corrections apply to the control, its implementation guides, and all evidence acceptance below. Regulatory mappings, retention obligations, and firm approval policy are unchanged.

| Claim checked | Verified product contract and evidence consequence | Primary Microsoft source |
|---|---|---|
| Availability and licensing | GA May 1, 2026; standalone Agent 365 with eligible Microsoft 365 subscriptions or included in E7. At least one qualifying user assignment enables Agent 365. Purchased SKU capacity alone does not establish assignment. Do not infer entitlement from guessed SKU prefixes. | [Overview](https://learn.microsoft.com/en-us/microsoft-agent-365/overview), [service description](https://learn.microsoft.com/en-us/office365/servicedescriptions/microsoft-agent-365/microsoft-agent-365) |
| Roles | AI Administrator and Entra Global Admin manage agents; AI Reader and Entra Global Reader can view registry and insights. AI Governance Lead is a firm responsibility, not an Entra role. AI Administrator alone cannot configure Conditional Access or Entra access-package policies. | [Roles and permissions](https://learn.microsoft.com/en-us/microsoft-agent-365/admin/agent-roles-perms), [activation policies](https://learn.microsoft.com/en-us/microsoft-agent-365/admin/agent-actions#activate-agents) |
| Navigation and request queue | Use **Agents > Overview** and **Agents > All agents > Registry / Requests**. Pending Requests shows three requests, newest first; it is not an oldest-first SLA report. Review the full Requests list and actual request dates. | [Agent management](https://learn.microsoft.com/en-us/microsoft-agent-365/admin/agent-365-overview), [requests](https://learn.microsoft.com/en-us/microsoft-agent-365/admin/agent-requests) |
| Metrics and exceptions | Overview hero metrics are Agent registry, Active users, Agent run-time, and Registry sync. Agents with exceptions is an actionable count/view. A derived rate is **100 × sessions with errors / sessions** from supported per-agent Activity data for the same period; higher is worse, zero sessions means no rate. It is not a governance-template variance rate or a native Overview percentage. | [Overview metrics](https://learn.microsoft.com/en-us/microsoft-agent-365/admin/agent-365-overview#agent-card-details), [agent activity](https://learn.microsoft.com/en-us/microsoft-agent-365/admin/agent-details#agent-activity) |
| Registry coverage and export | Registry visibility depends on supported platform integrations; draft visibility currently covers Copilot Studio only. Learn describes CSV export and an Excel export with **All agents / Filtered agents** scope. Inspect the actual format, headers, filters, and source coverage. Approval attribution, zone, and template fields are firm evidence requirements, not guaranteed export columns. | [Registry](https://learn.microsoft.com/en-us/microsoft-agent-365/admin/agent-registry-overview) |
| Graph and SDK | The documented package route is `/v1.0/copilot/admin/catalog/packages` (also documented in beta), with `CopilotPackages.Read.All` and Agent 365 licensing. Follow every opaque `@odata.nextLink`. Pending requests can be filtered with `requestStatus eq 'pending'`; `lastModifiedDateTime` is **not** the submission date. No cited source establishes `/beta/agentGovernance`, `/beta/admin/agent365`, `AgentGovernance.Read.All`, or the old helper names as Microsoft contracts. | [List packages](https://learn.microsoft.com/en-us/microsoft-365-copilot/extensibility/api/admin-settings/package/copilotpackages-list), [registry API overview](https://learn.microsoft.com/en-us/microsoft-agent-365/admin/graph-api) |
| Templates | Default template policies now include Entra network visibility, SharePoint content permissions insights, Purview Know your data, and Defender capabilities as well as identity, lifecycle, access, and audit policies. These are not exclusively custom additions. License assignment is documented during activation. Capture actual template and downstream policy state; a template name is not proof of enforcement. | [Lifecycle actions and default template policies](https://learn.microsoft.com/en-us/microsoft-agent-365/admin/agent-actions) |
| Settings and suggestions | Security templates are under **Agents > Settings > Security templates**. Agent management rules have feature-specific scope; applying a template by rule is a one-time bulk action, not scheduled enforcement. No dedicated agent-suggestions policy or its availability date was established; keep that claim unresolved rather than infer GA or unavailability. | [Agent settings](https://learn.microsoft.com/en-us/microsoft-agent-365/admin/agent-settings) |
| Lifecycle and updates | Install/Uninstall, Block/Unblock, and Delete/Restore/Permanently delete have distinct effects. Delete is soft deletion with a 30-day recovery window; permanent deletion is separate. Blocking Foundry or SharePoint agents affects Copilot Chat availability, not all source-platform execution. Pending updates leave the previous version accessible until approval. | [Agent actions](https://learn.microsoft.com/en-us/microsoft-agent-365/admin/agent-actions), [pending updates](https://learn.microsoft.com/en-us/microsoft-agent-365/admin/agent-requests#requested-agents-pending-update) |
| Agent instances | Current documentation describes AI teammate instances with their own Entra identity, license, mailbox, OneDrive, and Teams presence. Historical May 1 preview references are not current feature-availability evidence and do not determine the firm's autonomy policy. | [Agent instances](https://learn.microsoft.com/en-us/microsoft-agent-365/admin/agent-details#agent-instances) |
| Researcher Computer Use | Use the admin **Agents > Researcher > Computer use** configuration. Capture all/specific/no-user scope, admin work-data access, and website policy. Even when admins enable work access, users must manually enable Work. The configuration source does not establish an October 2025 GA date, universal default-on, or a Graph policy endpoint; these claims are withdrawn. Test the tenant's available capability rather than assume availability. | [Researcher configuration](https://learn.microsoft.com/en-us/copilot/manage/researcher-agent-computer-use), [agent details](https://learn.microsoft.com/en-us/microsoft-agent-365/admin/agent-details#computer-use) |
| SIEM retention and schema | These namespace/category names are firm evidence labels, not guaranteed native audit events. Validate source events, ingestion, and retrieval. Log Analytics analytics retention is at most 730 days; multi-year retention uses table total/long-term retention or separately retained exports, not a six-year workspace analytics setting. | [Log Analytics retention](https://learn.microsoft.com/en-us/azure/azure-monitor/logs/data-retention-configure) |

**Unknowns requiring tenant evidence:** rollout-specific UI labels, actual license identifiers and assignments, per-platform inventory completeness, template enforcement, API response coverage, Researcher availability, and SIEM event mapping. No screenshots were captured and no tenant configuration was changed in this review.

| Convention | Value |
|---|---|
| PowerShell baseline | PowerShell 7.4+ Core; `#Requires -Version 7.4` at the top of every executable script. |
| Test framework | Manual checks below. Pester 5.5+ is an optional firm harness choice, not a delivered implementation. |
| Output discipline | No `Write-Host`. All evidence emitted as structured `[pscustomobject]` instances via `Write-Output`, then serialized with `ConvertTo-Json -Depth 8` to evidence files. |
| Evidence retention | Six (6) years on WORM-protected storage for the full signed evidence pack — aligning to FINRA Rule 4511 / SEC Rule 17a-4(f). The 3-year minimum applies only to non-supervisory administrative artifacts the firm has documented as out-of-scope of supervisory recordkeeping. |
| Hashing | SHA-256 over canonical JSON; chained leaf hashes plus a Merkle root in `attestation.json` (see §10.4). |
| Run identifier | Every test run is tagged `AGT225-yyyyMMdd-HHmmss-<8charGuid>` and embedded in every evidence record and artifact filename. |
| Canonical role names | Per [`docs/reference/role-catalog.md`](../../../reference/role-catalog.md). **AI Administrator** and **Entra Global Admin** can manage agents; **AI Reader** and **Entra Global Reader** provide read-only verification access. |

> This playbook **helps meet** recordkeeping, supervision, change-management, access-management, and oversight expectations under the regulations enumerated above. It is one component of a defensible AI governance program; it does not replace a registered-principal designation, written supervisory procedures, model risk management practices required by Fed SR 26-2 (formerly SR 11-7) / OCC Bulletin 2026-13 (formerly OCC 2011-12), or the firm's own legal review.

---

## §0 Pre-Test Prerequisites

### 0.1 Operator role prerequisites

Use documented product roles for the surface under review and separately assigned firm responsibilities for approval/sign-off. Apply the firm's PIM policy to privileged access. Read-only assertions in §2–§9 are separated from write actions; these manual verification procedures **do not perform remediation**. The previously named `Set-Agent365TemplateBulk` and `Invoke-Agent365PendingApprovalDrain` functions are not supplied implementations. Follow the supported portal procedure under an approved change ticket; companion mutation adapters stop with `ManualEvidenceRequired`.

| Role (canonical) | Required for | PIM activation window |
|---|---|---|
| Entra Global Admin | Privileged tenant administration or emergency remediation when required; do not make this role a prerequisite for all read-only verification | 2 hours, JIT, with ticketed justification |
| AI Administrator | Day-to-day Agents administration: pending requests (§3), ownership (§4), templates (§5), inventory (§6), activity evidence (§7), and Researcher settings (§8). Read-only operations only in this playbook; verify Billing and separate service permissions independently. | 4 hours, JIT |
| AI Reader / Entra Global Reader | Evidence-only registry and insights access; use documented roles for each additional evidence source | Per firm policy |
| Purview Compliance Admin | Purview-side evidence for template policy bindings (§5) and audit forwarding (§9); confirm the actual Audit and retention permissions required for the selected operation separately | 4 hours |
| Power Platform Admin | Read access to Microsoft Copilot Studio environment governance metadata for agents that surface in Agent 365 from Copilot Studio (cross-referenced in §6) | 2 hours |
| AI Governance Lead | Firm responsibility, not an Entra built-in role: counter-signs the quarterly attestation packet in §13; reviews governance evidence; signs the evidence pack in §10 | Standing assignment with quarterly recertification per Control 2.8 |
| Compliance Officer | Counter-signs the quarterly attestation packet in §13 and signs Zone 3 governance template variances | Standing |
| Information Security Officer | Reviews exception-rate threshold variances; reviews Researcher with Computer Use Zone 3 configurations | Standing |
| Technology Risk Manager | Receives the §10 evidence pack and integrates it into the firm's technology-risk reporting per OCC Bulletin 2026-13 (formerly OCC 2011-12) | Standing |
| Change Management Lead | Reconciles Agent 365 approval timestamps with change tickets per Control 2.3 (verified in §3) | Standing |

> **Least privilege.** No operator should hold **Entra Global Admin** persistently. Day-to-day verification work in §2–§9 is performed under **AI Administrator** with **Entra Global Reader** as the witness role. **Entra Global Admin** is reserved for tenant enrollment, licensing changes, and emergency remediation, and is operated under PIM with JIT activation.

### 0.2 Module baseline

The module list below is a historical firm harness example, not a Microsoft minimum or a validated Agent 365 module distribution. Manual portal verification does not require these modules. Validate each SDK operation and pin only the modules your approved implementation uses.

```powershell
#Requires -Version 7.4
#Requires -Modules @{ ModuleName='Microsoft.Graph.Authentication';        ModuleVersion='2.25.0' }
#Requires -Modules @{ ModuleName='Microsoft.Graph.Identity.DirectoryManagement'; ModuleVersion='2.25.0' }
#Requires -Modules @{ ModuleName='Microsoft.Graph.Users';                 ModuleVersion='2.25.0' }
#Requires -Modules @{ ModuleName='Microsoft.Graph.Beta.Applications';     ModuleVersion='2.25.0' }
#Requires -Modules @{ ModuleName='Microsoft.Graph.Beta.DeviceManagement'; ModuleVersion='2.25.0' }
#Requires -Modules @{ ModuleName='MicrosoftTeams';                        ModuleVersion='6.5.0'  }
#Requires -Modules @{ ModuleName='Pester';                                ModuleVersion='5.5.0'  }

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'
$ProgressPreference    = 'SilentlyContinue'
```

> **Graph boundary:** use the documented package API and `CopilotPackages.Read.All` described in the ledger. The old `Get-Agent365*` names are neither Microsoft cmdlets nor implemented wrappers in the companion guide. There is no verified unified governance API or SDK module behind those names. Use manual evidence for fields and policies not supplied by an independently validated adapter.

### 0.3 PRE gates (must all pass before §2–§9 execute)

The operator records these seven pre-flight gates. `Invoke-Agt225PreFlight.ps1` is not supplied by this repository. A failed or unverified gate blocks acceptance; retain the gate results as `preflight-FAILED-<runId>.json` using the firm's approved evidence process.

| Gate | ID | Purpose | Failure behavior |
|---|---|---|---|
| Module presence | PRE-01 | For optional automation only, confirms approved modules and documented operation contracts; manual review records this dependency as not used | HALT |
| Graph context | PRE-02 | For optional package collection, confirms documented `CopilotPackages.Read.All`, role, tenant, and entitlement; grant other scopes only for their documented feature-specific operations | HALT |
| Tenant identification | PRE-03 | Captures `tenantId`, `displayName`, `verifiedDomains[0].name` for every evidence record | HALT |
| License gate | PRE-04 | Confirms the feature's actual eligible subscription and assigned qualifying Agent 365 user entitlement; do not use guessed SKU-prefix matching | HALT — required feature entitlement or assignment not evidenced |
| Agent 365 admin blade reachability | PRE-05 | Opens Agents > Overview and All agents > Registry under the intended role; optional API tests are recorded separately | If the required surface is inaccessible or unverified: HALT |
| Clock skew gate | PRE-06 | Verifies capture-system UTC against the firm's trusted clock; the 60-second tolerance is firm policy, not a documented Agent 365 API guarantee | HALT — clock skew invalidates timestamp evidence for FINRA 4511 / SEC 17a-4 |
| Evidence root writeable | PRE-07 | Confirms `$env:AGT225_EVIDENCE_ROOT` exists, is writeable, and resolves to a path under WORM-eligible storage (validated by checking the parent storage account's immutability policy where applicable) | HALT |

### 0.4 Run identifier and evidence root

```powershell
function New-Agt225RunId {
    $ts   = (Get-Date).ToUniversalTime().ToString('yyyyMMdd-HHmmss')
    $guid = ([guid]::NewGuid().ToString('N')).Substring(0,8)
    "AGT225-$ts-$guid"
}

$script:RunId        = New-Agt225RunId
$script:RunTimestamp = (Get-Date).ToUniversalTime().ToString('o')
$script:EvidenceRoot = Join-Path $env:AGT225_EVIDENCE_ROOT $script:RunId
New-Item -Path $script:EvidenceRoot -ItemType Directory -Force | Out-Null
```

Every evidence record produced in §2–§9 is written under `$script:EvidenceRoot` and the `runId` is embedded in the filename of every artifact assembled into the §10 evidence pack.

---

## §1 Namespace Catalog

The eight Verification Criteria from [Control 2.25](../../../controls/pillar-2-management/2.25-agent-365-admin-center-governance-console.md) (the "VCs") are evidenced by eight test namespaces. Each namespace produces independent evidence records that combine into a single signed evidence pack (§10). The eight namespaces include the cross-cutting SIEM evidence check; APPROVAL covers VC-2 and VC-4.

| Namespace | Section | Evidences VC | Cadence | Owner |
|---|---|---|---|---|
| `LICENSE` | §2 | VC-1 — Agent 365 / M365 E7 license coverage and Agents blade visibility | Monthly | AI Administrator |
| `APPROVAL` | §3 | VC-2 (admin approval workflow enforced) **and** VC-4 (pending requests resolved within firm-defined SLA) | Daily (Z3) / Weekly (Z2) | AI Governance Lead |
| `OWNER` | §4 | VC-5 — Ownerless Agents card shows zero or actively remediated | Daily | AI Governance Lead |
| `TEMPLATE` | §5 | VC-3 — Governance template assigned (Default for Z2; Custom-with-Access-Package for Z3) | Weekly | AI Administrator |
| `INVENTORY` | §6 | VC-7 — Monthly inventory exported and retained on WORM with required field set | Monthly | AI Governance Lead |
| `EXCEPTION` | §7 | VC-6 — Exception rate monitored against documented threshold | Weekly | Information Security Officer |
| `RESEARCHER` | §8 | VC-8 — Researcher with Computer Use configured per zone with affirmative decision | Quarterly + on-change | Information Security Officer |
| `SIEM` | §9 | Cross-cutting — Agent 365 governance events forwarded to SIEM with 6-year retention; chains with Control 3.1 | Weekly | Entra Security Admin |

Each namespace section follows an identical 8-part structure, mirroring the sister [Control 2.26 verification playbook](../2.26/verification-testing.md):

1. **Criterion mapping** — explicit pointer to which numbered VC in Control 2.25 §Verification Criteria is satisfied.
2. **Pre-conditions** — what must already be true (PRE gates passed; reference data present; Graph scopes granted).
3. **Manual verification procedure** — collect current source evidence, reconcile firm policy, and record unresolved dependencies before assigning a result.
4. **Sample passing JSON evidence record** — exact shape that flows into the evidence pack.
5. **Sample failing JSON evidence record** with a remediation pointer to §11.
6. **Examiner artifact** — filename pattern, retention duration, signing policy.
7. **Zone thresholds** — PASS / WARN / FAIL bands per zone.
8. **Regulator mapping** — which specific regulatory citation each test supports.

### 1.1 Evidence record schema (canonical)

Every evidence record produced by every namespace MUST conform to this schema. The firm's implemented validator must enforce this schema before signing. Neither Test-Agt225EvidenceSchema nor a validated pack assembler is supplied; see §10.5.

```json
{
  "control_id": "2.25",
  "run_id": "AGT225-20260415-093012-a1b2c3d4",
  "run_timestamp": "2026-04-15T09:30:12Z",
  "tenant_id": "11111111-2222-3333-4444-555555555555",
  "tenant_display_name": "Contoso Bank, N.A.",
  "cloud": "Commercial",
  "zone": "2",
  "namespace": "APPROVAL",
  "criterion": "VC-2",
  "subject_id": "agent-payments-summarizer-001",
  "subject_type": "agent",
  "status": "PASS",
  "assertion": "Z2 agent has non-null approver UPN and approvalTimestamp",
  "observed_value": {
    "approver_upn": "ai.administrator@contoso.com",
    "approval_timestamp": "2026-04-12T14:00:11Z",
    "change_ticket_id": "CHG0042311"
  },
  "expected_value": {
    "approver_upn": "<non-null>",
    "approval_timestamp": "<non-null>",
    "change_ticket_id": "<resolves to a Control 2.3 ticket>"
  },
  "evidence_artifacts": ["approval-snapshot-AGT225-20260415-093012-a1b2c3d4.json"],
  "regulator_mappings": ["FINRA-3110","FINRA-25-07","SOX-404","OCC-2011-12"],
  "remediation_ref": null,
  "operator_upn": "agt225-runner@contoso.com",
  "schema_version": "1.0"
}
```

Field semantics:

| Field | Type | Notes |
|---|---|---|
| `control_id` | string | Always `"2.25"` for this playbook. |
| `run_id` | string | Output of `New-Agt225RunId`; identical across every record in a single run. |
| `run_timestamp` | ISO-8601 string | Captured when the manual verification run starts, frozen for the run. |
| `tenant_id` / `tenant_display_name` | string | From PRE-03. |
| `cloud` | enum | `Commercial / Unknown`. |
| `zone` | enum | `1 / 2 / 3 / all`. `all` is used for tenant-wide records (e.g., LICENSE, SIEM). |
| `namespace` | enum | One of the namespace IDs in §1. |
| `criterion` | enum | `VC-1` … `VC-8`, or `VC-1..8 (cross-cutting)` for SIEM. |
| `subject_id` | string | The agent ID, template ID, policy ID, or other Graph object ID. |
| `subject_type` | enum | `agent / pending_approval / governance_template / inventory_export / exception_metric / researcher_policy / diagnostic_setting`. |
| `status` | enum | `PASS / WARN / FAIL / SKIPPED / ERROR`. `ERROR` indicates the test could not run; `SKIPPED` is the not-applicable case. |
| `assertion` | string | Human-readable statement of what was tested; written to be examiner-readable without context. |
| `observed_value` / `expected_value` | object | Free-form structured payload; both fields MUST be present even when one is trivial. |
| `evidence_artifacts` | array | Filenames (relative to evidence root) of the supporting artifacts. |
| `regulator_mappings` | array | Citation tokens from the controlled vocabulary in §1.2. |
| `remediation_ref` | string or null | A `TRG-{NS}-NN` pointer into §11 when `status != 'PASS'`. |
| `operator_upn` | string | Verified operator identity from the evidence source; `Get-MgContext` is relevant only when optional Graph collection is used. |
| `schema_version` | string | Always `"1.0"` for this playbook revision. |

### 1.2 Regulator mapping vocabulary

| Token | Citation |
|---|---|
| `FINRA-3110` | FINRA Rule 3110 (Supervision) |
| `FINRA-4511` | FINRA Rule 4511 (Books and Records — General Requirements) |
| `FINRA-25-07` | FINRA RN 24-09 / Rule 3110 (AI Tools) |
| `SEC-17a-3` | SEC Rule 17a-3 (Records to be Made) |
| `SEC-17a-4` | SEC Rule 17a-4 (Records Retention) |
| `SOX-302` | Sarbanes-Oxley Section 302 (Management Certification) |
| `SOX-404` | Sarbanes-Oxley Section 404 (Internal Controls) |
| `GLBA-501b` | Gramm-Leach-Bliley Act §501(b) (Safeguards Rule) |
| `OCC-2011-12` | OCC Bulletin 2026-13 (formerly OCC Bulletin 2011-12) (Technology Risk Management) |
| `NYDFS-500` | NYDFS 23 NYCRR 500 (Cybersecurity Requirements) |
| `FFIEC-IS` | FFIEC IT Examination Handbook — Information Security booklet |
| `FFIEC-MGMT` | FFIEC IT Examination Handbook — Management booklet |

> **No FINRA Rule 3110 substitution.** Wherever `FINRA-3110` appears in a regulator-mapping table in §2–§10, it indicates that the control element in question **supports** the firm's Rule 3110 supervisory obligation by providing reviewable evidence of admin oversight. It does **not** indicate that the Agent 365 governance console substitutes for the firm's obligation to designate an appropriately registered principal where Rule 3110 requires that designation. The firm's WSPs remain the authoritative supervisory document; this playbook's evidence supports those WSPs.

---

## §2 LICENSE Namespace — VC-1

### 2.1 Criterion mapping

This namespace evidences **VC-1: Agent 365 licensing confirmed**. The test asserts that the tenant under examination holds a license entitlement that surfaces the Microsoft Agent 365 Admin Center governance console and its Agents blade — with the required feature-specific entitlements and at least one qualifying Agent 365 user assignment for Agent 365 enablement. Basic registry/governance access may exist through eligible Microsoft 365 plans without Agent 365-only features. Verify each criterion's entitlement separately.

### 2.2 Pre-conditions

- PRE-01 through PRE-07 passed or explicitly recorded as unused optional automation dependencies (§0.3).
- The operator has **AI Administrator** activated via PIM with a justification that references this playbook ID.
- Optional SDK collection uses independently validated operations and approved module pins; manual portal review does not require the historical module baseline.
- The firm's License Catalog reference data (`license-catalog.json`, maintained by the Identity Engineering team per Control 2.4) is available at `$env:AGT225_LICENSE_CATALOG`. This file enumerates the SKU partnumbers the firm has procured and is the source of truth for whether a SKU is "current" or "deprecated".

### 2.3 Manual verification procedure

1. Open **Billing > Licenses** and record the actual product identifiers, purchased capacity, enabled service plans, and assigned users. Confirm at least one qualifying Agent 365 user assignment for Agent 365 enablement; distinguish basic Microsoft 365 registry access from Agent 365-only features.
2. Record the eligible Microsoft 365 base subscription and the entitlement for each feature under test. Do not require a separate Copilot SKU solely because standalone Agent 365 is used.
3. Open **Agents > Overview** and **Agents > All agents > Registry** under the intended role. Capture tenant ID, operator role, timestamp, and errors. API reachability is a separate test, not proof of portal access.
4. Compare the observed identifiers with the firm's current, approved license catalog. Missing assignment evidence is `ERROR`/`ManualEvidenceRequired`, not PASS.

Use the [licensing sources in the ledger](#microsoft-documentation-verification-ledger). Raw SKU counts alone do not prove this criterion.

### 2.4 Sample passing evidence record

```json
{
  "control_id": "2.25",
  "run_id": "AGT225-20260415-093012-a1b2c3d4",
  "run_timestamp": "2026-04-15T09:30:12Z",
  "tenant_id": "11111111-2222-3333-4444-555555555555",
  "tenant_display_name": "Contoso Bank, N.A.",
  "cloud": "Commercial",
  "zone": "all",
  "namespace": "LICENSE",
  "criterion": "VC-1",
  "subject_id": "tenant-license-posture",
  "subject_type": "inventory_export",
  "status": "PASS",
  "assertion": "Tenant holds at least one Agent 365-eligible SKU with Enabled > 0",
  "observed_value": { "qualifying_user_assignment_verified": true },
  "expected_value": { "qualifying_user_assignment_verified": true },
  "evidence_artifacts": ["license-skus-AGT225-20260415-093012-a1b2c3d4.json"],
  "regulator_mappings": ["FINRA-4511","SEC-17a-4","SOX-404","OCC-2011-12"],
  "remediation_ref": null,
  "operator_upn": "agt225-runner@contoso.com",
  "schema_version": "1.0"
}
```

### 2.5 Sample failing evidence record

```json
{
  "control_id": "2.25",
  "run_id": "AGT225-20260415-093012-a1b2c3d4",
  "run_timestamp": "2026-04-15T09:30:12Z",
  "tenant_id": "11111111-2222-3333-4444-555555555555",
  "tenant_display_name": "Contoso Bank, N.A.",
  "cloud": "Commercial",
  "zone": "all",
  "namespace": "LICENSE",
  "criterion": "VC-1",
  "subject_id": "tenant-agent365-assignment",
  "subject_type": "inventory_export",
  "status": "FAIL",
  "assertion": "A qualifying Agent 365 user assignment is evidenced",
  "observed_value": { "qualifying_user_assignment_verified": false },
  "expected_value": { "qualifying_user_assignment_verified": true },
  "evidence_artifacts": ["license-skus-AGT225-20260415-093012-a1b2c3d4.json"],
  "regulator_mappings": ["FINRA-25-07","OCC-2011-12"],
  "remediation_ref": "TRG-LICENSE-02",
  "operator_upn": "agt225-runner@contoso.com",
  "schema_version": "1.0"
}
```

### 2.6 Examiner artifact

| Property | Value |
|---|---|
| Filename pattern | `license-skus-<runId>.json` and `license-evidence-<runId>.ndjson` |
| Storage | `$env:AGT225_EVIDENCE_ROOT/<runId>/license/` |
| Retention | 6 years on WORM (FINRA 4511 / SEC 17a-4(f)) |
| Signing | Bundled into the §10 evidence pack and signed at the pack level by AI Governance Lead |
| Distribution | AI Governance Lead, Compliance Officer, Technology Risk Manager |

### 2.7 Zone thresholds

| Zone | PASS | WARN | FAIL |
|---|---|---|---|
| Z1 (Personal) | All four manual checks evidenced | Catalog currency check WARNs | Required feature entitlement or qualifying user assignment missing |
| Z2 (Team) | All four manual checks evidenced | Catalog currency WARN | Same as Z1 — license absence blocks all downstream |
| Z3 (Enterprise) | All four manual checks evidenced, plus license has been re-attested in the trailing 90 days | Re-attestation > 90 days but < 180 days | Required feature entitlement/assignment absent OR re-attestation > 180 days |

### 2.8 Regulator mapping

| Test | FINRA-3110 | FINRA-4511 | FINRA-25-07 | SEC-17a-4 | SOX-404 | GLBA-501b | OCC-2011-12 | NYDFS-500 | FFIEC-MGMT |
|---|---|---|---|---|---|---|---|---|---|
| Eligible SKU present | — | ✓ | ✓ | ✓ | ✓ | — | ✓ | — | ✓ |
| Qualifying user assignment evidenced | — | — | ✓ | — | — | — | ✓ | — | ✓ |
| Blade reachable | ✓ | — | ✓ | — | — | — | ✓ | — | ✓ |
| Catalog currency | — | — | — | — | ✓ | — | ✓ | — | ✓ |

---

## §3 APPROVAL Namespace — VC-2 + VC-4

### 3.1 Criterion mapping

This namespace evidences **two** Verification Criteria simultaneously because they share the same data source (the Agent 365 admin approval queue) and the same review cadence:

- **VC-2: Admin approval workflow enforced.** Quarterly sample of N ≥ 10 production agents shows non-null `approverUpn` and `approvalTimestamp`, and each approval traces to a Control 2.3 change ticket.
- **VC-4: Pending requests resolved within firm SLA.** Pending publish/activate requests visible in the Agent 365 admin queue are resolved within the firm's documented SLA — illustratively 5 business days for Z2 and 1 business day for Z3 (the firm sets these in policy; this playbook reads `$env:AGT225_SLA_Z2_BD` and `$env:AGT225_SLA_Z3_BD`).

> **Firm SLA values are illustrative.** The 5 BD / 1 BD values shown here are placeholders. The firm's AI Governance Council sets the production SLA values, documents them in policy, and re-affirms them annually. Manual review uses the firm's approved values; environment-variable names below are optional harness inputs, not evidence that a harness is implemented.

### 3.2 Pre-conditions

- PRE gates passed.
- AI Administrator activated.
- Reference data: `$env:AGT225_CHANGE_TICKET_RESOLVER` is the URL of the firm's change-ticket lookup API (per Control 2.3), used by `Resolve-Agt225ChangeTicket` to validate ticket IDs returned by the Agent 365 API.
- Reference data: `$env:AGT225_APPROVAL_SAMPLE_N` (default 10) — sample size for VC-2.
- Reference data: `$env:AGT225_SLA_Z2_BD` (default 5) and `$env:AGT225_SLA_Z3_BD` (default 1) — pending-request SLA in business days.

### 3.3 Manual verification procedure

1. Open **Agents > All agents > Requests**. Review all relevant request states (Pending review, Pending update, Pending activate), not only the three newest requests shown on Overview.
2. Capture actual request dates, request type, agent identifier, disposition, reviewer, and the firm's zone classification. Compute age against the firm's business calendar and configured SLA.
3. Reconcile approval samples with retained approval evidence and Control 2.3 tickets. Approver, approval date, and change-ticket ID may need approved manual records; they are not guaranteed registry export fields.
4. For an approved test change in a non-production tenant, capture before/after request and availability state. Verify pending updates leave the previous version accessible before approval.
5. If using the documented package request filters, follow all pages. Do not substitute package `lastModifiedDateTime` for request submission or approval time. Unavailable attribution or queue coverage blocks acceptance.

The [requests documentation](https://learn.microsoft.com/en-us/microsoft-agent-365/admin/agent-requests) is the portal contract; the firm's signed approval log supplies any missing evidence.

### 3.4 Sample passing evidence (VC-2)

```json
{
  "control_id": "2.25",
  "run_id": "AGT225-20260415-093012-a1b2c3d4",
  "run_timestamp": "2026-04-15T09:30:12Z",
  "tenant_id": "11111111-2222-3333-4444-555555555555",
  "tenant_display_name": "Contoso Bank, N.A.",
  "cloud": "Commercial",
  "zone": "3",
  "namespace": "APPROVAL",
  "criterion": "VC-2",
  "subject_id": "approval-sample-z3",
  "subject_type": "pending_approval",
  "status": "PASS",
  "assertion": "Z3 approval sample (n=10) has non-null approverUpn",
  "observed_value": { "sample_size": 10, "null_approver_count": 0, "null_approver_ids": [] },
  "expected_value": { "null_approver_count": 0 },
  "evidence_artifacts": [
    "approval-sample-z3-AGT225-20260415-093012-a1b2c3d4.json",
    "approval-sample-z3-changetickets-AGT225-20260415-093012-a1b2c3d4.json"
  ],
  "regulator_mappings": ["FINRA-3110","FINRA-4511","SEC-17a-3","SOX-404","OCC-2011-12"],
  "remediation_ref": null,
  "operator_upn": "agt225-runner@contoso.com",
  "schema_version": "1.0"
}
```

### 3.5 Sample failing evidence (VC-4)

```json
{
  "control_id": "2.25",
  "run_id": "AGT225-20260415-093012-a1b2c3d4",
  "run_timestamp": "2026-04-15T09:30:12Z",
  "tenant_id": "11111111-2222-3333-4444-555555555555",
  "tenant_display_name": "Contoso Bank, N.A.",
  "cloud": "Commercial",
  "zone": "3",
  "namespace": "APPROVAL",
  "criterion": "VC-4",
  "subject_id": "pending-sla-z3",
  "subject_type": "pending_approval",
  "status": "FAIL",
  "assertion": "No Z3 pending request older than 1 business day(s)",
  "observed_value": {
    "breach_count": 2,
    "breach_ids": ["pa-2026-0411-007","pa-2026-0411-014"],
    "cutoff_utc": "2026-04-14T09:30:12Z"
  },
  "expected_value": { "breach_count": 0, "sla_business_days": 1 },
  "evidence_artifacts": ["pending-z3-AGT225-20260415-093012-a1b2c3d4.json"],
  "regulator_mappings": ["FINRA-3110","FINRA-25-07","OCC-2011-12","NYDFS-500","FFIEC-MGMT"],
  "remediation_ref": "TRG-APPROVAL-05",
  "operator_upn": "agt225-runner@contoso.com",
  "schema_version": "1.0"
}
```

### 3.6 Examiner artifact

| Property | Value |
|---|---|
| Filename pattern | `approval-sample-z{2,3}-<runId>.json`, `pending-z{2,3}-<runId>.json`, `approval-evidence-<runId>.ndjson`, `change-ticket-resolutions-<runId>.json` |
| Storage | `$env:AGT225_EVIDENCE_ROOT/<runId>/approval/` |
| Retention | 6 years on WORM |
| Signing | Pack-level signature; the change-ticket resolution sub-artifact is dual-signed by AI Governance Lead and Change Management Lead |
| Distribution | AI Governance Lead, Compliance Officer, Change Management Lead, Technology Risk Manager |

### 3.7 Zone thresholds

| Zone | PASS | WARN | FAIL |
|---|---|---|---|
| Z1 | N/A — Z1 is not admin-gated; the namespace emits `SKIPPED` with `assertion='Z1 not in scope for admin approval'` | — | — |
| Z2 | All sampled agents have non-null approver + timestamp + valid ticket; no pending request > 5 BD | One sample item has a stale ticket (Open/InProgress) | Any null approver, null timestamp, or pending > 5 BD |
| Z3 | All sampled have approver + timestamp + valid ticket; no pending request > 1 BD | One sample with stale ticket | Any null approver, null timestamp, or pending > 1 BD |

### 3.8 Regulator mapping

| Test | FINRA-3110 | FINRA-4511 | FINRA-25-07 | SEC-17a-3 | SEC-17a-4 | SOX-302 | SOX-404 | GLBA-501b | OCC-2011-12 | NYDFS-500 | FFIEC-MGMT |
|---|---|---|---|---|---|---|---|---|---|---|---|
| Non-null approver | ✓ | ✓ | ✓ | ✓ | — | — | ✓ | — | ✓ | — | ✓ |
| Timestamp present | ✓ | ✓ | — | — | ✓ | ✓ | ✓ | — | ✓ | — | — |
| Change ticket trace | ✓ | ✓ | — | — | — | — | ✓ | — | ✓ | ✓ | ✓ |
| Z2 pending SLA | ✓ | — | ✓ | — | — | — | — | — | ✓ | — | ✓ |
| Z3 pending SLA | ✓ | — | ✓ | — | — | — | — | — | ✓ | ✓ | ✓ |

> **Note on FINRA-3110.** The ✓ marks above indicate the test produces evidence that **supports** the firm's Rule 3110 supervisory documentation. They do not indicate that the test result is itself a Rule 3110 supervisory record; the firm's WSPs and registered-principal review attestations remain the authoritative supervisory records.

---

## §4 OWNER Namespace — VC-5

### 4.1 Criterion mapping

This namespace evidences **VC-5: Ownerless Agents card is zero or actively remediated within 48 hours**. The Microsoft Agent 365 Admin Center surfaces an "Ownerless Agents" governance card; the native view identifies agents without assigned owners; disabled/departed-owner detection must also be reconciled against directory and source-platform evidence. This namespace asserts that either (a) the count is zero, or (b) every entry has an open remediation ticket aged ≤ 48 hours and bound to a designated interim owner per Control 3.6.

### 4.2 Pre-conditions

- PRE gates passed.
- AI Administrator activated.
- Reference data: `$env:AGT225_REMEDIATION_TICKET_RESOLVER` (per Control 3.6) is the URL used by `Resolve-Agt225OwnerRemediationTicket` to validate that an open ticket exists for each ownerless agent.

### 4.3 Manual verification procedure

1. Open **Agents > Overview > Agents without owners** and capture the resulting filtered registry list.
2. Reconcile IDs with Control 1.2 and Control 3.6 sources using the same scope and capture time. The native card identifies agents without assigned owners; independently check disabled, departed, or otherwise invalid owners. Do not assume the card implements every firm orphan-detection rule.
3. For each finding, verify a named interim owner, open remediation ticket, detection time, and due date against the existing zone thresholds.
4. Capture the post-remediation owner from the agent detail view and source platform after an authorized change. An empty or unavailable source is not proof of zero findings.

Apply the [registry ownerless-agent guidance](https://learn.microsoft.com/en-us/microsoft-agent-365/admin/agent-registry-overview#agents-without-owners).

### 4.4 Sample passing evidence

```json
{
  "control_id": "2.25", "run_id": "AGT225-20260415-093012-a1b2c3d4",
  "run_timestamp": "2026-04-15T09:30:12Z", "tenant_id": "11111111-2222-3333-4444-555555555555",
  "tenant_display_name": "Contoso Bank, N.A.", "cloud": "Commercial",
  "zone": "all", "namespace": "OWNER", "criterion": "VC-5",
  "subject_id": "ownerless-agents-card", "subject_type": "agent",
  "status": "PASS",
  "assertion": "All ownerless agents are either nonexistent or under <=48h remediation",
  "observed_value": { "ownerless_total": 0, "offender_count": 0, "offenders": [] },
  "expected_value": { "offender_count": 0 },
  "evidence_artifacts": ["ownerless-snapshot-AGT225-20260415-093012-a1b2c3d4.json"],
  "regulator_mappings": ["FINRA-3110","FINRA-4511","SOX-404","OCC-2011-12","NYDFS-500"],
  "remediation_ref": null, "operator_upn": "agt225-runner@contoso.com", "schema_version": "1.0"
}
```

### 4.5 Sample failing evidence

```json
{
  "control_id": "2.25", "run_id": "AGT225-20260415-093012-a1b2c3d4",
  "run_timestamp": "2026-04-15T09:30:12Z", "tenant_id": "11111111-2222-3333-4444-555555555555",
  "tenant_display_name": "Contoso Bank, N.A.", "cloud": "Commercial",
  "zone": "all", "namespace": "OWNER", "criterion": "VC-5",
  "subject_id": "ownerless-agents-card", "subject_type": "agent",
  "status": "FAIL",
  "assertion": "All ownerless agents are either nonexistent or under <=48h remediation",
  "observed_value": {
    "ownerless_total": 3, "offender_count": 2,
    "offenders": [
      { "agent_id": "agent-loan-summarizer-014", "prior_owner": "leavers.user1@contoso.com",
        "ticket_exists": false, "ticket_state": null, "ticket_age_h": 9999 },
      { "agent_id": "agent-treasury-ops-002", "prior_owner": "leavers.user2@contoso.com",
        "ticket_exists": true, "ticket_state": "Open", "ticket_age_h": 73.4 }
    ]
  },
  "expected_value": { "offender_count": 0 },
  "evidence_artifacts": ["ownerless-snapshot-AGT225-20260415-093012-a1b2c3d4.json"],
  "regulator_mappings": ["FINRA-3110","FINRA-4511","SOX-404","OCC-2011-12","NYDFS-500"],
  "remediation_ref": "TRG-OWNER-01", "operator_upn": "agt225-runner@contoso.com", "schema_version": "1.0"
}
```

### 4.6 Examiner artifact

| Property | Value |
|---|---|
| Filename | `ownerless-snapshot-<runId>.json`, `owner-evidence-<runId>.ndjson` |
| Storage | `$env:AGT225_EVIDENCE_ROOT/<runId>/owner/` |
| Retention | 6 years on WORM |
| Signing | Pack-level. Z3 failures additionally generate a same-day email-of-record to AI Governance Lead and CISO. |
| Distribution | AI Governance Lead, Compliance Officer, Information Security Officer |

### 4.7 Zone thresholds

| Zone | PASS | WARN | FAIL |
|---|---|---|---|
| Z1 | Verify ownership or document an approved scope exclusion; no automatic PASS from zone alone | — | — |
| Z2 | Count = 0 OR each entry has open ticket aged ≤ 48h | One entry approaching 48h (>36h) | Any entry without open ticket OR ticket aged > 48h |
| Z3 | Count = 0 OR each entry has open ticket aged ≤ 24h | One entry approaching 24h (>18h) | Any entry without open ticket OR ticket aged > 24h |

### 4.8 Regulator mapping

| Test | FINRA-3110 | FINRA-4511 | SOX-404 | GLBA-501b | OCC-2011-12 | NYDFS-500 | FFIEC-IS |
|---|---|---|---|---|---|---|---|
| Ownerless 48h | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| Z3 24h | ✓ | — | ✓ | ✓ | ✓ | ✓ | ✓ |

---

## §5 TEMPLATE Namespace — VC-3

### 5.1 Criterion mapping

This namespace evidences **VC-3: Governance template applied universally to Z2 and Z3 agents; Z3 agents specifically use a Custom template that is bound to a Microsoft Entra Access Package**. The Microsoft Agent 365 Admin Center allows a Default template (firm-wide baseline) and one or more Custom templates. For Zone 3 (Enterprise) agents, the firm policy in Control 2.25 requires the Custom template to be bound to an Entra Access Package so identity-governance reviews and joiner/mover/leaver flows operate per Control 2.26.

### 5.2 Pre-conditions

- PRE gates passed.
- AI Administrator activated.
- Reference data: `$env:AGT225_TEMPLATE_BASELINE` JSON file enumerates the firm's approved template IDs and which are eligible for which zone.

### 5.3 Manual verification procedure

1. Capture the selected policy template during publication or activation and its current policy composition. Compare it with the firm's approved zone baseline.
2. Verify the downstream Entra, Purview, SharePoint, and Defender policy configuration separately. Network visibility, Know your data, and content permissions insights are also in Microsoft's documented default template; do not identify a template as Custom solely from those policies.
3. For Zone 3, capture the firm's required custom-template, access-package, assignment-policy, and reviewer evidence from the appropriate admin surfaces. Treat their association as an evidence join, not an assumed `entraAccessPackageId` Graph property.
4. Use the appropriate privileged Entra role for Conditional Access or access-package policy configuration; AI Administrator alone cannot configure those policies. This verification does not perform those changes.
5. Mark missing template, binding, or enforcement evidence unresolved. Registry presence and template naming are insufficient for PASS.

See [activation and default template policies](https://learn.microsoft.com/en-us/microsoft-agent-365/admin/agent-actions#activate-agents).

### 5.4 Sample passing evidence

```json
{
  "control_id": "2.25", "run_id": "AGT225-20260415-093012-a1b2c3d4",
  "run_timestamp": "2026-04-15T09:30:12Z", "tenant_id": "11111111-2222-3333-4444-555555555555",
  "tenant_display_name": "Contoso Bank, N.A.", "cloud": "Commercial",
  "zone": "3", "namespace": "TEMPLATE", "criterion": "VC-3",
  "subject_id": "z3-access-package-binding", "subject_type": "governance_template",
  "status": "PASS",
  "assertion": "Every Z3 Custom template binds to a non-null Entra Access Package",
  "observed_value": { "unbound_count": 0, "unbound_ids": [] },
  "expected_value": { "unbound_count": 0 },
  "evidence_artifacts": ["templates-AGT225-20260415-093012-a1b2c3d4.json"],
  "regulator_mappings": ["FINRA-3110","SOX-404","GLBA-501b","OCC-2011-12","NYDFS-500"],
  "remediation_ref": null, "operator_upn": "agt225-runner@contoso.com", "schema_version": "1.0"
}
```

### 5.5 Sample failing evidence

```json
{
  "control_id": "2.25", "run_id": "AGT225-20260415-093012-a1b2c3d4",
  "run_timestamp": "2026-04-15T09:30:12Z", "tenant_id": "11111111-2222-3333-4444-555555555555",
  "tenant_display_name": "Contoso Bank, N.A.", "cloud": "Commercial",
  "zone": "3", "namespace": "TEMPLATE", "criterion": "VC-3",
  "subject_id": "z3-custom-template", "subject_type": "governance_template",
  "status": "FAIL",
  "assertion": "Every Z3 agent uses a Custom template (not Default)",
  "observed_value": { "z3_total": 24, "offender_count": 3,
                      "offender_ids": ["agent-payments-bot-007","agent-fraud-triage-002","agent-aml-screen-014"] },
  "expected_value": { "offender_count": 0 },
  "evidence_artifacts": ["templates-AGT225-20260415-093012-a1b2c3d4.json"],
  "regulator_mappings": ["FINRA-3110","SOX-404","OCC-2011-12","NYDFS-500"],
  "remediation_ref": "TRG-TEMPLATE-02", "operator_upn": "agt225-runner@contoso.com", "schema_version": "1.0"
}
```

### 5.6 Examiner artifact

| Property | Value |
|---|---|
| Filename | `templates-<runId>.json`, `template-evidence-<runId>.ndjson`, `access-package-reviewers-<runId>.json` |
| Storage | `$env:AGT225_EVIDENCE_ROOT/<runId>/template/` |
| Retention | 6 years on WORM |
| Signing | Pack-level; cross-references the §6 inventory by `agentId` |
| Distribution | AI Administrator, AI Governance Lead, Identity Engineering Lead |

### 5.7 Zone thresholds

| Zone | PASS | WARN | FAIL |
|---|---|---|---|
| Z1 | N/A — Z1 not template-bound; emits informational `SKIPPED` | — | — |
| Z2 | 100% have a Default or Custom template | 95–99% coverage with open remediation tickets | < 95% coverage OR any uncovered agent without ticket |
| Z3 | 100% have a Custom template + non-null Access Package + non-null Reviewer | One agent with template binding open ticket aged ≤ 24h | Any Z3 agent on Default OR with null Access Package OR with no Reviewer |

### 5.8 Regulator mapping

| Test | FINRA-3110 | FINRA-25-07 | SOX-404 | GLBA-501b | OCC-2011-12 | NYDFS-500 | FFIEC-MGMT |
|---|---|---|---|---|---|---|---|
| Z2 coverage | — | ✓ | ✓ | — | ✓ | — | ✓ |
| Z3 Custom | ✓ | — | ✓ | — | ✓ | ✓ | ✓ |
| Z3 Access Package | ✓ | — | ✓ | ✓ | ✓ | ✓ | ✓ |
| Z3 Reviewer | ✓ | — | ✓ | — | ✓ | ✓ | ✓ |

---

## §6 INVENTORY Namespace — VC-7

### 6.1 Criterion mapping

This namespace evidences **VC-7: Inventory exported monthly, WORM-protected, ISO 8601-dated, 12 months retained, with required field set**. The registry exposes agents discoverable through supported integrations; completeness across platforms, channels, draft states, and firm zones requires reconciliation. The firm's monthly governance process exports this inventory to WORM storage. This namespace asserts the export occurred, is well-formed, contains the required fields, and the trailing 12 months are present and unmodified.

### 6.2 Pre-conditions

- PRE gates passed.
- AI Administrator activated.
- Reference data: `$env:AGT225_INVENTORY_ARCHIVE_ROOT` — root path of the WORM archive (e.g., an Azure Storage container with an immutability policy or an Amazon S3 Object Lock bucket; the firm's storage architecture must satisfy SEC 17a-4(f) WORM requirements).
- Reference data: `$env:AGT225_INVENTORY_REQUIRED_FIELDS` — JSON array of field names; defaults to the canonical set: `["agentId","displayName","publisher","platform","ownerUpn","status","deploymentScope","governanceTemplate","lastApprovalTimestamp","approverUpn","createdAt","updatedAt","zone","tenantId"]`.

### 6.3 Manual verification procedure

1. Export from **Agents > All agents > Registry** with the intended **All agents / Filtered agents** scope recorded. Retain the original CSV or Excel file and capture applied filters and the export timestamp.
2. Reconcile IDs and counts against the same source scope and collection time. Total agents does not change with filtering. Multiple representations of one agent and unsupported draft/platform coverage require an explicit reconciliation, not an arbitrary row-count tolerance.
3. Compare every required firm evidence field with the actual headers. Supplement missing owner, zone, template, and approval attribution from approved sources with provenance. Do not manufacture values or claim the raw export contains all required columns.
4. Verify the trailing 12 monthly artifacts, date-stamped names, signed hash manifest, and storage retention configuration. Retain native exports alongside any normalized JSON. A hash comparison detects a content change; it does not prove a storage immutability policy is enabled.
5. Document collection gaps, absent months, incomplete fields, and source/format differences before assigning a result.

See [registry export and coverage](https://learn.microsoft.com/en-us/microsoft-agent-365/admin/agent-registry-overview).

### 6.4 Sample passing evidence

```json
{
  "control_id": "2.25", "run_id": "AGT225-20260415-093012-a1b2c3d4",
  "run_timestamp": "2026-04-15T09:30:12Z", "tenant_id": "11111111-2222-3333-4444-555555555555",
  "tenant_display_name": "Contoso Bank, N.A.", "cloud": "Commercial",
  "zone": "all", "namespace": "INVENTORY", "criterion": "VC-7",
  "subject_id": "inventory-12mo-coverage", "subject_type": "inventory_export",
  "status": "PASS",
  "assertion": "Trailing 12 monthly exports present in WORM archive",
  "observed_value": {
    "present_months": ["2025-05","2025-06","2025-07","2025-08","2025-09","2025-10",
                       "2025-11","2025-12","2026-01","2026-02","2026-03","2026-04"],
    "missing_months": []
  },
  "expected_value": { "missing_months": [] },
  "evidence_artifacts": ["inventory-coverage-AGT225-20260415-093012-a1b2c3d4.json"],
  "regulator_mappings": ["FINRA-4511","SEC-17a-3","SEC-17a-4","SOX-404","OCC-2011-12"],
  "remediation_ref": null, "operator_upn": "agt225-runner@contoso.com", "schema_version": "1.0"
}
```

### 6.5 Sample failing evidence

```json
{
  "control_id": "2.25", "run_id": "AGT225-20260415-093012-a1b2c3d4",
  "run_timestamp": "2026-04-15T09:30:12Z", "tenant_id": "11111111-2222-3333-4444-555555555555",
  "tenant_display_name": "Contoso Bank, N.A.", "cloud": "Commercial",
  "zone": "all", "namespace": "INVENTORY", "criterion": "VC-7",
  "subject_id": "inventory-hash-integrity", "subject_type": "inventory_export",
  "status": "FAIL",
  "assertion": "Every archived export hash matches the manifest (immutable)",
  "observed_value": {
    "tampered_count": 1,
    "tampered": [
      { "file": "agent365-inventory-2025-11-01.json",
        "expected": "5a7c2e...c811", "observed": "9f01b3...44df" }
    ]
  },
  "expected_value": { "tampered_count": 0 },
  "evidence_artifacts": ["inventory-hash-manifest-AGT225-20260415-093012-a1b2c3d4.json"],
  "regulator_mappings": ["FINRA-4511","SEC-17a-4","SOX-302","SOX-404"],
  "remediation_ref": "TRG-INVENTORY-04", "operator_upn": "agt225-runner@contoso.com", "schema_version": "1.0"
}
```

### 6.6 Examiner artifact

| Property | Value |
|---|---|
| Filename | `agent365-inventory-yyyy-MM-dd.json` (the monthly export); `inventory-hash-manifest.json` (chain-of-custody manifest); `inventory-evidence-<runId>.ndjson` (manual verification records) |
| Storage | WORM archive at `$env:AGT225_INVENTORY_ARCHIVE_ROOT` |
| Retention | 6 years on WORM, with the firm's documented immutability policy referenced in the §10 attestation |
| Signing | Each monthly export hash chained into the manifest, signed by AI Governance Lead at the time of monthly capture; the §10 pack additionally signs the manual verification records |
| Distribution | AI Governance Lead, Compliance Officer, Internal Audit |

### 6.7 Zone thresholds

| Zone | PASS | WARN | FAIL |
|---|---|---|---|
| All zones (this is a tenant-wide control) | All manual checks evidenced | One missing month within trailing 12, with a documented gap-explanation memo | Any hash tamper, OR > 1 missing month, OR required field absent in latest export |

### 6.8 Regulator mapping

| Test | FINRA-4511 | SEC-17a-3 | SEC-17a-4 | SOX-302 | SOX-404 | OCC-2011-12 | FFIEC-MGMT |
|---|---|---|---|---|---|---|---|
| 12 months present | ✓ | ✓ | ✓ | — | ✓ | ✓ | ✓ |
| ISO naming | ✓ | — | ✓ | — | ✓ | — | — |
| Required fields | ✓ | ✓ | ✓ | — | ✓ | ✓ | ✓ |
| Hash integrity | ✓ | — | ✓ | ✓ | ✓ | ✓ | ✓ |

---

## §7 EXCEPTION Namespace — VC-6

### 7.1 Criterion mapping

This namespace evidences **VC-6: Exception rate monitored against a documented threshold (illustrative ≤ 5%) with the past three documented review cycles**. The native Overview surfaces Agents with exceptions as a count. A firm-derived rate uses sessions with errors divided by total sessions for the same supported Activity scope and time period; it does not measure governance-template bypasses. This namespace asserts the metric is below the firm's threshold and that the firm's AI Governance Council reviewed it on the documented cadence.

> **Threshold is firm-set, not Microsoft-set.** The 5% value used as an illustrative example throughout this section is **not a Microsoft-published threshold**. The firm's AI Governance Council documents the threshold in policy (recommended starting point: 5%; mature programs frequently target 2%) and re-affirms it annually. An optional firm harness may read the threshold from `$env:AGT225_EXCEPTION_THRESHOLD_PCT`.

### 7.2 Pre-conditions

- PRE gates passed.
- AI Administrator activated.
- Reference data: `$env:AGT225_EXCEPTION_THRESHOLD_PCT` (default 5).
- Reference data: `$env:AGT225_EXCEPTION_REVIEW_LOG` — a JSON file of dated AI Governance Council review entries; produced by the council secretary per Control 4.5.

### 7.3 Manual verification procedure

1. Capture **Agents with exceptions** on Overview and the filtered registry view. Record this as a count, not a percentage.
2. For supported agents, open **Activity** and record Exceptions (sessions with an error) and Sessions for the same date range and scope.
3. If the firm uses a derived exception rate, calculate `100 * error_sessions / sessions`. Require a positive denominator and complete, comparable telemetry. Higher values are worse; no sessions or missing telemetry yields no rate, not zero or PASS.
4. Compare only a validated rate with the firm's documented threshold and zone cap. Keep policy-template variance reporting in a separate firm register; it is not the native Exceptions measure.
5. Confirm the three required review-cycle records and escalation decisions. Missing measurements or review evidence block acceptance.

See [agent Activity metrics](https://learn.microsoft.com/en-us/microsoft-agent-365/admin/agent-details#agent-activity).

### 7.4 Sample passing evidence

```json
{
  "control_id": "2.25", "run_id": "AGT225-20260415-093012-a1b2c3d4",
  "run_timestamp": "2026-04-15T09:30:12Z", "tenant_id": "11111111-2222-3333-4444-555555555555",
  "tenant_display_name": "Contoso Bank, N.A.", "cloud": "Commercial",
  "zone": "all", "namespace": "EXCEPTION", "criterion": "VC-6",
  "subject_id": "exception-rate-tenant", "subject_type": "exception_metric",
  "status": "PASS",
  "assertion": "Tenant exception rate <= 5%",
  "observed_value": { "exception_rate_pct": 2.7, "numerator": 11, "denominator": 410 },
  "expected_value": { "exception_rate_pct_max": 5 },
  "evidence_artifacts": ["exception-metric-AGT225-20260415-093012-a1b2c3d4.json"],
  "regulator_mappings": ["FINRA-3110","FINRA-25-07","SOX-404","OCC-2011-12","FFIEC-MGMT"],
  "remediation_ref": null, "operator_upn": "agt225-runner@contoso.com", "schema_version": "1.0"
}
```

### 7.5 Sample failing evidence

```json
{
  "control_id": "2.25", "run_id": "AGT225-20260415-093012-a1b2c3d4",
  "run_timestamp": "2026-04-15T09:30:12Z", "tenant_id": "11111111-2222-3333-4444-555555555555",
  "tenant_display_name": "Contoso Bank, N.A.", "cloud": "Commercial",
  "zone": "3", "namespace": "EXCEPTION", "criterion": "VC-6",
  "subject_id": "exception-rate-z3", "subject_type": "exception_metric",
  "status": "FAIL",
  "assertion": "Z3 exception rate <= 2.5% (half of firm-wide threshold)",
  "observed_value": { "exception_rate_pct": 4.1 },
  "expected_value": { "exception_rate_pct_max": 2.5 },
  "evidence_artifacts": ["exception-metric-AGT225-20260415-093012-a1b2c3d4.json"],
  "regulator_mappings": ["FINRA-3110","SOX-404","OCC-2011-12","NYDFS-500"],
  "remediation_ref": "TRG-EXCEPTION-02", "operator_upn": "agt225-runner@contoso.com", "schema_version": "1.0"
}
```

### 7.6 Examiner artifact

| Property | Value |
|---|---|
| Filename | `exception-metric-<runId>.json`, `exception-review-log-<runId>.json`, `exception-evidence-<runId>.ndjson` |
| Storage | `$env:AGT225_EVIDENCE_ROOT/<runId>/exception/` |
| Retention | 6 years on WORM |
| Signing | Pack-level. The review log sub-artifact is dual-signed by AI Governance Lead and Compliance Officer. |
| Distribution | AI Governance Lead, Compliance Officer, Information Security Officer, Technology Risk Manager |

### 7.7 Zone thresholds

| Zone | PASS | WARN | FAIL |
|---|---|---|---|
| Z1 | Always SKIPPED — the firm has explicitly excluded this zone from this review; do not infer a native metric exclusion | — | — |
| Z2 | Rate ≤ firm threshold (illustrative 5%) | Within 1 percentage point of threshold | Above threshold OR review cycle missed |
| Z3 | Rate ≤ half of firm threshold (illustrative 2.5%) | Within 0.5 pp of cap | Above cap OR review cycle missed |

### 7.8 Regulator mapping

| Test | FINRA-3110 | FINRA-25-07 | SOX-404 | OCC-2011-12 | NYDFS-500 | FFIEC-MGMT |
|---|---|---|---|---|---|---|
| Tenant rate | ✓ | ✓ | ✓ | ✓ | — | ✓ |
| Z3 rate | ✓ | — | ✓ | ✓ | ✓ | ✓ |
| Review cadence | ✓ | — | ✓ | ✓ | — | ✓ |

---

## §8 RESEARCHER Namespace — VC-8

### 8.1 Criterion mapping

This namespace evidences **VC-8: Researcher with Computer Use is configured per zone with a documented affirmative decision**. The current configuration source documents user/group access, work-data access, and website policy controls; it does not substantiate the previous October 2025 GA or universal availability/default-on claims. Because the capability allows the agent to perform automated browser interactions (click, type, navigate) against arbitrary URLs, the firm must make and document an affirmative per-zone decision: enabled for which users, with which URL allow-list, and signed by which approvers.

### 8.2 Pre-conditions

- PRE gates passed.
- AI Administrator activated.
- Reference data: `$env:AGT225_RESEARCHER_DECISION_LOG` — a JSON file of the firm's per-zone affirmative decisions with signers and effective dates, owned by the AI Governance Council.

### 8.3 Manual verification procedure

1. Open the Microsoft 365 admin **Agents** page, select **Researcher**, and inspect **Computer use** if available. If absent, record an availability/rollout gap; do not infer a restrictive configuration.
2. Capture the three documented controls: allowed users (all/specific/none), whether Researcher may access work data, and websites (all/allow specified/exclude specified).
3. Reconcile the effective users/groups with the firm's zone membership and signed decision log. Zone is a firm classification, not a native `policy.z3` property.
4. When work-data access is admin-enabled, users must still manually enable **Work** in Sources. When disabled, confirm that Work is unavailable. Test the approved and excluded websites in a controlled session without sensitive data.
5. Verify the decision's age, required signers, effective group membership, and website rules. Do not infer universal default-on, an October 2025 GA date, or a supported Graph policy API.

Use [Researcher admin configuration](https://learn.microsoft.com/en-us/copilot/manage/researcher-agent-computer-use); retain screenshots locally in the approved evidence repository.

### 8.4 Sample passing evidence

```json
{
  "control_id": "2.25", "run_id": "AGT225-20260415-093012-a1b2c3d4",
  "run_timestamp": "2026-04-15T09:30:12Z", "tenant_id": "11111111-2222-3333-4444-555555555555",
  "tenant_display_name": "Contoso Bank, N.A.", "cloud": "Commercial",
  "zone": "3", "namespace": "RESEARCHER", "criterion": "VC-8",
  "subject_id": "researcher-z3-policy-match", "subject_type": "researcher_policy",
  "status": "PASS",
  "assertion": "Tenant Researcher policy for Z3 matches documented affirmative decision",
  "observed_value": {
    "tenant_scope": "group:sg-research-pilot",
    "tenant_urls": ["https://research.fed.gov/*","https://www.sec.gov/*"]
  },
  "expected_value": {
    "documented_scope": "group:sg-research-pilot",
    "documented_urls": ["https://research.fed.gov/*","https://www.sec.gov/*"]
  },
  "evidence_artifacts": ["researcher-policy-AGT225-20260415-093012-a1b2c3d4.json"],
  "regulator_mappings": ["FINRA-3110","FINRA-25-07","SOX-404","GLBA-501b","OCC-2011-12","NYDFS-500"],
  "remediation_ref": null, "operator_upn": "agt225-runner@contoso.com", "schema_version": "1.0"
}
```

### 8.5 Sample failing evidence

```json
{
  "control_id": "2.25", "run_id": "AGT225-20260415-093012-a1b2c3d4",
  "run_timestamp": "2026-04-15T09:30:12Z", "tenant_id": "11111111-2222-3333-4444-555555555555",
  "tenant_display_name": "Contoso Bank, N.A.", "cloud": "Commercial",
  "zone": "3", "namespace": "RESEARCHER", "criterion": "VC-8",
  "subject_id": "researcher-z3-policy-match", "subject_type": "researcher_policy",
  "status": "FAIL",
  "assertion": "Tenant Researcher policy for Z3 matches documented affirmative decision",
  "observed_value": {
    "tenant_scope": "AllUsers",
    "tenant_urls": ["*"]
  },
  "expected_value": {
    "documented_scope": "group:sg-research-pilot",
    "documented_urls": ["https://research.fed.gov/*","https://www.sec.gov/*"]
  },
  "evidence_artifacts": ["researcher-policy-AGT225-20260415-093012-a1b2c3d4.json"],
  "regulator_mappings": ["FINRA-3110","FINRA-25-07","SOX-404","GLBA-501b","OCC-2011-12","NYDFS-500"],
  "remediation_ref": "TRG-RESEARCHER-03", "operator_upn": "agt225-runner@contoso.com", "schema_version": "1.0"
}
```

### 8.6 Examiner artifact

| Property | Value |
|---|---|
| Filename | `researcher-policy-<runId>.json`, `researcher-decision-log-<runId>.json`, `researcher-evidence-<runId>.ndjson` |
| Storage | `$env:AGT225_EVIDENCE_ROOT/<runId>/researcher/` |
| Retention | 6 years on WORM |
| Signing | Decision log dual-signed by AI Governance Lead and CISO at decision time; pack-level signature on manual verification records |
| Distribution | AI Governance Lead, CISO, Compliance Officer, Information Security Officer |

### 8.7 Zone thresholds

| Zone | PASS | WARN | FAIL |
|---|---|---|---|
| Z1 | Decision present <= 365d, signer = AI Governance Lead | Decision 365–545 days old | No decision OR > 545 days |
| Z2 | Decision present, signer = AI Governance Lead, scope is named group (not "AllUsers") | Decision aged or scope drift | "AllUsers" scope OR no decision |
| Z3 | Decision present, dual-signed AI Governance Lead + CISO, scope is named group, URL allow-list matches | Drift in URL allow-list with open ticket | "AllUsers" scope, "*" URL pattern, or missing CISO signature |

### 8.8 Regulator mapping

| Test | FINRA-3110 | FINRA-25-07 | SOX-404 | GLBA-501b | OCC-2011-12 | NYDFS-500 |
|---|---|---|---|---|---|---|
| Decision present | ✓ | ✓ | ✓ | — | ✓ | — |
| Z3 dual sign | ✓ | — | ✓ | ✓ | ✓ | ✓ |
| Policy match | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |

---

## §9 SIEM Namespace — Cross-Cutting

### 9.1 Criterion mapping

This namespace is **cross-cutting** — it does not map to a single VC, but rather provides defensible evidence that the Agent 365 governance events feeding all eight criteria are forwarded to the firm's SIEM with the retention required by FINRA Rule 4511 / SEC Rule 17a-4(f). It chains with [Control 3.9 Microsoft Sentinel Integration](../../../controls/pillar-3-reporting/3.9-microsoft-sentinel-integration.md) which is the authoritative control for SIEM forwarding generally; this namespace asserts only the Agent 365-specific subset.

### 9.2 Pre-conditions

- PRE gates passed.
- Operator holds **Entra Global Reader** plus the SIEM platform's read role (e.g., Microsoft Sentinel Reader) for query execution.
- Reference data: `$env:AGT225_SIEM_QUERY_ENDPOINT` (e.g., a Sentinel Log Analytics workspace ID), and `$env:AGT225_SIEM_QUERY_FN` — name of the saved KQL query that returns the trailing 7 days of Agent 365 governance events.

### 9.3 Manual verification procedure

1. With the Control 3.9 operator, map each required evidence stream to its actual audit/telemetry source, connector, table, and documented operation names. The namespace labels in this playbook are firm labels, not native `AgentGovernanceCategory` fields.
2. Trace an authorized, known test action from its source record into the SIEM, comparing agent ID, actor, event time, ingestion time, and result. A quiet period alone does not establish a broken pipeline or successful forwarding.
3. Read the actual table retention configuration and separately retained export policy. For Log Analytics, analytics retention is at most 730 days; inspect **total retention / long-term retention** for multi-year storage. A workspace analytics value of 2192 days is not a valid test.
4. Verify retrieval of retained data and the existing six-year evidence-archive requirement independently. Do not infer immutability from Log Analytics retention alone.
5. Record unmapped categories, incomplete ingestion, failed retrieval, and missing retention evidence as unresolved, not as allowed quiet-category PASS results.

See [Log Analytics data retention](https://learn.microsoft.com/en-us/azure/azure-monitor/logs/data-retention-configure).

### 9.4 Sample passing evidence

```json
{
  "control_id": "2.25", "run_id": "AGT225-20260415-093012-a1b2c3d4",
  "run_timestamp": "2026-04-15T09:30:12Z", "tenant_id": "11111111-2222-3333-4444-555555555555",
  "tenant_display_name": "Contoso Bank, N.A.", "cloud": "Commercial",
  "zone": "all", "namespace": "SIEM", "criterion": "VC-1..8 (cross-cutting)",
  "subject_id": "siem-retention-config", "subject_type": "diagnostic_setting",
  "status": "PASS",
  "assertion": "SIEM table total retention and separate evidence archive meet the existing firm retention policy",
  "observed_value": { "table_total_retention_days": 2557, "archive_policy_verified": true },
  "expected_value": { "table_total_retention_days_min": 2192, "archive_policy_verified": true },
  "evidence_artifacts": ["siem-retention-AGT225-20260415-093012-a1b2c3d4.json"],
  "regulator_mappings": ["FINRA-4511","SEC-17a-4","SOX-404","OCC-2011-12"],
  "remediation_ref": null, "operator_upn": "agt225-runner@contoso.com", "schema_version": "1.0"
}
```

### 9.5 Sample failing evidence

```json
{
  "control_id": "2.25", "run_id": "AGT225-20260415-093012-a1b2c3d4",
  "run_timestamp": "2026-04-15T09:30:12Z", "tenant_id": "11111111-2222-3333-4444-555555555555",
  "tenant_display_name": "Contoso Bank, N.A.", "cloud": "Commercial",
  "zone": "all", "namespace": "SIEM", "criterion": "VC-1..8 (cross-cutting)",
  "subject_id": "siem-event-presence", "subject_type": "diagnostic_setting",
  "status": "FAIL",
  "assertion": "SIEM ingest pipeline yields >=1 Agent 365 event in trailing 7d",
  "observed_value": { "event_count_7d": 0 },
  "expected_value": { "event_count_7d_min": 1 },
  "evidence_artifacts": ["siem-query-AGT225-20260415-093012-a1b2c3d4.json"],
  "regulator_mappings": ["FINRA-4511","SEC-17a-4","SOX-404","OCC-2011-12","NYDFS-500","FFIEC-IS"],
  "remediation_ref": "TRG-SIEM-01", "operator_upn": "agt225-runner@contoso.com", "schema_version": "1.0"
}
```

### 9.6 Examiner artifact

| Property | Value |
|---|---|
| Filename | `siem-query-<runId>.json`, `siem-retention-<runId>.json`, `siem-evidence-<runId>.ndjson` |
| Storage | `$env:AGT225_EVIDENCE_ROOT/<runId>/siem/` |
| Retention | 6 years on WORM (the SIEM evidence is archived in addition to the SIEM's own retention) |
| Signing | Pack-level. Cross-references Control 3.9 evidence pack via `parent_pack_ref`. |
| Distribution | AI Governance Lead, Information Security Officer, Entra Security Admin |

### 9.7 Zone thresholds

This namespace operates tenant-wide; no zone differentiation. PASS requires verified source mapping, known-event ingestion/retrieval, retention configuration, and archive evidence. Missing coverage remains unresolved; no quiet-category allowance substitutes for evidence.

### 9.8 Regulator mapping

| Test | FINRA-4511 | SEC-17a-4 | SOX-404 | OCC-2011-12 | NYDFS-500 | FFIEC-IS |
|---|---|---|---|---|---|---|
| Event presence 7d | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| Retention >= 6yr | ✓ | ✓ | ✓ | ✓ | — | — |
| Namespace coverage | ✓ | — | ✓ | ✓ | — | — |

---

## §10 Evidence Pack Assembly & Signing

### 10.1 Pack layout

After all manual checks complete, the firm's validated assembly process (not supplied here as `Build-Agt225EvidencePack`) assembles a single signed pack at `$script:EvidenceRoot/pack/`:

```
<runId>/
├── pack/
│   ├── attestation.json              # Merkle root + signer + timestamps
│   ├── attestation.json.sig          # Detached signature (RFC 5652 CMS or PGP)
│   ├── manifest.json                 # Per-file metadata: path, size, sha256
│   ├── summary.md                    # Human-readable executive summary
│   └── findings.csv                  # Flat CSV of all evidence records
├── license/
├── approval/
├── owner/
├── template/
├── inventory/
├── exception/
├── researcher/
├── siem/
```

### 10.2 Pack metadata

```json
{
  "control_id": "2.25",
  "control_version": "v1.4",
  "playbook_version": "v1.4",
  "run_id": "AGT225-20260415-093012-a1b2c3d4",
  "run_started_utc": "2026-04-15T09:30:12Z",
  "run_completed_utc": "2026-04-15T09:47:08Z",
  "tenant_id": "11111111-2222-3333-4444-555555555555",
  "tenant_display_name": "Contoso Bank, N.A.",
  "cloud": "Commercial",
  "operator_upn": "agt225-runner@contoso.com",
  "operator_role_at_run": "AI Administrator (PIM activated)",
  "witness_upn": "agt225-witness@contoso.com",
  "witness_role_at_run": "Entra Global Reader (PIM activated)",
  "namespace_results": {
    "LICENSE":    { "pass": 4, "warn": 0, "fail": 0, "skipped": 0, "error": 0 },
    "APPROVAL":   { "pass": 5, "warn": 0, "fail": 0, "skipped": 0, "error": 0 },
    "OWNER":      { "pass": 2, "warn": 0, "fail": 0, "skipped": 0, "error": 0 },
    "TEMPLATE":   { "pass": 3, "warn": 0, "fail": 0, "skipped": 0, "error": 0 },
    "INVENTORY":  { "pass": 4, "warn": 0, "fail": 0, "skipped": 0, "error": 0 },
    "EXCEPTION":  { "pass": 3, "warn": 0, "fail": 0, "skipped": 0, "error": 0 },
    "RESEARCHER": { "pass": 3, "warn": 0, "fail": 0, "skipped": 0, "error": 0 },
    "SIEM":       { "pass": 3, "warn": 0, "fail": 0, "skipped": 0, "error": 0 }
  },
  "pack_status": "PASS",
  "merkle_root_sha256": "f3a9...c021",
  "schema_version": "1.0"
}
```

### 10.3 Signing

The pack is signed by the AI Governance Lead using a key managed in the firm's PKI or Azure Key Vault (managed HSM where available). The witness (Entra Global Reader operator) co-signs attesting to the dual-control read of the pack contents prior to publication.

### 10.4 Merkle root

Every evidence record file contributes a SHA-256 leaf hash (computed over the canonical JSON serialization). Leaves are sorted lexicographically by filename and combined pairwise into a binary Merkle tree; the root hash is recorded as `merkle_root_sha256` in `attestation.json`. A validated integrity checker must detect changed records; `Test-Agt225PackIntegrity` is an illustrative helper name, not a supplied implementation.

### 10.5 Schema validation

Before signing, the firm's implemented schema validator must validate every record against the §1.1 contract; `Test-Agt225EvidenceSchema` is not supplied here. Records failing schema validation are not signed; the pack assembler exits with a non-zero status and writes `schema-violation-<runId>.json` to the pack directory for triage.

### 10.6 Publication

Signed packs are published to `$env:AGT225_PACK_PUBLICATION_ROOT` (a WORM container distinct from the working evidence root) and an index entry is appended to the firm's evidence-pack registry per Control 2.13. The publication step emits an OpenTelemetry span that flows to the firm's observability platform and to the SIEM (Control 3.1).

### 10.7 Retention

| Cloud | Retention | Authority |
|---|---|---|
| Commercial | 6 years on WORM | FINRA 4511 / SEC 17a-4(f) |

---

## §11 Failure Triage Matrix

When a manual verification check fails, the evidence record carries a `remediation_ref` of the form `TRG-{NS}-NN`. This matrix maps each ID to severity, SLA band, owner, and the remediation playbook section.

| Triage ID | Severity | SLA to remediate | Owner | Remediation reference |
|---|---|---|---|---|
| TRG-LICENSE-01 | Critical | 1 BD | Procurement Lead + Entra Global Admin | [Portal Walkthrough §0.3](./portal-walkthrough.md) |
| TRG-LICENSE-02 | Critical | 1 BD | Procurement Lead | [Portal Walkthrough §0.3](./portal-walkthrough.md) |
| TRG-LICENSE-03 | Critical | 4 hours | AI Administrator | [Troubleshooting](./troubleshooting.md) §3.1 |
| TRG-LICENSE-04 | Medium | 30 days | Procurement Lead | [Portal Walkthrough §0.3](./portal-walkthrough.md) |
| TRG-APPROVAL-01 | High | 2 BD | AI Governance Lead | [Portal Walkthrough §4](./portal-walkthrough.md) |
| TRG-APPROVAL-02 | Medium | 5 BD | AI Governance Lead | [Portal Walkthrough §4](./portal-walkthrough.md) |
| TRG-APPROVAL-03 | High | 2 BD | Change Management Lead | [Portal Walkthrough §4](./portal-walkthrough.md) |
| TRG-APPROVAL-04 | High | 1 BD | AI Governance Lead | [PowerShell Setup](./powershell-setup.md) §4.2 |
| TRG-APPROVAL-05 | Critical | 4 hours | AI Governance Lead | [PowerShell Setup](./powershell-setup.md) §4.3 |
| TRG-OWNER-01 | High | 48 hours | AI Governance Lead | [Portal Walkthrough §2.3](./portal-walkthrough.md) |
| TRG-OWNER-02 | Critical | 24 hours | AI Governance Lead | [Portal Walkthrough §2.3](./portal-walkthrough.md) |
| TRG-TEMPLATE-01 | High | 5 BD | AI Administrator | [Portal Walkthrough §8](./portal-walkthrough.md) |
| TRG-TEMPLATE-02 | Critical | 2 BD | AI Administrator | [Portal Walkthrough §8](./portal-walkthrough.md) |
| TRG-TEMPLATE-03 | Critical | 2 BD | Identity Engineering Lead | [Portal Walkthrough §8](./portal-walkthrough.md) |
| TRG-TEMPLATE-04 | High | 5 BD | Identity Engineering Lead | [Portal Walkthrough §8](./portal-walkthrough.md) |
| TRG-INVENTORY-01 | High | 5 BD | AI Governance Lead | [PowerShell Setup](./powershell-setup.md) §5.1 |
| TRG-INVENTORY-02 | Medium | 5 BD | AI Governance Lead | [PowerShell Setup](./powershell-setup.md) §5.2 |
| TRG-INVENTORY-03 | High | 5 BD | AI Governance Lead | [PowerShell Setup](./powershell-setup.md) §5.3 |
| TRG-INVENTORY-04 | Critical | 4 hours (IR escalation) | CISO + AI Governance Lead | [Troubleshooting](./troubleshooting.md) §6.1 |
| TRG-EXCEPTION-01 | High | 30 days | AI Governance Lead | [Portal Walkthrough §2.1](./portal-walkthrough.md) |
| TRG-EXCEPTION-02 | Critical | 10 BD | AI Governance Lead + CISO | [Portal Walkthrough §2.1](./portal-walkthrough.md) |
| TRG-EXCEPTION-03 | Critical | 1 quarter | AI Governance Lead | [Portal Walkthrough §2.1](./portal-walkthrough.md) |
| TRG-RESEARCHER-01 | High | 30 days | AI Governance Lead | [Portal Walkthrough §9](./portal-walkthrough.md) |
| TRG-RESEARCHER-02 | Critical | 10 BD | AI Governance Lead + CISO | [Portal Walkthrough §9](./portal-walkthrough.md) |
| TRG-RESEARCHER-03 | Critical | 4 hours | AI Administrator | [PowerShell Setup](./powershell-setup.md) §7.3 |
| TRG-SIEM-01 | High | 1 BD | Entra Security Admin | [Troubleshooting](./troubleshooting.md) §9.1 |
| TRG-SIEM-02 | Critical | 5 BD | Entra Security Admin | [PowerShell Setup](./powershell-setup.md) §9.2 |
| TRG-SIEM-03 | Medium | 30 days | Entra Security Admin | [Troubleshooting](./troubleshooting.md) §9.3 |

> Severity bands: **Critical** — examiner-visible if unremediated; **High** — examiner-visible if recurring or pattern; **Medium** — process improvement; **Informational**.

---

## §12 Cross-Control Verification Dependencies

This playbook is one node in the broader Pillar 2 governance graph. The following dependencies must be considered when reading this evidence pack.

| Direction | Control | Interaction |
|---|---|---|
| Upstream | [1.2 Agent Registry & Integrated Apps Management](../../../controls/pillar-1-security/1.2-agent-registry-and-integrated-apps-management.md) | Provides the "golden" agent inventory consumed by the OWNER and INVENTORY namespaces. If 1.2 evidence shows registry drift, 2.25 OWNER evidence is suspect. |
| Upstream | [2.26 Entra Agent ID Identity Governance](../../../controls/pillar-2-management/2.26-entra-agent-id-identity-governance.md) | Provides the Entra Access Package binding asserted in §5 TEMPLATE for Z3 agents. If 2.26 evidence shows orphaned access packages, 2.25 TEMPLATE PASS is downgraded to WARN. |
| Upstream | [2.3 Change Management and Release Planning](../../../controls/pillar-2-management/2.3-change-management-and-release-planning.md) | Provides the change-ticket records cross-referenced by §3 APPROVAL `Resolve-Agt225ChangeTicket`. |
| Upstream | [2.8 Access Control and Segregation of Duties](../../../controls/pillar-2-management/2.8-access-control-and-segregation-of-duties.md) | Provides the 90-day re-attestation evidence referenced in §2.7 Z3 PASS criteria. |
| Lateral | [2.13 Documentation and Record Keeping](../../../controls/pillar-2-management/2.13-documentation-and-record-keeping.md) | Receives the §10 published pack metadata. |
| Downstream | [3.9 Microsoft Sentinel Integration](../../../controls/pillar-3-reporting/3.9-microsoft-sentinel-integration.md) | Consumes the SIEM forwarding namespace; the §9 evidence cross-references the parent 3.9 pack via `parent_pack_ref`. |
| Downstream | [3.6 Orphaned Agent Detection & Remediation](../../../controls/pillar-3-reporting/3.6-orphaned-agent-detection-and-remediation.md) | Consumes the §4 OWNER findings; offender list flows directly into 3.6 remediation queue. |
| Downstream | 4.5 AI Governance Council Operations (planned) | Consumes the §7 EXCEPTION review-cycle artifacts; council secretary maintains `$env:AGT225_EXCEPTION_REVIEW_LOG`. |

When assembling a quarterly attestation for an examiner, present the 2.25 evidence pack alongside the 1.2 and 2.26 packs of the same quarter — examiners typically request the trio together as evidence of admin-gated lifecycle for AI agents.

---

## §13 Quarterly Attestation Runbook

### 13.1 Cadence

| Activity | Cadence | Owner |
|---|---|---|
| Run §2–§9 manual verification | Daily (Z3-touching tests), Weekly (full suite), Monthly (with INVENTORY) | AI Administrator |
| Assemble §10 evidence pack | Monthly | AI Governance Lead |
| Quarterly attestation packet | Quarterly (within 15 BD of quarter end) | AI Governance Lead + Compliance Officer |
| Annual control re-baseline (review thresholds in §3, §7) | Annually | AI Governance Council |

### 13.2 Quarterly packet contents

1. The three monthly §10 evidence packs from the quarter, with their attestation.json files.
2. A quarterly summary memo `2.25-quarterly-summary-yyyy-Qn.md` covering: namespace pass rates; trend vs. prior quarter; open remediation tickets; threshold variance review (if any threshold in `$env:AGT225_*` was changed during the quarter, the change is recorded with its approver and effective date).
4. The signed cross-reference index linking the 2.25 pack to the 1.2 and 2.26 packs of the same quarter.

### 13.3 Attestation signers

- **AI Governance Lead** — primary signer, attests to operational accuracy.
- **Compliance Officer** — counter-signer, attests to regulatory mapping accuracy.
- **Information Security Officer** — counter-signer for any quarter containing a TRG-*-Critical finding.
- **Technology Risk Manager** — receives the packet for inclusion in firm technology-risk reporting per OCC Bulletin 2026-13 (formerly OCC Bulletin 2011-12).

### 13.4 Distribution

| Recipient | Distribution form | Retention obligation |
|---|---|---|
| Internal Audit | WORM-protected link; read-only | Per audit's own retention policy |
| Compliance Department | WORM-protected link | 6 years |
| Examiner (on request) | Signed PDF export of `summary.md` plus selected evidence records | Per examiner request |
| Firm GRC platform | Structured ingest of `findings.csv` plus `attestation.json` | Per GRC retention policy |

### 13.5 Continuous improvement

Each quarterly review identifies up to three improvement items, recorded in the firm's GRC platform, owned by the AI Governance Lead, and re-checked at the next quarterly review. Common improvement themes include: tightening firm-set thresholds (§3 SLA, §7 exception cap) as the program matures; expanding the §6 INVENTORY field set to capture additional governance metadata as Microsoft adds it; tightening the §8 RESEARCHER URL allow-list as the firm's research workflow stabilizes.

---

## §14 References

- Control source of truth: [Control 2.25 — Microsoft Agent 365 Admin Center Governance Console](../../../controls/pillar-2-management/2.25-agent-365-admin-center-governance-console.md)
- Sister verification playbook (gold-standard structural template): [Control 2.26 verification-testing](../2.26/verification-testing.md)
- Sibling playbooks for this control: [Portal Walkthrough](./portal-walkthrough.md) · [PowerShell Setup](./powershell-setup.md) · [Troubleshooting](./troubleshooting.md)
- Role catalog: [`docs/reference/role-catalog.md`](../../../reference/role-catalog.md)
- Regulatory mapping vocabulary: [`docs/reference/regulatory-mappings.md`](../../../reference/regulatory-mappings.md)

---

*Updated: November 2026 | Version: v1.6.2 | UI Verification Status: Needs Review (documentation verified 2026-11-09; tenant execution pending)*
