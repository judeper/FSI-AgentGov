"""Tests for ``scripts/verify_solutions_docs.py``."""

from __future__ import annotations

import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPTS_DIR = REPO_ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS_DIR))

import verify_solutions_docs as vsd  # noqa: E402, I001

LOCK_PAYLOAD = {
    "schemaVersion": "1.5.0",
    "counts": {"total": 2, "live": 1, "preview": 1},
    "solutions": {
        "alpha": {
            "id": "alpha",
            "version": "1.0.0",
            "status": "live",
            "controls": ["1.1", "2.1"],
        },
        "beta": {
            "id": "beta",
            "version": "0.1.0-preview",
            "status": "preview",
            "controls": ["3.1"],
        },
    },
}

SOLUTIONS_INDEX_GOOD = """\
## Companion Inventory (2 Solutions: 1 Live + 1 Preview)

| Solution | Repository folder | Version | Primary controls | Patterns | Drivers | CoE | Summary |
|----------|-------------------|---------|------------------|----------|---------|-----|---------|
| [Alpha](#alpha) | [`alpha`](https://github.com/judeper/FSI-AgentGov-Solutions/tree/main/alpha) | v1.0.0 | 1.1, 2.1 | P1 | AI Governance | Govern | Live. |
| [Beta](#beta) | [`beta`](https://github.com/judeper/FSI-AgentGov-Solutions/tree/main/beta) | v0.1.0-preview | 3.1 | — | — | — | **Preview.** Preview summary. |

## Solution Details

### Alpha
- **Repository folder:** [`alpha`](https://github.com/judeper/FSI-AgentGov-Solutions/tree/main/alpha)
- **Version:** v1.0.0
- **Primary controls:** 1.1, 2.1

### Beta
- **Repository folder:** [`beta`](https://github.com/judeper/FSI-AgentGov-Solutions/tree/main/beta)
- **Version:** v0.1.0-preview
- **Status:** Preview
- **Primary controls:** 3.1
"""

SOLUTIONS_INTEGRATION_GOOD = """\
## Solution-to-Control Mapping

### Alpha Example

| Control | How Solution Helps |
|---------|-------------------|
| **1.1 Alpha Control** | Example |

**Repository Link:** [alpha](https://github.com/judeper/FSI-AgentGov-Solutions/tree/main/alpha)

### Beta Example

| Control | How Solution Helps |
|---------|-------------------|
| **3.1 Beta Control** | Example |

**Repository Link:** [beta](https://github.com/judeper/FSI-AgentGov-Solutions/tree/main/beta)

## Cross-Solution Integration Layer
"""


SENTINEL_LINE = (
    "*No companion solution for this control — see the "
    "[Solutions Index](../../reference/solutions-index.md#coverage-scope) for the "
    "full companion-solution catalog and coverage scope.*"
)

# 4.9 is absent from LOCK_PAYLOAD, so the sentinel is correct there.
CONTROL_DOCS_GOOD = {"4.9-unmapped-control.md": f"# Control 4.9\n\n{SENTINEL_LINE}\n"}


def _setup(
    monkeypatch,
    tmp_path,
    *,
    solutions_index: str,
    solutions_integration: str,
    control_docs: dict[str, str] | None = None,
) -> None:
    lock = tmp_path / "solutions-lock.json"
    lock.write_text(json.dumps(LOCK_PAYLOAD), encoding="utf-8")
    index = tmp_path / "solutions-index.md"
    index.write_text(solutions_index, encoding="utf-8")
    integration = tmp_path / "solutions-integration.md"
    integration.write_text(solutions_integration, encoding="utf-8")

    controls_dir = tmp_path / "controls" / "pillar-1-security"
    controls_dir.mkdir(parents=True)
    for name, body in (CONTROL_DOCS_GOOD if control_docs is None else control_docs).items():
        (controls_dir / name).write_text(body, encoding="utf-8")

    monkeypatch.setattr(vsd, "LOCK_FILE", lock)
    monkeypatch.setattr(vsd, "SOLUTIONS_INDEX", index)
    monkeypatch.setattr(vsd, "SOLUTIONS_INTEGRATION", integration)
    monkeypatch.setattr(vsd, "CONTROLS_DIR", tmp_path / "controls")


