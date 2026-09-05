Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$inputData = [Console]::In.ReadToEnd() | ConvertFrom-Json -Depth 100
$repoRoot = Split-Path -Parent (Split-Path -Parent $PSScriptRoot)
$operator = Join-Path $repoRoot "scripts\trusted\Invoke-TrustedDependencyArtifactRuleset.ps1"
$modelPath = Join-Path $repoRoot "scripts\trusted\trusted-dependency-ruleset.mjs"
$contractPath = Join-Path $repoRoot ".github\trusted-policy\trusted-dependency-artifact-app-contract.json"
$Repository = "judeper/FSI-AgentGov"
$Branch = "main"
$AppId = 8675309
$githubApiOrigin = "https://api.github.com"
$githubWebOrigin = "https://github.com"
$calls = [System.Collections.Generic.List[object]]::new()
$cursor = 0

if ($null -ne $inputData.PSObject.Properties["culture"]) {
    $culture = if ([string]$inputData.culture -eq "Invariant") {
        [System.Globalization.CultureInfo]::InvariantCulture
    } else {
        [System.Globalization.CultureInfo]::GetCultureInfo([string]$inputData.culture)
    }
    [System.Globalization.CultureInfo]::CurrentCulture = $culture
    [System.Globalization.CultureInfo]::CurrentUICulture = $culture
}

$ast = [System.Management.Automation.Language.Parser]::ParseFile($operator, [ref]$null, [ref]$null)
foreach ($definition in $ast.FindAll({
    param($node)
    $node -is [System.Management.Automation.Language.FunctionDefinitionAst]
}, $false)) {
    . ([scriptblock]::Create($definition.Extent.Text))
}

function ConvertFrom-EncodedFixtureJson {
    param([Parameter(Mandatory)][string]$Base64)
    $json = [System.Text.Encoding]::UTF8.GetString(
        [Convert]::FromBase64String($Base64)
    )
    return $json | ConvertFrom-Json -Depth 100
}

function gh { throw "network is forbidden in the operator fixture" }
function Invoke-RestMethod { throw "network is forbidden in the operator fixture" }

if ($inputData.operation -eq "transport") {
    function Invoke-RestMethod {
        param($Uri, $Method, $Headers, $MaximumRedirection, $ErrorAction, $ContentType, $Body)
        $calls.Add([ordered]@{
            uri = $Uri
            method = $Method
            redirections = $MaximumRedirection
            installationCredential = ($Headers.Authorization -eq "Bearer TEST_FIXTURE_INSTALLATION")
        })
        if ($inputData.fail) { throw "transport included TEST_FIXTURE_INSTALLATION in an unsafe exception" }
        if ($null -ne $inputData.PSObject.Properties["payloadBase64"]) {
            return ConvertFrom-EncodedFixtureJson -Base64 $inputData.payloadBase64
        }
        return [pscustomobject]@{ ok = $true }
    }
} else {
    function Invoke-AppJson {
        param($Endpoint, $BearerToken, $Method = "GET")
        $calls.Add([ordered]@{
            endpoint = $Endpoint
            method = $Method
            appCredential = ($BearerToken -eq "TEST_FIXTURE_JWT")
            installationCredential = ($BearerToken -eq "TEST_FIXTURE_INSTALLATION")
        })
        if ($inputData.operation -in @("repositories", "installations")) {
            if ($script:cursor -ge $inputData.pages.Count) { throw "unexpected fixture page request" }
            $page = $inputData.pages[$script:cursor++]
            if ($page -is [array]) { Write-Output -NoEnumerate $page }
            else { $page }
            return
        }
        switch -Regex ($Endpoint) {
            '^app$' { return $inputData.app }
            '^app/installations\?' { Write-Output -NoEnumerate $inputData.installations; return }
            '^repos/.+/installation$' { return $inputData.installation }
            '^app/installations/[0-9]+/access_tokens$' {
                if ($null -ne $inputData.PSObject.Properties["tokenPayloadBase64"]) {
                    return ConvertFrom-EncodedFixtureJson -Base64 $inputData.tokenPayloadBase64
                }
                $expiry = if ($inputData.expiry -is [string] -or $inputData.expiry -is [DateTime]) {
                    $inputData.expiry
                } else {
                    ConvertTo-GitHubUtcTimestamp `
                        -InputObject ([DateTimeOffset]::UtcNow.AddSeconds([int]$inputData.expiry)) `
                        -FieldName "fixture installation token expiry"
                }
                return [pscustomobject]@{
                    token = "TEST_FIXTURE_INSTALLATION"
                    expires_at = $expiry
                    permissions = $inputData.permissions
                }
            }
            '^installation/repositories\?' {
                if ($script:cursor -ge $inputData.pages.Count) { throw "unexpected fixture page request" }
                return $inputData.pages[$script:cursor++]
            }
            '^installation/token$' {
                if ($inputData.revokeFails) { throw "fixture revocation failure" }
                return
            }
            default { throw "unexpected fixture endpoint" }
        }
    }
}

