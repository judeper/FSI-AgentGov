<#
.SYNOPSIS
    Registers a Windows Scheduled Task that runs the unattended autodoc drafter daily against a
    dedicated checkout the task fully owns.

.DESCRIPTION
    The task runs scripts/autodoc_runner.py on a schedule. The runner is a no-op unless the
    AUTODOC_ENABLED environment variable is 'true' (the master activation switch), so
    registering the task does NOT by itself enable autonomous drafting.

    Dedicated checkout: the task operates on its OWN clone of the repository (-CheckoutPath, default
    a sibling '<repo>.autodoc'), NOT the operator's working tree. This script clones it once at
    registration (seeding the idempotency ledger from the operator's checkout if present). Each run
    the task hard-syncs that checkout to origin/<base> (fetch + checkout + reset --hard) so the runner
    always sees the latest merged Learn Monitor report — without ever touching the operator's working
    tree, branches, or uncommitted changes. The sync is fail-closed: any fetch/checkout/reset error
    throws before the runner starts.

    The task runs as the current user, inheriting that user's GitHub Copilot CLI authentication (the
    licensed account) for drafting.

    For GitHub writes (push / PR / escalation issue) the runner calls bare `git push origin` and
    `gh`, which would otherwise use the machine's *active* GitHub account. On a box whose active
    account is an Enterprise Managed User (EMU), that account is denied write access (HTTP 403) to a
    personal repo. The task therefore authenticates every write as -PushAccount: at task time it
    resolves that account's token from the gh keyring (no static secret is stored) into GH_TOKEN, and
    the dedicated checkout's local .git/config routes git's github.com credentials through
    `gh auth git-credential` (which uses that GH_TOKEN). The override lives in the checkout's config,
    so the operator's interactive git/gh accounts are untouched.

    Prerequisite: the repo must have the `autodoc` and `escalate` labels (the runner attaches them to
    PRs/issues). Create the missing one(s) once with, e.g.:
        gh label create autodoc --color 0E8A16 --description "Automated Learn Monitor documentation pipeline"

.PARAMETER RepoPath
    Absolute path to the operator's repository working tree (e.g. C:\dev\FSI-AgentGov). Used to
    resolve the origin URL and to seed the ledger; the task itself runs against -CheckoutPath.

