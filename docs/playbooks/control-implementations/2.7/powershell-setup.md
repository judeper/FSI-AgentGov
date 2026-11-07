# Control 2.7: Vendor and Third-Party Risk Management — PowerShell Setup

> Companion to [Control 2.7](../../../controls/pillar-2-management/2.7-vendor-and-third-party-risk-management.md). Provides read-mostly PowerShell automation for connector inventory, DLP analysis, custom-connector enumeration, and vendor evidence collection.

!!! warning "Read the FSI PowerShell baseline first"
    Before running any command in this playbook, read the [**PowerShell Authoring Baseline for FSI Implementations**](../../_shared/powershell-baseline.md). It is the canonical source for module version pinning, mutation safety (`-WhatIf` / `SupportsShouldProcess`), Dataverse compatibility, and SHA-256 evidence emission. Snippets below show abbreviated patterns; the baseline is authoritative.

!!! info "Read-mostly by design"
    These scripts read tenant state and emit evidence files. They **do not** mutate DLP policies, connector classifications, or Microsoft Copilot Studio settings. Use the portal walkthrough or your IaC pipeline for change-controlled mutations. All emitted files should be hashed (SHA-256) and stored in your audit-evidence repository.

---

**Last Verified:** 2026-11-06

**Verification scope:** Documentation-only review of the read commands and evidence boundaries; no tenant/API execution or screenshots tested. Corrected 2026-11-07 for documented `Get-AdminPowerAppConnector` and `Get-DlpPolicy` coverage limits and the `Get-DlpPolicy` list `.Value` envelope, using Microsoft documentation and static review of module 2.0.198 only; the scripts remain unexecuted and the date above is not renewed for the rest of this page.

## Prerequisites

```powershell
# Pin module versions per the FSI baseline
Install-Module -Name Microsoft.PowerApps.Administration.PowerShell -RequiredVersion 2.0.198 -Force
Install-Module -Name Microsoft.Graph.Devices.ServiceAnnouncement -RequiredVersion '<CAB-approved-version>' -Scope CurrentUser

# Run Power Apps commands in Windows PowerShell 5.1 per the shared baseline.
$ErrorActionPreference = 'Stop'
Add-PowerAppsAccount -Endpoint prod

# Verify actual environment visibility under the authorized administrative role.
Get-AdminPowerAppEnvironment | Select-Object DisplayName, EnvironmentName, EnvironmentType | Format-Table
```

