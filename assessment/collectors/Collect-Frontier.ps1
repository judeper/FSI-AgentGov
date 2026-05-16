<#
.SYNOPSIS
    Facilitator-led frontier readiness collector for FSI Agent Governance assessment.

.DESCRIPTION
    Reads the frontier-readiness.json manifest and collects answers to the 25 readiness
    questions via facilitator prompting (interactive mode) or a pre-recorded answers file
    (batch mode for tests and automation).

    Outputs frontier.json consumed by the assessment scoring engine (score_frontier.py).
    No Microsoft 365 API calls are made — this collector is entirely facilitator-driven.

.PARAMETER OutputFile
    Mandatory. Path where the collected frontier.json will be written.

.PARAMETER ManifestPath
    Path to frontier-readiness.json. Defaults to the sibling manifest folder
    (assessment\manifest\frontier-readiness.json relative to this script).

.PARAMETER InputFile
    Optional. Path to a pre-recorded answers JSON file. Activates batch (non-interactive)
    mode. Expected shape:
      { "facilitator": "...", "answers": { "Q01": { "value": "yes", ... }, ... } }

.PARAMETER Facilitator
    Optional. Facilitator name recorded in output metadata. When provided alongside
    -InputFile, overrides the InputFile's facilitator field.

.PARAMETER TenantId
    Accepted for orchestrator parameter-passthrough compatibility; ignored by this collector.

.PARAMETER AuthMode
    Accepted for orchestrator parameter-passthrough compatibility; ignored by this collector.

.PARAMETER ClientId
    Accepted for orchestrator parameter-passthrough compatibility; ignored by this collector.

.PARAMETER ClientSecret
    Accepted for orchestrator parameter-passthrough compatibility; ignored by this collector.

.OUTPUTS
    frontier.json — Structured JSON with _metadata block and per-question answers.

.NOTES
    Part of the FSI Agent Governance Assessment Engine — Frontier Readiness Collector.
    Exit codes: 0 = success, 1 = session aborted or partial, 2 = fatal error.
    Version: 1.0.0
#>

#Requires -Version 7.0

[CmdletBinding(SupportsShouldProcess)]
param(
    [Parameter(Mandatory)]
    [string] $OutputFile,

    [string] $ManifestPath = (Join-Path $PSScriptRoot '..\manifest\frontier-readiness.json'),

    [string] $InputFile,

    [string] $Facilitator,

    # Accepted for orchestrator splatting compatibility — not used by this collector.
    [string] $TenantId,
    [string] $AuthMode,
    [string] $ClientId,
    [SecureString] $ClientSecret
)

$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest

# ─── Tracking arrays ──────────────────────────────────────────────────────────
$script:Warnings = [System.Collections.Generic.List[string]]::new()
$script:Errors   = [System.Collections.Generic.List[string]]::new()
$startTime       = [datetime]::UtcNow

# ─── Helper functions ─────────────────────────────────────────────────────────

function Write-Status {
    [CmdletBinding()]
    param(
        [string] $Message,
        [ValidateSet('Info', 'Success', 'Warning', 'Error')]
        [string] $Level = 'Info'
    )
    $color = switch ($Level) {
        'Success' { 'Green'  }
        'Warning' { 'Yellow' }
        'Error'   { 'Red'    }
        default   { 'Cyan'   }
    }
    Write-Host $Message -ForegroundColor $color
}

function Get-LevelLabel {
    [CmdletBinding()]
    param([int] $Level)
    switch ($Level) {
        100 { '100 (Initial)'     }
        200 { '200 (Repeatable)'  }
        300 { '300 (Defined)'     }
        400 { '400 (Capable)'     }
        500 { '500 (Optimized)'   }
        default { $Level.ToString() }
    }
}

# ─── Load and validate manifest ───────────────────────────────────────────────
if (-not (Test-Path $ManifestPath)) {
    Write-Status "Manifest not found: $ManifestPath" -Level Error
    $script:Errors.Add("Manifest not found: $ManifestPath")
    exit 2
}

$manifest = Get-Content -Path $ManifestPath -Raw -Encoding UTF8 | ConvertFrom-Json

$manifestVersion = $manifest.version
$questions       = $manifest.questions

if ($null -eq $questions -or $questions.Count -eq 0) {
    Write-Status "Manifest contains no questions: $ManifestPath" -Level Error
    $script:Errors.Add("Manifest contains no questions.")
    exit 2
}

$totalQuestions = $questions.Count
Write-Status "Loaded manifest v$manifestVersion — $totalQuestions questions." -Level Info

