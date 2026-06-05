# PowerShell Setup: Control 2.19 — Customer AI Disclosure and Transparency

!!! warning "Read the FSI PowerShell baseline first"
    Before running any command in this playbook, read the [**PowerShell Authoring Baseline for FSI Implementations**](../../_shared/powershell-baseline.md). It is the canonical source for module version pinning, sovereign-cloud (GCC / GCC High / DoD) endpoints, mutation safety (`-WhatIf` / `SupportsShouldProcess`), Dataverse compatibility, and SHA-256 evidence emission. Snippets below are abbreviated; the baseline is authoritative.

**Last Updated:** April 2026
**Modules Required:** `Microsoft.PowerApps.Administration.PowerShell` (Windows PowerShell 5.1, Desktop edition only) for environment metadata; `Microsoft.PowerPlatform.Dataverse.Client` (preferred) **or** `Microsoft.Xrm.Data.PowerShell` (legacy, still supported) for Dataverse log queries; `Az.OperationalInsights` if logs land in a Log Analytics workspace

!!! note "Scope of automation"
    Microsoft Copilot Studio does not currently expose an admin-API to mutate topic content (greeting / Escalate). The disclosure copy and the **Transfer conversation** node must be configured in the **portal walkthrough**. The PowerShell scripts below are read-only / reporting helpers used to **evidence** disclosure delivery and escalation behavior. Treat all sample numbers as **ILLUSTRATIVE**.

---

## Prerequisites

```powershell
# Pin versions per your CAB (illustrative versions shown).
Install-Module -Name Microsoft.PowerApps.Administration.PowerShell `
    -RequiredVersion '<approved-version>' -Repository PSGallery -Scope CurrentUser -AllowClobber

# Preferred modern Dataverse client
Install-Module -Name Microsoft.PowerPlatform.Dataverse.Client `
    -RequiredVersion '<approved-version>' -Repository PSGallery -Scope CurrentUser -AllowClobber

# Legacy fallback (still supported in many tenants)
# Install-Module -Name Microsoft.Xrm.Data.PowerShell -RequiredVersion '<approved-version>' ...
```

```powershell
# Edition guard for Power Apps Administration cmdlets (per baseline §2)
if ($PSVersionTable.PSEdition -ne 'Desktop') {
    throw "Microsoft.PowerApps.Administration.PowerShell requires Windows PowerShell 5.1 (Desktop). Detected: $($PSVersionTable.PSEdition) $($PSVersionTable.PSVersion)."
}
```

For sovereign tenants (GCC / GCC High / DoD), set the appropriate cloud endpoint per the baseline before connecting.

---

## Script 1: Query the Disclosure-Event Log (Read-Only)

```powershell
<#
.SYNOPSIS
    Query the AI disclosure event log from Dataverse for a given period.
.DESCRIPTION
    Read-only export. Produces a CSV and a summary suitable for evidence collection
    under SEC 17a-4 / FINRA 4511 (recordkeeping) and Control 2.19 verification.
.PARAMETER DataverseUrl
    Org URL, e.g. https://contoso.crm.dynamics.com
.PARAMETER StartDate
    Inclusive start (UTC).
.PARAMETER EndDate
    Inclusive end (UTC).
.PARAMETER OutputPath
    Folder to write CSV + summary JSON.
.EXAMPLE
    .\Get-DisclosureLog.ps1 -DataverseUrl 'https://contoso.crm.dynamics.com' `
        -StartDate '2026-01-01' -EndDate '2026-01-31' -OutputPath '.\evidence\2.19'
.NOTES
    Read-only. No SupportsShouldProcess required — no tenant mutation.
#>
[CmdletBinding()]
param(
    [Parameter(Mandatory)] [string]   $DataverseUrl,
    [Parameter()]          [datetime] $StartDate = (Get-Date).AddDays(-30).ToUniversalTime(),
    [Parameter()]          [datetime] $EndDate   = (Get-Date).ToUniversalTime(),
    [Parameter()]          [string]   $OutputPath = '.\evidence\2.19'
)

