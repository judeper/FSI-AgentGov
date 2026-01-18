import os
import re
import subprocess
import sys
from pathlib import Path

DOCS_DIR = Path("docs")
CONTROL_INDEX_PATH = DOCS_DIR / "controls" / "CONTROL-INDEX.md"
REG_MAPPINGS_PATH = DOCS_DIR / "reference" / "regulatory-mappings.md"
PILLARS_DIR = DOCS_DIR / "controls"

CANON_UPDATED = "Updated: January 2026"
CANON_VERSION = "Version: v1.1"
CANON_UI_STATUS_PREFIX = "UI Verification Status:"
# Control files use a Roles & Responsibilities section instead of a single Primary Owner field
ROLES_SECTION = "## Roles & Responsibilities"

REQUIRED_HEADINGS = [
    "## Objective",
    "## Why This Matters for FSI",
    "## Control Description",
    "## Related Controls",
    "## Additional Resources",
]

REQUIRED_SUBHEADINGS = [
    # Zone-Specific Requirements is a ## heading, not a ### subheading
]

_LEGACY_MARKER_PATTERNS = [
    re.compile(r"\*\*Last Updated:\*\*", re.IGNORECASE),
    re.compile(r"\bLast Updated:\b", re.IGNORECASE),
    re.compile(r"\*\*Version:\*\*\s*2\.0\b", re.IGNORECASE),
    re.compile(r"\bVersion:\s*2\.0\b", re.IGNORECASE),
]

_REQUIRED_METADATA_FIELDS = [
    "**Control ID:**",
    "**Pillar:**",
    "**Regulatory Reference:**",
]

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
            if f.name == "index.md": 
                continue
            # Store both the file object and relative path with forward slashes
            rel_path = str(f.relative_to(DOCS_DIR)).replace('\\', '/')
            files.append((f.name, rel_path, p_dir.name))
    return sorted(files, key=lambda x: x[1])


def validate_control_file(path: Path):
    """Validate control structure and required beta metadata."""
    content = path.read_text(encoding="utf-8")
    failures = []

    # 0) Must look like a control page (title)
    if not re.search(r"^#\s+Control\s+\d+\.\d+:\s+.+$", content, flags=re.MULTILINE):
        failures.append("missing or malformed control title (expected '# Control X.Y: ...')")

    # 1) Minimal structural headings (current baseline across repo)

    for heading in REQUIRED_HEADINGS:
        if heading not in content:
            failures.append(f"missing heading: {heading}")

    for heading in REQUIRED_SUBHEADINGS:
        if heading not in content:
            failures.append(f"missing subheading: {heading}")

    # 2) Required Overview metadata block fields
    for field in _REQUIRED_METADATA_FIELDS:
        if field not in content:
            failures.append(f"missing required metadata field: {field}")

    if ROLES_SECTION not in content:
        failures.append("missing Roles & Responsibilities section")

    if CANON_UPDATED not in content:
        failures.append(f"missing canonical '{CANON_UPDATED}' in footer")

    if CANON_VERSION not in content:
        failures.append(f"missing canonical '{CANON_VERSION}' in footer")

    if CANON_UI_STATUS_PREFIX not in content:
        failures.append("missing UI Verification Status in footer")

    # 3) Guardrail: legacy version/update markers should not remain
    for pattern in _LEGACY_MARKER_PATTERNS:
        if pattern.search(content):
            failures.append(f"contains legacy marker matching: {pattern.pattern}")

    return failures

def verify_consistency():
    controls = parse_control_index()
    files = get_pillar_files()
    
    print(f"Found {len(controls)} controls in Index.")
    print(f"Found {len(files)} content files in Pillars.")
    
    # 1. Check if files exist for controls
    # Check if the filename starts with the control ID followed by a dash
    missing_files = []
    for cid in controls:
        found = False
        for filename, rel_path, pillar in files:
            # Match control ID at start of filename (e.g., "1.1-" matches "1.1")
            if filename.startswith(f"{cid}-"):
                found = True
                break
        if not found:
            missing_files.append(cid)
            
    if missing_files:
        print(f"WARNING: No file found for controls: {missing_files}")
    else:
        print("SUCCESS: All controls have corresponding files.")

    # 3. Validate control content (structure + beta metadata)
    print("\n--- CONTROL CONTENT VALIDATION ---\n")
    hard_failures = 0
    for filename, rel_path, pillar in files:
        # rel_path already includes reference/... relative to docs
        full_path = DOCS_DIR / rel_path
        if not full_path.exists():
            continue

        failures = validate_control_file(full_path)
        if failures:
            hard_failures += 1
            print(f"❌ {rel_path}")
            for failure in failures:
                print(f"   - {failure}")

    if hard_failures == 0:
        print("✅ All control files meet required beta structure + footer standards.")
    else:
        print(f"\nERROR: {hard_failures} control files failed required validation.")
        raise SystemExit(1)

    # 4) Validate that all docs fragment links (#anchors) resolve.
    print("\n--- DOCS ANCHOR VALIDATION ---\n")
    validator_path = Path(__file__).parent / "validate_docs_anchors.py"
    if validator_path.exists():
        result = subprocess.run(
            [sys.executable, str(validator_path)],
            cwd=Path(__file__).resolve().parents[1],
            check=False,
        )
        if result.returncode != 0:
            raise SystemExit(result.returncode)
    else:
        print(f"WARNING: Anchor validator not found at {validator_path} (skipping).")

    # 2. Generate Nav Structure for mkdocs.yml
    print("\n--- SUGGESTED NAV STRUCTURE ---\n")
    current_pillar = ""
    for filename, rel_path, pillar in files:
        if pillar != current_pillar:
            print(f"  - {pillar}:")
            current_pillar = pillar
            
        # Format: - Name: path
        name = filename.replace('.md', '').replace('-', ' ').title()
        # rel_path is already docs-relative (e.g., reference/pillar-1-security/1.1-...).
        print(f"    - {name}: {rel_path}")

if __name__ == "__main__":
    verify_consistency()
