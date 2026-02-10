# Deployment Guide

**Parent:** [Deny Event Correlation Report](index.md)

---

## Overview

This guide provides end-to-end deployment instructions for the deny event correlation solution across your environment.

---

## Deployment Architecture

```mermaid
flowchart TB
    subgraph Prerequisites
        M365[M365 E5 License]
        PBI[Power BI Pro/Premium]
        AZURE[Azure Subscription]
    end

    subgraph Phase1[Phase 1: Infrastructure]
        STORAGE[Azure Blob Storage]
        APPINS[Application Insights]
        KEYVAULT[Azure Key Vault]
    end

    subgraph Phase2[Phase 2: Extraction]
        RUNBOOK[Azure Automation Runbook]
        SCHEDULE[Daily Schedule]
    end

    subgraph Phase3[Phase 3: Reporting]
        PBIWS[Power BI Workspace]
        DATASET[Dataset + Refresh]
        REPORT[Dashboard]
    end

    Prerequisites --> Phase1
    Phase1 --> Phase2
    Phase2 --> Phase3
```

---

## Prerequisites Checklist

### Licensing

- [ ] Microsoft 365 E5 or E5 Compliance (for Audit Premium)
- [ ] Power BI Pro (per-user) or Power BI Premium (capacity)
- [ ] Azure subscription (for storage and automation)

### Permissions

| Task | Required Role |
|------|---------------|
| Search-UnifiedAuditLog | Purview Audit Reader or Purview Compliance Admin |
| Application Insights API | Reader role on App Insights resource |
| Azure Automation | Automation Contributor |
| Power BI publish | Workspace Contributor or Admin |

### Service Accounts

Create a dedicated Entra ID App Registration for automated extraction:

1. Create App Registration in **Entra ID** > **App registrations**
2. Add API permission: **Office 365 Exchange Online** > **Application** > `Exchange.ManageAsApp`
3. Grant admin consent (tenant admin)
4. Assign Entra role: **Purview Audit Reader**
5. Create a client secret or upload a certificate
6. Store credentials in Azure Key Vault

---

## Phase 1: Infrastructure Setup

### Step 1.1: Create Azure Storage Account

```powershell
# Create resource group
az group create --name rg-fsi-governance --location eastus

# Create storage account
az storage account create `
    --name stfsigovernance `
    --resource-group rg-fsi-governance `
    --location eastus `
    --sku Standard_LRS `
    --kind StorageV2

# Create container for deny events
az storage container create `
    --name deny-events `
    --account-name stfsigovernance

# Enable immutable storage (for SEC 17a-4)
az storage container immutability-policy create `
    --resource-group rg-fsi-governance `
    --account-name stfsigovernance `
    --container-name deny-events `
    --period 2555  # 7 years in days
```

### Step 1.2: Create Azure Key Vault

```powershell
# Create Key Vault
az keyvault create `
    --name kv-fsi-governance `
    --resource-group rg-fsi-governance `
    --location eastus

# Store Exchange Online App Registration client secret
az keyvault secret set `
    --vault-name kv-fsi-governance `
    --name "sp-exchangeonline" `
    --value "<app-registration-client-secret>"

# Store App Insights service principal client secret
az keyvault secret set `
    --vault-name kv-fsi-governance `
    --name "sp-appinsights" `
    --value "<appinsights-sp-client-secret>"
```

!!! warning "No Hardcoded Credentials"
    Never store user passwords or API keys directly in scripts. All credentials must be retrieved from Azure Key Vault at runtime using `Get-AzKeyVaultSecret`. The `ConvertTo-SecureString -AsPlainText -Force` pattern is prohibited — use `PSCredential` constructed from Key Vault `SecretValue` instead.

### Key Vault Prerequisites

The following secrets must be configured in Azure Key Vault before running extraction scripts:

| Secret Name | Purpose | When Required |
|-------------|---------|---------------|
| `sp-exchangeonline` | Exchange Online App Registration client secret | When not using certificate auth |
| `sp-appinsights` | Application Insights service principal client secret | Always (for RAI telemetry) |

**Required RBAC roles on the Key Vault:**

| Role | Assigned To | Purpose |
|------|-------------|---------|
| Key Vault Secrets User | Automation service principal | Read secrets at runtime |
| Key Vault Administrator | Governance admin | Manage secret lifecycle |

### Step 1.3: Configure Application Insights

For each Zone 2/3 Copilot Studio agent:

1. Open Copilot Studio portal
2. Select agent > **Settings** > **Generative AI**
3. Enable **Advanced settings**
4. Enter Application Insights connection string
5. Save and Publish

---

## Phase 2: Automation Setup

### Step 2.1: Create Azure Automation Account

```powershell
# Create Automation Account
az automation account create `
    --name aa-fsi-governance `
    --resource-group rg-fsi-governance `
    --location eastus

