# Control 1.9 — PowerShell Setup: Data Retention and Deletion Policies

**Control:** 1.9 — Data Retention and Deletion Policies
**Pillar:** Pillar 1 — Security
**Audience:** Purview Records Manager, Purview Compliance Admin, Power Platform Admin
**Companion playbooks:** [Portal walkthrough](./portal-walkthrough.md) · [Verification & testing](./verification-testing.md) · [Troubleshooting](./troubleshooting.md)

!!! warning "Read the FSI PowerShell baseline first"
    Before running anything below, read the [**PowerShell Authoring Baseline for FSI Implementations**](../../_shared/powershell-baseline.md). It is the canonical source for `ExchangeOnlineManagement` version pinning, sovereign-cloud (GCC / GCC High / DoD) endpoints, mutation safety (`-WhatIf` / `SupportsShouldProcess`), and SHA-256 evidence emission. Snippets below assume that baseline is in effect.

> This playbook automates Control 1.9 via **Security & Compliance PowerShell** (the IPPS endpoint exposed by `ExchangeOnlineManagement`). Every mutating command below is wrapped in safety checks, supports `-WhatIf`, and writes evidence artifacts intended for examiner production.
>
> **Hedging note.** This automation helps meet, and is recommended to support compliance with, SEC 17 CFR 240.17a-4, FINRA 4511, SOX §404 / §802, GLBA 501(b), CFTC 1.31, and IRS recordkeeping rules. It does **not by itself** satisfy 17a-4(f) — see the parent control's "SEC 17a-4(f) caveat."

---

## §1. Pre-flight

### 1.1 Module and edition

| Module | Required version | Edition |
|---|---|---|
| `ExchangeOnlineManagement` | Pin to a CAB-approved stable production release | Desktop (5.1) or Core (7.2+) |

```powershell
# Pin to a CAB-approved version. Substitute <version>.
Install-Module -Name ExchangeOnlineManagement `
    -RequiredVersion '<version>' `
    -Repository PSGallery `
    -Scope CurrentUser `
    -AllowClobber `
    -AcceptLicense
```

### 1.2 Required role

The signed-in account must hold **Purview Records Manager** *and* **Purview Compliance Admin** to author labels, policies, and apply Preservation Lock. For Zone 3 lock application, require a second-person review (named in the change ticket) before the lock cmdlet runs.

### 1.3 Connect to Security & Compliance

```powershell
# Commercial cloud
Connect-IPPSSession -ShowBanner:$false

# GCC High
# Connect-IPPSSession -ConnectionUri https://ps.compliance.protection.office365.us/powershell-liveid/ `
#     -AzureADAuthorizationEndpointUri https://login.microsoftonline.us/common -ShowBanner:$false

# DoD
# Connect-IPPSSession -ConnectionUri https://l5.ps.compliance.protection.office365.us/powershell-liveid/ `
#     -AzureADAuthorizationEndpointUri https://login.microsoftonline.us/common -ShowBanner:$false
```

Verify the session:

```powershell
Get-ConnectionInformation | Where-Object { $_.ConnectionUri -like '*compliance*' } |
    Select-Object UserPrincipalName, ConnectionUri, State
```

### 1.4 Common parameters used below

```powershell
$EvidenceRoot = 'C:\fsi-evidence\1.9'
$null = New-Item -ItemType Directory -Path $EvidenceRoot -Force
$Stamp = (Get-Date).ToString('yyyyMMdd-HHmmss')

