# Milestone v4: Audit Configuration Validator

**Status:** ✅ SHIPPED 2026-02-06
**Phases:** 1-4
**Total Plans:** 11

## Overview

This milestone delivers an automated audit configuration validation solution for Microsoft 365 and Power Platform environments. The solution validates that audit logging is properly enabled and configured across tenant-level unified audit, per-environment Power Platform audit, and Purview retention policies. The validator provides continuous monitoring, configuration drift detection, and compliance evidence export to support SEC 17a-4(f) automatic verification requirements.

## Phases

### Phase 1: Core Validation Scripts

**Goal**: PowerShell scripts validate tenant-level audit configuration with robust error handling and dual validation strategy to prevent false positives.

**Depends on**: Nothing (first phase)

**Requirements**: TVAL-01, TVAL-02, TVAL-03, TVAL-04, PVAL-01, PVAL-02, PVAL-03, INFR-05

**Plans**: 3 plans

Plans:
- [x] 01-01-PLAN.md — Auth helpers and Unified Audit Log validation with dual strategy (TVAL-01, TVAL-03, TVAL-04, INFR-05)
- [x] 01-02-PLAN.md — Mailbox audit and Purview retention validation (TVAL-02, PVAL-01, PVAL-02, PVAL-03)
- [x] 01-03-PLAN.md — Main orchestrator and end-to-end verification

**Details:**
- 6 PowerShell scripts (2,191 total lines)
- Dual validation strategy: cmdlet checks + canary event retrieval
- CustomAttribute15 for canary events (auditable, non-disruptive)
- 24-hour grace period for newly-enabled audit
- Zone-specific retention thresholds: Zone1=180d, Zone2=365d, Zone3=730d

### Phase 2: Infrastructure & Environment Validation

**Goal**: Solution infrastructure established with Dataverse schema for status tracking, and per-environment audit validation using Dataverse Web API.

**Depends on**: Phase 1

**Requirements**: INFR-01, INFR-02, INFR-03, INFR-04, EVAL-01, EVAL-02, EVAL-03, EVAL-04, EVAL-05, EVID-03

**Plans**: 3 plans

Plans:
- [x] 02-01-PLAN.md — Solution structure, Dataverse API client, schema scripts, env vars, connection refs, and deploy orchestrator (INFR-01, INFR-02, INFR-03, INFR-04, EVID-03)
- [x] 02-02-PLAN.md — Power Platform auth helper, Dataverse write helper, and environment discovery with registry sync (EVAL-04)
- [x] 02-03-PLAN.md — Per-environment audit and retention validators with environment-level orchestrator (EVAL-01, EVAL-02, EVAL-03, EVAL-05)

**Details:**
- 9 PowerShell scripts (3,517 total lines) + 7 Python deployment scripts
- Tier 2 solution pattern (README, CHANGELOG, docs/, scripts/, src/)
- Organization-owned Dataverse tables for immutable validation history
- fsi_ publisher prefix, fsi_cr_* connection refs, fsi_ACV_* env vars
- Trial/Developer environment filtering with 24-hour grace period

### Phase 3: Automated Orchestration & Alerting

**Goal**: Scheduled validation runs with automatic drift detection and multi-channel alerting when configuration issues are detected.

**Depends on**: Phase 2

**Requirements**: AUTO-01, AUTO-02, AUTO-03, AUTO-04

**Plans**: 2 plans

Plans:
- [x] 03-01-PLAN.md — Azure Automation runbook wrappers and drift detection helper (AUTO-01, AUTO-02)
- [x] 03-02-PLAN.md — Power Automate flow definitions, adaptive card templates, and deployment guide (AUTO-01, AUTO-02, AUTO-03, AUTO-04)

**Details:**
- 3 PowerShell scripts (831 lines) + 5 flow/alert definition files (2,167 lines)
- Daily schedule offset (tenant 6 AM, environment 7 AM UTC)
- Drift detection compares numeric severity values with fail-open design
- Severity-based alert routing (Failed/Error → Teams + email, Warning → email only)
- Scope Try-Catch pattern for flow error handling

### Phase 4: Evidence Export & Framework Integration

**Goal**: Compliance evidence export with integrity hashing and Control 1.7 documentation updates for complete framework integration.

**Depends on**: Phase 3

**Requirements**: EVID-01, EVID-02, EVID-04, DOCS-01, DOCS-02, DOCS-03, DOCS-04

**Plans**: 3 plans

Plans:
- [x] 04-01-PLAN.md — Evidence export scripts with JSON output and SHA-256 integrity hashing (EVID-01, EVID-02, EVID-04)
- [x] 04-02-PLAN.md — Control 1.7 tip admonition and solutions-index.md catalog entry (DOCS-01, DOCS-02)
- [x] 04-03-PLAN.md — Solution README update and evidence export deployment guide (DOCS-03, DOCS-04)

**Details:**
- SHA-256 companion file with standard two-space delimiter format
- ConvertTo-Json -Depth 10 for complete nested validation data
- Option set values mapped to human-readable strings
- Control 1.7 "Automated Validation" tip admonition
- Solution v1.0.0 README with prerequisites and quick start

---

## Milestone Summary

**Key Decisions:**

- Dual validation strategy (cmdlet + canary event) to prevent false positives
- Organization-owned Dataverse tables for immutable audit history (no update/delete)
- Zone thresholds stored as environment variables (not hardcoded)
- Daily schedule offset (tenant 6 AM, environment 7 AM UTC) prevents resource contention
- Severity-based alert routing reduces Teams noise while documenting all drift
- SHA-256 companion file uses standard format compatible with shasum/certutil/sha256sum
- Enhance existing Control 1.7 (not create new control number)

**Issues Resolved:**

- False positive prevention via dual validation and 24-hour grace period
- Dataverse immutability via organization-owned tables with security role restriction
- Trial/Developer environment noise via automatic filtering
- Cross-platform evidence verification via standard SHA-256 format

**Issues Deferred:**

- Auto-remediation (v4.1+) — too risky without approval workflow
- Advanced validation: SEC 17a-4(f) compliance report, WORM verification (v4.1+)
- Integration: ELM hooks, Compliance Dashboard feeds (v9)

**Technical Debt Incurred:**

None. All phases completed without deferred items or workarounds.

---

_For current project status, see .planning/ROADMAP.md_
