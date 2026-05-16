"""Generate per-role pre-session homework pages from the unified manifest.

Auto-generates one MkDocs page per administrator role under
`docs/assessment/pre-session/<role-slug>/index.md`, listing the controls
that role owns from `assessment/manifest/controls.json`.

Usage:
    python scripts/generate_homework_pages.py

Wire-up as MkDocs hook in mkdocs.yml:
    hooks:
      - scripts/hooks/generate_homework_pages_hook.py
"""
from __future__ import annotations

import json
import logging
import re
from collections import defaultdict
from pathlib import Path
from typing import Any

log = logging.getLogger("mkdocs.generate_homework_pages")

REPO_ROOT = Path(__file__).resolve().parents[1]
MANIFEST_PATH = REPO_ROOT / "assessment" / "manifest" / "controls.json"
OUTPUT_DIR = REPO_ROOT / "docs" / "assessment" / "pre-session"


def slugify(text: str) -> str:
    """Convert role name to URL-safe slug.
    
    Example: "Power Platform Admin" -> "power-platform-admin"
    """
    # Convert to lowercase
    slug = text.lower()
    # Replace non-alphanumeric with hyphens
    slug = re.sub(r'[^a-z0-9]+', '-', slug)
    # Strip leading/trailing hyphens
    slug = slug.strip('-')
    return slug


def is_todo_role(role: str) -> bool:
    """Check if role is a TODO placeholder."""
    return role.startswith("TODO:") or "TODO" in role


def group_controls_by_role(controls: list[dict[str, Any]]) -> dict[str, list[dict[str, Any]]]:
    """Group controls by role ownership.
    
    Returns:
        Dict mapping role name to list of controls that role owns.
    """
    role_controls = defaultdict(list)
    todo_roles = set()
    
    for control in controls:
        roles = control.get("roles", [])
        for role in roles:
            if is_todo_role(role):
                todo_roles.add(role)
                continue
            role_controls[role].append(control)
    
    if todo_roles:
        log.warning(
            f"Skipped {len(todo_roles)} TODO role(s): "
            + ", ".join(sorted(todo_roles))
        )
    
    return dict(role_controls)


def _to_relative(url: str, *, markdown_source: bool = False) -> str:
    """Convert manifest site-root URLs to paths relative to homework pages.

    When ``markdown_source`` is true, convert directory-style site URLs to the
    corresponding ``.md`` source path so MkDocs recognizes the link during
    source validation. Keep directory-style paths for destinations that are
    intentionally authored that way (for example playbook walkthrough links).
    External and fragment URLs are unchanged.
    """
    if not url or not isinstance(url, str):
        return "#"
    if url.startswith(("http://", "https://", "#", "mailto:")):
        return url
    if url.startswith("/"):
        relative = "../../.." + url
        if markdown_source and relative.endswith("/"):
            return relative[:-1] + ".md"
        return relative
    return url


