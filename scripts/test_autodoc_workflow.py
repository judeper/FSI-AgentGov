"""Tests for trusted autodoc workflow metadata classification."""

from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

import autodoc_workflow as workflow
import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
WORKFLOW_PATH = REPO_ROOT / ".github" / "workflows" / "autodoc-verify.yml"


def test_workflow_persists_pr_metadata_before_contract_extraction() -> None:
    workflow_text = WORKFLOW_PATH.read_text(encoding="utf-8")

    pr_number = workflow_text.index('PR_NUMBER="$EVENT_PR"')
    metadata_write = workflow_text.index(
        'gh api "repos/$REPO/pulls/$PR_NUMBER" > .autodoc/pr-meta.json'
    )
    metadata_read = workflow_text.index(
        'pr = json.loads((work / "pr-meta.json").read_text(encoding="utf-8"))'
    )

    assert pr_number < metadata_write < metadata_read


def test_workflow_fails_explicitly_when_escalation_token_is_unavailable() -> None:
    workflow_text = WORKFLOW_PATH.read_text(encoding="utf-8")

    assert "Refuse silent escalation when write token is unavailable" in workflow_text
    assert "steps.app-token.outputs.token == ''" in workflow_text
    assert "no label or comment was written" in workflow_text
    assert "steps.app-token.outputs.token != ''" in workflow_text


