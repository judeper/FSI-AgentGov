# Control 1.8: Runtime Protection and External Threat Detection - PowerShell Setup

> This playbook provides PowerShell automation guidance for [Control 1.8](../../../controls/pillar-1-security/1.8-runtime-protection-and-external-threat-detection.md).

---

## Connect to Power Platform

```powershell
Install-Module -Name Microsoft.PowerApps.Administration.PowerShell -Force

# Connect to Power Platform (interactive authentication)
Add-PowerAppsAccount

# For automated/unattended scenarios, use service principal authentication:
# $appId = "<Application-Client-ID>"
# $secret = "<Client-Secret>"
# $tenantId = "<Tenant-ID>"
# Add-PowerAppsAccount -ApplicationId $appId -ClientSecret $secret -TenantID $tenantId
```

---

## Get Managed Environment Status

```powershell
$Environments = Get-AdminPowerAppEnvironment

$EnvReport = @()
foreach ($Env in $Environments) {
    $EnvReport += [PSCustomObject]@{
        DisplayName = $Env.DisplayName
        EnvironmentName = $Env.EnvironmentName
        IsManaged = $Env.Properties.protectionLevel -eq "Standard"
        Location = $Env.Location
        EnvironmentType = $Env.EnvironmentType
    }
}

Write-Host "Managed Environment Status:" -ForegroundColor Cyan
$EnvReport | Format-Table -AutoSize
```

---

## Create Webhook App Registration for Defender Integration

The following script automates the creation of an Entra app registration with Federated Identity Credentials (FIC) for Additional Threat Detection.

```powershell
<#
.SYNOPSIS
    Creates Entra app registration for Copilot Studio Defender integration.

.DESCRIPTION
    This script:
    1. Creates an Entra app registration for webhook authentication
    2. Configures Federated Identity Credentials (FIC) for secure token exchange
    3. Outputs the Application ID for Power Platform configuration

.PARAMETER TenantId
    Your Microsoft Entra ID tenant ID (GUID format)

.PARAMETER WebhookEndpoint
    The full HTTPS URL of your security provider webhook

.PARAMETER DisplayName
    Optional display name for the app registration (default: CopilotStudio-ThreatDetection-Webhook)

.PARAMETER FICName
    Optional name for the Federated Identity Credential (default: CopilotStudio-FIC)

.EXAMPLE
    .\Create-CopilotWebhookApp.ps1 -TenantId "12345678-1234-1234-1234-123456789012" `
        -WebhookEndpoint "https://defender-webhook.azurewebsites.net/api/evaluate"

