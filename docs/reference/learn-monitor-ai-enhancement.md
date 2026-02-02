# Learn Monitor AI-Assisted Drafts Enhancement

This document describes the design for enhancing the Learn Monitor workflow with AI-assisted documentation update drafts.

---

## Executive Summary

**Current State:** The Learn Monitor detects Microsoft Learn documentation changes and creates PRs with change reports. Humans must manually review reports and update affected documentation.

**Enhanced State:** After detecting changes, Claude Code reviews the change report and drafts specific documentation updates, creating a follow-up PR with proposed edits for human approval.

---

## Design Overview

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           CURRENT WORKFLOW                                  │
│                                                                             │
│  Daily 6 AM UTC                                                             │
│  ┌──────────┐    ┌──────────┐    ┌──────────┐    ┌──────────────────────┐  │
│  │  Fetch   │───▶│  Hash &  │───▶│ Classify │───▶│ Create Detection PR  │  │
│  │  URLs    │    │  Compare │    │ Changes  │    │ (state + report)     │  │
│  └──────────┘    └──────────┘    └──────────┘    └──────────────────────┘  │
│                                                             │               │
│                                                             ▼               │
│                                                   ┌──────────────────────┐  │
│                                                   │  MANUAL: Review &    │  │
│                                                   │  Update Docs         │  │
│                                                   └──────────────────────┘  │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│                          ENHANCED WORKFLOW                                  │
│                                                                             │
│  Daily 6 AM UTC                                                             │
│  ┌──────────┐    ┌──────────┐    ┌──────────┐    ┌──────────────────────┐  │
│  │  Fetch   │───▶│  Hash &  │───▶│ Classify │───▶│ Create Detection PR  │  │
│  │  URLs    │    │  Compare │    │ Changes  │    │ (state + report)     │  │
│  └──────────┘    └──────────┘    └──────────┘    └──────────────────────┘  │
│                                                             │               │
│                                                             ▼               │
│                                                   ┌──────────────────────┐  │
│                                            NEW    │  Claude Code         │  │
│                                           ─────▶  │  Reviews Report      │  │
│                                                   └──────────────────────┘  │
│                                                             │               │
│                                                             ▼               │
│                                                   ┌──────────────────────┐  │
│                                            NEW    │  Create Draft PR     │  │
│                                           ─────▶  │  with Doc Updates    │  │
│                                                   └──────────────────────┘  │
│                                                             │               │
│                                                             ▼               │
│                                                   ┌──────────────────────┐  │
│                                                   │  HUMAN: Review &     │  │
│                                                   │  Approve/Edit        │  │
│                                                   └──────────────────────┘  │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Implementation Options

### Option A: GitHub Actions Workflow (Recommended)

Add a new workflow that triggers when the detection PR is created, uses Claude Code to analyze and draft updates.

**Pros:**
- Fully automated, no manual intervention to start
- Runs in CI environment with proper permissions
- Creates audit trail in GitHub Actions logs

**Cons:**
- Requires Claude API key in GitHub Secrets
- API costs for each run
- Limited by GitHub Actions runner time limits

### Option B: Manual Claude Code Invocation

Create a skill/script that a human invokes after reviewing the detection PR.

**Pros:**
- Human decides when to run
- Lower API costs (only runs when needed)
- More control over when AI assistance is used

**Cons:**
- Not fully automated
- Requires human to remember to run it

### Option C: Hybrid Approach

GitHub Actions creates a comment on the detection PR with instructions to invoke Claude Code locally.

**Pros:**
- Best of both worlds
- Human remains in the loop
- Clear workflow guidance

**Cons:**
- Slightly more complex
- Still requires manual step

---

## Recommended Implementation: Option A with Guardrails

### Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    learn-monitor-ai-assist.yml                              │
│                                                                             │
│  Trigger: PR created with label "learn-watch"                               │
│                                                                             │
│  Steps:                                                                     │
│  1. Checkout repo                                                           │
│  2. Read change report from PR                                              │
│  3. Filter for HIGH priority changes only                                   │
│  4. For each affected control/playbook:                                     │
│     a. Read current documentation                                           │
│     b. Analyze what changed in Microsoft Learn                              │
│     c. Draft specific edits                                                 │
│  5. Create new branch: learn-monitor/docs-update-{run_number}               │
│  6. Apply drafted edits                                                     │
│  7. Run validation (mkdocs build --strict)                                  │
│  8. Create PR with drafted updates                                          │
│  9. Link new PR to detection PR                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Key Design Decisions

#### 1. Scope Limitation
- Only process HIGH priority changes (not MEDIUM or NOISE)
- Skip CRITICAL changes (require immediate human attention)
- Maximum 10 controls per run to limit API costs

#### 2. Change Categories Handled

