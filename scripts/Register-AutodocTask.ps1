<#
.SYNOPSIS
    Registers a Windows Scheduled Task that runs the unattended autodoc drafter daily.

.DESCRIPTION
    The task runs scripts/autodoc_runner.py on a schedule. The runner is a no-op unless the
    AUTODOC_ENABLED environment variable is 'true' (the master activation switch), so
    registering the task does NOT by itself enable autonomous drafting.

    The task action prunes stale git worktrees first (in case a prior run crashed mid-draft),
    then invokes the runner. It runs as the current user, inheriting that user's GitHub Copilot
    CLI authentication (the licensed account) and the gh/git credentials used for pushes.

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

    [string]$PythonExe = 'python'
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
$innerCommand = @(
    "git -C `"$resolvedRepo`" worktree prune;",
    "& `"$PythonExe`" `"$runnerScript`" --repo `"$resolvedRepo`"",
    "--draft-model `"$DraftModel`" --review-model `"$ReviewModel`""
) -join ' '

$argument = "-NoProfile -ExecutionPolicy Bypass -Command `"$innerCommand`""

$action = New-ScheduledTaskAction -Execute 'powershell.exe' -Argument $argument -WorkingDirectory $resolvedRepo
$trigger = New-ScheduledTaskTrigger -Daily -At $AtTime
$settings = New-ScheduledTaskSettingsSet -StartWhenAvailable -ExecutionTimeLimit (New-TimeSpan -Hours 2)
$description = 'FSI-AgentGov autonomous Learn Monitor documentation drafter. Inert unless AUTODOC_ENABLED=true.'

if ($PSCmdlet.ShouldProcess($TaskName, 'Register scheduled task')) {
    Register-ScheduledTask -TaskName $TaskName -Action $action -Trigger $trigger -Settings $settings -Description $description -Force | Out-Null
    Write-Output "Registered scheduled task '$TaskName' (daily at $AtTime) running: $runnerScript"
    Write-Output "The runner stays inert until AUTODOC_ENABLED=true. To activate, set that env var; to stop, unset it or run: Unregister-ScheduledTask -TaskName '$TaskName' -Confirm:`$false"
}