def test_passes_on_clean_docs(monkeypatch, tmp_path):
    _setup(
        monkeypatch,
        tmp_path,
        solutions_index=SOLUTIONS_INDEX_GOOD,
        solutions_integration=SOLUTIONS_INTEGRATION_GOOD,
    )
    n, msgs = vsd.run_all_checks()
    assert n == 0, "\n".join(msgs)


def test_fails_on_inventory_controls_drift(monkeypatch, tmp_path):
    _setup(
        monkeypatch,
        tmp_path,
        solutions_index=SOLUTIONS_INDEX_GOOD.replace("| v1.0.0 | 1.1, 2.1 |", "| v1.0.0 | 1.1 |", 1),
        solutions_integration=SOLUTIONS_INTEGRATION_GOOD,
    )
    n, msgs = vsd.run_all_checks()
    assert n >= 1
    assert any("inventory row controls" in msg for msg in msgs)


def test_fails_when_preview_status_line_is_missing(monkeypatch, tmp_path):
    _setup(
        monkeypatch,
        tmp_path,
        solutions_index=SOLUTIONS_INDEX_GOOD.replace("- **Status:** Preview\n", "", 1),
        solutions_integration=SOLUTIONS_INTEGRATION_GOOD,
    )
    n, msgs = vsd.run_all_checks()
    assert n >= 1
    assert any("must include a status line" in msg for msg in msgs)


def test_fails_when_integration_section_uses_noncanonical_control(monkeypatch, tmp_path):
    _setup(
        monkeypatch,
        tmp_path,
        solutions_index=SOLUTIONS_INDEX_GOOD,
        solutions_integration=SOLUTIONS_INTEGRATION_GOOD.replace("**1.1 Alpha Control**", "**9.9 Alpha Control**", 1),
    )
    n, msgs = vsd.run_all_checks()
    assert n >= 1
    assert any("cites control '9.9'" in msg for msg in msgs)


def test_fails_when_integration_section_keeps_status_line(monkeypatch, tmp_path):
    _setup(
        monkeypatch,
        tmp_path,
        solutions_index=SOLUTIONS_INDEX_GOOD,
        solutions_integration=SOLUTIONS_INTEGRATION_GOOD.replace(
            "**Repository Link:** [alpha](https://github.com/judeper/FSI-AgentGov-Solutions/tree/main/alpha)",
            "**Status:** Completed\n\n**Repository Link:** [alpha](https://github.com/judeper/FSI-AgentGov-Solutions/tree/main/alpha)",
            1,
        ),
    )
    n, msgs = vsd.run_all_checks()
    assert n >= 1
    assert any("must not publish per-solution status lines" in msg for msg in msgs)


def test_fails_when_mapped_control_claims_no_companion_solution(monkeypatch, tmp_path):
    """Regression guard for the control 1.2 / agent-365-lifecycle-governance drift."""
    _setup(
        monkeypatch,
        tmp_path,
        solutions_index=SOLUTIONS_INDEX_GOOD,
        solutions_integration=SOLUTIONS_INTEGRATION_GOOD,
        control_docs={"1.1-mapped-control.md": f"# Control 1.1\n\n{SENTINEL_LINE}\n"},
    )
    n, msgs = vsd.run_all_checks()
    assert n >= 1
    assert any(
        "control 1.1 declares no companion solution" in msg and "'alpha'" in msg
        for msg in msgs
    )


def test_allows_control_to_omit_some_mapped_solutions(monkeypatch, tmp_path):
    """The check is a contradiction guard, not a completeness guard."""
    body = (
        "# Control 1.1\n\n"
        '!!! tip "Automation Available"\n'
        "    See [Alpha](https://github.com/judeper/FSI-AgentGov-Solutions/tree/main/alpha).\n"
    )
    _setup(
        monkeypatch,
        tmp_path,
        solutions_index=SOLUTIONS_INDEX_GOOD,
        solutions_integration=SOLUTIONS_INTEGRATION_GOOD,
        control_docs={"1.1-mapped-control.md": body, "2.1-also-mapped.md": body},
    )
    n, msgs = vsd.run_all_checks()
    assert n == 0, "\n".join(msgs)
