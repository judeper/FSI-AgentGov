"""Tests for autodoc_classifier.py — the deterministic, fail-closed routing gate.

The guiding requirement (from the June 2026 autodoc council review) is that the
classifier must NEVER promote a compliance-sensitive change to ``autodraft`` /
``automerge_eligible``. These tests encode that as executable guardrails, plus
integration checks against the real report fixtures in ``reports/monitoring/``.
"""

from __future__ import annotations

from pathlib import Path

import autodoc_classifier as ac
import pytest

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


def _assert_human_not_automerge(text, category=None, classification="MEDIUM"):
    d = ac.classify_change(_change(f"--- +++ @@\n+{text}", classification=classification))
    assert d.route == "human"
    assert d.automerge_eligible is False
    if category:
        assert category in d.sensitive_categories


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


@pytest.mark.parametrize(
    "text",
    [
        "Records are retained for one year.",
        "Records are retained for ninety days.",
        "Records are retained for thirty (30) days.",
        "Retention changed to 1y.",
        "Retention changed to 90d.",
        "Retention changed to 6m.",
        "Retention changed to 12 months.",
    ],
)
def test_duration_bypasses_route_to_human(text):
    _assert_human_not_automerge(text, "duration_or_retention")


@pytest.mark.parametrize(
    "text,category",
    [
        ("Records retained for a one-year period.", "duration_or_retention"),
        ("Logs are retained for a year.", "duration_or_retention"),
        ("kept for half a year.", "duration_or_retention"),
        ("Retention is one hundred eighty days.", "duration_or_retention"),
        ("This maps to Reg-SP.", "regulatory_citation"),
        (
            "This maps to HIPAA / PCI DSS / CCPA / GDPR / NIST 800-53 / "
            "SOC 2 / ISO 27001 requirements.",
            "regulatory_citation",
        ),
        ("Reviews occur quarterly.", "duration_or_retention"),
        ("Reviews occur annually.", "duration_or_retention"),
    ],
)
def test_round2_confirmed_sensitive_paraphrases_route_to_human(text, category):
    _assert_human_not_automerge(text, category)


@pytest.mark.parametrize(
    "text",
    [
        "The deadline is Sept. 30, 2026.",
        "The feature ships in Sep 2026.",
        "The deadline is 9/30/2026.",
        "The deadline is 2026-09-30.",
        "The change lands in Q3 2026.",
    ],
)
def test_date_bypasses_route_to_human(text):
    _assert_human_not_automerge(text, "date_or_deadline")


@pytest.mark.parametrize(
    "text",
    [
        "This maps to Reg S-P obligations.",
        "This maps to Regulation S-P obligations.",
        "This maps to Reg SCI obligations.",
        "This maps to Reg BI obligations.",
        "Records must follow 17 CFR 240.17a-4.",
        "This maps to ISO/IEC 27001 certification.",
    ],
)
def test_regulatory_citation_bypasses_route_to_human(text):
    _assert_human_not_automerge(text, "regulatory_citation")


@pytest.mark.parametrize(
    "text",
    [
        "Requires Microsoft 365 A5.",
        "Requires G5.",
        "Requires E5.",
        "Requires F3.",
        "Requires P2.",
        "Requires A1.",
    ],
)
def test_license_sku_bypasses_route_to_human(text):
    _assert_human_not_automerge(text, "license_sku")


@pytest.mark.parametrize(
    "text",
    [
        "Configure DLP before rollout.",
        "Configure data loss prevention before rollout.",
        "Use eDiscovery for investigation.",
        "Retention policies apply.",
        "Apply a sensitivity label.",
        "Information barrier policies apply.",
        "Place content under legal hold.",
        "Encryption is required.",
        "Review the audit log.",
        "Privacy review is required.",
        "PII is in scope.",
        "Supervision policies apply.",
        "Insider risk signals changed.",
    ],
)
def test_compliance_surface_bypasses_route_to_human(text):
    _assert_human_not_automerge(text, "compliance_surface")


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


