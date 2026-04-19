# PowerShell Setup: Control 2.14 — Training and Awareness Program

!!! warning "Read the FSI PowerShell baseline first"
    Before running any command in this playbook, read the [**PowerShell Authoring Baseline for FSI Implementations**](../../_shared/powershell-baseline.md). It is the canonical source for module version pinning, sovereign-cloud (GCC / GCC High / DoD) endpoints, mutation safety (`-WhatIf` / `SupportsShouldProcess`), Dataverse compatibility, and SHA-256 evidence emission. Snippets below show the patterns; the baseline is authoritative.

**Last Updated:** April 2026
**Modules Required:** `Microsoft.Graph` (User.Read.All, RoleManagement.Read.All, optional Mail.Send), `ExchangeOnlineManagement` (only if mail-flow analysis is needed)
**Mutation Profile:** Read-only against Entra and Graph; mail send (Step 3) is gated by `-WhatIf` and `ShouldProcess`

---

## Scope and Limits

This playbook automates the **measurable** parts of Control 2.14:

1. Identify users in scope for training based on their Entra role assignments.
2. Reconcile a roster of expected trainees against an LMS-exported completion list.
3. Generate signed (SHA-256) evidence artifacts suitable for FINRA / SEC examination.
4. Optionally send reminders via Microsoft Graph mail (gated).

