# Microsoft Learn Documentation Monitor - How It Works

This guide explains how the automated Microsoft Learn documentation monitoring system works, when it runs, and how to use it locally.

---

## Quick Reference

| Question | Answer |
|----------|--------|
| When does it run? | **Daily at 6:00 AM UTC** via GitHub Actions |
| When is a PR created? | **Every Sunday** (weekly baseline) OR **when changes are detected** |
| Where are changes stored? | `data/learn-monitor-state.json` (content hashes), `reports/learn-changes/*.md` (reports) |
| How to test locally? | `python scripts/learn_monitor.py --dry-run --limit 5` |

---

## System Overview

The Learn monitor tracks **191 Microsoft Learn URLs** from the [Microsoft Learn URLs](microsoft-learn-urls.md) watchlist and detects content changes that may require updates to framework documentation.

```
+---------------------------------------------------------------------+
|                      How the Monitor Works                          |
+---------------------------------------------------------------------+
|                                                                     |
|  1. WATCHLIST                    2. FETCH & HASH                    |
|  +---------------------+         +---------------------+            |
|  | microsoft-learn-    |   -->   | For each URL:       |            |
|  | urls.md (191 URLs)  |         | - Fetch HTML        |            |
|  +---------------------+         | - Extract content   |            |
|                                  | - Compute SHA-256   |            |
|                                  +---------------------+            |
|                                           |                         |
|                                           v                         |
|  3. COMPARE                      4. CLASSIFY CHANGES                |
|  +---------------------+         +---------------------+            |
|  | data/learn-monitor- |   -->   | meaningful/minor/   |            |
|  | state.json          |         | noise               |            |
|  | (previous hashes)   |         +---------------------+            |
|  +---------------------+                  |                         |
|                                           v                         |
|  5. OUTPUT                       6. CI TRIGGERS PR                  |
|  +---------------------+         +---------------------+            |
|  | reports/learn-      |         | Exit code 1 OR      |            |
|  | changes/*.md        |         | Sunday = Create PR  |            |
|  +---------------------+         +---------------------+            |
|                                                                     |
+---------------------------------------------------------------------+
```

---

## Key Files

| File | Purpose |
|------|---------|
| `scripts/learn_monitor.py` | Main Python script |
| `.github/workflows/learn-monitor.yml` | GitHub Actions workflow |
| `docs/reference/microsoft-learn-urls.md` | Watchlist of 191 URLs to monitor |
| `data/learn-monitor-state.json` | Stores content hashes (created on first run) |
| `reports/learn-changes/*.md` | Change detection reports |

---

## Change Classification

The monitor classifies changes into categories to prioritize review:

| Classification | Triggers | Priority |
|---------------|----------|----------|
| **CRITICAL** | Affects `portal-walkthrough.md` playbooks | Immediate update required |
| **HIGH** | UI navigation steps, policy language, deprecations | Review and update |
| **MEDIUM** | General content updates | Review optional |
| **NOISE** | Metadata, dates, formatting | Ignored |

### Patterns Detected as Meaningful

The monitor looks for patterns that indicate substantive changes:

**UI Navigation (affects playbooks):**

- Navigation keywords: `click`, `select`, `go to`, `navigate`
- Portal references: `Admin center`, `portal`, `Power Platform`, `Purview`
- UI elements: `button`, `menu`, `tab`, `panel`, `dialog`, `blade`

**Policy/Compliance (affects controls):**

- Callout boxes: `Important:`, `Warning:`, `Note:`, `Caution:`
- Requirement language: `required`, `must`, `should not`, `prohibited`
- Compliance terms: `compliance`, `audit`, `retention`, `DLP`

**Deprecation (requires action):**

- Lifecycle terms: `deprecated`, `removed`, `no longer`, `retired`
- Release stages: `preview`, `GA`, `generally available`

---

## GitHub Actions Workflow

The workflow (`.github/workflows/learn-monitor.yml`) runs:

- **Schedule:** Daily at 6:00 AM UTC (`cron: '0 6 * * *'`)
- **Manual:** Can be triggered via `workflow_dispatch`

### PR Creation Logic

```
IF (today is Sunday) OR (exit_code == 1):
    Create PR with changes
ELSE:
    No PR (just update state)
```

### Baseline vs. Change Detection Runs

The workflow detects whether this is a **baseline run** (first successful execution) or a **change detection run** (subsequent executions):

| Run Type | Condition | PR Body Content |
|----------|-----------|-----------------|
| **Baseline** | State file doesn't exist before script runs | Explains this establishes the baseline; no change reports expected; simplified 2-step review |
| **Change Detection** | State file exists | Full instructions to check reports and update affected documentation |

**How it works:**

```bash
# Before running the monitor script:
if [ ! -f "data/learn-monitor-state.json" ]; then
    echo "is_baseline=true"  # First run
else
    echo "is_baseline=false"  # Subsequent run
fi
```