# Import required modules
$modules = @(
    "ExchangeOnlineManagement",
    "Az.Storage",
    "Az.KeyVault",
    "Az.Accounts"
)

foreach ($module in $modules) {
    az automation module create `
        --automation-account-name aa-fsi-governance `
        --resource-group rg-fsi-governance `
        --name $module `
        --content-link "https://www.powershellgallery.com/api/v2/package/$module"
}
```

### Step 2.2: Deploy DECClient Module

Upload the `DECClient.psm1` shared module to the Automation Account:

1. In Azure portal, navigate to **Automation Account** > **Modules**
2. Select **Add a module** > **Browse from gallery** or upload custom
3. Upload `DECClient.psm1` from the solution's `scripts/private/` directory
4. Verify module is imported successfully

### Step 2.3: Create Orchestration Runbook

Create runbook `Invoke-DailyDenyReport`:

```powershell
#Requires -Version 7.0
#Requires -Modules @{ ModuleName="Az.Accounts"; ModuleVersion="3.0.0" }, @{ ModuleName="Az.KeyVault"; ModuleVersion="5.0.0" }, @{ ModuleName="ExchangeOnlineManagement"; ModuleVersion="3.0.0" }

<#
.SYNOPSIS
    Daily orchestration for deny event extraction.
.DESCRIPTION
    Runs all three extraction scripts using Entra ID service principal
    authentication via DECClient module. Credentials retrieved from Azure
    Key Vault — no hardcoded secrets. Uploads results to blob storage.
#>
[CmdletBinding()]
param(
    [Parameter(Mandatory)][ValidateNotNullOrEmpty()][string]$TenantId,
    [Parameter(Mandatory)][ValidateNotNullOrEmpty()][string]$ClientId,
    [Parameter(Mandatory)][ValidateNotNullOrEmpty()][string]$KeyVaultName,
    [Parameter(Mandatory)][ValidateNotNullOrEmpty()][string]$AppInsightsAppId,
    [ValidateNotNullOrEmpty()][string]$AppInsightsSecretName = 'sp-appinsights',
    [ValidateNotNullOrEmpty()][string]$CertificateThumbprint,
    [ValidateNotNullOrEmpty()][string]$StorageAccountName = "stfsigovernance",
    [ValidateNotNullOrEmpty()][string]$ContainerName = "deny-events",
    [ValidateRange(1, 90)][int]$DaysBack = 1,
    [ValidateSet('CSV','JSON')][string]$OutputFormat = 'CSV',
    [switch]$DryRun
)

$ErrorActionPreference = 'Stop'

# Import shared authentication module
Import-Module "$PSScriptRoot/private/DECClient.psm1" -Force

# Validate connections via DECClient
$connectParams = @{
    TenantId     = $TenantId
    ClientId     = $ClientId
    KeyVaultName = $KeyVaultName
    Services     = @('ExchangeOnline', 'AppInsights')
    DryRun       = $DryRun
}
if ($CertificateThumbprint) {
    $connectParams['CertificateThumbprint'] = $CertificateThumbprint
}
$connectResult = Connect-DECServices @connectParams

if ($DryRun) {
    Write-Output "[DryRun] Validation complete. Errors: $($connectResult.Errors.Count)"
    return
}

# Date range and output setup
$dateStamp = (Get-Date).AddDays(-$DaysBack).ToString("yyyy-MM-dd")
$ext = if ($OutputFormat -eq 'JSON') { 'json' } else { 'csv' }
$tempDir = Join-Path $env:TEMP "DenyReport-$dateStamp"
New-Item -ItemType Directory -Path $tempDir -Force | Out-Null

# Run extraction scripts
Write-Output "Extracting CopilotInteraction deny events..."
& .\Export-CopilotDenyEvents.ps1 -TenantId $TenantId -ClientId $ClientId `
    -KeyVaultName $KeyVaultName -DaysBack $DaysBack `
    -OutputPath "$tempDir\CopilotDenyEvents-$dateStamp.$ext" `
    -OutputFormat $OutputFormat

Write-Output "Extracting DLP events..."
& .\Export-DlpCopilotEvents.ps1 -TenantId $TenantId -ClientId $ClientId `
    -KeyVaultName $KeyVaultName -DaysBack $DaysBack `
    -OutputPath "$tempDir\DlpCopilotEvents-$dateStamp.$ext" `
    -OutputFormat $OutputFormat

Write-Output "Extracting RAI telemetry..."
& .\Export-RaiTelemetry.ps1 -AppInsightsAppId $AppInsightsAppId `
    -TenantId $TenantId -ClientId $ClientId `
    -KeyVaultName $KeyVaultName -SecretName $AppInsightsSecretName `
    -DaysBack $DaysBack `
    -OutputPath "$tempDir\RaiTelemetry-$dateStamp.$ext" `
    -OutputFormat $OutputFormat

# Upload to blob storage
$storageContext = New-AzStorageContext -StorageAccountName $StorageAccountName `
    -UseConnectedAccount

