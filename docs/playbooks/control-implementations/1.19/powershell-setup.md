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

## Complete Configuration Script

```powershell
<#
.SYNOPSIS
    Configures Control 1.19 - eDiscovery for Agent Interactions

.DESCRIPTION
    This script creates eDiscovery cases and content searches for AI agent
    interactions to support regulatory investigations.

.PARAMETER CaseName
    Name for the eDiscovery case

.PARAMETER Members
    Array of email addresses for case members

.PARAMETER SearchName
    Name for the content search

.PARAMETER StartDate
    Start date for search (optional)

.PARAMETER EndDate
    End date for search (optional)

.EXAMPLE
    .\Configure-Control-1.19.ps1 -CaseName "FINRA-2026-Q1" -Members @("legal@contoso.com") -SearchName "Agent-Conversations"

.NOTES
    Last Updated: January 2026
    Related Control: Control 1.19 - eDiscovery for Agent Interactions
#>

param(
    [Parameter(Mandatory=$true)]
    [string]$CaseName,

    [Parameter(Mandatory=$true)]
    [string[]]$Members,

    [Parameter(Mandatory=$true)]
    [string]$SearchName,

    [string]$StartDate,
    [string]$EndDate
)

try {
    # Connect to Security & Compliance
    Write-Host "Connecting to Security & Compliance Center..." -ForegroundColor Cyan
    Connect-IPPSSession

    Write-Host "Configuring Control 1.19: eDiscovery for Agent Interactions" -ForegroundColor Cyan

    # Step 1: Create eDiscovery case
    Write-Host "`n[Step 1] Creating eDiscovery case..." -ForegroundColor Yellow
    $existingCase = Get-ComplianceCase -Identity $CaseName -ErrorAction SilentlyContinue
    if ($existingCase) {
        Write-Host "  [EXISTS] Case already exists: $CaseName" -ForegroundColor Yellow
        $case = $existingCase
    } else {
        $case = New-ComplianceCase -Name $CaseName -CaseType "eDiscovery"
        Write-Host "  [CREATED] Case: $CaseName" -ForegroundColor Green
    }

    # Step 2: Add case members
    Write-Host "`n[Step 2] Adding case members..." -ForegroundColor Yellow
    foreach ($member in $Members) {
        try {
            Add-ComplianceCaseMember -Case $CaseName -Member $member -ErrorAction Stop
            Write-Host "  [ADDED] $member" -ForegroundColor Green
        } catch {
            if ($_.Exception.Message -like "*already a member*") {
                Write-Host "  [EXISTS] $member" -ForegroundColor Yellow
            } else {
                throw
            }
        }
    }

    # Step 3: Create content search
    Write-Host "`n[Step 3] Creating content search for agent interactions..." -ForegroundColor Yellow
    $query = 'kind:microsoftteams AND (from:"Copilot" OR subject:"Agent" OR body:"AI assistant")'

    if ($StartDate -and $EndDate) {
        $query += " AND (date>=$StartDate AND date<=$EndDate)"
    }

    $existingSearch = Get-ComplianceSearch -Identity $SearchName -ErrorAction SilentlyContinue
    if ($existingSearch) {
        Write-Host "  [EXISTS] Search already exists: $SearchName" -ForegroundColor Yellow
    } else {
        $search = New-ComplianceSearch -Name $SearchName `
            -Case $CaseName `
            -ContentMatchQuery $query `
            -ExchangeLocation All
        Write-Host "  [CREATED] Search: $SearchName" -ForegroundColor Green
        Write-Host "  Query: $query" -ForegroundColor Gray
    }

    # Step 4: Start the search
    Write-Host "`n[Step 4] Starting content search..." -ForegroundColor Yellow
    Start-ComplianceSearch -Identity $SearchName
    Write-Host "  Search started. Monitor progress in Purview portal." -ForegroundColor Green

    # Step 5: Validate configuration
    Write-Host "`n[Step 5] Validating configuration..." -ForegroundColor Yellow
    $validatedCase = Get-ComplianceCase -Identity $CaseName
    $validatedSearch = Get-ComplianceSearch -Identity $SearchName
    Write-Host "  Case status: $($validatedCase.Status)" -ForegroundColor Green
    Write-Host "  Search status: $($validatedSearch.Status)" -ForegroundColor Green

    Write-Host "`n[PASS] Control 1.19 configuration completed successfully" -ForegroundColor Green
}
catch {
    Write-Host "[FAIL] Error: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host "[INFO] Stack trace: $($_.ScriptStackTrace)" -ForegroundColor Yellow
    exit 1
}
finally {
    # Cleanup connections
    Disconnect-ExchangeOnline -Confirm:$false -ErrorAction SilentlyContinue
    Write-Host "`nDisconnected from Security & Compliance Center" -ForegroundColor Gray
}
```

---

[Back to Control 1.19](../../../controls/pillar-1-security/1.19-ediscovery-for-agent-interactions.md) | [Portal Walkthrough](portal-walkthrough.md) | [Verification Testing](verification-testing.md) | [Troubleshooting](troubleshooting.md)
