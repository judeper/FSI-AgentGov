"""Regression tests for runnable playbook PowerShell callable validation."""

from __future__ import annotations

import re
import shutil
import subprocess
import sys
import textwrap
from pathlib import Path

import pytest

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

import verify_playbook_powershell_helpers as verifier  # noqa: E402


def _read_control_112_markdown() -> str:
    return (SCRIPT_DIR.parent / verifier.DOC_PATH).read_text(encoding="utf-8")


TENANT_ID = "11111111-2222-3333-4444-555555555555"


def _ps_quote_path(path: Path) -> str:
    return str(path).replace("'", "''")


def _run_control_112_extracted_sweep(workspace_mode: str) -> subprocess.CompletedProcess[str]:
    markdown = _read_control_112_markdown()
    runbook = verifier._extract_runbook_fence(markdown)

    artifact_root = SCRIPT_DIR / ".runtime-test-artifacts"
    case_root = artifact_root / f"agt112-{workspace_mode}"
    if case_root.exists():
        shutil.rmtree(case_root)
    case_root.mkdir(parents=True, exist_ok=True)

    try:
        runbook_path = case_root / "Invoke-Agt112Sweep.extracted.ps1"
        runbook_path.write_text(runbook, encoding="utf-8")

        evidence_path = case_root / "evidence"
        exports_path = case_root / "exports"
        evidence_path.mkdir(parents=True, exist_ok=True)
        exports_path.mkdir(parents=True, exist_ok=True)

        policy_export_path = exports_path / "policy.csv"
        alert_export_path = exports_path / "alerts.csv"
        harness_path = case_root / "run-extracted-sweep.ps1"

        harness_script = textwrap.dedent(
            f"""
            Set-StrictMode -Version Latest
            $ErrorActionPreference = 'Stop'

            function Get-FsiIrmPolicyEvidenceStatus {{
                param([string]$PolicyExportPath, [string]$AlertExportPath)
                [pscustomobject]@{{ Status = 'NotApplicable'; Component = 'PolicyInventory' }}
            }}
            function Get-FsiAdaptiveProtectionStatus {{
                [pscustomobject]@{{ Status = 'NotApplicable'; Component = 'AdaptiveProtection' }}
            }}
            function Get-FsiIrmHrConnectorState {{
                [pscustomobject]@{{ Status = 'NotApplicable'; Component = 'HrConnector' }}
            }}
            function Get-FsiIrmSignalCoverage {{
                [pscustomobject]@{{ Status = 'NotApplicable'; Component = 'SignalCoverage' }}
            }}
            function Test-FsiIrmAlertRouting {{
                param([string]$WorkspaceId)
                [pscustomobject]@{{ Status = 'NotApplicable'; Component = 'AlertRouting'; WorkspaceId = $WorkspaceId }}
            }}
            function Test-FsiIrmAnonymization {{
                [pscustomobject]@{{ Status = 'NotApplicable'; Component = 'Anonymization' }}
            }}
            function Get-FsiIrmAgentAbuseIndicators {{
                [pscustomobject]@{{ Status = 'NotApplicable'; Component = 'AgentAbuseIndicators' }}
            }}
            function Write-FsiEvidence {{
                param(
                    [Parameter(Mandatory)] [object]$Object,
                    [Parameter(Mandatory)] [string]$Name,
                    [Parameter(Mandatory)] [string]$EvidencePath
                )
                New-Item -ItemType Directory -Force -Path $EvidencePath | Out-Null
                $outPath = Join-Path -Path $EvidencePath -ChildPath "$Name.json"
                $Object | ConvertTo-Json -Depth 20 | Set-Content -LiteralPath $outPath -Encoding utf8
            }}

            $script:FsiCloud = 'Commercial'
            $evidencePath = '{_ps_quote_path(evidence_path)}'
            $policyExportPath = '{_ps_quote_path(policy_export_path)}'
            $alertExportPath = '{_ps_quote_path(alert_export_path)}'
            $runbookPath = '{_ps_quote_path(runbook_path)}'
            $tenantId = '{TENANT_ID}'

            switch ('{workspace_mode}') {{
                'omitted' {{
                    . $runbookPath -EvidencePath $evidencePath -PolicyExportPath $policyExportPath -AlertExportPath $alertExportPath -TenantId $tenantId
                }}
                'null' {{
                    . $runbookPath -EvidencePath $evidencePath -PolicyExportPath $policyExportPath -AlertExportPath $alertExportPath -TenantId $tenantId -WorkspaceId $null
                }}
                'supplied' {{
                    . $runbookPath -EvidencePath $evidencePath -PolicyExportPath $policyExportPath -AlertExportPath $alertExportPath -TenantId $tenantId -WorkspaceId 'workspace-123'
                }}
                default {{
                    throw "Unknown workspace_mode: {workspace_mode}"
                }}
            }}

            $artifacts = @(Get-ChildItem -LiteralPath $evidencePath -Filter 'Control-1.12_*_PolicyEvidenceAggregate_*.json')
            if ($artifacts.Count -ne 1) {{
                throw "Expected exactly one aggregate artifact but found $($artifacts.Count)"
            }}

            $aggregate = Get-Content -LiteralPath $artifacts[0].FullName -Raw | ConvertFrom-Json -Depth 20
            if ($aggregate.OverallStatus -ne 'NotApplicable') {{
                throw "Expected OverallStatus=NotApplicable but got '$($aggregate.OverallStatus)'"
            }}

            Write-Output "OVERALL_STATUS=$($aggregate.OverallStatus)"
            """
        ).strip()

        harness_path.write_text(harness_script, encoding="utf-8")
        return subprocess.run(
            ["pwsh", "-NoProfile", "-File", str(harness_path)],
            cwd=SCRIPT_DIR.parent,
            capture_output=True,
            text=True,
        )
    finally:
        shutil.rmtree(case_root, ignore_errors=True)
        if artifact_root.exists() and not any(artifact_root.iterdir()):
            artifact_root.rmdir()


