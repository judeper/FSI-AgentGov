#!/usr/bin/env python3
"""Guard against Playwright container-pin drift.

Workflows that pin a Playwright Docker image
(``container.image: mcr.microsoft.com/playwright:<tag>``) bake in browser
binaries for one specific Playwright version. Those browsers must match the
``@playwright/test`` client version in ``package.json`` exactly, or every test
fails at ``browserType.launch`` — the v1.60.0 image vs v1.61.1 client skew that
silently broke the ``e2e-full`` suite after the Dependabot bump in #583.

Scope (deliberately narrow):

* **Checked:** only ``container.image:`` Playwright pins, discovered dynamically
  across ``.github/workflows/*.yml``. Today that is ``e2e.yml`` and
  ``update-snapshots.yml``; any future pinned workflow is covered automatically.
* **NOT checked:** runtime-install workflows that run ``npx playwright install``
  (``e2e-smoke.yml``, ``prod-smoke.yml``, ``prod-smoke-scheduled.yml``). They pull
  browsers matching the installed client at run time and self-heal.
* **Ignored:** ``@axe-core/playwright`` — a separate package on its own version.

The distro suffix (``-noble`` / ``-jammy`` / ...) is ignored; only the
``vX.Y.Z`` version token is compared.

Run with ``--check`` in CI (wired into the required "manifest / index / nav
drift" job in ``python-quality.yml``) to fail on drift.
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
PACKAGE_JSON = REPO_ROOT / "package.json"
WORKFLOWS_DIR = REPO_ROOT / ".github" / "workflows"

# Matches e.g.  image: mcr.microsoft.com/playwright:v1.61.1-noble
# Captures the version token (optional leading v) and ignores the distro suffix.
# Only the official Playwright image is matched — other container images are
# intentionally left alone.
PIN_RE = re.compile(
    r"image:\s*mcr\.microsoft\.com/playwright:"
    r"v?(?P<version>\d+\.\d+\.\d+)"
    r"(?:-[a-z0-9]+)?",
)


def normalize(version: str) -> str:
    """Strip a leading ``v`` and any npm range prefix for clean comparison."""
    return version.lstrip("v^~=<> ").strip()


def _display(path: Path) -> str:
    try:
        return path.relative_to(REPO_ROOT).as_posix()
    except ValueError:
        return path.name


def expected_version(package_json: Path = PACKAGE_JSON) -> str:
    """Return the pinned ``@playwright/test`` version from package.json.

    Reads the exact ``@playwright/test`` key — NOT ``@axe-core/playwright``,
    which is an unrelated package on its own version line.
    """
    data = json.loads(package_json.read_text(encoding="utf-8"))
    for section in ("devDependencies", "dependencies"):
        deps = data.get(section, {})
        if "@playwright/test" in deps:
            return normalize(deps["@playwright/test"])
    raise SystemExit(
        "ERROR: @playwright/test not found in package.json "
        "dependencies/devDependencies."
    )


def find_container_pins(workflows_dir: Path = WORKFLOWS_DIR):
    """Return ``[(workflow_path, pinned_version), ...]`` for every pin found."""
    pins: list[tuple[Path, str]] = []
    candidates = sorted(workflows_dir.glob("*.yml")) + sorted(
        workflows_dir.glob("*.yaml")
    )
    for wf in candidates:
        for line in wf.read_text(encoding="utf-8").splitlines():
            m = PIN_RE.search(line)
            if m:
                pins.append((wf, normalize(m.group("version"))))
    return pins


def evaluate(expected: str, pins) -> list[str]:
    """Return human-readable drift messages (empty list == in sync)."""
    problems: list[str] = []
    for wf, version in pins:
        if version != expected:
            problems.append(
                f"DRIFT: {_display(wf)} pins Playwright {version} but "
                f"package.json @playwright/test is {expected}"
            )
    return problems


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--check",
        action="store_true",
        help="Exit non-zero on drift (default behavior; flag kept for clarity).",
    )
    parser.parse_args(argv)

    expected = expected_version()
    pins = find_container_pins()

    print(f"Expected Playwright version (@playwright/test): {expected}")
    if not pins:
        print("No Playwright container.image pins found (nothing to check).")
        return 0
    for wf, version in pins:
        print(f"  {_display(wf)}: {version}")
    print()

    problems = evaluate(expected, pins)
    if problems:
        print("\n".join(problems))
        print(
            "\nFAIL: Playwright container pin(s) drift from @playwright/test. "
            "Bump the image tag(s) to match package.json (or pin @playwright/test "
            "to the image version). Runtime-install workflows that run "
            "`npx playwright install` are intentionally not checked."
        )
        return 1

    print(f"OK: all {len(pins)} Playwright container pin(s) match {expected}.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
