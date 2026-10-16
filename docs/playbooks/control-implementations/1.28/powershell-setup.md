# PowerShell Setup: Control 1.28 - Policy-Based Agent Publishing Restrictions

!!! warning "Read the FSI PowerShell baseline first"
    Before running any command in this playbook, read the [**PowerShell Authoring Baseline for FSI Implementations**](../../_shared/powershell-baseline.md). It is authoritative for module pinning, mutation safety, Dataverse compatibility, and SHA-256 evidence emission.

**Last Updated:** October 2026<br>
**Primary Module:** `Microsoft.PowerApps.Administration.PowerShell` (Windows PowerShell 5.1, Desktop edition)<br>
**Estimated Time:** 30-45 minutes (initial setup); inventory collection depends on environment count

## Prerequisites

- [ ] Windows PowerShell 5.1, as required by [Microsoft's PowerShell guidance](https://learn.microsoft.com/en-us/power-platform/admin/powerapps-powershell)
- [ ] Power Platform Admin role for tenant data policies
- [ ] Approved pinned module versions and tested policy definitions
- [ ] Authorized Dataverse read access for the environments being inventoried

## Module Installation (Pinned)

```powershell
if ($PSVersionTable.PSEdition -ne 'Desktop' -or $PSVersionTable.PSVersion.Major -ne 5) {
    throw 'Use Windows PowerShell 5.1 for the Power Platform administration module.'
}

Install-Module -Name Microsoft.PowerApps.Administration.PowerShell `
    -RequiredVersion '<version>' -Repository PSGallery -Scope CurrentUser `
    -AllowClobber -AcceptLicense
Install-Module -Name Microsoft.PowerApps.PowerShell `
    -RequiredVersion '<version>' -Repository PSGallery -Scope CurrentUser `
    -AllowClobber -AcceptLicense
Import-Module Microsoft.PowerApps.Administration.PowerShell -ErrorAction Stop
Add-PowerAppsAccount -Endpoint prod
```

Use `Get-Command` and `Get-Help` against the approved version. Current Learn references document `New-DlpPolicy`, `Get-DlpPolicy`, `Set-DlpPolicy`, and `Remove-DlpPolicy`. Do not assume older Admin-prefixed commands are aliases or that `Add-PowerAppEnvironmentToPolicy` / `Get-AdminPowerAppChatbot` exist: the live references reviewed for this control do not establish those commands.

## Script 1 - Discover Current DLP Posture (Read-Only)

Save as `Export-DlpPolicyEvidence.ps1` after the module/session setup above. Preserve the complete response rather than projecting unverified `PolicyName`, `Environments`, or compliance fields. Microsoft examples can return policy definitions under a `.value` collection; inspect the actual response from the pinned module before processing it.

```powershell
$ErrorActionPreference = 'Stop'
$timestamp = Get-Date -Format 'yyyyMMdd-HHmmss'
$outDir = Join-Path (Get-Location) 'evidence\1.28'
New-Item -ItemType Directory -Force -Path $outDir | Out-Null
$policies = Get-DlpPolicy -ErrorAction Stop
if ($null -eq $policies) { throw 'No policy response returned; do not treat this as verified coverage.' }

$jsonPath = Join-Path $outDir "dlp-policies-$timestamp.json"
$policies | ConvertTo-Json -Depth 100 |
    Out-File -FilePath $jsonPath -Encoding UTF8 -ErrorAction Stop
$hash = (Get-FileHash -Path $jsonPath -Algorithm SHA256 -ErrorAction Stop).Hash
"$jsonPath`tSHA256:$hash" |
    Out-File -FilePath (Join-Path $outDir "evidence-manifest-$timestamp.txt") -Encoding UTF8
Write-Host "Policy evidence: $jsonPath"
Write-Host "SHA-256: $hash"
```

Reconcile this response with PPAC's saved policy Scope / Applied to information. An empty inventory in a tenant with known policies is a failed collection, not a clean result.

## Script 2 - Apply an Approved Policy Definition (Mutation; WhatIf Supported)

[New-DlpPolicy](https://learn.microsoft.com/en-us/powershell/module/microsoft.powerapps.administration.powershell/new-dlppolicy) supports `-NewPolicy`. [Set-DlpPolicy](https://learn.microsoft.com/en-us/powershell/module/microsoft.powerapps.administration.powershell/set-dlppolicy) requires `-PolicyName` and `-UpdatedPolicy`; it does **not** expose `-ConnectorGroups`.

The following wrapper accepts a complete, separately approved and version-tested policy definition. It does not invent a connector payload or derive scope from environment names. For first-time configuration without such a definition, use the [Portal Walkthrough](portal-walkthrough.md).

```powershell
[CmdletBinding(SupportsShouldProcess = $true, ConfirmImpact = 'High')]
param(
    [Parameter(Mandatory)]
    [ValidateSet('Create', 'Update')]
    [string] $Operation,
    [Parameter(Mandatory)]
    [string] $DefinitionPath,
    [string] $PolicyName
)

$ErrorActionPreference = 'Stop'
$definition = Get-Content -LiteralPath $DefinitionPath -Raw -ErrorAction Stop |
    ConvertFrom-Json -ErrorAction Stop
if ($null -eq $definition) { throw 'An approved policy definition is required.' }
if ($Operation -eq 'Update' -and [string]::IsNullOrWhiteSpace($PolicyName)) {
    throw 'Update requires the existing policy GUID in PolicyName.'
}

if ($PSCmdlet.ShouldProcess($DefinitionPath, "$Operation data policy")) {
    $timestamp = Get-Date -Format 'yyyyMMdd-HHmmss'
    $evidencePath = Join-Path (Get-Location) 'evidence\1.28'
    New-Item -ItemType Directory -Force -Path $evidencePath | Out-Null
    Start-Transcript -Path (Join-Path $evidencePath "policy-change-$timestamp.log") -ErrorAction Stop
    try {
        $before = Get-DlpPolicy -ErrorAction Stop
        if ($null -eq $before) { throw 'Cannot snapshot current policies; mutation stopped.' }
        $before | ConvertTo-Json -Depth 100 |
            Out-File -FilePath (Join-Path $evidencePath "before-$timestamp.json") -Encoding UTF8
        if ($Operation -eq 'Create') {
            New-DlpPolicy -NewPolicy $definition -ErrorAction Stop
        } else {
            Set-DlpPolicy -PolicyName $PolicyName -UpdatedPolicy $definition -ErrorAction Stop
        }
        Get-DlpPolicy -ErrorAction Stop | ConvertTo-Json -Depth 100
    } finally {
        Stop-Transcript
    }
}
```

Run with `-WhatIf` first. After an approved mutation, separately inspect the read-back and PPAC saved settings for the exact policy GUID, connector classifications, default group, and environment scope. A successful command alone is not verification. The wrapper snapshots current policies and records a transcript, but does not provide automatic rollback; test restoration in non-production. These excerpts show core operations only: integrate the shared baseline's JSON evidence manifest and hashing of all snapshots/transcripts in the production runbook.

## Step 3 - Assign Policy Scope by Explicit Environment ID

Use PPAC **Security -> Data and privacy -> Data policy -> [Policy] -> Edit Policy**, select the intended scope and environment IDs, and save. Follow [Manage data policies](https://learn.microsoft.com/en-us/power-platform/admin/prevent-data-loss).

For automation, include the reviewed scope/environment definition in Script 2's complete policy payload, validated against your pinned module. Do not run the previously suggested `Add-PowerAppEnvironmentToPolicy` loop or infer production scope solely from a display-name wildcard. Capture policy read-back with Script 1 and test the actual assigned environment.

## Script 4 - Hash a Dataverse Agent Inventory Export (Read-Only Evidence)

Microsoft documents inventory through the CoE dashboard or a Power Automate Dataverse **List rows from selected environment** action in [Configure data policies for agents](https://learn.microsoft.com/en-us/microsoft-copilot-studio/admin-data-loss-prevention#identify-and-troubleshoot-the-impact-of-data-policies). The [Agent (bot) table](https://learn.microsoft.com/en-us/power-apps/developer/data-platform/reference/entities/bot) is the source for agent records; it is not a per-agent DLP assessment API.

1. For each in-scope environment, use the authorized Dataverse connection to list Bots rows; handle pagination and document any failed or inaccessible environments.
2. Export a CSV with `EnvironmentId`, `botid`, `name`, `modifiedon`, and creator identity where available. Resolve lookup values explicitly if an identity is needed.
3. Reconcile publication state with Copilot Studio's published-agent view. Do not relabel Dataverse active/inactive state as `PublishStatus`.
4. Obtain per-agent DLP evidence from **Channels -> Details -> Download**. Preserve its DLP violations / Blocked channels sheets separately; inventory alone cannot produce compliant-agent totals.
5. Save the CSV outside tracked documentation, then run this evidence wrapper as `Hash-AgentInventory.ps1`:

```powershell
[CmdletBinding()]
param(
    [Parameter(Mandatory)]
    [string] $CsvPath
)

$ErrorActionPreference = 'Stop'
$csv = Get-Item -LiteralPath $CsvPath -ErrorAction Stop
if ($csv.PSIsContainer -or $csv.Extension -ne '.csv') {
    throw 'CsvPath must identify an existing CSV inventory export.'
}
$rows = @(Import-Csv -LiteralPath $csv.FullName -ErrorAction Stop)
if ($rows.Count -eq 0) { throw 'Empty inventory; reconcile collection scope before recording evidence.' }
$required = @('EnvironmentId', 'botid', 'name', 'modifiedon')
foreach ($column in $required) {
    if ($rows[0].PSObject.Properties.Name -notcontains $column) {
        throw "Inventory is missing required column: $column"
    }
}
$hash = (Get-FileHash -LiteralPath $csv.FullName -Algorithm SHA256 -ErrorAction Stop).Hash
$manifestPath = "$($csv.FullName).sha256.txt"
"$($csv.FullName)`tSHA256:$hash" |
    Out-File -LiteralPath $manifestPath -Encoding UTF8 -ErrorAction Stop
Write-Host "Inventory rows: $($rows.Count)"
Write-Host "SHA-256: $hash"
Write-Host "Evidence manifest: $manifestPath"
```

This validates the export's shape and hash, not collection completeness or DLP posture. Reconcile counts, environment access, and pagination before accepting the evidence.

## Step 5 - Schedule Evidence Collection

Schedule the **configured Dataverse inventory flow** weekly and review its failures, pagination, and environment coverage. If scheduling Script 1 locally, use Windows PowerShell 5.1 and the approved authentication/runbook pattern from the shared baseline. A Windows scheduled-task account is not a Microsoft Entra service principal, and an unattended task cannot rely on interactive sign-in.

Script 4 hashes an existing export; it does not refresh the inventory. Do not schedule it alone as an agent discovery job.

## Validation Commands

```powershell
Get-Command -Module Microsoft.PowerApps.Administration.PowerShell -Name *Dlp*
Get-Help New-DlpPolicy -Full
Get-Help Set-DlpPolicy -Full
Get-DlpPolicy -ErrorAction Stop | ConvertTo-Json -Depth 100
Get-FileHash -LiteralPath '<inventory.csv>' -Algorithm SHA256
```

## Known Gaps in PowerShell Coverage

- No documented per-agent DLP pass/fail cmdlet is established by the sources reviewed here. Use actual Copilot Studio error details and workbook exports.
- No documented native publishing-approval cmdlet is established here. Use a configured intake/pipeline gate and role restrictions.
- Do not treat an unavailable cmdlet or inaccessible environment as an empty, successful inventory.
- These examples were checked against live Microsoft Learn on 2026-10-14, not executed against a tenant. Validate approved definitions and pinned module behavior in non-production before use.

---

[Back to Control 1.28](../../../controls/pillar-1-security/1.28-policy-based-agent-publishing-restrictions.md) | [Portal Walkthrough](portal-walkthrough.md) | [Verification & Testing](verification-testing.md) | [Troubleshooting](troubleshooting.md)

---

*Updated: October 2026 | Version: v1.6.2 | UI Verification Status: Current (Microsoft Learn review 2026-10-14; tenant execution pending)*