def test_workflow_imports_trusted_helper_from_repo_root() -> None:
    workflow_text = WORKFLOW_PATH.read_text(encoding="utf-8")
    import_match = re.search(
        r"^\s*((?:from scripts )?import autodoc_workflow as workflow)\s*$",
        workflow_text,
        re.MULTILINE,
    )

    assert import_match is not None
    completed = subprocess.run(
        [sys.executable, "-c", import_match.group(1)],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    assert completed.returncode == 0, completed.stderr


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


def test_parse_pr_markers_accepts_runner_source_report_marker() -> None:
    parsed = workflow.parse_pr_markers(
        "AUTODOC-FINGERPRINT: sha256:abc\nSource report: reports/monitoring/learn-changes-test.md\n"
    )

    assert parsed["fingerprint"] == "sha256:abc"
    assert parsed["report_path"] == "reports/monitoring/learn-changes-test.md"
    assert parsed["route"] is None


def test_derive_trusted_contract_uses_base_routing_data(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    report_rel = "reports/monitoring/learn-changes-test.md"
    report_file = tmp_path / "reports" / "monitoring" / "learn-changes-test.md"
    report_file.parent.mkdir(parents=True)
    report_file.write_text("report body", encoding="utf-8")

    trusted_contract = {
        "schema_version": 1,
        "fingerprint": "sha256:abc",
        "report_path": report_rel,
        "allowed_files": ["docs/reference/microsoft-learn-urls.md"],
        "allowed_headings": ["Copilot Studio"],
        "forbidden_paths": ["scripts/**"],
    }
    spec = {
        "fingerprint": "sha256:abc",
        "route": "autodraft",
        "body": "```json\n" + json.dumps(trusted_contract) + "\n```",
    }

    monkeypatch.setattr(workflow, "_route_specs_for_report", lambda *_args, **_kwargs: [spec])
    pr_body = "AUTODOC-FINGERPRINT: sha256:abc\nSource report: reports/monitoring/learn-changes-test.md\n"

    resolved = workflow.derive_trusted_contract(pr_body, repo_root=tmp_path)

    assert resolved["fingerprint"] == "sha256:abc"
    assert resolved["route"] == "autodraft"
    assert resolved["report_path"] == report_rel
    assert resolved["contract"]["allowed_files"] == ["docs/reference/microsoft-learn-urls.md"]


def test_derive_trusted_contract_fails_on_route_mismatch(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    report_rel = "reports/monitoring/learn-changes-test.md"
    report_file = tmp_path / "reports" / "monitoring" / "learn-changes-test.md"
    report_file.parent.mkdir(parents=True)
    report_file.write_text("report body", encoding="utf-8")
    contract = {
        "schema_version": 1,
        "fingerprint": "sha256:abc",
        "report_path": report_rel,
        "allowed_files": ["docs/reference/microsoft-learn-urls.md"],
        "allowed_headings": ["Copilot Studio"],
        "forbidden_paths": ["scripts/**"],
    }
    spec = {
        "fingerprint": "sha256:abc",
        "route": "autodraft",
        "body": "```json\n" + json.dumps(contract) + "\n```",
    }
    monkeypatch.setattr(workflow, "_route_specs_for_report", lambda *_args, **_kwargs: [spec])

    with pytest.raises(ValueError, match="does not match trusted route"):
        workflow.derive_trusted_contract(
            "AUTODOC-FINGERPRINT: sha256:abc\n"
            "AUTODOC-ROUTE: human\n"
            "Source report: reports/monitoring/learn-changes-test.md\n",
            repo_root=tmp_path,
        )


def test_derive_trusted_contract_fails_closed_for_missing_report_file(tmp_path: Path) -> None:
    with pytest.raises(ValueError, match="does not exist on base checkout"):
        workflow.derive_trusted_contract(
            "AUTODOC-FINGERPRINT: sha256:abc\n"
            "Source report: reports/monitoring/learn-changes-missing.md\n",
            repo_root=tmp_path,
        )


def test_derive_trusted_contract_fails_closed_for_widened_pr_allowlist(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    report_rel = "reports/monitoring/learn-changes-test.md"
    report_file = tmp_path / "reports" / "monitoring" / "learn-changes-test.md"
    report_file.parent.mkdir(parents=True)
    report_file.write_text("report body", encoding="utf-8")
    trusted_contract = {
        "schema_version": 1,
        "fingerprint": "sha256:abc",
        "report_path": report_rel,
        "allowed_files": ["docs/reference/microsoft-learn-urls.md"],
        "allowed_headings": ["Copilot Studio"],
        "forbidden_paths": ["scripts/**"],
    }
    spec = {
        "fingerprint": "sha256:abc",
        "route": "autodraft",
        "body": "```json\n" + json.dumps(trusted_contract) + "\n```",
    }
    monkeypatch.setattr(workflow, "_route_specs_for_report", lambda *_args, **_kwargs: [spec])

    pr_supplied_contract = {
        "fingerprint": "sha256:abc",
        "allowed_files": [
            "docs/reference/microsoft-learn-urls.md",
            "docs/controls/pillar-1-security/1.1-example.md",
        ],
    }
    pr_body = (
        "AUTODOC-FINGERPRINT: sha256:abc\n"
        "Source report: reports/monitoring/learn-changes-test.md\n\n"
        "```json\n"
        + json.dumps(pr_supplied_contract)
        + "\n```"
    )

    with pytest.raises(ValueError, match="widens allowed_files"):
        workflow.derive_trusted_contract(pr_body, repo_root=tmp_path)


def test_preflight_changed_files_rejects_path_outside_trusted_allowlist() -> None:
    contract = {
        "allowed_files": ["docs/reference/microsoft-learn-urls.md"],
        "forbidden_paths": ["scripts/**", ".github/**"],
    }

    with pytest.raises(ValueError, match="not listed in trusted contract allowed_files"):
        workflow.preflight_changed_files(
            [{"filename": "docs/controls/pillar-1-security/1.1-example.md", "status": "modified"}],
            contract,
        )


def test_preflight_changed_files_allows_trusted_markdown_edit() -> None:
    contract = {
        "allowed_files": ["docs/reference/microsoft-learn-urls.md"],
        "forbidden_paths": ["scripts/**", ".github/**"],
    }

    assert workflow.preflight_changed_files(
        [{"filename": "docs/reference/microsoft-learn-urls.md", "status": "modified"}],
        contract,
    ) == ["docs/reference/microsoft-learn-urls.md"]
