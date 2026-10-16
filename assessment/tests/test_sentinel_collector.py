"""Run the Sentinel collector with local mocks; no Azure modules or network calls."""

from __future__ import annotations

import json
import shutil
import subprocess
import uuid
from pathlib import Path

import pytest

COLLECTOR = Path(__file__).resolve().parents[1] / "collectors" / "Collect-Sentinel.ps1"
EXPECTED_QUERY = (
    'CopilotActivity | where RecordType == "CopilotInteraction" '
    "| where TimeGenerated > ago(7d) | count"
)

HARNESS = r"""
param([string]$Collector, [string]$OutputDir, [int]$Count, [switch]$QueryFails)
$ErrorActionPreference = 'Stop'
$ConfirmPreference = 'None'
function Import-Module {
    param([string]$Name, $ErrorAction)
    if ($Name -ne 'Az.OperationalInsights') { throw "Unexpected module: $Name" }
}
function Connect-AzAccount {
    param($TenantId, $SubscriptionId, $ErrorAction)
}
function Set-AzContext {
    param($SubscriptionId, $ErrorAction)
}
function Get-AzOperationalInsightsWorkspace {
    param($ResourceGroupName, $Name, $ErrorAction)
    [pscustomobject]@{
        CustomerId = 'mock-workspace-id'
        ResourceId = 'mock-resource-id'
        Name = $Name
        Location = 'eastus'
        ProvisioningState = 'Succeeded'
        Sku = 'PerGB2018'
        RetentionInDays = 30
        WorkspaceCapping = $null
    }
}
function Get-AzAccessToken {
    param($ResourceUrl, $ErrorAction)
    [pscustomobject]@{ Token = 'local-mock-only' }
}
function Invoke-RestMethod {
    param($Uri, $Method, $Headers, $ErrorAction)
    [pscustomobject]@{ value = @() }
}
function Invoke-AzOperationalInsightsQuery {
    param($WorkspaceId, $Query, $ErrorAction)
    [pscustomobject]@{ WorkspaceId = $WorkspaceId; Query = $Query } |
        ConvertTo-Json | Set-Content (Join-Path $OutputDir 'query.json')
    if ($QueryFails) { throw 'Mock query failure: table unavailable' }
    [pscustomobject]@{ Results = @([pscustomobject]@{ Count = $Count }) }
}
& $Collector -TenantId 'mock-tenant' -AuthMode Interactive -OutputDir $OutputDir `
    -SubscriptionId 'mock-subscription' -ResourceGroup 'mock-group' `
    -WorkspaceName 'mock-workspace' -Verbose -Confirm:$false
exit $LASTEXITCODE
"""


@pytest.fixture
def runtime_dir():
    artifacts = Path(__file__).resolve().parent / ".runtime-test-artifacts"
    case = artifacts / uuid.uuid4().hex
    case.mkdir(parents=True)
    try:
        yield case
    finally:
        shutil.rmtree(case)
        if artifacts.exists() and not any(artifacts.iterdir()):
            artifacts.rmdir()


@pytest.mark.parametrize(
    ("count", "query_fails", "exit_code"),
    [(5, False, 0), (0, False, 0), (0, True, 1)],
    ids=["records-present", "zero-records", "query-error"],
)
def test_copilot_query_and_collection_outcome(runtime_dir, count, query_fails, exit_code):
    pwsh = shutil.which("pwsh")
    if not pwsh:
        pytest.skip("PowerShell 7 is required for mocked collector execution")
    harness = runtime_dir / "harness.ps1"
    harness.write_text(HARNESS, encoding="utf-8")
    command = [
        pwsh, "-NoLogo", "-NoProfile", "-NonInteractive", "-File", str(harness),
        "-Collector", str(COLLECTOR), "-OutputDir", str(runtime_dir), "-Count", str(count),
    ]
    if query_fails:
        command.append("-QueryFails")
    process = subprocess.run(command, capture_output=True, text=True, encoding="utf-8", timeout=30)
    assert process.returncode == exit_code, process.stdout + process.stderr
    emitted = json.loads((runtime_dir / "query.json").read_text(encoding="utf-8-sig"))
    assert emitted == {"WorkspaceId": "mock-workspace-id", "Query": EXPECTED_QUERY}
    output = json.loads((runtime_dir / "collected" / "sentinel.json").read_text(encoding="utf-8-sig"))
    assert set(output) == {"workspace", "dataConnectors", "kqlAuditCheck", "_metadata"}
    assert output["workspace"]["WorkspaceId"] == "mock-workspace-id"
    assert output["dataConnectors"] == {
        "TotalConnectors": 0, "ConnectorSummary": None, "Office365Enabled": False, "McasEnabled": False,
    }
    warnings = output["_metadata"]["warnings"]
    if query_fails:
        assert output["kqlAuditCheck"] is None
        assert warnings == ["Section 3 (KQL Audit) failed: Mock query failure: table unavailable"]
        assert "Partial collection: 1/3 sections returned null." in process.stdout
    else:
        check = output["kqlAuditCheck"]
        assert set(check) == {"Query", "RecordCount", "HasRecords", "QueryTimeRange", "ExecutedAt"}
        assert check["Query"] == EXPECTED_QUERY
        assert check["RecordCount"] == count
        assert check["HasRecords"] is (count > 0)
        assert check["QueryTimeRange"] == "7 days"
        assert check["ExecutedAt"]
        if count:
            assert warnings == []
            assert "Found 5 CopilotActivity record(s)" in process.stdout
            assert "does not establish coverage of all AI or Power Platform audit sources" in process.stdout
        else:
            assert len(warnings) == 1
            assert "No CopilotActivity records for Copilot interactions found" in warnings[0]
            assert "zero records alone do not prove capture failure" in warnings[0]
    for warning in warnings:
        assert warning in process.stdout
