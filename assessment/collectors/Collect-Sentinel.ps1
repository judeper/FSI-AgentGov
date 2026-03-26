<#
.SYNOPSIS
    Collects Microsoft Sentinel / Log Analytics configuration data for FSI Agent Governance assessment.

.DESCRIPTION
    Validates Sentinel workspace existence, enumerates data connectors (Office 365,
    Microsoft Cloud App Security), and runs a KQL audit query to confirm Copilot
    interaction audit records exist in the last 7 days.

    Outputs a structured JSON file (sentinel.json) consumed by the assessment engine.

    Pattern references:
      - Set-InactivityTimeout.ps1 — Azure token acquisition (Get-AzAccessToken)
      - Invoke-SharingAudit.ps1 — REST API invocation patterns
      - Invoke-HardeningBaselineCheck.ps1 — multi-control baseline check structure

.PARAMETER TenantId
    Mandatory. Azure AD tenant ID.

.PARAMETER AuthMode
    Mandatory. Authentication mode: Interactive or ServicePrincipal.

.PARAMETER ClientId
    Optional. Application (client) ID for service principal authentication.

.PARAMETER ClientSecret
    Optional. Client secret as SecureString for service principal authentication.

.PARAMETER OutputDir
    Mandatory. Root output directory. Collected JSON is written to $OutputDir\collected\sentinel.json.

.PARAMETER SubscriptionId
    Mandatory. Azure subscription ID containing the Sentinel workspace.

.PARAMETER ResourceGroup
    Mandatory. Resource group name containing the Sentinel workspace.

.PARAMETER WorkspaceName
    Mandatory. Log Analytics workspace name.

.OUTPUTS
    sentinel.json — JSON file with workspace details, data connectors, and KQL audit check results.

.NOTES
    Part of the FSI Agent Governance Assessment Engine — Sentinel Collector.
    Requires Az.OperationalInsights module.
    Exit codes: 0 = success, 1 = partial failure (some sections null), 2 = total failure.
    Version: 1.0.0
#>

#Requires -Version 7.0

[CmdletBinding()]
param(
    [Parameter(Mandatory)]
    [ValidateNotNullOrEmpty()]
    [string]$TenantId,

    [Parameter(Mandatory)]
    [ValidateSet('Interactive', 'ServicePrincipal')]
    [string]$AuthMode,

    [Parameter()]
    [string]$ClientId,

    [Parameter()]
    [securestring]$ClientSecret,

    [Parameter(Mandatory)]
    [ValidateNotNullOrEmpty()]
    [string]$OutputDir,

    [Parameter(Mandatory)]
    [ValidateNotNullOrEmpty()]
    [string]$SubscriptionId,

    [Parameter(Mandatory)]
    [ValidateNotNullOrEmpty()]
    [string]$ResourceGroup,

    [Parameter(Mandatory)]
    [ValidateNotNullOrEmpty()]
    [string]$WorkspaceName
)

$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest

# ─── Initialise ──────────────────────────────────────────────────────
$warnings = [System.Collections.Generic.List[string]]::new()
$collectedDir = Join-Path $OutputDir 'collected'
if (-not (Test-Path $collectedDir)) {
    New-Item -ItemType Directory -Path $collectedDir -Force | Out-Null
}
$outputFile = Join-Path $collectedDir 'sentinel.json'

# ─── Module Import ───────────────────────────────────────────────────
Import-Module Az.OperationalInsights -ErrorAction Stop
Write-Verbose "Loaded Az.OperationalInsights module."

# ─── Authentication ──────────────────────────────────────────────────
# Pattern: Set-InactivityTimeout.ps1 — Connect-AzAccount for token acquisition
Write-Verbose "Authenticating to Azure in $AuthMode mode..."

