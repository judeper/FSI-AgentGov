# Playbook 3.13-B: PowerShell Setup — Automated Inventory Export and Alert Configuration

**Playbook ID:** 3.13-B
**Control:** 3.13 — Agent 365 Admin Center Analytics and Reporting
**Pillar:** Reporting
**Estimated Duration:** 2–4 hours (initial setup); ongoing automation thereafter
**Required Role:** Entra Global Admin, Exchange Online Admin (for retention), Power Platform Admin (for alerts)
**Prerequisites:** Microsoft Graph PowerShell SDK installed; Power Automate license; Azure subscription for storage
**Last Verified:** March 2026

---

!!! info "Automation Scope"
    This playbook covers: (1) automated agent inventory export via Microsoft Graph API and PowerShell, (2) WORM-compliant storage configuration for SEC 17a-4 compliance, (3) Power Automate alert workflow setup for exception rate and pending request threshold notifications, and (4) scheduled task configuration for recurring exports. Manual portal export procedures are covered in Playbook 3.13-A.

!!! warning "Graph API Preview Endpoints"
    The Microsoft Graph API endpoints for Agent 365 inventory data are subject to change during the Preview period. Validate all endpoint paths against the current Microsoft Graph API documentation before deploying scripts to production. Script examples in this playbook use placeholder endpoint paths that reflect the expected API structure based on available documentation as of March 2026.

---

## Overview

Manual inventory exports (Playbook 3.13-A) are sufficient for Zone 1 and Zone 2 quarterly cadences. Zone 3 firms requiring monthly exports and automated alerting need a programmatic approach. This playbook provides the automation framework to:

- Export agent inventory on a scheduled basis without manual portal access
- Store exports automatically in WORM-compliant Azure Blob Storage
- Send automated alerts to compliance stakeholders when exception rate or pending request thresholds are breached
- Produce evidence-ready export files suitable for FINRA examination production

---

## Part 1: Environment Setup

### Step 1.1: Install Required PowerShell Modules

Open PowerShell 7.x as Administrator on the workstation or automation host that will run scheduled exports.

```powershell
# Install Microsoft Graph PowerShell SDK
Install-Module -Name Microsoft.Graph -Scope AllUsers -Force

# Install Azure PowerShell module (for WORM storage configuration)
Install-Module -Name Az -Scope AllUsers -Force

# Install Exchange Online module (for retention policy verification)
Install-Module -Name ExchangeOnlineManagement -Scope AllUsers -Force

# Verify installations
Get-Module -ListAvailable Microsoft.Graph* | Select-Object Name, Version
Get-Module -ListAvailable Az* | Select-Object Name, Version
```

### Step 1.2: Register an Entra Application for Unattended Export

For scheduled (unattended) exports, you must register an Entra application with appropriate Graph API permissions rather than using interactive sign-in.

**1.2.1** Navigate to Entra Admin Center: `https://entra.microsoft.com`

**1.2.2** Go to: Applications > App registrations > New registration

**1.2.3** Configure the registration:
- **Name**: `FSI-AgentGov-InventoryExport`
- **Supported account types**: Accounts in this organizational directory only
- **Redirect URI**: Leave blank (this is a daemon/service application)

**1.2.4** After registration, record the following values:
- **Application (client) ID**
- **Directory (tenant) ID**

**1.2.5** Create a client secret: Certificates & secrets > New client secret
- Description: `AgentInventoryExport-Prod`
- Expiry: 24 months (align with your secret rotation policy)
- Record the secret value immediately — it will not be displayed again.

**1.2.6** Grant API permissions:
- API permissions > Add a permission > Microsoft Graph > Application permissions
- Add: `Reports.Read.All` (for usage/analytics data)
- Add: `Directory.Read.All` (for agent registry data)
- Select **Grant admin consent** for all permissions.

!!! danger "Secret Management"
    Store the client secret in Azure Key Vault. Do NOT embed secrets in plaintext in scripts or configuration files. Use the Key Vault references pattern in your automation scripts as shown below.

---

## Part 2: Automated Agent Inventory Export Script

### Step 2.1: Configure Script Variables

Save the following as `Export-AgentInventory.ps1` in your automation scripts directory.

