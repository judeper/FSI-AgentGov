# Playbook 3.14-B: PowerShell and SDK Setup — Installing the Observability SDK and Configuring Log Retention

!!! warning "Read the FSI PowerShell baseline first"
    Before running any command in this playbook, read the [**PowerShell Authoring Baseline for FSI Implementations**](../../_shared/powershell-baseline.md). It is the canonical source for module version pinning, sovereign-cloud (GCC / GCC High / DoD) endpoints, mutation safety (`-WhatIf` / `SupportsShouldProcess`), Dataverse compatibility, and SHA-256 evidence emission. Snippets below may show abbreviated patterns; the baseline is authoritative.

**Playbook ID:** 3.14-B
**Control:** 3.14 — Agent 365 Observability SDK and Custom Agent Telemetry
**Pillar:** Reporting
**Estimated Duration:** 3–6 hours (initial SDK integration per agent); 30–60 minutes (log retention configuration)
**Required Role:** Copilot Studio Agent Author / Application developer (SDK implementation, non-admin role); Entra Global Admin (Entra diagnostic settings); Power Platform Admin or Azure subscription Owner (storage and Log Analytics provisioning); Purview Audit Reader (Unified Audit Log verification)
**Last Verified:** April 2026

---

!!! info "SDK Preview Status"
    The Agent 365 Observability SDK packages are available for Python, JavaScript, and .NET. Full integration with the M365 Admin Center metrics dashboard requires Frontier program enrollment. SDK package names, configuration APIs, and required environment variables may change during the Preview period. Validate all package versions and configuration parameters against the current Microsoft Learn documentation and official SDK repository before deploying to production.

!!! warning "Mandatory for Zone 3"
    For Zone 3 (Regulated) tenants, SDK implementation is mandatory for ALL custom agents. A custom agent deployed in production without Observability SDK instrumentation constitutes a control deficiency requiring remediation within 30 days.

---

## Overview

This playbook covers:
1. Installing the Agent 365 Observability SDK for Python, JavaScript, and .NET agents
2. Configuring the SDK in each language runtime
3. Setting the required environment variables for telemetry export
4. Configuring Entra diagnostic settings for agentSignIn log retention via PowerShell
5. Verifying telemetry flow from development through to the Admin Center and Purview

---

## Part 1: Python SDK Installation and Configuration

### Step 1.1: Install the Python Package

The Agent 365 Observability SDK for Python is distributed via PyPI.

```bash
# Install from PyPI
pip install microsoft-agents-a365

# For development environments, also install test utilities
pip install microsoft-agents-a365[dev]

# Verify installation
pip show microsoft-agents-a365
```

Confirm the installed package output includes:
- **Name**: microsoft-agents-a365
- **Version**: Check Microsoft Learn for the current recommended version
- **Location**: your environment's site-packages directory

### Step 1.2: Configure the Python SDK

The SDK requires a token resolver function that provides a valid Microsoft identity token for the agent's service principal. The agent must be registered in Microsoft Entra ID before SDK initialization.

