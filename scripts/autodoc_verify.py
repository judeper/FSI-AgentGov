"""Deterministic verifier for autonomous documentation PRs.

This module is intentionally pure-stdlib and offline. The pure-function core is
usable from tests and from merge-gate wrappers; the CLI only handles file I/O.
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from dataclasses import asdict, dataclass, field
from fnmatch import fnmatchcase
from pathlib import Path, PurePosixPath
from typing import Any

DEFAULT_MAX_TOTAL_LINES = 120
FINGERPRINT_PREFIX = "AUTODOC-FINGERPRINT:"
REQUIRED_CONTRACT_KEYS = {
    "schema_version",
    "fingerprint",
    "allowed_files",
    "allowed_headings",
    "forbidden_paths",
}

# The independent cross-vendor LLM faithfulness verifier plugs in here from the
# merge-gate wrapper. This deterministic module does not import SDKs or call
# model APIs; an injected callable must return Finding objects.
_LLM_HOOK = None


@dataclass
class HunkChange:
    """Line-level changes within a unified-diff hunk."""

    old_start: int
    old_count: int
    new_start: int
    new_count: int
    added_line_numbers: list[int] = field(default_factory=list)
    removed_line_numbers: list[int] = field(default_factory=list)
    added_lines: list[str] = field(default_factory=list)
    removed_lines: list[str] = field(default_factory=list)


@dataclass
class FileChange:
    """Aggregated changes for one repository-relative path."""

    path: str
    old_path: str | None = None
    added_lines: list[str] = field(default_factory=list)
    removed_lines: list[str] = field(default_factory=list)
    added_line_numbers: list[int] = field(default_factory=list)
    removed_line_numbers: list[int] = field(default_factory=list)
    hunks: list[HunkChange] = field(default_factory=list)


@dataclass
class Finding:
    """Verifier finding."""

    check: str
    severity: str
    path: str
    message: str

    def __post_init__(self) -> None:
        if self.severity not in {"block", "warn"}:
            raise ValueError(f"Unsupported finding severity: {self.severity}")


def load_contract(path_or_dict: str | Path | dict[str, Any]) -> dict[str, Any]:
    """Load and validate an authoring contract."""

    if isinstance(path_or_dict, dict):
        contract = dict(path_or_dict)
    else:
        path = Path(path_or_dict)
        try:
            contract = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            raise ValueError(f"Contract is not valid JSON: {path}") from exc
        except OSError as exc:
            raise ValueError(f"Unable to read contract: {path}") from exc

    if not isinstance(contract, dict):
        raise ValueError("Contract must be a JSON object")

    missing = sorted(REQUIRED_CONTRACT_KEYS - set(contract))
    if missing:
        raise ValueError(f"Contract missing required key(s): {', '.join(missing)}")

    if contract["schema_version"] != 1:
        raise ValueError("Contract schema_version must be 1")

    _require_string(contract, "fingerprint")
    _require_string_list(contract, "allowed_files")
    _require_string_list(contract, "allowed_headings")
    _require_string_list(contract, "forbidden_paths")
    return contract


def parse_unified_diff(diff_text: str) -> dict[str, FileChange]:
    """Parse standard ``git diff`` unified text into FileChange objects."""

    changes: dict[str, FileChange] = {}
    current: FileChange | None = None
    current_key: str | None = None
    current_hunk: HunkChange | None = None
    old_line = 0
    new_line = 0

    for raw_line in diff_text.splitlines():
        if raw_line.startswith("diff --git "):
            old_path, new_path = _parse_diff_git_paths(raw_line)
            path = new_path if new_path != "/dev/null" else old_path
            current = FileChange(path=path, old_path=old_path)
            current_key = path
            changes[current_key] = current
            current_hunk = None
            continue

        if current is None:
            continue

        if raw_line.startswith("--- "):
            old = _clean_diff_path(raw_line[4:].strip())
            current.old_path = None if old == "/dev/null" else old
            continue

        if raw_line.startswith("+++ "):
            new = _clean_diff_path(raw_line[4:].strip())
            if new != "/dev/null" and new != current.path:
                if current_key is not None:
                    changes.pop(current_key, None)
                current.path = new
                current_key = new
                changes[current_key] = current
            continue

        hunk_match = re.match(r"^@@ -(\d+)(?:,(\d+))? \+(\d+)(?:,(\d+))? @@", raw_line)
        if hunk_match:
            old_start = int(hunk_match.group(1))
            old_count = int(hunk_match.group(2) or "1")
            new_start = int(hunk_match.group(3))
            new_count = int(hunk_match.group(4) or "1")
            current_hunk = HunkChange(
                old_start=old_start,
                old_count=old_count,
                new_start=new_start,
                new_count=new_count,
            )
            current.hunks.append(current_hunk)
            old_line = old_start
            new_line = new_start
            continue

        if current_hunk is None:
            continue

        if raw_line.startswith("+") and not raw_line.startswith("+++"):
            text = raw_line[1:]
            current.added_lines.append(text)
            current.added_line_numbers.append(new_line)
            current_hunk.added_lines.append(text)
            current_hunk.added_line_numbers.append(new_line)
            new_line += 1
        elif raw_line.startswith("-") and not raw_line.startswith("---"):
            text = raw_line[1:]
            current.removed_lines.append(text)
            current.removed_line_numbers.append(old_line)
            current_hunk.removed_lines.append(text)
            current_hunk.removed_line_numbers.append(old_line)
            old_line += 1
        elif raw_line.startswith(" "):
            old_line += 1
            new_line += 1
        elif raw_line.startswith("\\"):
            continue

    return changes


def check_fingerprint(contract: dict[str, Any], pr_body: str | None) -> list[Finding]:
    """Require a contract fingerprint and, when provided, the same PR-body marker."""

    fingerprint = contract.get("fingerprint")
    if not isinstance(fingerprint, str) or not fingerprint.strip():
        return [
            Finding(
                check="fingerprint",
                severity="block",
                path="",
                message="Contract fingerprint is missing or empty.",
            )
        ]

    if pr_body is not None:
        expected = f"{FINGERPRINT_PREFIX} {fingerprint}"
        if expected not in pr_body:
            return [
                Finding(
                    check="fingerprint",
                    severity="block",
                    path="",
                    message=f"PR body does not contain required marker: {expected}",
                )
            ]

    return []


def check_path_allowlist(changed_paths: list[str], contract: dict[str, Any]) -> list[Finding]:
    """Block any changed path outside the contract allowlist or inside forbidden globs."""

    findings: list[Finding] = []
    allowed = {_normalize_repo_path(path) for path in contract.get("allowed_files", [])}
    forbidden = [_normalize_repo_glob(pattern) for pattern in contract.get("forbidden_paths", [])]

    for path in sorted({_normalize_repo_path(changed_path) for changed_path in changed_paths}):
        if path not in allowed:
            findings.append(
                Finding(
                    check="path_allowlist",
                    severity="block",
                    path=path,
                    message="Changed path is not listed in contract allowed_files.",
                )
            )

        matched_pattern = next((pattern for pattern in forbidden if _matches_glob(path, pattern)), None)
        if matched_pattern:
            findings.append(
                Finding(
                    check="path_allowlist",
                    severity="block",
                    path=path,
                    message=f"Changed path matches forbidden_paths pattern: {matched_pattern}",
                )
            )

    return findings


def check_diff_minimality(
    file_changes: dict[str, FileChange],
    contract: dict[str, Any],
    max_total_lines: int = DEFAULT_MAX_TOTAL_LINES,
    max_files: int | None = None,
) -> list[Finding]:
    """Block mass rewrites by changed-file and changed-line thresholds."""

    findings: list[Finding] = []
    file_limit = max_files if max_files is not None else len(contract.get("allowed_files", []))
    total_lines = sum(len(change.added_lines) + len(change.removed_lines) for change in file_changes.values())

    if len(file_changes) > file_limit:
        findings.append(
            Finding(
                check="diff_minimality",
                severity="block",
                path="",
                message=f"Changed file count {len(file_changes)} exceeds allowed limit {file_limit}.",
            )
        )

    if total_lines > max_total_lines:
        findings.append(
            Finding(
                check="diff_minimality",
                severity="block",
                path="",
                message=f"Changed line count {total_lines} exceeds limit {max_total_lines}.",
            )
        )

    return findings


def check_section_allowlist(
    file_contents: dict[str, str],
    file_changes: dict[str, FileChange],
    contract: dict[str, Any],
) -> list[Finding]:
    """Require every added line to live under an allowed Markdown heading."""

    findings: list[Finding] = []
    allowed_headings = {heading.strip() for heading in contract.get("allowed_headings", [])}
    normalized_contents = {_normalize_repo_path(path): content for path, content in file_contents.items()}

    for path, change in sorted(file_changes.items()):
        normalized_path = _normalize_repo_path(path)
        content = normalized_contents.get(normalized_path)
        if content is None:
            findings.append(
                Finding(
                    check="section_allowlist",
                    severity="block",
                    path=normalized_path,
                    message="Post-edit file content was not provided for changed path.",
                )
            )
            continue

        lines = content.splitlines()
        heading_by_line = _heading_lookup(lines)
        if len(change.added_line_numbers) != len(change.added_lines):
            findings.append(
                Finding(
                    check="section_allowlist",
                    severity="block",
                    path=normalized_path,
                    message="Diff parser did not provide one post-edit line number per added line.",
                )
            )
            continue

        for line_number, added_line in zip(change.added_line_numbers, change.added_lines, strict=False):
            heading = _nearest_heading(heading_by_line, line_number)
            if heading is None:
                findings.append(
                    Finding(
                        check="section_allowlist",
                        severity="block",
                        path=normalized_path,
                        message=f"Added line {line_number} has no preceding Markdown heading.",
                    )
                )
                continue
            if heading not in allowed_headings:
                snippet = added_line.strip()
                if len(snippet) > 80:
                    snippet = f"{snippet[:77]}..."
                findings.append(
                    Finding(
                        check="section_allowlist",
                        severity="block",
                        path=normalized_path,
                        message=(
                            f"Added line {line_number} is under heading '{heading}', "
                            f"which is not in allowed_headings. Line: {snippet}"
                        ),
                    )
                )

    return findings


def check_language(changed_md_paths: list[str], repo_root: str | Path) -> list[Finding]:
    """Run the repository FSI language linter against changed Markdown files."""

    md_paths = [_normalize_repo_path(path) for path in changed_md_paths if _normalize_repo_path(path).endswith(".md")]
    if not md_paths:
        return []

    repo_root_path = Path(repo_root)
    script_path = repo_root_path / "scripts" / "verify_language_rules.py"
    if not script_path.exists():
        return [
            Finding(
                check="language",
                severity="block",
                path="",
                message="scripts\\verify_language_rules.py was not found under repo_root.",
            )
        ]

    cmd = [sys.executable, str(script_path), *[_to_os_relative_path(path) for path in md_paths]]
    result = subprocess.run(
        cmd,
        cwd=repo_root_path,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        check=False,
    )
    if result.returncode == 0:
        return []

    return _parse_language_linter_output(result.stdout, result.stderr)


def check_claim_support(added_lines: list[str], report_text: str) -> list[Finding]:
    """Block added factual claims that lack support in the source report."""

    findings: list[Finding] = []
    normalized_report = _normalize_text(report_text)
    report_tokens = set(_meaningful_tokens(report_text))

    for index, raw_line in enumerate(added_lines, start=1):
        line = _strip_diff_marker(raw_line).strip()
        if not line:
            continue

        markers = _factual_markers(line)
        if not markers:
            continue

        if _claim_supported(line, markers, normalized_report, report_tokens):
            continue

        findings.append(
            Finding(
                check="claim_support",
                severity="block",
                path="",
                message=f"Added factual line {index} lacks support in source report: {line}",
            )
        )

    return findings


def verify(
    contract: str | Path | dict[str, Any],
    diff_text: str,
    file_contents: dict[str, str],
    report_text: str,
    pr_body: str | None = None,
    repo_root: str | Path = ".",
) -> dict[str, Any]:
    """Run all deterministic checks and return a JSON-serializable verdict."""

    loaded_contract = load_contract(contract)
    file_changes = parse_unified_diff(diff_text)
    changed_paths = list(file_changes)
    added_lines = [line for change in file_changes.values() for line in change.added_lines]
    removed_lines = [line for change in file_changes.values() for line in change.removed_lines]

    findings: list[Finding] = []
    findings.extend(check_fingerprint(loaded_contract, pr_body))
    findings.extend(check_path_allowlist(changed_paths, loaded_contract))
    findings.extend(check_diff_minimality(file_changes, loaded_contract))
    findings.extend(check_section_allowlist(file_contents, file_changes, loaded_contract))
    findings.extend(check_claim_support(added_lines, report_text))
    findings.extend(check_language([path for path in changed_paths if path.endswith(".md")], repo_root))

    if _LLM_HOOK is not None:
        findings.extend(_LLM_HOOK(loaded_contract, diff_text, file_contents, report_text, pr_body))

    block_count = sum(1 for finding in findings if finding.severity == "block")
    warn_count = sum(1 for finding in findings if finding.severity == "warn")
    return {
        "pass": block_count == 0,
        "findings": [asdict(finding) for finding in findings],
        "summary": {
            "changed_files": len(file_changes),
            "changed_paths": changed_paths,
            "added_lines": len(added_lines),
            "removed_lines": len(removed_lines),
            "block_findings": block_count,
            "warn_findings": warn_count,
        },
    }


def main(argv: list[str] | None = None) -> int:
    """CLI entry point."""

    parser = argparse.ArgumentParser(description="Verify an autonomous documentation PR diff.")
    parser.add_argument("--contract", required=True, help="Path to authoring contract JSON.")
    parser.add_argument("--report", required=True, help="Path to source monitoring report.")
    parser.add_argument("--diff", required=True, help="Path to unified diff, or '-' for stdin.")
    parser.add_argument("--head-dir", default=".", help="Directory containing post-edit file contents.")
    parser.add_argument("--pr-body", help="Optional path to PR body text.")
    parser.add_argument("--json", required=True, help="Output path for verdict JSON.")
    args = parser.parse_args(argv)

    diff_text = sys.stdin.read() if args.diff == "-" else Path(args.diff).read_text(encoding="utf-8")
    report_text = Path(args.report).read_text(encoding="utf-8")
    pr_body = Path(args.pr_body).read_text(encoding="utf-8") if args.pr_body else None
    head_dir = Path(args.head_dir)

    file_contents = _read_post_edit_contents(head_dir, parse_unified_diff(diff_text))
    verdict = verify(
        contract=args.contract,
        diff_text=diff_text,
        file_contents=file_contents,
        report_text=report_text,
        pr_body=pr_body,
        repo_root=head_dir,
    )

    output_path = Path(args.json)
    if output_path.parent != Path("."):
        output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(verdict, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    _print_summary(verdict)
    return 0 if verdict["pass"] else 1


def _require_string(contract: dict[str, Any], key: str) -> None:
    if not isinstance(contract.get(key), str):
        raise ValueError(f"Contract key '{key}' must be a string")


def _require_string_list(contract: dict[str, Any], key: str) -> None:
    value = contract.get(key)
    if not isinstance(value, list) or not all(isinstance(item, str) for item in value):
        raise ValueError(f"Contract key '{key}' must be a list of strings")


def _parse_diff_git_paths(line: str) -> tuple[str, str]:
    parts = line.split()
    if len(parts) < 4:
        return "", ""
    return _clean_diff_path(parts[2]), _clean_diff_path(parts[3])


def _clean_diff_path(raw_path: str) -> str:
    cleaned = raw_path.strip().strip('"')
    if cleaned == "/dev/null":
        return cleaned
    if cleaned.startswith("a/") or cleaned.startswith("b/"):
        cleaned = cleaned[2:]
    return _normalize_repo_path(cleaned)


def _normalize_repo_path(path: str) -> str:
    normalized = path.replace("\\", "/").strip()
    while normalized.startswith("./"):
        normalized = normalized[2:]
    return normalized


def _normalize_repo_glob(pattern: str) -> str:
    return _normalize_repo_path(pattern)


def _matches_glob(path: str, pattern: str) -> bool:
    return fnmatchcase(path, pattern) or PurePosixPath(path).match(pattern)


def _heading_lookup(lines: list[str]) -> dict[int, str]:
    headings: dict[int, str] = {}
    for index, line in enumerate(lines, start=1):
        match = re.match(r"^(#{1,6})\s+(.+?)\s*#*\s*$", line)
        if match:
            headings[index] = match.group(2).strip()
    return headings


def _nearest_heading(heading_by_line: dict[int, str], line_number: int) -> str | None:
    candidates = [heading_line for heading_line in heading_by_line if heading_line <= line_number]
    if not candidates:
        return None
    return heading_by_line[max(candidates)]


def _to_os_relative_path(path: str) -> str:
    return str(Path(*_normalize_repo_path(path).split("/")))


def _parse_language_linter_output(stdout: str, stderr: str) -> list[Finding]:
    findings: list[Finding] = []
    lines = (stdout + "\n" + stderr).splitlines()
    current_path = ""
    index = 0
    while index < len(lines):
        line = lines[index]
        if line.startswith("❌ "):
            current_path = line[2:].strip().split(" [", 1)[0].strip()
        stripped = line.strip()
        if stripped.startswith("Line "):
            detail = stripped
            if index + 1 < len(lines) and lines[index + 1].strip().startswith(">"):
                detail = f"{detail} {lines[index + 1].strip()}"
            findings.append(
                Finding(
                    check="language",
                    severity="block",
                    path=_normalize_repo_path(current_path),
                    message=detail,
                )
            )
        index += 1

    if findings:
        return findings

    output = (stdout + "\n" + stderr).strip()
    if len(output) > 800:
        output = f"{output[:797]}..."
    return [
        Finding(
            check="language",
            severity="block",
            path="",
            message=output or "FSI language linter failed without output.",
        )
    ]


def _strip_diff_marker(line: str) -> str:
    if line.startswith("+") and not line.startswith("+++"):
        return line[1:]
    return line


def _normalize_text(text: str) -> str:
    return re.sub(r"\s+", " ", text.casefold()).strip()


def _factual_markers(line: str) -> list[str]:
    markers: list[str] = []
    occupied_spans: list[tuple[int, int]] = []
    prioritized_patterns = [
        r"\b\d{4}-\d{2}-\d{2}\b",
        r"\b(?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{4}\b",
    ]
    marker_patterns = [
        r"\bpreview\b",
        r"\bGA\b",
        r"\bgenerally available\b",
        r"\bdeprecated\b",
        r"\bretired\b",
        r"\bmust\b",
        r"\brequired\b",
        r"\bretention\b",
        r"\blicen[cs]e\b",
        r"\bSKU\b",
        r"\b[AEFG]\d\b",
    ]

    for pattern in prioritized_patterns:
        for match in re.finditer(pattern, line, flags=re.IGNORECASE):
            markers.append(match.group(0))
            occupied_spans.append(match.span())

    for match in re.finditer(r"\b\d+(?:\.\d+)?%?\b", line, flags=re.IGNORECASE):
        if not any(start <= match.start() < end for start, end in occupied_spans):
            markers.append(match.group(0))

    for pattern in marker_patterns:
        for match in re.finditer(pattern, line, flags=re.IGNORECASE):
            markers.append(match.group(0))
    return markers


def _claim_supported(
    line: str,
    markers: list[str],
    normalized_report: str,
    report_tokens: set[str],
) -> bool:
    for marker in markers:
        normalized_marker = _normalize_text(marker)
        if _is_specific_marker(marker) and normalized_marker in normalized_report:
            return True

    line_tokens = _meaningful_tokens(line)
    if len(line_tokens) < 3:
        return False

    overlap = sum(1 for token in line_tokens if token in report_tokens)
    return overlap / len(line_tokens) >= 0.55


def _is_specific_marker(marker: str) -> bool:
    return bool(
        re.search(r"\d", marker)
        or re.fullmatch(r"\bGA\b", marker, flags=re.IGNORECASE)
        or re.search(r"\bgenerally available\b", marker, flags=re.IGNORECASE)
        or re.fullmatch(r"\b(?:preview|deprecated|retired|retention|licen[cs]e|SKU)\b", marker, flags=re.IGNORECASE)
    )


def _meaningful_tokens(text: str) -> list[str]:
    stopwords = {
        "and",
        "are",
        "for",
        "from",
        "has",
        "have",
        "into",
        "not",
        "the",
        "this",
        "that",
        "with",
        "you",
        "your",
    }
    tokens = re.findall(r"[A-Za-z0-9][A-Za-z0-9-]*", text.casefold())
    return [token for token in tokens if len(token) >= 3 and token not in stopwords]


def _read_post_edit_contents(head_dir: Path, file_changes: dict[str, FileChange]) -> dict[str, str]:
    contents: dict[str, str] = {}
    for path in file_changes:
        if not _is_safe_relative_path(path):
            continue
        target = head_dir / _to_os_relative_path(path)
        try:
            contents[_normalize_repo_path(path)] = target.read_text(encoding="utf-8")
        except OSError:
            continue
    return contents


def _is_safe_relative_path(path: str) -> bool:
    normalized = _normalize_repo_path(path)
    if not normalized or normalized.startswith("/"):
        return False
    return all(part not in {"", ".", ".."} for part in normalized.split("/"))


def _print_summary(verdict: dict[str, Any]) -> None:
    status = "PASS" if verdict["pass"] else "FAIL"
    summary = verdict["summary"]
    print(f"Autodoc verification: {status}")
    print(
        f"Changed files: {summary['changed_files']} | "
        f"Added lines: {summary['added_lines']} | Removed lines: {summary['removed_lines']} | "
        f"Blocks: {summary['block_findings']} | Warnings: {summary['warn_findings']}"
    )
    for finding in verdict["findings"]:
        print(f"- [{finding['severity']}] {finding['check']} {finding['path']}: {finding['message']}")


if __name__ == "__main__":
    sys.exit(main())
