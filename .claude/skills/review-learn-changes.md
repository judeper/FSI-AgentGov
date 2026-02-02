---
name: review-learn-changes
description: Review Learn Monitor change report and draft documentation updates. Use when a Learn Monitor PR is created with detected Microsoft Learn documentation changes.
allowed-tools:
  - Read
  - Glob
  - Grep
  - Edit
  - Write
  - Bash
  - Task
  - TodoWrite
user-invocable: true
---

# Review Learn Changes Skill

This skill analyzes Microsoft Learn documentation change reports and drafts updates to FSI-AgentGov documentation.

## When to Use

- After a Learn Monitor PR is created (label: `learn-watch`)
- When `reports/learn-changes/learn-changes-*.md` contains HIGH priority changes
- To prepare documentation updates for human review

## Workflow

### Step 1: Find the Latest Change Report

```bash
ls -la reports/learn-changes/ | tail -5
```

Or if given a PR number:
```bash
gh pr view {PR_NUMBER} --json files -q '.files[].path'
```

### Step 2: Read and Parse the Change Report

Read the change report file. Look for:

1. **Summary statistics** at the top (Total URLs, Meaningful Changes count)
2. **HIGH priority changes** - these are the ones to process
3. **Affected Controls** listed under each change
4. **Affected Playbooks** listed under each change
5. **What Changed** diff blocks showing the actual changes

### Step 3: Categorize Changes

For each HIGH priority change, categorize it:

| Category | Pattern | Action |
|----------|---------|--------|
| **DATE_UPDATE** | Timeline/deadline changed | Update affected docs with new date |
| **UI_CHANGE** | Portal navigation, button names | Update portal-walkthrough.md |
| **FEATURE_GA** | "Preview" removed, "GA" added | Remove preview tags |
| **DEPRECATION** | "deprecated", "retired", "no longer" | Add warning callout |
| **NEW_DOC** | New page (diff starts with `+` only) | Add cross-reference |
| **URL_REDIRECT** | URL in redirects section | Update microsoft-learn-urls.md |
| **SCOPE_CHANGE** | Applicability changed (e.g., 21Vianet only) | Add scope clarification |
| **POLICY_CHANGE** | Compliance/regulatory language | FLAG for human review |
| **SKIP** | Formatting, minor wording | No action needed |

### Step 4: For Each Actionable Change

1. **Read the affected control/playbook** to understand current content
2. **Analyze the diff** to determine what specifically changed
3. **Draft the edit** following these rules:

#### Edit Rules

- **Minimal changes**: Only edit what's necessary
- **Preserve structure**: Don't reorganize or reformat
- **Use consistent language**: Follow CONTRIBUTING.md guidelines
- **Add info boxes for updates**: Use MkDocs admonitions

```markdown
!!! info "Updated February 2026"
    Microsoft extended the Sentinel Azure portal deprecation date from July 2026 to March 31, 2027.
```

- **Never edit regulatory language** without flagging for review
- **Cross-reference new docs** in "Related Resources" sections

### Step 5: Create Update Summary

Before making any edits, output a summary:

```markdown
## Learn Monitor AI Assist - Update Summary

**Report Analyzed:** reports/learn-changes/learn-changes-YYYY-MM-DD.md
**Date:** YYYY-MM-DD

### Proposed Updates

| # | Control/Playbook | Change Type | Proposed Edit |
|---|------------------|-------------|---------------|
| 1 | Control 3.9 | DATE_UPDATE | Update Sentinel deadline to March 31, 2027 |
| 2 | Control 1.19 | SCOPE_CHANGE | Add note about 21Vianet applicability |
| ... | ... | ... | ... |

### Flagged for Human Review

| # | Control/Playbook | Reason |
|---|------------------|--------|
| 1 | Control 2.12 | Policy language change detected |

### Skipped (No Action Needed)

- Change X: Minor wording (SKIP)
- Change Y: Formatting only (SKIP)
```

### Step 6: Apply Updates (with User Confirmation)

Ask the user: "Do you want me to apply these {N} updates?"

If yes:
1. Use the Edit tool to make each change
2. Track progress with TodoWrite
3. After all edits, run validation:

```bash
mkdocs build --strict 2>&1 | head -50
```

### Step 7: Handle URL Redirects

If the report contains URL redirects:

1. Read `docs/reference/microsoft-learn-urls.md`
2. Update each redirected URL to its new target
3. Note: Some redirects add `?view=...` which can be ignored

### Step 8: Final Summary

Output:
- Number of files modified
- Validation status (pass/fail)
- Any issues encountered
- Recommendation for next steps

## Example Session

```
User: /review-learn-changes

Claude: I'll analyze the latest Learn Monitor change report.

[Reads reports/learn-changes/learn-changes-2026-02-01.md]

Found 31 HIGH priority changes affecting 15 controls.

## Proposed Updates

| # | Control | Change Type | Proposed Edit |
|---|---------|-------------|---------------|
| 1 | Control 3.9 | DATE_UPDATE | Sentinel deadline: July 2026 → March 31, 2027 |
| 2 | Control 1.19 | SCOPE_CHANGE | Classic eDiscovery: Add 21Vianet scope note |
...

## Flagged for Human Review

| # | Control | Reason |
|---|---------|--------|
| 1 | Control 2.6 | New Model Risk Management guidance needs review |

Do you want me to apply the 12 automated updates?

User: Yes, apply them

Claude: [Applies edits using Edit tool]
[Runs mkdocs build --strict]

✓ Applied 12 updates across 8 files
✓ Build validation passed
⚠ 1 change flagged for your review (Control 2.6)

Recommendation: Review the changes, then commit with message:
"docs: Apply Learn Monitor updates from 2026-02-01 report"
```

## Safety Rules

1. **Never auto-commit** - all changes require human review
2. **Never edit FINRA/SEC/OCC language** without explicit approval
3. **Stop and ask** if unsure about a change
4. **Preserve existing info boxes** - add new ones, don't remove
5. **Track all changes** with TodoWrite for audit trail

## Related Files

- `docs/reference/learn-monitor-guide.md` - How the monitor works
- `docs/reference/learn-monitor-ai-enhancement.md` - This enhancement design
- `scripts/learn_monitor.py` - The detection script
- `CONTRIBUTING.md` - Language guidelines
