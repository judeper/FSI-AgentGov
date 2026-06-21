#!/usr/bin/env python3
"""Pending-baseline helpers for the Learn autodoc pipeline."""

from __future__ import annotations

import hashlib
import json
import os
import re
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

PENDING_RELATIVE_DIR = Path("data") / "monitor-pending" / "learn"
_SAFE_CHARS_RE = re.compile(r"[^A-Za-z0-9._-]+")


def defer_enabled(env: dict[str, str] | None = None) -> bool:
    """Return True only when AUTODOC_ENABLED is exactly true after trim/lower."""
    source = env if env is not None else os.environ
    return source.get("AUTODOC_ENABLED", "").strip().lower() == "true"


def _safe_url_slug(url: str) -> str:
    parsed = urlparse(url)
    raw = f"{parsed.netloc}{parsed.path}".strip("/") or "url"
    slug = _SAFE_CHARS_RE.sub("-", raw.lower()).strip(".-_")
    while ".." in slug:
        slug = slug.replace("..", "-")
    return (slug or "url")[:96].strip(".-_") or "url"


def pending_path(url: str, content_hash: str, base_dir: str | Path) -> Path:
    """Return the deterministic pending blob path for a single Learn URL change.

    The filename is keyed on BOTH the URL and the change's ``content_hash`` so that two
    distinct changes to the same URL (e.g. a second change detected while the first change's
    escalation issue is still open) produce two independent blobs rather than overwriting one
    another. Keying on the URL alone silently orphaned the earlier change's blob.
    """
    digest = hashlib.sha256(f"{url}\n{content_hash}".encode("utf-8")).hexdigest()[:24]
    filename = f"{_safe_url_slug(url)}-{digest}.json"
    return Path(base_dir) / PENDING_RELATIVE_DIR / filename


def load_pending(path: str | Path) -> dict[str, Any] | None:
    """Load one pending blob, returning None when it does not exist."""
    pending_file = Path(path)
    if not pending_file.exists():
        return None

    pending = json.loads(pending_file.read_text(encoding="utf-8"))
    if not isinstance(pending, dict):
        raise ValueError(f"Pending blob must be a JSON object: {pending_file}")
    return pending


def write_pending(path: str | Path, url: str, new_hash: str, normalized: str, detected_at: str) -> None:
    """Write a stable pending blob for a deferred Learn baseline change."""
    pending_file = Path(path)
    pending_file.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "schema_version": 1,
        "source": "learn",
        "url": url,
        "content_hash": new_hash,
        "normalized_content": normalized,
        "detected_at": detected_at,
    }
    temp_file = pending_file.with_name(f"{pending_file.name}.tmp")
    temp_file.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    temp_file.replace(pending_file)


def is_already_pending(url: str, new_hash: str, base_dir: str | Path) -> bool:
    """Return True when this URL already has a pending blob for this exact hash."""
    pending = load_pending(pending_path(url, new_hash, base_dir))
    return bool(pending and pending.get("url") == url and pending.get("content_hash") == new_hash)
