# Linus — Review History

## 2026-06-04 — Sovereign-Cloud Removal (Pillar-1 Playbooks 1.11–1.20, Wave B)

**Mode:** XCUT SOVEREIGN REMOVAL — Pillar-1 playbooks, controls 1.11–1.20
**Branch:** `fix/pb-xcut-sov-pb-p1`
**Commit:** `836aefaaa`
**Result:** ✅ COMPLETE — local branch only; coordinator pushes

### Summary

- **30 files modified**, 618 insertions / 2,196 deletions
- Re-grep returned **ZERO** files with sovereign content in 1.11–1.20 scope
  (only `1.12/troubleshooting.md` remained — intentionally skipped per mission)
- `python scripts/verify_language_rules.py` ✅ no prohibited language found

### Recipe learnings (wave B additions)

- **3-pass Python script approach** again required. Pass 1 (~70% of hits via
  section-deletion and code-block cleanup), pass 2 (~90% via generic patterns
  and file-specific handlers), pass 3 (~99% surgical edits). Final 2 hits were
  direct `edit` tool calls.
- **`!!! warning/danger` admonition removal** needs an extra regex that matches
  the `!!! ... "..."` header line plus the indented body lines that follow — the
  generic pass-2 `delete_admonition_block` helper works well for this.
- **Lowercase `**note.**` blockquotes** (as opposed to `**Sovereign note.**`)
  were missed by pass-2 patterns; always check for case variants.
- **Table column removal** (e.g., "Sovereign clouds where path applies" column
  in 1.14 portal walkthrough) requires a dedicated helper that tracks which
  column index to drop across header, separator, and data rows.
- **JSON `"cloud"` enum fields** (`["Commercial","GCC","GCCHigh","DoD"]`) in
  evidence schema code blocks are easy to miss — target with explicit regex.
- **21Vianet carve-outs** in eDiscovery files (1.19) are a separate sovereign
  pattern. The "Classic eDiscovery retired — except 21Vianet" danger admonition
  required editing the heading + removing the carve-out paragraph while
  preserving the core retirement notice.
- **`sovereignCloud` property in PS output objects** (e.g., `sovereignCloud =
  $Session.Cloud`) needs targeted removal — generic SOV_PAT picks it up but
  Python regex for output object fields needs a line-level match.

---

## 2026-06-04 — Sovereign-Cloud Removal (Pillar-1 Playbooks 1.1–1.10, Wave A)

**Mode:** XCUT SOVEREIGN REMOVAL — Pillar-1 playbooks, controls 1.1–1.10 + `_shared/powershell-baseline.md`
**Branch:** `fix/pb-xcut-sov-pb-p1`
**Commit:** `d35196bc4`
**Result:** ✅ COMPLETE — local branch only; coordinator pushes

### Summary

- **33 files modified**, 256 insertions / 2,375 deletions
- Verified re-grep returned **ZERO** files with sovereign content in scope
- `python scripts/verify_language_rules.py` ✅ no prohibited language found

### Recipe learnings (sovereign removal)

- **Multi-pass approach required.** The first Python script (pass 1) handled
  ~70% of hits via exact-string replacement. The second and third passes caught
  sections that had slightly different text than expected. Total: 3 Python
  scripts + 8 surgical direct `edit` calls.
- **`[ValidateSet]` removal:** the pattern `[ValidateSet(...)]` on one line,
  `[string]$Param = 'default'` on the next is common. Use a single regex
  that matches both lines together; removing just the ValidateSet line leaves
  a standalone `[string]$Param...` that still passes grep if the removed
  ValidateSet contained gov cloud names.
- **Section-header only removals:** when all table rows are removed but the
  section header (e.g., `## Sovereign Cloud Availability`) remains, it still
  shows up in grep. Always remove headers together with their content in one
  pass.
- **Attestation language:** hardcoded phrases like "in the declared sovereign
  cloud" appear in many attestation note sections verbatim. Search for "declared
  sovereign" as a reliable pattern.
- **SOV-* test namespaces:** renamed to FEAT-* (feature availability
  verification) rather than deleted — the underlying Audit Premium / PAYG
  availability checks are still valid for commercial tenants.
- **1.2/powershell-setup.md is large (~100KB).** The `Resolve-Agt12CloudProfile`
  helper was replaced with a simplified `Initialize-Agt12Session` that targets
  Global/Commercial only. The §2 section was rewritten inline in the script.

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
