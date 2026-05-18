"""MkDocs hook — copy assessment data assets into the built site.

Runs during ``mkdocs build`` / ``mkdocs serve``. Copies:

* ``assessment/manifest/controls.json`` → ``site/assessment/data/controls.json``
* ``assessment/data/solutions-lock.json`` → ``site/assessment/data/solutions-lock.json``

This is the v1.4 plumbing that lets the SPA fetch the manifest at
runtime as a static asset (``/assessment/data/controls.json``), keeping
the engine and the SPA bound to a single source of truth.

Authoring-placeholder gating (finding U-022)
---------------------------------------------
The manifest intentionally carries ``TODO:`` placeholders in
``priority`` / ``yesBar`` / ``partialBar`` / ``noBar`` and in
``facilitatorNotes.{ask,followUp}`` for controls whose facilitator
content has not yet been authored. We strip those placeholders out of
the **published** manifest copy so they cannot leak into the
customer-facing SPA drawer, agenda exports, or any other consumer of
``/assessment/data/controls.json``. The source manifest under
``assessment/manifest/`` is left untouched and continues to serve as
the authoring backlog.

Wire-up in ``mkdocs.yml``::

    hooks:
      - scripts/hooks/copy_assessment_data.py
"""
from __future__ import annotations

import json
import logging
import shutil
from pathlib import Path

log = logging.getLogger("mkdocs.copy_assessment_data")

REPO_ROOT = Path(__file__).resolve().parents[2]
MANIFEST_SRC = REPO_ROOT / "assessment" / "manifest" / "controls.json"
MANIFEST_REL = "assessment/data/controls.json"
SOURCES = {
    REPO_ROOT / "assessment" / "data" / "solutions-lock.json": "assessment/data/solutions-lock.json",
    REPO_ROOT / "assessment" / "data" / "README.md": "assessment/data/README.md",
}

# Manifest fields whose TODO placeholders must NOT reach the SPA. Keep this
# list aligned with `assessment-app.js::mergeManifestIntoControls`.
_SCRUB_STRING_FIELDS = ("priority", "yesBar", "partialBar", "noBar")
_SCRUB_FACILITATOR_FIELDS = ("ask", "followUp")


def _is_todo(value: object) -> bool:
    return isinstance(value, str) and value.strip().startswith("TODO:")


def scrub_manifest_todos(controls: list[dict]) -> tuple[list[dict], int]:
    """Return (scrubbed_controls, count_of_fields_scrubbed).

    ``priority`` is dropped when it is a TODO so downstream consumers see a
    missing key rather than a placeholder value. The string content fields
    (``yesBar`` / ``partialBar`` / ``noBar``) are replaced with empty strings
    so SPA truthy guards (``if (ctrl.yesBar)``) skip rendering. Facilitator
    notes ``ask`` / ``followUp`` get the same empty-string treatment.

    The source list is not mutated.
    """
    scrubbed = 0
    cleaned: list[dict] = []
    for ctrl in controls:
        c = dict(ctrl)  # shallow copy is enough — we only rewrite top-level fields
        for field in _SCRUB_STRING_FIELDS:
            v = c.get(field)
            if _is_todo(v):
                scrubbed += 1
                if field == "priority":
                    c.pop(field, None)
                else:
                    c[field] = ""
        fn = c.get("facilitatorNotes")
        if isinstance(fn, dict):
            new_fn = dict(fn)
            for sub in _SCRUB_FACILITATOR_FIELDS:
                if _is_todo(new_fn.get(sub)):
                    scrubbed += 1
                    new_fn[sub] = ""
            c["facilitatorNotes"] = new_fn
        cleaned.append(c)
    return cleaned, scrubbed


def _write_manifest_scrubbed(dest: Path) -> int:
    """Write the manifest to ``dest`` with TODO placeholders stripped.

    Returns the number of TODO fields that were scrubbed.
    """
    if not MANIFEST_SRC.exists():
        log.warning("copy_assessment_data: manifest source missing: %s", MANIFEST_SRC)
        return 0
    controls = json.loads(MANIFEST_SRC.read_text(encoding="utf-8"))
    if not isinstance(controls, list):
        log.error("copy_assessment_data: manifest is not a list; copying verbatim")
        shutil.copyfile(MANIFEST_SRC, dest)
        return 0
    cleaned, scrubbed = scrub_manifest_todos(controls)
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(json.dumps(cleaned, indent=2) + "\n", encoding="utf-8")
    return scrubbed


def on_post_build(config, **_kwargs):
    """Copy assessment data assets into the built site after MkDocs finishes."""
    site_dir = Path(config["site_dir"])
    copied = 0

    # Scrub-and-copy the manifest separately so we never publish TODO leakage.
    manifest_dest = site_dir / MANIFEST_REL
    scrubbed = _write_manifest_scrubbed(manifest_dest)
    if manifest_dest.exists():
        copied += 1
        log.info(
            "copy_assessment_data: published manifest with %d TODO field(s) scrubbed",
            scrubbed,
        )

    for src, rel in SOURCES.items():
        if not src.exists():
            log.warning("copy_assessment_data: source missing: %s", src)
            continue
        dest = site_dir / rel
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(src, dest)
        copied += 1
    log.info("copy_assessment_data: copied %d assessment asset(s)", copied)
