# Linus — Review History

## Learnings

### Sovereign-Removal Recipe (2026-06-04)

- **Recipe file:** `maintainers-local/tmp/pb-findings/XCUT-sovereign-REMOVAL.md` — read this first on any future batch before touching files.
- **Three delete classes:** (1) dedicated heading+body sections, (2) sovereign-only admonition/callout blocks (`> **Sovereign cloud.**`), (3) per-cloud endpoint/table rows. Each needs a distinct edit pattern.
- **Inline mixed sentences:** keep the commercial clause, drop the sovereign qualifier — do not delete the whole sentence.
- **Downstream anchors break:** when deleting whole scenarios the TOC anchor and the `§N` heading numbers both shift; update the TOC link text, the heading, and any inline `§N L4` cross-references in the same pass.
- **Scenario count in section title** is a literal string — update it to match the new count (25 → 23 after removing Scenarios 14 and 24).
- **Expected mkdocs failures:** nav entry (mkdocs.yml, coordinator) and 1.20 inbound link (next batch) both fail `--strict` — this is documented in the recipe and is not an error in Linus-owned files.
- **ValidateSet PowerShell params:** when a helper script has `[ValidateSet('Commercial','GCC','GCCH','DoD')]`, simplify to `[string] $Param = 'Commercial'` rather than leaving a dangling ValidateSet with no valid gov-cloud options.

## 2026-06-04 — Escalation Re-Verification Batch (#365 #370 #372 #373)

**Mode:** REMEDIATION (4 verified SME-escalation corrections, one batch PR)
**Scope:** 4 control files across Pillars 1 and 3
**Result:** ✅ COMPLETE — PR #390 opened (ready for review; Danny merges)

### Corrections Applied

| Issue | File | Change |
|-------|------|--------|
| #370 | `3.9-microsoft-sentinel-integration.md` | Sentinel MCP Server: "GA November 2025" → "Preview as of September 2025" with live-page verify prompt |
| #372 | `3.7-ppac-security-posture-assessment.md` | Actions page re-framed as top-level PPAC peer, not child of Security node |
| #373 | `3.13-agent-365-admin-center-analytics.md` | Computer Use: removed "GA / no longer Frontier-gated"; rewritten as Frontier program (preview, Feb 2026) |
| #365 | `1.15-encryption-data-in-transit-and-at-rest.md` | Customer Key SKU: updated both line ~51 and ~65 to match MS Learn verbatim — Premium recommended for production, Standard for testing only |

### Validation Results
- `mkdocs build --strict` ✅ zero errors, zero warnings
- `python scripts/verify_controls.py` ✅ all 78 controls valid
- `python scripts/verify_language_rules.py` ✅ no prohibited language found

### Git / PR
- Branch: `fix/escalation-reverify-batch-365-370-372-373`
- Commit: `1b8324657`
- PR: #390 https://github.com/judeper/FSI-AgentGov/pull/390 (ready-for-review; closes #365 #370 #372 #373)
- EMU account: restored to `judep_microsoft`



## 2026-06-04 — Learn Monitor Consolidation (Follow-Up: All 9 Remaining Bot PRs)

**Mode:** CONSOLIDATION (one squash PR + close 9 bot PRs)
**Scope:** Bot PRs #343-#383 (9 PRs with conflicting monitor-state.json)
**Result:** ✅ COMPLETE

### Root Cause of Prior Failure
Earlier attempt tried sequential per-PR merge — GitHub's merge conflict detection persisted because the local conflict-resolutions were never pushed via the tokenized URL fallback. Per-PR sequential merging of a 4.8MB cumulative JSON was the wrong approach.

