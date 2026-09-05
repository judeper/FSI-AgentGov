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

    [Parameter(ParameterSetName = "Apply", Mandatory)]
    [Parameter(ParameterSetName = "ReadBack", Mandatory)]
    [ValidateRange(1, [Int32]::MaxValue)]
    [Int32]$ProbePullRequest,

    [Parameter(ParameterSetName = "Apply", Mandatory)]
    [Parameter(ParameterSetName = "ReadBack", Mandatory)]
    [ValidateRange(1, [Int32]::MaxValue)]
    [Int32]$SpoofProbePullRequest,

    [Parameter(ParameterSetName = "Apply")]
    [Parameter(ParameterSetName = "ReadBack")]
    [ValidatePattern("^[0-9a-f]{40}$")]
    [string]$ProbeMergeGroupSha,

    [Parameter()]
    [ValidateNotNullOrEmpty()]
    [string]$AppPrivateKeyPath,

    [ValidatePattern("^[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+$")]
    [string]$Repository = "judeper/FSI-AgentGov",

    [ValidatePattern("^[A-Za-z0-9._/-]+$")]
    [string]$Branch = "main"
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$repoRoot = Split-Path -Parent (Split-Path -Parent $PSScriptRoot)
$planPath = Join-Path $repoRoot ".github\trusted-policy\trusted-dependency-artifact-ruleset.plan.json"
$contractPath = Join-Path $repoRoot ".github\trusted-policy\trusted-dependency-artifact-app-contract.json"
$modelPath = Join-Path $PSScriptRoot "trusted-dependency-ruleset.mjs"
$jwtModelPath = Join-Path $PSScriptRoot "github-app-jwt.mjs"

if (!(Test-Path -LiteralPath $planPath)) { throw "Trusted ruleset plan not found: $planPath" }
if (!(Test-Path -LiteralPath $contractPath)) { throw "GitHub App contract not found: $contractPath" }
if (!(Test-Path -LiteralPath $modelPath)) { throw "Trusted ruleset model not found: $modelPath" }
if (!(Test-Path -LiteralPath $jwtModelPath)) { throw "GitHub App JWT helper not found: $jwtModelPath" }
if ($Repository -ne "judeper/FSI-AgentGov" -or $Branch -ne "main") {
    throw "This operator is permanently bound to judeper/FSI-AgentGov main"
}

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

function Get-OwnerIdentity {
    $output = & gh api user --jq "{login:.login,id:.id}" 2>&1
    $exitCode = $LASTEXITCODE
    if ($exitCode -ne 0) {
        throw "owner GitHub authentication failed"
    }
    return ConvertFrom-ToolJson -Output $output -Operation "owner identity"
}

function Assert-OwnerAuthentication {
    $identity = Get-OwnerIdentity
    if ([string]$identity.login -ne "judeper") {
        throw "owner authentication must resolve to judeper; App credentials are not accepted for owner operations"
    }
    return $identity
}

