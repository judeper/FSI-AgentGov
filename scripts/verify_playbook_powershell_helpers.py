#!/usr/bin/env python3
"""Validate callable integrity for runnable PowerShell artifacts in playbooks."""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

DOC_PATH = Path("docs/playbooks/control-implementations/1.12/powershell-setup.md")
RUNBOOK_MARKER = "# Save as: scripts/Invoke-Agt112Sweep.ps1"
FENCE_RE = re.compile(r"```powershell\s*\n(.*?)\n```", re.IGNORECASE | re.DOTALL)
FUNCTION_RE = re.compile(r"(?mi)^\s*function\s+([A-Za-z_][\w-]*)\s*\{")
HELPER_CALL_RE = re.compile(r"\b(?:Get|Set|Test|Write)-Fsi[A-Za-z0-9-]*\b")
MANDATORY_PARAM_RE = re.compile(
    r"\[Parameter\(\s*Mandatory(?:\s*=\s*\$true)?\s*\)\]\s*(?:\[[^\]]+\]\s*)*\$(\w+)",
    re.IGNORECASE | re.DOTALL,
)


def _extract_powershell_fences(markdown: str) -> list[str]:
    return FENCE_RE.findall(markdown)


def _extract_runbook_fence(markdown: str, marker: str = RUNBOOK_MARKER) -> str:
    for fence in _extract_powershell_fences(markdown):
        if marker in fence:
            return fence
    raise ValueError(f"Could not locate runbook code fence containing marker: {marker}")


def _extract_defined_functions(markdown: str) -> dict[str, set[str]]:
    definitions: dict[str, set[str]] = {}
    for fence in _extract_powershell_fences(markdown):
        matches = list(FUNCTION_RE.finditer(fence))
        for idx, match in enumerate(matches):
            name = match.group(1)
            body_start = match.end()
            body_end = matches[idx + 1].start() if idx + 1 < len(matches) else len(fence)
            body = fence[body_start:body_end]
            mandatory = {m.group(1) for m in MANDATORY_PARAM_RE.finditer(body)}
            definitions[name] = mandatory
    return definitions


def _logical_lines(script: str) -> list[str]:
    logical: list[str] = []
    current = ""
    for raw in script.splitlines():
        stripped = raw.strip()
        if not stripped:
            if current:
                logical.append(current.strip())
                current = ""
            continue
        if stripped.endswith("`"):
            current += stripped[:-1] + " "
            continue
        current += stripped
        logical.append(current.strip())
        current = ""
    if current:
        logical.append(current.strip())
    return logical


def _extract_runbook_calls(runbook_script: str) -> dict[str, list[str]]:
    calls: dict[str, list[str]] = {}
    for line in _logical_lines(runbook_script):
        for match in HELPER_CALL_RE.finditer(line):
            name = match.group(0)
            argument_slice = line[match.end():]
            calls.setdefault(name, []).append(argument_slice)
    return calls


def validate_markdown_callable_integrity(markdown: str) -> list[str]:
    errors: list[str] = []
    definitions = _extract_defined_functions(markdown)
    runbook = _extract_runbook_fence(markdown)
    calls = _extract_runbook_calls(runbook)
    externally_supplied_helpers = {"Write-FsiEvidence"}

    required_runbook_helpers = {"Get-FsiIrmPolicyEvidenceStatus"}
    missing_required = sorted(required_runbook_helpers - set(calls))
    if missing_required:
        errors.append(f"runbook missing required helper invocation(s): {', '.join(missing_required)}")

    undefined = sorted(
        name for name in calls if name not in definitions and name not in externally_supplied_helpers
    )
    if undefined:
        errors.append(f"runbook references undefined helper(s): {', '.join(undefined)}")

    for helper_name, arg_slices in calls.items():
        mandatory = definitions.get(helper_name, set())
        if not mandatory:
            continue
        for invocation_index, args in enumerate(arg_slices, start=1):
            missing = sorted(param for param in mandatory if f"-{param}" not in args)
            if missing:
                errors.append(
                    f"{helper_name} invocation #{invocation_index} missing mandatory "
                    f"parameter(s): {', '.join(missing)}"
                )

    return errors


def validate_file(path: Path) -> list[str]:
    content = path.read_text(encoding="utf-8")
    return validate_markdown_callable_integrity(content)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--path",
        type=Path,
        default=DOC_PATH,
        help=f"Path to markdown file to validate (default: {DOC_PATH})",
    )
    args = parser.parse_args(argv)

    if not args.path.exists():
        print(f"FAIL: markdown file not found: {args.path}")
        return 2

    errors = validate_file(args.path)
    if errors:
        print(f"FAIL: {args.path}")
        for err in errors:
            print(f"  - {err}")
        return 1

    print(f"PASS: {args.path} callable integrity is valid")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
