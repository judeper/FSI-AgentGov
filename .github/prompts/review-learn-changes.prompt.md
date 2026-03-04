---
name: "review-learn-changes"
description: "Review unified monitoring system reports (Learn or Regulatory) and draft documentation updates"
tools: ["read", "edit", "search", "execute"]
---

<objective>
Analyze reports from the unified monitoring system (Microsoft Learn + Regulatory sources) and draft updates to FSI-AgentGov documentation. For Learn changes, auto-draft edits to affected controls and playbooks. For Regulatory changes, produce a triage summary only — never auto-edit regulatory content.

This prompt handles both report types via the same invocation. The system detects which type of report is present and routes accordingly.
</objective>

<context>
Report locations (check both, prefer most recent):
@reports/monitoring/
@reports/learn-changes/

Reference files:
@docs/reference/microsoft-learn-urls.md
@docs/controls/CONTROL-INDEX.md
@CONTRIBUTING.md
</context>

<safety_rules>
**These rules are non-negotiable. Violating any of them is a workflow failure.**

1. **Never auto-commit** — all changes require explicit human approval
2. **Never auto-edit regulatory content** — regulatory changes produce triage summaries only, per CONTRIBUTING.md
3. **Stop and ask** if unsure about any change
4. **Preserve existing admonition boxes** — add new ones, do not remove existing
5. **Follow FSI language rules** — never use "ensures compliance", "guarantees", "will prevent", "eliminates risk"
6. **Validate after edits** — run `mkdocs build --strict` before presenting results
</safety_rules>

<process>

<step name="find_latest_report">
## Step 1: Find the Latest Change Report

Search for the most recent monitoring report:

```powershell
Get-ChildItem -Path reports/monitoring/, reports/learn-changes/ -Filter *.md -Recurse -ErrorAction SilentlyContinue | Sort-Object LastWriteTime -Descending | Select-Object -First 5
```

Or if the user specifies a PR number, read the PR files to find the report path.

**Report types** (identified by filename pattern):

| Pattern | Type | Workflow |
|---------|------|----------|
| `learn-changes-*.md` | Learn | Auto-draft eligible |
| `regulatory-changes-*.md` | Regulatory | Triage only |

Read the most recent report (or the one the user specifies).
</step>

<step name="parse_report">
## Step 2: Parse the Change Report

### For Learn Change Reports

Extract:
1. **Summary statistics** — Total URLs checked, Meaningful Changes count
2. **HIGH priority changes** — these are the actionable items
3. **Affected Controls** listed under each change
4. **Affected Playbooks** listed under each change
5. **What Changed** diff blocks showing actual content changes

### For Regulatory Change Reports

Extract:
1. **Executive Summary** with counts by severity (CRITICAL, HIGH, MEDIUM, NOISE)
2. **CRITICAL/HIGH items** — these require human review
3. **Potentially Affected Controls** from keyword matching
4. **Source** (Federal Register agency or FINRA notice type)
</step>

<step name="categorize_changes">
## Step 3: Categorize Each Change

### Learn Change Categories

| Category | Pattern | Action |
|----------|---------|--------|
| **DATE_UPDATE** | Timeline or deadline changed | Update affected docs with new date |
| **UI_CHANGE** | Portal navigation, button names, menu paths | Update portal-walkthrough.md |
| **FEATURE_GA** | "Preview" removed, "GA" added | Remove preview tags, update availability |
| **DEPRECATION** | "deprecated", "retired", "no longer available" | Add deprecation warning admonition |
| **NEW_DOC** | New page (diff is all additions) | Add cross-reference in related controls |
| **URL_REDIRECT** | URL in redirects section | Update microsoft-learn-urls.md |
| **SCOPE_CHANGE** | Applicability changed (e.g., 21Vianet only) | Add scope clarification |
| **POLICY_CHANGE** | Compliance or regulatory language changed | FLAG for human review — do not auto-edit |
| **SKIP** | Formatting, minor wording, metadata date | No action needed |

### Regulatory Change Categories

| Category | Pattern | Action |
|----------|---------|--------|
| **AI_GOVERNANCE** | AI, machine learning, automated decision-making | Flag for human review |
| **RECORDKEEPING** | Records, retention, books and records | Flag for human review |
| **SUPERVISION** | Supervision, review, monitoring | Flag for human review |
| **DATA_PROTECTION** | Privacy, data security, PII | Flag for human review |
| **OUT_OF_SCOPE** | Trading rules, fee schedules, non-AI topics | Dismiss |

**IMPORTANT:** Regulatory changes are triage only. Do NOT draft edits.
</step>

<step name="draft_or_triage">
## Step 4: Draft Edits (Learn) or Triage (Regulatory)

### For Learn Changes (Auto-Draft Eligible)

