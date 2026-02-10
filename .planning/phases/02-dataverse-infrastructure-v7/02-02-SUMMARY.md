---
phase: 2
plan: 2
status: complete
started: 2026-02-10
completed: 2026-02-10
---

# Summary: Plan 02-02 — Environment Variables, Connection References, and deploy.py Orchestrator

## Result

Created three scripts completing the Dataverse infrastructure deployment pipeline. `create_environment_variables.py` deploys 7 `fsi_CMM_*` configuration variables (scan frequency, grace period, sandbox/draft toggles, baseline age threshold, Teams alert channel/group IDs). `create_connection_references.py` deploys 3 connection references for Dataverse, Office 365, and Teams connectors. `deploy.py` orchestrates the full 4-step pipeline (test connection → schema → env vars → connection refs) with selective deployment flags (`--tables-only`, `--vars-only`, `--refs-only`) and post-deployment guidance covering security role configuration, connection binding, and verification. All operations are idempotent with dry-run support. Imports across all four modules verified successfully.

## Files Created/Modified

| Action | File | Lines |
|--------|------|-------|
| CREATE | `content-moderation-monitor/scripts/create_environment_variables.py` | ~253 |
| CREATE | `content-moderation-monitor/scripts/create_connection_references.py` | ~188 |
| CREATE | `content-moderation-monitor/scripts/deploy.py` | ~248 |

## Commits

| Hash | Message |
|------|---------|
| `162e0da` | feat(cmm): add env vars, connection refs, and deploy orchestrator |

## Decisions Made

- Environment variable types use Dataverse numeric codes (100000000=String, 100000001=Decimal) matching the Dataverse Web API schema rather than string type names.
- Boolean-like configuration (IncludeSandbox, IncludeDrafts) stored as String type with "true"/"false" values rather than Dataverse Boolean type, consistent with Power Platform environment variable conventions.
- Teams alert variables (GroupId, ChannelId) default to empty string — no default value record is created for these, requiring explicit admin configuration.
- Post-deployment guidance only prints on full (non-selective) deployment to avoid noise during partial runs.
- `deploy.py` validates that either `--interactive` or both `--client-id` and `--client-secret` are provided before attempting connection, providing a clear error message.

## Discovered Work

- No additional work discovered. All three tasks completed as planned.