$ReviewerStage1 = 'records-mgmt-stage1@contoso.com'
$ReviewerStage2 = 'compliance-stage2@contoso.com'
$ReviewerStage3 = 'legal-stage3@contoso.com'
```

---

## §2. Idempotent label creation

`New-ComplianceTag` fails if the tag exists. Wrap creates in an idempotency check and use `Set-ComplianceTag` for updates. **`Set-ComplianceTag` cannot reduce retention on a record/regulatory label** — see §6.

### 2.1 Helper: ensure a label exists

```powershell
function Ensure-ComplianceTag {
    [CmdletBinding(SupportsShouldProcess)]
    param(
        [Parameter(Mandatory)] [string] $Name,
        [Parameter(Mandatory)] [string] $Comment,
        [Parameter(Mandatory)] [int]    $RetentionDurationDays,
        [Parameter(Mandatory)] [ValidateSet('Keep','Delete','KeepAndDelete')] [string] $RetentionAction,
        [bool]   $IsRecordLabel  = $false,
        [bool]   $Regulatory     = $false,
        [string] $ReviewerEmail
    )

    $existing = Get-ComplianceTag -Identity $Name -ErrorAction SilentlyContinue
    if ($existing) {
        Write-Host "[SKIP] Label '$Name' already exists." -ForegroundColor Yellow
        return $existing
    }

    if ($PSCmdlet.ShouldProcess($Name, "Create retention label")) {
        $params = @{
            Name              = $Name
            Comment           = $Comment
            RetentionDuration = $RetentionDurationDays
            RetentionAction   = $RetentionAction
            RetentionType     = 'CreationAgeInDays'
        }
        if ($IsRecordLabel)        { $params.IsRecordLabel = $true }
        if ($Regulatory)           { $params.Regulatory    = $true }
        if ($ReviewerEmail)        { $params.ReviewerEmail = $ReviewerEmail }

        New-ComplianceTag @params -ErrorAction Stop |
            Tee-Object -FilePath (Join-Path $EvidenceRoot "label-$Name-$Stamp.json")
        Write-Host "[CREATED] Label '$Name'." -ForegroundColor Green
    }
}
```

### 2.2 Create the FSI label set

```powershell
# Communications classification (3 years)
Ensure-ComplianceTag -Name 'FSI-Agent-Communications-3Year' `
    -Comment 'Agent transcript classified as a communication under SEC 17a-4(b)(4). 3-year retention.' `
    -RetentionDurationDays 1095 `
    -RetentionAction KeepAndDelete `
    -IsRecordLabel $true `
    -ReviewerEmail $ReviewerStage2

# Books-and-records (6 years)
Ensure-ComplianceTag -Name 'FSI-Agent-BooksRecords-6Year' `
    -Comment 'Agent transcript that evidences or generates a 17a-3 record. 6-year retention.' `
    -RetentionDurationDays 2190 `
    -RetentionAction KeepAndDelete `
    -IsRecordLabel $true `
    -ReviewerEmail $ReviewerStage2

# Regulatory record (10 years, immutable)
Ensure-ComplianceTag -Name 'FSI-Agent-RegRecord-10Year' `
    -Comment 'Agent audit metadata and regulated artifacts. 10-year retention; immutable.' `
    -RetentionDurationDays 3650 `
    -RetentionAction KeepAndDelete `
    -IsRecordLabel $true `
    -Regulatory $true `
    -ReviewerEmail $ReviewerStage3

# Agent configuration (6 years, automatic deletion)
Ensure-ComplianceTag -Name 'FSI-Agent-Configuration-6Year' `
    -Comment 'Agent definitions, version history, exports. 6-year retention.' `
    -RetentionDurationDays 2190 `
    -RetentionAction Delete
```

!!! warning "Regulatory record is one-way"
    Once `Regulatory = $true` is set on a label, the label cannot be unmarked or deleted, items it has been applied to cannot have the label removed, and retention can only be **extended**. Treat creation of a regulatory label as a SEV-2 change.

---

## §3. Idempotent retention-policy creation for AI surfaces

