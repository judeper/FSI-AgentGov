#!/usr/bin/env python3
"""Stage 2 auto-merge unlock gate + agreement ledger for autodoc *redirect* PRs.

(Distinct from ``autodoc_canary.py``, which is the deterministic poison-pill guard.)

Redirect auto-merge stays OFF until there is evidence that the unattended redirect
pipeline agrees with human judgement. This module records, per auto-drafted redirect,
the PR and its eventual human outcome, and computes whether auto-merge may unlock.

The unlock gate is **fail-closed** and multi-condition:

* the master switch ``AUTOMERGE_ENABLED`` env var must be ``true``;
* there must be at least ``AUTOMERGE_MIN_SAMPLES`` terminal samples in the window;
* those samples must span at least ``AUTOMERGE_MIN_WEEKS`` weeks;
* the **merged-exactly-as-is** rate must be >= ``AUTOMERGE_MIN_AGREEMENT``;
* there must be **zero post-merge reverts** in the window.

"Merged exactly as-is" reuses the same independent diff verifier the CI gate uses
(:mod:`autodoc_redirect_ci_verify`): a merged redirect counts as agreement only when
the merged diff is a clean single-URL-cell swap of the *same* old->new URLs the
runner drafted. A human edit (different diff) counts as ``merged_edited`` (not
agreement); a closed-unmerged PR counts as ``closed``; a reverted one as ``reverted``.

Thresholds default conservatively and are intended to be tuned with real data
(decide-late). All values are read from the environment so nothing is hard-locked.
"""

from __future__ import annotations

import hashlib
import json
import os
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Callable

import autodoc_redirect_ci_verify as redirect_verify

SCHEMA_VERSION = 1
TERMINAL_OUTCOMES = {"merged_as_is", "merged_edited", "closed", "reverted"}
LEDGER_PATH = "data/autodoc-automerge-ledger.json"


def _now() -> datetime:
    return datetime.now(timezone.utc)


def _iso(dt: datetime) -> str:
    return dt.astimezone(timezone.utc).isoformat()


def _parse_iso(value: str) -> datetime:
    return datetime.fromisoformat(value)


def load_ledger(path: Path) -> dict[str, Any]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        data = {}
    data.setdefault("schema_version", SCHEMA_VERSION)
    data.setdefault("samples", {})
    return data


