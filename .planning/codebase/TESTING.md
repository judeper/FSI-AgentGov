# Testing Patterns

**Analysis Date:** 2026-02-02

## Test Framework

**Runner:**
- No dedicated test runner found (pytest, unittest not configured)
- Validation scripts serve as integration tests: `verify_controls.py`, `verify_templates.py`, `validate_before_push.py`

**Assertion Library:**
- No formal assertion library
- Validation scripts use explicit checks and exit codes

**Run Commands:**
```bash
python scripts/validate_before_push.py     # Pre-push validation (mkdocs, controls, links)
python scripts/verify_controls.py          # Control structure validation (62 controls)
python scripts/verify_excel_templates.py   # Excel template validation
python scripts/learn_monitor.py --dry-run  # Microsoft Learn monitoring (no state save)
python scripts/learn_monitor.py --limit 5  # Limited test run (5 URLs)
mkdocs build --strict                      # MkDocs build validation (no errors/warnings)
mkdocs serve                               # Local preview
```

## Test File Organization

**Location:**
- No dedicated `tests/` directory
- Validation scripts in `scripts/` directory: `verify_*.py`, `validate_*.py`
- Hooks in `scripts/hooks/`: `boundary-check.py`, `researcher-package-reminder.py`

**Naming:**
- `verify_*.py` - Control and template validation
- `validate_*.py` - Pre-push and documentation validation
- `*_test.py` or `*.spec.py` - Not used

**Structure:**
```
scripts/
├── verify_controls.py              # Validates 62 control file structure
├── verify_templates.py             # Validates template structure
├── verify_excel_templates.py       # Validates Excel checklist format
├── validate_before_push.py         # Pre-push integration check
├── validate_docs_anchors.py        # Markdown fragment link validation
├── learn_monitor.py                # Microsoft Learn URL monitoring
└── hooks/
    ├── boundary-check.py           # Bash command boundary enforcement
    └── researcher-package-reminder.py  # Post-edit reminder
```

## Test Structure

**Validation Pattern from `verify_controls.py`:**
```python
def verify_consistency():
    """Run all consistency checks."""
    controls = parse_control_index()
    files = get_pillar_files()

    # 1. Check file existence
    missing_files = []
    for cid in controls:
        found = False
        for filename, rel_path, pillar in files:
            if filename.startswith(f"{cid}-"):
                found = True
                break
        if not found:
            missing_files.append(cid)

    # 2. Validate control content
    hard_failures = 0
    for filename, rel_path, pillar in files:
        failures = validate_control_file(full_path)
        if failures:
            hard_failures += 1
            print(f"❌ {rel_path}")
            for failure in failures:
                print(f"   - {failure}")

    # 3. Report results
    if hard_failures == 0:
        print("✅ All control files meet required standards.")
    else:
        raise SystemExit(1)
```

**Patterns:**
- Setup phase: Parse configuration, load file lists
- Validation phase: Iterate and check each item
- Reporting phase: Print results with visual indicators (✓, ✗, ⚠)
- Exit with meaningful codes (0=success, 1=failure)

## Mocking

**Framework:**
- Not used (validation scripts test real files on disk)
- Network mocking occurs implicitly via `--dry-run` flags

**Patterns:**
- Learn Monitor testing with `--dry-run` flag skips state persistence
- Learn Monitor testing with `--limit N` reduces URL count
- Learn Monitor testing with `--url` enables single-URL debug mode

**Example from `learn_monitor.py` (lines 637-646):**
```python
parser.add_argument("--dry-run", action="store_true",
                   help="Don't save state or write report")
parser.add_argument("--limit", type=int,
                   help="Limit number of URLs to check (for testing)")
parser.add_argument("--debug", "-d", action="store_true",
                   help="Enable debug output (very verbose)")
parser.add_argument("--url", type=str,
                   help="Check a single URL (for debugging)")
```

**What to Mock:**
- Network requests (implicit via test mode)
- File I/O (test with sample files)

**What NOT to Mock:**
- Actual file system validation (verify real files)
- Markdown parsing and anchor validation
- Control structure checks

## Fixtures and Factories

**Test Data:**
- No formal fixture framework
- Test data embedded in scripts as configuration
- REQUIRED_HEADINGS list in `verify_controls.py` (lines 22-33) serves as control structure fixture

**Example - Control structure fixture from `verify_controls.py`:**
```python
REQUIRED_HEADINGS = [
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

_REQUIRED_METADATA_FIELDS = [
    "**Control ID:**",
    "**Pillar:**",
    "**Regulatory Reference:**",
]
```

**Location:**
- Configuration at module top: `PILLARS` dict in `compile_researcher_package.py`
- Pattern definitions: `_LEGACY_MARKER_PATTERNS`, `_HTML_ID_RE` in respective scripts
- Watchlist: `docs/reference/microsoft-learn-urls.md`

## Coverage

**Requirements:**
- No formal coverage tool configured
- Manual validation of critical paths
- All 62 controls structurally validated before build passes

**View Coverage:**
```bash
# No automated coverage reports - manual verification required
# Control validation covers all 62 controls
python scripts/verify_controls.py

# Anchor validation covers all docs
python scripts/validate_docs_anchors.py

# Build validation covers all markdown syntax
mkdocs build --strict
```

