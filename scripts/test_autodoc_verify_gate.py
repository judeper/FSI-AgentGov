"""Tests for the deterministic autodoc verification gate orchestrator."""

from __future__ import annotations

import io
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


class _CapableStream:
    """Stand-in for a healthy ``TextIOWrapper``: supports ``reconfigure``, ``write``, ``flush``."""

    def __init__(self) -> None:
        self.reconfigured: list[dict[str, Any]] = []
        self.written: list[str] = []
        self.flushes = 0

    def reconfigure(self, **kwargs: Any) -> None:
        self.reconfigured.append(kwargs)

    def write(self, text: str) -> int:
        self.written.append(text)
        return len(text)

    def flush(self) -> None:
        self.flushes += 1


class _HostileReconfigureStream:
    """Writable stream whose ``reconfigure`` raises, like a detached or closed wrapper."""

    def __init__(self, error: BaseException) -> None:
        self._error = error
        self.written: list[str] = []

    def reconfigure(self, **_kwargs: Any) -> None:
        raise self._error

    def write(self, text: str) -> int:
        self.written.append(text)
        return len(text)

    def flush(self) -> None:
        return None


class _EncodingBoundStream:
    """Stream without ``reconfigure`` that refuses text its encoding cannot represent."""

    def __init__(self, encoding: str) -> None:
        self.encoding = encoding
        self.written: list[str] = []

    def write(self, text: str) -> int:
        text.encode(self.encoding)
        self.written.append(text)
        return len(text)

    def flush(self) -> None:
        return None


class _DeadStream:
    """Stream whose ``write`` and ``flush`` always raise, like a closed or broken pipe."""

    def __init__(self, error: BaseException) -> None:
        self._error = error
        self.write_attempts = 0

    def write(self, _text: str) -> int:
        self.write_attempts += 1
        raise self._error

    def flush(self) -> None:
        raise self._error


class _FlakyStream:
    """Stream that accepts a fixed number of writes and then fails permanently."""

    def __init__(self, accepts: int, error: BaseException) -> None:
        self._accepts = accepts
        self._error = error
        self.written: list[str] = []
        self.write_attempts = 0

    def write(self, text: str) -> int:
        self.write_attempts += 1
        if len(self.written) >= self._accepts:
            raise self._error
        self.written.append(text)
        return len(text)

    def flush(self) -> None:
        return None


def _closed_stream() -> io.TextIOWrapper:
    stream = open(os.devnull, "w", encoding="utf-8")
    stream.close()
    return stream


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


def test_configure_diagnostic_streams_reconfigures_capable_streams(monkeypatch: pytest.MonkeyPatch) -> None:
    """The guard must not disable the UTF-8 upgrade on streams that do support it."""

    out, err = _CapableStream(), _CapableStream()
    monkeypatch.setattr(sys, "stdout", out)
    monkeypatch.setattr(sys, "stderr", err)

    gate.configure_diagnostic_streams()

    assert out.reconfigured == [{"encoding": "utf-8", "errors": "replace"}]
    assert err.reconfigured == [{"encoding": "utf-8", "errors": "replace"}]


@pytest.mark.parametrize(
    "make_stream",
    [
        pytest.param(lambda: None, id="missing"),
        pytest.param(io.StringIO, id="no-reconfigure-attribute"),
        pytest.param(_closed_stream, id="closed"),
        pytest.param(lambda: _HostileReconfigureStream(ValueError("underlying buffer detached")), id="detached"),
        pytest.param(lambda: _HostileReconfigureStream(OSError("device disappeared")), id="oserror"),
        pytest.param(lambda: _HostileReconfigureStream(AttributeError("buffer is gone")), id="attributeerror"),
    ],
)
def test_configure_diagnostic_streams_tolerates_unreconfigurable_streams(
    monkeypatch: pytest.MonkeyPatch, make_stream: Any
) -> None:
    monkeypatch.setattr(sys, "stdout", make_stream())
    monkeypatch.setattr(sys, "stderr", make_stream())

    gate.configure_diagnostic_streams()

    assert isinstance(gate.emit_diagnostic("post-configure diagnostic"), bool)


def test_ascii_fallback_is_total_and_bounded() -> None:
    assert gate.ascii_fallback("") == ""
    assert gate.ascii_fallback("plain ascii line") == "plain ascii line"
    assert gate.ascii_fallback("check \u2705 done") == "check \\u2705 done"
    assert gate.ascii_fallback("lone \udcff surrogate") == "lone \\udcff surrogate"

    rendered = gate.ascii_fallback("\u2192" * gate._LOG_LINE_LIMIT)
    assert rendered.isascii()
    assert len(rendered) == gate._LOG_LINE_LIMIT
    assert rendered.endswith("...")


def test_emit_diagnostic_writes_the_line_and_its_own_terminator(monkeypatch: pytest.MonkeyPatch) -> None:
    stream = _CapableStream()
    monkeypatch.setattr(sys, "stdout", stream)

    assert gate.emit_diagnostic("- [block] language docs/x.md: bad") is True
    assert stream.written == ["- [block] language docs/x.md: bad\n"]