def save_ledger(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _url_pair_key(old_url: str, new_url: str) -> str:
    return hashlib.sha256(f"{old_url}\n{new_url}".encode("utf-8")).hexdigest()


def record_drafted(
    path: Path,
    *,
    fingerprint: str,
    pr_number: int,
    pr_url: str,
    old_url: str,
    new_url: str,
    now: datetime | None = None,
) -> None:
    """Record a freshly auto-drafted redirect PR as an ``open`` sample.

    Idempotent on fingerprint: re-recording the same change does not reset a sample
    that already reached a terminal outcome.
    """

    now = now or _now()
    data = load_ledger(path)
    existing = data["samples"].get(fingerprint)
    if existing and existing.get("outcome") in TERMINAL_OUTCOMES:
        return
    data["samples"][fingerprint] = {
        "fingerprint": fingerprint,
        "pr_number": int(pr_number),
        "pr_url": pr_url,
        "old_url": old_url,
        "new_url": new_url,
        "url_pair": _url_pair_key(old_url, new_url),
        "drafted_at": _iso(now),
        "outcome": "open",
        "outcome_at": None,
    }
    save_ledger(path, data)


@dataclass
class PrState:
    """Outcome of an opened sample PR, as observed from GitHub."""

    state: str  # "open" | "merged" | "closed"
    merged_diff: str | None = None  # the base...merge diff when state == "merged"
    reverted: bool = False


def _classify_merged(sample: dict[str, Any], merged_diff: str | None) -> str:
    """merged_as_is iff the merged diff is a clean swap of the SAME old->new URLs."""

    if not merged_diff:
        return "merged_edited"
    try:
        old_url, new_url = redirect_verify.verify_redirect_diff(merged_diff)
    except redirect_verify.NotCleanRedirect:
        return "merged_edited"
    if old_url == sample.get("old_url") and new_url == sample.get("new_url"):
        return "merged_as_is"
    return "merged_edited"


def reconcile(path: Path, fetch_state: Callable[[dict[str, Any]], PrState], now: datetime | None = None) -> dict[str, Any]:
    """Update every ``open`` sample with its observed PR outcome. Returns the data.

    ``fetch_state`` is injected (GitHub API in production, a stub in tests) and maps a
    sample dict to a :class:`PrState`. Any per-sample lookup error leaves that sample
    ``open`` (fail-safe: an unobserved PR never counts as agreement). A merged sample
    later found reverted transitions to ``reverted``.
    """

    now = now or _now()
    data = load_ledger(path)
    changed = False
    for sample in data["samples"].values():
        outcome = sample.get("outcome")
        if outcome in {"merged_as_is", "merged_edited"}:
            if _maybe_reverted(sample, fetch_state):
                sample["outcome"] = "reverted"
                sample["outcome_at"] = _iso(now)
                changed = True
            continue
        if outcome != "open":
            continue
        try:
            observed = fetch_state(sample)
        except Exception:  # noqa: BLE001 - one PR lookup failure must not abort reconcile.
            continue
        if observed.reverted:
            sample["outcome"] = "reverted"
        elif observed.state == "merged":
            sample["outcome"] = _classify_merged(sample, observed.merged_diff)
        elif observed.state == "closed":
            sample["outcome"] = "closed"
        else:
            continue  # still open
        sample["outcome_at"] = _iso(now)
        changed = True
    if changed:
        save_ledger(path, data)
    return data


def _maybe_reverted(sample: dict[str, Any], fetch_state: Callable[[dict[str, Any]], PrState]) -> bool:
    try:
        return bool(fetch_state(sample).reverted)
    except Exception:  # noqa: BLE001
        return False


@dataclass
class UnlockState:
    unlocked: bool
    reason: str
    samples: int
    merged_as_is: int
    reverts: int
    agreement: float
    weeks_span: float


def config_from_env() -> dict[str, Any]:
    def _int(name: str, default: int) -> int:
        try:
            return int(os.environ.get(name, "").strip() or default)
        except ValueError:
            return default

    def _float(name: str, default: float) -> float:
        try:
            return float(os.environ.get(name, "").strip() or default)
        except ValueError:
            return default

    return {
        "enabled": os.environ.get("AUTOMERGE_ENABLED", "").strip().lower() == "true",
        "min_samples": _int("AUTOMERGE_MIN_SAMPLES", 10),
        "min_weeks": _float("AUTOMERGE_MIN_WEEKS", 4.0),
        "min_agreement": _float("AUTOMERGE_MIN_AGREEMENT", 1.0),
        "window_days": _int("AUTOMERGE_WINDOW_DAYS", 120),
    }


def unlock_state(path: Path, now: datetime | None = None, config: dict[str, Any] | None = None) -> UnlockState:
    """Evaluate the fail-closed auto-merge unlock gate from the agreement ledger."""

    now = now or _now()
    cfg = config or config_from_env()
    data = load_ledger(path)

    window_start = now - timedelta(days=cfg["window_days"])
    terminal: list[dict[str, Any]] = []
    for sample in data["samples"].values():
        outcome = sample.get("outcome")
        at = sample.get("outcome_at")
        if outcome in TERMINAL_OUTCOMES and at:
            try:
                if _parse_iso(at) >= window_start:
                    terminal.append(sample)
            except ValueError:
                continue

    samples = len(terminal)
    merged_as_is = sum(1 for s in terminal if s["outcome"] == "merged_as_is")
    reverts = sum(1 for s in terminal if s["outcome"] == "reverted")
    agreement = (merged_as_is / samples) if samples else 0.0

    times = [_parse_iso(s["outcome_at"]) for s in terminal if s.get("outcome_at")]
    weeks_span = ((max(times) - min(times)).days / 7.0) if len(times) >= 2 else 0.0

    def _fail(reason: str) -> UnlockState:
        return UnlockState(False, reason, samples, merged_as_is, reverts, agreement, weeks_span)

    if not cfg["enabled"]:
        return _fail("AUTOMERGE_ENABLED is not 'true'")
    if reverts > 0:
        return _fail(f"{reverts} post-merge revert(s) in window")
    if samples < cfg["min_samples"]:
        return _fail(f"only {samples} terminal sample(s); need >= {cfg['min_samples']}")
    if weeks_span < cfg["min_weeks"]:
        return _fail(f"samples span {weeks_span:.1f} week(s); need >= {cfg['min_weeks']}")
    if agreement < cfg["min_agreement"]:
        return _fail(f"agreement {agreement:.2f} < required {cfg['min_agreement']:.2f}")
    return UnlockState(True, "unlocked", samples, merged_as_is, reverts, agreement, weeks_span)
