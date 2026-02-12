---
phase: 4
plan: 1
status: Complete
completed: 2026-02-12
---

# Summary 04-01: ValidateMimeTypePlugin + Deployment Scripts

## Status: Complete

## What Was Built

### 1. MimeConfig.json (`src/MimeConfig.json`)

Zone 3 server-side MIME validation configuration file containing:

- **10 allowed MIME types** with magic byte signatures: PDF, PNG, JPEG, GIF, TIFF, plain text, CSV, XLSX, DOCX, PPTX
- **7 blocked executable signatures**: PE/MS-DOS (MZ), ELF, Mach-O (4 variants), Java class
- Enforcement mode set to `Block` (with `LogOnly` alternative)
- 10 MB max file size guard (`maxFileSizeBytes: 10485760`)
- Correlation ID header for trace integration
- Aligned with `scripts/governance/mime-templates/zone3.json` allowedMimeTypes list

### 2. ValidateMimeTypePlugin.cs (`src/ValidateMimeTypePlugin.cs`)

Dataverse pre-validation plugin implementing `IPlugin` (Microsoft.Xrm.Sdk) with 5-step validation pipeline:

1. **File size guard** — rejects files exceeding configured max
2. **Blocked signature scan** — checks leading bytes against PE/ELF/Mach-O/Java signatures
3. **Allowlist check** — verifies declared MIME type is in allowed set
4. **Magic-byte consistency** — confirms file header matches declared type; text types validated for absence of binary content
5. **OpenXML deep inspection** — for DOCX/XLSX/PPTX, verifies PK zip header and `[Content_Types].xml` presence

Key design elements:
- Configuration loaded from secure or unsecure plugin step configuration (MimeConfig.json content)
- Dual enforcement modes: `Block` (throws `InvalidPluginExecutionException`) and `LogOnly` (trace warning)
- Correlation ID from plugin execution context for tracing
- `JsonElement` handling for `magicBytes` field (supports both single string and array of strings)
- Comprehensive XML documentation comments throughout

### 3. register-plugin.ps1 (`scripts/governance/register-plugin.ps1`)

PowerShell 7.0+ deployment script for Plugin Registration Tool automation:

- Registers plugin assembly via Dataverse Web API (`POST /api/data/v9.2/pluginassemblies`)
- Registers plugin type for `ValidateMimeTypePlugin`
- Registers plugin step on `Create` of `annotation` entity at pre-validation stage (stage 10)
- Attaches MimeConfig.json as step configuration
- Idempotent — checks for existing registrations before creating
- `-WhatIf` support via `SupportsShouldProcess`
- Token fallback via `Get-AzAccessToken`

### 4. test-plugin.ps1 (`scripts/governance/test-plugin.ps1`)

PowerShell 7.0+ integration test script with 5 test cases:

| # | Test | Expected | Description |
|---|------|----------|-------------|
| 1 | PDF-Valid-Signature | PASS | Valid PDF with correct magic bytes |
| 2 | PNG-Valid-Signature | PASS | Valid PNG with correct magic bytes |
| 3 | EXE-Disguised-As-Text | FAIL (blocked) | PE header in .txt file |
| 4 | Text-Clean-Content | PASS | Clean ASCII text file |
| 5 | Oversized-File-Guard | FAIL (blocked) | 11 MB file exceeds 10 MB limit |

- Reports `[PASS]`/`[FAIL]` pattern consistent with existing governance scripts
- Cleanup: deletes test annotations after verification (`-SkipCleanup` to retain)
- Outputs summary table with pass/fail counts

## Decisions Made

1. **Config in step configuration, not file system** — Plugin reads MimeConfig.json from the Dataverse plugin step's secure/unsecure configuration string rather than from a file path, since Dataverse sandbox plugins cannot access the file system.

2. **System.Text.Json over Newtonsoft** — Used `System.Text.Json` for config deserialization since it's included in .NET Core and avoids an additional assembly dependency in the sandbox.

3. **JsonElement for magicBytes** — Used `JsonElement?` type for the `magicBytes` property to handle both single-string (`"25 50 44 46"`) and array-of-strings (`["49 49 2A 00", "4D 4D 00 2A"]`) JSON representations without requiring separate config models.

4. **PE and MS-DOS share one entry** — The plan listed PE executable and MS-DOS as separate blocked signatures, but both use the `4D 5A` magic bytes. Combined into a single entry named "PE/MS-DOS Executable" to avoid duplicate checks.

5. **Banner pattern** — Followed the existing `Deploy-DetectionFlow.ps1` and `FsiMimeControl.psm1` banner pattern with cyan box borders for visual consistency.

6. **Oversized test file** — Used 11 MB (11 × 1024 × 1024 zero bytes) as the oversized test payload to clearly exceed the 10 MB limit.

## Commits

- `feat(phase-04): add MimeConfig.json Zone 3 server-side MIME validation config`
- `feat(phase-04): add ValidateMimeTypePlugin.cs Dataverse pre-validation plugin`
- `feat(phase-04): add register-plugin.ps1 and test-plugin.ps1 deployment scripts`

## File Manifest

| File | Action | Description |
|------|--------|-------------|
| `src/MimeConfig.json` | Created | Zone 3 MIME validation configuration (10 allowed, 7 blocked) |
| `src/ValidateMimeTypePlugin.cs` | Created | Dataverse IPlugin with 5-step validation pipeline |
| `scripts/governance/register-plugin.ps1` | Created | Plugin Registration Tool automation script |
| `scripts/governance/test-plugin.ps1` | Created | Integration test script with 5 test cases |
| `.planning/phases/04-dataverse-plugin-exception-management/04-01-SUMMARY.md` | Created | This summary |

## Validation

- [x] MimeConfig.json parses as valid JSON (10 allowed types, 7 blocked signatures)
- [x] All 4 files pass FSI language rule check (no forbidden phrases)
- [x] PowerShell scripts follow existing patterns (banner, comment-based help, `#Requires`)
- [x] C# plugin follows IPlugin contract (constructor with config strings, `Execute` method)
- [x] Allowed MIME types align with `scripts/governance/mime-templates/zone3.json` allowedMimeTypes
