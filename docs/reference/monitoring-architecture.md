# Unified Monitoring System Architecture

This document describes the comprehensive architecture of the FSI-AgentGov monitoring system for detecting external changes that may require framework updates.

---

## Executive Summary

**Purpose:** Proactively detect changes in external sources (Microsoft Learn documentation, regulatory notices) that may impact the FSI Agent Governance Framework, enabling timely documentation updates.

**Implementation Status:** Active and operational as of February 2026.

**Coverage:**
- **Microsoft Learn:** 209 URLs monitored daily
- **Regulatory Sources:** Federal Register (SEC, CFTC, OCC, Federal Reserve) + FINRA notices monitored weekly

**Key Principle:** ONE unified monitoring system with multiple source adapters, not separate independent monitors.

---

## System Overview

```
┌──────────────────────────────────────────────────────────────────────────┐
│                     UNIFIED MONITORING ARCHITECTURE                      │
│                                                                          │
│  ┌────────────────────────────────────────────────────────────────┐     │
│  │                    SHARED INFRASTRUCTURE                        │     │
│  │  ┌─────────────────────────────────────────────────────────┐   │     │
│  │  │  monitoring_shared.py (Unified Framework)                │   │     │
│  │  │  - State management                                      │   │     │
│  │  │  - Report generation                                     │   │     │
│  │  │  - Control mapping                                       │   │     │
│  │  │  - Change classification                                 │   │     │
│  │  └─────────────────────────────────────────────────────────┘   │     │
│  │                                                                 │     │
│  │  ┌────────────────┐         ┌──────────────────────────────┐   │     │
│  │  │ Shared State   │         │ Shared Report Directory      │   │     │
│  │  │ data/monitor-  │         │ reports/monitoring/          │   │     │
│  │  │ state.json     │         │ - learn-changes-*.md         │   │     │
│  │  │                │         │ - regulatory-changes-*.md    │   │     │
│  │  └────────────────┘         └──────────────────────────────┘   │     │
│  └─────────────────────────────────────────────────────────────┘   │     │
│                                                                      │     │
│  ┌────────────────────────────────────────────────────────────────┐     │
│  │                     SOURCE ADAPTERS                            │     │
│  ├────────────────────────────────────────────────────────────────┤     │
│  │  ┌─────────────────────┐     ┌─────────────────────────────┐  │     │
│  │  │ learn_monitor.py    │     │ regulatory_monitor.py       │  │     │
│  │  │ - Fetch Learn URLs  │     │ - Fetch Federal Register    │  │     │
│  │  │ - Hash content      │     │ - Fetch FINRA notices       │  │     │
│  │  │ - Classify changes  │     │ - Keyword matching          │  │     │
│  │  │ - Map to controls   │     │ - Map to controls           │  │     │
│  │  │                     │     │                             │  │     │
│  │  │ Schedule: Daily     │     │ Schedule: Weekly            │  │     │
│  │  │ 6:00 AM UTC         │     │ Wednesday 6:00 AM UTC       │  │     │
│  │  └─────────────────────┘     └─────────────────────────────┘  │     │
│  └────────────────────────────────────────────────────────────────┘     │
│                                                                          │
│  ┌────────────────────────────────────────────────────────────────┐     │
│  │                  AI-ASSISTED REVIEW                             │     │
│  │  ┌──────────────────────────────────────────────────────────┐  │     │
│  │  │ .claude/skills/review-learn-changes.md                   │  │     │
│  │  │ - Learn reports: Auto-draft edits                        │  │     │
│  │  │ - Regulatory reports: Triage only                        │  │     │
│  │  │                                                           │  │     │
│  │  │ Invocation: Manual (user runs /review-learn-changes)     │  │     │
│  │  └──────────────────────────────────────────────────────────┘  │     │
│  └────────────────────────────────────────────────────────────────┘     │
│                                                                          │
└──────────────────────────────────────────────────────────────────────────┘
```

---

## Unified Framework

### monitoring_shared.py

**Location:** `scripts/monitoring_shared.py`
**Purpose:** Core framework providing shared utilities for all monitoring sources

**Key Functions:**

| Function | Purpose |
|----------|---------|
| `load_state()` | Load monitoring state from unified state file |
| `save_state()` | Save monitoring state to unified state file |
| `classify_change()` | Classify changes (CRITICAL/HIGH/MEDIUM/NOISE) |
| `map_to_controls()` | Map changes to affected framework controls |
| `generate_report()` | Generate markdown change reports |
| `normalize_content()` | Clean and normalize content for comparison |
| `compute_hash()` | Generate SHA-256 content hashes |

