"""MkDocs build-SHA cache-bust hook.

Computes a build SHA at build time and:
  * Writes ``<docs_dir>/version.json`` with the framework version (read
    from the repo-root ``VERSION`` file), the build SHA, and an ISO
    timestamp so deployment smoke tests can poll the live site for the
    deployed SHA *and* downstream consumers can read the canonical
    framework version.
  * Injects ``<meta name="build-sha" content="...">`` into every rendered
    page just after ``<head>`` for in-page diagnostics.
  * Appends ``?v=<sha>`` to any ``assessment-app.js`` ``<script src=...>``
    references emitted into the HTML so a new deploy busts CDN/browser
    caches even when the underlying URL is unchanged.

Canonical version source (PR-0, Tier -1):
    The repo-root ``VERSION`` file is the single source of truth for the
    framework version. ``scripts/verify_version_stamps.py`` reads the same
    file to enforce footer/header stamp consistency across the repo.

Phase C, step 0. Referenced from ``mkdocs.yml`` ``hooks:``.
"""

from __future__ import annotations

import datetime as _dt
import json
import os
import re
import subprocess
from pathlib import Path

# Module-level cache so on_pre_build / on_post_page agree on the SHA.
_BUILD_SHA: str | None = None


def _read_canonical_version(config) -> str:
    """Read the framework version from the repo-root VERSION file.

    Falls back to ``"unknown"`` if the file is missing or malformed so the
    build never fails purely on version-file issues; ``verify_version_stamps``
    is the gate that hard-fails on drift.
    """
    docs_dir = Path(config["docs_dir"])
    repo_root = docs_dir.parent
    version_file = repo_root / "VERSION"
    if not version_file.exists():
        return "unknown"
    raw = version_file.read_text(encoding="utf-8").strip()
    return raw or "unknown"


def _compute_sha() -> str:
    global _BUILD_SHA
    if _BUILD_SHA:
        return _BUILD_SHA
    sha = os.environ.get("GITHUB_SHA")
    if not sha:
        try:
            sha = (
                subprocess.check_output(
                    ["git", "rev-parse", "HEAD"], stderr=subprocess.DEVNULL
                )
                .strip()
                .decode("ascii")
            )
        except Exception:
            sha = f"dev-{int(_dt.datetime.utcnow().timestamp())}"
    _BUILD_SHA = sha
    return sha


def on_pre_build(config, **_kwargs):
    """Write ``version.json`` to the docs source dir before the build runs.

    MkDocs copies non-Markdown files from ``docs_dir`` into ``site_dir``,
    so writing here makes ``/version.json`` available on the deployed site.
    """
    sha = _compute_sha()
    docs_dir = Path(config["docs_dir"])
    payload = {
        "version": _read_canonical_version(config),
        "sha": sha,
        "builtAt": _dt.datetime.utcnow().replace(microsecond=0).isoformat() + "Z",
    }
    (docs_dir / "version.json").write_text(
        json.dumps(payload, indent=2) + "\n", encoding="utf-8"
    )


_ASSESSMENT_SRC_RE = re.compile(
    r'(<script[^>]*\bsrc="[^"]*assessment-app\.js)(\?[^"]*)?(")',
    re.IGNORECASE,
)
_HEAD_RE = re.compile(r"(<head[^>]*>)", re.IGNORECASE)


def on_post_page(output: str, page=None, config=None, **_kwargs) -> str:
    """Cache-bust assessment-app.js script tags and inject build-SHA meta."""
    sha = _compute_sha()
    output = _ASSESSMENT_SRC_RE.sub(rf"\1?v={sha}\3", output)
    meta = f'<meta name="build-sha" content="{sha}">'
    output, count = _HEAD_RE.subn(rf"\1{meta}", output, count=1)
    if count == 0 and "<head" in output.lower() is False:
        # Defensive fallback (should not trigger for mkdocs-material pages).
        return output
    return output
