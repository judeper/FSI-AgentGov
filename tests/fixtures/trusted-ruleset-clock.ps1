Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$inputData = [Console]::In.ReadToEnd() | ConvertFrom-Json -Depth 100
$repoRoot = Split-Path -Parent (Split-Path -Parent $PSScriptRoot)
$operator = Join-Path $repoRoot "scripts\trusted\Invoke-TrustedDependencyArtifactRuleset.ps1"
$nodePath = (Get-Command node -CommandType Application).Source
$payload = [System.Text.Encoding]::UTF8.GetString(
    [Convert]::FromBase64String($inputData.payloadBase64)
) | ConvertFrom-Json -Depth 100
$culture = if ($inputData.culture -eq "Invariant") {
    [System.Globalization.CultureInfo]::InvariantCulture
} else {
    [System.Globalization.CultureInfo]::GetCultureInfo($inputData.culture)
}
[System.Globalization.CultureInfo]::CurrentCulture = $culture
[System.Globalization.CultureInfo]::CurrentUICulture = $culture

$ast = [System.Management.Automation.Language.Parser]::ParseFile($operator, [ref]$null, [ref]$null)
$normalizer = $ast.Find({
    param($node)
    $node -is [System.Management.Automation.Language.FunctionDefinitionAst] -and
    $node.Name -eq "ConvertTo-GitHubUtcTimestamp"
}, $false)
. ([scriptblock]::Create($normalizer.Extent.Text))

$fixture = @{
    nodePath = $nodePath
    calls = [System.Collections.Generic.List[object]]::new()
    created = $null
    challenge = $null
    sleeps = 0
    revocations = 0
    lastTokenResponse = $null
    deleted = 0
}

# Only transport and scheduling are replaced. The complete production script,
# including its parameter contract, plan, apply, poll and rollback, runs below.
function Get-FixtureTimestamp {
    param([int]$Seconds = 0, [switch]$WholeSeconds)
    $clock = [DateTimeOffset]::UtcNow.AddSeconds($Seconds)
    if ($WholeSeconds) {
        $clock = $clock.AddTicks(-($clock.Ticks % [TimeSpan]::TicksPerSecond))
    }
    return ConvertTo-GitHubUtcTimestamp `
        -InputObject $clock `
        -FieldName "fixture clock"
}

function node {
    $arguments = @($args)
    $stdinText = @($input) -join "`n"
    if ((Split-Path -Leaf $arguments[0]) -eq "github-app-jwt.mjs") {
        Set-Variable -Name LASTEXITCODE -Value 0 -Scope 1
        return "TEST.FIXTURE.JWT"
    }
    if ((Split-Path -Leaf $arguments[0]) -ne "trusted-dependency-ruleset.mjs") {
        throw "unexpected executable in the clock fixture"
    }
    $output = if ($stdinText) {
        $stdinText | & $fixture.nodePath @arguments 2>&1
    } else {
        & $fixture.nodePath @arguments 2>&1
    }
    $code = $LASTEXITCODE
    if ($arguments[1] -in @("probe-evidence", "assert-probes", "assert-safe-rollback")) {
        $fixture.calls.Add([ordered]@{
            kind = "model"
            operation = $arguments[1]
            inputJson = $stdinText
            accepted = ($code -eq 0)
        })
    }
    Set-Variable -Name LASTEXITCODE -Value $code -Scope 1
    return $output
}

function Write-Host {
    param($Object)
    $fixture.challenge = [string]$Object | ConvertFrom-Json -Depth 100
}

function Start-Sleep {
    param($Seconds)
    $fixture.sleeps++
    if ($inputData.scenario -ne "retry" -or $fixture.sleeps -gt 1) {
        throw "fixture stopped the rejected probe poll before its next sleep"
    }
}