```python
"""
Agent 365 Observability SDK — Python Configuration
Control: 3.14 - Agent 365 Observability SDK and Custom Agent Telemetry
FSI-AgentGov Framework | Pillar 3: Reporting

PREREQUISITES:
- Entra app registration created for this agent service
- Application (client) ID and tenant ID from Entra registration
- Client certificate or secret available (retrieve from Azure Key Vault)
- ENABLE_A365_OBSERVABILITY_EXPORTER environment variable set to "true"
"""

import os
from azure.identity import ClientSecretCredential, DefaultAzureCredential
from microsoft_agents_a365.observability.core import config

# ============================================================
# TOKEN RESOLVER SETUP
# Provides the Microsoft identity token required by the SDK.
# Best practice: use DefaultAzureCredential for managed identity
# in Azure-hosted agents; ClientSecretCredential for on-premises.
# ============================================================

def get_token_resolver():
    """
    Returns a token resolver function compatible with the Agent 365 SDK.
    In production: use managed identity (DefaultAzureCredential).
    In development: use client secret credential from Key Vault.
    """

    # Option A: Managed Identity (preferred for Azure-hosted agents)
    # Requires the agent's Azure resource (App Service, Container Apps, etc.)
    # to have a system-assigned or user-assigned managed identity configured.
    credential = DefaultAzureCredential()

    # Option B: Client Secret (for non-Azure or on-premises agents)
    # credential = ClientSecretCredential(
    #     tenant_id=os.environ["AZURE_TENANT_ID"],
    #     client_id=os.environ["AZURE_CLIENT_ID"],
    #     client_secret=os.environ["AZURE_CLIENT_SECRET"]  # Retrieve from Key Vault
    # )

    # Scope required for Agent 365 telemetry export
    A365_SCOPE = "https://agent365.microsoft.com/.default"

    def token_resolver():
        """Returns a current access token for Agent 365 telemetry export."""
        token = credential.get_token(A365_SCOPE)
        return token.token

    return token_resolver


# ============================================================
# SDK INITIALIZATION
# Must be called at agent startup, before any agent logic runs.
# ============================================================

def initialize_observability():
    """
    Initializes the Agent 365 Observability SDK.

    service_name: Unique identifier for this agent service.
                  Appears in Admin Center as the agent display name source.
                  Use a consistent name that matches the Entra app registration.

    service_namespace: Organizational namespace for grouping related agents.
                       Recommended format: "org.division.team" or "lob.function"

    token_resolver: Callable that returns a current Microsoft identity token.
    """

    config.configure(
        service_name=os.environ.get("AGENT_SERVICE_NAME", "my-fsi-agent"),
        service_namespace=os.environ.get("AGENT_SERVICE_NAMESPACE", "contoso.capital.research"),
        token_resolver=get_token_resolver(),
    )

    print(f"Agent 365 Observability initialized: {os.environ.get('AGENT_SERVICE_NAME')}")
    print(f"Exporter enabled: {os.environ.get('ENABLE_A365_OBSERVABILITY_EXPORTER', 'false')}")


# ============================================================
# USAGE: Call initialize_observability() at agent startup
# ============================================================
#
# if __name__ == "__main__":
#     initialize_observability()
#     # ... your agent logic here
```

### Step 1.3: Set Required Environment Variables (Python)

Set the following environment variables in your agent's runtime environment. Use Azure App Configuration, Azure Key Vault references, or your organization's secrets management platform — do NOT hard-code these values.

```bash
# Required: Enables telemetry export to Agent 365 service
export ENABLE_A365_OBSERVABILITY_EXPORTER=true

# Required: Agent identity (match to Entra app registration name)
export AGENT_SERVICE_NAME="contoso-research-agent"
export AGENT_SERVICE_NAMESPACE="contoso.capital.research"

# Required for ClientSecretCredential (if not using managed identity)
export AZURE_TENANT_ID="your-tenant-id"
export AZURE_CLIENT_ID="your-agent-app-client-id"
# Retrieve AZURE_CLIENT_SECRET from Key Vault — never set in plaintext

# Optional: Override default Agent 365 endpoint (leave unset unless directed by Microsoft Support)
# export AGENT365_ENDPOINT="https://agent365.microsoft.com"
```

---

## Part 2: JavaScript/TypeScript SDK Installation and Configuration

### Step 2.1: Install the npm Package

```bash
# Install using npm
npm install @microsoft/agents-a365-observability

# Or using yarn
yarn add @microsoft/agents-a365-observability

# Verify installation
npm list @microsoft/agents-a365-observability
```

### Step 2.2: Configure the JavaScript/TypeScript SDK

```typescript
/**
 * Agent 365 Observability SDK — TypeScript Configuration
 * Control: 3.14 - Agent 365 Observability SDK and Custom Agent Telemetry
 * FSI-AgentGov Framework | Pillar 3: Reporting
 */

import { configure } from '@microsoft/agents-a365-observability';
import { DefaultAzureCredential } from '@azure/identity';

// Token resolver using DefaultAzureCredential (managed identity preferred)
const credential = new DefaultAzureCredential();
const A365_SCOPE = 'https://agent365.microsoft.com/.default';

const tokenResolver = async (): Promise<string> => {
    const token = await credential.getToken(A365_SCOPE);
    if (!token) {
        throw new Error('Failed to acquire token for Agent 365 Observability');
    }
    return token.token;
};

// Initialize SDK at application startup
export function initializeObservability(): void {
    configure({
        serviceName: process.env.AGENT_SERVICE_NAME ?? 'my-fsi-agent-js',
        serviceNamespace: process.env.AGENT_SERVICE_NAMESPACE ?? 'contoso.capital.trading',
        tokenResolver,
    });

    console.log(`Agent 365 Observability initialized.`);
    console.log(`Exporter enabled: ${process.env.ENABLE_A365_OBSERVABILITY_EXPORTER ?? 'false'}`);
}
```

