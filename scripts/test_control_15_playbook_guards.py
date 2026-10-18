"""Offline regression coverage for the documented DLP evidence examples."""

import json
import re
import shutil
import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
PLAYBOOKS = ROOT / "docs" / "playbooks" / "control-implementations"


def block_with(path, function):
    text = path.read_text(encoding="utf-8")
    return next(
        block
        for block in re.findall(r"```powershell\s*\n(.*?)```", text, re.S)
        if f"function {function} " in block
    )


def test_cap06_requires_retained_trigger_and_deadline():
    text = (PLAYBOOKS / "1.7" / "verification-testing.md").read_text(
        encoding="utf-8"
    )
    assert "function Get-FsiDlpOverrideEvidence " in text
    assert "[Parameter(Mandatory)] [ValidateNotNullOrEmpty()] [string]$Marker" in text
    assert "[Parameter(Mandatory)] [datetimeoffset]$TriggeredAtUtc" in text
    assert "[Parameter(Mandatory)] [datetimeoffset]$ObservationDeadlineUtc" in text


def test_wrapper_invokes_canonical_writer_and_verifies_hashes():
    block = block_with(
        PLAYBOOKS / "1.5" / "powershell-setup.md", "Invoke-FsiControl15Audit"
    )
    assert "Write-FsiEvidence -Object $results[$k] -Name $k" in block
    assert "Get-FileHash" in block
    assert "manifest.json" in block
    assert "summary.txt" in block


def test_downstream_assessment_preserves_enforcement_boundaries():
    controls = {
        entry["id"]: entry
        for entry in json.loads(
            (ROOT / "assessment" / "manifest" / "controls.json").read_text(
                encoding="utf-8"
            )
        )
    }
    encryption = controls["1.15"]["facilitatorNotes"]["followUp"]
    assert "DKE is file-level protection" in encryption
    assert "VIEW and EXTRACT" in encryption
    assert "only supported AI-app encryption path" not in encryption
    assert "separately deployed" in controls["1.17"]["yesBar"]
    assert "not agent-level label inheritance" in next(
        check["description"] for check in controls["1.26"]["checks"]
        if check["check_id"] == "1.26.b"
    )


def test_upload_tests_do_not_pass_unsupported_inspection_paths():
    upload = (PLAYBOOKS / "1.26" / "verification-testing.md").read_text(
        encoding="utf-8"
    )
    mime = (PLAYBOOKS / "1.25" / "verification-testing.md").read_text(
        encoding="utf-8"
    )
    assert "auto-labeling policies covering the Dataverse environment" not in upload
    assert "unsupported direct-upload gap not passed" in upload
    assert "not automatically a Purview DLP policy match" in mime


@pytest.mark.skipif(shutil.which("pwsh") is None, reason="PowerShell is not installed")
def test_cap06_offline_event_and_deadline_cases(tmp_path):
    block = block_with(
        PLAYBOOKS / "1.7" / "verification-testing.md", "Get-FsiDlpOverrideEvidence"
    )
    harness = r"""
Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'
__FUNCTION__
function Search-AuditLogPaged {
    [CmdletBinding()]
    param($StartDate, $EndDate, $RecordTypes)
    if ($script:QueryFails) { throw 'query failed' }
    if ($StartDate -ne ([datetimeoffset]'2026-10-01T00:00:00Z').UtcDateTime) {
        throw 'Trigger window was not retained'
    }
    $script:Rows
}
function Assert-Status($Expected, $AsOf) {
    $result = Get-FsiDlpOverrideEvidence -Marker 'retained-marker' `
        -TriggeredAtUtc '2026-10-01T00:00:00Z' `
        -ObservationDeadlineUtc '2026-10-02T00:00:00Z' -AsOfUtc $AsOf
    if ($result.status -ne $Expected -or $result.marker -ne 'retained-marker') {
        throw "Expected $Expected; got $($result.status)"
    }
}
$script:QueryFails = $false
$script:Rows = @()
Assert-Status PENDING '2026-10-01T12:00:00Z'
Assert-Status FAIL '2026-10-02T00:00:00Z'
Assert-Status FAIL '2026-10-04T00:00:00Z'
foreach ($serialized in @($false, $true)) {
    $exception = [pscustomobject]@{
        Reason = 'Override'; Justification = 'retained-marker'
    }
    if ($serialized) { $exception = $exception | ConvertTo-Json -Compress }
    $script:Rows = @([pscustomobject]@{
        AuditData = (@{ Operation = 'DlpRuleUndo'; ExceptionInfo = $exception } |
            ConvertTo-Json -Depth 5 -Compress)
    })
    Assert-Status PASS '2026-10-01T12:00:00Z'
    Assert-Status PASS '2026-10-04T00:00:00Z'
}
$script:Rows = @([pscustomobject]@{
    AuditData = '{"Operation":"DlpRuleUndo","ExceptionInfo":"{\"Reason\":\"Override\",\"Justification\":\"different-marker\"}"}'
})
Assert-Status FAIL '2026-10-04T00:00:00Z'
$script:Rows = @([pscustomobject]@{
    AuditData = '{"Operation":"DlpRuleUndo","ExceptionInfo":"not-json"}'
})
$threw = $false
try { Assert-Status FAIL '2026-10-04T00:00:00Z' } catch { $threw = $true }
if (-not $threw) { throw 'Malformed evidence was treated as absence' }
$script:QueryFails = $true
$threw = $false
try { Assert-Status FAIL '2026-10-04T00:00:00Z' } catch { $threw = $true }
if (-not $threw) { throw 'Query failure was treated as absence' }
'CAP-06 offline cases passed'
""".replace("__FUNCTION__", block)
    script = tmp_path / "cap06.ps1"
    script.write_text(harness, encoding="utf-8")
    result = subprocess.run(
        ["pwsh", "-NoProfile", "-File", str(script)],
        capture_output=True,
        text=True,
        check=False,
        timeout=60,
    )
    assert result.returncode == 0, result.stdout + result.stderr


