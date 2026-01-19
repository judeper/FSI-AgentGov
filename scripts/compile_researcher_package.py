#!/usr/bin/env python3
"""
Compile FSI-AgentGov controls into researcher package documents.
Creates consolidated markdown files for external research review.
"""

import os
import re
from pathlib import Path

BASE_DIR = Path(r"C:\dev\FSI-AgentGov")
DOCS_DIR = BASE_DIR / "docs" / "controls"
OUTPUT_DIR = BASE_DIR / "maintainers-local" / "researcher-package"

# Pillar definitions with control numbers
PILLARS = {
    1: {
        "name": "Security",
        "folder": "pillar-1-security",
        "controls": list(range(1, 24)),  # 1.1 to 1.23
        "description": "Protect data, manage access, and maintain audit trails for AI agents."
    },
    2: {
        "name": "Management",
        "folder": "pillar-2-management",
        "controls": list(range(1, 22)),  # 2.1 to 2.21
        "description": "Govern agent lifecycle, risk management, and operational oversight."
    },
    3: {
        "name": "Reporting",
        "folder": "pillar-3-reporting",
        "controls": list(range(1, 11)),  # 3.1 to 3.10
        "description": "Provide visibility, accountability, and metrics for agent governance."
    },
    4: {
        "name": "SharePoint",
        "folder": "pillar-4-sharepoint",
        "controls": list(range(1, 8)),  # 4.1 to 4.7
        "description": "Govern SharePoint content that AI agents can access and use."
    }
}


def convert_internal_links(content: str) -> str:
    """Convert internal markdown links to plain text references."""
    # Convert [Control X.Y](../path) to "See Control X.Y"
    content = re.sub(
        r'\[Control (\d+\.\d+)\]\([^)]+\)',
        r'See Control \1',
        content
    )
    # Convert [text](../pillar-X-name/...) links to plain text
    content = re.sub(
        r'\[([^\]]+)\]\(\.\./pillar-\d+-[^)]+\)',
        r'\1',
        content
    )
    # Convert relative image paths to note about images
    content = re.sub(
        r'!\[([^\]]*)\]\(\.\./\.\./images/[^)]+\)',
        r'[Image: \1]',
        content
    )
    return content


def get_control_files(pillar_num: int) -> list:
    """Get sorted list of control files for a pillar."""
    pillar = PILLARS[pillar_num]
    folder = DOCS_DIR / pillar["folder"]

    control_files = []
    for ctrl_num in pillar["controls"]:
        # Find file matching control number
        pattern = f"{pillar_num}.{ctrl_num}-*.md"
        matches = list(folder.glob(pattern))
        if matches:
            control_files.append(matches[0])
        else:
            print(f"  Warning: No file found for Control {pillar_num}.{ctrl_num}")

    return control_files


def read_index_file(pillar_num: int) -> str:
    """Read the index.md for a pillar."""
    pillar = PILLARS[pillar_num]
    index_path = DOCS_DIR / pillar["folder"] / "index.md"

    if index_path.exists():
        with open(index_path, 'r', encoding='utf-8') as f:
            content = f.read()
        # Convert links
        content = convert_internal_links(content)
        return content
    return ""


def compile_pillar(pillar_num: int) -> str:
    """Compile a single pillar into a complete markdown document."""
    pillar = PILLARS[pillar_num]

    lines = []

    # Header
    lines.append(f"# Pillar {pillar_num}: {pillar['name']} Controls - Research Review Package\n")
    lines.append("")

    # Pillar overview
    lines.append("## Pillar Overview\n")
    lines.append(f"{pillar['description']}\n")
    lines.append("")

    # Read index content for overview
    index_content = read_index_file(pillar_num)
    if index_content:
        # Extract overview section from index
        lines.append(index_content)
        lines.append("")

    # Table of Contents
    control_files = get_control_files(pillar_num)
    lines.append("## Table of Contents\n")
    for i, ctrl_file in enumerate(control_files, 1):
        ctrl_name = ctrl_file.stem.split('-', 1)[1].replace('-', ' ').title()
        ctrl_id = ctrl_file.stem.split('-')[0]
        lines.append(f"{i}. Control {ctrl_id}: {ctrl_name}")
    lines.append("")
    lines.append("---\n")

    # Compile each control
    for ctrl_file in control_files:
        ctrl_id = ctrl_file.stem.split('-')[0]
        print(f"  Processing Control {ctrl_id}...")

        with open(ctrl_file, 'r', encoding='utf-8') as f:
            content = f.read()

        # Convert internal links
        content = convert_internal_links(content)

        # Add control content
        lines.append(content)
        lines.append("")
        lines.append("---\n")

    # Footer
    lines.append("")
    lines.append("*Generated: January 2026*")
    lines.append(f"*Source: {DOCS_DIR / pillar['folder']}/*")
    lines.append("")

    return "\n".join(lines)


def main():
    """Compile all pillar documents."""
    print("FSI-AgentGov Researcher Package Compiler")
    print("=" * 50)

    # Ensure output directory exists
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    for pillar_num in PILLARS:
        pillar = PILLARS[pillar_num]
        output_file = OUTPUT_DIR / f"0{pillar_num}-Pillar-{pillar_num}-{pillar['name']}-Controls.md"

        print(f"\nCompiling Pillar {pillar_num}: {pillar['name']}...")

        content = compile_pillar(pillar_num)

        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(content)

        # Count lines
        line_count = content.count('\n')
        print(f"  Written to: {output_file}")
        print(f"  Lines: {line_count:,}")

    print("\n" + "=" * 50)
    print("Compilation complete!")
    print(f"Output directory: {OUTPUT_DIR}")


if __name__ == "__main__":
    main()
