# Playwright UI smoke tests — DEFERRED

Playwright is **not** part of the v1.4 test bundle. Browser binaries add roughly
**~250 MB** to CI install time and are not justified for the current SPA scope —
the Vitest + jsdom suite under `tests/spa/` already covers manifest integrity,
zone exclusion, role filtering, solutions-lock contract, and URL composition.

When a maintainer decides to add Playwright later, here is the recommended scope.

## Recommended pinned versions

```json
{
  "devDependencies": {
    "@playwright/test": "1.45.0"
  }
}
```

Pin and bump deliberately — Playwright's browser binaries change between minor
versions and CI cache invalidations are expensive.

## Recommended UI smoke tests (one per epic)

| Epic | Smoke scenario |
|------|----------------|
| **E1 — How-to-verify drawer** | Open Phase 1, click drawer toggle on control 1.1, assert drawer body appears, press `Esc`, assert drawer collapses and focus returns to the toggle. |
| **E2 — Zone auto-exclusion + override banner** | On Scoping, deselect Zone 3 + Zone 2; advance to Phase 1; assert a Zone-3-only control shows the auto-N/A banner. Click "Mark applicable", enter a note, assert override is captured. |
| **E4 — Role filter** | Open the role filter dropdown, pick `Power Platform Admin`, assert only matching control rows are visible (CSS `display` toggle), assert live count badge updates. |
| **E5 — Sector calibration** | On Scoping, change sector to `bank`; reopen drawer for a control with non-TODO `sectorYesBar.bank`; assert sector-specific yes-bar text renders. |
| **E6 — Priority starter set** | On Scoping, choose "Priority starter set"; assert Phase 1 renders only the 5 starter controls; assert Continue button disabled until all 5 are answered. |
| **E9 — Facilitator mode** | Visit `/assessment/?mode=facilitate`; assert the facilitator banner, session timer Start/Pause/Reset, per-row ask blockquote, and time badge are present. |
| **Agenda export** | If agenda export ships with E10, assert downloaded `.md`/`.txt` file content matches the on-screen agenda. |

## Suggested layout

```
tests/playwright/
├── fixtures/
│   └── seed-state.json
├── e1.drawer.spec.ts
├── e2.zone-exclusion.spec.ts
├── e4.role-filter.spec.ts
├── e5.sector.spec.ts
├── e6.starter-set.spec.ts
├── e9.facilitator.spec.ts
└── playwright.config.ts
```

## CI integration when added

- Add a separate workflow (`.github/workflows/spa-ui-tests.yml`) so the heavy
  browser install doesn't slow down the lightweight `spa-tests.yml` job.
- Cache the Playwright browser binaries with the
  `actions/cache` action keyed on the resolved Playwright version.
- Run only on PRs that touch `docs/javascripts/**` or `docs/stylesheets/**`.
