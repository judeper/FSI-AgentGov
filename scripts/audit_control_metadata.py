#!/usr/bin/env python3
"""
Audit script to check control file metadata and footers.
Checks for:
- Required metadata fields (Control ID, Pillar, Regulatory Reference)
- Footer format and version
- Roles & Responsibilities section
"""

import os
import re
from pathlib import Path

def audit_control_file(filepath):
    """Audit a single control file for metadata compliance."""
    issues = []

    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
        lines = content.split('\n')

    # Check first 30 lines for required metadata
    first_30 = '\n'.join(lines[:30])

    # Check for required metadata fields
    if '**Control ID:**' not in first_30:
        issues.append("Missing '**Control ID:**' metadata")

    if '**Pillar:**' not in first_30:
        issues.append("Missing '**Pillar:**' metadata")

    if '**Regulatory Reference:**' not in first_30:
        issues.append("Missing '**Regulatory Reference:**' metadata")

    # Check for Roles & Responsibilities section
    if '## Roles & Responsibilities' not in content and '## Roles and Responsibilities' not in content:
        issues.append("Missing '## Roles & Responsibilities' section")

    # Check last 10 lines for footer
    last_10 = '\n'.join(lines[-10:])

    # Look for footer pattern: *Updated: ... | Version: ... | UI Verification Status: ...*
    footer_pattern = r'\*Updated:.*?\|.*?Version:.*?\|.*?UI Verification Status:.*?\*'
    footer_match = re.search(footer_pattern, last_10)

    if not footer_match:
        issues.append("Missing or malformed footer")
    else:
        footer_text = footer_match.group(0)

        # Check version is v1.1
        if 'Version: v1.0' in footer_text:
            issues.append("Footer has v1.0 (should be v1.1)")
        elif 'Version: v1.1' not in footer_text:
            issues.append("Footer missing 'Version: v1.1'")

        # Check UI Verification Status is valid
        if 'UI Verification Status: Current' not in footer_text and \
           'UI Verification Status: Needs Verification' not in footer_text:
            issues.append("Invalid UI Verification Status (should be 'Current' or 'Needs Verification')")

    return issues

def main():
    """Main audit function."""
    project_root = Path(__file__).parent.parent
    controls_dir = project_root / 'docs' / 'controls'

    all_controls = []

    # Find all control files (excluding index.md)
    for pillar_dir in controls_dir.glob('pillar-*'):
        if pillar_dir.is_dir():
            for control_file in pillar_dir.glob('*.md'):
                if control_file.name != 'index.md':
                    all_controls.append(control_file)

    all_controls.sort()

    print(f"Found {len(all_controls)} control files to audit\n")
    print("="*80)

    compliant_controls = []
    non_compliant_controls = {}

    for control_file in all_controls:
        issues = audit_control_file(control_file)

        if issues:
            non_compliant_controls[control_file] = issues
        else:
            compliant_controls.append(control_file)

    # Print summary statistics
    print("\n" + "="*80)
    print("AUDIT SUMMARY")
    print("="*80)
    print(f"Total controls checked: {len(all_controls)}")
    print(f"Compliant controls: {len(compliant_controls)}")
    print(f"Non-compliant controls: {len(non_compliant_controls)}")
    print(f"Compliance rate: {len(compliant_controls)/len(all_controls)*100:.1f}%")

    # Print non-compliant controls
    if non_compliant_controls:
        print("\n" + "="*80)
        print("NON-COMPLIANT CONTROLS")
        print("="*80)

        for control_file, issues in non_compliant_controls.items():
            rel_path = control_file.relative_to(project_root)
            print(f"\n{rel_path}")
            for issue in issues:
                print(f"  - {issue}")

    # Print compliant controls
    if compliant_controls:
        print("\n" + "="*80)
        print("COMPLIANT CONTROLS")
        print("="*80)
        for control_file in compliant_controls:
            rel_path = control_file.relative_to(project_root)
            print(f"  [OK] {rel_path}")

    return len(non_compliant_controls)

if __name__ == '__main__':
    exit_code = main()
    exit(exit_code)
