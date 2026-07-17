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

            switch ('{workspace_mode}') {{
                'omitted' {{
                    . $runbookPath -EvidencePath $evidencePath -PolicyExportPath $policyExportPath -AlertExportPath $alertExportPath
                }}
                'null' {{
                    . $runbookPath -EvidencePath $evidencePath -PolicyExportPath $policyExportPath -AlertExportPath $alertExportPath -WorkspaceId $null
                }}
                'supplied' {{
                    . $runbookPath -EvidencePath $evidencePath -PolicyExportPath $policyExportPath -AlertExportPath $alertExportPath -WorkspaceId 'workspace-123'
                }}
                default {{
                    throw "Unknown workspace_mode: {workspace_mode}"
                }}
            }}

            $aggregatePath = Join-Path -Path $evidencePath -ChildPath 'agt112-aggregate.json'
            if (-not (Test-Path -LiteralPath $aggregatePath -PathType Leaf)) {{
                throw "Aggregate artifact missing: $aggregatePath"
            }}

            $aggregate = Get-Content -LiteralPath $aggregatePath -Raw | ConvertFrom-Json -Depth 20
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
