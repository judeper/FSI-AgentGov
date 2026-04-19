# Scorched-Earth Audit Methodology

**Status:** Active — adopted April 2026 after three successive "deep audit" passes failed to find issues that a fourth pass surfaced.

> Internal process doc. Not published to the docs site.

---

## Why this exists

Every prior "deep audit" of this repository was a **deeper sample**, not an enumeration. The same failure mode repeated:

| Pass | What was checked | What was missed | Root cause |
|---|---|---|---|
| Original Monday-readiness | 4 user-facing surfaces (README, site, assessment) | Solutions Bridge wired to nothing; v1.3 footers everywhere | Sampled what a customer would *click*, not what *exists* |
| Post-fix "deep audit" | Top-of-tree docs + framework + controls + 1 shared playbook | 312 per-control playbook footers; 3 AI-config files; advanced-impl page footers | Scope was **assumption-driven** ("where I expect drift to be") not **enumeration-driven** |
| AI-files check | `.github/copilot-instructions.md`, `.claude/CLAUDE.md`, `.claude/skills/verify-ui.md` | Per-control playbooks (3-clicks-deep) | Treated playbooks as second-tier despite customers clicking into them |
| Drift-sweep (this methodology) | All 12 dimensions enumerated | SPA scoring modal "72 controls" string; 16 cells across 6 Excel files; control authoring template still on v1.2 | These were caught — methodology worked |

**Three structural failures we keep making:**

1. **No complete enumeration step.** We list files we expect to be affected, instead of running ONE repo-wide grep for the symptom and triaging EVERY hit.
2. **No classification matrix.** Hits are implicitly "in scope" or "out of scope" — never explicitly **MUST CHANGE / MUST KEEP / FLAG-FOR-HUMAN.**
3. **Single-dimension audit.** We chase one drift symptom (e.g., "v1.3 in footers"). We never ask "what *other* drift dimensions might exist that we haven't grep'd for?"

## The 12 rules

