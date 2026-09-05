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

    [Parameter(Mandatory)]
    [ValidateNotNullOrEmpty()]
    [string]$EvaluatorOrigin,

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
    [ValidateRange(30, 900)]
    [Int32]$ProbeTimeoutSeconds = 300,

    [Parameter(ParameterSetName = "Apply")]
    [Parameter(ParameterSetName = "ReadBack")]
    [ValidateRange(5, 60)]
    [Int32]$ProbePollSeconds = 10,

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
$policyPath = Join-Path $repoRoot ".github\trusted-policy\dependency-artifact-policy.json"
$githubApiOrigin = "https://api.github.com"
$githubWebOrigin = "https://github.com"

if (!(Test-Path -LiteralPath $planPath)) { throw "Trusted ruleset plan not found: $planPath" }
if (!(Test-Path -LiteralPath $contractPath)) { throw "GitHub App contract not found: $contractPath" }
if (!(Test-Path -LiteralPath $modelPath)) { throw "Trusted ruleset model not found: $modelPath" }
if (!(Test-Path -LiteralPath $jwtModelPath)) { throw "GitHub App JWT helper not found: $jwtModelPath" }
if (!(Test-Path -LiteralPath $policyPath)) { throw "Trusted artifact policy not found: $policyPath" }
if ($Repository -ne "judeper/FSI-AgentGov" -or $Branch -ne "main") {
    throw "This operator is permanently bound to judeper/FSI-AgentGov main"
}

function Assert-PinnedGitHubOrigins {
    $apiOverride = [string]$env:GITHUB_API_URL
    if (
        ![string]::IsNullOrWhiteSpace($apiOverride) -and
        $apiOverride.TrimEnd("/") -ne $githubApiOrigin
    ) {
        throw "ambient GITHUB_API_URL overrides are not permitted"
    }
    $serverOverride = [string]$env:GITHUB_SERVER_URL
    if (
        ![string]::IsNullOrWhiteSpace($serverOverride) -and
        $serverOverride.TrimEnd("/") -ne $githubWebOrigin
    ) {
        throw "ambient GITHUB_SERVER_URL overrides are not permitted"
    }
    $hostOverride = [string]$env:GH_HOST
    if (
        ![string]::IsNullOrWhiteSpace($hostOverride) -and
        $hostOverride.Trim().ToLowerInvariant() -ne "github.com"
    ) {
        throw "ambient GH_HOST overrides are not permitted"
    }
}

function Get-ValidatedEvaluatorOrigin {
    try {
        $uri = [Uri]$EvaluatorOrigin
    } catch {
        throw "EvaluatorOrigin must be an absolute HTTPS origin"
    }
    if (
        !$uri.IsAbsoluteUri -or
        $uri.Scheme -ne "https" -or
        $uri.AbsolutePath -ne "/" -or
        ![string]::IsNullOrEmpty($uri.Query) -or
        ![string]::IsNullOrEmpty($uri.Fragment) -or
        ![string]::IsNullOrEmpty($uri.UserInfo) -or
        $uri.IsLoopback -or
        $uri.Host -in @("github.com", "api.github.com")
    ) {
        throw "EvaluatorOrigin must be an exact external HTTPS origin"
    }
    return $uri.GetLeftPart([System.UriPartial]::Authority)
}

function ConvertTo-CompactJson {
    param([Parameter(Mandatory)]$Value)
    return (ConvertTo-Json -InputObject $Value -Depth 100 -Compress)
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
    $output = & gh api --hostname github.com user --jq "{login:.login,id:.id}" 2>&1
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
        [Parameter(Mandatory)][string]$BearerToken,
        [ValidateSet("GET", "POST", "DELETE")][string]$Method = "GET"
    )
    $uri = "$githubApiOrigin/$Endpoint"
    $headers = @{
        Accept = "application/vnd.github+json"
        "X-GitHub-Api-Version" = "2026-03-10"
        Authorization = "Bearer $BearerToken"
        "User-Agent" = "trusted-dependency-artifact-ruleset"
    }
    try {
        $parameters = @{
            Uri = $uri
            Method = $Method
            Headers = $headers
            ErrorAction = "Stop"
            MaximumRedirection = 0
        }
        if ($Method -eq "POST") {
            $parameters.ContentType = "application/json"
            $parameters.Body = "{}"
        }
        return Invoke-RestMethod @parameters
    } catch {
        throw "GitHub App $Method $Endpoint failed"
    }
}

