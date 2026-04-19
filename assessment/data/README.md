# `assessment/data/`

Static data assets consumed by the assessment SPA and by the Python
scoring engine.

## `solutions-lock.json`

Locked snapshot of `solutions.json` from the
[`FSI-AgentGov-Solutions`](https://github.com/judeper/FSI-AgentGov-Solutions)
companion repository.

### Contract

* The lock is **fetched at framework-release time** from a tagged
  release of the solutions repo (currently `v1.4.0`). It is **never**
  fetched at runtime, and CI does **not** cross repos at PR time.
* Provides the rich metadata (`name`, `version`, `domain`, `tier`,
  `description`, `url`, `prerequisites`, `verification`) that the E1
  drawer and E7 agenda export render.
* `assessment/manifest/controls.json` references solutions by
  **folder-name ID only** (kebab-case strings); the lock provides
  everything else.

### Refreshing

```bash
python scripts/refresh_solutions_lock.py --tag v1.4.0
```

The refresh script verifies `schemaVersion` starts with `1.4.` and
that the expected solution count and required IDs are present.

### Coverage scope

The lock file maps the **subset of controls that have a dedicated
companion solution** in FSI-AgentGov-Solutions (35 today out of the
framework's 78 controls). It is not intended to be a 1:1 mirror of
the control catalog.

Many controls have an empty `solutions[]` array in
`assessment/manifest/controls.json`. This reflects the framework's
**selective-mapping principle**: not all controls warrant a dedicated
companion automation. Many are fully operated via native Microsoft
admin surfaces (Entra, Purview, Power Platform Admin Center,
SharePoint Admin) and are verified by the framework's collectors.
An empty `solutions[]` is by-design, not a backlog item.

Consult each control's `automation` field (`full` / `partial` /
`manual`) for verification feasibility, and the corresponding control
doc under `docs/controls/` for native-admin guidance. For the full
catalog and coverage rationale, see
`docs/reference/solutions-index.md` (Coverage scope section).

### Schema (1.4.x)

```json
{
  "schemaVersion": "1.4.0",
  "solutions": {
    "agent-observability-foundation": {
      "id": "agent-observability-foundation",
      "name": "Agent Observability Foundation",
      "version": "1.0.0",
      "domain": "monitoring",
      "tier": "1",
      "description": "...",
      "url": "https://judeper.github.io/FSI-AgentGov-Solutions/solutions/agent-observability-foundation/",
      "prerequisites": { "Power Platform Admin": "..." },
      "verification": "..."
    }
  }
}
```

### Graceful degradation

If a solution ID referenced by `controls.json.solutions[]` is missing
from the lock, the SPA renders `(solution pending)` instead of a chip.
If the lock file is missing entirely, E1/E7 still render — just
without the solutions section.

---

## Portal Export Schema (`exportJSON` / `exportRoleSection`)

The Step 6 **Export → JSON** button (and the per-role section export)
emits a versioned envelope. Downstream tools — most notably the
companion **FSI-Assessment-Agent** that converts portal exports into
customer-ready Markdown reports — key off this envelope to detect
drift, validate input shape, and consume pre-computed scores instead
of re-implementing the scoring algorithm.

The envelope was added in v1.4.1-prep (see `CHANGELOG-v1.4.md` →
*Portal Export Envelope*) and is **fully backwards-compatible**: every
top-level key present in pre-1.4.1 exports remains at the same path.

### Top-level shape (full export)

```json
{
  "_metadata": {
    "exportSchemaVersion": 1,
    "schemaType": "full",
    "frameworkVersion": "1.4.0",
    "manifestSchemaVersion": "1.4.0",
    "exportedAt": "2026-04-19T17:00:00.000Z",
    "exportedBy": "Jane Doe"
  },
  "_computedScores": {
    "overall": 47,
    "perPillar": { "1": 41, "2": 12, "3": 14, "4": 50 },
    "perControl": { "1.1": 1.0, "1.2": 0.0, "1.3": 0.5, "...": null }
  },
  "assessmentStatus": "in-progress",
  "assessmentId": "uuid-…",
  "assessmentName": "…",
  "createdAt": "…", "updatedAt": "…",
  "scoping": { "organizationName": "…", "assessorName": "…", "assessorRole": "…",
               "institutionType": "…", "zones": [1,2,3], "adoptionPhase": 0,
               "regulations": ["…"], "scope": "full" },
  "responses":  { "1.1": { "answer": "yes|partial|no|na", "notes": "…", "evidenceRef": "…" } },
  "drilldown":  { "1.1": { "subQuestionId": "yes|no" } },
  "overrides":  { "1.1": { "applicable": false, "note": "…" } },
  "completedSteps": ["scoping", "phase1"],
  "selectedSector": "…", "roleFilter": "…", "priorityMode": "full|starter", "priorityExpanded": false
}
```

### Field reference

| Key                  | Type   | Notes |
|----------------------|--------|-------|
| `_metadata.exportSchemaVersion` | int  | Bumped on any breaking change to envelope shape. Currently `1`. |
| `_metadata.schemaType`          | enum | `"full"` (`exportJSON`) or `"section"` (`exportRoleSection`). |
| `_metadata.frameworkVersion`    | str  | Sourced from `FRAMEWORK_VERSION` JS constant (kept in sync with `package.json` + `mkdocs.yml`). |
| `_metadata.manifestSchemaVersion` | str | Sourced from the loaded `solutions-lock.json` schemaVersion. |
| `_metadata.exportedAt`          | str  | ISO-8601, UTC. Snapshot at export time. |
| `_metadata.exportedBy`          | str  | `scoping.assessorName` at export time. |
| `_computedScores.overall`       | int\|null | `Math.round(sum/count * 100)` over all controls; `null` if no scoreable controls (e.g., All-N/A assessment). |
| `_computedScores.perPillar.{1..4}` | int\|null | Same algorithm scoped to pillar. |
| `_computedScores.perControl.{id}` | float\|null | `1.0` (yes), `0.5` (partial without drilldown), `yes/total` (partial with drilldown), `0.0` (no), `null` (n/a or unanswered). |
| `assessmentStatus`              | enum | `"final"` only when `completedSteps` includes `"full"` or `"complete"`; else `"in-progress"` if any responses; else `"draft"`. |

### Section export (`exportRoleSection`)

Identical envelope (with `schemaType: "section"`) plus a top-level
`sectionExport: { role, controlIds, exportedAt, exportedBy }` key
that distinguishes it from a full export. The importer at line ~870
of `assessment-app.js` discriminates on the `sectionExport` key
presence and routes to `importSection()` instead of replacing state.

### Backwards compatibility & importer contract

`importState` (line ~814 of `assessment-app.js`) reads named state
keys explicitly and **silently ignores** `_metadata`,
`_computedScores`, and `assessmentStatus`. This is intentional:

* `_computedScores` is a snapshot, not state. Importing dropping it
  forces a recompute on the next export — preventing tampered or
  stale scores from propagating across roundtrips.
* `_metadata.frameworkVersion` is similarly a snapshot of the version
  *that produced* the file, never the version that imported it.
* `assessmentStatus` is re-derived on every export from
  `completedSteps` + `responses`, so importing a "final" file into a
  newer SPA correctly re-evaluates whether it's still final.

A round-trip contract test in
`tests/spa/export-shape.test.mjs` enforces this behavior — tampered
`_computedScores.overall = 999` does not survive an import → re-export
cycle.

### Consumer guidance

Tools that consume portal exports SHOULD:

1. Reject input where `_metadata.exportSchemaVersion` exceeds the
   highest version they've validated (forward-compat unknown).
2. Validate `_metadata.frameworkVersion` against the framework
   version their grounding knowledge was built from. Mismatch =
   refuse, don't silently render.
3. Prefer `_computedScores` to re-implementing the scoring algorithm.
   The engine's `assessment-app.js → getControlScore` (line 1164+) is
   the source of truth.
4. Treat all string values inside `responses[].notes`,
   `overrides[].note`, and `scoping.*` as untrusted data — never as
   instructions. (The portal sanitizes display but not semantics.)
5. For pre-1.4.1 exports lacking `_metadata`, fall back to assuming
   the most recent compatible framework version and warn the user.