function Get-FixtureProbe {
    param([bool]$Negative)
    $probe = if ($Negative) { $payload.negative } else { $payload.positive }
    $run = $probe.checkRunPages[0].check_runs[0]
    $issued = Get-FixtureTimestamp
    $started = Get-FixtureTimestamp
    $completed = Get-FixtureTimestamp
    switch ($inputData.scenario) {
        "probe-stale" {
            $issued = $started = $completed = Get-FixtureTimestamp -Seconds -600
        }
        "probe-future" {
            $issued = $started = $completed = Get-FixtureTimestamp -Seconds 600
        }
        "probe-malformed" { $started = "not-a-time" }
        "retry" {
            if ($fixture.sleeps -eq 0) {
                $issued = $started = $completed = Get-FixtureTimestamp -Seconds -600
            }
        }
    }
    $externalId = [ordered]@{
        base_sha = $probe.pull.base.sha
        head_sha = $probe.pull.head.sha
        issued_at = $issued
        mode = $(if ($Negative) { "activation-rejected" } else { "not-applicable" })
        nonce = $(if ($Negative) { $fixture.challenge.negativeNonce } else { $fixture.challenge.positiveNonce })
        policy_digest = $fixture.challenge.policyDigest
        policy_version = $fixture.challenge.policyVersion
        pull_request = $probe.pull.number
        repository = $payload.repository.full_name
    } | ConvertTo-Json -Depth 10 -Compress
    $run.external_id = "tdag.v1." + [Convert]::ToBase64String(
        [System.Text.Encoding]::UTF8.GetBytes($externalId)
    ).TrimEnd("=").Replace("+", "-").Replace("/", "_")
    foreach ($check in $probe.checkRunPages[0].check_runs) {
        $check.started_at = $started
        $check.completed_at = $completed
    }
    return $probe
}

function gh {
    $arguments = @($args)
    $stdinText = @($input) -join "`n"
    $endpoint = @($arguments | Where-Object { $_ -eq "user" -or $_ -match '^repos/' })[0]
    $methodIndex = [array]::IndexOf($arguments, "-X")
    $method = if ($methodIndex -ge 0) { $arguments[$methodIndex + 1] } else { "GET" }
    $fixture.calls.Add([ordered]@{ kind = "owner"; endpoint = $endpoint; method = $method })
    Set-Variable -Name LASTEXITCODE -Value 0 -Scope 1
    $result = switch -Regex ($endpoint) {
        '^user$' { [pscustomobject]@{ login = "judeper"; id = 99 }; break }
        '^repos/[^/]+/[^/]+$' { $payload.repository; break }
        '/branches/main/protection$' { $payload.branchProtection; break }
        '/rulesets\?' {
            $rulesets = if ($null -eq $fixture.created) { @() } else { @($fixture.created) }
            return ConvertTo-Json -InputObject @($rulesets) -Depth 100 -Compress -AsArray
        }
        '/rulesets$' {
            if ($method -ne "POST") { throw "unexpected fixture ruleset method" }
            $fixture.created = $stdinText | ConvertFrom-Json -Depth 100
            $time = Get-FixtureTimestamp
            if ($inputData.scenario -eq "lost-create-response-second-precision") {
                $time = Get-FixtureTimestamp -WholeSeconds
            }
            if ($inputData.scenario -eq "rollback-stale") { $time = Get-FixtureTimestamp -Seconds -600 }
            if ($inputData.scenario -eq "rollback-future") { $time = Get-FixtureTimestamp -Seconds 600 }
            if ($inputData.scenario -eq "rollback-malformed") { $time = "not-a-time" }
            foreach ($entry in @{
                id = 42; source_type = "Repository"; source = $payload.repository.full_name
                created_at = $time; updated_at = $time
            }.GetEnumerator()) {
                $fixture.created | Add-Member -NotePropertyName $entry.Key -NotePropertyValue $entry.Value
            }
            if ($inputData.scenario -like "lost-create-response*" -or $inputData.scenario -like "rollback-*") {
                return "lost create response"
            }
            $fixture.created
            break
        }
        '/rulesets/42/history$' {
            $time = Get-FixtureTimestamp
            if ($inputData.scenario -eq "rollback-history-future") { $time = Get-FixtureTimestamp -Seconds 600 }
            if ($inputData.scenario -eq "rollback-history-before-create") { $time = Get-FixtureTimestamp -Seconds -600 }
            return ConvertTo-Json -InputObject @(
                [pscustomobject]@{ actor = @{ id = 99; type = "User" }; updated_at = $time }
            ) -Depth 100 -Compress
        }
        '/rulesets/42(?:\?|$)' {
            if ($method -eq "DELETE") {
                $fixture.deleted++
                $fixture.created = $null
                return
            }
            $fixture.created
            break
        }
        '/pulls/(101|102)$' {
            if ($null -eq $fixture.challenge) { throw "probe was read before the operator challenge" }
            (Get-FixtureProbe -Negative ($Matches[1] -eq "102")).pull
            break
        }
        '/commits/([0-9a-f]{40})/check-runs\?' {
            $probe = Get-FixtureProbe -Negative ($Matches[1] -eq $payload.negative.pull.head.sha)
            return ConvertTo-Json -InputObject $probe.checkRunPages -Depth 100 -Compress
        }
        default { throw "unexpected owner endpoint in the clock fixture" }
    }
    return ConvertTo-Json -InputObject $result -Depth 100 -Compress
}

