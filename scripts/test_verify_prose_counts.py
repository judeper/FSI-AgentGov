"""Tests for ``scripts/verify_prose_counts.py``.

Drives the three checks against synthetic fixtures via monkeypatched module
constants. Covers a positive case (clean repo) plus three negative cases
(one per check) plus the rubber-duck-flagged false-positive scenarios that
caused the verifier to fail itself during AS9b development:

  * SOX 302/404 in a regulation-name cell must NOT be flagged
  * "Tier 2 companion solutions" inside a Solution Details paragraph must
    NOT be flagged
  * Historical version-history prose accurately quoting a prior version
    count must NOT be flagged
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPTS_DIR = REPO_ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS_DIR))

import verify_prose_counts as vpc  # noqa: E402, I001


CLEAN_REGULATORY = """\
## Regulations

Some preamble.

## Control Coverage Summary by Regulation

!!! warning "Quantitative coverage figures temporarily withdrawn"
    Numeric per-regulation control counts and coverage percentages
    previously published in this table reflected a hand-curated mapping
    against an earlier 72-control catalog.

| Regulation | Implementation Status |
|-----------|----------------------|
| FINRA 4511 | Full coverage - implementation required |
| SOX 302/404 | Substantial coverage |
| SEC 17a-3/4 | Substantial coverage |
| FINRA 3110/2111 (AI) | Partial - supervision/suitability focus |

> Note: see disclaimer.

## Next Section

Goodbye.
"""


DRIFT_REGULATORY = """\
## Control Coverage Summary by Regulation

!!! warning "Quantitative coverage figures temporarily withdrawn"
    body text.

| Regulation | Applicable Controls | Coverage |
|-----------|---------------------|----------|
| FINRA 4511 | 62/72 | 86% |
| SOX 302/404 | 35/72 | 49% |
"""


CLEAN_INVENTORY = """\
## Companion Inventory (3 Solutions: 2 Live + 1 Preview)

