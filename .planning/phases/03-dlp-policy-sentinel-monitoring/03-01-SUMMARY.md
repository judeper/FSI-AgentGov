---
phase: 3
plan: 1
status: complete
started: 2026-02-12
completed: 2026-02-12
---

# Summary 03-01: DLP Policy Template + Sentinel KQL Queries

## Status: Complete

All three artifacts created and validated successfully.

## Files Created

| File | Description |
|------|-------------|
| `src/dlp-policy-template.json` | Purview DLP policy template with two rules blocking 22 dangerous file extensions |
| `src/query-mime-blocks.kql` | Sentinel KQL query — 30-day blocked upload summary with daily trend and top-10 variants |
| `src/query-exception-usage.kql` | Sentinel KQL query — 90-day exception register usage analysis with anomaly detection |

## Task Completion

### Task 1: DLP Policy Template ✓

- Valid JSON, parseable without errors
- `displayName`: "FSI Agent Governance - MIME Type Upload Restrictions"
- `mode`: "TestWithNotifications" (safe default)
- **Rule 1** — Block Executable File Uploads: 11 extensions (exe, bat, cmd, ps1, vbs, js, jar, dll, msi, scr, hta), severity High
- **Rule 2** — Block Script and Archive File Uploads: 11 extensions (com, cpl, inf, lnk, pif, reg, sct, wsf, wsh, cab, gadget), severity Medium
- Incident reports configured for both rules with admin notifications
- `_deploymentNotes` field with deployment guidance
- Environment filter with placeholder GUIDs and comments
- Metadata includes framework version, control reference, applicable zones

### Task 2: query-mime-blocks.kql ✓

- Source table: `PowerPlatformDlpActivity_CL` with `PowerPlatformAdminActivity` alternative noted
- Time filter: 30 days
- Aggregation: BlockCount, FirstBlocked, LastBlocked by FileExtension, UserPrincipalName, EnvironmentName
- Commented-out daily trend variant with `bin(TimeGenerated, 1d)` and `render timechart`
- Commented-out top-10 blocked extensions variant

### Task 3: query-exception-usage.kql ✓

- Source table: `PowerPlatformDlpActivity_CL`
- Time filter: 90 days (parameterized via `LookbackDays`)
- Exception list: Parameterized `ExceptionMimeTypes` dynamic array with placeholder values
- Aggregation: UploadCount, DistinctUsers, FirstUpload, LastUpload by MimeType, EnvironmentName
- Anomaly detection: Weekly baseline calculation with DeviationRatio comparing current week vs 90-day average
- Alert threshold: Commented-out `| where DeviationRatio > 3.0` filter with minimum count threshold

## Decisions Made

1. **Parameterized time ranges in exception query** — Used `let LookbackDays = 90d` variable instead of inline `ago(90d)` for easier customization. The plan specified inline `ago(90d)` but parameterization is more practical for Sentinel analytics rules.

2. **DLP operation type filters** — Used multiple operation type values (`Blocked`, `Denied`, `BlockedUpload`) with fallback to `ActionTaken_s == "Block"` since Power Platform DLP audit schema varies by tenant configuration.

3. **Exception query placeholder MIME types** — Used common archive types (`x-zip-compressed`, `x-tar`, `x-7z-compressed`, `octet-stream`) as example exception values since the plan did not specify particular types.

4. **Minimum count threshold on alert variant** — Added `CurrentWeekCount > 5` alongside the 3x deviation filter to reduce false positives on low-volume exception types.

## Verification Results

- JSON validation: Passed (valid JSON, 2 rules, correct extension counts)
- FSI language check: Passed (no prohibited phrases in any file)
- Table references: Correct (`PowerPlatformDlpActivity_CL`)
- Time ranges: Correct (30d for blocks, 90d for exceptions)
- KQL commented-out variants: Present in both files

## Issues

None.