function Get-AppJwt {
    $keyPath = $AppPrivateKeyPath
    if ([string]::IsNullOrWhiteSpace($keyPath)) {
        $keyPath = $env:GITHUB_APP_PRIVATE_KEY_PATH
    }
    if (
        [string]::IsNullOrWhiteSpace($keyPath) -and
        [string]::IsNullOrWhiteSpace($env:GITHUB_APP_PRIVATE_KEY)
    ) {
        throw "App verification requires GITHUB_APP_PRIVATE_KEY_PATH or GITHUB_APP_PRIVATE_KEY at runtime"
    }
    if ($keyPath -and !(Test-Path -LiteralPath $keyPath -PathType Leaf)) {
        throw "App private key path is unavailable"
    }
    if ($keyPath) {
        $resolvedKeyPath = (Resolve-Path -LiteralPath $keyPath).Path
        $resolvedRepoRoot = (Resolve-Path -LiteralPath $repoRoot).Path.TrimEnd("\") + "\"
        if ($resolvedKeyPath.StartsWith($resolvedRepoRoot, [System.StringComparison]::OrdinalIgnoreCase)) {
            throw "App private key must be outside the repository"
        }
    }

    $hadPath = Test-Path Env:GITHUB_APP_PRIVATE_KEY_PATH
    $savedPath = $env:GITHUB_APP_PRIVATE_KEY_PATH
    try {
        if ($AppPrivateKeyPath) {
            $env:GITHUB_APP_PRIVATE_KEY_PATH = $AppPrivateKeyPath
        }
        $output = & node $jwtModelPath --app-id $AppId.ToString() 2>&1
        $exitCode = $LASTEXITCODE
        if ($exitCode -ne 0) {
            throw "GitHub App JWT generation failed"
        }
        $jwt = (($output | ForEach-Object { $_.ToString() }) -join "").Trim()
        if ($jwt -notmatch '^[^.]+\.[^.]+\.[^.]+$') {
            throw "GitHub App JWT generation returned an invalid token"
        }
        return $jwt
    } finally {
        if ($hadPath) {
            $env:GITHUB_APP_PRIVATE_KEY_PATH = $savedPath
        } else {
            Remove-Item Env:GITHUB_APP_PRIVATE_KEY_PATH -ErrorAction SilentlyContinue
        }
    }
}

function Invoke-AppJson {
    param(
        [Parameter(Mandatory)][string]$Endpoint,
        [Parameter(Mandatory)][string]$Jwt
    )
    $apiUrl = [string]($env:GITHUB_API_URL)
    if ([string]::IsNullOrWhiteSpace($apiUrl)) { $apiUrl = "https://api.github.com" }
    $uri = "$($apiUrl.TrimEnd('/'))/$Endpoint"
    $headers = @{
        Accept = "application/vnd.github+json"
        "X-GitHub-Api-Version" = "2026-03-10"
        Authorization = "Bearer $Jwt"
        "User-Agent" = "trusted-dependency-artifact-ruleset"
    }
    try {
        return Invoke-RestMethod -Uri $uri -Method Get -Headers $headers -ErrorAction Stop
    } catch {
        throw "GitHub App GET $Endpoint failed"
    }
}

function Get-AppContract {
    try {
        $contract = Get-Content -LiteralPath $contractPath -Raw | ConvertFrom-Json -Depth 100
    } catch {
        throw "GitHub App contract is unreadable"
    }
    if ([int]$contract.schemaVersion -ne 2) {
        throw "GitHub App contract schema version is unsupported"
    }
    return $contract
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
        [ValidateSet("GET", "POST", "DELETE")][string]$Method = "GET",
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
        if ($Method -eq "DELETE") { return $null }
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
        -Endpoint "repos/$Repository/branches/$Branch/protection"
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

function Assert-DesiredAppBinding {
    param([Parameter(Mandatory)]$Desired)
    $statusRules = @(
        $Desired.rules | Where-Object { $_.type -eq "required_status_checks" }
    )
    if (
        $statusRules.Count -ne 1 -or
        @($statusRules[0].parameters.required_status_checks).Count -ne 1 -or
        [Int64]$statusRules[0].parameters.required_status_checks[0].integration_id -ne $AppId
    ) {
        throw "materialized ruleset integration_id does not match the dedicated App ID"
    }
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
            (
                [string]::IsNullOrWhiteSpace([string]$_.source_type) -or
                $_.source_type -eq "Repository"
            )
        }
    )
}

function Assert-AppInstallation {
    param([Parameter(Mandatory)][string]$Jwt)

    $contract = Get-AppContract
    $app = Invoke-AppJson -Endpoint "app" -Jwt $Jwt
    if ([Int64]$app.id -ne $AppId -or [string]$app.slug -eq "github-actions") {
        throw "App JWT identity does not match the requested dedicated GitHub App"
    }

    $installation = Invoke-AppJson -Endpoint "repos/$Repository/installation" -Jwt $Jwt
    if ($null -eq $installation -or [Int64]$installation.app_id -ne $AppId) {
        throw "The dedicated GitHub App is not installed on $Repository"
    }
    [void](Invoke-TrustedModel `
        -Operation "assert-app-installation" `
        -InputObject ([ordered]@{
            app = $app
            installation = $installation
            contract = $contract
            appId = $AppId
            repository = $Repository
        }))
    if (
        [string]$installation.target_type -ne "User" -or
        [string]$installation.account.login -ne "judeper" -or
        [string]$installation.repository_selection -ne "selected"
    ) {
        throw "The dedicated GitHub App installation is not scoped to the repository owner"
    }

    $expectedPermissions = @{}
    foreach ($property in @($contract.allowedRepositoryPermissions.PSObject.Properties)) {
        $expectedPermissions[$property.Name] = [string]$property.Value
    }
    if ([bool]$contract.mergeQueue.enabledByThisPlan) {
        $expectedPermissions[[string]$contract.mergeQueue.permission] = "read"
    }
    $actualPermissions = @{}
    foreach ($property in @($installation.permissions.PSObject.Properties)) {
        if ($null -ne $property.Value) {
            $actualPermissions[$property.Name] = [string]$property.Value
        }
    }
    foreach ($name in $expectedPermissions.Keys) {
        if ($actualPermissions[$name] -ne $expectedPermissions[$name]) {
            throw "The dedicated GitHub App permission '$name' is not '$($expectedPermissions[$name])'"
        }
    }
    foreach ($name in $actualPermissions.Keys) {
        if (!$expectedPermissions.ContainsKey($name)) {
            throw "The dedicated GitHub App has an unapproved repository permission '$name'"
        }
    }

    $expectedEvents = @($contract.requiredWebhookEvents | ForEach-Object { [string]$_ })
    if ([bool]$contract.mergeQueue.enabledByThisPlan) {
        $expectedEvents += @($contract.mergeQueue.events | ForEach-Object { [string]$_ })
    }
    $actualEvents = @($installation.events | ForEach-Object { [string]$_ })
    $eventDifferences = @(Compare-Object ($expectedEvents | Sort-Object) ($actualEvents | Sort-Object) -SyncWindow 0)
    if ($eventDifferences.Count -gt 0) {
        throw "The dedicated GitHub App webhook event contract does not match"
    }
    if ($installation.PSObject.Properties.Name -contains "repositories") {
        $repositories = @($installation.repositories)
        if (
            $repositories.Count -ne 1 -or
            [string]$repositories[0].full_name -ne $Repository
        ) {
            throw "The dedicated GitHub App installation is not limited to the target repository"
        }
    }
    return $installation
}

