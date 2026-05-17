# PowerShell Setup: Control 2.18 — Automated Conflict of Interest Testing

!!! warning "Read the FSI PowerShell baseline first"
    Before running any command in this playbook, read the [**PowerShell Authoring Baseline for FSI Implementations**](../../_shared/powershell-baseline.md). It is the canonical source for module version pinning, sovereign-cloud (GCC / GCC High / DoD) endpoints, mutation safety (`-WhatIf` / `SupportsShouldProcess`), Dataverse compatibility, and SHA-256 evidence emission. Snippets below show abbreviated patterns; the baseline is authoritative.

**Last Updated:** April 2026<br>
**Modules Required:** `Microsoft.Graph` (audit log queries), `Microsoft.PowerApps.Administration.PowerShell` (agent inventory), `ImportExcel` (reporting). Custom HTTP calls to the Copilot Studio evaluation endpoint use the agent's REST surface — no dedicated PowerShell module exists for evaluation runs as of April 2026.<br>
**Tenant Footprint:** Read-only against tenant data; writes only to the local evidence working directory and (optionally) to a configured SharePoint evidence library.

This playbook automates the **execution, evidence collection, and validation** layers of Control 2.18. The portal walkthrough remains the canonical place to *configure* test sets and graders; PowerShell is for running the suite, hashing the artefacts, and producing the compliance pack.

---

## 1. Prerequisites and Module Setup

```powershell
# Pin module versions per the FSI PowerShell baseline. Replace <version>
# placeholders with the versions approved by your Change Advisory Board.
$modules = @(
    @{ Name = 'Microsoft.Graph';                            Version = '<approved-version>' },
    @{ Name = 'Microsoft.PowerApps.Administration.PowerShell'; Version = '<approved-version>' },
    @{ Name = 'ImportExcel';                                Version = '<approved-version>' }
)

foreach ($m in $modules) {
    if (-not (Get-Module -ListAvailable -Name $m.Name | Where-Object Version -eq $m.Version)) {
        Install-Module -Name $m.Name `
            -RequiredVersion $m.Version `
            -Repository PSGallery `
            -Scope CurrentUser `
            -AllowClobber `
            -AcceptLicense
    }
}

# Sovereign-cloud guard — adjust per the baseline. Default below is Commercial.
$Cloud           = 'Commercial'   # Commercial | GCC | GCCHigh | DoD
$GraphEnv        = 'Global'       # Global | USGov | USGovDoD | China
$PowerAppsEndpt  = 'prod'         # prod | usgov | usgovhigh | dod | china

# Microsoft.PowerApps.Administration.PowerShell requires Windows PowerShell 5.1.
if ($PSVersionTable.PSEdition -ne 'Desktop' -and $RequirePowerAppsAdmin) {
    throw "Microsoft.PowerApps.Administration.PowerShell requires Windows PowerShell 5.1 (Desktop edition). Detected: $($PSVersionTable.PSEdition) $($PSVersionTable.PSVersion)."
}
```

---

## 2. Run the COI Evaluation Test Suite

This script invokes the Copilot Studio agent's evaluation endpoint (or the agent's published API) for each scenario in a test set, evaluates responses against per-scenario criteria, and produces a CSV result file plus a JSON detail file with hashes.

```powershell
<#
.SYNOPSIS
    Executes the automated COI test suite against a Copilot Studio agent.

.DESCRIPTION
    Loads JSON test cases from -TestSuitePath, calls the agent endpoint for
    each prompt, evaluates the response against per-scenario criteria, and
    writes time-stamped CSV (summary) + JSON (detail) artefacts with SHA-256
    hashes recorded in an evidence-register CSV.

    Read-only against tenant data. Writes only under -OutputPath.

    Supports -WhatIf for dry runs (no agent calls executed).

.PARAMETER AgentEndpoint
    The agent API or evaluation endpoint URL.

.PARAMETER ApiToken
    Bearer token for the agent endpoint. Source from Azure Key Vault — never
    embed in scripts. Service-principal auth is preferred for FINRA Rule 3110
    supervisory continuity.

