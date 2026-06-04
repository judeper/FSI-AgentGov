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