1. **Enumerate, don't sample.** ONE repo-wide grep per symptom. No file lists from memory.
2. **Classify every single hit** into 🔴 MUST-CHANGE / 🟢 MUST-KEEP / 🟡 FLAG-FOR-HUMAN.
3. **Document the classification rule** so a second human can re-run and verify.
4. **Emit a coverage report** before executing: "N hits → X change, Y keep, Z flag."
5. **Execute fixes**, then **re-run the same enumeration** and verify residuals == initial KEEP count.
6. **Open the aperture.** Beyond the obvious symptom, ask: what *adjacent* drift dimensions could exist? List them, grep them, classify them.
7. **Pin a clean baseline first.** Before any bulk operation, prove the pre-state passes validation, so post-state failures aren't misattributed.
8. **Commit isolation.** Group atomic logical units into separate commits so any one can be rolled back without entangling others.
9. **Programmatic diff verification, not statistical spot-check.** Parse `git diff`, assert each change matches the expected transformation. (6 random samples = 4.6% — won't catch correlated regex bugs.)
10. **Autopilot defaults.** When user input unavailable: ambiguous → FLAG_HUMAN + leave alone (conservative). Never bulk-edit a FLAG_HUMAN row. If ≥20% of a dimension is FLAG_HUMAN, refine rules and re-classify.
11. **Honesty over completeness.** Don't bump version claims (e.g., "v1.4 compatible") without positive re-validation evidence. Companion-repo solution version stamps in particular: leave alone unless re-validation evidence exists.
12. **Time budget + ship trigger.** Set a wall-clock budget per phase. On 50% overrun, commit P0+P1 work, document P2 deferred, ship partial. Better a clean partial than incomplete attempt at full.

## When to invoke this methodology

**USE for:**
- Version bump (e.g., v1.3.x → v1.4.0)
- Count change (e.g., 71 → 78 controls, 33 → 35 solutions)
- Structural rename (folder, schema field, template)
- Any repo-wide claim ("all controls", "every page", "100% coverage")

**Do NOT invoke for:**
- Single-file fixes
- Typo passes
- Content additions to a known location

**Threshold rule:** If the symptom could plausibly appear in ≥3 file types OR ≥3 directories, invoke this methodology. Otherwise direct edit is fine.

## Standard 12 drift dimensions

| Dim | Name | Symptom regex | Notes |
|---|---|---|---|
| A | Version stamps | `v1\.[0-3](\.\d+)?` | Exclude `CHANGELOG-v1.[0-3].md`, `package-lock.json`, `node_modules/`, `site/`, `releases/` |
| B | Solution count | `\b(28\|33\|35)\s+(live\s+)?solutions?\b` | `35 live = 35 lock entries` is consistent (preview-placeholder concept retired in v1.4.0) |
| C | Control count | `\b(71\|72)[\s\-]+controls?\b` | Historical changelog rows are MUST_KEEP; check live docs |
| D | Year/month stamps | `v1\.4\.0[\s\-—\|]+(NotApril)\s+2026` | Catches footer date mismatches |
| E | Manifest field completeness | Programmatic JSON walk for empty fields | Catches "wired-to-nothing" patterns like Solutions Bridge |
| F | Lock file cross-consistency | Diff `solutions-lock.json` keys vs companion-repo folders | Catches added/removed solutions out of sync |
| G | Excel templates | openpyxl walk over `docs/downloads/*.xlsx` for v1.3 / 71 / 72 | AMWINS downloads these |
| H | Workflow / CI files | Grep `.github/workflows/*.yml` for v1.3 + counts | Catches CI depending on stale paths/versions |
| I | Top-level meta files | Grep root `*.md` for v1.0-v1.3 | README, AGENTS.md, CONTRIBUTING — historical changelog table is OK |
| J | Companion repo cross-refs | Grep companion repo for "v1.3 framework" | **AUDIT-ONLY by default per rule 11** — bumping requires positive re-validation |
| K | Schema / template files | `docs/templates/**/*.md` | Affects future content — P1 not P0 |
| L | Assessment SPA | `docs/javascripts/assessment*.js`, `docs/stylesheets/assessment.css`, `overrides/main.html` | Customer-visible, P0 |

Path verification BEFORE running any dimension: actual paths drift over time (e.g., SPA may move from `docs/assessment/` to `docs/javascripts/`). Always `Test-Path` / `Get-ChildItem` first.

## Workflow checklist

```
[ ] Phase 0: Pin clean baseline (mkdocs build --strict on pre-state)
[ ] Phase 1: Enumeration sweep — grep each dimension, count hits, classify TRIVIAL/MEDIUM/LARGE
[ ] Phase 2: Per-dimension classification — write findings file with rule documentation
[ ] Phase 3: Coverage report — N hits → X change, Y keep, Z flag (gate to execution)
[ ] Phase 4: Execute MUST_CHANGE fixes, atomic commit per dimension
[ ] Phase 5: Re-run grep, verify residuals == MUST_KEEP count
[ ] Phase 6: Single push at end (Pages throttle protection), monitor deploy, verify live
[ ] Phase 7: Update flag-for-human file with un-fixed items
```

## Findings file template

Per-dimension findings live in session workspace as `audit-dim-X.md`:

```markdown
# Dimension X — <Name>
**Total hits:** N | **MUST_CHANGE:** X | **MUST_KEEP:** Y | **FLAG_HUMAN:** Z

**Classification rules:**
- 🔴 MUST_CHANGE: <explicit pattern>
- 🟢 MUST_KEEP: <explicit allowlist patterns>
- 🟡 FLAG_HUMAN: <ambiguity criteria>

| File | Line | Match | Class | Priority | Action | Status |
|---|---|---|---|---|---|---|
```

## Priority levels

Every finding gets P0 / P1 / P2:

- **P0** = Customer-visible immediately (live site, assessment SPA, README, downloadable artifacts)
- **P1** = Will be visible eventually (templates, advanced-impl pages, schemas)
- **P2** = Internal only (CI, scripts, AI config history lines, audit reports)

Only P0 + P1 must ship before customer-facing milestones. P2 can defer.

## Session ownership

If this methodology is being run as part of a GSD workflow, see `.github/instructions/session-ownership.instructions.md`. Findings files (`files/audit-*.md` in session workspace) are safe to write; shared state files (`.planning/STATE.md`, `ROADMAP.md`) require ownership claim.
