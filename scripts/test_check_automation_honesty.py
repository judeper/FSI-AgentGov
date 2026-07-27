"""Tests for scripts/check_automation_honesty.py.

The guard exists because ``automation`` claims in the manifest are promises to
a reviewer about what the assessment engine actually scored. It must catch
overclaims, permit conservative understatement, and refuse to let the baseline
absorb newly introduced drift.
"""

import copy
import importlib.util
import json
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "assessment"))

_SPEC = importlib.util.spec_from_file_location(
    "check_automation_honesty", REPO_ROOT / "scripts" / "check_automation_honesty.py"
)
guard = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(guard)


ISSUE_263_CONTROLS = ("1.2", "1.4", "1.6", "1.8", "1.10")


def _control(automation, pass_conditions, methods=("Graph_API",)):
    return {
        "id": "9.9",
        "automation": automation,
        "collection_methods": list(methods),
        "checks": [
            {
                "check_id": f"9.9.{chr(97 + i)}",
                "description": "test check",
                "api_call": "Get-MgServicePrincipal",
                "pass_condition": pc,
                "zone_required": [1, 2, 3],
                **({"collection_methods": ["Manual"]} if not pc else {}),
            }
            for i, pc in enumerate(pass_conditions)
        ],
    }


# --- rule semantics -------------------------------------------------------


def test_full_requires_every_check_auto_evaluable():
    facts = guard.evaluate_control(
        _control("full", ["agent_inventory_exists", "not_a_real_evaluator"])
    )
    assert facts["violation"] is not None
    assert "full automation" in facts["violation"]


def test_full_is_honest_when_all_checks_are_wired():
    facts = guard.evaluate_control(_control("full", ["agent_inventory_exists"]))
    assert facts["violation"] is None


def test_full_with_no_checks_is_an_overclaim():
    facts = guard.evaluate_control(_control("full", []))
    assert facts["violation"] is not None


def test_partial_requires_at_least_one_wired_evaluator():
    facts = guard.evaluate_control(_control("partial", ["not_a_real_evaluator"]))
    assert facts["violation"] is not None
    assert "partial automation" in facts["violation"]


def test_partial_is_honest_with_one_wired_and_one_manual_gate():
    facts = guard.evaluate_control(_control("partial", ["agent_inventory_exists", ""]))
    assert facts["violation"] is None


def test_understating_automation_is_allowed():
    """Conservative claims are the fail-closed direction and never fail."""
    assert guard.evaluate_control(_control("manual", []))["violation"] is None
    assert (
        guard.evaluate_control(_control("manual", ["agent_inventory_exists"]))[
            "violation"
        ]
        is None
    )
    # All checks wired but only claiming partial — understated, still honest.
    assert (
        guard.evaluate_control(_control("partial", ["agent_inventory_exists"]))[
            "violation"
        ]
        is None
    )


def test_unknown_automation_value_is_a_violation():
    facts = guard.evaluate_control(_control("mostly", ["agent_inventory_exists"]))
    assert facts["violation"] is not None
    assert "unknown automation value" in facts["violation"]


# --- ratchet behaviour ----------------------------------------------------


def test_new_overclaim_fails_the_check():
    controls = [_control("full", ["agent_inventory_exists", "not_a_real_evaluator"])]
    failures = guard.check(controls, baseline={})
    assert any(f.startswith("NEW OVERCLAIM 9.9") for f in failures)


def test_baseline_absorbs_known_overclaims():
    controls = [_control("full", ["agent_inventory_exists", "not_a_real_evaluator"])]
    baseline = guard.collect_violations(controls)
    assert guard.check(controls, baseline) == []


def test_stale_baseline_entry_fails():
    controls = [_control("full", ["agent_inventory_exists"])]
    baseline = {
        "9.9": {
            "automation": "full",
            "auto_evaluable": 1,
            "checks": 2,
            "reason": "historic",
        }
    }
    failures = guard.check(controls, baseline)
    assert any(f.startswith("STALE BASELINE 9.9") for f in failures)


def test_worsening_a_baselined_control_fails():
    controls = [
        _control("full", ["agent_inventory_exists", "nope_one", "nope_two"]),
    ]
    baseline = guard.collect_violations(
        [_control("full", ["agent_inventory_exists", "nope_one"])]
    )
    failures = guard.check(controls, baseline)
    assert any(f.startswith("BASELINE DRIFT 9.9") for f in failures)