This ensures PR reviewers see appropriate instructions based on the run type.

**Exit Codes:**

| Code | Meaning | Action |
|------|---------|--------|
| `0` | No meaningful changes detected | No PR created |
| `1` | Meaningful changes detected | PR created |
| `2` | Error during execution | Check workflow logs |

---

## Testing Locally

### 1. Quick Test (5 URLs, no state changes)

```bash
python scripts/learn_monitor.py --dry-run --limit 5
```

### 2. Test with Verbose Output

```bash
python scripts/learn_monitor.py --dry-run --limit 10 --verbose
```

### 3. Debug a Single URL

```bash
python scripts/learn_monitor.py --url "https://learn.microsoft.com/en-us/power-platform/admin/managed-environment-overview"
```

### 4. Full Run (creates state file)

```bash
# First run establishes baseline (no report generated)
python scripts/learn_monitor.py

# Subsequent runs detect changes
python scripts/learn_monitor.py
```

---

## Understanding the Output

### State File (`data/learn-monitor-state.json`)

The state file stores SHA-256 content hashes for each monitored URL:

```json
{
  "https://learn.microsoft.com/...": {
    "hash": "abc123...",
    "last_checked": "2026-01-24T06:00:00Z",
    "title": "Managed Environments Overview"
  }
}
```

### Change Reports (`reports/learn-changes/learn-changes-YYYY-MM-DD.md`)

Reports are generated when changes are detected:

- Date and summary of changes
- List of affected URLs with classification
- Diff snippets showing what changed
- Recommended actions for each change

---

## Verifying the Monitor is Working

### Option 1: Check GitHub Actions

```bash
gh run list --workflow=learn-monitor.yml --limit 5
```

### Option 2: Run Locally

```bash
# Dry run (no state changes)
python scripts/learn_monitor.py --dry-run --limit 5 --verbose

# Full baseline run
python scripts/learn_monitor.py --limit 20
```

### Option 3: Check for Recent Reports

```bash
ls -la reports/learn-changes/
```

---

## Responding to Change Alerts

When the monitor detects changes and creates a PR:

1. **Review the change report** in `reports/learn-changes/`
2. **Assess the classification** (CRITICAL, HIGH, MEDIUM, NOISE)
3. **Update affected documentation:**
   - CRITICAL: Update playbooks immediately
   - HIGH: Update controls and playbooks
   - MEDIUM: Review and update if needed
   - NOISE: No action required
4. **Merge the PR** to update the baseline state

---

## End-to-End Verification Procedure

To verify the Learn Monitor works correctly, follow these steps:

### Step 1: Establish Baseline (or use existing)

```bash
# If no state file exists, create baseline
python3 scripts/learn_monitor.py --limit 5

# Expected: "Baseline established. No report generated on first run."
```

### Step 2: Run Again (No Changes Expected)

```bash
python3 scripts/learn_monitor.py --limit 5

# Expected: "Meaningful changes: 0" - No report generated
```

### Step 3: Simulate a Content Change

```bash
# Inject fake old content to trigger change detection
python3 -c "
import json
with open('data/learn-monitor-state.json', 'r') as f:
    state = json.load(f)
first_url = list(state['urls'].keys())[0]
state['urls'][first_url]['normalized_content'] = 'OLD CONTENT'
state['urls'][first_url]['content_hash'] = 'sha256:fake_hash'
with open('data/learn-monitor-state.json', 'w') as f:
    json.dump(state, f, indent=2)
"

# Run monitor - should detect change
python3 scripts/learn_monitor.py --limit 5

# Expected: "CHANGED: meaningful" and report generated
```

### Step 4: Verify Report Created

```bash
ls -la reports/learn-changes/
cat reports/learn-changes/learn-changes-*.md
```

### Step 5: Restore State File

```bash
git checkout data/learn-monitor-state.json
rm reports/learn-changes/learn-changes-*.md
```

### Verification Summary

| Step | Expected Result |
|------|-----------------|
| Baseline run | "Baseline established. No report generated." |
| No-change run | "Meaningful changes: 0" |
| Simulated change | "CHANGED: meaningful" + report generated |
| Report content | Shows diff, affected controls, priority |

---

## Troubleshooting

| Issue | Cause | Resolution |
|-------|-------|------------|
| No state file exists | Monitor hasn't run yet | Run `python scripts/learn_monitor.py` to create baseline |
| URL fetch failures | Network issues or URL changed | Check URL validity, retry later |
| Too many false positives | NOISE detection needs tuning | Review patterns in `learn_monitor.py` |
| Workflow not running | GitHub Actions disabled | Check repository Actions settings |

---

## Related Documentation

- [Microsoft Learn URLs](microsoft-learn-urls.md) - The watchlist of monitored URLs
- `.claude/CLAUDE.md` - Repository instructions including monitor usage (in project root)

---

*FSI Agent Governance Framework v1.2 - January 2026*
