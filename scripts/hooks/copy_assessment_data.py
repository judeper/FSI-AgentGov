"""MkDocs hook — copy assessment data assets into the built site.

Runs during ``mkdocs build`` / ``mkdocs serve``. Copies:

* ``assessment/manifest/controls.json`` → ``site/assessment/data/controls.json``
* ``assessment/data/solutions-lock.json`` → ``site/assessment/data/solutions-lock.json``

This is the v1.4 plumbing that lets the SPA fetch the manifest at
runtime as a static asset (``/assessment/data/controls.json``), keeping
the engine and the SPA bound to a single source of truth.

Wire-up in ``mkdocs.yml``::

    hooks:
      - scripts/hooks/copy_assessment_data.py
"""
from __future__ import annotations

import logging
import shutil
from pathlib import Path

log = logging.getLogger("mkdocs.copy_assessment_data")

REPO_ROOT = Path(__file__).resolve().parents[2]
SOURCES = {
    REPO_ROOT / "assessment" / "manifest" / "controls.json": "assessment/data/controls.json",
    REPO_ROOT / "assessment" / "data" / "solutions-lock.json": "assessment/data/solutions-lock.json",
    REPO_ROOT / "assessment" / "data" / "README.md": "assessment/data/README.md",
}


def on_post_build(config, **_kwargs):
    """Copy assessment data assets into the built site after MkDocs finishes."""
    site_dir = Path(config["site_dir"])
    copied = 0
    for src, rel in SOURCES.items():
        if not src.exists():
            log.warning("copy_assessment_data: source missing: %s", src)
            continue
        dest = site_dir / rel
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(src, dest)
        copied += 1
    log.info("copy_assessment_data: copied %d assessment asset(s)", copied)