.EXAMPLE
    .\Create-CopilotWebhookApp.ps1 -TenantId "12345678-1234-1234-1234-123456789012" `
        -WebhookEndpoint "https://my-security-provider.com/webhook" `
        -DisplayName "Copilot-Defender-Prod" `
        -FICName "DefenderFIC-Prod"

.NOTES
    Last Updated: February 2026
    Related Control: Control 1.8 - Runtime Protection and External Threat Detection
    Requires: Microsoft.Graph PowerShell module with Application.ReadWrite.All permission
#>

param(
    [Parameter(Mandatory=$true)]
    [ValidatePattern('^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$')]
    [string]$TenantId,

    [Parameter(Mandatory=$true)]
    [ValidatePattern('^https://')]
    [string]$WebhookEndpoint,

    [Parameter(Mandatory=$false)]
    [string]$DisplayName = "CopilotStudio-ThreatDetection-Webhook",

    [Parameter(Mandatory=$false)]
    [string]$FICName = "CopilotStudio-FIC"
)

try {
    Write-Host "=== Creating Copilot Studio Defender Integration App ===" -ForegroundColor Cyan

    # Connect to Microsoft Graph
    Write-Host "`nStep 1: Connecting to Microsoft Graph..." -ForegroundColor White
    Connect-MgGraph -Scopes "Application.ReadWrite.All" -TenantId $TenantId

    # Create app registration
    Write-Host "`nStep 2: Creating app registration..." -ForegroundColor White
    $AppParams = @{
        DisplayName = $DisplayName
        SignInAudience = "AzureADMyOrg"
        Description = "Enables Copilot Studio to authenticate with external threat detection provider"
        Tags = @("CopilotStudio", "ThreatDetection", "FSI-AgentGov")
    }

    $App = New-MgApplication @AppParams

    Write-Host "  [DONE] App registration created" -ForegroundColor Green
    Write-Host "  Application ID: $($App.AppId)" -ForegroundColor Yellow
    Write-Host "  Object ID: $($App.Id)" -ForegroundColor Yellow

    # Encode values for FIC subject identifier
    Write-Host "`nStep 3: Encoding FIC subject identifier..." -ForegroundColor White
    $TenantIdBase64 = [Convert]::ToBase64String([Text.Encoding]::UTF8.GetBytes($TenantId))
    $EndpointBase64 = [Convert]::ToBase64String([Text.Encoding]::UTF8.GetBytes($WebhookEndpoint))

    Write-Host "  Tenant ID (Base64): $TenantIdBase64" -ForegroundColor Gray
    Write-Host "  Endpoint (Base64): $EndpointBase64" -ForegroundColor Gray

    # Configure Federated Identity Credential
    Write-Host "`nStep 4: Configuring Federated Identity Credential..." -ForegroundColor White
    $SubjectIdentifier = "/eid1/c/pub/t/$TenantIdBase64/a/m1WPnYRZpEaQKq1Cceg--g/$EndpointBase64"

    $FicParams = @{
        ApplicationId = $App.Id
        BodyParameter = @{
            Name = $FICName
            Issuer = "https://login.microsoftonline.com/$TenantId/v2.0"
            Subject = $SubjectIdentifier
            Audiences = @("api://AzureADTokenExchange")
            Description = "FIC for Power Platform Copilot Studio threat detection"
        }
    }

    New-MgApplicationFederatedIdentityCredential @FicParams

    Write-Host "  [DONE] Federated Identity Credential configured" -ForegroundColor Green

    # Output summary
    Write-Host "`n=== CONFIGURATION COMPLETE ===" -ForegroundColor Cyan
    Write-Host "Use these values in Power Platform Admin Center:" -ForegroundColor White
    Write-Host ""
    Write-Host "  Azure Entra App ID: $($App.AppId)" -ForegroundColor Yellow
    Write-Host "  Endpoint Link:      $WebhookEndpoint" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Portal Path: Power Platform Admin Center > Security > Threat detection > Additional threat detection" -ForegroundColor Gray

    # Return app details for automation
    return [PSCustomObject]@{
        ApplicationId = $App.AppId
        ObjectId = $App.Id
        DisplayName = $DisplayName
        WebhookEndpoint = $WebhookEndpoint
        FICName = $FICName
        TenantId = $TenantId
    }
}
catch {
    Write-Host "[FAIL] Error: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host "[INFO] Ensure you have Application.ReadWrite.All permission in Microsoft Graph" -ForegroundColor Yellow
    throw
}
```

---

## Verify App Registration and FIC Configuration

```powershell
<#
.SYNOPSIS
    Verifies existing Copilot Studio Defender integration app registration.

.DESCRIPTION
    Checks that the app registration and FIC are configured correctly.

.PARAMETER AppId
    The Application (client) ID to verify

.EXAMPLE
    .\Verify-CopilotWebhookApp.ps1 -AppId "12345678-1234-1234-1234-123456789012"
#>

param(
    [Parameter(Mandatory=$true)]
    [string]$AppId
)

try {
    Connect-MgGraph -Scopes "Application.Read.All"

    # Get app registration by AppId
    $App = Get-MgApplication -Filter "appId eq '$AppId'"

    if (-not $App) {
        Write-Host "[FAIL] App registration not found: $AppId" -ForegroundColor Red
        return
    }

    Write-Host "=== App Registration Verification ===" -ForegroundColor Cyan
    Write-Host "Display Name: $($App.DisplayName)" -ForegroundColor Green
    Write-Host "Application ID: $($App.AppId)" -ForegroundColor Green
    Write-Host "Object ID: $($App.Id)" -ForegroundColor Green
    Write-Host "Sign-In Audience: $($App.SignInAudience)" -ForegroundColor Green

    # Get Federated Identity Credentials
    $Fics = Get-MgApplicationFederatedIdentityCredential -ApplicationId $App.Id

    if ($Fics.Count -eq 0) {
        Write-Host "[WARN] No Federated Identity Credentials found" -ForegroundColor Yellow
    } else {
        Write-Host "`n=== Federated Identity Credentials ===" -ForegroundColor Cyan
        foreach ($Fic in $Fics) {
            Write-Host "Name: $($Fic.Name)" -ForegroundColor Green
            Write-Host "Issuer: $($Fic.Issuer)" -ForegroundColor Gray
            Write-Host "Subject: $($Fic.Subject)" -ForegroundColor Gray
            Write-Host "Audiences: $($Fic.Audiences -join ', ')" -ForegroundColor Gray
            Write-Host ""
        }
    }

    Write-Host "[PASS] App registration verification complete" -ForegroundColor Green
}
catch {
    Write-Host "[FAIL] Error: $($_.Exception.Message)" -ForegroundColor Red
}
```

---

## Enable Additional Threat Detection via Power Platform API

For organizations wanting to automate threat detection configuration across multiple environments:

```powershell
<#
.SYNOPSIS
    Configures Additional Threat Detection for Power Platform environments via API.

