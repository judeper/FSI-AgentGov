# Phase 3 Verification: Zone Access Validation

## Verification Scope

**Phase goal:** Automate M365 Admin Center agent access settings verification per zone policy and admin exclusion group validation

**Success criteria from ROADMAP:**
1. `Test-ZoneAgentAccess.ps1` reads agent access control configuration, compares to zone policy
2. Validates `CopilotForM365AdminExclude` Entra group exists and is populated; validates staged deployment group configuration per zone
3. Drift detection with structured comparison output suitable for daily scheduling; results compatible with existing alerting patterns (adaptive cards)
4. Follows established conventions: `#Requires -Version 7.0`, `ErrorAction Stop`, `-OutputFormat`/`-OutputPath` parameters

## Verification Results

### Criterion 1: Agent Access Configuration Reading ✅

**Evidence:** `Test-ZoneAgentAccess.ps1` Check 1 (ZAV-01) reads agent access control configuration via Graph beta API (`/admin/microsoft365/copilot/settings`), extracts agent access policy setting, normalizes values (AllAgents, OrgAndMicrosoftVerified, OrgOnly), and compares to zone policy:
- Zone 1: All agents allowed (any setting acceptable)
- Zone 2: OrgAndMicrosoftVerified or OrgOnly required
- Zone 3: OrgOnly required

Check 4 (ZAV-04) validates web search control setting per zone (enabled Zone 1, warning Zone 2, fail Zone 3).

**Status:** PASSED

### Criterion 2: Admin Exclusion Group + Deployment Group Validation ✅

**Evidence:** Check 2 (ZAV-02) validates:
- Group existence via Graph API (`/v1.0/groups?$filter=displayName eq 'CopilotForM365AdminExclude'`)
- Group type is Security (securityEnabled=True, mailEnabled=False)
- Member count via `/$count` with ConsistencyLevel=eventual
- Zone-appropriate enforcement (Zone 1: optional, Zone 2: compliance roles, Zone 3: traders/restricted)

Check 3 (ZAV-03) validates deployment group configuration:
- Zone 1: Optional (Pass)
- Zone 2: Recommended (Warning if absent)
- Zone 3: Mandatory (Fail if absent)
- Semi-automated with graceful API degradation

**Status:** PASSED

### Criterion 3: Drift Detection + Alerting Compatibility ✅

**Evidence:**
- `Import-AccessBaseline` and `Compare-AccessBaseline` functions detect 4 drift types: PolicyChanged, StatusChanged, GroupMembershipChanged, NewCheck
- Composite key: `CheckId|Context|Zone`
- Auto-saves baseline after each scan for daily scheduling
- `src/adaptive-card-zone-access-alert.json` provides Teams adaptive card template compatible with Power Automate webhook flows
- Template follows UASD pattern with scalar, per-finding, and per-drift template variables

**Status:** PASSED

### Criterion 4: Convention Compliance ✅

**Evidence:**
- `#Requires -Version 7.0` present
- `$ErrorActionPreference = 'Stop'` present
- `[CmdletBinding(SupportsShouldProcess)]` with WhatIf support
- Standard parameters: `-OutputFormat` (Table/JSON/Object), `-OutputPath`, `-ZoneMapping`, `-IncludeEvidence`, `-BaselinePath`
- Cyan box-drawing banner
- SHA-256 evidence hashing (per-check + overall IntegrityHash)
- Results object with Metadata, Summary, Checks, Drifts, Gaps properties
- Console summary with box-drawing matching established pattern
- Script parses without errors in PowerShell 7.0+

**Status:** PASSED

## Build Validation

| Check | Result |
|-------|--------|
| `mkdocs build --strict` | PASSED |
| `verify_controls.py` | 62/62 controls, anchor validation passed |
| PowerShell parse check | No errors |
| JSON validation (adaptive card) | Valid |

## Overall Verdict: PASSED ✅

All 4 success criteria met. Phase 3 delivers:
- `scripts/governance/Test-ZoneAgentAccess.ps1` (1145 lines) — 4 check groups with zone-based validation
- `src/adaptive-card-zone-access-alert.json` — Teams notification template
- `scripts/governance/README.md` — Updated with new script entry

Requirements ZAV-01, ZAV-02, ZAV-03 all delivered.