def test_additive_control_change_routes_to_human():
    d = ac.classify_change(_change(
        "--- +++ @@\n+Add a neutral cross reference.", controls=["1.15"]
    ))
    assert d.route == "human"
    assert d.automerge_eligible is False
    assert d.affects_control is True


def test_missing_diff_routes_to_human():
    d = ac.classify_change(_change(""))
    assert d.route == "human"
    assert d.automerge_eligible is False


def test_unknown_or_missing_tier_routes_to_human():
    for tier in ("", "LOW"):
        d = ac.classify_change(_change("--- +++ @@\n+Neutral addition.", classification=tier))
        assert d.route == "human"
        assert d.automerge_eligible is False


def test_parse_critical_without_reason_routes_to_human():
    text = """### 1. Critical Without Reason

**URL:** https://learn.microsoft.com/en-us/example/critical
**Classification:** CRITICAL

**What Changed:**
```diff
--- +++ @@
+A neutral sentence under a critical tier.
```
"""
    changes = ac.parse_report(text)
    assert len(changes) == 1
    assert changes[0].classification == "CRITICAL"
    assert changes[0].reason == ""
    d = ac.classify_change(changes[0])
    assert d.route == "human"
    assert d.automerge_eligible is False


def test_parse_extracts_content_hash_line():
    # The Content-Hash line is the change's exact identity. It must round-trip from the report
    # into Change.content_hash and through classify_change into the RoutingDecision so the
    # contract/issue body can carry it for the deferred-baseline advance step.
    text = """### 1. Identity Carrier

**URL:** https://learn.microsoft.com/en-us/example/identity
**Classification:** MEDIUM (General content update)
**Content-Hash:** sha256:abc123def456

**What Changed:**
```diff
--- +++ @@
+A neutral sentence.
```
"""
    changes = ac.parse_report(text)
    assert len(changes) == 1
    assert changes[0].content_hash == "sha256:abc123def456"
    assert ac.classify_change(changes[0]).content_hash == "sha256:abc123def456"


def test_parse_summary_only_entry_routes_to_human():
    text = """### 1. Summary Only

**URL:** https://learn.microsoft.com/en-us/example/summary
**Classification:** MEDIUM (General content update)
"""
    changes = ac.parse_report(text)
    assert len(changes) == 1
    assert changes[0].diff_text == ""
    d = ac.classify_change(changes[0])
    assert d.route == "human"
    assert d.automerge_eligible is False


def test_parse_deduplicates_by_url_preferring_diff_block():
    text = """### 1. Summary Only

**URL:** https://learn.microsoft.com/en-us/example/duplicate
**Classification:** MEDIUM (General content update)

---

### 2. Detailed

**URL:** https://learn.microsoft.com/en-us/example/duplicate
**Classification:** MEDIUM (General content update)

**What Changed:**
```diff
--- +++ @@
+A neutral sentence.
```
"""
    changes = ac.parse_report(text)
    assert len(changes) == 1
    assert changes[0].topic == "Detailed"
    assert changes[0].diff_text.strip()


def test_regression_731_deduplicates_redirect_rows_by_canonical_source():
    text = """## URL Redirects Detected

| Original URL | Final URL |
|---|---|
| https://learn.microsoft.com/en-us/a?msockid=one | https://learn.microsoft.com/en-us/b?utm_source=monitor |
| https://learn.microsoft.com/en-us/a?utm_campaign=two | https://learn.microsoft.com/en-us/b |
"""
    redirects = [change for change in ac.parse_report(text) if change.kind == "redirect"]
    assert len(redirects) == 1
    assert redirects[0].url == "https://learn.microsoft.com/en-us/a"
    assert redirects[0].destination_url == "https://learn.microsoft.com/en-us/b"


def test_conflicting_destinations_for_one_canonical_source_fail_closed():
    text = """## URL Redirects Detected

| Original URL | Final URL |
|---|---|
| https://learn.microsoft.com/en-us/a?msockid=one | https://learn.microsoft.com/en-us/b |
| https://learn.microsoft.com/en-us/a?utm_campaign=two | https://learn.microsoft.com/en-us/c |
"""
    changes = ac.parse_report(text)
    assert len(changes) == 1
    assert changes[0].classification == "REDIRECT_CONFLICT"
    assert ac.classify_change(changes[0]).route == "human"


