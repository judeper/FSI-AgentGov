"""Validate Markdown fragment links (#anchors) within the docs.

Purpose
- Ensure bookmark-style URLs (page#fragment) are shareable and do not break.
- Catch broken links to missing anchors early in CI/local checks.

Scope
- Checks docs/**/*.md for Markdown links that include a fragment (#...).
- Resolves relative links to other markdown files within docs/.
- Validates that the target file contains the fragment as either:
  - an explicit HTML anchor: <a id="fragment"></a>
  - an explicit heading ID via attr_list: ## Heading {#fragment}
  - an auto-derived heading slug (best-effort) from Markdown headings

Notes
- This is intentionally conservative: it ignores external URLs and links to non-.md assets.
- The slugification is a best-effort approximation of MkDocs' heading IDs; explicit IDs are preferred
  for long-lived, shareable links.
"""

from __future__ import annotations

import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Optional

DOCS_DIR = Path(__file__).resolve().parents[1] / "docs"

# Keep in sync with mkdocs.yml `exclude_docs:`. These directories are not published.
DEFAULT_EXCLUDED_TOP_LEVEL_DIRS = {"images", "scripts", "templates"}


_LINK_RE = re.compile(r"\[[^\]]+\]\(([^)]+)\)")

# HTML anchor: <a id="foo"></a>
_HTML_ID_RE = re.compile(r"<a\s+id=\"([^\"]+)\"\s*></a>", re.IGNORECASE)

# Attr_list heading IDs: ## Title {#foo}
_ATTR_LIST_ID_RE = re.compile(r"\{#([A-Za-z0-9][A-Za-z0-9_-]*)\}\s*$")

# Markdown headings: # / ## / ### ...
_HEADING_RE = re.compile(r"^(#{1,6})\s+(.+?)\s*$")


@dataclass(frozen=True)
class LinkIssue:
    source_file: Path
    source_line: int
    raw_link: str
    target_file: Path
    fragment: str
    reason: str


def _strip_inline_code(text: str) -> str:
    return re.sub(r"`[^`]+`", "", text)


def _slugify_heading(text: str) -> str:
    """Best-effort slugifier for MkDocs-style heading IDs."""
    text = _strip_inline_code(text)
    text = text.strip().lower()

    # Remove common punctuation, keep alphanumerics, spaces, underscores, hyphens.
    text = re.sub(r"[^a-z0-9 _-]", "", text)
    text = text.replace("_", "-")
    text = re.sub(r"\s+", "-", text)
    text = re.sub(r"-+", "-", text).strip("-")
    return text


def _split_link_target(raw: str) -> tuple[str, Optional[str]]:
    """Return (path_part, fragment) where fragment excludes the leading '#'."""
    raw = raw.strip()

    # Drop optional title suffix: (path "title")
    # This is a simple heuristic; we don't attempt full markdown parsing.
    if "\"" in raw:
        raw = raw.split("\"")[0].strip()

    if "#" not in raw:
        return raw, None

    path_part, fragment = raw.split("#", 1)
    fragment = fragment.strip()
    if fragment == "":
        return path_part, None
    return path_part.strip(), fragment


def _is_external_link(path_part: str) -> bool:
    lowered = path_part.lower()
    return lowered.startswith("http://") or lowered.startswith("https://") or lowered.startswith("mailto:")


def _resolve_target_file(source_file: Path, path_part: str) -> Optional[Path]:
    """Resolve a markdown link path into an absolute file path under docs/.

    Returns None for non-markdown or non-docs links.
    """
    path_part = path_part.strip()
    if path_part == "":
        return source_file

    # Ignore external links and pure fragments.
    if _is_external_link(path_part):
        return None

    # Ignore mkdocs-relative paths without extension that are clearly site urls.
    # Example: (getting-started/overview/#foo). We'll map these to docs .md best-effort.
    p = Path(path_part)

    # Strip leading '/' (site-absolute) and treat as docs-relative.
    if str(p).startswith("/"):
        p = Path(str(p).lstrip("/"))

    if p.suffix == "":
        # Heuristic: treat as a docs path pointing to a directory or a markdown file.
        # - If it exists as docs/<p>.md, use it.
        # - Else if docs/<p>/index.md exists, use it.
        candidate_md = (DOCS_DIR / p).with_suffix(".md")
        if candidate_md.exists():
            return candidate_md
        candidate_index = DOCS_DIR / p / "index.md"
        if candidate_index.exists():
            return candidate_index
        return None

    if p.suffix.lower() != ".md":
        return None

    resolved = (source_file.parent / p).resolve()
    try:
        resolved.relative_to(DOCS_DIR)
    except ValueError:
        return None

    return resolved