if ($inputData.operation -eq "probe-evidence") {
    $script:probePayload = ConvertFrom-EncodedFixtureJson -Base64 $inputData.payloadBase64
    $script:probePullReads = 0
    function Invoke-GhJson {
        param($Endpoint, $Method = "GET", $Body, [switch]$AllowNotFound, [switch]$Paginate)
        $calls.Add([ordered]@{ endpoint = $Endpoint; method = $Method })
        if ($Endpoint -match '/pulls/[0-9]+$') {
            $value = if ($script:probePullReads -eq 0) {
                $script:probePayload.pull
            } else {
                $script:probePayload.after
            }
            $script:probePullReads++
            return $value
        }
        if ($Endpoint -match '/check-runs\?') {
            return $script:probePayload.checkRunPages
        }
        throw "unexpected fixture endpoint"
    }
}

try {
    switch ($inputData.operation) {
        "repositories" { $value = @(Get-AllInstallationRepositories -InstallationToken "TEST_FIXTURE_INSTALLATION") }
        "installations" { $value = @(Get-AllAppInstallations -Jwt "TEST_FIXTURE_JWT") }
        "assert-installation" { $value = Assert-AppInstallation -Jwt "TEST_FIXTURE_JWT" }
        "transport" { $value = Invoke-AppJson -Endpoint "installation/repositories" -BearerToken "TEST_FIXTURE_INSTALLATION" }
        "timestamp-contract" {
            if ($null -ne $inputData.PSObject.Properties["payloadBase64"]) {
                $payload = ConvertFrom-EncodedFixtureJson -Base64 $inputData.payloadBase64
                $timestamp = $payload.value
            } elseif ($null -ne $inputData.PSObject.Properties["dateTimeOffsetBase64"]) {
                $timestampText = [System.Text.Encoding]::UTF8.GetString(
                    [Convert]::FromBase64String([string]$inputData.dateTimeOffsetBase64)
                )
                $timestamp = [DateTimeOffset]::Parse(
                    $timestampText,
                    [System.Globalization.CultureInfo]::InvariantCulture,
                    [System.Globalization.DateTimeStyles]::RoundtripKind
                )
            } else {
                $timestamp = [System.Text.Encoding]::UTF8.GetString(
                    [Convert]::FromBase64String([string]$inputData.literalBase64)
                )
            }
            $sourceKind = if ($timestamp -is [DateTime]) {
                $timestamp.Kind.ToString()
            } elseif ($timestamp -is [DateTimeOffset]) {
                $timestamp.Offset.ToString()
            } else {
                $null
            }
            $value = [ordered]@{
                sourceType = $timestamp.GetType().FullName
                sourceKind = $sourceKind
                normalized = ConvertTo-GitHubUtcTimestamp `
                    -InputObject $timestamp `
                    -FieldName "fixture timestamp"
            }
        }
        "ruleset-created-at" {
            $payload = ConvertFrom-EncodedFixtureJson -Base64 $inputData.payloadBase64
            $value = ConvertTo-GitHubUtcTimestamp `
                -InputObject $payload.created_at `
                -FieldName "Managed ruleset read-back created_at"
        }
        "probe-evidence" {
            $value = Get-ProbeEvidence -PullRequest ([int]$inputData.pullNumber)
        }
        "rollback-contract" {
            $payload = ConvertFrom-EncodedFixtureJson -Base64 $inputData.payloadBase64
            [void](Set-GitHubJsonTimestampContract `
                -InputObject $payload `
                -Context "rollback fixture")
            [void](Invoke-TrustedModel `
                -Operation "assert-safe-rollback" `
                -InputObject $payload)
            $value = $payload
        }
        default { throw "unsupported fixture operation" }
    }
    $result = [ordered]@{ ok = $true; value = $value; calls = $calls.ToArray() }
} catch {
    $result = [ordered]@{ ok = $false; error = $_.Exception.Message; calls = $calls.ToArray() }
}
ConvertTo-Json -InputObject $result -Depth 100 -Compress
