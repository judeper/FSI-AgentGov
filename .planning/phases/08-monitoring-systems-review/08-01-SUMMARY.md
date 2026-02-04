---
phase: 08-monitoring-systems-review
plan: 01
subsystem: monitoring
tags: [learn-monitor, monitoring-framework, state-management, reporting, control-mapping]
requires: []
provides:
  - Unified monitoring framework with pluggable source adapters
  - Control-to-URL impact mapping in change reports
  - Unified state file format supporting multiple source types
  - Enhanced report format with summary tables and detailed diff sections
affects:
  - Plan 08-02 (Regulatory Monitor implementation)
  - Plan 08-03 (AI-assisted review workflow)
tech-stack:
  added: []
  patterns:
    - Unified monitoring architecture (one system, multiple source adapters)
    - Source-keyed state management (single file for all monitoring sources)
    - Control-to-URL impact mapping
    - Atomic state file writes with backup
    - Tiered classification system (CRITICAL/HIGH/MEDIUM/NOISE)
key-files:
  created:
    - scripts/monitoring_shared.py
  modified:
    - scripts/learn_monitor.py
    - .github/workflows/learn-monitor.yml
decisions:
  - title: "Unified state file format"
    rationale: "Single data/monitor-state.json with source-keyed sections enables one monitoring system with multiple adapters instead of separate systems"
    impact: "Simplifies state management, enables cross-source reporting, prepares for regulatory monitor"
  - title: "Backward compatibility with state migration"
    rationale: "Automatically migrates old learn-monitor-state.json to unified format on first load"
    impact: "Zero disruption for existing deployments, preserves historical baseline"
  - title: "Reports directory unification"
    rationale: "All monitoring outputs to reports/monitoring/ with source-specific filenames (learn-changes-*.md, regulatory-changes-*.md)"
    impact: "Consistent report location across all monitoring sources"
  - title: "Control-to-URL impact mapping"
    rationale: "find_affected_controls() scans docs/controls/ and docs/playbooks/ to show which framework components reference each changed URL"
    impact: "Change reports now answer 'which controls are affected?' not just 'what changed?'"
  - title: "Summary table for quick scanning"
    rationale: "format_change_summary() generates markdown table with shortened URLs, affected controls, and action required"
    impact: "Enables 30-second review of daily/weekly monitor runs"
metrics:
  duration: "7 minutes"
  completed: "2026-02-04"
---

# Phase 8 Plan 01: Unified Monitoring Framework Summary

**One-liner:** Refactored Learn Monitor into unified monitoring framework with shared utilities, control-to-URL impact mapping, and enhanced reports showing which controls are affected by each detected change.

## What Was Built

### 1. Unified Monitoring Framework (`scripts/monitoring_shared.py`)

Created 590-line shared module providing the foundation for all monitoring source adapters:

**Shared Utilities (extracted from learn_monitor.py):**
- `fetch_page()` - HTTP fetching with retry logic and redirect tracking
- `normalize_content()` - HTML normalization with BeautifulSoup (strips scripts, nav, masks dates)
- `compute_hash()` - SHA-256 content hashing
- `classify_change()` - 4-tier classification (CRITICAL/HIGH/MEDIUM/NOISE) with pattern matching

**Control-to-URL Impact Mapping (new):**
- `find_affected_controls()` - Scans `docs/controls/pillar-*/` and `docs/playbooks/` for files referencing a URL
- Returns: list of {control_id, title, file_path} and list of {playbook_type, file_path, priority}
- Priority: CRITICAL for portal-walkthrough playbooks, HIGH for others

**Summary Table Generation (new):**
- `format_change_summary()` - Generates markdown table for quick scanning
- Columns: #, URL (shortened), Classification, Affected Controls, Action Required
- Action based on priority: "Update portal-walkthrough" (CRITICAL), "Review and update" (HIGH), etc.

**Unified State Management (new architecture):**
- Single `data/monitor-state.json` with source-keyed sections:
  ```json
  {
    "version": 1,
    "sources": {
      "learn": { "last_run": "...", "urls": {...} },
      "regulatory-federal-register": { "last_run": "...", "entries": {...} }
    }
  }
  ```
- `load_state()` / `save_state_atomic()` - Unified state loading with atomic writes
- `get_source_state()` / `set_source_state()` - Helper methods for source-specific state access
- **Backward compatibility:** Automatically migrates old `learn-monitor-state.json` on first load

**Unified Report Format Helpers:**
- `generate_report_header()` - Standard header with title, date, metadata
- `generate_executive_summary()` - Tier counts table (CRITICAL/HIGH/MEDIUM/NOISE)
- `write_report()` - Write to `reports/monitoring/` with atomic operations

### 2. Refactored Learn Monitor (`scripts/learn_monitor.py`)

Converted from standalone script to first source adapter using shared framework:

**Before refactor:** 857 lines with inline implementations
**After refactor:** 579 lines importing from monitoring_shared

