import openpyxl
from docx import Document
import os

# Paths
XLSX_PATH = "templates/FSI_Agent_Governance_Framework_v1.0_Beta.xlsx"
DOCX_PATH = "templates/FSI_Agent_Governance_Complete_v1.0_Beta.docx"

def verify_xlsx():
    print("=" * 60)
    print("EXCEL TEMPLATE VERIFICATION")
    print("=" * 60)
    
    if not os.path.exists(XLSX_PATH):
        print(f"ERROR: {XLSX_PATH} not found")
        return
    
    wb = openpyxl.load_workbook(XLSX_PATH, read_only=True)
    sheets = wb.sheetnames
    
    print(f"\nFile: {XLSX_PATH}")
    print(f"Total Sheets: {len(sheets)}")
    print("\nSheet Names:")
    for i, name in enumerate(sheets, 1):
        print(f"  {i}. {name}")
    
    # Expected sheets based on spec
    expected = [
        "Dashboard",
        "Security", "Management", "Reporting", "SharePoint",  # 4 assessment
        "Control Summary",
        "Maturity Levels", "Regulatory Mappings", "Admin Portals", 
        "Zone Classification", "RACI"  # Reference
    ]
    
    print("\n--- Spec Validation ---")
    missing = [e for e in expected if not any(e.lower() in s.lower() for s in sheets)]
    if missing:
        print(f"MISSING SHEETS (approx match): {missing}")
    else:
        print("All expected sheet categories found (using fuzzy match)")
    
    wb.close()

def verify_docx():
    print("\n" + "=" * 60)
    print("WORD DOCUMENT VERIFICATION")
    print("=" * 60)
    
    if not os.path.exists(DOCX_PATH):
        print(f"ERROR: {DOCX_PATH} not found")
        return
    
    doc = Document(DOCX_PATH)
    
    print(f"\nFile: {DOCX_PATH}")
    print(f"Total Paragraphs: {len(doc.paragraphs)}")
    print(f"Total Tables: {len(doc.tables)}")
    
    # Extract headings
    headings = []
    for para in doc.paragraphs:
        if para.style and para.style.name and para.style.name.startswith('Heading'):
            headings.append((para.style.name, para.text[:80]))
    
    print(f"\nHeadings Found: {len(headings)}")
    for style, text in headings[:15]:  # Show first 15
        print(f"  [{style}] {text}")
    
    if len(headings) > 15:
        print(f"  ... and {len(headings) - 15} more")

if __name__ == "__main__":
    verify_xlsx()
    verify_docx()
