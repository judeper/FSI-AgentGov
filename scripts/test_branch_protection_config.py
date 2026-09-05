"""Regression checks for the planned source-bound dependency gate ruleset."""

from __future__ import annotations

import json
from pathlib import Path


def load_plan() -> dict:
    repo_root = Path(__file__).resolve().parent.parent
    return json.loads(
        (
            repo_root
            / ".github"
            / "trusted-policy"
            / "trusted-dependency-artifact-ruleset.plan.json"
        ).read_text(encoding="utf-8")
    )


def test_legacy_name_only_branch_protection_payload_is_removed() -> None:
    repo_root = Path(__file__).resolve().parent.parent
    assert not (repo_root / ".github" / "branch-protection.json").exists()
    assert not (repo_root / ".github" / "branch-protection.meta.json").exists()


def test_ruleset_plan_is_explicitly_non_applied_and_source_bound() -> None:
    plan = load_plan()
    assert plan["state"] == "planned-not-applied"
    assert plan["repository"] == "judeper/FSI-AgentGov"
    assert plan["ownerType"] == "User"
    assert plan["defaultBranch"] == "main"
    assert plan["requiredWorkflowBinding"]["status"] == "unavailable-for-this-repository"
    assert plan["expectedSource"] == {
        "kind": "dedicated-github-app",
        "appId": "${DEDICATED_GITHUB_APP_ID}",
        "checkName": "trusted-dependency-artifact",
        "rejectGitHubActions": True,
    }


def test_ruleset_requires_strict_app_source_and_full_pr_safety_controls() -> None:
    plan = load_plan()
    rules = {rule["type"]: rule.get("parameters", {}) for rule in plan["ruleset"]["rules"]}
    assert plan["ruleset"]["bypass_actors"] == []
    assert plan["ruleset"]["conditions"]["ref_name"] == {
        "include": ["refs/heads/main"],
        "exclude": [],
    }
    assert rules["required_status_checks"] == {
        "do_not_enforce_on_create": False,
        "strict_required_status_checks_policy": True,
        "required_status_checks": [
            {
                "context": "trusted-dependency-artifact",
                "integration_id": "${DEDICATED_GITHUB_APP_ID}",
            }
        ],
    }
    assert rules["pull_request"]["require_code_owner_review"] is True
    assert rules["pull_request"]["required_review_thread_resolution"] is True
    assert {"non_fast_forward", "deletion", "required_linear_history"} <= rules.keys()
    assert "workflows" not in rules
    assert "merge_queue" not in rules


def test_plan_preserves_the_owner_read_back_strict_branch_protection() -> None:
    plan = load_plan()
    legacy = plan["legacyBranchProtection"]
    assert legacy["preserveExactly"] is True
    assert legacy["requirePresent"] is True
    assert legacy["requireAdminEnforcementIfPresent"] is True
    checks = legacy["expectedRequiredStatusChecks"]
    assert len(checks) == 13
    assert {check["app_id"] for check in checks} == {15368}
    assert {check["context"] for check in checks} == {
        "e2e-smoke",
        "gitleaks",
        "dependency-review",
        "Analyze (python)",
        "Analyze (javascript)",
        "mkdocs-strict",
        "verify_version_stamps",
        "ruff",
        "pytest (assessment + scripts)",
        "manifest / index / nav drift",
        "FSI language rules",
        "autodoc-redirect-verify",
        "autodoc-verify",
    }


def test_plan_requires_both_source_probes_before_apply() -> None:
    plan = load_plan()
    assert plan["preflight"] == {
        "requirePositiveAppProbe": True,
        "requireNegativeActionsProbe": True,
        "requireProbePullRequests": True,
        "positiveMergeability": "clean",
        "negativeMergeability": "blocked",
    }


def test_security_setting_assets_are_in_trusted_paths() -> None:
    repo_root = Path(__file__).resolve().parent.parent
    policy = json.loads(
        (
            repo_root
            / ".github"
            / "trusted-policy"
            / "dependency-artifact-policy.json"
        ).read_text(encoding="utf-8")
    )
    for path in (
        ".github/trusted-policy/trusted-dependency-artifact-ruleset.plan.json",
        ".github/trusted-policy/trusted-dependency-artifact-app-contract.json",
        ".github/trusted-policy/PRETRUST-REVIEW-RUNBOOK.md",
        ".github/TRUSTED-DEPENDENCY-GATE.md",
        "SECURITY.md",
        "scripts/trusted/Invoke-TrustedDependencyArtifactRuleset.ps1",
        "scripts/trusted/trusted-dependency-ruleset.mjs",
        "scripts/verify-required-checks.mjs",
    ):
        assert path in policy["trustedPaths"], path
