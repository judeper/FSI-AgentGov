---
phase: 2
status: passed
verified_at: 2026-02-12
---

# Phase 2 Verification: Publishing Restriction Governance

## Status: PASSED

## Goal Assessment

**Phase Goal:** Create the `restrict-agent-publishing.ps1` governance script validating 6 publishing restriction criteria with SHA-256 evidence export and hardening baseline integration.

**Result:** Goal fully achieved. All 3 requirements (PUB-01, PUB-02, PUB-03) delivered.

## Success Criteria Evaluation

| # | Criterion | Status | Evidence |
|---|-----------|--------|----------|
| 1 | `restrict-agent-publishing.ps1` validates 6 criteria | Pass | Script validates env maker role, security groups, share-with-everyone, DLP, managed env limits, approval workflow |
| 2 | SHA-256 evidence export and structured JSON output | Pass | `Get-EvidenceHash` per-check, overall `IntegrityHash`, Dataverse-compatible JSON |
| 3 | Hardening baseline items 1-6 reclassified | Pass | Check Group 0 added, version bumped to 1.2.0, cross-reference logic implemented |
| 4 | Follows established conventions | Pass | `#Requires -Version 7.0`, `ErrorAction Stop`, standard parameters, cyan banner |

## Validation Results

| Check | Result |
|-------|--------|
| `restrict-agent-publishing.ps1` parse | 0 errors |
| `Invoke-HardeningBaselineCheck.ps1` parse | 0 errors |
| `mkdocs build --strict` | Pass |
| `verify_controls.py` | 62/62 controls |

## Requirements Delivered

| Requirement | Description | Status |
|-------------|-------------|--------|
| PUB-01 | restrict-agent-publishing.ps1 with 6 criteria | Complete |
| PUB-02 | SHA-256 evidence export and JSON output | Complete |
| PUB-03 | Hardening baseline items 1-6 integration | Complete |

## Files Created/Modified

| File | Action | Purpose |
|------|--------|---------|
| `scripts/governance/restrict-agent-publishing.ps1` | Created | 6-criteria publishing governance script |
| `scripts/governance/Invoke-HardeningBaselineCheck.ps1` | Modified | Items 1-6 cross-reference, version 1.2.0 |
| `scripts/governance/README.md` | Modified | Updated descriptions, added Test-AgentAuthConfiguration |

## Gaps Found

None.