$ErrorActionPreference = 'Stop'
New-Item -ItemType Directory -Path $OutputPath -Force | Out-Null

Write-Host "[INFO] Connecting to Dataverse: $DataverseUrl" -ForegroundColor Cyan
# Modern client (recommended). Auth method should be MFA / managed identity per baseline.
Import-Module Microsoft.PowerPlatform.Dataverse.Client
$client = Get-CrmConnection -InteractiveMode -OrganizationUrl $DataverseUrl

$fetchXml = @"
<fetch top="5000">
  <entity name="fsi_aidisclosurelog">
    <attribute name="fsi_sessionid" />
    <attribute name="fsi_eventtype" />
    <attribute name="fsi_disclosuretype" />
    <attribute name="fsi_disclosureversion" />
    <attribute name="fsi_jurisdiction" />
    <attribute name="fsi_channel" />
    <attribute name="fsi_userpseudoid" />
    <attribute name="createdon" />
    <filter type="and">
      <condition attribute="createdon" operator="on-or-after" value="$($StartDate.ToString('o'))" />
      <condition attribute="createdon" operator="on-or-before" value="$($EndDate.ToString('o'))" />
    </filter>
    <order attribute="createdon" descending="false" />
  </entity>
</fetch>
"@

$results = $client.RetrieveMultiple([Microsoft.Xrm.Sdk.Query.FetchExpression]::new($fetchXml))
$rows = $results.Entities | ForEach-Object {
    [pscustomobject]@{
        SessionId         = $_['fsi_sessionid']
        EventType         = $_['fsi_eventtype']
        DisclosureType    = $_['fsi_disclosuretype']
        DisclosureVersion = $_['fsi_disclosureversion']
        Jurisdiction      = $_['fsi_jurisdiction']
        Channel           = $_['fsi_channel']
        UserPseudoId      = $_['fsi_userpseudoid']
        Timestamp         = $_['createdon']
    }
}

# --- Summary ---
$total              = $rows.Count
$delivered          = ($rows | Where-Object EventType -eq 'DisclosureDelivered').Count
$reminders          = ($rows | Where-Object EventType -eq 'ReminderDelivered').Count
$escalationsOffered = ($rows | Where-Object EventType -eq 'EscalationOffered').Count
$escalationsTaken   = ($rows | Where-Object EventType -eq 'EscalationAccepted').Count
$takeRate           = if ($escalationsOffered) { [math]::Round(($escalationsTaken / $escalationsOffered) * 100, 1) } else { 0 }

Write-Host "`n=== Disclosure Event Summary (period $($StartDate.ToString('u')) → $($EndDate.ToString('u'))) ===" -ForegroundColor Cyan
Write-Host "Total events              : $total"
Write-Host "Disclosures delivered     : $delivered"
Write-Host "Reminders delivered       : $reminders"
Write-Host "Escalations offered       : $escalationsOffered"
Write-Host "Escalations accepted      : $escalationsTaken"
Write-Host "Escalation take rate (%)  : $takeRate"

# --- Outputs ---
$csvPath  = Join-Path $OutputPath ("DisclosureLog-{0:yyyyMMdd-HHmmss}.csv" -f (Get-Date))
$jsonPath = Join-Path $OutputPath ("DisclosureSummary-{0:yyyyMMdd-HHmmss}.json" -f (Get-Date))

$rows | Export-Csv -Path $csvPath -NoTypeInformation -Encoding UTF8

[pscustomobject]@{
    PeriodStartUtc            = $StartDate
    PeriodEndUtc              = $EndDate
    TotalEvents               = $total
    DisclosuresDelivered      = $delivered
    RemindersDelivered        = $reminders
    EscalationsOffered        = $escalationsOffered
    EscalationsAccepted       = $escalationsTaken
    EscalationTakeRatePercent = $takeRate
    GeneratedUtc              = (Get-Date).ToUniversalTime()
} | ConvertTo-Json -Depth 4 | Out-File -FilePath $jsonPath -Encoding UTF8

