#requires -Version 5.1
[CmdletBinding()]
param(
  [string]$Branch = "main",
  [string]$ConfigPath = ".github/branch-protection.json"
)
$ErrorActionPreference = "Stop"
$repo = "judeper/FSI-AgentGov"

if (!(Test-Path $ConfigPath)) { throw "Config not found: $ConfigPath" }

# Switch to push-capable account
$prior = (gh api user -q .login)
if ($prior -ne "judeper") {
  gh auth switch -u judeper | Out-Null
}

try {
  $body = Get-Content $ConfigPath -Raw
  Write-Host "Applying branch protection to $repo`:$Branch ..."
  $resp = $body | gh api -X PUT "repos/$repo/branches/$Branch/protection" --input -
  Write-Host "Response:`n$resp"
  $applied = $resp | ConvertFrom-Json
  $expectedCtx = (Get-Content $ConfigPath | ConvertFrom-Json).required_status_checks.contexts
  $actualCtx = $applied.required_status_checks.contexts
  $missing = $expectedCtx | Where-Object { $_ -notin $actualCtx }
  if ($missing) { throw "Contexts missing from applied protection: $($missing -join ',')" }
  Write-Host "OK: branch protection applied. Required contexts: $($actualCtx -join ', ')"
} finally {
  if ($prior -ne "judeper") {
    gh auth switch -u $prior | Out-Null
  }
}