### Consolidation Approach
Single `chore/consolidate-learn-monitor-reports` branch off current main:
1. Took newest `data/monitor-state.json` + `.backup` from `origin/monitoring/learn-139` (PR #383)
2. Grabbed each of the 9 disjoint daily report files from their respective origin branches
3. Committed, pushed via tokenized URL (Windows credential manager bypass)
4. Created PR #385, waited for CI (shim correctly emitted e2e-smoke + mkdocs-strict: success)
5. Merged PR #385 via REST API (EMU GraphQL workaround)
6. Commented + closed PRs #343, #344, #345, #346, #347, #350, #351, #352, #383 via REST API

### Outcomes

| Item | Result |
|------|--------|
| Consolidation PR | #385 merged (SHA: `a45d4bccb879549f71a7b6b11fe78c41e0586fcf`) |
| Open PR board | Empty — no bot PRs remaining |
| 10 daily reports on main | 05-26 through 06-04 all present |
| monitor-state.json | Newest version (learn-139/PR #383) |
| EMU account | Restored to `judep_microsoft` |

### Follow-Up Drift Items
None. No control content updates triggered by any of the 9 daily reports.

### Key Lessons
- **Tokenized push** is mandatory for Windows (credential manager caches EMU token)
- **REST API** is mandatory for merge/comment/close (gh GraphQL fails for EMU accounts)
- **Consolidation beats sequential** for cumulative JSON files with divergent bot branches

---

## 2026-06-04 — Learn Monitor PR Cleanup (Attempt 1 — Blocked)

**Mode:** SEQUENTIAL MERGE (bot drift reports)
**Scope:** 10 Learn Monitor scheduled-report PRs (#342-#383)
**Result:** 1/10 merged; 9/10 blocked by merge conflict detection

- **PR #342** (2026-05-26): ✅ **MERGED** (SHA: `c3ea45eb6`)
- **PRs #343-#383**: ❌ **BLOCKED** — local conflict-resolutions never pushed via tokenized URL

---

## 2026-06-03 — Controls Pilot Review

**Mode:** FINDINGS-FIRST (discovery only, no doc edits)
**Scope:** 5 pilot control files — 1.5, 2.1, 2.6, 3.8, 4.6
**Finding IDs used:** F-20260603-100 through F-20260603-104 (5 findings)
**Index:** `.squad/review/reports/INDEX-controls-20260603.md`

### Findings raised

| ID | Severity | File | Summary |
|----|----------|------|---------|
| F-20260603-100 | P1 | 2.6 | Additional Resources line 289: "built-in evaluators reference" label points to observability overview page |
| F-20260603-101 | P1 | 2.6 | Additional Resources line 288: "evaluation-approach-gen-ai" URL resolves to same observability page (link drift) |
| F-20260603-102 | P2 | 2.6 | Body text uses stale "Azure AI Foundry" brand at lines 42, 137, 138 vs correct "Microsoft Foundry" |
| F-20260603-103 | P2 | 3.8 | Feature Status table line 25: Agent overview listed GA (Status col) with future Expected GA date — contradiction |
| F-20260603-104 | P2 | instructions | fsi-control-template.instructions.md section 8 name "Implementation Guides" ≠ canonical "Implementation Playbooks" |

### Controls cleared (no findings)

- **1.5** (DLP and Sensitivity Labels) — FSI language clean; preview labels correct; links appear current
- **2.1** (Managed Environments) — Fed SR 26-2 naming correct; internal link to `agent-identity-architecture.md` live
- **4.6** (Grounding Scope Governance) — FINRA RN 25-07 clarification correct; RCD prerequisites documented

### Next-ID available

F-20260603-105 (within this date range); or F-20260604-100 on the next run date.

---

## 2026-06-03 — Framework Layer Review (Phase 2 Stage A)

**Mode:** FINDINGS-FIRST (discovery only, no doc edits)
**Scope:** All 15 files in `docs/framework/`
**Finding IDs used:** F-20260603-001 through F-20260603-003 (Linus framework reservation)
**Index:** `.squad/review/findings/INDEX-framework-20260603.md`

### Findings raised

| ID | Severity | File | Summary |
|----|----------|------|---------|
| F-20260603-001 | P1 | relationship-to-copilotgov.md | Comparison table states 71 controls / 284 playbooks — stale; correct values are 78 / 312 |
| F-20260603-002 | P2 | transformation-patterns.md | Line 88: OCC Bulletin 2026-13 missing "(formerly OCC 2011-12)" in same sentence where Fed SR 26-2 has "(formerly SR 11-7)" |
| F-20260603-003 | P1 | agent-identity-architecture.md | CA policy JSON examples use non-standard API fields `includeAgents` and `agentRisk` not present in Graph API conditionalAccessConditionSet schema |

### Files cleared (no findings)

regulatory-framework.md, zones-and-tiers.md, governance-fundamentals.md,
agent-lifecycle.md, operating-model.md, governance-cadence.md,
agentic-capability-drivers.md, agentic-coe.md, solutions-integration.md,
adoption-roadmap.md, executive-summary.md, index.md — all passed
banned-phrase scan, old-designator scan, and spot GA/Preview checks.

---

## 2026-06-03 — Phase 5: Apply Verified Remediations (DRY-RUN)

**Mode:** APPLY (local branch only, no push)
**Branch:** `review/pilot-remediations-20260603`
**Inputs:** Phase 4 remediation plan (Danny) + 8 Livingston verification certificates
**Date applied:** 2026-06-03

### Batches applied (5 commits)

| Batch | Findings | File(s) | Commit SHA | Status |
|-------|----------|---------|------------|--------|
| B1 | F-001 | `docs/framework/relationship-to-copilotgov.md` | 037df9330 | ✅ committed |
| B2 | F-002 | `docs/framework/transformation-patterns.md` | 378ed1808 | ✅ committed |
| B3 | F-100, F-101, F-102 | `docs/controls/pillar-2-management/2.6-model-risk-management-sr-26-2.md` | 94b542b37 | ✅ committed |
| B4 | F-103 | `docs/controls/pillar-3-reporting/3.8-copilot-hub-and-governance-dashboard.md` | a941d77b1 | ✅ committed |
| B5 | F-003 (Option B only) | `docs/framework/agent-identity-architecture.md` | 6ff514938 | ✅ committed (DRAFT PR) |

### Deferred / escalated

| Item | Reason | Artifact |
|------|--------|---------|
| B6 (F-104) | Outside editable set — `.github/instructions/` requires repo owner sign-off | `.squad/review/remediations/B6-template-label-DEFERRED.md` |
| E1 (F-003 Option A) | Escalated — verifier refused to certify precise JSON fix; requires Microsoft Graph beta SME | `.squad/review/escalated/ISSUE-003-ca-agent-fields.md` |

### Validation results

| Command | Result |
|---------|--------|
| `mkdocs build --strict` | ✅ PASS — 0 errors, 0 warnings (78.08s) |
| `python scripts/verify_controls.py` | ✅ PASS — all 78 controls valid |
| `python scripts/verify_language_rules.py` | ✅ PASS — no prohibited language found |