def test_emit_diagnostic_falls_back_to_ascii_on_restrictive_streams(monkeypatch: pytest.MonkeyPatch) -> None:
    stream = _EncodingBoundStream("cp1252")
    monkeypatch.setattr(sys, "stdout", stream)

    assert gate.emit_diagnostic("- [block] language docs/x.md: \u2705 \u2192 done") is True
    assert stream.written == ["- [block] language docs/x.md: \\u2705 \\u2192 done\n"]


@pytest.mark.parametrize(
    "make_stream",
    [
        pytest.param(lambda: None, id="missing"),
        pytest.param(_closed_stream, id="closed"),
        pytest.param(lambda: _DeadStream(ValueError("I/O operation on closed file.")), id="closed-shim"),
        pytest.param(lambda: _DeadStream(OSError("broken pipe")), id="broken-pipe"),
        pytest.param(lambda: _DeadStream(AttributeError("write is gone")), id="not-writable"),
    ],
)
def test_emit_diagnostic_reports_loss_instead_of_raising(monkeypatch: pytest.MonkeyPatch, make_stream: Any) -> None:
    monkeypatch.setattr(sys, "stdout", make_stream())

    assert gate.emit_diagnostic("- [block] language docs/x.md: bad") is False


def test_emit_diagnostic_stops_after_the_ascii_fallback_also_fails(monkeypatch: pytest.MonkeyPatch) -> None:
    stream = _DeadStream(UnicodeEncodeError("ascii", "\u2705", 0, 1, "not encodable"))
    monkeypatch.setattr(sys, "stdout", stream)

    assert gate.emit_diagnostic("\u2705 unencodable") is False
    assert stream.write_attempts == 2


def test_log_findings_stops_at_the_first_dead_write(monkeypatch: pytest.MonkeyPatch) -> None:
    stream = _DeadStream(OSError("broken pipe"))
    monkeypatch.setattr(sys, "stdout", stream)

    gate.log_findings({"deterministic": {"findings": [_det_fail()["findings"][0]]}})

    assert stream.write_attempts == 1


def test_log_findings_emits_what_it_can_before_the_stream_dies(monkeypatch: pytest.MonkeyPatch) -> None:
    stream = _FlakyStream(3, OSError("broken pipe"))
    monkeypatch.setattr(sys, "stdout", stream)
    findings = [
        {"check": "language", "severity": "block", "path": f"docs/{index}.md", "message": "bad"}
        for index in range(gate._LOG_FINDING_LIMIT + 3)
    ]

    gate.log_findings({"deterministic": {"findings": findings}})

    assert len(stream.written) == 3
    assert stream.write_attempts == 4


def test_flush_diagnostics_keeps_healthy_streams(monkeypatch: pytest.MonkeyPatch) -> None:
    out, err = _CapableStream(), _CapableStream()
    monkeypatch.setattr(sys, "stdout", out)
    monkeypatch.setattr(sys, "stderr", err)

    gate.flush_diagnostics()

    assert (out.flushes, err.flushes) == (1, 1)
    assert sys.stdout is out
    assert sys.stderr is err


def test_flush_diagnostics_detaches_unflushable_streams(monkeypatch: pytest.MonkeyPatch) -> None:
    """CPython turns an unflushable std stream into exit status 120 during finalization."""

    monkeypatch.setattr(sys, "stdout", _DeadStream(OSError("flush failed")))
    monkeypatch.setattr(sys, "stderr", _DeadStream(ValueError("I/O operation on closed file.")))

    gate.flush_diagnostics()

    assert sys.stdout is None
    assert sys.stderr is None


