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

$ast = [System.Management.Automation.Language.Parser]::ParseFile($operator, [ref]$null, [ref]$null)
foreach ($definition in $ast.FindAll({
    param($node)
    $node -is [System.Management.Automation.Language.FunctionDefinitionAst]
}, $false)) {
    . ([scriptblock]::Create($definition.Extent.Text))
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
                $expiry = if ($inputData.expiry -is [string]) {
                    $inputData.expiry
                } else {
                    [DateTimeOffset]::UtcNow.AddSeconds([int]$inputData.expiry).ToString("yyyy-MM-ddTHH:mm:ssZ")
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

try {
    switch ($inputData.operation) {
        "repositories" { $value = @(Get-AllInstallationRepositories -InstallationToken "TEST_FIXTURE_INSTALLATION") }
        "installations" { $value = @(Get-AllAppInstallations -Jwt "TEST_FIXTURE_JWT") }
        "assert-installation" { $value = Assert-AppInstallation -Jwt "TEST_FIXTURE_JWT" }
        "transport" { $value = Invoke-AppJson -Endpoint "installation/repositories" -BearerToken "TEST_FIXTURE_INSTALLATION" }
        default { throw "unsupported fixture operation" }
    }
    $result = [ordered]@{ ok = $true; value = $value; calls = $calls.ToArray() }
} catch {
    $result = [ordered]@{ ok = $false; error = $_.Exception.Message; calls = $calls.ToArray() }
}
ConvertTo-Json -InputObject $result -Depth 100 -Compress
