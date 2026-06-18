"""Tests for autodoc_classifier.py — the deterministic, fail-closed routing gate.

The guiding requirement (from the June 2026 autodoc council review) is that the
classifier must NEVER promote a compliance-sensitive change to ``autodraft`` /
``automerge_eligible``. These tests encode that as executable guardrails, plus
integration checks against the real report fixtures in ``reports/monitoring/``.
"""

from __future__ import annotations

from pathlib import Path

import autodoc_classifier as ac

PROJECT_ROOT = Path(__file__).resolve().parent.parent
REPORTS_DIR = PROJECT_ROOT / "reports" / "monitoring"


# ---------------------------------------------------------------------------
# Diff helpers
# ---------------------------------------------------------------------------
def test_added_and_removed_lines():
    diff = "--- +++ @@ -1,2 +1,3 @@\n context\n-old line\n+new line\n+second new"
    assert ac.added_lines(diff) == ["new line", "second new"]
    assert ac.removed_lines(diff) == ["old line"]


def test_is_additive_only_true_for_pure_additions():
    diff = "--- +++ @@ -1,1 +1,3 @@\n context\n+added one\n+added two"
    assert ac.is_additive_only(diff) is True


def test_is_additive_only_false_for_rewrite():
    diff = "--- +++ @@ -1,2 +1,2 @@\n-removed prose\n+replacement prose"
    assert ac.is_additive_only(diff) is False


def test_is_additive_only_false_for_empty():
    assert ac.is_additive_only("") is False


# ---------------------------------------------------------------------------
# Routing gates — every HARD_HUMAN category must force route="human"
# ---------------------------------------------------------------------------
def _change(diff, classification="MEDIUM", controls=None, kind="content"):
    return ac.Change(
        topic="Test", url="https://learn.microsoft.com/en-us/x",
        classification=classification, affected_controls=controls or [],
        diff_text=diff, kind=kind,
    )


def test_critical_tier_routes_to_human():
    d = ac.classify_change(_change("--- +++ @@\n+a harmless addition", classification="CRITICAL"))
    assert d.route == "human"
    assert d.automerge_eligible is False


def test_regulatory_citation_routes_to_human():
    d = ac.classify_change(_change("--- +++ @@\n+This satisfies SEC 17a-4 recordkeeping."))
    assert d.route == "human"
    assert "regulatory_citation" in d.sensitive_categories


def test_date_routes_to_human():
    d = ac.classify_change(_change("--- +++ @@\n+Available starting March 2027."))
    assert d.route == "human"
    assert "date_or_deadline" in d.sensitive_categories


def test_retention_duration_routes_to_human():
    d = ac.classify_change(_change("--- +++ @@\n+Records are retained for 7 years."))
    assert d.route == "human"
    assert "duration_or_retention" in d.sensitive_categories


def test_license_sku_routes_to_human():
    d = ac.classify_change(_change("--- +++ @@\n+Requires a Microsoft 365 E5 license."))
    assert d.route == "human"
    assert "license_sku" in d.sensitive_categories


def test_deprecation_routes_to_human():
    d = ac.classify_change(_change("--- +++ @@\n+This feature is deprecated and will be removed."))
    assert d.route == "human"
    assert "deprecation" in d.sensitive_categories


def test_policy_language_routes_to_human():
    d = ac.classify_change(_change("--- +++ @@\n+Administrators must enable audit logging."))
    assert d.route == "human"
    assert "policy_language" in d.sensitive_categories


def test_overclaim_routes_to_human():
    d = ac.classify_change(_change("--- +++ @@\n+This control guarantees regulatory coverage."))
    assert d.route == "human"
    assert "overclaim" in d.sensitive_categories


def test_control_prose_edit_routes_to_human():
    # Affects a control AND is a rewrite (not additive) -> human.
    d = ac.classify_change(_change(
        "--- +++ @@\n-old portal path\n+new portal path", controls=["1.15"]
    ))
    assert d.route == "human"
    assert d.affects_control is True


# ---------------------------------------------------------------------------
# The narrow "autodraft" / "automerge" promotions
# ---------------------------------------------------------------------------
def test_mechanical_addition_is_autodraft():
    d = ac.classify_change(_change(
        "--- +++ @@\n+See the new agent governance overview for related guidance."
    ))
    assert d.route == "autodraft"
    assert d.automerge_eligible is True


def test_addition_with_number_is_autodraft_but_not_automerge():
    d = ac.classify_change(_change(
        "--- +++ @@\n+There are now three panes; see pane number 2 for details."
    ))
    # "number" is fine for drafting, but a bare digit blocks unattended merge.
    assert d.route == "autodraft"
    assert d.automerge_eligible is False
    assert any("number" in r for r in d.reasons)


def test_high_tier_addition_is_not_automerge_eligible():
    d = ac.classify_change(_change(
        "--- +++ @@\n+A short neutral cross reference sentence.", classification="HIGH"
    ))
    assert d.route == "autodraft"
    assert d.automerge_eligible is False  # only MEDIUM/NOISE may auto-merge


def test_redirect_is_autodraft_and_automerge():
    d = ac.classify_change(_change("", kind="redirect"))
    assert d.route == "autodraft"
    assert d.automerge_eligible is True
    assert d.kind == "redirect"


# ---------------------------------------------------------------------------
# Integration: real report fixtures must never mis-promote compliance changes
# ---------------------------------------------------------------------------
def _load(name):
    p = REPORTS_DIR / name
    return p.read_text(encoding="utf-8") if p.exists() else None


def test_parse_real_report_extracts_changes():
    text = _load("learn-changes-2026-06-11.md")
    if text is None:
        import pytest
        pytest.skip("fixture report not present")
    changes = ac.parse_report(text)
    # The 06-11 report has 6 detailed change blocks + 1 redirect.
    content = [c for c in changes if c.kind == "content"]
    assert len(content) >= 5
    topics = {c.topic for c in content}
    assert any("Encryption" in t for t in topics)


def test_cmk_change_routes_to_human_despite_mislabel():
    """The CMK change is a content REWRITE the monitor mislabelled 'Deprecation';
    the classifier must still route it to a human (CRITICAL tier + prose edit)."""
    text = _load("learn-changes-2026-06-11.md")
    if text is None:
        import pytest
        pytest.skip("fixture report not present")
    decisions = ac.classify_report(text)
    cmk = next((d for d in decisions if "customer-managed-key" in d.url), None)
    assert cmk is not None
    assert cmk.route == "human"
    assert cmk.automerge_eligible is False


def test_no_control_touching_change_is_automerge_eligible():
    """Fail-closed invariant: nothing that affects a control file may auto-merge."""
    for name in ("learn-changes-2026-06-11.md", "learn-changes-2026-06-18.md"):
        text = _load(name)
        if text is None:
            continue
        for d in ac.classify_report(text):
            if d.affects_control:
                assert d.automerge_eligible is False, f"{name}: {d.url} mis-promoted"
