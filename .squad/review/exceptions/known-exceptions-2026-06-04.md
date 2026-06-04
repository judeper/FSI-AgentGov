# Known Exceptions — 2026-06-04

## Exception 8 — Learn Monitor Consolidation Doctrine

**Registered:** 2026-06-04  
**Source:** Linus / PR-board cleanup Wave 2 (Learn Monitor PRs #342–#352, #383)  
**Status:** Active  

### Description

When multiple Learn Monitor bot PRs queue up sequentially with cumulative `data/monitor-state.json` conflicts (4.8MB superset caching pattern):

**❌ DO NOT attempt:**
- Sequential merges (PR1 → main, then PR2 → main, etc.)
- Local conflict resolution + force-push to individual PR branches
- Awaiting GitHub auto-rebase (does not bypass merge-conflict detection)

**✅ DO instead — Consolidation Strategy:**
1. Create ONE consolidation branch off current main
2. Cherry-pick or add the NEWEST PR's `data/monitor-state.json` (the authoritative final state)
3. Cherry-pick or add every disjoint daily report file (`reports/monitoring/learn-changes-*.md`) from each blocked PR
4. Push consolidation branch via tokenized URL (if EMU account active)
5. Open single conflict-free PR, merge (REST API + EMU workaround if needed)
6. Close superseded bot PRs with citing comment (REST API closes, not GraphQL to avoid EMU Unauthorized)

### Rationale

- Each bot PR's monitor-state.json is a cumulative superset of the prior state — only the NEWEST is authoritative
- The 4.8MB file size + JSON structure defeats git auto-merge even when the merge would be resolvable locally
- GitHub's merge-conflict detection persists even after local resolution + force-push (by design, safety feature)
- The daily report files are disjoint per PR — no conflicts; consolidation preserves full audit trail

### Evidence

**Wave 2 Cleanup (2026-06-04):**
- PR #342 (2026-05-26 report) → merged successfully ✅
- PRs #343–#347, #350–#352, #383 (2026-05-27 through 2026-06-04 reports) → all blocked with merge-conflict errors ❌
- Attempts to resolve: local merge, local rebase, force-push, REST API merge with/without admin flag → all rejected ❌
- Consolidation PR #385 built per doctrine → merged conflict-free ✅
- Superseded PRs closed via REST API with comment citing #385 → all closed ✅
- Final state: All 10 daily reports + newest monitor-state.json on main

### Implementation Notes

- When closing superseded PRs via REST API, use `PATCH /repos/{owner}/{repo}/pulls/{n}` with `{state: "closed"}` to avoid GraphQL EMU Unauthorized on GraphQL mutations
- The consolidation branch must be built off **current main** (after any prior Learn Monitor merges) to get the right superset base
- Store consolidation PR SHA in commit message for audit trail

---

### Related Procedures

- `.squad/review/reports/merge-log-2026-06-04.md` — Wave 2 consolidation details + PR closure log
- `.squad/decisions/decisions.md` — Linus decision drop: Learn Monitor PR Cleanup outcome
