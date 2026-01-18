from pathlib import Path
import os
import sys

# Fix Unicode encoding issues on Windows
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

try:
    import openpyxl
    HAS_OPENPYXL = True
except ImportError:
    HAS_OPENPYXL = False
    print("Note: openpyxl not installed - Excel validation will be limited")

# Paths - look in docs/downloads for the actual template files
DOWNLOADS_DIR = Path("docs/downloads")
TEMPLATES_DIR = Path("docs/templates")

# Expected Excel checklists
EXPECTED_CHECKLISTS = [
    "compliance-officer-checklist.xlsx",
    "entra-administrator-checklist.xlsx",
    "governance-maturity-dashboard.xlsx",
    "power-platform-administrator-checklist.xlsx",
    "purview-administrator-checklist.xlsx",
    "sharepoint-administrator-checklist.xlsx"
]

def verify_checklists():
    print("=" * 60)
    print("EXCEL CHECKLIST VERIFICATION")
    print("=" * 60)
    
    if not DOWNLOADS_DIR.exists():
        print(f"ERROR: {DOWNLOADS_DIR} not found")
        return False
    
    all_found = True
    for checklist in EXPECTED_CHECKLISTS:
        file_path = DOWNLOADS_DIR / checklist
        if file_path.exists():
            print(f"✅ Found: {checklist}")
            if HAS_OPENPYXL:
                try:
                    wb = openpyxl.load_workbook(file_path, read_only=True)
                    print(f"   Sheets: {', '.join(wb.sheetnames)}")
                    wb.close()
                except Exception as e:
                    print(f"   ⚠️ Could not read: {e}")
        else:
            print(f"❌ Missing: {checklist}")
            all_found = False
    
    return all_found

def verify_markdown_template():
    print("\n" + "=" * 60)
    print("MARKDOWN TEMPLATE VERIFICATION")
    print("=" * 60)
    
    template_path = TEMPLATES_DIR / "control-setup-template.md"
    
    if not template_path.exists():
        print(f"ERROR: {template_path} not found")
        return False
    
    content = template_path.read_text(encoding='utf-8')
    
    # Check for required sections (canonical template structure matching actual controls)
    required_sections = [
        "## Objective",
        "## Why This Matters for FSI",
        "## Control Description",
        "## Key Configuration Points",
        "## Zone-Specific Requirements",
        "## Roles & Responsibilities",
        "## Related Controls",
        "## Implementation Guides",
        "## Verification Criteria",
        "## Additional Resources",
    ]

    required_snippets = [
        "**Control ID:**",
        "**Pillar:**",
        "**Regulatory Reference:**",
        "Updated: January 2026",
        "Version: v1.1",
        "UI Verification Status:",
    ]
    
    print(f"\nFile: {template_path}")
    print(f"Size: {len(content)} bytes")
    print("\nRequired Sections:")
    
    all_found = True
    for section in required_sections:
        if section in content:
            print(f"  ✅ {section}")
        else:
            print(f"  ❌ {section} - MISSING")
            all_found = False

    print("\nRequired Template Fields:")
    for snippet in required_snippets:
        if snippet in content:
            print(f"  ✅ {snippet}")
        else:
            print(f"  ❌ {snippet} - MISSING")
            all_found = False
    
    return all_found

def verify_downloads_index():
    print("\n" + "=" * 60)
    print("DOWNLOADS INDEX VERIFICATION")
    print("=" * 60)
    
    index_path = DOWNLOADS_DIR / "index.md"
    
    if not index_path.exists():
        print(f"ERROR: {index_path} not found")
        return False
    
    content = index_path.read_text(encoding='utf-8')
    
    # Check that all checklists are referenced in the index
    all_referenced = True
    for checklist in EXPECTED_CHECKLISTS:
        if checklist in content:
            print(f"  ✅ Referenced: {checklist}")
        else:
            print(f"  ❌ Not referenced: {checklist}")
            all_referenced = False
    
    return all_referenced

if __name__ == "__main__":
    print("\nFSI Agent Governance - Template Verification\n")
    
    checklists_ok = verify_checklists()
    template_ok = verify_markdown_template()
    index_ok = verify_downloads_index()
    
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print(f"Excel Checklists: {'✅ PASS' if checklists_ok else '❌ FAIL'}")
    print(f"Markdown Template: {'✅ PASS' if template_ok else '❌ FAIL'}")
    print(f"Downloads Index: {'✅ PASS' if index_ok else '❌ FAIL'}")
    
    if not (checklists_ok and template_ok and index_ok):
        sys.exit(1)
