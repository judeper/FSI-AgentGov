# E2E export fixtures

These JSON files are full-assessment exports captured from real SPA runs.
They are used by `tests/e2e/11b-cold-start-full-import.spec.mjs` and any
other spec that needs a known-good import payload.

## Regenerating a fixture

To recapture from a current SPA build (e.g. after a schema change in
`exportJSON()` / `_metadata`):

```pwsh
# 1. Boot the SPA via the test harness
npx playwright test tests/e2e/11-import-roundtrip.spec.mjs --project chromium --headed

# 2. In the live SPA, scope+answer per the persona at
#    tests/e2e/fixtures/personas/<name>.json, click "Export Results" →
#    "Export as Full Assessment", and save the downloaded JSON to
#    tests/e2e/fixtures/exports/<name>-export.json.
```

The schema is stable enough that hand-edits are safe for date/id fields,
but the canonical procedure is to capture a real export so the fixture
tracks any future `exportSchemaVersion` bumps in
`docs/javascripts/assessment-app.js`.

The schema contract that consuming tests rely on:

- `_metadata.exportSchemaVersion`, `_metadata.exportedAt`
- `assessmentId` (string, used as the per-id storage slot key)
- `scoping.{organizationName,institutionType,zones[]}`
- `responses[<controlId>].answer` ∈ { yes, partial, no, na }
- `assessmentName` (string, drives the "Resume <name>" button label)