.DESCRIPTION
    Uses Power Platform Admin API to enable threat detection at environment level.
    Note: This is an advanced automation scenario. Portal configuration is recommended for initial setup.

.PARAMETER EnvironmentId
    The Power Platform environment ID (GUID)

.PARAMETER AppId
    The Entra app registration Application ID

.PARAMETER WebhookEndpoint
    The security provider webhook URL

.PARAMETER ErrorBehavior
    "Allow" or "Block" - behavior when provider is unavailable

.EXAMPLE
    .\Configure-ThreatDetection.ps1 -EnvironmentId "env-guid" -AppId "app-guid" `
        -WebhookEndpoint "https://webhook.example.com" -ErrorBehavior "Block"
#>

param(
    [Parameter(Mandatory=$true)]
    [string]$EnvironmentId,

    [Parameter(Mandatory=$true)]
    [string]$AppId,

    [Parameter(Mandatory=$true)]
    [string]$WebhookEndpoint,

    [Parameter(Mandatory=$false)]
    [ValidateSet("Allow", "Block")]
    [string]$ErrorBehavior = "Block"
)

try {
    # Connect to Power Platform
    Add-PowerAppsAccount

    Write-Host "=== Configuring Additional Threat Detection ===" -ForegroundColor Cyan
    Write-Host "Environment: $EnvironmentId" -ForegroundColor White
    Write-Host "Error Behavior: $ErrorBehavior" -ForegroundColor White

    # Note: Direct API configuration requires Power Platform Admin API access
    # This example shows the configuration structure

    $ThreatDetectionConfig = @{
        isEnabled = $true
        enableDataSharing = $true
        applicationId = $AppId
        endpointUrl = $WebhookEndpoint
        errorBehavior = $ErrorBehavior
    }

    Write-Host "`nConfiguration to apply:" -ForegroundColor Yellow
    $ThreatDetectionConfig | Format-List

    # Note: No dedicated threat-detection cmdlet exists as of Feb 2026.
    # Use the Power Platform Admin Center UI or the admin connector REST API instead.

    Write-Host "`n[INFO] Use Power Platform Admin Center UI for initial configuration" -ForegroundColor Yellow
    Write-Host "[INFO] API automation is recommended for bulk deployment after initial validation" -ForegroundColor Yellow
}
catch {
    Write-Host "[FAIL] Error: $($_.Exception.Message)" -ForegroundColor Red
}
```

---

## Audit Log Analysis for Threats

```powershell
# Connect to Security & Compliance
Connect-IPPSSession

$StartDate = (Get-Date).AddDays(-7)
$EndDate = Get-Date

# Search for Copilot Studio security events
$SecurityEvents = Search-UnifiedAuditLog `
    -StartDate $StartDate `
    -EndDate $EndDate `
    -RecordType CopilotInteraction `
    -ResultSize 1000

Write-Host "Copilot interaction events found: $($SecurityEvents.Count)" -ForegroundColor Yellow

# Parse for security-relevant events
$SecurityAnalysis = $SecurityEvents | ForEach-Object {
    $AuditData = $_.AuditData | ConvertFrom-Json

    [PSCustomObject]@{
        Date = $_.CreationDate
        User = $_.UserIds
        Operation = $AuditData.Operation
        AppName = $AuditData.AppName
        Result = $AuditData.ResultStatus
        SecurityFlag = if ($AuditData.Operation -match "block|inject|jailbreak") { "ALERT" } else { "Normal" }
    }
}