def test_control_112_runbook_callable_integrity_passes() -> None:
    markdown = _read_control_112_markdown()
    assert verifier.validate_markdown_callable_integrity(markdown) == []


def test_fails_when_runbook_calls_undefined_helper() -> None:
    markdown = _read_control_112_markdown()
    broken = re.sub(
        r"Get-FsiIrmPolicyEvidenceStatus\s+-PolicyExportPath[^\r\n]*",
        "Get-FsiIrmPolicyInventory",
        markdown,
        count=1,
    )
    errors = verifier.validate_markdown_callable_integrity(broken)
    assert any("undefined helper" in err for err in errors)


def test_fails_when_mandatory_parameters_are_omitted() -> None:
    markdown = _read_control_112_markdown()
    broken = re.sub(
        r"Get-FsiIrmPolicyEvidenceStatus\s+-PolicyExportPath[^\r\n]*",
        "Get-FsiIrmPolicyEvidenceStatus",
        markdown,
        count=1,
    )
    errors = verifier.validate_markdown_callable_integrity(broken)
    assert any("missing mandatory parameter" in err for err in errors)


@pytest.mark.parametrize("workspace_mode", ["omitted", "null", "supplied"])
def test_control_112_extracted_runbook_aggregate_survives_workspaceid_variants(workspace_mode: str) -> None:
    completed = _run_control_112_extracted_sweep(workspace_mode)
    combined_output = (completed.stdout or "") + (completed.stderr or "")
    assert completed.returncode == 0, combined_output
    assert "OVERALL_STATUS=NotApplicable" in (completed.stdout or "")
    assert "PropertyNotFoundException" not in combined_output


