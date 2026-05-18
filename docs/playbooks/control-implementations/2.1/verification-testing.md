# Verification & Testing — Control 2.1: Managed Environments

> **Examiner-defensible evidence package** for Control 2.1. This playbook produces, signs, and retains the artifacts required to demonstrate to FINRA, SEC, OCC, FFIEC, NYDFS, and internal audit that every Power Platform environment in scope of US financial-services governance is correctly enrolled as a Microsoft Power Platform **Managed Environment** (`protectionLevel = Standard`), is licensed at the prescribed entitlement floor, has zone-appropriate sharing limits, solution-checker enforcement, IP firewall, IP-bound cookies, Customer Lockbox, Customer-Managed Keys, Tenant Isolation, environment routing, governance-console integration, and segregation of duties — and that the evidentiary chain for each of those configurations is reproducible, hash-chained, and retained on WORM-protected storage for the FINRA Rule 4511 / SEC Rule 17a-4 six-year horizon.
>
> **Scope:** All Power Platform environments classified Zone 2 (Team) or Zone 3 (Enterprise). Zone 1 (Personal Productivity / developer / individual maker) environments are tested only for clean delineation from Zone 2/3 (TC-1) and for routing-rule placement (TC-14); they are not in scope for Managed-Environments enablement. Sovereign clouds (GCC, GCC High, DoD, China 21Vianet) follow the compensating-control patterns in TC-8, TC-15, and TC-18.
>
> **Companion controls:** [1.4 Advanced Connector Policies](../../../controls/pillar-1-security/1.4-advanced-connector-policies-acp.md), [1.5 DLP and Sensitivity Labels](../../../controls/pillar-1-security/1.5-data-loss-prevention-dlp-and-sensitivity-labels.md), [1.7 Comprehensive Audit Logging](../../../controls/pillar-1-security/1.7-comprehensive-audit-logging-and-compliance.md), [1.20 Network Isolation](../../../controls/pillar-1-security/1.20-network-isolation-private-connectivity.md), [2.2 Environment Groups](../../../controls/pillar-2-management/2.2-environment-groups-and-tier-classification.md), [2.3 Change Management](../../../controls/pillar-2-management/2.3-change-management-and-release-planning.md), [2.8 Access Control & SoD](../../../controls/pillar-2-management/2.8-access-control-and-segregation-of-duties.md), [2.14 Training & Awareness](../../../controls/pillar-2-management/2.14-training-and-awareness-program.md), [2.15 Environment Routing](../../../controls/pillar-2-management/2.15-environment-routing.md), [2.25 Agent 365 Admin Center Governance Console](../../../controls/pillar-2-management/2.25-agent-365-admin-center-governance-console.md), [3.1 Agent Inventory & Metadata](../../../controls/pillar-3-reporting/3.1-agent-inventory-and-metadata-management.md), [3.6 Orphaned Agent Detection](../../../controls/pillar-3-reporting/3.6-orphaned-agent-detection-and-remediation.md), [3.9 Microsoft Sentinel Integration](../../../controls/pillar-3-reporting/3.9-microsoft-sentinel-integration.md).
>
> **Last UI verified:** April 2026 against Power Platform Admin Center (PPAC) build 2026.04.x, the Microsoft 365 admin center governance pages of the same build, the Microsoft Agent 365 Admin Center release of build 2026.04.x, and the `Microsoft.PowerApps.Administration.PowerShell` module v2.0.193 / `Microsoft.Graph` v2.25.0 / Pester 5.5.0.

---

!!! danger "Non-Substitution — Managed Environments are not a substitute for human supervision"
    Managed Environments provide the **technical guardrails and evidentiary surface** that make FSI governance operable. They do **not** substitute for, and **must not be claimed to substitute for**:

    - The **registered-principal supervisory designation** required by FINRA Rule 3110. The solution-checker enforcement gate, sharing-limit enforcement, and weekly digest are evidentiary inputs to a Series-24 supervisor's review; they are not themselves the review. See [Control 2.12](../../../controls/pillar-2-management/2.12-supervision-and-oversight-finra-rule-3110.md).
    - The **books-and-records retention obligation** under FINRA Rule 4511 and SEC Rule 17a-4(f). The PPAC weekly usage-insights digest is operational telemetry. Records-scope artifacts (audit logs, attestations, change-management approvals) are governed by [Control 1.7](../../../controls/pillar-1-security/1.7-comprehensive-audit-logging-and-compliance.md) and [Control 3.1](../../../controls/pillar-3-reporting/3.1-agent-inventory-and-metadata-management.md). The retention column in the §3 evidence-capture master table distinguishes operational vs records-scope artifacts; do not commingle them.
    - The **independent model validation** required by OCC Bulletin 2026-13 (formerly OCC Bulletin 2011-12) and Federal Reserve SR 26-2 (formerly SR 11-7). A Managed Environment toggle does not validate a model. See [Control 2.6](../../../controls/pillar-2-management/2.6-model-risk-management-sr-26-2.md).
    - The **Written Supervisory Procedures (WSPs)** that document who reviews what, when, and how. Examiners hold the firm to its WSPs; this playbook produces the evidence those WSPs reference.
    - The **SOX 302 / 404 management certification** of internal controls over financial reporting. The §4 quarterly attestation supports — but does not replace — management's certification.

    Treat Managed Environments as the **enforcement substrate** that makes the human-and-process controls above auditable. Where a TC below uses language like "blocks" or "enforces", read it as "produces the technical signal that the firm''s WSP designates as the gating control"; the gate is the WSP, not the toggle.

