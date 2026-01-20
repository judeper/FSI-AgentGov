# Script Validation Guide

This guide provides step-by-step instructions for validating PowerShell and KQL scripts used in the FSI Agent Governance Framework playbooks.

---

## 1. Prerequisites

### Azure and Microsoft 365 Requirements

| Requirement | Purpose |
|-------------|---------|
| Azure subscription with Log Analytics workspace | Required for KQL query validation |
| Microsoft 365 tenant with E5 or equivalent licensing | Required for Purview and Sentinel features |
| Microsoft Sentinel workspace (Zone 3) | Required for advanced threat detection queries |
| PowerShell 7.x or later | Required for cross-platform script execution |

### Required PowerShell Modules

Install the following modules before running governance scripts:

```powershell
# Microsoft 365 Administration
Install-Module -Name ExchangeOnlineManagement -Force -AllowClobber
Install-Module -Name Microsoft.Online.SharePoint.PowerShell -Force -AllowClobber
Install-Module -Name MicrosoftTeams -Force -AllowClobber

# Power Platform Administration
Install-Module -Name Microsoft.PowerApps.Administration.PowerShell -Force -AllowClobber
Install-Module -Name Microsoft.PowerApps.PowerShell -Force -AllowClobber

# Microsoft Graph
Install-Module -Name Microsoft.Graph -Force -AllowClobber
Install-Module -Name Microsoft.Graph.Beta -Force -AllowClobber

# Azure Modules (for KQL/Sentinel)
Install-Module -Name Az.Accounts -Force -AllowClobber
Install-Module -Name Az.Monitor -Force -AllowClobber
Install-Module -Name Az.OperationalInsights -Force -AllowClobber

# Security and Compliance
Install-Module -Name ExchangeOnlineManagement -Force -AllowClobber  # Includes compliance cmdlets
```

### Verify Module Installation

```powershell
# Verify all required modules are installed
$requiredModules = @(
    'ExchangeOnlineManagement',
    'Microsoft.Online.SharePoint.PowerShell',
    'MicrosoftTeams',
    'Microsoft.PowerApps.Administration.PowerShell',
    'Microsoft.Graph',
    'Az.Accounts',
    'Az.Monitor',
    'Az.OperationalInsights'
)

foreach ($module in $requiredModules) {
    $installed = Get-Module -ListAvailable -Name $module
    if ($installed) {
        Write-Host "[PASS] $module v$($installed.Version)" -ForegroundColor Green
    } else {
        Write-Host "[MISSING] $module - Install with: Install-Module -Name $module" -ForegroundColor Red
    }
}
```

---

## 2. PowerShell Validation Steps

### Step 2.1: Connect to Services

Before running governance scripts, establish connections to required services:

```powershell
# Connect to Exchange Online (includes Purview/Compliance)
Connect-ExchangeOnline -UserPrincipalName admin@yourtenant.onmicrosoft.com

# Connect to Microsoft Graph
Connect-MgGraph -Scopes "Directory.Read.All", "Policy.Read.All", "AuditLog.Read.All"

# Connect to Power Platform
Add-PowerAppsAccount

# Connect to Azure (for Log Analytics/Sentinel)
Connect-AzAccount
Set-AzContext -SubscriptionId "your-subscription-id"

# Connect to SharePoint Online
Connect-SPOService -Url https://yourtenant-admin.sharepoint.com
```

### Step 2.2: Run Test Scripts

Test scripts from each pillar to verify connectivity and permissions:

**Pillar 1 - Security Test:**

```powershell
# Test DLP policy retrieval
try {
    $dlpPolicies = Get-DlpCompliancePolicy -ErrorAction Stop
    Write-Host "[PASS] Retrieved $($dlpPolicies.Count) DLP policies" -ForegroundColor Green
}
catch {
    Write-Host "[FAIL] Cannot retrieve DLP policies: $($_.Exception.Message)" -ForegroundColor Red
}
```

**Pillar 2 - Management Test:**

```powershell
# Test Power Platform environment retrieval
try {
    $environments = Get-AdminPowerAppEnvironment -ErrorAction Stop
    Write-Host "[PASS] Retrieved $($environments.Count) Power Platform environments" -ForegroundColor Green
}
catch {
    Write-Host "[FAIL] Cannot retrieve environments: $($_.Exception.Message)" -ForegroundColor Red
}
```

**Pillar 3 - Reporting Test:**

```powershell
# Test audit log search
try {
    $auditLogs = Search-UnifiedAuditLog -StartDate (Get-Date).AddDays(-1) -EndDate (Get-Date) -RecordType PowerApps -ResultSize 10 -ErrorAction Stop
    Write-Host "[PASS] Audit log search returned $($auditLogs.Count) records" -ForegroundColor Green
}
catch {
    Write-Host "[FAIL] Cannot search audit logs: $($_.Exception.Message)" -ForegroundColor Red
}
```

**Pillar 4 - SharePoint Test:**

```powershell
# Test SharePoint site retrieval
try {
    $sites = Get-SPOSite -Limit 10 -ErrorAction Stop
    Write-Host "[PASS] Retrieved $($sites.Count) SharePoint sites" -ForegroundColor Green
}
catch {
    Write-Host "[FAIL] Cannot retrieve SharePoint sites: $($_.Exception.Message)" -ForegroundColor Red
}
```

### Step 2.3: Verify Expected Output

Each script should produce output matching expected patterns:

| Script Type | Expected Output | Validation |
|-------------|-----------------|------------|
| Inventory scripts | JSON/CSV with agent metadata | Verify schema matches documentation |
| Policy scripts | Policy objects with GUID | Verify policy exists in portal |
| Audit scripts | Audit records with timestamps | Verify date range coverage |
| Compliance scripts | Status objects (Compliant/Non-Compliant) | Cross-check with portal status |