```powershell
<#
.SYNOPSIS
    Exports the Microsoft 365 Agent 365 inventory and uploads to WORM-compliant
    Azure Blob Storage for SEC 17a-4 compliance.

.DESCRIPTION
    Connects to Microsoft Graph using a registered Entra application (service principal),
    retrieves the full agent inventory, exports to a dated CSV file, and uploads the
    file to Azure Blob Storage configured with an immutability policy.

    Regulatory context: Produces examination artifacts under FINRA Rule 4511 and
    SEC Rules 17a-3/17a-4. Export files are named with ISO date stamps to establish
    a defensible record of the agent roster at each measurement date.

.NOTES
    Control:       3.13 - Agent 365 Admin Center Analytics and Reporting
    Version:       v1.0
    Last Updated:  March 2026
    Prerequisite:  Microsoft.Graph and Az modules installed; Entra app registered
                   with Reports.Read.All and Directory.Read.All permissions.
    WARNING:       Graph API endpoints for Agent 365 data are in Preview.
                   Validate endpoint paths against current Microsoft Learn docs
                   before deploying to production.
#>

# ============================================================
# CONFIGURATION — Edit these values for your environment
# ============================================================

# Entra App Registration credentials (retrieve from Azure Key Vault in production)
$TenantId         = "YOUR_TENANT_ID"
$ClientId         = "YOUR_APP_CLIENT_ID"

# Key Vault reference for client secret (recommended approach)
$KeyVaultName     = "YOUR_KEYVAULT_NAME"
$SecretName       = "AgentInventoryExport-ClientSecret"

# Azure Storage settings
$StorageAccountName   = "YOUR_STORAGE_ACCOUNT"
$StorageContainerName = "agent-inventory-exports"
$ResourceGroupName    = "YOUR_RESOURCE_GROUP"

# Local staging path (temporary, before upload to WORM storage)
$LocalStagingPath     = "C:\Temp\AgentExports"

# Tenant display name (used in filename)
$TenantDisplayName    = "ContosoCapital"

# Alert configuration
$ComplianceEmailRecipient = "compliance@yourfirm.com"
$ExceptionRateAlertThreshold = 90  # Alert if exception rate drops below this %
$PendingRequestAlertThreshold = 10  # Alert if pending requests exceed this count

# ============================================================
# END CONFIGURATION
# ============================================================

# --- Connect to Azure Key Vault and retrieve client secret ---
Write-Host "[$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')] Connecting to Azure Key Vault..." -ForegroundColor Cyan
Connect-AzAccount -Identity  # Uses managed identity if running on Azure VM/Automation
$SecretValue = (Get-AzKeyVaultSecret -VaultName $KeyVaultName -Name $SecretName -AsPlainText)
$SecureSecret = ConvertTo-SecureString $SecretValue -AsPlainText -Force

# --- Connect to Microsoft Graph ---
Write-Host "[$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')] Connecting to Microsoft Graph..." -ForegroundColor Cyan
$ClientSecretCredential = New-Object -TypeName System.Management.Automation.PSCredential `
    -ArgumentList $ClientId, $SecureSecret

Connect-MgGraph -TenantId $TenantId -ClientSecretCredential $ClientSecretCredential

Write-Host "[$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')] Graph connection established." -ForegroundColor Green

# --- Retrieve Agent Inventory via Graph API ---
# NOTE: Validate the exact endpoint path against current Microsoft Learn documentation.
# The endpoint below reflects the expected Agent 365 API structure as of March 2026.
Write-Host "[$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')] Retrieving agent inventory..." -ForegroundColor Cyan

try {
    # Primary inventory endpoint — adjust path per current API documentation
    $AgentInventoryUri = "https://graph.microsoft.com/beta/admin/m365Apps/agents"
    $AgentInventory    = Invoke-MgGraphRequest -Uri $AgentInventoryUri -Method GET

    $Agents = $AgentInventory.value

    # Handle pagination for large inventories
    while ($AgentInventory.'@odata.nextLink') {
        $AgentInventory = Invoke-MgGraphRequest -Uri $AgentInventory.'@odata.nextLink' -Method GET
        $Agents        += $AgentInventory.value
    }

    Write-Host "[$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')] Retrieved $($Agents.Count) agents." -ForegroundColor Green
}
catch {
    Write-Error "Failed to retrieve agent inventory: $_"
    Write-Warning "If this is a 404 error, the API endpoint path may have changed. Verify against Microsoft Learn."
    exit 1
}