# Build driver name lookup from manifest
$driverNames = @{}
foreach ($driver in $manifest.drivers) {
    $driverNames[$driver.id] = $driver.name
}

# ─── Collect answers ──────────────────────────────────────────────────────────
$answers  = [ordered]@{}
$mode     = 'interactive'
$aborted  = $false

# Resolve facilitator value: param takes precedence over InputFile field
$facilitatorValue = if ($PSBoundParameters.ContainsKey('Facilitator') -and -not [string]::IsNullOrWhiteSpace($Facilitator)) {
    $Facilitator
} else {
    $null
}

if ($PSBoundParameters.ContainsKey('InputFile')) {

    # ── Batch / non-interactive mode ──────────────────────────────────────────
    $mode = 'batch'

    if (-not (Test-Path $InputFile)) {
        Write-Status "InputFile not found: $InputFile" -Level Error
        $script:Errors.Add("InputFile not found: $InputFile")
        exit 2
    }

    $inputData = Get-Content -Path $InputFile -Raw -Encoding UTF8 | ConvertFrom-Json

    # InputFile facilitator only applies when the param was not supplied
    if ($null -eq $facilitatorValue -and
        $inputData.PSObject.Properties.Name -contains 'facilitator' -and
        -not [string]::IsNullOrWhiteSpace($inputData.facilitator)) {
        $facilitatorValue = $inputData.facilitator
    }

    # Index the input answers by question_id
    $inputAnswers = @{}
    if ($inputData.PSObject.Properties.Name -contains 'answers') {
        foreach ($prop in $inputData.answers.PSObject.Properties) {
            $inputAnswers[$prop.Name] = $prop.Value
        }
    }

    foreach ($q in $questions) {
        $qId        = $q.question_id
        $answerEntry = $null

        if ($inputAnswers.ContainsKey($qId)) {
            $raw      = $inputAnswers[$qId]
            $rawValue = if ($raw.PSObject.Properties.Name -contains 'value') { $raw.value } else { $null }

            # Validate value per answer_format
            switch ($q.answer_format) {
                'yes_no_partial' {
                    $allowed = @('yes', 'partial', 'no')
                    if ($null -ne $rawValue -and $rawValue -notin $allowed) {
                        Write-Status "Invalid value '$rawValue' for $qId — expected yes/partial/no/null." -Level Error
                        $script:Errors.Add("Invalid value '$rawValue' for $qId.")
                        exit 2
                    }
                }
                'scale_1_5' {
                    if ($null -ne $rawValue) {
                        $intVal = $rawValue -as [int]
                        if ($null -eq $intVal -or $intVal -lt 1 -or $intVal -gt 5) {
                            Write-Status "Invalid value '$rawValue' for $qId — expected integer 1-5 or null." -Level Error
                            $script:Errors.Add("Invalid scale value '$rawValue' for $qId.")
                            exit 2
                        }
                        $rawValue = $intVal
                    }
                }
                'text' {
                    # Any string or null is valid.
                }
            }

            $evidenceNote = if ($raw.PSObject.Properties.Name -contains 'evidence_note') { $raw.evidence_note } else { $null }
            $respondent   = if ($raw.PSObject.Properties.Name -contains 'respondent')    { $raw.respondent   } else { $null }

            $answerEntry = [ordered]@{
                value         = $rawValue
                evidence_note = $evidenceNote
                respondent    = $respondent
            }
        }
        else {
            # Missing from InputFile — record as skipped
            $script:Warnings.Add("No answer for $qId in InputFile — recorded as skipped.")
            $answerEntry = [ordered]@{
                value         = $null
                evidence_note = $null
                respondent    = $null
            }
        }

        $answers[$qId] = $answerEntry
    }

    Write-Status "Batch mode: loaded $($answers.Count) answers from InputFile." -Level Success
}
else {

    # ── Interactive / facilitator-led mode ────────────────────────────────────
    Write-Status '=== FSI Frontier Readiness Assessment — Facilitator Session ===' -Level Info
    Write-Status "Answer each question. Type 'q' to quit, 's' to skip a question." -Level Info

    $questionIndex = 0

    foreach ($q in $questions) {
        $questionIndex++
        $qId        = $q.question_id
        $driverName = if ($driverNames.ContainsKey($q.driver)) { $driverNames[$q.driver] } else { $q.driver }
        $levelLabel = Get-LevelLabel -Level $q.level

        Write-Host ''
        Write-Host ('=' * 64) -ForegroundColor DarkGray
        Write-Host "[$qId / $totalQuestions]  Driver: $driverName  Level: $levelLabel" -ForegroundColor White
        Write-Host ('-' * 64) -ForegroundColor DarkGray
        Write-Host "Q: $($q.question_text)" -ForegroundColor Yellow
        Write-Host ''
        Write-Host "FSI context: $($q.fsi_context)" -ForegroundColor Gray
        Write-Host ''

        $promptText = switch ($q.answer_format) {
            'yes_no_partial' { 'Answer (y = yes, p = partial, n = no, s = skip, q = quit)' }
            'scale_1_5'      { 'Answer (1-5 scale, s = skip, q = quit)'                    }
            'text'           { 'Answer (free text, s = skip, q = quit)'                    }
            default          { 'Answer (s = skip, q = quit)'                               }
        }

        $answerValue = $null
        $inputValid  = $false

        while (-not $inputValid) {
            $raw = (Read-Host $promptText).Trim()

            if ($raw -eq 'q') {
                Write-Status 'Session aborted by facilitator.' -Level Warning
                $aborted = $true
                break
            }

            switch ($q.answer_format) {
                'yes_no_partial' {
                    switch ($raw.ToLower()) {
                        { $_ -in @('y', 'yes')     } { $answerValue = 'yes';     $inputValid = $true }
                        { $_ -in @('p', 'partial') } { $answerValue = 'partial'; $inputValid = $true }
                        { $_ -in @('n', 'no')      } { $answerValue = 'no';      $inputValid = $true }
                        { $_ -in @('s', 'skip')    } { $answerValue = $null;     $inputValid = $true }
                        default { Write-Host "  Enter y, p, n, s, or q." -ForegroundColor Red }
                    }
                }
                'scale_1_5' {
                    if ($raw -in @('s', 'skip')) {
                        $answerValue = $null
                        $inputValid  = $true
                    }
                    else {
                        $intVal = $raw -as [int]
                        if ($null -ne $intVal -and $intVal -ge 1 -and $intVal -le 5) {
                            $answerValue = $intVal
                            $inputValid  = $true
                        }
                        else {
                            Write-Host "  Enter a number 1-5, s, or q." -ForegroundColor Red
                        }
                    }
                }
                'text' {
                    $answerValue = if ($raw -in @('s', 'skip')) { $null } else { $raw }
                    $inputValid  = $true
                }
                default {
                    $answerValue = $null
                    $inputValid  = $true
                }
            }
        }

        if ($aborted) { break }

        # Optional evidence note and respondent (only when a real answer was given)
        $evidenceNote = $null
        $respondent   = $null

        if ($null -ne $answerValue) {
            $noteRaw = (Read-Host 'Evidence note (Enter to skip)').Trim()
            if ($noteRaw -ne '') { $evidenceNote = $noteRaw }

            $respRaw = (Read-Host 'Respondent (Enter to skip)').Trim()
            if ($respRaw -ne '') { $respondent = $respRaw }
        }

        $answers[$qId] = [ordered]@{
            value         = $answerValue
            evidence_note = $evidenceNote
            respondent    = $respondent
        }
    }

    if ($aborted) {
        Write-Status 'Writing partial results before exit...' -Level Warning
    }
}