.PARAMETER TestSuitePath
    Folder containing one JSON file per test case. Each JSON must include:
        category, name, prompt, criteria[]
    Each criterion is { type: contains|not_contains|regex|min_length, pattern: ... }.

.PARAMETER OutputPath
    Folder where CSV summary, JSON detail, and evidence register are written.

.EXAMPLE
    .\Invoke-COITests.ps1 -AgentEndpoint 'https://...' `
        -ApiToken (Get-Secret -Name 'coi-eval-token') `
        -TestSuitePath '.\test_cases' -OutputPath '.\evidence' -WhatIf
#>
[CmdletBinding(SupportsShouldProcess = $true, ConfirmImpact = 'Low')]
param(
    [Parameter(Mandatory)] [string] $AgentEndpoint,
    [Parameter(Mandatory)] [string] $ApiToken,
    [string] $TestSuitePath = '.\test_cases',
    [string] $OutputPath    = '.\evidence',
    [int]    $TimeoutSec    = 60
)

$ErrorActionPreference = 'Stop'
New-Item -ItemType Directory -Force -Path $OutputPath | Out-Null

function Test-Criterion {
    param($Response, $Criterion)
    switch ($Criterion.type) {
        'contains'     { return [bool]($Response -match [regex]::Escape($Criterion.pattern)) }
        'not_contains' { return [bool]($Response -notmatch [regex]::Escape($Criterion.pattern)) }
        'regex'        { return [bool]($Response -match $Criterion.pattern) }
        'min_length'   { return [bool]($Response.Length -ge [int]$Criterion.pattern) }
        default        { Write-Warning "Unknown criterion type: $($Criterion.type)"; return $true }
    }
}

$testFiles = Get-ChildItem -Path $TestSuitePath -Filter '*.json' -Recurse
if (-not $testFiles) { throw "No test cases found under $TestSuitePath" }

$results = foreach ($file in $testFiles) {
    $tc = Get-Content $file.FullName -Raw | ConvertFrom-Json
    Write-Verbose "Running $($tc.category)/$($tc.name)"

    if ($PSCmdlet.ShouldProcess($AgentEndpoint, "POST evaluation for $($tc.name)")) {
        try {
            $body = @{ message = $tc.prompt; context = $tc.context } | ConvertTo-Json -Depth 5
            $resp = Invoke-RestMethod -Uri $AgentEndpoint -Method Post `
                        -Headers @{ Authorization = "Bearer $ApiToken" } `
                        -Body $body -ContentType 'application/json' -TimeoutSec $TimeoutSec

            $violations = @()
            foreach ($c in $tc.criteria) {
                if (-not (Test-Criterion -Response $resp.message -Criterion $c)) {
                    $violations += $c.name
                }
            }

            [PSCustomObject]@{
                TestFile   = $file.Name
                Category   = $tc.category
                TestName   = $tc.name
                Passed     = ($violations.Count -eq 0)
                Violations = ($violations -join '; ')
                Response   = $resp.message
                TimestampUtc = (Get-Date).ToUniversalTime().ToString('o')
            }
        }
        catch {
            [PSCustomObject]@{
                TestFile   = $file.Name
                Category   = $tc.category
                TestName   = $tc.name
                Passed     = $false
                Violations = "ExecutionError: $($_.Exception.Message)"
                Response   = $null
                TimestampUtc = (Get-Date).ToUniversalTime().ToString('o')
            }
        }
    }
}

if (-not $results) {
    Write-Warning "Dry run (-WhatIf): no agent calls executed. Exiting."
    return
}

# Summary
$total  = $results.Count
$passed = ($results | Where-Object Passed).Count
$rate   = [math]::Round(($passed / $total) * 100, 1)
Write-Host ("=== COI Suite: {0}/{1} passed ({2}%) ===" -f $passed, $total, $rate)

# Persist artefacts
$stamp     = Get-Date -Format 'yyyyMMdd-HHmmss'
$summary   = Join-Path $OutputPath "Control-2.18_TestResults_$stamp.csv"
$detail    = Join-Path $OutputPath "Control-2.18_TestResultsDetail_$stamp.json"
$register  = Join-Path $OutputPath "Control-2.18_EvidenceRegister.csv"