def test_flush_diagnostics_tolerates_missing_streams(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(sys, "stdout", None)
    monkeypatch.setattr(sys, "stderr", None)

    gate.flush_diagnostics()

    assert sys.stdout is None


@pytest.mark.parametrize(
    ("deterministic", "expected_exit", "expected_conclusion"),
    [
        (_det_pass, 0, "pass"),
        (_det_fail, 1, "fail"),
    ],
)
def test_main_keeps_gate_json_and_exit_code_without_usable_diagnostics(
    monkeypatch: pytest.MonkeyPatch,
    workspace: Path,
    deterministic: Any,
    expected_exit: int,
    expected_conclusion: str,
) -> None:
    paths = _write_cli_inputs(workspace)
    monkeypatch.setattr(gate.autodoc_verify, "verify", deterministic)
    monkeypatch.setattr(sys, "stdout", _DeadStream(ValueError("I/O operation on closed file.")))

    exit_code = gate.main(_cli_argv(paths))

    result = json.loads(paths["out"].read_text(encoding="utf-8"))
    assert exit_code == expected_exit
    assert result["conclusion"] == expected_conclusion
    assert result["deterministic"] == deterministic()
    assert sys.stdout is None


_VERIFIER_PASS = (
    "autodoc_verify.verify = lambda *a, **k: "
    "{'pass': True, 'findings': [], 'summary': {'block_findings': 0, 'warn_findings': 0}}"
)

_CP1252_ONLY_STDOUT = """\
class _Cp1252Only:
    def __init__(self, buffer):
        self._buffer = buffer

    def write(self, text):
        self._buffer.write(text.encode("cp1252"))
        return len(text)

    def flush(self):
        self._buffer.flush()

sys.stdout = _Cp1252Only(sys.__stdout__.buffer)
"""

_UNFLUSHABLE_STDOUT = """\
class _Unflushable:
    def write(self, text):
        return len(text)

    def flush(self):
        raise OSError("stdout flush failed")

sys.stdout = _Unflushable()
"""

_CLOSED_STDOUT = """\
import os

_closed = open(os.devnull, "w")
_closed.close()
sys.stdout = _closed
"""


def _run_gate_in_subprocess(
    workspace: Path,
    argv: list[str],
    *,
    stream_setup: str,
    verifier: str = _VERIFIER_PASS,
) -> subprocess.CompletedProcess[bytes]:
    """Execute the gate's real ``__main__`` block with a hostile ``sys.stdout`` installed."""

    gate_path = str(SCRIPT_DIR / "autodoc_verify_gate.py")
    runner = workspace / "runner.py"
    runner.write_text(
        "\n".join(
            [
                "import sys",
                f"sys.path.insert(0, {str(SCRIPT_DIR)!r})",
                "import autodoc_verify",
                verifier,
                stream_setup,
                f"sys.argv = {[gate_path, *argv]!r}",
                "import runpy",
                f"runpy.run_path({gate_path!r}, run_name='__main__')",
                "",
            ]
        ),
        encoding="utf-8",
    )
    return subprocess.run([sys.executable, str(runner)], capture_output=True, check=False)


def test_cli_survives_restrictive_stream_without_reconfigure(workspace: Path) -> None:
    """A cp1252-only stdout that lacks ``reconfigure`` must degrade the log, not the gate."""

    paths = _write_cli_inputs(workspace)
    message = "Line 3: \u2705 ::error::spoofed " + ("\u2192" * (gate._LOG_MESSAGE_LIMIT + 50))
    deterministic = {
        "pass": False,
        "findings": [{"check": "language", "severity": "block", "path": ALLOWED_PATH, "message": message}],
        "summary": {"block_findings": 1, "warn_findings": 0},
    }
    verifier = f"_RESULT = {deterministic!r}\nautodoc_verify.verify = lambda *a, **k: _RESULT"

    completed = _run_gate_in_subprocess(
        workspace, _cli_argv(paths), stream_setup=_CP1252_ONLY_STDOUT, verifier=verifier
    )

    stdout = completed.stdout.decode("cp1252")
    stderr = completed.stderr.decode("utf-8", "replace")
    result = json.loads(paths["out"].read_text(encoding="utf-8"))
    finding_lines = [line for line in stdout.splitlines() if line.startswith("- [")]

    assert completed.returncode == 1
    assert "Traceback" not in stderr
    assert stdout.isascii()
    assert len(finding_lines) == 1
    assert len(finding_lines[0]) <= gate._LOG_LINE_LIMIT
    logged_message = finding_lines[0].split(": ", 1)[1]
    assert logged_message.startswith("Line 3: \\u2705 ::error::spoofed")
    assert all(not line.lstrip().startswith("::") for line in stdout.splitlines())
    assert result["conclusion"] == "fail"
    assert result["deterministic"]["findings"][0]["message"] == message


@pytest.mark.parametrize(
    "stream_setup",
    [
        pytest.param("sys.stdout = None", id="missing"),
        pytest.param(_CLOSED_STDOUT, id="closed"),
        pytest.param("import io\nsys.stdout = io.StringIO()", id="no-reconfigure-attribute"),
        pytest.param(_UNFLUSHABLE_STDOUT, id="unflushable"),
    ],
)
@pytest.mark.parametrize(
    ("use_missing_contract", "expected_exit", "expected_conclusion"),
    [
        pytest.param(False, 0, "pass", id="pass"),
        pytest.param(True, 2, "needs_human", id="needs-human"),
    ],
)
def test_cli_preserves_exit_code_and_gate_json_for_hostile_streams(
    workspace: Path,
    stream_setup: str,
    use_missing_contract: bool,
    expected_exit: int,
    expected_conclusion: str,
) -> None:
    """Both consumers route on the exit code alone, so it must survive unusable diagnostics."""

    paths = _write_cli_inputs(workspace)
    contract = workspace / "absent-contract.json" if use_missing_contract else None

    completed = _run_gate_in_subprocess(workspace, _cli_argv(paths, contract=contract), stream_setup=stream_setup)

    result = json.loads(paths["out"].read_text(encoding="utf-8"))
    assert completed.returncode == expected_exit
    assert b"Traceback" not in completed.stderr
    assert result["conclusion"] == expected_conclusion


def _cli_argv(paths: dict[str, Path], *, contract: Path | None = None) -> list[str]:
    return [
        "--contract",
        str(contract if contract is not None else paths["contract"]),
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
