"""Regression tests for Control 1.3 §4b sensitivity-label lookup via .Name property.

Issue #248: ``Get-MgBetaInformationProtectionPolicyLabel`` filtering must use the
documented ``.Name`` property.  The old (broken) code filtered on ``.DisplayName``,
which does NOT exist on ``MicrosoftGraphInformationProtectionLabel`` objects returned
by the Graph Beta SDK — causing every lookup to silently match nothing.

Two-layer coverage:

Static layer (pure Python, no pwsh):
  - Playbook text contains the correct ``$_.Name -eq`` filter pattern.
  - Playbook text does NOT contain the broken ``$_.DisplayName -eq`` filter pattern.
  - Array materialisation ``@(...)`` is present so ``.Count`` is reliable.
  - Zero-match path enumerates available names.
  - Duplicate-match path emits an ambiguity warning.

Runtime layer (PowerShell subprocess, requires pwsh):
  One match     — Update-MgGroup is called; [DONE] is emitted.
  Zero matches  — warning with available names; no Update call.
  Dup matches   — ambiguity warning; no Update call.
  Legacy shape  — ``Name=null`` / ``DisplayName=target`` object does NOT produce a
                  false-positive match (safe-compatibility check).
  Regression guard — ``DisplayName`` matches but ``Name`` does not → NOT applied.
                     If this test ever fails it means the filter reverted to
                     ``.DisplayName``, which is the original bug.
  Converse       — ``Name`` matches even when ``DisplayName`` differs → IS applied
                   (confirms ``.Name`` is the authoritative filter).

Requirement gap assessment
--------------------------
Issue #248 asks for "safe compatibility behavior."  Linus did NOT add a
``.DisplayName`` fallback for legacy objects; he intentionally chose the
zero-match + warning path for objects whose ``.Name`` is null/missing.
This is safe (no false-positive assignment, clear diagnostic message) but
means an operator with a tenant whose labels have null ``.Name`` fields
gets a warning listing zero available names — potentially confusing.

Gap verdict: NO functional gap against the stated requirement.  The
zero-match + warning path IS safe.  A usability improvement (fallback to
``.DisplayName`` when ``.Name`` is absent) is a separate enhancement, not a
requirement of issue #248.  If the coordinator disagrees, route back to
Linus with specific acceptance criteria before the tests are adjusted.
"""

from __future__ import annotations

import re
import shutil
import subprocess
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parent
PLAYBOOK_PATH = (
    REPO_ROOT / "docs" / "playbooks" / "control-implementations" / "1.3" / "powershell-setup.md"
)

_FENCE_RE = re.compile(r"```powershell\s*\n(.*?)\n```", re.IGNORECASE | re.DOTALL)
_FUNCTION_MARKER = "function Set-AgentGroundingSite"
_EXAMPLE_SPLIT = "\n# Example\n"

# Property-access pattern assertions
_NAME_FILTER_PAT = r"\$_\.Name\s+-eq\s+\$SensitivityLabelName"
_DISPLAYNAME_FILTER_PAT = r"\$_\.DisplayName\s+-eq\s+\$SensitivityLabelName"


# ---------------------------------------------------------------------------
# Shared helpers
# ---------------------------------------------------------------------------


def _read_playbook() -> str:
    assert PLAYBOOK_PATH.exists(), f"playbook not found: {PLAYBOOK_PATH}"
    return PLAYBOOK_PATH.read_text(encoding="utf-8")


def _extract_section4_fence(markdown: str) -> str:
    """Return the raw text of the powershell fence containing Set-AgentGroundingSite."""
    for fence in _FENCE_RE.findall(markdown):
        if _FUNCTION_MARKER in fence:
            return fence
    raise ValueError(f"No fence found containing {_FUNCTION_MARKER!r}")


def _extract_function_def(fence: str) -> str:
    """Return only the function definition, stripping the trailing example call."""
    if _EXAMPLE_SPLIT in fence:
        return fence.split(_EXAMPLE_SPLIT)[0].rstrip()
    # Fallback: locate the last top-level closing brace
    lines = fence.splitlines()
    for i in range(len(lines) - 1, -1, -1):
        if lines[i].strip() == "}":
            return "\n".join(lines[: i + 1])
    return fence


