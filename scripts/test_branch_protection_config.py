"""Regression checks for the committed main-branch protection target."""

from __future__ import annotations

import json
from pathlib import Path


def test_branch_protection_preserves_live_checks_and_adds_autodoc_gates() -> None:
    repo_root = Path(__file__).resolve().parent.parent
    protection = json.loads(
        (repo_root / ".github" / "branch-protection.json").read_text(encoding="utf-8")
    )
    required = protection["required_status_checks"]
    assert required["strict"] is True
    assert protection["enforce_admins"] is True
    assert required["contexts"] == [
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
        "trusted-dependency-artifact",
    ]
    assert "markdown-link-check" not in required["contexts"]


def test_branch_protection_body_carries_only_api_fields() -> None:
    """The file is PUT verbatim to the branch-protection API.

    Repository-only metadata must live in the sidecar file, or the API rejects
    the request and protection silently stops being applied.
    """
    repo_root = Path(__file__).resolve().parent.parent
    protection = json.loads(
        (repo_root / ".github" / "branch-protection.json").read_text(encoding="utf-8")
    )
    assert set(protection["required_status_checks"]) == {"strict", "contexts"}


def test_trusted_dependency_artifact_context_is_declared_and_resolvable() -> None:
    """`trusted-dependency-artifact` is published through the Checks API.

    A ``pull_request_target`` job's automatic check run attaches to the default
    branch commit rather than the pull request head, so it can never satisfy a
    required status check. The gate publishes its own check run instead, and the
    sidecar declaration is what keeps that wiring honest.
    """
    repo_root = Path(__file__).resolve().parent.parent
    meta = json.loads(
        (repo_root / ".github" / "branch-protection.meta.json").read_text(
            encoding="utf-8"
        )
    )
    declaration = meta["api_published_contexts"]["trusted-dependency-artifact"]
    for key in ("workflow", "publisher", "policy"):
        assert (repo_root / declaration[key]).is_file(), key

    policy = json.loads(
        (repo_root / declaration["policy"]).read_text(encoding="utf-8")
    )
    assert policy[declaration["policy_key"]] == "trusted-dependency-artifact"

    workflow = (repo_root / declaration["workflow"]).read_text(encoding="utf-8")
    assert "pull_request_target" in workflow
    # The gate must never materialise candidate code in its workspace.
    assert "pull_request.head.ref" not in workflow
    assert "refs/pull/" not in workflow
