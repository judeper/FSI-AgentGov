# Roadmap: Agent Security Configuration Governance (v17)

## Overview

Automate per-agent authentication enforcement, publishing restriction validation, and zone-based access configuration governance — closing the manual attestation gap across Controls 1.1, 3.7, and 3.8. Converts 6 manual-only SSPM checks to automated validation, creates the phantom `restrict-agent-publishing.ps1` governance script, and adds zone-policy compliance verification for agent access settings.

**Source:** Three high-priority pending todos from v16 research addressing automation gaps where agent-level security checks are manual-only.

**Execution model:** 4 phases. Phases 1–3 are independent (parallel-eligible). Phase 4 depends on 1–3. Within each phase, plans target non-overlapping file sets for parallel execution.

## Phases

- [x] **Phase 1: Agent Authentication Enforcement** — PowerShell script validating 6 SSPM items per agent, zone-based logic, drift detection, SHA-256 evidence export
- [x] **Phase 2: Publishing Restriction Governance** — `restrict-agent-publishing.ps1` validating 6 publishing criteria, SHA-256 evidence, hardening baseline integration
- [x] **Phase 3: Zone Access Validation** — M365 Admin Center agent access settings verification per zone, admin exclusion group validation, drift detection
- [x] **Phase 4: Framework Integration & Validation** — Controls 1.1/3.7/3.8 updates, solutions-index entry, hardening baseline reclassification, full build validation

## Status: COMPLETE (2026-02-12)

All 4 phases, 8 plans, 12 requirements delivered. Archived to milestones/.
