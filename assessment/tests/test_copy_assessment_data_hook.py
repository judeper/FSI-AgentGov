"""Tests for ``scripts/hooks/copy_assessment_data.py``.

The mkdocs hook publishes the manifest to ``site/assessment/data/controls.json``.
Manifest ``TODO:`` authoring placeholders must be stripped before the file
reaches the customer-facing SPA (finding U-022).
"""
from __future__ import annotations

import importlib.util
import json
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
HOOK_PATH = REPO_ROOT / "scripts" / "hooks" / "copy_assessment_data.py"
MANIFEST_PATH = REPO_ROOT / "assessment" / "manifest" / "controls.json"


def _load_hook_module():
    spec = importlib.util.spec_from_file_location("copy_assessment_data_hook", HOOK_PATH)
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture(scope="module")
def hook():
    return _load_hook_module()


@pytest.fixture(scope="module")
def manifest():
    return json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))


def test_scrub_drops_todo_priority(hook):
    controls = [
        {
            "id": "X.1",
            "priority": "TODO: critical|high|medium|low",
            "yesBar": "TODO: concise pass criteria",
            "partialBar": "TODO: partial coverage criteria",
            "noBar": "TODO: fail criteria",
            "facilitatorNotes": {
                "ask": "TODO: facilitator question",
                "followUp": "TODO: follow-up hint",
                "timeBudgetMinutes": 5,
            },
        }
    ]
    cleaned, count = hook.scrub_manifest_todos(controls)
    assert count == 6
    c = cleaned[0]
    assert "priority" not in c
    assert c["yesBar"] == ""
    assert c["partialBar"] == ""
    assert c["noBar"] == ""
    assert c["facilitatorNotes"]["ask"] == ""
    assert c["facilitatorNotes"]["followUp"] == ""
    # timeBudgetMinutes is structural, not a placeholder.
    assert c["facilitatorNotes"]["timeBudgetMinutes"] == 5


def test_scrub_preserves_authored_values(hook):
    controls = [
        {
            "id": "1.1",
            "priority": "critical",
            "yesBar": "Environment Maker role removed from All Users.",
            "partialBar": "Publisher group exists but Environment Maker still open.",
            "noBar": "Environment Maker is open to All Users.",
            "facilitatorNotes": {
                "ask": "Is publishing restricted to a named publisher group?",
                "followUp": "Open Power Platform admin center > Environments.",
                "timeBudgetMinutes": 6,
            },
        }
    ]
    cleaned, count = hook.scrub_manifest_todos(controls)
    assert count == 0
    c = cleaned[0]
    assert c["priority"] == "critical"
    assert c["yesBar"].startswith("Environment Maker")
    assert c["facilitatorNotes"]["ask"].startswith("Is publishing")


def test_scrub_does_not_mutate_input(hook):
    original = {
        "id": "X.1",
        "priority": "TODO: critical",
        "facilitatorNotes": {"ask": "TODO: q", "followUp": "TODO: f", "timeBudgetMinutes": 5},
    }
    snapshot = json.loads(json.dumps(original))
    hook.scrub_manifest_todos([original])
    assert original == snapshot


def test_scrub_handles_missing_facilitator_notes(hook):
    controls = [{"id": "X.1", "priority": "high"}]
    cleaned, count = hook.scrub_manifest_todos(controls)
    assert count == 0
    assert cleaned[0] == {"id": "X.1", "priority": "high"}


def test_real_manifest_produces_zero_todo_leakage(hook, manifest):
    """Whatever TODOs exist in the committed manifest, none survive scrubbing."""
    cleaned, _ = hook.scrub_manifest_todos(manifest)
    serialized = json.dumps(cleaned)
    # No literal "TODO:" substring should survive in the published payload.
    assert "TODO:" not in serialized, "TODO placeholder leaked through scrubber"
    # And the scrubbed payload is still a list of 78 controls.
    assert len(cleaned) == 78


def test_write_manifest_scrubbed_emits_clean_file(hook, tmp_path):
    dest = tmp_path / "assessment" / "data" / "controls.json"
    scrubbed_count = hook._write_manifest_scrubbed(dest)
    assert dest.exists()
    payload = dest.read_text(encoding="utf-8")
    assert "TODO:" not in payload, "published manifest still contains TODO placeholders"
    parsed = json.loads(payload)
    assert isinstance(parsed, list)
    assert len(parsed) == 78
    # The scrubbed count is non-negative and bounded by 6 fields × 78 controls.
    assert 0 <= scrubbed_count <= 6 * 78
