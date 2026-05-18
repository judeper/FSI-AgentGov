#!/usr/bin/env python3
"""verify_build_output.py — fail CI on incomplete MkDocs build output.

Why this exists:
  `mkdocs build --strict` catches warnings/errors emitted during the build, but
  it does not assert that the rendered `site/` tree still contains the expected
  route families and search assets. A widened `exclude_docs` pattern or a
  partial artifact/deploy step can therefore exit 0 while omitting large parts
  of the published site.

Usage:
  python scripts/verify_build_output.py
  python scripts/verify_build_output.py site
  python scripts/verify_build_output.py --min-reference-html 20 --min-controls-html 60

Run this immediately after `python -m mkdocs build --strict` (or `mkdocs build
--strict`) so the assertions inspect a fresh `site/` tree.
"""
from __future__ import annotations

import argparse
import sys
from dataclasses import dataclass
from pathlib import Path

DEFAULT_SITE_ROOT = Path("site")
DEFAULT_MIN_REFERENCE_HTML = 20
DEFAULT_MIN_CONTROLS_HTML = 60
DEFAULT_MIN_SEARCH_BYTES = 100_000
DEFAULT_MIN_INDEX_BYTES = 1_024
SEARCH_INDEX_CANDIDATES = (
    Path("search/search_index.json"),
    Path("search/search_index.json.gz"),
)


@dataclass(frozen=True)
class CheckResult:
    """One human-readable post-build assertion result."""

    label: str
    ok: bool
    detail: str


@dataclass(frozen=True)
class Thresholds:
    """Thresholds for required built-site artifacts."""

    min_reference_html: int
    min_controls_html: int
    min_search_bytes: int
    min_index_bytes: int


def count_html(directory: Path) -> int:
    """Return the number of HTML files under a directory tree."""
    if not directory.is_dir():
        return 0
    return sum(1 for _ in directory.rglob("*.html"))


def find_search_index(site_root: Path) -> Path | None:
    """Return the emitted search index asset, if any."""
    for relative_path in SEARCH_INDEX_CANDIDATES:
        candidate = site_root / relative_path
        if candidate.is_file():
            return candidate
    return None


def verify(site_root: Path, thresholds: Thresholds) -> list[CheckResult]:
    """Collect post-build assertions for the rendered site tree."""
    results: list[CheckResult] = []

    index_html = site_root / "index.html"
    if index_html.is_file():
        index_bytes = index_html.stat().st_size
        results.append(CheckResult(
            label="site index",
            ok=index_bytes >= thresholds.min_index_bytes,
            detail=(
                f"expected {index_html} to be at least {thresholds.min_index_bytes} bytes; "
                f"found {index_bytes}"
            ),
        ))
    else:
        results.append(CheckResult(
            label="site index",
            ok=False,
            detail=f"expected {index_html} to exist after the MkDocs build",
        ))

    reference_dir = site_root / "reference"
    reference_html_count = count_html(reference_dir)
    results.append(CheckResult(
        label="reference subtree",
        ok=reference_html_count >= thresholds.min_reference_html,
        detail=(
            f"expected at least {thresholds.min_reference_html} HTML files under {reference_dir}; "
            f"found {reference_html_count}"
        ),
    ))

    controls_dir = site_root / "controls"
    controls_html_count = count_html(controls_dir)
    results.append(CheckResult(
        label="controls subtree",
        ok=controls_html_count >= thresholds.min_controls_html,
        detail=(
            f"expected at least {thresholds.min_controls_html} HTML files under {controls_dir}; "
            f"found {controls_html_count}"
        ),
    ))

    search_index = find_search_index(site_root)
    if search_index is None:
        expected_paths = ", ".join(str(site_root / path) for path in SEARCH_INDEX_CANDIDATES)
        results.append(CheckResult(
            label="search index",
            ok=False,
            detail=(
                "expected a generated search index asset after the MkDocs build; "
                f"looked for {expected_paths}"
            ),
        ))
    else:
        search_bytes = search_index.stat().st_size
        results.append(CheckResult(
            label="search index",
            ok=search_bytes >= thresholds.min_search_bytes,
            detail=(
                f"expected {search_index} to be at least {thresholds.min_search_bytes} bytes; "
                f"found {search_bytes}"
            ),
        ))

    return results


def build_parser() -> argparse.ArgumentParser:
    """Construct the CLI argument parser."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "site_root",
        nargs="?",
        default=DEFAULT_SITE_ROOT,
        type=Path,
        help="Path to the built MkDocs site/ directory (default: site).",
    )
    parser.add_argument(
        "--min-reference-html",
        type=int,
        default=DEFAULT_MIN_REFERENCE_HTML,
        help=(
            "Minimum number of rendered HTML files expected under site/reference/ "
            f"(default: {DEFAULT_MIN_REFERENCE_HTML})."
        ),
    )
    parser.add_argument(
        "--min-controls-html",
        type=int,
        default=DEFAULT_MIN_CONTROLS_HTML,
        help=(
            "Minimum number of rendered HTML files expected under site/controls/ "
            f"(default: {DEFAULT_MIN_CONTROLS_HTML})."
        ),
    )
    parser.add_argument(
        "--min-search-bytes",
        type=int,
        default=DEFAULT_MIN_SEARCH_BYTES,
        help=(
            "Minimum size for site/search/search_index.json (or .json.gz) in bytes "
            f"(default: {DEFAULT_MIN_SEARCH_BYTES})."
        ),
    )
    parser.add_argument(
        "--min-index-bytes",
        type=int,
        default=DEFAULT_MIN_INDEX_BYTES,
        help=(
            "Minimum size for site/index.html in bytes "
            f"(default: {DEFAULT_MIN_INDEX_BYTES})."
        ),
    )
    return parser


def main() -> int:
    """CLI entry point."""
    parser = build_parser()
    args = parser.parse_args()

    if not args.site_root.is_dir():
        print(f"ERROR: built site root not found: {args.site_root}", file=sys.stderr)
        print("Run `python -m mkdocs build --strict` before invoking this verifier.", file=sys.stderr)
        return 2

    thresholds = Thresholds(
        min_reference_html=args.min_reference_html,
        min_controls_html=args.min_controls_html,
        min_search_bytes=args.min_search_bytes,
        min_index_bytes=args.min_index_bytes,
    )
    results = verify(args.site_root, thresholds)
    failures = [result for result in results if not result.ok]

    if failures:
        print("FAIL: built site output assertions failed:", file=sys.stderr)
        for failure in failures:
            print(f"  - {failure.label}: {failure.detail}", file=sys.stderr)
        print(
            "Re-run the MkDocs build and inspect mkdocs.yml exclude_docs/not_in_nav, "
            "workflow artifact handling, or deploy-copy steps.",
            file=sys.stderr,
        )
        return 1

    index_html = args.site_root / "index.html"
    reference_html_count = count_html(args.site_root / "reference")
    controls_html_count = count_html(args.site_root / "controls")
    search_index = find_search_index(args.site_root)
    search_label = search_index.name if search_index else "missing"
    search_bytes = search_index.stat().st_size if search_index else 0
    print(
        "OK: build output verified "
        f"(index.html={index_html.stat().st_size} bytes, "
        f"reference_html={reference_html_count}, "
        f"controls_html={controls_html_count}, "
        f"search_asset={search_label}, "
        f"search_bytes={search_bytes})."
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