def _build_mock_labels(label_defs: list[dict]) -> str:
    """Return a PowerShell function body for Get-MgBetaInformationProtectionPolicyLabel."""
    lines: list[str] = [
        "function Get-MgBetaInformationProtectionPolicyLabel {",
        "    param([switch]$All)",
    ]
    if not label_defs:
        lines.append("    @()")
    else:
        lines.append("    @(")
        items: list[str] = []
        for d in label_defs:
            item: list[str] = ["        [pscustomobject]@{"]
            for k, v in d.items():
                if v is None:
                    item.append(f"            {k} = $null")
                else:
                    escaped_v = str(v).replace("'", "''")
                    item.append(f"            {k} = '{escaped_v}'")
            item.append("        }")
            items.append("\n".join(item))
        lines.append(",\n".join(items))
        lines.append("    )")
    lines.append("}")
    return "\n".join(lines)


# Sentinel-based template avoids f-string brace conflicts with PowerShell syntax.
_HARNESS_TMPL = """\
Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'
$WarningPreference      = 'Continue'
$ConfirmPreference      = 'None'

function Get-SPOSite {
    param([string]$Identity, [switch]$Detailed, $ErrorAction)
    [pscustomobject]@{
        SharingCapability = 'ExternalUserSharingOnly'
        SensitivityLabel  = ''
        GroupId           = [Guid]'aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa'
    }
}
function Set-SPOSite { <# no-op mock #> }
function Update-MgGroup {
    param($GroupId, $BodyParameter)
    Write-Output 'UPDATE_MGGROUP_CALLED'
}

##MOCK_LABELS##

. '##FUNC_PATH##'

Set-AgentGroundingSite `
    -SiteUrl              'https://test.sharepoint.com/sites/Test' `
    -Zone                 Zone1 `
    -SensitivityLabelName '##LABEL_NAME##' `
    -Confirm:$false
"""

_ARTIFACTS_ROOT = SCRIPT_DIR / ".runtime-test-artifacts"


def _run_case(
    case_name: str,
    label_defs: list[dict],
    label_name: str = "Confidential-FSI",
) -> subprocess.CompletedProcess[str]:
    """Build and run a harness for one label-filter test case; clean up on exit."""
    markdown = _read_playbook()
    fence = _extract_section4_fence(markdown)
    func_def = _extract_function_def(fence)

    case_root = _ARTIFACTS_ROOT / f"ctrl13-{case_name}"
    if case_root.exists():
        shutil.rmtree(case_root)
    case_root.mkdir(parents=True, exist_ok=True)

    try:
        func_path = case_root / "Set-AgentGroundingSite.ps1"
        func_path.write_text(func_def, encoding="utf-8")

        mock_labels = _build_mock_labels(label_defs)
        # Paths on Windows may contain backslashes; single-quoted PS strings treat them literally.
        func_path_ps = str(func_path).replace("'", "''")
        label_name_ps = label_name.replace("'", "''")

        harness = (
            _HARNESS_TMPL
            .replace("##MOCK_LABELS##", mock_labels)
            .replace("##FUNC_PATH##", func_path_ps)
            .replace("##LABEL_NAME##", label_name_ps)
        )
        harness_path = case_root / "harness.ps1"
        harness_path.write_text(harness, encoding="utf-8")

        return subprocess.run(
            ["pwsh", "-NoProfile", "-NonInteractive", "-File", str(harness_path)],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
        )
    finally:
        shutil.rmtree(case_root, ignore_errors=True)
        if _ARTIFACTS_ROOT.exists() and not any(_ARTIFACTS_ROOT.iterdir()):
            _ARTIFACTS_ROOT.rmdir()


# ---------------------------------------------------------------------------
# Static tests (pure Python — no pwsh required)
# ---------------------------------------------------------------------------


def test_section4b_filter_uses_name_property() -> None:
    """§4b Where-Object must filter on .Name, not .DisplayName."""
    fence = _extract_section4_fence(_read_playbook())
    assert re.search(_NAME_FILTER_PAT, fence), (
        "§4b label filter does not use $_.Name -eq $SensitivityLabelName. "
        "The documented property on MicrosoftGraphInformationProtectionLabel is .Name."
    )


