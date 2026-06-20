"""Tests for the Stage 2 auto-merge unlock gate + agreement ledger."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from pathlib import Path

import autodoc_automerge as am

TARGET = "docs/reference/microsoft-learn-urls.md"
OLD = "https://learn.microsoft.com/en-us/old/"
NEW = "https://learn.microsoft.com/en-us/new/"


def _merged_diff(old: str, new: str) -> str:
    return (
        f"diff --git a/{TARGET} b/{TARGET}\n--- a/{TARGET}\n+++ b/{TARGET}\n@@ -1 +1 @@\n"
        f"-| Title | {old} | Mar 2026 |\n+| Title | {new} | Mar 2026 |\n"
    )


def _t(days_ago: float) -> datetime:
    return datetime(2026, 6, 20, tzinfo=timezone.utc) - timedelta(days=days_ago)


def _enabled_cfg(**over) -> dict:
    cfg = {"enabled": True, "min_samples": 3, "min_weeks": 2.0, "min_agreement": 1.0, "window_days": 120}
    cfg.update(over)
    return cfg


def _seed(path: Path, n: int, *, outcome: str, first_days_ago: float = 30, span_days: float = 21) -> None:
    """Seed n samples with a given terminal outcome spread across span_days."""
    data = am.load_ledger(path)
    for i in range(n):
        fp = f"sha256:{outcome}{i:03d}"
        at = _t(first_days_ago - (span_days * i / max(n - 1, 1)))
        data["samples"][fp] = {
            "fingerprint": fp, "pr_number": 100 + i, "pr_url": f"u{i}",
            "old_url": OLD, "new_url": NEW, "url_pair": "x",
            "drafted_at": am._iso(at), "outcome": outcome, "outcome_at": am._iso(at),
        }
    am.save_ledger(path, data)


def test_record_drafted_creates_open_sample(tmp_path: Path) -> None:
    p = tmp_path / "led.json"
    am.record_drafted(p, fingerprint="sha256:a", pr_number=5, pr_url="u", old_url=OLD, new_url=NEW, now=_t(0))
    s = am.load_ledger(p)["samples"]["sha256:a"]
    assert s["outcome"] == "open" and s["pr_number"] == 5 and s["old_url"] == OLD


def test_record_drafted_idempotent_on_terminal(tmp_path: Path) -> None:
    p = tmp_path / "led.json"
    am.record_drafted(p, fingerprint="sha256:a", pr_number=5, pr_url="u", old_url=OLD, new_url=NEW, now=_t(10))
    data = am.load_ledger(p)
    data["samples"]["sha256:a"]["outcome"] = "merged_as_is"
    am.save_ledger(p, data)
    am.record_drafted(p, fingerprint="sha256:a", pr_number=5, pr_url="u", old_url=OLD, new_url=NEW, now=_t(0))
    assert am.load_ledger(p)["samples"]["sha256:a"]["outcome"] == "merged_as_is"


def test_reconcile_merged_as_is(tmp_path: Path) -> None:
    p = tmp_path / "led.json"
    am.record_drafted(p, fingerprint="sha256:a", pr_number=5, pr_url="u", old_url=OLD, new_url=NEW, now=_t(5))
    am.reconcile(p, lambda s: am.PrState("merged", merged_diff=_merged_diff(OLD, NEW)), now=_t(0))
    assert am.load_ledger(p)["samples"]["sha256:a"]["outcome"] == "merged_as_is"


def test_reconcile_merged_edited_when_diff_differs(tmp_path: Path) -> None:
    p = tmp_path / "led.json"
    am.record_drafted(p, fingerprint="sha256:a", pr_number=5, pr_url="u", old_url=OLD, new_url=NEW, now=_t(5))
    other = "https://learn.microsoft.com/en-us/other/"
    am.reconcile(p, lambda s: am.PrState("merged", merged_diff=_merged_diff(OLD, other)), now=_t(0))
    assert am.load_ledger(p)["samples"]["sha256:a"]["outcome"] == "merged_edited"


def test_reconcile_closed_and_revert(tmp_path: Path) -> None:
    p = tmp_path / "led.json"
    am.record_drafted(p, fingerprint="sha256:c", pr_number=6, pr_url="u", old_url=OLD, new_url=NEW, now=_t(5))
    am.reconcile(p, lambda s: am.PrState("closed"), now=_t(0))
    assert am.load_ledger(p)["samples"]["sha256:c"]["outcome"] == "closed"

    am.record_drafted(p, fingerprint="sha256:r", pr_number=7, pr_url="u", old_url=OLD, new_url=NEW, now=_t(5))
    am.reconcile(p, lambda s: am.PrState("merged", merged_diff=_merged_diff(OLD, NEW), reverted=True), now=_t(0))
    assert am.load_ledger(p)["samples"]["sha256:r"]["outcome"] == "reverted"


def test_reconcile_fetch_error_leaves_open(tmp_path: Path) -> None:
    p = tmp_path / "led.json"
    am.record_drafted(p, fingerprint="sha256:a", pr_number=5, pr_url="u", old_url=OLD, new_url=NEW, now=_t(5))

    def boom(_s):
        raise RuntimeError("gh down")

    am.reconcile(p, boom, now=_t(0))
    assert am.load_ledger(p)["samples"]["sha256:a"]["outcome"] == "open"


def test_unlock_locked_when_disabled(tmp_path: Path) -> None:
    p = tmp_path / "led.json"
    _seed(p, 5, outcome="merged_as_is")
    st = am.unlock_state(p, now=_t(0), config=_enabled_cfg(enabled=False))
    assert not st.unlocked and "AUTOMERGE_ENABLED" in st.reason


def test_unlock_locked_too_few_samples(tmp_path: Path) -> None:
    p = tmp_path / "led.json"
    _seed(p, 2, outcome="merged_as_is")
    st = am.unlock_state(p, now=_t(0), config=_enabled_cfg(min_samples=3))
    assert not st.unlocked and "terminal sample" in st.reason


def test_unlock_locked_on_revert(tmp_path: Path) -> None:
    p = tmp_path / "led.json"
    _seed(p, 4, outcome="merged_as_is")
    _seed(p, 1, outcome="reverted", first_days_ago=10, span_days=0)
    st = am.unlock_state(p, now=_t(0), config=_enabled_cfg())
    assert not st.unlocked and "revert" in st.reason


def test_unlock_locked_low_agreement(tmp_path: Path) -> None:
    p = tmp_path / "led.json"
    _seed(p, 3, outcome="merged_as_is")
    _seed(p, 2, outcome="merged_edited", first_days_ago=8, span_days=4)
    st = am.unlock_state(p, now=_t(0), config=_enabled_cfg(min_agreement=1.0))
    assert not st.unlocked and "agreement" in st.reason


def test_unlock_locked_short_span(tmp_path: Path) -> None:
    p = tmp_path / "led.json"
    _seed(p, 5, outcome="merged_as_is", first_days_ago=3, span_days=1)
    st = am.unlock_state(p, now=_t(0), config=_enabled_cfg(min_weeks=2.0))
    assert not st.unlocked and "week" in st.reason


def test_unlock_unlocked_when_all_met(tmp_path: Path) -> None:
    p = tmp_path / "led.json"
    _seed(p, 5, outcome="merged_as_is", first_days_ago=30, span_days=21)
    st = am.unlock_state(p, now=_t(0), config=_enabled_cfg(min_samples=3, min_weeks=2.0, min_agreement=1.0))
    assert st.unlocked and st.agreement == 1.0 and st.reverts == 0


def test_unlock_window_excludes_old_samples(tmp_path: Path) -> None:
    p = tmp_path / "led.json"
    _seed(p, 5, outcome="merged_as_is", first_days_ago=300, span_days=21)
    st = am.unlock_state(p, now=_t(0), config=_enabled_cfg(window_days=120))
    assert not st.unlocked and st.samples == 0
