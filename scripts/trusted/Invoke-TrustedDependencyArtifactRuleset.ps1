#requires -Version 7.0
[CmdletBinding(DefaultParameterSetName = "Plan", SupportsShouldProcess, ConfirmImpact = "Medium")]
param(
    [Parameter(ParameterSetName = "Plan")]
    [switch]$Plan,

    [Parameter(ParameterSetName = "Apply", Mandatory)]
    [switch]$Apply,

    [Parameter(ParameterSetName = "ReadBack", Mandatory)]
    [switch]$ReadBack,

    [Parameter(Mandatory)]
    [ValidatePattern("^[1-9][0-9]*$")]
    [Int64]$AppId,

    [Parameter(ParameterSetName = "Apply", Mandatory)]
    [ValidatePattern("^[0-9a-f]{64}$")]
    [string]$ExpectedLiveDigest,

    [Parameter(ParameterSetName = "Apply", Mandatory)]
    [ValidatePattern("^[0-9a-f]{64}$")]
    [string]$ExpectedIntendedRulesetDigest,

    [Parameter(ParameterSetName = "Apply", Mandatory)]
    [ValidatePattern("^[0-9a-f]{64}$")]
    [string]$ConfirmationToken,

    [Parameter(ParameterSetName = "ReadBack")]
    [ValidateRange(1, [Int32]::MaxValue)]
    [Int32]$ProbePullRequest,

    [Parameter(ParameterSetName = "ReadBack")]
    [ValidatePattern("^[0-9a-f]{40}$")]
    [string]$ProbeMergeGroupSha,

    [ValidatePattern("^[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+$")]
    [string]$Repository = "judeper/FSI-AgentGov",

    [ValidatePattern("^[A-Za-z0-9._/-]+$")]
    [string]$Branch = "main"
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$repoRoot = Split-Path -Parent (Split-Path -Parent $PSScriptRoot)
$planPath = Join-Path $repoRoot ".github\trusted-policy\trusted-dependency-artifact-ruleset.plan.json"
$modelPath = Join-Path $PSScriptRoot "trusted-dependency-ruleset.mjs"

if (!(Test-Path -LiteralPath $planPath)) { throw "Trusted ruleset plan not found: $planPath" }
if (!(Test-Path -LiteralPath $modelPath)) { throw "Trusted ruleset model not found: $modelPath" }

function ConvertTo-CompactJson {
    param([Parameter(Mandatory)]$Value)
    return ($Value | ConvertTo-Json -Depth 100 -Compress)
}

function ConvertFrom-ToolJson {
    param(
        [Parameter(Mandatory)][object[]]$Output,
        [Parameter(Mandatory)][string]$Operation
    )
    $text = ($Output | ForEach-Object { $_.ToString() }) -join "`n"
    if ([string]::IsNullOrWhiteSpace($text)) {
        throw "$Operation returned no JSON"
    }
    try {
        return $text | ConvertFrom-Json -Depth 100
    } catch {
        throw "$Operation returned invalid JSON"
    }
}

function Invoke-TrustedModel {
    param(
        [Parameter(Mandatory)][string]$Operation,
        [Parameter()][object]$InputObject,
        [Parameter()][string[]]$Arguments = @()
    )
    if ($PSBoundParameters.ContainsKey("InputObject")) {
        $inputJson = ConvertTo-CompactJson $InputObject
        $output = $inputJson | & node $modelPath $Operation @Arguments 2>&1
    } else {
        $output = & node $modelPath $Operation @Arguments 2>&1
    }
    $exitCode = $LASTEXITCODE
    if ($exitCode -ne 0) {
        throw "Trusted ruleset model '$Operation' failed (exit $exitCode)"
    }
    return ConvertFrom-ToolJson -Output $output -Operation "Trusted ruleset model '$Operation'"
}

function Invoke-GhJson {
    param(
        [Parameter(Mandatory)][string]$Endpoint,
        [ValidateSet("GET", "POST")][string]$Method = "GET",
        [Parameter()][object]$Body,
        [switch]$AllowNotFound,
        [switch]$Paginate
    )

    $arguments = @(
        "api",
        "-H", "Accept: application/vnd.github+json",
        "-H", "X-GitHub-Api-Version: 2026-03-10",
        "-X", $Method
    )
    if ($Paginate) {
        $arguments += @("--paginate", "--slurp")
    }
    $arguments += $Endpoint

    if ($PSBoundParameters.ContainsKey("Body")) {
        $bodyJson = ConvertTo-CompactJson $Body
        $output = $bodyJson | & gh @arguments --input - 2>&1
    } else {
        $output = & gh @arguments 2>&1
    }
    $exitCode = $LASTEXITCODE
    $text = ($output | ForEach-Object { $_.ToString() }) -join "`n"
    if ($exitCode -ne 0) {
        if ($AllowNotFound -and $text -match "HTTP 404|Not Found") {
            return $null
        }
        throw "gh api $Method $Endpoint failed (exit $exitCode)"
    }
    if ([string]::IsNullOrWhiteSpace($text)) {
        throw "gh api $Method $Endpoint returned no JSON"
    }
    try {
        return $text | ConvertFrom-Json -Depth 100
    } catch {
        throw "gh api $Method $Endpoint returned invalid JSON"
    }
}

function Get-LiveState {
    $repositoryState = Invoke-GhJson -Endpoint "repos/$Repository"
    if (
        $repositoryState.full_name -ne $Repository -or
        $repositoryState.owner.type -ne "User" -or
        $repositoryState.default_branch -ne $Branch
    ) {
        throw "Wrong repository, owner type, or default branch; refusing to continue"
    }

    $pages = Invoke-GhJson -Endpoint "repos/$Repository/rulesets?includes_parents=true&per_page=100" -Paginate
    $summaries = @()
    foreach ($page in @($pages)) {
        $summaries += @($page)
    }
    $rulesets = @()
    foreach ($summary in $summaries) {
        $rulesets += Invoke-GhJson -Endpoint "repos/$Repository/rulesets/$($summary.id)?includes_parents=true"
    }
    $branchProtection = Invoke-GhJson `
        -Endpoint "repos/$Repository/branches/$Branch/protection" `
        -AllowNotFound
    return [ordered]@{
        repository = $repositoryState
        branchProtection = $branchProtection
        rulesets = $rulesets
    }
}

function Get-DesiredRuleset {
    return Invoke-TrustedModel `
        -Operation "materialize" `
        -Arguments @("--plan", $planPath, "--app-id", $AppId.ToString())
}

function Get-Digest {
    param([Parameter(Mandatory)]$Value)
    return (Invoke-TrustedModel -Operation "digest" -InputObject $Value).digest
}

function Get-Snapshot {
    param([Parameter(Mandatory)]$LiveState)
    return Invoke-TrustedModel -Operation "snapshot" -InputObject $LiveState
}

function Get-ConfirmationToken {
    param(
        [Parameter(Mandatory)][string]$LiveDigest,
        [Parameter(Mandatory)][string]$IntendedRulesetDigest
    )
    $material = "$Repository|$Branch|$AppId|$LiveDigest|$IntendedRulesetDigest"
    $sha = [System.Security.Cryptography.SHA256]::Create()
    try {
        return (($sha.ComputeHash([System.Text.Encoding]::UTF8.GetBytes($material)) |
            ForEach-Object { $_.ToString("x2") }) -join "")
    } finally {
        $sha.Dispose()
    }
}

function Get-ManagedRulesets {
    param([Parameter(Mandatory)]$LiveState)
    return @(
        $LiveState.rulesets | Where-Object {
            $_.name -eq "trusted-dependency-artifact-app-gate" -and
            $_.source_type -eq "Repository"
        }
    )
}

function Assert-AppInstallation {
    $installation = Invoke-GhJson -Endpoint "repos/$Repository/installation" -AllowNotFound
    if ($null -eq $installation -or [Int64]$installation.app_id -ne $AppId) {
        throw "The requested dedicated GitHub App ID is not installed on $Repository"
    }
    if ([string]$installation.app_slug -eq "github-actions") {
        throw "GitHub Actions is not an acceptable authoritative check publisher"
    }
    if (
        [string]$installation.permissions.contents -ne "read" -or
        [string]$installation.permissions.checks -ne "write"
    ) {
        throw "The dedicated GitHub App installation lacks the required contents:read and checks:write permissions"
    }
}

function Assert-ApplyCapability {
    param([Parameter(Mandatory)]$LiveState)
    $actor = (& gh api user --jq ".login" 2>&1 | ForEach-Object { $_.ToString() }) -join ""
    $exitCode = $LASTEXITCODE
    if ($exitCode -ne 0 -or $actor.Trim() -ne "judeper") {
        throw "Apply requires the judeper owner account; no auth switching is performed"
    }
    if ($LiveState.repository.permissions.admin -ne $true) {
        throw "Apply requires confirmed repository administration permission"
    }
    if ($LiveState.repository.allow_squash_merge -ne $true) {
        throw "The planned linear-history ruleset requires squash merging to be enabled"
    }
}

function Assert-PostReadBack {
    param(
        [Parameter(Mandatory)]$Before,
        [Parameter(Mandatory)]$Desired
    )
    $after = Get-LiveState
    $managed = @(Get-ManagedRulesets $after)
    if ($managed.Count -ne 1) {
        throw "Read-back found $($managed.Count) managed rulesets; expected exactly one"
    }
    Assert-AppInstallation
    [void](Invoke-TrustedModel `
        -Operation "assert-readback" `
        -InputObject ([ordered]@{
            repository = $after.repository
            ruleset = $managed[0]
            branchProtection = $after.branchProtection
        }) `
        -Arguments @("--plan", $planPath, "--app-id", $AppId.ToString()))
    [void](Invoke-TrustedModel `
        -Operation "assert-unrelated-preserved" `
        -InputObject ([ordered]@{
            before = $Before
            after = $after
            managedRulesetName = $Desired.name
        }))

    $mergeQueueRules = @(
        $after.rulesets | Where-Object {
            $_.enforcement -eq "active" -and
            @($_.rules | Where-Object { $_.type -eq "merge_queue" }).Count -gt 0
        }
    )
    if ($mergeQueueRules.Count -gt 0 -and [string]::IsNullOrWhiteSpace($ProbeMergeGroupSha)) {
        throw "An active merge queue needs an exact merge-group SHA probe before this gate can be declared verified"
    }
    if (![string]::IsNullOrWhiteSpace($ProbeMergeGroupSha)) {
        $mergeRuns = Invoke-GhJson -Endpoint "repos/$Repository/commits/$ProbeMergeGroupSha/check-runs?per_page=100"
        [void](Invoke-TrustedModel `
            -Operation "assert-expected-source-check" `
            -InputObject ([ordered]@{
                checkRuns = $mergeRuns.check_runs
                targetSha = $ProbeMergeGroupSha
                appId = $AppId
                checkName = "trusted-dependency-artifact"
            }))
    }
    if ($ProbePullRequest -gt 0) {
        $pull = Invoke-GhJson -Endpoint "repos/$Repository/pulls/$ProbePullRequest"
        $headSha = [string]$pull.head.sha
        $runs = Invoke-GhJson -Endpoint "repos/$Repository/commits/$headSha/check-runs?per_page=100"
        [void](Invoke-TrustedModel `
            -Operation "assert-expected-source-check" `
            -InputObject ([ordered]@{
                checkRuns = $runs.check_runs
                targetSha = $headSha
                appId = $AppId
                checkName = "trusted-dependency-artifact"
            }))
    }
    return $after
}

[void](Invoke-TrustedModel -Operation "validate-plan" -Arguments @("--plan", $planPath))
$live = Get-LiveState
$snapshot = Get-Snapshot $live
$desired = Get-DesiredRuleset
$intendedRulesetDigest = Get-Digest $desired
$confirmation = Get-ConfirmationToken `
    -LiveDigest $snapshot.digest `
    -IntendedRulesetDigest $intendedRulesetDigest

if (!$Apply -and !$ReadBack) {
    [ordered]@{
        mode = "plan-only"
        remoteWrite = $false
        planState = "planned-not-applied"
        repository = $Repository
        branch = $Branch
        appId = $AppId
        liveDigest = $snapshot.digest
        intendedRulesetDigest = $intendedRulesetDigest
        confirmationToken = $confirmation
        existingManagedRulesets = @(Get-ManagedRulesets $live).Count
        warning = "No remote setting was changed. The gate remains BLOCKED and non-enforced."
    } | ConvertTo-Json -Depth 10
    return
}

if ($ReadBack) {
    [void](Assert-PostReadBack -Before $live -Desired $desired)
    [ordered]@{
        mode = "read-back"
        verified = $true
        repository = $Repository
        branch = $Branch
        appId = $AppId
        proof = "Expected-source App binding and every planned ruleset field matched. Unrelated protection state was not changed by this operation."
    } | ConvertTo-Json -Depth 10
    return
}

Assert-ApplyCapability $live
Assert-AppInstallation
if ($ExpectedLiveDigest -ne $snapshot.digest) {
    throw "Live repository security state drifted; generate a new plan before applying"
}
if ($ExpectedIntendedRulesetDigest -ne $intendedRulesetDigest) {
    throw "Intended ruleset digest does not match the reviewed plan"
}
if ($ConfirmationToken -ne $confirmation) {
    throw "Confirmation token does not bind this repository, live state, App ID, and intent"
}
if (@(Get-ManagedRulesets $live).Count -ne 0) {
    throw "A managed ruleset already exists; this create-only script will not PUT or replace remote state"
}

if (!$PSCmdlet.ShouldProcess("$Repository/$Branch", "create the planned expected-source GitHub App ruleset")) {
    [ordered]@{
        mode = "what-if"
        remoteWrite = $false
        warning = "No remote setting was changed. The gate remains BLOCKED and non-enforced."
    } | ConvertTo-Json -Depth 10
    return
}

[void](Invoke-GhJson -Endpoint "repos/$Repository/rulesets" -Method "POST" -Body $desired)
[void](Assert-PostReadBack -Before $live -Desired $desired)
[ordered]@{
    mode = "apply"
    verified = $true
    repository = $Repository
    branch = $Branch
    appId = $AppId
    proof = "Read-back matched the dedicated App source, strict required check, reviews, CODEOWNERS, conversation resolution, force-push/deletion block, linear history, and no bypass actors."
} | ConvertTo-Json -Depth 10