def _run_control_112_real_helper_scenario(case_name: str, scenario: str) -> subprocess.CompletedProcess[str]:
    """Run the extracted runbook with the real documented helper and a caller-supplied scenario."""
    markdown = _read_control_112_markdown()
    runbook = verifier._extract_runbook_fence(markdown)
    helper = verifier._extract_runbook_fence(markdown, marker="function Get-FsiIrmPolicyEvidenceStatus")

    artifact_root = SCRIPT_DIR / ".runtime-test-artifacts"
    case_root = artifact_root / f"agt112-{case_name}"
    if case_root.exists():
        shutil.rmtree(case_root)
    case_root.mkdir(parents=True, exist_ok=True)

    try:
        (case_root / "helper.ps1").write_text(helper, encoding="utf-8")
        (case_root / "Invoke-Agt112Sweep.extracted.ps1").write_text(runbook, encoding="utf-8")
        exports_path = case_root / "exports"
        exports_path.mkdir()
        (exports_path / "policy.csv").write_text("Name,Template\r\nP1,Risky AI usage\r\n", encoding="utf-8")
        (exports_path / "alerts.csv").write_text("AlertId\r\n", encoding="utf-8")

        harness = textwrap.dedent(
            f"""
            Set-StrictMode -Version Latest
            $ErrorActionPreference = 'Stop'
            . '{_ps_quote_path(case_root / "helper.ps1")}'
            $runbookPath = '{_ps_quote_path(case_root / "Invoke-Agt112Sweep.extracted.ps1")}'
            $evidencePath = '{_ps_quote_path(case_root / "evidence")}'
            $policyExportPath = '{_ps_quote_path(exports_path / "policy.csv")}'
            $alertExportPath = '{_ps_quote_path(exports_path / "alerts.csv")}'
            $tenantId = '{TENANT_ID}'
            function Invoke-Runbook {{
                param([hashtable]$Extra = @{{}})
                . $runbookPath -EvidencePath $evidencePath -PolicyExportPath $policyExportPath `
                    -AlertExportPath $alertExportPath @Extra | Out-Null
            }}
            function Get-Aggregates {{
                if (-not (Test-Path -LiteralPath $evidencePath)) {{ return @() }}
                @(Get-ChildItem -LiteralPath $evidencePath -Filter 'Control-1.12_*_PolicyEvidenceAggregate_*.json')
            }}
            """
        ).strip() + "\n" + textwrap.dedent(scenario).strip() + "\n"
        harness_path = case_root / "run-scenario.ps1"
        harness_path.write_text(harness, encoding="utf-8")
        return subprocess.run(
            ["pwsh", "-NoProfile", "-File", str(harness_path)],
            cwd=SCRIPT_DIR.parent,
            capture_output=True,
            text=True,
        )
    finally:
        shutil.rmtree(case_root, ignore_errors=True)
        if artifact_root.exists() and not any(artifact_root.iterdir()):
            artifact_root.rmdir()


def test_control_112_runbook_binds_tenant_and_run_identity_and_stays_pending() -> None:
    completed = _run_control_112_real_helper_scenario(
        "identity",
        """
        Invoke-Runbook @{ TenantId = $tenantId }
        $files = @(Get-Aggregates)
        if ($files.Count -ne 1) { throw "expected one aggregate, found $($files.Count)" }
        $body = Get-Content -LiteralPath $files[0].FullName -Raw | ConvertFrom-Json -Depth 20
        if ($body.TenantId -ne $tenantId) { throw "TenantId not embedded: $($body.TenantId)" }
        if ($body.RunId -notmatch '^IRM112-\\d{8}-\\d{6}-[0-9a-f]{8}$') { throw "bad RunId: $($body.RunId)" }
        if ($files[0].Name -ne "Control-1.12_$($tenantId)_Commercial_PolicyEvidenceAggregate_$($body.RunId).json") {
            throw "file name is not tenant/run bound: $($files[0].Name)"
        }
        if ($body.OverallStatus -ne 'Pending') { throw "present manual exports must stay Pending, got $($body.OverallStatus)" }
        $recorded = (Get-Content -LiteralPath "$($files[0].FullName).sha256" -Raw).Trim()
        if ($recorded -ne (Get-FileHash -LiteralPath $files[0].FullName -Algorithm SHA256).Hash) { throw 'sidecar hash mismatch' }
        Write-Output 'IDENTITY_OK'
        """,
    )
    combined_output = (completed.stdout or "") + (completed.stderr or "")
    assert completed.returncode == 0, combined_output
    assert "IDENTITY_OK" in (completed.stdout or "")