function Get-AppContract {
    try {
        $contract = Get-Content -LiteralPath $contractPath -Raw | ConvertFrom-Json -Depth 100
    } catch {
        throw "GitHub App contract is unreadable"
    }
    if ([int]$contract.schemaVersion -ne 3) {
        throw "GitHub App contract schema version is unsupported"
    }
    return $contract
}

function Get-PolicyEvidence {
    return Invoke-TrustedModel `
        -Operation "policy-evidence" `
        -Arguments @("--policy", $policyPath)
}

function New-ProbeNonce {
    $bytes = [byte[]]::new(32)
    [System.Security.Cryptography.RandomNumberGenerator]::Fill($bytes)
    return (($bytes | ForEach-Object { $_.ToString("x2") }) -join "")
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
        "--hostname", "github.com",
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
    $material = "$Repository|$Branch|$AppId|$validatedEvaluatorOrigin|$LiveDigest|$IntendedRulesetDigest"
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

function Get-AllAppInstallations {
    param([Parameter(Mandatory)][string]$Jwt)
    $installations = [System.Collections.Generic.List[object]]::new()
    $ids = [System.Collections.Generic.HashSet[long]]::new()
    for ($page = 1; $page -le 100; $page++) {
        $response = Invoke-AppJson `
            -Endpoint "app/installations?per_page=100&page=$page" `
            -BearerToken $Jwt
        $count = 0
        foreach ($installation in $response) {
            if (
                $null -eq $installation -or $installation -is [array] -or
                $null -eq $installation.PSObject.Properties["id"] -or
                $installation.id -isnot [long] -and $installation.id -isnot [int] -or
                $installation.id -le 0 -or !$ids.Add([long]$installation.id)
            ) {
                throw "GitHub App installation pagination contains a malformed or duplicate ID"
            }
            $installations.Add($installation)
            $count++
        }
        if ($count -gt 100) { throw "GitHub App installation page exceeded its page size" }
        if ($count -lt 100) { return $installations.ToArray() }
    }
    throw "GitHub App installation pagination exceeded the safety bound"
}

function Get-AllInstallationRepositories {
    param([Parameter(Mandatory)][string]$InstallationToken)
    $repositories = [System.Collections.Generic.List[object]]::new()
    $ids = [System.Collections.Generic.HashSet[long]]::new()
    $reportedTotal = $null
    for ($page = 1; $page -le 100; $page++) {
        $response = Invoke-AppJson `
            -Endpoint "installation/repositories?per_page=100&page=$page" `
            -BearerToken $InstallationToken
        if (
            $null -eq $response -or $response -is [array] -or
            $null -eq $response.PSObject.Properties["total_count"] -or
            $null -eq $response.PSObject.Properties["repositories"] -or
            $response.total_count -isnot [long] -and $response.total_count -isnot [int] -or
            $response.total_count -lt 0 -or $response.total_count -gt 10000 -or
            $response.repositories -isnot [array]
        ) {
            throw "GitHub App repository enumeration omitted a valid total_count or repositories array"
        }
        if ($null -eq $reportedTotal) { $reportedTotal = [int]$response.total_count }
        if ($response.total_count -ne $reportedTotal) {
            throw "GitHub App repository enumeration total_count changed between pages"
        }
        $count = 0
        foreach ($repositoryRecord in $response.repositories) {
            if (
                $null -eq $repositoryRecord -or $repositoryRecord -is [array] -or
                $null -eq $repositoryRecord.PSObject.Properties["id"] -or
                $null -eq $repositoryRecord.PSObject.Properties["full_name"] -or
                $repositoryRecord.id -isnot [long] -and $repositoryRecord.id -isnot [int] -or
                $repositoryRecord.id -le 0 -or !$ids.Add([long]$repositoryRecord.id) -or
                [string]::IsNullOrWhiteSpace([string]$repositoryRecord.full_name)
            ) {
                throw "GitHub App repository pagination contains a malformed or duplicate repository"
            }
            $repositories.Add($repositoryRecord)
            $count++
        }
        if ($count -gt 100 -or $repositories.Count -gt $reportedTotal) {
            throw "GitHub App repository enumeration exceeded its reported count"
        }
        if ($count -lt 100) {
            if ($repositories.Count -ne $reportedTotal) {
                throw "GitHub App repository enumeration count did not match total_count"
            }
            return $repositories.ToArray()
        }
    }
    throw "GitHub App repository pagination exceeded the safety bound"
}

function Assert-AppInstallation {
    param([Parameter(Mandatory)][string]$Jwt)

    $contract = Get-AppContract
    $app = Invoke-AppJson -Endpoint "app" -BearerToken $Jwt
    if ([Int64]$app.id -ne $AppId -or [string]$app.slug -eq "github-actions") {
        throw "App JWT identity does not match the requested dedicated GitHub App"
    }

    $installations = @(Get-AllAppInstallations -Jwt $Jwt)
    $installation = Invoke-AppJson `
        -Endpoint "repos/$Repository/installation" `
        -BearerToken $Jwt
    if (
        $null -eq $installation -or
        [Int64]$installation.id -le 0 -or
        [Int64]$installation.app_id -ne $AppId
    ) {
        throw "The dedicated GitHub App is not installed on $Repository"
    }

    $tokenResponse = Invoke-AppJson `
        -Endpoint "app/installations/$([Int64]$installation.id)/access_tokens" `
        -BearerToken $Jwt `
        -Method "POST"
    $installationToken = [string]$tokenResponse.token
    if ([string]::IsNullOrWhiteSpace($installationToken)) {
        throw "GitHub App installation token creation returned no token"
    }

    $repositories = $null
    $validationFailure = $null
    try {
        $expiresAt = [DateTimeOffset]::MinValue
        $expiryText = [string]$tokenResponse.expires_at
        if (
            $expiryText -notmatch '^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?Z$' -or
            ![DateTimeOffset]::TryParse($expiryText, [System.Globalization.CultureInfo]::InvariantCulture,
                [System.Globalization.DateTimeStyles]::None, [ref]$expiresAt)
        ) {
            throw "GitHub App installation token expiry is invalid"
        }
        $now = [DateTimeOffset]::UtcNow
        $maxLifetime = [int]$contract.installationVerification.maxTokenLifetimeSeconds
        if ($expiresAt -le $now -or $expiresAt -gt $now.AddSeconds($maxLifetime)) {
            throw "GitHub App installation token expiry is invalid"
        }
        $repositories = @(Get-AllInstallationRepositories -InstallationToken $installationToken)
        [void](Invoke-TrustedModel `
            -Operation "assert-app-installation" `
            -InputObject ([ordered]@{
                app = $app
                installations = $installations
                installation = $installation
                repositories = $repositories
                tokenPermissions = $tokenResponse.permissions
                contract = $contract
                appId = $AppId
                repository = $Repository
            }))
    } catch {
        $validationFailure = $_.Exception.Message
    }

    try {
        [void](Invoke-AppJson `
            -Endpoint "installation/token" `
            -BearerToken $installationToken `
            -Method "DELETE")
    } catch {
        if ($null -ne $validationFailure) {
            throw "$validationFailure; temporary installation token revocation also failed"
        }
        throw "temporary GitHub App installation token revocation failed"
    } finally {
        $installationToken = $null
        $tokenResponse.token = $null
    }
    if ($null -ne $validationFailure) { throw $validationFailure }
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
    if (
        [string]$pull.state -ne "open" -or
        [string]$pull.base.ref -ne $Branch -or
        [string]$pull.base.repo.full_name -ne $Repository -or
        [string]$pull.head.repo.full_name -ne $Repository
    ) {
        throw "Probe pull request must be open and use same-repository branches against the pinned base"
    }
    $headSha = [string]$pull.head.sha
    $baseSha = [string]$pull.base.sha
    if ($headSha -notmatch "^[0-9a-f]{40}$" -or $baseSha -notmatch "^[0-9a-f]{40}$") {
        throw "Probe pull request has an invalid head or base SHA"
    }
    if ($null -eq $pull.mergeable -or [string]::IsNullOrWhiteSpace([string]$pull.mergeable_state)) {
        throw "Probe pull request mergeability is not yet available; refusing an ambiguous result"
    }
    $pages = Invoke-GhJson `
        -Endpoint "repos/$Repository/commits/$headSha/check-runs?filter=all&per_page=100" `
        -Paginate
    $after = Invoke-GhJson -Endpoint "repos/$Repository/pulls/$PullRequest"
    return Invoke-TrustedModel `
        -Operation "probe-evidence" `
        -InputObject ([ordered]@{
            pull = $pull
            after = $after
            checkRunPages = @($pages)
            pullNumber = $PullRequest
            repository = $Repository
        })
}

