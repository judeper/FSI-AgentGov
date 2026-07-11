"""Offline tests for the Change Radar pipeline.

Covers the monitor (baseline suppression, change detection, fail-closed shape
handling, agent filter), the generator, and the drift/language checker. All
tests run fully offline using injected fixtures and ``tmp_path`` -- no network
and no mutation of repo state.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

SCRIPTS_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPTS_DIR.parent
sys.path.insert(0, str(SCRIPTS_DIR))

import change_radar_monitor as cr  # noqa: E402
import check_change_radar_data_drift as drift  # noqa: E402
import gen_change_radar_data as gen  # noqa: E402

ITEM_A = {
    "id": 111,
    "title": "Copilot Studio: agent sharing controls",
    "description": "Admins govern agent sharing and publishing.",
    "status": "Launched",
    "publicDisclosureAvailabilityDate": "October CY2025",
    "tagsContainer": {"products": [{"tagName": "Microsoft Copilot Studio"}]},
}
ITEM_B = {
    "id": 222,
    "title": "Purview: audit logs for agent management",
    "description": "Agent admin actions recorded in unified audit.",
    "status": "Launched",
    "tagsContainer": {"products": [{"tagName": "Microsoft Purview"}]},
}
ITEM_NON_AGENT = {
    "id": 999,
    "title": "Edge: new tab page refresh",
    "description": "Unrelated browser change.",
    "status": "In development",
    "tagsContainer": {"products": [{"tagName": "Microsoft Edge"}]},
}


def _write(path: Path, items: list) -> str:
    path.write_text(json.dumps(items), encoding="utf-8")
    return str(path)


def _run(tmp_path: Path, items: list, name: str) -> tuple[int, Path, Path]:
    fixture = _write(tmp_path / f"{name}.json", items)
    state = tmp_path / "state.json"
    pending = tmp_path / "pending"
    reports = tmp_path / "reports"
    rc = cr.main([
        "--input", fixture,
        "--state", str(state),
        "--pending-dir", str(pending),
        "--report-dir", str(reports),
    ])
    return rc, pending, reports


# --- module import / API surface ---

def test_modules_expose_main():
    assert callable(cr.main)
    assert callable(gen.main)
    assert callable(drift.main)


# --- agent filter ---

def test_is_agent_relevant_filter():
    assert cr.is_agent_relevant(ITEM_A)
    assert cr.is_agent_relevant(ITEM_B)
    assert not cr.is_agent_relevant(ITEM_NON_AGENT)


def test_item_hash_is_stable_and_change_sensitive():
    h1 = cr.item_hash(ITEM_A)
    h2 = cr.item_hash(dict(ITEM_A))
    assert h1 == h2
    changed = dict(ITEM_A, status="Rolling out")
    assert cr.item_hash(changed) != h1


# --- baseline suppression ---

def test_first_run_suppresses_pending(tmp_path: Path):
    rc, pending, reports = _run(tmp_path, [ITEM_A, ITEM_B, ITEM_NON_AGENT], "v1")
    assert rc == 0
    assert not pending.exists() or not list(pending.glob("*.json"))
    state = json.loads((tmp_path / "state.json").read_text(encoding="utf-8"))
    roadmap = state["sources"]["roadmap"]
    assert roadmap["last_run"]
    # Only agent-relevant items are baselined.
    assert set(roadmap["items"].keys()) == {"111", "222"}


def test_second_identical_run_detects_no_changes(tmp_path: Path):
    _run(tmp_path, [ITEM_A, ITEM_B, ITEM_NON_AGENT], "v1")
    rc, pending, _ = _run(tmp_path, [ITEM_A, ITEM_B, ITEM_NON_AGENT], "v1b")
    assert rc == 0
    assert not pending.exists() or not list(pending.glob("*.json"))


# --- delta detection: new / changed / withdrawn ---

def test_delta_writes_pending_blobs(tmp_path: Path):
    _run(tmp_path, [ITEM_A, ITEM_B, ITEM_NON_AGENT], "v1")
    item_a_changed = dict(ITEM_A, status="Rolling out")
    item_new = {
        "id": 333,
        "title": "Power Platform: agent inventory export",
        "description": "Agent inventory metadata export.",
        "status": "Launched",
        "tagsContainer": {"products": [{"tagName": "Microsoft Power Platform"}]},
    }
    rc, pending, reports = _run(
        tmp_path, [item_a_changed, item_new, ITEM_NON_AGENT], "v2"
    )
    assert rc == 1  # changes staged -> signals the workflow to open the gate PR
    blobs = sorted(p.name for p in pending.glob("*.json"))
    # 111 changed, 333 new, 222 withdrawn.
    assert any("roadmap-111-" in b for b in blobs)
    assert any("roadmap-333-" in b for b in blobs)
    assert any("roadmap-222-" in b for b in blobs)
    assert list(reports.glob("change-radar-*.md"))


def test_pending_blob_shape_and_no_published_mapping(tmp_path: Path):
    _run(tmp_path, [ITEM_A, ITEM_B], "v1")
    item_new = {
        "id": 444,
        "title": "Copilot Studio: agent audit export",
        "description": "Audit logs for agent management.",
        "status": "Launched",
        "tagsContainer": {"products": [{"tagName": "Microsoft Purview"}]},
    }
    _, pending, _ = _run(tmp_path, [ITEM_A, ITEM_B, item_new], "v2")
    blob = json.loads(next(pending.glob("roadmap-444-*.json")).read_text(encoding="utf-8"))
    assert blob["change_type"] == "new"
    assert blob["source"] == "roadmap"
    # Suggested mappings are present but explicitly unconfirmed (never published).
    assert "suggested_controls" in blob
    assert any(c["id"] == "1.7" for c in blob["suggested_controls"])  # "audit" keyword
    assert "UNCONFIRMED" in blob["note"]


# --- fail-closed ---

def test_fail_closed_on_non_list_shape(tmp_path: Path):
    fixture = tmp_path / "bad.json"
    fixture.write_text(json.dumps({"value": []}), encoding="utf-8")
    rc = cr.main(["--input", str(fixture), "--state", str(tmp_path / "s.json"),
                  "--pending-dir", str(tmp_path / "p"), "--report-dir", str(tmp_path / "r")])
    assert rc == 2
    assert not (tmp_path / "s.json").exists()


def test_fail_closed_on_missing_required_fields(tmp_path: Path):
    fixture = tmp_path / "bad2.json"
    fixture.write_text(json.dumps([{"id": 1}]), encoding="utf-8")  # missing 'title'
    rc = cr.main(["--input", str(fixture), "--state", str(tmp_path / "s.json"),
                  "--pending-dir", str(tmp_path / "p"), "--report-dir", str(tmp_path / "r")])
    assert rc == 2


# --- generator + drift against the real committed data ---

def test_generator_builds_clean_and_subset_of_manifest():
    doc, errors = gen.build()
    assert errors == [], f"items.json failed validation: {errors}"
    assert doc["count"] == len(doc["items"])
    manifest = json.loads(gen.MANIFEST.read_text(encoding="utf-8"))
    manifest_ids = {str(c["id"]) for c in (manifest if isinstance(manifest, list) else manifest["controls"])}
    referenced = {c["id"] for it in doc["items"] for c in it["controls"]}
    assert referenced <= manifest_ids  # subset, not equality


def test_committed_data_passes_drift_and_language():
    assert drift.main(["--check"]) == 0