# Identify potential threats
$Threats = $SecurityAnalysis | Where-Object { $_.SecurityFlag -eq "ALERT" }

if ($Threats.Count -gt 0) {
    Write-Host "POTENTIAL THREATS DETECTED:" -ForegroundColor Red
    $Threats | Format-Table
} else {
    Write-Host "No threat indicators found in period" -ForegroundColor Green
}
```

---

## Check Connector Security

```powershell
# Get connectors used by agents in managed environments
$Connectors = Get-AdminPowerAppConnector

$HighRiskConnectors = $Connectors | Where-Object {
    $_.Properties.displayName -match "HTTP|Custom|SQL|File"
}

if ($HighRiskConnectors.Count -gt 0) {
    Write-Host "High-risk connectors requiring review:" -ForegroundColor Yellow
    $HighRiskConnectors | Select-Object @{N='Name'; E={$_.Properties.displayName}}, ConnectorId | Format-Table
}
```

---

## Generate Security Report

```powershell
$Report = @{
    ReportDate = Get-Date
    AnalysisPeriod = "$StartDate to $EndDate"
    TotalCopilotEvents = $SecurityEvents.Count
    ThreatIndicators = $Threats.Count
    ManagedEnvironments = ($EnvReport | Where-Object { $_.IsManaged }).Count
    UnmanagedEnvironments = ($EnvReport | Where-Object { -not $_.IsManaged }).Count
}

Write-Host "=== RUNTIME PROTECTION SECURITY SUMMARY ===" -ForegroundColor Cyan
$Report | Format-List

# Export detailed report
$SecurityAnalysis | Export-Csv "RuntimeProtection-Analysis-$(Get-Date -Format 'yyyyMMdd').csv" -NoTypeInformation
```

---

## Sentinel Detection Rule (KQL)

```kql
// Prompt Injection Detection
PowerPlatformAdminActivity
| where Operation == "PromptInjectionDetected"
| extend AgentName = tostring(parse_json(ExtendedProperties).AgentName)
| project TimeGenerated, UserId, AgentName, ClientIP, Operation
| order by TimeGenerated desc
```

---

## Complete Configuration Script

```powershell
<#
.SYNOPSIS
    Configures Control 1.8 - Runtime Protection and External Threat Detection

.DESCRIPTION
    This script:
    1. Audits Managed Environment status across all environments
    2. Searches audit logs for security events
    3. Identifies high-risk connectors
    4. Generates security analysis report

.PARAMETER TenantId
    Microsoft Entra ID tenant ID for webhook configuration (optional)

.PARAMETER OutputPath
    Path for security reports (default: current directory)

.EXAMPLE
    .\Configure-Control-1.8.ps1 -OutputPath "C:\SecurityReports"

.NOTES
    Last Updated: February 2026
    Related Control: Control 1.8 - Runtime Protection and External Threat Detection
#>

param(
    [Parameter(Mandatory=$false)]
    [string]$TenantId,

    [Parameter(Mandatory=$false)]
    [string]$OutputPath = "."
)

