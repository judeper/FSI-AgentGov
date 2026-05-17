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


def _setup(monkeypatch, tmp_path, *, solutions_index: str, solutions_integration: str) -> None:
    lock = tmp_path / "solutions-lock.json"
    lock.write_text(json.dumps(LOCK_PAYLOAD), encoding="utf-8")
    index = tmp_path / "solutions-index.md"
    index.write_text(solutions_index, encoding="utf-8")
    integration = tmp_path / "solutions-integration.md"
    integration.write_text(solutions_integration, encoding="utf-8")
    monkeypatch.setattr(vsd, "LOCK_FILE", lock)
    monkeypatch.setattr(vsd, "SOLUTIONS_INDEX", index)
    monkeypatch.setattr(vsd, "SOLUTIONS_INTEGRATION", integration)


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
