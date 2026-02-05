# ROADMAP: FSI-AgentGov v2 — Tech Debt, Architecture & Solution Completion

**Project:** FSI-AgentGov Comprehensive Audit & Enhancement
**Core Value:** Documentation and solutions that US FSI customers trust — every control accurate, every solution working, ongoing maintenance sustainable.
**Created:** 2026-02-04
**Depth:** Focused (5 phases)

## Overview

This roadmap delivers tech debt resolution, documentation architecture improvements, and two solution completions. Phase ordering prioritizes security fixes first (CRITICAL/HIGH findings), then documentation usability, then monitoring configuration, then solution completion one at a time.

**Previous milestone:** v1 complete (33/33 requirements, 8 phases, 35 plans). See `.planning/v1-MILESTONE-AUDIT.md`.

---

## Phase 1: PowerShell Tech Debt Resolution

**Goal:** All PowerShell scripts in FSI-AgentGov-Solutions meet FSI production security and quality standards.

**Dependencies:** None (starting phase)

**Requirements:** DEBT-01, DEBT-02, DEBT-03, DEBT-04

**Scope:** FSI-AgentGov-Solutions repository (`/Users/admin/dev/FSI-AgentGov-Solutions`)

**Work Items:**

| Item | Severity | File(s) | Description |
|------|----------|---------|-------------|
| DEBT-01 | CRITICAL | `conditional-access-automation/scripts/Register-ServicePrincipal.ps1` | Replace 3 instances of `ConvertTo-SecureString -AsPlainText -Force` (lines 149, 154, 159) with SecretManagement module pattern |
| DEBT-02 | HIGH | `conditional-access-automation/scripts/Test-PolicyCompliance.ps1` | Add try/catch error handling to unprotected code paths (config loading, Graph connection, policy retrieval, compliance checks) |
| DEBT-03 | MEDIUM | 11 PowerShell scripts across 5 solutions | Add `#Requires -Version` and `#Requires -Modules` statements declaring module dependencies |
| DEBT-04 | MEDIUM | `environment-lifecycle-management/scripts/requirements.txt`, `finra-supervision-workflow/scripts/requirements.txt` | Remove unused Python dependencies |

**Scripts missing #Requires (DEBT-03):**
1. `deny-event-correlation-report/scripts/Export-CopilotDenyEvents.ps1`
2. `deny-event-correlation-report/scripts/Export-DlpCopilotEvents.ps1`
3. `deny-event-correlation-report/scripts/Invoke-DailyDenyReport.ps1`
4. `deny-event-correlation-report/scripts/Export-RaiTelemetry.ps1`
5. `pipeline-governance-cleanup/src/Get-PipelineInventory.ps1`
6. `pipeline-governance-cleanup/src/Send-OwnerNotifications.ps1`
7. `segregation-detector/scripts/Invoke-SoDScan.ps1`
8. `segregation-detector/scripts/Import-ConflictRules.ps1`
9. `scope-drift-monitor/scripts/New-AgentBaseline.ps1`
10. `rag-source-validator/scripts/Invoke-SourceValidation.ps1`
11. `dr-testing-framework/scripts/Invoke-DRTest.ps1`

**Success Criteria:**
1. Zero instances of `ConvertTo-SecureString -AsPlainText -Force` in any PowerShell script
2. Test-PolicyCompliance.ps1 has try/catch error handling on all code paths with structured error messages
3. All 14 PowerShell scripts have `#Requires` statements declaring version and module dependencies
4. No unused dependencies in any `requirements.txt` file
5. All scripts pass regex-based validation (reuse Phase 7 validation approach)

**Plans:** 4 plans

Plans:
- [x] 01-01-PLAN.md — Fix CRITICAL secret exposure and HIGH error handling in CAA solution
- [x] 01-02-PLAN.md — Add #Requires to deny-event-correlation and pipeline-governance scripts
- [x] 01-03-PLAN.md — Add #Requires to remaining 5 scripts and clean FINRA requirements.txt
- [x] 01-04-PLAN.md — Comprehensive regex-based validation across all scripts

---

## Phase 2: Documentation Architecture Improvements

**Goal:** Users can navigate the 254-page documentation site with breadcrumb context and discover playbooks directly from control pages.

**Dependencies:** None (independent of Phase 1)

**Requirements:** ARCH-01, ARCH-02

**Scope:** FSI-AgentGov repository (this repo)

**Work Items:**

| Item | Description |
|------|-------------|
| ARCH-01 | Add `navigation.path` feature to `mkdocs.yml` theme features (config-only change) |
| ARCH-02 | Add INFO admonition box to all 62 control pages linking to their 4 playbooks |

**Success Criteria:**
1. Breadcrumb navigation visible on all pages (except homepage) after `mkdocs serve`
2. All 62 control pages contain an INFO admonition box with links to 4 playbooks (portal-walkthrough, powershell-setup, verification-testing, troubleshooting)
3. `mkdocs build --strict` passes with zero errors
4. `verify_controls.py` reports all 62 controls valid

**Plans:** 3 plans

Plans:
- [x] 02-01-PLAN.md — Enable breadcrumb navigation + Pillar 1 INFO admonitions (24 controls)
- [x] 02-02-PLAN.md — Pillar 2 INFO admonitions (21 controls)
- [x] 02-03-PLAN.md — Pillar 3+4 INFO admonitions (17 controls) + full site verification

---

## Phase 3: Monitoring Configuration Externalization

**Goal:** Learn Monitor and Regulatory Monitor classification patterns are configurable via YAML without code changes.

**Dependencies:** Phase 1 (tech debt clean before adding features)

**Requirements:** ARCH-03

**Scope:** FSI-AgentGov repository — `scripts/` directory