if ($AuthMode -eq 'Interactive') {
    Connect-AzAccount -TenantId $TenantId -SubscriptionId $SubscriptionId -ErrorAction Stop
}
else {
    if (-not $ClientId -or -not $ClientSecret) {
        throw "ServicePrincipal auth requires -ClientId and -ClientSecret parameters."
    }
    $credential = [System.Management.Automation.PSCredential]::new($ClientId, $ClientSecret)
    Connect-AzAccount -TenantId $TenantId -SubscriptionId $SubscriptionId `
        -ServicePrincipal -Credential $credential -ErrorAction Stop
}

# Set active subscription context
Set-AzContext -SubscriptionId $SubscriptionId -ErrorAction Stop | Out-Null
Write-Verbose "Azure authentication successful. Subscription: $SubscriptionId"

# ═══════════════════════════════════════════════════════════════════════
# Section 1: Workspace Existence and Configuration
# Supports: Control 3.1 (Audit Logging), SIEM workspace validation
# ═══════════════════════════════════════════════════════════════════════
$workspaceInfo = $null
try {
    Write-Verbose "Section 1: Validating Sentinel workspace existence..."
    $workspace = Get-AzOperationalInsightsWorkspace `
        -ResourceGroupName $ResourceGroup `
        -Name $WorkspaceName `
        -ErrorAction Stop

    $workspaceInfo = [PSCustomObject]@{
        WorkspaceId       = $workspace.CustomerId
        ResourceId        = $workspace.ResourceId
        Name              = $workspace.Name
        Location          = $workspace.Location
        ProvisioningState = $workspace.ProvisioningState
        Sku               = $workspace.Sku
        RetentionInDays   = $workspace.RetentionInDays
        WorkspaceCapping  = $workspace.WorkspaceCapping
    }
    Write-Verbose "  Workspace '$WorkspaceName' found. State: $($workspace.ProvisioningState), SKU: $($workspace.Sku)"
}
catch {
    $warnings.Add("Section 1 (Workspace) failed: $($_.Exception.Message)")
    Write-Warning $warnings[-1]
}

# ═══════════════════════════════════════════════════════════════════════
# Section 2: Data Connectors
# Supports: Control 3.1 (Audit Ingestion) — verify Office 365 and MCAS connectors
# Pattern: Invoke-HardeningBaselineCheck.ps1 — baseline item enumeration
# ═══════════════════════════════════════════════════════════════════════
$dataConnectors = $null
try {
    Write-Verbose "Section 2: Enumerating Sentinel data connectors..."

    # Use Azure REST API for Sentinel data connectors (more reliable than Get-AzOperationalInsightsDataSource
    # for Sentinel-specific connectors like Office365 and MCAS)
    $connectorApiUri = "https://management.azure.com/subscriptions/$SubscriptionId" +
        "/resourceGroups/$ResourceGroup" +
        "/providers/Microsoft.OperationalInsights/workspaces/$WorkspaceName" +
        "/providers/Microsoft.SecurityInsights/dataConnectors?api-version=2023-02-01"

    # Acquire ARM token
    # Pattern: Set-InactivityTimeout.ps1 — Get-AzAccessToken for resource-specific tokens
    $armToken = $null
    try {
        $armTokenResult = Get-AzAccessToken -ResourceUrl "https://management.azure.com" -ErrorAction Stop
        if ($armTokenResult.Token -is [securestring]) {
            $armToken = $armTokenResult.Token | ConvertFrom-SecureString -AsPlainText
        }
        else {
            $armToken = $armTokenResult.Token
        }
    }
    catch {
        throw "Failed to acquire ARM token: $($_.Exception.Message)"
    }

    $headers = @{
        Authorization  = "Bearer $armToken"
        'Content-Type' = 'application/json'
    }
    $connectorResponse = Invoke-RestMethod -Uri $connectorApiUri -Method GET -Headers $headers -ErrorAction Stop

    # Extract connectors of interest
    $targetKinds = @('Office365', 'MicrosoftCloudAppSecurity', 'AzureActiveDirectory', 'MicrosoftThreatProtection')

    $dataConnectors = [PSCustomObject]@{
        TotalConnectors     = if ($connectorResponse.value) { $connectorResponse.value.Count } else { 0 }
        ConnectorSummary    = if ($connectorResponse.value) {
            $connectorResponse.value | ForEach-Object {
                [PSCustomObject]@{
                    Id        = $_.id
                    Name      = $_.name
                    Kind      = $_.kind
                    Etag      = $_.etag
                }
            }
        }
        else { @() }
        Office365Enabled    = $false
        McasEnabled         = $false
    }

    if ($connectorResponse.value) {
        $dataConnectors.Office365Enabled = ($connectorResponse.value | Where-Object { $_.kind -eq 'Office365' }).Count -gt 0
        $dataConnectors.McasEnabled = ($connectorResponse.value | Where-Object { $_.kind -eq 'MicrosoftCloudAppSecurity' }).Count -gt 0

        if (-not $dataConnectors.Office365Enabled) {
            $warnings.Add("Section 2: Office365 data connector is NOT enabled in workspace '$WorkspaceName'.")
            Write-Warning $warnings[-1]
        }
        if (-not $dataConnectors.McasEnabled) {
            $warnings.Add("Section 2: MicrosoftCloudAppSecurity data connector is NOT enabled in workspace '$WorkspaceName'.")
            Write-Warning $warnings[-1]
        }
    }
    Write-Verbose "  Data connectors enumerated. Office365=$($dataConnectors.Office365Enabled), MCAS=$($dataConnectors.McasEnabled)"
}
catch {
    $warnings.Add("Section 2 (Data Connectors) failed: $($_.Exception.Message)")
    Write-Warning $warnings[-1]
}

