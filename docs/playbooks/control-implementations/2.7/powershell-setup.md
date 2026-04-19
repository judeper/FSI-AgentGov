# Control 2.7: Vendor and Third-Party Risk Management — PowerShell Setup

> Companion to [Control 2.7](../../../controls/pillar-2-management/2.7-vendor-and-third-party-risk-management.md). Provides read-mostly PowerShell automation for connector inventory, DLP analysis, custom-connector enumeration, and vendor evidence collection.

!!! warning "Read the FSI PowerShell baseline first"
    Before running any command in this playbook, read the [**PowerShell Authoring Baseline for FSI Implementations**](../../_shared/powershell-baseline.md). It is the canonical source for module version pinning, sovereign-cloud (GCC / GCC High / DoD) endpoints, mutation safety (`-WhatIf` / `SupportsShouldProcess`), Dataverse compatibility, and SHA-256 evidence emission. Snippets below show abbreviated patterns; the baseline is authoritative.

!!! info "Read-mostly by design"
    These scripts read tenant state and emit evidence files. They **do not** mutate DLP policies, connector classifications, or Copilot Studio settings. Use the portal walkthrough or your IaC pipeline for change-controlled mutations. All emitted files should be hashed (SHA-256) and stored in your audit-evidence repository.

---

## Prerequisites

```powershell
# Pin module versions per the FSI baseline
Install-Module -Name Microsoft.PowerApps.Administration.PowerShell -RequiredVersion 2.0.198 -Force
Install-Module -Name Microsoft.Graph.DeviceManagement.Enrollment -Scope CurrentUser -Force  # for ServiceMessage
Install-Module -Name Microsoft.Graph.Reports -Scope CurrentUser -Force

# Interactive auth (use device code in restricted endpoints)
Add-PowerAppsAccount -Endpoint prod    # use 'usgov', 'usgovhigh', 'dod' for sovereign clouds

# Required role: Power Platform Admin (read-only sufficient for inventory)
Get-AdminPowerAppEnvironment | Select-Object DisplayName, EnvironmentName, EnvironmentType | Format-Table
```

---

## 1. Connector Inventory Across All Environments

```powershell
function Export-PpConnectorInventory {
    [CmdletBinding()]
    param(
        [string]$OutputPath = ".\evidence\2.7\connector-inventory.csv"
    )
    New-Item -ItemType Directory -Path (Split-Path $OutputPath) -Force | Out-Null

    $envs = Get-AdminPowerAppEnvironment
    $rows = foreach ($env in $envs) {
        Write-Verbose "Scanning environment $($env.DisplayName)"
        $connectors = Get-AdminPowerAppConnector -EnvironmentName $env.EnvironmentName -ErrorAction SilentlyContinue
        foreach ($c in $connectors) {
            [pscustomobject]@{
                EnvironmentDisplayName = $env.DisplayName
                EnvironmentId          = $env.EnvironmentName
                EnvironmentType        = $env.EnvironmentType
                ConnectorName          = $c.DisplayName
                ConnectorId            = $c.Name
                Publisher              = $c.Properties.publisher
                IsMicrosoft            = ($c.Properties.publisher -eq 'Microsoft')
                IsCustom               = ($c.Properties.connectorType -eq 'Custom')
                CreatedBy              = $c.Properties.createdBy.displayName
                CreatedTime            = $c.Properties.createdTime
                ApiDefinitionUrl       = $c.Properties.apiDefinitionUrl
                CollectedAt            = (Get-Date).ToUniversalTime().ToString('o')
            }
        }
    }

    $rows | Export-Csv -Path $OutputPath -NoTypeInformation -Encoding UTF8
    $hash = (Get-FileHash -Path $OutputPath -Algorithm SHA256).Hash
    Write-Host "Inventory written: $OutputPath" -ForegroundColor Green
    Write-Host "SHA-256: $hash"
    return [pscustomobject]@{ Path = $OutputPath; Sha256 = $hash; RowCount = $rows.Count }
}

Export-PpConnectorInventory -Verbose
```

---

## 2. DLP Policy Posture Report

```powershell
function Export-DlpPolicyPosture {
    [CmdletBinding()]
    param(
        [string]$OutputPath = ".\evidence\2.7\dlp-policy-posture.csv"
    )
    New-Item -ItemType Directory -Path (Split-Path $OutputPath) -Force | Out-Null

    $policies = Get-DlpPolicy
    $rows = foreach ($p in $policies) {
        $business    = $p.connectorGroups | Where-Object { $_.classification -eq 'General' }
        $nonBusiness = $p.connectorGroups | Where-Object { $_.classification -eq 'Confidential' }
        $blocked     = $p.connectorGroups | Where-Object { $_.classification -eq 'Blocked' }

        [pscustomobject]@{
            PolicyName            = $p.displayName
            PolicyId              = $p.name
            EnvironmentType       = $p.environmentType
            BusinessConnectors    = ($business.connectors | Measure-Object).Count
            NonBusinessConnectors = ($nonBusiness.connectors | Measure-Object).Count
            BlockedConnectors     = ($blocked.connectors | Measure-Object).Count
            CustomConnectorRule   = $p.customConnectorUrlPatternsDefinition.rules.order -join ';'
            CreatedTime           = $p.createdTime
            LastModifiedTime      = $p.lastModifiedTime
            CollectedAt           = (Get-Date).ToUniversalTime().ToString('o')
        }
    }

    $rows | Export-Csv -Path $OutputPath -NoTypeInformation -Encoding UTF8
    $hash = (Get-FileHash $OutputPath -Algorithm SHA256).Hash
    Write-Host "DLP posture written: $OutputPath  SHA-256: $hash" -ForegroundColor Green
    return $rows
}

Export-DlpPolicyPosture
```