## Test Types

**Unit Tests:**
- Not formalized
- Single-responsibility functions testable in isolation: `parse_watchlist()`, `classify_change()`, `_slugify_heading()`
- Example testable function from `validate_docs_anchors.py` (lines 65-75):
```python
def _slugify_heading(text: str) -> str:
    """Best-effort slugifier for MkDocs-style heading IDs."""
    text = _strip_inline_code(text)
    text = text.strip().lower()
    text = re.sub(r"[^a-z0-9 _-]", "", text)
    text = text.replace("_", "-")
    text = re.sub(r"\s+", "-", text)
    text = re.sub(r"-+", "-", text).strip("-")
    return text
```

**Integration Tests:**
- `validate_before_push.py` - Full workflow validation (mkdocs + controls + links)
- `learn_monitor.py` - Full monitoring workflow with state management
- All validation scripts test against real codebase

**Example integration workflow from `validate_before_push.py` (lines 59-83):**
```python
def main():
    """Run all pre-push validations."""
    repo_root = Path(__file__).parent.parent

    checks = []

    # 1. MkDocs build (checks internal links and markdown syntax)
    checks.append(run_command(
        ["mkdocs", "build", "--strict"],
        "MkDocs build (internal links + markdown)",
        cwd=repo_root
    ))

    # 2. Control file validation
    checks.append(run_command(
        [sys.executable, "scripts/verify_controls.py"],
        "Control file structure validation",
        cwd=repo_root
    ))

    # 3. External link validation (sample)
    sample_files = [
        "docs/controls/pillar-1-security/1.1-restrict-agent-publishing-by-authorization.md",
        "docs/controls/pillar-2-management/2.1-managed-environments.md",
    ]
```

**E2E Tests:**
- Not automated in separate suite
- `learn_monitor.py` serves as E2E test for documentation monitoring

## Common Patterns

**Error Handling in Validation:**
- Check for required fields, report failures, continue to next item
- Accumulate failures rather than failing fast
- Print detailed error messages with context

**Example from `verify_controls.py` (lines 89-131):**
```python
def validate_control_file(path: Path):
    """Validate control structure and required metadata."""
    content = path.read_text(encoding="utf-8")
    failures = []

    # Check title format
    if not re.search(r"^#\s+Control\s+\d+\.\d+[:\-]\s+.+$", content, flags=re.MULTILINE):
        failures.append("missing or malformed control title")

    # Check required sections
    for heading in REQUIRED_HEADINGS:
        if heading not in content:
            failures.append(f"missing heading: {heading}")

    # Check metadata
    for field in _REQUIRED_METADATA_FIELDS:
        if field not in content:
            failures.append(f"missing required metadata field: {field}")

    return failures
```

**Stateful Testing Pattern:**
- Learn Monitor maintains state file: `data/learn-monitor-state.json`
- First run establishes baseline (no report generated)
- Subsequent runs compare against baseline
- State includes: content hash, normalized content, timestamps, metadata

**Example state management from `learn_monitor.py` (lines 375-396):**
```python
def load_state(state_path: Path) -> dict:
    """Load state from JSON file."""
    if state_path.exists():
        try:
            return json.loads(state_path.read_text(encoding='utf-8'))
        except json.JSONDecodeError:
            print("WARNING: State file corrupt, starting fresh")
    return {
        "schema_version": 2,
        "last_run": None,
        "urls": {},
        "statistics": {}
    }

def save_state(state: dict, state_path: Path):
    """Save state to JSON file."""
    state_path.parent.mkdir(parents=True, exist_ok=True)
    state_path.write_text(
        json.dumps(state, indent=2, ensure_ascii=False),
        encoding='utf-8'
    )
```

**Markdown Validation Pattern:**
- Regex patterns extract and validate links
- Fragment anchors validated against explicit IDs or auto-derived headings
- Support for three anchor formats:
  - HTML anchors: `<a id="fragment"></a>`
  - Attr_list IDs: `## Heading {#fragment}`
  - Auto-slugified headings

**Example from `validate_docs_anchors.py` (lines 39-48):**
```python
_LINK_RE = re.compile(r"\[[^\]]+\]\(([^)]+)\)")
_HTML_ID_RE = re.compile(r"<a\s+id=\"([^\"]+)\"\s*></a>", re.IGNORECASE)
_ATTR_LIST_ID_RE = re.compile(r"\{#([A-Za-z0-9][A-Za-z0-9_-]*)\}\s*$")
_HEADING_RE = re.compile(r"^(#{1,6})\s+(.+?)\s*$")
```

## CI/CD Integration

**Pre-Push Validation:**
- Run `python scripts/validate_before_push.py` before push
- Checks: mkdocs build, control structure, sample external links
- Flags optional markdown-link-check if installed (npm)

**Git Hooks Configuration:**
- Configured in `.claude/settings.json` with Claude Code hooks
- PreToolUse: `boundary-check.py` validates Bash command boundaries
- PostToolUse: `researcher-package-reminder.py` reminds to regenerate package after edits

---

*Testing analysis: 2026-02-02*