This playbook does **not** read directly from Microsoft Viva Learning. Programmatic access to Viva Learning learner records is currently delivered through the [Employee Experience Graph APIs](https://learn.microsoft.com/en-us/graph/api/resources/employeeexperience-overview) (`/employeeExperience/learningProviders`, `/learningContents`, `/learningCourseActivities`) which are in **beta** and subject to change. For audit-defensible reporting in regulated tenants, treat the LMS / Viva-exported CSV as the system of record and have the LMS owner countersign the export.

---

## Prerequisites

```powershell
# Pin module versions per your firm's CAB-approved baseline.
# Replace <version> with the version validated for your tenant.
Install-Module Microsoft.Graph `
    -RequiredVersion '<version>' `
    -Repository PSGallery `
    -Scope CurrentUser `
    -AcceptLicense

# Sovereign-cloud aware connection (commercial shown; see baseline for GCC / GCC High / DoD)
Connect-MgGraph -Scopes 'User.Read.All','RoleManagement.Read.All' -Environment Global
```

---

## Script 1 — Identify Users In Scope for Training

```powershell
<#
.SYNOPSIS
    Build the in-scope trainee roster from Entra role assignments.
.DESCRIPTION
    Maps a curated list of Entra directory roles to a "training required" flag,
    enriches users with department/job title, and emits a SHA-256 signed JSON
    artifact for evidence.
.PARAMETER OutputPath
    Directory to write the evidence artifact (default .\evidence-2.14).
.EXAMPLE
    .\Get-TrainingRoster.ps1 -OutputPath .\evidence-2.14
.NOTES
    Read-only. Requires User.Read.All and RoleManagement.Read.All.
#>
[CmdletBinding()]
param(
    [string]$OutputPath = ".\evidence-2.14"
)

$ErrorActionPreference = 'Stop'
New-Item -ItemType Directory -Force -Path $OutputPath | Out-Null
$ts = Get-Date -Format 'yyyyMMddTHHmmssZ'
Start-Transcript -Path (Join-Path $OutputPath "transcript-roster-$ts.log") -IncludeInvocationHeader

# Canonical roles whose holders require AI governance training.
# Names below are Entra built-in role display names (NOT this framework's
# canonical short names) because that is what Get-MgDirectoryRole returns.
$inScopeRoles = @(
    'Power Platform Administrator',
    'Compliance Administrator',
    'Compliance Data Administrator',
    'SharePoint Administrator',
    'Exchange Administrator',
    'Teams Administrator',
    'AI Administrator',
    'Knowledge Administrator',
    'Knowledge Manager',
    'Global Administrator'
)

$roster = @()
foreach ($role in (Get-MgDirectoryRole)) {
    if ($inScopeRoles -notcontains $role.DisplayName) { continue }
    $members = Get-MgDirectoryRoleMember -DirectoryRoleId $role.Id -All -ErrorAction SilentlyContinue
    foreach ($m in $members) {
        # Members may be users, groups, or service principals; filter to users.
        if ($m.AdditionalProperties['@odata.type'] -ne '#microsoft.graph.user') { continue }
        $u = Get-MgUser -UserId $m.Id -Property 'id,displayName,mail,userPrincipalName,department,jobTitle,accountEnabled' -ErrorAction SilentlyContinue
        if (-not $u) { continue }
        $roster += [PSCustomObject]@{
            UserId        = $u.Id
            DisplayName   = $u.DisplayName
            Mail          = $u.Mail
            UPN           = $u.UserPrincipalName
            Department    = $u.Department
            JobTitle      = $u.JobTitle
            AccountEnabled = $u.AccountEnabled
            EntraRole     = $role.DisplayName
            CollectedUtc  = $ts
        }
    }
}

# Deduplicate (users may hold multiple in-scope roles)
$roster = $roster | Sort-Object UserId, EntraRole -Unique

# Emit JSON + CSV + manifest (SHA-256)
$jsonPath = Join-Path $OutputPath "training-roster-$ts.json"
$csvPath  = Join-Path $OutputPath "training-roster-$ts.csv"
$roster | ConvertTo-Json -Depth 5 | Set-Content -Path $jsonPath -Encoding UTF8
$roster | Export-Csv -Path $csvPath -NoTypeInformation -Encoding UTF8

$manifest = @($jsonPath, $csvPath) | ForEach-Object {
    [PSCustomObject]@{
        file          = Split-Path $_ -Leaf
        sha256        = (Get-FileHash $_ -Algorithm SHA256).Hash
        bytes         = (Get-Item $_).Length
        generated_utc = $ts
        script        = 'Get-TrainingRoster'
    }
}
$manifest | ConvertTo-Json -Depth 4 | Set-Content -Path (Join-Path $OutputPath "manifest-roster-$ts.json") -Encoding UTF8

Write-Host "[OK] Roster: $($roster.Count) users in scope" -ForegroundColor Green
Stop-Transcript
```

---

## Script 2 — Reconcile Roster vs LMS Completions

```powershell
<#
.SYNOPSIS
    Reconcile the in-scope roster against an LMS / Viva Learning completion export.
.DESCRIPTION
    Joins the roster (Script 1 output) with a CSV exported from the firm's
    learning system. Produces compliant / non-compliant / expired buckets
    plus SHA-256 signed evidence.
.PARAMETER RosterCsv
    CSV produced by Script 1.
.PARAMETER CompletionsCsv
    LMS-exported CSV with at minimum: Mail, CourseId, CompletionDateUtc.
.PARAMETER RequiredCourseId
    The course identifier used by your LMS to denote AI Governance training.
.PARAMETER ValidityDays
    Days a completion remains valid before refresher is required (default 365).
.PARAMETER OutputPath
    Evidence directory (default .\evidence-2.14).
.EXAMPLE
    .\Get-TrainingCompliance.ps1 -RosterCsv .\evidence-2.14\training-roster-*.csv `
        -CompletionsCsv .\lms-export.csv -RequiredCourseId 'AI-GOV-101'
#>
[CmdletBinding()]
param(
    [Parameter(Mandatory)] [string]$RosterCsv,
    [Parameter(Mandatory)] [string]$CompletionsCsv,
    [Parameter(Mandatory)] [string]$RequiredCourseId,
    [int]$ValidityDays = 365,
    [string]$OutputPath = ".\evidence-2.14"
)

$ErrorActionPreference = 'Stop'
New-Item -ItemType Directory -Force -Path $OutputPath | Out-Null
$ts = Get-Date -Format 'yyyyMMddTHHmmssZ'

$roster      = Import-Csv -Path $RosterCsv
$completions = Import-Csv -Path $CompletionsCsv |
    Where-Object { $_.CourseId -eq $RequiredCourseId }

# Index latest completion per user mail (case-insensitive)
$latest = @{}
foreach ($c in $completions) {
    $key = $c.Mail.ToLowerInvariant()
    $dt  = [datetime]::Parse($c.CompletionDateUtc, [System.Globalization.CultureInfo]::InvariantCulture)
    if (-not $latest.ContainsKey($key) -or $latest[$key] -lt $dt) {
        $latest[$key] = $dt
    }
}

$now    = (Get-Date).ToUniversalTime()
$cutoff = $now.AddDays(-1 * $ValidityDays)

$report = foreach ($u in $roster) {
    $key = if ($u.Mail) { $u.Mail.ToLowerInvariant() } else { $u.UPN.ToLowerInvariant() }
    if ($latest.ContainsKey($key)) {
        $dt = $latest[$key]
        $status = if ($dt -ge $cutoff) { 'Compliant' } else { 'Expired' }
    } else {
        $dt = $null
        $status = 'NotCompleted'
    }
    [PSCustomObject]@{
        DisplayName        = $u.DisplayName
        Mail               = $u.Mail
        UPN                = $u.UPN
        EntraRole          = $u.EntraRole
        Department         = $u.Department
        LastCompletionUtc  = if ($dt) { $dt.ToString('o') } else { '' }
        Status             = $status
    }
}

$total       = $report.Count
$compliant   = ($report | Where-Object Status -eq 'Compliant').Count
$expired     = ($report | Where-Object Status -eq 'Expired').Count
$notDone     = ($report | Where-Object Status -eq 'NotCompleted').Count
$rate        = if ($total -gt 0) { [math]::Round(($compliant / $total) * 100, 1) } else { 0 }

Write-Host "Total in-scope: $total" -ForegroundColor Cyan
Write-Host "Compliant:      $compliant ($rate%)" -ForegroundColor Green
Write-Host "Expired:        $expired" -ForegroundColor Yellow
Write-Host "Not completed:  $notDone" -ForegroundColor Red

$jsonPath = Join-Path $OutputPath "training-compliance-$ts.json"
$csvPath  = Join-Path $OutputPath "training-compliance-$ts.csv"
$report | ConvertTo-Json -Depth 4 | Set-Content -Path $jsonPath -Encoding UTF8
$report | Export-Csv -Path $csvPath -NoTypeInformation -Encoding UTF8

$summary = [PSCustomObject]@{
    GeneratedUtc      = $ts
    RequiredCourseId  = $RequiredCourseId
    ValidityDays      = $ValidityDays
    Total             = $total
    Compliant         = $compliant
    Expired           = $expired
    NotCompleted      = $notDone
    CompliancePct     = $rate
}
$summary | ConvertTo-Json -Depth 3 | Set-Content -Path (Join-Path $OutputPath "training-summary-$ts.json")

# Manifest
$manifest = @($jsonPath, $csvPath) | ForEach-Object {
    [PSCustomObject]@{
        file          = Split-Path $_ -Leaf
        sha256        = (Get-FileHash $_ -Algorithm SHA256).Hash
        bytes         = (Get-Item $_).Length
        generated_utc = $ts
        script        = 'Get-TrainingCompliance'
    }
}
$manifest | ConvertTo-Json -Depth 4 | Set-Content -Path (Join-Path $OutputPath "manifest-compliance-$ts.json")
```

---

## Script 3 — Send Reminders (Mutation; -WhatIf Required)

```powershell
<#
.SYNOPSIS
    Send training reminder emails via Microsoft Graph.
.DESCRIPTION
    Sends from a designated mailbox using Send-MgUserMail. Supports -WhatIf
    and ShouldProcess so dry-runs are safe. Records every send (or would-send)
    in an evidence artifact.
.PARAMETER NonCompliantCsv
    Output of Script 2 filtered to Status -ne 'Compliant'.
.PARAMETER SenderUpn
    Mailbox to send from (must be licensed; service mailbox preferred).
.PARAMETER TrainingUrl
    Deep link to the training page in Viva Learning or your LMS.
.EXAMPLE
    .\Send-TrainingReminders.ps1 -NonCompliantCsv .\non-compliant.csv `
        -SenderUpn aigov-no-reply@contoso.com `
        -TrainingUrl 'https://contoso.sharepoint.com/sites/AIGovernanceLearning' -WhatIf
#>
[CmdletBinding(SupportsShouldProcess, ConfirmImpact = 'High')]
param(
    [Parameter(Mandatory)] [string]$NonCompliantCsv,
    [Parameter(Mandatory)] [string]$SenderUpn,
    [Parameter(Mandatory)] [string]$TrainingUrl,
    [string]$OutputPath = ".\evidence-2.14"
)

# Requires the Mail.Send delegated or application scope with consent.
# Connect-MgGraph -Scopes 'Mail.Send' -Environment Global

$ErrorActionPreference = 'Stop'
New-Item -ItemType Directory -Force -Path $OutputPath | Out-Null
$ts = Get-Date -Format 'yyyyMMddTHHmmssZ'
$log = @()

$users = Import-Csv -Path $NonCompliantCsv
foreach ($u in $users) {
    $body = @"
Hello $($u.DisplayName),

Our records indicate you have not completed (or your completion has expired) the
required AI Governance training associated with your role: $($u.EntraRole).

Please complete the training within 14 days:
$TrainingUrl

This requirement supports our firm's obligations under FINRA Rule 3110 and
related supervisory expectations. If you believe this notice is in error,
contact the AI Governance team.

— AI Governance Office
"@

    $message = @{
        message = @{
            subject      = 'Action required: AI Governance training'
            body         = @{ contentType = 'Text'; content = $body }
            toRecipients = @(@{ emailAddress = @{ address = $u.Mail } })
        }
        saveToSentItems = $true
    }

    if ($PSCmdlet.ShouldProcess($u.Mail, "Send AI Governance training reminder")) {
        try {
            Send-MgUserMail -UserId $SenderUpn -BodyParameter $message
            $log += [PSCustomObject]@{ Mail = $u.Mail; Status = 'Sent'; Utc = (Get-Date).ToUniversalTime().ToString('o') }
        } catch {
            $log += [PSCustomObject]@{ Mail = $u.Mail; Status = "Error: $($_.Exception.Message)"; Utc = (Get-Date).ToUniversalTime().ToString('o') }
        }
    } else {
        $log += [PSCustomObject]@{ Mail = $u.Mail; Status = 'WhatIf'; Utc = (Get-Date).ToUniversalTime().ToString('o') }
    }
}

$logPath = Join-Path $OutputPath "reminder-log-$ts.csv"
$log | Export-Csv -Path $logPath -NoTypeInformation -Encoding UTF8

[PSCustomObject]@{
    file          = Split-Path $logPath -Leaf
    sha256        = (Get-FileHash $logPath -Algorithm SHA256).Hash
    bytes         = (Get-Item $logPath).Length
    generated_utc = $ts
    script        = 'Send-TrainingReminders'
} | ConvertTo-Json | Set-Content -Path (Join-Path $OutputPath "manifest-reminders-$ts.json")

Write-Host "Reminders processed: $($log.Count). See $logPath" -ForegroundColor Cyan
```

---

## Notes on Viva Learning Programmatic Access

If your firm wants direct (non-LMS) reads of Viva Learning data, the relevant Microsoft Graph surface is `/employeeExperience/learningProviders` and related entities. As of April 2026 these endpoints are **beta**. Treat them as "monitor-only" for now; do not use them as the system of record for FINRA / SEC examinations until they reach v1.0 GA. See [Microsoft Learn — Employee experience overview](https://learn.microsoft.com/en-us/graph/api/resources/employeeexperience-overview).

---

[Back to Control 2.14](../../../controls/pillar-2-management/2.14-training-and-awareness-program.md) | [Portal Walkthrough](portal-walkthrough.md) | [Verification & Testing](verification-testing.md) | [Troubleshooting](troubleshooting.md)