Set the required environment variables as shown in Step 1.3 (same variable names apply across all SDK languages).

---

## Part 3: .NET SDK Installation and Configuration

### Step 3.1: Install NuGet Packages

The .NET SDK is distributed as a family of NuGet packages. Install the packages appropriate to your agent architecture.

```powershell
# Core package — required for all .NET agents
dotnet add package Microsoft.Agents.A365.Observability

# Runtime integration — required if agent uses the Microsoft Agents Runtime
dotnet add package Microsoft.Agents.A365.Observability.Runtime

# Hosting integration — required for ASP.NET Core / Generic Host agents
dotnet add package Microsoft.Agents.A365.Observability.Hosting

# Optional extension packages — install as needed for your agent's LLM or framework:
# For Azure OpenAI / OpenAI API integration:
dotnet add package Microsoft.Agents.A365.Observability.OpenAI

# For Semantic Kernel-based agents:
dotnet add package Microsoft.Agents.A365.Observability.SemanticKernel

# For Microsoft Agent Framework-based agents:
dotnet add package Microsoft.Agents.A365.Observability.AgentFramework

# Verify installation
dotnet list package | Select-String "Microsoft.Agents.A365"
```

Expected output from `dotnet list package`:
```
> Microsoft.Agents.A365.Observability             [version]
> Microsoft.Agents.A365.Observability.Hosting     [version]
> Microsoft.Agents.A365.Observability.Runtime     [version]
```

### Step 3.2: Configure the .NET SDK

**For ASP.NET Core / Generic Host agents** (recommended pattern using `Microsoft.Agents.A365.Observability.Hosting`):

```csharp
// Program.cs — .NET 8 Generic Host configuration
// Control: 3.14 - Agent 365 Observability SDK and Custom Agent Telemetry
// FSI-AgentGov Framework | Pillar 3: Reporting

using Azure.Identity;
using Microsoft.Agents.A365.Observability.Hosting;
using Microsoft.Extensions.DependencyInjection;
using Microsoft.Extensions.Hosting;

var builder = Host.CreateApplicationBuilder(args);

// Add Agent 365 Observability to the DI container
builder.Services.AddAgentObservability(options =>
{
    options.ServiceName      = builder.Configuration["AgentObservability:ServiceName"]
                               ?? "contoso-compliance-agent";
    options.ServiceNamespace = builder.Configuration["AgentObservability:ServiceNamespace"]
                               ?? "contoso.capital.compliance";

    // Token resolver using managed identity (DefaultAzureCredential)
    // For on-premises agents: substitute ClientSecretCredential
    var credential = new DefaultAzureCredential();
    options.TokenResolver  = async () =>
    {
        var token = await credential.GetTokenAsync(
            new Azure.Core.TokenRequestContext(
                new[] { "https://agent365.microsoft.com/.default" }
            )
        );
        return token.Token;
    };
});

// If using Semantic Kernel extension:
// builder.Services.AddAgentObservabilitySemanticKernel();

// If using OpenAI extension:
// builder.Services.AddAgentObservabilityOpenAI();

var app = builder.Build();
await app.RunAsync();
```

**appsettings.json** (non-sensitive configuration):
```json
{
  "AgentObservability": {
    "ServiceName": "contoso-compliance-agent",
    "ServiceNamespace": "contoso.capital.compliance"
  }
}
```

**Environment variables** (set via Azure App Service configuration or Key Vault references):
```
ENABLE_A365_OBSERVABILITY_EXPORTER=true
AZURE_TENANT_ID=<tenant-id>
AZURE_CLIENT_ID=<agent-app-client-id>
```

### Step 3.3: Verify .NET Package Integrity

```powershell
# List all installed Agent 365 packages and their versions for documentation
$ProjectPath = "C:\src\your-agent-project"
Push-Location $ProjectPath

dotnet list package | Where-Object { $_ -match "Microsoft.Agents.A365" }

Pop-Location

# Example expected output:
# > Microsoft.Agents.A365.Observability                    1.0.0-preview.X
# > Microsoft.Agents.A365.Observability.Hosting            1.0.0-preview.X
# > Microsoft.Agents.A365.Observability.SemanticKernel     1.0.0-preview.X
```

Document all installed package versions in the agent's deployment manifest for SOX IT general controls testing purposes.

---

## Part 4: Entra Diagnostic Settings Configuration via PowerShell

The portal-based configuration is covered in Playbook 3.14-A. Use PowerShell for automated configuration or for organizations that require infrastructure-as-code (IaC) governance of diagnostic settings.

