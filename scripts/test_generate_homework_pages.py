"""Tests for generate_homework_pages.py."""
from __future__ import annotations

import sys
from pathlib import Path

# Make scripts/ importable regardless of pytest invocation directory.
SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

import generate_homework_pages  # noqa: E402


def test_format_control_section_uses_markdown_source_for_control_docs() -> None:
    control = {
        "id": "1.15",
        "name": "Encryption Data in Transit and at Rest",
        "pillar_name": "Security",
        "zonesApplicable": [1, 2, 3],
        "controlDocUrl": "/controls/pillar-1-security/1.15-encryption-data-in-transit-and-at-rest/",
        "portalPlaybookUrl": "/playbooks/control-implementations/1.15/portal-walkthrough/",
    }

    rendered = generate_homework_pages.format_control_section(control)

    assert "../../../controls/pillar-1-security/1.15-encryption-data-in-transit-and-at-rest.md" in rendered
    assert "../../../playbooks/control-implementations/1.15/portal-walkthrough.md" in rendered


def test_to_relative_leaves_external_links_unchanged() -> None:
    assert (
        generate_homework_pages._to_relative("https://learn.microsoft.com/foo")
        == "https://learn.microsoft.com/foo"
    )
