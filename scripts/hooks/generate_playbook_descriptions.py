"""generate_playbook_descriptions.py — MkDocs hook: per-page meta descriptions for
playbook/control-implementation pages (SEO-02).

All 395 playbook pages previously shared the site-level fallback description
("Governance framework for Microsoft 365 AI agents…"), killing SERP differentiation.
This hook auto-generates a unique, 140–160-char description for each playbook page
that does not already have a ``description:`` key in its front matter.

Description pattern (from SEO audit recommendation):
  "[Verb] Control {ID} ({Name}) {context} — for M365 administrators in US financial services."

Example:
  "Configure Control 1.1 (Restrict Agent Publishing) via the admin portal — step-by-step
   walkthrough for M365 administrators in US financial services."

Source of truth:
- Control ID and name → page.parent.title (nav section, e.g. "1.1 Restrict Agent Publishing")
- Playbook type → filename stem (portal-walkthrough, powershell-setup, etc.)

The hook fires in on_page_markdown, after nav construction (page.parent is set) but
before template rendering, so page.meta['description'] is picked up by the og:description
and twitter:description tags in overrides/main.html.
"""
from __future__ import annotations

import re
from pathlib import Path

# Nav label → description template components.
_PLAYBOOK_TEMPLATES: dict[str, dict[str, str]] = {
    "portal-walkthrough": {
        "verb": "Configure",
        "tail": "via the admin portal — step-by-step walkthrough",
    },
    "powershell-setup": {
        "verb": "Automate",
        "tail": "using PowerShell — step-by-step setup guide",
    },
    "troubleshooting": {
        "verb": "Troubleshoot",
        "tail": "— diagnostic and resolution guide",
    },
    "verification-testing": {
        "verb": "Verify",
        "tail": "— verification and testing checklist",
    },
}
_SUFFIX = "for M365 administrators in US financial services."
_STRIP_TAGS = re.compile(r"<[^>]+>")


def on_page_markdown(markdown: str, *, page, config, files) -> str | None:  # noqa: ARG001
    """Inject auto-generated description into page.meta for control-implementation playbooks."""
    # Only process playbook implementation pages
    if not (
        page.file
        and page.file.src_uri
        and page.file.src_uri.startswith("playbooks/control-implementations/")
    ):
        return None

    # Skip if an explicit description is already set in front matter
    if page.meta.get("description"):
        return None

    # Playbook type from filename stem (e.g. "portal-walkthrough")
    playbook_type = Path(page.file.src_uri).stem

    # Control section title from nav parent (e.g. "1.1 Restrict Agent Publishing")
    parent_title: str = ""
    if page.parent and page.parent.title:
        parent_title = _STRIP_TAGS.sub("", page.parent.title).strip()

    # Split "1.1 Restrict Agent Publishing" → id="1.1", name="Restrict Agent Publishing"
    parts = parent_title.split(" ", 1)
    control_id = parts[0] if parts else ""
    control_name = parts[1] if len(parts) > 1 else ""

    if not control_id:
        return None  # Can't generate a useful description without a control ID

    tmpl = _PLAYBOOK_TEMPLATES.get(playbook_type)
    if tmpl:
        if control_name:
            subject = f"Control {control_id} ({control_name})"
        else:
            subject = f"Control {control_id}"
        description = f"{tmpl['verb']} {subject} {tmpl['tail']} {_SUFFIX}"
    else:
        # Unknown playbook type — generic but still control-unique
        if control_name:
            description = (
                f"Implementation guide for Control {control_id} ({control_name}) "
                f"— {_SUFFIX}"
            )
        else:
            description = f"Implementation guide for Control {control_id} — {_SUFFIX}"

    page.meta["description"] = description
    return None  # Markdown content is unchanged