# --- Evidence integrity (per baseline §4) ---
$csvHash  = (Get-FileHash -Path $csvPath  -Algorithm SHA256).Hash
$jsonHash = (Get-FileHash -Path $jsonPath -Algorithm SHA256).Hash
"$csvHash  $(Split-Path $csvPath  -Leaf)"  | Out-File -FilePath (Join-Path $OutputPath 'SHA256SUMS.txt') -Append -Encoding UTF8
"$jsonHash  $(Split-Path $jsonPath -Leaf)" | Out-File -FilePath (Join-Path $OutputPath 'SHA256SUMS.txt') -Append -Encoding UTF8

Write-Host "`n[PASS] CSV  : $csvPath"
Write-Host "[PASS] JSON : $jsonPath"
Write-Host "[PASS] SHA-256 hashes appended to SHA256SUMS.txt"
```

---

## Script 2: Generate a Markdown Compliance Report

```powershell
<#
.SYNOPSIS
    Render a Compliance-friendly Markdown report from a previously-exported summary JSON.
.DESCRIPTION
    Pure transform: JSON → Markdown. No tenant connection. Safe to run on an evidence host.
.PARAMETER SummaryJsonPath
    Path to a JSON file produced by Get-DisclosureLog.ps1.
.PARAMETER OutputPath
    Folder to write the Markdown report.
.EXAMPLE
    .\New-DisclosureComplianceReport.ps1 -SummaryJsonPath '.\evidence\2.19\DisclosureSummary-20260131-090000.json'
#>
[CmdletBinding()]
param(
    [Parameter(Mandatory)] [string] $SummaryJsonPath,
    [Parameter()]          [string] $OutputPath = (Split-Path $SummaryJsonPath -Parent)
)

$summary = Get-Content $SummaryJsonPath -Raw | ConvertFrom-Json

$md = @"
# Control 2.19 — Disclosure Compliance Report

**Period (UTC):** $($summary.PeriodStartUtc) → $($summary.PeriodEndUtc)
**Generated (UTC):** $($summary.GeneratedUtc)

## Summary

| Metric | Value |
|--------|-------|
| Total events | $($summary.TotalEvents) |
| Disclosures delivered | $($summary.DisclosuresDelivered) |
| Reminders delivered | $($summary.RemindersDelivered) |
| Escalations offered | $($summary.EscalationsOffered) |
| Escalations accepted | $($summary.EscalationsAccepted) |
| Escalation take rate (%) | $($summary.EscalationTakeRatePercent) |

## Interpretation Notes

- A near-100% ratio of `DisclosuresDelivered` to unique sessions in the period suggests the Conversation Start topic is wired correctly across channels.
- A material drop in `DisclosuresDelivered` against session counts in the underlying engagement-hub system may indicate a regression — see Troubleshooting.
- Escalation take rate is informational only; correct *availability* of the human-handoff path is what supports compliance with FINRA Rule 2210, CFPB UDAAP, and Colorado AI Act on-request handoff requirements.

## Evidence References

- Source export: $(Split-Path $SummaryJsonPath -Leaf)
- See `SHA256SUMS.txt` in the same evidence folder for integrity hashes.

---
*Generated by FSI Agent Governance Framework — Control 2.19*
"@

$reportPath = Join-Path $OutputPath ("DisclosureComplianceReport-{0:yyyyMMdd-HHmmss}.md" -f (Get-Date))
$md | Out-File -FilePath $reportPath -Encoding UTF8
Write-Host "[PASS] Report written: $reportPath"
```

---

## Script 3: Validate Control 2.19 Configuration (Read-Only)

```powershell
<#
.SYNOPSIS
    Performs read-only validation checks for Control 2.19.
.DESCRIPTION
    Confirms (1) presence of the disclosure-event log table in Dataverse, (2) at least one
    DisclosureDelivered event in the last 24 hours, and (3) at least one EscalationOffered
    event in the last 7 days. Emits a structured result for evidence collection.
.PARAMETER DataverseUrl
    Org URL.
.EXAMPLE
    .\Validate-Control-2.19.ps1 -DataverseUrl 'https://contoso.crm.dynamics.com'
#>
[CmdletBinding()]
param(
    [Parameter(Mandatory)] [string] $DataverseUrl
)

