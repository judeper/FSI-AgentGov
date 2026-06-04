# Decisions Log

## 2026-06-04: Dependabot PR Cleanup (Rusty)

**Agent:** Rusty (Scripts/CI/Assessment)  
**Outcome:** Wave 1 of PR-board cleanup — 3 Dependabot PRs merged

### Merged PRs

| PR | Change | Merge SHA | Risk Level |
|---|--------|-----------|-----------|
| #348 | msal >=1.36.0 → >=1.37.0 | `99373048` | LOW |
| #349 | gitleaks-action v2 → v3 (Node 20→24 runtime; v2 EOL Sep 16 2026) | `2fa8819f` | MEDIUM (researched as safe) |
| #353 | vitest/vitest-ui 4.1.7 → 4.1.8 (dev deps, SPA test suite passed) | `fe8badca` | LOW |

**Notes:**
- All required CI checks passed (mkdocs-strict, e2e-smoke)
- #349 gate: v2 Node 20 deprecation on Sep 16 2026; v3 compatible with `.gitleaks.toml`
- Account discipline: EMU (`judep_microsoft`) → `judeper` for writes → restored to EMU after

---

## 2026-06-04: Learn Monitor PR Cleanup (Linus)

**Agent:** Linus  
**Outcome:** Wave 2 of PR-board cleanup — 1 sequential merge then consolidation of 9 blocked PRs via conflict-free strategy

### Issue

