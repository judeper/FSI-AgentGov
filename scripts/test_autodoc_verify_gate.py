"""Tests for the deterministic autodoc verification gate orchestrator."""

from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any

import pytest

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

import autodoc_verify_gate as gate  # noqa: E402

ALLOWED_PATH = "docs/test.md"


def _contract() -> dict[str, Any]:
    return {
        "schema_version": 1,
        "fingerprint": "sha256:test",
        "report_path": "reports/monitoring/learn-changes-test.md",
        "source_url": "https://learn.microsoft.com/test",
        "classification": "minor",
        "route": "autodraft",
        "automerge_eligible": True,
        "allowed_files": [ALLOWED_PATH],
        "allowed_headings": ["Additional Resources"],
        "forbidden_paths": ["scripts/**", ".github/**"],
        "validation": ["python scripts/verify_language_rules.py <files>"],
    }


def _det_pass(*_args: Any, **_kwargs: Any) -> dict[str, Any]:
    return {"pass": True, "findings": [], "summary": {"block_findings": 0, "warn_findings": 0}}


def _det_fail(*_args: Any, **_kwargs: Any) -> dict[str, Any]:
    return {
        "pass": False,
        "findings": [{"check": "path_allowlist", "severity": "block", "path": "scripts/x.py", "message": "blocked"}],
        "summary": {"block_findings": 1, "warn_findings": 0},
    }


def _det_raise(*_args: Any, **_kwargs: Any) -> dict[str, Any]:
    raise RuntimeError("verifier unavailable")


def test_run_gate_deterministic_pass() -> None:
    result = gate.run_gate(
        _contract(),
        "Source report",
        "+Added claim",
        {ALLOWED_PATH: "# Test\n"},
        pr_body="AUTODOC-FINGERPRINT: sha256:test",
        repo_root=".",
        _det=_det_pass,
    )

    assert result["conclusion"] == "pass"
    assert "llm" not in result


def test_run_gate_deterministic_fail() -> None:
    result = gate.run_gate(
        _contract(),
        "Source report",
        "+Added claim",
        {ALLOWED_PATH: "# Test\n"},
        pr_body="AUTODOC-FINGERPRINT: sha256:test",
        repo_root=".",
        _det=_det_fail,
    )

    assert result["conclusion"] == "fail"
    assert "blocking finding" in result["summary"]


def test_run_gate_deterministic_exception_fails_closed() -> None:
    result = gate.run_gate(
        _contract(),
        "Source report",
        "+Added claim",
        {ALLOWED_PATH: "# Test\n"},
        pr_body="AUTODOC-FINGERPRINT: sha256:test",
        repo_root=".",
        _det=_det_raise,
    )

    assert result["conclusion"] == "fail"
    assert result["deterministic"]["findings"][0]["check"] == "deterministic_exception"


@pytest.fixture()
def workspace(request: pytest.FixtureRequest) -> Path:
    safe_name = re.sub(r"[^A-Za-z0-9_.-]+", "-", request.node.name)
    root = Path("scripts") / ".autodoc-verify-gate-test" / safe_name
    shutil.rmtree(root, ignore_errors=True)
    root.mkdir(parents=True)
    try:
        yield root
    finally:
        shutil.rmtree(root, ignore_errors=True)


@pytest.mark.parametrize(
    ("deterministic", "expected_exit", "expected_conclusion"),
    [
        (_det_fail, 1, "fail"),
        (_det_pass, 0, "pass"),
    ],
)
def test_main_exit_codes(
    monkeypatch: pytest.MonkeyPatch,
    workspace: Path,
    deterministic: Any,
    expected_exit: int,
    expected_conclusion: str,
) -> None:
    paths = _write_cli_inputs(workspace)

    monkeypatch.setattr(gate.autodoc_verify, "verify", deterministic)

    exit_code = gate.main(
        [
            "--contract",
            str(paths["contract"]),
            "--report",
            str(paths["report"]),
            "--diff",
            str(paths["diff"]),
            "--head-dir",
            str(paths["head_dir"]),
            "--pr-body",
            str(paths["pr_body"]),
            "--out",
            str(paths["out"]),
        ]
    )

    result = json.loads(paths["out"].read_text(encoding="utf-8"))
    assert exit_code == expected_exit
    assert result["conclusion"] == expected_conclusion


def test_sanitize_log_text_collapses_whitespace_and_strips_control_characters() -> None:
    assert gate.sanitize_log_text("a\x00b\tc\r\nd", 100) == "a b c d"
    assert gate.sanitize_log_text("x" * 50, 10) == "xxxxxxx..."
    assert gate.sanitize_log_text("", 10) == ""


def test_log_findings_neutralizes_actions_workflow_commands(capsys: pytest.CaptureFixture[str]) -> None:
    """PR-controlled finding text must never render as a GitHub Actions log command."""

    result = {
        "deterministic": {
            "findings": [
                {
                    "check": "language",
                    "severity": "block",
                    "path": "docs/x.md",
                    "message": "Line 3\n::error::spoofed\n::add-mask::secret",
                }
            ]
        }
    }

    gate.log_findings(result)
    out = capsys.readouterr().out

    assert "::error::spoofed" in out
    assert all(not line.lstrip().startswith("::") for line in out.splitlines())
    assert len([line for line in out.splitlines() if line.startswith("- [")]) == 1


