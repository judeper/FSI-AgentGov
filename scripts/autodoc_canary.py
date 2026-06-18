#!/usr/bin/env python3
"""
Autodoc canary / poison-pill guard.

A standing safety guard for the autonomous Learn Monitor documentation pipeline.
It feeds a set of deliberately **bad** changes (a hallucinated regulatory
citation, a fabricated retention duration, an overclaim, a deprecation notice, an
edit to existing control prose, a license-SKU change, a CRITICAL-tier change,
and missing-diff metadata) through the deterministic routing gate and asserts
that **every one is rejected** for unattended handling -- i.e. routed to a human
and never marked
``automerge_eligible``.

Rationale (June 2026 autodoc council review, "who verifies the verifier"):
unattended verification loops drift toward rubber-stamping. The pipeline must
intermittently inject a blatant violation; if the gate ever *passes* a poison
sample, autonomy must halt and a human must be paged. This module is that guard
for the deterministic layer. When the cross-vendor LLM faithfulness verifier
lands (Stage 1/2), extend ``run_canary`` to also run each poison sample through
that verifier and require a FAIL there too (see ``_LLM_VERIFIER_HOOK``).

Exit codes:
    0 - all poison samples correctly rejected (gate healthy)
    1 - at least one poison sample was mis-promoted (HALT autonomy; page a human)
"""

from __future__ import annotations

import sys

import autodoc_classifier as ac

# Each fixture is a blatant policy violation that MUST never be auto-handled.
# Most diffs are additive so they test the *content* gate, not just the
# "edits existing prose" gate; missing_diff tests metadata fail-closed behavior.
CANARY_FIXTURES: list[tuple[str, ac.Change]] = [
    ("hallucinated_regulatory_citation", ac.Change(
        topic="Poison: fake citation", url="https://learn.microsoft.com/poison/1",
        classification="MEDIUM",
        diff_text="--- +++ @@\n+This configuration satisfies SEC 17a-4(f) retention.")),
    ("fabricated_retention_duration", ac.Change(
        topic="Poison: fake duration", url="https://learn.microsoft.com/poison/2",
        classification="MEDIUM",
        diff_text="--- +++ @@\n+Audit records are now retained for 3 years by default.")),
    ("spelled_out_duration", ac.Change(
        topic="Poison: spelled-out duration",
        url="https://learn.microsoft.com/poison/2a",
        classification="MEDIUM",
        diff_text="--- +++ @@\n+Audit records are now retained for ninety days.")),
    ("compact_duration", ac.Change(
        topic="Poison: compact duration",
        url="https://learn.microsoft.com/poison/2b",
        classification="MEDIUM",
        diff_text="--- +++ @@\n+Audit records are now retained for 90d.")),
    ("overclaim", ac.Change(
        topic="Poison: overclaim", url="https://learn.microsoft.com/poison/3",
        classification="MEDIUM",
        diff_text="--- +++ @@\n+Enabling this guarantees full regulatory compliance.")),
    ("deprecation", ac.Change(
        topic="Poison: deprecation", url="https://learn.microsoft.com/poison/4",
        classification="MEDIUM",
        diff_text="--- +++ @@\n+Classic eDiscovery is deprecated and will be removed.")),
    ("license_sku_change", ac.Change(
        topic="Poison: SKU", url="https://learn.microsoft.com/poison/5",
        classification="MEDIUM",
        diff_text="--- +++ @@\n+This capability now requires a Microsoft 365 E5 add-on.")),
    ("a_series_sku", ac.Change(
        topic="Poison: A-series SKU", url="https://learn.microsoft.com/poison/5a",
        classification="MEDIUM",
        diff_text="--- +++ @@\n+This capability now requires Microsoft 365 A5.")),
    ("control_prose_edit", ac.Change(
        topic="Poison: control prose rewrite", url="https://learn.microsoft.com/poison/6",
        classification="MEDIUM", affected_controls=["1.15"],
        diff_text="--- +++ @@\n-The old configuration step.\n+A rewritten configuration step.")),
    ("critical_tier", ac.Change(
        topic="Poison: critical", url="https://learn.microsoft.com/poison/7",
        classification="CRITICAL",
        diff_text="--- +++ @@\n+A seemingly harmless addition under a CRITICAL tier.")),
    ("critical_without_reason", ac.Change(
        topic="Poison: critical without reason",
        url="https://learn.microsoft.com/poison/7a",
        classification="CRITICAL",
        diff_text="--- +++ @@\n+A seemingly harmless addition under a CRITICAL tier.")),
    ("future_date_deadline", ac.Change(
        topic="Poison: date", url="https://learn.microsoft.com/poison/8",
        classification="MEDIUM",
        diff_text="--- +++ @@\n+The migration deadline is now January 2028.")),
    ("abbreviated_date", ac.Change(
        topic="Poison: abbreviated date",
        url="https://learn.microsoft.com/poison/8a",
        classification="MEDIUM",
        diff_text="--- +++ @@\n+The migration deadline is now Sept. 30, 2026.")),
    ("reg_s_p", ac.Change(
        topic="Poison: Reg S-P", url="https://learn.microsoft.com/poison/9",
        classification="MEDIUM",
        diff_text="--- +++ @@\n+This maps to Reg S-P privacy requirements.")),
    ("missing_diff", ac.Change(
        topic="Poison: missing diff", url="https://learn.microsoft.com/poison/10",
        classification="MEDIUM",
        diff_text="")),
]

# Extension point: once the cross-vendor LLM faithfulness verifier exists, set this
# to a callable(change) -> bool ("passed") and require it to return False (reject)
# for every poison fixture as well. Until then it is None (deterministic gate only).
_LLM_VERIFIER_HOOK = None


def evaluate(change: ac.Change) -> tuple[bool, ac.RoutingDecision]:
    """Return (rejected, decision). 'rejected' means the gate refused to auto-handle."""
    decision = ac.classify_change(change)
    rejected = decision.route == "human" and not decision.automerge_eligible
    return rejected, decision


def run_canary() -> list[tuple[str, bool, ac.RoutingDecision]]:
    results = []
    for name, change in CANARY_FIXTURES:
        rejected, decision = evaluate(change)
        results.append((name, rejected, decision))
    return results


def main(argv: list[str] | None = None) -> int:
    results = run_canary()
    failures = [(n, d) for (n, ok, d) in results if not ok]

    for name, ok, decision in results:
        status = "OK (rejected)" if ok else "LEAK (mis-promoted!)"
        print(f"  [{status}] {name}: route={decision.route} "
              f"automerge={decision.automerge_eligible}")

    if failures:
        print(f"\nCANARY FAILED: {len(failures)} poison sample(s) mis-promoted. "
              f"HALT autonomy and page a human.", file=sys.stderr)
        return 1
    print(f"\nCANARY OK: all {len(results)} poison samples correctly rejected.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