For each actionable change:
1. Read the affected control or playbook file
2. Analyze the diff to determine what specifically changed
3. Draft the minimal edit following these rules:
   - **Minimal changes** — only edit what is necessary
   - **Preserve structure** — do not reorganize or reformat existing content
   - **Use consistent language** — follow CONTRIBUTING.md guidelines
   - **Add admonitions for updates:**
     ```markdown
     !!! info "Updated [Month Year]"
         [Description of what changed and the new information.]
     ```
   - **Never edit regulatory language** without flagging for human review
   - **Cross-reference new docs** in "Additional Resources" sections

### For Regulatory Changes (Triage Only)

For each CRITICAL/HIGH item:
1. Read the suggested affected controls to verify keyword matching accuracy
2. Assess relevance — is this truly applicable to AI agent governance in M365?
3. Categorize as "Requires Human Review" or "Out of Scope (Dismiss)"
4. **Do NOT draft edits** — the triage summary is the deliverable
</step>

<step name="present_summary">
## Step 5: Present Summary for Approval

### Learn Change Summary Format

```markdown
## Monitoring AI Assist — Learn Changes Summary

**Report:** reports/monitoring/learn-changes-YYYY-MM-DD.md
**Date:** YYYY-MM-DD

### Proposed Updates

| # | Control/Playbook | Change Type | Proposed Edit |
|---|------------------|-------------|---------------|
| 1 | Control 3.9 | DATE_UPDATE | Update Sentinel deadline to March 31, 2027 |
| 2 | Control 1.19 | SCOPE_CHANGE | Add 21Vianet applicability note |

### Flagged for Human Review

| # | Control/Playbook | Reason |
|---|------------------|--------|
| 1 | Control 2.12 | Policy language change detected |

### Skipped (No Action)

- Change X: Minor wording (SKIP)
- Change Y: Formatting only (SKIP)
```

### Regulatory Change Summary Format

```markdown
## Monitoring AI Assist — Regulatory Triage

**Report:** reports/monitoring/regulatory-changes-YYYY-MM-DD.md
**Date:** YYYY-MM-DD

### Requires Human Review

| # | Item | Source | Suggested Controls | Relevance |
|---|------|--------|-------------------|-----------|
| 1 | SEC AI Oversight Rule | SEC | 2.6, 2.15, 3.5 | HIGH — agent supervision |

### Out of Scope (Dismiss)

| # | Item | Reason |
|---|------|--------|
| 1 | OCC Bank Merger Policy | Not applicable to AI agent governance |

### Next Steps
Items under "Requires Human Review" need detailed analysis. Do NOT auto-edit regulatory content.
```

**Ask the user:** "Do you want me to apply the {N} proposed Learn updates?"
For regulatory reports, present the triage summary and stop.
</step>

<step name="apply_edits">
## Step 6: Apply Updates (Learn Changes Only)

**Only execute this step for Learn changes, and only after user approval.**

For each approved edit:
1. Apply the change using the edit tool
2. After all edits are applied, validate:

```powershell
mkdocs build --strict 2>&1 | Select-Object -First 50
```

If validation fails, report the error and attempt one fix cycle.
</step>

<step name="handle_url_redirects">
## Step 7: Handle URL Redirects (Learn Changes Only)

If the Learn change report contains URL redirects:
1. Read `docs/reference/microsoft-learn-urls.md`
2. Update each redirected URL to its new target
3. Ignore `?view=...` query parameter additions (cosmetic)

Regulatory reports do not have URL redirects — skip this step.
</step>

<step name="final_summary">
## Step 8: Final Summary

### For Learn Changes (After Edits Applied)

Report:
- Number of files modified
- Validation status (pass/fail)
- Any issues encountered
- Suggested commit message:
  ```
  docs: apply Learn Monitor updates from YYYY-MM-DD report
  ```

### For Regulatory Changes (After Triage)

Report:
- Items requiring human review (count and list)
- Items dismissed as out-of-scope (count)
- Recommendation: review flagged items and determine if framework updates are needed
</step>

</process>

<examples>

### Example 1: Learn Changes (Auto-Draft)

```
User: /review-learn-changes

Copilot: I'll analyze the latest monitoring report.

Reading reports/monitoring/learn-changes-2026-02-01.md...

Found 31 HIGH priority changes affecting 15 controls.

## Proposed Updates

| # | Control/Playbook | Change Type | Proposed Edit |
|---|------------------|-------------|---------------|
| 1 | Control 3.9 | DATE_UPDATE | Sentinel deadline: July 2026 → March 31, 2027 |
| 2 | Control 1.19 | SCOPE_CHANGE | Classic eDiscovery: Add 21Vianet scope note |
| 3 | Controls 1.1, 1.5, 1.6 | NEW_DOC | Add Agent Essentials cross-references |

Do you want me to apply these 12 updates?

User: Yes, apply them

Copilot: Applied 12 updates across 8 files.
✓ mkdocs build --strict passed
⚠ 1 change flagged for your review (Control 2.6)

Suggested commit: "docs: apply Learn Monitor updates from 2026-02-01 report"
```

### Example 2: Regulatory Changes (Triage Only)

```
User: Review the regulatory changes

Copilot: I'll analyze the latest regulatory monitoring report.

Reading reports/monitoring/regulatory-changes-2026-02-04.md...

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

</examples>