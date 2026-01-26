# Control 1.11: Conditional Access and Phishing-Resistant MFA - PowerShell Setup

> This playbook provides PowerShell automation guidance for [Control 1.11](../../../controls/pillar-1-security/1.11-conditional-access-and-phishing-resistant-mfa.md).

---

## Connect to Microsoft Graph

```powershell
# Install Microsoft Graph module if needed
Install-Module Microsoft.Graph -Force -AllowClobber

# Connect with appropriate scopes
Connect-MgGraph -Scopes "Policy.Read.All","Policy.ReadWrite.ConditionalAccess","Directory.Read.All","AuditLog.Read.All"

# Verify connection
Get-MgContext
```

---

## Get Conditional Access Policies

```powershell
# List all Conditional Access policies
Get-MgIdentityConditionalAccessPolicy |
    Select-Object DisplayName, State, CreatedDateTime, ModifiedDateTime |
    Format-Table

# Get details of a specific policy
$policy = Get-MgIdentityConditionalAccessPolicy -Filter "displayName eq 'Require MFA for Agent Creators'"
$policy | ConvertTo-Json -Depth 10
```

---

## Get Authentication Strengths

```powershell
# List available authentication strengths
Get-MgPolicyAuthenticationStrengthPolicy |
    Select-Object Id, DisplayName, Description, PolicyType |
    Format-Table -AutoSize

# Get phishing-resistant strength ID
$phishingResistant = Get-MgPolicyAuthenticationStrengthPolicy |
    Where-Object { $_.DisplayName -match "phishing" -or $_.DisplayName -match "resistant" } |
    Select-Object -First 1

$phishingResistant | Format-List Id, DisplayName, Description
```

---

## Create Conditional Access Policy

```powershell
# Discover phishing-resistant Authentication Strength policy Id
$phishingResistantStrengthId = (Get-MgPolicyAuthenticationStrengthPolicy |
    Where-Object { $_.DisplayName -match "phishing" -and $_.DisplayName -match "resistant" } |
    Select-Object -First 1).Id

if (-not $phishingResistantStrengthId) {
    throw "Could not find phishing-resistant Authentication Strength policy."
}

# Define policy for enterprise agent creators
$params = @{
    DisplayName = "FSI-Enterprise-Agent-Creators-PhishingResistantMFA"
    State = "enabledForReportingButNotEnforced"  # Start in report-only
    Conditions = @{
        Users = @{
            IncludeGroups = @("sg-enterprise-agent-creators")
            ExcludeGroups = @("sg-emergency-access")
        }
        Applications = @{
            IncludeApplications = @("All")
        }
        ClientAppTypes = @("all")
    }
    GrantControls = @{
        Operator = "OR"
        BuiltInControls = @()
        AuthenticationStrength = @{
            Id = $phishingResistantStrengthId
        }
    }
}

New-MgIdentityConditionalAccessPolicy -BodyParameter $params
```

---

## Configure Named Locations

```powershell
# Create a named location for corporate offices
$namedLocationParams = @{
    "@odata.type" = "#microsoft.graph.ipNamedLocation"
    DisplayName = "Corporate Offices"
    IsTrusted = $true
    IpRanges = @(
        @{
            "@odata.type" = "#microsoft.graph.iPv4CidrRange"
            CidrAddress = "203.0.113.0/24"
        },
        @{
            "@odata.type" = "#microsoft.graph.iPv4CidrRange"
            CidrAddress = "198.51.100.0/24"
        }
    )
}

New-MgIdentityConditionalAccessNamedLocation -BodyParameter $namedLocationParams

# List named locations
Get-MgIdentityConditionalAccessNamedLocation |
    Select-Object DisplayName, IsTrusted, CreatedDateTime |
    Format-Table
```

---

## Audit Agent Sign-In Activity

```powershell
# Get sign-in logs for agents (requires Graph beta endpoint)
$agentSignIns = Get-MgBetaAuditLogSignIn -Filter "isInteractive eq false and signInEventTypes/any(t: t eq 'nonInteractiveUser')" -Top 100

# Filter for agent-related sign-ins
$agentSignIns | Where-Object { $_.AppDisplayName -match "Copilot|Agent|Bot" } |
    Select-Object CreatedDateTime, UserDisplayName, AppDisplayName, Status, ConditionalAccessStatus |
    Format-Table

# Export agent sign-in report
$agentSignIns | Export-Csv -Path "Agent-SignIn-Report.csv" -NoTypeInformation
```

---

## Monitor CA Policy Enforcement

```powershell
# Get CA policy application results from sign-in logs
$caResults = Get-MgBetaAuditLogSignIn -Filter "createdDateTime ge $(Get-Date).AddDays(-7).ToString('yyyy-MM-ddTHH:mm:ssZ')" -Top 500

# Analyze CA enforcement
$caResults | ForEach-Object {
    foreach ($caPolicy in $_.AppliedConditionalAccessPolicies) {
        [PSCustomObject]@{
            Date = $_.CreatedDateTime
            User = $_.UserDisplayName
            PolicyName = $caPolicy.DisplayName
            Result = $caPolicy.Result
            GrantControls = ($caPolicy.GrantControls -join ", ")
        }
    }
} | Group-Object PolicyName, Result |
    Select-Object Name, Count |
    Sort-Object Count -Descending |
    Format-Table

# Export CA enforcement report
$caResults | Export-Csv -Path "CA-Enforcement-Report.csv" -NoTypeInformation
```