**Design Principle:** Source adapters (Learn Monitor, Regulatory Monitor) are thin wrappers that fetch content and delegate to `monitoring_shared.py` for all common operations.

---

## State File

### data/monitor-state.json

**Purpose:** Unified state file tracking all monitored sources

**Structure:**

```json
{
  "last_updated": "2026-02-04T06:00:00Z",
  "sources": {
    "learn": {
      "urls": {
        "https://learn.microsoft.com/...": {
          "hash": "sha256:abc123...",
          "last_checked": "2026-02-04T06:00:00Z",
          "title": "Managed Environments Overview",
          "normalized_content": "..."
        }
      }
    },
    "regulatory": {
      "federal_register": {
        "last_checked": "2026-02-04T06:00:00Z",
        "items": {
          "2026-02228": {
            "title": "SEC Rule Filing...",
            "hash": "sha256:def456...",
            "agency": "SEC",
            "document_type": "Rule"
          }
        }
      },
      "finra": {
        "last_checked": "2026-02-04T06:00:00Z",
        "items": {
          "trade-reporting-notice-20260114": {
            "title": "Trade Reporting Notice...",
            "hash": "sha256:ghi789...",
            "notice_type": "Trade Reporting"
          }
        }
      }
    }
  }
}
```

**Benefits of Unified State:**
- Single source of truth for all monitoring
- Cross-source correlation possible
- Simplified backup and restore
- Reduced state file management complexity

---

## Report Directory

### reports/monitoring/

**Purpose:** Unified directory for all monitoring reports

**Report Types:**

| Report Pattern | Source | Frequency | Purpose |
|----------------|--------|-----------|---------|
| `learn-changes-YYYY-MM-DD.md` | Learn Monitor | Daily (if changes) | Microsoft Learn documentation updates |
| `regulatory-changes-YYYY-MM-DD.md` | Regulatory Monitor | Weekly (if changes) | Federal Register + FINRA regulatory notices |

**Report Format (Learn):**

```markdown
# Learn Monitor Report - YYYY-MM-DD

**Run Date:** YYYY-MM-DD
**URLs Monitored:** 209
**Meaningful Changes:** N

## Summary

[Executive summary table]

## HIGH Priority Changes

### URL: [Microsoft Learn URL]

**Affected Controls:** 1.1, 1.5, 2.3
**Affected Playbooks:** 1.1/portal-walkthrough.md

**What Changed:**
[Diff showing before/after]
```

**Report Format (Regulatory):**

```markdown
# Regulatory Monitor Report - YYYY-MM-DD

**Run Date:** YYYY-MM-DD
**New Items:** N
**Sources:** Federal Register (SEC, CFTC, OCC, Federal Reserve) + FINRA Notices

## Summary

[Executive summary table by category]

## HIGH Priority Items

### [Regulatory Item Title]

**Source:** SEC
**Potentially Affected Controls:** [keyword-matched controls]

[Summary of item]
```

**Why Unified Directory:**
- Single location for all change reports
- Simplified AI-assisted review workflow
- Easier backup and archival
- Clear organizational structure

---

## Source Adapters

### Learn Monitor

**Script:** `scripts/learn_monitor.py`
**Workflow:** `.github/workflows/learn-monitor.yml`
**Schedule:** Daily at 6:00 AM UTC

**Data Source:** `docs/reference/microsoft-learn-urls.md` (209 URLs)

**Process:**
1. Load URLs from watchlist
2. Fetch each URL via HTTP
3. Extract meaningful content (remove headers, navigation, metadata)
4. Normalize content (whitespace, encoding)
5. Compute SHA-256 hash
6. Compare to previous hash in state file
7. If changed, classify change (CRITICAL/HIGH/MEDIUM/NOISE)
8. Map to affected controls via URL-to-control mapping
9. Generate report if meaningful changes detected
10. Update state file

**Exit Codes:**
- `0` - No meaningful changes
- `1` - Meaningful changes detected (triggers PR creation)
- `2` - Error during execution

**PR Creation Logic:**
- Every Sunday (baseline run), OR
- When exit code = 1 (changes detected)

### Regulatory Monitor

**Script:** `scripts/regulatory_monitor.py`
**Workflow:** `.github/workflows/regulatory-monitor.yml`
**Schedule:** Weekly on Wednesday at 6:00 AM UTC

**Data Sources:**
- Federal Register API (SEC, CFTC, OCC, Federal Reserve)
- FINRA regulatory notices (web scraping)