$ErrorActionPreference = 'Stop'
$results = [System.Collections.Generic.List[object]]::new()

function Add-Check {
    param([string]$Id, [string]$Name, [bool]$Pass, [string]$Detail)
    $results.Add([pscustomobject]@{
        CheckId  = $Id
        Name     = $Name
        Status   = if ($Pass) { 'PASS' } else { 'FAIL' }
        Detail   = $Detail
        TimeUtc  = (Get-Date).ToUniversalTime()
    })
}

Import-Module Microsoft.PowerPlatform.Dataverse.Client
$client = Get-CrmConnection -InteractiveMode -OrganizationUrl $DataverseUrl

# Check 1: Log table exists
try {
    $null = $client.RetrieveMultiple(
        [Microsoft.Xrm.Sdk.Query.FetchExpression]::new('<fetch top="1"><entity name="fsi_aidisclosurelog"/></fetch>'))
    Add-Check 'C1' 'Disclosure log table reachable' $true 'fsi_aidisclosurelog responded.'
} catch {
    Add-Check 'C1' 'Disclosure log table reachable' $false $_.Exception.Message
}

# Check 2: Recent DisclosureDelivered
$since24h = (Get-Date).ToUniversalTime().AddHours(-24).ToString('o')
$fetch2 = @"
<fetch top="1">
  <entity name="fsi_aidisclosurelog">
    <filter>
      <condition attribute="fsi_eventtype" operator="eq" value="DisclosureDelivered" />
      <condition attribute="createdon" operator="on-or-after" value="$since24h" />
    </filter>
  </entity>
</fetch>
"@
try {
    $r = $client.RetrieveMultiple([Microsoft.Xrm.Sdk.Query.FetchExpression]::new($fetch2))
    Add-Check 'C2' 'DisclosureDelivered event in last 24h' ($r.Entities.Count -ge 1) "Rows: $($r.Entities.Count)"
} catch {
    Add-Check 'C2' 'DisclosureDelivered event in last 24h' $false $_.Exception.Message
}

# Check 3: EscalationOffered in last 7 days
$since7d = (Get-Date).ToUniversalTime().AddDays(-7).ToString('o')
$fetch3 = @"
<fetch top="1">
  <entity name="fsi_aidisclosurelog">
    <filter>
      <condition attribute="fsi_eventtype" operator="eq" value="EscalationOffered" />
      <condition attribute="createdon" operator="on-or-after" value="$since7d" />
    </filter>
  </entity>
</fetch>
"@
try {
    $r = $client.RetrieveMultiple([Microsoft.Xrm.Sdk.Query.FetchExpression]::new($fetch3))
    Add-Check 'C3' 'EscalationOffered event in last 7 days' ($r.Entities.Count -ge 1) "Rows: $($r.Entities.Count)"
} catch {
    Add-Check 'C3' 'EscalationOffered event in last 7 days' $false $_.Exception.Message
}

$results | Format-Table -AutoSize
$exit = ($results | Where-Object Status -eq 'FAIL').Count
exit $exit
```

---

## Operational Notes

- **No mutation cmdlets** are included — disclosure copy and the **Transfer conversation** node must be edited in the Copilot Studio portal (see [portal walkthrough](portal-walkthrough.md))
- For Power Automate flow exports (the `LogAiDisclosureEvent` flow), use the standard solution-export pipeline (Control 2.4) — do **not** edit flow JSON in place
- For sovereign tenants, replace authentication with managed-identity / certificate flows per baseline §3
- Schedule Script 1 + Script 2 as a monthly Azure Automation runbook; deposit outputs in an immutable storage account (WORM/legal-hold) to support SEC 17a-4 / FINRA 4511 retention

---

[Back to Control 2.19](../../../controls/pillar-2-management/2.19-customer-ai-disclosure-and-transparency.md) | [Portal Walkthrough](portal-walkthrough.md) | [Verification Testing](verification-testing.md) | [Troubleshooting](troubleshooting.md)
---

*Updated: May 2026 | Version: v1.6.2 | UI Verification Status: Current*
