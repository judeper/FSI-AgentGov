#!/usr/bin/env python3
"""Trusted helpers used by autodoc pull_request_target workflows."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Iterable

AUTODOC_BRANCH_PREFIXES = ("autodoc/", "copilot/")


def is_autodoc_pr(head_ref: str, label_names: Iterable[str]) -> bool:
    """Return whether PR metadata identifies a same-pipeline autodoc change."""

    labels = {str(name) for name in label_names}
    return head_ref.startswith(AUTODOC_BRANCH_PREFIXES) and "autodoc" in labels


def classify_metadata(pr: dict[str, Any], labels: list[dict[str, Any]]) -> dict[str, str]:
    """Convert GitHub PR/label API payloads into workflow outputs."""

    label_names = {
        str(label["name"])
        for label in labels
        if isinstance(label, dict) and isinstance(label.get("name"), str)
    }
    head = pr.get("head") or {}
    head_repo = head.get("repo") or {}
    head_ref = str(head.get("ref") or "")
    return {
        "pr": str(pr.get("number") or ""),
        "head_ref": head_ref,
        "head_sha": str(head.get("sha") or ""),
        "head_repo": str(head_repo.get("full_name") or ""),
        "is_autodoc": str(is_autodoc_pr(head_ref, label_names)).lower(),
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pr-json", required=True)
    parser.add_argument("--labels-json", required=True)
    parser.add_argument("--github-output", required=True)
    args = parser.parse_args(argv)

    pr = json.loads(Path(args.pr_json).read_text(encoding="utf-8"))
    labels = json.loads(Path(args.labels_json).read_text(encoding="utf-8"))
    if not isinstance(pr, dict) or not isinstance(labels, list):
        raise SystemExit("Unexpected GitHub metadata shape.")

    outputs = classify_metadata(pr, labels)
    if not all(outputs[key] for key in ("pr", "head_ref", "head_sha", "head_repo")):
        raise SystemExit("Required pull request metadata is missing.")
    with Path(args.github_output).open("a", encoding="utf-8") as handle:
        for key, value in outputs.items():
            handle.write(f"{key}={value}\n")
    print(
        f"PR #{outputs['pr']} head={outputs['head_ref']} "
        f"is_autodoc={outputs['is_autodoc']}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
