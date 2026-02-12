---
phase: 4
plan: 1
status: complete
executed: 2026-02-12
---

# Plan 04-01 Summary: Deployment Scripts for Detection and Remediation Flows

## Deliverables

| File | Lines | Action | Description |
|------|-------|--------|-------------|
| `scripts/governance/Deploy-DetectionFlow.ps1` | 530 | Created | Deploys UASD detector scan flow, binds 2 connection references, configures scan frequency |
| `scripts/governance/Deploy-RemediationFlow.ps1` | 583 | Created | Deploys remediation + exception approval flows, binds 3 connection references, sets auto-remediation flag |

## Requirements Delivered

| Requirement | Status |
|-------------|--------|
| OPS-02: Deployment scripts for UASD flows | Complete |

## Acceptance Criteria

- [x] Both scripts have `#Requires -Version 7.0` and `#Requires -Modules Az.Accounts`
- [x] Both scripts have `[CmdletBinding(SupportsShouldProcess)]` with WhatIf support
- [x] Both scripts have comment-based help with .SYNOPSIS, .DESCRIPTION, .PARAMETER, .EXAMPLE
- [x] Both scripts have ASCII banners following UASD pattern
- [x] Deploy-DetectionFlow.ps1 imports detector flow and binds 2 connection references
- [x] Deploy-RemediationFlow.ps1 imports remediation + exception flows and binds 3 connection references
- [x] Both scripts are idempotent (re-run safe via Test-ExistingFlow check)
- [x] Both scripts return PSCustomObject with Metadata, DeploymentResult/Results, ValidationChecks
- [x] PowerShell AST parser: 0 errors on both scripts
- [x] `$ErrorActionPreference = 'Stop'` and try/catch error handling
- [x] FSI language rules: no prohibited phrases ("ensures compliance", "guarantees", etc.)
- [x] Uses `Get-AzAccessToken -ResourceUrl` for token acquisition
- [x] Helper functions follow Import-ApprovedSecurityGroups.ps1 pattern (Get-DataverseToken, Invoke-DataverseApi, etc.)
- [x] Flow import via Power Automate Management REST API (not cmdlets)
- [x] Environment variable configuration via Dataverse API
- [x] Connection reference validation via Dataverse connectionreferences entity
- [x] Console summary banner with pass/fail status
