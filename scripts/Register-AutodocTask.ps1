<#
.SYNOPSIS
    Registers a Windows Scheduled Task that runs the unattended autodoc drafter daily.

.DESCRIPTION
    The task runs scripts/autodoc_runner.py on a schedule. The runner is a no-op unless the
    AUTODOC_ENABLED environment variable is 'true' (the master activation switch), so
    registering the task does NOT by itself enable autonomous drafting.

    The task action prunes stale git worktrees first (in case a prior run crashed mid-draft),
    then invokes the runner. It runs as the current user, inheriting that user's GitHub Copilot
    CLI authentication (the licensed account) for drafting.

    For GitHub writes (push / PR / escalation issue) the runner calls bare `git push origin` and
    `gh`, which would otherwise use the machine's *active* GitHub account. On a box whose active
    account is an Enterprise Managed User (EMU), that account is denied write access (HTTP 403) to a
    personal repo. The task therefore authenticates every write as -PushAccount: at task time it
    resolves that account's token from the gh keyring (no static secret is stored) into GH_TOKEN and
    routes git's github.com credentials through `gh auth git-credential` via a process-scoped
    GIT_CONFIG override. These environment variables live only inside the task process, so the
    operator's interactive git/gh accounts are untouched.

    Prerequisite: the repo must have the `autodoc` and `escalate` labels (the runner attaches them to
    PRs/issues). Create the missing one(s) once with, e.g.:
        gh label create autodoc --color 0E8A16 --description "Automated Learn Monitor documentation pipeline"

.PARAMETER RepoPath
    Absolute path to the repository working tree (e.g. C:\dev\FSI-AgentGov).

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

    [string]$PushAccount = 'judeper'
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$resolvedRepo = (Resolve-Path -Path $RepoPath).Path
$runnerScript = Join-Path -Path $resolvedRepo -ChildPath 'scripts/autodoc_runner.py'
if (-not (Test-Path -Path $runnerScript)) {
    throw "Runner not found at $runnerScript. Pass the repository root via -RepoPath."
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

$repoLit = ConvertTo-PSLiteral -Value $resolvedRepo
$runnerLit = ConvertTo-PSLiteral -Value $runnerScript
$pythonLit = ConvertTo-PSLiteral -Value $PythonExe
$draftLit = ConvertTo-PSLiteral -Value $DraftModel
$reviewLit = ConvertTo-PSLiteral -Value $ReviewModel
$pushLit = ConvertTo-PSLiteral -Value $PushAccount

# Authenticate every git/PR write as the push account for the duration of the runner process only.
# The runner uses bare `git push origin` and `gh`; without this they would use the machine's active
# GitHub account (denied 403 on an EMU-licensed box). We resolve the push account's token from the
# gh keyring AT TASK TIME (no static secret persisted) into GH_TOKEN, and a process-scoped GIT_CONFIG
# override routes git's github.com credentials through `gh auth git-credential` so the bare push uses
# the same token. The `$env:` references are escaped so they evaluate inside the task, not now.
$authSetup = @(
    "`$env:GH_TOKEN=(gh auth token --user $pushLit)",
    "`$env:GIT_CONFIG_COUNT='2'",
    "`$env:GIT_CONFIG_KEY_0='credential.https://github.com.helper'",
    "`$env:GIT_CONFIG_VALUE_0=''",
    "`$env:GIT_CONFIG_KEY_1='credential.https://github.com.helper'",
    "`$env:GIT_CONFIG_VALUE_1='!gh auth git-credential'"
) -join '; '

$innerCommand = "$authSetup; git -C $repoLit worktree prune; & $pythonLit $runnerLit --repo $repoLit --draft-model $draftLit --review-model $reviewLit"
$encodedCommand = [Convert]::ToBase64String([System.Text.Encoding]::Unicode.GetBytes($innerCommand))
$argument = "-NoProfile -ExecutionPolicy Bypass -EncodedCommand $encodedCommand"

$action = New-ScheduledTaskAction -Execute 'powershell.exe' -Argument $argument -WorkingDirectory $resolvedRepo
$trigger = New-ScheduledTaskTrigger -Daily -At $AtTime
$settings = New-ScheduledTaskSettingsSet -StartWhenAvailable -ExecutionTimeLimit (New-TimeSpan -Hours 2)
$description = 'FSI-AgentGov autonomous Learn Monitor documentation drafter. Inert unless AUTODOC_ENABLED=true.'

if ($PSCmdlet.ShouldProcess($TaskName, 'Register scheduled task')) {
    Register-ScheduledTask -TaskName $TaskName -Action $action -Trigger $trigger -Settings $settings -Description $description -Force | Out-Null
    Write-Output "Registered scheduled task '$TaskName' (daily at $AtTime) running: $runnerScript"
    Write-Output "The runner stays inert until AUTODOC_ENABLED=true. To activate, set that env var; to stop, unset it or run: Unregister-ScheduledTask -TaskName '$TaskName' -Confirm:`$false"
}