---

## Export Policies for Evidence

```powershell
# Export all CA policies as JSON
$policies = Get-MgIdentityConditionalAccessPolicy
$policies | ConvertTo-Json -Depth 10 | Out-File "CA-Policies-Export-$(Get-Date -Format 'yyyyMMdd').json"

# Export authentication strengths
$strengths = Get-MgPolicyAuthenticationStrengthPolicy
$strengths | ConvertTo-Json -Depth 10 | Out-File "AuthStrengths-Export-$(Get-Date -Format 'yyyyMMdd').json"
```

---

## Complete Configuration Script

```powershell
<#
.SYNOPSIS
    Configures Control 1.11 - Conditional Access and Phishing-Resistant MFA

.DESCRIPTION
    This script configures Conditional Access policies for AI agent creators,
    including phishing-resistant MFA requirements and named locations.

.PARAMETER PolicyName
    The name for the Conditional Access policy

.PARAMETER IncludeGroups
    Security groups to include in the policy

.PARAMETER ExcludeGroups
    Security groups to exclude (e.g., emergency access)

.EXAMPLE
    .\Configure-Control-1.11.ps1 -PolicyName "FSI-Agent-Creators-MFA" -IncludeGroups @("sg-agent-creators")

.NOTES
    Last Updated: January 2026
    Related Control: Control 1.11 - Conditional Access and Phishing-Resistant MFA
#>

param(
    [Parameter(Mandatory=$true)]
    [string]$PolicyName,

    [Parameter(Mandatory=$true)]
    [string[]]$IncludeGroups,

    [string[]]$ExcludeGroups = @("sg-emergency-access")
)

try {
    # Connect to Microsoft Graph
    Write-Host "Connecting to Microsoft Graph..." -ForegroundColor Cyan
    Connect-MgGraph -Scopes "Policy.Read.All","Policy.ReadWrite.ConditionalAccess","Directory.Read.All"

    Write-Host "Configuring Control 1.11: Conditional Access and Phishing-Resistant MFA" -ForegroundColor Cyan

    # Step 1: Get phishing-resistant authentication strength
    Write-Host "`n[Step 1] Discovering phishing-resistant authentication strength..." -ForegroundColor Yellow
    $phishingResistantStrength = Get-MgPolicyAuthenticationStrengthPolicy |
        Where-Object { $_.DisplayName -match "phishing" -and $_.DisplayName -match "resistant" } |
        Select-Object -First 1

    if (-not $phishingResistantStrength) {
        throw "Could not find phishing-resistant Authentication Strength policy."
    }
    Write-Host "  Found: $($phishingResistantStrength.DisplayName)" -ForegroundColor Green

    # Step 2: Create Conditional Access policy
    Write-Host "`n[Step 2] Creating Conditional Access policy..." -ForegroundColor Yellow
    $params = @{
        DisplayName = $PolicyName
        State = "enabledForReportingButNotEnforced"
        Conditions = @{
            Users = @{
                IncludeGroups = $IncludeGroups
                ExcludeGroups = $ExcludeGroups
            }
            Applications = @{
                IncludeApplications = @("All")
            }
            ClientAppTypes = @("all")
        }
        GrantControls = @{
            Operator = "OR"
            BuiltInControls = @()
            AuthenticationStrength = @{
                Id = $phishingResistantStrength.Id
            }
        }
    }

    $policy = New-MgIdentityConditionalAccessPolicy -BodyParameter $params
    Write-Host "  Created policy: $($policy.DisplayName)" -ForegroundColor Green

    # Step 3: Export configuration for evidence
    Write-Host "`n[Step 3] Exporting configuration for compliance evidence..." -ForegroundColor Yellow
    $exportPath = "CA-Policy-Export-$(Get-Date -Format 'yyyyMMdd-HHmmss').json"
    $policy | ConvertTo-Json -Depth 10 | Out-File $exportPath
    Write-Host "  Exported to: $exportPath" -ForegroundColor Green

    Write-Host "`n[PASS] Control 1.11 configuration completed successfully" -ForegroundColor Green
}
catch {
    Write-Host "[FAIL] Error: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host "[INFO] Stack trace: $($_.ScriptStackTrace)" -ForegroundColor Yellow
    exit 1
}
finally {
    # Cleanup connections
    if (Get-MgContext) {
        Disconnect-MgGraph -ErrorAction SilentlyContinue
        Write-Host "`nDisconnected from Microsoft Graph" -ForegroundColor Gray
    }
}
```

---

*Updated: January 2026 | Version: v1.2*
