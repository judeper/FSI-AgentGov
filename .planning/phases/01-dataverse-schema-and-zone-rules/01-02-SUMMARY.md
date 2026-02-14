---
phase: 1
plan: 2
title: "Zone Rules & Classification Logic"
completed: 2026-02-13
commit: 983f019
---

# Phase 1 Plan 02 Summary: Zone Rules & Classification Logic

## What Was Built

Created `scripts/asard_zone_rules.py` — zone-based sharing rules configuration, zone classification logic, sharing principal parsing, and compliance evaluation functions.

### Deliverables

| Artifact | Description |
|----------|-------------|
| `ZONE_SHARING_RULES` | Zone 0/1/2/3 rule definitions (allow_individual, allow_group, allow_everyone, allow_public, require_approved_groups) |
| `classify_environment_zone()` | Cascade: Dataverse policy lookup → naming convention → fallback |
| `parse_sharing_principals()` | BAP API JSON parser → structured dict (individuals, groups, everyone, public) |
| `evaluate_zone_compliance()` | Zone-specific rule evaluation with violation type detection |
| `get_approved_groups_for_zone()` | Dataverse lookup for approved security groups per zone |
| `check_agent_compliance()` | End-to-end orchestrator: classify → parse → evaluate → enrich |
| `test_asard_zone_rules.py` | 29 unit tests — all passing |

### Zone Rules Summary

| Zone | Individual | Group | Everyone | Public | Approved Required |
|------|-----------|-------|----------|--------|-------------------|
| 0 (Unclassified) | ✅ | ✅ | ❌ | ❌ | No |
| 1 (Personal) | ✅ | ❌ | ❌ | ❌ | No |
| 2 (Team) | ✅ | ✅ | ❌ | ❌ | No |
| 3 (Enterprise) | ❌ | ✅ | ❌ | ❌ | Yes |

### Tech Stack

- Python 3 standard library (json, re, logging)
- `caa_client.CAAClient` for Dataverse queries (optional)
- pytest for unit tests

## Key Files

| File | Action | Description |
|------|--------|-------------|
| `scripts/asard_zone_rules.py` | Created | Zone rules, classification, evaluation |
| `scripts/test_asard_zone_rules.py` | Created | 29 unit test stubs |

## Dependency Graph

```
01-01-PLAN (schema) → 01-02-PLAN (this) → 02-01-PLAN (detection uses check_agent_compliance)
```

## Decisions Made

1. Zone classification cascade: policy table → naming convention → fallback (matches plan spec)
2. Zone 0 (Unclassified) same rules as Zone 2 (no Everyone/Public) — safe default
3. Organization-wide sharing treated as equivalent to Everyone (`has_everyone = True`)
4. Approved group check case-insensitive (group IDs lowered for comparison)
5. Test stubs use pytest structure per plan specification

## Self-Check

- [x] Syntax check passes (`python -m py_compile`)
- [x] Import test passes — all functions importable
- [x] 29/29 unit tests pass
- [x] Zone 1 flags group sharing as non-compliant ✓
- [x] Zone 2 flags Everyone/Public as non-compliant ✓
- [x] Zone 3 flags unapproved groups as non-compliant ✓
- [x] Zone classification case-insensitive ✓
- [x] Malformed JSON handled gracefully ✓
- [x] `check_agent_compliance()` output format matches fsi_AgentSharingCompliance schema ✓