function Assert-ApplyCapability {
    param([Parameter(Mandatory)]$LiveState)
    $ownerIdentity = Assert-OwnerAuthentication
    [void](Invoke-TrustedModel `
        -Operation "assert-owner" `
        -InputObject ([ordered]@{
            login = $ownerIdentity.login
            repository = $LiveState.repository
        }))
    if ($LiveState.repository.permissions.admin -ne $true) {
        throw "Apply requires confirmed repository administration permission"
    }
    if ($LiveState.repository.allow_squash_merge -ne $true) {
        throw "The planned linear-history ruleset requires squash merging to be enabled"
    }
}

function Get-ProbeEvidence {
    param([Parameter(Mandatory)][Int32]$PullRequest)
    $pull = Invoke-GhJson -Endpoint "repos/$Repository/pulls/$PullRequest"
    if ([string]$pull.base.ref -ne $Branch) {
        throw "Probe pull request targets the wrong base branch"
    }
    $headSha = [string]$pull.head.sha
    if ($headSha -notmatch "^[0-9a-f]{40}$") {
        throw "Probe pull request has an invalid head SHA"
    }
    if ($null -eq $pull.mergeable -or [string]::IsNullOrWhiteSpace([string]$pull.mergeable_state)) {
        throw "Probe pull request mergeability is not yet available; refusing an ambiguous result"
    }
    $runs = Invoke-GhJson -Endpoint "repos/$Repository/commits/$headSha/check-runs?per_page=100"
    return [ordered]@{
        pull = [ordered]@{
            number = $PullRequest
            headSha = $headSha
            mergeable = [bool]$pull.mergeable
            mergeable_state = [string]$pull.mergeable_state
        }
        checkRuns = @($runs.check_runs)
    }
}

function Assert-AppCheckProbes {
    param(
        [Parameter(Mandatory)]$Positive,
        [Parameter(Mandatory)]$Negative
    )
    if ($ProbePullRequest -eq $SpoofProbePullRequest) {
        throw "positive and negative source probes must be different pull requests"
    }
    [void](Invoke-TrustedModel `
        -Operation "assert-probes" `
        -InputObject ([ordered]@{
            positive = $Positive
            negative = $Negative
            appId = $AppId
            checkName = "trusted-dependency-artifact"
        }))
}

function Assert-PostReadBack {
    param(
        [Parameter(Mandatory)]$Before,
        [Parameter(Mandatory)]$Desired,
        [Parameter(Mandatory)][string]$AppJwt
    )
    $after = Get-LiveState
    $managed = @(Get-ManagedRulesets $after)
    if ($managed.Count -ne 1) {
        throw "Read-back found $($managed.Count) managed rulesets; expected exactly one"
    }
    [void](Assert-AppInstallation -Jwt $AppJwt)
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

    Assert-AppCheckProbes `
        -Positive (Get-ProbeEvidence -PullRequest $ProbePullRequest) `
        -Negative (Get-ProbeEvidence -PullRequest $SpoofProbePullRequest)

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
    return $after
}

