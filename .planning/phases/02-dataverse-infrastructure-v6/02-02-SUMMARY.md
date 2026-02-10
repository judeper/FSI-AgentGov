---
phase: 2
plan: 2
status: complete
duration: 8min
---

# Summary: Plan 02-02 — Environment Variables, Connection References, and deploy.py Orchestrator

## Status: COMPLETE

## What Was Done
- Created `create_environment_variables.py` with 6 environment variables using `fsi_AAM_*` prefix (GracePeriodHours, ScanFrequencyHours, IncludeSandbox, BaselineMaxAgeDays, TeamsGroupId, TeamsChannelId)
- Created `create_connection_references.py` with 3 connection references following `fsi_cr_{connector}_accessmonitor` naming (Dataverse, Office 365, Teams)
- Created `deploy.py` orchestrator with full deployment pipeline (schema → env vars → connection refs), selective modes (--tables-only, --vars-only, --refs-only), dry-run support, and AAM-specific post-deployment guidance
- All three scripts import from `aam_client` (AAMClient), consistent with Wave 1 dependency
- All operations are idempotent with existence checks before creation
- Followed exact ACV patterns from `audit-configuration-validator/scripts/` adapted for AAM

## Files Created/Modified
| File | Action | Repository |
|------|--------|------------|
| `agent-access-monitor/scripts/create_environment_variables.py` | CREATE | FSI-AgentGov-Solutions |
| `agent-access-monitor/scripts/create_connection_references.py` | CREATE | FSI-AgentGov-Solutions |
| `agent-access-monitor/scripts/deploy.py` | CREATE | FSI-AgentGov-Solutions |

## Key Design Elements

### Environment Variables (6)
| Schema Name | Type | Default |
|------------|------|---------|
| `fsi_AAM_GracePeriodHours` | Decimal (100000001) | 48 |
| `fsi_AAM_ScanFrequencyHours` | Decimal (100000001) | 24 |
| `fsi_AAM_IncludeSandbox` | String (100000000) | false |
| `fsi_AAM_BaselineMaxAgeDays` | Decimal (100000001) | 30 |
| `fsi_AAM_TeamsGroupId` | String (100000000) | (empty) |
| `fsi_AAM_TeamsChannelId` | String (100000000) | (empty) |

### Connection References (3)
| Logical Name | Connector |
|-------------|-----------|
| `fsi_cr_dataverse_accessmonitor` | `shared_commondataserviceforapps` |
| `fsi_cr_office365_accessmonitor` | `shared_office365` |
| `fsi_cr_teams_accessmonitor` | `shared_teams` |

### deploy.py CLI Flags
- `--tenant-id`, `--client-id`, `--client-secret`, `--environment-url` (with AAM_* env var fallbacks)
- `--interactive` — browser auth
- `--dry-run` — preview mode
- `--tables-only`, `--vars-only`, `--refs-only` — selective deployment (mutually exclusive)
- `--verbose` — additional output

## Decisions Made
- Followed ACV pattern exactly: same function signatures, same query patterns, same CLI arg structure
- Used `ENV_VAR_DEFINITIONS` (list of dicts) matching ACV's `ENV_VARIABLES` structure with keys: schemaname, displayname, description, type, defaultvalue
- Connection references include post-create binding instructions printed to stdout
- deploy.py post-deployment output is AAM-specific (references AccessValidationHistory security, fsi_AAM_* variables, fsi_cr_*_accessmonitor references)
- Type codes: Decimal=100000001, String=100000000 (matching Dataverse EnvironmentVariableDefinition type codes)

## Commits
- (not yet committed — files created, ready for review)