# --- Build Export Object ---
$ExportDate = Get-Date -Format "yyyyMMdd"
$ExportTimestamp = Get-Date -Format "yyyy-MM-ddTHH:mm:ssZ"

$ExportData = foreach ($Agent in $Agents) {
    [PSCustomObject]@{
        ExportDate          = $ExportTimestamp
        TenantId            = $TenantId
        TenantDisplayName   = $TenantDisplayName
        AgentId             = $Agent.id
        AgentDisplayName    = $Agent.displayName
        Publisher           = $Agent.publisher
        PublisherType       = $Agent.publisherType  # Microsoft / Organization / Partner
        Platform            = $Agent.platform
        Status              = $Agent.status
        Owner               = $Agent.owner
        OwnerEmail          = $Agent.ownerEmail
        CreatedDateTime     = $Agent.createdDateTime
        LastModifiedDateTime = $Agent.lastModifiedDateTime
        Description         = $Agent.description
    }
}

# --- Export to CSV ---
if (-not (Test-Path $LocalStagingPath)) {
    New-Item -ItemType Directory -Path $LocalStagingPath | Out-Null
}

$ExportFileName = "AgentInventory_${TenantDisplayName}_${ExportDate}.csv"
$LocalFilePath  = Join-Path $LocalStagingPath $ExportFileName

$ExportData | Export-Csv -Path $LocalFilePath -NoTypeInformation -Encoding UTF8
Write-Host "[$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')] Exported to: $LocalFilePath ($($ExportData.Count) records)" -ForegroundColor Green

# --- Upload to WORM-Compliant Azure Blob Storage ---
Write-Host "[$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')] Uploading to WORM storage..." -ForegroundColor Cyan

$StorageAccount = Get-AzStorageAccount -ResourceGroupName $ResourceGroupName `
    -Name $StorageAccountName
$StorageContext = $StorageAccount.Context

Set-AzStorageBlobContent `
    -File $LocalFilePath `
    -Container $StorageContainerName `
    -Blob $ExportFileName `
    -Context $StorageContext `
    -Force

Write-Host "[$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')] Upload complete: $ExportFileName" -ForegroundColor Green

# --- Clean up local staging file ---
Remove-Item $LocalFilePath -Force
Write-Host "[$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')] Local staging file removed." -ForegroundColor Cyan

# --- Disconnect ---
Disconnect-MgGraph
Write-Host "[$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')] Agent inventory export completed successfully." -ForegroundColor Green
```

---

## Part 3: WORM-Compliant Azure Blob Storage Configuration

Zone 3 firms must store agent inventory exports in WORM-compliant (Write Once Read Many) Azure Blob Storage to satisfy SEC Rule 17a-4(f) requirements for non-rewriteable, non-erasable electronic records.

### Step 3.1: Create Storage Account with Immutability Support

```powershell
# Connect to Azure
Connect-AzAccount

# Set variables
$ResourceGroupName  = "rg-fsi-agentgov-records"
$StorageAccountName = "fsiagentrec$(Get-Random -Maximum 9999)"  # Must be globally unique
$Location           = "eastus"  # Use your preferred Azure region
$ContainerName      = "agent-inventory-exports"

# Create resource group if it does not exist
New-AzResourceGroup -Name $ResourceGroupName -Location $Location -ErrorAction SilentlyContinue

# Create Storage Account with version-level immutability support
# Note: AllowBlobPublicAccess must be disabled per FSI security baseline
New-AzStorageAccount `
    -ResourceGroupName $ResourceGroupName `
    -Name $StorageAccountName `
    -Location $Location `
    -SkuName Standard_GRS `
    -Kind StorageV2 `
    -AllowBlobPublicAccess $false `
    -MinimumTlsVersion TLS1_2 `
    -EnableHttpsTrafficOnly $true

Write-Host "Storage account created: $StorageAccountName"

# Get storage context
$StorageAccount = Get-AzStorageAccount -ResourceGroupName $ResourceGroupName `
    -Name $StorageAccountName
$Context = $StorageAccount.Context

# Create container for agent inventory exports
New-AzStorageContainer -Name $ContainerName -Context $Context

Write-Host "Container created: $ContainerName"
```

### Step 3.2: Configure Time-Based Retention (Immutability Policy)

