---
phase: 01
plan: 03
subsystem: telemetry-infrastructure
tags: [azure, python, teardown, verification, sec-17a-4, worm]

depends:
  requires: ["01-01"]
  provides: ["teardown-script", "telemetry-verification", "worm-verification"]
  affects: ["01-04", "02-*"]

tech-stack:
  added: ["azure-monitor-query>=1.3.0"]
  patterns: ["lab-cycling-workflow", "read-only-verification", "worm-policy-check"]

files:
  created:
    - agent-observability-foundation/scripts/teardown.py
    - agent-observability-foundation/scripts/verify_telemetry.py
    - agent-observability-foundation/scripts/verify_worm.py
  modified:
    - agent-observability-foundation/scripts/requirements.txt

decisions:
  - id: TEARDOWN-SAFETY
    choice: "Confirmation prompt before deletion"
    rationale: "Teardown is destructive; user must explicitly confirm unless --force"
  - id: WORM-READONLY
    choice: "verify_worm.py never creates/modifies policies"
    rationale: "WORM lock is irreversible; verification-only prevents accidents"
  - id: TELEMETRY-GRACEFUL
    choice: "Return warnings (not failures) for missing data"
    rationale: "New deployments won't have data yet; infrastructure check passes if configured correctly"

metrics:
  duration: "5 minutes"
  completed: "2026-02-05"
---

# Phase 01 Plan 03: Teardown and Verification Scripts Summary

**One-liner:** Lab cycling teardown + read-only verification scripts for telemetry flow and WORM compliance

## What Was Built

### teardown.py — Resource Cleanup Script

Safe deletion script for lab cycling workflow. Enables the deploy-test-destroy-repeat pattern critical for development and testing.

**Key features:**
- Deletes resources in **reverse dependency order** (diagnostic settings -> RBAC -> App Insights -> Log Analytics -> Storage)
- **Safety confirmation prompt** requires user to type "yes" before deletion (unless `--force`)
- **WORM-aware error handling**: If storage has immutable policy, provides guidance instead of failing silently
- **Never deletes resource groups** (too dangerous for shared environments)
- Supports `--dry-run` and `--config` flags matching provision.py patterns
- Tracks deletion results: deleted / already absent / failed

### verify_telemetry.py — Telemetry Flow Verification

Post-deployment verification script to confirm Copilot Studio telemetry is flowing to Application Insights.

**Verification checks:**
1. Application Insights exists and is workspace-based
2. Retention >= 730 days (SEC 17a-4(b)(4) compliance)
3. customEvents table has data in lookback window
4. CopilotInteraction events detected (Copilot Studio connected)

**KQL query executed:**
```kql
customEvents
| where timestamp > ago({hours}h)
| summarize EventCount=count(), DistinctSessions=dcount(session_Id) by name
| order by EventCount desc
```

**Exit codes:**
- 0: All checks passed
- 1: Critical failure (infrastructure misconfigured)
- 2: Infrastructure OK but no data yet (warnings only)

### verify_worm.py — WORM Policy Verification (READ-ONLY)

Read-only verification of WORM (Write Once Read Many) immutability policy. Per LOCKED DECISION, this script **never creates, modifies, or locks** policies.

**Verification checks:**
1. Storage account exists and is StorageV2 (not HNS-enabled)
2. Blob container exists
3. Immutability policy is present
4. Policy state is "Locked" (SEC 17a-4(f) requirement)
5. Retention >= 2555 days (~7 years for SEC 17a-4(a))

**Compliance status returns:**
- COMPLIANT: Locked policy with adequate retention
- PARTIALLY_COMPLIANT: Policy exists but unlocked or insufficient retention
- NOT_CONFIGURED: No policy found (expected for new deployments)

## Requirements Satisfaction

| Requirement | Status | Evidence |
|-------------|--------|----------|
| TELE-01 (verification) | Satisfied | verify_telemetry.py checks App Insights exists and is workspace-based |
| TELE-02 (retention) | Satisfied | verify_telemetry.py checks retention >= 730 days |
| TELE-03 (WORM verification) | Satisfied | verify_worm.py read-only policy check with compliance reporting |
| Lab cycling | Satisfied | teardown.py enables deploy-test-destroy workflow |

## Commits

| Hash | Message |
|------|---------|
| 754a4cb | feat(01-03): add teardown.py for lab resource cleanup |
| d13ab33 | feat(01-03): add telemetry and WORM verification scripts |

## Deviations from Plan

None - plan executed exactly as written.

## Key Code Artifacts

**teardown.py — Reverse Deletion Order:**
```python
# Delete in reverse dependency order
# 1. Delete diagnostic settings first (depends on App Insights)
# 2. Delete RBAC assignments
# 3. Delete Application Insights
# 4. Delete Log Analytics workspace
# 5. Delete Storage account (may fail if WORM-locked)
```

**verify_telemetry.py — Graceful KQL Dependency:**
```python
try:
    from azure.monitor.query import LogsQueryClient, LogsQueryStatus
    LOGS_QUERY_AVAILABLE = True
except ImportError:
    LOGS_QUERY_AVAILABLE = False
```

**verify_worm.py — Read-Only Guard:**
```python
# READ-ONLY: Get immutability policy
policy = storage_client.blob_containers.get_immutability_policy(...)
# Note: No set_immutability_policy or lock_immutability_policy calls anywhere
```

## Lab Cycling Workflow Complete

With this plan complete, users have the full lifecycle:

```bash
# Deploy infrastructure
python provision.py --config config/config.yml

# Verify telemetry is flowing
python verify_telemetry.py --config config/config.yml

# Verify WORM policy (after manual configuration)
python verify_worm.py --config config/config.yml

# Tear down for next cycle
python teardown.py --config config/config.yml
```

## Next Phase Readiness

**Prerequisites for 01-04 (Governance Mapping):**
- All scripts functional and tested
- Requirements.txt updated with azure-monitor-query
- Documentation structure ready for governance-mapping.md

**Blockers:** None

**Open questions:** None
