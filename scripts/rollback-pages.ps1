<#
.SYNOPSIS
  Re-deploy GitHub Pages from a prior known-good tag. Target MTTR ~2min.

.DESCRIPTION
  Operates on tags of the form 'pages-good-<SHA>'. By default rolls back to
  the second-most-recent such tag (i.e. the previous good deploy). Triggers
  the publish_docs.yml workflow at that ref via `gh workflow run`, then polls
  the production /version.json until its SHA matches the rollback target's
  commit SHA (or 5 minutes elapses).

  NOTE: Auto-tagging 'pages-good-<SHA>' after each successful publish requires
  a small edit to .github/workflows/publish_docs.yml (a final tag step on
  success). This script is ready to use as soon as that lands; until then it
  operates on whatever 'pages-good-*' tags exist in the repo.

.PARAMETER Tag
  Specific tag to roll back to. If omitted, defaults to the second-most-recent
  'pages-good-*' tag by creation date.

.EXAMPLE
  pwsh -File scripts/rollback-pages.ps1
  pwsh -File scripts/rollback-pages.ps1 -Tag pages-good-abc1234
#>
[CmdletBinding()]
param(
    [string]$Tag,
    [string]$VersionUrl = 'https://judeper.github.io/FSI-AgentGov/version.json',
    [int]$TimeoutSeconds = 300,
    [int]$PollIntervalSeconds = 15
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

# Fetch tags + their creation dates, sort desc.
& git fetch --tags --quiet
$tagLines = & git for-each-ref --sort=-creatordate --format='%(refname:short)' 'refs/tags/pages-good-*'
if (-not $tagLines) {
    throw "No 'pages-good-*' tags found. (Hint: publish_docs.yml needs to auto-tag successful deploys.)"
}
$tags = @($tagLines)

if (-not $Tag) {
    if ($tags.Count -lt 2) {
        throw "Need at least 2 'pages-good-*' tags to default to 'previous good'. Found: $($tags.Count). Pass -Tag explicitly."
    }
    $Tag = $tags[1]
    Write-Host "Defaulting to previous-good tag: $Tag (most recent is $($tags[0]))"
} else {
    if ($tags -notcontains $Tag) {
        throw "Tag '$Tag' is not in the pages-good-* set."
    }
    Write-Host "Rolling back to specified tag: $Tag"
}

$targetSha = (& git rev-list -n 1 $Tag).Trim()
Write-Host "Target commit SHA: $targetSha"

Write-Host "Triggering publish_docs.yml @ $Tag ..."
& gh workflow run publish_docs.yml --ref $Tag
if ($LASTEXITCODE -ne 0) {
    throw "gh workflow run failed (exit $LASTEXITCODE)."
}

Write-Host "Polling $VersionUrl every ${PollIntervalSeconds}s up to ${TimeoutSeconds}s ..."
$deadline = (Get-Date).AddSeconds($TimeoutSeconds)
$success = $false
while ((Get-Date) -lt $deadline) {
    Start-Sleep -Seconds $PollIntervalSeconds
    try {
        $resp = Invoke-RestMethod -Uri $VersionUrl -TimeoutSec 10 -Headers @{ 'Cache-Control' = 'no-cache' }
        $liveSha = $null
        foreach ($prop in 'sha','commit','commitSha','gitSha') {
            if ($resp.PSObject.Properties.Name -contains $prop) { $liveSha = [string]$resp.$prop; break }
        }
        if ($liveSha) {
            Write-Host "  live sha: $liveSha"
            if ($liveSha.StartsWith($targetSha) -or $targetSha.StartsWith($liveSha)) {
                $success = $true
                break
            }
        } else {
            Write-Host "  (version.json had no recognizable sha field)"
        }
    } catch {
        Write-Host "  fetch failed: $($_.Exception.Message)"
    }
}

if ($success) {
    Write-Host "ROLLBACK SUCCESS: $VersionUrl now serves $targetSha (tag $Tag)."
    exit 0
}

$body = @"
Rollback to ``$Tag`` (commit ``$targetSha``) did not propagate to $VersionUrl within ${TimeoutSeconds}s.

Triggered: ``gh workflow run publish_docs.yml --ref $Tag``

Investigate the publish_docs.yml run and Pages deployment status.
"@
Write-Warning "Rollback did not verify within timeout. Opening tracking issue..."
& gh issue create --title "rollback failed: $Tag" --body $body
exit 1