```powershell
# Enable version-level WORM immutability on the container
# Retention period: 2,190 days = 6 years (FINRA 4511 / SEC 17a-4 requirement)
# IMPORTANT: Once a locked policy is set, the retention period cannot be shortened.
# Test with unlocked policy first; lock only after compliance review.

$RetentionDays = 2190  # 6 years

# Set immutability policy (UNLOCKED — for testing and review)
Set-AzStorageContainerImmutabilityPolicy `
    -ResourceGroupName $ResourceGroupName `
    -StorageAccountName $StorageAccountName `
    -ContainerName $ContainerName `
    -ImmutabilityPeriod $RetentionDays

Write-Host "Immutability policy set: $RetentionDays days (UNLOCKED — review before locking)"

# TO LOCK THE POLICY (irreversible — do not run until compliance review is complete):
# $Policy = Get-AzStorageContainerImmutabilityPolicy `
#     -ResourceGroupName $ResourceGroupName `
#     -StorageAccountName $StorageAccountName `
#     -ContainerName $ContainerName
# Lock-AzStorageContainerImmutabilityPolicy `
#     -ResourceGroupName $ResourceGroupName `
#     -StorageAccountName $StorageAccountName `
#     -ContainerName $ContainerName `
#     -Etag $Policy.Etag

Write-Host "WORM storage configuration complete."
Write-Host "REMINDER: Lock the immutability policy after compliance review to satisfy SEC 17a-4(f)."
```

!!! danger "Immutability Policy Locking is Irreversible"
    Once you lock an Azure Blob Storage immutability policy, you cannot reduce the retention period or delete the policy. Only lock the policy after CCO and Legal review confirms the 6-year retention period is appropriate. An inadvertent lock with an incorrect retention period will require creating a new storage container.

---

## Part 4: Configure Scheduled Task for Automated Export

### Step 4.1: Windows Task Scheduler (On-Premises Automation Host)

```powershell
# Create scheduled task for monthly agent inventory export
# Adjust trigger schedule per your Zone designation:
# - Zone 2: Quarterly (every 3 months)
# - Zone 3: Monthly (first business day of each month)

$TaskName        = "FSI-AgentGov-InventoryExport"
$ScriptPath      = "C:\FSIAgentGov\Scripts\Export-AgentInventory.ps1"
$ServiceAccount  = "DOMAIN\svc-agentgov-export"  # Use a dedicated service account

# Create the action
$Action = New-ScheduledTaskAction `
    -Execute "pwsh.exe" `
    -Argument "-NonInteractive -ExecutionPolicy Bypass -File `"$ScriptPath`""

# Create monthly trigger (first day of each month at 02:00 AM)
$Trigger = New-ScheduledTaskTrigger `
    -Monthly `
    -DaysOfMonth 1 `
    -At "02:00AM"

# Create settings
$Settings = New-ScheduledTaskSettingsSet `
    -ExecutionTimeLimit (New-TimeSpan -Hours 2) `
    -RestartCount 2 `
    -RestartInterval (New-TimeSpan -Minutes 30)

# Register the task
Register-ScheduledTask `
    -TaskName $TaskName `
    -Action $Action `
    -Trigger $Trigger `
    -Settings $Settings `
    -RunLevel Highest `
    -Description "FSI AgentGov: Monthly agent inventory export for SEC 17a-4 compliance"

Write-Host "Scheduled task registered: $TaskName"
```

### Step 4.2: Azure Automation (Cloud-Based Alternative)

For organizations preferring cloud-based automation without on-premises infrastructure:

```powershell
# Create Azure Automation Account for agent governance automation
$AutomationAccountName = "aa-fsi-agentgov"
$AutomationRG          = "rg-fsi-agentgov-records"
$Location              = "eastus"

New-AzAutomationAccount `
    -ResourceGroupName $AutomationRG `
    -Name $AutomationAccountName `
    -Location $Location `
    -AssignSystemIdentity  # Use managed identity — no stored credentials

Write-Host "Azure Automation Account created: $AutomationAccountName"
Write-Host "Assign managed identity the required Graph API permissions via Entra."
Write-Host "Import Export-AgentInventory.ps1 as a Runbook in the Automation Account."
Write-Host "Create a Schedule in the Automation Account for monthly execution."
```

---

## Part 5: Power Automate Alert Workflow Configuration

### Step 5.1: Create Compliance Alert Flow