The existing Power Apps version pin is retained, not newly certified against a tenant. Substitute the approved Graph version before installation. [Get-MgServiceAnnouncementMessage](https://learn.microsoft.com/en-us/powershell/module/microsoft.graph.devices.serviceannouncement/get-mgserviceannouncementmessage?view=graph-powershell-1.0) is in **Microsoft.Graph.Devices.ServiceAnnouncement**, not DeviceManagement.Enrollment or Reports.

---

## 1. Custom Connector Evidence Across Authorized Environments

[Get-AdminPowerAppConnector](https://learn.microsoft.com/en-us/powershell/module/microsoft.powerapps.administration.powershell/get-adminpowerappconnector?view=pa-ps-latest) returns **custom connectors**, not the complete prebuilt/certified catalog or a complete usage inventory. Preserve raw output instead of inferring publisher, connector type, owner, or API URLs from undocumented projected properties. Reconcile it with the portal [resource inventory](portal-walkthrough.md#part-1-build-the-connector-inventory-ppac), approved vendor records, and agent tools. Confirm every required environment is visible; a successful empty response alone does not establish completeness.

!!! warning "Known limitation: solution-packaged custom connectors are not returned"
    Microsoft documents that `Get-AdminPowerAppConnector` **doesn't list custom connectors that are in a solution** ([Power Platform PowerShell support](https://learn.microsoft.com/en-us/power-platform/admin/powerapps-powershell), "Display all custom connectors in the tenant"). Solution-based ALM is a normal delivery path, so this export is a **partial** list of the custom connectors visible to the cmdlet, not a complete custom-connector inventory. An empty `CustomConnectors` array, a zero count or a connector absent from the JSON does **not** show that no custom connector exists. Before relying on the export, separately reconcile it against the contents of the relevant solutions and the portal resource inventory under an authorized role, and record any connector found only there. This limitation was confirmed from Microsoft documentation and the `Microsoft.PowerApps.Administration.PowerShell` 2.0.198 reference text only; it was not reproduced in a tenant.

```powershell
function Export-CustomConnectorInventory {
    [CmdletBinding()]
    param(
        [string]$OutputPath = ".\evidence\2.7\custom-connectors.json"
    )
    $ErrorActionPreference = 'Stop'
    New-Item -ItemType Directory -Path (Split-Path $OutputPath) -Force | Out-Null

    $envs = @(Get-AdminPowerAppEnvironment -ErrorAction Stop)
    $rows = @(foreach ($env in $envs) {
        Write-Verbose "Scanning environment $($env.DisplayName)"
        $connectors = @(Get-AdminPowerAppConnector -EnvironmentName $env.EnvironmentName -ErrorAction Stop)
        [pscustomobject]@{
            EnvironmentDisplayName = $env.DisplayName
            EnvironmentId          = $env.EnvironmentName
            ReturnedCustomConnectorCount = $connectors.Count
            CustomConnectors       = $connectors
            CompletenessLimitation = 'Excludes solution-packaged custom connectors (documented Get-AdminPowerAppConnector limitation); not a complete inventory. Reconcile against solution contents and portal inventory.'
            CollectedAt            = (Get-Date).ToUniversalTime().ToString('o')
        }
    })

    ConvertTo-Json -InputObject $rows -Depth 100 | Set-Content -Path $OutputPath -Encoding UTF8
    $hash = (Get-FileHash -Path $OutputPath -Algorithm SHA256).Hash
    Write-Host "Inventory written: $OutputPath" -ForegroundColor Green
    Write-Host "SHA-256: $hash"
    return [pscustomobject]@{ Path = $OutputPath; Sha256 = $hash; EnvironmentCount = $rows.Count }
}

Export-CustomConnectorInventory -Verbose
```

---

## 2. DLP Policy Posture Report

The [custom connector policy reference](https://learn.microsoft.com/en-us/power-platform/admin/dlp-custom-connector-parity) maps **Confidential = Business** and **General = Non-business**. Host URL rules are obtained separately with **Get-PowerAppPolicyUrlPatterns**, using the tenant ID and policy GUID; they are not an assumed embedded field in **Get-DlpPolicy**. Retain the full policy and ordered pattern payloads for manual scope/classification reconciliation; counts alone are not effective-policy evidence.

!!! warning "Known limitations of Get-DlpPolicy output, and a response envelope"
    Microsoft documents two known issues for `Get-DlpPolicy` ([Power Platform PowerShell support](https://learn.microsoft.com/en-us/power-platform/admin/powerapps-powershell), "Retrieve a list of data policy objects"): (1) **connector display names** are those from policy creation or the last time the connector was moved within the policy, so later renames are not reflected; and (2) **connectors that are in the policy's default group and were never moved are not returned**. The default group is whatever the policy configures; it is not necessarily Non-business. Per-group counts, and any connector list built from this output, can therefore **understate the default group** and show stale names. Treat the CSV as a summary of the connectors the cmdlet returned, not a complete or effective classification of every connector, and reconcile it with the policy's portal view. Microsoft's documented workaround moves a connector out of and back into a group; that **mutates policy**, is not part of this read-only collector, and should not be used as an inventory tactic without a separate change ticket. These limits come from Microsoft documentation and have not been reproduced in a tenant.

    Unlike the single-policy form (`-PolicyName`), the list form returned by `Get-DlpPolicy` in `Microsoft.PowerApps.Administration.PowerShell` 2.0.198 is a response object whose `Value` property holds the policy items; the module's REST helper returns that envelope without unwrapping it, and Microsoft's administration sample enumerates `.Value`. The example below therefore validates and enumerates `.Value` and fails closed when it is absent, instead of reading `name` or `connectorGroups` from the envelope. `Get-AdminDlpPolicy` is a different cmdlet with a different endpoint and output projection and is not a substitute.

    **Not executed against a tenant.** Static review supports `.Value`, `name`, `displayName` and `connectorGroups[].classification` / `.connectors` on policy items. It does **not** establish that `environmentType`, `createdTime` or `lastModifiedTime` are present and populated for every list item (the timestamp support found is for policy-creation responses), so blank values in those CSV columns mean "not returned", not "unchanged". Treat the script as unvalidated until run by an authorized owner against the approved module version, including zero, one, multiple and paged policies. `Get-PowerAppPolicyUrlPatterns` parameters and the documented rule-object shape were checked, not its endpoint behavior or applicability to every policy.

```powershell
function Export-DlpPolicyPosture {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory)] [string]$TenantId,
        [string]$OutputPath = ".\evidence\2.7\dlp-policy-posture.csv"
    )
    $ErrorActionPreference = 'Stop'
    New-Item -ItemType Directory -Path (Split-Path $OutputPath) -Force | Out-Null

    $response = Get-DlpPolicy -ErrorAction Stop
    ConvertTo-Json -InputObject $response -Depth 100 |
        Set-Content "$OutputPath.policies.json" -Encoding UTF8
    if ($null -eq $response -or -not $response.PSObject.Properties['Value'] -or $null -eq $response.Value) {
        throw 'Get-DlpPolicy response has no Value collection; reconcile the raw response before continuing.'
    }
    $policies = @($response.Value)
    if (-not $policies.Count) {
        Write-Warning 'Value is empty; this is not proof that no policies exist. Reconcile with the portal under an authorized role.'
    }
    $patterns = @(foreach ($p in $policies) {
        if (-not $p.name) { throw 'Policy GUID missing; reconcile raw policy output before continuing.' }
        if (-not $p.PSObject.Properties['connectorGroups']) { throw "Policy $($p.name) has no connectorGroups; do not report zero counts." }
        [pscustomobject]@{
            PolicyId = $p.name
            UrlPatterns = Get-PowerAppPolicyUrlPatterns -TenantId $TenantId -PolicyName $p.name -ErrorAction Stop
        }
    })
    ConvertTo-Json -InputObject $patterns -Depth 100 |
        Set-Content "$OutputPath.url-patterns.json" -Encoding UTF8
    $rows = @(foreach ($p in $policies) {
        $business    = $p.connectorGroups | Where-Object { $_.classification -eq 'Confidential' }
        $nonBusiness = $p.connectorGroups | Where-Object { $_.classification -eq 'General' }
        $blocked     = $p.connectorGroups | Where-Object { $_.classification -eq 'Blocked' }

        [pscustomobject]@{
            PolicyName            = $p.displayName
            PolicyId              = $p.name
            EnvironmentType       = $p.environmentType
            ReturnedBusinessConnectors    = ($business.connectors | Measure-Object).Count
            ReturnedNonBusinessConnectors = ($nonBusiness.connectors | Measure-Object).Count
            ReturnedBlockedConnectors     = ($blocked.connectors | Measure-Object).Count
            CreatedTime           = $p.createdTime
            LastModifiedTime      = $p.lastModifiedTime
            CollectedAt           = (Get-Date).ToUniversalTime().ToString('o')
        }
    })

    if ($rows.Count) {
        $rows | Export-Csv -Path $OutputPath -NoTypeInformation -Encoding UTF8
    } else {
        '"PolicyName","PolicyId","EnvironmentType","ReturnedBusinessConnectors","ReturnedNonBusinessConnectors","ReturnedBlockedConnectors","CreatedTime","LastModifiedTime","CollectedAt"' |
            Set-Content -Path $OutputPath -Encoding UTF8
    }
    foreach ($file in @($OutputPath, "$OutputPath.policies.json", "$OutputPath.url-patterns.json")) {
        $hash = (Get-FileHash $file -Algorithm SHA256).Hash
        Write-Host "DLP evidence: $file  SHA-256: $hash" -ForegroundColor Green
    }
    return $rows
}

Export-DlpPolicyPosture -TenantId '<tenant-id>'
```

---

## 3. Inventory Reconciliation

Use Section 1's custom connector evidence without a publisher-based filter: a non-Microsoft publisher does not identify a custom connector, and custom connectors can reach Microsoft or third-party endpoints. Section 1's export omits solution-packaged custom connectors, so reconcile it with solution contents and the portal resource inventory, and keep any connector found only there in the register with its source. Section 2's counts omit never-moved default-group connectors and can show stale connector names, so classify from the policy's portal view rather than the CSV alone. Neither export is a complete inventory, and absence from either is not evidence that a connector does not exist or is unclassified. Record maker permissions, owner/shared visibility, resource usage and endpoint reviews. Tenant Host URL patterns do not constrain dynamically changed hosts after policy evaluation. DLP governs **usage**, not the right to create a custom connector; the [Environment Maker role](https://learn.microsoft.com/en-us/power-platform/admin/environments-overview#environment-roles) includes creation rights. Sharing limits are not a custom-connector creation switch.

Retrieve classic connector action/endpoint configurations separately where used ([connector configuration commands](https://learn.microsoft.com/en-us/power-platform/admin/connector-endpoint-filtering)). ACP settings and agent-level MCP tool selections require their own evidence; this DLP report does not collect them.

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
    $ErrorActionPreference = 'Stop'
    New-Item -ItemType Directory -Path (Split-Path $OutputPath) -Force | Out-Null

    $cutoff = (Get-Date).AddDays(-$DaysBack)
    $msgs = @(Get-MgServiceAnnouncementMessage -All -ErrorAction Stop |
            Where-Object {
                ($_.Services -contains 'Power Platform' -or
                 $_.Services -contains 'Microsoft Copilot Studio' -or
                 $_.Services -contains 'Microsoft 365 Copilot') -and
                $_.LastModifiedDateTime -gt $cutoff
            })

    ConvertTo-Json -InputObject $msgs -Depth 100 |
        Set-Content "$OutputPath.json" -Encoding UTF8

    $msgs | Select-Object Id, Title, Severity, ActionRequiredByDateTime,
                          LastModifiedDateTime, @{n='Services';e={$_.Services -join ';'}} |
        Export-Csv -Path $OutputPath -NoTypeInformation -Encoding UTF8

    Write-Host "Captured $($msgs.Count) Message Center entries -> $OutputPath" -ForegroundColor Green
}

Export-PowerPlatformMessageCenter -DaysBack 30
```

These announcements are a **vendor change signal** for Microsoft as a first-party AI/connector provider. Map material entries (model deprecation, connector retirement, security-affecting changes) into the Tier T1/T5 reassessment workflow.

The service-name filter is a convenience, not complete advisory coverage. Review unfiltered Message Center posts and current release guidance; an empty match is not proof of no vendor changes. STP attestations are downloaded separately, not supplied by this cmdlet. A zero-message CSV is not relied upon: retain the raw JSON array and query period.

---

## 5. Combined Vendor Risk Snapshot

```powershell
function Invoke-Control27Snapshot {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory)] [string]$TenantId,
        [string]$OutputRoot = ".\evidence\2.7\snapshot-$((Get-Date -Format 'yyyyMMdd-HHmmss'))"
    )
    $ErrorActionPreference = 'Stop'
    if (Test-Path -LiteralPath $OutputRoot) {
        throw 'Choose a new snapshot folder; refusing to mix stale and current evidence.'
    }
    New-Item -ItemType Directory -Path $OutputRoot -Force | Out-Null

    Export-DlpPolicyPosture -TenantId $TenantId -OutputPath "$OutputRoot\dlp-policy-posture.csv" | Out-Null
    Export-CustomConnectorInventory -OutputPath "$OutputRoot\custom-connectors.json"       | Out-Null
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

Invoke-Control27Snapshot -TenantId '<tenant-id>'
```

---

## Operational Notes

- **Tenant collection is read-only.** Installation/authentication and local file writes have their own effects; the collectors do not change tenant DLP, connector or agent configuration. Never add DLP mutations without `-WhatIf`/`-Confirm`, change tickets, and documented rollback.
- **Service principal usage.** For unattended collection, follow the FSI baseline pattern (certificate-based auth, just-in-time vault retrieval, scoped admin role). Avoid storing client secrets on disk.
- **Evidence handling.** Snapshot output may include connector names that are themselves sensitive (e.g., internal API surface). Store in a least-privilege evidence repository governed by Purview retention.
- **Coverage limits travel with the evidence.** Keep the solution-packaged custom connector and `Get-DlpPolicy` default-group/stale-name limitations in the evidence cover note; a manifest that hashes the files does not make them complete.

---

## Related Playbooks

- [Portal Walkthrough](portal-walkthrough.md)
- [Verification & Testing](verification-testing.md)
- [Troubleshooting](troubleshooting.md)

---

*Updated: November 2026 | Version: v1.6.2 | UI Verification Status: Needs Review (documentation-only; no tenant execution)*
