---
phase: 3
plan: 2
title: "Exception Manager canvas app + Import script"
status: Complete
executed: 2026-02-12
---

# Plan 03-02 Summary: Exception Manager Canvas App + Import Script

## Status: Complete

**Executed:** 2026-02-12
**Duration:** Single session
**Dependencies met:** 01-01-PLAN.md (Dataverse schema), 01-02-PLAN.md (scanning flow)

## Deliverables

| File | Lines | Action | Description |
|------|-------|--------|-------------|
| `scripts/governance/Import-ApprovedSecurityGroups.ps1` | 525 | CREATE | Approved security group CSV/JSON import with Dataverse upsert |
| `src/uasd-exception-manager-app.json` | 596 | CREATE | Exception Manager canvas app specification (3 screens) |

## Requirements Delivered

| Requirement | Description | Delivered |
|-------------|-------------|-----------|
| REM-03 | Exception Manager canvas app definition with submission, status view, and expiration display | Yes |
| OPS-01 | Import-ApprovedSecurityGroups.ps1 with CSV/JSON import, upsert on fsi_entraid_group_id, idempotent | Yes |

## Acceptance Criteria

### Import Script (`Import-ApprovedSecurityGroups.ps1`)

- [x] `#Requires -Version 7.0` and `#Requires -Modules Az.Accounts`
- [x] `[CmdletBinding(SupportsShouldProcess)]` with WhatIf support
- [x] Comment-based help with .SYNOPSIS, .DESCRIPTION, .PARAMETER, .EXAMPLE (3 examples)
- [x] ASCII banner with solution name ("UASD — Import Approved Security Groups")
- [x] CSV and JSON input format support with auto-detection
- [x] Upsert on `fsi_entraid_group_id` (idempotent — query, then PATCH or POST)
- [x] Zone mapping to `fsi_acv_zone` option set values (Zone1=0, Zone2=1, Zone3=2, All=3)
- [x] Summary report with Created/Updated/Skipped/Errors counts
- [x] PSCustomObject return with Metadata, Summary, Details properties
- [x] PowerShell AST parser validation: 0 errors
- [x] `$ErrorActionPreference = 'Stop'` and try/catch per Dataverse operation
- [x] Helper functions: Get-DataverseToken, Invoke-DataverseApi, ConvertTo-ZoneValue, Import-GroupsFromCsv, Import-GroupsFromJson

### Canvas App Specification (`uasd-exception-manager-app.json`)

- [x] Valid JSON specification document (validated via Python json.load)
- [x] 3 screens defined: ExceptionSubmissionScreen, ExceptionStatusScreen, ExpirationDashboardScreen
- [x] Data source connections to 3 Dataverse tables (fsi_AgentSharingSetting, fsi_SharingException, fsi_ApprovedSecurityGroup)
- [x] Exception submission creates fsi_SharingException with status=Pending, 90-day expiry, auto-generated name
- [x] Status view with color-coded exception state badges (Pending=Amber, Approved=Green, Denied=Red, Expired=Gray)
- [x] Expiration dashboard shows approved exceptions expiring within 14 days with days-remaining color coding
- [x] Tab-based navigation: Submit Exception | My Requests | Expiring Soon
- [x] Lab-grade minimal viable implementation (non-responsive, fixed layout)

## Key Structural Elements

### Import Script

- **5 helper functions:** `Get-DataverseToken`, `Invoke-DataverseApi`, `ConvertTo-ZoneValue`, `Import-GroupsFromCsv`, `Import-GroupsFromJson`
- **Upsert pattern:** Query by `$filter=fsi_entraid_group_id eq '{GroupId}'`, then PATCH (update) or POST (create)
- **Payload fields:** `fsi_entraid_group_id`, `fsi_display_name`, `fsi_acv_zone`, `fsi_is_active`, `fsi_added_by`, `fsi_added_at`
- **WhatIf mode:** Shows preview table of groups that would be processed without writing to Dataverse
- **Console output:** Banner at start, per-record status (Created/Updated/Error), summary banner at end

### Canvas App Specification

- **Schema:** `https://fsi-agentgov/schemas/canvas-app-spec/1.0`
- **Screen 1 (Submit):** Agent dropdown, violation type, data classification, justification (50-char minimum), submit with Patch()
- **Screen 2 (Status):** Gallery filtered by User().Email, status filter dropdown, sorted by requested_at descending
- **Screen 3 (Expiring):** Gallery of approved exceptions within 14-day window, <=7 days = Red, 8-14 days = Amber
- **Option sets referenced:** `fsi_UASD_exceptionstatus`, `fsi_UASD_violationtype`, `fsi_UASD_dataclassification`

## Validation Results

| Check | Result |
|-------|--------|
| PowerShell AST parse | 0 errors |
| JSON syntax validation | Valid |
| No prohibited language ("ensures compliance", "guarantees") | Confirmed |