.PARAMETER CheckoutPath
    Absolute path to the dedicated checkout the task owns and hard-syncs each run. Defaults to a
    sibling '<RepoPath>.autodoc'. Cloned from the operator repo's origin if it does not yet exist.
    Must differ from -RepoPath (the task hard-resets this checkout and must never target the
    operator's working tree).

.PARAMETER DraftModel
    Copilot model id used to DRAFT edits (e.g. a strong model).

.PARAMETER ReviewModel
    Copilot model id used for the INDEPENDENT review. Must be a DIFFERENT model family than
    DraftModel so the author never grades its own work.

.PARAMETER TaskName
    Scheduled task name. Defaults to 'FSI-AgentGov-Autodoc'.

.PARAMETER AtTime
    Daily start time (HH:mm, host local time). Default '12:30' (after the daily Learn Monitor).

.PARAMETER PythonExe
    Python executable to run the runner with. Default 'python'.

.PARAMETER PushAccount
    GitHub account used for all repository writes (push, PR, escalation issues). Its token is read
    from the gh keyring at task time and used for both git and gh. Default 'judeper'.

.EXAMPLE
    ./Register-AutodocTask.ps1 -RepoPath C:\dev\FSI-AgentGov -DraftModel claude-opus-4.8 -ReviewModel gpt-5.5

.NOTES
    Remove with:  Unregister-ScheduledTask -TaskName 'FSI-AgentGov-Autodoc' -Confirm:$false
    Kill-switch:  set AUTODOC_ENABLED to anything but 'true' (or remove it) to make the runner inert.
    The dedicated checkout ('<repo>.autodoc' by default) can be deleted to force a fresh clone next
    registration; the runner's idempotency ledger lives in it (data/autodoc-ledger.json, untracked).
#>
[CmdletBinding(SupportsShouldProcess)]
param(
    [Parameter(Mandatory)]
    [string]$RepoPath,

    [Parameter(Mandatory)]
    [string]$DraftModel,

    [Parameter(Mandatory)]
    [string]$ReviewModel,

    [string]$TaskName = 'FSI-AgentGov-Autodoc',

    [ValidatePattern('^\d{2}:\d{2}$')]
    [string]$AtTime = '12:30',

    [string]$PythonExe = 'python',

    [string]$PushAccount = 'judeper',

    [string]$CheckoutPath = ''
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$resolvedRepo = (Resolve-Path -Path $RepoPath).Path

# Dedicated checkout the task fully owns. The runner only ever reads the report/ledger from, and
# writes branches inside, this checkout — so the task can hard-sync it to origin/<base> every run
# without ever touching the operator's working tree. Default: a sibling '<repo>.autodoc'.
if ([string]::IsNullOrWhiteSpace($CheckoutPath)) {
    $CheckoutPath = "$resolvedRepo.autodoc"
}
# The task hard-resets (git reset --hard) the dedicated checkout every run, so it must NEVER be the
# operator's working tree — that would discard their uncommitted work.
if ([System.IO.Path]::GetFullPath($CheckoutPath).TrimEnd('\', '/') -ieq [System.IO.Path]::GetFullPath($resolvedRepo).TrimEnd('\', '/')) {
    throw "CheckoutPath must differ from RepoPath. The task hard-resets the dedicated checkout each run; pointing it at the operator's working tree ($resolvedRepo) would discard uncommitted work."
}
$originUrl = (& git -C $resolvedRepo remote get-url origin 2>$null | Select-Object -First 1)
if ([string]::IsNullOrWhiteSpace($originUrl)) {
    throw "Could not resolve the 'origin' remote URL from $resolvedRepo."
}
$originUrl = $originUrl.Trim()

# The task hard-resets this checkout every run, so it must only ever touch a checkout THIS script
# created. We mark a freshly cloned checkout with a sentinel inside .git/ (which is never committed
# and survives `git reset --hard`). Adopting any existing checkout that lacks the sentinel is refused
# — this is robust where a string path comparison is not (junction/symlink aliases to the operator
# tree, 8.3 short paths, an unrelated repo pointed at by mistake).
$ownedMarker = Join-Path -Path $CheckoutPath -ChildPath '.git/autodoc-owned'
if (Test-Path -Path (Join-Path -Path $CheckoutPath -ChildPath '.git')) {
    if (-not (Test-Path -Path $ownedMarker)) {
        throw "CheckoutPath '$CheckoutPath' is an existing checkout that was not created by this script (no .git/autodoc-owned marker). The task hard-resets the dedicated checkout each run; refusing to adopt an unmanaged checkout (it may be the operator's working tree or another repo). Remove it or pass a fresh -CheckoutPath."
    }
    Write-Output "Using existing autodoc checkout: $CheckoutPath"
}
elseif (Test-Path -Path $CheckoutPath) {
    throw "CheckoutPath '$CheckoutPath' exists but is not a git checkout. Remove it or pass a different -CheckoutPath."
}
elseif ($PSCmdlet.ShouldProcess($CheckoutPath, "Clone $originUrl for the autodoc task")) {
    & git clone --quiet $originUrl $CheckoutPath
    if ($LASTEXITCODE -ne 0) { throw "git clone of $originUrl into $CheckoutPath failed (exit $LASTEXITCODE)." }
    # Claim the checkout so future runs/registrations know this script owns it (safe to hard-reset).
    Set-Content -Path $ownedMarker -Value "Created by Register-AutodocTask.ps1 for $TaskName" -Encoding ascii
    # Seed the idempotency ledger from the operator's checkout so the first task run does not
    # reprocess already-handled changes (the runner dedupes anyway, but this avoids the churn).
    $srcLedger = Join-Path -Path $resolvedRepo -ChildPath 'data/autodoc-ledger.json'
    $dstLedger = Join-Path -Path $CheckoutPath -ChildPath 'data/autodoc-ledger.json'
    if ((Test-Path -Path $srcLedger) -and -not (Test-Path -Path $dstLedger)) {
        Copy-Item -Path $srcLedger -Destination $dstLedger
        Write-Output "Seeded autodoc ledger into the dedicated checkout."
    }
}

# Absolute checkout path for the task command literals (works even under -WhatIf, when the clone has
# not been created and Resolve-Path would fail).
$resolvedCheckout = if (Test-Path -Path $CheckoutPath) { (Resolve-Path -Path $CheckoutPath).Path } else { [System.IO.Path]::GetFullPath($CheckoutPath) }
$runnerScript = Join-Path -Path $resolvedCheckout -ChildPath 'scripts/autodoc_runner.py'
if ((Test-Path -Path $resolvedCheckout) -and -not (Test-Path -Path $runnerScript)) {
    throw "Runner not found at $runnerScript in the autodoc checkout."
}

# Route the dedicated checkout's github.com credentials through `gh auth git-credential` (which uses
# the task's GH_TOKEN = the push account). This is set in the checkout's LOCAL config — a file — where
# the empty-value reset of the inherited (manager / gh-setup-git) helper works reliably. The earlier
# GIT_CONFIG_* env approach failed under the Task Scheduler's Windows PowerShell 5.1 host, which drops
# an empty-string env var so git reported "missing config value GIT_CONFIG_VALUE_0". The config lives
# in .git/config, so it survives the per-run `git reset --hard`. Idempotent (unset, then reset + add).
if ((Test-Path -Path (Join-Path -Path $resolvedCheckout -ChildPath '.git')) -and $PSCmdlet.ShouldProcess($resolvedCheckout, 'Configure github.com credential helper')) {
    & git -C $resolvedCheckout config --unset-all 'credential.https://github.com.helper' 2>$null
    & git -C $resolvedCheckout config 'credential.https://github.com.helper' ''
    if ($LASTEXITCODE -ne 0) { throw "Failed to reset the credential helper in $resolvedCheckout." }
    & git -C $resolvedCheckout config --add 'credential.https://github.com.helper' '!gh auth git-credential'
    if ($LASTEXITCODE -ne 0) { throw "Failed to set the credential helper in $resolvedCheckout." }
}

# The task command: prune stale worktrees, then run the unattended drafter. The runner itself
# is gated on $env:AUTODOC_ENABLED so this is safe to register before going live.
#
# Paths/models are embedded as single-quoted PowerShell literals (spaces/quotes safe), and the
# whole script is passed via -EncodedCommand so Task Scheduler's command-line parsing cannot
# mangle nested quotes (e.g. "C:\Program Files\Python\python.exe" or a repo path with spaces).
function ConvertTo-PSLiteral {
    param([string]$Value)
    return "'" + ($Value -replace "'", "''") + "'"
}

$checkoutLit = ConvertTo-PSLiteral -Value $resolvedCheckout
$runnerLit = ConvertTo-PSLiteral -Value $runnerScript
$pythonLit = ConvertTo-PSLiteral -Value $PythonExe
$draftLit = ConvertTo-PSLiteral -Value $DraftModel
$reviewLit = ConvertTo-PSLiteral -Value $ReviewModel
$pushLit = ConvertTo-PSLiteral -Value $PushAccount
# The runner targets 'main' (its only supported base branch), so keep the checkout sync on 'main'.
$baseLit = ConvertTo-PSLiteral -Value 'main'
$originRefLit = ConvertTo-PSLiteral -Value 'origin/main'

# Authenticate every git/PR write as the push account for the duration of the runner process only.
# The runner uses bare `git push origin` and `gh`; without this they would use the machine's active
# GitHub account (denied 403 on an EMU-licensed box). We resolve the push account's token from the
# gh keyring AT TASK TIME (no static secret persisted) into GH_TOKEN. Git's github.com credential
# helper is set to `!gh auth git-credential` in the dedicated checkout's LOCAL config (see below), so
# `git` and `gh` both authenticate with that GH_TOKEN. The `$env:` references are escaped so they
# evaluate inside the task, not now.
#
# Fail closed: if the token cannot be resolved (keyring unreachable, account absent, task running
# without an interactive session), THROW before the runner starts — otherwise GH_TOKEN would be empty
# and the runner would silently fall back to the machine's active account (the denied/EMU one).
$authSetup = @(
    "`$autodocToken=(gh auth token --user $pushLit)",
    "if (`$LASTEXITCODE -ne 0 -or [string]::IsNullOrWhiteSpace(`$autodocToken)) { throw 'Register-AutodocTask: could not resolve a GitHub token for the push account from the gh keyring; aborting so the runner does not write as the wrong/denied account.' }",
    "`$env:GH_TOKEN=`$autodocToken"
) -join '; '

# Before each run, hard-sync the dedicated checkout to the latest origin/<base> so the runner reads
# the newest merged Learn Monitor report. Fail closed: any git error throws before the runner starts,
# rather than silently processing a stale report. reset --hard does not remove untracked files, so the
# idempotency ledger (data/autodoc-ledger.json) survives. This only ever touches the dedicated
# checkout, never the operator's working tree.
$syncSetup = @(
    "git -C $checkoutLit fetch --quiet origin $baseLit",
    "if (`$LASTEXITCODE -ne 0) { throw 'Register-AutodocTask: git fetch failed in the autodoc checkout; aborting.' }",
    "git -C $checkoutLit checkout --quiet $baseLit",
    "if (`$LASTEXITCODE -ne 0) { throw 'Register-AutodocTask: git checkout of the base branch failed; aborting.' }",
    "git -C $checkoutLit reset --hard --quiet $originRefLit",
    "if (`$LASTEXITCODE -ne 0) { throw 'Register-AutodocTask: git reset --hard to origin failed; aborting.' }",
    "git -C $checkoutLit worktree prune"
) -join '; '

$innerCommand = "$authSetup; $syncSetup; & $pythonLit $runnerLit --repo $checkoutLit --draft-model $draftLit --review-model $reviewLit"
$encodedCommand = [Convert]::ToBase64String([System.Text.Encoding]::Unicode.GetBytes($innerCommand))
$argument = "-NoProfile -ExecutionPolicy Bypass -EncodedCommand $encodedCommand"

$action = New-ScheduledTaskAction -Execute 'powershell.exe' -Argument $argument -WorkingDirectory $resolvedCheckout
$trigger = New-ScheduledTaskTrigger -Daily -At $AtTime
$settings = New-ScheduledTaskSettingsSet -StartWhenAvailable -ExecutionTimeLimit (New-TimeSpan -Hours 2)
$description = 'FSI-AgentGov autonomous Learn Monitor documentation drafter. Inert unless AUTODOC_ENABLED=true.'

if ($PSCmdlet.ShouldProcess($TaskName, 'Register scheduled task')) {
    Register-ScheduledTask -TaskName $TaskName -Action $action -Trigger $trigger -Settings $settings -Description $description -Force | Out-Null
    Write-Output "Registered scheduled task '$TaskName' (daily at $AtTime)."
    Write-Output "  Dedicated checkout: $resolvedCheckout (hard-synced to origin/main each run)"
    Write-Output "  Writes as: $PushAccount (token from gh keyring at run time)"
    Write-Output "The runner stays inert until AUTODOC_ENABLED=true. To activate, set that env var; to stop, unset it or run: Unregister-ScheduledTask -TaskName '$TaskName' -Confirm:`$false"
}