# ═══════════════════════════════════════════════════════════════════════
# Section 3: KQL Audit Check — Copilot Interaction Records
# Supports: Control 3.1 (Audit Evidence) — confirm agent audit logs exist
# ═══════════════════════════════════════════════════════════════════════
$kqlAuditCheck = $null
try {
    Write-Verbose "Section 3: Running KQL audit check for CopilotInteraction records..."

    if ($workspaceInfo) {
        $kqlQuery = 'AuditLogs | where OperationName contains "CopilotInteraction" | where TimeGenerated > ago(7d) | count'

        $queryResult = Invoke-AzOperationalInsightsQuery `
            -WorkspaceId $workspaceInfo.WorkspaceId `
            -Query $kqlQuery `
            -ErrorAction Stop

        $recordCount = 0
        if ($queryResult.Results) {
            # The count query returns a single row with a Count column
            $countValue = $queryResult.Results | Select-Object -First 1
            if ($countValue.Count) {
                $recordCount = [int]$countValue.Count
            }
            elseif ($countValue.'Count') {
                $recordCount = [int]$countValue.'Count'
            }
        }

        $kqlAuditCheck = [PSCustomObject]@{
            Query           = $kqlQuery
            RecordCount     = $recordCount
            HasRecords      = ($recordCount -gt 0)
            QueryTimeRange  = '7 days'
            ExecutedAt      = (Get-Date -Format 'o')
        }

        if ($recordCount -eq 0) {
            $warnings.Add("Section 3: No CopilotInteraction audit records found in the last 7 days. Verify audit ingestion pipeline.")
            Write-Warning $warnings[-1]
        }
        else {
            Write-Verbose "  Found $recordCount CopilotInteraction record(s) in the last 7 days."
        }
    }
    else {
        $warnings.Add("Section 3 (KQL Audit): Skipped — workspace info unavailable.")
        Write-Warning $warnings[-1]
    }
}
catch {
    $warnings.Add("Section 3 (KQL Audit) failed: $($_.Exception.Message)")
    Write-Warning $warnings[-1]
}

# ═══════════════════════════════════════════════════════════════════════
# Build Output
# ═══════════════════════════════════════════════════════════════════════
$result = [ordered]@{
    workspace       = $workspaceInfo
    dataConnectors  = $dataConnectors
    kqlAuditCheck   = $kqlAuditCheck
    _metadata       = [ordered]@{
        collector       = 'Collect-Sentinel'
        timestamp       = (Get-Date -Format 'o')
        tenant_id       = $TenantId
        subscription_id = $SubscriptionId
        resource_group  = $ResourceGroup
        workspace_name  = $WorkspaceName
        warnings        = @($warnings)
    }
}

$json = $result | ConvertTo-Json -Depth 10
$json | Out-File -FilePath $outputFile -Encoding utf8
Write-Verbose "Output written to $outputFile"

# ─── Exit Code ───────────────────────────────────────────────────────
$sectionValues = @($workspaceInfo, $dataConnectors, $kqlAuditCheck)
$nullSections = @($sectionValues | Where-Object { $null -eq $_ })

if ($nullSections.Count -eq $sectionValues.Count) {
    Write-Error "All sections failed to collect data. See warnings for details."
    exit 2
}
elseif ($nullSections.Count -gt 0) {
    Write-Warning "Partial collection: $($nullSections.Count)/$($sectionValues.Count) sections returned null."
    exit 1
}
else {
    Write-Verbose "All sections collected successfully."
    exit 0
}