try {
    # Connect to Power Platform
    Add-PowerAppsAccount

    Write-Host "=== Configuring Control 1.8: Runtime Protection ===" -ForegroundColor Cyan

    # Step 1: Get Managed Environment status for all environments
    Write-Host "`nStep 1: Auditing Managed Environment status..." -ForegroundColor White
    $Environments = Get-AdminPowerAppEnvironment

    $EnvReport = @()
    foreach ($Env in $Environments) {
        $EnvReport += [PSCustomObject]@{
            DisplayName = $Env.DisplayName
            EnvironmentName = $Env.EnvironmentName
            IsManaged = $Env.Properties.protectionLevel -eq "Standard"
            Location = $Env.Location
            EnvironmentType = $Env.EnvironmentType
        }
    }

    $managedCount = ($EnvReport | Where-Object { $_.IsManaged }).Count
    $unmanagedCount = ($EnvReport | Where-Object { -not $_.IsManaged }).Count

    Write-Host "  [DONE] Managed: $managedCount | Unmanaged: $unmanagedCount" -ForegroundColor Green
    $EnvReport | Format-Table DisplayName, IsManaged, EnvironmentType -AutoSize

    # Step 2: Connect to Security & Compliance and search for threat events
    Write-Host "`nStep 2: Searching for security events..." -ForegroundColor White
    Connect-IPPSSession

    $StartDate = (Get-Date).AddDays(-7)
    $EndDate = Get-Date

    $SecurityEvents = Search-UnifiedAuditLog `
        -StartDate $StartDate `
        -EndDate $EndDate `
        -RecordType CopilotInteraction `
        -ResultSize 1000

    Write-Host "  [DONE] Found $($SecurityEvents.Count) Copilot interaction events" -ForegroundColor Green

    # Step 3: Analyze security events
    Write-Host "`nStep 3: Analyzing for threat indicators..." -ForegroundColor White
    $SecurityAnalysis = $SecurityEvents | ForEach-Object {
        $AuditData = $_.AuditData | ConvertFrom-Json

        [PSCustomObject]@{
            Date = $_.CreationDate
            User = $_.UserIds
            Operation = $AuditData.Operation
            AppName = $AuditData.AppName
            Result = $AuditData.ResultStatus
            SecurityFlag = if ($AuditData.Operation -match "block|inject|jailbreak") { "ALERT" } else { "Normal" }
        }
    }

    $Threats = $SecurityAnalysis | Where-Object { $_.SecurityFlag -eq "ALERT" }

    if ($Threats.Count -gt 0) {
        Write-Host "  [ALERT] Potential threats detected: $($Threats.Count)" -ForegroundColor Red
        $Threats | Format-Table Date, User, Operation -AutoSize
    } else {
        Write-Host "  [PASS] No threat indicators found in period" -ForegroundColor Green
    }

    # Step 4: Check for high-risk connectors
    Write-Host "`nStep 4: Checking for high-risk connectors..." -ForegroundColor White
    $Connectors = Get-AdminPowerAppConnector

    $HighRiskConnectors = $Connectors | Where-Object {
        $_.Properties.displayName -match "HTTP|Custom|SQL|File"
    }

    if ($HighRiskConnectors.Count -gt 0) {
        Write-Host "  [WARN] High-risk connectors requiring review: $($HighRiskConnectors.Count)" -ForegroundColor Yellow
        $HighRiskConnectors | Select-Object @{N='Name'; E={$_.Properties.displayName}}, ConnectorId | Format-Table
    } else {
        Write-Host "  [PASS] No high-risk connectors detected" -ForegroundColor Green
    }

    # Step 5: Generate and export security report
    Write-Host "`nStep 5: Generating security report..." -ForegroundColor White
    $Report = @{
        ReportDate = Get-Date
        AnalysisPeriod = "$StartDate to $EndDate"
        TotalCopilotEvents = $SecurityEvents.Count
        ThreatIndicators = $Threats.Count
        ManagedEnvironments = $managedCount
        UnmanagedEnvironments = $unmanagedCount
        HighRiskConnectors = $HighRiskConnectors.Count
    }

    Write-Host "`n=== RUNTIME PROTECTION SECURITY SUMMARY ===" -ForegroundColor Cyan
    $Report | Format-List

    # Export detailed report
    $SecurityAnalysis | Export-Csv "$OutputPath\RuntimeProtection-Analysis-$(Get-Date -Format 'yyyyMMdd').csv" -NoTypeInformation
    $EnvReport | Export-Csv "$OutputPath\ManagedEnvironments-$(Get-Date -Format 'yyyyMMdd').csv" -NoTypeInformation

    Write-Host "  [DONE] Reports exported to: $OutputPath" -ForegroundColor Green

    Write-Host "`n[PASS] Control 1.8 configuration completed successfully" -ForegroundColor Green
}
catch {
    Write-Host "[FAIL] Error: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host "[INFO] Stack trace: $($_.ScriptStackTrace)" -ForegroundColor Yellow
    exit 1
}
finally {
    # Disconnect from Security & Compliance Center
    Disconnect-ExchangeOnline -Confirm:$false -ErrorAction SilentlyContinue
}
```

---

## Related Playbooks

- [Portal Walkthrough](./portal-walkthrough.md) - Step-by-step portal configuration
- [Verification & Testing](./verification-testing.md) - Test procedures
- [Troubleshooting](./troubleshooting.md) - Common issues and solutions

---

*Updated: February 2026 | Version: v1.3*