The exact location parameter names for **Microsoft 365 Copilot and AI experiences**, **Enterprise AI Apps**, and **Other AI Apps** evolve as Microsoft adds capabilities. Always cross-check against [`New-RetentionCompliancePolicy`](https://learn.microsoft.com/en-us/powershell/module/exchange/new-retentioncompliancepolicy) immediately before a production change.

### 3.1 Helper: ensure a policy + rule exist

```powershell
function Ensure-RetentionPolicy {
    [CmdletBinding(SupportsShouldProcess)]
    param(
        [Parameter(Mandatory)] [string] $PolicyName,
        [Parameter(Mandatory)] [string] $RuleName,
        [Parameter(Mandatory)] [int]    $RetentionDurationDays,
        [Parameter(Mandatory)] [hashtable] $LocationParams,
        [string] $ContentMatchQuery
    )

    $existing = Get-RetentionCompliancePolicy -Identity $PolicyName -ErrorAction SilentlyContinue
    if (-not $existing) {
        if ($PSCmdlet.ShouldProcess($PolicyName, "Create retention policy")) {
            New-RetentionCompliancePolicy -Name $PolicyName @LocationParams -ErrorAction Stop |
                Out-Null
            Write-Host "[CREATED] Policy '$PolicyName'." -ForegroundColor Green
        }
    } else {
        Write-Host "[SKIP] Policy '$PolicyName' already exists." -ForegroundColor Yellow
    }

    $rule = Get-RetentionComplianceRule -Policy $PolicyName -ErrorAction SilentlyContinue |
        Where-Object Name -eq $RuleName
    if (-not $rule) {
        if ($PSCmdlet.ShouldProcess($RuleName, "Create retention rule")) {
            $ruleParams = @{
                Name                       = $RuleName
                Policy                     = $PolicyName
                RetentionDuration          = $RetentionDurationDays
                RetentionComplianceAction  = 'KeepAndDelete'
            }
            if ($ContentMatchQuery) { $ruleParams.ContentMatchQuery = $ContentMatchQuery }
            New-RetentionComplianceRule @ruleParams -ErrorAction Stop | Out-Null
            Write-Host "[CREATED] Rule '$RuleName'." -ForegroundColor Green
        }
    } else {
        Write-Host "[SKIP] Rule '$RuleName' already exists." -ForegroundColor Yellow
    }
}
```

### 3.2 Microsoft 365 Copilot and AI experiences

```powershell
Ensure-RetentionPolicy -PolicyName 'FSI-Copilot-AIExperiences-Retention' `
    -RuleName  'FSI-Copilot-AIExperiences-6Year' `
    -RetentionDurationDays 2190 `
    -LocationParams @{ ModernGroupLocation = 'All' }
# NOTE: The exact location switch for Copilot/AI experiences may be named differently
# (e.g., -CopilotLocation, -CopilotExperiencesLocation, -ModernGroupLocation in some
# configurations). Verify with `Get-Help New-RetentionCompliancePolicy -Full` against
# your pinned ExchangeOnlineManagement module before running in production.
```

### 3.3 Agent-related Exchange email retention (content-match safety net)

```powershell
Ensure-RetentionPolicy -PolicyName 'FSI-AgentEmail-Retention' `
    -RuleName  'FSI-AgentEmail-6Year' `
    -RetentionDurationDays 2190 `
    -LocationParams @{ ExchangeLocation = 'All' } `
    -ContentMatchQuery '(Copilot OR "agent" OR "AI assistant" OR chatbot)'
```

### 3.4 SharePoint / OneDrive container retention

```powershell
Ensure-RetentionPolicy -PolicyName 'FSI-AgentSharePoint-Retention' `
    -RuleName  'FSI-AgentSharePoint-6Year' `
    -RetentionDurationDays 2190 `
    -LocationParams @{ SharePointLocation = 'All'; OneDriveLocation = 'All' }
```

---

## §4. Publish the FSI agent labels

```powershell
$LabelPolicyName = 'FSI-Agent-Labels-Publish-Zone3'
$existing = Get-RetentionCompliancePolicy -Identity $LabelPolicyName -ErrorAction SilentlyContinue
if (-not $existing) {
    New-RetentionCompliancePolicy -Name $LabelPolicyName `
        -ExchangeLocation     'All' `
        -SharePointLocation   'All' `
        -OneDriveLocation     'All' `
        -ModernGroupLocation  'All' `
        -Comment 'Publishes FSI Control 1.9 retention labels to Zone 3 in-scope locations.' |
        Out-Null
}

$AgentLabels = Get-ComplianceTag | Where-Object { $_.Name -like 'FSI-Agent-*' }
$RuleName    = 'FSI-Agent-Labels-Rule'
$rule = Get-RetentionComplianceRule -Policy $LabelPolicyName -ErrorAction SilentlyContinue |
    Where-Object Name -eq $RuleName
if (-not $rule) {
    New-RetentionComplianceRule -Name $RuleName `
        -Policy $LabelPolicyName `
        -PublishComplianceTag $AgentLabels.Name | Out-Null
}
```

Verify distribution:

```powershell
Get-RetentionCompliancePolicy -Identity $LabelPolicyName |
    Select-Object Name, Mode, Enabled, DistributionStatus