function Assert-AppCheckProbes {
    param(
        [Parameter(Mandatory)]$Positive,
        [Parameter(Mandatory)]$Negative,
        [Parameter(Mandatory)][string]$RulesetCreatedAt,
        [Parameter(Mandatory)][string]$ObservedAt,
        [Parameter(Mandatory)]$PolicyEvidence,
        [Parameter(Mandatory)][string]$PositiveNonce,
        [Parameter(Mandatory)][string]$NegativeNonce
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
            policyDigest = $PolicyEvidence.digest
            policyVersion = $PolicyEvidence.version
            positiveNonce = $PositiveNonce
            negativeNonce = $NegativeNonce
            evaluatorOrigin = $validatedEvaluatorOrigin
            rulesetCreatedAt = $RulesetCreatedAt
            observedAt = $ObservedAt
            positiveMode = "not-applicable"
            negativeMode = "activation-rejected"
            maxAgeSeconds = 300
        }))
}

function Wait-AppCheckProbes {
    param(
        [Parameter(Mandatory)][string]$RulesetCreatedAt,
        [Parameter(Mandatory)]$PolicyEvidence,
        [Parameter(Mandatory)][string]$PositiveNonce,
        [Parameter(Mandatory)][string]$NegativeNonce
    )
    $deadline = [DateTimeOffset]::UtcNow.AddSeconds($ProbeTimeoutSeconds)
    $lastFailure = "fresh post-ruleset probe evidence was not observed"
    do {
        try {
            $positive = Get-ProbeEvidence -PullRequest $ProbePullRequest
            $negative = Get-ProbeEvidence -PullRequest $SpoofProbePullRequest
            $observedAt = [DateTimeOffset]::UtcNow.UtcDateTime.ToString("yyyy-MM-ddTHH:mm:ss.fffZ")
            Assert-AppCheckProbes `
                -Positive $positive `
                -Negative $negative `
                -RulesetCreatedAt $RulesetCreatedAt `
                -ObservedAt $observedAt `
                -PolicyEvidence $PolicyEvidence `
                -PositiveNonce $PositiveNonce `
                -NegativeNonce $NegativeNonce
            return
        } catch {
            $lastFailure = $_.Exception.Message
        }
        if ([DateTimeOffset]::UtcNow -lt $deadline) {
            Start-Sleep -Seconds $ProbePollSeconds
        }
    } while ([DateTimeOffset]::UtcNow -lt $deadline)
    throw "fresh post-ruleset probes were not verified within $ProbeTimeoutSeconds seconds: $lastFailure"
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
    $rulesetCreatedAt = [string]$managed[0].created_at
    if ([string]::IsNullOrWhiteSpace($rulesetCreatedAt)) {
        throw "Managed ruleset read-back omitted created_at"
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

    $policyEvidence = Get-PolicyEvidence
    $positiveNonce = New-ProbeNonce
    $negativeNonce = New-ProbeNonce
    while ($negativeNonce -eq $positiveNonce) {
        $negativeNonce = New-ProbeNonce
    }
    Write-Host (
        [ordered]@{
            message = "Trigger the independently deployed evaluator for both probe PRs using these fresh, non-secret challenges."
            repository = $Repository
            rulesetCreatedAt = $rulesetCreatedAt
            policyDigest = $policyEvidence.digest
            policyVersion = $policyEvidence.version
            positivePullRequest = $ProbePullRequest
            positiveNonce = $positiveNonce
            negativePullRequest = $SpoofProbePullRequest
            negativeNonce = $negativeNonce
        } | ConvertTo-Json -Depth 5 -Compress
    )
    Wait-AppCheckProbes `
        -RulesetCreatedAt $rulesetCreatedAt `
        -PolicyEvidence $policyEvidence `
        -PositiveNonce $positiveNonce `
        -NegativeNonce $negativeNonce

    $final = Get-LiveState
    $finalManaged = @(Get-ManagedRulesets $final)
    if (
        $finalManaged.Count -ne 1 -or
        [Int64]$finalManaged[0].id -ne [Int64]$managed[0].id
    ) {
        throw "Managed ruleset identity changed while probe evidence was collected"
    }
    [void](Assert-AppInstallation -Jwt $AppJwt)
    [void](Invoke-TrustedModel `
        -Operation "assert-readback" `
        -InputObject ([ordered]@{
            repository = $final.repository
            ruleset = $finalManaged[0]
            branchProtection = $final.branchProtection
        }) `
        -Arguments @("--plan", $planPath, "--app-id", $AppId.ToString()))
    [void](Invoke-TrustedModel `
        -Operation "assert-unrelated-preserved" `
        -InputObject ([ordered]@{
            before = $Before
            after = $final
            managedRulesetName = $Desired.name
        }))
    $after = $final

    $mergeQueueRules = @(
        $after.rulesets | Where-Object {
            $_.enforcement -eq "active" -and
            @($_.rules | Where-Object { $_.type -eq "merge_queue" }).Count -gt 0
        }
    )
    if ($mergeQueueRules.Count -gt 0) {
        throw "An active merge queue is outside this reviewed plan; add signed merge-group evidence in a later policy revision"
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
                $Before.rulesets | ForEach-Object { [Int64]$_.id }
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
    if ((Get-Snapshot $after).digest -ne (Get-Snapshot $Before).digest) {
        throw "automatic rollback observed unrelated security drift; owner attention is required"
    }
    return $true
}

[void](Assert-PinnedGitHubOrigins)
$validatedEvaluatorOrigin = Get-ValidatedEvaluatorOrigin
[void](Invoke-TrustedModel -Operation "validate-plan" -Arguments @("--plan", $planPath))
[void](Invoke-TrustedModel -Operation "validate-contract" -Arguments @("--contract", $contractPath))
$owner = Assert-OwnerAuthentication
$live = Get-LiveState
[void](Invoke-TrustedModel `
    -Operation "assert-legacy-baseline" `
    -InputObject ([ordered]@{
        repository = $live.repository
        branchProtection = $live.branchProtection
    }) `
    -Arguments @("--plan", $planPath))
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
        evaluatorOrigin = $validatedEvaluatorOrigin
        liveDigest = $snapshot.digest
        intendedRulesetDigest = $intendedRulesetDigest
        confirmationToken = $confirmation
        existingManagedRulesets = @(Get-ManagedRulesets $live).Count
        probeContract = "Fresh positive App success and negative App failure plus same-name Actions success must be produced after ruleset creation."
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
        evaluatorOrigin = $validatedEvaluatorOrigin
        proof = "Expected-source App binding and every planned ruleset field matched. Unrelated protection state was not changed by this operation."
    } | ConvertTo-Json -Depth 10
    return
}

Assert-ApplyCapability $live
$appJwt = Get-AppJwt
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

[void](Assert-AppInstallation -Jwt $appJwt)
$preCreate = Get-LiveState
if ((Get-Snapshot $preCreate).digest -ne $snapshot.digest) {
    throw "Live repository security state changed during App verification; refusing to create"
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
    evaluatorOrigin = $validatedEvaluatorOrigin
    proof = "Read-back matched the dedicated App source, strict required check, reviews, CODEOWNERS, conversation resolution, force-push/deletion block, linear history, and no bypass actors."
} | ConvertTo-Json -Depth 10
