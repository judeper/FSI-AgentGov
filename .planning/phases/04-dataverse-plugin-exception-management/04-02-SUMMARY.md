---
phase: 4
plan: 2
status: Complete
completed: 2026-02-12
---

# Plan 04-02 Summary: Exception Register + Validation Script + Request Template

## Status: Complete

## What Was Built

### 1. MIME Type Exception Register (`scripts/governance/mime-type-exceptions.csv`)

CSV register template for tracking approved MIME type exceptions with 20 columns:
`ExceptionId`, `Requestor`, `RequestorEmail`, `Department`, `RequestDate`, `MimeType`, `Extensions`, `BusinessJustification`, `AlternativesConsidered`, `RiskAssessment`, `MitigatingControls`, `Approver`, `ApproverEmail`, `ApprovalDate`, `ReviewDate`, `ExpirationDate`, `Status`, `Zone`, `EnvironmentId`, `Notes`.

Includes two sample rows:
- **EXC-MIME-001:** `application/zip` exception in Zone 2 for document exchange workflow (review date 90 days from request, expiration 1 year from approval)
- **EXC-MIME-002:** `application/x-zip-compressed` exception in Zone 3 for regulatory filing portal (enhanced monitoring tier, restricted access)

Both samples reference DLP scanning and Sentinel monitoring as mitigating controls.

### 2. Exception Validation Script (`scripts/governance/validate-exceptions.ps1`)

PowerShell 7.0+ script that validates environment MIME configuration against zone templates and the exception register. Features:

- **Parameters:** `DataverseUrl` (mandatory), `AccessToken` (optional), `ExceptionRegisterPath` (default path), `ZoneTemplate` (zone1/zone2/zone3), `OutputFormat` (Table/JSON/Object), `OutputPath`, `IncludeEvidence`
- **Processing:** Imports `FsiMimeControl.psm1`, calls `Get-FsiMimeConfig` to read environment state, loads zone template JSON, imports exception CSV filtered by Active status and environment ID, then classifies each MIME type as Template/Exception/Unauthorized
- **Expired/Expiring detection:** Flags exceptions with past ReviewDate or ExpirationDate, and warns for exceptions within 30 days of either date
- **Output:** PSCustomObject array with `MimeType`, `Source`, `ExceptionId`, `Status`, `ExpirationDate`, `Action` fields
- **Summary:** Counts for Compliant, Exception-Covered, Unauthorized, Expired, Expiring Soon
- **Console output:** `[PASS]`/`[FAIL]`/`[WARN]` pattern consistent with `Invoke-HardeningBaselineCheck.ps1`
- **Evidence:** Optional SHA-256 integrity hash via `-IncludeEvidence`
- **Output handling:** Follows same `OutputFormat`/`OutputPath` pattern as `FsiMimeControl.psm1` and `Invoke-HardeningBaselineCheck.ps1`

### 3. Exception Request Template (`docs/templates/exception-template.md`)

Markdown form template for requesting MIME type exceptions with 8 sections:

1. **Requestor Information** — Name, Email, Department, Date
2. **Exception Details** — MIME Type(s), Extension(s), Zone, Environment ID/Name
3. **Business Justification** — Purpose/workflow, volume/frequency, duration (permanent/temporary with checkboxes)
4. **Alternatives Considered** — Table format for evaluated alternatives and rejection reasons
5. **Risk Assessment** — Threat scenario checkboxes, data sensitivity classification, likelihood/impact rating
6. **Mitigating Controls** — Checkbox-style fields for DLP, Sentinel, scanning, access restrictions
7. **Approval** — Approver details, conditions, approval decision checkboxes
8. **Review Schedule** — Next review date, cadence, responsible reviewer, review criteria checklist

Includes header metadata (Template Version 1.0, Control Reference 1.25) and footer with submission instructions. All language follows FSI-safe guidelines — no overclaims.

## Decisions Made

- **No deviations from plan.** All three files created exactly as specified in acceptance criteria.
- **Environment matching logic:** `validate-exceptions.ps1` matches exceptions by both the raw Dataverse URL and OrganizationId from `Get-FsiMimeConfig`, plus blank EnvironmentId (global exceptions), providing flexible matching.
- **Banner style:** Used the same `╔══╗` banner pattern from `FsiMimeControl.psm1` and `Invoke-HardeningBaselineCheck.ps1` for visual consistency.
- **SupportsShouldProcess:** Added `-WhatIf` support to `validate-exceptions.ps1` consistent with other governance scripts.
- **Review criteria in template:** Added a review criteria checklist in Section 8 to guide periodic reviews, aligning with Control 1.25 zone requirements.

## Commits

1. `feat(governance): add MIME type exception register, validation script, and request template`

## File Manifest

| File | Action | Description |
|------|--------|-------------|
| `scripts/governance/mime-type-exceptions.csv` | Created | Exception register with 20 columns and 2 sample rows |
| `scripts/governance/validate-exceptions.ps1` | Created | PowerShell validation script comparing env config against register |
| `docs/templates/exception-template.md` | Created | Markdown exception request form template |
| `.planning/phases/04-dataverse-plugin-exception-management/04-02-SUMMARY.md` | Created | This summary |
