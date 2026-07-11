"""Tests for autodoc_canary.py — the poison-pill guard must reject every sample."""

from __future__ import annotations

import json

import autodoc_canary as canary


def test_every_poison_sample_is_rejected():
    results = canary.run_canary()
    assert results, "canary fixture set is empty"
    leaks = [name for name, rejected, _ in results if not rejected]
    assert leaks == [], f"poison samples mis-promoted by the routing gate: {leaks}"


def test_canary_main_returns_zero_when_healthy():
    assert canary.main([]) == 0


def test_cross_model_adapter_uses_existing_review_api_offline():
    calls: list[tuple[str, int]] = []

    def reject_runner(prompt: str, model: str, timeout: int) -> str:
        calls.append((model, timeout))
        assert "no evidence supports the added claim" in prompt
        return json.dumps(
            {
                "verdict": "fail",
                "confidence": 1,
                "unsupported_claims": ["unsupported poison claim"],
                "overbroad_edits": [],
                "notes": "rejected",
            }
        )

    verifier = canary.make_cross_model_verifier(model="review-model", timeout=17, runner=reject_runner)
    results = canary.run_canary(verifier)
    assert all(rejected for _name, rejected, _decision in results)
    assert len(calls) == len(canary.CANARY_FIXTURES)
    assert set(calls) == {("review-model", 17)}


def test_cross_model_canary_fails_closed_on_reviewer_pass_or_exception():
    assert any(
        not rejected
        for _name, rejected, _decision in canary.run_canary(lambda _name, _change: False)
    )

    def unavailable(_name, _change):
        raise RuntimeError("reviewer unavailable")

    assert any(not rejected for _name, rejected, _decision in canary.run_canary(unavailable))


def test_fixture_set_covers_each_hard_human_category():
    # Sanity: the poison set should exercise the breadth of the gate.
    names = {name for name, _ in canary.CANARY_FIXTURES}
    for expected in (
        "hallucinated_regulatory_citation",
        "fabricated_retention_duration",
        "spelled_out_duration",
        "compact_duration",
        "hyphenated_duration",
        "quantified_year",
        "half_year_duration",
        "framework_citation_hipaa",
        "iso_iec_27001",
        "reg_sp_hyphen",
        "frequency_adverb_quarterly",
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
        "link_prose_anchor_title",
        "missing_diff",
    ):
        assert expected in names
