<#
.SYNOPSIS
    FSI-AgentGov Assessment Engine orchestrator.

.DESCRIPTION
    Runs collectors in sequence, scores 78 controls against zone thresholds,
    and generates a pre-filled assessment report with focused manual questionnaire.

.EXAMPLE
    .\run-assessment.ps1 -TenantId "abc-123" -Zone 2 -AuthMode Interactive -CustomerName "Contoso Financial" `
        -SubscriptionId "sub-id" -ResourceGroup "rg-sentinel" -WorkspaceName "sentinel-ws"
#>
[CmdletBinding()]
param(
    [Parameter(Mandatory)]
    [string] $TenantId,

    [Parameter(Mandatory)]
    [ValidateSet(1, 2, 3)]
    [int] $Zone,

    [Parameter(Mandatory)]
    [ValidateSet("Interactive", "ServicePrincipal")]
    [string] $AuthMode,

    [string] $ClientId,

    [SecureString] $ClientSecret,

    [Parameter(Mandatory)]
    [string] $CustomerName,

    [string] $ApprovedSitesCsv,

    [string[]] $SkipCollectors = @(),

    [string] $OutputDir = (Join-Path $PSScriptRoot "output"),

    [string] $SubscriptionId,

    [string] $ResourceGroup,

    [string] $WorkspaceName
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

# ── Timing ──────────────────────────────────────────────────────────────────
$script:StartTime = Get-Date

# ── Constants ───────────────────────────────────────────────────────────────
$Collectors = [ordered]@{
    PPAC       = @{ Script = "collectors\Collect-PPAC.ps1";       RequiresAuth = $true  }
    Graph      = @{ Script = "collectors\Collect-Graph.ps1";      RequiresAuth = $true  }
    Purview    = @{ Script = "collectors\Collect-Purview.ps1";    RequiresAuth = $true  }
    SharePoint = @{ Script = "collectors\Collect-SharePoint.ps1"; RequiresAuth = $true  }
    Sentinel   = @{ Script = "collectors\Collect-Sentinel.ps1";   RequiresAuth = $true  }
}

$MaturityLabels = @{
    0 = "Not Implemented"
    1 = "Baseline (25%)"
    2 = "Recommended (50%)"
    3 = "Advanced (75%)"
    4 = "Fully Regulated (100%)"
}

# ── Helper functions ────────────────────────────────────────────────────────

function Resolve-PythonPath {
    <#
    .SYNOPSIS
        Locate a usable Python 3 interpreter.
    #>
    foreach ($candidate in @("python3", "python", "py")) {
        try {
            $ver = & $candidate --version 2>&1
            if ($ver -match "Python 3") { return $candidate }
        } catch { }
    }
    throw "Python 3 is required but was not found. Install Python 3.10+ and ensure it is on PATH."
}

function Write-Banner {
    param([string] $Text)
    $line = "=" * 72
    Write-Host ""
    Write-Host $line -ForegroundColor Cyan
    Write-Host "  $Text" -ForegroundColor Cyan
    Write-Host $line -ForegroundColor Cyan
    Write-Host ""
}

function Write-CollectorStatus {
    param(
        [string] $Name,
        [string] $Status,
        [string] $Detail = ""
    )
    $color = switch ($Status) {
        "Running"  { "Yellow" }
        "Success"  { "Green" }
        "Partial"  { "DarkYellow" }
        "Failed"   { "Red" }
        "Skipped"  { "DarkGray" }
        default    { "White" }
    }
    $icon = switch ($Status) {
        "Running"  { "[~]" }
        "Success"  { "[+]" }
        "Partial"  { "[!]" }
        "Failed"   { "[X]" }
        "Skipped"  { "[-]" }
        default    { "[ ]" }
    }
    $msg = "$icon $($Name.PadRight(14)) $Status"
    if ($Detail) { $msg += "  — $Detail" }
    Write-Host $msg -ForegroundColor $color
}

# ── Parameter validation ────────────────────────────────────────────────────

Write-Banner "FSI-AgentGov Assessment Engine"

Write-Host "Tenant:       $TenantId"
Write-Host "Zone:         $Zone"
Write-Host "Auth Mode:    $AuthMode"
Write-Host "Customer:     $CustomerName"
Write-Host "Output:       $OutputDir"
Write-Host ""

if ($AuthMode -eq "ServicePrincipal") {
    if (-not $ClientId)     { throw "ClientId is required when AuthMode is ServicePrincipal." }
    if (-not $ClientSecret) { throw "ClientSecret is required when AuthMode is ServicePrincipal." }
}

if ("Sentinel" -notin $SkipCollectors) {
    if (-not $SubscriptionId)  { throw "SubscriptionId is required when the Sentinel collector is enabled. Use -SkipCollectors @('Sentinel') to skip." }
    if (-not $ResourceGroup)   { throw "ResourceGroup is required when the Sentinel collector is enabled." }
    if (-not $WorkspaceName)   { throw "WorkspaceName is required when the Sentinel collector is enabled." }
}

$Python = Resolve-PythonPath
Write-Host "Python:       $Python"
Write-Host ""

# ── Create output directory structure ───────────────────────────────────────

$CollectedDir = Join-Path $OutputDir "collected"
if (Test-Path $OutputDir) {
    Write-Host "Cleaning previous output..." -ForegroundColor DarkGray
    Remove-Item -Path $OutputDir -Recurse -Force
}
New-Item -ItemType Directory -Path $CollectedDir -Force | Out-Null
Write-Host "Output directory created: $OutputDir" -ForegroundColor DarkGray
Write-Host ""

# ── Run collectors ──────────────────────────────────────────────────────────

Write-Banner "Phase 1: Data Collection"

$collectorResults = @{}

foreach ($name in $Collectors.Keys) {
    if ($name -in $SkipCollectors) {
        Write-CollectorStatus -Name $name -Status "Skipped"
        $collectorResults[$name] = @{ ExitCode = -1; Status = "Skipped" }
        continue
    }

    $scriptPath = Join-Path $PSScriptRoot $Collectors[$name].Script

    if (-not (Test-Path $scriptPath)) {
        Write-CollectorStatus -Name $name -Status "Failed" -Detail "Script not found: $scriptPath"
        $collectorResults[$name] = @{ ExitCode = 2; Status = "Failed"; Detail = "Script not found" }
        continue
    }

    Write-CollectorStatus -Name $name -Status "Running"

    $collectorArgs = @{
        TenantId   = $TenantId
        AuthMode   = $AuthMode
        OutputFile = Join-Path $CollectedDir "$($name.ToLower()).json"
    }

    if ($AuthMode -eq "ServicePrincipal") {
        $collectorArgs.ClientId     = $ClientId
        $collectorArgs.ClientSecret = $ClientSecret
    }

    if ($name -eq "Sentinel") {
        $collectorArgs.SubscriptionId = $SubscriptionId
        $collectorArgs.ResourceGroup  = $ResourceGroup
        $collectorArgs.WorkspaceName  = $WorkspaceName
    }

    if ($name -eq "SharePoint" -and $ApprovedSitesCsv) {
        $collectorArgs.ApprovedSitesCsv = $ApprovedSitesCsv
    }

    try {
        & $scriptPath @collectorArgs
        $exitCode = $LASTEXITCODE
        if ($null -eq $exitCode) { $exitCode = 0 }

        switch ($exitCode) {
            0 {
                Write-CollectorStatus -Name $name -Status "Success"
                $collectorResults[$name] = @{ ExitCode = 0; Status = "Success" }
            }
            1 {
                Write-CollectorStatus -Name $name -Status "Partial" -Detail "Some data sources returned warnings"
                Write-Warning "Collector '$name' completed with partial results (exit code 1)."
                $collectorResults[$name] = @{ ExitCode = 1; Status = "Partial" }
            }
            default {
                Write-CollectorStatus -Name $name -Status "Failed" -Detail "Exit code $exitCode"
                Write-Error "Collector '$name' failed with exit code $exitCode." -ErrorAction Continue
                $collectorResults[$name] = @{ ExitCode = $exitCode; Status = "Failed" }
            }
        }
    }
    catch {
        Write-CollectorStatus -Name $name -Status "Failed" -Detail $_.Exception.Message
        Write-Error "Collector '$name' threw an exception: $($_.Exception.Message)" -ErrorAction Continue
        $collectorResults[$name] = @{ ExitCode = 2; Status = "Failed"; Detail = $_.Exception.Message }
    }
}

Write-Host ""

# ── Collector summary ───────────────────────────────────────────────────────

$successCount = ($collectorResults.Values | Where-Object { $_.ExitCode -eq 0 }).Count
$partialCount = ($collectorResults.Values | Where-Object { $_.ExitCode -eq 1 }).Count
$failedCount  = ($collectorResults.Values | Where-Object { $_.ExitCode -ge 2 }).Count
$skippedCount = ($collectorResults.Values | Where-Object { $_.ExitCode -eq -1 }).Count

Write-Host "Collection complete: $successCount succeeded, $partialCount partial, $failedCount failed, $skippedCount skipped" -ForegroundColor $(if ($failedCount -gt 0) { "Yellow" } else { "Green" })
Write-Host ""

# ── Phase 2: Scoring ───────────────────────────────────────────────────────

Write-Banner "Phase 2: Scoring Engine"

$manifestPath = Join-Path $PSScriptRoot "manifest\controls.json"
$scoresPath   = Join-Path $OutputDir "scores.json"

if (-not (Test-Path $manifestPath)) {
    throw "Controls manifest not found at: $manifestPath"
}

$scoreArgs = @(
    (Join-Path $PSScriptRoot "engine\score.py"),
    "--manifest", $manifestPath,
    "--collected", $CollectedDir,
    "--zone", $Zone,
    "--output", $scoresPath
)

Write-Host "Running: $Python engine\score.py --zone $Zone" -ForegroundColor DarkGray
& $Python @scoreArgs
if ($LASTEXITCODE -ne 0) {
    throw "Scoring engine failed with exit code $LASTEXITCODE."
}
Write-Host "Scores written to: $scoresPath" -ForegroundColor Green
Write-Host ""

# ── Phase 3: Report generation ──────────────────────────────────────────────

Write-Banner "Phase 3: Report Generation"

$reportArgs = @(
    (Join-Path $PSScriptRoot "engine\report.py"),
    "--scores", $scoresPath,
    "--manifest", $manifestPath,
    "--customer", $CustomerName,
    "--zone", $Zone,
    "--output-dir", $OutputDir
)

Write-Host "Running: $Python engine\report.py --customer `"$CustomerName`" --zone $Zone" -ForegroundColor DarkGray
& $Python @reportArgs
if ($LASTEXITCODE -ne 0) {
    throw "Report generator failed with exit code $LASTEXITCODE."
}
Write-Host "Reports written to: $OutputDir" -ForegroundColor Green
Write-Host ""

