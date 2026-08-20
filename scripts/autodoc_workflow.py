#!/usr/bin/env python3
"""Trusted helpers used by autodoc pull_request_target workflows."""

from __future__ import annotations

import argparse
import json
import re
from fnmatch import fnmatchcase
from pathlib import Path, PurePosixPath
from typing import Any, Iterable

AUTODOC_BRANCH_PREFIXES = ("autodoc/", "copilot/")
FINGERPRINT_PREFIX = "AUTODOC-FINGERPRINT:"

_FINGERPRINT_RE = re.compile(rf"^{re.escape(FINGERPRINT_PREFIX)}\s*(\S+)\s*$", re.MULTILINE)
_AUTODOC_REPORT_RE = re.compile(r"^AUTODOC-REPORT:\s*(\S+)\s*$", re.MULTILINE)
_SOURCE_REPORT_RE = re.compile(r"^Source report:\s*(\S+)\s*$", re.MULTILINE | re.IGNORECASE)
_AUTODOC_ROUTE_RE = re.compile(r"^AUTODOC-ROUTE:\s*(\S+)\s*$", re.MULTILINE)
_JSON_CONTRACT_RE = re.compile(r"```json\s*(\{.*?\})\s*```", re.DOTALL)


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


def parse_pr_markers(pr_body: str) -> dict[str, str | None]:
    """Extract trusted autodoc markers from a pull request body."""

    body = pr_body or ""
    fingerprint_match = _FINGERPRINT_RE.search(body)
    if not fingerprint_match:
        raise ValueError("PR body is missing AUTODOC-FINGERPRINT.")

    report_match = _AUTODOC_REPORT_RE.search(body) or _SOURCE_REPORT_RE.search(body)
    if not report_match:
        raise ValueError("PR body is missing report marker (AUTODOC-REPORT or Source report).")

    route_match = _AUTODOC_ROUTE_RE.search(body)
    route = route_match.group(1).strip() if route_match else None
    return {
        "fingerprint": fingerprint_match.group(1).strip(),
        "report_path": report_match.group(1).strip(),
        "route": route,
    }


def derive_trusted_contract(pr_body: str, repo_root: str | Path = ".") -> dict[str, Any]:
    """Derive authoritative contract/report/route data from trusted base-branch content."""

    markers = parse_pr_markers(pr_body)
    fingerprint = str(markers["fingerprint"])
    report_path = _validate_report_path(str(markers["report_path"]), repo_root)
    report_file = _repo_path(Path(repo_root), report_path)
    report_text = report_file.read_text(encoding="utf-8")

    specs = _route_specs_for_report(report_text, Path(report_path).name, repo_root)
    matches = [spec for spec in specs if spec.get("fingerprint") == fingerprint]
    if len(matches) != 1:
        raise ValueError(
            f"Trusted routing data did not resolve exactly one contract for fingerprint {fingerprint} "
            f"(matches={len(matches)})."
        )

    spec = matches[0]
    trusted_route = str(spec.get("route") or "").strip()
    if not trusted_route:
        raise ValueError("Trusted routing decision is missing for the resolved fingerprint.")

    hinted_route = str(markers["route"] or "").strip()
    if hinted_route and hinted_route != trusted_route:
        raise ValueError(
            f"PR body AUTODOC-ROUTE {hinted_route!r} does not match trusted route {trusted_route!r}."
        )

    contract = _extract_contract_for_fingerprint(str(spec.get("body") or ""), fingerprint, required=True)
    if str(contract.get("report_path") or "") != report_path:
        raise ValueError(
            f"Trusted contract report_path {contract.get('report_path')!r} does not match marker report_path {report_path!r}."
        )

    supplied_contract = _extract_contract_for_fingerprint(pr_body, fingerprint, required=False)
    if supplied_contract is not None:
        _enforce_not_widened_allowlist(contract, supplied_contract)

    return {
        "fingerprint": fingerprint,
        "report_path": report_path,
        "route": trusted_route,
        "contract": contract,
    }