The following Power Automate flow template sends automated email alerts to the Compliance Officer when exception rate or pending request thresholds are breached. Configure this flow in Power Automate (https://make.powerautomate.com).

**Flow Name**: `FSI-AgentGov-3.13-ComplianceAlerts`

**Trigger**: Scheduled (every 24 hours for Zone 3; every 7 days for Zone 2)

**Flow Logic** (configure using Power Automate UI or import JSON definition):

```
TRIGGER: Recurrence (Daily for Zone 3 / Weekly for Zone 2)

ACTION 1: HTTP - Call Microsoft Graph API
  Method: GET
  URI: https://graph.microsoft.com/beta/admin/m365Apps/agents/analyticsOverview
  Authentication: OAuth 2.0 (Entra app registration)

ACTION 2: Parse JSON (parse the Graph API response)

ACTION 3: Condition — Exception Rate Check
  IF: analyticsOverview.exceptionRate < 90
  THEN: Send Email (Office 365 Outlook)
    To: [ComplianceEmailRecipient]
    Subject: [ALERT] Agent Exception Rate Below Threshold — Review Required
    Body: Exception rate is currently [exceptionRate]%, below the 90% alert threshold.
          Review required per Control 3.13 Zone [X] procedures.
          Date/Time: [utcNow()]
          Action Required: Review exception events and initiate root cause analysis.

ACTION 4: Condition — Pending Requests Check
  IF: analyticsOverview.pendingRequestsCount > 10
  THEN: Send Email (Office 365 Outlook)
    To: [ComplianceEmailRecipient]
    Subject: [ALERT] Agent Pending Requests Exceed Threshold — Disposition Required
    Body: Pending agent requests: [pendingRequestsCount] (threshold: 10).
          Disposition required within 48 hours per Control 3.13 Zone 3 procedures.
          Date/Time: [utcNow()]
          Action Required: Navigate to M365 Admin Center > Agents > Overview >
          Manage Requests and disposition all pending requests.
```

!!! note "Graph API Schema"
    The specific Graph API endpoint and response schema for Agent 365 analytics data should be validated against current Microsoft Learn documentation. The `analyticsOverview` endpoint and property names above are illustrative based on documented capabilities as of March 2026. Adjust the HTTP action URI and Parse JSON schema to match the actual API response structure in your tenant.

---

## Part 6: Verification

After completing setup, run the following verification commands:

```powershell
# Test Graph API connection
Connect-MgGraph -TenantId $TenantId -ClientSecretCredential $ClientSecretCredential
$TestResult = Invoke-MgGraphRequest -Uri "https://graph.microsoft.com/v1.0/organization" -Method GET
Write-Host "Tenant: $($TestResult.value[0].displayName)"
Disconnect-MgGraph

# Verify WORM storage configuration
$Policy = Get-AzStorageContainerImmutabilityPolicy `
    -ResourceGroupName $ResourceGroupName `
    -StorageAccountName $StorageAccountName `
    -ContainerName $ContainerName
Write-Host "Immutability period: $($Policy.ImmutabilityPeriodSinceCreationInDays) days"
Write-Host "Policy state: $($Policy.State)"  # Should be "Locked" for production Zone 3

# Test export script (dry run)
& "C:\FSIAgentGov\Scripts\Export-AgentInventory.ps1" -WhatIf
```

---

## Completion Checklist

- [ ] Microsoft.Graph and Az PowerShell modules installed
- [ ] Entra app registration created with required permissions and admin consent granted
- [ ] Client secret stored in Azure Key Vault (not in plaintext)
- [ ] Export-AgentInventory.ps1 script configured and tested
- [ ] WORM-compliant Azure Blob Storage container created
- [ ] Immutability policy set (unlocked) and reviewed with CCO and Legal before locking
- [ ] Immutability policy locked (Zone 3 production environments)
- [ ] Scheduled task or Azure Automation runbook configured for recurring export
- [ ] Power Automate compliance alert flow created and tested
- [ ] Alert email received successfully from test run
- [ ] All configuration documented in IT governance register

---

[Back to Control 3.13](../../../controls/pillar-3-reporting/3.13-agent-365-admin-center-analytics.md) | [Portal Walkthrough](portal-walkthrough.md) | [Verification Testing](verification-testing.md) | [Troubleshooting](troubleshooting.md)

*Updated: March 2026 | Version: v1.3*