---

## 3. Custom Connector Enumeration (Highest Risk Tier T4)

```powershell
function Export-CustomConnectorInventory {
    [CmdletBinding()]
    param(
        [string]$OutputPath = ".\evidence\2.7\custom-connectors.csv"
    )
    New-Item -ItemType Directory -Path (Split-Path $OutputPath) -Force | Out-Null

    $envs = Get-AdminPowerAppEnvironment
    $rows = foreach ($env in $envs) {
        $custom = Get-AdminPowerAppConnector -EnvironmentName $env.EnvironmentName |
                  Where-Object { $_.Properties.connectorType -eq 'Custom' -or $_.Properties.publisher -ne 'Microsoft' }
        foreach ($c in $custom) {
            [pscustomobject]@{
                Environment      = $env.DisplayName
                ConnectorName    = $c.DisplayName
                Publisher        = $c.Properties.publisher
                CreatedBy        = $c.Properties.createdBy.displayName
                CreatedTime      = $c.Properties.createdTime
                ApiDefinitionUrl = $c.Properties.apiDefinitionUrl
                CollectedAt      = (Get-Date).ToUniversalTime().ToString('o')
            }
        }
    }

    $rows | Export-Csv -Path $OutputPath -NoTypeInformation -Encoding UTF8
    Write-Host "Custom connector inventory: $($rows.Count) rows -> $OutputPath" -ForegroundColor Yellow
    return $rows
}

Export-CustomConnectorInventory
```

---

## 4. Microsoft Service Trust / Message Center Vendor Signals

```powershell
# Required Graph scopes: ServiceMessage.Read.All
Connect-MgGraph -Scopes 'ServiceMessage.Read.All' -NoWelcome

function Export-PowerPlatformMessageCenter {
    [CmdletBinding()]
    param(
        [int]$DaysBack = 30,
        [string]$OutputPath = ".\evidence\2.7\message-center-power-platform.csv"
    )
    New-Item -ItemType Directory -Path (Split-Path $OutputPath) -Force | Out-Null

    $cutoff = (Get-Date).AddDays(-$DaysBack)
    $msgs = Get-MgServiceAnnouncementMessage -All |
            Where-Object {
                ($_.Services -contains 'Power Platform' -or
                 $_.Services -contains 'Microsoft Copilot Studio' -or
                 $_.Services -contains 'Microsoft 365 Copilot') -and
                $_.LastModifiedDateTime -gt $cutoff
            }

    $msgs | Select-Object Id, Title, Severity, ActionRequiredByDateTime,
                          LastModifiedDateTime, @{n='Services';e={$_.Services -join ';'}} |
        Export-Csv -Path $OutputPath -NoTypeInformation -Encoding UTF8

    Write-Host "Captured $($msgs.Count) Message Center entries -> $OutputPath" -ForegroundColor Green
}

Export-PowerPlatformMessageCenter -DaysBack 30
```

These announcements are a **vendor change signal** for Microsoft as a first-party AI/connector provider. Map material entries (model deprecation, connector retirement, security-affecting changes) into the Tier T1/T5 reassessment workflow.

---

## 5. Combined Vendor Risk Snapshot

```powershell
function Invoke-Control27Snapshot {
    [CmdletBinding()]
    param(
        [string]$OutputRoot = ".\evidence\2.7\snapshot-$((Get-Date -Format 'yyyyMMdd-HHmmss'))"
    )
    New-Item -ItemType Directory -Path $OutputRoot -Force | Out-Null

    Export-PpConnectorInventory     -OutputPath "$OutputRoot\connector-inventory.csv"     | Out-Null
    Export-DlpPolicyPosture         -OutputPath "$OutputRoot\dlp-policy-posture.csv"      | Out-Null
    Export-CustomConnectorInventory -OutputPath "$OutputRoot\custom-connectors.csv"       | Out-Null
    Export-PowerPlatformMessageCenter -DaysBack 30 -OutputPath "$OutputRoot\msg-center.csv" | Out-Null

    # Emit a manifest with SHA-256 per file for evidence integrity
    Get-ChildItem $OutputRoot -File | ForEach-Object {
        [pscustomobject]@{
            File   = $_.Name
            Bytes  = $_.Length
            Sha256 = (Get-FileHash $_.FullName -Algorithm SHA256).Hash
        }
    } | Export-Csv "$OutputRoot\manifest.csv" -NoTypeInformation -Encoding UTF8

    Write-Host "Snapshot complete: $OutputRoot" -ForegroundColor Cyan
}

Invoke-Control27Snapshot
```

---

## Operational Notes

- **No mutations.** Every cmdlet above is read-only. Never wrap these in scripts that change DLP classification without `-WhatIf`/`-Confirm`, change tickets, and a documented rollback.
- **Service principal usage.** For unattended collection, follow the FSI baseline pattern (certificate-based auth, just-in-time vault retrieval, scoped admin role). Avoid storing client secrets on disk.
- **Sovereign clouds.** For GCC, GCC High, or DoD tenants, pass the appropriate `-Endpoint` to `Add-PowerAppsAccount` and the equivalent national-cloud endpoint to `Connect-MgGraph`.
- **Evidence handling.** Snapshot output may include connector names that are themselves sensitive (e.g., internal API surface). Store in a least-privilege evidence repository governed by Purview retention.

---

## Related Playbooks

- [Portal Walkthrough](portal-walkthrough.md)
- [Verification & Testing](verification-testing.md)
- [Troubleshooting](troubleshooting.md)

---

*Updated: April 2026 | Version: v1.4.0 | UI Verification Status: Current*
