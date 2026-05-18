# Control 1.10 — PowerShell Setup: Communication Compliance Monitoring

**Control:** [1.10 Communication Compliance Monitoring](../../../controls/pillar-1-security/1.10-communication-compliance-monitoring.md)
**Baseline:** [PowerShell baseline (`_shared/powershell-baseline.md`)](../../_shared/powershell-baseline.md)
**Audience:** M365 administrator at a US financial services organization (FINRA / SEC / GLBA / OCC / Fed SR 26-2 (formerly SR 11-7) / CFTC oversight) operating Microsoft 365 Copilot, Agent Builder, and Copilot Studio agents.
**Sovereign clouds:** Commercial / GCC / GCC High / DoD — connection helper in [Section 1](#1-pre-flight) and full reference in [Section 7](#7-sovereign-cloud-reference).
**Required modules:** `ExchangeOnlineManagement` ≥ 3.5.0 (provides both `Connect-ExchangeOnline` and `Connect-IPPSSession`).

!!! warning "Read the FSI PowerShell baseline first"
    Before running any command in this playbook, read the [**PowerShell Authoring Baseline for FSI Implementations**](../../_shared/powershell-baseline.md). It is the canonical source for module version pinning, sovereign-cloud (GCC / GCC High / DoD) endpoints, mutation safety (`-WhatIf` / `SupportsShouldProcess`), transcript capture, and SHA-256 evidence emission. Snippets below assume you have already complied with that baseline.

> **Scope of this file.** PowerShell automation for **Microsoft Purview Communication Compliance (CC)** as it applies to Copilot, Agent Builder, and Copilot Studio agent communications. PowerShell coverage for CC is **deliberately partial**:
>
> - **PowerShell *is not* supported for creating, updating, or deleting Communication Compliance policies, classifiers, OCR settings, priority user groups, adaptive scopes, or reviewer dispositions.** All CC policy CRUD must be performed in the Microsoft Purview portal. See Microsoft Learn — [Create and manage communication compliance policies](https://learn.microsoft.com/en-us/purview/communication-compliance-policies).
> - **PowerShell *is* supported for the legacy *Supervisory Review* family** (`*-SupervisoryReviewPolicyV2`, `*-SupervisoryReviewRule`, `Get-SupervisoryReviewActivity`, `Get-SupervisoryReviewReport`). Supervisory Review is the cmdlet surface that backs the older Microsoft 365 supervision policies and remains the authoritative PowerShell-accessible source of reviewer activity for evidence collection.
> - **Audit Log evidence** (`Search-UnifiedAuditLog` for `SupervisionRuleMatch`, `SupervisionPolicyCreated`, `SupervisionPolicyUpdated`, `SupervisionPolicyDeleted`, `SupervisoryReviewTag`) is the cross-cutting evidence path used by FSI auditors when they need a tenant-wide event stream rather than per-policy reviewer activity.
>
> **Do not** treat this playbook as a substitute for portal-driven CC policy administration. Treat it as the **evidence, reconciliation, and supervisory-review automation layer** for Control 1.10.

---

## 0. Wrong-shell trap (READ FIRST)

Communication Compliance and Supervisory Review cmdlets live in **two separate PowerShell sessions**. Running a cmdlet in the wrong session produces either a `CommandNotFoundException` or, worse, **silent zero results that look like clean evidence**. Every script block in this playbook is labelled with its required session — do not strip those labels when copying.

| Cmdlet family | Required session | Module | If you run it in the wrong session |
|---|---|---|---|
| `*-SupervisoryReviewPolicyV2`, `*-SupervisoryReviewRule`, `Get-SupervisoryReviewActivity`, `Get-SupervisoryReviewReport` | `Connect-IPPSSession` (Security & Compliance / IPPS) | `ExchangeOnlineManagement` | `CommandNotFoundException` from `Connect-ExchangeOnline`. |
| `Search-UnifiedAuditLog` for **CC operations** (`Supervision*`, `SupervisoryReviewTag`) | `Connect-IPPSSession` (IPPS) | `ExchangeOnlineManagement` | Returns rows from `Connect-ExchangeOnline` for some record types but **silently misses** Communication Compliance operations indexed only on the IPPS endpoint. |
| `Get-RoleGroup`, `Get-RoleGroupMember`, `Add-RoleGroupMember`, `Remove-RoleGroupMember` for *Communication Compliance* role groups | `Connect-IPPSSession` (IPPS) | `ExchangeOnlineManagement` | Exchange `Get-RoleGroup` exists but resolves a **different** role-group catalog and silently returns 0 hits for `*Communication Compliance*`. |
| `Get-AdminAuditLogConfig` (to verify `UnifiedAuditLogIngestionEnabled`) | `Connect-ExchangeOnline` | `ExchangeOnlineManagement` | From `Connect-IPPSSession`, returns `False` for `UnifiedAuditLogIngestionEnabled` even when audit ingestion is on — Control 1.7 evidence becomes false-clean. |

> Always assert session state at the top of every script via `Get-ConnectionInformation` (provided by `ExchangeOnlineManagement` 3.x). The `Initialize-Cc110Session` helper in [Section 1](#1-pre-flight) does this for you.

---

## 1. Pre-flight

Every Control 1.10 PowerShell session **must** start with the same five steps:

1. Pin the `ExchangeOnlineManagement` module version (CAB-approved).
2. Resolve sovereign-cloud connection parameters from a single switch.
3. Connect to **IPPS** (Security & Compliance) — supervisory review and CC audit operations are IPPS-only.
4. Verify the caller is a member of `Communication Compliance Admins` (and optionally `Communication Compliance Investigators` for evidence collection runs).
5. Verify the tenant has the licensing required for Communication Compliance (Microsoft 365 E5 / E5 Compliance / Insider Risk Management add-on).

The helper below is a single drop-in pre-flight. Save it as `Initialize-Cc110Session.ps1` in your evidence-collection module.

```powershell
#Requires -Version 7.2
#Requires -Modules @{ ModuleName = 'ExchangeOnlineManagement'; RequiredVersion = '3.5.0' }

function Initialize-Cc110Session {
    <#
    .SYNOPSIS
        Pre-flight for Control 1.10 (Communication Compliance Monitoring).
    .DESCRIPTION
        Resolves sovereign endpoint, opens an IPPS session if not already
        connected, asserts module version pin, asserts caller role membership
        (Communication Compliance Admins), and emits a session-state PSCustomObject
        for downstream scripts to consume. Read-only — no tenant mutation.
    .PARAMETER UserPrincipalName
        UPN used to authenticate to IPPS.
    .PARAMETER Cloud
        Microsoft 365 cloud the tenant is in. Default: Commercial.
    .PARAMETER RequiredRoleGroup
        Role group caller must be a member of. Default: 'Communication Compliance Admins'.
    .EXAMPLE
        $ctx = Initialize-Cc110Session -UserPrincipalName admin@contoso.com -Cloud GCCHigh
    #>
    [CmdletBinding()]
    param(
        [Parameter(Mandatory)] [string] $UserPrincipalName,
        [ValidateSet('Commercial','GCC','GCCHigh','DoD')]
        [string] $Cloud = 'Commercial',
        [string] $RequiredRoleGroup = 'Communication Compliance Admins'
    )

    $ErrorActionPreference = 'Stop'

    # 1. Module pin assertion
    $exo = Get-Module -ListAvailable -Name ExchangeOnlineManagement |
           Sort-Object Version -Descending | Select-Object -First 1
    if (-not $exo) {
        throw "ExchangeOnlineManagement module not installed. Install pinned version per CAB approval."
    }
    if ($exo.Version -lt [version]'3.5.0') {
        throw "ExchangeOnlineManagement $($exo.Version) is below the 3.5.0 minimum required for IPPS REST + CC operations."
    }

    # 2. Resolve sovereign endpoint
    $endpoint = switch ($Cloud) {
        'Commercial' { @{ Uri = 'https://ps.compliance.protection.outlook.com/powershell-liveid/'
                          Aad = 'https://login.microsoftonline.com/organizations' } }
        'GCC'        { @{ Uri = 'https://ps.compliance.protection.outlook.com/powershell-liveid/'
                          Aad = 'https://login.microsoftonline.com/organizations' } }
        'GCCHigh'    { @{ Uri = 'https://ps.compliance.protection.office365.us/powershell-liveid/'
                          Aad = 'https://login.microsoftonline.us/organizations' } }
        'DoD'        { @{ Uri = 'https://l5.ps.compliance.protection.office365.us/powershell-liveid/'
                          Aad = 'https://login.microsoftonline.us/organizations' } }
    }

    # 3. Open IPPS session (idempotent — only connects if no live IPPS session)
    $existing = Get-ConnectionInformation -ErrorAction SilentlyContinue |
                Where-Object { $_.ConnectionUri -like '*compliance.protection*' -and $_.State -eq 'Connected' }
    if (-not $existing) {
        Connect-IPPSSession `
            -UserPrincipalName $UserPrincipalName `
            -ConnectionUri $endpoint.Uri `
            -AzureADAuthorizationEndpointUri $endpoint.Aad | Out-Null
    }

    # 4. Role membership check (caller must be in $RequiredRoleGroup)
    $callerUpn = $UserPrincipalName
    $members = Get-RoleGroupMember -Identity $RequiredRoleGroup -ErrorAction Stop
    $isMember = $members | Where-Object {
        $_.PrimarySmtpAddress -eq $callerUpn -or $_.WindowsLiveID -eq $callerUpn -or $_.Name -eq $callerUpn
    }
    if (-not $isMember) {
        throw "Caller $callerUpn is not a member of '$RequiredRoleGroup'. Communication Compliance cmdlets will fail or return partial results."
    }

    # 5. License surface check (informational — CC requires E5/E5 Compliance/IRM add-on)
    # Licensing detail belongs in Control 2.1; here we only flag the CC service plan.
    $ccPolicies = Get-SupervisoryReviewPolicyV2 -ErrorAction SilentlyContinue
    if ($null -eq $ccPolicies) {
        Write-Warning "Get-SupervisoryReviewPolicyV2 returned null. Tenant may lack the Communication Compliance / Insider Risk Management license. Verify in Microsoft 365 admin center before treating zero results as evidence."
    }

    [PSCustomObject]@{
        Cloud            = $Cloud
        ConnectionUri    = $endpoint.Uri
        Aad              = $endpoint.Aad
        Caller           = $callerUpn
        RequiredRoleGroup= $RequiredRoleGroup
        ModuleVersion    = $exo.Version.ToString()
        ConnectedAtUtc   = (Get-Date).ToUniversalTime()
        TenantId         = (Get-ConnectionInformation | Select-Object -First 1).TenantID
    }
}
```

> **Why role membership is a hard pre-flight.** `Get-SupervisoryReviewPolicyV2` returns an **empty list** without throwing when the caller lacks permission. Without the membership assertion, an unauthorized run produces a zero-row evidence file that looks identical to a tenant with no policies — the exact pattern auditors flag as **fabricated false-clean evidence**.

---

## 2. PowerShell coverage boundary — what the shell can and cannot do for CC

This table is the single source of truth for what belongs in PowerShell vs. what belongs in the Microsoft Purview portal for Control 1.10. It is paraphrased from Microsoft Learn — [Communication Compliance — Create and manage policies](https://learn.microsoft.com/en-us/purview/communication-compliance-policies) and [Permissions](https://learn.microsoft.com/en-us/purview/communication-compliance-permissions). Reverify before each change window — Microsoft has been moving CC functionality between surfaces.

| Capability | PowerShell? | Where it lives |
|---|---|---|
| Create / update / delete Communication Compliance policies (modern CC, including Copilot interactions template) | **No** | Microsoft Purview portal → Communication compliance → Policies |
| Configure trainable classifiers on a CC policy | **No** | Purview portal |
| Configure OCR on a CC policy | **No** | Purview portal |
| Configure Priority User Groups | **No** | Purview portal |
| Configure adaptive scopes assigned to a CC policy | **No** (use Purview portal for the assignment; adaptive scope objects themselves are PS-accessible via `Get-AdaptiveScope` for inventory only) | Purview portal |
| Reviewer disposition in the alert queue (resolve / escalate / tag) | **No** | Purview portal |
| Read / export reviewer activity for a **supervisory review** policy | **Yes** — `Get-SupervisoryReviewActivity -PolicyId -StartDate -EndDate` | IPPS PowerShell |
| Generate the supervisory review report | **Yes** — `Get-SupervisoryReviewReport` | IPPS PowerShell |
| Inventory supervisory review policies / rules | **Yes** — `Get-SupervisoryReviewPolicyV2`, `Get-SupervisoryReviewRule` | IPPS PowerShell |
| Create a supervisory review policy or rule (legacy supervision surface, still PS-supported) | **Yes** — `New-SupervisoryReviewPolicyV2`, `New-SupervisoryReviewRule` | IPPS PowerShell |
| Audit-log evidence stream for CC operations (`SupervisionRuleMatch`, `SupervisionPolicyCreated`, `SupervisionPolicyUpdated`, `SupervisionPolicyDeleted`, `SupervisoryReviewTag`) | **Yes** — `Search-UnifiedAuditLog` (paged) | IPPS PowerShell (UAL via IPPS endpoint) |
| Communication Compliance role-group membership (Admins / Investigators / Analysts / Viewers) | **Yes** — `Get-RoleGroup`, `Get-RoleGroupMember`, `Add-RoleGroupMember`, `Remove-RoleGroupMember` | IPPS PowerShell |
| Configure tenant-wide audit ingestion (`UnifiedAuditLogIngestionEnabled`) | **Yes** — but that is **Control 1.7**, not 1.10 | Exchange Online PowerShell |

> **Do not promote PowerShell as a substitute for portal CC policy CRUD.** If a sub-script in this playbook appears to "create a CC policy" via `New-SupervisoryReviewPolicyV2`, it is creating a **supervisory review** policy — a related but distinct object surface. Use it deliberately and document the choice in your change ticket.

---

## 3. Inventory (read-only)

All commands in this section run from **`Connect-IPPSSession`** (use `Initialize-Cc110Session` first). Output is read-only and safe to run during business hours.

### 3.1 Inventory supervisory review policies

```powershell
# Session: IPPS
$ctx = Initialize-Cc110Session -UserPrincipalName $env:USERPRINCIPALNAME -Cloud Commercial

$policies = Get-SupervisoryReviewPolicyV2 -ErrorAction Stop

$policies |
    Select-Object Name, Enabled, Reviewers, PreservationPeriodInDays, UserReportingWorkloads, WhenCreatedUTC, WhenChangedUTC, Guid |
    Sort-Object Name |
    Format-Table -AutoSize
```

> **Schema reference.** `New-SupervisoryReviewPolicyV2` defines reviewers via `-Reviewers <String[]>` (an array of UPNs). Reviewer assignment **lives on the policy**, not on the rule. If you see a script using `-ReviewerEmail`, it is wrong — that parameter does not exist.

### 3.2 Inventory supervisory review rules per policy

```powershell
# Session: IPPS
foreach ($p in $policies) {
    $rules = Get-SupervisoryReviewRule -Policy $p.Guid -ErrorAction SilentlyContinue
    [PSCustomObject]@{
        PolicyName  = $p.Name
        PolicyGuid  = $p.Guid
        RuleCount   = ($rules | Measure-Object).Count
        Rules       = $rules | Select-Object Name, SamplingRate, ContentSources, Condition, Ocr
    }
} | ConvertTo-Json -Depth 6
```

### 3.3 Snapshot Communication Compliance role-group membership

```powershell
# Session: IPPS
$ccRoleGroups = @(
    'Communication Compliance',
    'Communication Compliance Admins',
    'Communication Compliance Analysts',
    'Communication Compliance Investigators',
    'Communication Compliance Viewers'
)

$snapshot = foreach ($g in $ccRoleGroups) {
    $rg = Get-RoleGroup -Identity $g -ErrorAction SilentlyContinue
    if (-not $rg) {
        [PSCustomObject]@{ RoleGroup = $g; Exists = $false; Members = @() }
        continue
    }
    $members = Get-RoleGroupMember -Identity $g -ErrorAction Stop |
               Select-Object Name, PrimarySmtpAddress, RecipientType
    [PSCustomObject]@{
        RoleGroup = $g
        Exists    = $true
        Members   = $members
        Count     = ($members | Measure-Object).Count
    }
}

$snapshot | ConvertTo-Json -Depth 5
```

> **Why all five role groups.** Microsoft consolidated the CC role groups in mid-2023 (the umbrella `Communication Compliance` role group was added). Tenants provisioned before that change still expose the four originals; tenants provisioned after may only expose the umbrella plus a subset. Snapshot all five so the diff between two evidence runs is unambiguous.

---

## 4. Supervisory review CRUD (state-changing)

These sections **modify tenant state**. Each function is wrapped in `[CmdletBinding(SupportsShouldProcess, ConfirmImpact='High')]`, captures a before-snapshot, and uses `-ErrorAction Stop` with try/catch — **never** `SilentlyContinue` on a mutation.

### 4.1 Create a supervisory review policy

```powershell
# Session: IPPS
function New-Cc110SupervisoryReviewPolicy {
    <#
    .SYNOPSIS
        Create a supervisory review policy with reviewers assigned at the policy level.
    .NOTES
        This is the *legacy supervision* surface. Modern Communication Compliance
        policies (including the Copilot interactions template) cannot be created
        via PowerShell — use the Purview portal. See Section 2 for the boundary.
    #>
    [CmdletBinding(SupportsShouldProcess, ConfirmImpact='High')]
    param(
        [Parameter(Mandatory)] [string]   $Name,
        [Parameter(Mandatory)] [string[]] $Reviewers,
        [int]    $PreservationPeriodInDays = 365,
        [string] $Comment = "Created by FSI Control 1.10 automation",
        [string] $EvidencePath = ".\evidence\1.10"
    )

    $ErrorActionPreference = 'Stop'
    New-Item -ItemType Directory -Force -Path $EvidencePath | Out-Null
    $ts = Get-Date -Format 'yyyyMMddTHHmmssZ'
    Start-Transcript -Path (Join-Path $EvidencePath "transcript-policy-create-$ts.log") -IncludeInvocationHeader

    try {
        # BEFORE snapshot
        $before = Get-SupervisoryReviewPolicyV2 -ErrorAction SilentlyContinue
        $before | ConvertTo-Json -Depth 6 | Set-Content (Join-Path $EvidencePath "before-policies-$ts.json") -Encoding UTF8

        if ($PSCmdlet.ShouldProcess("$Name", "Create supervisory review policy with $($Reviewers.Count) reviewer(s)")) {
            $created = New-SupervisoryReviewPolicyV2 `
                -Name $Name `
                -Reviewers $Reviewers `
                -PreservationPeriodInDays $PreservationPeriodInDays `
                -Comment $Comment `
                -ErrorAction Stop
        }

        # AFTER snapshot — only on success
        $after = Get-SupervisoryReviewPolicyV2 -Identity $Name -ErrorAction Stop
        $after | ConvertTo-Json -Depth 6 | Set-Content (Join-Path $EvidencePath "after-policy-$Name-$ts.json") -Encoding UTF8

        [PSCustomObject]@{
            Result      = 'PASS'
            PolicyName  = $after.Name
            PolicyGuid  = $after.Guid
            Reviewers   = $after.Reviewers
            CreatedAtUtc= (Get-Date).ToUniversalTime()
        }
    }
    catch {
        # No PASS banner — propagate the failure so the run is recorded as FAIL.
        Write-Error "Supervisory review policy creation FAILED for '$Name': $_"
        [PSCustomObject]@{
            Result    = 'FAIL'
            PolicyName= $Name
            Error     = $_.Exception.Message
        }
    }
    finally {
        Stop-Transcript | Out-Null
    }
}
```

### 4.2 Add a rule to a supervisory review policy

```powershell
# Session: IPPS
function Add-Cc110SupervisoryReviewRule {
    <#
    .SYNOPSIS
        Add a rule to an existing supervisory review policy.
    .NOTES
        New-SupervisoryReviewRule does NOT take -Reviewers; reviewers live on the
        policy (Section 4.1). This rule defines what content gets sampled and the
        sampling rate.
    #>
    [CmdletBinding(SupportsShouldProcess, ConfirmImpact='High')]
    param(
        [Parameter(Mandatory)] [string] $RuleName,
        [Parameter(Mandatory)] [string] $PolicyIdentity,   # accepts Name or Guid
        [ValidateRange(1,100)] [int] $SamplingRate = 10,
        [string[]] $ContentSources = @('Exchange','Teams'),
        [string]   $Condition,
        [bool]     $Ocr = $true,
        [string]   $EvidencePath = ".\evidence\1.10"
    )

    $ErrorActionPreference = 'Stop'
    New-Item -ItemType Directory -Force -Path $EvidencePath | Out-Null
    $ts = Get-Date -Format 'yyyyMMddTHHmmssZ'
    Start-Transcript -Path (Join-Path $EvidencePath "transcript-rule-create-$ts.log") -IncludeInvocationHeader

    try {
        $before = Get-SupervisoryReviewRule -Policy $PolicyIdentity -ErrorAction SilentlyContinue
        $before | ConvertTo-Json -Depth 6 | Set-Content (Join-Path $EvidencePath "before-rules-$ts.json") -Encoding UTF8

        if ($PSCmdlet.ShouldProcess("$RuleName on $PolicyIdentity", "Create supervisory review rule")) {
            $params = @{
                Name           = $RuleName
                Policy         = $PolicyIdentity
                SamplingRate   = $SamplingRate
                ContentSources = $ContentSources
                Ocr            = $Ocr
                ErrorAction    = 'Stop'
            }
            if ($Condition) { $params.Condition = $Condition }
            $created = New-SupervisoryReviewRule @params
        }

        $after = Get-SupervisoryReviewRule -Policy $PolicyIdentity -ErrorAction Stop
        $after | ConvertTo-Json -Depth 6 | Set-Content (Join-Path $EvidencePath "after-rules-$ts.json") -Encoding UTF8

        [PSCustomObject]@{ Result='PASS'; RuleName=$RuleName; Policy=$PolicyIdentity; SamplingRate=$SamplingRate }
    }
    catch {
        Write-Error "Supervisory review rule creation FAILED for '$RuleName' on '$PolicyIdentity': $_"
        [PSCustomObject]@{ Result='FAIL'; RuleName=$RuleName; Error=$_.Exception.Message }
    }
    finally {
        Stop-Transcript | Out-Null
    }
}
```

### 4.3 Update an existing supervisory review rule

```powershell
# Session: IPPS
function Set-Cc110SupervisoryReviewRule {
    [CmdletBinding(SupportsShouldProcess, ConfirmImpact='High')]
    param(
        [Parameter(Mandatory)] [string] $RuleIdentity,
        [int]      $SamplingRate,
        [string[]] $ContentSources,
        [string]   $Condition,
        [string]   $EvidencePath = ".\evidence\1.10"
    )

    $ErrorActionPreference = 'Stop'
    New-Item -ItemType Directory -Force -Path $EvidencePath | Out-Null
    $ts = Get-Date -Format 'yyyyMMddTHHmmssZ'
    Start-Transcript -Path (Join-Path $EvidencePath "transcript-rule-update-$ts.log") -IncludeInvocationHeader

    try {
        $before = Get-SupervisoryReviewRule -Identity $RuleIdentity -ErrorAction Stop
        $before | ConvertTo-Json -Depth 6 | Set-Content (Join-Path $EvidencePath "before-rule-$ts.json") -Encoding UTF8

        $params = @{ Identity = $RuleIdentity; ErrorAction = 'Stop' }
        if ($PSBoundParameters.ContainsKey('SamplingRate'))   { $params.SamplingRate   = $SamplingRate }
        if ($PSBoundParameters.ContainsKey('ContentSources')) { $params.ContentSources = $ContentSources }
        if ($PSBoundParameters.ContainsKey('Condition'))      { $params.Condition      = $Condition }

        if ($PSCmdlet.ShouldProcess($RuleIdentity, "Update supervisory review rule")) {
            Set-SupervisoryReviewRule @params
        }

        $after = Get-SupervisoryReviewRule -Identity $RuleIdentity -ErrorAction Stop
        $after | ConvertTo-Json -Depth 6 | Set-Content (Join-Path $EvidencePath "after-rule-$ts.json") -Encoding UTF8

        [PSCustomObject]@{ Result='PASS'; RuleIdentity=$RuleIdentity }
    }
    catch {
        Write-Error "Supervisory review rule update FAILED for '$RuleIdentity': $_"
        [PSCustomObject]@{ Result='FAIL'; RuleIdentity=$RuleIdentity; Error=$_.Exception.Message }
    }
    finally {
        Stop-Transcript | Out-Null
    }
}
```

### 4.4 Add or remove members from a CC role group

```powershell
# Session: IPPS
function Set-Cc110RoleGroupMembership {
    [CmdletBinding(SupportsShouldProcess, ConfirmImpact='High')]
    param(
        [Parameter(Mandatory)] [ValidateSet(
            'Communication Compliance',
            'Communication Compliance Admins',
            'Communication Compliance Analysts',
            'Communication Compliance Investigators',
            'Communication Compliance Viewers')]
        [string] $RoleGroup,
        [Parameter(Mandatory)] [ValidateSet('Add','Remove')] [string] $Action,
        [Parameter(Mandatory)] [string] $Member,
        [string] $EvidencePath = ".\evidence\1.10"
    )

    $ErrorActionPreference = 'Stop'
    New-Item -ItemType Directory -Force -Path $EvidencePath | Out-Null
    $ts = Get-Date -Format 'yyyyMMddTHHmmssZ'

    try {
        $before = Get-RoleGroupMember -Identity $RoleGroup -ErrorAction Stop
        $before | Select-Object Name, PrimarySmtpAddress |
            ConvertTo-Json -Depth 4 |
            Set-Content (Join-Path $EvidencePath "before-rg-$RoleGroup-$ts.json") -Encoding UTF8

        if ($PSCmdlet.ShouldProcess("$Member", "$Action $RoleGroup")) {
            switch ($Action) {
                'Add'    { Add-RoleGroupMember    -Identity $RoleGroup -Member $Member -ErrorAction Stop }
                'Remove' { Remove-RoleGroupMember -Identity $RoleGroup -Member $Member -Confirm:$false -ErrorAction Stop }
            }
        }

        $after = Get-RoleGroupMember -Identity $RoleGroup -ErrorAction Stop
        $after | Select-Object Name, PrimarySmtpAddress |
            ConvertTo-Json -Depth 4 |
            Set-Content (Join-Path $EvidencePath "after-rg-$RoleGroup-$ts.json") -Encoding UTF8

        $delta = Compare-Object -ReferenceObject $before -DifferenceObject $after -Property PrimarySmtpAddress
        [PSCustomObject]@{
            Result    = 'PASS'
            RoleGroup = $RoleGroup
            Action    = $Action
            Member    = $Member
            Delta     = $delta
        }
    }
    catch {
        Write-Error "Role-group membership change FAILED ($Action $Member on $RoleGroup): $_"
        [PSCustomObject]@{ Result='FAIL'; RoleGroup=$RoleGroup; Action=$Action; Member=$Member; Error=$_.Exception.Message }
    }
}
```

> **Why no `SilentlyContinue`.** The original Control 1.10 script suppressed `Add-RoleGroupMember` failures with `-ErrorAction SilentlyContinue` and then printed a hard-coded `[PASS]` banner. The result was an evidence file that always claimed success even when the cmdlet rejected the member (license missing, role-group locked, principal not found). Auditors treat that pattern as **fabricated evidence**. Always use `-ErrorAction Stop` in a `try/catch` and only emit a `PASS` row when the post-mutation state matches intent.

---

## 5. Evidence collection — Audit log and supervisory review activity

This section is the **audit-defensible evidence path** for Control 1.10. It runs read-only, captures a transcript, paginates the Unified Audit Log without silent truncation, calls `Get-SupervisoryReviewActivity` per policy, exports JSON + CSV, and writes a `manifest.json` with SHA-256 hashes.

### 5.1 Paged Unified Audit Log collector for CC operations

The CC operations indexed in the Unified Audit Log are (verified against Microsoft Learn — [Audit log activities § Communication compliance](https://learn.microsoft.com/en-us/purview/audit-log-activities)):

| Operation | Description |
|---|---|
| `SupervisionRuleMatch` | A user sent a message that matches a CC policy condition. |
| `SupervisionPolicyCreated` | A CC admin created a CC policy. |
| `SupervisionPolicyUpdated` | A CC admin updated a CC policy. |
| `SupervisionPolicyDeleted` | A CC admin deleted a CC policy. |
| `SupervisoryReviewTag` | A reviewer applied a tag to a message (Compliant / Non-compliant / Questionable / Resolved). |

> **Critical:** `Search-UnifiedAuditLog` is hard-capped at 5,000 rows per call. A single-call `-ResultSize 5000` **silently truncates** at the cap and returns no error. The collector below uses the documented session-paging pattern (`-SessionId <guid>` + `-SessionCommand ReturnLargeSet`), loops until an empty page returns, and **hard-fails** if the per-session ceiling (50,000 rows per session) is reached without exhaustion — at that point you must narrow the date window and re-run.

```powershell
# Session: IPPS
function Get-Cc110AuditEvidence {
    <#
    .SYNOPSIS
        Paged Unified Audit Log collector for Communication Compliance operations.
    .DESCRIPTION
        Iterates Search-UnifiedAuditLog using session-paging until an empty page
        is returned. Hard-fails if the per-session ceiling is hit without
        exhaustion (caller must narrow date range). Writes JSON + CSV with
        SHA-256 sidecars and updates manifest.json.
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
            'SupervisionRuleMatch',
            'SupervisionPolicyCreated',
            'SupervisionPolicyUpdated',
            'SupervisionPolicyDeleted',
            'SupervisoryReviewTag'
        )
    )

    $ErrorActionPreference = 'Stop'
    New-Item -ItemType Directory -Force -Path $OutputDirectory | Out-Null
    $runId = [guid]::NewGuid().Guid
    $ts    = Get-Date -Format 'yyyyMMddTHHmmssZ'
    Start-Transcript -Path (Join-Path $OutputDirectory "transcript-ual-$ts.log") -IncludeInvocationHeader

    try {
        $sessionId = "cc110-$runId"
        $all       = New-Object System.Collections.Generic.List[object]
        $pageIndex = 0
        $maxPages  = 10   # 10 pages × 5000 rows = 50,000 row session ceiling

        do {
            $pageIndex++
            $page = Search-UnifiedAuditLog `
                -StartDate $StartUtc `
                -EndDate   $EndUtc `
                -Operations $Operations `
                -SessionId $sessionId `
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

        # Emit JSON
        $jsonPath = Join-Path $OutputDirectory "ual-cc110-$ts.json"
        $all | ConvertTo-Json -Depth 10 | Set-Content -Path $jsonPath -Encoding UTF8

        # Emit CSV (flattened AuditData JSON for spreadsheet review — NOT a retention store)
        $csvPath = Join-Path $OutputDirectory "ual-cc110-$ts.csv"
        $all | Select-Object CreationDate, UserIds, Operations, RecordType, ResultIndex, ResultCount, Identity, AuditData |
            Export-Csv -Path $csvPath -NoTypeInformation -Encoding UTF8

        # Hashes + manifest
        $jsonHash = (Get-FileHash -Path $jsonPath -Algorithm SHA256).Hash
        $csvHash  = (Get-FileHash -Path $csvPath  -Algorithm SHA256).Hash
        Set-Content -Path "$jsonPath.sha256" -Value $jsonHash -Encoding ASCII
        Set-Content -Path "$csvPath.sha256"  -Value $csvHash  -Encoding ASCII

        $manifest = [PSCustomObject]@{
            runId      = $runId
            control    = '1.10'
            artifact   = 'communication-compliance-ual'
            tenantId   = (Get-ConnectionInformation | Select-Object -First 1).TenantID
            cloud      = (Get-ConnectionInformation | Select-Object -First 1).ConnectionUri
            runner     = "$env:USERDOMAIN\$env:USERNAME"
            startUtc   = $StartUtc.ToString('o')
            endUtc     = $EndUtc.ToString('o')
            params     = @{ Operations = $Operations }
            outputs    = @(
                @{ file = (Split-Path $jsonPath -Leaf); sha256 = $jsonHash; bytes = (Get-Item $jsonPath).Length }
                @{ file = (Split-Path $csvPath  -Leaf); sha256 = $csvHash;  bytes = (Get-Item $csvPath ).Length }
            )
            rowCount      = $all.Count
            pagesConsumed = $pageIndex
            generatedUtc  = (Get-Date).ToUniversalTime().ToString('o')
        }
        $manifestPath = Join-Path $OutputDirectory "manifest-ual-$ts.json"
        $manifest | ConvertTo-Json -Depth 6 | Set-Content -Path $manifestPath -Encoding UTF8

        $manifest
    }
    finally {
        Stop-Transcript | Out-Null
    }
}
```

### 5.2 Per-policy reviewer activity collector

`Get-SupervisoryReviewActivity` is the **per-policy** evidence path — distinct from UAL because it reflects reviewer dispositions (Compliant / Non-compliant / Questionable / Resolved) joined to the message item (`ItemSubject`, `ActivityId`, `ActionType`, `ActionAppliedBy`, `ItemStatusAfterAction`). Run it per supervisory review policy when an auditor asks for the reviewer trail behind a specific policy.

```powershell
# Session: IPPS
function Get-Cc110SupervisoryReviewActivity {
    <#
    .SYNOPSIS
        Per-policy supervisory review activity collector for Control 1.10 evidence.
    .PARAMETER PolicyId
        Policy GUID from Get-SupervisoryReviewPolicyV2.
    #>
    [CmdletBinding()]
    param(
        [Parameter(Mandatory)] [string]   $PolicyId,
        [Parameter(Mandatory)] [datetime] $StartUtc,
        [Parameter(Mandatory)] [datetime] $EndUtc,
        [Parameter(Mandatory)] [string]   $OutputDirectory
    )

    $ErrorActionPreference = 'Stop'
    New-Item -ItemType Directory -Force -Path $OutputDirectory | Out-Null
    $ts    = Get-Date -Format 'yyyyMMddTHHmmssZ'
    $runId = [guid]::NewGuid().Guid
    Start-Transcript -Path (Join-Path $OutputDirectory "transcript-srvactivity-$PolicyId-$ts.log") -IncludeInvocationHeader

    try {
        $rows = Get-SupervisoryReviewActivity `
            -PolicyId  $PolicyId `
            -StartDate $StartUtc `
            -EndDate   $EndUtc `
            -ErrorAction Stop |
            Sort-Object Timestamp -Descending |
            Select-Object PolicyId, ItemSubject, ActivityId, Timestamp, ActionType, ActionAppliedBy, ItemStatusAfterAction

        $jsonPath = Join-Path $OutputDirectory "srvactivity-$PolicyId-$ts.json"
        $csvPath  = Join-Path $OutputDirectory "srvactivity-$PolicyId-$ts.csv"
        $rows | ConvertTo-Json -Depth 6 | Set-Content -Path $jsonPath -Encoding UTF8
        $rows | Export-Csv -Path $csvPath -NoTypeInformation -Encoding UTF8

        $jsonHash = (Get-FileHash -Path $jsonPath -Algorithm SHA256).Hash
        $csvHash  = (Get-FileHash -Path $csvPath  -Algorithm SHA256).Hash
        Set-Content -Path "$jsonPath.sha256" -Value $jsonHash -Encoding ASCII
        Set-Content -Path "$csvPath.sha256"  -Value $csvHash  -Encoding ASCII

        $manifest = [PSCustomObject]@{
            runId        = $runId
            control      = '1.10'
            artifact     = 'supervisory-review-activity'
            policyId     = $PolicyId
            tenantId     = (Get-ConnectionInformation | Select-Object -First 1).TenantID
            cloud        = (Get-ConnectionInformation | Select-Object -First 1).ConnectionUri
            runner       = "$env:USERDOMAIN\$env:USERNAME"
            startUtc     = $StartUtc.ToString('o')
            endUtc       = $EndUtc.ToString('o')
            outputs      = @(
                @{ file = (Split-Path $jsonPath -Leaf); sha256 = $jsonHash; bytes = (Get-Item $jsonPath).Length }
                @{ file = (Split-Path $csvPath  -Leaf); sha256 = $csvHash;  bytes = (Get-Item $csvPath ).Length }
            )
            rowCount     = ($rows | Measure-Object).Count
            generatedUtc = (Get-Date).ToUniversalTime().ToString('o')
        }
        $manifest | ConvertTo-Json -Depth 6 |
            Set-Content -Path (Join-Path $OutputDirectory "manifest-srvactivity-$PolicyId-$ts.json") -Encoding UTF8

        $manifest
    }
    finally {
        Stop-Transcript | Out-Null
    }
}
```

> **Records-retention caveat (FINRA 4511 / SEC 17a-4(b)(4)).** Exporting CSV / JSON to a local file system **does not** by itself satisfy SEC 17a-4(b)(4) WORM requirements or FINRA 4511 record-keeping rules. Records retention is the responsibility of [Control 1.9 (Records Retention)](../../../controls/pillar-1-security/1.9-data-retention-and-deletion-policies.md) and the underlying [Control 1.7 (Audit Logging)](../../../controls/pillar-1-security/1.7-comprehensive-audit-logging-and-compliance.md). Land the artifacts produced by this section into a Microsoft Purview retention-locked repository or an Azure Storage container with an immutability policy, and reference the storage path in your change ticket. The SHA-256 sidecars in this section provide content-integrity evidence; they do not provide WORM.

### 5.3 End-to-end evidence run

```powershell
# Session: IPPS
$ctx = Initialize-Cc110Session -UserPrincipalName admin@contoso.com -Cloud Commercial

$evidenceRoot = "\\wormshare\fsi-evidence\1.10\$(Get-Date -Format 'yyyy-MM-dd')"

# UAL sweep — last 7 days
Get-Cc110AuditEvidence `
    -StartUtc (Get-Date).ToUniversalTime().AddDays(-7) `
    -EndUtc   (Get-Date).ToUniversalTime() `
    -OutputDirectory $evidenceRoot

# Per-policy supervisory review activity — every CC policy in the tenant
Get-SupervisoryReviewPolicyV2 | ForEach-Object {
    Get-Cc110SupervisoryReviewActivity `
        -PolicyId $_.Guid `
        -StartUtc (Get-Date).ToUniversalTime().AddDays(-30) `
        -EndUtc   (Get-Date).ToUniversalTime() `
        -OutputDirectory $evidenceRoot
}
```

---

## 6. Reviewer reconciliation

Auditors routinely ask "who is allowed to review messages flagged by policy *X*, and is that the same set of people who actually applied tags last quarter?" This section produces a single artifact answering both halves.

```powershell
# Session: IPPS
function Get-Cc110ReviewerReconciliation {
    <#
    .SYNOPSIS
        For each supervisory review policy, compare the reviewer set defined on
        the policy to the actual ActionAppliedBy values from the past N days,
        and to current Communication Compliance role-group membership.
    #>
    [CmdletBinding()]
    param(
        [int]    $DaysBack = 90,
        [string] $OutputDirectory = ".\evidence\1.10"
    )

    $ErrorActionPreference = 'Stop'
    New-Item -ItemType Directory -Force -Path $OutputDirectory | Out-Null
    $ts = Get-Date -Format 'yyyyMMddTHHmmssZ'
    $start = (Get-Date).ToUniversalTime().AddDays(-$DaysBack)
    $end   = (Get-Date).ToUniversalTime()

    $ccAdmins = (Get-RoleGroupMember -Identity 'Communication Compliance Admins' -ErrorAction SilentlyContinue).PrimarySmtpAddress
    $ccInvest = (Get-RoleGroupMember -Identity 'Communication Compliance Investigators' -ErrorAction SilentlyContinue).PrimarySmtpAddress

    $report = foreach ($p in Get-SupervisoryReviewPolicyV2) {
        $activity = Get-SupervisoryReviewActivity -PolicyId $p.Guid -StartDate $start -EndDate $end -ErrorAction SilentlyContinue
        $actualReviewers = $activity | Select-Object -ExpandProperty ActionAppliedBy -Unique
        $declared = @($p.Reviewers)

        [PSCustomObject]@{
            Policy                 = $p.Name
            PolicyGuid             = $p.Guid
            DeclaredReviewers      = $declared
            ActualReviewersDays    = $DaysBack
            ActualReviewers        = $actualReviewers
            DeclaredButNeverActed  = $declared        | Where-Object { $_ -notin $actualReviewers }
            ActedButNotDeclared    = $actualReviewers | Where-Object { $_ -notin $declared }
            CcAdminsOverlap        = $declared        | Where-Object { $_ -in $ccAdmins }
            CcInvestigatorsOverlap = $declared        | Where-Object { $_ -in $ccInvest }
        }
    }

    $jsonPath = Join-Path $OutputDirectory "reviewer-reconciliation-$ts.json"
    $report | ConvertTo-Json -Depth 6 | Set-Content -Path $jsonPath -Encoding UTF8
    $hash = (Get-FileHash -Path $jsonPath -Algorithm SHA256).Hash
    Set-Content -Path "$jsonPath.sha256" -Value $hash -Encoding ASCII

    $report
}
```

> Use the **`ActedButNotDeclared`** column as a flag: anyone who tagged messages on a policy but is not in the policy's declared reviewer list is either (a) a permitted CC Admin acting on behalf of a reviewer — record the rationale, or (b) a permission gap that needs Control 1.10 + Control 2.8 (Access Control and Segregation of Duties) follow-up. Anyone in **`DeclaredButNeverActed`** for 90+ days is a reviewer-rotation candidate — surface them in your monthly attestation.

---

## 7. Sovereign cloud reference

Verified against Microsoft Learn — [Connect to Security & Compliance PowerShell](https://learn.microsoft.com/en-us/powershell/exchange/connect-to-scc-powershell) (last verified April 2026). **Reverify before each change window — Microsoft has rotated the GCC High and DoD endpoints multiple times in the last 24 months.**

| Cloud | `-ConnectionUri` | `-AzureADAuthorizationEndpointUri` |
|---|---|---|
| Commercial / GCC | `https://ps.compliance.protection.outlook.com/powershell-liveid/` (default — can be omitted) | `https://login.microsoftonline.com/organizations` (default — can be omitted) |
| GCC High | `https://ps.compliance.protection.office365.us/powershell-liveid/` | `https://login.microsoftonline.us/organizations` |
| DoD | `https://l5.ps.compliance.protection.office365.us/powershell-liveid/` | `https://login.microsoftonline.us/organizations` |

```powershell
# Commercial / GCC
Connect-IPPSSession -UserPrincipalName $upn

# GCC High
Connect-IPPSSession -UserPrincipalName $upn `
    -ConnectionUri 'https://ps.compliance.protection.office365.us/powershell-liveid/' `
    -AzureADAuthorizationEndpointUri 'https://login.microsoftonline.us/organizations'

# DoD
Connect-IPPSSession -UserPrincipalName $upn `
    -ConnectionUri 'https://l5.ps.compliance.protection.office365.us/powershell-liveid/' `
    -AzureADAuthorizationEndpointUri 'https://login.microsoftonline.us/organizations'
```

> **Never use commercial endpoints from a sovereign tenant.** The cmdlet will appear to succeed (it authenticates against commercial AAD), but every supervisory review and CC audit query returns zero rows — producing **false-clean** evidence. The `Initialize-Cc110Session` helper in Section 1 enforces the correct endpoint via the `-Cloud` switch.

---

## 8. Anti-patterns (what NOT to do)

These are the patterns most likely to produce silent or fabricated evidence for Control 1.10. Reject any of them in PR review.

1. **Single-call `Search-UnifiedAuditLog -ResultSize 5000`.** Silently truncates at 5,000 rows. **Always** use the session-paging loop in Section 5.1 and hard-fail at the per-session ceiling.
2. **`-ErrorAction SilentlyContinue` on a tenant-mutation cmdlet** (e.g., `Add-RoleGroupMember`, `New-SupervisoryReviewPolicyV2`, `Set-SupervisoryReviewRule`) followed by a hard-coded `[PASS]` banner. This is the single most common pattern that produces fabricated evidence. Use `-ErrorAction Stop` in `try/catch` and emit the result row only after a verified after-snapshot.
3. **Running supervisory review or CC role-group cmdlets from `Connect-ExchangeOnline`** instead of `Connect-IPPSSession`. Produces `CommandNotFoundException` at best, silent zero results at worst.
4. **Using `-RecordType CopilotInteraction` as evidence for Communication Compliance.** `CopilotInteraction` is the audit surface for [Control 1.7 (Audit Logging)](../../../controls/pillar-1-security/1.7-comprehensive-audit-logging-and-compliance.md), not 1.10. Communication Compliance evidence comes from `SupervisionRuleMatch`, `SupervisionPolicy*`, and `SupervisoryReviewTag`.
5. **Inventing a `CopilotInteraction` RecordType filter that does not match Microsoft Learn.** Always reverify `RecordType` and `Operations` strings against [audit-log-activities](https://learn.microsoft.com/en-us/purview/audit-log-activities) before shipping a script.
6. **Passing a DLP Sensitive Information Type inventory off as CC evidence.** `Get-DlpSensitiveInformationType` belongs to Control 1.5 (DLP) and Control 1.13 (Sensitive Information Types). It tells you nothing about whether a Communication Compliance policy is operational. Remove it from any CC evidence script.
7. **Plain `Export-Csv` with no SHA-256 sidecar and no immutability target.** Spreadsheet exports are not audit evidence under SEC 17a-4(b)(4). Land artifacts in a WORM-eligible store (Purview retention lock or Azure Storage immutability) and emit a SHA-256 sidecar — see Section 5.
8. **No `Start-Transcript`.** Without a transcript, you cannot prove which cmdlets ran, against which tenant, by which principal, in which order. Every script in this playbook starts with `Start-Transcript` and ends with `Stop-Transcript`.
9. **No pre-flight role check.** `Get-SupervisoryReviewPolicyV2` returns an empty list (no error) when the caller lacks permission. Without the `Initialize-Cc110Session` role-membership assertion, a zero-row file looks identical to a clean tenant.
10. **No module version pin.** Floating `Install-Module ExchangeOnlineManagement -Force` upgrades break reproducibility across change windows and have, in the past, changed the schema returned by `Get-SupervisoryReviewActivity`. Pin the version in your CAB ticket.
11. **`New-SupervisoryReviewRule -ReviewerEmail …` or `… -Reviewers …`.** Neither parameter exists on the rule cmdlet. Reviewers are assigned **on the policy** via `New-SupervisoryReviewPolicyV2 -Reviewers <String[]>`. The rule defines the sampled content set (`-Condition`, `-SamplingRate`, `-ContentSources`).
12. **Promoting PowerShell as a substitute for the Purview portal for CC policy CRUD.** Per Microsoft Learn, modern Communication Compliance policies (including the Copilot interactions template) cannot be created or edited via PowerShell. Document this boundary in every change ticket so reviewers do not expect a PS-based diff.
13. **Treating `Get-SupervisoryReviewActivity` as tenant-wide.** It is **per-policy** — the `-PolicyId` parameter is mandatory. Loop over `Get-SupervisoryReviewPolicyV2` to cover the full tenant, as in Section 5.3.
14. **Hard-coded reviewer email lists committed to source control.** Pass reviewers via parameters or pull from an Entra group; do not ship UPNs in playbook code.

---

## 9. Cross-links

| Concern | Control |
|---|---|
| Records retention / WORM landing for CC evidence artifacts | [Control 1.9 — Records Retention and Immutability](../../../controls/pillar-1-security/1.9-data-retention-and-deletion-policies.md) |
| Tenant-wide audit ingestion (`UnifiedAuditLogIngestionEnabled`), `CopilotInteraction` audit surface | [Control 1.7 — Audit Logging for AI Interactions](../../../controls/pillar-1-security/1.7-comprehensive-audit-logging-and-compliance.md) |
| DLP and Sensitivity Labels used by CC policy classifiers | [Control 1.5 — Data Loss Prevention (DLP) and Sensitivity Labels](../../../controls/pillar-1-security/1.5-data-loss-prevention-dlp-and-sensitivity-labels.md) |
| Insider Risk Management — adjacent cmdlet surface and shared role groups | [Control 1.12 — Insider Risk Management for Agent Misuse](../../../controls/pillar-1-security/1.12-insider-risk-detection-and-response.md) |
| eDiscovery holds against CC evidence | [Control 1.19 — eDiscovery for AI-Generated Content](../../../controls/pillar-1-security/1.19-ediscovery-for-agent-interactions.md) |
| Trainable classifiers / Sensitive Information Types referenced by CC rules | [Control 1.13 — Custom Sensitive Information Types](../../../controls/pillar-1-security/1.13-sensitive-information-types-sits-and-pattern-recognition.md) |
| Identity & access for reviewer / admin role-group assignments | [Control 1.2 — Identity and Access Management for AI Agents](../../../controls/pillar-1-security/1.2-agent-registry-and-integrated-apps-management.md) |

**Microsoft Learn references (verify before each change window):**

- [Communication compliance — Create and manage policies](https://learn.microsoft.com/en-us/purview/communication-compliance-policies)
- [Communication compliance — Permissions and role groups](https://learn.microsoft.com/en-us/purview/communication-compliance-permissions)
- [Communication compliance — Investigate and remediate alerts](https://learn.microsoft.com/en-us/purview/communication-compliance-investigate-remediate)
- [Connect to Security & Compliance PowerShell](https://learn.microsoft.com/en-us/powershell/exchange/connect-to-scc-powershell)
- [`New-SupervisoryReviewPolicyV2`](https://learn.microsoft.com/en-us/powershell/module/exchange/new-supervisoryreviewpolicyv2)
- [`New-SupervisoryReviewRule`](https://learn.microsoft.com/en-us/powershell/module/exchange/new-supervisoryreviewrule)
- [`Get-SupervisoryReviewActivity`](https://learn.microsoft.com/en-us/powershell/module/exchange/get-supervisoryreviewactivity)
- [`Get-SupervisoryReviewReport`](https://learn.microsoft.com/en-us/powershell/module/exchange/get-supervisoryreviewreport)
- [`Search-UnifiedAuditLog`](https://learn.microsoft.com/en-us/powershell/module/exchange/search-unifiedauditlog)
- [Audit log activities — Communication compliance](https://learn.microsoft.com/en-us/purview/audit-log-activities)

---

*Updated: May 2026 | Version: v1.6.2 | UI Verification Status: Current*
