import re
import subprocess
import sys
from datetime import date, timedelta
from pathlib import Path

# Fix Unicode encoding issues on Windows
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

DOCS_DIR = Path("docs")
CONTROL_INDEX_PATH = DOCS_DIR / "controls" / "CONTROL-INDEX.md"
REG_MAPPINGS_PATH = DOCS_DIR / "reference" / "regulatory-mappings.md"
PILLARS_DIR = DOCS_DIR / "controls"
PLAYBOOKS_DIR = DOCS_DIR / "playbooks" / "control-implementations"

REQUIRED_PLAYBOOK_FILES = [
    "portal-walkthrough.md",
    "powershell-setup.md",
    "verification-testing.md",
    "troubleshooting.md",
]

def _accepted_update_dates(lookback_months=3):
    """Generate accepted 'Updated: Month Year' values for the current and previous months."""
    today = date.today()
    dates = []
    first_of_month = today.replace(day=1)
    for _i in range(lookback_months):
        label = f"Updated: {first_of_month.strftime('%B %Y')}"
        if label not in dates:
            dates.append(label)
        # Move to first of previous month
        first_of_month = (first_of_month - timedelta(days=1)).replace(day=1)
    return dates

CANON_UPDATED = f"Updated: {date.today().strftime('%B %Y')}"
# Control docs carry a footer "Version: vX.Y" that tracks the framework
# release the control's template structure was last validated against.
# When the framework cuts a new minor (e.g., v1.4 → v1.5 → v1.6), add the
# new "Version: vX.Y" prefix to _ACCEPTED_VERSION so existing controls and
# bulk-bumped controls both pass. Older accepted values stay listed so
# unmodified historical controls keep validating.
#
# NOTE (PR-0, Tier -1): _ACCEPTED_VERSION intentionally permits historical
# narrative such as "Earlier in v1.5.0 we shipped..." inside control bodies.
# Footer-stamp drift on framework-layer docs (README, DISCLAIMER, framework/*,
# .claude/CLAUDE.md) is enforced by scripts/verify_version_stamps.py — pinning
# *that* check to a single canonical version, not to this multi-version list.
CANON_VERSION = "Version: v1.6"
_ACCEPTED_UPDATED = _accepted_update_dates(lookback_months=3)
_ACCEPTED_VERSION = ["Version: v1.2", "Version: v1.3", "Version: v1.4", "Version: v1.5", "Version: v1.6"]
CANON_UI_STATUS_PREFIX = "UI Verification Status:"
# Control files use a Roles & Responsibilities section instead of a single Primary Owner field
ROLES_SECTION = "## Roles & Responsibilities"

REQUIRED_HEADINGS = [
    "## Objective",
    "## Why This Matters for FSI",
    "## Control Description",
    "## Key Configuration Points",
    "## Zone-Specific Requirements",
    "## Roles & Responsibilities",
    "## Related Controls",
    "## Implementation Playbooks",
    "## Verification Criteria",
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
    # CONTROL-INDEX.md uses table format: | 1.1 | [Control Name](path.md) | Implementation |
    matches = re.findall(r'\|\s*(\d+\.\d+)\s*\|\s*\[?([^\]\|]+)\]?', content)
    if not matches:
        print(f"WARNING: No control IDs parsed from {CONTROL_INDEX_PATH}. "
              "Index consistency check will be skipped.")
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
    # Accept both formats: "# Control X.Y: Name" or "# Control X.Y - Name"
    if not re.search(r"^#\s+Control\s+\d+\.\d+[:\-]\s+.+$", content, flags=re.MULTILINE):
        failures.append("missing or malformed control title (expected '# Control X.Y: ...' or '# Control X.Y - ...')")

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

    if not any(v in content for v in _ACCEPTED_UPDATED):
        failures.append(f"missing canonical update date in footer (accepted: {_ACCEPTED_UPDATED})")

    if not any(v in content for v in _ACCEPTED_VERSION):
        failures.append(f"missing canonical version in footer (accepted: {_ACCEPTED_VERSION})")

    if CANON_UI_STATUS_PREFIX not in content:
        failures.append("missing UI Verification Status in footer")

    # 3) Guardrail: legacy version/update markers should not remain
    for pattern in _LEGACY_MARKER_PATTERNS:
        if pattern.search(content):
            failures.append(f"contains legacy marker matching: {pattern.pattern}")

    return failures


def validate_playbook_files(control_id: str) -> list[str]:
    """Validate that 4 standard playbook files exist for a control."""
    failures = []
    playbook_dir = PLAYBOOKS_DIR / control_id
    if not playbook_dir.exists():
        failures.append(f"playbook directory missing: {playbook_dir}")
        return failures
    for fname in REQUIRED_PLAYBOOK_FILES:
        if not (playbook_dir / fname).exists():
            failures.append(f"missing playbook: {playbook_dir / fname}")
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
        for filename, _rel_path, _pillar in files:
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
    for _filename, rel_path, _pillar in files:
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

    # 3b) Validate playbook files exist per control
    print("\n--- PLAYBOOK FILE VALIDATION ---\n")
    playbook_failures = 0
    for filename, _rel_path, _pillar in files:
        # Extract control ID from filename (e.g., "1.1-restrict-agent-publishing.md" -> "1.1")
        match = re.match(r"^(\d+\.\d+)-", filename)
        if not match:
            continue
        control_id = match.group(1)
        pb_issues = validate_playbook_files(control_id)
        if pb_issues:
            playbook_failures += 1
            print(f"❌ {control_id}")
            for issue in pb_issues:
                print(f"   - {issue}")

    if playbook_failures == 0:
        print("✅ All controls have 4 standard playbook files.")
    else:
        print(f"\nERROR: {playbook_failures} controls missing playbook files.")
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
