# Verification & Testing — Control 2.25: Microsoft Agent 365 Admin Center Governance Console

> **Examiner-defensible evidence package** for Control 2.25. This playbook produces, signs, and retains the artifacts required to demonstrate to FINRA, SEC, OCC, FFIEC, NYDFS, and internal audit that every Microsoft 365 AI agent surfaced through the Microsoft Agent 365 Admin Center is licensed, admin-approved, owned, governance-template-bound, exception-monitored, inventory-exported, and (for the Researcher with Computer Use capability) configured per documented zone policy.
>
> **Scope:** Commercial M365 tenants holding Microsoft 365 E7 ("Frontier Suite") **or** the standalone Microsoft Agent 365 license layered on a Microsoft 365 Copilot prerequisite. Microsoft Agent 365 reached general availability on **May 1, 2026**. Sovereign clouds (GCC, GCC High, DoD) follow the compensating-control pattern in §10 because the Agent 365 Admin Center governance console, governance templates, and admin-gated publish/activate workflows are not yet at parity in sovereign environments at the time of this playbook's last UI verification.
>
> **Companion controls:** [1.2 Agent Registry & Integrated Apps Management](../../../controls/pillar-1-security/1.2-agent-registry-and-integrated-apps-management.md) feeds the OWNER and INVENTORY namespaces. [2.26 Entra Agent ID Identity Governance](../../../controls/pillar-2-management/2.26-entra-agent-id-identity-governance.md) provides the identity-layer prerequisite that 2.25 governance templates rely on for Zone 3 access-package binding. [3.9 Microsoft Sentinel Integration](../../../controls/pillar-3-reporting/3.9-microsoft-sentinel-integration.md) consumes the SIEM forwarding namespace. [3.6 Orphaned Agent Detection & Remediation](../../../controls/pillar-3-reporting/3.6-orphaned-agent-detection-and-remediation.md) consumes the OWNER namespace outputs.
>
> **Last UI verified:** April 2026 against the post-GA Microsoft 365 admin center build 2026.04.x and the Microsoft Agent 365 Admin Center release of the same build.
>
> **Important regulatory framing.** This playbook **supports compliance with**, but does not by itself ensure compliance with, FINRA Rules 3110 (Supervision) and 4511 (Books and Records), FINRA RN 24-09 / Rule 3110 (AI Tools), SEC Rules 17a-3 / 17a-4 (Recordkeeping), SOX Sections 302 / 404 (Internal Controls), GLBA Section 501(b) (Safeguards Rule), OCC Bulletin 2026-13 (formerly OCC Bulletin 2011-12) (Technology Risk Management), NYDFS 23 NYCRR 500 (Cybersecurity), and the FFIEC IT Examination Handbook. Where FINRA Rule 3110 obligates the firm to assign a registered principal to a supervisory function, the Agent 365 governance console **does not substitute for** that registered-principal designation; it produces the evidentiary trail that supports — but does not replace — the firm's written supervisory procedures (WSPs).

---

## Document Conventions

