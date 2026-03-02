# Microsoft Learn Documentation Monitor - How It Works

This guide explains how the automated Microsoft Learn documentation monitoring system works, when it runs, and how to use it locally.

---

## Quick Reference

| Question | Answer |
|----------|--------|
| When does it run? | **Daily at 6:00 AM UTC** via GitHub Actions |
| When is a PR created? | **Every Sunday** (weekly baseline) OR **when changes are detected** |
| Where are changes stored? | `data/monitor-state.json` (unified state), `reports/monitoring/learn-changes-*.md` (reports) |
| How to test locally? | `python scripts/learn_monitor.py --dry-run --limit 5` |

---

## System Overview

The Learn monitor tracks **~207 Microsoft Learn URLs** from the [Microsoft Learn URLs](microsoft-learn-urls.md) watchlist and detects content changes that may require updates to framework documentation.

**Part of Unified Monitoring System:** The Learn Monitor is one source adapter within the broader unified monitoring architecture. See [monitoring-architecture.md](monitoring-architecture.md) for the complete system design.

```
+---------------------------------------------------------------------+
|                      How the Learn Monitor Works                    |
+---------------------------------------------------------------------+
|                                                                     |
|  1. WATCHLIST                    2. FETCH & HASH                    |
|  +---------------------+         +---------------------+            |
|  | microsoft-learn-    |   -->   | For each URL:       |            |
|  | urls.md (209 URLs)  |         | - Fetch HTML        |            |
|  +---------------------+         | - Extract content   |            |
|                                  | - Compute SHA-256   |            |
|                                  +---------------------+            |
|                                           |                         |
|                                           v                         |
|  3. COMPARE                      4. CLASSIFY CHANGES                |
|  +---------------------+         +---------------------+            |
|  | data/monitor-       |   -->   | meaningful/minor/   |            |
|  | state.json (unified)|         | noise               |            |
|  | (previous hashes)   |         +---------------------+            |
|  +---------------------+                  |                         |
|                                           v                         |
|  5. OUTPUT                       6. CI TRIGGERS PR                  |
|  +---------------------+         +---------------------+            |
|  | reports/monitoring/ |         | Exit code 1 OR      |            |
|  | learn-changes-*.md  |         | Sunday = Create PR  |            |
|  +---------------------+         +---------------------+            |
|                                                                     |
+---------------------------------------------------------------------+
|  Framework: monitoring_shared.py provides state, classification,   |
|  control mapping, and report generation capabilities               |
+---------------------------------------------------------------------+
```

---

## Key Files

| File | Purpose |
|------|---------|
| `scripts/learn_monitor.py` | Learn Monitor source adapter |
| `scripts/monitoring_shared.py` | Unified monitoring framework (state, classification, control mapping) |
| `scripts/regulatory_monitor.py` | Regulatory source adapter (Federal Register, FINRA) |
| `.github/workflows/learn-monitor.yml` | GitHub Actions workflow for Learn Monitor |
| `docs/reference/microsoft-learn-urls.md` | Watchlist of 209 URLs to monitor |
| `data/monitor-state.json` | Unified state file (content hashes for all sources) |
| `reports/monitoring/learn-changes-*.md` | Learn change reports |
| `reports/monitoring/regulatory-changes-*.md` | Regulatory change reports |

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

### State File (`data/monitor-state.json`)

The unified state file stores SHA-256 content hashes for all monitored sources (Learn + Regulatory):

```json
{
  "last_updated": "2026-02-04T06:00:00Z",
  "sources": {
    "learn": {
      "urls": {
        "https://learn.microsoft.com/...": {
          "hash": "sha256:abc123...",
          "last_checked": "2026-02-04T06:00:00Z",
          "title": "Managed Environments Overview"
        }
      }
    },
    "regulatory": { ... }
  }
}
```

