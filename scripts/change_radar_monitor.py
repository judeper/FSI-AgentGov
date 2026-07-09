#!/usr/bin/env python3
"""Change Radar roadmap monitor (curation-assist, fail-closed).

Fetches the public **Microsoft Release Communications** feed (the Microsoft 365
roadmap), filters to agent-relevant items, and diffs them against a dedicated
state file. New, changed, or withdrawn items are written as **pending
candidates** (with *suggested* control mappings) for a human to review and then
hand-author into ``data/change-radar/items.json``. The monitor never publishes a
control mapping itself -- the published feed is author-written.

Design (mirrors ``learn_monitor.py`` but for a JSON API):
  * **Separate state file** ``data/change-radar-state.json`` (NOT the 4.8 MB
    shared ``monitor-state.json``) to avoid full-file rewrite contention.
  * **First-run baseline suppression** -- the first run records the current
    snapshot WITHOUT emitting pending items (the live feed has ~1900 items).
  * **Fail-closed on shape error** -- if the API is unreachable or the payload
    is not the expected list-of-items shape, exit non-zero and write nothing.
  * **Fail-closed surfacing** -- the monitor advances state in its working tree
    so the gate PR carries the new baseline; because state lives in git, the
    baseline only becomes authoritative when the PR merges. A closed (unmerged)
    PR leaves ``main`` untouched, so the items re-surface on the next run.
  * Raw Microsoft text is written only under ``data/change-radar-pending/``
    (excluded from the commercial-scope linter); it is never promoted to a
    published file.

Usage::

    python scripts/change_radar_monitor.py [--dry-run] [--input FILE] [--limit N]
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

SCRIPTS_DIR = Path(__file__).resolve().parent
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

import monitoring_shared as ms  # noqa: E402

REPO_ROOT = SCRIPTS_DIR.parent
API_URL = "https://www.microsoft.com/releasecommunications/api/v1/m365"
STATE_PATH = REPO_ROOT / "data" / "change-radar-state.json"
PENDING_DIR = REPO_ROOT / "data" / "change-radar-pending"
REPORT_DIR = REPO_ROOT / "reports" / "monitoring"
DOCS_DIR = REPO_ROOT / "docs"
SOURCE_KEY = "roadmap"
ROADMAP_URL_FMT = "https://www.microsoft.com/microsoft-365/roadmap?featureid={id}"
USER_AGENT = "FSI-AgentGov-ChangeRadar/1.0 (+https://github.com/judeper/FSI-AgentGov)"

# An item is agent-relevant when its title contains one of these markers. Kept
# deliberately precise (recall over a human gate is fine; noise is not).
AGENT_TITLE_KEYWORDS = ("agent", "copilot studio", "agent builder")

# Coarse keyword -> candidate control IDs. SUGGESTIONS ONLY: written into pending
# blobs for human review, never published. A maintainer confirms or replaces them.
CANDIDATE_KEYWORD_MAP: dict[str, list[str]] = {
    "audit": ["1.7", "3.3"],
    "publish": ["1.1", "1.28"],
    "sharing": ["1.1", "1.28"],
    "share": ["1.1", "1.28"],
    "ownership": ["1.2", "3.6"],
    "inventory": ["1.2", "3.1", "3.11"],
    "metadata": ["3.1", "1.2"],
    "dlp": ["1.5", "1.17"],
    "data loss prevention": ["1.5", "1.17"],
    "sensitivity label": ["1.5"],
    "dspm": ["1.6", "1.24"],
    "data security posture": ["1.6", "1.24"],
    "connector": ["1.4"],
    "mcp": ["1.4", "1.14"],
    "sharepoint": ["4.5", "4.1"],
    "identity": ["2.26"],
    "entra": ["2.26"],
    "orchestrat": ["2.17"],
    "workflow": ["2.17"],
    "file upload": ["1.26", "1.25"],
    "retention": ["1.9"],
    "ediscovery": ["1.19"],
    "insider risk": ["1.12"],
    "approval": ["1.1", "2.24"],
}


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def fetch_items(session) -> list:
    """Fetch and parse the roadmap feed. Fail-closed: raise on any shape error."""
    result = ms.fetch_page(API_URL, session)
    if result["status_code"] != 200 or result["error"]:
        raise RuntimeError(
            f"roadmap API fetch failed: status={result['status_code']} error={result['error']}"
        )
    try:
        data = json.loads(result["content"])
    except json.JSONDecodeError as exc:
        raise RuntimeError(f"roadmap API did not return valid JSON: {exc}") from exc
    return _validate_items(data)


def _validate_items(data) -> list:
    if not isinstance(data, list):
        raise RuntimeError(f"roadmap API payload is {type(data).__name__}, expected a list")
    for idx, item in enumerate(data[:50]):  # sample-validate the shape, fail-closed
        if not isinstance(item, dict) or "id" not in item or "title" not in item:
            raise RuntimeError(
                f"roadmap API item #{idx} missing required 'id'/'title' "
                "(API shape changed) -- refusing to proceed"
            )
    return data


def _products(item: dict) -> list[str]:
    container = item.get("tagsContainer") or {}
    products = container.get("products") or []
    return sorted({str(p.get("tagName", "")).strip() for p in products if p.get("tagName")})


def is_agent_relevant(item: dict) -> bool:
    title = (item.get("title") or "").lower()
    return any(kw in title for kw in AGENT_TITLE_KEYWORDS)


def item_projection(item: dict) -> dict:
    """Stable subset of fields used for change detection (order-independent)."""
    return {
        "id": item.get("id"),
        "title": item.get("title"),
        "description": item.get("description"),
        "status": item.get("status"),
        "preview": item.get("publicPreviewDate"),
        "ga": item.get("publicDisclosureAvailabilityDate"),
        "products": _products(item),
    }


def item_hash(item: dict) -> str:
    return ms.compute_hash(json.dumps(item_projection(item), sort_keys=True, ensure_ascii=False))


def suggest_controls(item: dict) -> list[dict]:
    """Suggest candidate control IDs (unconfirmed) from keywords + URL match."""
    haystack = f"{item.get('title') or ''} {item.get('description') or ''}".lower()
    suggestions: dict[str, str] = {}
    for keyword, control_ids in CANDIDATE_KEYWORD_MAP.items():
        if keyword in haystack:
            for cid in control_ids:
                suggestions.setdefault(cid, f"keyword:{keyword}")
    # Deterministic URL match against a real external link, when present. Roadmap
    # items rarely carry one; skip the (expensive) docs scan when absent.
    external_link = item.get("moreInfoLink")
    if external_link:
        affected = ms.find_affected_controls(external_link, DOCS_DIR)
        for ctrl in affected.get("controls", []):
            cid = ctrl.get("control_id")
            if cid:
                suggestions[cid] = "url-match"
    return [{"id": cid, "source": src} for cid, src in sorted(suggestions.items())]


def pending_path(item_id, content_hash: str, pending_dir: Path) -> Path:
    digest = content_hash.split(":")[-1][:12]
    return pending_dir / f"roadmap-{item_id}-{digest}.json"


def write_pending(item: dict, change_type: str, content_hash: str, pending_dir: Path) -> Path:
    path = pending_path(item.get("id"), content_hash, pending_dir)
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "schema_version": 1,
        "source": SOURCE_KEY,
        "change_type": change_type,
        "id": item.get("id"),
        "title": item.get("title"),
        "raw_description": item.get("description"),
        "status": item.get("status"),
        "preview_date": item.get("publicPreviewDate"),
        "ga_date": item.get("publicDisclosureAvailabilityDate"),
        "products": _products(item),
        "roadmap_url": ROADMAP_URL_FMT.format(id=item.get("id")),
        "content_hash": content_hash,
        "suggested_controls": suggest_controls(item),
        "detected_at": _now(),
        "note": (
            "Suggested mappings are UNCONFIRMED candidates for human review. "
            "Author the published entry by hand in data/change-radar/items.json; "
            "do not copy raw_description verbatim."
        ),
    }
    tmp = path.with_name(path.name + ".tmp")
    tmp.write_text(json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False) + "\n", encoding="utf-8")
    tmp.replace(path)
    return path


def write_report(changes: list[dict], run_date: str, report_dir: Path) -> Path:
    report_dir.mkdir(parents=True, exist_ok=True)
    path = report_dir / f"change-radar-{run_date}.md"
    lines = [
        f"# Change Radar monitor - {run_date}",
        "",
        f"Detected {len(changes)} agent-relevant roadmap change(s) awaiting human review.",
        "Suggested control mappings are unconfirmed; author published entries by hand in "
        "`data/change-radar/items.json`.",
        "",
        "| Change | ID | Title | Status | Suggested controls | Roadmap |",
        "| --- | --- | --- | --- | --- | --- |",
    ]
    for ch in changes:
        item = ch["item"]
        sugg = ", ".join(c["id"] for c in suggest_controls(item)) or "-"
        url = ROADMAP_URL_FMT.format(id=item.get("id"))
        title = str(item.get("title", "")).replace("|", "\\|")
        lines.append(
            f"| {ch['type']} | {item.get('id')} | {title} | {item.get('status', '-')} | {sugg} | [link]({url}) |"
        )
    lines.append("")
    path.write_text("\n".join(lines), encoding="utf-8")
    return path


def detect_changes(current: dict[str, dict], prev_items: dict[str, dict]) -> list[dict]:
    changes: list[dict] = []
    for item_id, entry in current.items():
        if item_id not in prev_items:
            changes.append({"type": "new", "id": item_id, "item": entry["item"], "hash": entry["hash"]})
        elif prev_items[item_id].get("hash") != entry["hash"]:
            changes.append({"type": "changed", "id": item_id, "item": entry["item"], "hash": entry["hash"]})
    for item_id, prev in prev_items.items():
        if item_id not in current:
            changes.append(
                {
                    "type": "withdrawn",
                    "id": item_id,
                    "item": {"id": int(item_id) if str(item_id).isdigit() else item_id,
                             "title": prev.get("title"), "status": "Withdrawn"},
                    "hash": prev.get("hash", ""),
                }
            )
    return changes


def load_raw_items(args) -> list:
    if args.input:
        data = json.loads(Path(args.input).read_text(encoding="utf-8"))
        return _validate_items(data)
    try:
        import requests
    except ImportError as exc:  # pragma: no cover - exercised only in live runs
        raise RuntimeError("requests is required for live fetch (pip install requests)") from exc
    session = requests.Session()
    session.headers.update({"User-Agent": USER_AGENT, "Accept": "application/json"})
    return fetch_items(session)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dry-run", action="store_true", help="Detect and report only; write nothing.")
    parser.add_argument("--input", help="Read raw items from a JSON file instead of fetching (offline/testing).")
    parser.add_argument("--limit", type=int, default=0, help="Cap the number of agent-relevant items processed (0 = all).")
    parser.add_argument("--state", default=str(STATE_PATH), help="State file path.")
    parser.add_argument("--pending-dir", default=str(PENDING_DIR), help="Pending blob directory.")
    parser.add_argument("--report-dir", default=str(REPORT_DIR), help="Monitor report directory.")
    args = parser.parse_args(argv)

    pending_dir = Path(args.pending_dir)
    report_dir = Path(args.report_dir)
    state_path = Path(args.state)

    try:
        raw = load_raw_items(args)
    except (RuntimeError, json.JSONDecodeError, OSError) as exc:
        print(f"FAIL (fail-closed): {exc}")
        return 2

    agent_items = [it for it in raw if is_agent_relevant(it)]
    if args.limit > 0:
        agent_items = agent_items[: args.limit]
    current: dict[str, dict] = {}
    for it in agent_items:
        current[str(it.get("id"))] = {"hash": item_hash(it), "item": it}
    print(f"Fetched {len(raw)} roadmap item(s); {len(agent_items)} agent-relevant.")

    state = ms.load_state(state_path)
    source_state = ms.get_source_state(state, SOURCE_KEY)
    run_date = datetime.now(timezone.utc).strftime("%Y-%m-%d")

    # First-run baseline suppression.
    if not source_state.get("last_run"):
        print(f"First run - establishing baseline of {len(current)} item(s) (no pending, no report).")
        if not args.dry_run:
            source_state["last_run"] = _now()
            source_state["items"] = {
                cid: {"hash": e["hash"], "status": e["item"].get("status"), "title": e["item"].get("title"),
                      "detected_at": _now()}
                for cid, e in current.items()
            }
            ms.set_source_state(state, SOURCE_KEY, source_state)
            ms.save_state_atomic(state, state_path)
        return 0

    prev_items = source_state.get("items", {})
    changes = detect_changes(current, prev_items)
    by_type: dict[str, int] = {}
    for ch in changes:
        by_type[ch["type"]] = by_type.get(ch["type"], 0) + 1
    print(f"Detected {len(changes)} change(s): " + (", ".join(f"{k}={v}" for k, v in sorted(by_type.items())) or "none"))

    if not changes:
        if not args.dry_run:
            source_state["last_run"] = _now()
            ms.set_source_state(state, SOURCE_KEY, source_state)
            ms.save_state_atomic(state, state_path)
        return 0

    if args.dry_run:
        for ch in changes:
            print(f"  [{ch['type']}] {ch['id']} {str(ch['item'].get('title',''))[:70]}")
        return 0

    written = 0
    for ch in changes:
        path = write_pending(ch["item"], ch["type"], ch["hash"], pending_dir)
        if path:
            written += 1
    report_path = write_report(changes, run_date, report_dir)
    print(f"Wrote {written} pending blob(s) to {pending_dir}")
    print(f"Wrote report {report_path}")

    # Advance the baseline in the working tree (authoritative only on PR merge).
    source_state["last_run"] = _now()
    source_state["items"] = {
        cid: {"hash": e["hash"], "status": e["item"].get("status"), "title": e["item"].get("title"),
              "detected_at": prev_items.get(cid, {}).get("detected_at", _now())}
        for cid, e in current.items()
    }
    ms.set_source_state(state, SOURCE_KEY, source_state)
    ms.save_state_atomic(state, state_path)
    # Signal "changes staged" so the workflow opens/updates the gate PR (mirrors
    # regulatory_monitor.py). 0 = baseline/no-change, 1 = changes, 2 = fail-closed.
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