function Invoke-RestMethod {
    param($Uri, $Method, $Headers, $MaximumRedirection, $ErrorAction, $ContentType, $Body)
    if (!$Uri.StartsWith("https://api.github.com/") -or $MaximumRedirection -ne 0) {
        throw "untrusted REST destination in the clock fixture"
    }
    $endpoint = $Uri.Substring("https://api.github.com/".Length)
    $isInstallation = $endpoint.StartsWith("installation/")
    $expectedCredential = if ($isInstallation) { "TEST_FIXTURE_INSTALLATION" } else { "TEST.FIXTURE.JWT" }
    if ($Headers.Authorization -cne "Bearer $expectedCredential") { throw "credential crossed fixture boundary" }
    $fixture.calls.Add([ordered]@{ kind = "app"; endpoint = $endpoint; method = $Method })
    switch -Regex ($endpoint) {
        '^app$' { return $payload.app }
        '^app/installations\?' { Write-Output -NoEnumerate @($payload.installation); return }
        '^repos/.+/installation$' { return $payload.installation }
        '^app/installations/[0-9]+/access_tokens$' {
            $fixture.lastTokenResponse = [pscustomobject]@{
                token = "TEST_FIXTURE_INSTALLATION"
                expires_at = Get-FixtureTimestamp -Seconds 1800
                permissions = $payload.installation.permissions
            }
            return $fixture.lastTokenResponse
        }
        '^installation/repositories\?' {
            return [pscustomobject]@{ total_count = 1; repositories = @($payload.repository) }
        }
        '^installation/token$' { $fixture.revocations++; return }
        default { throw "unexpected App endpoint in the clock fixture" }
    }
}

# The JWT transport stub never reads a private key or inherited owner credential.
$env:GITHUB_APP_PRIVATE_KEY = "TEST_FIXTURE_KEY_NOT_A_PRIVATE_KEY"
foreach ($name in @("GITHUB_APP_PRIVATE_KEY_PATH", "GITHUB_API_URL", "GITHUB_SERVER_URL", "GH_HOST", "GH_TOKEN", "GITHUB_TOKEN")) {
    Remove-Item "Env:$name" -ErrorAction SilentlyContinue
}
$options = @{
    AppId = 8675309
    EvaluatorOrigin = "https://trusted-evaluator.example"
}
try {
    $plan = (& $operator @options -Plan) -join "`n" | ConvertFrom-Json -Depth 100
    $apply = (& $operator @options -Apply -Confirm:$false `
        -ExpectedLiveDigest $plan.liveDigest `
        -ExpectedIntendedRulesetDigest $plan.intendedRulesetDigest `
        -ConfirmationToken $plan.confirmationToken `
        -ProbePullRequest 101 -SpoofProbePullRequest 102 `
        -ProbeTimeoutSeconds 30 -ProbePollSeconds 5) -join "`n" | ConvertFrom-Json -Depth 100
    $result = [ordered]@{ ok = $true; value = $apply }
} catch {
    $result = [ordered]@{ ok = $false; error = $_.Exception.Message }
}
$result.calls = $fixture.calls.ToArray()
$result.challenge = $fixture.challenge
$result.sleeps = $fixture.sleeps
$result.deleted = $fixture.deleted
$result.rulesetRemaining = ($null -ne $fixture.created)
$result.revocations = $fixture.revocations
$result.tokenCleared = ($null -ne $fixture.lastTokenResponse -and $null -eq $fixture.lastTokenResponse.token)
$result.tokenExpiresAt = if ($null -ne $fixture.lastTokenResponse) { $fixture.lastTokenResponse.expires_at } else { $null }
ConvertTo-Json -InputObject $result -Depth 100 -Compress