# ─── Write output JSON ────────────────────────────────────────────────────────
$endTime     = [datetime]::UtcNow
$durationMin = [int][math]::Round(($endTime - $startTime).TotalMinutes)

$outputDir = Split-Path -Path $OutputFile -Parent
if (-not [string]::IsNullOrWhiteSpace($outputDir) -and -not (Test-Path $outputDir)) {
    New-Item -ItemType Directory -Path $outputDir -Force | Out-Null
}

$result = [ordered]@{
    _metadata = [ordered]@{
        collector_version        = '1.0.0'
        timestamp                = $endTime.ToString('o')
        facilitator              = $facilitatorValue
        session_duration_minutes = $durationMin
        mode                     = $mode
        manifest_version         = $manifestVersion
        warnings                 = @($script:Warnings)
        errors                   = @($script:Errors)
    }
    answers   = $answers
}

$json = $result | ConvertTo-Json -Depth 10 -Compress:$false
[System.IO.File]::WriteAllText($OutputFile, $json, (New-Object System.Text.UTF8Encoding $false))
Write-Status "Output written to $OutputFile" -Level Success

# ─── Exit code ────────────────────────────────────────────────────────────────
if ($aborted)                  { exit 1 }
if ($script:Errors.Count -gt 0) { exit 1 }
exit 0