def test_section4b_does_not_use_displayname_as_filter() -> None:
    """The nonexistent .DisplayName direct-filter must not appear in §4b.

    MicrosoftGraphInformationProtectionLabel does not expose .DisplayName as a
    user-visible label name property.  Filtering on it silently matches nothing.
    This test is the primary regression lock for issue #248.
    """
    fence = _extract_section4_fence(_read_playbook())
    assert not re.search(_DISPLAYNAME_FILTER_PAT, fence), (
        "§4b Where-Object filter references .DisplayName — this property does not "
        "exist on the label object returned by Get-MgBetaInformationProtectionPolicyLabel."
    )


def test_section4b_materialises_results_with_array_operator() -> None:
    """@($allLabels | Where-Object ...) must be present.

    Without @(...), Get-MgBetaInformationProtectionPolicyLabel returning a single
    object causes PowerShell to unwrap the scalar, making .Count unreliable.
    """
    fence = _extract_section4_fence(_read_playbook())
    # Accept either tight or spaced variant: @($allLabels ... or @( $allLabels ...
    assert re.search(r"@\(\s*\$allLabels\s*\|", fence), (
        "§4b must materialise matches with @(...) to guarantee .Count reliability "
        "when a single label is returned."
    )


def test_section4b_zero_match_path_enumerates_available_names() -> None:
    """Zero-match warning must list available label names to aid diagnosis."""
    fence = _extract_section4_fence(_read_playbook())
    # The code should build a $available list from $allLabels
    assert "$available" in fence, (
        "§4b zero-match path should enumerate available label names in the warning message."
    )
    assert "Available names:" in fence, (
        "§4b zero-match warning should include 'Available names:' for operator guidance."
    )


def test_section4b_duplicate_match_path_emits_ambiguity_warning() -> None:
    """The duplicate-match branch must block assignment and warn about ambiguity."""
    fence = _extract_section4_fence(_read_playbook())
    assert "ambiguously" in fence or "cannot apply" in fence, (
        "§4b must warn and refuse to apply a label when multiple entries share the same Name."
    )


def test_section4b_comment_documents_name_not_displayname() -> None:
    """The §4b code comment should document that .Name is used, not .DisplayName.

    This is not a functional gate but it locks in that the fix is intentional
    and documented inline for future maintainers.
    """
    fence = _extract_section4_fence(_read_playbook())
    assert ".Name" in fence and "DisplayName" in fence, (
        "§4b should reference both .Name (the correct property) and DisplayName "
        "(the incorrect one) in comments to document the intentional choice."
    )


# ---------------------------------------------------------------------------
# Runtime tests — exercise the extracted function with mocked cmdlets
# ---------------------------------------------------------------------------


def test_one_name_match_calls_update_mggroup() -> None:
    """Exactly one .Name match → Update-MgGroup called; [DONE] emitted."""
    result = _run_case(
        "one-match",
        label_defs=[{"Id": "id-001", "Name": "Confidential-FSI"}],
    )
    combined = (result.stdout or "") + (result.stderr or "")
    assert result.returncode == 0, f"Harness exited non-zero:\n{combined}"
    assert "UPDATE_MGGROUP_CALLED" in result.stdout, (
        "Expected Update-MgGroup to be called for a single exact .Name match.\n" + combined
    )
    assert "[DONE]" in combined, f"Expected [DONE] confirmation in output.\n{combined}"


def test_zero_name_matches_warns_with_available_names() -> None:
    """No .Name matches → warning listing available names; Update-MgGroup NOT called."""
    result = _run_case(
        "zero-match",
        label_defs=[
            {"Id": "id-002", "Name": "Internal"},
            {"Id": "id-003", "Name": "Public"},
        ],
    )
    combined = (result.stdout or "") + (result.stderr or "")
    assert result.returncode == 0, f"Harness exited non-zero:\n{combined}"
    assert "UPDATE_MGGROUP_CALLED" not in result.stdout, (
        "Update-MgGroup must NOT be called when no label .Name matches.\n" + combined
    )
    assert "not found" in combined.lower(), (
        f"Expected 'not found' warning text.\n{combined}"
    )
    # Available names should appear in the warning to help the operator
    assert "Internal" in combined or "Public" in combined, (
        f"Warning should enumerate available label names.\n{combined}"
    )


