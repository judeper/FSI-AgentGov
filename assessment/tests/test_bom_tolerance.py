"""Regression tests for AS-ORCH-FIX BOM tolerance.

Closes F-RUN-ASSESSMENT-ORCH-BOM-01: Windows PowerShell 5.x collectors
emit JSON files with a UTF-8 BOM (EF BB BF prefix). The Python engine
loaders previously used encoding="utf-8" which raises UnicodeDecodeError
on BOM-prefixed input. Switched to encoding="utf-8-sig" which transparently
consumes the BOM if present.

These tests prove that score.py and score_frontier.py can each load a
BOM-prefixed JSON file without crashing.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

ASSESSMENT_ROOT = Path(__file__).resolve().parent.parent
ENGINE_DIR = ASSESSMENT_ROOT / "engine"

sys.path.insert(0, str(ENGINE_DIR))

import score  # noqa: E402
import score_frontier  # noqa: E402


def write_bom_json(path: Path, data: dict) -> None:
    """Write JSON file prefixed with a UTF-8 BOM (mimics Windows PS 5.x)."""
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = json.dumps(data, indent=2).encode("utf-8")
    path.write_bytes(b"\xef\xbb\xbf" + payload)


def test_score_load_json_tolerates_bom(tmp_path: Path) -> None:
    """score.load_json must accept BOM-prefixed JSON without crashing."""
    target = tmp_path / "ppac-bom.json"
    write_bom_json(target, {"controls": [], "_metadata": {"tenant": "t1"}})

    # First 3 bytes are BOM. Confirm fixture is set up correctly.
    assert target.read_bytes()[:3] == b"\xef\xbb\xbf"

    data = score.load_json(target)
    assert data == {"controls": [], "_metadata": {"tenant": "t1"}}


def test_score_frontier_load_json_tolerates_bom(tmp_path: Path) -> None:
    """score_frontier.load_json must accept BOM-prefixed JSON without crashing."""
    target = tmp_path / "frontier-bom.json"
    write_bom_json(target, {"_metadata": {}, "answers": {"q1": "yes"}})

    assert target.read_bytes()[:3] == b"\xef\xbb\xbf"

    data = score_frontier.load_json(target)
    assert data == {"_metadata": {}, "answers": {"q1": "yes"}}


def test_score_load_json_still_handles_no_bom(tmp_path: Path) -> None:
    """utf-8-sig must remain backward-compatible with BOM-less files."""
    target = tmp_path / "ppac-nobom.json"
    target.write_text(json.dumps({"k": "v"}), encoding="utf-8")

    assert target.read_bytes()[:3] != b"\xef\xbb\xbf"

    data = score.load_json(target)
    assert data == {"k": "v"}