**Work Items:**

| Item | Description |
|------|-------------|
| ARCH-03 | Extract hardcoded classification patterns from `monitoring_shared.py` and `regulatory_monitor.py` into `scripts/config/monitoring-config.yaml`; add YAML loader with validation; add `--config` and `--validate` CLI flags |

**Success Criteria:**
1. Classification patterns defined in YAML configuration file
2. `learn_monitor.py --dry-run --limit 5` works with externalized config
3. Both monitors support `--config` and `--validate` CLI flags
4. Non-developers can adjust monitoring sensitivity by editing YAML

**Plans:** 2 plans

Plans:
- [x] 03-01-PLAN.md — Create YAML config file and add config loading infrastructure
- [x] 03-02-PLAN.md — Update monitors to use config-driven classification

---

## Phase 4: Compliance Dashboard Completion

**Goal:** Compliance Dashboard moves from beta to production-ready with deployable Power Automate flows and Power BI template.

**Dependencies:** Phase 1 (solutions repo tech debt resolved first)

**Requirements:** SOL-01

**Scope:** FSI-AgentGov-Solutions — `compliance-dashboard/`

**Success Criteria:**
1. Power Automate flow definitions deployable (3 core data collection flows)
2. Power BI template (.pbit) opens in Power BI Desktop and renders correctly
3. Sample data loads successfully via load script
4. DAX measures calculate compliance scores accurately
5. README documents all prerequisites, deployment steps, and known limitations
6. Solution version updated from v1.0.0-beta to v1.0.0

**Plans:** 4 plans

Plans:
- [x] 04-01-PLAN.md — Enhance sample data generation with 90-day history and realistic distributions
- [x] 04-02-PLAN.md — Create Power Platform solution package source structure with flow definitions
- [x] 04-03-PLAN.md — Create deployment documentation (checklist, Power BI spec, README update)
- [x] 04-04-PLAN.md — Final verification and human approval checkpoint

---

## Phase 5: Scope Drift Monitor Completion

**Goal:** Scope Drift Monitor moves from WIP to production-ready with detection logic and alert workflow.

**Dependencies:** Phase 4 (one solution at a time per project constraints)

**Requirements:** SOL-02

**Scope:** FSI-AgentGov-Solutions — `scope-drift-monitor/`

**Success Criteria:**
1. Baseline capture script validated and documented
2. Access log aggregation implemented for available data sources
3. Drift detection logic compares baseline vs actual access
4. Alert workflow sends notifications on violations
5. README documents all prerequisites, deployment steps, and known limitations
6. Solution version updated from v1.0.0 to v1.1.0

**Plans:** 4 plans

Plans:
- [x] 05-01-PLAN.md — Enhance PowerShell scripts for baseline capture and manual detection
- [x] 05-02-PLAN.md — Create solution package source with Dataverse schema and flows
- [x] 05-03-PLAN.md — Create expansion workflow and deployment documentation
- [x] 05-04-PLAN.md — Final verification and human approval checkpoint

---

## Progress

| Phase | Requirements | Status | Progress |
|-------|--------------|--------|----------|
| 1 - PowerShell Tech Debt Resolution | 4 | Complete | ██████████ 100% |
| 2 - Documentation Architecture | 2 | Complete | ██████████ 100% |
| 3 - Monitoring Configuration | 1 | Complete | ██████████ 100% |
| 4 - Compliance Dashboard | 1 | Complete | ██████████ 100% |
| 5 - Scope Drift Monitor | 1 | Complete | ██████████ 100% |

**Total:** 9/9 requirements mapped (100% coverage)

---

## Coverage Validation

All 9 v2 requirements mapped to phases:

**Phase 1 (4 requirements):**
- DEBT-01: Fix Register-ServicePrincipal.ps1 secret exposure
- DEBT-02: Add error handling to Test-PolicyCompliance.ps1
- DEBT-03: Add #Requires statements to 11 PowerShell scripts
- DEBT-04: Remove unused dependencies in requirements.txt files

**Phase 2 (2 requirements):**
- ARCH-01: Enable breadcrumb navigation
- ARCH-02: Add playbook discoverability admonitions

**Phase 3 (1 requirement):**
- ARCH-03: Externalize monitoring classification patterns to YAML

**Phase 4 (1 requirement):**
- SOL-01: Complete Compliance Dashboard (beta -> production)

**Phase 5 (1 requirement):**
- SOL-02: Complete Scope Drift Monitor (WIP -> production)

**Orphans:** None (100% coverage achieved)

---

## Deferred (v3)

| Item | Reason |
|------|--------|
| ARCH-04: Navigation auto-generation | Risk of breaking pedagogical structure; needs research phase |
| ARCH-05: SQLite state file | JSON sufficient for 209 URLs; revisit if scale exceeds 1000 |
| MCP server for governance framework | Separate initiative |
| Copilot Studio agent for governance Q&A | Separate initiative |
| Complete Planned solutions (RAG, COI, Hallucination, DR) | Focus on 2 closest-to-done solutions |

---

## Notes

**Phase ordering rationale:**
- Phase 1 resolves CRITICAL/HIGH security findings before any new feature work
- Phase 2 can run in parallel with Phase 1 (different repos, independent work)
- Phase 3 follows tech debt (monitoring improvements after security clean)
- Phases 4-5 complete solutions one at a time per project constraint
- ARCH-04/ARCH-05 deferred per research recommendations

**Cross-repo coordination:**
- Phase 1, 4, 5 operate in FSI-AgentGov-Solutions
- Phase 2, 3 operate in FSI-AgentGov
- Git commits must run from within target repo

---

*Roadmap version: 2.8*
*Last updated: 2026-02-05*
