"""Tests for trusted autodoc workflow metadata classification."""

from __future__ import annotations

import json
from pathlib import Path

import autodoc_workflow as workflow
import pytest

WORKFLOW_PATH = Path(__file__).resolve().parents[1] / ".github" / "workflows" / "autodoc-verify.yml"


@pytest.mark.parametrize("head_ref", ["autodoc/abc123", "copilot/autodoc-fix"])
def test_is_autodoc_pr_accepts_both_pipeline_prefixes(head_ref: str) -> None:
    assert workflow.is_autodoc_pr(head_ref, {"autodoc"})


@pytest.mark.parametrize("head_ref", ["feature/docs", "autodocish/x", "copilotish/x"])
def test_is_autodoc_pr_rejects_other_prefixes(head_ref: str) -> None:
    assert not workflow.is_autodoc_pr(head_ref, {"autodoc"})


def test_is_autodoc_pr_requires_label() -> None:
    assert not workflow.is_autodoc_pr("autodoc/abc123", {"documentation"})


def test_main_writes_fail_closed_metadata_outputs(tmp_path) -> None:
    pr_path = tmp_path / "pr.json"
    labels_path = tmp_path / "labels.json"
    output_path = tmp_path / "output.txt"
    pr_path.write_text(
        json.dumps(
            {
                "number": 42,
                "head": {
                    "ref": "copilot/autodoc-fix",
                    "sha": "abc",
                    "repo": {"full_name": "judeper/FSI-AgentGov"},
                },
            }
        ),
        encoding="utf-8",
    )
    labels_path.write_text(json.dumps([{"name": "autodoc"}]), encoding="utf-8")

    assert workflow.main(
        [
            "--pr-json",
            str(pr_path),
            "--labels-json",
            str(labels_path),
            "--github-output",
            str(output_path),
        ]
    ) == 0
    outputs = dict(line.split("=", 1) for line in output_path.read_text(encoding="utf-8").splitlines())
    assert outputs["is_autodoc"] == "true"
    assert outputs["head_ref"] == "copilot/autodoc-fix"


def test_workflow_uses_trusted_base_and_builtin_token() -> None:
    text = WORKFLOW_PATH.read_text(encoding="utf-8")

    assert "pull_request_target:" in text
    assert "issues: write" in text
    assert "ref: ${{ steps.pr.outputs.base_sha }}" in text
    assert "persist-credentials: false" in text
    assert "actions/create-github-app-token" not in text
    assert "pull-requests: write" not in text
    assert text.count("GH_TOKEN: ${{ github.token }}") >= 4
    assert "only Markdown files may be fetched under pull_request_target" in text
    assert text.index("Refuse forked autodoc PRs") < text.index(
        "Fetch diff and allowed PR head markdown files"
    )
