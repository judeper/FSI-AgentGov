# Summary: Plan 02-01 — Detector Flow JSON + Adaptive Card Template

**Status:** Complete
**Executed:** 2026-02-12
**Duration:** ~15 minutes

## Deliverables

| File | Lines | Action | Commit |
|------|-------|--------|--------|
| `src/uasd-detector-scan-agents.json` | 1,950 | CREATE | `4e81330` |
| `src/adaptive-card-uasd-alert.json` | 280 | CREATE | `4e81330` |

## Requirements Delivered

| Requirement | Description | Status |
|-------------|-------------|--------|
| DET-01 | Detector flow with 5 violation rules | ✅ Complete |
| DET-03 | Adaptive card template with severity styling | ✅ Complete |

## Acceptance Criteria

### Flow JSON (`uasd-detector-scan-agents.json`)

- [x] Valid JSON file parseable by `ConvertFrom-Json`
- [x] Connection references: `fsi_cr_dataverse_sharingdetector` and `fsi_cr_teams_sharingdetector`
- [x] Recurrence trigger set to daily at 0600 UTC
- [x] 8 variable initializations with correct types and sequential runAfter chain
- [x] Scope_Try/Scope_Catch error handling pattern
- [x] BAP API HTTP actions with MSI authentication and `api.bap.microsoft.com` audience
- [x] All 5 violation rules implemented with correct violation type values and severity mappings
- [x] Exception check before each violation creation
- [x] Duplicate violation prevention for existing Open violations
- [x] Adaptive card composition and Teams posting
- [x] All Dataverse entity set names match schema script

### Adaptive Card (`adaptive-card-uasd-alert.json`)

- [x] Valid Adaptive Card v1.4 JSON
- [x] Header section with severity-based container style
- [x] Scan summary section with agent/violation/environment counts
- [x] Violations section with repeating item template
- [x] Action buttons for PPAC portal, audit script, and documentation
- [x] `_metadata` section documenting template variables and severity mappings
- [x] `msteams.width: "Full"` for Teams rendering
- [x] Pattern consistent with `src/adaptive-card-caa-alert.json`

## Key Structural Elements

### Flow JSON

- **2 connection references:** Dataverse (shared_commondataserviceforapps) + Teams (shared_teams)
- **Trigger:** Daily recurrence at 0600 UTC
- **8 variables:** DataverseUrl, HomeTenantId, TeamsGroupId, TeamsChannelId, ScanRunId, ViolationCards, TotalAgents, ViolationCount
- **5 Dataverse entities:** fsi_agentsharingsettings, fsi_sharingviolations, fsi_sharingexceptions, fsi_approvedsecuritygroups, fsi_sharingpolicies
- **5 violation rules:** ORG_WIDE_SHARING (0/Critical), PUBLIC_INTERNET_LINK (1/Critical), UNAPPROVED_GROUP (2/High), EXCESSIVE_INDIVIDUAL (3/Medium), CROSS_TENANT_ACCESS (4/High)
- **Error handling:** Scope_Try/Scope_Catch with Teams error notification

### Adaptive Card

- **Sections:** headerSection, scanSummarySection, violationsSection
- **Actions:** View in PPAC, Run Audit Script, View Documentation
- **Severity mapping:** Critical=Attention, High=Warning, Medium=Accent, Low=Good

## Decisions Made

- Followed CAA flow JSON pattern exactly (1332 lines → 1950 lines due to 5 rules + nested loops)
- Used same adaptive card structure as CAA alert (492 lines → 280 lines, simpler violation model)
- No email connector — UASD uses Teams-only alerting per solution spec

## Discovered Work

None.