def test_duplicate_name_matches_warns_and_blocks_assignment() -> None:
    """Two objects with the same .Name → ambiguity warning; Update-MgGroup NOT called."""
    result = _run_case(
        "dup-match",
        label_defs=[
            {"Id": "id-010", "Name": "Confidential-FSI"},
            {"Id": "id-011", "Name": "Confidential-FSI"},
        ],
    )
    combined = (result.stdout or "") + (result.stderr or "")
    assert result.returncode == 0, f"Harness exited non-zero:\n{combined}"
    assert "UPDATE_MGGROUP_CALLED" not in result.stdout, (
        "Update-MgGroup must NOT be called on an ambiguous duplicate Name match.\n" + combined
    )
    assert "ambiguously" in combined.lower() or "cannot apply" in combined.lower(), (
        f"Expected ambiguity warning text.\n{combined}"
    )


def test_legacy_shape_null_name_does_not_produce_false_positive() -> None:
    """Safe-compatibility check: a label object with Name=null (but DisplayName=target)
    must NOT trigger Update-MgGroup.

    ``$null -eq 'Confidential-FSI'`` is ``$false`` so the Where-Object filter correctly
    excludes these objects.  This verifies no false-positive match can arise from
    legacy or malformed label objects where .Name has not been populated.
    """
    result = _run_case(
        "legacy-null-name",
        label_defs=[{"Id": "id-020", "Name": None, "DisplayName": "Confidential-FSI"}],
    )
    combined = (result.stdout or "") + (result.stderr or "")
    assert result.returncode == 0, f"Harness exited non-zero:\n{combined}"
    assert "UPDATE_MGGROUP_CALLED" not in result.stdout, (
        "Legacy object with Name=null must NOT trigger Update-MgGroup. "
        "A null .Name must not match the target label — safe compatibility.\n" + combined
    )
    assert "not found" in combined.lower(), (
        f"Expected zero-match 'not found' warning for Name=null legacy shape.\n{combined}"
    )


def test_displayname_match_without_name_match_does_not_apply_label() -> None:
    """PRIMARY REGRESSION GUARD for issue #248.

    When .DisplayName matches the requested label name but .Name does NOT,
    the label must NOT be applied.

    If this test fails (UPDATE_MGGROUP_CALLED appears in stdout) it means the
    filter has reverted to using .DisplayName instead of .Name — which is the
    exact bug fixed by issue #248.
    """
    result = _run_case(
        "displayname-regression-guard",
        # .DisplayName matches the requested name; .Name deliberately does not.
        label_defs=[{"Id": "id-030", "Name": "Internal", "DisplayName": "Confidential-FSI"}],
        label_name="Confidential-FSI",
    )
    combined = (result.stdout or "") + (result.stderr or "")
    assert result.returncode == 0, f"Harness exited non-zero:\n{combined}"
    assert "UPDATE_MGGROUP_CALLED" not in result.stdout, (
        "REGRESSION DETECTED: Update-MgGroup was called when .DisplayName matched but "
        ".Name did not.  The filter is using .DisplayName instead of .Name.\n" + combined
    )


def test_name_match_with_different_displayname_applies_label() -> None:
    """Converse of the regression guard: .Name matches even when .DisplayName differs.

    Confirms that .Name is the sole authoritative filter and a differing .DisplayName
    value on the same object does not suppress the match.
    """
    result = _run_case(
        "name-match-displayname-differs",
        label_defs=[{"Id": "id-040", "Name": "Confidential-FSI", "DisplayName": "Something-Else"}],
    )
    combined = (result.stdout or "") + (result.stderr or "")
    assert result.returncode == 0, f"Harness exited non-zero:\n{combined}"
    assert "UPDATE_MGGROUP_CALLED" in result.stdout, (
        "Expected Update-MgGroup to be called when .Name matches the target, "
        "even if .DisplayName differs.\n" + combined
    )
