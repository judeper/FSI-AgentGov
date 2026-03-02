---
name: review-learn-changes
description: Review unified monitoring system reports (Learn or Regulatory) and draft documentation updates. Use when monitoring PRs are created with detected changes from Microsoft Learn or regulatory sources.
allowed-tools:
  - Read
  - Glob
  - Grep
  - Edit
  - Write
  - Bash
  - Task
user-invocable: true
---

# Review Monitoring Changes Skill

This skill analyzes reports from the unified monitoring system (Microsoft Learn + Regulatory sources) and drafts updates to FSI-AgentGov documentation.

## When to Use

- After a monitoring PR is created (labels: `learn-watch` or `monitoring`)
- When `reports/learn-changes/` contains HIGH priority changes
- To prepare documentation updates for human review

## Workflow

### Step 0.5: Determine Report Type

First, identify which type of report to review:

```bash
# List recent reports
ls -la reports/learn-changes/ | tail -10
```

**Report Types:**

| Report Type | Pattern | Purpose |
|-------------|---------|---------|
| Learn Changes | `learn-changes-*.md` | Microsoft Learn documentation updates |
| Regulatory Changes | `regulatory-changes-*.md` | Federal Register + FINRA notices |

**Default behavior:** Review the most recent report of either type.

**User can specify:** "Review the Learn changes" or "Review the regulatory changes"

### Step 1: Find the Latest Change Report

```bash
ls -la reports/learn-changes/ | tail -5
```

Or if given a PR number:
```bash
gh pr view {PR_NUMBER} --json files -q '.files[].path'
```

### Step 2: Read and Parse the Change Report

Read the change report file. The parsing approach differs by report type:

#### For Learn Change Reports (`learn-changes-*.md`):

Look for:

1. **Summary statistics** at the top (Total URLs, Meaningful Changes count)
2. **HIGH priority changes** - these are the ones to process
3. **Affected Controls** listed under each change
4. **Affected Playbooks** listed under each change
5. **What Changed** diff blocks showing the actual changes

#### For Regulatory Change Reports (`regulatory-changes-*.md`):

Look for:

1. **Executive Summary** with counts by category (CRITICAL, HIGH, MEDIUM, NOISE)
2. **CRITICAL/HIGH items** - these require review
3. **Potentially Affected Controls** suggested by keyword matching
4. **Source** (Federal Register agency or FINRA notice type)

### Step 3: Categorize Changes

#### For Learn Change Reports

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

#### For Regulatory Change Reports

For each CRITICAL/HIGH regulatory item:

| Category | Pattern | Action |
|----------|---------|--------|
| **AI_GOVERNANCE** | AI, machine learning, automated decision-making | Review suggested controls, validate mapping |
| **RECORDKEEPING** | Records, retention, books and records | Review suggested controls, validate mapping |
| **SUPERVISION** | Supervision, review, monitoring | Review suggested controls, validate mapping |
| **DATA_PROTECTION** | Privacy, data security, PII | Review suggested controls, validate mapping |
| **CONTENT_MODERATION** | Content review, harmful content | Review suggested controls, validate mapping |
| **OUT_OF_SCOPE** | Not applicable to AI agents | No action needed |

**IMPORTANT:** Do NOT auto-draft edits for regulatory content. Regulatory changes require human review per CONTRIBUTING.md safety rules. Instead, create a triage summary showing which items need detailed human review.

### Step 4: For Each Actionable Change

#### For Learn Changes (Auto-Draft Eligible):

1. **Read the affected control/playbook** to understand current content
2. **Analyze the diff** to determine what specifically changed
3. **Draft the edit** following these rules:

#### For Regulatory Changes (Triage Only):

1. **Read the suggested affected controls** to verify the keyword matching was accurate
2. **Assess relevance** - is this truly applicable to AI agent governance?
3. **Create triage summary** - which items need human review vs. can be dismissed as out-of-scope
4. **Do NOT draft edits** - regulatory content requires human review

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

Before making any edits, output a summary. The format differs by report type:

#### For Learn Change Reports:

```markdown
## Monitoring System AI Assist - Learn Changes Summary

**Report Analyzed:** reports/learn-changes/learn-changes-YYYY-MM-DD.md
**Date:** YYYY-MM-DD
**Report Type:** Microsoft Learn Documentation

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

#### For Regulatory Change Reports:

```markdown
## Monitoring System AI Assist - Regulatory Changes Triage