**Process:**
1. Query Federal Register API for recent documents from target agencies
2. Scrape FINRA regulatory notices
3. For each new item:
   - Extract title, abstract, document type
   - Compute content hash
   - Check if already seen in state file
   - If new, classify relevance (CRITICAL/HIGH/MEDIUM/NOISE) via keyword matching
   - Suggest potentially affected controls based on keywords
4. Generate report if new items detected
5. Update state file

**Exit Codes:**
- `0` - No new items
- `1` - New items detected (triggers PR creation)
- `2` - Error during execution

**Keywords for Control Mapping:**

| Keyword Category | Keywords | Maps To |
|------------------|----------|---------|
| AI/ML | artificial intelligence, machine learning, automated decision | 1.8, 2.6, 2.15 |
| Recordkeeping | records, retention, books and records, archive | 3.1, 3.2, 3.3 |
| Supervision | supervision, review, oversight, monitoring | 2.6, 2.15, 3.5 |
| Data Protection | privacy, data security, PII, confidential | 1.1, 1.2, 1.3 |
| Content Moderation | harmful content, content review, moderation | 1.27, 1.8 |

---

## AI-Assisted Review

**Skill:** `.claude/skills/review-learn-changes.md`
**Invocation:** Manual via `/review-learn-changes`

### Learn Report Workflow

When a Learn change report is created:

1. User invokes `/review-learn-changes` in Claude Code
2. Skill reads `reports/monitoring/learn-changes-*.md`
3. For each HIGH priority change:
   - Read affected control/playbook
   - Analyze the diff from Microsoft Learn
   - Draft specific edit
4. Present summary to user:
   - Proposed updates (auto-draftable)
   - Flagged for human review (policy/regulatory language)
   - Skipped (formatting/noise)
5. User confirms: "Apply the N updates"
6. Skill applies edits using Edit tool
7. Runs `mkdocs build --strict` validation
8. User reviews, commits, and pushes

**Auto-Draft Eligible Changes:**
- UI navigation step updates
- Date/deadline changes
- Feature GA/deprecation notices
- URL redirects
- New documentation cross-references

**Flagged for Human Review:**
- Policy language changes
- New compliance requirements
- Security guidance changes
- Licensing changes

### Regulatory Report Workflow

When a regulatory change report is created:

1. User invokes `/review-learn-changes` in Claude Code
2. Skill reads `reports/monitoring/regulatory-changes-*.md`
3. For each CRITICAL/HIGH item:
   - Read suggested affected controls
   - Assess relevance to AI agent governance
   - Validate keyword-based suggestions
4. Present triage summary:
   - Requires human review (with relevance assessment)
   - Out of scope (dismissible)
5. User conducts detailed analysis
6. User determines if framework updates needed

**IMPORTANT:** Regulatory changes are NEVER auto-edited per CONTRIBUTING.md safety rules. The skill provides triage assistance only.

---

## Change Classification

**4-Tier System:**

| Classification | Criteria | Action |
|----------------|----------|--------|
| **CRITICAL** | Affects portal-walkthrough.md playbooks, breaking changes, security vulnerabilities | Immediate update required |
| **HIGH** | UI steps, policy language, deprecations, new capabilities | Review and update |
| **MEDIUM** | General content updates, minor documentation changes | Review optional |
| **NOISE** | Metadata, dates, formatting, out-of-scope regulatory items | Ignore |

**Learn Classification Logic:**

- Contains UI keywords (`click`, `navigate`, `portal`, `admin center`) + affects playbook → CRITICAL
- Contains policy keywords (`required`, `must`, `prohibited`, `compliance`) → HIGH
- Contains deprecation keywords (`deprecated`, `retired`, `no longer`) → HIGH
- Contains release keywords (`preview`, `GA`, `generally available`) → HIGH
- Substantive content change → MEDIUM
- Metadata/formatting only → NOISE

**Regulatory Classification Logic:**

- Contains AI/supervision/recordkeeping keywords → HIGH (if SEC/FINRA/OCC/Fed)
- Contains data protection keywords → HIGH (if GLBA-relevant agency)
- Trading rules, fee schedules, non-AI topics → NOISE
- Keyword matching to framework controls → Suggests affected controls

---

## Maintenance Procedures

### Weekly Maintenance (~30 minutes)

**Monday Morning:**

1. **Check Learn Monitor PR** (created Sunday baseline or when changes detected)
   ```bash
   gh pr list --label "learn-watch"
   ```

