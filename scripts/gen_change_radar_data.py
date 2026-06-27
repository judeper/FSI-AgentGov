#!/usr/bin/env python3
"""Generate the Change Radar data file for the FSI-AgentGov docs site.

Reads the confirmed, human-reviewed feed items in
``data/change-radar/items.json`` and the authoritative control manifest
(``assessment/manifest/controls.json``), validates that every referenced
control ID exists in the manifest, enriches each mapping with the control's
title and published URL, and emits the JSON consumed by the Change Radar page.

Unlike the Control Explorer generator, the Change Radar feed is **variable
length** -- it is a curated subset of platform changes, not the fixed 79-control
catalog -- so there is intentionally no ``EXPECTED_COUNT`` gate here. The only
hard invariant is that every referenced control ID is a member (subset) of the
manifest.

Output: ``docs/javascripts/change-radar-data.json`` with the shape::

    { "generatedAt": "<ISO-8601 UTC>", "count": <n>, "items": [ ... ] }

The script is idempotent except for ``generatedAt``; the drift checker
(``check_change_radar_data_drift.py``) compares everything but that field.
"""
from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
ITEMS = REPO_ROOT / "data" / "change-radar" / "items.json"
MANIFEST = REPO_ROOT / "assessment" / "manifest" / "controls.json"
OUTPUT = REPO_ROOT / "docs" / "javascripts" / "change-radar-data.json"

# Fields copied verbatim from each confirmed item into the published feed.
ITEM_PASSTHROUGH = (
    "id",
    "title",
    "summary",
    "products",
    "status",
    "timing",
    "gaDate",
    "roadmapUrl",
    "lifecycle",
    "whatToReview",
    "addedOn",
    "lastReviewed",
)
VALID_LIFECYCLE = {"active", "changed", "withdrawn"}


def _read_json(path: Path):
    if not path.exists():
        raise FileNotFoundError(f"expected file not found: {path.relative_to(REPO_ROOT)}")
    with path.open(encoding="utf-8") as handle:
        return json.load(handle)


def _control_index(manifest) -> dict:
    """Map control id -> {title, url} from the manifest."""
    controls = manifest if isinstance(manifest, list) else manifest.get("controls", [])
    index: dict[str, dict] = {}
    for control in controls:
        cid = str(control.get("id", "")).strip()
        if not cid:
            continue
        title = str(control.get("title", "")).strip()
        # Strip the "Control X.Y: " prefix the manifest uses in its title field.
        prefix = f"Control {cid}:"
        if title.startswith(prefix):
            title = title[len(prefix):].strip()
        # controlDocUrl is the absolute published path ("/controls/.../").
        url = (control.get("controlDocUrl") or "").strip()
        pillar = str(control.get("pillar_name", "")).strip()
        regs = [str(r).strip() for r in (control.get("regulatory") or []) if str(r).strip()]
        index[cid] = {"title": title, "url": url, "pillar": pillar, "regulations": regs}
    return index


def build() -> tuple[dict, list[str]]:
    """Build the feed document. Returns (doc, errors). Fabricate nothing."""
    errors: list[str] = []
    items_doc = _read_json(ITEMS)
    manifest = _read_json(MANIFEST)
    control_index = _control_index(manifest)

    raw_items = items_doc.get("items", []) if isinstance(items_doc, dict) else []
    if not isinstance(raw_items, list):
        errors.append("items.json 'items' must be a list")
        raw_items = []

    seen_ids: set = set()
    out_items: list[dict] = []
    for idx, item in enumerate(raw_items, 1):
        if not isinstance(item, dict):
            errors.append(f"item #{idx} is not a JSON object")
            continue
        item_id = item.get("id")
        if item_id is None:
            errors.append(f"item #{idx} is missing required field 'id'")
            continue
        if item_id in seen_ids:
            errors.append(f"item #{idx}: duplicate id {item_id!r}")
        seen_ids.add(item_id)

        lifecycle = item.get("lifecycle", "active")
        if lifecycle not in VALID_LIFECYCLE:
            errors.append(
                f"item {item_id}: invalid lifecycle {lifecycle!r} "
                f"(expected one of {sorted(VALID_LIFECYCLE)})"
            )

        out: dict = {}
        for key in ITEM_PASSTHROUGH:
            if key in item:
                out[key] = item[key]

        mapped_controls: list[dict] = []
        pillars: list[str] = []
        regulations: list[str] = []
        for ctrl in item.get("controls", []):
            cid = str(ctrl.get("id", "")).strip()
            if cid not in control_index:
                errors.append(
                    f"item {item_id}: control id {cid!r} is not in the manifest "
                    f"(assessment/manifest/controls.json)"
                )
                continue
            meta = control_index[cid]
            mapped_controls.append(
                {
                    "id": cid,
                    "title": meta["title"],
                    "url": meta["url"],
                    "pillar": meta["pillar"],
                    "rationale": str(ctrl.get("rationale", "")).strip(),
                }
            )
            if meta["pillar"] and meta["pillar"] not in pillars:
                pillars.append(meta["pillar"])
            for reg in meta["regulations"]:
                if reg not in regulations:
                    regulations.append(reg)
        if not mapped_controls:
            errors.append(f"item {item_id}: no valid control mappings")
        out["controls"] = mapped_controls
        out["pillars"] = sorted(pillars)
        out["regulations"] = sorted(regulations)
        out_items.append(out)

    doc = {
        "generatedAt": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "count": len(out_items),
        "items": out_items,
    }
    return doc, errors


def main() -> int:
    try:
        doc, errors = build()
    except (FileNotFoundError, json.JSONDecodeError, ValueError) as exc:
        print(f"FAIL: {exc}")
        return 1

    if errors:
        print("FAIL: Change Radar items did not validate:")
        for err in errors:
            print(f"  - {err}")
        return 1

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(doc, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    print("Change Radar data generator")
    print(f"  items    : {ITEMS.relative_to(REPO_ROOT)}")
    print(f"  output   : {OUTPUT.relative_to(REPO_ROOT)}")
    print(f"  count    : {doc['count']} feed item(s)")
    all_controls = sorted({c["id"] for it in doc["items"] for c in it["controls"]})
    print(f"  controls : {len(all_controls)} distinct control(s) referenced")
    return 0


if __name__ == "__main__":
    sys.exit(main())
