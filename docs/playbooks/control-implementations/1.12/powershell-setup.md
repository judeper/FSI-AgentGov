# Control 1.12 — PowerShell Setup: Insider Risk Management

**Control:** [1.12 Insider Risk Detection and Response](../../../controls/pillar-1-security/1.12-insider-risk-detection-and-response.md)
**Baseline:** [PowerShell baseline (`_shared/powershell-baseline.md`)](../../_shared/powershell-baseline.md)
**Audience:** M365 administrator at a US financial services organization (FINRA / SEC / GLBA / OCC / Fed SR 11-7 / CFTC oversight) operating Microsoft 365 Copilot, Agent Builder, and Copilot Studio agents.
**Sovereign clouds:** Commercial / GCC / GCC High / DoD — connection helper in [Section 1](#1-pre-flight) and full reference in [Section 8](#8-sovereign-cloud-reference). Insider Risk Management (and Adaptive Protection in particular) has **limited availability** in GCC / GCC High / DoD — see [Section 8](#8-sovereign-cloud-reference) and [Section 9](#9-anti-patterns-what-not-to-do).
**Required modules:**

- `ExchangeOnlineManagement` ≥ 3.5.0 — provides `Connect-IPPSSession`, `Search-UnifiedAuditLog`, `Get-RoleGroupMember`, `New-ComplianceCase`.
- `Microsoft.Graph.Authentication` ≥ 2.15.0 — provides `Connect-MgGraph` and `Invoke-MgGraphRequest` for the Microsoft Graph **beta** Insider Risk Management endpoints.
- `Microsoft.Graph.Beta.Security` ≥ 2.15.0 — installed only when you intend to use the typed cmdlets; this playbook uses `Invoke-MgGraphRequest` against the raw beta endpoint to keep the schema stable as the beta surface evolves.

!!! danger "READ FIRST — Insider Risk Management has essentially no PowerShell cmdlet surface for policy CRUD"

    All Insider Risk Management (IRM) **policy, settings, indicator, priority-user-group, role-group definition, and Adaptive Protection configuration is portal-only** in the Microsoft Purview portal. There is **no** `Get-InsiderRiskPolicy`, no `Get-InsiderRiskAlert`, no `Get-InsiderRiskPriorityUserGroup`, and no `New-/Set-/Remove-InsiderRisk*` cmdlet on Microsoft Learn. **Any script that calls those cmdlet names is calling something that does not exist** — the cmdlet will fail with `CommandNotFoundException`, and any prior version of this playbook that suppressed the error with `-ErrorAction SilentlyContinue` followed by a `[PASS]` banner produced **fabricated evidence**.

    What PowerShell *can* do for Control 1.12 is a tightly bounded set:

    1. **Unified Audit Log search** for IRM-emitted operations under the `InsiderRiskManagement*` family via `Search-UnifiedAuditLog -Operations …` (paged with `-SessionId` + `-SessionCommand ReturnLargeSet`).
    2. **Role-group inventory** for the six IRM role groups via `Get-RoleGroupMember` from `Connect-IPPSSession`.
    3. **Microsoft Graph beta** read of cases and alerts via `GET /beta/security/cases/insiderRiskCases` and `GET /beta/security/alerts_v2?$filter=serviceSource eq 'microsoftInsiderRiskManagement'`.
    4. **Case creation** via the generic compliance-case cmdlet `New-ComplianceCase -CaseType InsiderRisk` — useful for spinning up an investigation shell from automation, but does **not** configure policies or indicators.
    5. **License and connector pre-flight** via `Get-MgSubscribedSku` and read-only inspection of audit logs for HR connector ingestion events.

    Treat this playbook as the **evidence, inventory, and case-bootstrap automation layer** for Control 1.12 — not as a substitute for portal-driven IRM administration.

---

## 0. PowerShell vs portal — the boundary table

This is the single source of truth for what belongs in PowerShell vs the Microsoft Purview portal for Control 1.12. Verify against Microsoft Learn — [Insider Risk Management — Get started](https://learn.microsoft.com/en-us/purview/insider-risk-management-configure) and [Insider Risk Management permissions](https://learn.microsoft.com/en-us/purview/insider-risk-management-permissions) — before each change window. Microsoft has been moving capabilities between surfaces, and the beta Graph endpoints in particular evolve.

| Capability | PowerShell? | Where it lives |
|---|---|---|
| Create / update / delete IRM policies (Data theft by departing users, Risky AI usage, **Risky Agents**, General data leaks, Security policy violations, etc.) | **No** | Microsoft Purview portal → Insider Risk Management → Policies |
| Configure IRM **settings** (privacy / pseudonymization, indicators, indicator thresholds, intelligent detections, policy timeframes, export, priority user groups, priority physical assets, intelligent detections, analytics) | **No** | Purview portal → Insider Risk Management → Settings |
| Configure **Forensic Evidence** capture rules and dual-authorization Approver assignments | **No** | Purview portal → Insider Risk Management → Forensic evidence |
| Configure **Adaptive Protection** (risk-level → DLP / DLM / Conditional Access mapping). Limited availability in GCC / GCC High / DoD. | **No** | Purview portal → Insider Risk Management → Adaptive protection |
| Triage alerts (assign, dismiss, confirm, escalate) | **No** | Purview portal → Insider Risk Management → Alerts |
| Investigate cases (review activity, content explorer, forensic clips) | **No** | Purview portal → Insider Risk Management → Cases |
| Define / update IRM **role groups** and their members | **Read-only via PowerShell** — `Get-RoleGroup`, `Get-RoleGroupMember`. Membership changes are documented for the IRM role groups but the canonical surface is Purview portal → Roles & scopes → Permissions. | IPPS PowerShell (read) / Purview portal (write) |
| **Read** IRM cases and alerts programmatically | **Yes — Microsoft Graph beta only.** `GET /beta/security/cases/insiderRiskCases`, `GET /beta/security/alerts_v2?$filter=serviceSource eq 'microsoftInsiderRiskManagement'`. No Exchange / IPPS cmdlet exists. | Microsoft Graph beta (`Invoke-MgGraphRequest`) |
| **Create** an IRM case shell (for example, to bootstrap an investigation triggered by an external SIEM rule) | **Yes** — `New-ComplianceCase -CaseType InsiderRisk`. Generic compliance-case cmdlet; does **not** configure policies or indicators. | IPPS PowerShell |
| Audit-log evidence stream for IRM operations (`InsiderRiskManagementAlert*`, `InsiderRiskManagementCase*`, `InsiderRiskManagementSettings*`, `InsiderRiskManagementPolicy*`, `InsiderRiskManagementWorkflow*`) | **Yes** — `Search-UnifiedAuditLog` (paged) | IPPS PowerShell |
| HR connector status (last successful upload, file row count, schema validation errors) | **Read-only via portal export today.** No supported PowerShell cmdlet returns HR connector run history. Use the Microsoft Purview portal → Data connectors → HR connector → Status, and emit the export as evidence. The audit log records connector configuration changes but not row-level ingestion success. | Purview portal (status); IPPS UAL (config-change events only) |
| License surface for IRM (E5 / E5 Compliance / Insider Risk Management standalone / Microsoft Purview Suite) | **Yes** — `Get-MgSubscribedSku` (Microsoft Graph) | Microsoft Graph |
| Tenant-wide audit ingestion (`UnifiedAuditLogIngestionEnabled`) — pre-requisite for IRM signal capture | **Yes** — but that is **Control 1.7**, not 1.12 | Exchange Online PowerShell |

> **Do not promote PowerShell as a substitute for portal IRM administration.** If a sub-script in this playbook appears to "create an IRM policy" or "set a priority user group", it is doing something else — most likely creating a generic compliance case shell, or reading the audit log for evidence of someone doing that work in the portal. Document the boundary in every change ticket so reviewers do not expect a PS-based diff.

---

## 1. Pre-flight

Every Control 1.12 PowerShell session **must** start with the same six steps:

1. Pin module versions (CAB-approved): `ExchangeOnlineManagement`, `Microsoft.Graph.Authentication`.
2. Resolve sovereign-cloud connection parameters from a single switch and **emit a clear warning** if the cloud is GCC / GCC High / DoD because IRM and especially Adaptive Protection have limited availability there.
3. Connect to **IPPS** (Security & Compliance) — IRM audit operations and IRM role groups are IPPS-only.
4. Connect to **Microsoft Graph** with the read scopes required for IRM cases and alerts on the beta endpoint.
5. Verify the caller is a member of at least one of the six IRM role groups (otherwise UAL queries scoped to IRM operations may return zero rows that look like clean evidence).
6. Verify the tenant has the licensing required for IRM (Microsoft 365 E5 / E5 Compliance / Insider Risk Management standalone / Microsoft Purview Suite).

Save the helper below as `Initialize-Irm112Session.ps1` in your evidence-collection module.

```powershell
#Requires -Version 7.2
#Requires -Modules @{ ModuleName = 'ExchangeOnlineManagement';        RequiredVersion = '3.5.0' }
#Requires -Modules @{ ModuleName = 'Microsoft.Graph.Authentication';  RequiredVersion = '2.15.0' }

function Initialize-Irm112Session {
    <#
    .SYNOPSIS
        Pre-flight for Control 1.12 (Insider Risk Management).
    .DESCRIPTION
        Resolves sovereign endpoint, opens an IPPS session and a Microsoft Graph
        session with IRM read scopes, asserts module version pins, asserts caller
        IRM role-group membership, asserts tenant license surface, and emits a
        session-state PSCustomObject for downstream scripts to consume. Read-only —
        no tenant mutation.
    .PARAMETER UserPrincipalName
        UPN used to authenticate to IPPS and Microsoft Graph.
    .PARAMETER Cloud
        Microsoft 365 cloud the tenant is in. Default: Commercial.
    .PARAMETER RequiredRoleGroups
        Caller must be a member of at least one of these IRM role groups. Default:
        all six. Override only when a least-privilege scope is being asserted.
    .EXAMPLE
        $ctx = Initialize-Irm112Session -UserPrincipalName admin@contoso.com -Cloud GCCHigh
    #>
    [CmdletBinding()]
    param(
        [Parameter(Mandatory)] [string] $UserPrincipalName,
        [ValidateSet('Commercial','GCC','GCCHigh','DoD')]
        [string] $Cloud = 'Commercial',
        [string[]] $RequiredRoleGroups = @(
            'Insider Risk Management',
            'Insider Risk Management Admins',
            'Insider Risk Management Analysts',
            'Insider Risk Management Investigators',
            'Insider Risk Management Auditors',
            'Insider Risk Management Approvers'
        )
    )

    $ErrorActionPreference = 'Stop'

    # 1. Module pin assertion
    $exo = Get-Module -ListAvailable -Name ExchangeOnlineManagement |
           Sort-Object Version -Descending | Select-Object -First 1
    if (-not $exo)              { throw "ExchangeOnlineManagement module not installed." }
    if ($exo.Version -lt [version]'3.5.0') {
        throw "ExchangeOnlineManagement $($exo.Version) is below the 3.5.0 minimum required for IPPS REST."
    }
    $mga = Get-Module -ListAvailable -Name Microsoft.Graph.Authentication |
           Sort-Object Version -Descending | Select-Object -First 1
    if (-not $mga)              { throw "Microsoft.Graph.Authentication module not installed." }
    if ($mga.Version -lt [version]'2.15.0') {
        throw "Microsoft.Graph.Authentication $($mga.Version) is below the 2.15.0 minimum required for Invoke-MgGraphRequest against the beta endpoint."
    }

    # 2. Resolve sovereign endpoints
    $endpoint = switch ($Cloud) {
        'Commercial' { @{
            IppsUri    = 'https://ps.compliance.protection.outlook.com/powershell-liveid/'
            Aad        = 'https://login.microsoftonline.com/organizations'
            GraphEnv   = 'Global'
            GraphHost  = 'https://graph.microsoft.com'
        } }
        'GCC'        { @{
            IppsUri    = 'https://ps.compliance.protection.outlook.com/powershell-liveid/'
            Aad        = 'https://login.microsoftonline.com/organizations'
            GraphEnv   = 'Global'
            GraphHost  = 'https://graph.microsoft.com'
        } }
        'GCCHigh'    { @{
            IppsUri    = 'https://ps.compliance.protection.office365.us/powershell-liveid/'
            Aad        = 'https://login.microsoftonline.us/organizations'
            GraphEnv   = 'USGov'
            GraphHost  = 'https://graph.microsoft.us'
        } }
        'DoD'        { @{
            IppsUri    = 'https://l5.ps.compliance.protection.office365.us/powershell-liveid/'
            Aad        = 'https://login.microsoftonline.us/organizations'
            GraphEnv   = 'USGovDoD'
            GraphHost  = 'https://dod-graph.microsoft.us'
        } }
    }

    # 2a. Sovereign-availability warning (CRITICAL — IRM / Adaptive Protection have limited gov-cloud availability)
    if ($Cloud -in @('GCC','GCCHigh','DoD')) {
        Write-Warning @"
Insider Risk Management has LIMITED AVAILABILITY in $Cloud per Microsoft Learn
(insider-risk-management-adaptive-protection). Several capabilities — including
Adaptive Protection, Risky AI usage, Risky Agents, and Risky browser usage — may
not be available, may have reduced indicator coverage, or may produce zero rows
for some queries in this script. ZERO ROWS IN $Cloud DOES NOT MEAN A CLEAN TENANT.
Document the gap as a Control 1.12 exception in your control register and apply
compensating controls: Communication Compliance (Control 1.10), Audit Premium
(Control 1.7), DLP and Sensitivity Labels (Control 1.5), Defender for Cloud Apps,
and Microsoft Sentinel UEBA. Reverify gov-cloud availability against Microsoft
Learn before each change window.
"@
    }

    # 3. Open IPPS session (idempotent)
    $existing = Get-ConnectionInformation -ErrorAction SilentlyContinue |
                Where-Object { $_.ConnectionUri -like '*compliance.protection*' -and $_.State -eq 'Connected' }
    if (-not $existing) {
        Connect-IPPSSession `
            -UserPrincipalName $UserPrincipalName `
            -ConnectionUri $endpoint.IppsUri `
            -AzureADAuthorizationEndpointUri $endpoint.Aad | Out-Null
    }

    # 4. Open Microsoft Graph session with IRM read scopes
    #    Scopes required for /beta/security/cases/insiderRiskCases and /beta/security/alerts_v2:
    #    - InsiderRiskManagement.Read.All  (cases)
    #    - SecurityAlert.Read.All          (alerts_v2 with serviceSource = microsoftInsiderRiskManagement)
    #    - Organization.Read.All           (Get-MgSubscribedSku for license pre-flight)
    $mgCtx = Get-MgContext -ErrorAction SilentlyContinue
    if (-not $mgCtx -or $mgCtx.Environment -ne $endpoint.GraphEnv) {
        Connect-MgGraph -Environment $endpoint.GraphEnv -Scopes @(
            'InsiderRiskManagement.Read.All',
            'SecurityAlert.Read.All',
            'Organization.Read.All'
        ) -NoWelcome | Out-Null
    }

    # 5. IRM role-group membership check (caller must be in AT LEAST ONE of $RequiredRoleGroups)
    $callerUpn = $UserPrincipalName
    $isMember  = $false
    $matchedGroup = $null
    foreach ($g in $RequiredRoleGroups) {
        $rg = Get-RoleGroup -Identity $g -ErrorAction SilentlyContinue
        if (-not $rg) { continue }
        $members = Get-RoleGroupMember -Identity $g -ErrorAction SilentlyContinue
        $hit = $members | Where-Object {
            $_.PrimarySmtpAddress -eq $callerUpn -or
            $_.WindowsLiveID      -eq $callerUpn -or
            $_.Name               -eq $callerUpn
        }
        if ($hit) { $isMember = $true; $matchedGroup = $g; break }
    }
    if (-not $isMember) {
        throw "Caller $callerUpn is not a member of any of the IRM role groups: $($RequiredRoleGroups -join ', '). IRM-scoped audit-log queries and Graph beta calls will return zero or partial results that are unsafe to treat as evidence."
    }

    # 6. License pre-flight (E5 / E5 Compliance / IRM standalone / Purview Suite)
    #    Verify the exact service-plan IDs for IRM against Microsoft Learn at the
    #    time of run — Microsoft updates the SKU and service-plan catalog regularly:
    #    https://learn.microsoft.com/en-us/entra/identity/users/licensing-service-plan-reference
    $skus = Get-MgSubscribedSku -ErrorAction Stop
    $irmCapableSkuPartNumbers = @(
        'ENTERPRISEPREMIUM',                # Microsoft 365 E5
        'INFORMATION_PROTECTION_COMPLIANCE',# Microsoft 365 E5 Compliance
        'M365_E5_SUITE_COMPONENTS',         # Microsoft 365 E5 Suite Components (variant)
        'MICROSOFT_365_E5_INSIDER_RISK_MANAGEMENT', # IRM standalone (verify exact SkuPartNumber on Learn)
        'PURVIEW_SUITE'                     # Microsoft Purview Suite (verify exact SkuPartNumber on Learn)
    )
    $licensedFor = $skus | Where-Object {
        $_.SkuPartNumber -in $irmCapableSkuPartNumbers -and $_.PrepaidUnits.Enabled -gt 0
    } | Select-Object -ExpandProperty SkuPartNumber
    if (-not $licensedFor) {
        Write-Warning "No IRM-capable SKU detected via Get-MgSubscribedSku. Verify license assignment in the Microsoft 365 admin center; do not treat zero-row IRM evidence as clean."
    }

    [PSCustomObject]@{
        Cloud              = $Cloud
        IppsUri            = $endpoint.IppsUri
        GraphEnv           = $endpoint.GraphEnv
        GraphHost          = $endpoint.GraphHost
        Caller             = $callerUpn
        MatchedRoleGroup   = $matchedGroup
        IrmCapableSkus     = $licensedFor
        ExoModuleVersion   = $exo.Version.ToString()
        GraphModuleVersion = $mga.Version.ToString()
        ConnectedAtUtc     = (Get-Date).ToUniversalTime()
        TenantId           = (Get-ConnectionInformation | Select-Object -First 1).TenantID
    }
}
```

> **Why role membership is a hard pre-flight.** A caller without any of the six IRM role groups will still be able to run `Search-UnifiedAuditLog`, but the IRM-scoped operations will be filtered out by the audit pipeline's permission projection — the result is an empty page that looks identical to a tenant where IRM is configured but quiet. Without the membership assertion, an unauthorized run produces a zero-row evidence file: the exact pattern auditors flag as **fabricated false-clean evidence**.

---

## 2. The six IRM role groups — read-only inventory

Per Microsoft Learn ([Insider Risk Management permissions](https://learn.microsoft.com/en-us/purview/insider-risk-management-permissions)) IRM defines **six** role groups. Snapshot all six on every evidence run so the diff between two runs is unambiguous and the **separation-of-duties rule** (Approvers must be distinct from Investigators; Auditors should be distinct from Admins and Investigators) can be programmatically asserted.

```powershell
# Session: IPPS
function Get-Irm112RoleGroupSnapshot {
    <#
    .SYNOPSIS
        Read-only inventory of all six IRM role groups.
    .DESCRIPTION
        Snapshots membership and computes separation-of-duties violations:
        (a) any principal in BOTH 'Insider Risk Management Approvers' AND
            'Insider Risk Management Investigators'  -> Forensic Evidence
            dual-authorization is broken.
        (b) any principal in BOTH 'Insider Risk Management Auditors' AND
            ('Insider Risk Management Admins' or 'Insider Risk Management
            Investigators')  -> independent assurance is broken.
    .PARAMETER OutputDirectory
        Where to land the JSON snapshot and SHA-256 sidecar.
    #>
    [CmdletBinding()]
    param(
        [Parameter(Mandatory)] [string] $OutputDirectory
    )

    $ErrorActionPreference = 'Stop'
    New-Item -ItemType Directory -Force -Path $OutputDirectory | Out-Null
    $ts    = Get-Date -Format 'yyyyMMddTHHmmssZ'
    $runId = [guid]::NewGuid().Guid

    $irmRoleGroups = @(
        'Insider Risk Management',
        'Insider Risk Management Admins',
        'Insider Risk Management Analysts',
        'Insider Risk Management Investigators',
        'Insider Risk Management Auditors',
        'Insider Risk Management Approvers'
    )

    $snapshot = foreach ($g in $irmRoleGroups) {
        $rg = Get-RoleGroup -Identity $g -ErrorAction SilentlyContinue
        if (-not $rg) {
            [PSCustomObject]@{ RoleGroup = $g; Exists = $false; Count = 0; Members = @() }
            continue
        }
        $members = Get-RoleGroupMember -Identity $g -ErrorAction Stop |
                   Select-Object Name, PrimarySmtpAddress, RecipientType
        [PSCustomObject]@{
            RoleGroup = $g
            Exists    = $true
            Count     = ($members | Measure-Object).Count
            Members   = $members
        }
    }

    # Separation-of-duties checks
    $approvers     = ($snapshot | Where-Object RoleGroup -eq 'Insider Risk Management Approvers').Members.PrimarySmtpAddress
    $investigators = ($snapshot | Where-Object RoleGroup -eq 'Insider Risk Management Investigators').Members.PrimarySmtpAddress
    $auditors      = ($snapshot | Where-Object RoleGroup -eq 'Insider Risk Management Auditors').Members.PrimarySmtpAddress
    $admins        = ($snapshot | Where-Object RoleGroup -eq 'Insider Risk Management Admins').Members.PrimarySmtpAddress

    $sodViolations = [PSCustomObject]@{
        ApproverAlsoInvestigator = $approvers | Where-Object { $_ -in $investigators }   # Forensic Evidence dual-auth
        AuditorAlsoAdmin         = $auditors  | Where-Object { $_ -in $admins }          # Independent assurance
        AuditorAlsoInvestigator  = $auditors  | Where-Object { $_ -in $investigators }   # Independent assurance
    }

    $jsonPath = Join-Path $OutputDirectory "1.12-rolegroups-$ts.json"
    $payload  = [PSCustomObject]@{
        runId          = $runId
        control        = '1.12'
        artifact       = 'irm-rolegroup-snapshot'
        generatedUtc   = (Get-Date).ToUniversalTime().ToString('o')
        roleGroups     = $snapshot
        sodViolations  = $sodViolations
    }
    $payload | ConvertTo-Json -Depth 8 | Set-Content -Path $jsonPath -Encoding UTF8
    $hash = (Get-FileHash -Path $jsonPath -Algorithm SHA256).Hash
    Set-Content -Path "$jsonPath.sha256" -Value $hash -Encoding ASCII

    # Compute deterministic pass criterion
    $hasViolation = ($sodViolations.ApproverAlsoInvestigator.Count -gt 0) -or
                    ($sodViolations.AuditorAlsoAdmin.Count -gt 0) -or
                    ($sodViolations.AuditorAlsoInvestigator.Count -gt 0)
    if ($hasViolation) {
        Write-Host "[FAIL] Separation-of-duties violation(s) detected in IRM role groups. See $jsonPath." -ForegroundColor Red
        $payload | Add-Member -NotePropertyName Result -NotePropertyValue 'FAIL' -PassThru | Out-Null
    } else {
        Write-Host "[PASS] All six IRM role groups inventoried; no separation-of-duties violations." -ForegroundColor Green
        $payload | Add-Member -NotePropertyName Result -NotePropertyValue 'PASS' -PassThru | Out-Null
    }

    $payload
}
```

> **Why all six.** The umbrella `Insider Risk Management` role group grants broad access and should generally be **avoided** in regulated FSI tenants in favor of the segmented groups. Tenants provisioned before the segmented model existed may still hold members in the umbrella; tenants provisioned after may not have the umbrella populated at all. Snapshotting all six makes the legacy footprint visible.

---

## 3. Audit-log evidence — IRM operations

The IRM operations indexed in the Unified Audit Log live under the `InsiderRiskManagement*` operation prefix. Verify the exact list against Microsoft Learn — [Audit log activities](https://learn.microsoft.com/en-us/purview/audit-log-activities) — at the time of run; Microsoft adds new IRM operations as the product grows. The set below is the operations consistently surfaced in the IRM family and is a sound starting point for a quarterly evidence sweep.

| Operation (verify on Learn before relying) | What it records |
|---|---|
| `InsiderRiskManagementAlertCreated` | An IRM alert was generated by a policy. |
| `InsiderRiskManagementAlertUpdated` | Triage state or assignment on an alert was changed. |
| `InsiderRiskManagementCaseCreated` | A case was opened (from an alert, manually, or via `New-ComplianceCase -CaseType InsiderRisk`). |
| `InsiderRiskManagementCaseUpdated` | Case state, assignment, notes, or attachments were updated. |
| `InsiderRiskManagementPolicyCreated` | A policy was created in the Purview portal. |
| `InsiderRiskManagementPolicyUpdated` | A policy was edited (indicators, scope, thresholds). |
| `InsiderRiskManagementPolicyDeleted` | A policy was deleted. |
| `InsiderRiskManagementSettingsUpdated` | A tenant-level IRM setting was changed (privacy / pseudonymization, indicators, intelligent detections, priority user groups, priority physical assets, analytics). |
| `InsiderRiskManagementWorkflowExecuted` | A user took action in the IRM workflow (assign reviewer, escalate to case, dismiss alert, send user notice). |

> **Critical:** `Search-UnifiedAuditLog` is hard-capped at 5,000 rows per call. A single-call `-ResultSize 5000` **silently truncates** at the cap and returns no error. The collector below uses the documented session-paging pattern (`-SessionId <guid>` + `-SessionCommand ReturnLargeSet`), loops until an empty page returns, and **hard-fails** if the per-session ceiling (50,000 rows per session) is reached without exhaustion — at that point you must narrow the date window and re-run.

```powershell
# Session: IPPS
function Get-Irm112AuditEvidence {
    <#
    .SYNOPSIS
        Paged Unified Audit Log collector for Insider Risk Management operations.
    .DESCRIPTION
        Iterates Search-UnifiedAuditLog using session-paging until an empty page is
        returned. Hard-fails if the per-session ceiling is hit without exhaustion
        (caller must narrow date range). Writes JSON + CSV with SHA-256 sidecars
        and updates manifest.
    .PARAMETER StartUtc
        UTC start of the audit window. Cannot be more than 180 days in the past
        for standard tenants (longer with audit retention add-on — Control 1.7).
    .PARAMETER EndUtc
        UTC end of the audit window.
    .PARAMETER OutputDirectory
        Where to land evidence files. Should be a WORM-eligible path
        (Purview retention lock or Azure Storage immutability).
    #>
    [CmdletBinding()]
    param(
        [Parameter(Mandatory)] [datetime] $StartUtc,
        [Parameter(Mandatory)] [datetime] $EndUtc,
        [Parameter(Mandatory)] [string]   $OutputDirectory,
        [string[]] $Operations = @(
            'InsiderRiskManagementAlertCreated',
            'InsiderRiskManagementAlertUpdated',
            'InsiderRiskManagementCaseCreated',
            'InsiderRiskManagementCaseUpdated',
            'InsiderRiskManagementPolicyCreated',
            'InsiderRiskManagementPolicyUpdated',
            'InsiderRiskManagementPolicyDeleted',
            'InsiderRiskManagementSettingsUpdated',
            'InsiderRiskManagementWorkflowExecuted'
        )
    )

    $ErrorActionPreference = 'Stop'
    New-Item -ItemType Directory -Force -Path $OutputDirectory | Out-Null
    $runId = [guid]::NewGuid().Guid
    $ts    = Get-Date -Format 'yyyyMMddTHHmmssZ'

    try {
        $sessionId = "irm112-$runId"
        $all       = New-Object System.Collections.Generic.List[object]
        $pageIndex = 0
        $maxPages  = 10   # 10 pages × 5000 rows = 50,000-row session ceiling

        do {
            $pageIndex++
            $page = Search-UnifiedAuditLog `
                -StartDate $StartUtc `
                -EndDate   $EndUtc `
                -Operations $Operations `
                -SessionId  $sessionId `
                -SessionCommand ReturnLargeSet `
                -ResultSize 5000 `
                -ErrorAction Stop

            if ($null -eq $page -or $page.Count -eq 0) { break }
            $all.AddRange($page)

            Write-Verbose "Page $pageIndex returned $($page.Count) rows; cumulative=$($all.Count)"

            if ($pageIndex -ge $maxPages -and $page.Count -eq 5000) {
                throw "Session ceiling reached ($($all.Count) rows) without exhaustion. Narrow the date window and re-run; treating partial results as evidence is not safe."
            }
        } while ($true)

        # JSON
        $jsonPath = Join-Path $OutputDirectory "1.12-ual-$ts.json"
        $all | ConvertTo-Json -Depth 10 | Set-Content -Path $jsonPath -Encoding UTF8

        # CSV (flattened — for reviewer convenience; the JSON is the authoritative artifact)
        $csvPath  = Join-Path $OutputDirectory "1.12-ual-$ts.csv"
        $all | Select-Object CreationDate, UserIds, Operations, RecordType, ResultIndex, ResultCount, Identity, AuditData |
            Export-Csv -Path $csvPath -NoTypeInformation -Encoding UTF8

        # Hashes + manifest
        $jsonHash = (Get-FileHash -Path $jsonPath -Algorithm SHA256).Hash
        $csvHash  = (Get-FileHash -Path $csvPath  -Algorithm SHA256).Hash
        Set-Content -Path "$jsonPath.sha256" -Value $jsonHash -Encoding ASCII
        Set-Content -Path "$csvPath.sha256"  -Value $csvHash  -Encoding ASCII

        $manifest = [PSCustomObject]@{
            runId         = $runId
            control       = '1.12'
            artifact      = 'irm-ual'
            tenantId      = (Get-ConnectionInformation | Select-Object -First 1).TenantID
            cloud         = (Get-ConnectionInformation | Select-Object -First 1).ConnectionUri
            runner        = "$env:USERDOMAIN\$env:USERNAME"
            startUtc      = $StartUtc.ToString('o')
            endUtc        = $EndUtc.ToString('o')
            params        = @{ Operations = $Operations }
            outputs       = @(
                @{ file = (Split-Path $jsonPath -Leaf); sha256 = $jsonHash; bytes = (Get-Item $jsonPath).Length }
                @{ file = (Split-Path $csvPath  -Leaf); sha256 = $csvHash;  bytes = (Get-Item $csvPath ).Length }
            )
            rowCount      = $all.Count
            pagesConsumed = $pageIndex
            generatedUtc  = (Get-Date).ToUniversalTime().ToString('o')
        }
        $manifestPath = Join-Path $OutputDirectory "1.12-manifest-ual-$ts.json"
        $manifest | ConvertTo-Json -Depth 6 | Set-Content -Path $manifestPath -Encoding UTF8

        # Deterministic pass criterion: collector exhausted without ceiling hit.
        # Zero rows is a valid PASS only when paired with the role-group snapshot
        # showing IRM is configured AND the gov-cloud warning was not the cause.
        Write-Host "[PASS] UAL collection complete. $($all.Count) row(s), $pageIndex page(s)." -ForegroundColor Green
        $manifest
    }
    catch {
        Write-Host "[FAIL] UAL collection failed: $($_.Exception.Message)" -ForegroundColor Red
        [PSCustomObject]@{
            Result = 'FAIL'
            Error  = $_.Exception.Message
        }
    }
}
```

> **Records-retention caveat (FINRA 4511 / SEC 17a-4(b)(4)).** Exporting CSV / JSON to a local file system **does not** by itself satisfy SEC 17a-4(b)(4) WORM requirements or FINRA 4511 record-keeping rules. IRM cases, alerts, and Forensic Evidence clips are working investigative artifacts — Forensic Evidence clips auto-delete 120 days after capture unless exported. Records retention is the responsibility of [Control 1.9 (Data Retention and Deletion Policies)](../../../controls/pillar-1-security/1.9-data-retention-and-deletion-policies.md) and the underlying [Control 1.7 (Comprehensive Audit Logging)](../../../controls/pillar-1-security/1.7-comprehensive-audit-logging-and-compliance.md). Land the artifacts produced by this section into a Microsoft Purview retention-locked repository or an Azure Storage container with an immutability policy, and reference the storage path in your change ticket. The SHA-256 sidecars in this section provide content-integrity evidence; they do not provide WORM.

---

## 4. Microsoft Graph beta — read IRM cases and alerts

Microsoft Graph **beta** is the only programmatic surface to read IRM case and alert objects. There is no Exchange / IPPS cmdlet that returns either. Verify the schema and endpoint shape against Microsoft Learn at run time; the beta surface evolves.

- Cases: `GET https://graph.microsoft.com/beta/security/cases/insiderRiskCases` (delegated scope `InsiderRiskManagement.Read.All`)
- Alerts: `GET https://graph.microsoft.com/beta/security/alerts_v2?$filter=serviceSource eq 'microsoftInsiderRiskManagement'` (delegated scope `SecurityAlert.Read.All`)

> **Pseudonymization-aware export.** IRM ships with **pseudonymization on by default** in the portal — usernames are replaced with anonymous identifiers in alerts and cases until an Investigator explicitly unmasks them under audit. The Graph beta responses respect that posture. The collector below has an `-IncludePseudonymizedExport` switch (default `$true`) that **does not attempt to unmask**. Unmasking requires explicit operator action through the portal under audit, and is recorded as `InsiderRiskManagementWorkflowExecuted` in the UAL — keep it in the portal, do not script it.

```powershell
# Session: Microsoft Graph (beta) — Connect-MgGraph already established by Initialize-Irm112Session
function Get-Irm112Cases {
    <#
    .SYNOPSIS
        Read IRM cases via Microsoft Graph beta.
    .PARAMETER OutputDirectory
        Where to land evidence files (JSON + SHA-256 sidecar + manifest).
    .PARAMETER GraphHost
        The Graph host for the tenant cloud (https://graph.microsoft.com,
        https://graph.microsoft.us, https://dod-graph.microsoft.us).
    .PARAMETER IncludePseudonymizedExport
        Default $true. Exports the response as the Graph beta returns it,
        with pseudonymized identifiers preserved. Unmasking is portal-only
        under audit and is intentionally not scripted here.
    #>
    [CmdletBinding()]
    param(
        [Parameter(Mandatory)] [string] $OutputDirectory,
        [Parameter(Mandatory)] [string] $GraphHost,
        [switch] $IncludePseudonymizedExport = $true
    )

    $ErrorActionPreference = 'Stop'
    New-Item -ItemType Directory -Force -Path $OutputDirectory | Out-Null
    $ts    = Get-Date -Format 'yyyyMMddTHHmmssZ'
    $runId = [guid]::NewGuid().Guid

    try {
        $uri  = "$GraphHost/beta/security/cases/insiderRiskCases"
        $cases = New-Object System.Collections.Generic.List[object]
        do {
            $resp = Invoke-MgGraphRequest -Method GET -Uri $uri -ErrorAction Stop
            if ($resp.value) { $cases.AddRange($resp.value) }
            $uri = $resp.'@odata.nextLink'
        } while ($uri)

        $jsonPath = Join-Path $OutputDirectory "1.12-cases-$ts.json"
        $cases | ConvertTo-Json -Depth 10 | Set-Content -Path $jsonPath -Encoding UTF8
        $hash = (Get-FileHash -Path $jsonPath -Algorithm SHA256).Hash
        Set-Content -Path "$jsonPath.sha256" -Value $hash -Encoding ASCII

        $manifest = [PSCustomObject]@{
            runId        = $runId
            control      = '1.12'
            artifact     = 'irm-cases'
            endpoint     = "$GraphHost/beta/security/cases/insiderRiskCases"
            pseudonymized= [bool]$IncludePseudonymizedExport
            outputs      = @(
                @{ file = (Split-Path $jsonPath -Leaf); sha256 = $hash; bytes = (Get-Item $jsonPath).Length }
            )
            caseCount    = $cases.Count
            generatedUtc = (Get-Date).ToUniversalTime().ToString('o')
        }
        $manifest | ConvertTo-Json -Depth 6 |
            Set-Content -Path (Join-Path $OutputDirectory "1.12-manifest-cases-$ts.json") -Encoding UTF8

        Write-Host "[PASS] IRM cases collected. $($cases.Count) case(s)." -ForegroundColor Green
        $manifest
    }
    catch {
        Write-Host "[FAIL] IRM case collection failed: $($_.Exception.Message)" -ForegroundColor Red
        [PSCustomObject]@{ Result='FAIL'; Error=$_.Exception.Message }
    }
}

function Get-Irm112Alerts {
    <#
    .SYNOPSIS
        Read IRM alerts via Microsoft Graph beta alerts_v2 with serviceSource filter.
    #>
    [CmdletBinding()]
    param(
        [Parameter(Mandatory)] [string] $OutputDirectory,
        [Parameter(Mandatory)] [string] $GraphHost,
        [switch] $IncludePseudonymizedExport = $true
    )

    $ErrorActionPreference = 'Stop'
    New-Item -ItemType Directory -Force -Path $OutputDirectory | Out-Null
    $ts    = Get-Date -Format 'yyyyMMddTHHmmssZ'
    $runId = [guid]::NewGuid().Guid

    try {
        # URL-encode the $filter expression — single quotes around the value, percent-encoding for the space
        $filter = "serviceSource eq 'microsoftInsiderRiskManagement'"
        $uri    = "$GraphHost/beta/security/alerts_v2?`$filter=$([uri]::EscapeDataString($filter))"
        $alerts = New-Object System.Collections.Generic.List[object]
        do {
            $resp = Invoke-MgGraphRequest -Method GET -Uri $uri -ErrorAction Stop
            if ($resp.value) { $alerts.AddRange($resp.value) }
            $uri = $resp.'@odata.nextLink'
        } while ($uri)

        $jsonPath = Join-Path $OutputDirectory "1.12-alerts-$ts.json"
        $alerts | ConvertTo-Json -Depth 10 | Set-Content -Path $jsonPath -Encoding UTF8
        $hash = (Get-FileHash -Path $jsonPath -Algorithm SHA256).Hash
        Set-Content -Path "$jsonPath.sha256" -Value $hash -Encoding ASCII

        $manifest = [PSCustomObject]@{
            runId        = $runId
            control      = '1.12'
            artifact     = 'irm-alerts'
            endpoint     = "$GraphHost/beta/security/alerts_v2"
            filter       = $filter
            pseudonymized= [bool]$IncludePseudonymizedExport
            outputs      = @(
                @{ file = (Split-Path $jsonPath -Leaf); sha256 = $hash; bytes = (Get-Item $jsonPath).Length }
            )
            alertCount   = $alerts.Count
            generatedUtc = (Get-Date).ToUniversalTime().ToString('o')
        }
        $manifest | ConvertTo-Json -Depth 6 |
            Set-Content -Path (Join-Path $OutputDirectory "1.12-manifest-alerts-$ts.json") -Encoding UTF8

        Write-Host "[PASS] IRM alerts collected. $($alerts.Count) alert(s)." -ForegroundColor Green
        $manifest
    }
    catch {
        Write-Host "[FAIL] IRM alert collection failed: $($_.Exception.Message)" -ForegroundColor Red
        [PSCustomObject]@{ Result='FAIL'; Error=$_.Exception.Message }
    }
}
```

> **Why beta and not v1.0.** As of the last verification date in the footer of this playbook, IRM cases are not exposed on the Microsoft Graph **v1.0** endpoint. Reverify before each change window — when v1.0 surfaces appear they will be the preferred surface for change-resistant automation. Until then, treat the beta endpoint as a versioned dependency and pin the schema you parse against in your evidence pipeline.

---

## 5. Bootstrap an IRM case (the only state-changing operation in this playbook)

`New-ComplianceCase -CaseType InsiderRisk` is the **only** PowerShell-supported IRM mutation. It creates a case **shell** — equivalent to "New case" in the Purview portal under Insider Risk Management → Cases. It does not configure indicators, attach alerts, or assign reviewers; that work is portal-only on the case's blade.

The function below is wrapped in `[CmdletBinding(SupportsShouldProcess, ConfirmImpact='High')]`, captures a before/after snapshot, uses `-ErrorAction Stop` with a `try/catch`, and emits a deterministic PASS/FAIL row only after a verified after-snapshot. **No `-ErrorAction SilentlyContinue` followed by a hard-coded `[PASS]`.**

```powershell
# Session: IPPS
function New-Irm112CaseShell {
    <#
    .SYNOPSIS
        Bootstrap an Insider Risk Management case shell from automation.
    .DESCRIPTION
        Calls New-ComplianceCase -CaseType InsiderRisk to create an empty case
        shell. Use when an external SIEM (Microsoft Sentinel, Splunk, etc.)
        needs to open an IRM case as part of an incident workflow. Indicator
        attachment, alert linkage, and reviewer assignment must be done in the
        Microsoft Purview portal — this function does NOT attempt those.
    .PARAMETER Name
        Case name. Use a deterministic naming scheme aligned with your incident
        management system (e.g., "SIEM-INC-12345 / 2026-04-16 / data-exfil").
    .PARAMETER Description
        Free-text description. Captured as the case description field.
    .PARAMETER EvidencePath
        Where to land before/after JSON snapshots, transcript, and manifest.
    #>
    [CmdletBinding(SupportsShouldProcess, ConfirmImpact='High')]
    param(
        [Parameter(Mandatory)] [string] $Name,
        [string] $Description = "Created by FSI Control 1.12 automation",
        [Parameter(Mandatory)] [string] $EvidencePath
    )

    $ErrorActionPreference = 'Stop'
    New-Item -ItemType Directory -Force -Path $EvidencePath | Out-Null
    $ts = Get-Date -Format 'yyyyMMddTHHmmssZ'

    try {
        # BEFORE snapshot — list IRM cases visible to the caller
        $before = Get-ComplianceCase -ErrorAction Stop |
                  Where-Object { $_.CaseType -eq 'InsiderRisk' }
        $before | ConvertTo-Json -Depth 6 |
            Set-Content -Path (Join-Path $EvidencePath "1.12-cases-before-$ts.json") -Encoding UTF8

        if ($PSCmdlet.ShouldProcess($Name, "Create Insider Risk Management case shell")) {
            $created = New-ComplianceCase `
                -Name        $Name `
                -CaseType    InsiderRisk `
                -Description $Description `
                -ErrorAction Stop
        }

        # AFTER snapshot — only on success
        $after = Get-ComplianceCase -Identity $Name -ErrorAction Stop
        $after | ConvertTo-Json -Depth 6 |
            Set-Content -Path (Join-Path $EvidencePath "1.12-case-after-$Name-$ts.json") -Encoding UTF8

        # Deterministic pass criterion: case appears in the after-snapshot with the requested name and CaseType.
        $pass = ($after.Name -eq $Name) -and ($after.CaseType -eq 'InsiderRisk')
        if ($pass) {
            Write-Host "[PASS] IRM case '$Name' created." -ForegroundColor Green
            [PSCustomObject]@{
                Result       = 'PASS'
                CaseName     = $after.Name
                CaseId       = $after.Identity
                CaseType     = $after.CaseType
                CreatedAtUtc = (Get-Date).ToUniversalTime()
            }
        } else {
            Write-Host "[FAIL] IRM case '$Name' was not found in the after-snapshot or is not of type InsiderRisk." -ForegroundColor Red
            [PSCustomObject]@{
                Result   = 'FAIL'
                CaseName = $Name
                Error    = 'After-snapshot did not confirm case creation.'
            }
        }
    }
    catch {
        Write-Host "[FAIL] IRM case creation failed: $($_.Exception.Message)" -ForegroundColor Red
        [PSCustomObject]@{
            Result   = 'FAIL'
            CaseName = $Name
            Error    = $_.Exception.Message
        }
    }
}
```

> **Why no `Set-` or `Remove-` wrapper.** Microsoft does not expose a stable PowerShell surface to add indicators, link alerts, attach evidence files, or assign reviewers to an IRM case. Closing or deleting an IRM case is a portal action and is recorded under `InsiderRiskManagementCaseUpdated` in the UAL — let the portal do it and capture the audit row. Wrapping `Remove-ComplianceCase` for an IRM case is technically possible but is not aligned with the IRM investigative workflow (cases are typically resolved, not deleted) and is intentionally omitted here.

---

## 6. End-to-end evidence run

This is the canonical Control 1.12 evidence sweep — pre-flight, role-group snapshot, UAL sweep, Graph beta cases, Graph beta alerts, all under a transcript and a single manifest.

```powershell
# Session: IPPS + Microsoft Graph
$ErrorActionPreference = 'Stop'

# 0. Pre-flight
$ctx = Initialize-Irm112Session -UserPrincipalName admin@contoso.com -Cloud Commercial

# 1. Evidence root — should be a WORM-eligible path (Purview retention lock or Azure Storage immutability)
$evidenceRoot = "\\wormshare\fsi-evidence\1.12\$(Get-Date -Format 'yyyy-MM-dd')"
New-Item -ItemType Directory -Force -Path $evidenceRoot | Out-Null

# 2. Transcript covers the entire run
$transcriptPath = Join-Path $evidenceRoot "1.12-transcript-$(Get-Date -Format 'yyyyMMddTHHmmssZ').txt"
Start-Transcript -Path $transcriptPath -IncludeInvocationHeader

try {
    # 3. Role-group snapshot
    $rg = Get-Irm112RoleGroupSnapshot -OutputDirectory $evidenceRoot

    # 4. UAL sweep — last 90 days
    $ual = Get-Irm112AuditEvidence `
        -StartUtc (Get-Date).ToUniversalTime().AddDays(-90) `
        -EndUtc   (Get-Date).ToUniversalTime() `
        -OutputDirectory $evidenceRoot

    # 5. Graph beta — cases and alerts
    $cases  = Get-Irm112Cases  -OutputDirectory $evidenceRoot -GraphHost $ctx.GraphHost -IncludePseudonymizedExport
    $alerts = Get-Irm112Alerts -OutputDirectory $evidenceRoot -GraphHost $ctx.GraphHost -IncludePseudonymizedExport

    # 6. Per-run manifest tying every artifact together
    $manifest = [PSCustomObject]@{
        runId            = [guid]::NewGuid().Guid
        control          = '1.12'
        artifact         = 'irm-evidence-pack'
        tenantId         = $ctx.TenantId
        cloud            = $ctx.Cloud
        ippsUri          = $ctx.IppsUri
        graphEnv         = $ctx.GraphEnv
        operatorUpn      = $ctx.Caller
        matchedRoleGroup = $ctx.MatchedRoleGroup
        irmCapableSkus   = $ctx.IrmCapableSkus
        modules          = @{
            ExchangeOnlineManagement       = $ctx.ExoModuleVersion
            'Microsoft.Graph.Authentication' = $ctx.GraphModuleVersion
        }
        components       = @{
            roleGroups = $rg.runId
            ual        = $ual.runId
            cases      = $cases.runId
            alerts     = $alerts.runId
        }
        files            = (Get-ChildItem $evidenceRoot -File | ForEach-Object {
            @{
                file   = $_.Name
                bytes  = $_.Length
                sha256 = if ($_.Extension -eq '.sha256') { $null } else { (Get-FileHash $_.FullName -Algorithm SHA256).Hash }
            }
        })
        startedUtc       = $ctx.ConnectedAtUtc.ToString('o')
        completedUtc     = (Get-Date).ToUniversalTime().ToString('o')
    }
    $manifestPath = Join-Path $evidenceRoot "1.12-manifest-$(Get-Date -Format 'yyyyMMddTHHmmssZ').json"
    $manifest | ConvertTo-Json -Depth 8 | Set-Content -Path $manifestPath -Encoding UTF8
    $manifestHash = (Get-FileHash -Path $manifestPath -Algorithm SHA256).Hash
    Set-Content -Path "$manifestPath.sha256" -Value $manifestHash -Encoding ASCII

    Write-Host "[PASS] Control 1.12 evidence pack written to $evidenceRoot" -ForegroundColor Green
}
catch {
    Write-Host "[FAIL] Control 1.12 evidence run aborted: $($_.Exception.Message)" -ForegroundColor Red
    throw
}
finally {
    Stop-Transcript | Out-Null
}
```

---

## 7. HR connector — read-only status reference

The Microsoft 365 HR connector is a key **non-Microsoft signal source** for IRM (resignation date, job-level changes, performance-improvement-plan flag). There is no supported PowerShell cmdlet that returns HR connector run history (last successful upload timestamp, file row count, schema validation errors). Treat HR connector status as **portal-only** today:

1. Microsoft Purview portal → **Data connectors** → **Connectors** → filter on **HR**.
2. For each HR connector, capture a screenshot of the **Status** tab (last upload UTC, last upload row count, validation errors over the last 30 days) and land it next to the rest of the 1.12 evidence pack.
3. The audit log records HR connector **configuration** changes (`InsiderRiskManagementSettingsUpdated` with the relevant target) but **not** row-level ingestion. Use Section 3's UAL collector to capture configuration drift; supplement with the portal screenshot for ingestion health.

> **Compensating telemetry.** If your tenant cannot stand up the Microsoft 365 HR connector (common in GCC High / DoD), document the gap as a Control 1.12 exception and substitute one of: (a) a custom Graph connector pushing HR signals into Microsoft Sentinel and feeding Sentinel UEBA (Control 1.6 / Control 1.7 cross-link), (b) Microsoft Defender for Cloud Apps anomaly detections on HR-relevant SaaS (Workday, ADP, SuccessFactors), (c) a Communication Compliance ([Control 1.10](../../../controls/pillar-1-security/1.10-communication-compliance-monitoring.md)) policy scoped to departing-user activity. These are **complementary**, not equivalent — record the gap in your control register.

---

## 8. Sovereign cloud reference

Verified against Microsoft Learn — [Connect to Security & Compliance PowerShell](https://learn.microsoft.com/en-us/powershell/exchange/connect-to-scc-powershell) and [Microsoft Graph national cloud deployments](https://learn.microsoft.com/en-us/graph/deployments) (last verified April 2026). **Reverify before each change window — Microsoft has rotated the GCC High and DoD endpoints multiple times in the last 24 months.**

| Cloud | IPPS `-ConnectionUri` | IPPS `-AzureADAuthorizationEndpointUri` | Graph host | `Connect-MgGraph -Environment` |
|---|---|---|---|---|
| Commercial / GCC | `https://ps.compliance.protection.outlook.com/powershell-liveid/` (default — can be omitted) | `https://login.microsoftonline.com/organizations` (default) | `https://graph.microsoft.com` | `Global` |
| GCC High | `https://ps.compliance.protection.office365.us/powershell-liveid/` | `https://login.microsoftonline.us/organizations` | `https://graph.microsoft.us` | `USGov` |
| DoD | `https://l5.ps.compliance.protection.office365.us/powershell-liveid/` | `https://login.microsoftonline.us/organizations` | `https://dod-graph.microsoft.us` | `USGovDoD` |

```powershell
# Commercial / GCC
Connect-IPPSSession -UserPrincipalName $upn
Connect-MgGraph -Environment Global -Scopes 'InsiderRiskManagement.Read.All','SecurityAlert.Read.All','Organization.Read.All'

# GCC High
Connect-IPPSSession -UserPrincipalName $upn `
    -ConnectionUri 'https://ps.compliance.protection.office365.us/powershell-liveid/' `
    -AzureADAuthorizationEndpointUri 'https://login.microsoftonline.us/organizations'
Connect-MgGraph -Environment USGov -Scopes 'InsiderRiskManagement.Read.All','SecurityAlert.Read.All','Organization.Read.All'

# DoD
Connect-IPPSSession -UserPrincipalName $upn `
    -ConnectionUri 'https://l5.ps.compliance.protection.office365.us/powershell-liveid/' `
    -AzureADAuthorizationEndpointUri 'https://login.microsoftonline.us/organizations'
Connect-MgGraph -Environment USGovDoD -Scopes 'InsiderRiskManagement.Read.All','SecurityAlert.Read.All','Organization.Read.All'
```

!!! danger "IRM availability in US Government clouds is limited"

    Per Microsoft Learn ([Adaptive Protection in Microsoft Purview](https://learn.microsoft.com/en-us/purview/insider-risk-management-adaptive-protection)) and the [Insider Risk Management overview](https://learn.microsoft.com/en-us/purview/insider-risk-management), several IRM capabilities — including **Adaptive Protection**, **Risky AI usage**, **Risky Agents**, and **Risky browser usage** — have **limited or no availability** in GCC, GCC High, and DoD. The Microsoft Graph beta endpoints used in [Section 4](#4-microsoft-graph-beta-read-irm-cases-and-alerts) may also have reduced or absent surface in those clouds.

    **Operationally, this means:**

    - A zero-row response from `Get-Irm112AuditEvidence`, `Get-Irm112Cases`, or `Get-Irm112Alerts` in a gov-cloud tenant is **not** evidence of a clean tenant — it may be evidence that the capability is not present.
    - The `Initialize-Irm112Session` helper emits a hard `Write-Warning` when the cloud is GCC / GCC High / DoD; **do not suppress it** in your evidence pipeline.
    - Document the gap as a Control 1.12 exception in your control register and apply compensating controls: [Control 1.10 (Communication Compliance)](../../../controls/pillar-1-security/1.10-communication-compliance-monitoring.md), [Control 1.7 (Comprehensive Audit Logging)](../../../controls/pillar-1-security/1.7-comprehensive-audit-logging-and-compliance.md), [Control 1.5 (DLP and Sensitivity Labels)](../../../controls/pillar-1-security/1.5-data-loss-prevention-dlp-and-sensitivity-labels.md), Microsoft Defender for Cloud Apps, and Microsoft Sentinel UEBA.
    - **Never use commercial endpoints from a sovereign tenant.** The cmdlet will appear to succeed (it authenticates against commercial AAD), but every IRM audit query and Graph beta call returns zero rows — producing **false-clean** evidence.

---

## 9. Anti-patterns (what NOT to do)

These are the patterns most likely to produce silent or fabricated evidence for Control 1.12. Reject any of them in PR review.

1. **Calling `Get-InsiderRiskPolicy`, `Get-InsiderRiskAlert`, `Get-InsiderRiskPriorityUserGroup`, or any `New-/Set-/Remove-InsiderRisk*` cmdlet.** **None of these cmdlets exist on Microsoft Learn.** The cmdlet will fail with `CommandNotFoundException`. Any prior version of this playbook that suppressed the error with `-ErrorAction SilentlyContinue` and emitted a `[PASS]` banner produced fabricated evidence. Verify every cmdlet against Microsoft Learn or `Get-Command` before writing it.
2. **Single-call `Search-UnifiedAuditLog -ResultSize 5000` for IRM operations.** Silently truncates at 5,000 rows. **Always** use the session-paging loop in Section 3 and hard-fail at the per-session ceiling.
3. **`-ErrorAction SilentlyContinue` on a tenant-mutation cmdlet** (`New-ComplianceCase`, `Add-RoleGroupMember`, `Remove-RoleGroupMember`) followed by a hard-coded `[PASS]` banner. This is the single most common pattern that produces fabricated evidence. Use `-ErrorAction Stop` in `try/catch` and emit the result row only after a verified after-snapshot, as in Section 5.
4. **Running IRM role-group cmdlets from `Connect-ExchangeOnline`** instead of `Connect-IPPSSession`. Exchange `Get-RoleGroup` exists but resolves a **different** role-group catalog and silently returns 0 hits for `*Insider Risk*`.
5. **Treating zero rows in a gov-cloud tenant as evidence of a clean tenant.** IRM and Adaptive Protection have limited availability in GCC / GCC High / DoD — see [Section 8](#8-sovereign-cloud-reference). The `Initialize-Irm112Session` warning is mandatory, not advisory.
6. **Attempting to script the unmask step** for pseudonymized identifiers in IRM cases or alerts. Unmasking is a portal action under audit; attempting to automate it bypasses the audit row that auditors rely on. Use the `-IncludePseudonymizedExport` posture in Section 4 and keep unmasking in the portal.
7. **Plain `Export-Csv` with no SHA-256 sidecar and no immutability target.** Spreadsheet exports are not audit evidence under SEC 17a-4(b)(4). Land artifacts in a WORM-eligible store (Purview retention lock or Azure Storage immutability) and emit a SHA-256 sidecar — see Section 6.
8. **No `Start-Transcript`.** Without a transcript, you cannot prove which cmdlets ran, against which tenant, by which principal, in which order. Every end-to-end run starts with `Start-Transcript` and ends with `Stop-Transcript` — see Section 6.
9. **No pre-flight role check.** UAL queries scoped to IRM operations may return an empty page (no error) when the caller lacks IRM role membership. Without the `Initialize-Irm112Session` membership assertion, a zero-row file looks identical to a clean tenant.
10. **No module version pin.** Floating `Install-Module` upgrades break reproducibility across change windows; `Microsoft.Graph.Authentication` in particular has shipped breaking changes to `Invoke-MgGraphRequest` parameter names. Pin both `ExchangeOnlineManagement` and `Microsoft.Graph.Authentication` versions in your CAB ticket.
11. **Asserting `New-ComplianceCase -CaseType InsiderRisk` configures a policy or attaches indicators.** It does neither. It creates an empty case shell. Indicator attachment, alert linkage, and reviewer assignment are portal-only on the case's blade.
12. **Treating IRM artifacts as books-and-records storage.** IRM cases, alerts, and Forensic Evidence clips are **working investigative artifacts** — Forensic Evidence clips auto-delete 120 days after capture unless exported. Books-and-records retention under SEC 17a-4 / FINRA 4511 is the responsibility of [Control 1.9 (Data Retention and Deletion Policies)](../../../controls/pillar-1-security/1.9-data-retention-and-deletion-policies.md). Cross-link in your change ticket.
13. **Shipping `Get-DataClassificationConnector` or any other speculative HR-connector cmdlet name.** As of the last verification date in the footer of this playbook, there is no supported PowerShell cmdlet that returns HR connector ingestion history. Treat HR connector status as portal-only — Section 7.
14. **Hard-coded admin UPN lists committed to source control.** Pass principals via parameters or pull from an Entra group; do not ship UPNs in playbook code.

---

## 10. Records-retention boundary

**IRM artifacts are NOT SEC 17a-4(b)(4) records storage.** Insider Risk Management is a detection and investigation surface — its alerts, cases, and Forensic Evidence clips are working investigative artifacts. Forensic Evidence clips in particular **auto-delete 120 days after capture** unless explicitly exported. Books-and-records retention under SEC 17a-4(b)(4), FINRA 4511, and CFTC Rule 1.31 is the responsibility of [Control 1.9 (Data Retention and Deletion Policies)](../../../controls/pillar-1-security/1.9-data-retention-and-deletion-policies.md) and the underlying [Control 1.7 (Comprehensive Audit Logging)](../../../controls/pillar-1-security/1.7-comprehensive-audit-logging-and-compliance.md).

For Control 1.12 specifically:

- **Land all evidence pack outputs** from Section 6 in a WORM-eligible store (Microsoft Purview retention-lock policy on a SharePoint Online library, or an Azure Storage container with an immutability policy). The local file system is **not** a retention store.
- **The SHA-256 sidecars** emitted by every collector in this playbook provide content-integrity evidence; they do **not** provide WORM. Pair them with the immutability target.
- **Reference the storage path** (and the retention-lock policy ID or Azure Storage immutability policy ID) in the change ticket that authorizes the evidence run.
- **For Forensic Evidence clips** specifically, if a clip is needed as a long-term artifact, export it from the IRM case before the 120-day auto-deletion and land the export in the same WORM-eligible store. The export action is recorded as `InsiderRiskManagementWorkflowExecuted` in the UAL — capture that audit row alongside the clip.

---

## 11. Cross-links

| Concern | Control |
|---|---|
| Records retention / WORM landing for IRM evidence artifacts and Forensic Evidence clip exports | [Control 1.9 — Data Retention and Deletion Policies](../../../controls/pillar-1-security/1.9-data-retention-and-deletion-policies.md) |
| Tenant-wide audit ingestion (`UnifiedAuditLogIngestionEnabled`) — pre-requisite for IRM signal capture | [Control 1.7 — Comprehensive Audit Logging](../../../controls/pillar-1-security/1.7-comprehensive-audit-logging-and-compliance.md) |
| DLP and Sensitivity Labels — signal source for IRM and target of Adaptive Protection | [Control 1.5 — DLP and Sensitivity Labels](../../../controls/pillar-1-security/1.5-data-loss-prevention-dlp-and-sensitivity-labels.md) |
| DSPM signals for Copilot and agent grounding data — feeds IRM Risky AI usage / Risky Agents | [Control 1.6 — Microsoft Purview DSPM for AI](../../../controls/pillar-1-security/1.6-microsoft-purview-dspm-for-ai.md) |
| Communication Compliance — adjacent supervisory surface, compensating control for gov-cloud IRM gaps | [Control 1.10 — Communication Compliance Monitoring](../../../controls/pillar-1-security/1.10-communication-compliance-monitoring.md) |
| eDiscovery holds against IRM case content | [Control 1.19 — eDiscovery for Agent Interactions](../../../controls/pillar-1-security/1.19-ediscovery-for-agent-interactions.md) |
| Identity & access for IRM role-group assignments | [Control 1.2 — Agent Registry and Integrated Apps Management](../../../controls/pillar-1-security/1.2-agent-registry-and-integrated-apps-management.md) |

**Microsoft Learn references (verify before each change window):**

- [Insider Risk Management — Overview](https://learn.microsoft.com/en-us/purview/insider-risk-management)
- [Insider Risk Management — Get started](https://learn.microsoft.com/en-us/purview/insider-risk-management-configure)
- [Insider Risk Management — Permissions](https://learn.microsoft.com/en-us/purview/insider-risk-management-permissions)
- [Insider Risk Management — Adaptive Protection (gov-cloud availability)](https://learn.microsoft.com/en-us/purview/insider-risk-management-adaptive-protection)
- [Insider Risk Management — Forensic Evidence](https://learn.microsoft.com/en-us/purview/insider-risk-management-forensic-evidence)
- [Audit log activities](https://learn.microsoft.com/en-us/purview/audit-log-activities)
- [`Search-UnifiedAuditLog`](https://learn.microsoft.com/en-us/powershell/module/exchange/search-unifiedauditlog)
- [`New-ComplianceCase`](https://learn.microsoft.com/en-us/powershell/module/exchange/new-compliancecase)
- [`Get-RoleGroupMember`](https://learn.microsoft.com/en-us/powershell/module/exchange/get-rolegroupmember)
- [Connect to Security & Compliance PowerShell](https://learn.microsoft.com/en-us/powershell/exchange/connect-to-scc-powershell)
- [Connect to Exchange Online PowerShell (sovereign endpoints)](https://learn.microsoft.com/en-us/powershell/exchange/connect-to-exchange-online-powershell)
- [Microsoft Graph beta — `insiderRiskCase` resource](https://learn.microsoft.com/en-us/graph/api/resources/security-insiderriskcase?view=graph-rest-beta)
- [Microsoft Graph beta — `alerts_v2` list](https://learn.microsoft.com/en-us/graph/api/security-alert-list?view=graph-rest-beta)
- [Microsoft Graph national cloud deployments](https://learn.microsoft.com/en-us/graph/deployments)

---

## Related playbooks

- [Portal Walkthrough](./portal-walkthrough.md) — step-by-step Purview portal configuration (the authoritative surface for IRM policy / settings / role-group / Adaptive Protection / Forensic Evidence administration).
- [Verification & Testing](./verification-testing.md) — test cases and evidence-collection criteria.
- [Troubleshooting](./troubleshooting.md) — common issues including the `CommandNotFoundException` failure mode for the fabricated `Get-InsiderRiskPolicy` / `Get-InsiderRiskAlert` / `Get-InsiderRiskPriorityUserGroup` cmdlets.

---

*Updated: April 2026 | Version: v1.4 | UI Verification Status: Current*
