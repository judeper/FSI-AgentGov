"""Regression tests for runnable playbook PowerShell callable validation."""

from __future__ import annotations

import re
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

import verify_playbook_powershell_helpers as verifier  # noqa: E402


def _read_control_112_markdown() -> str:
    return (SCRIPT_DIR.parent / verifier.DOC_PATH).read_text(encoding="utf-8")


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