def test_regression_732_canonicalizes_msockid_before_routing():
    text = """### 1. Tracked source

**URL:** https://learn.microsoft.com/en-us/example?msockid=abc123
**Classification:** MEDIUM

**What Changed:**
```diff
--- +++ @@
+A neutral sentence.
```
"""
    change = ac.parse_report(text)[0]
    decision = ac.classify_change(change)
    assert change.url == "https://learn.microsoft.com/en-us/example"
    assert decision.url == change.url


def test_regression_733_strips_all_known_tracking_but_preserves_functional_query_and_fragment():
    url = (
        "https://learn.microsoft.com/en-us/example?"
        "view=power-platform&WT.mc_id=a&utm_source=b&ocid=c&lang=en-us#limits"
    )
    assert ac._canonicalize_url(url) == (
        "https://learn.microsoft.com/en-us/example?view=power-platform&lang=en-us#limits"
    )


# ---------------------------------------------------------------------------
# The narrow "autodraft" promotions; automerge remains redirect-only
# ---------------------------------------------------------------------------
def test_mechanical_addition_is_autodraft():
    d = ac.classify_change(_change(
        "--- +++ @@\n+See the new agent governance overview for related guidance."
    ))
    assert d.route == "autodraft"
    assert d.automerge_eligible is False
    assert any("automerge is redirect-only" in r for r in d.reasons)


def test_benign_markdown_cross_reference_is_not_automerge_eligible():
    d = ac.classify_change(_change(
        "--- +++ @@\n+- See also: [Agent guidance](https://learn.microsoft.com/fwlink/link)"
    ))
    assert d.route == "autodraft"
    assert d.automerge_eligible is False
    assert any("automerge is redirect-only" in r for r in d.reasons)


@pytest.mark.parametrize(
    "addition",
    [
        "[how to permanently erase customer data](https://x.co)",
        '[Docs](https://x.co "erase messages before any discovery request")',
        "See the new overview.",
    ],
)
def test_content_additions_are_never_automerge_eligible(addition):
    d = ac.classify_change(_change(f"--- +++ @@\n+{addition}"))
    assert d.automerge_eligible is False
    assert any("automerge is redirect-only" in r for r in d.reasons)


def test_addition_with_number_is_autodraft_but_not_automerge():
    d = ac.classify_change(_change(
        "--- +++ @@\n+There are now three panes; see pane number 2 for details."
    ))
    # "number" is fine for drafting, but content never qualifies for unattended merge.
    assert d.route == "autodraft"
    assert d.automerge_eligible is False
    assert any("automerge is redirect-only" in r for r in d.reasons)


def test_high_tier_addition_is_not_automerge_eligible():
    d = ac.classify_change(_change(
        "--- +++ @@\n+A short neutral cross reference sentence.", classification="HIGH"
    ))
    assert d.route == "autodraft"
    assert d.automerge_eligible is False


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


def test_0618_control_changes_and_summary_only_entries_fail_closed():
    text = _load("learn-changes-2026-06-18.md")
    if text is None:
        pytest.skip("fixture report not present")
    changes = ac.parse_report(text)
    assert changes
    for change in changes:
        d = ac.classify_change(change)
        if change.affected_controls:
            assert d.automerge_eligible is False, f"{change.url} mis-promoted"
        if change.kind == "content" and not change.diff_text.strip():
            assert d.route != "autodraft", f"{change.url} summary-only autodraft"


def test_0618_automerge_eligible_is_redirect_only():
    text = _load("learn-changes-2026-06-18.md")
    if text is None:
        pytest.skip("fixture report not present")
    for change in ac.parse_report(text):
        d = ac.classify_change(change)
        if d.automerge_eligible:
            assert d.kind == "redirect", f"{change.url} content mis-promoted"
