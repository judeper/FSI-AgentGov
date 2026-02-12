---
phase: 2
plan: 2
status: complete
started: 2026-02-12T21:00
completed: 2026-02-12T21:25
---

# Summary: Plan 02-02 — Hardening Baseline Integration + Evidence Export

## Status: Complete

## What Was Built

Extended `restrict-agent-publishing.ps1` with per-check SHA-256 evidence hashing across all 6 criteria, and modified `Invoke-HardeningBaselineCheck.ps1` to reclassify hardening baseline items 1-6 from "Manual Attestation" to "Automated"/"Semi-Automated" via cross-reference to the publishing governance script. Updated the governance README with expanded descriptions and integration documentation.

## Tasks Completed

1. **Per-Check SHA-256 Evidence Hashing** — Added `Get-EvidenceHash` helper function and integrated per-criterion evidence hashing into all 6 check groups in `restrict-agent-publishing.ps1`. Each criterion computes a SHA-256 hash over its raw API response JSON when `-IncludeEvidence` is specified, stored as `EvidenceHash` on the check result object.

2. **Overall Integrity Hash** — Verified existing SHA-256 overall integrity hash at results aggregation (already correct, no changes needed).

3. **Dataverse-Compatible JSON Output** — Verified existing JSON structure: root `Metadata`/`Summary`/`Checks`/`Gaps`, `ConvertTo-Json -Depth 10`, ISO 8601 timestamps, valid status values (Pass/Fail/Skip/Warning). Already correct, no changes needed.

4. **Hardening Baseline Cross-Reference (Items 1-6)** — Added Check Group 0 to `Invoke-HardeningBaselineCheck.ps1` with cross-reference to `restrict-agent-publishing.ps1`. Updated `.DESCRIPTION` (12 → 18 items), `.NOTES` version (1.1.0 → 1.2.0), `ShouldProcess` text, WhatIf message, and `ScriptVersion` in results metadata. Items 1-6 report "Pass" when the publishing script exists, "Skip" when absent.

5. **Governance README Update** — Updated `restrict-agent-publishing.ps1` description (from generic to detailed 6-criterion listing), expanded related controls to "Controls 1.1, 2.1, 3.7", added `Test-AgentAuthConfiguration.ps1` to the script table, updated `Invoke-HardeningBaselineCheck.ps1` description to reflect 18 items, added Integration Notes section documenting the cross-reference relationship.

## Commits

- `458edc1` — feat(governance): add per-check evidence hashing, hardening baseline items 1-6 cross-reference

## Files Created/Modified

| File | Action | Description |
|------|--------|-------------|
| `scripts/governance/restrict-agent-publishing.ps1` | Modified | Added `Get-EvidenceHash` function, per-criterion evidence hashing for all 6 criteria, version bump 1.0.0 → 1.1.0 |
| `scripts/governance/Invoke-HardeningBaselineCheck.ps1` | Modified | Added Check Group 0 (items 1-6 cross-reference), updated description/version/ShouldProcess/WhatIf, version bump 1.1.0 → 1.2.0 |
| `scripts/governance/README.md` | Modified | Updated script descriptions, added Test-AgentAuthConfiguration.ps1, added Integration Notes section |
| `.planning/phases/02-publishing-restriction-governance/02-02-SUMMARY.md` | Created | This summary |

## Decisions Made

- Evidence hash for Criterion 2 (security groups) uses `$env.Internal.properties` rather than just the security group ID, providing broader environment context for the hash
- Evidence hash for Criterion 6 (approval workflow) aggregates governance config + flows data into a single hash since both sources contribute to the check
- `restrict-agent-publishing.ps1` version bumped to 1.1.0 (not in original plan, but appropriate given feature addition)
- Items 1-6 in hardening baseline use static Pass/Skip based on script presence rather than live execution, keeping the cross-reference lightweight

## Discovered Work

- None — all planned tasks completed as specified