function Invoke-SafeRollback {
    param(
        [Parameter(Mandatory)]$CreatedRuleset,
        [Parameter(Mandatory)]$Before,
        [Parameter(Mandatory)]$Desired,
        [Parameter(Mandatory)][string]$StartedAt,
        [Parameter(Mandatory)][Int64]$OwnerId
    )
    $createdId = [Int64]$CreatedRuleset.id
    if ($createdId -le 0) {
        throw "automatic rollback refused: create response had no valid ruleset ID"
    }
    $readBack = Invoke-GhJson -Endpoint "repos/$Repository/rulesets/$createdId"
    $history = Invoke-GhJson -Endpoint "repos/$Repository/rulesets/$createdId/history"
    $endedAt = [DateTimeOffset]::UtcNow.UtcDateTime.ToString("yyyy-MM-ddTHH:mm:ss.fffZ")
    [void](Invoke-TrustedModel `
        -Operation "assert-safe-rollback" `
        -InputObject ([ordered]@{
            beforeRulesetIds = @(
                @(Get-ManagedRulesets $Before) | ForEach-Object { [Int64]$_.id }
            )
            createdRuleset = $CreatedRuleset
            readBackRuleset = $readBack
            history = @($history)
            ownerId = $OwnerId
            expectedRuleset = $Desired
            expectedRepository = $Repository
            startedAt = $StartedAt
            endedAt = $endedAt
        }))
    [void](Invoke-GhJson `
        -Endpoint "repos/$Repository/rulesets/$createdId" `
        -Method "DELETE")
    $after = Get-LiveState
    if (@(Get-ManagedRulesets $after | Where-Object { [Int64]$_.id -eq $createdId }).Count -ne 0) {
        throw "automatic rollback did not remove the just-created ruleset"
    }
    return $true
}

[void](Invoke-TrustedModel -Operation "validate-plan" -Arguments @("--plan", $planPath))
[void](Invoke-TrustedModel -Operation "validate-contract" -Arguments @("--contract", $contractPath))
$owner = Assert-OwnerAuthentication
$live = Get-LiveState
$snapshot = Get-Snapshot $live
$desired = Get-DesiredRuleset
[void](Assert-DesiredAppBinding -Desired $desired)
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
    $appJwt = Get-AppJwt
    [void](Assert-PostReadBack -Before $live -Desired $desired -AppJwt $appJwt)
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
$appJwt = Get-AppJwt
[void](Assert-AppInstallation -Jwt $appJwt)
[void](Assert-AppCheckProbes `
    -Positive (Get-ProbeEvidence -PullRequest $ProbePullRequest) `
    -Negative (Get-ProbeEvidence -PullRequest $SpoofProbePullRequest))
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

$startedAt = [DateTimeOffset]::UtcNow.UtcDateTime.ToString("yyyy-MM-ddTHH:mm:ss.fffZ")
$created = $null
try {
    $created = Invoke-GhJson -Endpoint "repos/$Repository/rulesets" -Method "POST" -Body $desired
    [void](Assert-PostReadBack -Before $live -Desired $desired -AppJwt $appJwt)
} catch {
    $failure = $_.Exception.Message
    if ($null -eq $created) {
        try {
            $reconciled = Get-LiveState
            $beforeIds = @(
                @(Get-ManagedRulesets $live) | ForEach-Object { [Int64]$_.id }
            )
            $newCandidates = @(
                Get-ManagedRulesets $reconciled | Where-Object {
                    $beforeIds -notcontains [Int64]$_.id
                }
            )
            if ($newCandidates.Count -eq 1) {
                $created = $newCandidates[0]
            }
        } catch {
            # A lost create response is handled as owner attention below.
        }
    }
    if ($null -eq $created) {
        throw "ruleset apply failed without a provable create target: $failure; owner attention is required"
    }
    try {
        [void](Invoke-SafeRollback `
            -CreatedRuleset $created `
            -Before $live `
            -Desired $desired `
            -StartedAt $startedAt `
            -OwnerId ([Int64]$owner.id))
    } catch {
        throw "ruleset apply verification failed: $failure; automatic rollback was refused or failed and requires owner attention"
    }
    throw "ruleset apply verification failed: $failure; the just-created ruleset was automatically rolled back"
}
[ordered]@{
    mode = "apply"
    verified = $true
    repository = $Repository
    branch = $Branch
    appId = $AppId
    proof = "Read-back matched the dedicated App source, strict required check, reviews, CODEOWNERS, conversation resolution, force-push/deletion block, linear history, and no bypass actors."
} | ConvertTo-Json -Depth 10