def test_write_refuses_to_add_new_control_ids(tmp_path, capsys):
    existing = {
        "1.3": {
            "automation": "partial",
            "auto_evaluable": 0,
            "checks": 2,
            "reason": "historic",
        }
    }
    controls = [_control("full", ["agent_inventory_exists", "not_a_real_evaluator"])]
    target = tmp_path / "baseline.json"
    rc = guard.write(controls, existing, path=target)
    assert rc == 1
    assert not target.exists()
    assert "refusing to add new control IDs" in capsys.readouterr().err


def test_write_clears_fixed_controls(tmp_path):
    existing = {
        "9.9": {
            "automation": "full",
            "auto_evaluable": 1,
            "checks": 2,
            "reason": "historic",
        }
    }
    controls = [_control("full", ["agent_inventory_exists"])]
    target = tmp_path / "baseline.json"
    rc = guard.write(controls, existing, path=target)
    assert rc == 0
    assert json.loads(target.read_text(encoding="utf-8"))["controls"] == {}


# --- live manifest --------------------------------------------------------


def test_live_manifest_passes_the_guard():
    controls = guard.load_manifest()
    assert guard.check(controls, guard.load_baseline()) == []


@pytest.mark.parametrize("control_id", ISSUE_263_CONTROLS)
def test_issue_263_controls_are_not_baselined(control_id):
    """The five controls reconciled in #263 must stand on their own."""
    assert control_id not in guard.load_baseline()


@pytest.mark.parametrize("control_id", ISSUE_263_CONTROLS)
def test_issue_263_controls_claim_honest_automation(control_id):
    controls = {c["id"]: c for c in guard.load_manifest()}
    facts = guard.evaluate_control(controls[control_id])
    assert facts["violation"] is None, facts["violation"]


def test_baseline_file_is_current():
    controls = guard.load_manifest()
    rendered = guard.render_baseline(guard.collect_violations(controls))
    assert guard.BASELINE.read_text(encoding="utf-8") == rendered


def test_baseline_only_lists_real_control_ids():
    known = {c["id"] for c in guard.load_manifest()}
    assert set(guard.load_baseline()) <= known


def test_manifest_regeneration_is_reproducible():
    """controls.json must stay derivable from generate_manifest.py."""
    spec = importlib.util.spec_from_file_location(
        "generate_manifest",
        REPO_ROOT / "assessment" / "manifest" / "generate_manifest.py",
    )
    gm = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(gm)
    rc = gm.main(["--check"])
    assert rc == 0


def test_control_1_2_downgraded_with_explicit_manual_gates():
    controls = {c["id"]: c for c in guard.load_manifest()}
    ctrl = controls["1.2"]
    checks = {chk["check_id"]: chk for chk in ctrl["checks"]}

    assert ctrl["automation"] == "partial"
    assert checks["1.2.a"]["pass_condition"] == "agent_inventory_exists"
    for check_id in ("1.2.b", "1.2.c"):
        assert checks[check_id]["pass_condition"] == ""
        assert checks[check_id]["collection_methods"] == ["Manual"]
    # Manual gates must not inflate the automated pass threshold.
    assert ctrl["zone_thresholds"]["zone3"]["min_checks_passed"] == 1
    assert isinstance(ctrl["manual_question"], str) and ctrl["manual_question"].strip()


@pytest.mark.parametrize("control_id", ("1.8", "1.10"))
def test_controls_without_evaluators_are_declared_manual(control_id):
    controls = {c["id"]: c for c in guard.load_manifest()}
    ctrl = controls[control_id]

    assert ctrl["automation"] == "manual"
    assert ctrl["checks"] == []
    assert ctrl["collection_methods"] == []
    assert all(
        threshold == {"min_checks_passed": 0, "maturity_score": 0}
        for threshold in ctrl["zone_thresholds"].values()
    )
    assert isinstance(ctrl["manual_question"], str) and ctrl["manual_question"].strip()


def test_manifest_is_not_mutated_by_evaluation():
    controls = guard.load_manifest()
    snapshot = copy.deepcopy(controls)
    guard.collect_violations(controls)
    assert controls == snapshot
