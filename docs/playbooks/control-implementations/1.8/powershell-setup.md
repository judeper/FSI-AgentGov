# Control 1.8: Runtime Protection and External Threat Detection - PowerShell Setup

> This playbook provides PowerShell automation guidance for [Control 1.8](../../../controls/pillar-1-security/1.8-runtime-protection-and-external-threat-detection.md).

---

## Connect to Power Platform

```powershell
Install-Module -Name Microsoft.PowerApps.Administration.PowerShell -Force
Add-PowerAppsAccount
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

## Create Webhook App Registration

```powershell
# Create-CopilotWebhookApp.ps1
param(
    [Parameter(Mandatory=$true)]
    [string]$TenantId,

    [Parameter(Mandatory=$true)]
    [string]$WebhookEndpoint
)

# Connect to Microsoft Graph
Connect-MgGraph -Scopes "Application.ReadWrite.All"

# Create app registration
$AppParams = @{
    DisplayName = "CopilotStudio-ThreatDetection-Webhook"
    SignInAudience = "AzureADMyOrg"
}

$App = New-MgApplication @AppParams

Write-Host "App registration created: $($App.AppId)" -ForegroundColor Green

# Encode values for FIC subject
$TenantIdBase64 = [Convert]::ToBase64String([Text.Encoding]::UTF8.GetBytes($TenantId))
$EndpointBase64 = [Convert]::ToBase64String([Text.Encoding]::UTF8.GetBytes($WebhookEndpoint))

# Configure Federated Identity Credential
$FicParams = @{
    ApplicationId = $App.Id
    BodyParameter = @{
        Name = "CopilotStudio-FIC"
        Issuer = "https://login.microsoftonline.com/$TenantId/v2.0"
        Subject = "/eid1/c/pub/t/$TenantIdBase64/a/m1WPnYRZpEaQKq1Cceg--g/$EndpointBase64"
        Audiences = @("api://AzureADTokenExchange")
    }
}

New-MgApplicationFederatedIdentityCredential @FicParams

Write-Host "Federated Identity Credential configured" -ForegroundColor Green
Write-Host "Application ID for Power Platform: $($App.AppId)" -ForegroundColor Cyan
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

```kusto
// Prompt Injection Detection
PowerPlatformAdminActivity
| where Operation == "PromptInjectionDetected"
| extend AgentName = tostring(parse_json(ExtendedProperties).AgentName)
| project TimeGenerated, UserId, AgentName, ClientIP, Operation
| order by TimeGenerated desc
```

---

*Updated: January 2026 | Version: v1.1*
