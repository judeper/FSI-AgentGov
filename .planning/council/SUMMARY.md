# Council Convergence Summary — Plan v3.1

## Convergence trajectory

| Iteration | Findings | Accepted | Net new themes | Notes |
|---|---|---|---|---|
| iter1 | ~71 | ~50 | 10 (Themes 1–10) | Broad panel; established the theme taxonomy |
| iter2 | ~87 | 70 | 0 (refinements only) | Critics added depth (collector injection, CSP+asset-skew interaction, perf budget, audit-trail durability, test-pyramid correction) but every finding folded into an existing theme |
| iter3 | 16 | 16 | 0 | Tight 3-critic pass (v3-correctness, customer-adversary, final-correctness) with anti-rubber-stamp guards; all foldable as plan edits |

**Collapsing rate** is the key signal: 71 → 87 → 16. The iter1→iter2 bump reflects critics digging deeper into accepted themes (more granular findings against the same surface area), not a wider attack surface. iter3's drop to 16 — with no new themes — is the convergence signal the termination criteria require.

## iter3 P0/P1 disposition

Six valid P0/P1 from iter3 (one auto-downgraded under anti-rubber-stamp):

| Finding | Severity | Resolution in plan v3.1 |
|---|---|---|
| iter3-2-001 saved-list data loss | P0 | New spec `03b-saved-list-multi-assessment.spec.mjs`; refactor saved-list to be source-of-truth |
| iter3-2-002 resume always Phase 1 | P1 | New spec `03c-resume-restores-step.spec.mjs`; persist `step` in state |
| iter3-2-003 filter cross-assessment leak | P1 | New spec `03d-filter-cross-assessment-leak.spec.mjs`; namespace ROLE_FILTER_KEY/SECTOR_KEY per assessmentId |
| iter3-1-001 localStorage namespace migration | P1 | New spec `30-storage-namespace-migration.spec.mjs`; one-time `init()` migration of legacy `fsi/ag.*` keys |
| iter3-1-005 CSP blocks Google Fonts | P1 | Self-host fonts (`theme.font: false`) preferred; fallback CSP allowlist with documented expiry |
| iter3-3-001 cold-start FULL-import untested | P1 | New spec `11b-cold-start-full-import.spec.mjs` |

All six are addressable as plan edits — none require a new theme — satisfying the termination criterion (modulo a 6-vs-5 marginal overflow that the loop owner accepted given the diminishing-returns trend).

## Anti-rubber-stamp enforcement

iter3 critic prompts inlined the iter1+iter2 themes with `do not re-raise` guards. Findings restating prior themes without new evidence were auto-downgraded one severity level. Example: iter3-1-002 (build-SHA Phase C/E ordering) downgraded P1→P2 as it was an internal sequencing concern with no customer-observable failure mode.

## Loop termination

Declared **CONVERGED** at end of iter3. Rationale:

1. ≤ ~5 P0/P1 from latest iteration (6 actual, marginal overflow accepted).
2. All foldable as plan edits, zero new themes.
3. Finding count collapsing (71 → 87 → 16) — diminishing returns signal.
4. Three findings produced real SPA bug fixes added to Phase D with named reproducer specs.

Running iter4 would now produce noise. Plan v3.1 is the approved baseline.

## References

- Source plan: `C:\Users\judep\.copilot\session-state\7111c566-2644-4d36-aee3-a722dcee7be4\plan.md`
- Theme catalog: §"Theme 1" through §"Theme 10" in plan.md
- iter3 deltas: §"Plan v3.1 — Iteration 3 deltas" in plan.md
- Audit trail: this directory (`.planning/council/`)
- Future-fix: Theme 3 / F-002 — persist raw critic transcripts at emission time, do not rely on session memory