$results | Select-Object TestFile, Category, TestName, Passed, Violations, TimestampUtc |
    Export-Csv -Path $summary -NoTypeInformation -Encoding UTF8
$results | ConvertTo-Json -Depth 6 | Out-File -FilePath $detail -Encoding UTF8

# Chain-of-custody hashes
$entries = foreach ($f in @($summary, $detail)) {
    $hash = (Get-FileHash -Path $f -Algorithm SHA256).Hash
    [PSCustomObject]@{
        FileName     = Split-Path $f -Leaf
        Sha256       = $hash
        SizeBytes    = (Get-Item $f).Length
        CapturedUtc  = (Get-Date).ToUniversalTime().ToString('o')
        Operator     = $env:USERNAME
        AgentEndpoint = $AgentEndpoint
    }
}
$entries | Export-Csv -Path $register -NoTypeInformation -Append -Encoding UTF8

Write-Host "Evidence written:`n  $summary`n  $detail`n  $register"

# Exit non-zero on failures so CI / Power Automate can detect regressions
if ($passed -lt $total) { exit 1 }
```

> **Token handling.** `-ApiToken` should be sourced from Azure Key Vault (`Get-AzKeyVaultSecret`) or an equivalent secret broker. Embedding a bearer token in a script file violates GLBA 501(b) Safeguards Rule expectations and is an audit finding.

---

## 3. Generate the COI Compliance Report

Aggregates the most recent N CSV exports into a single Markdown report suitable for Compliance and AI Risk Committee distribution.

```powershell
[CmdletBinding()]
param(
    [string] $EvidencePath = '.\evidence',
    [string] $ReportPath   = '.\reports',
    [int]    $LookbackRuns = 5
)

$ErrorActionPreference = 'Stop'
New-Item -ItemType Directory -Force -Path $ReportPath | Out-Null

$resultFiles = Get-ChildItem -Path $EvidencePath -Filter 'Control-2.18_TestResults_*.csv' |
    Sort-Object LastWriteTime -Descending | Select-Object -First $LookbackRuns
if (-not $resultFiles) { throw "No result files found under $EvidencePath" }

$all = $resultFiles | ForEach-Object { Import-Csv $_.FullName }
$byCategory = $all | Group-Object Category | ForEach-Object {
    $passed = ($_.Group | Where-Object { $_.Passed -eq 'True' }).Count
    [PSCustomObject]@{
        Category  = $_.Name
        Total     = $_.Count
        Passed    = $passed
        Failed    = $_.Count - $passed
        PassRate  = [math]::Round(($passed / $_.Count) * 100, 1)
    }
}

$failures = $all | Where-Object { $_.Passed -eq 'False' } | Select-Object -First 25

$report = @"
# Control 2.18 — COI Testing Compliance Report

**Generated (UTC):** $((Get-Date).ToUniversalTime().ToString('o'))
**Runs included:** $($resultFiles.Count) (most recent)
**Total test executions:** $($all.Count)

## Pass rate by category

| Category | Total | Passed | Failed | Pass Rate |
|----------|-------|--------|--------|-----------|
$(($byCategory | ForEach-Object { "| $($_.Category) | $($_.Total) | $($_.Passed) | $($_.Failed) | $($_.PassRate)% |" }) -join "`n")

## Recent failures (up to 25)

$(if ($failures) {
    ($failures | ForEach-Object { "- ``[$($_.Category)]`` $($_.TestName) — $($_.Violations)" }) -join "`n"
} else { "_None._" })

## Recommendation

$(if ($failures) {
    "Review failed cases with Compliance and the Agent Owner. Trigger remediation per WSPs and re-run the suite before promoting any further agent change."
} else {
    "All sampled runs pass. Maintain recurring execution and quarterly methodology review."
})

---

*Generated by Control-2.18 reporting script. Cross-reference with the evidence register for SHA-256 chain of custody.*
"@

$reportFile = Join-Path $ReportPath ("Control-2.18_ComplianceReport_{0}.md" -f (Get-Date -Format 'yyyyMMdd'))
$report | Out-File -FilePath $reportFile -Encoding UTF8
Write-Host "Report written: $reportFile"
```

---

## 4. Validate Control 2.18 Configuration (Read-Only)

This validator inventories agents in scope, confirms recent evaluation runs, and verifies evidence-register integrity. It performs **no writes** against tenant data.

```powershell
<#
.SYNOPSIS
    Read-only validation of Control 2.18 configuration and evidence.

