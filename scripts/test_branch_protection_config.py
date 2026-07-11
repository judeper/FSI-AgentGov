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
    ]
    assert "markdown-link-check" not in required["contexts"]