def format_control_section(control: dict[str, Any]) -> str:
    """Format a single control for the homework page."""
    lines = []
    
    # Header
    control_id = control.get("id", "Unknown")
    control_name = control.get("name", control.get("title", "Untitled"))
    lines = [f"## Control {control_id} — {control_name}", ""]
    
    # Badges
    pillar_name = control.get("pillar_name", f"Pillar {control.get('pillar', '?')}")
    zones = control.get("zonesApplicable", [])
    zone_str = ", ".join(f"Zone {z}" for z in sorted(zones))
    lines.append(f"**{pillar_name}** · {zone_str}")
    lines.append("")
    
    # Pass criteria (skip if TODO)
    yes_bar = control.get("yesBar", "")
    if yes_bar and not yes_bar.startswith("TODO:"):
        lines.append(f"**Pass criteria:** {yes_bar}")
        lines.append("")
    
    # Verify in (portal links)
    verify_in = control.get("verifyIn", [])
    if verify_in:
        lines.append("**Verify in:**")
        lines.append("")
        for portal_info in verify_in:
            portal = portal_info.get("portal", "Unknown Portal")
            path = portal_info.get("path", "")
            url = _to_relative(portal_info.get("url", "#"))
            lines.append(f"- [{portal} — {path}]({url})")
        lines.append("")
    else:
        control_doc_url = _to_relative(
            control.get("controlDocUrl", "#"),
            markdown_source=True,
        )
        lines.append(f"**Verify in:** *See [control documentation]({control_doc_url}).*")
        lines.append("")
    
    # PowerShell verification
    verify_ps = control.get("verifyPowerShell", "").strip()
    if verify_ps:
        lines.append("**PowerShell:**")
        lines.append("")
        lines.append("```powershell")
        lines.append(verify_ps)
        lines.append("```")
        lines.append("")
    
    # Evidence expected
    evidence = control.get("evidenceExpected", [])
    if evidence:
        lines.append("**Evidence to bring:**")
        lines.append("")
        for item in evidence:
            lines.append(f"- {item}")
        lines.append("")
    
    # Footer links
    control_doc_url = _to_relative(
        control.get("controlDocUrl", "#"),
        markdown_source=True,
    )
    portal_playbook_url = _to_relative(
        control.get("portalPlaybookUrl", "#"),
        markdown_source=True,
    )
    lines.append(
        f"[Full control documentation]({control_doc_url}) · "
        f"[Portal walkthrough]({portal_playbook_url})"
    )
    lines.append("")
    
    return "\n".join(lines)


def generate_homework_page(
    role: str,
    controls: list[dict[str, Any]],
    output_path: Path,
) -> None:
    """Generate a single homework page for a role."""
    lines = []
    
    # Title
    lines.append(f"# Pre-Session Homework: {role}")
    lines.append("")
    
    # Intro
    lines.append(
        f"This page lists the {len(controls)} control(s) you are responsible for "
        f"as **{role}**. Please review each control and bring the requested "
        f"evidence to your assessment session."
    )
    lines.append("")
    lines.append(
        "For the full assessment experience, see the "
        "[Readiness Assessment](../../index.md)."
    )
    lines.append("")
    lines.append("---")
    lines.append("")
    
    # Sort controls by ID
    sorted_controls = sorted(controls, key=lambda c: c.get("id", ""))
    
    # Control sections
    for control in sorted_controls:
        lines.append(format_control_section(control))
    
    # Footer
    lines.append("---")
    lines.append("")
    lines.append(
        "*Generated from `assessment/manifest/controls.json` by "
        "`scripts/generate_homework_pages.py`. Edit the manifest, then re-run.*"
    )
    
    # Write file
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text("\n".join(lines), encoding="utf-8")
    log.info(f"Generated homework page: {output_path.relative_to(REPO_ROOT)}")


def generate_all_homework_pages() -> dict[str, int]:
    """Generate all homework pages from the manifest.
    
    Returns:
        Dict mapping role name to control count.
    """
    # Load manifest
    if not MANIFEST_PATH.exists():
        log.error(f"Manifest not found: {MANIFEST_PATH}")
        return {}
    
    with open(MANIFEST_PATH, encoding="utf-8") as f:
        controls = json.load(f)
    
    log.info(f"Loaded {len(controls)} controls from manifest")
    
    # Group by role
    role_controls = group_controls_by_role(controls)
    log.info(f"Found {len(role_controls)} unique roles")
    
    # Generate pages
    role_stats = {}
    for role, role_control_list in sorted(role_controls.items()):
        slug = slugify(role)
        output_path = OUTPUT_DIR / slug / "index.md"
        generate_homework_page(role, role_control_list, output_path)
        role_stats[role] = len(role_control_list)
    
    log.info(f"Generated {len(role_stats)} homework pages")
    return role_stats


def main():
    """CLI entry point."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(levelname)s: %(message)s",
    )
    
    role_stats = generate_all_homework_pages()
    
    if role_stats:
        print("\n[OK] Generated homework pages:")
        for role, count in sorted(role_stats.items()):
            slug = slugify(role)
            print(f"  {slug:50s} {count:2d} controls  ({role})")
    else:
        print("[ERROR] No homework pages generated")
        return 1
    
    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main())
