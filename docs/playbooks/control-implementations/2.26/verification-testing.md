# Verification & Testing — Control 2.26: Entra Agent ID Identity Governance

> **Examiner-defensible evidence package** for Control 2.26. This playbook produces, signs, and retains the artifacts required to demonstrate to FINRA, SEC, OCC, FFIEC, and internal audit that every Microsoft 365 AI agent identity in the tenant is sponsored, lifecycle-governed, periodically reviewed, and forwarded to the SIEM with 6-year retention.
>
> **Post-GA status (May 2026):** Microsoft Agent 365 reached general availability on May 1, 2026 and Microsoft Entra Agent ID is generally available. The pre-GA "Frontier program enrollment" gate is replaced by **Microsoft Agent 365 / Microsoft 365 E7 license assignment**. Pre-flight gate `PRE-06` and the §9 `TRG-PREVIEW-01` test retain their pre-GA names for backward compatibility; the underlying probe (HTTP 200 from `/beta/agents`) remains the correct observable because both the pre-GA Frontier enrollment and the post-GA license assignment manifest as the same API reachability state for the calling principal. A follow-up issue tracks renaming PRE-06 / TRG-PREVIEW-01 to license-coverage terms.
>
> **Scope:** Commercial M365 tenants with Microsoft Agent 365 or Microsoft 365 E7 licensing assigned to the operating admin and the in-scope sponsor / agent-owner users. Sovereign clouds (GCC, GCC High, DoD) follow the compensating-control pattern in §8 because the Entra Agent ID feature has no announced availability in sovereign environments at the time of this playbook's last UI verification.
>
> **Companion controls:** [1.2 Agent Registry & Integrated Apps Management](../../../controls/pillar-1-security/1.2-agent-registry-and-integrated-apps-management.md) feeds the SPONSOR namespace (§2). [3.6 Orphaned Agent Detection & Remediation](../../../controls/pillar-3-reporting/3.6-orphaned-agent-detection-and-remediation.md) consumes the LIFECYCLE namespace outputs (§4).
>
> **Last UI verified:** May 2026 against Microsoft Entra admin center build 2026.05.x and Microsoft Graph beta endpoint.

---

## Document Conventions

| Convention | Value |
|---|---|
| PowerShell baseline | PowerShell 7.4+ Core; `#Requires -Version 7.4` |
| Test framework | Pester 5.5+ |
| Output discipline | No `Write-Host`. All evidence emitted as structured objects via `Write-Output`, then serialized to JSON. |
| Sovereign cloud handling | All Pester suites detect tenant cloud and emit `SKIPPED` with compensating-control pointer rather than `FAIL` (see §8). |
| Evidence retention | 6 years (FINRA Rule 4511 / SEC 17a-4) on WORM-protected storage. |
| Hashing | SHA-256 over canonical JSON; chain hashes in `attestation.json` per §10. |
| Sovereign anchor | All sovereign-aware functions reference `../../_shared/powershell-baseline.md#3-sovereign-cloud-endpoints-gcc-gcc-high-dod`. |

> **Regulatory framing.** This playbook helps meet recordkeeping, access-management, and oversight expectations under FINRA Rules 3110 and 4511, FINRA Notice 25-07, SEC Rule 17a-4, SOX §404, GLBA §501(b), OCC Bulletin 2026-13 (formerly OCC Bulletin 2011-12), and FFIEC IT Examination Handbook (Information Security & Management). It does **not** by itself ensure compliance; organizations should verify findings against their own legal and regulatory obligations and tailor thresholds to their risk appetite.

---

## §0 Pre-Test Prerequisites & Sovereign Cloud Bootstrap

### 0.1 Operator prerequisites

The operator running this playbook must hold one of the following Entra role assignments, scoped to the tenant under test, and activated through Privileged Identity Management (PIM) for the duration of the test run:

| Role (canonical) | Required for |
|---|---|
| Entra Identity Governance Admin | Access package, access review, and lifecycle workflow read APIs (§3, §4, §5, §6) |
| Entra Agent ID Admin | Agent identity enumeration, sponsor field reads (§2, §9) |
| Entra Security Reader | Audit log reads, sign-in log reads (§7) |
| Purview Compliance Admin (read) | Cross-check audit retention labels in §7 |
| AI Governance Lead | Counter-signs the quarterly attestation packet in §13 |

The Pester suites in §2–§9 are **read-only** and do not require write permissions. Remediation runbooks referenced from failure paths (e.g., `Set-AgentSponsorBulk` from the sister [PowerShell Setup](powershell-setup.md) playbook) require additional write scopes and a separate change ticket.

### 0.2 Module baseline

```powershell
#Requires -Version 7.4
#Requires -Modules @{ ModuleName='Microsoft.Graph.Authentication'; ModuleVersion='2.20.0' }
#Requires -Modules @{ ModuleName='Microsoft.Graph.Identity.Governance'; ModuleVersion='2.20.0' }
#Requires -Modules @{ ModuleName='Microsoft.Graph.Identity.SignIns'; ModuleVersion='2.20.0' }
#Requires -Modules @{ ModuleName='Microsoft.Graph.Beta.Applications'; ModuleVersion='2.20.0' }
#Requires -Modules @{ ModuleName='Pester'; ModuleVersion='5.5.0' }

$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest
```

### 0.3 PRE gates (must all pass before §2–§9 execute)

The bootstrap script `Invoke-Agt226PreFlight.ps1` runs seven pre-flight gates. Any `FAIL` halts the suite and emits a single evidence artifact `preflight-FAILED-<runId>.json`. Any `SKIPPED` from PRE-06 redirects the run to §8 (sovereign compensating control).

| Gate | ID | Purpose | Failure behavior |
|---|---|---|---|
| Module presence | PRE-01 | Confirms required modules loaded at the pinned versions above | HALT |
| Graph context | PRE-02 | Confirms Connect-MgGraph established with required scopes | HALT |
| Tenant identification | PRE-03 | Captures `tenantId`, `displayName`, `verifiedDomains[0].name` for every evidence record | HALT |
| Cloud detection | PRE-04 | Reads `(Get-MgContext).Environment` and maps to `Commercial / GCC / GCCH / DoD` | Continue with `cloud` field set |
| License gate | PRE-05 | Confirms tenant holds at least one **Microsoft Agent 365** or **Microsoft 365 E7** SKU (post-GA: `SkuPartNumber -like 'Microsoft_Agent_365*' -or -like 'M365_E7*'`). Pre-GA, this gate looked for a `Microsoft_365_Copilot*` SKU — verify exact SKU part numbers in your tenant via `Get-MgSubscribedSku` and update the regex if needed. | HALT — Agent ID requires post-GA licensing |
| Agent ID API operability gate | PRE-06 | Confirms the `/beta/agents` endpoint is reachable to the calling principal (HTTP 200 vs 404/403). Pre-GA this gate also evidenced Frontier program enrollment; post-GA a 404/403 most likely indicates a license-coverage gap, RBAC gap, or sovereign-cloud non-availability. | If 404/403 in Commercial: HALT with remediation pointer (license + RBAC); if sovereign: route to §8 |
| Clock skew gate | PRE-07 | Compares local UTC to `Date` header from Graph response; aborts if drift > 60 seconds | HALT |

### 0.4 Sovereign bootstrap pattern

```powershell
function Test-Agt226SovereignTenant {
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
    }
}
```

When `is_sovereign` is `$true`, every Pester `It` block in §2–§7 and §9 emits:

```json
{ "status": "SKIPPED", "reason": "Entra Agent ID not GA in sovereign cloud at run time", "compensating_control_ref": "§8" }
```

This produces a defensible audit trail showing the test was attempted, was correctly skipped on regulatory-sound grounds, and was supplemented by the manual attestation in §8 — rather than appearing as an unexplained gap.

### 0.5 Run identifier

Every test run is tagged with a deterministic `runId` of the form `AGT226-yyyyMMdd-HHmmss-<8charGuid>`. The `runId` is embedded in every evidence record and in the filename of every artifact produced by §10.

---

## §1 Namespace Catalog

The eight Verification Criteria from [Control 2.26](../../../controls/pillar-2-management/2.26-entra-agent-id-identity-governance.md) are evidenced by eight test namespaces. Each namespace produces independent evidence records that combine into a single signed evidence pack (§10).

| Namespace | Evidences Criterion | Section | Cadence | Owner |
|---|---|---|---|---|
| `PREVIEW` | C2.26-1 (Agent ID surface reachable — Microsoft Agent 365 / M365 E7 + Microsoft 365 Copilot license coverage; namespace name retained for backward-compat) | §9 | Per release / monthly | Entra Agent ID Admin |
| `SPONSOR` | C2.26-2 (every Z2/Z3 agent has assigned sponsor) | §2 | Daily | AI Governance Lead |
| `ACCESSPKG` | C2.26-3 + C2.26-4 (packages exist; ≤365-day expiry; no perpetual Z3) | §3 | Daily | Entra Identity Governance Admin |
| `LIFECYCLE` | C2.26-5 (workflow triggers on sponsor departure; manager-transfer succeeds) | §4 | Weekly | Entra Identity Governance Admin |
| `REVIEW` | C2.26-6 (quarterly Z3 access certification) | §5 | Quarterly | Compliance Officer |
| `EXPIRY` | C2.26-7 (renewal-with-justification or removal within 24h of expiry) | §6 | Daily | AI Governance Lead |
| `SIEM` | C2.26-8 (events forwarded to SIEM with 6-year retention) | §7 | Weekly | Entra Security Admin |
| `SOV` | All criteria — sovereign compensating attestation | §8 | Quarterly (sovereign tenants only) | AI Governance Lead |

Each namespace section in this document follows an identical structure:

1. **Criterion mapping** — explicit pointer to which numbered criterion in Control 2.26 §9 is satisfied.
2. **Pre-conditions** — what must already be true (e.g., access packages exist, Graph scopes granted).
3. **Pester suite** — `Describe "AGT226-{NS}" { Context "Zone {1|2|3}" { It "..." } }` with PS 7.4 / Pester 5.5 syntax.
4. **Sample passing JSON evidence record** — exact shape that flows into the evidence pack.
5. **Sample failing JSON evidence record + remediation pointer** — links to a numbered triage entry in §11.
6. **Examiner artifact** — filename pattern, retention duration, signing policy.
7. **Zone 1 / Zone 2 / Zone 3 thresholds** — pass/warn/fail bands per zone.
8. **Regulator mapping** — which specific regulatory citation each test supports.

### 1.1 Evidence record schema (canonical)

Every evidence record produced by every namespace MUST conform to this schema. The schema is enforced by `Test-Agt226EvidenceSchema` in §10.

```json
{
  "control_id": "2.26",
  "run_id": "AGT226-20260415-093012-a1b2c3d4",
  "run_timestamp": "2026-04-15T09:30:12Z",
  "tenant_id": "11111111-2222-3333-4444-555555555555",
  "tenant_display_name": "Contoso Bank, N.A.",
  "cloud": "Commercial",
  "namespace": "SPONSOR",
  "criterion": "C2.26-2",
  "zone": "2",
  "subject_id": "agent-payments-summarizer-001",
  "subject_type": "agent_identity",
  "status": "PASS",
  "assertion": "Agent has non-null sponsor field referencing an active employee",
  "observed_value": { "sponsor_id": "user-44ab-...", "sponsor_active": true },
  "expected_value": { "sponsor_id": "<non-null>", "sponsor_active": true },
  "evidence_artifacts": ["sponsor-snapshot-AGT226-20260415-093012-a1b2c3d4.json"],
  "regulator_mappings": ["FINRA-3110", "SOX-404", "GLBA-501b", "OCC-2011-12"],
  "remediation_ref": null,
  "operator_upn": "agt226-runner@contoso.com",
  "schema_version": "1.0"
}
```

---

## §2 SPONSOR — Sponsor Assignment Evidence

### 2.1 Criterion mapping

This namespace evidences **C2.26-2**: *every Zone 2 and Zone 3 agent identity has a non-null, currently active sponsor recorded in the Entra Agent ID extension attribute `sponsorObjectId`*. Zone 1 agents are personal-scope and inherit sponsorship from the creator's user account; the Zone 1 test therefore verifies `creator == sponsor` rather than a discrete sponsor field.

