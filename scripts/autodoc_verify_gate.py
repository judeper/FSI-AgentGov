"""Fail-closed merge-gate orchestrator for autodoc pull requests.

Runs the deterministic verifier only. The independent cross-model review runs
locally in the unattended runner before a pull request is opened; this CI gate
is a deterministic backstop suitable for a branch-protection required check.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Callable

import autodoc_verify

Conclusion = str
DeterministicVerifier = Callable[..., dict[str, Any]]

_EXIT_CODES = {"pass": 0, "fail": 1, "needs_human": 2}


def run_gate(
    contract: dict[str, Any],
    report_text: str,
    diff_text: str,
    file_contents: dict[str, str],
    *,
    pr_body: str | None,
    repo_root: str | Path,
    _det: DeterministicVerifier | None = None,
) -> dict[str, Any]:
    """Run the deterministic verifier and fail closed on any blocking finding."""

    det = _det or autodoc_verify.verify

    try:
        deterministic = det(
            contract,
            diff_text,
            file_contents,
            report_text,
            pr_body=pr_body,
            repo_root=repo_root,
        )
    except Exception as exc:
        deterministic = {
            "pass": False,
            "findings": [
                {
                    "check": "deterministic_exception",
                    "severity": "block",
                    "path": "",
                    "message": f"{type(exc).__name__}: {exc}",
                }
            ],
            "summary": {"block_findings": 1, "warn_findings": 0},
        }

    if deterministic.get("pass"):
        return _result("pass", deterministic, "Deterministic verifier passed.")
    return _result("fail", deterministic, _deterministic_failure_summary(deterministic))


def main(argv: list[str] | None = None) -> int:
    """CLI entry point for GitHub Actions."""

    parser = argparse.ArgumentParser(description="Run the autodoc deterministic verification gate.")
    parser.add_argument("--contract", required=True, help="Path to authoring contract JSON.")
    parser.add_argument("--report", required=True, help="Path to source monitoring report.")
    parser.add_argument("--diff", required=True, help="Path to unified PR diff, or '-' for stdin.")
    parser.add_argument("--head-dir", required=True, help="Directory containing post-edit changed file contents.")
    parser.add_argument("--pr-body", required=True, help="Path to pull request body text.")
    parser.add_argument("--out", required=True, help="Path where gate result JSON should be written.")
    args = parser.parse_args(argv)

    try:
        contract = autodoc_verify.load_contract(args.contract)
        report_text = Path(args.report).read_text(encoding="utf-8")
        diff_text = sys.stdin.read() if args.diff == "-" else Path(args.diff).read_text(encoding="utf-8")
        pr_body = Path(args.pr_body).read_text(encoding="utf-8")
        head_dir = Path(args.head_dir)
        file_contents = autodoc_verify._read_post_edit_contents(  # noqa: SLF001 - CLI companion uses verifier helper.
            head_dir,
            autodoc_verify.parse_unified_diff(diff_text),
        )
        result = run_gate(
            contract,
            report_text,
            diff_text,
            file_contents,
            pr_body=pr_body,
            repo_root=head_dir,
        )
    except Exception as exc:
        result = {
            "conclusion": "needs_human",
            "deterministic": {},
            "summary": f"Autodoc verify gate CLI error: {type(exc).__name__}: {exc}",
        }

    _write_json(args.out, result)
    print(f"Autodoc verify gate: {result['conclusion']} - {result['summary']}")
    return _EXIT_CODES.get(result["conclusion"], 2)


def _result(
    conclusion: Conclusion,
    deterministic: dict[str, Any],
    summary: str,
) -> dict[str, Any]:
    return {
        "conclusion": conclusion,
        "deterministic": deterministic,
        "summary": summary,
    }


def _deterministic_failure_summary(deterministic: dict[str, Any]) -> str:
    summary = deterministic.get("summary", {})
    block_count = summary.get("block_findings")
    if block_count is None:
        block_count = sum(1 for finding in deterministic.get("findings", []) if finding.get("severity") == "block")
    return f"Deterministic verifier failed with {block_count} blocking finding(s)."


def _write_json(path: str, result: dict[str, Any]) -> None:
    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")


if __name__ == "__main__":
    raise SystemExit(main())