| Solution | Folder | Version | Summary |
|----------|--------|---------|---------|
| [Alpha](#alpha) | [`alpha`](https://example.com/alpha) | v1.0.0 | First. |
| [Beta](#beta) | [`beta`](https://example.com/beta) | v1.0.0 | Second. |
| [Gamma](#gamma) | [`gamma`](https://example.com/gamma) | v0.1.0-preview | Preview. |

## Solution Details

### Alpha

- Patterns: P1
- Drivers: AI Governance
- Wires Tier 2 companion solutions into the dashboard.
"""


DRIFT_INVENTORY_ROW_COUNT_OFF = """\
## Companion Inventory (3 Solutions)

| Solution | Folder |
|----------|--------|
| [Alpha](#alpha) | [`alpha`](https://example.com/alpha) |
| [Beta](#beta) | [`beta`](https://example.com/beta) |
"""


PROSE_GOOD_README = """\
# Project

## Overview

The companion repo contains 3 companion solutions (2 live + 1 preview).
All 2 live companion solutions are tagged with metadata.

## What's New in v1.6

- 2 live solution implementations plus 1 preview solution (3 companion
  solutions total) cover the catalog.

## Document Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.5 | 2026 | 35 companion solutions tagged with CAPE metadata |
"""


PROSE_DRIFT_README = """\
# Project

## Overview

The companion repo contains 4 companion solutions.
"""


def _write_lock(tmp_path: Path) -> Path:
    lock = tmp_path / "solutions-lock.json"
    payload = {
        "schemaVersion": "1.0.0",
        "solutions": {
            "alpha": {"id": "alpha", "status": "live"},
            "beta": {"id": "beta", "status": "live"},
            "gamma": {"id": "gamma", "status": "preview"},
        },
    }
    lock.write_text(json.dumps(payload), encoding="utf-8")
    return lock


def _setup(monkeypatch, tmp_path, *, regulatory: str, inventory: str,
           prose_files: dict[str, str]) -> None:
    """Lay out fixture files and re-point module globals at them."""
    lock = _write_lock(tmp_path)
    reg_path = tmp_path / "regulatory.md"
    reg_path.write_text(regulatory, encoding="utf-8")
    inv_path = tmp_path / "inventory.md"
    inv_path.write_text(inventory, encoding="utf-8")
    prose_paths: list[Path] = []
    for name, body in prose_files.items():
        p = tmp_path / name
        p.write_text(body, encoding="utf-8")
        prose_paths.append(p)
    monkeypatch.setattr(vpc, "REPO_ROOT", tmp_path)
    monkeypatch.setattr(vpc, "LOCK_FILE", lock)
    monkeypatch.setattr(vpc, "REGULATORY_FILE", reg_path)
    monkeypatch.setattr(vpc, "SOLUTIONS_INDEX", inv_path)
    monkeypatch.setattr(vpc, "WATCHED_PROSE_FILES", prose_paths)
    # Re-bind the per-file skip with the test inventory path so Check 3
    # skips the inventory and Solution Details sections within it.
    monkeypatch.setattr(
        vpc,
        "PER_FILE_SECTION_SKIPS",
        {inv_path: ("Companion Inventory", "Solution Details")},
    )


def test_passes_on_clean_repo(monkeypatch, tmp_path):
    _setup(
        monkeypatch, tmp_path,
        regulatory=CLEAN_REGULATORY,
        inventory=CLEAN_INVENTORY,
        prose_files={"readme.md": PROSE_GOOD_README},
    )
    n, msgs, counts = vpc.run_all_checks()
    assert n == 0, "\n".join(msgs)
    assert counts == {"total": 3, "live": 2, "preview": 1}


def test_fails_on_reintroduced_table_denominator(monkeypatch, tmp_path):
    _setup(
        monkeypatch, tmp_path,
        regulatory=DRIFT_REGULATORY,
        inventory=CLEAN_INVENTORY,
        prose_files={"readme.md": PROSE_GOOD_README},
    )
    n, msgs, _ = vpc.run_all_checks()
    assert n >= 1
    joined = "\n".join(msgs)
    assert "62/72" in joined or "35/72" in joined


def test_fails_on_inventory_row_count_drift(monkeypatch, tmp_path):
    _setup(
        monkeypatch, tmp_path,
        regulatory=CLEAN_REGULATORY,
        inventory=DRIFT_INVENTORY_ROW_COUNT_OFF,
        prose_files={"readme.md": PROSE_GOOD_README},
    )
    n, msgs, _ = vpc.run_all_checks()
    assert n >= 1
    assert any("Companion Inventory" in m for m in msgs)


def test_fails_on_prose_count_drift(monkeypatch, tmp_path):
    _setup(
        monkeypatch, tmp_path,
        regulatory=CLEAN_REGULATORY,
        inventory=CLEAN_INVENTORY,
        prose_files={"readme.md": PROSE_DRIFT_README},
    )
    n, msgs, _ = vpc.run_all_checks()
    assert n >= 1
    assert any("4 total" in m for m in msgs)


def test_does_not_flag_sox_section_citation(monkeypatch, tmp_path):
    """SOX 302/404 in a regulation-name cell is NOT a control denominator."""
    body = """\
## Control Coverage Summary by Regulation

| Regulation | Implementation Status |
|-----------|----------------------|
| SOX 302/404 | Substantial coverage |
| FINRA 3110/2111 (AI) | Partial |
| SEC 17a-3/4 | Substantial coverage |
"""
    _setup(
        monkeypatch, tmp_path,
        regulatory=body,
        inventory=CLEAN_INVENTORY,
        prose_files={"readme.md": PROSE_GOOD_README},
    )
    n, msgs, _ = vpc.run_all_checks()
    assert n == 0, "\n".join(msgs)


def test_does_not_flag_tier_descriptor_in_inventory(monkeypatch, tmp_path):
    """'Tier 2 companion solutions' inside Solution Details prose is OK."""
    inventory_with_tier_text = CLEAN_INVENTORY  # already mentions "Tier 2"
    _setup(
        monkeypatch, tmp_path,
        regulatory=CLEAN_REGULATORY,
        inventory=inventory_with_tier_text,
        prose_files={"readme.md": PROSE_GOOD_README},
    )
    n, msgs, _ = vpc.run_all_checks()
    assert n == 0, "\n".join(msgs)


def test_does_not_flag_history_section_quoting_old_count(monkeypatch, tmp_path):
    """Release-history prose accurately quoting a prior version count is OK."""
    readme = """\
# Project

## Overview

3 companion solutions (2 live + 1 preview).

## Document Version History

| Version | Notes |
|---------|-------|
| 1.5.0 | 35 companion solutions tagged with CAPE metadata |
| 1.4.0 | 33 companion solutions in catalog |
"""
    _setup(
        monkeypatch, tmp_path,
        regulatory=CLEAN_REGULATORY,
        inventory=CLEAN_INVENTORY,
        prose_files={"readme.md": readme},
    )
    n, msgs, _ = vpc.run_all_checks()
    assert n == 0, "\n".join(msgs)


def test_check_mode_returns_nonzero_exit(monkeypatch, tmp_path, capsys):
    _setup(
        monkeypatch, tmp_path,
        regulatory=CLEAN_REGULATORY,
        inventory=CLEAN_INVENTORY,
        prose_files={"readme.md": PROSE_DRIFT_README},
    )
    rc = vpc.main(["--check"])
    assert rc == 1
    out = capsys.readouterr().out
    assert "drift issue" in out


def test_default_mode_returns_zero_even_on_drift(monkeypatch, tmp_path):
    """Without --check, drift is reported but exit is 0 (advisory mode)."""
    _setup(
        monkeypatch, tmp_path,
        regulatory=CLEAN_REGULATORY,
        inventory=CLEAN_INVENTORY,
        prose_files={"readme.md": PROSE_DRIFT_README},
    )
    rc = vpc.main([])
    assert rc == 0
