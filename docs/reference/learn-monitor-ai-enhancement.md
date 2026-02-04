# Unified Monitoring System - AI-Assisted Review Implementation Guide

This document describes the AI-assisted review capability for the unified monitoring system (Microsoft Learn + Regulatory sources).

---

## Executive Summary

**Implementation Status:** Active and functional as of February 2026.

**Current State:** The unified monitoring system detects changes from Microsoft Learn documentation and regulatory sources (Federal Register, FINRA). AI-assisted review provides automated drafts for Learn changes and triage analysis for regulatory changes.

**How It Works:** The `/review-learn-changes` Claude Code skill analyzes monitoring reports and either drafts specific documentation updates (Learn changes) or provides triage summaries (regulatory changes) for human review.

---

## System Architecture

```
┌──────────────────────────────────────────────────────────────────────────────┐
│                       UNIFIED MONITORING SYSTEM                              │
│                                                                              │
│  ┌─────────────────────┐         ┌─────────────────────┐                    │
│  │  Learn Monitor      │         │ Regulatory Monitor  │                    │
│  │  (Daily 6 AM UTC)   │         │ (Weekly Wed 6 AM)   │                    │
│  └──────────┬──────────┘         └──────────┬──────────┘                    │
│             │                               │                                │
│             └───────────────┬───────────────┘                                │
│                             │                                                │
│                             ▼                                                │
│                  ┌──────────────────────┐                                    │
│                  │ monitoring_shared.py │ (Unified framework)                │
│                  │ - Shared state file  │                                    │
│                  │ - Shared reports dir │                                    │
│                  │ - Control mapping    │                                    │
│                  └──────────┬───────────┘                                    │
│                             │                                                │
│                             ▼                                                │
│                  ┌──────────────────────┐                                    │
│                  │  Create Report in    │                                    │
│                  │  reports/monitoring/ │                                    │
│                  └──────────┬───────────┘                                    │
│                             │                                                │
│                             ▼                                                │
│         ┌───────────────────┴───────────────────┐                            │
│         │                                       │                            │
│         ▼                                       ▼                            │
│  ┌──────────────────┐                  ┌──────────────────┐                 │
│  │ Learn Report     │                  │ Regulatory Report│                 │
│  │ (learn-changes-) │                  │ (regulatory-    )│                 │
│  └────────┬─────────┘                  └────────┬─────────┘                 │
│           │                                     │                            │
│           └────────────┬────────────────────────┘                            │
│                        │                                                     │
│                        ▼                                                     │
│              ┌─────────────────────┐                                         │
│              │ /review-learn-      │ (AI-assisted review)                    │
│              │  changes skill      │                                         │
│              └─────────┬───────────┘                                         │
│                        │                                                     │
│         ┌──────────────┴──────────────┐                                      │
│         ▼                              ▼                                     │
│  ┌──────────────┐              ┌──────────────┐                             │
│  │ Learn: Auto  │              │ Regulatory:  │                             │
│  │ Draft Edits  │              │ Triage Only  │                             │
│  └──────┬───────┘              └──────┬───────┘                             │
│         │                              │                                     │
│         └──────────────┬───────────────┘                                     │
│                        │                                                     │
│                        ▼                                                     │
│              ┌─────────────────────┐                                         │
│              │ HUMAN: Review &     │                                         │
│              │ Approve/Edit        │                                         │
│              └─────────────────────┘                                         │
│                                                                              │
└──────────────────────────────────────────────────────────────────────────────┘
```

---

## Implementation Approach

The system uses **Manual Claude Code Invocation** (formerly "Option B") with distinct workflows for different report types:

### Learn Changes: Auto-Draft with Human Approval

Human invokes `/review-learn-changes` skill after monitoring PR is created:

1. Read Learn change report from `reports/monitoring/`
2. Filter for HIGH priority changes
3. For each affected control/playbook:
   - Read current documentation
   - Analyze what changed in Microsoft Learn
   - Draft specific edits
4. Present summary of proposed updates to human
5. Apply edits with user confirmation
6. Run validation (`mkdocs build --strict`)
7. Human reviews, commits, and pushes changes

### Regulatory Changes: Triage with Human Decision

Human invokes `/review-learn-changes` skill for regulatory reports:

1. Read regulatory change report from `reports/monitoring/`
2. For each CRITICAL/HIGH item:
   - Read suggested affected controls
   - Assess relevance to AI agent governance
   - Validate keyword-based suggestions
3. Present triage summary (requires review vs. out-of-scope)
4. Human conducts detailed analysis and determines if framework updates are needed

**Rationale:** Regulatory language changes require human judgment and cannot be auto-drafted per CONTRIBUTING.md safety rules.

### Key Design Decisions

#### 1. Scope Limitation (Learn Changes)
- Process HIGH priority changes
- Flag CRITICAL changes for immediate attention
- Human controls when to run (cost optimization)

#### 2. Change Categories Handled

**Learn Changes (Auto-Draft):**