@pytest.mark.skipif(shutil.which("pwsh") is None, reason="PowerShell is not installed")
def test_wrapper_offline_manifest_and_failure_cases(tmp_path):
    wrapper = block_with(
        PLAYBOOKS / "1.5" / "powershell-setup.md", "Invoke-FsiControl15Audit"
    )
    writer = block_with(
        ROOT / "docs" / "playbooks" / "_shared" / "powershell-baseline.md",
        "Write-FsiEvidence",
    )
    harness = r"""
Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'
__WRAPPER__
$script:Connections = 0
function Initialize-FsiDlpSession {
    $script:Connections++
    [pscustomobject]@{ Status = 'Pending' }
}
function Connect-ExchangeOnline { }
function Get-FsiDlpCoverage { [pscustomobject]@{ Status = 'Pending' } }
function Get-FsiCopilotDlpPolicies { [pscustomobject]@{ Status = 'Pending' } }
function Test-FsiPolicyTipOverrideSettings { [pscustomobject]@{ Status = 'Pending' } }
function Get-FsiSensitivityLabelInventory { [pscustomobject]@{ Status = 'Pending' } }
function Get-FsiAdaptiveProtectionStatus { [pscustomobject]@{ Status = 'Pending' } }
function Get-FsiDlpAuditEvents { [pscustomobject]@{ Status = 'Pending' } }
function Invoke-Fixture($Path) {
    Invoke-FsiControl15Audit -TenantId 'offline' -UserPrincipalName 'offline' `
        -EvidencePath $Path -Confirm:$false
}
$threw = $false
try { Invoke-Fixture (Join-Path $PSScriptRoot 'missing') } catch { $threw = $true }
if (-not $threw -or $script:Connections -ne 0) {
    throw 'Missing writer did not fail before connections'
}
$module = New-Module -Name FsiEvidenceFixture -ScriptBlock {
__WRITER__
    Export-ModuleMember -Function Write-FsiEvidence
}
Import-Module $module
$path = Join-Path $PSScriptRoot 'healthy'
$rollup = @(Invoke-Fixture $path)
$manifest = @(Get-Content (Join-Path $path 'manifest.json') -Raw | ConvertFrom-Json)
if ($rollup.Count -ne 8 -or $manifest.Count -ne 10) {
    throw 'Expected eight result artifacts plus summary and finalized transcript'
}
foreach ($entry in $manifest) {
    $artifact = Join-Path $path $entry.file
    if ((Get-FileHash $artifact).Hash -ne $entry.sha256 -or
        (Get-Item $artifact).Length -ne $entry.bytes) {
        throw 'Finalized artifact hash/length mismatch'
    }
}
$threw = $false
try { Invoke-Fixture $path } catch { $threw = $true }
if (-not $threw) { throw 'Existing run directory was overwritten' }
Remove-Module FsiEvidenceFixture
$badWriter = New-Module -Name FsiBrokenEvidenceFixture -ScriptBlock {
__WRITER__
    Rename-Item Function:Write-FsiEvidence Write-FixtureEvidence
    function Write-FsiEvidence {
        param($Object, $Name, $EvidencePath)
        $path = Write-FixtureEvidence -Object $Object -Name $Name -EvidencePath $EvidencePath
        Add-Content -LiteralPath $path -Value 'tampered'
        $path
    }
    Export-ModuleMember -Function Write-FsiEvidence
}
Import-Module $badWriter
$threw = $false
try { Invoke-Fixture (Join-Path $PSScriptRoot 'tampered') } catch { $threw = $true }
if (-not $threw) { throw 'Corrupt writer returned a success-shaped rollup' }
'Wrapper offline cases passed'
""".replace("__WRAPPER__", wrapper).replace("__WRITER__", writer)
    script = tmp_path / "wrapper.ps1"
    script.write_text(harness, encoding="utf-8")
    result = subprocess.run(
        ["pwsh", "-NoProfile", "-File", str(script)],
        capture_output=True,
        text=True,
        check=False,
        timeout=60,
    )
    assert result.returncode == 0, result.stdout + result.stderr
