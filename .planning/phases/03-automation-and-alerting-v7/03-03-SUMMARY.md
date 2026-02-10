# Summary: Plan 03-03

## Status: Complete

## Commits
- `d64fa5a` — fix(cmm): align Dataverse column names in flow and docs with deployed schema; add CHANGELOG v0.3.0 entry

## Files Modified
| File | Action |
|------|--------|
| content-moderation-monitor/scripts/Start-ModerationValidationRunbook.ps1 | VERIFIED — no changes needed |
| content-moderation-monitor/src/moderation-validation-flow.json | MODIFIED — fixed 5 Dataverse column names in Write_Validation_History |
| content-moderation-monitor/src/adaptive-card-moderation-alert.json | VERIFIED — placeholders consistent with runbook output |
| content-moderation-monitor/docs/FLOW_SETUP.md | MODIFIED — fixed 5 column names in mapping table |
| content-moderation-monitor/scripts/private/CMMClient.psm1 | VERIFIED — column names match deployed schema |
| content-moderation-monitor/scripts/create_dataverse_schema.py | VERIFIED — authoritative schema reference |
| content-moderation-monitor/CHANGELOG.md | MODIFIED — added v0.3.0 entry |

## Verification Results
- [x] Moderation level ranking correct (High=1, Medium=2, Low=3)
- [x] Drift direction classification correct (currentRank > baselineRank → Weakened, < → Strengthened, unknown → Changed)
- [x] Batch baseline optimization confirmed (single `Get-ModerationBaseline -ActiveOnly` call, hashtable O(1) lookup)
- [x] Edge cases handled (no baseline → IsFirstRun, query failure → fail open, all first run → HasDrift=false)
- [x] Structural mappings verified (runbook → flow → card → Dataverse) — 5 mismatches found and fixed
- [x] Dataverse write path verified (action order, runAfter conditions, entity set, connection reference)
- [x] FLOW_SETUP.md validation history section complete (Step 4 with column mapping, troubleshooting 403/404/400, hedged language)
- [x] CHANGELOG.md v0.3.0 entry added

## Decisions Made
- **Fixed 5 Dataverse column names** in flow JSON and FLOW_SETUP.md to match the schema deployed by `create_dataverse_schema.py`:
  - `fsi_runid` → `fsi_run_id`
  - `fsi_overallstatus` → `fsi_overall_status`
  - `fsi_violationcount` → `fsi_violation_count`
  - `fsi_totalagents` → `fsi_total_agents`
  - `fsi_summaryjson` → `fsi_summary_json`
- CMMClient.psm1 already had the correct underscore pattern — no changes needed there

## Detailed Verification

### Task 1: Drift Detection Logic

**Moderation level comparison:** Correct. `Get-ModerationDriftDirection` uses `$rankMap` (High=1, Medium=2, Low=3). `currentRank > baselineRank` → 'Weakened', `< baselineRank` → 'Strengthened', null rank → 'Changed', equal → 'Unchanged'.

**Batch baseline optimization:** Correct. Single `Get-ModerationBaseline -ActiveOnly` call (lines 304-306), hashtable construction `$baselineMap[$b.AgentId] = $b` (lines 309-311), O(1) lookup via `$baselineMap.ContainsKey($agentId)` (line 339). No per-agent Dataverse queries in drift path.

**Edge cases:**
- No active baseline for agent → `$driftEntry.IsFirstRun = $true` (line 358-359)
- Baseline exists but agent removed → skipped (only iterates `$agentLookup.Keys`)
- All agents first run → `$globalIsFirstRun = $true`, `Drift.HasDrift = $false`, `Drift.DriftedAgents = 0`
- Dataverse query failure → `$baselineQueryFailed = $true` → `$globalIsFirstRun = $true` (fail open)

### Task 2: Structural Consistency (Runbook → Flow → Card → Dataverse)

**Runbook output → Parse_Results schema:** All 24 properties match exactly (RunType, Timestamp, TotalAgents, TotalEnvironments, OverallStatus, Reason, ZoneSummary with Zone1/2/3, Violations array with 9 properties, Drift with HasDrift/IsFirstRun/DriftedAgents/Details, AlertRequired, AlertSeverity).

**Parse_Results → Adaptive card placeholders:** All mapped correctly — ${AlertSeverity}, ${Timestamp}, ${OverallStatus}, ${TotalAgents}, ${TotalEnvironments}, ${Reason}, ${Z1Compliant}, ${Z1Total}, etc. Note: inline card in flow uses a simplified version (header + summary only); full card template is in adaptive-card-moderation-alert.json for reference.

**Parse_Results → Dataverse columns:** 5 column name mismatches found and fixed (see Decisions above). After fix, all 8 columns map correctly.

**Write_Validation_History sequencing:** Correct — runs after Parse_Results [Succeeded]; Check_Alert_Required runs after Write_Validation_History [Succeeded, Failed].

### Task 3: FLOW_SETUP.md

Step 4 covers validation history write completely:
- Column mapping table (8 columns with types and descriptions) — now with corrected column names
- Explains why write runs before alerting
- Troubleshooting table for 403, 404, 400 errors
- Uses FSI hedged language ("supports compliance with", "helps ensure")
- Additional troubleshooting in dedicated section at bottom

### Task 4: CHANGELOG v0.3.0

Added complete entry documenting all Phase 3 additions (runbook, baseline capture, adaptive card, flow, FLOW_SETUP.md) and changes (Save-CMMBaseline completion, Get-ModerationBaseline enhancement, version bump).

## Discovered Work
- The inline adaptive card in the flow's `Post_Teams_Card` action is a simplified summary-only version. Zone replace calls (`${Z1Total}`, `${Z1Compliant}`, etc.) are no-ops since those placeholders don't appear in the simplified card. This is functional but could be cleaned up in a future cosmetic pass (low priority, no runtime impact).
- The inline card also lacks `${Z3Compliant}` in the replace chain (11 replaces total, 5 are no-ops). Again, cosmetic only.
