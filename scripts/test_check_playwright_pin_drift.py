"""Tests for check_playwright_pin_drift.py — the coupled-pin guard.

These prove the guard closes the #583 class of failure: a Dependabot bump to
``@playwright/test`` that leaves a pinned Playwright ``container.image:`` behind,
silently breaking ``e2e-full`` (skipped on PRs, so invisible at review time).

They also assert the guard's deliberate scope: it ignores the distro suffix,
ignores ``@axe-core/playwright``, and only looks at ``container.image:`` pins
(never runtime-install workflows).
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

# Make scripts/ importable regardless of pytest invocation directory.
SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

import check_playwright_pin_drift as guard  # noqa: E402


def _package_json(path: Path, playwright: str = "1.61.1", axe: str = "4.12.1") -> Path:
    path.write_text(
        json.dumps(
            {
                "devDependencies": {
                    "@axe-core/playwright": axe,
                    "@playwright/test": playwright,
                }
            }
        ),
        encoding="utf-8",
    )
    return path


def _workflow(directory: Path, name: str, body: str) -> Path:
    directory.mkdir(parents=True, exist_ok=True)
    wf = directory / name
    wf.write_text(body, encoding="utf-8")
    return wf


def _container(image: str) -> str:
    return f"jobs:\n  x:\n    container:\n      image: {image}\n"


# -- expected_version --------------------------------------------------------

def test_expected_reads_playwright_test_not_axe(tmp_path: Path) -> None:
    pkg = _package_json(tmp_path / "package.json", playwright="1.61.1", axe="4.12.1")
    assert guard.expected_version(pkg) == "1.61.1"


def test_expected_strips_range_prefix(tmp_path: Path) -> None:
    pkg = _package_json(tmp_path / "package.json", playwright="^1.61.1")
    assert guard.expected_version(pkg) == "1.61.1"


# -- find_container_pins -----------------------------------------------------

def test_finds_container_image_pins(tmp_path: Path) -> None:
    wfdir = tmp_path / "workflows"
    _workflow(wfdir, "e2e.yml", _container("mcr.microsoft.com/playwright:v1.61.1-noble"))
    pins = guard.find_container_pins(wfdir)
    assert [v for _, v in pins] == ["1.61.1"]


def test_runtime_install_workflow_is_not_a_pin(tmp_path: Path) -> None:
    wfdir = tmp_path / "workflows"
    _workflow(
        wfdir,
        "e2e-smoke.yml",
        "jobs:\n  x:\n    steps:\n      - run: npx playwright install --with-deps chromium\n",
    )
    assert guard.find_container_pins(wfdir) == []


def test_non_playwright_image_is_ignored(tmp_path: Path) -> None:
    wfdir = tmp_path / "workflows"
    _workflow(wfdir, "other.yml", _container("node:20-bookworm"))
    assert guard.find_container_pins(wfdir) == []


# -- evaluate ----------------------------------------------------------------

def test_matching_pin_has_no_drift() -> None:
    pins = [(Path("e2e.yml"), "1.61.1")]
    assert guard.evaluate("1.61.1", pins) == []


def test_distro_suffix_is_ignored(tmp_path: Path) -> None:
    wfdir = tmp_path / "workflows"
    _workflow(wfdir, "e2e.yml", _container("mcr.microsoft.com/playwright:v1.61.1-noble"))
    _workflow(
        wfdir, "snap.yml", _container("mcr.microsoft.com/playwright:v1.61.1-jammy")
    )
    pins = guard.find_container_pins(wfdir)
    assert guard.evaluate("1.61.1", pins) == []


def test_drift_is_detected() -> None:
    pins = [(Path("e2e.yml"), "1.60.0"), (Path("snap.yml"), "1.49.0")]
    problems = guard.evaluate("1.61.1", pins)
    assert len(problems) == 2
    assert all("DRIFT" in p for p in problems)


# -- end-to-end on the real repo (keeps the committed repo honest) -----------

def test_repository_pins_are_in_sync() -> None:
    """The committed repo must have no Playwright pin drift.

    This makes a future `@playwright/test` bump that forgets a container image
    fail pytest too, not just the dedicated drift step — defense in depth.
    """
    assert guard.main(["--check"]) == 0