**Report Analyzed:** reports/learn-changes/regulatory-changes-YYYY-MM-DD.md
**Date:** YYYY-MM-DD
**Report Type:** Regulatory (Federal Register + FINRA)

### Requires Human Review

| # | Item | Source | Suggested Controls | Relevance Assessment |
|---|------|--------|-------------------|---------------------|
| 1 | SEC Proposed Rule on AI Oversight | SEC | 2.6, 2.15, 3.5 | HIGH - directly impacts agent supervision |
| 2 | FINRA Notice on Recordkeeping | FINRA | 3.1, 3.2 | MEDIUM - may affect audit requirements |

### Out of Scope (Dismiss)

| # | Item | Reason |
|---|------|--------|
| 1 | OCC Bank Merger Policy | Not applicable to AI agent governance |
| 2 | CFTC Position Limits | Not applicable to M365 AI agents |

### Next Steps

Items marked "Requires Human Review" need detailed analysis to determine if framework updates are needed. Do NOT auto-edit regulatory content per CONTRIBUTING.md safety rules.
```

### Step 6: Apply Updates (Learn Changes Only)

**For Learn changes:** Ask the user: "Do you want me to apply these {N} updates?"

If yes:
1. Use the Edit tool to make each change
2. After all edits, run validation:

```bash
mkdocs build --strict 2>&1 | head -50
```

**For Regulatory changes:** Skip this step. Regulatory items require human analysis and decision-making per CONTRIBUTING.md safety rules. The triage summary from Step 5 is the deliverable.

### Step 7: Handle URL Redirects (Learn Changes Only)

If the Learn change report contains URL redirects:

1. Read `docs/reference/microsoft-learn-urls.md`
2. Update each redirected URL to its new target
3. Note: Some redirects add `?view=...` which can be ignored

Regulatory reports don't have URL redirects - skip this step.

### Step 8: Final Summary

Output depends on report type:

#### For Learn Changes (Auto-Edited):
- Number of files modified
- Validation status (pass/fail)
- Any issues encountered
- Recommendation for next steps (commit message, etc.)

#### For Regulatory Changes (Triaged):
- Number of items requiring human review
- Number of items dismissed as out-of-scope
- Recommendation: Review flagged items and determine if framework updates are needed

## Example Sessions

### Example 1: Learn Changes (Auto-Edit)

```
User: /review-learn-changes

Claude: I'll analyze the latest monitoring report.

[Reads reports/learn-changes/learn-changes-2026-02-01.md]

Found 31 HIGH priority Learn changes affecting 15 controls.

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

### Example 2: Regulatory Changes (Triage Only)

```
User: Review the regulatory changes

Claude: I'll analyze the latest regulatory monitoring report.

[Reads reports/learn-changes/regulatory-changes-2026-02-04.md]

Found 4 regulatory items. All classified as NOISE.

## Triage Summary

### Out of Scope (Dismiss)

| # | Item | Reason |
|---|------|--------|
| 1 | SEC - Fixed Income Clearing Corp rule | Not applicable to AI agent governance |
| 2 | CBOE Exchange trading rule | Not applicable to AI agent governance |
| 3 | NYSE fee schedule update | Not applicable to AI agent governance |
| 4 | FINRA trade reporting notice | Not applicable to AI agent governance |

All items are out of scope for the FSI Agent Governance Framework. No action needed.
```

## Safety Rules

1. **Never auto-commit** - all changes require human review
2. **Never edit regulatory language** (FINRA/SEC/OCC/Federal Register content) without explicit approval
3. **Regulatory changes = triage only** - do NOT auto-draft edits for regulatory content per CONTRIBUTING.md
4. **Stop and ask** if unsure about a change
5. **Preserve existing info boxes** - add new ones, don't remove
6. **Track all changes** for audit trail

## Related Files

- `docs/reference/monitoring-architecture.md` - Unified monitoring system architecture
- `docs/reference/learn-monitor-guide.md` - Learn Monitor documentation
- `docs/reference/learn-monitor-ai-enhancement.md` - AI-assisted review implementation
- `scripts/monitoring_shared.py` - Unified monitoring framework
- `scripts/learn_monitor.py` - Learn source adapter
- `scripts/regulatory_monitor.py` - Regulatory source adapter
- `CONTRIBUTING.md` - Language guidelines
