<#
.SYNOPSIS
  Push to origin as the 'judeper' GitHub account, with active-account guard
  and post-push remote-SHA verification.

.DESCRIPTION
  The 'gh' CLI maintains a single "active" auth account per host, and that
  active account can flip silently mid-session (for example, after another
  tool runs `gh auth switch`, after `gh auth login`, or when an MCP/extension
  refreshes credentials). AGENTS.md calls this out as a footgun: pushes can
  end up authored or attributed to the wrong account if the active GH user
  isn't asserted right before `git push`.

  This wrapper:
    1. Captures the currently-active gh account (so it can be restored).
    2. Switches the active account to 'judeper' and asserts the switch
       actually took effect (`gh api user -q .login`).
    3. Runs `git push @args` (any pass-through args you supply).
    4. Verifies the remote branch tip SHA matches local HEAD.
    5. Restores the prior active account (only if it wasn't 'judeper').

  No tokens are ever written to disk — auth flows entirely through the gh
  CLI's credential store.

.EXAMPLE
  pwsh -File scripts/push-as-judeper.ps1
  pwsh -File scripts/push-as-judeper.ps1 -u origin HEAD
  pwsh -File scripts/push-as-judeper.ps1 origin infra/scripts-batch
#>
[CmdletBinding()]
param(
    [Parameter(ValueFromRemainingArguments = $true)]
    $RestArgs
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

function Get-ActiveGhAccount {
    # gh auth status writes to stderr; capture both streams.
    $raw = & gh auth status 2>&1 | Out-String
    foreach ($line in ($raw -split "`r?`n")) {
        if ($line -match 'account\s+(\S+)\s+\(active\)') {
            return $Matches[1]
        }
        if ($line -match 'Logged in to [^ ]+ as (\S+).*\(active\)') {
            return $Matches[1]
        }
    }
    return $null
}

$priorAccount = Get-ActiveGhAccount
if ($priorAccount) {
    Write-Host "Prior active gh account: $priorAccount"
} else {
    Write-Host "Prior active gh account: <unknown>"
}

Write-Host "Switching active gh account to 'judeper'..."
& gh auth switch -u judeper
if ($LASTEXITCODE -ne 0) {
    throw "gh auth switch -u judeper failed (exit $LASTEXITCODE)."
}

$current = (& gh api user -q .login).Trim()
if ($current -ne 'judeper') {
    throw "Active gh account is '$current', expected 'judeper'. Aborting push."
}
Write-Host "Verified active gh account: $current"

$branch = (& git rev-parse --abbrev-ref HEAD).Trim()
$localSha = (& git rev-parse HEAD).Trim()
Write-Host "Local HEAD: $branch @ $localSha"

try {
    Write-Host "Running: git push $($RestArgs -join ' ')"
    if ($RestArgs) {
        & git push @RestArgs
    } else {
        & git push
    }
    if ($LASTEXITCODE -ne 0) {
        throw "git push failed (exit $LASTEXITCODE)."
    }

    Write-Host "Verifying remote SHA for refs/heads/$branch ..."
    $remoteSha = (& gh api "repos/judeper/FSI-AgentGov/commits/$branch" -q .sha).Trim()
    if ($remoteSha -ne $localSha) {
        throw "Remote SHA mismatch: local=$localSha remote=$remoteSha"
    }
    Write-Host "Remote SHA matches local HEAD: $remoteSha"
}
finally {
    if ($priorAccount -and $priorAccount -ne 'judeper') {
        Write-Host "Restoring prior gh account: $priorAccount"
        & gh auth switch -u $priorAccount | Out-Null
    } else {
        Write-Host "No prior-account restore needed."
    }
}