**Changes:**
- Replaced inline `fetch_page()`, `normalize_content()`, `compute_hash()`, `classify_change()` with imports
- Replaced inline state management with unified state helpers
- Updated state file path: `data/learn-monitor-state.json` → `data/monitor-state.json`
- Updated report directory: `reports/learn-changes/` → `reports/monitoring/`
- Added source key constant: `SOURCE_KEY = "learn"`
- Report generation now uses shared helpers (`generate_report_header()`, `generate_executive_summary()`)

**Preserved:**
- All CLI arguments (--dry-run, --limit, --verbose, --debug, --url)
- Exit codes (0 = no changes, 1 = changes detected, 2 = error)
- Watchlist parsing logic (microsoft-learn-urls.md)
- URL entry data classes
- Debug single-URL mode

### 3. Enhanced Report Format

Reports now include control-to-URL impact mapping:

**Structure:**
1. **Header** - Title, date, URLs checked
2. **Executive Summary** - Tier counts (CRITICAL: N, HIGH: N, MEDIUM: N, NOISE: N)
3. **Change Summary Table** - Quick-scan format:
   | # | URL | Classification | Affected Controls | Action Required |
   |---|-----|----------------|-------------------|-----------------|
   | 1 | .../dlp-policies | CRITICAL | 1.3, 1.5 | Update portal-walkthrough |
4. **Detailed Changes** - For CRITICAL/HIGH only:
   - URL (full)
   - Classification badge
   - **Affected Controls** - Lists control IDs and titles that reference this URL
   - **Affected Playbooks** - Lists playbook paths with priority indicators (⚠️ CRITICAL, ℹ️ HIGH)
   - **What Changed** - Unified diff (truncated to 100 lines)
5. **Redirects** - URL redirects detected
6. **Errors** - HTTP errors or fetch failures
7. **MEDIUM/NOISE** - Collapsed list (URLs only, no diffs)

**Example output:**
```markdown
## Change Summary (Quick Scan)

| # | URL | Classification | Affected Controls | Action Required |
|---|-----|----------------|-------------------|-----------------|
| 1 | dlp-policies | CRITICAL | 1.3, 1.5 | Update portal-walkthrough |

## CRITICAL: Playbook Updates Required

### 1. DLP Policies Documentation

**Affected Controls:**
- Control 1.3: Data Loss Prevention for AI Agents
  - File: `controls/pillar-1-security/1.3-dlp-for-ai-agents.md`
- Control 1.5: Connector Governance
  - File: `controls/pillar-1-security/1.5-connector-governance.md`

**Affected Playbooks:**
- ⚠️ `playbooks/control-implementations/1.3/portal-walkthrough.md` (CRITICAL)
- ℹ️ `playbooks/control-implementations/1.3/powershell-setup.md` (HIGH)
```

### 4. Updated GitHub Workflow

Updated `.github/workflows/learn-monitor.yml` for unified architecture:

**Changes:**
- Baseline detection: checks for both `data/monitor-state.json` OR `data/learn-monitor-state.json` (migration support)
- Report path: `reports/learn-changes/` → `reports/monitoring/`
- State file references: `learn-monitor-state.json` → `monitor-state.json`
- PR description notes: "unified state for all monitoring sources" and "control-to-URL impact mapping"

**Preserved:**
- All workflow triggers (daily schedule, manual dispatch)
- PR creation logic (Sunday baseline OR changes detected)
- AI-assisted review instructions (`/review-learn-changes`)
- Comment with HIGH priority changes

## Deviations from Plan

**None.** Plan executed exactly as written.

Both tasks completed:
1. ✅ Create unified monitoring framework in monitoring_shared.py
2. ✅ Enhance change report format with control mapping and summary+diff

## Technical Decisions

### 1. Atomic State File Writes

**Decision:** Use temp file + rename pattern in `save_state_atomic()`

**Implementation:**
```python
with tempfile.NamedTemporaryFile(dir=state_path.parent, delete=False) as f:
    json.dump(state, f)
    temp_path = f.name
Path(temp_path).replace(state_path)  # Atomic on POSIX
```

**Rationale:**
- Prevents corruption if script interrupted during write
- Critical for CI/CD workflows where interrupts are common
- Creates `.json.backup` before overwriting (best-effort recovery)

### 2. String Path Handling

**Decision:** Convert string paths to Path objects in state management functions

**Implementation:**
```python
def load_state(state_path):
    state_path = Path(state_path) if not isinstance(state_path, Path) else state_path
```

**Rationale:**
- Allows both `Path` objects and strings for flexibility
- Prevents `AttributeError: 'str' object has no attribute 'parent'`
- Maintains type safety for pathlib operations

### 3. Migration on First Load

**Decision:** Migrate old state format transparently during `load_state()`

**Implementation:**
```python
old_state_path = state_path.parent / "learn-monitor-state.json"
if not state_path.exists() and old_state_path.exists():
    print(f"Migrating old state file from {old_state_path} to unified format...")
    old_state = json.loads(old_state_path.read_text())
    return {"version": 1, "sources": {"learn": old_state}}
```