def test_control_112_runbook_preserves_earlier_evidence_across_runs() -> None:
    completed = _run_control_112_real_helper_scenario(
        "preserve",
        """
        Invoke-Runbook @{ TenantId = $tenantId }
        $first = @(Get-Aggregates)
        $firstHash = (Get-FileHash -LiteralPath $first[0].FullName -Algorithm SHA256).Hash
        Invoke-Runbook @{ TenantId = $tenantId }
        $all = @(Get-Aggregates)
        if ($all.Count -ne 2) { throw "second run replaced earlier evidence; found $($all.Count) file(s)" }
        $still = $all | Where-Object { $_.Name -eq $first[0].Name }
        if ((Get-FileHash -LiteralPath $still.FullName -Algorithm SHA256).Hash -ne $firstHash) { throw 'earlier evidence was modified' }
        Write-Output 'PRESERVE_OK'
        """,
    )
    combined_output = (completed.stdout or "") + (completed.stderr or "")
    assert completed.returncode == 0, combined_output
    assert "PRESERVE_OK" in (completed.stdout or "")


def test_control_112_runbook_rejects_overwrite_for_reused_run_id() -> None:
    completed = _run_control_112_real_helper_scenario(
        "reuse",
        """
        $runId = 'IRM112-20261018-221300-ab12cd34'
        Invoke-Runbook @{ TenantId = $tenantId; RunId = $runId }
        $first = @(Get-Aggregates)[0]
        $firstHash = (Get-FileHash -LiteralPath $first.FullName -Algorithm SHA256).Hash
        $rejected = $false
        try { Invoke-Runbook @{ TenantId = $tenantId; RunId = $runId } }
        catch { $rejected = $_.Exception.Message -match 'will not be overwritten' }
        if (-not $rejected) { throw 'a reused RunId must be rejected instead of overwriting evidence' }
        if ((Get-FileHash -LiteralPath $first.FullName -Algorithm SHA256).Hash -ne $firstHash) { throw 'existing evidence was modified' }
        if (@(Get-Aggregates).Count -ne 1) { throw 'unexpected extra artifacts' }
        Write-Output 'REUSE_REJECTED'
        """,
    )
    combined_output = (completed.stdout or "") + (completed.stderr or "")
    assert completed.returncode == 0, combined_output
    assert "REUSE_REJECTED" in (completed.stdout or "")


@pytest.mark.parametrize("tenant", ["contoso.onmicrosoft.com", "../escape", ""])
def test_control_112_runbook_rejects_non_guid_tenant_id(tenant: str) -> None:
    completed = _run_control_112_real_helper_scenario(
        "badtenant",
        f"""
        $rejected = $false
        try {{ Invoke-Runbook @{{ TenantId = '{tenant}' }} }} catch {{ $rejected = $true }}
        if (-not $rejected) {{ throw 'non-GUID tenant identifier was accepted' }}
        if (@(Get-Aggregates).Count -ne 0) {{ throw 'evidence was written for an invalid tenant' }}
        Write-Output 'TENANT_REJECTED'
        """,
    )
    combined_output = (completed.stdout or "") + (completed.stderr or "")
    assert completed.returncode == 0, combined_output
    assert "TENANT_REJECTED" in (completed.stdout or "")