```

---

## §5. Audit-log retention for deletion events

```powershell
$AuditPolicyName = 'FSI-DeletionAudit-10Year'
$existing = Get-UnifiedAuditLogRetentionPolicy -Identity $AuditPolicyName -ErrorAction SilentlyContinue
if (-not $existing) {
    New-UnifiedAuditLogRetentionPolicy -Name $AuditPolicyName `
        -Description 'Extended retention for retention/disposition/deletion events (Control 1.9).' `
        -Operations FileDeleted, FileVersionRecycled, HardDelete, SoftDelete, MoveToDeletedItems, `
                    ApplyRetentionLabel, RemoveRetentionLabel, `
                    NewRetentionComplianceRule, SetRetentionCompliancePolicy `
        -RetentionDuration TenYears `
        -Priority 100
}
```

> Audit-log retention beyond Microsoft 365 Audit (Standard) requires Microsoft 365 Audit (Premium) and the appropriate per-user license. See [Control 1.7](../../../controls/pillar-1-security/1.7-comprehensive-audit-logging-and-compliance.md).

---

## §6. Preservation Lock — irreversible

> **STOP.** Read this entire section before running the lock cmdlet. After this completes, the policy cannot be disabled, deleted, or shortened by anyone — including Microsoft Support.

### 6.1 Pre-lock validation

```powershell
function Test-PolicyReadyForLock {
    param([Parameter(Mandatory)] [string] $PolicyName)

    $p = Get-RetentionCompliancePolicy -Identity $PolicyName -DistributionDetail
    $r = Get-RetentionComplianceRule -Policy $PolicyName

    $issues = @()
    if (-not $p)                               { $issues += 'Policy not found.' }
    if ($p.Enabled -ne $true)                  { $issues += 'Policy is not Enabled.' }
    if ($p.Mode -ne 'Enforce')                 { $issues += "Policy Mode is '$($p.Mode)' (not 'Enforce')." }
    if ($p.DistributionStatus -ne 'Success')   { $issues += "DistributionStatus is '$($p.DistributionStatus)'." }
    if ($p.RetentionComplianceLockType -eq 'Lock') { $issues += 'Policy is already Locked.' }
    if (-not $r)                               { $issues += 'No rules attached to policy.' }
    foreach ($rule in $r) {
        if ($rule.RetentionDuration -lt 1095) {
            $issues += "Rule '$($rule.Name)' retention is $($rule.RetentionDuration) days (< 3 years floor)."
        }
    }

    if ($issues) {
        Write-Host "[BLOCK] '$PolicyName' is NOT ready for lock:" -ForegroundColor Red
        $issues | ForEach-Object { Write-Host "  - $_" -ForegroundColor Red }
        return $false
    }
    Write-Host "[OK] '$PolicyName' passed pre-lock validation." -ForegroundColor Green
    return $true
}
```

### 6.2 Apply Preservation Lock (with explicit confirmation)

```powershell
function Lock-RetentionPolicy {
    [CmdletBinding(SupportsShouldProcess, ConfirmImpact='High')]
    param(
        [Parameter(Mandatory)] [string] $PolicyName,
        [Parameter(Mandatory)] [string] $ChangeTicket,
        [Parameter(Mandatory)] [string] $SecondReviewerUpn
    )

    if (-not (Test-PolicyReadyForLock -PolicyName $PolicyName)) { return }

    $confirmation = Read-Host "Type the policy name '$PolicyName' to confirm IRREVERSIBLE Preservation Lock"
    if ($confirmation -ne $PolicyName) {
        Write-Host "[ABORT] Confirmation did not match. No action taken." -ForegroundColor Yellow
        return
    }

    if ($PSCmdlet.ShouldProcess($PolicyName,
        "Apply Preservation Lock (IRREVERSIBLE) under ticket $ChangeTicket, reviewed by $SecondReviewerUpn")) {

        Set-RetentionCompliancePolicy -Identity $PolicyName `
            -RetentionComplianceLockType Lock -ErrorAction Stop

        $evidence = Get-RetentionCompliancePolicy -Identity $PolicyName |
            Select-Object Name, Mode, Enabled, RetentionComplianceLockType, WhenChanged
        $evidence | ConvertTo-Json |
            Out-File (Join-Path $EvidenceRoot "lock-$PolicyName-$Stamp.json")
        Write-Host "[LOCKED] '$PolicyName'. Evidence saved." -ForegroundColor Green
    }
}

# Example (Zone 3 only):
# Lock-RetentionPolicy -PolicyName 'FSI-Copilot-AIExperiences-Retention' `
#     -ChangeTicket 'CHG-0123456' -SecondReviewerUpn 'records.mgr@contoso.com'
```

### 6.3 Locked-policy gotchas

| Gotcha | Reality | Mitigation |
|---|---|---|
| "Locked" prevents *all* changes | False — you can still **add** locations and **extend** retention | Document permitted change paths in the change ticket |
| Lock can be removed by Global Admin | False — no role can unlock | Treat lock as a CAB SEV-2 change with second-person review |
| Lock applies to label policies too | True — `Set-RetentionCompliancePolicy -RetentionComplianceLockType Lock` works on the policy that publishes labels | Lock the publish-policy after labels stabilize |
| Lock affects existing rules retroactively | True — but new rules added after lock are also locked | Add all rules **before** locking |
| Lock survives tenant-to-tenant migration | Microsoft does not support migrating locked policies in tenant moves | Plan the records strategy with the tenant lifecycle in mind |

---

## §7. Evidence export

```powershell
$labels   = Get-ComplianceTag | Where-Object { $_.Name -like 'FSI-Agent-*' } |
    Select-Object Name, RetentionDuration, RetentionAction, IsRecordLabel, Regulatory, ReviewerEmail, WhenCreated, WhenChanged
$labels | Export-Csv (Join-Path $EvidenceRoot "labels-$Stamp.csv") -NoTypeInformation

$policies = Get-RetentionCompliancePolicy | Where-Object { $_.Name -like 'FSI-*' } |
    Select-Object Name, Mode, Enabled, DistributionStatus, RetentionComplianceLockType, WhenCreated, WhenChanged
$policies | Export-Csv (Join-Path $EvidenceRoot "policies-$Stamp.csv") -NoTypeInformation

$rules    = foreach ($p in $policies) {
    Get-RetentionComplianceRule -Policy $p.Name -ErrorAction SilentlyContinue |
        Select-Object @{n='PolicyName';e={$p.Name}}, Name, RetentionDuration, RetentionComplianceAction, ContentMatchQuery
}
$rules | Export-Csv (Join-Path $EvidenceRoot "rules-$Stamp.csv") -NoTypeInformation

# SHA-256 evidence stamp (per FSI baseline)
Get-ChildItem -Path $EvidenceRoot -Filter "*-$Stamp.*" | ForEach-Object {
    [PSCustomObject]@{
        File   = $_.Name
        SHA256 = (Get-FileHash -Path $_.FullName -Algorithm SHA256).Hash
    }
} | Export-Csv (Join-Path $EvidenceRoot "evidence-manifest-$Stamp.csv") -NoTypeInformation
```

---

## §8. Cleanup

```powershell
Disconnect-ExchangeOnline -Confirm:$false -ErrorAction SilentlyContinue
```

---

## Cross-references

- [Control 1.7 — Comprehensive Audit Logging and Compliance](../../../controls/pillar-1-security/1.7-comprehensive-audit-logging-and-compliance.md)
- [Microsoft Learn: `New-ComplianceTag`](https://learn.microsoft.com/en-us/powershell/module/exchange/new-compliancetag)
- [Microsoft Learn: `New-RetentionCompliancePolicy`](https://learn.microsoft.com/en-us/powershell/module/exchange/new-retentioncompliancepolicy)
- [Microsoft Learn: Use Preservation Lock](https://learn.microsoft.com/en-us/purview/retention-preservation-lock)

---

[Back to Control 1.9](../../../controls/pillar-1-security/1.9-data-retention-and-deletion-policies.md) · [Portal walkthrough](./portal-walkthrough.md) · [Verification & testing](./verification-testing.md) · [Troubleshooting](./troubleshooting.md)

---

*Updated: April 2026 | Version: v1.6.2*