| Change Type | AI Action |
|-------------|-----------|
| UI navigation step changes | Update portal-walkthrough.md playbooks |
| Date/deadline changes | Update affected controls and playbooks |
| Feature GA/deprecation | Add/update info boxes in controls |
| Policy language changes | Flag for human review (don't auto-edit) |
| New documentation pages | Create cross-reference entries |

**Regulatory Changes (Triage Only):**

| Change Type | AI Action |
|-------------|-----------|
| AI governance-related | Validate suggested controls, flag for human review |
| Recordkeeping/supervision | Validate suggested controls, flag for human review |
| Data protection/content | Validate suggested controls, flag for human review |
| Out of scope | Identify as dismissible |

#### 3. Safety Guardrails

- **Never auto-commit:** All drafts require human review
- **Validation gate:** mkdocs build must pass after edits
- **Regulatory language check:** Never auto-edit regulatory content per CONTRIBUTING.md
- **Human invocation:** User decides when to run the skill

---

## Implementation Status

### Phase 1: Unified Framework (Complete ✅)

**Delivered:** `scripts/monitoring_shared.py`

**Capabilities:**
- Shared state management (`data/monitor-state.json`)
- Shared report directory (`reports/monitoring/`)
- Control mapping and classification
- Pluggable source adapters (Learn + Regulatory)

### Phase 2: Source Adapters (Complete ✅)

**Learn Monitor:** `scripts/learn_monitor.py`
- 209 Microsoft Learn URLs monitored
- Daily runs via GitHub Actions
- Produces `reports/monitoring/learn-changes-*.md`

**Regulatory Monitor:** `scripts/regulatory_monitor.py`
- Federal Register APIs (SEC, CFTC, OCC, Fed Reserve)
- FINRA regulatory notices
- Weekly runs via GitHub Actions
- Produces `reports/monitoring/regulatory-changes-*.md`

### Phase 3: AI-Assisted Review Skill (Complete ✅)

**Delivered:** `.claude/skills/review-learn-changes.md`

**Workflow:**
1. User invokes `/review-learn-changes` after monitoring PR created
2. Skill determines report type (Learn or Regulatory)
3. For Learn reports:
   - Analyzes HIGH priority changes
   - Drafts specific documentation edits
   - Applies edits with user confirmation
   - Runs validation
4. For Regulatory reports:
   - Validates control mapping suggestions
   - Assesses relevance to AI agent governance
   - Creates triage summary (review vs. dismiss)
   - Human conducts detailed analysis

### Future Enhancements (Optional)

**GitHub Actions Integration:**
- Automated invocation of AI review on PR creation
- Requires Claude API key in GitHub Secrets
- Cost vs. benefit evaluation needed

---

## Change Classification and Response

### Learn Changes

#### Auto-Draft Eligible

| Pattern Detected | Update Action |
|-----------------|---------------|
| Portal path changed | Update portal-walkthrough.md navigation steps |
| Button/menu renamed | Update portal-walkthrough.md UI references |
| Date deadline extended | Update control and FAQ with new date |
| Feature now GA | Remove "Preview" tags, update availability |
| Feature deprecated | Add deprecation warning box |
| URL redirect | Update microsoft-learn-urls.md |

#### Flag for Human Review

| Pattern Detected | Reason |
|-----------------|--------|
| Policy language changes | Regulatory implications |
| New compliance requirements | Legal review needed |
| Licensing changes | Business impact |
| Security guidance changes | Risk assessment needed |
| CRITICAL classification | Immediate attention required |

#### Skip

| Pattern Detected | Reason |
|-----------------|--------|
| Formatting only | No substantive change |
| Date metadata | Noise |
| Minor wording tweaks | Low impact |
| 21Vianet-only changes | Not applicable to US FSI |

### Regulatory Changes

#### Triage Categories

| Category | Pattern | Response |
|----------|---------|----------|
| **Requires Review** | AI, supervision, recordkeeping, data protection keywords | Validate suggested controls, flag for human analysis |
| **Out of Scope** | Trading rules, fee schedules, non-AI topics | Identify as dismissible |

**IMPORTANT:** Regulatory changes are NEVER auto-edited. The skill produces a triage summary only.

---

## Usage Examples

### Example 1: Learn Changes with Auto-Draft

```bash
# User invokes skill
/review-learn-changes

# Skill analyzes report
Reading reports/monitoring/learn-changes-2026-02-01.md...

Found 31 HIGH priority changes affecting 15 controls.

Proposed Updates:
1. Control 3.9: Update Sentinel deadline (July 2026 → March 31, 2027)
2. Control 1.19: Add 21Vianet scope note for eDiscovery classic
3. Controls 1.1, 1.5, 1.6: Add Agent Essentials cross-references
...

Do you want me to apply these 12 updates?

# User approves
Yes, apply them

# Skill applies edits and validates
Applied 12 updates across 8 files
✓ mkdocs build --strict passed

Recommendation: Review changes and commit with:
"docs: Apply Learn Monitor updates from 2026-02-01 report"
```

### Example 2: Regulatory Changes with Triage

```bash
# User invokes skill for regulatory report
/review-learn-changes

# Skill analyzes report
Reading reports/monitoring/regulatory-changes-2026-02-04.md...

Found 4 regulatory items. All classified as NOISE.

Triage Summary:

Out of Scope (Dismiss):
1. SEC - Fixed Income Clearing Corp rule (not AI governance-related)
2. CBOE Exchange trading rule (not AI governance-related)
3. NYSE fee schedule update (not AI governance-related)
4. FINRA trade reporting notice (not AI governance-related)

All items are out of scope. No action needed.
```

---

## Related Documentation

- **Monitoring Architecture:** [monitoring-architecture.md](monitoring-architecture.md) - Unified monitoring system overview
- **Learn Monitor Guide:** [learn-monitor-guide.md](learn-monitor-guide.md) - Learn Monitor documentation
- **Claude Code Skill:** `.claude/skills/review-learn-changes.md` - User-invocable skill
- **Contributing Guide:** `CONTRIBUTING.md` - Language guidelines and safety rules

---

*Implementation Guide v2.0 - February 2026 (Active implementation)*
