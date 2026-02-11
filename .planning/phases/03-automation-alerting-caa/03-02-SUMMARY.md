---
phase: 3
plan: 2
status: complete
started: 2026-02-10
completed: 2026-02-10
---

# Plan 03-02 Summary: Teams Adaptive Card Template

## Outcome

**COMPLETE** — All tasks delivered. The Teams adaptive card template (`src/adaptive-card-caa-alert.json`) provides a comprehensive CA policy compliance alert card with severity-colored header, run summary metrics, zone compliance table (3 zones with pass/total counts and threshold badges), violation details with regulatory context, drift detection with dimension/direction indicators, and three action buttons.

## Files Created

| File | Purpose |
|------|---------|
| `src/adaptive-card-caa-alert.json` | Adaptive Card v1.4 template for CA compliance alerts — main deliverable |

## Must-Haves Delivered

| # | Must-Have | Status | Implementation |
|---|----------|--------|----------------|
| 3 | Teams adaptive card with zone-based severity classification | ✅ | Card header shows severity badge via `${SeverityStyle}` / `${SeverityColor}` (CRITICAL→attention, HIGH→warning, WARNING→accent, Passed→good), zone compliance section with 3 zone rows showing `${ZoneXPassed}/${ZoneXTotal}` and threshold labels, violation list with per-item zone attribution |

## Key Design Decisions

1. **`${variableName}` template syntax**: All 32 template variables use Power Automate-compatible string substitution. Scalar values are replaced directly; array items (violations, drift) are built dynamically by the flow and injected into the card body.

2. **Violations/drift as item templates**: The `violationsSection` and `driftSection` containers each contain a single representative item (`violationItem`, `driftItem`) showing the per-item structure. The Power Automate flow (Plan 03-03) iterates the runbook output arrays and replicates these elements for each result.

3. **Conditional visibility via flow logic**: Rather than using Adaptive Card Templating `$when` expressions (which require a different templating engine), the card sections are always present in the template. The flow controls visibility by including/excluding sections based on `ViolationCount > 0` and `DriftCount > 0`.

4. **`_metadata` as integration contract**: The card includes a `_metadata` object documenting severity color/style mappings, all template variable names (scalar, perViolation, perDrift), and flow integration notes. This serves as a contract between the card template and the Power Automate flow.

5. **`msteams.width: Full`**: Uses Teams-specific full-width rendering for better readability of the zone compliance table and violation details.

## Card Structure

| Section | Card Element | Template Variables |
|---------|-------------|-------------------|
| Header | Container with `${SeverityStyle}`, ColumnSet | `OverallStatus`, `CheckedAt`, `OverallSeverityBadge`, `SeverityStyle`, `SeverityColor` |
| Run Summary | ColumnSet with two FactSets | `OverallStatus`, `CheckedAt`, `TotalPolicies`, `ComplianceRate`, `PassedCount`, `FailedCount`, `DriftCount`, `OverallSeverity` |
| Zone Compliance | 3 ColumnSets with threshold badges | `Zone1Passed`, `Zone1Total`, `Zone2Passed`, `Zone2Total`, `Zone3Passed`, `Zone3Total` |
| Violations | Container with item template | `ViolationCount`, `ViolationType`, `ViolationPolicyName`, `ViolationZone`, `ViolationExpected`, `ViolationActual`, `ViolationSeverity`, `ViolationSeverityColor`, `ViolationRegulatoryContext` |
| Drift Detection | Container with item template | `DriftCount`, `DriftType`, `DriftPolicyName`, `DriftDimension`, `DriftDirection`, `DriftZone` |
| Actions | 3 Action.OpenUrl buttons | `DocsBaseUrl` |

## Severity Color Mapping

| Severity | Container Style | TextBlock Color | Threshold |
|----------|----------------|-----------------|-----------|
| CRITICAL | attention | Attention (red) | Zone 3 failures |
| HIGH | warning | Warning (orange) | Zone 2 failures |
| WARNING | accent | Accent (yellow) | Zone 1 failures |
| Passed | good | Good (green) | All zones passing |

## Verification Checklist

- [x] Valid Adaptive Card v1.4 schema (`$schema` URL, `version: "1.4"`, valid JSON)
- [x] All template variables use `${variableName}` syntax (32 unique variables)
- [x] Severity badge color mapping: CRITICAL→attention, HIGH→warning, WARNING→accent, Passed→good
- [x] Zone summary table shows 3 zones with pass/total counts and threshold badges
- [x] Violation section conditionally visible (flow manages `violationsSection` visibility)
- [x] Drift detection section conditionally visible (flow manages `driftSection` visibility)
- [x] CA-specific fields: PolicyName, ViolationType, DriftDimension, DriftDirection (PolicyId used by flow internally, not displayed on card)
- [x] Action URLs: Entra portal (correct deep link), Run Manual Check (Azure Automation), View Documentation (`${DocsBaseUrl}/controls/pillar-1-security/1.11-conditional-access-policies/`)
- [ ] Card renders correctly in Adaptive Card Designer preview — not verified in this environment; structure follows v1.4 spec

## Commits

1. `856c94e` — `feat(caa): add Teams adaptive card template for CA compliance alerts`

## Notes

- The card template is consumed by the Power Automate daily compliance scan flow (Plan 03-03). The flow parses the runbook JSON output (Plan 03-01) and substitutes template variables before posting to Teams.
- `PolicyId` is available in the runbook output but intentionally not displayed on the card — it is an internal GUID not useful to operators reading the alert.
- The `DocsBaseUrl` variable allows the documentation link to work across environments (dev, staging, production GitHub Pages URLs).
- The `iconUrl` on the "View in Entra Portal" action references the official Microsoft Entra ID icon from Microsoft Learn.

## Dependencies for Next Plans

- **Plan 03-03** (Power Automate flow): Consumes this card template, replacing `${variableName}` placeholders with runbook output values and building dynamic violation/drift item arrays.