.DESCRIPTION
    1. Inventories Copilot Studio / Power Platform agents tagged as
       in-scope for COI testing.
    2. Confirms a recent evaluation run exists per agent (within
       -MaxRunAgeDays).
    3. Recomputes SHA-256 hashes against the evidence register and reports
       drift.

    Returns a structured object suitable for piping to a dashboard or CI gate.
#>
[CmdletBinding()]
param(
    [string] $EvidencePath = '.\evidence',
    [int]    $MaxRunAgeDays = 35,
    [string[]] $InScopeAgentTags = @('coi-required')
)

$ErrorActionPreference = 'Stop'

# 1. Recent evaluation runs
$latest = Get-ChildItem -Path $EvidencePath -Filter 'Control-2.18_TestResults_*.csv' -ErrorAction SilentlyContinue |
    Sort-Object LastWriteTime -Descending | Select-Object -First 1
$recentRunOk = $latest -and ($latest.LastWriteTime -gt (Get-Date).AddDays(-$MaxRunAgeDays))

# 2. Evidence-register hash integrity
$register = Join-Path $EvidencePath 'Control-2.18_EvidenceRegister.csv'
$drift = @()
if (Test-Path $register) {
    Import-Csv $register | ForEach-Object {
        $path = Join-Path $EvidencePath $_.FileName
        if (Test-Path $path) {
            $current = (Get-FileHash -Path $path -Algorithm SHA256).Hash
            if ($current -ne $_.Sha256) {
                $drift += [PSCustomObject]@{
                    FileName       = $_.FileName
                    RegisteredHash = $_.Sha256
                    CurrentHash    = $current
                }
            }
        } else {
            $drift += [PSCustomObject]@{
                FileName       = $_.FileName
                RegisteredHash = $_.Sha256
                CurrentHash    = '<missing>'
            }
        }
    }
}

[PSCustomObject]@{
    LatestRunFile       = $latest.FullName
    LatestRunTimestamp  = $latest.LastWriteTime
    RecentRunOk         = [bool]$recentRunOk
    EvidenceRegister    = (Test-Path $register)
    HashDriftCount      = $drift.Count
    HashDriftDetail     = $drift
    InScopeAgentTags    = $InScopeAgentTags
    Cloud               = $Cloud
    GeneratedUtc        = (Get-Date).ToUniversalTime().ToString('o')
}
```

> **What this validator does not do.** It does not vouch for the **content** of the evaluation (that is the job of the graders and Compliance review). It confirms the *operational discipline* — that runs are happening on cadence and that artefacts have not been altered after the fact.

---

## 5. Operational Reminders

- **Mutation safety.** Every script in this playbook honours `-WhatIf` and `-Confirm` (`SupportsShouldProcess`). Run with `-WhatIf` first against any new agent endpoint.
- **No tenant writes.** This control's PowerShell footprint is read-only against tenant configuration. The only writes are local evidence files (and optionally a configured evidence library).
- **Service-principal execution.** Recurring runs must execute under a service principal owned by the Compliance or AI Governance function — not under a personal account. This is a FINRA Rule 3110 supervisory-continuity expectation.
- **Sovereign clouds.** Re-validate endpoints (`-Endpoint`, `-Environment`) against the [PowerShell Authoring Baseline](../../_shared/powershell-baseline.md) before running in GCC / GCC High / DoD tenants. Wrong endpoints produce **false-clean** results.
- **Evidence retention.** Move CSV / JSON / register files into the SharePoint Compliance Evidence Library on completion; do not leave Zone 3 evidence on a workstation longer than necessary.

---

[Back to Control 2.18](../../../controls/pillar-2-management/2.18-automated-conflict-of-interest-testing.md) | [Portal Walkthrough](portal-walkthrough.md) | [Verification & Testing](verification-testing.md) | [Troubleshooting](troubleshooting.md)
---

*Updated: May 2026 | Version: v1.6.2 | UI Verification Status: Current*