def _collect_anchors(md_text: str) -> set[str]:
    anchors: set[str] = set()

    for match in _HTML_ID_RE.finditer(md_text):
        anchors.add(match.group(1).strip())

    for line in md_text.splitlines():
        heading_match = _HEADING_RE.match(line)
        if not heading_match:
            continue

        heading_text = heading_match.group(2).strip()

        # If explicit {#id} is present at end, use it and also consider the slug of the visible text.
        id_match = _ATTR_LIST_ID_RE.search(heading_text)
        if id_match:
            anchors.add(id_match.group(1))
            heading_text = _ATTR_LIST_ID_RE.sub("", heading_text).strip()

        slug = _slugify_heading(heading_text)
        if slug:
            anchors.add(slug)

    return anchors


def _iter_markdown_files(
    root: Path,
    *,
    excluded_top_level_dirs: set[str],
) -> Iterable[Path]:
    for path in root.rglob("*.md"):
        rel = path.relative_to(root)
        if rel.parts and rel.parts[0] in excluded_top_level_dirs:
            continue
        yield path


def validate_docs_anchors(
    docs_dir: Path = DOCS_DIR,
    *,
    excluded_top_level_dirs: set[str] | None = None,
) -> list[LinkIssue]:
    issues: list[LinkIssue] = []

    if excluded_top_level_dirs is None:
        excluded_top_level_dirs = set(DEFAULT_EXCLUDED_TOP_LEVEL_DIRS)

    anchor_cache: dict[Path, set[str]] = {}

    for md_file in _iter_markdown_files(docs_dir, excluded_top_level_dirs=excluded_top_level_dirs):
        try:
            content = md_file.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            content = md_file.read_text(encoding="utf-8-sig")

        for i, line in enumerate(content.splitlines(), start=1):
            for link_match in _LINK_RE.finditer(line):
                raw_target = link_match.group(1)
                path_part, fragment = _split_link_target(raw_target)

                if fragment is None:
                    continue

                target_file = _resolve_target_file(md_file, path_part)
                if target_file is None:
                    continue

                if not target_file.exists():
                    issues.append(
                        LinkIssue(
                            source_file=md_file,
                            source_line=i,
                            raw_link=raw_target,
                            target_file=target_file,
                            fragment=fragment,
                            reason="target markdown file does not exist",
                        )
                    )
                    continue

                if target_file not in anchor_cache:
                    try:
                        t = target_file.read_text(encoding="utf-8")
                    except UnicodeDecodeError:
                        t = target_file.read_text(encoding="utf-8-sig")
                    anchor_cache[target_file] = _collect_anchors(t)

                anchors = anchor_cache[target_file]
                if fragment not in anchors:
                    issues.append(
                        LinkIssue(
                            source_file=md_file,
                            source_line=i,
                            raw_link=raw_target,
                            target_file=target_file,
                            fragment=fragment,
                            reason="fragment not found in target (add explicit anchor/id)",
                        )
                    )

    return issues


def main(argv: list[str]) -> int:
    docs_dir = DOCS_DIR
    include_excluded = False

    args = argv[1:]
    if "--include-excluded" in args:
        include_excluded = True
        args = [a for a in args if a != "--include-excluded"]

    if len(args) > 0:
        docs_dir = Path(args[0]).resolve()

    excluded = set() if include_excluded else set(DEFAULT_EXCLUDED_TOP_LEVEL_DIRS)
    issues = validate_docs_anchors(docs_dir, excluded_top_level_dirs=excluded)
    if not issues:
        print("✅ Docs anchor validation passed (no broken #fragments).")
        return 0

    print(f"❌ Docs anchor validation failed: {len(issues)} broken #fragment link(s).")
    for issue in issues:
        src_rel = issue.source_file.relative_to(docs_dir)
        tgt_rel = issue.target_file.relative_to(docs_dir) if issue.target_file.exists() else issue.target_file
        print(f"- {src_rel}:{issue.source_line} -> ({issue.raw_link})")
        print(f"  target: {tgt_rel}#{issue.fragment}")
        print(f"  reason: {issue.reason}")

    return 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
