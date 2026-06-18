"""Tests for autodoc_canary.py — the poison-pill guard must reject every sample."""

from __future__ import annotations

import autodoc_canary as canary


def test_every_poison_sample_is_rejected():
    results = canary.run_canary()
    assert results, "canary fixture set is empty"
    leaks = [name for name, rejected, _ in results if not rejected]
    assert leaks == [], f"poison samples mis-promoted by the routing gate: {leaks}"


def test_canary_main_returns_zero_when_healthy():
    assert canary.main([]) == 0


def test_fixture_set_covers_each_hard_human_category():
    # Sanity: the poison set should exercise the breadth of the gate.
    names = {name for name, _ in canary.CANARY_FIXTURES}
    for expected in (
        "hallucinated_regulatory_citation",
        "fabricated_retention_duration",
        "spelled_out_duration",
        "compact_duration",
        "overclaim",
        "deprecation",
        "license_sku_change",
        "a_series_sku",
        "control_prose_edit",
        "critical_tier",
        "critical_without_reason",
        "future_date_deadline",
        "abbreviated_date",
        "reg_s_p",
        "missing_diff",
    ):
        assert expected in names
