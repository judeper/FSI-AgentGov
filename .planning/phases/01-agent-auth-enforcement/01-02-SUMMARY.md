# Summary: Plan 01-02 — Drift Detection + Evidence Export + JSON Output

## Status: Complete

## What Was Built

Extended `Test-AgentAuthConfiguration.ps1` with drift detection (comparing current scan against a previous baseline), SHA-256 per-check evidence hashing, Dataverse-compatible JSON output, and baseline auto-save.

## Tasks Completed

| Task | Description | Status |
|------|-------------|--------|
| 1. Baseline Loading & Comparison | Import-AuthBaseline + Compare-AgentAuthBaseline with 4 drift types | Done |
| 2. SHA-256 Evidence Hashing | EvidenceJson parameter on New-AuthCheckResult, per-check hashing | Done |
| 3. Dataverse JSON Structure | EvidenceHash in checks, Drifts array, DriftCount in Metadata | Done |
| 4. Baseline Auto-Save | Save results to BaselinePath with ShouldProcess/WhatIf support | Done |
| 5. Console Drift Summary | Drift section in console output with type breakdown | Done |

## Key Decisions

- Composite key for drift comparison: `"$EnvironmentId|$AgentId|$SSPMId"` — handles agents across environments
- Four drift types: NewAgent, RemovedAgent, SettingChanged, StatusChanged
- Evidence hashing is opportunistic — only when evidence JSON is available
- Drifts array always present (empty `[]` when no baseline)
- Version bumped from 1.0.0 → 1.1.0 to reflect drift detection capability

## Files Modified

| File | Lines | Change |
|------|-------|--------|
| `scripts/governance/Test-AgentAuthConfiguration.ps1` | 762 → 1020 (+258) | Added drift functions, evidence hashing, baseline auto-save, drift console summary |

## Files Created

None

## Commits

- `fcb9016` — `feat(governance): add drift detection, SHA-256 evidence hashing, and Dataverse JSON output`

## Must-Have Verification

| Must-Have | Status | Evidence |
|-----------|--------|----------|
| MH-3: Drift detection compares against previous baseline with SHA-256 | Met | Import-AuthBaseline + Compare-AgentAuthBaseline + per-check EvidenceHash |
| MH-4: JSON output structured for Dataverse ingestion | Met | PascalCase properties, SSPMId/EvidenceHash/DriftType in output, ISO 8601 timestamps |

## Discovered Work

None — all tasks completed as planned.

---
*Completed: 2026-02-12*