The SPONSOR namespace is the keystone of Control 2.26: an unsponsored agent is, for examination purposes, an orphan. FINRA Rule 3110 (Supervision) and OCC Bulletin 2026-13 (formerly OCC Bulletin 2011-12) (Model Risk Management) both require a named individual accountable for the system's behavior. An empty sponsor field is therefore a Critical finding and pages the on-call AI Governance Lead within 15 minutes (see §11).

### 2.2 Pre-conditions

- PRE-01 through PRE-07 from §0 returned `PASS`.
- The current Graph context holds `AgentIdentity.Read.All` and `User.Read.All` delegated or application scopes.
- The sister function `Get-AllAgentIdentities` from [PowerShell Setup §3.1](powershell-setup.md) is available in the session module path.
- The reference dataset `agents-expected.csv` (the "golden list" maintained by the AI Governance Lead per Control 1.2) is reachable at the path supplied via `-ExpectedAgentsCsv`.

### 2.3 Pester suite

```powershell
#Requires -Version 7.4
#Requires -Modules Pester

BeforeDiscovery {
    $sov = Test-Agt226SovereignTenant
    $script:CloudTag = $sov.cloud
    $script:IsSovereign = $sov.is_sovereign
    if (-not $script:IsSovereign) {
        $script:Agents = Get-AllAgentIdentities
        $script:UnsponsoredZ23 = Get-AgentsWithoutSponsors -Zones 2,3
    }
}

Describe "AGT226-SPONSOR" -Tag 'C2.26','SPONSOR' {

    Context "Sovereign cloud short-circuit" -Skip:(-not $script:IsSovereign) {
        It "emits SKIPPED with §8 compensating control pointer" {
            $rec = New-Agt226EvidenceRecord -Namespace 'SPONSOR' `
                -Criterion 'C2.26-2' -Zone 'all' -Status 'SKIPPED' `
                -Assertion 'Sovereign tenant; manual attestation per §8' `
                -RemediationRef 'TRG-SOV-01'
            $rec.status | Should -Be 'SKIPPED'
        }
    }

    Context "Zone 2" -Skip:$script:IsSovereign {
        It "every Zone 2 agent has a non-null sponsorObjectId" {
            $z2 = $script:Agents | Where-Object zone -eq 2
            $missing = $z2 | Where-Object { -not $_.sponsorObjectId }
            $missing.Count | Should -Be 0 -Because "C2.26-2 requires Z2 sponsorship"
        }
        It "every Zone 2 sponsor references an enabled user account" {
            $z2 = $script:Agents | Where-Object zone -eq 2
            foreach ($a in $z2) {
                $u = Get-MgUser -UserId $a.sponsorObjectId -Property accountEnabled -ErrorAction SilentlyContinue
                $u.accountEnabled | Should -BeTrue -Because "agent $($a.id) sponsor must be active"
            }
        }
    }

    Context "Zone 3" -Skip:$script:IsSovereign {
        It "every Zone 3 agent has a sponsorObjectId AND a backup sponsor" {
            $z3 = $script:Agents | Where-Object zone -eq 3
            foreach ($a in $z3) {
                $a.sponsorObjectId         | Should -Not -BeNullOrEmpty
                $a.backupSponsorObjectId   | Should -Not -BeNullOrEmpty -Because "Z3 requires dual-sponsor per Control 2.26 §5"
            }
        }
        It "no Zone 3 agent shares a sponsor and backup sponsor (separation of duties)" {
            $z3 = $script:Agents | Where-Object zone -eq 3
            foreach ($a in $z3) {
                $a.sponsorObjectId | Should -Not -Be $a.backupSponsorObjectId
            }
        }
    }

    Context "Zone 1" -Skip:$script:IsSovereign {
        It "every Zone 1 agent's sponsor equals its creator (personal scope)" {
            $z1 = $script:Agents | Where-Object zone -eq 1
            foreach ($a in $z1) {
                $a.sponsorObjectId | Should -Be $a.createdBy.user.id
            }
        }
    }
}
```

### 2.4 Sample passing evidence record

```json
{
  "control_id": "2.26",
  "run_id": "AGT226-20260415-093012-a1b2c3d4",
  "run_timestamp": "2026-04-15T09:30:12Z",
  "tenant_id": "11111111-2222-3333-4444-555555555555",
  "cloud": "Commercial",
  "namespace": "SPONSOR",
  "criterion": "C2.26-2",
  "zone": "2",
  "subject_id": "agent-payments-summarizer-001",
  "subject_type": "agent_identity",
  "status": "PASS",
  "assertion": "Z2 agent has non-null active sponsor",
  "observed_value": {
    "sponsor_id": "44ab1234-5678-90ab-cdef-1234567890ab",
    "sponsor_upn": "alice.banker@contoso.com",
    "sponsor_active": true,
    "sponsor_assignment_date": "2025-11-02T14:22:00Z"
  },
  "expected_value": { "sponsor_id": "<non-null>", "sponsor_active": true },
  "evidence_artifacts": ["sponsor-snapshot-AGT226-20260415-093012-a1b2c3d4.json"],
  "regulator_mappings": ["FINRA-3110", "SOX-404", "GLBA-501b", "OCC-2011-12"],
  "remediation_ref": null,
  "schema_version": "1.0"
}
```

### 2.5 Sample failing evidence record

```json
{
  "control_id": "2.26",
  "run_id": "AGT226-20260415-093012-a1b2c3d4",
  "run_timestamp": "2026-04-15T09:30:12Z",
  "tenant_id": "11111111-2222-3333-4444-555555555555",
  "cloud": "Commercial",
  "namespace": "SPONSOR",
  "criterion": "C2.26-2",
  "zone": "3",
  "subject_id": "agent-loan-decisioner-007",
  "subject_type": "agent_identity",
  "status": "FAIL",
  "assertion": "Z3 agent must have non-null active sponsor and backup sponsor",
  "observed_value": {
    "sponsor_id": "44ab1234-5678-90ab-cdef-1234567890ab",
    "sponsor_active": false,
    "sponsor_termination_date": "2026-03-31T23:59:59Z",
    "backup_sponsor_id": null
  },
  "expected_value": { "sponsor_id": "<active user>", "backup_sponsor_id": "<non-null>" },
  "evidence_artifacts": ["sponsor-snapshot-AGT226-20260415-093012-a1b2c3d4.json"],
  "regulator_mappings": ["FINRA-3110", "SOX-404", "OCC-2011-12"],
  "remediation_ref": "TRG-SPONSOR-01",
  "schema_version": "1.0"
}
```

Remediation `TRG-SPONSOR-01` (see §11.2): page on-call AI Governance Lead, suspend agent within 4 hours per Z3 SLA, run `Set-AgentSponsorBulk` once a successor sponsor is named.

### 2.6 Examiner artifact

| Artifact | Filename pattern | Retention | Signed by |
|---|---|---|---|
| Sponsor snapshot | `sponsor-snapshot-<runId>.json` | 6 years (FINRA 4511) | AI Governance Lead (`attestation.json` chain entry) |
| Pester results (JUnit XML) | `pester-SPONSOR-<runId>.xml` | 6 years | Same |
| Failing-record extract (if any) | `sponsor-failures-<runId>.json` | 6 years + open until remediated | Same, plus remediation ticket reference |

### 2.7 Zone thresholds

| Zone | PASS band | WARN band | FAIL band |
|---|---|---|---|
| Zone 1 | 100% of Z1 agents have `sponsor == creator` | n/a | any mismatch |
| Zone 2 | 100% sponsored AND 100% sponsors active | ≥ 99% sponsored AND any sponsor inactive < 7 days | < 99% sponsored OR any sponsor inactive ≥ 7 days |
| Zone 3 | 100% sponsored AND 100% backup-sponsored AND separation enforced | n/a (no WARN band for Z3 — pass or fail) | any deviation |

### 2.8 Regulator mapping

| Test | FINRA 3110 | FINRA 4511 | SOX §404 | GLBA §501(b) | OCC Bulletin 2026-13 (formerly OCC 2011-12) |
|---|---|---|---|---|---|
| Z2 sponsor non-null | ✓ supervision | ✓ recordkeeping | ✓ named owner of control | — | ✓ model owner |
| Z2 sponsor active | ✓ ongoing supervision | — | ✓ control operating effectiveness | ✓ designated employee | ✓ model owner |
| Z3 dual sponsor | ✓ heightened supervision | ✓ | ✓ segregation | ✓ | ✓ model owner + challenger |
| Z1 sponsor==creator | ✓ user-level accountability | ✓ | — | — | — |

---

## §3 ACCESSPKG — Access Package Design & Assignment Evidence

### 3.1 Criterion mapping

This namespace evidences two criteria simultaneously:

- **C2.26-3** — Entra Identity Governance access packages exist for every standard agent resource bundle, and **Zone 3 agents may obtain resources only via access packages** (no direct group, role, or app-permission assignments).
- **C2.26-4** — every access package assignment policy on Z2 and Z3 packages enforces a **time-bound expiration ≤ 365 days**, and **no Z3 assignment is perpetual**.

The catalog under test is `"AI Agent Resources"` (per [PowerShell Setup §4.2](powershell-setup.md)). All packages within this catalog are in scope.

### 3.2 Pre-conditions

- PRE gates pass; Graph context holds `EntitlementManagement.Read.All`.
- The catalog `"AI Agent Resources"` exists. If the catalog is missing the suite emits a single `FAIL` record at the catalog level (criterion C2.26-3) and short-circuits.
- Reference design document `agent-package-design.json` (maintained by Entra Identity Governance Admin) lists the expected packages and their resource compositions.

### 3.3 Pester suite

<a id="vc-4-no-perpetual-z3"></a>

```powershell
Describe "AGT226-ACCESSPKG" -Tag 'C2.26','ACCESSPKG' {

    BeforeAll {
        $script:Catalog = Get-MgEntitlementManagementAccessPackageCatalog `
            -Filter "displayName eq 'AI Agent Resources'" -ErrorAction SilentlyContinue
        $script:Packages = if ($script:Catalog) {
            Get-MgEntitlementManagementAccessPackage -Filter "catalogId eq '$($script:Catalog.Id)'" -All
        } else { @() }
        $script:Assignments = Get-AgentAccessPackageAssignments
    }

    Context "Catalog presence (C2.26-3)" -Skip:$script:IsSovereign {
        It "the 'AI Agent Resources' catalog exists" {
            $script:Catalog | Should -Not -BeNullOrEmpty
        }
        It "the catalog contains at least one package" {
            $script:Packages.Count | Should -BeGreaterThan 0
        }
    }

    Context "Z3 channels (C2.26-3)" -Skip:$script:IsSovereign {
        It "no Zone 3 agent has direct group memberships outside an access package" {
            $z3 = $script:Agents | Where-Object zone -eq 3
            foreach ($a in $z3) {
                $direct = Get-MgUserMemberOf -UserId $a.id -All |
                    Where-Object { $_.AdditionalProperties.assignmentType -ne 'accessPackage' }
                $direct.Count | Should -Be 0 -Because "agent $($a.id) (Z3) must receive resources only via packages"
            }
        }
        It "no Zone 3 agent holds a directly assigned Entra role" {
            $z3 = $script:Agents | Where-Object zone -eq 3
            foreach ($a in $z3) {
                $roles = Get-MgRoleManagementDirectoryRoleAssignment `
                    -Filter "principalId eq '$($a.id)'" -All
                $roles.Count | Should -Be 0
            }
        }
    }

    Context "Time-bound expiry (C2.26-4)" -Skip:$script:IsSovereign {
        It "every Z2/Z3 package assignment policy has duration ≤ 365 days" {
            foreach ($pkg in $script:Packages) {
                $policies = Get-MgEntitlementManagementAccessPackageAssignmentPolicy `
                    -Filter "accessPackageId eq '$($pkg.Id)'" -All
                foreach ($pol in $policies) {
                    $dur = $pol.Expiration.Duration
                    if ($null -ne $dur) {
                        # Parse ISO-8601 duration (e.g., P365D, P1Y)
                        $days = ConvertFrom-Iso8601Duration $dur
                        $days | Should -BeLessOrEqual 365 -Because "policy $($pol.Id) on package $($pkg.DisplayName)"
                    } else {
                        # Type must not be 'noExpiration' for Z3
                        $pol.Expiration.Type | Should -Not -Be 'noExpiration'
                    }
                }
            }
        }
        It "no Zone 3 access package allows perpetual assignment" {
            $z3pkgs = $script:Packages | Where-Object { $_.AdditionalProperties.zone -eq '3' }
            foreach ($pkg in $z3pkgs) {
                $policies = Get-MgEntitlementManagementAccessPackageAssignmentPolicy `
                    -Filter "accessPackageId eq '$($pkg.Id)'" -All
                foreach ($pol in $policies) {
                    $pol.Expiration.Type | Should -Not -Be 'noExpiration'
                }
            }
        }
    }
}
```

### 3.4 Sample passing evidence record

```json
{
  "control_id": "2.26",
  "run_id": "AGT226-20260415-093012-a1b2c3d4",
  "namespace": "ACCESSPKG",
  "criterion": "C2.26-4",
  "zone": "3",
  "subject_id": "pkg-trading-floor-research-bundle",
  "subject_type": "access_package_policy",
  "status": "PASS",
  "assertion": "Z3 access package policy duration ≤ 365 days and not perpetual",
  "observed_value": {
    "policy_id": "policy-9af8...",
    "duration_days": 90,
    "expiration_type": "afterDuration",
    "requires_approval": true,
    "approver_count": 2
  },
  "expected_value": { "duration_days": "≤365", "expiration_type": "!=noExpiration" },
  "regulator_mappings": ["FINRA-3110", "SOX-404", "OCC-2011-12", "FFIEC-IS-AccessMgmt"],
  "evidence_artifacts": ["accesspkg-snapshot-AGT226-20260415-093012-a1b2c3d4.json"],
  "schema_version": "1.0"
}
```

### 3.5 Sample failing evidence record

```json
{
  "control_id": "2.26",
  "namespace": "ACCESSPKG",
  "criterion": "C2.26-3",
  "zone": "3",
  "subject_id": "agent-loan-decisioner-007",
  "subject_type": "agent_identity",
  "status": "FAIL",
  "assertion": "Z3 agent must receive resources only via access packages",
  "observed_value": {
    "direct_group_memberships": [
      { "groupId": "g-credit-models", "assignmentType": "direct", "addedOn": "2026-02-10T11:00:00Z" }
    ]
  },
  "expected_value": { "direct_group_memberships": [] },
  "remediation_ref": "TRG-ACCESSPKG-02",
  "regulator_mappings": ["FINRA-3110","SOX-404","OCC-2011-12"],
  "schema_version": "1.0"
}
```

`TRG-ACCESSPKG-02` (§11.3): remove the direct membership within 24 hours; re-assign the agent through the access package; record the variance in the Identity Governance change log.

### 3.6 Examiner artifact

| Artifact | Filename | Retention |
|---|---|---|
| Catalog & package design snapshot | `accesspkg-snapshot-<runId>.json` | 6 years |
| Per-policy expiry table (CSV) | `accesspkg-policies-<runId>.csv` | 6 years |
| Pester JUnit | `pester-ACCESSPKG-<runId>.xml` | 6 years |

### 3.7 Zone thresholds

| Zone | PASS | WARN | FAIL |
|---|---|---|---|
| Zone 1 | n/a — Z1 agents do not consume access packages | — | — |
| Zone 2 | 100% of Z2 packages have ≤ 365-day expiry | one package 366–400 days, with documented variance | any package > 400 days OR any `noExpiration` policy |
| Zone 3 | 100% of Z3 resources via packages AND 100% policies ≤ 365 days AND zero `noExpiration` | n/a | any deviation |

### 3.8 Regulator mapping

| Test | FINRA 3110 | SOX §404 | OCC Bulletin 2026-13 (formerly OCC 2011-12) | FFIEC IS — Access Mgmt |
|---|---|---|---|---|
| Catalog exists | ✓ | ✓ | ✓ | ✓ |
| Z3 channel discipline | ✓ | ✓ segregation | ✓ | ✓ |
| ≤365-day expiry | ✓ | ✓ recurring review | ✓ | ✓ periodic recertification |
| No perpetual Z3 | ✓ | ✓ | ✓ | ✓ |

---

## §4 LIFECYCLE — Sponsor-Departure Workflow Evidence

### 4.1 Criterion mapping

This namespace evidences **C2.26-5**: a Microsoft Entra **Lifecycle Workflow** is configured and active for the trigger *user account becomes inactive or marked as a leaver*, and that workflow's task on agent identities — specifically the **default automatic manager-transfer behavior of Entra** — has executed for every sponsor departure observed in the lookback window.

> **Important accuracy note.** This control does **not** require organizations to build a custom suspend-on-leave workflow. Entra's default behavior, when a sponsor's user account transitions to `accountEnabled = false` or carries the `employeeLeaveDateTime` past trigger, is to transfer agent ownership to the sponsor's manager. The Pester tests verify that this default occurred. A custom suspension workflow is reserved for the case where the manager **declines** the transfer (escalation path; see §11.5).

### 4.2 Pre-conditions

- Lifecycle Workflows feature is licensed (Entra ID Governance SKU).
- The reference workflow `Agent Sponsor Departure Transfer` exists and is in `enabled` state.
- The lookback window for verification is the prior 30 days by default; configurable via `-LookbackDays`.

### 4.3 Pester suite

```powershell
Describe "AGT226-LIFECYCLE" -Tag 'C2.26','LIFECYCLE' {

    BeforeAll {
        $script:WfName = 'Agent Sponsor Departure Transfer'
        $script:Wf = Get-MgIdentityGovernanceLifecycleWorkflow `
            -Filter "displayName eq '$script:WfName'" -ErrorAction SilentlyContinue
        $script:Lookback = (Get-Date).AddDays(-30).ToUniversalTime()
        $script:Departures = Get-MgUser -All `
            -Filter "employeeLeaveDateTime ge $($script:Lookback.ToString('o'))" `
            -Property id,userPrincipalName,employeeLeaveDateTime,manager
    }

    Context "Workflow definition" -Skip:$script:IsSovereign {
        It "the lifecycle workflow exists and is enabled" {
            $script:Wf | Should -Not -BeNullOrEmpty
            $script:Wf.IsEnabled | Should -BeTrue
        }
        It "the workflow trigger is the leaver scenario" {
            $script:Wf.ExecutionConditions.AdditionalProperties['@odata.type'] |
                Should -Match 'triggerAndScopeBasedConditions'
            $script:Wf.ExecutionConditions.Trigger.AdditionalProperties.timeBasedAttribute |
                Should -Be 'employeeLeaveDateTime'
        }
        It "the workflow includes the manager-transfer task on agent identities" {
            $taskTypes = $script:Wf.Tasks.TaskDefinitionId
            $taskTypes | Should -Contain 'reassignAgentOwnerToManager'
        }
    }

    Context "Workflow execution within lookback" -Skip:$script:IsSovereign {
        It "every departed sponsor in the lookback window has a workflow run" {
            foreach ($d in $script:Departures) {
                $sponsoredAgents = $script:Agents | Where-Object sponsorObjectId -eq $d.Id
                if ($sponsoredAgents.Count -eq 0) { continue }
                $runs = Get-MgIdentityGovernanceLifecycleWorkflowRun `
                    -LifecycleWorkflowId $script:Wf.Id -All |
                    Where-Object { $_.Subject.Id -eq $d.Id }
                $runs.Count | Should -BeGreaterOrEqual 1 -Because "departure $($d.UserPrincipalName) must trigger workflow"
            }
        }
        It "every workflow run completed with status Completed (not Failed)" {
            $runs = Get-MgIdentityGovernanceLifecycleWorkflowRun `
                -LifecycleWorkflowId $script:Wf.Id -All |
                Where-Object { $_.StartedDateTime -ge $script:Lookback }
            foreach ($r in $runs) {
                $r.ProcessingStatus | Should -BeIn @('completed','completedWithErrors')
                if ($r.ProcessingStatus -eq 'completedWithErrors') {
                    # Must have a logged escalation
                    $r.AdditionalProperties.ContainsKey('escalation_ticket') | Should -BeTrue
                }
            }
        }
    }

    Context "Manager-transfer outcome" -Skip:$script:IsSovereign {
        It "for every successful run, the affected agent's sponsor now equals the departed user's manager" {
            $runs = Get-MgIdentityGovernanceLifecycleWorkflowRun `
                -LifecycleWorkflowId $script:Wf.Id -All |
                Where-Object { $_.ProcessingStatus -eq 'completed' -and $_.StartedDateTime -ge $script:Lookback }
            foreach ($r in $runs) {
                $departedId = $r.Subject.Id
                $managerId  = (Get-MgUser -UserId $departedId -ExpandProperty manager).Manager.Id
                $agents = $script:Agents | Where-Object sponsorObjectId -eq $departedId
                # Refresh agent records post-run
                foreach ($a in $agents) {
                    $fresh = Get-AllAgentIdentities -AgentId $a.id
                    $fresh.sponsorObjectId | Should -Be $managerId `
                        -Because "default manager-transfer should have replaced sponsor"
                }
            }
        }
    }
}
```

### 4.4 Sample passing evidence record

```json
{
  "control_id": "2.26",
  "namespace": "LIFECYCLE",
  "criterion": "C2.26-5",
  "zone": "all",
  "subject_id": "wf-run-2c7b9-20260411",
  "subject_type": "lifecycle_workflow_run",
  "status": "PASS",
  "assertion": "Sponsor-departure workflow executed and manager-transfer succeeded",
  "observed_value": {
    "departed_sponsor_upn": "departed.banker@contoso.com",
    "departure_date": "2026-04-10T17:00:00Z",
    "workflow_run_id": "2c7b9-20260411",
    "processing_status": "completed",
    "agents_affected": 3,
    "manager_now_sponsor": true
  },
  "regulator_mappings": ["FINRA-3110","SOX-404","OCC-2011-12","GLBA-501b"],
  "evidence_artifacts": ["lifecycle-runs-AGT226-20260415-093012-a1b2c3d4.json"],
  "schema_version": "1.0"
}
```

### 4.5 Sample failing evidence record

```json
{
  "control_id": "2.26",
  "namespace": "LIFECYCLE",
  "criterion": "C2.26-5",
  "subject_id": "wf-run-9z3a-20260413",
  "status": "FAIL",
  "assertion": "Departed sponsor's agents were not transferred",
  "observed_value": {
    "departed_sponsor_upn": "departed2.banker@contoso.com",
    "departure_date": "2026-04-12T17:00:00Z",
    "workflow_run_id": null,
    "agents_still_pointing_at_departed_sponsor": 2
  },
  "remediation_ref": "TRG-LIFECYCLE-01",
  "regulator_mappings": ["FINRA-3110","OCC-2011-12"],
  "schema_version": "1.0"
}
```

`TRG-LIFECYCLE-01` (§11.4): manually invoke `Set-AgentSponsorBulk` with the departed user's manager as new sponsor; open a problem ticket against the lifecycle workflow; if manager declines transfer, escalate to the suspension path in §11.5.

### 4.6 Examiner artifact

| Artifact | Filename | Retention |
|---|---|---|
| Workflow definition snapshot | `lifecycle-workflow-def-<runId>.json` | 6 years |
| Workflow run log (last 30 days) | `lifecycle-runs-<runId>.json` | 6 years |
| Departed-sponsor reconciliation table | `lifecycle-reconciliation-<runId>.csv` | 6 years |

### 4.7 Zone thresholds

| Zone | PASS | WARN | FAIL |
|---|---|---|---|
| Zone 1 | n/a — Z1 agents are deleted with creator account by default | — | — |
| Zone 2 | 100% of departed sponsors processed within 24 hours | one departure processed 24–72 hours late, with documented justification | any departure unprocessed > 72 hours |
| Zone 3 | 100% processed within 4 hours AND every transfer cross-checked against backup sponsor | n/a | any Z3 agent unprocessed > 4 hours |

### 4.8 Regulator mapping

| Test | FINRA 3110 | SOX §404 | GLBA §501(b) | OCC Bulletin 2026-13 (formerly OCC 2011-12) |
|---|---|---|---|---|
| Workflow exists & enabled | ✓ supervisory system | ✓ control design | ✓ designated employee continuity | ✓ model owner continuity |
| Run within lookback | ✓ supervision evidence | ✓ control operating | ✓ | ✓ |
| Manager-transfer outcome | ✓ accountability transfer | ✓ | ✓ | ✓ challenger continuity |

---

## §5 REVIEW — Quarterly Access Certification Evidence

### 5.1 Criterion mapping

This namespace evidences **C2.26-6**: a **quarterly access review campaign** is configured against every Zone 3 access package and every group that grants Z3 agent identities elevated scope, and the most recent campaign **completed with a recorded decision** (Approve / Deny / Don't know — counted as Deny per default policy) for every reviewer-subject pair, attributed to a named certifier with a timestamp.

### 5.2 Pre-conditions

- Entra ID Governance (Access Reviews) licensed.
- The quarterly campaign template `Z3 Agent Access Recertification` is deployed.
- Lookback window is the most recently completed calendar quarter.

### 5.3 Pester suite

```powershell
Describe "AGT226-REVIEW" -Tag 'C2.26','REVIEW' {

    BeforeAll {
        $script:Quarter = Get-PreviousQuarterBoundary  # returns @{ start; end; label='Q1-2026' }
        $script:Reviews = Get-MgIdentityGovernanceAccessReviewDefinition -All |
            Where-Object { $_.DisplayName -like 'Z3 Agent Access Recertification*' }
    }

    Context "Campaign existence" -Skip:$script:IsSovereign {
        It "the Z3 quarterly campaign exists" {
            $script:Reviews.Count | Should -BeGreaterThan 0
        }
        It "every Z3 access package is in scope of at least one campaign" {
            $z3pkgs = $script:Packages | Where-Object { $_.AdditionalProperties.zone -eq '3' }
            foreach ($pkg in $z3pkgs) {
                $covered = $script:Reviews | Where-Object {
                    $_.Scope.AdditionalProperties.resourceScopes -contains $pkg.Id
                }
                $covered.Count | Should -BeGreaterThan 0 -Because "package $($pkg.DisplayName) needs Q-recertification"
            }
        }
    }

    Context "Campaign completion within prior quarter" -Skip:$script:IsSovereign {
        It "every campaign in scope completed within the prior quarter" {
            foreach ($r in $script:Reviews) {
                $instances = Get-MgIdentityGovernanceAccessReviewDefinitionInstance `
                    -AccessReviewScheduleDefinitionId $r.Id -All |
                    Where-Object {
                        $_.StartDateTime -ge $script:Quarter.start -and
                        $_.EndDateTime   -le $script:Quarter.end
                    }
                $instances.Count | Should -BeGreaterThan 0
                foreach ($inst in $instances) {
                    $inst.Status | Should -Be 'Completed'
                }
            }
        }
        It "every reviewer decision has a named certifier and a timestamp" {
            foreach ($r in $script:Reviews) {
                $instances = Get-MgIdentityGovernanceAccessReviewDefinitionInstance `
                    -AccessReviewScheduleDefinitionId $r.Id -All
                foreach ($inst in $instances) {
                    $decisions = Get-MgIdentityGovernanceAccessReviewDefinitionInstanceDecision `
                        -AccessReviewScheduleDefinitionId $r.Id `
                        -AccessReviewInstanceId $inst.Id -All
                    foreach ($d in $decisions) {
                        $d.ReviewedBy.Id      | Should -Not -BeNullOrEmpty
                        $d.ReviewedDateTime   | Should -Not -BeNullOrEmpty
                        $d.Decision           | Should -BeIn @('Approve','Deny','DontKnow','NotReviewed')
                    }
                }
            }
        }
        It "any 'NotReviewed' decision has been auto-applied per default policy (Deny)" {
            foreach ($r in $script:Reviews) {
                $r.Settings.DefaultDecisionEnabled | Should -BeTrue
                $r.Settings.DefaultDecision | Should -Be 'Deny'
            }
        }
    }
}
```

### 5.4 Sample passing evidence record

```json
{
  "control_id": "2.26",
  "namespace": "REVIEW",
  "criterion": "C2.26-6",
  "zone": "3",
  "subject_id": "review-Q1-2026-pkg-trading-floor-research",
  "subject_type": "access_review_instance",
  "status": "PASS",
  "assertion": "Quarterly Z3 access review completed with named certifier per decision",
  "observed_value": {
    "campaign_label": "Q1-2026",
    "instance_id": "rev-9af8...",
    "started": "2026-01-05T00:00:00Z",
    "completed": "2026-03-15T17:00:00Z",
    "decisions_total": 47,
    "approved": 41,
    "denied": 5,
    "not_reviewed_auto_denied": 1,
    "all_decisions_have_certifier": true
  },
  "regulator_mappings": ["FINRA-3110","FINRA-25-07","SOX-404","OCC-2011-12","FFIEC-IS-AccessMgmt"],
  "evidence_artifacts": ["review-decisions-Q1-2026.json"],
  "schema_version": "1.0"
}
```

### 5.5 Sample failing evidence record

```json
{
  "control_id": "2.26",
  "namespace": "REVIEW",
  "criterion": "C2.26-6",
  "subject_id": "review-Q1-2026-pkg-loan-decisioner",
  "status": "FAIL",
  "assertion": "Quarterly review must complete with all decisions attributed",
  "observed_value": {
    "campaign_label": "Q1-2026",
    "completed": null,
    "decisions_pending": 12,
    "default_decision_applied": false
  },
  "remediation_ref": "TRG-REVIEW-01",
  "regulator_mappings": ["FINRA-3110","SOX-404","OCC-2011-12"],
  "schema_version": "1.0"
}
```

`TRG-REVIEW-01` (§11.6): force-apply the default decision via Graph; notify the Compliance Officer; document the lapse for the next 1.2 sponsor attestation cycle.

### 5.6 Examiner artifact

| Artifact | Filename | Retention |
|---|---|---|
| Campaign definition | `review-definition-<runId>.json` | 6 years |
| Per-instance decision export | `review-decisions-<quarterLabel>.json` | 7 years (one year > FINRA minimum to absorb late audits) |
| Reviewer attestation summary CSV | `review-summary-<quarterLabel>.csv` | 6 years |

### 5.7 Zone thresholds

| Zone | PASS | WARN | FAIL |
|---|---|---|---|
| Zone 1 | n/a — Z1 not subject to quarterly review | — | — |
| Zone 2 | annual review (not quarterly); test in §5 evaluates at year-end only | semi-annual lapse | annual lapse |
| Zone 3 | 100% campaigns completed AND 100% decisions certified within the quarter | one decision late ≤ 7 days, with justification | any campaign uncompleted at quarter close |

### 5.8 Regulator mapping

| Test | FINRA 3110 | FINRA 25-07 | SOX §404 | OCC Bulletin 2026-13 (formerly OCC 2011-12) | FFIEC IS |
|---|---|---|---|---|---|
| Campaign exists | ✓ | ✓ | ✓ | ✓ | ✓ |
| Completion in quarter | ✓ | ✓ | ✓ recurring | ✓ ongoing monitoring | ✓ recertification |
| Named certifier per decision | ✓ supervision attribution | ✓ | ✓ control evidence | ✓ | ✓ |

---

## §6 EXPIRY — Renewal & Removal Evidence

### 6.1 Criterion mapping

This namespace evidences **C2.26-7**: every access package assignment that has expired within the prior 90 days has been **either**:

- **(a)** explicitly renewed, with a recorded business justification authored by the Sponsor and counter-acknowledged by the access package owner, **or**
- **(b)** removed within 24 hours of expiry, with audit-log evidence of group/role removal.

A grace state — expired-but-still-granting-access — is a Critical finding.

### 6.2 Pre-conditions

- Audit log retention ≥ 90 days (Entra default for non-Premium is 30 days; Premium P1+ provides 30 days; Diagnostic Settings export to Log Analytics or SIEM extends this — see §7).
- The reference renewal-justification store (`renewals.csv`, maintained by AI Governance Lead) contains the per-renewal justification text and signatures.

### 6.3 Pester suite

```powershell
Describe "AGT226-EXPIRY" -Tag 'C2.26','EXPIRY' {

    BeforeAll {
        $script:Window = (Get-Date).AddDays(-90).ToUniversalTime()
        $script:ExpiredAssignments = Get-AgentAccessPackageAssignments |
            Where-Object {
                $_.expiredDateTime -ge $script:Window -and
                $_.expiredDateTime -le (Get-Date).ToUniversalTime()
            }
        $script:Renewals = Import-Csv -Path $env:AGT226_RENEWALS_CSV
    }

    Context "Disposition coverage (C2.26-7)" -Skip:$script:IsSovereign {
        It "every expired assignment has either renewal evidence or removal evidence" {
            foreach ($a in $script:ExpiredAssignments) {
                $renewal = $script:Renewals | Where-Object assignmentId -eq $a.id
                if ($renewal) {
                    $renewal.justification    | Should -Not -BeNullOrEmpty
                    $renewal.sponsorSignature | Should -Not -BeNullOrEmpty
                    $renewal.ownerSignature   | Should -Not -BeNullOrEmpty
                } else {
                    # Must show removal within 24h
                    $removeEvent = Get-MgAuditLogDirectoryAudit -All `
                        -Filter "activityDisplayName eq 'Remove member from group' and targetResources/any(t:t/id eq '$($a.targetId)')" |
                        Where-Object { $_.ActivityDateTime -ge $a.expiredDateTime -and `
                                       $_.ActivityDateTime -le $a.expiredDateTime.AddHours(24) }
                    $removeEvent.Count | Should -BeGreaterThan 0 `
                        -Because "assignment $($a.id) had no renewal and must show removal within 24h"
                }
            }
        }
    }

    Context "Renewal quality (C2.26-7a)" -Skip:$script:IsSovereign {
        It "every renewal justification is at least 50 characters and references a business reason" {
            foreach ($r in $script:Renewals) {
                $r.justification.Length | Should -BeGreaterOrEqual 50
                $r.justification | Should -Match '(business case|regulator|customer|product|incident)'
            }
        }
        It "no renewal extends a Z3 assignment beyond 365 days from original grant" {
            foreach ($r in $script:Renewals | Where-Object zone -eq '3') {
                $orig = [datetime]$r.originalGrantDate
                $newEnd = [datetime]$r.newExpiryDate
                ($newEnd - $orig).TotalDays | Should -BeLessOrEqual 365
            }
        }
    }
}
```

### 6.4 Sample passing record (renewal path)

```json
{
  "control_id": "2.26",
  "namespace": "EXPIRY",
  "criterion": "C2.26-7",
  "zone": "2",
  "subject_id": "assignment-payments-summarizer-2025Q4",
  "subject_type": "access_package_assignment",
  "status": "PASS",
  "assertion": "Expired assignment renewed with valid justification and signatures",
  "observed_value": {
    "expired_at": "2026-03-31T23:59:59Z",
    "disposition": "renewed",
    "justification_chars": 187,
    "sponsor_signature_at": "2026-03-30T14:00:00Z",
    "owner_signature_at": "2026-03-31T09:15:00Z",
    "new_expiry_at": "2026-09-30T23:59:59Z"
  },
  "regulator_mappings": ["FINRA-3110","FINRA-4511","SOX-404","OCC-2011-12"],
  "evidence_artifacts": ["expiry-snapshot-AGT226-20260415-093012-a1b2c3d4.json","renewals-2026Q1.csv"],
  "schema_version": "1.0"
}
```

### 6.5 Sample passing record (removal path)

```json
{
  "control_id": "2.26",
  "namespace": "EXPIRY",
  "criterion": "C2.26-7",
  "zone": "3",
  "subject_id": "assignment-trading-research-2025Q4",
  "status": "PASS",
  "assertion": "Expired assignment with no renewal removed within 24h",
  "observed_value": {
    "expired_at": "2026-03-31T23:59:59Z",
    "disposition": "removed",
    "removal_event_id": "audit-evt-77ac...",
    "removal_at": "2026-04-01T03:12:00Z",
    "elapsed_hours": 3.2
  },
  "regulator_mappings": ["FINRA-3110","SOX-404","OCC-2011-12"],
  "schema_version": "1.0"
}
```

### 6.6 Sample failing record

```json
{
  "control_id": "2.26",
  "namespace": "EXPIRY",
  "criterion": "C2.26-7",
  "zone": "3",
  "subject_id": "assignment-loan-decisioner-2025Q4",
  "status": "FAIL",
  "assertion": "Expired Z3 assignment must be renewed with justification or removed ≤24h",
  "observed_value": {
    "expired_at": "2026-03-31T23:59:59Z",
    "disposition": "stale",
    "current_state": "still_granting_access",
    "elapsed_hours_since_expiry": 372
  },
  "remediation_ref": "TRG-EXPIRY-01",
  "regulator_mappings": ["FINRA-3110","FINRA-4511","SOX-404","OCC-2011-12"],
  "schema_version": "1.0"
}
```

`TRG-EXPIRY-01` (§11.7): immediately remove the assignment via `Remove-MgEntitlementManagementAssignmentRequest`; open a Critical incident; capture root-cause and add to the next §13 quarterly attestation packet.

### 6.7 Examiner artifact

| Artifact | Filename | Retention |
|---|---|---|
| Expiry disposition table | `expiry-snapshot-<runId>.json` | 6 years |
| Renewal justifications (signed) | `renewals-<quarterLabel>.csv` + `.sig` | 6 years |
| Removal audit-event extract | `expiry-removals-<runId>.json` | 6 years |

### 6.8 Zone thresholds

| Zone | PASS | WARN | FAIL |
|---|---|---|---|
| Zone 1 | n/a (no formal access packages) | — | — |
| Zone 2 | 100% disposed within 24h of expiry | one disposition 24–72h late, with justification | any disposition > 72h late |
| Zone 3 | 100% disposed within 24h AND 0 stale-grant events | n/a | any stale-grant > 0 hours |

### 6.9 Regulator mapping

| Test | FINRA 3110 | FINRA 4511 | SOX §404 | OCC Bulletin 2026-13 (formerly OCC 2011-12) |
|---|---|---|---|---|
| Disposition coverage | ✓ | ✓ retention of decisions | ✓ control operating | ✓ |
| Renewal quality | ✓ | ✓ | ✓ documented justification | ✓ challenger can re-evaluate |
| Removal SLA | ✓ | ✓ | ✓ | ✓ |

---

## §7 SIEM — Forwarding & 6-Year Retention Evidence

### 7.1 Criterion mapping

This namespace evidences **C2.26-8**: Entra Agent ID lifecycle events (sponsor change, package assignment, access review decision, lifecycle workflow execution) are **forwarded to the organization's SIEM** with **6-year retention** in compliance with FINRA Rule 4511 and SEC Rule 17a-4.

> **Important architectural note.** Entra Diagnostic Settings export only at the **category level** (e.g., `AuditLogs`, `IdentityRiskEvents`). Per-event filtering for "agent identity" specifically does **not** happen at the Entra side. The SIEM is the place where agent-related events are isolated using a downstream rule that correlates on `category eq 'AuditLogs'` AND `targetResources.type eq 'AgentIdentity'` (or the equivalent type token in the active Graph schema). The Pester suite therefore tests:
>
> 1. Entra Diagnostic Setting exists at the tenant level and emits the relevant categories.
> 2. The SIEM has received at least one event matching the agent-identity correlation rule in the prior 24 hours.
> 3. The SIEM index housing the events has a retention policy of ≥ 6 years configured.

### 7.2 Pre-conditions

- Diagnostic Setting (e.g., `AgentID-To-SIEM`) exists at tenant scope and exports `AuditLogs`, `SignInLogs`, `IdentityRiskEvents`, and `EnrichedOffice365AuditLogs` (or sovereign-equivalent categories).
- A SIEM API endpoint and bearer token are available via `$env:AGT226_SIEM_BASEURL` and `$env:AGT226_SIEM_TOKEN`.
- The SIEM correlation rule `AgentID-Lifecycle-Events` is deployed.

### 7.3 Pester suite

```powershell
Describe "AGT226-SIEM" -Tag 'C2.26','SIEM' {

    BeforeAll {
        $script:DiagSettings = Get-MgSubscriptionDiagnosticSetting -All -ErrorAction SilentlyContinue
        $script:SiemBase  = $env:AGT226_SIEM_BASEURL
        $script:SiemToken = $env:AGT226_SIEM_TOKEN
    }

    Context "Entra-side export" -Skip:$script:IsSovereign {
        It "a Diagnostic Setting forwards AuditLogs to the SIEM destination" {
            $relevant = $script:DiagSettings | Where-Object {
                $_.Logs.Category -contains 'AuditLogs' -and $_.Logs.Enabled -contains $true
            }
            $relevant.Count | Should -BeGreaterThan 0
        }
        It "the export destination is the contracted SIEM workspace or Event Hub" {
            $relevant = $script:DiagSettings | Where-Object { $_.Logs.Category -contains 'AuditLogs' }
            foreach ($s in $relevant) {
                ($s.WorkspaceId -or $s.EventHubAuthorizationRuleId) | Should -BeTrue
            }
        }
    }

    Context "SIEM-side ingestion" -Skip:$script:IsSovereign {
        It "the SIEM has received at least one agent-identity event in the prior 24 hours" {
            $headers = @{ Authorization = "Bearer $script:SiemToken" }
            $body = @{
                query = "search index=entra category=AuditLogs targetResources.type=AgentIdentity earliest=-24h | stats count"
            } | ConvertTo-Json
            $resp = Invoke-RestMethod -Method Post -Uri "$script:SiemBase/search" -Headers $headers -Body $body -ContentType 'application/json'
            $resp.results.count | Should -BeGreaterThan 0
        }
        It "the SIEM index housing entra logs has retention ≥ 2190 days (6 years)" {
            $headers = @{ Authorization = "Bearer $script:SiemToken" }
            $resp = Invoke-RestMethod -Method Get -Uri "$script:SiemBase/indexes/entra" -Headers $headers
            [int]$resp.retentionDays | Should -BeGreaterOrEqual 2190
        }
        It "the SIEM index is configured WORM / immutable" {
            $headers = @{ Authorization = "Bearer $script:SiemToken" }
            $resp = Invoke-RestMethod -Method Get -Uri "$script:SiemBase/indexes/entra" -Headers $headers
            $resp.immutable | Should -BeTrue
        }
    }
}
```

### 7.4 Sample passing record

```json
{
  "control_id": "2.26",
  "namespace": "SIEM",
  "criterion": "C2.26-8",
  "zone": "all",
  "subject_id": "diag-setting-AgentID-To-SIEM",
  "subject_type": "diagnostic_setting",
  "status": "PASS",
  "assertion": "Entra exports AuditLogs to SIEM and SIEM retains ≥6y immutable",
  "observed_value": {
    "diagnostic_setting_name": "AgentID-To-SIEM",
    "categories": ["AuditLogs","SignInLogs","IdentityRiskEvents"],
    "destination": "eventhub://contoso-secops-eh/entra",
    "siem_index": "entra",
    "siem_retention_days": 2557,
    "siem_immutable": true,
    "events_last_24h": 142
  },
  "regulator_mappings": ["FINRA-4511","SEC-17a-4","SOX-404","GLBA-501b","OCC-2011-12"],
  "evidence_artifacts": ["siem-forwarding-AGT226-20260415-093012-a1b2c3d4.json"],
  "schema_version": "1.0"
}
```

### 7.5 Sample failing record

```json
{
  "control_id": "2.26",
  "namespace": "SIEM",
  "criterion": "C2.26-8",
  "status": "FAIL",
  "assertion": "SIEM index must retain ≥2190 days",
  "observed_value": {
    "siem_index": "entra",
    "siem_retention_days": 365,
    "siem_immutable": false
  },
  "remediation_ref": "TRG-SIEM-01",
  "regulator_mappings": ["FINRA-4511","SEC-17a-4"],
  "schema_version": "1.0"
}
```

`TRG-SIEM-01` (§11.8): engage SecOps to extend retention; raise immutable-storage variance with the Compliance Officer; consider compensating cold-storage export to Azure Storage with WORM lock pending remediation.

### 7.6 Examiner artifact

| Artifact | Filename | Retention |
|---|---|---|
| Diagnostic Setting snapshot | `siem-diagsettings-<runId>.json` | 6 years |
| SIEM ingestion proof (search response) | `siem-ingestion-<runId>.json` | 6 years |
| SIEM index policy snapshot | `siem-index-policy-<runId>.json` | 6 years |

### 7.7 Zone thresholds

| Zone | PASS | WARN | FAIL |
|---|---|---|---|
| All zones | Diagnostic Setting active AND SIEM events flowing AND retention ≥6y AND immutable | retention 5y–6y, with documented remediation plan | retention < 5y OR no events flowing OR not immutable |

### 7.8 Regulator mapping

| Test | FINRA 4511 | SEC 17a-4 | SOX §404 | GLBA §501(b) |
|---|---|---|---|---|
| Diag setting active | ✓ | ✓ | ✓ logging control | ✓ |
| SIEM ingestion | ✓ | ✓ | ✓ | ✓ |
| 6y retention | ✓ (6y minimum) | ✓ (3y for first 2y readily accessible; this exceeds) | ✓ | ✓ |
| Immutability | — | ✓ WORM requirement | ✓ | ✓ tamper-evident |

---

## §8 SOV — Sovereign Cloud Compensating Control

### 8.1 Why this section exists

At the time of this playbook's last UI verification (April 2026), the **Microsoft Entra Agent ID feature is not generally available in sovereign cloud environments** (Microsoft 365 GCC, GCC High, and DoD). Tenants in those clouds therefore cannot satisfy criteria C2.26-1 through C2.26-7 using Entra-native tooling.

Rather than treating this as an automatic failure — which would understate examiner-defensible posture for organizations that legitimately operate in sovereign clouds for jurisdictional reasons — Control 2.26 §6 prescribes a **manual compensating attestation**, executed quarterly by the AI Governance Lead and counter-signed by the Compliance Officer. This section documents the test that verifies the attestation has been executed, signed, and retained.

### 8.2 Compensating control flow

For sovereign tenants, every Pester `Describe` block in §2–§7 and §9 short-circuits to `SKIPPED` (see §0.4). The SOV namespace is the **only** namespace that runs to completion in a sovereign tenant, and it operates against artifacts produced by the manual quarterly attestation rather than against live Graph endpoints.

The manual attestation packet (`sov-attestation-<quarterLabel>.json`) is produced by the runbook in §13.4 and includes:

- A statement of the agent identity inventory (collected manually from agent owner records since live `/agents` Graph enumeration is unavailable).
- A per-agent sponsor mapping (collected from internal CMDB / IGA system that **does** operate in the sovereign cloud).
- A per-agent access scope mapping (collected from group membership reports in the sovereign tenant).
- Attestation that no agent identity is operating outside its assigned sponsor's accountability.
- Sponsor and Compliance Officer digital signatures (PKCS#7 over canonical JSON).

### 8.3 Pester suite

```powershell
Describe "AGT226-SOV" -Tag 'C2.26','SOV' {

    BeforeAll {
        $script:Sov = Test-Agt226SovereignTenant
        $script:Quarter = Get-PreviousQuarterBoundary
        $script:AttestationPath = Join-Path $env:AGT226_EVIDENCE_ROOT `
            "sov-attestation-$($script:Quarter.label).json"
        $script:SignaturePath   = "$script:AttestationPath.sig"
    }

    Context "Applicability" {
        It "this suite runs only in sovereign clouds" -Skip:(-not $script:Sov.is_sovereign) {
            $script:Sov.cloud | Should -BeIn @('GCC','GCCH','DoD')
        }
    }

    Context "Manual attestation packet exists" -Skip:(-not $script:Sov.is_sovereign) {
        It "the attestation file for the prior quarter is present" {
            Test-Path $script:AttestationPath | Should -BeTrue
        }
        It "the attestation file is digitally signed" {
            Test-Path $script:SignaturePath | Should -BeTrue
            $verify = Invoke-Pkcs7Verify -DataPath $script:AttestationPath -SignaturePath $script:SignaturePath
            $verify.IsValid | Should -BeTrue
        }
        It "the attestation lists at least one named sponsor and contains the manual sponsor map" {
            $att = Get-Content $script:AttestationPath -Raw | ConvertFrom-Json
            $att.sponsors.Count | Should -BeGreaterThan 0
            $att.sponsors[0].sponsor_upn | Should -Not -BeNullOrEmpty
            $att.agent_inventory.Count | Should -BeGreaterThan 0
        }
        It "the attestation carries both Sponsor and Compliance Officer signatures" {
            $att = Get-Content $script:AttestationPath -Raw | ConvertFrom-Json
            $att.signatures.sponsor             | Should -Not -BeNullOrEmpty
            $att.signatures.compliance_officer  | Should -Not -BeNullOrEmpty
            $att.signatures.compliance_officer.signed_at | Should -Not -BeNullOrEmpty
        }
        It "attestation date is within the prior quarter window" {
            $att = Get-Content $script:AttestationPath -Raw | ConvertFrom-Json
            $signed = [datetime]$att.signatures.compliance_officer.signed_at
            $signed | Should -BeGreaterOrEqual $script:Quarter.start
            $signed | Should -BeLessOrEqual $script:Quarter.end.AddDays(15) # 15-day grace for sign-off
        }
    }
}
```

### 8.4 Sample passing record

```json
{
  "control_id": "2.26",
  "namespace": "SOV",
  "criterion": "C2.26-1..7 (compensating)",
  "zone": "all",
  "subject_id": "sov-attestation-Q1-2026",
  "subject_type": "manual_attestation",
  "status": "PASS",
  "assertion": "Sovereign quarterly attestation present, signed by Sponsor and Compliance Officer",
  "observed_value": {
    "cloud": "GCCH",
    "quarter_label": "Q1-2026",
    "agent_inventory_count": 23,
    "sponsor_count": 11,
    "sponsor_signed_at": "2026-04-08T14:00:00Z",
    "compliance_officer_signed_at": "2026-04-09T10:30:00Z",
    "pkcs7_signature_valid": true
  },
  "regulator_mappings": ["FINRA-3110","SOX-404","OCC-2011-12","GLBA-501b"],
  "evidence_artifacts": ["sov-attestation-Q1-2026.json","sov-attestation-Q1-2026.json.sig"],
  "schema_version": "1.0"
}
```

### 8.5 Sample failing record

```json
{
  "control_id": "2.26",
  "namespace": "SOV",
  "criterion": "C2.26-1..7 (compensating)",
  "status": "FAIL",
  "assertion": "Sovereign quarterly attestation must be present and dual-signed",
  "observed_value": {
    "attestation_present": false,
    "last_attestation_label": "Q4-2025",
    "days_since_last_attestation": 121
  },
  "remediation_ref": "TRG-SOV-02",
  "regulator_mappings": ["FINRA-3110","OCC-2011-12"],
  "schema_version": "1.0"
}
```

`TRG-SOV-02` (§11.9): immediately initiate the quarterly attestation runbook (§13.4); declare the lapse to the Compliance Officer and document for board reporting; do **not** mark prior-quarter SOV as PASS retroactively.

### 8.6 Examiner artifact

| Artifact | Filename | Retention |
|---|---|---|
| Quarterly attestation packet | `sov-attestation-<quarterLabel>.json` | 7 years |
| PKCS#7 detached signature | `sov-attestation-<quarterLabel>.json.sig` | 7 years |
| Manual agent inventory CSV | `sov-inventory-<quarterLabel>.csv` | 6 years |

### 8.7 Zone thresholds

| Zone | PASS | WARN | FAIL |
|---|---|---|---|
| All zones (sovereign tenants only) | Quarterly attestation present, dual-signed, within 15-day grace of quarter close | Attestation 16–45 days late, with documented justification | Attestation > 45 days late or signature invalid |

### 8.8 Regulator mapping

| Test | FINRA 3110 | SOX §404 | OCC Bulletin 2026-13 (formerly OCC 2011-12) | FFIEC IS |
|---|---|---|---|---|
| Manual attestation cadence | ✓ supervision under sovereign constraints | ✓ compensating control documented | ✓ model owner accountability preserved | ✓ access management compensating |
| Dual signature | ✓ supervisor + compliance | ✓ segregation of duties | ✓ challenger | ✓ separation |

---

## §9 PREVIEW — Agent ID Licensing & Blade Operability Verification

!!! info "Namespace name preserved for backward-compatibility"
    Pre-GA this namespace evidenced Microsoft Frontier program enrollment + Copilot licensing. Post-GA (May 2026) it evidences **Microsoft Agent 365 / Microsoft 365 E7 license assignment** plus **Agent ID API surface operability**. The `PREVIEW` namespace name, the `TRG-PREVIEW-01` runbook ID, and the `frontier_probe_status` field name are retained to keep evidence-pack schemas backward-compatible across the GA cutover. **Field semantics have changed** — see prose below.

### 9.1 Criterion mapping

This namespace evidences **C2.26-1**: the Entra Agent ID feature is enabled in the tenant. Post-GA, enablement requires **two independent gates** to be true at the time of verification:

1. The tenant holds at least one **Microsoft Agent 365** or **Microsoft 365 E7** SKU assignment (the "license gate" already executed in PRE-05). Pre-GA this gate looked for a `Microsoft_365_Copilot*` SKU; post-GA the relevant SKUs are Agent 365 (standalone) or M365 E7 (suite). Verify exact SKU part numbers in your tenant via `Get-MgSubscribedSku` before adopting the patterns below.
2. The Agent ID API surface is reachable to the calling principal (the "operability gate" already executed in PRE-06).

In addition, the **Agent identities** blade must be reachable in the Microsoft Entra admin center. Because the blade itself does not have a stable Graph API for "blade rendering", the Pester test for blade visibility is replaced by an **API-surface probe**: if `/beta/agents` returns HTTP 200 with a JSON body (even an empty collection), the blade is considered present and operable.

### 9.2 Pre-conditions

- PRE-05 (Agent 365 / M365 E7 license) and PRE-06 (Agent ID API operability) returned `PASS`.
- Graph context holds `AgentIdentity.Read.All`.
- Probe URL: `https://graph.microsoft.com/beta/agents?$top=1` for Commercial; sovereign equivalents per the [shared sovereign endpoint table](../../_shared/powershell-baseline.md#3-sovereign-cloud-endpoints-gcc-gcc-high-dod) (the SOV namespace handles the sovereign skip path; this section operates in Commercial only).

### 9.3 Pester suite

```powershell
Describe "AGT226-PREVIEW" -Tag 'C2.26','PREVIEW' {

    BeforeAll {
        # Post-GA: prefer Agent 365 / M365 E7 SKUs. Verify SkuPartNumber values
        # in your tenant via Get-MgSubscribedSku before relying on these patterns.
        $script:LicenseSkus = Get-MgSubscribedSku -All |
            Where-Object {
                $_.SkuPartNumber -like 'Microsoft_Agent_365*' -or
                $_.SkuPartNumber -like 'M365_E7*'             -or
                # transitional fallback for tenants still on pre-GA Copilot SKUs
                $_.SkuPartNumber -like 'Microsoft_365_Copilot*'
            }
        $script:Probe = $null
        try {
            $script:Probe = Invoke-MgGraphRequest -Method GET `
                -Uri 'https://graph.microsoft.com/beta/agents?$top=1' -ErrorAction Stop
        } catch {
            $script:ProbeError = $_.Exception.Message
        }
    }

    Context "License gate (C2.26-1a)" -Skip:$script:IsSovereign {
        It "tenant holds at least one Agent 365 / M365 E7 (or transitional Copilot) SKU" {
            $script:LicenseSkus.Count | Should -BeGreaterThan 0
        }
        It "at least one license is assigned (consumedUnits > 0)" {
            ($script:LicenseSkus | Measure-Object -Property ConsumedUnits -Sum).Sum |
                Should -BeGreaterThan 0
        }
    }

    Context "Agent ID API operability gate (C2.26-1b)" -Skip:$script:IsSovereign {
        It "the /beta/agents endpoint returns HTTP 200 (Agent ID surface reachable)" {
            $script:Probe | Should -Not -BeNullOrEmpty
            $script:Probe.value | Should -BeOfType [System.Object[]]
        }
        It "the response shape contains the expected agent-identity properties when populated" {
            if ($script:Probe.value.Count -gt 0) {
                $first = $script:Probe.value[0]
                $first.id            | Should -Not -BeNullOrEmpty
                $first.displayName   | Should -Not -BeNullOrEmpty
                # sponsor field key may vary by schema generation; tolerate both
                ($first.sponsorObjectId -or $first.sponsorId) | Should -BeTrue
            }
        }
    }

    Context "Blade operability proxy (C2.26-1c)" -Skip:$script:IsSovereign {
        It "blade probe did not return 403 (RBAC or license-coverage misconfiguration)" {
            $script:ProbeError | Should -NotMatch '403'
        }
        It "blade probe did not return 404 (Agent ID surface not reachable to caller)" {
            $script:ProbeError | Should -NotMatch '404'
        }
    }
}
```

### 9.4 Sample passing record

```json
{
  "control_id": "2.26",
  "namespace": "PREVIEW",
  "criterion": "C2.26-1",
  "zone": "all",
  "subject_id": "tenant-feature-state",
  "subject_type": "feature_enablement",
  "status": "PASS",
  "assertion": "Agent 365 / M365 E7 licensed AND Agent ID API reachable",
  "observed_value": {
    "license_skus": ["Microsoft_Agent_365"],
    "license_consumed_units": 1500,
    "frontier_probe_status": 200,
    "agents_endpoint_response": "ok",
    "agents_count_in_probe": 23
  },
  "regulator_mappings": ["SOX-404","OCC-2011-12"],
  "evidence_artifacts": ["preview-state-AGT226-20260415-093012-a1b2c3d4.json"],
  "schema_version": "1.0"
}
```

> **Field-name carryover.** `frontier_probe_status` is retained as the field key for the HTTP status returned by the `/beta/agents` probe. The field name is preserved to keep examiner pipelines that already parse this key working across the GA cutover. Post-GA, a `200` indicates the Agent ID surface is reachable; a `403/404` indicates a license-coverage or RBAC gap, **not** a Frontier-enrollment gap.

### 9.5 Sample failing record

```json
{
  "control_id": "2.26",
  "namespace": "PREVIEW",
  "criterion": "C2.26-1",
  "status": "FAIL",
  "assertion": "Agent ID operability gate must return HTTP 200 from /beta/agents",
  "observed_value": {
    "license_skus": ["Microsoft_Agent_365"],
    "frontier_probe_status": 404,
    "probe_error": "Resource not found: /beta/agents"
  },
  "remediation_ref": "TRG-PREVIEW-01",
  "regulator_mappings": ["SOX-404","OCC-2011-12"],
  "schema_version": "1.0"
}
```

`TRG-PREVIEW-01` (§11.10): confirm Microsoft Agent 365 / M365 E7 license is assigned to the calling principal and the tenant has at least one consumed unit; verify the calling principal holds the required RBAC role (Entra Agent ID Admin or AI Administrator); halt deployment of any new Z2/Z3 agents while the gap persists; downgrade any Z2/Z3 agents created during the gap to Z1 and re-evaluate when access is restored. If license + RBAC are confirmed and the surface is still unreachable, raise a Microsoft support case via standard support channels.

### 9.6 Examiner artifact

| Artifact | Filename | Retention |
|---|---|---|
| Feature-state snapshot | `preview-state-<runId>.json` | 6 years |
| Copilot SKU list | `preview-skus-<runId>.json` | 6 years |
| Agent ID API probe response (raw) | `preview-agent-id-api-probe-<runId>.json` | 6 years |

### 9.7 Zone thresholds

| Zone | PASS | WARN | FAIL |
|---|---|---|---|
| All zones | Both gates PASS AND probe returns 200 | one gate PASS, other PASS within prior 7 days but transient probe error | either gate FAIL or probe returns 403/404 |

### 9.8 Regulator mapping

| Test | SOX §404 | OCC Bulletin 2026-13 (formerly OCC 2011-12) |
|---|---|---|
| License gate | ✓ control prerequisite | ✓ tooling licensed for model use |
| Agent ID API surface gate | ✓ feature in known state | ✓ change-managed feature enablement |
| Blade probe | ✓ control operable | ✓ |

---

## §10 Evidence Pack Assembly, Signing & Retention

### 10.1 Purpose

Each Pester run produces dozens of individual evidence records. The evidence pack consolidates them into a single, signed, hash-chained artifact that an examiner can ingest as one unit.

The companion function in [PowerShell Setup §6](powershell-setup.md), `Export-Control226EvidencePackage`, produces the pack. This section documents the **schema** the pack must conform to, the **hash chain** that links the records, and the **retention** policy applied at the storage layer.

### 10.2 Pack structure

```
evidence-pack-AGT226-20260415-093012-a1b2c3d4/
├── manifest.json                           # Top-level descriptor (schema below)
├── attestation.json                        # Signature chain
├── records/
│   ├── 0001-PREVIEW.json
│   ├── 0002-SPONSOR-zone1.json
│   ├── 0003-SPONSOR-zone2.json
│   ├── ... (one file per evidence record)
│   └── NNNN-SOV.json
├── pester/
│   ├── pester-PREVIEW.xml
│   ├── pester-SPONSOR.xml
│   └── ... (JUnit XML per namespace)
├── snapshots/
│   ├── sponsor-snapshot-<runId>.json
│   ├── accesspkg-snapshot-<runId>.json
│   ├── lifecycle-runs-<runId>.json
│   ├── review-decisions-<quarterLabel>.json
│   ├── expiry-snapshot-<runId>.json
│   └── siem-forwarding-<runId>.json
└── README.md                               # Plain-text examiner orientation
```

### 10.3 `manifest.json` schema

```json
{
  "pack_version": "1.0",
  "control_id": "2.26",
  "run_id": "AGT226-20260415-093012-a1b2c3d4",
  "tenant_id": "11111111-2222-3333-4444-555555555555",
  "tenant_display_name": "Contoso Bank, N.A.",
  "cloud": "Commercial",
  "produced_at": "2026-04-15T09:42:18Z",
  "operator_upn": "agt226-runner@contoso.com",
  "namespaces_executed": ["PREVIEW","SPONSOR","ACCESSPKG","LIFECYCLE","REVIEW","EXPIRY","SIEM"],
  "namespaces_skipped": [],
  "record_count": 187,
  "pass_count": 184,
  "fail_count": 2,
  "warn_count": 1,
  "skipped_count": 0,
  "criteria_coverage": {
    "C2.26-1": "PASS",
    "C2.26-2": "PASS",
    "C2.26-3": "PASS",
    "C2.26-4": "PASS",
    "C2.26-5": "FAIL",
    "C2.26-6": "PASS",
    "C2.26-7": "FAIL",
    "C2.26-8": "WARN"
  },
  "merkle_root_sha256": "9c1b...e7af",
  "signing_certificate_thumbprint": "AB12...EF34"
}
```

### 10.4 Hash chain (`attestation.json`)

Each record file is hashed (SHA-256 over its UTF-8 byte content). The hashes are concatenated in lexical filename order and hashed again to form the **Merkle root**. The Merkle root is then signed by the operator's code-signing certificate. The chain is committed to `attestation.json`:

```json
{
  "algorithm": "SHA-256",
  "leaves": [
    { "filename": "records/0001-PREVIEW.json",          "sha256": "a1b2..." },
    { "filename": "records/0002-SPONSOR-zone1.json",    "sha256": "c3d4..." },
    { "filename": "records/0003-SPONSOR-zone2.json",    "sha256": "e5f6..." }
  ],
  "merkle_root_sha256": "9c1b...e7af",
  "signatures": [
    {
      "role": "ai_governance_lead",
      "signer_upn": "agt226-runner@contoso.com",
      "certificate_thumbprint": "AB12...EF34",
      "signed_at": "2026-04-15T09:42:30Z",
      "signature_pkcs7_b64": "MIIE...=="
    },
    {
      "role": "compliance_officer",
      "signer_upn": "compliance.officer@contoso.com",
      "certificate_thumbprint": "CD56...7890",
      "signed_at": "2026-04-15T16:05:11Z",
      "signature_pkcs7_b64": "MIIE...=="
    }
  ]
}
```

A second signature from the Compliance Officer is appended within 24 hours of pack production. Packs without a counter-signature are considered **draft** and may not be cited as primary evidence in an examination.

### 10.5 Schema validation

```powershell
function Test-Agt226EvidenceSchema {
    [CmdletBinding()]
    param([Parameter(Mandatory)][string]$RecordPath)

    $required = @(
        'control_id','run_id','run_timestamp','tenant_id','cloud',
        'namespace','criterion','zone','subject_id','subject_type',
        'status','assertion','observed_value','expected_value',
        'evidence_artifacts','regulator_mappings','schema_version'
    )

    $rec = Get-Content $RecordPath -Raw | ConvertFrom-Json
    $missing = $required | Where-Object { -not $rec.PSObject.Properties.Name.Contains($_) }

    [pscustomobject]@{
        path     = $RecordPath
        valid    = ($missing.Count -eq 0)
        missing  = $missing
    }
}
```

The pack assembler MUST refuse to publish a pack containing any record that fails schema validation.

### 10.6 Retention & storage

<a id="storage-immutability-check"></a>

| Layer | Where | Retention | Immutability |
|---|---|---|---|
| Hot | Azure Blob Storage container `agt226-evidence-hot` | 90 days | Versioning + soft delete |
| Warm | Azure Blob Storage container `agt226-evidence-warm` (Cool tier) | 1 year | Versioning + legal hold during audits |
| Cold | Azure Blob Storage container `agt226-evidence-cold` (Archive tier) with **immutability policy locked** | 6 years from pack date (FINRA 4511); 7 years for SOV packs | Locked time-based retention policy |
| Mirror | SIEM index `agt226-evidence` (parsed manifest + criteria coverage only) | 6 years | Immutable index |

The lifecycle policy that promotes packs from Hot → Warm → Cold is defined in [PowerShell Setup §6.3](powershell-setup.md). The immutability policy is locked at the storage account level and cannot be removed during the retention window — this is the property that satisfies SEC Rule 17a-4(f) WORM expectations.

### 10.7 Examiner-friendly README

Every pack ships with a `README.md` written for a non-technical examiner audience. The README:

1. Names the control (`2.26 — Entra Agent ID Identity Governance`).
2. States the run window (e.g., "Evidence collected for the 24-hour window ending 2026-04-15 09:30 UTC").
3. Lists the eight Verification Criteria and the namespace each maps to.
4. Provides a quick-glance table of `criteria_coverage` from `manifest.json`.
5. Points the examiner to the relevant `records/*.json` and `snapshots/*.json` files for any FAIL.
6. Includes the operator's name and contact email.

---

## §11 Failure Triage Matrix

### 11.1 Severity bands & escalation SLAs

| Severity | Meaning | Page on-call within | Containment SLA | Resolution SLA | Examples |
|---|---|---|---|---|---|
| Critical | Z3 agent operating without sponsor, perpetual Z3 grant, stale-grant > 24h | 15 minutes | 1 hour (suspend) | 24 hours | TRG-SPONSOR-01 (Z3 sponsor null), TRG-EXPIRY-01 (Z3 stale), TRG-PREVIEW-01 |
| High | Z2 agent without sponsor, lifecycle workflow failure, SIEM retention < 5y, missing quarterly review | 1 hour | 4 hours | 72 hours | TRG-SPONSOR-02 (Z2), TRG-LIFECYCLE-01, TRG-SIEM-01, TRG-REVIEW-01 |
| Medium | Z2 expiry > 24h–72h late, package expiry 366–400 days, manager declines transfer (escalation) | 4 hours | 24 hours | 7 days | TRG-EXPIRY-02, TRG-ACCESSPKG-01, TRG-LIFECYCLE-02 |
| Low | Z1 sponsor != creator (data hygiene), justification < 50 chars, single transient probe error | 1 business day | 5 business days | 30 days | TRG-SPONSOR-03, TRG-EXPIRY-03 |

### 11.2 TRG-SPONSOR-01 — Z3 sponsor null or inactive

- **Trigger:** §2 Pester suite reports a Z3 agent with `sponsorObjectId == null` or `sponsor_active == false`.
- **Containment:** within 4 hours, suspend the agent identity (set `accountEnabled = false` via `Update-MgAgent`); notify Compliance Officer.
- **Remediation:** identify successor sponsor via the agent owner team's escalation list; run `Set-AgentSponsorBulk -AgentId <id> -SponsorUpn <new>` from the sister playbook; re-enable agent only after both primary and backup sponsor are recorded.
- **Evidence to attach:** the failing record, the suspension audit-event ID, the new sponsor mapping, the Compliance Officer acknowledgement.
- **Cross-reference:** [Troubleshooting §3.1](troubleshooting.md).

### 11.3 TRG-ACCESSPKG-02 — Z3 direct (non-package) assignment detected

- **Trigger:** §3 reports any direct group/role assignment on a Z3 agent.
- **Containment:** remove the direct assignment within 24 hours via `Remove-MgGroupMemberByRef` or `Remove-MgRoleManagementDirectoryRoleAssignment`.
- **Remediation:** identify the equivalent access package and request assignment via the package; document the variance with root-cause (most commonly: emergency access not subsequently rolled into a package).
- **Cross-reference:** [Troubleshooting §3.2](troubleshooting.md).

### 11.4 TRG-LIFECYCLE-01 — Departure not processed

- **Trigger:** §4 reports a departed sponsor whose agents still point at the departed user.
- **Containment:** manually invoke `Set-AgentSponsorBulk` with the departed user's manager as the new sponsor.
- **Remediation:** open a problem ticket against the lifecycle workflow; capture the workflow run failure log; if the workflow consistently fails, raise a Microsoft support case via standard support channels.

### 11.5 TRG-LIFECYCLE-02 — Manager declines transfer (escalation)

- **Trigger:** §4 workflow run completes with `processing_status == 'completedWithErrors'` and the error indicates the manager declined to accept ownership.
- **Action:** activate the **suspension** path: set agent `accountEnabled = false`; assign temporary stewardship to the AI Governance Lead; place the agent in a 30-day reassignment hold; if no permanent owner is named within 30 days, retire the agent per Control 3.6.
- **This is the ONE case where suspension is the correct outcome.** The Pester tests do not preemptively check for suspension; they only check for the manager-transfer outcome. Suspension only enters the picture when the manager-transfer path fails.

### 11.6 TRG-REVIEW-01 — Quarterly review incomplete

- **Trigger:** §5 reports an in-scope campaign with `status != 'Completed'` at quarter close, or pending decisions without auto-applied default.
- **Containment:** force-apply the configured default decision (`Deny`) via `Update-MgIdentityGovernanceAccessReviewDefinitionInstance`; this removes access from any reviewer-skipped subject.
- **Remediation:** investigate why the campaign did not complete (most commonly: reviewer absent without a configured fallback reviewer); reconfigure fallback reviewers; document the lapse for the next §13 packet and for the next 1.2 sponsor attestation cycle.

### 11.7 TRG-EXPIRY-01 — Stale grant (expired but still granting access)

- **Trigger:** §6 reports a Z3 assignment past its `expiredDateTime` whose underlying group/role membership still resolves.
- **Containment:** within 1 hour, force-remove via `Remove-MgEntitlementManagementAssignmentRequest` or, failing that, direct group/role removal.
- **Remediation:** raise a Critical incident; invoke root-cause analysis (e.g., entitlement management background job stalled, custom workflow blocking removal); add to the next §13 packet for board reporting.

### 11.8 TRG-SIEM-01 — SIEM retention < 6 years or not immutable

- **Trigger:** §7 reports `siem_retention_days < 2190` or `siem_immutable == false`.
- **Containment:** as a temporary compensating control, configure an Azure Storage account with an immutable, time-based retention policy of 6 years and export Entra Diagnostic Settings to that account in parallel with the SIEM.
- **Remediation:** engage SecOps to extend SIEM retention; raise the variance with the Compliance Officer; document the temporary parallel export and decommission it once SIEM is compliant.

### 11.9 TRG-SOV-02 — Sovereign attestation missing or late

- **Trigger:** §8 reports the prior-quarter attestation absent or > 45 days late.
- **Containment:** initiate the §13.4 quarterly attestation runbook immediately.
- **Remediation:** declare the lapse; the prior quarter cannot be retroactively passed; document for board reporting.

### 11.10 TRG-PREVIEW-01 — Agent ID licensing or operability gate FAIL

- **Trigger:** §9 reports `frontier_probe_status` of 403/404, or no Agent 365 / M365 E7 license consumed.
- **Containment:** halt deployment of any new Z2/Z3 agents.
- **Remediation:** confirm Microsoft Agent 365 or Microsoft 365 E7 license is assigned and consumed; verify the calling principal holds the Entra Agent ID Admin or AI Administrator role; if license + RBAC are confirmed and the surface is still unreachable, raise a Microsoft support case via standard support channels. Downgrade any Z2/Z3 agents created during the gap to Z1 and re-evaluate when access is restored.

### 11.11 Generic "Low" data-hygiene findings

Findings classified Low (e.g., justification text under 50 chars, transient probe errors, single Z1 sponsor mismatch) accumulate in a single `low-findings-<runId>.csv` artifact. They are reviewed monthly by the AI Governance Lead and any pattern (e.g., consistent under-50-char justifications from one team) is escalated to a training intervention rather than an incident.

---

## §12 Cross-Control Verification Dependencies

Control 2.26 does not stand alone. Two adjacent controls produce or consume data that this verification playbook depends on or feeds:

### 12.1 Upstream — Control 1.2 Sponsor Attestation

The SPONSOR namespace (§2) takes as input the **golden agent list** maintained by Control 1.2. Specifically:

- `agents-expected.csv` — the authoritative list of agents that *should* exist in the tenant, with their assigned sponsor and zone classification, signed by the AI Governance Lead during the most recent 1.2 attestation cycle.
- The 1.2 attestation packet's hash chain is referenced in 2.26's `manifest.json` as `upstream_dependencies[0]`, providing a verifiable link from a 2.26 evidence pack back to the 1.2 packet that authored its expectations.

If the 1.2 attestation is overdue (> 30 days), the SPONSOR namespace emits a `WARN`-level record (`status: WARN`, `assertion: "Upstream 1.2 attestation overdue; sponsor expectations may be stale"`) for every Z2/Z3 agent. This makes a 1.2 attestation lapse visible in 2.26's evidence trail rather than silently degrading 2.26's signal.

| 2.26 dependency | Source artifact in 1.2 | Failure if missing |
|---|---|---|
| Expected agent inventory | `1.2/sponsor-attestation-<quarterLabel>.json` → `agents[]` | SPONSOR namespace WARN; manual reconciliation required |
| Sponsor signature on each agent | Same → `agents[].sponsor_signature` | TRG-SPONSOR-04 (data hygiene) |
| Quarter-aligned attestation date | Same → `attestation_date` | If > 90 days old, WARN; if > 180 days, FAIL |

### 12.2 Downstream — Control 3.6 Orphan Agent Detection

The LIFECYCLE namespace (§4) produces a `lifecycle-runs-<runId>.json` artifact that lists every workflow run, its outcome, and the agents affected. Control 3.6's orphan-detection job consumes this artifact to:

- Identify agents whose sponsor was successfully transferred to a manager but whose manager has subsequently also departed (a "double-departure orphan").
- Identify agents flagged as `completedWithErrors` in 2.26 for which a 30-day suspension hold has expired without reassignment (a "permanent orphan").

The 3.6 control's orphan registry, in turn, feeds back into the next 2.26 SPONSOR run as an input dimension: an agent listed in the 3.6 orphan registry is flagged in §2's evidence record with `observed_value.orphan_registry_match: true`.

| 2.26 output | 3.6 consumer behavior | 2.26-side test |
|---|---|---|
| `lifecycle-runs-<runId>.json` | Orphan detector parses for `completedWithErrors` runs | None (3.6 owns its own verification) |
| `sponsor-failures-<runId>.json` | Orphan detector promotes all entries to its registry | None |
| `criteria_coverage.C2.26-5 == FAIL` | Triggers a 3.6 sweep within 4 hours | §11.4 includes a notification step to the 3.6 owner |

### 12.3 Cross-pack reconciliation test

A weekly out-of-band Pester run executes `Test-Agt226-CrossControlReconciliation`, which ensures:

```powershell
Describe "AGT226-XCONTROL" -Tag 'C2.26','XCTRL' {

    It "every agent in the most recent 1.2 attestation appears in the most recent 2.26 SPONSOR run" {
        $expected = (Get-Latest12Attestation).agents.id | Sort-Object
        $observed = (Get-Latest226SponsorPack).records |
            Where-Object namespace -eq 'SPONSOR' |
            ForEach-Object subject_id | Sort-Object -Unique
        $missing = Compare-Object $expected $observed | Where-Object SideIndicator -eq '<='
        $missing.Count | Should -Be 0
    }

    It "every Critical FAIL in the most recent 2.26 LIFECYCLE run is reflected in the 3.6 orphan registry within 4 hours" {
        $criticalFails = (Get-Latest226Pack).records |
            Where-Object { $_.namespace -eq 'LIFECYCLE' -and $_.status -eq 'FAIL' }
        foreach ($f in $criticalFails) {
            $orphan = Get-36OrphanRegistry | Where-Object subject_id -eq $f.subject_id
            $orphan | Should -Not -BeNullOrEmpty
            ((Get-Date) - [datetime]$orphan.added_at).TotalHours | Should -BeLessOrEqual 4
        }
    }
}
```

The reconciliation evidence record is itself signed and stored alongside the 2.26 evidence pack in a sub-folder `xcontrol/`.

---

## §13 Quarterly Attestation Runbook for the AI Governance Lead

### 13.1 Purpose

The quarterly attestation is the human gate that turns a stack of automated evidence packs into a single, signed, examiner-presentable assertion: *"As AI Governance Lead, I have reviewed the prior quarter of Control 2.26 evidence and certify that all eight Verification Criteria were met, or where they were not, that the documented remediation completed within SLA."*

This runbook is executed by the AI Governance Lead **within 15 calendar days of the quarter's close** and counter-signed by the Compliance Officer **within 30 days**.

### 13.2 Inputs

The Lead assembles, in order:

1. The 12 weekly evidence packs produced over the prior quarter (one per week from the standing Pester schedule).
2. The 90 daily SPONSOR/EXPIRY snapshots (light-weight subsets of the full pack).
3. The prior quarter's REVIEW campaign decision exports.
4. The most recent 1.2 sponsor attestation (upstream dependency per §12.1).
5. The 3.6 orphan registry delta over the quarter (downstream consumer per §12.2).
6. Any incident tickets with severity Critical or High that traced back to a §11 triage entry.

### 13.3 Procedure (Commercial cloud)

| Step | Action | Owner | Output |
|---|---|---|---|
| 1 | Run `Get-AgentGovernanceSummary -Quarter $prior` from sister playbook | AI Governance Lead | `summary-<quarterLabel>.json` |
| 2 | Verify `criteria_coverage` shows all 8 criteria as PASS or PASS-with-remediated-FAIL | AI Governance Lead | Pass/Fail decision |
| 3 | For each remediated FAIL, attach the closing ticket (resolution evidence) | AI Governance Lead | `remediations-<quarterLabel>/` folder |
| 4 | Compute SHA-256 over `summary-<quarterLabel>.json` + remediation folder canonical JSON | AI Governance Lead | Attestation hash |
| 5 | Sign attestation packet with code-signing certificate | AI Governance Lead | `quarterly-attestation-<quarterLabel>.json.sig` |
| 6 | Forward to Compliance Officer for counter-signature within 30 days | AI Governance Lead → Compliance Officer | Counter-signature appended |
| 7 | Promote signed packet to Cold storage with 7-year locked immutability | Compliance Officer | Immutable-locked blob URL |
| 8 | File the packet URL with the Board Risk Committee secretariat | Compliance Officer | Board minute reference |

### 13.4 Procedure (sovereign cloud variant)

Sovereign tenants follow steps 1–8 above with these substitutions:

- Step 1 source: manual agent inventory + sponsor map gathered from the sovereign-resident IGA / CMDB rather than from `Get-AgentGovernanceSummary`.
- Step 2 evaluation: per-criterion attestation that the compensating manual control was performed (the SOV namespace evidence pack from §8 satisfies this).
- Step 5: signature is over the **manual** attestation packet structured per §8.2 rather than the automated summary.
- Step 7: 7-year retention (one year more than commercial), reflecting the higher reliance on the manual attestation as primary evidence.

### 13.5 Quarterly attestation packet schema

```json
{
  "schema_version": "1.0",
  "control_id": "2.26",
  "quarter_label": "Q1-2026",
  "quarter_start": "2026-01-01T00:00:00Z",
  "quarter_end":   "2026-03-31T23:59:59Z",
  "tenant_id": "11111111-2222-3333-4444-555555555555",
  "cloud": "Commercial",
  "criteria_attestation": {
    "C2.26-1": { "status": "PASS", "evidence_pack_count": 12, "fail_remediated_count": 0 },
    "C2.26-2": { "status": "PASS", "evidence_pack_count": 12, "fail_remediated_count": 1, "remediation_refs": ["INC-2026-0421"] },
    "C2.26-3": { "status": "PASS", "evidence_pack_count": 12, "fail_remediated_count": 0 },
    "C2.26-4": { "status": "PASS", "evidence_pack_count": 12, "fail_remediated_count": 0 },
    "C2.26-5": { "status": "PASS", "evidence_pack_count": 12, "fail_remediated_count": 2, "remediation_refs": ["INC-2026-0489","INC-2026-0512"] },
    "C2.26-6": { "status": "PASS", "evidence_pack_count": 1,  "fail_remediated_count": 0 },
    "C2.26-7": { "status": "PASS", "evidence_pack_count": 12, "fail_remediated_count": 1, "remediation_refs": ["INC-2026-0533"] },
    "C2.26-8": { "status": "PASS", "evidence_pack_count": 12, "fail_remediated_count": 0 }
  },
  "upstream_attestation_ref": "1.2/sponsor-attestation-Q1-2026.json",
  "downstream_consumer_ref": "3.6/orphan-registry-Q1-2026.json",
  "signatures": {
    "ai_governance_lead": {
      "signer_upn": "ai.gov.lead@contoso.com",
      "signed_at": "2026-04-12T15:00:00Z",
      "certificate_thumbprint": "AB12...EF34",
      "signature_pkcs7_b64": "MIIE...=="
    },
    "compliance_officer": {
      "signer_upn": "compliance.officer@contoso.com",
      "signed_at": "2026-04-22T11:30:00Z",
      "certificate_thumbprint": "CD56...7890",
      "signature_pkcs7_b64": "MIIE...=="
    }
  }
}
```

### 13.6 Failure path within the runbook itself

If any criterion ends the quarter with an unremediated FAIL, the Lead MUST NOT sign a clean attestation. Instead:

1. Mark `criteria_attestation.<criterion>.status = "FAIL_OPEN"`.
2. Attach the open ticket reference and projected remediation date.
3. Sign the packet anyway (a "qualified attestation"); counter-signature still required.
4. Notify the Board Risk Committee secretariat within 5 business days.
5. Repeat the quarterly cycle on the closing of the open finding (interim attestation).

A qualified attestation is itself examiner-defensible — it documents that the control owner is aware of, and managing, an open issue. A *missing* attestation, by contrast, is not.

### 13.7 Validation runbook

After signing, the Lead runs:

```powershell
Test-Agt226QuarterlyAttestation -PacketPath "quarterly-attestation-Q1-2026.json"
```

which verifies:

- All 8 criteria are present.
- All `evidence_pack_count` values are ≥ the expected cadence (12 weekly for most; 1 for REVIEW; 90 for SPONSOR/EXPIRY daily snapshots).
- All referenced `remediation_refs` resolve to closed tickets.
- Both signatures verify against trusted certificate authorities.
- The packet is hash-linked to the upstream 1.2 attestation and to the downstream 3.6 orphan registry.

A `PASS` from this validator is the green light to file with the Board secretariat.

---

## Footer

| | |
|---|---|
| **Control** | [2.26 — Entra Agent ID Identity Governance](../../../controls/pillar-2-management/2.26-entra-agent-id-identity-governance.md) |
| **Sister playbooks** | [Portal Walkthrough](portal-walkthrough.md) · [PowerShell Setup](powershell-setup.md) · [Troubleshooting](troubleshooting.md) |
| **Last UI verified** | April 2026 |
| **Document version** | v1.0 |
| **Updated** | April 2026 |

> This playbook supports — but does not by itself ensure — compliance with FINRA Rules 3110 and 4511, FINRA Notice 25-07, SEC Rule 17a-4, SOX §404, GLBA §501(b), OCC Bulletin 2026-13 (formerly OCC Bulletin 2011-12), and the FFIEC IT Examination Handbook. Organizations should verify findings against their own legal and regulatory obligations and tailor zone thresholds to their documented risk appetite.
---

*Updated: May 2026 | Version: v1.6.2 | UI Verification Status: Current*
