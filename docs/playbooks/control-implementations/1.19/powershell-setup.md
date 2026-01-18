# PowerShell Setup: Control 1.19 - eDiscovery for Agent Interactions

**Last Updated:** January 2026
**Modules Required:** ExchangeOnlineManagement

## Prerequisites

```powershell
Install-Module -Name ExchangeOnlineManagement -Force -Scope CurrentUser
```

---

## Automated Scripts

### Create eDiscovery Case

```powershell
<#
.SYNOPSIS
    Creates eDiscovery case for agent content investigation

.EXAMPLE
    .\New-AgentDiscoveryCase.ps1 -CaseName "FINRA-2026-Q1" -Members @("legal@contoso.com")
#>

param(
    [Parameter(Mandatory=$true)]
    [string]$CaseName,
    [Parameter(Mandatory=$true)]
    [string[]]$Members
)

Write-Host "=== Create eDiscovery Case ===" -ForegroundColor Cyan

Connect-IPPSSession

$case = New-ComplianceCase -Name $CaseName -CaseType "eDiscovery"

foreach ($member in $Members) {
    Add-ComplianceCaseMember -Case $CaseName -Member $member
}

Write-Host "Case created: $CaseName" -ForegroundColor Green
Write-Host "Members: $($Members -join ', ')"

Disconnect-ExchangeOnline -Confirm:$false
```

### Create Content Search for Agent Data

```powershell
<#
.SYNOPSIS
    Creates content search for AI agent interactions

.EXAMPLE
    .\New-AgentContentSearch.ps1 -CaseName "FINRA-2026-Q1" -SearchName "Agent-Conversations"
#>

param(
    [Parameter(Mandatory=$true)]
    [string]$CaseName,
    [Parameter(Mandatory=$true)]
    [string]$SearchName,
    [string]$StartDate,
    [string]$EndDate
)

Write-Host "=== Create Agent Content Search ===" -ForegroundColor Cyan

Connect-IPPSSession

$query = 'kind:microsoftteams AND (from:"Copilot" OR subject:"Agent" OR body:"AI assistant")'

if ($StartDate -and $EndDate) {
    $query += " AND (date>=$StartDate AND date<=$EndDate)"
}

$search = New-ComplianceSearch -Name $SearchName `
    -Case $CaseName `
    -ContentMatchQuery $query `
    -ExchangeLocation All

Write-Host "Search created: $SearchName" -ForegroundColor Green
Write-Host "Query: $query"

# Start the search
Start-ComplianceSearch -Identity $SearchName
Write-Host "Search started. Check progress in Purview portal."

Disconnect-ExchangeOnline -Confirm:$false
```

---

## Validation Script

```powershell
<#
.SYNOPSIS
    Validates Control 1.19 - eDiscovery configuration

.EXAMPLE
    .\Validate-Control-1.19.ps1
#>

Write-Host "=== Control 1.19 Validation ===" -ForegroundColor Cyan

Connect-IPPSSession

# Check 1: eDiscovery cases
Write-Host "`n[Check 1] eDiscovery Cases" -ForegroundColor Cyan
$cases = Get-ComplianceCase
Write-Host "Active cases: $($cases.Count)"

# Check 2: Compliance searches
Write-Host "`n[Check 2] Compliance Searches" -ForegroundColor Cyan
$searches = Get-ComplianceSearch | Select-Object -First 5
$searches | ForEach-Object { Write-Host "  - $($_.Name): $($_.Status)" }

# Check 3: Holds
Write-Host "`n[Check 3] eDiscovery Holds" -ForegroundColor Cyan
Write-Host "[INFO] Check holds in Purview portal under each case"

Disconnect-ExchangeOnline -Confirm:$false

Write-Host "`n=== Validation Complete ===" -ForegroundColor Cyan
```

---

[Back to Control 1.19](../../../controls/pillar-1-security/1.19-ediscovery-for-agent-interactions.md) | [Portal Walkthrough](portal-walkthrough.md) | [Verification Testing](verification-testing.md) | [Troubleshooting](troubleshooting.md)