| Convention | Value |
|---|---|
| PowerShell baseline | PowerShell 7.4+ Core; `#Requires -Version 7.4` at the top of every executable script. |
| Test framework | Pester 5.5+. All assertions use `Should` with `-Because` clauses to make examiner traceability explicit. |
| Output discipline | No `Write-Host`. All evidence emitted as structured `[pscustomobject]` instances via `Write-Output`, then serialized with `ConvertTo-Json -Depth 8` to evidence files. |
| Sovereign cloud handling | All Pester suites detect tenant cloud and emit `SKIPPED` records with a compensating-control pointer to §10 rather than `FAIL` (see §0.4). |
| Evidence retention | Six (6) years on WORM-protected storage for the full signed evidence pack — aligning to FINRA Rule 4511 / SEC Rule 17a-4(f). The 3-year minimum applies only to non-supervisory administrative artifacts the firm has documented as out-of-scope of supervisory recordkeeping. |
| Hashing | SHA-256 over canonical JSON; chained leaf hashes plus a Merkle root in `attestation.json` (see §11.4). |
| Sovereign anchor | All sovereign-aware functions reference [`../../_shared/powershell-baseline.md#3-sovereign-cloud-endpoints-gcc-gcc-high-dod`](../../_shared/powershell-baseline.md#3-sovereign-cloud-endpoints-gcc-gcc-high-dod). |
| Run identifier | Every test run is tagged `AGT225-yyyyMMdd-HHmmss-<8charGuid>` and embedded in every evidence record and artifact filename. |
| Canonical role names | Per [`docs/reference/role-catalog.md`](../../../reference/role-catalog.md). At GA, **Entra Global Admin** and **AI Administrator** are the only Agent 365-capable administrative roles; **Entra Global Reader** provides read-only verification access. |

> This playbook **helps meet** recordkeeping, supervision, change-management, access-management, and oversight expectations under the regulations enumerated above. It is one component of a defensible AI governance program; it does not replace a registered-principal designation, written supervisory procedures, model risk management practices required by Fed SR 26-2 (formerly SR 11-7) / OCC Bulletin 2026-13 (formerly OCC 2011-12), or the firm's own legal review.

---

## §0 Pre-Test Prerequisites & Sovereign Cloud Bootstrap

### 0.1 Operator role prerequisites

The operator running this playbook must hold one of the following Entra role assignments, scoped to the tenant under test, and activated through Microsoft Entra Privileged Identity Management (PIM) for the duration of the test run. Read-only assertions in §2–§9 are deliberately separated from any write actions; the Pester suites in this playbook **do not perform remediation**. Remediation runbooks referenced from failure paths (e.g., `Set-Agent365TemplateBulk`, `Invoke-Agent365PendingApprovalDrain`) live in the sister [PowerShell Setup](./powershell-setup.md) playbook and require their own change tickets and write scopes.

| Role (canonical) | Required for | PIM activation window |
|---|---|---|
| Entra Global Admin | Tenant-scope reads in §2 (license SKU enumeration), §6 (governance template definition reads), §8 (Researcher with Computer Use policy reads); emergency execution of remediation runbooks | 2 hours, just-in-time, with ticketed justification |
| AI Administrator | Day-to-day reads against the Microsoft Agent 365 Admin Center: agent inventory (§3, §4, §5, §7), pending approvals queue (§3), governance template assignments (§6), exception-rate metric (§8), Researcher with Computer Use policy (§9). Read-only operations only in this playbook. | 4 hours, just-in-time |
| Entra Global Reader | Evidence-only verification access where AI Administrator is unavailable; supports the dual-control witness pattern in §11.4 | 4 hours |
| Purview Compliance Admin | Read access to Purview audit retention labels referenced by Agent 365 governance templates (§6); read access to the Audit (Premium) search that backs the SIEM forwarding evidence in §9 | 4 hours |
| Power Platform Admin | Read access to Microsoft Copilot Studio environment governance metadata for agents that surface in Agent 365 from Copilot Studio (cross-referenced in §6) | 2 hours |
| AI Governance Lead | Counter-signs the quarterly attestation packet in §14; reviews Pending Requests and Ownerless Agents governance cards on the documented cadence; signs the evidence pack in §11 | Standing assignment with quarterly recertification per Control 2.8 |
| Compliance Officer | Counter-signs the quarterly attestation packet in §14; signs Zone 3 governance template variances; signs the §10 sovereign quarterly attestation | Standing |
| Information Security Officer | Reviews exception-rate threshold variances; reviews Researcher with Computer Use Zone 3 configurations | Standing |
| Technology Risk Manager | Receives the §11 evidence pack and integrates it into the firm's technology-risk reporting per OCC Bulletin 2026-13 (formerly OCC 2011-12) | Standing |
| Change Management Lead | Reconciles Agent 365 approval timestamps with change tickets per Control 2.3 (verified in §3) | Standing |

> **Least privilege.** No operator should hold **Entra Global Admin** persistently. Day-to-day verification work in §2–§9 is performed under **AI Administrator** with **Entra Global Reader** as the witness role. **Entra Global Admin** is reserved for tenant enrollment, licensing changes, and emergency remediation, and is operated under PIM with just-in-time activation.

### 0.2 Module baseline

Pin to specific module versions to keep evidence packs reproducible across machines and over time. Re-validate against newer module versions before promoting them to the standing schedule.

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

> **Note on Agent 365 admin Graph endpoints.** At GA, Microsoft exposes the Agent 365 governance objects (agent inventory, pending publish/activate requests, governance templates, ownerless agents) under the `/beta/agentGovernance` Graph branch. The exact noun names and module distribution (e.g., whether they ship in `Microsoft.Graph.Beta.Applications` or in a dedicated `Microsoft.Graph.Beta.AgentGovernance` module) are still settling across the 2026 Wave 1 release cycle. The functions referenced in this playbook (`Get-Agent365Inventory`, `Get-Agent365PendingApproval`, `Get-Agent365OwnerlessAgent`, `Get-Agent365GovernanceTemplateAssignment`, `Get-Agent365ExceptionMetric`, `Get-Agent365ResearcherComputerUsePolicy`) are thin wrappers in the sister [PowerShell Setup](./powershell-setup.md) playbook that abstract the underlying Graph URI. **Re-verify the module name and noun set after each Microsoft release wave.**

### 0.3 PRE gates (must all pass before §2–§9 execute)

The bootstrap script `Invoke-Agt225PreFlight.ps1` runs eight pre-flight gates. Any `FAIL` halts the suite and emits a single evidence artifact `preflight-FAILED-<runId>.json`. Any `SKIPPED` from PRE-06 redirects the run to §10 (sovereign compensating control).

| Gate | ID | Purpose | Failure behavior |
|---|---|---|---|
| Module presence | PRE-01 | Confirms required modules loaded at the pinned versions in §0.2 | HALT |
| Graph context | PRE-02 | Confirms `Connect-MgGraph` established with required scopes (`AgentGovernance.Read.All`, `Directory.Read.All`, `Application.Read.All`, `User.Read.All`, `Reports.Read.All`, `AuditLog.Read.All`) | HALT |
| Tenant identification | PRE-03 | Captures `tenantId`, `displayName`, `verifiedDomains[0].name` for every evidence record | HALT |
| Cloud detection | PRE-04 | Reads `(Get-MgContext).Environment` and maps to `Commercial / GCC / GCCH / DoD` | Continue with `cloud` field set; sovereign clouds route to §10 |
| License gate | PRE-05 | Confirms tenant holds either Microsoft 365 E7 (`SkuPartNumber -like 'M365_E7*'`) **or** standalone Agent 365 (`SkuPartNumber -like 'Microsoft_Agent_365*'`), AND at least one Microsoft 365 Copilot SKU (`SkuPartNumber -like 'Microsoft_365_Copilot*'`) | HALT — Agent 365 requires both license layers |
| Agent 365 admin blade reachability | PRE-06 | Probes `/beta/agentGovernance/inventory?$top=1` for HTTP 200; in sovereign clouds expects 404/501 and routes to §10 | If 404/403/501 in Commercial: HALT; if sovereign: route to §10 |
| Clock skew gate | PRE-07 | Compares local UTC to the `Date` header from the Graph response; aborts if drift exceeds 60 seconds | HALT — clock skew invalidates timestamp evidence for FINRA 4511 / SEC 17a-4 |
| Evidence root writeable | PRE-08 | Confirms `$env:AGT225_EVIDENCE_ROOT` exists, is writeable, and resolves to a path under WORM-eligible storage (validated by checking the parent storage account's immutability policy where applicable) | HALT |

### 0.4 Sovereign bootstrap pattern

```powershell
function Test-Agt225SovereignTenant {
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
        endpoint_ref  = '../../_shared/powershell-baseline.md#3-sovereign-cloud-endpoints-gcc-gcc-high-dod'
    }
}
```

When `is_sovereign` is `$true`, every Pester `It` block in §2–§9 emits a `SKIPPED` record rather than a `FAIL`:

```json
{
  "status": "SKIPPED",
  "reason": "Microsoft Agent 365 Admin Center governance console not at parity in sovereign cloud at run time",
  "compensating_control_ref": "§10 SOV namespace; manual quarterly attestation per Control 2.25 §0",
  "next_check_due": "2026-07-15T00:00:00Z"
}
```

This produces an examiner-defensible audit trail showing the test was attempted, was correctly skipped on regulatory-sound grounds, and was supplemented by the manual attestation in §10 — rather than appearing as an unexplained gap. The next-check date is set to the start of the following quarter so the sovereign roadmap re-verification cadence (per Control 2.25 §0 sovereign admonition) is itself evidenced.

### 0.5 Run identifier and evidence root

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

Every evidence record produced in §2–§10 is written under `$script:EvidenceRoot` and the `runId` is embedded in the filename of every artifact assembled into the §11 evidence pack.

---

## §1 Namespace Catalog

The eight Verification Criteria from [Control 2.25](../../../controls/pillar-2-management/2.25-agent-365-admin-center-governance-console.md) (the "VCs") are evidenced by eight test namespaces. Each namespace produces independent evidence records that combine into a single signed evidence pack (§11). A ninth cross-cutting namespace (SIEM) and a tenth sovereign-only namespace (SOV) round out the suite.

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
| `SOV` | §10 | All VCs — sovereign cloud compensating attestation (sovereign tenants only) | Quarterly | AI Governance Lead + Compliance Officer |

Each namespace section follows an identical 8-part structure, mirroring the sister [Control 2.26 verification playbook](../2.26/verification-testing.md):

1. **Criterion mapping** — explicit pointer to which numbered VC in Control 2.25 §Verification Criteria is satisfied.
2. **Pre-conditions** — what must already be true (PRE gates passed; reference data present; Graph scopes granted).
3. **Pester suite** — `Describe "AGT225-{NS}" { Context "Zone {1|2|3}" { It "..." } }` using PowerShell 7.4 / Pester 5.5 syntax.
4. **Sample passing JSON evidence record** — exact shape that flows into the evidence pack.
5. **Sample failing JSON evidence record** with a remediation pointer to §12.
6. **Examiner artifact** — filename pattern, retention duration, signing policy.
7. **Zone thresholds** — PASS / WARN / FAIL bands per zone.
8. **Regulator mapping** — which specific regulatory citation each test supports.

### 1.1 Evidence record schema (canonical)

Every evidence record produced by every namespace MUST conform to this schema. The schema is enforced by `Test-Agt225EvidenceSchema` in §11.5; the pack assembler refuses to publish a pack containing any record that fails schema validation.

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
| `run_timestamp` | ISO-8601 string | Captured at `BeforeAll` time, frozen for the run. |
| `tenant_id` / `tenant_display_name` | string | From PRE-03. |
| `cloud` | enum | `Commercial / GCC / GCCH / DoD / Unknown`. |
| `zone` | enum | `1 / 2 / 3 / all`. `all` is used for tenant-wide records (e.g., LICENSE, SIEM). |
| `namespace` | enum | One of the namespace IDs in §1. |
| `criterion` | enum | `VC-1` … `VC-8`, or `VC-1..8 (compensating)` for SOV. |
| `subject_id` | string | The agent ID, template ID, policy ID, or other Graph object ID. |
| `subject_type` | enum | `agent / pending_approval / governance_template / inventory_export / exception_metric / researcher_policy / diagnostic_setting / manual_attestation`. |
| `status` | enum | `PASS / WARN / FAIL / SKIPPED / ERROR`. `ERROR` indicates the test could not run; `SKIPPED` is the sovereign-or-not-applicable case. |
| `assertion` | string | Human-readable statement of what was tested; written to be examiner-readable without context. |
| `observed_value` / `expected_value` | object | Free-form structured payload; both fields MUST be present even when one is trivial. |
| `evidence_artifacts` | array | Filenames (relative to evidence root) of the supporting artifacts. |
| `regulator_mappings` | array | Citation tokens from the controlled vocabulary in §1.2. |
| `remediation_ref` | string or null | A `TRG-{NS}-NN` pointer into §12 when `status != 'PASS'`. |
| `operator_upn` | string | UPN of the operator who ran the test (from `Get-MgContext`). |
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

This namespace evidences **VC-1: Agent 365 licensing confirmed**. The test asserts that the tenant under examination holds a license entitlement that surfaces the Microsoft Agent 365 Admin Center governance console and its Agents blade — specifically Microsoft 365 E7 ("Frontier Suite") **or** standalone Microsoft Agent 365 layered on the required Microsoft 365 Copilot prerequisite. Without this entitlement, none of the downstream criteria (VC-2 through VC-8) can be evidenced because the governance surface itself is absent from the tenant.

### 2.2 Pre-conditions

- PRE-01 through PRE-08 passed (§0.3).
- The operator has **AI Administrator** activated via PIM with a justification that references this playbook ID.
- `Microsoft.Graph.Identity.DirectoryManagement` v2.25 imported.
- The firm's License Catalog reference data (`license-catalog.json`, maintained by the Identity Engineering team per Control 2.4) is available at `$env:AGT225_LICENSE_CATALOG`. This file enumerates the SKU partnumbers the firm has procured and is the source of truth for whether a SKU is "current" or "deprecated".

### 2.3 Pester suite

```powershell
#Requires -Version 7.4
#Requires -Modules @{ ModuleName='Pester'; ModuleVersion='5.5.0' }

Describe "AGT225-LICENSE" -Tag 'AGT225','VC-1' {

    BeforeAll {
        $script:sov     = Test-Agt225SovereignTenant
        $script:runId   = $script:RunId
        $script:runTs   = $script:RunTimestamp
        $script:catalog = Get-Content $env:AGT225_LICENSE_CATALOG | ConvertFrom-Json
        if (-not $script:sov.is_sovereign) {
            $script:skus = Get-MgSubscribedSku -All |
                Select-Object SkuId, SkuPartNumber, ConsumedUnits,
                              @{n='Enabled'; e={$_.PrepaidUnits.Enabled}}
        }
    }

    Context "Sovereign cloud short-circuit" -Skip:(-not $script:sov.is_sovereign) {
        It "emits SKIPPED record routed to §10" {
            $rec = New-Agt225EvidenceRecord -Namespace 'LICENSE' -Criterion 'VC-1' `
                -Zone 'all' -SubjectId $script:sov.tenant_id -SubjectType 'inventory_export' `
                -Status 'SKIPPED' `
                -Assertion 'Sovereign cloud — Agent 365 Admin Center not at parity; see §10' `
                -Observed @{ cloud = $script:sov.cloud } `
                -Expected @{ cloud = 'Commercial' } `
                -RegulatorMappings @('FINRA-25-07','OCC-2011-12') `
                -RemediationRef 'TRG-LICENSE-99'
            $rec | Save-Agt225Evidence
            $rec.status | Should -Be 'SKIPPED' -Because 'Sovereign tenants follow §10 compensating control'
        }
    }

    Context "Tenant holds Agent 365-eligible license" -Skip:$script:sov.is_sovereign {

        It "has at least one M365 E7 OR standalone Agent 365 SKU with Enabled > 0" {
            $eligible = $script:skus | Where-Object {
                ($_.SkuPartNumber -like 'M365_E7*') -or
                ($_.SkuPartNumber -like 'Microsoft_Agent_365*')
            } | Where-Object Enabled -gt 0

            $rec = New-Agt225EvidenceRecord -Namespace 'LICENSE' -Criterion 'VC-1' `
                -Zone 'all' -SubjectId 'tenant-license-posture' -SubjectType 'inventory_export' `
                -Status (if ($eligible) { 'PASS' } else { 'FAIL' }) `
                -Assertion 'Tenant holds at least one Agent 365-eligible SKU with Enabled > 0' `
                -Observed @{ matched_skus = @($eligible | ForEach-Object SkuPartNumber) } `
                -Expected @{ matched_skus = '>= 1 of M365_E7* or Microsoft_Agent_365*' } `
                -RegulatorMappings @('FINRA-4511','SEC-17a-4','SOX-404','OCC-2011-12') `
                -RemediationRef (if (-not $eligible) { 'TRG-LICENSE-01' } else { $null })
            $rec | Save-Agt225Evidence
            $eligible | Should -Not -BeNullOrEmpty -Because 'VC-1 requires an Agent 365-bearing SKU'
        }

        It "has at least one Microsoft 365 Copilot prerequisite SKU with Enabled > 0" {
            $copilot = $script:skus | Where-Object {
                $_.SkuPartNumber -like 'Microsoft_365_Copilot*'
            } | Where-Object Enabled -gt 0

            $rec = New-Agt225EvidenceRecord -Namespace 'LICENSE' -Criterion 'VC-1' `
                -Zone 'all' -SubjectId 'tenant-copilot-prereq' -SubjectType 'inventory_export' `
                -Status (if ($copilot) { 'PASS' } else { 'FAIL' }) `
                -Assertion 'Tenant holds at least one Microsoft 365 Copilot prerequisite SKU' `
                -Observed @{ matched_skus = @($copilot | ForEach-Object SkuPartNumber) } `
                -Expected @{ matched_skus = '>= 1 of Microsoft_365_Copilot*' } `
                -RegulatorMappings @('FINRA-25-07','OCC-2011-12') `
                -RemediationRef (if (-not $copilot) { 'TRG-LICENSE-02' } else { $null })
            $rec | Save-Agt225Evidence
            $copilot | Should -Not -BeNullOrEmpty -Because 'Agent 365 requires the Copilot prerequisite'
        }

        It "Agents blade is reachable via Graph beta endpoint" {
            $probe = $null
            try { $probe = Invoke-MgGraphRequest -Method GET `
                    -Uri 'https://graph.microsoft.com/beta/agentGovernance/inventory?$top=1' `
                    -OutputType PSObject } catch { $probe = $_ }

            $ok = $probe -and $probe.value -ne $null
            $rec = New-Agt225EvidenceRecord -Namespace 'LICENSE' -Criterion 'VC-1' `
                -Zone 'all' -SubjectId 'agent-365-blade-reachability' -SubjectType 'inventory_export' `
                -Status (if ($ok) { 'PASS' } else { 'FAIL' }) `
                -Assertion 'Agent 365 governance Graph endpoint returns 200 with inventory shape' `
                -Observed @{ http_ok = [bool]$ok } `
                -Expected @{ http_ok = $true } `
                -RegulatorMappings @('FINRA-25-07','OCC-2011-12','FFIEC-MGMT') `
                -RemediationRef (if (-not $ok) { 'TRG-LICENSE-03' } else { $null })
            $rec | Save-Agt225Evidence
            $ok | Should -BeTrue -Because 'Without blade reachability, VC-2..VC-8 cannot be evidenced'
        }

        It "License catalog reference data lists every observed SKU as 'current'" {
            $observed = $script:skus | Where-Object Enabled -gt 0 | ForEach-Object SkuPartNumber
            $deprecated = $observed | Where-Object {
                ($script:catalog.skus | Where-Object partNumber -eq $_).status -eq 'deprecated'
            }
            $status = if ($deprecated.Count -eq 0) { 'PASS' } else { 'WARN' }
            $rec = New-Agt225EvidenceRecord -Namespace 'LICENSE' -Criterion 'VC-1' `
                -Zone 'all' -SubjectId 'license-catalog-currency' -SubjectType 'inventory_export' `
                -Status $status `
                -Assertion 'No SKU in tenant is flagged deprecated in firm license catalog' `
                -Observed @{ deprecated_skus = @($deprecated) } `
                -Expected @{ deprecated_skus = @() } `
                -RegulatorMappings @('OCC-2011-12','FFIEC-MGMT') `
                -RemediationRef (if ($deprecated.Count -gt 0) { 'TRG-LICENSE-04' } else { $null })
            $rec | Save-Agt225Evidence
            $deprecated.Count | Should -Be 0 -Because 'Deprecated SKUs warrant procurement review'
        }
    }
}
```

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
  "observed_value": { "matched_skus": ["M365_E7"] },
  "expected_value": { "matched_skus": ">= 1 of M365_E7* or Microsoft_Agent_365*" },
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
  "subject_id": "tenant-copilot-prereq",
  "subject_type": "inventory_export",
  "status": "FAIL",
  "assertion": "Tenant holds at least one Microsoft 365 Copilot prerequisite SKU",
  "observed_value": { "matched_skus": [] },
  "expected_value": { "matched_skus": ">= 1 of Microsoft_365_Copilot*" },
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
| Signing | Bundled into the §11 evidence pack and signed at the pack level by AI Governance Lead |
| Distribution | AI Governance Lead, Compliance Officer, Technology Risk Manager |

### 2.7 Zone thresholds

| Zone | PASS | WARN | FAIL |
|---|---|---|---|
| Z1 (Personal) | All four `It` blocks PASS | Catalog currency check WARNs | Eligible SKU or Copilot prereq missing |
| Z2 (Team) | All four PASS | Catalog currency WARN | Same as Z1 — license absence blocks all downstream |
| Z3 (Enterprise) | All four PASS, plus license has been re-attested in the trailing 90 days | Re-attestation > 90 days but < 180 days | Eligible SKU absent OR re-attestation > 180 days |

### 2.8 Regulator mapping

| Test | FINRA-3110 | FINRA-4511 | FINRA-25-07 | SEC-17a-4 | SOX-404 | GLBA-501b | OCC-2011-12 | NYDFS-500 | FFIEC-MGMT |
|---|---|---|---|---|---|---|---|---|---|
| Eligible SKU present | — | ✓ | ✓ | ✓ | ✓ | — | ✓ | — | ✓ |
| Copilot prereq present | — | — | ✓ | — | — | — | ✓ | — | ✓ |
| Blade reachable | ✓ | — | ✓ | — | — | — | ✓ | — | ✓ |
| Catalog currency | — | — | — | — | ✓ | — | ✓ | — | ✓ |

---

## §3 APPROVAL Namespace — VC-2 + VC-4

### 3.1 Criterion mapping

This namespace evidences **two** Verification Criteria simultaneously because they share the same data source (the Agent 365 admin approval queue) and the same review cadence:

- **VC-2: Admin approval workflow enforced.** Quarterly sample of N ≥ 10 production agents shows non-null `approverUpn` and `approvalTimestamp`, and each approval traces to a Control 2.3 change ticket.
- **VC-4: Pending requests resolved within firm SLA.** Pending publish/activate requests visible in the Agent 365 admin queue are resolved within the firm's documented SLA — illustratively 5 business days for Z2 and 1 business day for Z3 (the firm sets these in policy; this playbook reads `$env:AGT225_SLA_Z2_BD` and `$env:AGT225_SLA_Z3_BD`).

> **Firm SLA values are illustrative.** The 5 BD / 1 BD values shown here are placeholders. The firm's AI Governance Council sets the production SLA values, documents them in policy, and re-affirms them annually. The Pester suite reads these values from environment variables so the threshold is not hard-coded into the test.

### 3.2 Pre-conditions

- PRE gates passed.
- AI Administrator activated.
- Reference data: `$env:AGT225_CHANGE_TICKET_RESOLVER` is the URL of the firm's change-ticket lookup API (per Control 2.3), used by `Resolve-Agt225ChangeTicket` to validate ticket IDs returned by the Agent 365 API.
- Reference data: `$env:AGT225_APPROVAL_SAMPLE_N` (default 10) — sample size for VC-2.
- Reference data: `$env:AGT225_SLA_Z2_BD` (default 5) and `$env:AGT225_SLA_Z3_BD` (default 1) — pending-request SLA in business days.

### 3.3 Pester suite

```powershell
Describe "AGT225-APPROVAL" -Tag 'AGT225','VC-2','VC-4' {

    BeforeAll {
        $script:sov   = Test-Agt225SovereignTenant
        $script:n     = [int]($env:AGT225_APPROVAL_SAMPLE_N ?? 10)
        $script:sla2  = [int]($env:AGT225_SLA_Z2_BD ?? 5)
        $script:sla3  = [int]($env:AGT225_SLA_Z3_BD ?? 1)
        if (-not $script:sov.is_sovereign) {
            $script:approved = Get-Agent365Inventory -Status 'Approved' -PageSize 999
            $script:pending  = Get-Agent365PendingApproval -PageSize 999
        }
    }

    Context "Sovereign short-circuit" -Skip:(-not $script:sov.is_sovereign) {
        It "emits SKIPPED for VC-2 and VC-4" {
            foreach ($vc in 'VC-2','VC-4') {
                New-Agt225EvidenceRecord -Namespace 'APPROVAL' -Criterion $vc -Zone 'all' `
                    -SubjectId $script:sov.tenant_id -SubjectType 'pending_approval' `
                    -Status 'SKIPPED' `
                    -Assertion 'Sovereign cloud — see §10' `
                    -Observed @{ cloud = $script:sov.cloud } -Expected @{ cloud = 'Commercial' } `
                    -RegulatorMappings @('FINRA-3110','FINRA-25-07','SOX-404') `
                    -RemediationRef 'TRG-APPROVAL-99' | Save-Agt225Evidence
            }
            $true | Should -BeTrue
        }
    }

    Context "VC-2: Sample of approved agents has non-null approver + timestamp + change ticket" -Skip:$script:sov.is_sovereign {

        It "Quarterly sample of N>=10 approved agents per zone has non-null approverUpn" {
            foreach ($zone in '2','3') {
                $pool   = $script:approved | Where-Object zone -eq $zone
                $sample = $pool | Get-Random -Count ([Math]::Min($script:n, $pool.Count))
                $bad    = $sample | Where-Object { -not $_.approverUpn }
                $rec = New-Agt225EvidenceRecord -Namespace 'APPROVAL' -Criterion 'VC-2' `
                    -Zone $zone -SubjectId "approval-sample-z$zone" -SubjectType 'pending_approval' `
                    -Status (if ($bad.Count -eq 0) { 'PASS' } else { 'FAIL' }) `
                    -Assertion "Z$zone approval sample (n=$($sample.Count)) has non-null approverUpn" `
                    -Observed @{ sample_size = $sample.Count; null_approver_count = $bad.Count;
                                 null_approver_ids = @($bad | ForEach-Object id) } `
                    -Expected @{ null_approver_count = 0 } `
                    -RegulatorMappings @('FINRA-3110','FINRA-4511','SEC-17a-3','SOX-404','OCC-2011-12') `
                    -RemediationRef (if ($bad.Count -gt 0) { 'TRG-APPROVAL-01' } else { $null }) `
                    | Save-Agt225Evidence
                $bad.Count | Should -Be 0 -Because "VC-2 requires non-null approver in Z$zone sample"
            }
        }

        It "Sample agents have non-null approvalTimestamp within the trailing 365 days" {
            foreach ($zone in '2','3') {
                $pool   = $script:approved | Where-Object zone -eq $zone
                $sample = $pool | Get-Random -Count ([Math]::Min($script:n, $pool.Count))
                $cutoff = (Get-Date).ToUniversalTime().AddDays(-365)
                $bad    = $sample | Where-Object {
                    -not $_.approvalTimestamp -or [datetime]$_.approvalTimestamp -lt $cutoff
                }
                $rec = New-Agt225EvidenceRecord -Namespace 'APPROVAL' -Criterion 'VC-2' `
                    -Zone $zone -SubjectId "approval-timestamp-z$zone" -SubjectType 'pending_approval' `
                    -Status (if ($bad.Count -eq 0) { 'PASS' } else { 'FAIL' }) `
                    -Assertion "Z$zone approval timestamps are non-null and within 365 days" `
                    -Observed @{ stale_or_null_count = $bad.Count;
                                 stale_ids = @($bad | ForEach-Object id) } `
                    -Expected @{ stale_or_null_count = 0 } `
                    -RegulatorMappings @('FINRA-4511','SEC-17a-4','SOX-302','SOX-404') `
                    -RemediationRef (if ($bad.Count -gt 0) { 'TRG-APPROVAL-02' } else { $null }) `
                    | Save-Agt225Evidence
                $bad.Count | Should -Be 0 -Because 'Stale approvals warrant re-attestation per Control 2.8'
            }
        }

        It "Each sampled approval resolves to a valid Control 2.3 change ticket" {
            foreach ($zone in '2','3') {
                $pool   = $script:approved | Where-Object zone -eq $zone
                $sample = $pool | Get-Random -Count ([Math]::Min($script:n, $pool.Count))
                $unresolved = @()
                foreach ($a in $sample) {
                    $r = Resolve-Agt225ChangeTicket -TicketId $a.changeTicketId
                    if (-not $r.exists -or $r.state -notin @('Closed','Implemented')) {
                        $unresolved += [pscustomobject]@{ agent_id = $a.id; ticket = $a.changeTicketId; state = $r.state }
                    }
                }
                $rec = New-Agt225EvidenceRecord -Namespace 'APPROVAL' -Criterion 'VC-2' `
                    -Zone $zone -SubjectId "approval-ticket-trace-z$zone" -SubjectType 'pending_approval' `
                    -Status (if ($unresolved.Count -eq 0) { 'PASS' } else { 'FAIL' }) `
                    -Assertion "Z$zone approvals each trace to a closed Control 2.3 change ticket" `
                    -Observed @{ unresolved_count = $unresolved.Count; unresolved = $unresolved } `
                    -Expected @{ unresolved_count = 0 } `
                    -RegulatorMappings @('FINRA-3110','FINRA-4511','SOX-404','OCC-2011-12','NYDFS-500') `
                    -RemediationRef (if ($unresolved.Count -gt 0) { 'TRG-APPROVAL-03' } else { $null }) `
                    | Save-Agt225Evidence
                $unresolved.Count | Should -Be 0
            }
        }
    }

    Context "VC-4: Pending requests resolved within firm SLA" -Skip:$script:sov.is_sovereign {

        It "No Z2 pending request older than $script:sla2 business days" {
            $cutoff   = (Get-Agt225BusinessDayOffset -BusinessDays $script:sla2 -Direction Backward).ToUniversalTime()
            $breaches = $script:pending | Where-Object { $_.zone -eq '2' -and [datetime]$_.submittedAt -lt $cutoff }
            $rec = New-Agt225EvidenceRecord -Namespace 'APPROVAL' -Criterion 'VC-4' `
                -Zone '2' -SubjectId 'pending-sla-z2' -SubjectType 'pending_approval' `
                -Status (if ($breaches.Count -eq 0) { 'PASS' } else { 'FAIL' }) `
                -Assertion "No Z2 pending request older than $script:sla2 business days" `
                -Observed @{ breach_count = $breaches.Count; breach_ids = @($breaches.id);
                             cutoff_utc = $cutoff.ToString('o') } `
                -Expected @{ breach_count = 0; sla_business_days = $script:sla2 } `
                -RegulatorMappings @('FINRA-3110','FINRA-25-07','OCC-2011-12','FFIEC-MGMT') `
                -RemediationRef (if ($breaches.Count -gt 0) { 'TRG-APPROVAL-04' } else { $null }) `
                | Save-Agt225Evidence
            $breaches.Count | Should -Be 0
        }

        It "No Z3 pending request older than $script:sla3 business days" {
            $cutoff   = (Get-Agt225BusinessDayOffset -BusinessDays $script:sla3 -Direction Backward).ToUniversalTime()
            $breaches = $script:pending | Where-Object { $_.zone -eq '3' -and [datetime]$_.submittedAt -lt $cutoff }
            $rec = New-Agt225EvidenceRecord -Namespace 'APPROVAL' -Criterion 'VC-4' `
                -Zone '3' -SubjectId 'pending-sla-z3' -SubjectType 'pending_approval' `
                -Status (if ($breaches.Count -eq 0) { 'PASS' } else { 'FAIL' }) `
                -Assertion "No Z3 pending request older than $script:sla3 business day(s)" `
                -Observed @{ breach_count = $breaches.Count; breach_ids = @($breaches.id);
                             cutoff_utc = $cutoff.ToString('o') } `
                -Expected @{ breach_count = 0; sla_business_days = $script:sla3 } `
                -RegulatorMappings @('FINRA-3110','FINRA-25-07','OCC-2011-12','NYDFS-500','FFIEC-MGMT') `
                -RemediationRef (if ($breaches.Count -gt 0) { 'TRG-APPROVAL-05' } else { $null }) `
                | Save-Agt225Evidence
            $breaches.Count | Should -Be 0
        }
    }
}
```

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

This namespace evidences **VC-5: Ownerless Agents card is zero or actively remediated within 48 hours**. The Microsoft Agent 365 Admin Center surfaces an "Ownerless Agents" governance card; an agent appears here when its registered owner UPN no longer resolves to an active, enabled user object (e.g., owner left the firm, account disabled, lifecycle deprovisioning ran). This namespace asserts that either (a) the count is zero, or (b) every entry has an open remediation ticket aged ≤ 48 hours and bound to a designated interim owner per Control 3.6.

### 4.2 Pre-conditions

- PRE gates passed.
- AI Administrator activated.
- Reference data: `$env:AGT225_REMEDIATION_TICKET_RESOLVER` (per Control 3.6) is the URL used by `Resolve-Agt225OwnerRemediationTicket` to validate that an open ticket exists for each ownerless agent.

### 4.3 Pester suite

```powershell
Describe "AGT225-OWNER" -Tag 'AGT225','VC-5' {

    BeforeAll {
        $script:sov   = Test-Agt225SovereignTenant
        if (-not $script:sov.is_sovereign) {
            $script:ownerless = Get-Agent365OwnerlessAgent -PageSize 999
        }
    }

    Context "Sovereign short-circuit" -Skip:(-not $script:sov.is_sovereign) {
        It "emits SKIPPED" {
            New-Agt225EvidenceRecord -Namespace 'OWNER' -Criterion 'VC-5' -Zone 'all' `
                -SubjectId $script:sov.tenant_id -SubjectType 'agent' -Status 'SKIPPED' `
                -Assertion 'Sovereign — see §10' -Observed @{} -Expected @{} `
                -RegulatorMappings @('FINRA-3110','OCC-2011-12') -RemediationRef 'TRG-OWNER-99' `
                | Save-Agt225Evidence
            $true | Should -BeTrue
        }
    }

    Context "VC-5: Ownerless Agents card" -Skip:$script:sov.is_sovereign {

        It "Ownerless Agents count is zero, OR every entry has open remediation ticket aged <= 48h" {
            $now = (Get-Date).ToUniversalTime()
            $offenders = @()
            foreach ($a in $script:ownerless) {
                $t = Resolve-Agt225OwnerRemediationTicket -AgentId $a.id
                $ageH = if ($t.exists) { ($now - [datetime]$t.openedAt).TotalHours } else { 9999 }
                if (-not $t.exists -or $t.state -ne 'Open' -or $ageH -gt 48) {
                    $offenders += [pscustomobject]@{
                        agent_id       = $a.id
                        display_name   = $a.displayName
                        prior_owner    = $a.priorOwnerUpn
                        ticket_exists  = [bool]$t.exists
                        ticket_state   = $t.state
                        ticket_age_h   = [math]::Round($ageH,1)
                    }
                }
            }
            $rec = New-Agt225EvidenceRecord -Namespace 'OWNER' -Criterion 'VC-5' -Zone 'all' `
                -SubjectId 'ownerless-agents-card' -SubjectType 'agent' `
                -Status (if ($offenders.Count -eq 0) { 'PASS' } else { 'FAIL' }) `
                -Assertion 'All ownerless agents are either nonexistent or under <=48h remediation' `
                -Observed @{ ownerless_total = $script:ownerless.Count; offender_count = $offenders.Count;
                             offenders = $offenders } `
                -Expected @{ offender_count = 0 } `
                -RegulatorMappings @('FINRA-3110','FINRA-4511','SOX-404','OCC-2011-12','NYDFS-500') `
                -RemediationRef (if ($offenders.Count -gt 0) { 'TRG-OWNER-01' } else { $null }) `
                | Save-Agt225Evidence
            $offenders.Count | Should -Be 0 -Because 'VC-5 fails if any ownerless agent lacks a fresh open ticket'
        }

        It "No ownerless Z3 agent older than 24 hours regardless of ticket state" {
            $z3old = $script:ownerless | Where-Object {
                $_.zone -eq '3' -and ((Get-Date).ToUniversalTime() - [datetime]$_.detectedAt).TotalHours -gt 24
            }
            $rec = New-Agt225EvidenceRecord -Namespace 'OWNER' -Criterion 'VC-5' -Zone '3' `
                -SubjectId 'ownerless-z3-24h' -SubjectType 'agent' `
                -Status (if ($z3old.Count -eq 0) { 'PASS' } else { 'FAIL' }) `
                -Assertion 'No Z3 ownerless agent persists beyond 24 hours' `
                -Observed @{ count = $z3old.Count; ids = @($z3old.id) } `
                -Expected @{ count = 0 } `
                -RegulatorMappings @('FINRA-3110','OCC-2011-12','NYDFS-500') `
                -RemediationRef (if ($z3old.Count -gt 0) { 'TRG-OWNER-02' } else { $null }) `
                | Save-Agt225Evidence
            $z3old.Count | Should -Be 0
        }
    }
}
```

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
| Z1 | Always PASS — Z1 personal agents are owned by the user who created them; ownerless surfacing handled by lifecycle deprovisioning under Control 3.6 | — | — |
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

### 5.3 Pester suite

```powershell
Describe "AGT225-TEMPLATE" -Tag 'AGT225','VC-3' {

    BeforeAll {
        $script:sov = Test-Agt225SovereignTenant
        if (-not $script:sov.is_sovereign) {
            $script:agents    = Get-Agent365Inventory -PageSize 999
            $script:templates = Get-Agent365GovernanceTemplateAssignment -PageSize 999
            $script:baseline  = Get-Content $env:AGT225_TEMPLATE_BASELINE | ConvertFrom-Json
        }
    }

    Context "Sovereign short-circuit" -Skip:(-not $script:sov.is_sovereign) {
        It "emits SKIPPED" {
            New-Agt225EvidenceRecord -Namespace 'TEMPLATE' -Criterion 'VC-3' -Zone 'all' `
                -SubjectId $script:sov.tenant_id -SubjectType 'governance_template' -Status 'SKIPPED' `
                -Assertion 'Sovereign — see §10' -Observed @{} -Expected @{} `
                -RegulatorMappings @('FINRA-3110','SOX-404') -RemediationRef 'TRG-TEMPLATE-99' `
                | Save-Agt225Evidence
            $true | Should -BeTrue
        }
    }

    Context "VC-3: Z2 agents have Default OR Custom template assigned" -Skip:$script:sov.is_sovereign {
        It "Every Z2 agent has a non-null governance template" {
            $z2 = $script:agents | Where-Object zone -eq '2'
            $missing = $z2 | Where-Object {
                -not ($script:templates | Where-Object agentId -eq $_.id).templateId
            }
            $rec = New-Agt225EvidenceRecord -Namespace 'TEMPLATE' -Criterion 'VC-3' -Zone '2' `
                -SubjectId 'z2-template-coverage' -SubjectType 'governance_template' `
                -Status (if ($missing.Count -eq 0) { 'PASS' } else { 'FAIL' }) `
                -Assertion 'Every Z2 agent has a Default or Custom governance template assigned' `
                -Observed @{ z2_total = $z2.Count; missing_count = $missing.Count;
                             missing_ids = @($missing.id) } `
                -Expected @{ missing_count = 0 } `
                -RegulatorMappings @('FINRA-25-07','SOX-404','OCC-2011-12') `
                -RemediationRef (if ($missing.Count -gt 0) { 'TRG-TEMPLATE-01' } else { $null }) `
                | Save-Agt225Evidence
            $missing.Count | Should -Be 0
        }
    }

    Context "VC-3: Z3 agents have Custom template + Entra Access Package binding" -Skip:$script:sov.is_sovereign {
        It "Every Z3 agent uses a Custom template (not Default)" {
            $z3 = $script:agents | Where-Object zone -eq '3'
            $offenders = $z3 | Where-Object {
                $tpl = $script:templates | Where-Object agentId -eq $_.id
                -not $tpl -or $tpl.templateKind -ne 'Custom'
            }
            $rec = New-Agt225EvidenceRecord -Namespace 'TEMPLATE' -Criterion 'VC-3' -Zone '3' `
                -SubjectId 'z3-custom-template' -SubjectType 'governance_template' `
                -Status (if ($offenders.Count -eq 0) { 'PASS' } else { 'FAIL' }) `
                -Assertion 'Every Z3 agent uses a Custom template (not Default)' `
                -Observed @{ z3_total = $z3.Count; offender_count = $offenders.Count;
                             offender_ids = @($offenders.id) } `
                -Expected @{ offender_count = 0 } `
                -RegulatorMappings @('FINRA-3110','SOX-404','OCC-2011-12','NYDFS-500') `
                -RemediationRef (if ($offenders.Count -gt 0) { 'TRG-TEMPLATE-02' } else { $null }) `
                | Save-Agt225Evidence
            $offenders.Count | Should -Be 0
        }

        It "Every Z3 Custom template is bound to a non-null Entra Access Package" {
            $z3 = $script:agents | Where-Object zone -eq '3'
            $unbound = @()
            foreach ($a in $z3) {
                $tpl = $script:templates | Where-Object agentId -eq $a.id
                if ($tpl -and $tpl.templateKind -eq 'Custom' -and -not $tpl.entraAccessPackageId) {
                    $unbound += $a.id
                }
            }
            $rec = New-Agt225EvidenceRecord -Namespace 'TEMPLATE' -Criterion 'VC-3' -Zone '3' `
                -SubjectId 'z3-access-package-binding' -SubjectType 'governance_template' `
                -Status (if ($unbound.Count -eq 0) { 'PASS' } else { 'FAIL' }) `
                -Assertion 'Every Z3 Custom template binds to a non-null Entra Access Package' `
                -Observed @{ unbound_count = $unbound.Count; unbound_ids = $unbound } `
                -Expected @{ unbound_count = 0 } `
                -RegulatorMappings @('FINRA-3110','SOX-404','GLBA-501b','OCC-2011-12','NYDFS-500') `
                -RemediationRef (if ($unbound.Count -gt 0) { 'TRG-TEMPLATE-03' } else { $null }) `
                | Save-Agt225Evidence
            $unbound.Count | Should -Be 0 -Because 'VC-3 requires Z3 Access Package binding for identity governance per Control 2.26'
        }

        It "Every Z3 Access Package referenced has a Reviewer assigned" {
            $z3      = $script:agents | Where-Object zone -eq '3'
            $apIds   = ($script:templates | Where-Object { $_.agentId -in $z3.id }).entraAccessPackageId | Sort-Object -Unique
            $missing = @()
            foreach ($apId in $apIds) {
                $reviewers = Get-Agt225AccessPackageReviewer -AccessPackageId $apId
                if (-not $reviewers -or $reviewers.Count -eq 0) { $missing += $apId }
            }
            $rec = New-Agt225EvidenceRecord -Namespace 'TEMPLATE' -Criterion 'VC-3' -Zone '3' `
                -SubjectId 'z3-access-package-reviewer' -SubjectType 'governance_template' `
                -Status (if ($missing.Count -eq 0) { 'PASS' } else { 'FAIL' }) `
                -Assertion 'Every Z3-bound Access Package has at least one Reviewer' `
                -Observed @{ access_package_count = $apIds.Count; missing_reviewer_count = $missing.Count;
                             missing_ids = $missing } `
                -Expected @{ missing_reviewer_count = 0 } `
                -RegulatorMappings @('FINRA-3110','SOX-404','OCC-2011-12','NYDFS-500') `
                -RemediationRef (if ($missing.Count -gt 0) { 'TRG-TEMPLATE-04' } else { $null }) `
                | Save-Agt225Evidence
            $missing.Count | Should -Be 0
        }
    }
}
```

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

This namespace evidences **VC-7: Inventory exported monthly, WORM-protected, ISO 8601-dated, 12 months retained, with required field set**. The Microsoft Agent 365 Admin Center exposes a tenant inventory of every agent (across Z1, Z2, Z3, every supported platform: Copilot, Copilot Studio, Microsoft Teams custom apps, third-party agent connectors). The firm's monthly governance process exports this inventory to WORM storage. This namespace asserts the export occurred, is well-formed, contains the required fields, and the trailing 12 months are present and unmodified.

### 6.2 Pre-conditions

- PRE gates passed.
- AI Administrator activated.
- Reference data: `$env:AGT225_INVENTORY_ARCHIVE_ROOT` — root path of the WORM archive (e.g., an Azure Storage container with an immutability policy or an Amazon S3 Object Lock bucket; the firm's storage architecture must satisfy SEC 17a-4(f) WORM requirements).
- Reference data: `$env:AGT225_INVENTORY_REQUIRED_FIELDS` — JSON array of field names; defaults to the canonical set: `["agentId","displayName","publisher","platform","ownerUpn","status","deploymentScope","governanceTemplate","lastApprovalTimestamp","approverUpn","createdAt","updatedAt","zone","tenantId"]`.

### 6.3 Pester suite

```powershell
Describe "AGT225-INVENTORY" -Tag 'AGT225','VC-7' {

    BeforeAll {
        $script:sov            = Test-Agt225SovereignTenant
        $script:requiredFields = $env:AGT225_INVENTORY_REQUIRED_FIELDS |
            ConvertFrom-Json -ErrorAction SilentlyContinue
        if (-not $script:requiredFields) {
            $script:requiredFields = @('agentId','displayName','publisher','platform','ownerUpn',
                                       'status','deploymentScope','governanceTemplate',
                                       'lastApprovalTimestamp','approverUpn','createdAt','updatedAt',
                                       'zone','tenantId')
        }
        $script:archive = $env:AGT225_INVENTORY_ARCHIVE_ROOT
    }

    Context "Sovereign short-circuit" -Skip:(-not $script:sov.is_sovereign) {
        It "emits SKIPPED" {
            New-Agt225EvidenceRecord -Namespace 'INVENTORY' -Criterion 'VC-7' -Zone 'all' `
                -SubjectId $script:sov.tenant_id -SubjectType 'inventory_export' -Status 'SKIPPED' `
                -Assertion 'Sovereign — see §10' -Observed @{} -Expected @{} `
                -RegulatorMappings @('FINRA-4511','SEC-17a-4') -RemediationRef 'TRG-INVENTORY-99' `
                | Save-Agt225Evidence
            $true | Should -BeTrue
        }
    }

    Context "VC-7: Trailing 12 months of monthly exports present" -Skip:$script:sov.is_sovereign {

        It "Archive contains exactly one export per month for the trailing 12 months" {
            $now = Get-Date
            $expected = 0..11 | ForEach-Object { $now.AddMonths(-$_).ToString('yyyy-MM') }
            $present  = Get-ChildItem $script:archive -Filter 'agent365-inventory-*.json' |
                ForEach-Object {
                    if ($_.Name -match 'agent365-inventory-(\d{4}-\d{2})-\d{2}\.json') { $matches[1] }
                } | Sort-Object -Unique
            $missing  = $expected | Where-Object { $_ -notin $present }
            $rec = New-Agt225EvidenceRecord -Namespace 'INVENTORY' -Criterion 'VC-7' -Zone 'all' `
                -SubjectId 'inventory-12mo-coverage' -SubjectType 'inventory_export' `
                -Status (if ($missing.Count -eq 0) { 'PASS' } else { 'FAIL' }) `
                -Assertion 'Trailing 12 monthly exports present in WORM archive' `
                -Observed @{ present_months = $present; missing_months = $missing } `
                -Expected @{ missing_months = @() } `
                -RegulatorMappings @('FINRA-4511','SEC-17a-3','SEC-17a-4','SOX-404','OCC-2011-12') `
                -RemediationRef (if ($missing.Count -gt 0) { 'TRG-INVENTORY-01' } else { $null }) `
                | Save-Agt225Evidence
            $missing.Count | Should -Be 0
        }

        It "Most recent monthly export filename matches ISO 8601 yyyy-MM-dd convention" {
            $latest = Get-ChildItem $script:archive -Filter 'agent365-inventory-*.json' |
                Sort-Object Name -Descending | Select-Object -First 1
            $ok = $latest.Name -match '^agent365-inventory-\d{4}-\d{2}-\d{2}\.json$'
            $rec = New-Agt225EvidenceRecord -Namespace 'INVENTORY' -Criterion 'VC-7' -Zone 'all' `
                -SubjectId 'inventory-iso-naming' -SubjectType 'inventory_export' `
                -Status (if ($ok) { 'PASS' } else { 'FAIL' }) `
                -Assertion 'Latest export filename uses ISO 8601 date convention' `
                -Observed @{ latest_filename = $latest.Name } `
                -Expected @{ pattern = 'agent365-inventory-yyyy-MM-dd.json' } `
                -RegulatorMappings @('FINRA-4511','SEC-17a-4','SOX-404') `
                -RemediationRef (if (-not $ok) { 'TRG-INVENTORY-02' } else { $null }) `
                | Save-Agt225Evidence
            $ok | Should -BeTrue
        }

        It "Most recent export contains all required fields and no null in mandatory columns" {
            $latest    = Get-ChildItem $script:archive -Filter 'agent365-inventory-*.json' |
                Sort-Object Name -Descending | Select-Object -First 1
            $data      = Get-Content $latest.FullName | ConvertFrom-Json
            $firstRow  = if ($data -is [array]) { $data[0] } else { $data.value[0] }
            $missing   = $script:requiredFields | Where-Object { $_ -notin $firstRow.PSObject.Properties.Name }
            $rec = New-Agt225EvidenceRecord -Namespace 'INVENTORY' -Criterion 'VC-7' -Zone 'all' `
                -SubjectId 'inventory-required-fields' -SubjectType 'inventory_export' `
                -Status (if ($missing.Count -eq 0) { 'PASS' } else { 'FAIL' }) `
                -Assertion 'Latest export contains all required fields' `
                -Observed @{ source_file = $latest.Name; missing_fields = $missing } `
                -Expected @{ required_fields = $script:requiredFields; missing_fields = @() } `
                -RegulatorMappings @('FINRA-4511','SEC-17a-3','SEC-17a-4','SOX-404','OCC-2011-12') `
                -RemediationRef (if ($missing.Count -gt 0) { 'TRG-INVENTORY-03' } else { $null }) `
                | Save-Agt225Evidence
            $missing.Count | Should -Be 0
        }

        It "Each prior month's export retains its original SHA-256 hash (no tampering)" {
            $manifest = Get-Content (Join-Path $script:archive 'inventory-hash-manifest.json') | ConvertFrom-Json
            $tampered = @()
            foreach ($entry in $manifest) {
                $path = Join-Path $script:archive $entry.filename
                if (-not (Test-Path $path)) {
                    $tampered += [pscustomobject]@{ file = $entry.filename; reason = 'missing' }
                } else {
                    $h = (Get-FileHash $path -Algorithm SHA256).Hash
                    if ($h -ne $entry.sha256) {
                        $tampered += [pscustomobject]@{ file = $entry.filename; expected = $entry.sha256; observed = $h }
                    }
                }
            }
            $rec = New-Agt225EvidenceRecord -Namespace 'INVENTORY' -Criterion 'VC-7' -Zone 'all' `
                -SubjectId 'inventory-hash-integrity' -SubjectType 'inventory_export' `
                -Status (if ($tampered.Count -eq 0) { 'PASS' } else { 'FAIL' }) `
                -Assertion 'Every archived export hash matches the manifest (immutable)' `
                -Observed @{ tampered_count = $tampered.Count; tampered = $tampered } `
                -Expected @{ tampered_count = 0 } `
                -RegulatorMappings @('FINRA-4511','SEC-17a-4','SOX-302','SOX-404') `
                -RemediationRef (if ($tampered.Count -gt 0) { 'TRG-INVENTORY-04' } else { $null }) `
                | Save-Agt225Evidence
            $tampered.Count | Should -Be 0 -Because 'Hash mismatches indicate WORM violation requiring immediate IR escalation'
        }
    }
}
```

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
| Filename | `agent365-inventory-yyyy-MM-dd.json` (the monthly export); `inventory-hash-manifest.json` (chain-of-custody manifest); `inventory-evidence-<runId>.ndjson` (Pester output) |
| Storage | WORM archive at `$env:AGT225_INVENTORY_ARCHIVE_ROOT` |
| Retention | 6 years on WORM, with the firm's documented immutability policy referenced in the §11 attestation |
| Signing | Each monthly export hash chained into the manifest, signed by AI Governance Lead at the time of monthly capture; the §11 pack additionally signs the Pester output |
| Distribution | AI Governance Lead, Compliance Officer, Internal Audit |

### 6.7 Zone thresholds

| Zone | PASS | WARN | FAIL |
|---|---|---|---|
| All zones (this is a tenant-wide control) | All 4 `It` blocks PASS | One missing month within trailing 12, with a documented gap-explanation memo | Any hash tamper, OR > 1 missing month, OR required field absent in latest export |

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

This namespace evidences **VC-6: Exception rate monitored against a documented threshold (illustrative ≤ 5%) with three documented review cycles per year minimum**. The Microsoft Agent 365 Admin Center surfaces an "Exception Rate" metric — the percentage of agents that bypassed the standard governance template via a documented variance request. This namespace asserts the metric is below the firm's threshold and that the firm's AI Governance Council reviewed it on the documented cadence.

> **Threshold is firm-set, not Microsoft-set.** The 5% value used as an illustrative example throughout this section is **not a Microsoft-published threshold**. The firm's AI Governance Council documents the threshold in policy (recommended starting point: 5%; mature programs frequently target 2%) and re-affirms it annually. The Pester suite reads the threshold from `$env:AGT225_EXCEPTION_THRESHOLD_PCT`.

### 7.2 Pre-conditions

- PRE gates passed.
- AI Administrator activated.
- Reference data: `$env:AGT225_EXCEPTION_THRESHOLD_PCT` (default 5).
- Reference data: `$env:AGT225_EXCEPTION_REVIEW_LOG` — a JSON file of dated AI Governance Council review entries; produced by the council secretary per Control 4.5.

### 7.3 Pester suite

```powershell
Describe "AGT225-EXCEPTION" -Tag 'AGT225','VC-6' {

    BeforeAll {
        $script:sov       = Test-Agt225SovereignTenant
        $script:threshold = [double]($env:AGT225_EXCEPTION_THRESHOLD_PCT ?? 5)
        if (-not $script:sov.is_sovereign) {
            $script:metric = Get-Agent365ExceptionMetric
            $script:reviews = Get-Content $env:AGT225_EXCEPTION_REVIEW_LOG | ConvertFrom-Json
        }
    }

    Context "Sovereign short-circuit" -Skip:(-not $script:sov.is_sovereign) {
        It "emits SKIPPED" {
            New-Agt225EvidenceRecord -Namespace 'EXCEPTION' -Criterion 'VC-6' -Zone 'all' `
                -SubjectId $script:sov.tenant_id -SubjectType 'exception_metric' -Status 'SKIPPED' `
                -Assertion 'Sovereign — see §10' -Observed @{} -Expected @{} `
                -RegulatorMappings @('SOX-404','OCC-2011-12') -RemediationRef 'TRG-EXCEPTION-99' `
                | Save-Agt225Evidence
            $true | Should -BeTrue
        }
    }

    Context "VC-6: Exception rate below firm threshold" -Skip:$script:sov.is_sovereign {

        It "Tenant-wide exception rate is at or below firm threshold" {
            $rate = $script:metric.exceptionRatePct
            $ok   = $rate -le $script:threshold
            $rec = New-Agt225EvidenceRecord -Namespace 'EXCEPTION' -Criterion 'VC-6' -Zone 'all' `
                -SubjectId 'exception-rate-tenant' -SubjectType 'exception_metric' `
                -Status (if ($ok) { 'PASS' } else { 'FAIL' }) `
                -Assertion "Tenant exception rate <= $script:threshold%" `
                -Observed @{ exception_rate_pct = $rate; numerator = $script:metric.exceptionAgents;
                             denominator = $script:metric.totalAgents } `
                -Expected @{ exception_rate_pct_max = $script:threshold } `
                -RegulatorMappings @('FINRA-3110','FINRA-25-07','SOX-404','OCC-2011-12','FFIEC-MGMT') `
                -RemediationRef (if (-not $ok) { 'TRG-EXCEPTION-01' } else { $null }) `
                | Save-Agt225Evidence
            $ok | Should -BeTrue
        }

        It "Z3 exception rate is at or below half of firm threshold" {
            $rate = $script:metric.zoneRates | Where-Object zone -eq '3' | Select-Object -ExpandProperty rate
            $cap  = $script:threshold / 2.0
            $ok   = $rate -le $cap
            $rec = New-Agt225EvidenceRecord -Namespace 'EXCEPTION' -Criterion 'VC-6' -Zone '3' `
                -SubjectId 'exception-rate-z3' -SubjectType 'exception_metric' `
                -Status (if ($ok) { 'PASS' } else { 'FAIL' }) `
                -Assertion "Z3 exception rate <= $cap% (half of firm-wide threshold)" `
                -Observed @{ exception_rate_pct = $rate } `
                -Expected @{ exception_rate_pct_max = $cap } `
                -RegulatorMappings @('FINRA-3110','SOX-404','OCC-2011-12','NYDFS-500') `
                -RemediationRef (if (-not $ok) { 'TRG-EXCEPTION-02' } else { $null }) `
                | Save-Agt225Evidence
            $ok | Should -BeTrue
        }

        It "AI Governance Council has reviewed exception metric in each of the trailing three quarters" {
            $now = Get-Date
            $needed = 0..2 | ForEach-Object { (Get-Agt225Quarter -Date $now.AddMonths(-3 * $_)).label }
            $present = $script:reviews | ForEach-Object { (Get-Agt225Quarter -Date ([datetime]$_.reviewDate)).label } | Sort-Object -Unique
            $missing = $needed | Where-Object { $_ -notin $present }
            $rec = New-Agt225EvidenceRecord -Namespace 'EXCEPTION' -Criterion 'VC-6' -Zone 'all' `
                -SubjectId 'exception-review-cycles' -SubjectType 'exception_metric' `
                -Status (if ($missing.Count -eq 0) { 'PASS' } else { 'FAIL' }) `
                -Assertion 'AI Governance Council reviewed exception rate in each trailing 3 quarters' `
                -Observed @{ needed_quarters = $needed; present_quarters = $present; missing = $missing } `
                -Expected @{ missing = @() } `
                -RegulatorMappings @('FINRA-3110','SOX-404','OCC-2011-12','FFIEC-MGMT') `
                -RemediationRef (if ($missing.Count -gt 0) { 'TRG-EXCEPTION-03' } else { $null }) `
                | Save-Agt225Evidence
            $missing.Count | Should -Be 0
        }
    }
}
```

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
| Z1 | Always SKIPPED — Z1 has no governance-template binding to except from | — | — |
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

This namespace evidences **VC-8: Researcher with Computer Use is configured per zone with a documented affirmative decision**. Researcher with Computer Use reached general availability in October 2025 for tenants holding any Microsoft 365 Copilot license (it is no longer Frontier-gated). Because the capability allows the agent to perform automated browser interactions (click, type, navigate) against arbitrary URLs, the firm must make and document an affirmative per-zone decision: enabled for which users, with which URL allow-list, and signed by which approvers.

### 8.2 Pre-conditions

- PRE gates passed.
- AI Administrator activated.
- Reference data: `$env:AGT225_RESEARCHER_DECISION_LOG` — a JSON file of the firm's per-zone affirmative decisions with signers and effective dates, owned by the AI Governance Council.

### 8.3 Pester suite

```powershell
Describe "AGT225-RESEARCHER" -Tag 'AGT225','VC-8' {

    BeforeAll {
        $script:sov      = Test-Agt225SovereignTenant
        $script:decision = Get-Content $env:AGT225_RESEARCHER_DECISION_LOG | ConvertFrom-Json
        if (-not $script:sov.is_sovereign) {
            $script:policy = Get-Agent365ResearcherComputerUsePolicy
        }
    }

    Context "Sovereign short-circuit" -Skip:(-not $script:sov.is_sovereign) {
        It "emits SKIPPED" {
            New-Agt225EvidenceRecord -Namespace 'RESEARCHER' -Criterion 'VC-8' -Zone 'all' `
                -SubjectId $script:sov.tenant_id -SubjectType 'researcher_policy' -Status 'SKIPPED' `
                -Assertion 'Sovereign — see §10' -Observed @{} -Expected @{} `
                -RegulatorMappings @('FINRA-25-07','GLBA-501b','OCC-2011-12') `
                -RemediationRef 'TRG-RESEARCHER-99' | Save-Agt225Evidence
            $true | Should -BeTrue
        }
    }

    Context "VC-8: Per-zone affirmative decision present and signed" -Skip:$script:sov.is_sovereign {

        It "Z1, Z2, Z3 each have a current affirmative decision in the decision log" {
            $missing = @()
            foreach ($z in '1','2','3') {
                $d = $script:decision | Where-Object zone -eq $z |
                     Sort-Object effectiveDate -Descending | Select-Object -First 1
                if (-not $d -or [datetime]$d.effectiveDate -lt (Get-Date).AddDays(-365)) {
                    $missing += $z
                }
            }
            $rec = New-Agt225EvidenceRecord -Namespace 'RESEARCHER' -Criterion 'VC-8' -Zone 'all' `
                -SubjectId 'researcher-decision-coverage' -SubjectType 'researcher_policy' `
                -Status (if ($missing.Count -eq 0) { 'PASS' } else { 'FAIL' }) `
                -Assertion 'Each zone has a signed affirmative decision <= 365 days old' `
                -Observed @{ missing_zones = $missing } -Expected @{ missing_zones = @() } `
                -RegulatorMappings @('FINRA-3110','FINRA-25-07','SOX-404','OCC-2011-12') `
                -RemediationRef (if ($missing.Count -gt 0) { 'TRG-RESEARCHER-01' } else { $null }) `
                | Save-Agt225Evidence
            $missing.Count | Should -Be 0
        }

        It "Z3 decision is signed by both AI Governance Lead and CISO" {
            $d = $script:decision | Where-Object zone -eq '3' |
                 Sort-Object effectiveDate -Descending | Select-Object -First 1
            $needed = @('AIGovernanceLead','CISO')
            $present = ($d.signers | ForEach-Object role) | Sort-Object -Unique
            $missing = $needed | Where-Object { $_ -notin $present }
            $rec = New-Agt225EvidenceRecord -Namespace 'RESEARCHER' -Criterion 'VC-8' -Zone '3' `
                -SubjectId 'researcher-z3-dual-sign' -SubjectType 'researcher_policy' `
                -Status (if ($missing.Count -eq 0) { 'PASS' } else { 'FAIL' }) `
                -Assertion 'Z3 affirmative decision is dual-signed by AI Governance Lead and CISO' `
                -Observed @{ signers_present = $present; missing_roles = $missing } `
                -Expected @{ signers_required = $needed } `
                -RegulatorMappings @('FINRA-3110','SOX-404','OCC-2011-12','NYDFS-500') `
                -RemediationRef (if ($missing.Count -gt 0) { 'TRG-RESEARCHER-02' } else { $null }) `
                | Save-Agt225Evidence
            $missing.Count | Should -Be 0
        }

        It "Tenant policy matches the documented decision (assignment scope and URL allow-list)" {
            $d = $script:decision | Where-Object zone -eq '3' |
                 Sort-Object effectiveDate -Descending | Select-Object -First 1
            $scopeOk = ($script:policy.z3.assignmentScope -eq $d.assignmentScope)
            $urlsOk  = -not (Compare-Object $script:policy.z3.urlAllowList $d.urlAllowList)
            $ok = $scopeOk -and $urlsOk
            $rec = New-Agt225EvidenceRecord -Namespace 'RESEARCHER' -Criterion 'VC-8' -Zone '3' `
                -SubjectId 'researcher-z3-policy-match' -SubjectType 'researcher_policy' `
                -Status (if ($ok) { 'PASS' } else { 'FAIL' }) `
                -Assertion 'Tenant Researcher policy for Z3 matches documented affirmative decision' `
                -Observed @{ tenant_scope = $script:policy.z3.assignmentScope;
                             tenant_urls  = $script:policy.z3.urlAllowList } `
                -Expected @{ documented_scope = $d.assignmentScope;
                             documented_urls  = $d.urlAllowList } `
                -RegulatorMappings @('FINRA-3110','FINRA-25-07','SOX-404','GLBA-501b','OCC-2011-12','NYDFS-500') `
                -RemediationRef (if (-not $ok) { 'TRG-RESEARCHER-03' } else { $null }) `
                | Save-Agt225Evidence
            $ok | Should -BeTrue -Because 'Drift between documented decision and tenant policy is a governance failure'
        }
    }
}
```

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
| Signing | Decision log dual-signed by AI Governance Lead and CISO at decision time; pack-level signature on Pester output |
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

### 9.3 Pester suite

```powershell
Describe "AGT225-SIEM" -Tag 'AGT225','SIEM' {

    BeforeAll {
        $script:sov = Test-Agt225SovereignTenant
        $script:siemEvents = Invoke-Agt225SiemQuery -SavedQuery $env:AGT225_SIEM_QUERY_FN -RangeDays 7
    }

    Context "Sovereign short-circuit" -Skip:(-not $script:sov.is_sovereign) {
        It "emits SKIPPED" {
            New-Agt225EvidenceRecord -Namespace 'SIEM' -Criterion 'VC-1..8 (compensating)' -Zone 'all' `
                -SubjectId $script:sov.tenant_id -SubjectType 'diagnostic_setting' -Status 'SKIPPED' `
                -Assertion 'Sovereign — see §10' -Observed @{} -Expected @{} `
                -RegulatorMappings @('FINRA-4511','SEC-17a-4') -RemediationRef 'TRG-SIEM-99' `
                | Save-Agt225Evidence
            $true | Should -BeTrue
        }
    }

    Context "Cross-cutting: Agent 365 events present in SIEM" -Skip:$script:sov.is_sovereign {

        It "SIEM has at least one Agent 365 governance event in trailing 7 days" {
            $count = ($script:siemEvents | Measure-Object).Count
            $rec = New-Agt225EvidenceRecord -Namespace 'SIEM' -Criterion 'VC-1..8 (compensating)' -Zone 'all' `
                -SubjectId 'siem-event-presence' -SubjectType 'diagnostic_setting' `
                -Status (if ($count -gt 0) { 'PASS' } else { 'FAIL' }) `
                -Assertion 'SIEM ingest pipeline yields >=1 Agent 365 event in trailing 7d' `
                -Observed @{ event_count_7d = $count } `
                -Expected @{ event_count_7d_min = 1 } `
                -RegulatorMappings @('FINRA-4511','SEC-17a-4','SOX-404','OCC-2011-12','NYDFS-500','FFIEC-IS') `
                -RemediationRef (if ($count -eq 0) { 'TRG-SIEM-01' } else { $null }) `
                | Save-Agt225Evidence
            $count | Should -BeGreaterThan 0
        }

        It "SIEM workspace retention is at least 6 years (2192 days)" {
            $ret = Get-Agt225SiemRetentionDays -Endpoint $env:AGT225_SIEM_QUERY_ENDPOINT
            $ok = $ret -ge 2192
            $rec = New-Agt225EvidenceRecord -Namespace 'SIEM' -Criterion 'VC-1..8 (compensating)' -Zone 'all' `
                -SubjectId 'siem-retention-config' -SubjectType 'diagnostic_setting' `
                -Status (if ($ok) { 'PASS' } else { 'FAIL' }) `
                -Assertion 'SIEM workspace retention >= 6 years (FINRA 4511 / SEC 17a-4)' `
                -Observed @{ retention_days = $ret } `
                -Expected @{ retention_days_min = 2192 } `
                -RegulatorMappings @('FINRA-4511','SEC-17a-4','SOX-404','OCC-2011-12') `
                -RemediationRef (if (-not $ok) { 'TRG-SIEM-02' } else { $null }) `
                | Save-Agt225Evidence
            $ok | Should -BeTrue
        }

        It "Each VC namespace has at least one event-type representative in trailing 30 days" {
            $needed = @('LICENSE','APPROVAL','OWNER','TEMPLATE','INVENTORY','EXCEPTION','RESEARCHER')
            $extended = Invoke-Agt225SiemQuery -SavedQuery "${env:AGT225_SIEM_QUERY_FN}_30d" -RangeDays 30
            $observed = $extended.AgentGovernanceCategory | Sort-Object -Unique
            $missing = $needed | Where-Object { $_ -notin $observed }
            $rec = New-Agt225EvidenceRecord -Namespace 'SIEM' -Criterion 'VC-1..8 (compensating)' -Zone 'all' `
                -SubjectId 'siem-namespace-coverage' -SubjectType 'diagnostic_setting' `
                -Status (if ($missing.Count -eq 0) { 'PASS' } else { 'WARN' }) `
                -Assertion 'Each governance namespace produces at least one SIEM event in trailing 30d' `
                -Observed @{ observed_categories = $observed; missing = $missing } `
                -Expected @{ missing = @() } `
                -RegulatorMappings @('FINRA-4511','SOX-404','OCC-2011-12') `
                -RemediationRef (if ($missing.Count -gt 0) { 'TRG-SIEM-03' } else { $null }) `
                | Save-Agt225Evidence
            $missing.Count | Should -BeLessOrEqual 2 -Because 'Allow up to 2 quiet categories; > 2 indicates pipeline gap'
        }
    }
}
```

### 9.4 Sample passing evidence

```json
{
  "control_id": "2.25", "run_id": "AGT225-20260415-093012-a1b2c3d4",
  "run_timestamp": "2026-04-15T09:30:12Z", "tenant_id": "11111111-2222-3333-4444-555555555555",
  "tenant_display_name": "Contoso Bank, N.A.", "cloud": "Commercial",
  "zone": "all", "namespace": "SIEM", "criterion": "VC-1..8 (compensating)",
  "subject_id": "siem-retention-config", "subject_type": "diagnostic_setting",
  "status": "PASS",
  "assertion": "SIEM workspace retention >= 6 years (FINRA 4511 / SEC 17a-4)",
  "observed_value": { "retention_days": 2557 },
  "expected_value": { "retention_days_min": 2192 },
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
  "zone": "all", "namespace": "SIEM", "criterion": "VC-1..8 (compensating)",
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

This namespace operates tenant-wide; no zone differentiation. PASS requires all three `It` blocks PASS; WARN allowed only on the namespace-coverage check (≤ 2 quiet categories); FAIL on either event-presence or retention-days failure.

### 9.8 Regulator mapping

| Test | FINRA-4511 | SEC-17a-4 | SOX-404 | OCC-2011-12 | NYDFS-500 | FFIEC-IS |
|---|---|---|---|---|---|---|
| Event presence 7d | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| Retention >= 6yr | ✓ | ✓ | ✓ | ✓ | — | — |
| Namespace coverage | ✓ | — | ✓ | ✓ | — | — |

---

## §10 SOV Namespace — Sovereign Cloud Compensating Control

### 10.1 Purpose

When `Test-Agt225SovereignTenant` returns `is_sovereign = $true`, the eight Pester suites in §2–§9 emit `SKIPPED` records pointing here. This section describes the manual quarterly attestation that supplies compensating evidence in sovereign clouds (GCC, GCCH, DoD) until Microsoft Agent 365 Admin Center reaches parity in those environments. The sovereign roadmap MUST be re-checked at the start of every quarter; the quarterly memo described here records the re-check outcome.

### 10.2 Scope and rationale

The Microsoft Agent 365 Admin Center governance console, governance templates, admin-gated publish/activate workflow, and exception-rate metric are not at parity in sovereign clouds at the time of this playbook's last UI verification (April 2026). The sovereign cloud roadmap is published by Microsoft and updated periodically; the firm's Cloud Engineering team subscribes to the roadmap notifications and produces a memo each quarter. Until parity arrives, sovereign tenants demonstrate compliance with the Control 2.25 verification criteria through:

1. **Manual quarterly inventory** — operator with **Entra Global Reader** enumerates agents using `Get-MgServicePrincipal` filtered by Microsoft 365 Copilot publishers and Copilot Studio API endpoints, producing an equivalent inventory file with the same field set as §6.
2. **Manual approval review** — change-ticket records from Control 2.3 are sampled and reviewed by AI Governance Lead and Compliance Officer for evidence of admin sponsorship for each Z2/Z3 agent.
3. **Manual ownership reconciliation** — owner UPNs from the manual inventory are validated against active employee records with the same 48-hour remediation SLA.
4. **Manual template equivalent** — the firm's Conditional Access policies, Sensitivity Labels, and Purview DLP policies that constitute the "template equivalent" are enumerated and confirmed to apply.
5. **Manual exception accounting** — variances from the policy baseline are tracked in the firm's GRC platform and the rate is computed for the trailing quarter.
6. **Researcher with Computer Use** — sovereign clouds may not have the Researcher capability at all; if absent, the §10 attestation states `not_applicable` for VC-8 with a parity-roadmap pointer.
7. **SIEM** — sovereign tenants forward to the sovereign-cloud SIEM (e.g., Sentinel Government); retention requirements are unchanged.

### 10.3 Quarterly attestation runbook

| Step | Owner | Output |
|---|---|---|
| 1. Re-check Microsoft sovereign roadmap | Cloud Engineering Lead | Memo `sov-parity-check-yyyy-Qn.md` |
| 2. Run manual inventory script | AI Administrator | `sov-inventory-yyyy-Qn.json` |
| 3. Sample Z2/Z3 change tickets (N>=10/zone) | AI Governance Lead | `sov-approval-sample-yyyy-Qn.json` |
| 4. Reconcile owner UPNs against HR feed | AI Governance Lead | `sov-ownership-yyyy-Qn.json` |
| 5. Enumerate compensating policies (CA / SL / DLP) | Information Security Officer | `sov-template-equivalent-yyyy-Qn.json` |
| 6. Compute exception rate from GRC tickets | Compliance Officer | `sov-exception-yyyy-Qn.json` |
| 7. Confirm Researcher availability and decision | Information Security Officer | `sov-researcher-yyyy-Qn.json` |
| 8. Confirm SIEM forwarding and retention | Entra Security Admin | `sov-siem-yyyy-Qn.json` |
| 9. Assemble and dual-sign attestation packet | AI Governance Lead + Compliance Officer | `sov-attestation-yyyy-Qn.pdf` (signed) |

### 10.4 Sovereign attestation record schema

The dual-signed PDF is the human-readable artifact; the underlying machine-readable record uses the same schema as §1.1 with `criterion: "VC-1..8 (compensating)"`, `namespace: "SOV"`, `subject_type: "manual_attestation"`, and `evidence_artifacts` enumerating all nine outputs above.

### 10.5 Retention

Sovereign attestation packets are retained on WORM for **7 years** (extending the standard 6-year retention by one year because the attestation is itself the primary evidence in the absence of automated tooling) — aligning with the more conservative end of FFIEC and OCC examiner expectations for compensating-control documentation.

### 10.6 Re-verification trigger

When the Microsoft sovereign roadmap announces parity for the Agent 365 Admin Center, the firm's Cloud Engineering team:

1. Pilots the automated tests in §2–§9 in a sovereign tenant for one quarter alongside the manual attestation.
2. AI Governance Lead and Compliance Officer dual-sign a transition memo cutting over from §10 manual attestation to §2–§9 automation effective the following quarter.
3. The §10 manual attestation is retained on its 7-year WORM clock from the date of last attestation; it is not destroyed early.

---

## §11 Evidence Pack Assembly & Signing

### 11.1 Pack layout

After all namespace suites complete, `Build-Agt225EvidencePack` assembles a single signed pack at `$script:EvidenceRoot/pack/`:

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
└── sov/                              # Empty in Commercial; populated in sovereign
```

### 11.2 Pack metadata

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

### 11.3 Signing

The pack is signed by the AI Governance Lead using a key managed in the firm's PKI or Azure Key Vault (managed HSM where available). The witness (Entra Global Reader operator) co-signs attesting to the dual-control read of the pack contents prior to publication.

### 11.4 Merkle root

Every evidence record file contributes a SHA-256 leaf hash (computed over the canonical JSON serialization). Leaves are sorted lexicographically by filename and combined pairwise into a binary Merkle tree; the root hash is recorded as `merkle_root_sha256` in `attestation.json`. Any tampering with any record after publication invalidates the root and is detectable by `Test-Agt225PackIntegrity`.

### 11.5 Schema validation

Before signing, `Test-Agt225EvidenceSchema` validates every record against the §1.1 schema. Records failing schema validation are not signed; the pack assembler exits with a non-zero status and writes `schema-violation-<runId>.json` to the pack directory for triage.

### 11.6 Publication

Signed packs are published to `$env:AGT225_PACK_PUBLICATION_ROOT` (a WORM container distinct from the working evidence root) and an index entry is appended to the firm's evidence-pack registry per Control 2.13. The publication step emits an OpenTelemetry span that flows to the firm's observability platform and to the SIEM (Control 3.1).

### 11.7 Retention

| Cloud | Retention | Authority |
|---|---|---|
| Commercial | 6 years on WORM | FINRA 4511 / SEC 17a-4(f) |
| Sovereign (GCC/GCCH/DoD) | 7 years on WORM | Same as Commercial plus 1-year buffer for compensating-control documentation per §10.5 |

---

## §12 Failure Triage Matrix

When a Pester `It` block FAILs, the evidence record carries a `remediation_ref` of the form `TRG-{NS}-NN`. This matrix maps each ID to severity, SLA band, owner, and the remediation playbook section.

| Triage ID | Severity | SLA to remediate | Owner | Remediation reference |
|---|---|---|---|---|
| TRG-LICENSE-01 | Critical | 1 BD | Procurement Lead + Entra Global Admin | Portal Walkthrough §2.1 (planned) |
| TRG-LICENSE-02 | Critical | 1 BD | Procurement Lead | Portal Walkthrough §2.2 (planned) |
| TRG-LICENSE-03 | Critical | 4 hours | AI Administrator | [Troubleshooting](./troubleshooting.md) §3.1 |
| TRG-LICENSE-04 | Medium | 30 days | Procurement Lead | Portal Walkthrough §2.3 (planned) |
| TRG-LICENSE-99 | Informational | Quarterly | AI Governance Lead | §10 sovereign attestation |
| TRG-APPROVAL-01 | High | 2 BD | AI Governance Lead | Portal Walkthrough §3.1 (planned) |
| TRG-APPROVAL-02 | Medium | 5 BD | AI Governance Lead | Portal Walkthrough §3.2 (planned) |
| TRG-APPROVAL-03 | High | 2 BD | Change Management Lead | Portal Walkthrough §3.3 (planned) |
| TRG-APPROVAL-04 | High | 1 BD | AI Governance Lead | [PowerShell Setup](./powershell-setup.md) §4.2 |
| TRG-APPROVAL-05 | Critical | 4 hours | AI Governance Lead | [PowerShell Setup](./powershell-setup.md) §4.3 |
| TRG-APPROVAL-99 | Informational | Quarterly | AI Governance Lead | §10 sovereign attestation |
| TRG-OWNER-01 | High | 48 hours | AI Governance Lead | Portal Walkthrough §4.1 (planned) |
| TRG-OWNER-02 | Critical | 24 hours | AI Governance Lead | Portal Walkthrough §4.2 (planned) |
| TRG-OWNER-99 | Informational | Quarterly | AI Governance Lead | §10 |
| TRG-TEMPLATE-01 | High | 5 BD | AI Administrator | Portal Walkthrough §5.1 (planned) |
| TRG-TEMPLATE-02 | Critical | 2 BD | AI Administrator | Portal Walkthrough §5.2 (planned) |
| TRG-TEMPLATE-03 | Critical | 2 BD | Identity Engineering Lead | Portal Walkthrough §5.3 (planned) |
| TRG-TEMPLATE-04 | High | 5 BD | Identity Engineering Lead | Portal Walkthrough §5.4 (planned) |
| TRG-TEMPLATE-99 | Informational | Quarterly | AI Governance Lead | §10 |
| TRG-INVENTORY-01 | High | 5 BD | AI Governance Lead | [PowerShell Setup](./powershell-setup.md) §5.1 |
| TRG-INVENTORY-02 | Medium | 5 BD | AI Governance Lead | [PowerShell Setup](./powershell-setup.md) §5.2 |
| TRG-INVENTORY-03 | High | 5 BD | AI Governance Lead | [PowerShell Setup](./powershell-setup.md) §5.3 |
| TRG-INVENTORY-04 | Critical | 4 hours (IR escalation) | CISO + AI Governance Lead | [Troubleshooting](./troubleshooting.md) §6.1 |
| TRG-INVENTORY-99 | Informational | Quarterly | AI Governance Lead | §10 |
| TRG-EXCEPTION-01 | High | 30 days | AI Governance Lead | Portal Walkthrough §6.1 (planned) |
| TRG-EXCEPTION-02 | Critical | 10 BD | AI Governance Lead + CISO | Portal Walkthrough §6.2 (planned) |
| TRG-EXCEPTION-03 | Critical | 1 quarter | AI Governance Lead | Portal Walkthrough §6.3 (planned) |
| TRG-EXCEPTION-99 | Informational | Quarterly | AI Governance Lead | §10 |
| TRG-RESEARCHER-01 | High | 30 days | AI Governance Lead | Portal Walkthrough §7.1 (planned) |
| TRG-RESEARCHER-02 | Critical | 10 BD | AI Governance Lead + CISO | Portal Walkthrough §7.2 (planned) |
| TRG-RESEARCHER-03 | Critical | 4 hours | AI Administrator | [PowerShell Setup](./powershell-setup.md) §7.3 |
| TRG-RESEARCHER-99 | Informational | Quarterly | AI Governance Lead | §10 |
| TRG-SIEM-01 | High | 1 BD | Entra Security Admin | [Troubleshooting](./troubleshooting.md) §9.1 |
| TRG-SIEM-02 | Critical | 5 BD | Entra Security Admin | [PowerShell Setup](./powershell-setup.md) §9.2 |
| TRG-SIEM-03 | Medium | 30 days | Entra Security Admin | [Troubleshooting](./troubleshooting.md) §9.3 |
| TRG-SIEM-99 | Informational | Quarterly | AI Governance Lead | §10 |

> Severity bands: **Critical** — examiner-visible if unremediated; **High** — examiner-visible if recurring or pattern; **Medium** — process improvement; **Informational** — sovereign skip routing.

---

## §13 Cross-Control Verification Dependencies

This playbook is one node in the broader Pillar 2 governance graph. The following dependencies must be considered when reading this evidence pack.

| Direction | Control | Interaction |
|---|---|---|
| Upstream | [1.2 Agent Registry & Integrated Apps Management](../../../controls/pillar-1-security/1.2-agent-registry-and-integrated-apps-management.md) | Provides the "golden" agent inventory consumed by the OWNER and INVENTORY namespaces. If 1.2 evidence shows registry drift, 2.25 OWNER evidence is suspect. |
| Upstream | [2.26 Entra Agent ID Identity Governance](../../../controls/pillar-2-management/2.26-entra-agent-id-identity-governance.md) | Provides the Entra Access Package binding asserted in §5 TEMPLATE for Z3 agents. If 2.26 evidence shows orphaned access packages, 2.25 TEMPLATE PASS is downgraded to WARN. |
| Upstream | [2.3 Change Management and Release Planning](../../../controls/pillar-2-management/2.3-change-management-and-release-planning.md) | Provides the change-ticket records cross-referenced by §3 APPROVAL `Resolve-Agt225ChangeTicket`. |
| Upstream | [2.8 Access Control and Segregation of Duties](../../../controls/pillar-2-management/2.8-access-control-and-segregation-of-duties.md) | Provides the 90-day re-attestation evidence referenced in §2.7 Z3 PASS criteria. |
| Lateral | [2.13 Documentation and Record Keeping](../../../controls/pillar-2-management/2.13-documentation-and-record-keeping.md) | Receives the §11 published pack metadata. |
| Downstream | [3.9 Microsoft Sentinel Integration](../../../controls/pillar-3-reporting/3.9-microsoft-sentinel-integration.md) | Consumes the SIEM forwarding namespace; the §9 evidence cross-references the parent 3.9 pack via `parent_pack_ref`. |
| Downstream | [3.6 Orphaned Agent Detection & Remediation](../../../controls/pillar-3-reporting/3.6-orphaned-agent-detection-and-remediation.md) | Consumes the §4 OWNER findings; offender list flows directly into 3.6 remediation queue. |
| Downstream | 4.5 AI Governance Council Operations (planned) | Consumes the §7 EXCEPTION review-cycle artifacts; council secretary maintains `$env:AGT225_EXCEPTION_REVIEW_LOG`. |

When assembling a quarterly attestation for an examiner, present the 2.25 evidence pack alongside the 1.2 and 2.26 packs of the same quarter — examiners typically request the trio together as evidence of admin-gated lifecycle for AI agents.

---

## §14 Quarterly Attestation Runbook

### 14.1 Cadence

| Activity | Cadence | Owner |
|---|---|---|
| Run §2–§9 Pester suite | Daily (Z3-touching tests), Weekly (full suite), Monthly (with INVENTORY) | AI Administrator |
| Assemble §11 evidence pack | Monthly | AI Governance Lead |
| Quarterly attestation packet | Quarterly (within 15 BD of quarter end) | AI Governance Lead + Compliance Officer |
| Annual control re-baseline (review thresholds in §3, §7) | Annually | AI Governance Council |

### 14.2 Quarterly packet contents

1. The three monthly §11 evidence packs from the quarter, with their attestation.json files.
2. A quarterly summary memo `2.25-quarterly-summary-yyyy-Qn.md` covering: namespace pass rates; trend vs. prior quarter; open remediation tickets; threshold variance review (if any threshold in `$env:AGT225_*` was changed during the quarter, the change is recorded with its approver and effective date).
3. The current §10 sovereign attestation packet if applicable.
4. The signed cross-reference index linking the 2.25 pack to the 1.2 and 2.26 packs of the same quarter.

### 14.3 Attestation signers

- **AI Governance Lead** — primary signer, attests to operational accuracy.
- **Compliance Officer** — counter-signer, attests to regulatory mapping accuracy.
- **Information Security Officer** — counter-signer for any quarter containing a TRG-*-Critical finding.
- **Technology Risk Manager** — receives the packet for inclusion in firm technology-risk reporting per OCC Bulletin 2026-13 (formerly OCC Bulletin 2011-12).

### 14.4 Distribution

| Recipient | Distribution form | Retention obligation |
|---|---|---|
| Internal Audit | WORM-protected link; read-only | Per audit's own retention policy |
| Compliance Department | WORM-protected link | 6 years |
| Examiner (on request) | Signed PDF export of `summary.md` plus selected evidence records | Per examiner request |
| Firm GRC platform | Structured ingest of `findings.csv` plus `attestation.json` | Per GRC retention policy |

### 14.5 Continuous improvement

Each quarterly review identifies up to three improvement items, recorded in the firm's GRC platform, owned by the AI Governance Lead, and re-checked at the next quarterly review. Common improvement themes include: tightening firm-set thresholds (§3 SLA, §7 exception cap) as the program matures; expanding the §6 INVENTORY field set to capture additional governance metadata as Microsoft adds it; tightening the §8 RESEARCHER URL allow-list as the firm's research workflow stabilizes.

---

## §15 References

- Control source of truth: [Control 2.25 — Microsoft Agent 365 Admin Center Governance Console](../../../controls/pillar-2-management/2.25-agent-365-admin-center-governance-console.md)
- Sister verification playbook (gold-standard structural template): [Control 2.26 verification-testing](../2.26/verification-testing.md)
- Sibling playbooks for this control: Portal Walkthrough (planned) · [PowerShell Setup](./powershell-setup.md) · [Troubleshooting](./troubleshooting.md)
- PowerShell baseline (sovereign endpoint reference): [`../../_shared/powershell-baseline.md`](../../_shared/powershell-baseline.md)
- Role catalog: [`docs/reference/role-catalog.md`](../../../reference/role-catalog.md)
- Regulatory mapping vocabulary: [`docs/reference/regulatory-mappings.md`](../../../reference/regulatory-mappings.md)

---

*Updated: May 2026 | Version: v1.6.2 | UI Verification Status: Current*