**Rationale:**
- Zero disruption for existing deployments
- Preserves baseline established in previous runs
- Old file remains untouched (can be manually deleted later)
- Migration happens once per environment

### 4. Control-to-URL Scanning Strategy

**Decision:** Scan both `docs/controls/` and `docs/playbooks/` directories

**Implementation:**
```python
# Scan controls
for pillar_dir in (docs_dir / 'controls').glob('pillar-*'):
    for control_file in pillar_dir.glob('*.md'):
        if url in control_file.read_text():
            affected['controls'].append({...})

# Scan playbooks
for control_dir in (docs_dir / 'playbooks' / 'control-implementations').glob('*'):
    for playbook_file in control_dir.glob('*.md'):
        if url in playbook_file.read_text():
            priority = 'CRITICAL' if playbook_file.stem == 'portal-walkthrough' else 'HIGH'
            affected['playbooks'].append({...})
```

**Rationale:**
- Controls: Determines if change affects framework specifications
- Playbooks: Determines if change affects implementation guides
- Priority CRITICAL for portal-walkthrough: UI changes break step-by-step instructions
- Priority HIGH for other playbooks: May require review but less urgent

## Testing Results

### Import Verification
```bash
PYTHONPATH=. python3 -c "from scripts.monitoring_shared import fetch_page, normalize_content, compute_hash, classify_change, save_state_atomic, load_state, find_affected_controls, format_change_summary, get_source_state, set_source_state; print('All imports OK')"
# Result: All imports OK ✅
```

### Learn Monitor Execution
```bash
python3 scripts/learn_monitor.py --dry-run --limit 2
# Result: Exit code 0 (no changes) ✅
# Note: "Migrating old state file from data/learn-monitor-state.json to unified format..." ✅
```

### Control-to-URL Mapping
```bash
python3 -c "from scripts.monitoring_shared import find_affected_controls; affected = find_affected_controls('https://learn.microsoft.com/en-us/power-platform/admin/database-security', Path('docs')); print(len(affected['controls']))"
# Result: 2 controls found (1.1, 2.8) ✅
```

### Summary Table Generation
```bash
# Tested with mock change objects
# Result: Markdown table with shortened URLs, affected controls, action required ✅
```

### State Migration
```bash
# First run after refactor migrated learn-monitor-state.json → monitor-state.json
# Verified: 209 URLs preserved, last_run timestamp preserved, schema_version maintained
```

## Next Phase Readiness

**Plan 08-02 (Regulatory Monitor)** can now:
1. Import shared utilities from `monitoring_shared.py`
2. Use unified state format (add source key: `"regulatory-federal-register"`, `"regulatory-finra"`, etc.)
3. Use shared report helpers for consistent formatting
4. Leverage same classification tiers (CRITICAL/HIGH/MEDIUM/NOISE)
5. Write reports to same `reports/monitoring/` directory

**Architecture established:**
- ✅ Base framework for all monitoring sources
- ✅ Unified state management
- ✅ Unified report format
- ✅ Control-to-URL impact mapping
- ✅ Classification system
- ✅ Atomic state writes

**Remaining for Plan 08-02:**
- Add regulatory source adapters (Federal Register, FINRA, state legislatures)
- Implement source-specific fetch logic (RSS/Atom feeds, HTML scraping)
- Implement regulatory-specific classification patterns
- Configure cadence per source (daily for Learn, weekly for regulatory)

## Files Changed

| File | Lines | Change Type | Description |
|------|-------|-------------|-------------|
| `scripts/monitoring_shared.py` | 590 | Created | Unified monitoring framework with 10+ exported functions |
| `scripts/learn_monitor.py` | 579 | Refactored | Converted to source adapter using shared framework |
| `.github/workflows/learn-monitor.yml` | 215 | Modified | Updated paths for unified state and reports directory |

**Total:** 1 new file, 2 modified files

## Commits

| Commit | Message |
|--------|---------|
| 193b4f4 | feat(08-01): create unified monitoring framework |
| 3a89e61 | feat(08-01): enhance report format with control mapping and unified directories |

## Metrics

- **Duration:** 7 minutes
- **Tasks completed:** 2/2
- **Verifications passed:** 7/7
- **Exit code:** 0 (success)
- **State migration:** Successful (209 URLs migrated from old format)
- **Backward compatibility:** 100% (all existing CLI arguments and exit codes preserved)

## Success Criteria Met

- ✅ Unified monitoring framework (`monitoring_shared.py`) provides shared state format, report format, classification, and utilities for all source types
- ✅ Learn Monitor refactored as first source adapter using the unified framework
- ✅ Change reports show WHICH controls are affected by each detected change (not just that a URL changed)
- ✅ Report format includes both quick-scan summary table and detailed diff sections
- ✅ Architecture is ready for Plan 08-02 to add regulatory sources as additional adapters within the same system

---

**Plan Status:** COMPLETE ✅
**Phase Status:** 1/3 plans complete
**Next:** Plan 08-02 (Regulatory Monitor implementation)