Get-ChildItem $tempDir -Filter "*.$ext" | ForEach-Object {
    Set-AzStorageBlobContent `
        -File $_.FullName `
        -Container $ContainerName `
        -Blob "$dateStamp/$($_.Name)" `
        -Context $storageContext `
        -Force
    Write-Output "Uploaded: $($_.Name)"
}

# Cleanup
Disconnect-ExchangeOnline -Confirm:$false -ErrorAction SilentlyContinue
Remove-Item $tempDir -Recurse -Force

Write-Output "Daily deny report complete for $dateStamp"
```

### Step 2.4: Schedule Runbook

```powershell
# Create daily schedule
az automation schedule create `
    --automation-account-name aa-fsi-governance `
    --resource-group rg-fsi-governance `
    --name "DailyDenyReport" `
    --frequency Day `
    --interval 1 `
    --start-time "2026-01-27T06:00:00Z"

# Link schedule to runbook
az automation job schedule create `
    --automation-account-name aa-fsi-governance `
    --resource-group rg-fsi-governance `
    --runbook-name "Invoke-DailyDenyReport" `
    --schedule-name "DailyDenyReport"
```

---

## Phase 3: Power BI Deployment

### Step 3.1: Import Template

1. Download `DenyEventCorrelation.pbit` from FSI-AgentGov-Solutions
2. Open in Power BI Desktop
3. When prompted, enter parameters:
   - Storage Account URL: `https://stfsigovernance.blob.core.windows.net/deny-events/`
   - Latest Date: `2026-01-26` (or current date)

### Step 3.2: Configure Data Source Credentials

1. In Power BI Desktop: **Transform Data** > **Data source settings**
2. Select Azure Blob Storage source
3. Configure authentication:
   - Account key, or
   - Azure AD (if configured)

### Step 3.3: Publish to Service

1. **Home** > **Publish**
2. Select workspace: "FSI Governance Reports"
3. After publish, open Power BI Service

### Step 3.4: Configure Scheduled Refresh

1. In Power BI Service, go to dataset settings
2. **Scheduled refresh** > Enable
3. Configure:
   - Frequency: Daily
   - Time: 7:00 AM (after extraction completes at 6 AM)
4. **Data source credentials** > Edit credentials

---

## Verification Checklist

### Phase 1 Verification

- [ ] Storage account created with immutable policy
- [ ] Key Vault contains all required secrets
- [ ] Application Insights receiving Copilot Studio telemetry

### Phase 2 Verification

- [ ] Automation account created with required modules
- [ ] Runbook executes without errors (test run)
- [ ] CSV files appear in blob storage after test run
- [ ] Schedule created and linked to runbook

### Phase 3 Verification

- [ ] Power BI template imported successfully
- [ ] Data refreshes without credential errors
- [ ] Dashboard displays data from all three sources
- [ ] Scheduled refresh configured and working

---

## Troubleshooting

### Common Issues

| Issue | Cause | Resolution |
|-------|-------|------------|
| "No audit data returned" | Permission or date range | Verify Purview Audit Reader role; check date range |
| "App Insights query failed" | Token or permission issue | Verify Monitoring Reader role on App Insights; check Key Vault secret |
| "Key Vault access denied" | Missing RBAC | Grant Key Vault Secrets User role to the service principal |
| "Blob upload failed" | Storage permissions | Grant Storage Blob Data Contributor role |
| "Power BI refresh failed" | Credential expiry | Update credentials in dataset settings |

### Log Locations

| Component | Log Location |
|-----------|--------------|
| Azure Automation | Automation Account > Jobs > Output |
| Power BI refresh | Dataset > Refresh history |
| Application Insights | App Insights > Logs (KQL) |

---

## Maintenance

### Weekly Tasks

- [ ] Review runbook job history for failures
- [ ] Check Power BI refresh history
- [ ] Verify data completeness (compare event counts)

### Monthly Tasks

- [ ] Rotate Key Vault secrets if required by policy
- [ ] Review certificate expiry for certificate-based authentication
- [ ] Review storage costs
- [ ] Archive old data beyond retention period

### Quarterly Tasks

- [ ] Review and update extraction scripts for schema changes
- [ ] Test disaster recovery (restore from backup)
- [ ] Update documentation for any changes

---

## Support

For issues with this solution:

1. Check [Troubleshooting](../../../playbooks/control-implementations/1.7/troubleshooting.md) for audit log issues
2. Review [Microsoft Learn: Copilot Audit](https://learn.microsoft.com/en-us/purview/audit-copilot)
3. Open issue in [FSI-AgentGov-Solutions](https://github.com/judeper/FSI-AgentGov-Solutions/issues)

---

*FSI Agent Governance Framework v1.2.38 - February 2026*