def test_log_findings_truncates_long_finding_lists(capsys: pytest.CaptureFixture[str]) -> None:
    findings = [
        {"check": "language", "severity": "block", "path": f"docs/{index}.md", "message": "bad"}
        for index in range(gate._LOG_FINDING_LIMIT + 3)
    ]

    gate.log_findings({"deterministic": {"findings": findings}})
    out = capsys.readouterr().out

    assert out.startswith(f"Deterministic findings ({len(findings)}):")
    assert len([line for line in out.splitlines() if line.startswith("- [")]) == gate._LOG_FINDING_LIMIT
    assert "3 additional finding(s) omitted" in out


def test_log_findings_is_silent_without_findings(capsys: pytest.CaptureFixture[str]) -> None:
    gate.log_findings({"deterministic": {"findings": []}})
    gate.log_findings({"deterministic": {}})
    gate.log_findings({})

    assert capsys.readouterr().out == ""


def test_main_logs_sanitized_findings(
    monkeypatch: pytest.MonkeyPatch, workspace: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    paths = _write_cli_inputs(workspace)
    monkeypatch.setattr(gate.autodoc_verify, "verify", _det_fail)

    exit_code = gate.main(
        [
            "--contract",
            str(paths["contract"]),
            "--report",
            str(paths["report"]),
            "--diff",
            str(paths["diff"]),
            "--head-dir",
            str(paths["head_dir"]),
            "--pr-body",
            str(paths["pr_body"]),
            "--out",
            str(paths["out"]),
        ]
    )
    out = capsys.readouterr().out

    assert exit_code == 1
    assert "Deterministic findings (1):" in out
    assert "- [block] path_allowlist scripts/x.py: blocked" in out


def test_cli_logs_unicode_findings_with_restrictive_stdout_encoding(workspace: Path) -> None:
    paths = _write_cli_inputs(workspace)
    contract = json.loads(paths["contract"].read_text(encoding="utf-8"))
    contract["allowed_headings"].append("Test")
    paths["contract"].write_text(json.dumps(contract), encoding="utf-8")
    finding_message = "Line 3: ✅ ::error::spoofed " + ("→" * (gate._LOG_MESSAGE_LIMIT + 50))
    linter_output = f"❌ {ALLOWED_PATH} [Tier 1]\n  {finding_message}\n"
    linter = paths["head_dir"] / "scripts" / "verify_language_rules.py"
    linter.parent.mkdir(parents=True)
    linter.write_text(
        "import sys\n"
        f"sys.stdout.buffer.write({linter_output.encode('utf-8')!r})\n"
        "raise SystemExit(1)\n",
        encoding="utf-8",
    )

    env = os.environ.copy()
    env["PYTHONIOENCODING"] = "cp1252:strict"
    completed = subprocess.run(
        [
            sys.executable,
            str(SCRIPT_DIR / "autodoc_verify_gate.py"),
            "--contract",
            str(paths["contract"]),
            "--report",
            str(paths["report"]),
            "--diff",
            str(paths["diff"]),
            "--head-dir",
            str(paths["head_dir"]),
            "--pr-body",
            str(paths["pr_body"]),
            "--out",
            str(paths["out"]),
        ],
        capture_output=True,
        text=True,
        encoding="utf-8",
        env=env,
        check=False,
    )

    result = json.loads(paths["out"].read_text(encoding="utf-8"))
    finding_lines = [line for line in completed.stdout.splitlines() if line.startswith("- [")]

    assert completed.returncode == 1
    assert "Traceback" not in completed.stderr
    assert len(finding_lines) == 1
    logged_message = finding_lines[0].split(": ", 1)[1]
    assert len(logged_message) <= gate._LOG_MESSAGE_LIMIT
    assert logged_message.startswith("Line 3: ✅ ::error::spoofed")
    assert logged_message.endswith("...")
    assert all(not line.lstrip().startswith("::") for line in completed.stdout.splitlines())
    assert result["conclusion"] == "fail"
    assert result["deterministic"]["findings"][0]["message"] == finding_message


def _write_cli_inputs(workspace: Path) -> dict[str, Path]:
    contract = workspace / "contract.json"
    report = workspace / "report.md"
    diff = workspace / "pr.diff"
    pr_body = workspace / "pr-body.txt"
    out = workspace / "gate.json"
    head_dir = workspace / "head"
    doc_path = head_dir / "docs" / "test.md"
    doc_path.parent.mkdir(parents=True)

    contract.write_text(json.dumps(_contract()), encoding="utf-8")
    report.write_text("Source report mentions the added claim.", encoding="utf-8")
    pr_body.write_text("Closes #1\n\nAUTODOC-FINGERPRINT: sha256:test\n", encoding="utf-8")
    doc_path.write_text("# Test\n\n## Additional Resources\nAdded claim.\n", encoding="utf-8")
    diff.write_text(
        f"""diff --git a/{ALLOWED_PATH} b/{ALLOWED_PATH}
--- a/{ALLOWED_PATH}
+++ b/{ALLOWED_PATH}
@@ -1,2 +1,4 @@
 # Test
+
+## Additional Resources
+Added claim.
""",
        encoding="utf-8",
    )
    return {
        "contract": contract,
        "report": report,
        "diff": diff,
        "pr_body": pr_body,
        "out": out,
        "head_dir": head_dir,
    }