2. **Review change report** in `reports/monitoring/learn-changes-*.md`
   - Check summary for HIGH/CRITICAL changes
   - Note number of affected controls

3. **Run AI-assisted review** (if HIGH priority changes exist)
   ```bash
   # In Claude Code
   /review-learn-changes
   ```

4. **Apply updates** and validate
   ```bash
   # After skill applies edits
   python3 -m mkdocs build --strict
   ```

5. **Commit and merge PR**
   ```bash
   git commit -m "docs: Apply Learn Monitor updates from [date]"
   git push
   gh pr merge --squash
   ```

**Thursday Morning:**

1. **Check Regulatory Monitor PR** (created Wednesday if changes detected)
   ```bash
   gh pr list --label "monitoring"
   ```

2. **Review change report** in `reports/monitoring/regulatory-changes-*.md`
   - Check summary for HIGH items
   - Note suggested affected controls

3. **Run AI-assisted triage**
   ```bash
   # In Claude Code
   /review-learn-changes
   ```

4. **Conduct detailed analysis** for items flagged as "Requires Human Review"
   - Read full regulatory text
   - Assess applicability to AI agent governance
   - Determine if framework updates needed

5. **Update framework** if needed (separate work session)
   - Create issue tracking regulatory change
   - Plan documentation updates
   - Implement and test

6. **Merge PR** (updates state file even if no framework changes)
   ```bash
   gh pr merge --squash
   ```

### Adding New URLs to Learn Monitor

**Process:**

1. **Add URL to watchlist**
   ```bash
   # Edit docs/reference/microsoft-learn-urls.md
   # Add new URL under appropriate section
   ```

2. **Map URL to controls**
   ```bash
   # Edit scripts/learn_monitor.py
   # Update URL_TO_CONTROLS mapping (around line 70-150)
   ```

3. **Run test**
   ```bash
   python3 scripts/learn_monitor.py --url "https://learn.microsoft.com/..." --dry-run
   ```

4. **Commit changes**
   ```bash
   git add docs/reference/microsoft-learn-urls.md scripts/learn_monitor.py
   git commit -m "feat: Add [topic] to Learn Monitor watchlist"
   ```

**Next scheduled run will pick up the new URL automatically.**

### Adding New Regulatory Sources

**Federal Register Agencies:**

Edit `scripts/regulatory_monitor.py` around line 30:

```python
FEDERAL_REGISTER_AGENCIES = [
    "securities-and-exchange-commission",
    "commodity-futures-trading-commission",
    "comptroller-of-the-currency",
    "federal-reserve-system",
    # Add new agency slug here
]
```

**FINRA Notice Types:**

Edit `scripts/regulatory_monitor.py` around line 250:

```python
FINRA_CATEGORIES = [
    "regulatory-notices",
    "disciplinary-actions",
    # Add new category here
]
```

**Keyword Mapping:**

Edit `scripts/monitoring_shared.py` around line 400:

```python
REGULATORY_KEYWORDS = {
    "ai_governance": {
        "keywords": ["artificial intelligence", "machine learning", ...],
        "controls": ["1.8", "2.6", "2.15"]
    },
    # Add new keyword category here
}
```

---

## Troubleshooting

| Issue | Symptoms | Resolution |
|-------|----------|------------|
| **Workflow not running** | No PRs created for days | Check GitHub Actions settings, verify GITHUB_TOKEN permissions |
| **State file corrupted** | JSON parsing errors | Restore from backup or delete and re-run monitor (establishes new baseline) |
| **False positives** | Too many NOISE changes classified as HIGH | Tune classification keywords in `monitoring_shared.py` |
| **Missing changes** | Known changes not detected | Verify URL in watchlist, check URL_TO_CONTROLS mapping |
| **API rate limits** | Federal Register API 429 errors | Workflow runs weekly to avoid limits; if persistent, add retry logic |
| **FINRA scraping failure** | Regulatory monitor fails | FINRA HTML structure changed; update scraping logic in `regulatory_monitor.py` |
| **mkdocs build fails after updates** | Broken links or syntax errors | Review AI-drafted edits manually, fix syntax, re-run build |

---

## Monitoring Approach Evaluation

**Requirement (MON-03):** Assess monitoring approach with documented rationale.

### Chosen Approach: Unified Monitoring with Source Adapters

**Rationale:**

**Why unified framework:**
- **Reduced code duplication:** Common operations (state management, report generation, control mapping) implemented once
- **Consistent classification:** All sources use the same 4-tier classification system
- **Simplified maintenance:** Bug fixes and enhancements apply to all sources
- **Cross-source correlation:** Future capability to detect related changes across sources
- **Single state file:** Easier backup, restore, and troubleshooting

