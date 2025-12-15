import os
import re
from pathlib import Path

DOCS_DIR = Path("docs")
CONTROL_INDEX_PATH = DOCS_DIR / "reference/CONTROL-INDEX.md"
REG_MAPPINGS_PATH = DOCS_DIR / "reference/regulatory-mappings.md"
PILLARS_DIR = DOCS_DIR / "reference"

def parse_control_index():
    """Extracts control IDs and titles from the Control Index."""
    controls = {}
    if not CONTROL_INDEX_PATH.exists():
        print(f"ERROR: {CONTROL_INDEX_PATH} not found.")
        return controls
        
    content = CONTROL_INDEX_PATH.read_text()
    # Assuming format: | 1.1 | [Restrict Agent Publishing...](...) | ...
    # Or markdown list: - **1.1**: ...
    # based on file preview, it likely has a table or headers.
    # Let's try a regex for "X.Y" ids.
    
    # We'll need to adjust this after seeing the file, but for now assuming standard ID format
    matches = re.findall(r'\|\s*(\d+\.\d+)\s*\|\s*\[?([^\]\|]+)\]?', content)
    for cid, title in matches:
        controls[cid] = title.strip()
    return controls

def get_pillar_files():
    """Finds all markdown files in pillar directories."""
    files = []
    # Pillars 1-4
    for i in range(1, 5):
        p_dir = [d for d in PILLARS_DIR.glob(f"pillar-{i}*") if d.is_dir()]
        if not p_dir:
            continue
        p_dir = p_dir[0]
        for f in p_dir.glob("*.md"):
            if f.name == "index.md": continue
            files.append(str(f.relative_to(DOCS_DIR)))
    return sorted(files)

def verify_consistency():
    controls = parse_control_index()
    files = get_pillar_files()
    
    print(f"Found {len(controls)} controls in Index.")
    print(f"Found {len(files)} content files in Pillars.")
    
    # 1. Check if files exist for controls
    # Naive check: does the filename start with the control ID?
    missing_files = []
    for cid in controls:
        found = False
        for f in files:
            if f.split('/')[-1].startswith(cid):
                found = True
                break
        if not found:
            missing_files.append(cid)
            
    if missing_files:
        print(f"WARNING: No file found for controls: {missing_files}")
    else:
        print("SUCCESS: All controls have corresponding files.")

    # 2. Generate Nav Structure for mkdocs.yml
    print("\n--- SUGGESTED NAV STRUCTURE ---\n")
    current_pillar = ""
    for f in files:
        # derive pillar name from path
        # reference/pillar-1-security/1.1-name.md
        parts = f.split('/')
        pillar = parts[1]
        
        if pillar != current_pillar:
            print(f"  - {pillar}:")
            current_pillar = pillar
            
        # Format: - Name: path
        name = parts[-1].replace('.md', '').replace('-', ' ').title()
        print(f"    - {name}: {f}")

if __name__ == "__main__":
    verify_consistency()
