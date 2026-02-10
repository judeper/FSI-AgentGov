---
phase: 1
plan: 2
title: "Get-EnvironmentAccessSettings.ps1 and Compare-ZoneCompliance.ps1"
status: complete
executed: 2026-02-09
duration: ~5min
---

# Summary: Plan 01-02

## What Was Built

Core query and comparison scripts for environment access validation:

| Artifact | Purpose |
|----------|---------|
| `scripts/Get-EnvironmentAccessSettings.ps1` | Query Power Platform environments for agent settings |
| `scripts/Compare-ZoneCompliance.ps1` | Compare settings against zone requirements |

## Features Implemented

**Get-EnvironmentAccessSettings.ps1:**
- Queries all environments via `Get-AdminPowerAppEnvironment`
- Queries environment groups via `Get-AdminPowerAppEnvironmentGroup`
- Extracts `bot-limitSharingMode`, `bot-authoringSharingDisabled`, `bot-publishedBotLimitSharingMode`
- Filters: Include/Exclude environments, Sandbox, Trial, Default, GracePeriod
- Zone classification via ELM or naming convention
- Returns structured PSCustomObject array

**Compare-ZoneCompliance.ps1:**
- Pipeline input from Get-EnvironmentAccessSettings
- Loads zone baseline from JSON
- Compares each setting against zone expectations
- Severity classification (Critical/High/Warning/Info)
- Regulatory context per violation
- Handles Unknown zones

## Key Decisions

| Decision | Rationale |
|----------|-----------|
| Pipeline-compatible design | Enables `Get- | Compare-` pattern |
| Gracefully handle missing settings | Some environments may not have all bot-* settings |
| Severity lookup by violation key | `{setting}_{actualValue}` pattern from baseline |

## Acceptance Criteria

- [x] Query all environments with agent access settings
- [x] Retrieve all three bot-* settings
- [x] Compare settings against zone requirements
- [x] Classify violations by severity
- [x] Support environment group query
- [x] Exclude sandbox/trial with grace period

## Files Created

```
agent-access-monitor/
└── scripts/
    ├── Get-EnvironmentAccessSettings.ps1
    └── Compare-ZoneCompliance.ps1
```

---
*Executed: 2026-02-09*