# ── Summary ─────────────────────────────────────────────────────────────────

Write-Banner "Assessment Complete"

if (Test-Path $scoresPath) {
    $scores = Get-Content $scoresPath -Raw | ConvertFrom-Json

    $totalControls = $scores.summary.total_controls
    $autoScored    = $scores.summary.auto_scored
    $needsManual   = $scores.summary.needs_manual
    $avgMaturity   = [math]::Round($scores.summary.average_maturity, 2)

    Write-Host "Customer:            $CustomerName"
    Write-Host "Zone:                $Zone"
    Write-Host "Total Controls:      $totalControls"
    Write-Host "Auto-scored:         $autoScored"
    Write-Host "Needs Manual Input:  $needsManual"
    Write-Host "Average Maturity:    $avgMaturity / 4.0"
    Write-Host ""

    Write-Host "Pillar Breakdown:" -ForegroundColor Cyan
    foreach ($pillarId in ($scores.summary.by_pillar.PSObject.Properties.Name | Sort-Object)) {
        $p = $scores.summary.by_pillar.$pillarId
        $pAvg = [math]::Round($p.average_maturity, 2)
        Write-Host "  Pillar $pillarId ($($p.pillar_name)): $pAvg / 4.0  ($($p.controls) controls)"
    }
    Write-Host ""
}

# Output files
Write-Host "Output Files:" -ForegroundColor Cyan
$outputFiles = Get-ChildItem -Path $OutputDir -Recurse -File
foreach ($f in $outputFiles) {
    $relPath = $f.FullName.Substring($OutputDir.Length + 1)
    $sizeKb  = [math]::Round($f.Length / 1024, 1)
    Write-Host "  $relPath ($sizeKb KB)"
}
Write-Host ""

# Elapsed time
$elapsed = (Get-Date) - $script:StartTime
Write-Host "Elapsed time: $($elapsed.ToString('hh\:mm\:ss'))" -ForegroundColor DarkGray
Write-Host ""