- PR #342 merged successfully (daily report 2026-05-26)
- Subsequent 9 PRs (#343–#347, #350–#352, #383) all blocked with GitHub merge-conflict errors despite:
  - All CI checks passing (e2e-smoke, mkdocs-strict)
  - Local conflict resolution possible (take incoming `data/monitor-state.json`)

**Root cause:** 4.8MB cumulative `data/monitor-state.json` (each PR is a superset of prior; git cannot auto-merge)

### Resolution: Consolidation Strategy

**Consolidation PR #385** → "chore(monitoring): consolidate 9 Learn Monitor daily reports 05-27..06-04 + latest monitor-state"

- **Merge SHA:** `a45d4bccb879549f71a7b6b11fe78c41e0586fcf`
- **Strategy:** One clean branch off main taking NEWEST `data/monitor-state.json` (from #383/learn-139) + all 9 disjoint daily report files
- **Result:** Conflict-free, all daily reports preserved (2026-05-27 through 2026-06-04)

### Bot PRs Closed as Superseded

All 9 blocks closed with citing comment via REST API (GraphQL EMU workaround):

| PR | Branch | Report Date |
|----|--------|-------------|
| #343 | learn-131 | 2026-05-27 |
| #344 | learn-132 | 2026-05-28 |
| #345 | learn-133 | 2026-05-29 |
| #346 | learn-134 | 2026-05-30 |
| #347 | learn-135 | 2026-05-31 |
| #350 | learn-136 | 2026-06-01 |
| #351 | learn-137 | 2026-06-02 |
| #352 | learn-138 | 2026-06-03 |
| #383 | learn-139 | 2026-06-04 |

### Squad Notes PR

**PR #386** — Added `linus/history.md` + CHANGELOG entry for #385 consolidation

- **Merge SHA:** `ab97bffde06ed5e52bd9ff831a4256b0874a7885`

### Follow-Up

- No Learn-drift control updates needed — daily reports contained standard URL drift data only
- Account discipline: EMU (`judep_microsoft`) → `judeper` for writes → restored to EMU after

---

## Board State After Wave 2

**ZERO open PRs** (no squad, no bot) — cleanup complete

---

## 2026-06-04: SME Escalation Re-verification + Remediation Cycle

**Verifier:** Saul (read-only QA; 2026-06-04)  
**Authors:** Danny (Lead), Linus (Docs)  
**Status:** 5 escalations closed; 2 PRs merged

### Resolved Escalations

#### #360 — Conditional Access JSON Fabrication

| Field | Value |
|-------|-------|
| **Pillar** | Framework (Agent Identity Architecture) |
| **Finding** | Graph-beta JSON payloads for Conditional Access policies were illustrative/fabricated, not API-ready |
| **Verdict** | VERIFIED (corrected payloads confirmed against Graph-beta API docs) |
| **Disposition** | Remediated + Merged |
| **PR** | #389 (SHA `36e2b7f96d5a08264ca3bc89305a90d9169ce105`) |
| **Citation** | https://learn.microsoft.com/en-us/graph/api/resources/conditionalaccesspolicy + 4 supporting MS Learn pages |

---

#### #365 — Customer Key Azure Key Vault SKU Guidance

| Field | Value |
|-------|-------|
| **Pillar** | 1.15 (Customer Key) |
| **Finding** | Control understated Microsoft's SKU recommendation ("Standard minimum" vs Microsoft's "Premium for production") |
| **Verdict** | VERIFIED (MS Learn explicitly: both SKUs supported; Premium strongly recommended for production; Standard for testing/validation only) |
| **Disposition** | Remediated + Merged (line 51 + line 65 updated; Zone 3 table already correct) |
| **PR** | #390 (SHA `fc94872dbe43ddb5c1910e1407ec46d955398224`) |
| **Citation** | https://learn.microsoft.com/en-us/purview/customer-key-set-up |

---

#### #370 — Sentinel MCP Server GA Status

| Field | Value |
|-------|-------|
| **Pillar** | 3.9 (Microsoft Sentinel Integration) |
| **Finding** | Claim "GA November 2025" contradicted by live MS Learn ("What's new" Sep 2025 labels MCP as Preview; Nov section: zero MCP entries) |
| **Verdict** | REFUTED |
| **Disposition** | Remediated + Merged (changed `(GA November 2025)` to `(Preview as of September 2025 — verify at edit time)`) |
| **PR** | #390 (SHA `fc94872dbe43ddb5c1910e1407ec46d955398224`) |
| **Citation** | https://learn.microsoft.com/en-us/azure/sentinel/whats-new + https://learn.microsoft.com/azure/sentinel/datalake/sentinel-mcp-overview |

---

#### #372 — PPAC Actions Page Navigation Hierarchy

| Field | Value |
|-------|-------|
| **Pillar** | 3.7 (Power Platform Compliance Portal) |
| **Finding** | Claim that Actions page lives "under Security node" contradicted by MS Learn (Actions is top-level; Security is peer that surfaces contextual recommendations from Actions) |
| **Verdict** | REFUTED |
| **Disposition** | Remediated + Merged (updated breadcrumb; reframed Security reference as peer surface, not parent) |
| **PR** | #390 (SHA `fc94872dbe43ddb5c1910e1407ec46d955398224`) |
| **Citation** | https://learn.microsoft.com/power-platform/admin/power-platform-advisor |

---

#### #373 — Computer Use Frontier Program Status

| Field | Value |
|-------|-------|
| **Pillar** | 3.13 (Agent 365 Admin Center Analytics) |
| **Finding** | Claim "GA October 2025 (no longer Frontier-gated)" contradicted by live MS Support article (Feb 2026: "currently available through the Frontier program [preview]") |
| **Verdict** | REFUTED |
| **Disposition** | Remediated + Merged (changed to "Researcher with Computer Use is available via the Microsoft Frontier program (preview) as of February 2026 — verify at edit time") |
| **PR** | #390 (SHA `fc94872dbe43ddb5c1910e1407ec46d955398224`) |
| **Citation** | https://support.microsoft.com/topic/get-started-using-researcher-with-computer-use-in-microsoft-365-copilot-frontier + https://learn.microsoft.com/microsoft-365/admin/manage/get-started-frontier |

---

### Durable Learning: M365 Roadmap GA Forecasts Are Not Authoritative

**Pattern Drivers:** #370, #373 (informs future support-status findings)

**Core Rule:** M365 Roadmap items forecast GA dates (e.g., item 511796: "Computer Use — GA November 2025"), but **live MS Learn / Support docs take precedence**. If the live doc labels a feature as Preview or Frontier, that label is source of truth.

**Evidence:**
- #370: Roadmap silent on Sentinel MCP GA; live "What's New" (Sep 2025) still says Preview.
- #373: Roadmap forecasts GA Nov 2025; live Support article (Feb 2026) explicitly says Frontier-program.

**Re-verification Protocol:** Fetch live MS Learn / Support at edit time; cite doc label only; include caveat "verify current status at edit time."

---

### Validation & Merge Summary

| Phase | Status |
|-------|--------|
| #360 Remediation (Danny) | ✅ mkdocs --strict, verify_controls.py, verify_language_rules.py all pass |
| #360 Merge (PR #389) | ✅ All 11 required checks green; merged 2026-06-04T20:08:23Z |
| #365–#373 Remediation (Linus) | ✅ mkdocs --strict, verify_controls.py, verify_language_rules.py all pass |
| #365–#373 Merge (PR #390) | ✅ All 11 required checks green; merged 2026-06-04T20:17:57Z; auto-closed #365, #370, #372, #373 |

**Account Discipline:** All writes via `judeper` account; restored to `judep_microsoft` (EMU) post-merge.
