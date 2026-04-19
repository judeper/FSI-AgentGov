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