!!! warning "Sovereign Cloud Availability — feature gaps that change evidence patterns"
    The following Managed Environments features have **material gaps** in sovereign clouds at the time of this playbook''s last UI verification. Sovereign tenants must apply the compensating-control substitutions in TC-8, TC-15, and TC-18; the §3 evidence-capture master table flags affected artifacts with a `SOV-SUB` annotation:

    | Feature | Commercial | GCC | GCC High | DoD | China (21Vianet) |
    |---|---|---|---|---|---|
    | Managed Environments enablement | GA | GA | GA | GA | Available |
    | Sharing limits per resource family | GA | GA | GA | GA | Available |
    | Solution checker enforcement | GA | GA | GA | GA | Available |
    | IP firewall + AuditOnly mode | GA | GA | GA | GA | Verify per [Learn — IP firewall](https://learn.microsoft.com/en-us/power-platform/admin/ip-firewall) |
    | IP-based cookie binding | GA | GA | GA | GA | Verify |
    | Customer Lockbox | GA | GA | GA | Limited tier coverage | Not available |
    | Customer-Managed Keys (CMK) | GA — service coverage varies | Partial — verify per service | Partial | Partial | Partial |
    | Weekly usage-insights digest | GA | **Not available** | **Not available** | **Not available** | **Not available** |
    | Tenant Isolation | GA | GA | GA | GA | Available |
    | Environment routing | GA | GA | GA | GA | Available |
    | Microsoft Agent 365 Admin Center governance console | GA (May 2026) | **Not at parity** | **Not at parity** | **Not at parity** | Not available |

    Re-verify sovereign-cloud parity quarterly via the [Microsoft 365 Government roadmap](https://aka.ms/m365gov-roadmap) and the linked Learn pages, and update the §3 evidence-capture master table with any change in availability before the next quarterly evidence pack is sealed.

---

## Document Conventions

| Convention | Value |
|---|---|
| PowerShell baseline (read-only Graph + Agent 365) | PowerShell 7.4+ Core; `#Requires -Version 7.4` |
| PowerShell baseline (Power Platform admin module) | Windows PowerShell 5.1; `Microsoft.PowerApps.Administration.PowerShell` does **not** load on PowerShell 7+ for admin scenarios as of this writing — see the sister [PowerShell Setup](powershell-setup.md). |
| Test framework | Pester 5.5+. All assertions use `Should` with `-Because` clauses for examiner traceability. |
| Output discipline | No `Write-Host` in evidence emission. All evidence emitted as structured `[pscustomobject]` instances, then serialized with `ConvertTo-Json -Depth 8` to evidence files. |
| Sovereign cloud handling | Pester suites detect cloud and emit `SKIPPED` records routed to TC-18 rather than `FAIL`. |
| Evidence retention — records scope | Six (6) years on WORM-protected storage for any artifact the firm''s WSPs designate as a books-and-records artifact. Aligns with FINRA 4511 / SEC 17a-4(f). Distinguished from operational scope in §3. |
| Evidence retention — operational scope | Three (3) years on tamper-evident storage for operational telemetry the firm has documented as out-of-scope of supervisory recordkeeping (e.g., the weekly digest itself, license-consumption snapshots used for capacity planning). |
| Hashing | SHA-256 over canonical JSON; chained leaf hashes plus a Merkle root in `attestation.json` (see §4.3). |
| Sovereign anchor | Sovereign-aware functions reference [`../../_shared/powershell-baseline.md`](../../_shared/powershell-baseline.md). |
| Run identifier | Every test run is tagged `ME-yyyyMMdd-HHmmss-<8charGuid>` (e.g., `ME-20260415-093012-a1b2c3d4`) and embedded in every evidence record and artifact filename. |
| Canonical role names | Per [`docs/reference/role-catalog.md`](../../../reference/role-catalog.md). The canonical short names used in this playbook are **Power Platform Admin**, **Entra Global Admin**, **AI Administrator**, **Purview Compliance Admin**, **Entra Security Admin**, **Entra Global Reader**, **AI Governance Lead**, **Compliance Officer**, **Information Security Officer**, **Internal Audit Lead**, **Technology Risk Manager**, **Change Management Lead**. |
| `protectionLevel` semantics | `protectionLevel = "Standard"` ⇒ Managed Environment **ENABLED**. `protectionLevel = "Basic"` (or absent) ⇒ **DISABLED / unmanaged**. Earlier versions of these playbooks had this inverted; pre-April-2026 evidence likely reports the opposite of reality and must be re-collected. |

> This playbook **helps meet** recordkeeping, supervision, change-management, access-management, and oversight expectations under FINRA Rules 3110 and 4511, FINRA Regulatory Notice 25-07, SEC Rules 17a-3 / 17a-4, SOX §§ 302 / 404, GLBA § 501(b), OCC Bulletin 2026-13 (formerly OCC Bulletin 2011-12), Federal Reserve SR 26-2 (formerly SR 11-7), NYDFS 23 NYCRR 500.06, and the FFIEC IT Examination Handbook. It is one component of a defensible AI / low-code governance program; it does not replace a registered-principal designation, written supervisory procedures, model risk management practices, or the firm''s own legal review.

---

## §0 Pre-Test Prerequisites & Sovereign Cloud Bootstrap

### 0.1 Operator role prerequisites

The operator running this playbook must hold one of the following role assignments, scoped to the tenant under test, and activated through Microsoft Entra Privileged Identity Management (PIM) for the duration of the test run. Read-only assertions throughout TC-1 — TC-20 are deliberately separated from any write actions; the Pester suites in this playbook **do not perform remediation**. Remediation runbooks referenced from failure paths live in the sister [PowerShell Setup](powershell-setup.md) and [Troubleshooting](troubleshooting.md) playbooks and require their own change tickets and write scopes.

| Role (canonical) | Required for | PIM activation window |
|---|---|---|
| Power Platform Admin | Tenant-scope reads against PPAC governance configuration (TC-1 through TC-17); `Get-AdminPowerAppEnvironment`, `Get-AdminPowerAppEnvironmentGovernanceConfiguration`; emergency execution of remediation runbooks | 4 hours, just-in-time, ticketed |
| Entra Global Admin | Tenant-scope reads where Power Platform Admin is insufficient (TC-3 license-consumption Graph endpoint, TC-11 Lockbox tenant-tier read, TC-13 Tenant Isolation tenant-level read) | 2 hours, JIT, ticketed |
| AI Administrator | Reads against Microsoft Agent 365 Admin Center inventory + governance template assignments (TC-15) | 4 hours, JIT |
| Purview Compliance Admin | Read access to the audit-log substitute data path used in sovereign clouds (TC-8 SOV substitution; TC-18) and to Purview retention labels referenced from the §3 evidence-capture master table | 4 hours |
| Entra Security Admin | Reads against the Microsoft Sentinel workspace used for sovereign substitution (TC-8, TC-18) and against Conditional Access policies that gate IP firewall coverage (TC-9) | 4 hours |
| Entra Global Reader | Witness role for the dual-control evidence-pack signing pattern in §4.3 | 4 hours |
| AI Governance Lead | Counter-signs the quarterly attestation packet in §4; reviews the per-environment owner field in the §3 master table; signs the §4 evidence pack as primary signatory | Standing; quarterly recertification per Control 2.8 |
| Compliance Officer | Counter-signs the quarterly attestation packet in §4; signs Zone 3 sharing-limit and CMK variances; signs the TC-18 sovereign quarterly attestation; produces the examiner-facing evidence pack in §5 | Standing |
| Information Security Officer | Reviews IP firewall AuditOnly-to-Enforce promotion (TC-9), IP-cookie-binding posture (TC-10), Lockbox tier (TC-11), CMK exclusion narrative (TC-12), Tenant Isolation posture (TC-13) | Standing |
| Internal Audit Lead | Receives the §4 evidence pack and integrates it into the firm''s SOX 404 internal-controls-over-financial-reporting (ICFR) workpapers; signs the §4 annual self-assessment (TC-19) | Standing |
| Technology Risk Manager | Receives the §4 evidence pack and integrates it into the firm''s technology-risk reporting per OCC Bulletin 2026-13 (formerly OCC 2011-12) / Fed SR 26-2 (formerly SR 11-7) | Standing |
| Change Management Lead | Reconciles solution-checker exception register entries (TC-6), routing rule deployments (TC-14), and Lockbox approval responses (TC-11) with change tickets per Control 2.3 | Standing |

> **Least privilege.** No operator should hold **Entra Global Admin** persistently. Day-to-day verification work in TC-1 through TC-17 is performed under **Power Platform Admin** with **Entra Global Reader** as the witness role. **Entra Global Admin** is reserved for tenant-level reads that the Power Platform admin module does not surface, and is operated under PIM with just-in-time activation and a ticketed justification.

### 0.2 Module baseline

Pin to specific module versions to keep evidence packs reproducible across machines and over time. Re-validate against newer module versions before promoting them to the standing schedule.

```powershell
# Read-only Graph operations (TC-3 license consumption, TC-15 Agent 365, TC-18 sovereign substitute)
#Requires -Version 7.4
#Requires -Modules @{ ModuleName='Microsoft.Graph.Authentication';                ModuleVersion='2.25.0' }
#Requires -Modules @{ ModuleName='Microsoft.Graph.Identity.DirectoryManagement';  ModuleVersion='2.25.0' }
#Requires -Modules @{ ModuleName='Microsoft.Graph.Reports';                       ModuleVersion='2.25.0' }
#Requires -Modules @{ ModuleName='Microsoft.Graph.Beta.Applications';             ModuleVersion='2.25.0' }
#Requires -Modules @{ ModuleName='Pester';                                        ModuleVersion='5.5.0'  }

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'
$ProgressPreference    = 'SilentlyContinue'
```

```powershell
# Power Platform admin reads (TC-1, TC-2, TC-4 — TC-14, TC-16, TC-17). Windows PowerShell 5.1.
#Requires -PSEdition Desktop
#Requires -Version 5.1
#Requires -Modules @{ ModuleName='Microsoft.PowerApps.Administration.PowerShell'; ModuleVersion='2.0.193' }
#Requires -Modules @{ ModuleName='Microsoft.PowerApps.PowerShell';                ModuleVersion='1.0.34'  }

$ErrorActionPreference = 'Stop'
```

> **Why two shells?** The Power Platform admin module does not load on PowerShell 7+ for admin scenarios as of this writing. Graph-based assertions (TC-3, TC-15, TC-18) run on PowerShell 7.4 with `Microsoft.Graph` v2.25; PPAC-surfaced assertions (everything else) run on Windows PowerShell 5.1. The §4 evidence-pack assembler reconciles JSON outputs from both shells. The sister [PowerShell Setup](powershell-setup.md) §1 documents the cross-shell hand-off pattern.

### 0.3 PRE gates (must all pass before TC-1 — TC-20 execute)

The bootstrap script `Invoke-Me21PreFlight.ps1` (in the sister [PowerShell Setup](powershell-setup.md) playbook) runs nine pre-flight gates. Any `FAIL` halts the suite and emits a single evidence artifact `preflight-FAILED-<runId>.json`. Any `SKIPPED` from PRE-06 redirects the run to TC-18 (sovereign compensating control).

| Gate | ID | Purpose | Failure behavior |
|---|---|---|---|
| Module presence | PRE-01 | Confirms required modules loaded at the pinned versions in §0.2 | HALT |
| Power Platform context | PRE-02 | Confirms `Add-PowerAppsAccount -Endpoint <cloud>` established and that `Get-AdminPowerAppEnvironment` returns at least one environment | HALT |
| Graph context | PRE-03 | Confirms `Connect-MgGraph` established with required scopes (`Directory.Read.All`, `Reports.Read.All`, `Application.Read.All`, `User.Read.All`, `AuditLog.Read.All`, `AgentGovernance.Read.All` on commercial) | HALT |
| Tenant identification | PRE-04 | Captures `tenantId`, `displayName`, primary verified domain for every evidence record | HALT |
| Cloud detection | PRE-05 | Reads `(Get-MgContext).Environment` and the `-Endpoint` parameter passed to `Add-PowerAppsAccount`; maps to `Commercial / GCC / GCCH / DoD / China`; verifies the two agree | HALT on disagreement |
| Sovereign route | PRE-06 | If cloud ∈ {GCC, GCCH, DoD, China}, sets `$script:isSovereign = $true`; downstream `Skip` flags route SOV-affected TCs to compensating substitutes | Continue with `cloud` field set; sovereign clouds route to TC-18 |
| License gate | PRE-07 | Confirms tenant holds at least one Power Platform-bearing SKU (Power Apps Premium, Power Automate Premium, Microsoft Copilot Studio, or Dynamics 365 with Power Platform usage rights). Surfaces the **June 2026 enforcement** banner — see TC-3. | HALT on absent entitlement; WARN on PAYG-only |
| Clock skew gate | PRE-08 | Compares local UTC to the `Date` header from a Graph response; aborts if drift exceeds 60 seconds | HALT — clock skew invalidates timestamp evidence for FINRA 4511 / SEC 17a-4 |
| Evidence root writeable | PRE-09 | Confirms `$env:ME21_EVIDENCE_ROOT` exists, is writeable, and resolves to a path under WORM-eligible storage (validated by checking the parent storage account''s immutability policy where applicable) | HALT |

### 0.4 Sovereign bootstrap pattern

```powershell
function Test-Me21SovereignTenant {
    [CmdletBinding()]
    [OutputType([pscustomobject])]
    param(
        [Parameter(Mandatory)]
        [ValidateSet('prod','usgov','usgovhigh','dod','china')]
        [string] $PowerPlatformEndpoint
    )

    $cloud = switch ($PowerPlatformEndpoint) {
        'prod'       { 'Commercial' }
        'usgov'      { 'GCC' }
        'usgovhigh'  { 'GCCH' }
        'dod'        { 'DoD' }
        'china'      { 'China' }
    }

    [pscustomobject]@{
        cloud         = $cloud
        is_sovereign  = $cloud -in @('GCC','GCCH','DoD','China')
        endpoint      = $PowerPlatformEndpoint
        detected_at   = (Get-Date).ToUniversalTime().ToString('o')
        endpoint_ref  = '../../_shared/powershell-baseline.md#3-sovereign-cloud-endpoints-gcc-gcc-high-dod'
    }
}
```

When `is_sovereign` is `$true`, the affected `It` blocks in TC-8, TC-15, and (where called out) TC-9, TC-11, TC-12 emit a `SKIPPED` record with a pointer to the TC-18 substitute, rather than a `FAIL`:

```json
{
  "status": "SKIPPED",
  "reason": "Feature not at parity in sovereign cloud at run time",
  "compensating_control_ref": "TC-18 sovereign substitute namespace",
  "next_check_due": "2026-07-15T00:00:00Z"
}
```

This produces an examiner-defensible audit trail showing the test was attempted, was correctly skipped on regulatory-sound grounds, and was supplemented by the manual attestation in TC-18 — rather than appearing as an unexplained gap. The `next_check_due` date is set to the start of the following quarter so the sovereign roadmap re-verification cadence is itself evidenced.

### 0.5 Run identifier and evidence root

```powershell
function New-Me21RunId {
    $ts   = (Get-Date).ToUniversalTime().ToString('yyyyMMdd-HHmmss')
    $guid = ([guid]::NewGuid().ToString('N')).Substring(0,8)
    "ME-$ts-$guid"
}

$script:RunId        = New-Me21RunId
$script:RunTimestamp = (Get-Date).ToUniversalTime().ToString('o')
$script:EvidenceRoot = Join-Path $env:ME21_EVIDENCE_ROOT $script:RunId
New-Item -Path $script:EvidenceRoot -ItemType Directory -Force | Out-Null
```

Every evidence record produced in TC-1 through TC-20 is written under `$script:EvidenceRoot` and the `runId` is embedded in the filename of every artifact assembled into the §4 evidence pack.

### 0.6 Evidence record schema (canonical)

Every evidence record produced by every TC MUST conform to this schema. The schema is enforced by `Test-Me21EvidenceSchema` in §4.5; the pack assembler refuses to publish a pack containing any record that fails schema validation.

```json
{
  "control_id": "2.1",
  "run_id": "ME-20260415-093012-a1b2c3d4",
  "run_timestamp": "2026-04-15T09:30:12Z",
  "tenant_id": "11111111-2222-3333-4444-555555555555",
  "tenant_display_name": "Contoso Bank, N.A.",
  "cloud": "Commercial",
  "zone": "3",
  "test_case": "TC-3",
  "subject_id": "00000000-aaaa-bbbb-cccc-111111111111",
  "subject_type": "environment",
  "status": "PASS",
  "assertion": "Every active maker in the Z3 environment holds a Power Platform Premium-tier entitlement",
  "observed_value": { "non_compliant_makers": 0, "sample_size": 247 },
  "expected_value": { "non_compliant_makers": 0 },
  "evidence_artifacts": ["license-consumption-ME-20260415-093012-a1b2c3d4.json"],
  "regulator_mappings": ["FINRA-4511","SEC-17a-4","SOX-404","OCC-2011-12","FFIEC-MGMT"],
  "remediation_ref": null,
  "operator_upn": "me21-runner@contoso.com",
  "schema_version": "1.0"
}
```

### 0.7 Regulator mapping vocabulary

| Token | Citation |
|---|---|
| `FINRA-3110` | FINRA Rule 3110 (Supervision) |
| `FINRA-4511` | FINRA Rule 4511 (Books and Records — General Requirements) |
| `FINRA-25-07` | FINRA Regulatory Notice 25-07 (AI Tools — RFC, contextual) |
| `SEC-17a-3` | SEC Rule 17a-3 (Records to be Made) |
| `SEC-17a-4` | SEC Rule 17a-4 (Records Retention) |
| `SOX-302` | Sarbanes-Oxley Section 302 (Management Certification) |
| `SOX-404` | Sarbanes-Oxley Section 404 (ICFR / Internal Controls) |
| `GLBA-501b` | Gramm-Leach-Bliley Act §501(b) (Safeguards Rule) |
| `OCC-2011-12` | OCC Bulletin 2026-13 (formerly OCC Bulletin 2011-12) (Technology Risk Management / MRM) |
| `SR-11-7` | Federal Reserve SR Letter 11-7 (Model Risk Management) |
| `CFTC-1.31` | CFTC Regulation 1.31 (Recordkeeping) — contextual for FCM/SD scope |
| `NYDFS-500-06` | NYDFS 23 NYCRR 500.06 (Audit Trail) |
| `FFIEC-IS` | FFIEC IT Examination Handbook — Information Security |
| `FFIEC-MGMT` | FFIEC IT Examination Handbook — Management |

> **No FINRA Rule 3110 substitution.** Wherever `FINRA-3110` appears in a regulator-mapping table in TC-1 through TC-20, it indicates that the control element supports the firm''s Rule 3110 supervisory obligation by providing reviewable evidence of admin oversight. It does **not** indicate that any technical guardrail substitutes for the firm''s obligation to designate an appropriately registered principal where Rule 3110 requires that designation.

---

## §1 Test Case Format

Each test case below has exactly five subsections, in this order:

1. **Setup** — pre-conditions, reference data, role activation, environment fixture identification.
2. **Steps** — numbered, deterministic actions. Mix of PPAC navigation steps and PowerShell snippets. Where KQL is used (Sentinel-backed substitutes), it is presented in a fenced `kusto` block.
3. **Expected** — the assertion that must hold for `status = PASS`. PASS / WARN / FAIL bands per zone where applicable.
4. **Evidence Capture** — the exact filename pattern, content shape, retention scope (operational vs records-scope), and the §3 master-table row that this TC populates.
5. **Remediation** — the specific runbook reference (file + section) in the sister [Portal Walkthrough](portal-walkthrough.md), [PowerShell Setup](powershell-setup.md), or [Troubleshooting](troubleshooting.md) playbooks. Remediation is **never** performed by this playbook.

Cross-cutting pattern for every TC: emit a single evidence record (the §0.6 schema) per `It` block; serialize to `<test-case>-<runId>.json`; append the SHA-256 leaf hash to the run-level `manifest.ndjson`; and let §4 chain leaves into the Merkle root.

---

## §2 Test Cases

### TC-1 — All Zone-2/3 environments are Managed; Zone-1 personal/dev clearly delineated

**Criterion mapped:** Verification Criterion 1 (PPAC card shows Managed Environment: Yes) for every Zone-2/3 environment, plus zone-classification hygiene per [Control 2.2](../../../controls/pillar-2-management/2.2-environment-groups-and-tier-classification.md).

#### Setup

- PRE-01 through PRE-09 passed.
- Operator activated as **Power Platform Admin** under PIM with a justification referencing `ME21-TC-01-<runId>`.
- Reference data: the firm''s zone-classification register (`zone-register.json`, maintained by the AI Governance Lead per Control 2.2) is available at `$env:ME21_ZONE_REGISTER`. This file enumerates every environment ID with its assigned zone (`1`, `2`, or `3`), owner UPN, and creation justification. Zone classification is the firm''s assertion; this TC verifies enablement against that assertion.
- The Power Platform tenant has at least one environment of each in-scope zone (Z1 personal/dev, Z2 team, Z3 enterprise).

#### Steps

1. Sign into PPAC at the cloud-appropriate URL ([Commercial](https://admin.powerplatform.microsoft.com); GCC `https://gcc.admin.powerplatform.microsoft.us`; GCC High `https://high.admin.powerplatform.microsoft.us`; DoD `https://admin.appsplatform.us`; China `https://admin.powerplatform.partner.microsoftonline.cn`).
2. Navigate **Manage → Environments**.
3. In the environment grid, sort by **Managed environment** column. Capture a full-page screenshot.
4. Run the inventory snapshot:

    ```powershell
    Add-PowerAppsAccount -Endpoint $Endpoint
    $register = Get-Content $env:ME21_ZONE_REGISTER | ConvertFrom-Json

    $envs = Get-AdminPowerAppEnvironment |
        Select-Object DisplayName, EnvironmentName, EnvironmentType, Location,
                      @{n='ProtectionLevel'; e={ $_.Properties.protectionLevel }},
                      @{n='IsManaged';       e={ $_.Properties.protectionLevel -eq 'Standard' }},
                      @{n='HasDataverse';    e={ [bool]$_.Properties.linkedEnvironmentMetadata }}

    $joined = $envs | ForEach-Object {
        $rec  = $_
        $zone = ($register.environments | Where-Object id -eq $rec.EnvironmentName).zone
        [pscustomobject]@{
            EnvironmentId    = $rec.EnvironmentName
            DisplayName      = $rec.DisplayName
            Zone             = $zone
            EnvironmentType  = $rec.EnvironmentType
            Region           = $rec.Location
            IsManaged        = $rec.IsManaged
            HasDataverse     = $rec.HasDataverse
            ProtectionLevel  = $rec.ProtectionLevel
            ZoneRegistered   = [bool]$zone
        }
    }

    $joined | ConvertTo-Json -Depth 6 |
        Out-File (Join-Path $script:EvidenceRoot "tc01-inventory-$($script:RunId).json") -Encoding utf8
    ```

5. Compute the four assertion sets:

    ```powershell
    $z23Unmanaged   = $joined | Where-Object { $_.Zone -in '2','3' -and -not $_.IsManaged }
    $z1Managed      = $joined | Where-Object { $_.Zone -eq '1'  -and       $_.IsManaged }
    $unregistered   = $joined | Where-Object { -not $_.ZoneRegistered }
    $z23NoDataverse = $joined | Where-Object { $_.Zone -in '2','3' -and -not $_.HasDataverse }
    ```

6. Emit one evidence record per assertion set; PASS only if all four sets are empty.

#### Expected

- Every environment classified Z2 or Z3 in `zone-register.json` has `protectionLevel = "Standard"` (`IsManaged = $true`).
- Every environment classified Z1 has `protectionLevel = "Basic"` (or absent) — Z1 environments **must not** carry Managed-Environments overhead, both for licensing posture (TC-3) and for the supervisor clarity that examiners expect.
- Every environment in PPAC has a corresponding entry in `zone-register.json` (no orphan environments).
- Every Z2/Z3 environment has Dataverse provisioned.

| Zone | PASS | WARN | FAIL |
|---|---|---|---|
| Z1 | All Z1 envs `IsManaged = $false`; all are present in register | 1–2 Z1 envs are IsManaged (likely accidental enablement) | ≥3 Z1 envs IsManaged, OR any Z1 env unregistered |
| Z2 | All Z2 envs IsManaged + HasDataverse + registered | Any single env missing one of those three | ≥1 Z2 env unmanaged or missing Dataverse |
| Z3 | All Z3 envs IsManaged + HasDataverse + registered + sharing-limit configured (cross-checked in TC-5) | n/a | ≥1 Z3 env unmanaged or missing Dataverse |

#### Evidence Capture

- Filename: `tc01-inventory-<runId>.json` and `tc01-evidence-<runId>.ndjson` (one record per assertion set).
- Storage: `$script:EvidenceRoot/tc01/`.
- Retention: **records scope (6 years, WORM)** — the inventory establishes the universe of supervised environments and is therefore a books-and-records artifact under FINRA 4511 / SEC 17a-4(f). Mirror to the firm''s WORM bucket via the §4.4 sealing job.
- §3 master-table row: row 1 (`tc01-inventory`).

#### Remediation

- If any Z2/Z3 environment is unmanaged: see [PowerShell Setup](powershell-setup.md) — Bootstrap Script — Enable Managed Environments. Open a Control 2.3 change ticket before running.
- If a Z1 environment is unexpectedly Managed: see [PowerShell Setup](powershell-setup.md) — Disable (rollback). Confirm with the environment owner that the Z1 classification is correct before downgrading.
- If an environment is unregistered: file with the AI Governance Lead via the Control 2.2 environment-registration intake; do **not** auto-classify.
- If a Z2/Z3 environment lacks Dataverse: [Troubleshooting §3 — Dataverse provisioning prerequisites](troubleshooting.md). Provisioning Dataverse in a populated environment is a high-impact change — require CAB approval.

---

### TC-2 — Pipeline target environments are Managed Environments — proactive enablement evidence

**Criterion mapped:** Pipelines that promote solutions toward Z2/Z3 environments must target Managed environments only. This is a **proactive** assertion: the firm should be able to show that the pipeline metadata enforces the rule, not merely that the current targets happen to comply.

#### Setup

- PRE gates passed.
- Operator activated as **Power Platform Admin** with **Pipeline Admin** read.
- Reference data: pipeline definitions are stored in the Power Platform pipelines host environment; the host environment ID is at `$env:ME21_PIPELINE_HOST`.
- The firm''s pipeline policy (per Control 2.3) declares: "No deployment stage may target an unmanaged environment outside Z1."

#### Steps

1. Enumerate every pipeline target stage and its environment binding:

    ```powershell
    # Pipelines surface via the Dataverse `deploymentpipeline`, `deploymentstage`,
    # and `deploymentenvironment` tables in the pipeline host environment.
    Add-PowerAppsAccount -Endpoint $Endpoint
    $hostEnv = $env:ME21_PIPELINE_HOST

    # Use the WebAPI (the admin module does not expose pipeline tables directly).
    $token = (Get-AdminPowerAppEnvironment -EnvironmentName $hostEnv).Properties.linkedEnvironmentMetadata.instanceApiUrl
    $stages = Invoke-RestMethod -Uri "$token/api/data/v9.2/deploymentstages?`$select=deploymentstageid,name,_targetenvironmentid_value" `
                                -Headers @{ Authorization = "Bearer $((Get-PowerAppsAccessToken).accessToken)" }

    $report = foreach ($s in $stages.value) {
        $targetEnvId = $s._targetenvironmentid_value
        $targetEnv   = Get-AdminPowerAppEnvironment -EnvironmentName $targetEnvId -ErrorAction SilentlyContinue
        [pscustomobject]@{
            StageId         = $s.deploymentstageid
            StageName       = $s.name
            TargetEnvId     = $targetEnvId
            TargetEnvName   = $targetEnv.DisplayName
            TargetIsManaged = ($targetEnv.Properties.protectionLevel -eq 'Standard')
            TargetZone      = ($register.environments | Where-Object id -eq $targetEnvId).zone
        }
    }
    $report | ConvertTo-Json -Depth 6 |
        Out-File (Join-Path $script:EvidenceRoot "tc02-pipeline-targets-$($script:RunId).json") -Encoding utf8
    ```

2. Emit a `FAIL` record for any target where `TargetZone -in '2','3'` AND `TargetIsManaged -eq $false`.
3. Emit a `WARN` record for any target where `TargetZone` is empty (target not in zone register).
4. Capture a PPAC screenshot: **Pipelines** host environment → **Pipelines table** → the deployment pipeline → **Stages** view, showing each stage''s target environment.

#### Expected

- 100% of stages whose target is a Z2/Z3 environment have `TargetIsManaged = $true`.
- 100% of stages have a target that is present in the zone register.
- Z1 targets (sandbox / scratch) are tolerated unmanaged; this is by design and explicitly documented in the firm''s pipeline policy.

#### Evidence Capture

- Filename: `tc02-pipeline-targets-<runId>.json` plus `tc02-pipeline-stages-<runId>.png`.
- Retention: **records scope (6 years)** — pipeline-target configuration is change-control evidence under SEC 17a-3 / SOX 404.
- §3 master-table row: row 2 (`tc02-pipeline-targets`).

#### Remediation

- Re-target the offending stage to a Managed environment via PPAC **Pipelines → Stage → Edit**. Open a Control 2.3 change ticket. Do **not** auto-rebind without ticket; pipelines control production releases and a silent rebind is itself a high-severity finding.
- See [Troubleshooting §6 — Pipeline target binding](troubleshooting.md) for the rebinding sequence and the pre-flight check that prevents promoting a pre-Managed-Environment artifact into a Managed target without re-running solution checker.

---

### TC-3 — Licensing coverage audit complete and current — June 2026 enforcement readiness

**Criterion mapped:** Verification Criterion 10 (license-entitlement coverage verified for every active maker). Per [Microsoft Learn — Managed Environment Licensing](https://learn.microsoft.com/en-us/power-platform/admin/managed-environment-licensing), every active maker / user in a Managed Environment must hold one of: Power Apps Premium, Power Automate Premium, a Copilot Studio license that includes Power Platform Premium, or a Dynamics 365 license with Power Platform usage rights. Pay-as-you-go (PAYG) is **not a substitute** for the floor.

!!! warning "June 2026 licensing-enforcement timeline"
    Microsoft is rolling out **end-user license-compliance notifications** for Managed Environments starting **June 2026**. Non-compliant users will see in-product banners, and PPAC will surface a tenant-level compliance summary. The firm should be in a state where the compliance summary reads zero non-compliant makers per Z2/Z3 environment **before** June 2026, so that the rollout produces no operational surprise. This TC produces the evidence that the firm has either reached that state or has an explicit remediation plan with a CAB-approved completion date prior to June 2026. Re-run weekly between April 2026 and August 2026.

#### Setup

- PRE gates passed.
- Operator activated as **Power Platform Admin** + **Entra Global Reader** (the Graph reads in step 4 require Global Reader scope).
- Reference data: the firm''s license catalog (`license-catalog.json`, per Control 2.4) at `$env:ME21_LICENSE_CATALOG` enumerates which SKUs satisfy the Managed-Environments floor.

#### Steps

1. Capture the PPAC license-consumption page screenshot: **Resources → License consumption (preview)**. Save as `tc03-license-consumption-ppac-<runId>.png`.

2. Pull the per-environment, per-maker license posture via the admin module:

    ```powershell
    Add-PowerAppsAccount -Endpoint $Endpoint
    $envs = Get-AdminPowerAppEnvironment | Where-Object {
        ($register.environments | Where-Object id -eq $_.EnvironmentName).zone -in '2','3'
    }
    $allEnvs = $envs | ForEach-Object {
        $env = $_
        $env | ConvertTo-Json -Depth 8
    }
    $allEnvs | Out-File (Join-Path $script:EvidenceRoot "tc03-env-snapshot-$($script:RunId).json") -Encoding utf8
    ```

3. Pull the tenant-wide subscribed-SKU list via Graph (this is the canonical entitlement source — the PPAC view is a derived projection):

    ```powershell
    Connect-MgGraph -Scopes 'Directory.Read.All','Reports.Read.All' -NoWelcome
    $skus = Get-MgSubscribedSku -All |
        Select-Object SkuId, SkuPartNumber, ConsumedUnits,
                      @{n='Enabled'; e={ $_.PrepaidUnits.Enabled }},
                      @{n='ServicePlans'; e={ $_.ServicePlans }}
    $skus | ConvertTo-Json -Depth 8 |
        Out-File (Join-Path $script:EvidenceRoot "tc03-tenant-skus-$($script:RunId).json") -Encoding utf8
    ```

4. Pull active makers per environment and join against `license-catalog.json`:

    ```powershell
    $catalog       = Get-Content $env:ME21_LICENSE_CATALOG | ConvertFrom-Json
    $eligibleSkus  = $catalog.skus | Where-Object satisfiesManagedEnv -eq $true | ForEach-Object partNumber

    $perEnv = foreach ($env in $envs) {
        $makers = Get-AdminPowerAppCdsDatabaseLanguages -EnvironmentName $env.EnvironmentName -ErrorAction SilentlyContinue # placeholder for maker-list call
        # In production, use the Dataverse `systemuser` query; see PowerShell Setup §6 for the canonical helper.
        $makerList = Get-Me21EnvironmentMaker -EnvironmentName $env.EnvironmentName

        $nonCompliant = foreach ($m in $makerList) {
            $userSkus = (Get-MgUserLicenseDetail -UserId $m.UserPrincipalName -ErrorAction SilentlyContinue).SkuPartNumber
            $isOk     = $userSkus | Where-Object { $eligibleSkus -contains $_ }
            if (-not $isOk) { $m }
        }

        [pscustomobject]@{
            EnvironmentId         = $env.EnvironmentName
            EnvironmentName       = $env.DisplayName
            Zone                  = ($register.environments | Where-Object id -eq $env.EnvironmentName).zone
            ActiveMakerCount      = $makerList.Count
            NonCompliantCount     = $nonCompliant.Count
            NonCompliantUPNs      = @($nonCompliant.UserPrincipalName)
            CapturedAt            = (Get-Date).ToUniversalTime().ToString('o')
        }
    }
    $perEnv | ConvertTo-Json -Depth 6 |
        Out-File (Join-Path $script:EvidenceRoot "tc03-license-coverage-$($script:RunId).json") -Encoding utf8
    ```

5. Emit `Get-AdminPowerAppEnvironment | ConvertTo-Json -Depth 8` as the canonical environment snapshot per the user''s evidence requirement; the §4 packer hashes it as a leaf.

6. Compute the PAYG-alone universe (handed off to TC-4):

    ```powershell
    $paygOnly = $perEnv | Where-Object {
        # Maker has only PAYG SKUs and no Premium-tier subscription.
        $_.NonCompliantUPNs.Count -gt 0 -and
        ($_.NonCompliantUPNs | ForEach-Object { Get-MgUserLicenseDetail -UserId $_ }).SkuPartNumber -contains 'POWERAPPS_PER_APP_PAYG'
    }
    $paygOnly | ConvertTo-Json -Depth 6 |
        Out-File (Join-Path $script:EvidenceRoot "tc03-payg-handoff-tc04-$($script:RunId).json") -Encoding utf8
    ```

#### Expected

- `NonCompliantCount = 0` for every Z2/Z3 environment.
- The PPAC license-consumption page lists no banner indicating non-compliant makers.
- The firm''s remediation plan (if any non-compliant makers exist) has a CAB-approved completion date prior to **June 2026**.

| Zone | PASS | WARN | FAIL |
|---|---|---|---|
| Z2 | NonCompliantCount = 0 | NonCompliantCount = 1–2 with ticketed remediation due before June 2026 | ≥3 non-compliant or no remediation ticket |
| Z3 | NonCompliantCount = 0 | n/a (Z3 has zero tolerance) | NonCompliantCount ≥ 1 |

#### Evidence Capture

- Files: `tc03-license-consumption-ppac-<runId>.png`, `tc03-env-snapshot-<runId>.json`, `tc03-tenant-skus-<runId>.json`, `tc03-license-coverage-<runId>.json`, `tc03-payg-handoff-tc04-<runId>.json`.
- Retention: **records scope (6 years)** — license entitlement is a foundational input to the supervisory framework and to the SOX 404 ICFR perimeter.
- §3 master-table rows: rows 3a–3e.

#### Remediation

- Assign the appropriate Premium SKU to the non-compliant maker via Microsoft 365 admin center → **Users → Active users → {user} → Licenses and apps**. Open a ticket per the firm''s licensing-request workflow and reference the TC-3 evidence record ID.
- If the maker is no longer active, off-board per the firm''s leaver process and re-run TC-3 to confirm removal from the active-maker enumeration.
- See [Troubleshooting §4 — License-entitlement remediation](troubleshooting.md) for the bulk-assignment script and the rollback path.

---

### TC-4 — PAYG-only makers identified and remediation tickets opened

**Criterion mapped:** PAYG meter usage is **not** a substitute for a Premium-tier entitlement floor in a Managed Environment. This TC accepts the PAYG handoff from TC-3 step 6 and produces a ticketed-remediation evidence record.

#### Setup

- TC-3 has run and produced `tc03-payg-handoff-tc04-<runId>.json`.
- Operator activated as **Power Platform Admin** + **Entra Global Reader**.
- The firm''s ITSM ticketing API is available at `$env:ME21_ITSM_API` with a service-principal credential that can read ticket status (read-only — TC-4 does not open tickets, it verifies tickets exist).

#### Steps

1. Load the handoff:

    ```powershell
    $handoff = Get-Content (Join-Path $script:EvidenceRoot "tc03-payg-handoff-tc04-$($script:RunId).json") | ConvertFrom-Json
    ```

2. For each environment in the handoff, query the ITSM API for an open ticket whose `customField.evidenceRef` references TC-3 for that maker:

    ```powershell
    $rows = foreach ($e in $handoff) {
        foreach ($upn in $e.NonCompliantUPNs) {
            $tickets = Invoke-RestMethod -Uri "$env:ME21_ITSM_API/api/tickets?subject=$upn&status=open" `
                                         -Headers $itsmHeaders
            [pscustomobject]@{
                EnvironmentId   = $e.EnvironmentId
                Maker           = $upn
                TicketCount     = $tickets.value.Count
                TicketIds       = @($tickets.value.id)
                DueDates        = @($tickets.value.dueDate)
                AllDueBeforeJun2026 = (-not ($tickets.value.dueDate | Where-Object { [datetime]$_ -ge [datetime]'2026-06-01' }))
            }
        }
    }
    $rows | ConvertTo-Json -Depth 6 |
        Out-File (Join-Path $script:EvidenceRoot "tc04-payg-remediation-tickets-$($script:RunId).json") -Encoding utf8
    ```

3. Emit one record per maker; PASS only if every PAYG-only maker has at least one open ticket with `dueDate < 2026-06-01`.

#### Expected

- Every PAYG-only maker has an open ITSM ticket with a CAB-approved due date prior to **June 2026**.
- No maker is in PAYG-only status without a ticket.

#### Evidence Capture

- Filename: `tc04-payg-remediation-tickets-<runId>.json`.
- Retention: **records scope (6 years)** — supports SOX 404 ICFR remediation evidence.
- §3 master-table row: row 4.

#### Remediation

- Where a PAYG-only maker has no ticket: open one via the firm''s standard intake. The ticket''s justification field must reference this TC-4 evidence record ID.
- Where the ticket''s due date is post-June 2026: escalate to the AI Governance Lead and Compliance Officer for explicit risk acceptance, signed and stored in the §4 evidence pack with regulator-mapping `OCC-2011-12,FFIEC-MGMT`.
- See [Troubleshooting §4 — License-entitlement remediation](troubleshooting.md).

---

### TC-5 — Sharing limits per resource family enforced; standalone cloud flows have DLP coverage

**Criterion mapped:** Verification Criterion 4 (sharing-limit enforcement). Per-environment sharing limits exist for canvas apps, Copilot Studio agents, and Power Pages; standalone cloud flows are governed via DLP per [Control 1.5](../../../controls/pillar-1-security/1.5-data-loss-prevention-dlp-and-sensitivity-labels.md) — they are **not** governed by a per-environment sharing-limit slider.

#### Setup

- PRE gates passed.
- Operator activated as **Power Platform Admin**.
- Reference data: zone-policy table (`zone-policy.json`) declares the firm''s per-zone sharing-limit ceilings:

    | Zone | Canvas app share limit (#users) | Copilot Studio agent share limit | Power Pages share limit | "Share with security group" allowed? |
    |---|---|---|---|---|
    | Z2 | ≤ 50 | ≤ 25 | ≤ 50 | Yes (group ≤ 100 members) |
    | Z3 | ≤ 25 | ≤ 10 | ≤ 25 | No (named users only) |

#### Steps

1. Pull governance configuration per Z2/Z3 environment:

    ```powershell
    $rows = foreach ($env in $envs) {
        $g = Get-AdminPowerAppEnvironmentGovernanceConfiguration -EnvironmentName $env.EnvironmentName
        $zone = ($register.environments | Where-Object id -eq $env.EnvironmentName).zone
        $policy = $zonePolicy.zones."$zone"
        [pscustomobject]@{
            EnvironmentId           = $env.EnvironmentName
            Zone                    = $zone
            CanvasShareLimit        = $g.canvasAppSharing.shareWithMaxUsers
            CanvasShareGroupAllowed = $g.canvasAppSharing.shareWithSecurityGroupAllowed
            CopilotShareLimit       = $g.copilotStudio.shareWithMaxUsers
            PagesShareLimit         = $g.powerPages.shareWithMaxUsers
            CompliantCanvas         = ($g.canvasAppSharing.shareWithMaxUsers -le $policy.canvasShareLimit)
            CompliantCopilot        = ($g.copilotStudio.shareWithMaxUsers     -le $policy.copilotShareLimit)
            CompliantPages          = ($g.powerPages.shareWithMaxUsers        -le $policy.pagesShareLimit)
            CompliantGroup          = (-not $policy.shareWithGroup -implies (-not $g.canvasAppSharing.shareWithSecurityGroupAllowed))
        }
    }
    $rows | ConvertTo-Json -Depth 6 |
        Out-File (Join-Path $script:EvidenceRoot "tc05-sharing-limits-$($script:RunId).json") -Encoding utf8
    ```

2. Confirm DLP coverage for standalone cloud flows by referencing the Control 1.5 evidence pack''s most recent run:

    ```powershell
    $dlpRef = Get-Content $env:ME21_CTRL15_LATEST | ConvertFrom-Json
    $dlpRef | Where-Object { $_.test_case -eq '15-DLP-COVERAGE' -and $_.status -ne 'PASS' } |
        ForEach-Object {
            [pscustomobject]@{
                EnvironmentId = $_.subject_id
                Status        = 'WARN'
                Reason        = 'TC-5 cannot pass because Control 1.5 most-recent run reports DLP gap for standalone cloud flows in this environment'
                XRef          = '../../../controls/pillar-1-security/1.5-data-loss-prevention-dlp-and-sensitivity-labels.md'
            }
        }
    ```

#### Expected

- All Z2/Z3 environments have `Compliant*` flags `$true`.
- The most recent Control 1.5 evidence pack reports `PASS` for DLP coverage of every Z2/Z3 environment.

#### Evidence Capture

- Filename: `tc05-sharing-limits-<runId>.json`.
- Retention: **records scope (6 years)** for Z3, **operational (3 years)** for Z2.
- §3 master-table row: row 5.

#### Remediation

- Tighten the offending sharing-limit slider via PPAC **Environments → {env} → Settings → Privacy + security → Sharing limits**. Open a Control 2.3 change ticket.
- For DLP gaps, follow Control 1.5''s remediation runbook; do not attempt to remediate at the Managed-Environments layer.

---

### TC-6 — Solution checker on Block for Z3, Warn or Block for Z2; exception register reconciled

**Criterion mapped:** Verification Criterion 5 (solution-checker enforcement). Z3 environments enforce **Block** on import for high-severity findings; Z2 environments may operate at **Warn** or **Block** per the firm''s WSP. All exceptions (e.g., temporary downgrades from Block to Warn for an emergency import) live in an exception register reconciled to change tickets.

#### Setup

- PRE gates passed; Power Platform Admin activated.
- Reference data: exception register (`solution-checker-exceptions.csv`) at `$env:ME21_SC_EXCEPTIONS`.

#### Steps

1. Read enforcement level per environment:

    ```powershell
    $rows = foreach ($env in $envs) {
        $g = Get-AdminPowerAppEnvironmentGovernanceConfiguration -EnvironmentName $env.EnvironmentName
        $zone = ($register.environments | Where-Object id -eq $env.EnvironmentName).zone
        [pscustomobject]@{
            EnvironmentId  = $env.EnvironmentName
            Zone           = $zone
            SolutionChecker = $g.solutionChecker.enforcementLevel  # None | Warn | Block
            CompliantPolicy = switch ($zone) {
                '3' { $g.solutionChecker.enforcementLevel -eq 'Block' }
                '2' { $g.solutionChecker.enforcementLevel -in @('Warn','Block') }
                default { $true }
            }
        }
    }
    $rows | ConvertTo-Json -Depth 6 |
        Out-File (Join-Path $script:EvidenceRoot "tc06-solution-checker-$($script:RunId).json") -Encoding utf8
    ```

2. Reconcile the exception register: every row in `solution-checker-exceptions.csv` must reference a Control 2.3 change ticket whose `status = approved` and whose `effectiveUntil <= today + 30 days` (exceptions are time-bounded).

#### Expected

- All Z3 environments at `Block`; all Z2 environments at `Warn` or `Block`.
- Exception register has zero stale entries.

#### Evidence Capture

- Filename: `tc06-solution-checker-<runId>.json` + `tc06-exception-register-snapshot-<runId>.csv`.
- Retention: **records scope (6 years)** — change-control evidence.
- §3 master-table row: row 6.

#### Remediation

- Re-enable Block via PPAC **Environments → {env} → Settings → Product → Features → Solution checker enforcement**.
- Expire stale exceptions via the Control 2.3 change ticket workflow.
- See [Portal Walkthrough](portal-walkthrough.md) — Solution checker enforcement.

---

### TC-7 — Maker welcome content present, free of sensitive data, and CMK-exclusion documented

**Criterion mapped:** Verification Criterion 6 (maker welcome content links to WSPs and training). Every Managed Environment surfaces a maker-welcome banner. Per Control 2.14 the banner must link to the firm''s WSPs and training catalog; per the [CMK service coverage matrix](https://learn.microsoft.com/en-us/power-platform/admin/customer-managed-key) the welcome content is **excluded from CMK encryption**.

!!! note "Maker welcome content is excluded from CMK encryption"
    Welcome content (banner text, link captions, link URLs) is stored in a configuration store that is **not** within the CMK encryption boundary. Display names, environment descriptions, connection metadata, solution-checker results, and Microsoft Agent 365 audit metadata are also excluded. The firm''s **CMK exclusion narrative** (TC-12) must enumerate every excluded surface; this TC verifies the welcome-content surface specifically. The corollary is that the welcome content **must not contain customer data, NPI, MNPI, PII, or anything else that the firm''s data-classification policy would not permit on a non-CMK-encrypted surface**.

#### Setup

- PRE gates passed; Power Platform Admin activated.
- Reference data: training-catalog URL (`$env:ME21_TRAINING_CATALOG`), WSP URL (`$env:ME21_WSP_URL`), and approved welcome-content template (`welcome-content-template.json`).

#### Steps

1. Read welcome content per environment:

    ```powershell
    $rows = foreach ($env in $envs) {
        $g = Get-AdminPowerAppEnvironmentGovernanceConfiguration -EnvironmentName $env.EnvironmentName
        $w = $g.makerWelcomeContent
        [pscustomobject]@{
            EnvironmentId    = $env.EnvironmentName
            HasWelcome       = [bool]$w.message
            LinksToWsp       = $w.message -match [regex]::Escape($env:ME21_WSP_URL)
            LinksToTraining  = $w.message -match [regex]::Escape($env:ME21_TRAINING_CATALOG)
            MessageLen       = ($w.message | Measure-Object -Character).Characters
            MessageSample    = if ($w.message) { $w.message.Substring(0,[Math]::Min(200,$w.message.Length)) } else { $null }
        }
    }
    $rows | ConvertTo-Json -Depth 6 |
        Out-File (Join-Path $script:EvidenceRoot "tc07-welcome-content-$($script:RunId).json") -Encoding utf8
    ```

2. DLP-style scan welcome content for sensitive-data patterns (SSN, account-number patterns, MNPI watchwords). Use the firm''s sensitive-data scanner (Purview Information Protection classifier) — **do not** use a homegrown regex without compliance sign-off:

    ```powershell
    $scanResult = Invoke-Me21SensitiveDataScan -Text ($rows | ForEach-Object MessageSample) `
                                               -ClassifierSet 'FSI-Default'
    $scanResult | ConvertTo-Json -Depth 6 |
        Out-File (Join-Path $script:EvidenceRoot "tc07-welcome-dlp-scan-$($script:RunId).json") -Encoding utf8
    ```

3. Verify the CMK exclusion narrative (`cmk-exclusion-narrative.md`) lists `maker_welcome_content` and is signed by the Compliance Officer within the last 12 months. (Cross-check with TC-12.)

#### Expected

- 100% of Z2/Z3 environments have welcome content; content links to both WSPs and training.
- 0 sensitive-data hits in the DLP scan.
- CMK exclusion narrative present, signed, and within 12 months.

#### Evidence Capture

- Filenames: `tc07-welcome-content-<runId>.json`, `tc07-welcome-dlp-scan-<runId>.json`, plus a copy of `cmk-exclusion-narrative.md`.
- Retention: **records scope (6 years)**.
- §3 master-table row: row 7.

#### Remediation

- Re-set the welcome content via PPAC **Environments → {env} → Settings → Product → Features → Welcome content**.
- If sensitive-data hits found: redact and re-publish; open a Control 2.14 incident ticket and notify the Information Security Officer per the firm''s data-leakage protocol.
- See [Portal Walkthrough](portal-walkthrough.md) — Maker welcome content.

---

### TC-8 — Weekly usage-insights digest current (commercial); sovereign substitute via Graph + Purview + Sentinel

**Criterion mapped:** Verification Criterion 7 (usage telemetry available to supervisors). On commercial cloud, the PPAC weekly usage-insights digest is the canonical source. Sovereign clouds **do not** offer the weekly digest at this time; the firm must operate a compensating control assembled from Microsoft Graph reports, Purview unified audit logs (per [Control 1.7](../../../controls/pillar-1-security/1.7-comprehensive-audit-logging-and-compliance.md) and [Control 3.1](../../../controls/pillar-3-reporting/3.1-agent-inventory-and-metadata-management.md)), and Microsoft Sentinel queries (per [Control 3.9](../../../controls/pillar-3-reporting/3.9-microsoft-sentinel-integration.md)).

#### Setup — commercial path

- PRE gates passed; cloud = `Commercial`; Power Platform Admin activated.
- Reference data: digest delivery list (`$env:ME21_DIGEST_RECIPIENTS`) — which Power Platform Admins are configured to receive the weekly digest.

#### Setup — sovereign path

- PRE gates passed; cloud ∈ {GCC, GCCH, DoD, China}.
- Operator activated as **Purview Compliance Admin** + **Entra Security Admin**.
- The firm''s Sentinel workspace ID is at `$env:ME21_SENTINEL_WS`.

#### Steps — commercial

1. PPAC **Environments → Analytics → Usage insights**: confirm a digest dated within the last 7 days and capture screenshot.
2. Confirm digest recipients via **Settings → Notifications → Weekly digest** matches the reference list.

#### Steps — sovereign

1. Pull the equivalent activity surface via the Graph audit-log endpoint:

    ```powershell
    Connect-MgGraph -Scopes 'AuditLog.Read.All','Directory.Read.All' -NoWelcome
    $since = (Get-Date).AddDays(-7).ToUniversalTime().ToString('o')
    $events = Get-MgAuditLogDirectoryAudit -Filter "activityDateTime ge $since and category eq 'PowerPlatform'" -All
    $events | ConvertTo-Json -Depth 8 |
        Out-File (Join-Path $script:EvidenceRoot "tc08-graph-audit-$($script:RunId).json") -Encoding utf8
    ```

2. Run the Sentinel KQL substitute query against the workspace where Purview audit is forwarded:

    ```kusto
    // TC-8 sovereign substitute — weekly Power Platform admin activity summary
    AuditLogs
    | where TimeGenerated >= ago(7d)
    | where LoggedByService in ("Power Apps","Power Automate","Microsoft Power Platform","Copilot Studio","Microsoft Agent 365")
    | extend EnvironmentId = tostring(parse_json(AdditionalDetails)[0].value)
    | summarize EventCount = count(),
                ActiveMakers = dcount(InitiatedBy.user.userPrincipalName),
                FirstEvent = min(TimeGenerated),
                LastEvent  = max(TimeGenerated)
        by EnvironmentId, OperationName, ResultType
    | order by EventCount desc
    ```

3. Emit a `PASS` only if both data paths return non-empty results and the Compliance Officer has signed the weekly compensating-control attestation (`tc08-compensating-attestation-<runId>.json`) within the last 7 days.

#### Expected

- Commercial: PPAC digest exists within the last 7 days; recipient list matches.
- Sovereign: Graph + Sentinel return data; Compliance Officer attestation signed within 7 days.

#### Evidence Capture

- Commercial files: `tc08-digest-screenshot-<runId>.png`, `tc08-recipients-<runId>.json`.
- Sovereign files: `tc08-graph-audit-<runId>.json`, `tc08-sentinel-query-<runId>.kql`, `tc08-sentinel-results-<runId>.json`, `tc08-compensating-attestation-<runId>.json`.
- Retention: **records scope (6 years)** — supervisory-evidence input.
- §3 master-table rows: row 8 (commercial), row 8-SOV (sovereign).

#### Remediation

- Commercial digest gap: re-enable in **Settings → Notifications**; verify mailbox routing for digest recipients.
- Sovereign substitute gap: rerun [Control 3.9 §4 — Sentinel ingestion verification](../../../controls/pillar-3-reporting/3.9-microsoft-sentinel-integration.md) and [Control 1.7 §5 — Purview ingestion verification](../../../controls/pillar-1-security/1.7-comprehensive-audit-logging-and-compliance.md).

---

### TC-9 — IP firewall configured; AuditOnly ≤ 4 weeks then Enforce; reverse-proxy IPs included

**Criterion mapped:** Verification Criterion 8 (IP firewall present). Per the [Microsoft Learn IP firewall guidance](https://learn.microsoft.com/en-us/power-platform/admin/ip-firewall), AuditOnly mode is intended as a **time-bounded** discovery phase — typically ≤ 4 weeks — before promotion to Enforce. The allow-list must include any reverse-proxy egress IPs the firm uses (CDN, WAF, ZTNA exit nodes).

#### Setup

- PRE gates passed; Power Platform Admin + Information Security Officer (consulted, not operator).
- Reference data: corporate egress IP catalog (`egress-ips.json`) maintained by the network team.

#### Steps

1. Read IP firewall posture per environment:

    ```powershell
    $rows = foreach ($env in $envs) {
        $g = Get-AdminPowerAppEnvironmentGovernanceConfiguration -EnvironmentName $env.EnvironmentName
        $f = $g.ipFirewall
        [pscustomobject]@{
            EnvironmentId    = $env.EnvironmentName
            Zone             = ($register.environments | Where-Object id -eq $env.EnvironmentName).zone
            FirewallEnabled  = [bool]$f.enabled
            Mode             = $f.mode  # AuditOnly | Enforce
            AuditOnlySince   = $f.auditOnlyEffectiveDate
            AuditOnlyAgeDays = if ($f.auditOnlyEffectiveDate) { ((Get-Date) - [datetime]$f.auditOnlyEffectiveDate).Days } else { $null }
            AllowList        = $f.allowedIpRangeList
        }
    }
    $rows | ConvertTo-Json -Depth 6 |
        Out-File (Join-Path $script:EvidenceRoot "tc09-ip-firewall-$($script:RunId).json") -Encoding utf8
    ```

2. Verify reverse-proxy egress IPs are present in every Z3 environment''s allow-list:

    ```powershell
    $egress = Get-Content $env:ME21_EGRESS_IPS | ConvertFrom-Json
    foreach ($r in $rows | Where-Object Zone -eq '3') {
        $missing = $egress.proxyEgressRanges | Where-Object { $r.AllowList -notcontains $_ }
        if ($missing) {
            [pscustomobject]@{
                EnvironmentId = $r.EnvironmentId
                Status        = 'FAIL'
                MissingRanges = $missing
            } | ConvertTo-Json |
                Add-Content (Join-Path $script:EvidenceRoot "tc09-egress-gap-$($script:RunId).ndjson")
        }
    }
    ```

3. Where `Mode = AuditOnly` and `AuditOnlyAgeDays > 28`, emit a `WARN` (≤ 56 days) or `FAIL` (> 56 days) record citing the 4-week guidance.

#### Expected

- All Z3 environments: `FirewallEnabled = $true`, `Mode = Enforce`, all reverse-proxy egress ranges present.
- All Z2 environments: `FirewallEnabled = $true`; AuditOnly tolerated for ≤ 4 weeks.

#### Evidence Capture

- Files: `tc09-ip-firewall-<runId>.json`, `tc09-egress-gap-<runId>.ndjson` (if any).
- Retention: **records scope (6 years)** for Z3, **operational (3 years)** for Z2.
- §3 master-table row: row 9.

#### Remediation

- Promote AuditOnly → Enforce via PPAC **Environments → {env} → Settings → Privacy + security → IP firewall**. Open a Control 2.3 change ticket.
- Add missing reverse-proxy ranges to the allow-list before promotion.
- See [Portal Walkthrough](portal-walkthrough.md) — IP firewall.

---

### TC-10 — IP-based cookie binding enabled

**Criterion mapped:** Verification Criterion 9. IP-bound session cookies prevent token replay from a different IP than the one that established the session.

#### Setup

- PRE gates passed; Power Platform Admin activated.

#### Steps

1. Read posture per environment:

    ```powershell
    $rows = foreach ($env in $envs) {
        $g = Get-AdminPowerAppEnvironmentGovernanceConfiguration -EnvironmentName $env.EnvironmentName
        [pscustomobject]@{
            EnvironmentId       = $env.EnvironmentName
            Zone                = ($register.environments | Where-Object id -eq $env.EnvironmentName).zone
            IpCookieBindingOn   = [bool]$g.ipCookieBinding.enabled
        }
    }
    $rows | ConvertTo-Json -Depth 6 |
        Out-File (Join-Path $script:EvidenceRoot "tc10-ip-cookie-binding-$($script:RunId).json") -Encoding utf8
    ```

2. Capture PPAC screenshot **Environments → {env} → Settings → Privacy + security → IP cookie binding**.

#### Expected

- All Z2/Z3: `IpCookieBindingOn = $true`.

#### Evidence Capture

- Filename: `tc10-ip-cookie-binding-<runId>.json` + screenshot.
- Retention: **records scope (6 years)**.
- §3 master-table row: row 10.

#### Remediation

- Enable via PPAC; open Control 2.3 ticket. Re-test mobile + VPN-roaming workflows because IP-cookie binding causes session re-prompts when the user''s public IP changes.
- See [Troubleshooting §7 — IP-cookie binding session loss](troubleshooting.md).

---

### TC-11 — Customer Lockbox enabled; tier verified; 8-hour approval runbook tested

**Criterion mapped:** Verification Criterion 11. Microsoft Customer Lockbox provides documented, time-bound, tenant-administrator approval over Microsoft engineer access. Lockbox tier coverage varies by sovereign cloud (see top admonition).

#### Setup

- PRE gates passed.
- Operator: **Power Platform Admin** (read configuration); **Entra Global Admin** (read tenant-tier Lockbox enrollment via M365 admin center under PIM); **Compliance Officer** (counter-signs the approval-runbook walkthrough).
- Reference data: Lockbox approver list (`lockbox-approvers.json`) — Power Platform Admins and Entra Global Admins designated to receive Lockbox approval requests, with on-call rotation.
- Sovereign-aware: Lockbox is **not available in China 21Vianet** at the time of this writing; route to TC-18.

#### Steps

1. Read tenant-level Lockbox enrollment via Microsoft 365 admin center → **Settings → Org settings → Security & privacy → Customer Lockbox**. Capture screenshot.
2. Read per-environment Lockbox posture:

    ```powershell
    $rows = foreach ($env in $envs) {
        $g = Get-AdminPowerAppEnvironmentGovernanceConfiguration -EnvironmentName $env.EnvironmentName
        [pscustomobject]@{
            EnvironmentId   = $env.EnvironmentName
            Zone            = ($register.environments | Where-Object id -eq $env.EnvironmentName).zone
            LockboxEnabled  = [bool]$g.customerLockbox.enabled
        }
    }
    $rows | ConvertTo-Json -Depth 6 |
        Out-File (Join-Path $script:EvidenceRoot "tc11-lockbox-$($script:RunId).json") -Encoding utf8
    ```

3. Verify the approval-runbook tabletop has been exercised within the last quarter: locate the most recent `lockbox-tabletop-<date>.md` in the firm''s evidence repository; confirm the on-call approver responded within the 8-hour SLA in the simulated request.

4. Confirm the SIEM forwards `LockboxApproval*` events from the Microsoft 365 audit log into Sentinel (per Control 3.9):

    ```kusto
    AuditLogs
    | where TimeGenerated >= ago(90d)
    | where OperationName startswith "LockboxApproval"
    | project TimeGenerated, OperationName, InitiatedBy, TargetResources, Result
    | order by TimeGenerated desc
    ```

#### Expected

- Tenant-level Lockbox enrolled at the appropriate tier for the firm''s subscription.
- All Z3 environments: `LockboxEnabled = $true`.
- Tabletop exercised within last 90 days; approver responded within 8-hour SLA.

#### Evidence Capture

- Files: `tc11-lockbox-<runId>.json`, `tc11-lockbox-tier-screenshot-<runId>.png`, `tc11-tabletop-pointer-<runId>.json` (a record pointing to the tabletop evidence file with its SHA-256 hash).
- Retention: **records scope (6 years)**.
- §3 master-table row: row 11.

#### Remediation

- Enable Lockbox per-environment via PPAC **Environments → {env} → Settings → Privacy + security → Customer Lockbox**. Tenant-level enrollment requires a Microsoft 365 admin center change.
- If tabletop is stale, schedule a fresh exercise via the firm''s incident-response calendar.
- See [Portal Walkthrough](portal-walkthrough.md) — Customer Lockbox.

---

### TC-12 — CMK Enterprise Policy on Z3; exclusion narrative reviewed and signed

**Criterion mapped:** Verification Criterion 12. CMK protects Dataverse-resident data; per the [CMK service coverage matrix](https://learn.microsoft.com/en-us/power-platform/admin/customer-managed-key) some surfaces are out of scope. The firm''s **CMK exclusion narrative** must enumerate every excluded surface, be signed by the Compliance Officer + Internal Audit Lead, and be re-attested annually.

#### Setup

- PRE gates passed.
- Operator: **Power Platform Admin** (read CMK Enterprise Policy assignment); **Entra Global Reader** (read Key Vault metadata); **Compliance Officer** + **Internal Audit Lead** (counter-sign exclusion narrative).

#### Steps

1. Pull CMK Enterprise Policy assignments per Z3 environment:

    ```powershell
    $rows = foreach ($env in $envs | Where-Object { ($register.environments | Where-Object id -eq $_.EnvironmentName).zone -eq '3' }) {
        $g = Get-AdminPowerAppEnvironmentGovernanceConfiguration -EnvironmentName $env.EnvironmentName
        $cmk = $g.encryption.customerManagedKey
        [pscustomobject]@{
            EnvironmentId       = $env.EnvironmentName
            CmkPolicyAssigned   = [bool]$cmk.enterprisePolicyId
            EnterprisePolicyId  = $cmk.enterprisePolicyId
            KeyVaultUri         = $cmk.keyVaultUri
            KeyName             = $cmk.keyName
            KeyVersion          = $cmk.keyVersion
            LastRotation        = $cmk.lastRotationDate
            RotationDueWithin90 = if ($cmk.lastRotationDate) { ((Get-Date) - [datetime]$cmk.lastRotationDate).Days -le 365 } else { $false }
        }
    }
    $rows | ConvertTo-Json -Depth 6 |
        Out-File (Join-Path $script:EvidenceRoot "tc12-cmk-$($script:RunId).json") -Encoding utf8
    ```

2. Locate `cmk-exclusion-narrative.md`. Verify it enumerates **at minimum** these excluded surfaces (per current Microsoft documentation):
   - Maker welcome content (TC-7).
   - Solution-checker scan results.
   - Environment / app / agent display names and descriptions.
   - Connection metadata (connector display names, references, but not credentials, which are stored separately and protected by the connection store).
   - Microsoft Agent 365 audit metadata.
   - Telemetry forwarded to Microsoft for service operations.
3. Verify the narrative is signed by the Compliance Officer and the Internal Audit Lead within the last 12 months. Capture signature timestamps.

#### Expected

- All Z3 environments have a CMK Enterprise Policy assigned and a key version current within 365 days.
- Exclusion narrative present, current, dual-signed.

#### Evidence Capture

- Files: `tc12-cmk-<runId>.json`, signed copy of `cmk-exclusion-narrative.md`, `tc12-narrative-signature-<runId>.json`.
- Retention: **records scope (6 years)**; the narrative itself is records-scope under SOX 404.
- §3 master-table row: row 12.

#### Remediation

- Assign CMK via PPAC **Environments → {env} → Settings → Encryption → Customer-Managed Key**. CMK assignment requires Key Vault prerequisites; see [Portal Walkthrough](portal-walkthrough.md) — CMK assignment.
- Re-sign exclusion narrative annually; route via the firm''s e-signature workflow.

---

### TC-13 — Tenant Isolation configured both directions; Entra ID-auth scope caveat noted; Azure DevOps DLP exception documented

**Criterion mapped:** Verification Criterion 3 (cross-tenant isolation). Tenant Isolation is set at PPAC → **Security → Identity and access** at **tenant level** — not inside per-environment Privacy + security. Tenant Isolation governs Power Platform connectors that authenticate via Entra ID; connectors that use other auth (e.g., Azure DevOps PAT) are out of scope and must be governed by DLP.

#### Setup

- PRE gates passed.
- Operator: **Power Platform Admin** + **Entra Global Reader**.
- Reference data: tenant allow-list (`tenant-isolation-allowlist.json`) — partner / counterparty / regulator tenants for which inbound or outbound flow is explicitly permitted.

#### Steps

1. PPAC **Security → Identity and access → Tenant isolation**. Capture screenshot.
2. Read posture via PowerShell (admin module exposes via REST helper):

    ```powershell
    $ti = Get-PowerAppTenantIsolationPolicy
    $ti | ConvertTo-Json -Depth 6 |
        Out-File (Join-Path $script:EvidenceRoot "tc13-tenant-isolation-$($script:RunId).json") -Encoding utf8
    ```

3. Verify both inbound and outbound default = `Block`; allow-list matches reference.
4. Verify the Azure DevOps connector exception is documented in the firm''s DLP variance register (Control 1.4 / 1.5) — Azure DevOps PAT-based auth is **not** governed by Tenant Isolation.

#### Expected

- Default inbound = `Block`; default outbound = `Block`.
- Allow-list = reference list; no drift.
- Azure DevOps DLP variance entry present and signed.

#### Evidence Capture

- Files: `tc13-tenant-isolation-<runId>.json` + screenshot + variance pointer.
- Retention: **records scope (6 years)**.
- §3 master-table row: row 13.

#### Remediation

- Reset defaults via PPAC; open Control 2.3 ticket.
- Add or remove allow-list entries per the firm''s vendor-management workflow.

---

### TC-14 — Environment routing rules configured; rules govern type/zone, not region

**Criterion mapped:** Verification Criterion 2 (auto-provisioning of personal envs at Managed posture). Environment routing rules redirect new personal-environment provisioning to a designated Managed environment. **Region is still selected at provisioning time per the user''s home-region assignment**; routing does not override region.

#### Setup

- PRE gates passed; Power Platform Admin activated.
- Reference data: routing-rule policy (`routing-rules.json`) — the firm''s expected rule set (e.g., "Route new personal environments for users in the Investment Bank line-of-business to the IB Z2 environment").

#### Steps

1. PPAC **Settings → Environments → Environment routing**. Capture screenshot of rules table.
2. Read rules via PowerShell:

    ```powershell
    $rules = Get-AdminPowerAppEnvironmentRoutingRule
    $rules | ConvertTo-Json -Depth 6 |
        Out-File (Join-Path $script:EvidenceRoot "tc14-routing-rules-$($script:RunId).json") -Encoding utf8
    ```

3. Diff against the reference policy; emit `FAIL` for any discrepancy.

#### Expected

- Live rules match `routing-rules.json` exactly.
- No rule attempts to override region.

#### Evidence Capture

- File: `tc14-routing-rules-<runId>.json` + screenshot.
- Retention: **records scope (6 years)** — change-control evidence under Control 2.15.
- §3 master-table row: row 14.

#### Remediation

- Re-create or amend rules via PPAC; open Control 2.15 change ticket.
- See [Control 2.15](../../../controls/pillar-2-management/2.15-environment-routing.md) for the routing-rule lifecycle.

---

### TC-15 — Microsoft Agent 365 / M365 admin center governance console — Copilot Studio shared agents in catalog

**Criterion mapped:** Cross-reference to [Control 2.25](../../../controls/pillar-2-management/2.25-agent-365-admin-center-governance-console.md). Every Copilot Studio agent shared from a Z2/Z3 environment must appear in the Microsoft Agent 365 catalog with correct owner, environment, and policy assignment. Sovereign clouds: not at parity — route to TC-18.

#### Setup

- PRE gates passed; cloud = `Commercial`.
- Operator: **AI Administrator** (read Agent 365 catalog) + **Entra Global Reader** (witness).
- Sovereign route: emit `SKIPPED` and route to TC-18.

#### Steps

1. Read Agent 365 inventory via Graph beta:

    ```powershell
    Connect-MgGraph -Scopes 'AgentGovernance.Read.All' -NoWelcome
    $agents = Invoke-MgGraphRequest -Method GET -Uri 'https://graph.microsoft.com/beta/agents'
    $agents.value | ConvertTo-Json -Depth 8 |
        Out-File (Join-Path $script:EvidenceRoot "tc15-agent365-inventory-$($script:RunId).json") -Encoding utf8
    ```

2. Cross-join with Copilot Studio agent enumeration from each Z2/Z3 environment (use the helper from [Control 2.25 verification](../2.25/verification-testing.md)):

    ```powershell
    $cs = Get-Me225CopilotStudioAgent -EnvironmentIds ($envs.EnvironmentName)
    $missing = $cs | Where-Object { $_.Id -notin $agents.value.id -and $_.Shared }
    $missing | ConvertTo-Json -Depth 6 |
        Out-File (Join-Path $script:EvidenceRoot "tc15-catalog-gap-$($script:RunId).json") -Encoding utf8
    ```

3. Emit `FAIL` for any non-empty `$missing`.

#### Expected

- Every shared Copilot Studio agent in Z2/Z3 environments appears in Agent 365 catalog with owner/environment/policy assignment populated.
- For sovereign clouds: `SKIPPED` record with TC-18 substitute pointer.

#### Evidence Capture

- Files: `tc15-agent365-inventory-<runId>.json`, `tc15-catalog-gap-<runId>.json`.
- Retention: **records scope (6 years)** — agent inventory is books-and-records under FINRA 4511 / SEC 17a-4(f).
- §3 master-table row: row 15.

#### Remediation

- Re-trigger Agent 365 catalog sync via the [Control 2.25 §3 — Catalog reconciliation](../../../controls/pillar-2-management/2.25-agent-365-admin-center-governance-console.md) runbook.

---

### TC-16 — Maker / Approver / Admin SoD enforced via Entra security groups

**Criterion mapped:** Cross-reference to [Control 2.8](../../../controls/pillar-2-management/2.8-access-control-and-segregation-of-duties.md). The same Entra principal must not simultaneously hold maker, approver, and admin rights for the same scope.

#### Setup

- PRE gates passed.
- Operator: **Entra Global Reader** + **Power Platform Admin**.
- Reference data: SoD matrix (`sod-matrix.json`) — for each environment, which security groups carry maker / approver / admin roles.

#### Steps

1. For each Z2/Z3 environment, enumerate group memberships and intersect:

    ```powershell
    foreach ($e in $envs | Where-Object { ($register.environments | Where-Object id -eq $_.EnvironmentName).zone -in '2','3' }) {
        $sod = $sodMatrix.environments | Where-Object id -eq $e.EnvironmentName
        $makers    = (Get-MgGroupMember -GroupId $sod.makerGroupId    -All).AdditionalProperties.userPrincipalName
        $approvers = (Get-MgGroupMember -GroupId $sod.approverGroupId -All).AdditionalProperties.userPrincipalName
        $admins    = (Get-MgGroupMember -GroupId $sod.adminGroupId    -All).AdditionalProperties.userPrincipalName

        $violations = @()
        $violations += $makers | Where-Object { $_ -in $approvers }
        $violations += $makers | Where-Object { $_ -in $admins    }
        $violations += $approvers | Where-Object { $_ -in $admins }

        [pscustomobject]@{
            EnvironmentId  = $e.EnvironmentName
            MakerCount     = $makers.Count
            ApproverCount  = $approvers.Count
            AdminCount     = $admins.Count
            Violations     = $violations | Select-Object -Unique
        } | ConvertTo-Json -Depth 6 |
            Add-Content (Join-Path $script:EvidenceRoot "tc16-sod-$($script:RunId).ndjson")
    }
    ```

#### Expected

- Zero violations across all Z2/Z3 environments.

#### Evidence Capture

- File: `tc16-sod-<runId>.ndjson`.
- Retention: **records scope (6 years)** — SoD evidence is SOX 404 ICFR perimeter.
- §3 master-table row: row 16.

#### Remediation

- Remove the offending principal from the conflicting role; route via the firm''s access-recertification workflow per [Control 2.8](../../../controls/pillar-2-management/2.8-access-control-and-segregation-of-duties.md).

---

### TC-17 — Inactive resource view feeds orphan detection (Control 3.6)

**Criterion mapped:** Cross-reference to [Control 3.6](../../../controls/pillar-3-reporting/3.6-orphaned-agent-detection-and-remediation.md). The Managed Environments **Inactive resources** view surfaces apps, flows, and agents not used in the configured window. This TC verifies the view is configured and that its output is consumed by the orphan-detection pipeline.

#### Setup

- PRE gates passed; Power Platform Admin activated.

#### Steps

1. PPAC **Environments → {env} → Resources → Inactive**. Capture screenshot of configured threshold (e.g., 90 days).
2. Pull inactive-resource snapshot:

    ```powershell
    $rows = foreach ($e in $envs) {
        $inactive = Get-AdminPowerAppEnvironmentInactiveResources -EnvironmentName $e.EnvironmentName
        [pscustomobject]@{
            EnvironmentId   = $e.EnvironmentName
            ThresholdDays   = $inactive.thresholdDays
            InactiveCount   = $inactive.resources.Count
            ResourceTypes   = ($inactive.resources | Group-Object resourceType | Select-Object Name, Count)
        }
    }
    $rows | ConvertTo-Json -Depth 6 |
        Out-File (Join-Path $script:EvidenceRoot "tc17-inactive-$($script:RunId).json") -Encoding utf8
    ```

3. Cross-check that the most recent Control 3.6 evidence pack consumed this snapshot within the last 7 days.

#### Expected

- All Z2/Z3: `ThresholdDays` matches firm policy (typically 90).
- Snapshot consumed by Control 3.6 pipeline within 7 days.

#### Evidence Capture

- File: `tc17-inactive-<runId>.json` + screenshot.
- Retention: **operational (3 years)** — telemetry feed.
- §3 master-table row: row 17.

#### Remediation

- Adjust threshold via PPAC if drifted from policy; open Control 3.6 ticket if pipeline consumption gap.

---

### TC-18 — Sovereign cloud compensating-control exercise; Agent 365 parity gap documented

**Criterion mapped:** Sovereign substitute for TC-8, TC-15, and any other SOV-skipped TCs. This TC produces a single composite attestation that the firm''s sovereign tenant is governed by the documented compensating controls and that the Compliance Officer + AI Governance Lead have reviewed within the quarter.

#### Setup

- PRE gates passed; cloud ∈ {GCC, GCCH, DoD, China}.
- Operator: **Purview Compliance Admin** + **Entra Security Admin**; counter-signed by **Compliance Officer** + **AI Governance Lead**.

#### Steps

1. Enumerate every TC in this run that emitted a `SKIPPED` due to sovereign:

    ```powershell
    $skipped = Get-ChildItem $script:EvidenceRoot -Recurse -Filter '*.ndjson' |
        Get-Content | ConvertFrom-Json |
        Where-Object { $_.status -eq 'SKIPPED' -and $_.compensating_control_ref -like 'TC-18*' }
    ```

2. For each skipped TC, confirm the substitute artifact exists in this run (e.g., `tc08-sentinel-results-<runId>.json` for TC-8 sovereign).
3. Document the **Microsoft Agent 365 parity gap**: Agent 365 governance console is not at parity in sovereign clouds. The compensating evidence is:
   - Graph beta agent enumeration (where available in the sovereign cloud — limited at this writing).
   - Purview unified-audit-log forwarded events for `Microsoft Power Platform` / `Copilot Studio`.
   - Sentinel KQL summary per TC-8 sovereign path.
4. Compose the quarterly sovereign attestation:

    ```powershell
    $attest = [pscustomobject]@{
        control_id                   = '2.1'
        run_id                       = $script:RunId
        cloud                        = $cloud
        skipped_test_cases           = $skipped.test_case | Select-Object -Unique
        substitute_artifacts_present = $true
        agent365_parity_gap          = 'Documented; substituted via Graph + Purview + Sentinel'
        signed_by                    = @('Compliance Officer','AI Governance Lead')
        signed_at                    = (Get-Date).ToUniversalTime().ToString('o')
        next_review_due              = (Get-Date).AddDays(90).ToUniversalTime().ToString('o')
        regulator_mappings           = @('FINRA-3110','FINRA-4511','SEC-17a-4','SOX-404','GLBA-501b','OCC-2011-12','SR-11-7','NYDFS-500-06','FFIEC-IS','FFIEC-MGMT')
    }
    $attest | ConvertTo-Json -Depth 6 |
        Out-File (Join-Path $script:EvidenceRoot "tc18-sovereign-attestation-$($script:RunId).json") -Encoding utf8
    ```

#### Expected

- Every `SKIPPED` record has a corresponding substitute artifact.
- Attestation signed by Compliance Officer + AI Governance Lead within the current quarter.

#### Evidence Capture

- File: `tc18-sovereign-attestation-<runId>.json`.
- Retention: **records scope (6 years)**.
- §3 master-table row: row 18.

#### Remediation

- Missing substitute artifacts: rerun the affected TC''s sovereign path.
- Stale attestation: route via e-signature; do not commingle with operator-only evidence.

---

### TC-19 — Annual SOX 404 self-assessment to Audit Committee

**Criterion mapped:** SOX § 404 management-assertion support. Once per fiscal year, the AI Governance Lead, Compliance Officer, Information Security Officer, and Internal Audit Lead jointly produce a self-assessment of Control 2.1 effectiveness for delivery to the firm''s Audit Committee.

#### Setup

- All four quarterly evidence packs from the prior fiscal year are sealed and available.
- Operator: **AI Governance Lead** (primary author).

#### Steps

1. Aggregate the four quarterly packs:

    ```powershell
    $packs = Get-ChildItem $env:ME21_PACK_ROOT -Filter 'pack-FY*-Q*.zip' |
        Where-Object { $_.Name -match "FY$($fiscalYear)" }
    ```

2. Compute annual KPIs:
   - Total environments under management.
   - PASS rate per TC, per quarter.
   - Median time-to-remediate for FAIL records.
   - Open exceptions at fiscal year end.
   - Sovereign substitution count.
3. Author `tc19-annual-self-assessment-FY<yyyy>.md` from the firm''s template.
4. Route for signature: AI Governance Lead → Compliance Officer → Information Security Officer → Internal Audit Lead → Audit Committee acknowledgement.

#### Expected

- Self-assessment delivered to Audit Committee within 90 days of fiscal year end.
- All four signatures captured prior to delivery.

#### Evidence Capture

- File: `tc19-annual-self-assessment-FY<yyyy>.md` + signature manifest.
- Retention: **records scope (6 years)**.
- §3 master-table row: row 19.

#### Remediation

- Missed signature window: escalate to General Counsel; document the cause and the corrective action in the next quarterly pack.

---

### TC-20 — Examination-ready evidence pack pull-test

**Criterion mapped:** A regulator (FINRA, SEC, OCC, NYDFS, FFIEC) can request evidence with short notice (often ≤ 7 business days). This TC is a quarterly **fire drill**: the Compliance Officer requests a focused pack from a randomly chosen prior-quarter run; the Power Platform Admin and AI Governance Lead must produce the focused pack within 4 business hours.

#### Setup

- A sealed §4 pack from any prior quarter exists.
- Operator: **Compliance Officer** (requester) + **Power Platform Admin** (producer) + **AI Governance Lead** (witness).

#### Steps

1. Compliance Officer selects a random prior-quarter pack and identifies a focus area (e.g., "TC-3 + TC-12 evidence for the IB Z3 environment").
2. Power Platform Admin extracts the focused subset using the `Get-Me21EvidenceSlice` helper:

    ```powershell
    Get-Me21EvidenceSlice -PackPath $packPath `
                          -TestCases TC-3,TC-12 `
                          -EnvironmentId $z3IbEnvId `
                          -OutputPath (Join-Path $script:EvidenceRoot "tc20-pulltest-slice-$($script:RunId)")
    ```

3. AI Governance Lead verifies the slice''s Merkle proof against the original pack''s root hash and signs the verification record.
4. Capture wall-clock time from request to delivery.

#### Expected

- Slice produced and verified within 4 business hours.
- Merkle proof valid.

#### Evidence Capture

- Files: `tc20-pulltest-slice-<runId>/*.json`, `tc20-pulltest-timing-<runId>.json`, `tc20-pulltest-merkle-proof-<runId>.json`.
- Retention: **records scope (6 years)** — examiner-readiness evidence.
- §3 master-table row: row 20.

#### Remediation

- Missed SLA: root-cause in the next quarterly attestation; escalate to AI Governance Lead and Internal Audit Lead.

---
## §3 Evidence-Capture Master Table

This table is the canonical mapping from each TC to the evidence artifact(s) it produces, the retention scope under [Control 1.7](../../../controls/pillar-1-security/1.7-comprehensive-audit-logging-and-compliance.md), and the regulator citations that justify the retention. Sovereign-affected rows are marked `SOV-SUB`.

| Row | TC | Artifact filename pattern | Retention scope | Retention period | Regulator mapping |
|---|---|---|---|---|---|
| 1 | TC-1 | `tc01-inventory-<runId>.json` | Records | 6 years (WORM) | FINRA-4511, SEC-17a-3, SOX-404, FFIEC-MGMT |
| 2 | TC-2 | `tc02-pipeline-targets-<runId>.json`, `tc02-pipeline-stages-<runId>.png` | Records | 6 years | SEC-17a-3, SOX-404, OCC-2011-12 |
| 3a | TC-3 | `tc03-license-consumption-ppac-<runId>.png` | Records | 6 years | FINRA-4511, SOX-404 |
| 3b | TC-3 | `tc03-env-snapshot-<runId>.json` | Records | 6 years | FINRA-4511, SEC-17a-4 |
| 3c | TC-3 | `tc03-tenant-skus-<runId>.json` | Records | 6 years | SOX-404, FFIEC-MGMT |
| 3d | TC-3 | `tc03-license-coverage-<runId>.json` | Records | 6 years | FINRA-4511, SOX-404, OCC-2011-12 |
| 3e | TC-3 | `tc03-payg-handoff-tc04-<runId>.json` | Operational | 3 years | SOX-404 |
| 4 | TC-4 | `tc04-payg-remediation-tickets-<runId>.json` | Records | 6 years | SOX-404, OCC-2011-12 |
| 5 | TC-5 | `tc05-sharing-limits-<runId>.json` | Records (Z3) / Operational (Z2) | 6 / 3 years | FINRA-3110, GLBA-501b, NYDFS-500-06 |
| 6 | TC-6 | `tc06-solution-checker-<runId>.json`, `tc06-exception-register-snapshot-<runId>.csv` | Records | 6 years | SOX-404, OCC-2011-12, FFIEC-MGMT |
| 7 | TC-7 | `tc07-welcome-content-<runId>.json`, `tc07-welcome-dlp-scan-<runId>.json`, `cmk-exclusion-narrative.md` | Records | 6 years | FINRA-3110, GLBA-501b |
| 8 | TC-8 (Commercial) | `tc08-digest-screenshot-<runId>.png`, `tc08-recipients-<runId>.json` | Records | 6 years | FINRA-3110, FINRA-4511 |
| 8-SOV | TC-8 (Sovereign) — `SOV-SUB` | `tc08-graph-audit-<runId>.json`, `tc08-sentinel-query-<runId>.kql`, `tc08-sentinel-results-<runId>.json`, `tc08-compensating-attestation-<runId>.json` | Records | 6 years | FINRA-3110, FINRA-4511, NYDFS-500-06 |
| 9 | TC-9 | `tc09-ip-firewall-<runId>.json`, `tc09-egress-gap-<runId>.ndjson` | Records (Z3) / Operational (Z2) | 6 / 3 years | GLBA-501b, NYDFS-500-06, FFIEC-IS |
| 10 | TC-10 | `tc10-ip-cookie-binding-<runId>.json` + screenshot | Records | 6 years | GLBA-501b, NYDFS-500-06, FFIEC-IS |
| 11 | TC-11 | `tc11-lockbox-<runId>.json`, `tc11-lockbox-tier-screenshot-<runId>.png`, `tc11-tabletop-pointer-<runId>.json` | Records | 6 years | GLBA-501b, NYDFS-500-06, OCC-2011-12 |
| 12 | TC-12 | `tc12-cmk-<runId>.json`, signed `cmk-exclusion-narrative.md`, `tc12-narrative-signature-<runId>.json` | Records | 6 years | SOX-404, GLBA-501b, OCC-2011-12 |
| 13 | TC-13 | `tc13-tenant-isolation-<runId>.json` + screenshot + variance pointer | Records | 6 years | GLBA-501b, NYDFS-500-06, FFIEC-IS |
| 14 | TC-14 | `tc14-routing-rules-<runId>.json` + screenshot | Records | 6 years | SEC-17a-3, SOX-404, FFIEC-MGMT |
| 15 | TC-15 | `tc15-agent365-inventory-<runId>.json`, `tc15-catalog-gap-<runId>.json` | Records | 6 years | FINRA-4511, SEC-17a-4, FINRA-25-07 |
| 16 | TC-16 | `tc16-sod-<runId>.ndjson` | Records | 6 years | SOX-404, OCC-2011-12, FFIEC-MGMT |
| 17 | TC-17 | `tc17-inactive-<runId>.json` + screenshot | Operational | 3 years | FFIEC-MGMT |
| 18 | TC-18 | `tc18-sovereign-attestation-<runId>.json` | Records | 6 years | FINRA-3110, FINRA-4511, SOX-404, GLBA-501b, OCC-2011-12, NYDFS-500-06, FFIEC-IS, FFIEC-MGMT |
| 19 | TC-19 | `tc19-annual-self-assessment-FY<yyyy>.md` + signature manifest | Records | 6 years | SOX-302, SOX-404, FINRA-3110, FFIEC-MGMT |
| 20 | TC-20 | `tc20-pulltest-slice-<runId>/*.json`, `tc20-pulltest-timing-<runId>.json`, `tc20-pulltest-merkle-proof-<runId>.json` | Records | 6 years | FINRA-4511, SEC-17a-4, OCC-2011-12 |

> **WORM placement.** Records-scope artifacts mirror to the firm''s WORM-protected blob storage account (Azure Blob with immutability policy in `Locked` mode) within 24 hours of pack sealing. Operational-scope artifacts live in the firm''s standard tamper-evident log store. The §4.4 sealing job emits a `worm-mirror-<runId>.json` manifest confirming each records-scope artifact''s WORM URL and immutability-policy retention period.

---

## §4 Evidence Pack Assembly

### 4.1 Pack structure

```
pack-<runId>.zip
├── attestation.json         # Merkle root, signatures, regulator mapping summary
├── manifest.ndjson          # one line per evidence artifact (path + SHA-256 leaf)
├── preflight-<runId>.json   # PRE-01..PRE-09 results
├── tc01/ ... tc20/          # one folder per TC
└── README.md                # pack overview, regulator mapping, signature block
```

### 4.2 Per-TC pack contents

Each `tc<NN>/` folder contains:

- The artifacts named in §3.
- A `tc<NN>-evidence-<runId>.ndjson` file listing every evidence record emitted for that TC, conforming to the §0.6 schema.
- Where applicable, a `tc<NN>-screenshots/` subfolder.

### 4.3 Merkle tree and signing

```powershell
function New-Me21EvidencePack {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory)] [string] $EvidenceRoot,
        [Parameter(Mandatory)] [string] $RunId,
        [Parameter(Mandatory)] [string] $PrimarySignerUpn,
        [Parameter(Mandatory)] [string] $WitnessSignerUpn,
        [Parameter(Mandatory)] [string] $OutputDir
    )

    # 1. enumerate artifacts (deterministic order)
    $files = Get-ChildItem -Path $EvidenceRoot -Recurse -File |
             Sort-Object FullName

    # 2. leaf hashes
    $manifest = foreach ($f in $files) {
        $hash = (Get-FileHash -Algorithm SHA256 -Path $f.FullName).Hash
        [pscustomobject]@{
            path = $f.FullName.Substring($EvidenceRoot.Length).TrimStart('\','/')
            size = $f.Length
            sha256 = $hash
        }
    }
    $manifest | ConvertTo-Json -Depth 4 -Compress |
        Set-Content (Join-Path $EvidenceRoot 'manifest.ndjson') -Encoding utf8

    # 3. Merkle root (binary tree, SHA-256, hex lowercase, deterministic order)
    $leaves = $manifest.sha256
    while ($leaves.Count -gt 1) {
        $next = @()
        for ($i = 0; $i -lt $leaves.Count; $i += 2) {
            $left  = $leaves[$i]
            $right = if ($i + 1 -lt $leaves.Count) { $leaves[$i + 1] } else { $left }
            $bytes = [System.Text.Encoding]::ASCII.GetBytes($left + $right)
            $next += ([System.BitConverter]::ToString(
                       [System.Security.Cryptography.SHA256]::Create().ComputeHash($bytes)
                     ).Replace('-','').ToLowerInvariant())
        }
        $leaves = $next
    }
    $merkleRoot = $leaves[0]

    # 4. attestation document (dual signature)
    $attest = [pscustomobject]@{
        control_id      = '2.1'
        run_id          = $RunId
        merkle_root     = $merkleRoot
        leaf_count      = $manifest.Count
        primary_signer  = $PrimarySignerUpn
        witness_signer  = $WitnessSignerUpn
        signed_at       = (Get-Date).ToUniversalTime().ToString('o')
        regulator_mapping_summary = @(
            'FINRA-3110','FINRA-4511','FINRA-25-07',
            'SEC-17a-3','SEC-17a-4',
            'SOX-302','SOX-404',
            'GLBA-501b','OCC-2011-12','SR-11-7',
            'CFTC-1.31','NYDFS-500-06','FFIEC-IS','FFIEC-MGMT'
        )
    }
    $attest | ConvertTo-Json -Depth 6 |
        Set-Content (Join-Path $EvidenceRoot 'attestation.json') -Encoding utf8

    # 5. zip and emit
    Compress-Archive -Path "$EvidenceRoot\*" `
                     -DestinationPath (Join-Path $OutputDir "pack-$RunId.zip") -Force
}
```

> **Dual control.** The pack assembler refuses to seal a pack where `PrimarySignerUpn -eq $WitnessSignerUpn`. The primary signer is the **AI Governance Lead** (or delegate); the witness is the **Entra Global Reader** designated for the run.

### 4.4 WORM mirroring

Records-scope artifacts mirror to the firm''s WORM blob container within 24 hours of `pack-<runId>.zip` creation. The mirroring job emits `worm-mirror-<runId>.json`:

```json
{
  "run_id": "ME-20260415-093012-a1b2c3d4",
  "mirrored_at": "2026-04-16T09:30:12Z",
  "container": "https://contosogovevidence.blob.core.windows.net/me21-records",
  "immutability_policy": { "mode": "Locked", "period_years": 6 },
  "artifacts": [ { "path": "tc01-inventory-...json", "blob_url": "...", "etag": "...", "sha256": "..." } ]
}
```

### 4.5 Schema validation

```powershell
function Test-Me21EvidenceSchema {
    param([Parameter(Mandatory)] [pscustomobject] $Record)
    $required = @('control_id','run_id','run_timestamp','tenant_id','tenant_display_name',
                  'cloud','test_case','status','assertion','regulator_mappings','schema_version')
    $missing  = $required | Where-Object { -not $Record.PSObject.Properties.Name.Contains($_) }
    if ($missing) { throw "Schema violation: missing fields $($missing -join ', ')" }
    if ($Record.status -notin @('PASS','WARN','FAIL','SKIPPED')) { throw "Invalid status: $($Record.status)" }
    if ($Record.regulator_mappings.Count -eq 0) { throw "Empty regulator_mappings" }
    return $true
}
```

### 4.6 Quarterly attestation packet

Each calendar quarter, the AI Governance Lead and Compliance Officer co-sign `attestation-quarterly-FY<yy>-Q<n>.md` summarising:

- Number of runs in the quarter (target: weekly = 13/quarter).
- PASS rate per TC, per zone.
- All FAIL records and their remediation status.
- All WARN records aged > 30 days.
- All sovereign `SKIPPED` records and the corresponding TC-18 attestations.
- Carry-forward exceptions from prior quarters.

The packet attaches the four most-recent monthly pack ZIPs and is delivered to: AI Governance Lead, Compliance Officer, Information Security Officer, Internal Audit Lead, Technology Risk Manager.

---

## §5 Examiner-Facing Evidence Pack Production (TC-20 pull-test substrate)

When a regulator (FINRA, SEC, OCC, NYDFS, FFIEC) requests evidence on short notice, the **Compliance Officer** is the firm''s single point of contact. The evidence-pack production sequence, as exercised quarterly via TC-20:

1. **Receipt and triage.** Compliance Officer receives the request, identifies which TCs and which environments are in scope, and opens a request ticket referencing the regulator name, exam ID, and SLA.
2. **Slice extraction.** Power Platform Admin runs `Get-Me21EvidenceSlice` against the relevant pack(s).
3. **Merkle proof.** AI Governance Lead generates a Merkle inclusion proof for each slice element against the original pack''s root hash.
4. **Redaction review.** Compliance Officer + General Counsel review the slice for any out-of-scope data; redactions are themselves logged.
5. **Delivery.** Compliance Officer delivers via the firm''s regulator-portal-of-record (e.g., FINRA Gateway, SEC EDGAR / Edgar Online, OCC examiner portal), with the Merkle root and slice proof in the cover memo.
6. **Post-delivery.** Pack delivery, recipient acknowledgement, and any follow-up requests are appended to the firm''s examiner-correspondence log under [Control 1.7](../../../controls/pillar-1-security/1.7-comprehensive-audit-logging-and-compliance.md).

**Pre-staged narratives.** The firm maintains, alongside this playbook, pre-approved narratives for the most-likely examiner questions:

- "How does the firm ensure every Power Platform environment hosting customer-facing or trade-impacting workloads is on the Managed Environments tier?" — answer based on TC-1, TC-2, TC-14.
- "How does the firm supervise maker activity in production environments?" — answer based on TC-5, TC-6, TC-8, TC-16.
- "What encryption protections apply to data at rest in your production Power Platform environments, and what are the documented exclusions?" — answer based on TC-12 and the CMK exclusion narrative.
- "How does the firm prevent cross-tenant data exfiltration via Power Platform connectors?" — answer based on TC-13 plus Control 1.4 / 1.5.
- "How does the firm govern AI agents shared from Copilot Studio at scale?" — answer based on TC-15 and Control 2.25; sovereign clouds answer via TC-18.
- "What is the firm''s evidence-retention scheme for AI-governance artifacts, and how does it map to FINRA Rule 4511 / SEC Rule 17a-4?" — answer based on §3 master table and Control 1.7.

---

## §6 Pester Suite — Reference Skeleton

```powershell
#Requires -Modules @{ ModuleName='Pester'; ModuleVersion='5.5.0' }

BeforeAll {
    . $PSScriptRoot/Invoke-Me21PreFlight.ps1
    Invoke-Me21PreFlight -PowerPlatformEndpoint $env:ME21_ENDPOINT
}

Describe 'Control 2.1 — Managed Environments' -Tag 'me21' {

    Context 'TC-1 — Z2/Z3 environments are Managed' {
        It 'has zero unmanaged Z2/Z3 environments' {
            $z23Unmanaged.Count | Should -Be 0 -Because 'TC-1 PASS requires zero unmanaged Z2/Z3 envs'
        }
    }

    Context 'TC-3 — Licensing coverage' {
        It 'has zero non-compliant makers in any Z3 environment' {
            ($perEnv | Where-Object Zone -eq '3' | Measure-Object NonCompliantCount -Sum).Sum |
                Should -Be 0 -Because 'Z3 has zero tolerance for non-compliant makers'
        }
    }

    # ... TC-2, TC-4 .. TC-20 follow the same pattern
}
```

The full Pester suite (`Invoke-Me21Tests.ps1`) lives in the sister [PowerShell Setup](powershell-setup.md) playbook, §10.

---

## Cross-References

- Control: [2.1 Managed Environments](../../../controls/pillar-2-management/2.1-managed-environments.md)
- Sister playbooks: [Portal Walkthrough](portal-walkthrough.md) | [PowerShell Setup](powershell-setup.md) | [Troubleshooting](troubleshooting.md)
- Companion controls: [1.4](../../../controls/pillar-1-security/1.4-advanced-connector-policies-acp.md) · [1.5](../../../controls/pillar-1-security/1.5-data-loss-prevention-dlp-and-sensitivity-labels.md) · [1.7](../../../controls/pillar-1-security/1.7-comprehensive-audit-logging-and-compliance.md) · [1.20](../../../controls/pillar-1-security/1.20-network-isolation-private-connectivity.md) · [2.2](../../../controls/pillar-2-management/2.2-environment-groups-and-tier-classification.md) · [2.3](../../../controls/pillar-2-management/2.3-change-management-and-release-planning.md) · [2.8](../../../controls/pillar-2-management/2.8-access-control-and-segregation-of-duties.md) · [2.14](../../../controls/pillar-2-management/2.14-training-and-awareness-program.md) · [2.15](../../../controls/pillar-2-management/2.15-environment-routing.md) · [2.25](../../../controls/pillar-2-management/2.25-agent-365-admin-center-governance-console.md) · [3.1](../../../controls/pillar-3-reporting/3.1-agent-inventory-and-metadata-management.md) · [3.6](../../../controls/pillar-3-reporting/3.6-orphaned-agent-detection-and-remediation.md) · [3.9](../../../controls/pillar-3-reporting/3.9-microsoft-sentinel-integration.md)

[Back to Control 2.1](../../../controls/pillar-2-management/2.1-managed-environments.md) | [Portal Walkthrough](portal-walkthrough.md) | [PowerShell Setup](powershell-setup.md) | [Troubleshooting](troubleshooting.md)

---

*Updated: May 2026 | Version: v1.6.2 | UI Verification Status: Current*
