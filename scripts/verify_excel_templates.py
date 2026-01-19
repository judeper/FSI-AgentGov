"""
Excel Template Verification Script for FSI-AgentGov v1.1

Verifies all Excel files in docs/downloads/ for:
1. Correct control counts per template
2. Stale version references (v1.0)
3. Outdated control counts (48 controls)
4. Legacy path references (reference/pillar)

Usage:
    python scripts/verify_excel_templates.py
"""

import os
import sys
from pathlib import Path
from openpyxl import load_workbook

# Expected control counts per template
EXPECTED_COUNTS = {
    "governance-maturity-dashboard.xlsx": 61,
    "purview-administrator-checklist.xlsx": 7,
    "sharepoint-administrator-checklist.xlsx": 7,
    "power-platform-administrator-checklist.xlsx": 7,
    "compliance-officer-checklist.xlsx": 12,
    "entra-administrator-checklist.xlsx": 4
}

# Stale content patterns to search for
STALE_PATTERNS = {
    "v1.0": "Outdated version reference",
    "48 control": "Outdated control count",
    "reference/pillar": "Legacy path reference"
}

def verify_excel_file(file_path):
    """Verify a single Excel file for control counts and stale content."""

    filename = os.path.basename(file_path)
    print(f"\n{'='*80}")
    print(f"Verifying: {filename}")
    print(f"{'='*80}")

    issues = []

    try:
        wb = load_workbook(file_path, data_only=True)

        # Count controls across all sheets
        total_controls = 0
        control_breakdown = {}

        for sheet_name in wb.sheetnames:
            sheet = wb[sheet_name]
            sheet_control_count = 0

            # Look for Control ID column (usually column A)
            # Count rows that look like control IDs (format: X.Y)
            for row in sheet.iter_rows(min_row=2, values_only=True):  # Skip header
                if row and row[0]:  # If first cell has value
                    cell_value = str(row[0]).strip()
                    # Match pattern like "1.1", "2.15", "3.10", "4.7"
                    if '.' in cell_value and len(cell_value.split('.')) == 2:
                        parts = cell_value.split('.')
                        if parts[0].isdigit() and parts[1].isdigit():
                            sheet_control_count += 1
                            total_controls += 1

            if sheet_control_count > 0:
                control_breakdown[sheet_name] = sheet_control_count

        # Verify control count
        expected_count = EXPECTED_COUNTS.get(filename, None)
        if expected_count is not None:
            if total_controls != expected_count:
                issues.append(
                    f"[FAIL] Control count mismatch: Found {total_controls}, expected {expected_count}"
                )
                print(f"[FAIL] Control count: {total_controls} (expected {expected_count})")
            else:
                print(f"[PASS] Control count: {total_controls} (correct)")
        else:
            print(f"[WARN] Control count: {total_controls} (no expected count defined)")

        # Show breakdown by sheet
        if control_breakdown:
            print(f"\n   Control breakdown by sheet:")
            for sheet_name, count in control_breakdown.items():
                print(f"   - {sheet_name}: {count} controls")

        # Search for stale content patterns
        print(f"\n   Checking for stale content...")
        stale_findings = {pattern: [] for pattern in STALE_PATTERNS.keys()}

        for sheet_name in wb.sheetnames:
            sheet = wb[sheet_name]

            for row_idx, row in enumerate(sheet.iter_rows(values_only=True), start=1):
                for col_idx, cell_value in enumerate(row, start=1):
                    if cell_value is not None:
                        cell_str = str(cell_value).lower()

                        for pattern, description in STALE_PATTERNS.items():
                            if pattern.lower() in cell_str:
                                col_letter = chr(64 + col_idx)  # Convert to A, B, C...
                                stale_findings[pattern].append({
                                    "sheet": sheet_name,
                                    "cell": f"{col_letter}{row_idx}",
                                    "value": str(cell_value)[:100]  # Truncate long values
                                })

        # Report stale findings
        stale_found = False
        for pattern, findings in stale_findings.items():
            if findings:
                stale_found = True
                description = STALE_PATTERNS[pattern]
                issues.append(f"[FAIL] Found '{pattern}' ({description}) in {len(findings)} location(s)")
                print(f"\n   [FAIL] Found '{pattern}' ({description}):")
                for finding in findings[:5]:  # Show first 5
                    print(f"      - {finding['sheet']}!{finding['cell']}: {finding['value']}")
                if len(findings) > 5:
                    print(f"      ... and {len(findings) - 5} more")

        if not stale_found:
            print(f"   [PASS] No stale content patterns found")

        wb.close()

    except Exception as e:
        issues.append(f"[FAIL] Error reading file: {str(e)}")
        print(f"[FAIL] Error: {str(e)}")

    return issues

def main():
    """Main verification function."""

    # Get project root
    script_dir = Path(__file__).parent
    project_root = script_dir.parent
    downloads_dir = project_root / "docs" / "downloads"

    print(f"FSI-AgentGov Excel Template Verification")
    print(f"{'='*80}")
    print(f"Project root: {project_root}")
    print(f"Downloads dir: {downloads_dir}")

    if not downloads_dir.exists():
        print(f"\n[FAIL] Downloads directory not found: {downloads_dir}")
        return 1

    # Find all Excel files
    excel_files = list(downloads_dir.glob("*.xlsx"))

    if not excel_files:
        print(f"\n[FAIL] No Excel files found in {downloads_dir}")
        return 1

    print(f"\nFound {len(excel_files)} Excel file(s) to verify")

    # Verify each file
    all_issues = {}
    for excel_file in sorted(excel_files):
        issues = verify_excel_file(excel_file)
        if issues:
            all_issues[excel_file.name] = issues

    # Summary report
    print(f"\n{'='*80}")
    print(f"VERIFICATION SUMMARY")
    print(f"{'='*80}")

    if all_issues:
        print(f"\n[FAIL] Issues found in {len(all_issues)} file(s):\n")
        for filename, issues in all_issues.items():
            print(f"{filename}:")
            for issue in issues:
                print(f"  {issue}")
            print()
        return 1
    else:
        print(f"\n[PASS] All Excel files passed verification!")
        print(f"   - Control counts correct")
        print(f"   - No stale content found")
        return 0

if __name__ == "__main__":
    sys.exit(main())