| Change Type | AI Action |
|-------------|-----------|
| UI navigation step changes | Update portal-walkthrough.md playbooks |
| Date/deadline changes | Update affected controls and playbooks |
| Feature GA/deprecation | Add/update info boxes in controls |
| Policy language changes | Flag for human review (don't auto-edit) |
| New documentation pages | Create cross-reference entries |

#### 3. Safety Guardrails

- **Never auto-merge:** All drafts require human approval
- **Validation gate:** mkdocs build must pass before PR creation
- **Diff size limit:** If changes exceed 500 lines, flag for manual review
- **Regulatory language check:** Never auto-edit sentences containing regulatory terms
- **Rollback ready:** Each change is a separate commit for easy revert

---

## Implementation Plan

### Phase 1: Script Development (This Session)

Create `scripts/learn_monitor_ai_assist.py`:

```python
#!/usr/bin/env python3
"""
Learn Monitor AI Assist - Analyzes change reports and drafts documentation updates.

Usage:
    python scripts/learn_monitor_ai_assist.py --report reports/learn-changes/learn-changes-2026-02-01.md
    python scripts/learn_monitor_ai_assist.py --pr 6
"""
```

**Capabilities:**
1. Parse change report markdown
2. Extract affected controls and playbooks
3. Analyze each change against current documentation
4. Generate specific edit recommendations
5. Output structured update plan (JSON/Markdown)

### Phase 2: Claude Code Skill

Create `.claude/skills/review-learn-changes.md`:

```yaml
---
name: review-learn-changes
description: Review Learn Monitor change report and draft documentation updates
allowed-tools: [Read, Glob, Grep, Edit, Write, Bash]
user-invocable: true
---
```

**Workflow:**
1. Read the latest change report
2. For each HIGH priority change:
   - Read the affected control/playbook
   - Analyze the diff from Microsoft Learn
   - Determine if update is needed
   - Draft specific edits
3. Create summary of proposed changes
4. Apply edits (with user confirmation)
5. Run validation

### Phase 3: GitHub Actions Integration (Future)

Create `.github/workflows/learn-monitor-ai-assist.yml`:

```yaml
name: Learn Monitor AI Assist

on:
  pull_request:
    types: [opened]
    paths:
      - 'reports/learn-changes/*.md'

jobs:
  analyze-changes:
    if: contains(github.event.pull_request.labels.*.name, 'learn-watch')
    runs-on: ubuntu-latest
    steps:
      # ... implementation
```

---

## Change Report Analysis Rules

### What to Update Automatically

| Pattern Detected | Update Action |
|-----------------|---------------|
| Portal path changed | Update portal-walkthrough.md navigation steps |
| Button/menu renamed | Update portal-walkthrough.md UI references |
| Date deadline extended | Update control and FAQ with new date |
| Feature now GA | Remove "Preview" tags, update availability |
| Feature deprecated | Add deprecation warning box |
| URL redirect | Update microsoft-learn-urls.md |

### What to Flag for Human Review

| Pattern Detected | Reason |
|-----------------|--------|
| Policy language changes | Regulatory implications |
| New compliance requirements | Legal review needed |
| Licensing changes | Business impact |
| Security guidance changes | Risk assessment needed |
| CRITICAL classification | Immediate attention required |

### What to Skip

| Pattern Detected | Reason |
|-----------------|--------|
| Formatting only | No substantive change |
| Date metadata | Noise |
| Minor wording tweaks | Low impact |
| 21Vianet-only changes | Not applicable to US FSI |

---

## PR #6 Analysis Preview

Based on the change report in PR #6, here's what the AI assistant would recommend:

### HIGH Priority Changes Requiring Updates

| # | Change | Affected Docs | Recommended Action |
|---|--------|---------------|-------------------|
| 1 | Sentinel Azure portal deprecation date changed (July 2026 → March 31, 2027) | Control 3.9, multiple Sentinel references | Update timeline references |
| 2 | eDiscovery classic retirement scope clarified (21Vianet only) | Control 1.19, eDiscovery playbooks | Add scope clarification note |
| 3 | New Agent Essentials documentation pages | Controls 1.1, 1.5, 1.6, 1.11, 2.1, 2.3, 3.1, 3.5, 3.8 | Add cross-references |
| 4 | Key Vault RBAC now default in CLI | Control 1.20 | Update PowerShell examples |
| 5 | AI Content Safety documentation expanded | Control 1.8 | Add new capability references |
| 6 | 54 URL redirects detected | microsoft-learn-urls.md | Batch update URLs |

### Changes to Skip

| # | Change | Reason |
|---|--------|--------|
| 1 | Copilot Studio UI text tweaks | Minor wording, no impact |
| 2 | Sensitivity labels note rewording | Formatting only |
| 3 | Device Control typo fix ("Portal" → "Portable") | Typo in MS doc, not ours |

---

## Testing Plan

### Test with PR #6

1. **Run analysis script** against `reports/learn-changes/learn-changes-2026-02-01.md`
2. **Review recommendations** for accuracy
3. **Apply a subset of changes** manually
4. **Validate** with `mkdocs build --strict`
5. **Iterate** on script based on results

### Success Criteria

- [ ] Script correctly identifies affected controls
- [ ] Script correctly categorizes changes (update/flag/skip)
- [ ] Generated edits are accurate and minimal
- [ ] No regulatory language violations
- [ ] mkdocs build passes after changes

---

## Cost Considerations

### API Usage Estimate

| Component | Tokens (est.) | Cost (est.) |
|-----------|---------------|-------------|
| Read change report | ~5,000 | $0.02 |
| Read affected docs (10 controls × 2,000 tokens) | ~20,000 | $0.08 |
| Generate recommendations | ~10,000 | $0.04 |
| **Total per run** | ~35,000 | **~$0.14** |

*Based on Claude Sonnet pricing. Using Haiku for classification would reduce costs.*

### Optimization Strategies

1. **Pre-filter changes** before calling Claude (skip NOISE/MEDIUM)
2. **Batch similar changes** (e.g., all Sentinel date updates together)
3. **Cache control content** across runs
4. **Use Haiku for classification**, Sonnet for drafting

---

## Next Steps

1. **Now:** Test the analysis approach manually with PR #6
2. **This session:** Create the Claude Code skill
3. **Future:** Implement GitHub Actions automation
4. **Future:** Add metrics/reporting on AI assist effectiveness

---

*Design Document v1.0 - February 2026*