def preflight_changed_files(changed_files: list[dict[str, Any]], contract: dict[str, Any]) -> list[str]:
    """Validate compare-file metadata against the trusted contract and return fetch paths."""

    allowed = _validated_allowed_list(contract, "trusted")
    forbidden_paths = contract.get("forbidden_paths")
    if not isinstance(forbidden_paths, list) or not all(isinstance(pattern, str) for pattern in forbidden_paths):
        raise ValueError("trusted contract forbidden_paths is malformed.")
    forbidden = [_safe_repo_glob(pattern) for pattern in forbidden_paths]
    fetch_paths: list[str] = []
    preflight_paths: list[str] = []
    failures: list[str] = []

    for item in changed_files:
        if not isinstance(item, dict):
            failures.append("Compare payload entry is not an object.")
            continue
        filename = item.get("filename")
        if not isinstance(filename, str):
            failures.append("Compare payload entry is missing filename.")
            continue
        path = _safe_repo_path(filename)
        fetch_paths.append(path)
        preflight_paths.append(path)

        previous = item.get("previous_filename")
        if isinstance(previous, str) and previous.strip():
            preflight_paths.append(_safe_repo_path(previous))

        status = item.get("status")
        if status not in {"added", "modified"}:
            failures.append(f"{path}: unsupported file status {status}")

    for path in sorted(set(preflight_paths)):
        if not path.endswith(".md"):
            failures.append(f"{path}: only Markdown files may be fetched under pull_request_target")
        if path not in allowed:
            failures.append(f"{path}: not listed in trusted contract allowed_files")
        matched = next((pattern for pattern in forbidden if _matches(path, pattern)), None)
        if matched:
            failures.append(f"{path}: matches forbidden_paths pattern {matched}")

    if failures:
        raise ValueError("Changed-file preflight failed:\n" + "\n".join(failures))
    return fetch_paths


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


def _route_specs_for_report(report_text: str, report_name: str, repo_root: str | Path) -> list[dict[str, Any]]:
    import autodoc_route

    return autodoc_route.route_report(
        report_text,
        report_name,
        {"schema_version": 1, "changes": {}},
        repo_root=repo_root,
    )


def _extract_contract_for_fingerprint(body: str, fingerprint: str, *, required: bool) -> dict[str, Any] | None:
    for match in _JSON_CONTRACT_RE.finditer(body or ""):
        try:
            candidate = json.loads(match.group(1))
        except json.JSONDecodeError:
            continue
        if isinstance(candidate, dict) and str(candidate.get("fingerprint") or "") == fingerprint:
            return candidate

    if required:
        raise ValueError("Contract JSON matching the PR fingerprint was not found.")
    return None


def _enforce_not_widened_allowlist(trusted: dict[str, Any], supplied: dict[str, Any]) -> None:
    supplied_allowed = _validated_allowed_list(supplied, "PR-supplied")
    trusted_allowed = _validated_allowed_list(trusted, "trusted")
    widened = sorted(path for path in supplied_allowed if path not in trusted_allowed)
    if widened:
        raise ValueError(
            "PR-supplied contract widens allowed_files beyond the trusted contract: "
            + ", ".join(widened)
        )


def _validated_allowed_list(contract: dict[str, Any], label: str) -> set[str]:
    allowed = contract.get("allowed_files")
    if not isinstance(allowed, list) or not all(isinstance(path, str) for path in allowed):
        raise ValueError(f"{label} contract allowed_files is malformed.")
    return {_safe_repo_path(path) for path in allowed}


def _validate_report_path(report_path: str, repo_root: str | Path) -> str:
    normalized = _safe_repo_path(report_path)
    if not normalized.startswith("reports/monitoring/"):
        raise ValueError(f"Contract report_path must be under reports/monitoring/: {normalized}")
    if not _repo_path(Path(repo_root), normalized).is_file():
        raise ValueError(f"Contract report_path does not exist on base checkout: {normalized}")
    return normalized


def _repo_path(root: Path, repo_relative_path: str) -> Path:
    return root / Path(*repo_relative_path.split("/"))


def _safe_repo_path(path: str) -> str:
    normalized = path.replace("\\", "/").strip().lstrip("/")
    while normalized.startswith("./"):
        normalized = normalized[2:]
    if not normalized or any(part in {"", ".", ".."} for part in normalized.split("/")):
        raise ValueError(f"Unsafe repository path: {path}")
    return normalized


def _safe_repo_glob(pattern: str) -> str:
    normalized = pattern.replace("\\", "/").strip().lstrip("/")
    while normalized.startswith("./"):
        normalized = normalized[2:]
    if not normalized or any(part in {"", ".", ".."} for part in normalized.split("/")):
        raise ValueError(f"Unsafe repository glob: {pattern}")
    return normalized


def _matches(path: str, pattern: str) -> bool:
    return fnmatchcase(path, pattern) or PurePosixPath(path).match(pattern)


if __name__ == "__main__":
    raise SystemExit(main())