### Change Reports (`reports/monitoring/learn-changes-YYYY-MM-DD.md`)

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
ls -la reports/monitoring/learn-changes-*.md
```

---

## Responding to Change Alerts

When the monitor detects changes and creates a PR:

### Option 1: AI-Assisted Review (Recommended)

Use the `/review-learn-changes` Claude Code skill for automated analysis:

```bash
# 1. Checkout the PR branch
gh pr checkout {PR_NUMBER}

# 2. Run the review skill in Claude Code
/review-learn-changes

# 3. Claude will:
#    - Read and categorize all changes
#    - Propose specific documentation edits
#    - Apply edits with your confirmation
#    - Run validation (mkdocs build --strict)

# 4. Commit and push the documentation updates
git add .
git commit -m "docs: Apply Learn Monitor updates"
git push

# 5. Merge the PR
gh pr merge {PR_NUMBER} --squash
```

### Option 2: Manual Review

1. **Review the change report** in `reports/monitoring/`
2. **Assess the classification** (CRITICAL, HIGH, MEDIUM, NOISE)
3. **Update affected documentation:**
   - CRITICAL: Update playbooks immediately
   - HIGH: Update controls and playbooks
   - MEDIUM: Review and update if needed
   - NOISE: No action required
4. **Merge the PR** to update the baseline state

### PR Labels

| Label | Meaning |
|-------|---------|
| `learn-watch` | All Learn Monitor PRs |
| `needs-review` | Changes detected that may require documentation updates |
| `documentation` | Documentation-related PR |
| `automated` | Created by automation |

---

## End-to-End Verification Procedure

To verify the Learn Monitor works correctly, follow these steps:

### Step 1: Establish Baseline (or use existing)

```bash
# If no state file exists for Learn URLs, create baseline
python3 scripts/learn_monitor.py --limit 5

# Expected: "Baseline established. No report generated on first run."
# State saved to: data/monitor-state.json (unified state file)
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
with open('data/monitor-state.json', 'r') as f:
    state = json.load(f)
first_url = list(state['sources']['learn']['urls'].keys())[0]
state['sources']['learn']['urls'][first_url]['normalized_content'] = 'OLD CONTENT'
state['sources']['learn']['urls'][first_url]['hash'] = 'sha256:fake_hash'
with open('data/monitor-state.json', 'w') as f:
    json.dump(state, f, indent=2)
"

# Run monitor - should detect change
python3 scripts/learn_monitor.py --limit 5

# Expected: "CHANGED: meaningful" and report generated
```

### Step 4: Verify Report Created

```bash
ls -la reports/monitoring/learn-changes-*.md
cat reports/monitoring/learn-changes-*.md
```

### Step 5: Restore State File

```bash
git checkout data/monitor-state.json
rm reports/monitoring/learn-changes-*.md
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
| No state file exists | Monitor hasn't run yet | Run `python scripts/learn_monitor.py` to create baseline (stored in unified `data/monitor-state.json`) |
| URL fetch failures | Network issues or URL changed | Check URL validity, retry later |
| Too many false positives | NOISE detection needs tuning | Review patterns in `monitoring_shared.py` classification logic |
| Workflow not running | GitHub Actions disabled | Check repository Actions settings |
| State file corrupted | JSON parsing errors | Restore from backup or delete and re-run monitor (establishes new baseline) |

---

## Related Documentation

- **Monitoring Architecture:** [monitoring-architecture.md](monitoring-architecture.md) - Comprehensive unified monitoring system documentation
- **AI-Assisted Review:** [learn-monitor-ai-enhancement.md](learn-monitor-ai-enhancement.md) - AI-assisted review implementation guide
- **Microsoft Learn URLs:** [microsoft-learn-urls.md](microsoft-learn-urls.md) - The watchlist of monitored URLs (~207 URLs)
- **Claude Code Skill:** `.claude/skills/review-learn-changes.md` - User-invocable skill for reviewing changes
- **Repository Instructions:** `.claude/CLAUDE.md` - Complete repository instructions (in project root)

---

*FSI Agent Governance Framework v1.2 - February 2026*