**Why source adapters:**
- **Separation of concerns:** Each adapter focuses on its data source specifics
- **Independent schedules:** Learn runs daily, Regulatory runs weekly (different change frequencies)
- **Extensibility:** Adding new sources (e.g., Azure Updates, Microsoft Tech Community) is straightforward
- **Different workflows:** Learn changes can be auto-drafted, regulatory changes require human review

**Why manual AI-assisted review:**
- **Cost control:** User decides when to invoke AI assistance (not every run)
- **Human oversight:** Critical for regulatory content per CONTRIBUTING.md
- **Flexibility:** User can review subset of changes, skip low-priority items
- **Safety:** Prevents automated commits of incorrect edits

### Alternative Approaches Considered

#### Alternative 1: Separate Independent Monitors

**Description:** Maintain completely separate scripts, state files, and report directories for Learn vs. Regulatory.

**Pros:**
- Complete independence (failure in one doesn't affect the other)
- Simpler initial implementation

**Cons:**
- **Code duplication:** 60-70% of code is identical (state management, classification, reporting)
- **Inconsistent classification:** Hard to maintain consistent standards across monitors
- **Multiple state files:** `data/learn-state.json` + `data/regulatory-state.json`
- **Multiple report dirs:** `reports/learn-changes/` + `reports/regulatory-changes/`
- **Maintenance burden:** Bug fixes need to be applied twice

**Decision:** Rejected. The duplication cost outweighs the independence benefit.

#### Alternative 2: Fully Automated with GitHub Actions

**Description:** GitHub Actions workflow automatically invokes Claude API to draft and commit edits when changes detected.

**Pros:**
- Fully automated, no human invocation needed
- Faster response to changes

**Cons:**
- **API costs:** ~$0.14 per Learn Monitor run × 365 days = ~$51/year (plus regulatory runs)
- **Safety risk:** Automated commits of incorrect edits
- **Claude API key in GitHub Secrets:** Security consideration
- **No human review gate:** Violates CONTRIBUTING.md requirement for regulatory content

**Decision:** Rejected for now. Manual invocation provides better cost control and safety. Could revisit as "Phase 4" enhancement with proper guardrails.

#### Alternative 3: Polling vs. Push-Based

**Description:** Instead of polling external sources on a schedule, use webhooks or RSS feeds to get push notifications.

**Pros:**
- More real-time detection
- Lower polling overhead

**Cons:**
- **Microsoft Learn has no webhooks:** Would need RSS feed or undocumented API
- **Federal Register has RSS:** But still requires polling to fetch full content
- **FINRA has no RSS:** Web scraping still required
- **Complexity:** Managing webhook endpoints, authentication, security
- **Reliability:** Push-based systems fail silently; polling failures are obvious

**Decision:** Rejected. Polling is reliable, simple, and sufficient for the framework's needs (daily/weekly cadence acceptable).

---

## State AI Law Monitoring

**Status:** Manual monitoring (not automated)

**Coverage:**
- Colorado AI Act (SB 24-205) - Effective February 1, 2026
- California AI Transparency Act (AB 2013) - Signed September 2024
- New York City Local Law 144 - Effective July 2023
- Illinois Biometric Information Privacy Act (BIPA) - Relevant to AI
- Texas Data Privacy and Security Act (HB 4) - Effective July 2024

**Process:**
- Monthly review of state legislature tracking services
- Quarterly review of framework for state law alignment
- Ad-hoc updates when new laws enacted

**Why not automated:**
- No unified API for state legislature tracking
- High variance in relevance (most state bills not applicable)
- Human judgment required to assess applicability to M365 AI agents
- Low change frequency (quarterly review sufficient)

**Future consideration:** Add RSS feeds for key state legislature sites if change frequency increases.

---

## Related Documentation

- **Learn Monitor Guide:** [learn-monitor-guide.md](learn-monitor-guide.md) - Learn Monitor user documentation
- **AI-Assisted Review:** [learn-monitor-ai-enhancement.md](learn-monitor-ai-enhancement.md) - AI-assisted review implementation
- **Claude Code Skill:** `.claude/skills/review-learn-changes.md` - User-invocable skill
- **Microsoft Learn URLs:** [microsoft-learn-urls.md](microsoft-learn-urls.md) - Monitored URL watchlist
- **Contributing Guide:** `CONTRIBUTING.md` - Language guidelines and safety rules

---

*FSI Agent Governance Framework v1.2.51 - February 2026*