---

## 3. KQL Query Validation Steps

### Step 3.1: Access Log Analytics Workspace

1. Navigate to Azure Portal → Log Analytics workspaces
2. Select your workspace
3. Click **Logs** in the left navigation

### Step 3.2: Verify Data Ingestion

Run these diagnostic queries to verify data sources are connected:

```kql
// Check Power Platform data ingestion
PowerPlatformAdminActivity
| summarize Count = count() by bin(TimeGenerated, 1d)
| order by TimeGenerated desc
| take 7

// Check Microsoft 365 audit data
OfficeActivity
| where TimeGenerated > ago(7d)
| summarize Count = count() by OfficeWorkload
| order by Count desc

// Check Azure AD sign-in data
SigninLogs
| summarize Count = count() by bin(TimeGenerated, 1d)
| order by TimeGenerated desc
| take 7
```

### Step 3.3: Test Sample Queries

**Agent Activity Query:**

```kql
// Agent creation and modification events
PowerPlatformAdminActivity
| where TimeGenerated > ago(30d)
| where OperationName has_any ("CreateCopilot", "UpdateCopilot", "DeleteCopilot", "PublishCopilot")
| project TimeGenerated, UserPrincipalName, OperationName, EnvironmentName
| order by TimeGenerated desc
| take 100
```

**Security Event Query:**

```kql
// DLP policy violations
OfficeActivity
| where TimeGenerated > ago(7d)
| where Operation == "DLPRuleMatch"
| project TimeGenerated, UserId, Operation, PolicyName = tostring(parse_json(PolicyDetails)[0].PolicyName)
| order by TimeGenerated desc
| take 50
```

### Step 3.4: Validate Table Availability

Verify required tables exist in your workspace:

```kql
// List available tables
search *
| distinct $table
| where $table has_any ("PowerPlatform", "Office", "Signin", "AuditLogs")
| order by $table asc
```

Expected tables for full governance coverage:

| Table | Purpose | Required For |
|-------|---------|--------------|
| `PowerPlatformAdminActivity` | Power Platform admin actions | Controls 2.1, 2.2, 3.1 |
| `OfficeActivity` | Microsoft 365 audit events | Controls 1.7, 3.2 |
| `SigninLogs` | Azure AD sign-ins | Control 1.11 |
| `AuditLogs` | Azure AD directory changes | Control 1.18 |
| `SecurityAlert` | Sentinel alerts | Control 3.9 |

---

## 4. Common Issues and Troubleshooting

### Module Version Conflicts

**Symptom:** Commands fail with "method not found" or "parameter not recognized" errors.

**Resolution:**

```powershell
# Remove and reinstall conflicting module
Remove-Module -Name Microsoft.Graph -Force -ErrorAction SilentlyContinue
Uninstall-Module -Name Microsoft.Graph -AllVersions -Force
Install-Module -Name Microsoft.Graph -Force -AllowClobber

# Clear module cache
Remove-Item "$env:USERPROFILE\Documents\PowerShell\Modules\Microsoft.Graph" -Recurse -Force -ErrorAction SilentlyContinue
```

### Authentication Failures

**Symptom:** "Access denied" or "Unauthorized" errors.

**Resolution:**

1. Verify account has required admin roles
2. Check conditional access policies don't block PowerShell access
3. For MFA-enabled accounts, use interactive authentication:

```powershell
# Interactive authentication with MFA
Connect-ExchangeOnline -UserPrincipalName admin@tenant.com -ShowBanner:$false

# For service accounts, use certificate authentication
Connect-ExchangeOnline -CertificateThumbprint "THUMBPRINT" -AppId "APP-ID" -Organization "tenant.onmicrosoft.com"
```

### Missing Data Sources

**Symptom:** KQL queries return no results.

**Resolution:**

1. Verify diagnostic settings are configured:
   - Azure Portal → Monitor → Diagnostic settings
   - Ensure Power Platform, Office 365, and Azure AD logs are sent to workspace

2. Check data ingestion latency (typically 5-15 minutes):

```kql
// Check latest ingestion time per table
union withsource=TableName *
| summarize LastIngestion = max(TimeGenerated) by TableName
| where LastIngestion > ago(1h)
| order by LastIngestion desc
```

### Table Schema Differences

**Symptom:** Queries fail with "column not found" errors.

**Resolution:**

```kql
// Inspect actual table schema
PowerPlatformAdminActivity
| getschema

// Use dynamic column access for varying schemas
PowerPlatformAdminActivity
| extend SafeColumn = iff(isnotempty(column_ifexists("NewColumnName", "")), NewColumnName, "N/A")
```

---

## 5. Validation Checklist

Before deploying governance scripts to production:

- [ ] All required PowerShell modules installed and updated
- [ ] Service connections established successfully
- [ ] Test scripts from each pillar execute without errors
- [ ] KQL queries return expected data
- [ ] Required Log Analytics tables are populated
- [ ] Authentication method works with your security policies
- [ ] Error handling produces meaningful messages
- [ ] Output format matches documentation requirements

---

## 6. Related Resources

- [PowerShell Module Documentation](../../reference/microsoft-learn-urls.md)
- [KQL Quick Reference](https://learn.microsoft.com/en-us/azure/data-explorer/kusto/query/)
- [Power Platform Admin PowerShell](https://learn.microsoft.com/en-us/power-platform/admin/powershell-installation)
- [Microsoft Graph PowerShell SDK](https://learn.microsoft.com/en-us/powershell/microsoftgraph/)

---

*FSI Agent Governance Framework v1.1 - January 2026*
