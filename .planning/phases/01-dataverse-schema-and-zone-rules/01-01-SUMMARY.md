---
phase: 1
plan: 1
title: "Dataverse Schema & Creation Script"
completed: 2026-02-13
commit: 983f019
---

# Phase 1 Plan 01 Summary: Dataverse Schema & Creation Script

## What Was Built

Created `scripts/create_asard_dataverse_schema.py` — an idempotent Dataverse schema deployment script following the established UASD pattern.

### Deliverables

| Artifact | Description |
|----------|-------------|
| `fsi_ASARD_compliancestatus` option set | Compliant (0), NonCompliant (1), Exception (2), Error (3) |
| `fsi_ASARD_violationtype` option set | Everyone (0), Public (1), UnapprovedGroup (2), ExcessiveIndividual (3), CrossTenant (4) |
| `fsi_AgentSharingCompliance` table | Agent sharing compliance tracking — 11 columns + primary name |
| `fsi_ApprovedSecurityGroupPolicy` table | Approved security groups per zone — 6 columns + primary name |
| Alternate key | `fsi_agentsharingcompliance_agentkey` on (fsi_agent_id, fsi_environment_id) |
| Seed data | 3 template records (one per zone) in fsi_ApprovedSecurityGroupPolicy |

### Pattern Compliance

- Follows UASD script structure exactly: `_label()`, `_string_col()`, `_memo_col()`, `_boolean_col()`, `_datetime_col()`, `_picklist_col()` helpers
- `SOLUTION_OPTIONSETS` dictionary for fsi_ASARD_* option sets
- `_create_table_with_columns()` for idempotent table + column creation
- `create_schema()` orchestrator with `[1/4]` through `[4/4]` step numbering
- CLI with `--dry-run`, `--verbose`, `--interactive`, `--tenant-id`, `--environment-url`, `--client-id`, `--client-secret`
- References but does NOT create shared option sets: `fsi_acv_zone`

### Tech Stack

- Python 3 + `caa_client.CAAClient`
- Dataverse Web API v9.2

## Key Files

| File | Action | Description |
|------|--------|-------------|
| `scripts/create_asard_dataverse_schema.py` | Created | Full schema creation script |

## Dependency Graph

```
01-01-PLAN (this) → 01-02-PLAN (zone rules depend on schema tables)
```

## Self-Check

- [x] Syntax check passes (`python -m py_compile`)
- [x] All option set names follow `fsi_ASARD_*` pattern
- [x] All table names follow `fsi_*` PascalCase pattern
- [x] All column schema names follow `fsi_*` snake_case pattern
- [x] References shared `fsi_acv_zone` via `@odata.bind` (does NOT create)
- [x] Idempotent: checks existence before creating
- [x] Alternate key defined on (fsi_agent_id, fsi_environment_id)
- [x] Seed data marked as templates with admin instructions