### Step 4.1: Configure MicrosoftServicePrincipalSignInLogs via Azure PowerShell

```powershell
<#
.SYNOPSIS
    Configures Entra diagnostic settings to route MicrosoftServicePrincipalSignInLogs
    to both Log Analytics (real-time query) and WORM-compliant blob storage (retention).

.NOTES
    Control:      3.14 - Agent 365 Observability SDK and Custom Agent Telemetry
    Regulatory:   FINRA Rule 4511 (6-year retention floor), SEC Rule 17a-4(f) (WORM)
    Version:      v1.0
    Last Updated: March 2026

    IMPORTANT: MicrosoftServicePrincipalSignInLogs is in Public Preview.
    Validate the log category name against current Azure documentation before running.
#>

# ============================================================
# CONFIGURATION — Edit for your environment
# ============================================================

$TenantId              = "YOUR_TENANT_ID"
$SubscriptionId        = "YOUR_SUBSCRIPTION_ID"
$LogAnalyticsWorkspaceId = "/subscriptions/$SubscriptionId/resourceGroups/rg-fsi-agentgov/providers/Microsoft.OperationalInsights/workspaces/law-fsi-agentgov"
$StorageAccountId      = "/subscriptions/$SubscriptionId/resourceGroups/rg-fsi-agentgov-records/providers/Microsoft.Storage/storageAccounts/fsiagentrec1234"
$DiagnosticSettingName = "FSI-AgentGov-ServicePrincipalSignInLogs"

# ============================================================

# Connect to Azure
Connect-AzAccount -TenantId $TenantId

# Set subscription context
Set-AzContext -SubscriptionId $SubscriptionId

# Define the Entra (AAD) resource URI for diagnostic settings
$EntraResourceUri = "/tenants/$TenantId/providers/microsoft.aadiam"

# Define which log categories to enable
$LogCategories = @(
    @{
        Category = "MicrosoftServicePrincipalSignInLogs"  # Public Preview
        Enabled  = $true
        RetentionPolicy = @{ Enabled = $false; Days = 0 }  # Retention managed by storage immutability policy
    },
    @{
        Category = "ServicePrincipalSignInLogs"
        Enabled  = $true
        RetentionPolicy = @{ Enabled = $false; Days = 0 }
    },
    @{
        Category = "AuditLogs"
        Enabled  = $true
        RetentionPolicy = @{ Enabled = $false; Days = 0 }
    }
)

# Convert to the format expected by Set-AzDiagnosticSetting
$LogSettings = $LogCategories | ForEach-Object {
    New-Object -TypeName Microsoft.Azure.Management.Monitor.Models.LogSettings `
        -Property @{
            Category        = $_.Category
            Enabled         = $_.Enabled
            RetentionPolicy = New-Object -TypeName Microsoft.Azure.Management.Monitor.Models.RetentionPolicy `
                -Property @{
                    Enabled = $_.RetentionPolicy.Enabled
                    Days    = $_.RetentionPolicy.Days
                }
        }
}

# Create or update the diagnostic setting
# Note: Entra diagnostic settings use a different cmdlet than resource diagnostic settings
# The Set-AzDiagnosticSetting below is the correct approach for Entra/AAD tenant-level settings
Set-AzDiagnosticSetting `
    -ResourceId $EntraResourceUri `
    -Name $DiagnosticSettingName `
    -WorkspaceId $LogAnalyticsWorkspaceId `
    -StorageAccountId $StorageAccountId `
    -Log $LogSettings `
    -Enabled $true

Write-Host "Diagnostic setting configured: $DiagnosticSettingName"
Write-Host "Log categories enabled: MicrosoftServicePrincipalSignInLogs, ServicePrincipalSignInLogs, AuditLogs"
Write-Host "Destinations: Log Analytics workspace + WORM blob storage"

# Verify the setting was created
Get-AzDiagnosticSetting -ResourceId $EntraResourceUri | Where-Object { $_.Name -eq $DiagnosticSettingName }
```

!!! note "Entra Diagnostic Settings API"
    Microsoft Entra ID diagnostic settings are configured at the tenant level using a specific resource URI format (`/tenants/{tenantId}/providers/microsoft.aadiam`). This differs from resource-level diagnostic settings. If the `Set-AzDiagnosticSetting` cmdlet returns an error with this resource URI, use the Azure REST API or the Entra Admin Center portal UI (Playbook 3.14-A, Part 2) as an alternative. The `Az.Monitor` module version must support Entra diagnostic settings — use `Az.Monitor 3.0.0` or later.

---

## Part 5: Verify Telemetry Flow via PowerShell

### Step 5.1: Query Log Analytics for Agent Telemetry

```powershell
<#
.SYNOPSIS
    Verifies that Agent 365 Observability telemetry is flowing to Log Analytics.
    Run this script after SDK implementation to confirm successful integration.
#>

# Connect
Connect-AzAccount -TenantId $TenantId
$WorkspaceName = "law-fsi-agentgov"
$WorkspaceRG   = "rg-fsi-agentgov"

# Get workspace resource ID
$Workspace = Get-AzOperationalInsightsWorkspace `
    -ResourceGroupName $WorkspaceRG `
    -Name $WorkspaceName

# Query for agent-related service principal sign-ins
$Query = @"
// Agent 365 Observability — Telemetry Verification Query
// Run against your Log Analytics workspace to confirm telemetry ingestion
// Control: 3.14 FSI-AgentGov

ServicePrincipalSignInLogs
| where TimeGenerated > ago(24h)
| extend IsAgent = tostring(parse_json(AdditionalDetails)['isAgent'])
| where IsAgent == "true" or AdditionalDetails contains "agent"
| project
    TimeGenerated,
    AppDisplayName,
    ServicePrincipalId,
    ResourceDisplayName,
    ResultType,
    ResultDescription,
    IPAddress,
    Location
| order by TimeGenerated desc
| take 50
"@

Write-Host "Querying Log Analytics for agent sign-in telemetry (last 24 hours)..."

$Results = Invoke-AzOperationalInsightsQuery `
    -WorkspaceId $Workspace.CustomerId `
    -Query $Query

if ($Results.Results.Count -eq 0) {
    Write-Warning "No agent sign-in records found in the last 24 hours."
    Write-Warning "Possible causes: SDK not yet deployed, no agent invocations in the query window, or telemetry lag."
} else {
    Write-Host "Agent sign-in records found: $($Results.Results.Count)" -ForegroundColor Green
    $Results.Results | Format-Table TimeGenerated, AppDisplayName, ResourceDisplayName, ResultType -AutoSize
}

# Check for MicrosoftServicePrincipalSignInLogs specifically
$Query2 = @"
MicrosoftServicePrincipalSignInLogs
| where TimeGenerated > ago(24h)
| summarize Count = count() by AppDisplayName
| order by Count desc
"@

Write-Host "`nQuerying MicrosoftServicePrincipalSignInLogs..."

try {
    $Results2 = Invoke-AzOperationalInsightsQuery `
        -WorkspaceId $Workspace.CustomerId `
        -Query $Query2

    if ($Results2.Results.Count -eq 0) {
        Write-Warning "MicrosoftServicePrincipalSignInLogs: No records found. Verify diagnostic setting is active."
    } else {
        Write-Host "MicrosoftServicePrincipalSignInLogs records found:" -ForegroundColor Green
        $Results2.Results | Format-Table AppDisplayName, Count -AutoSize
    }
}
catch {
    Write-Warning "MicrosoftServicePrincipalSignInLogs table not found. The diagnostic setting may not yet be active, or the log category may use a different table name in your workspace."
}
```

### Step 5.2: Verify Purview Audit Log via PowerShell

```powershell
<#
.SYNOPSIS
    Searches the Unified Audit Log in Microsoft Purview for agent session records.
    Confirms that Agent 365 Observability SDK telemetry is flowing to Purview.

    Requires: ExchangeOnlineManagement module (Search-UnifiedAuditLog cmdlet)
    Permissions: Purview Audit Reader (View-Only Audit Logs)

    NOTE: Search-UnifiedAuditLog is deprecated; Microsoft has announced retirement
    in favor of the Microsoft Graph auditLogs API
    (https://learn.microsoft.com/en-us/graph/api/resources/security-auditlogquery).
    For Zone 3 production automation built after April 2026, prefer the Graph
    auditLogs/queries endpoint. Validate cmdlet availability against the current
    Microsoft Learn deprecation timeline before scheduling this script.
#>

# Connect to Exchange Online (provides access to Unified Audit Log)
Connect-ExchangeOnline -UserPrincipalName "admin@yourfirm.com"

# Search for agent-related audit records
$StartDate = (Get-Date).AddDays(-7)
$EndDate   = Get-Date

Write-Host "Searching Unified Audit Log for agent session records (last 7 days)..."

# Note: When the AgentSignIn / AgentSession record types reach GA in your tenant,
# replace the broad search below with -RecordType "AgentSignIn","AgentSession".
# The current Preview record types vary by tenant region; the broad search below
# captures activity by operation name pattern instead of record type.
$AuditResults = Search-UnifiedAuditLog `
    -StartDate $StartDate `
    -EndDate $EndDate `
    -Operations "AgentSession*","AgentToolCall*","agentSignIn*" `
    -ResultSize 1000

if ($AuditResults.Count -eq 0) {
    Write-Warning "No agent audit records found."
    Write-Warning "Verify: (1) SDK is deployed with ENABLE_A365_OBSERVABILITY_EXPORTER=true"
    Write-Warning "         (2) Agent has been invoked since SDK deployment"
    Write-Warning "         (3) Purview audit record type 'AgentSignIn' is available in your tenant"
} else {
    Write-Host "Agent audit records found: $($AuditResults.Count)" -ForegroundColor Green
    $AuditResults | Select-Object CreationDate, UserIds, Operations, RecordType | Format-Table -AutoSize
}

# Verify retention policy is configured
Write-Host "`nChecking Unified Audit Log retention configuration..."
# Note: retention policies are managed in Purview portal; PowerShell verification
# uses the Get-RetentionCompliancePolicy cmdlet from the Security & Compliance module
# Install-Module -Name ExchangeOnlineManagement if not already installed

Disconnect-ExchangeOnline -Confirm:$false
Write-Host "Audit log verification complete."
```

---

## Part 6: SDK Implementation Registry

Maintain the following registry for each custom agent in the tenant. Store this registry in the firm's governance document management system.

```powershell
# Generate SDK Implementation Registry report
# Run after implementing SDK across all custom agents

$SDKRegistry = @(
    [PSCustomObject]@{
        AgentName           = "Contoso Research Agent"
        AgentEntraClientId  = "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"
        Platform            = "Azure AI Foundry"
        SDKLanguage         = "Python"
        SDKPackage          = "microsoft-agents-a365"
        SDKVersion          = "1.0.0-preview.X"
        ImplementationDate  = "2026-03-15"
        VerifiedInAdminCenter = $true
        PurviewTelemetryConfirmed = $true
        DefenderAlertingConfirmed = $true
        Owner               = "Research Technology Team"
        OwnerEmail          = "research-tech@yourfirm.com"
        Zone                = "Zone 3"
        LastReviewDate      = "2026-03-22"
        Notes               = ""
    }
    # Add additional agents here
)

# Export to CSV for governance documentation
$RegistryFileName = "SDKImplementationRegistry_$(Get-Date -Format 'yyyyMMdd').csv"
$SDKRegistry | Export-Csv -Path "C:\FSIAgentGov\$RegistryFileName" -NoTypeInformation -Encoding UTF8
Write-Host "SDK Implementation Registry exported: $RegistryFileName"
```

---

## Completion Checklist

- [ ] Python SDK installed and configured (`microsoft-agents-a365` package)
- [ ] JavaScript/TypeScript SDK installed if applicable (`@microsoft/agents-a365-observability` package)
- [ ] .NET SDK packages installed: `Microsoft.Agents.A365.Observability` (core) + applicable extensions
- [ ] `ENABLE_A365_OBSERVABILITY_EXPORTER=true` set in all production agent runtime environments
- [ ] Token resolver configured (managed identity preferred; client secret via Key Vault for on-premises)
- [ ] `service_name` and `service_namespace` set and consistent with Entra app registration
- [ ] Entra diagnostic setting created for `MicrosoftServicePrincipalSignInLogs`
- [ ] Diagnostic setting routes to Log Analytics workspace AND WORM blob storage
- [ ] WORM blob storage immutability policy locked (Zone 3)
- [ ] SDK-instrumented agents confirmed visible in M365 Admin Center Agent Registry
- [ ] Purview audit log search confirms telemetry ingestion
- [ ] Log Analytics query confirms sign-in log data flow
- [ ] SDK Implementation Registry document created and stored
- [ ] All package versions documented in agent deployment manifest

---

[Back to Control 3.14](../../../controls/pillar-3-reporting/3.14-agent-365-observability-sdk.md) | [Portal Walkthrough](portal-walkthrough.md) | [Verification Testing](verification-testing.md) | [Troubleshooting](troubleshooting.md)

*Updated: April 2026 | Version: v1.3.3 | UI Verification Status: Current*
