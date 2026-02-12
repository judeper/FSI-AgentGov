# Milestone v2: Tech Debt, Architecture & Solution Completion

**Status:** SHIPPED 2026-02-05
**Phases:** 1-5 (v2 numbering)
**Total Plans:** 17

## Overview

Resolved accumulated tech debt, modernized documentation architecture, and brought 2 WIP solutions to production-ready status. Phase ordering prioritized security fixes first (CRITICAL/HIGH findings), then documentation usability, then monitoring configuration, then solution completion one at a time.

**Previous milestone:** v1 complete (33/33 requirements, 8 phases, 35 plans). See `v1-MILESTONE-AUDIT.md`.

---

## Phases

### Phase 1: PowerShell Tech Debt Resolution

**Goal:** All PowerShell scripts in FSI-AgentGov-Solutions meet FSI production security and quality standards.

**Dependencies:** None (starting phase)

**Requirements:** DEBT-01, DEBT-02, DEBT-03, DEBT-04

**Scope:** FSI-AgentGov-Solutions repository

**Work Items:**

| Item | Severity | File(s) | Description |
|------|----------|---------|-------------|
| DEBT-01 | CRITICAL | `conditional-access-automation/scripts/Register-ServicePrincipal.ps1` | Replace 3 instances of `ConvertTo-SecureString -AsPlainText -Force` with SecretManagement module pattern |
| DEBT-02 | HIGH | `conditional-access-automation/scripts/Test-PolicyCompliance.ps1` | Add try/catch error handling to unprotected code paths |
| DEBT-03 | MEDIUM | 11 PowerShell scripts across 5 solutions | Add `#Requires -Version` and `#Requires -Modules` statements |
| DEBT-04 | MEDIUM | `finra-supervision-workflow/scripts/requirements.txt` | Remove unused Python dependencies |

**Success Criteria:** All 4 met
1. Zero instances of `ConvertTo-SecureString -AsPlainText -Force`
2. Test-PolicyCompliance.ps1 has try/catch error handling (4 blocks)
3. All 14 PowerShell scripts have `#Requires` statements
4. No unused dependencies in requirements.txt files

**Plans:**
- [x] 01-01-PLAN.md — Fix CRITICAL secret exposure and HIGH error handling in CAA solution
- [x] 01-02-PLAN.md — Add #Requires to deny-event-correlation and pipeline-governance scripts
- [x] 01-03-PLAN.md — Add #Requires to remaining 5 scripts and clean FINRA requirements.txt
- [x] 01-04-PLAN.md — Comprehensive regex-based validation across all scripts

---

### Phase 2: Documentation Architecture Improvements

**Goal:** Users can navigate the 254-page documentation site with breadcrumb context and discover playbooks directly from control pages.

**Dependencies:** None (independent of Phase 1)

**Requirements:** ARCH-01, ARCH-02

**Scope:** FSI-AgentGov repository

**Work Items:**

| Item | Description |
|------|-------------|
| ARCH-01 | Add `navigation.path` feature to `mkdocs.yml` theme features |
| ARCH-02 | Add INFO admonition box to all 62 control pages linking to their 4 playbooks |

**Success Criteria:** All 4 met
1. Breadcrumb navigation visible on all pages
2. All 62 control pages contain INFO admonition with playbook links
3. `mkdocs build --strict` passes
4. `verify_controls.py` reports all 62 controls valid

**Plans:**
- [x] 02-01-PLAN.md — Enable breadcrumb navigation + Pillar 1 INFO admonitions (24 controls)
- [x] 02-02-PLAN.md — Pillar 2 INFO admonitions (21 controls)
- [x] 02-03-PLAN.md — Pillar 3+4 INFO admonitions (17 controls) + full site verification

---

### Phase 3: Monitoring Configuration Externalization

**Goal:** Learn Monitor and Regulatory Monitor classification patterns are configurable via YAML without code changes.

**Dependencies:** Phase 1 (tech debt clean before adding features)

**Requirements:** ARCH-03

**Scope:** FSI-AgentGov repository — `scripts/` directory

**Work Items:**

| Item | Description |
|------|-------------|
| ARCH-03 | Extract hardcoded classification patterns from Python to YAML config; add --config and --validate CLI flags |

**Success Criteria:** All 4 met
1. Classification patterns defined in YAML configuration file (391 lines)
2. `learn_monitor.py --dry-run --limit 5` works with externalized config
3. Both monitors support `--config` and `--validate` CLI flags
4. Non-developers can adjust monitoring sensitivity by editing YAML

**Plans:**
- [x] 03-01-PLAN.md — Create YAML config file and add config loading infrastructure
- [x] 03-02-PLAN.md — Update monitors to use config-driven classification

---

### Phase 4: Compliance Dashboard Completion

**Goal:** Compliance Dashboard moves from beta to production-ready with deployable Power Automate flows and Power BI template.

**Dependencies:** Phase 1 (solutions repo tech debt resolved first)

**Requirements:** SOL-01

**Scope:** FSI-AgentGov-Solutions — `compliance-dashboard/`

**Success Criteria:** All 6 met
1. Power Automate flow definitions deployable (2 core flows)
2. Power BI template spec documented (883 lines)
3. Sample data loads successfully (1,742 assessments, 90 scores, 13 exceptions)
4. DAX measures calculate compliance scores accurately
5. README documents all prerequisites and deployment steps
6. Solution version updated to v1.0.0

**Plans:**
- [x] 04-01-PLAN.md — Enhance sample data generation with 90-day history
- [x] 04-02-PLAN.md — Create Power Platform solution package source structure
- [x] 04-03-PLAN.md — Create deployment documentation (checklist, Power BI spec, README)
- [x] 04-04-PLAN.md — Final verification and human approval checkpoint

---

### Phase 5: Scope Drift Monitor Completion

**Goal:** Scope Drift Monitor moves from WIP to production-ready with detection logic and alert workflow.

**Dependencies:** Phase 4 (one solution at a time per project constraints)

**Requirements:** SOL-02

**Scope:** FSI-AgentGov-Solutions — `scope-drift-monitor/`

**Success Criteria:** All 6 met
1. Baseline capture script validated and documented
2. Access log aggregation implemented for available data sources
3. Drift detection logic compares baseline vs actual access
4. Alert workflow sends notifications on violations
5. README documents all prerequisites and deployment steps
6. Solution version updated to v1.1.0

**Plans:**
- [x] 05-01-PLAN.md — Enhance PowerShell scripts for baseline capture and manual detection
- [x] 05-02-PLAN.md — Create solution package source with Dataverse schema and flows
- [x] 05-03-PLAN.md — Create expansion workflow and deployment documentation
- [x] 05-04-PLAN.md — Final verification and human approval checkpoint

---

## Milestone Summary

**Decimal Phases:** None

**Key Decisions:**
- Tech debt before architecture — Fix security/quality issues before adding new features
- Architecture before solutions — Documentation improvements benefit all future work
- Defer MCP server and Copilot agent to v3 — Keep v2 focused
- Only complete 2 WIP solutions in v2 — Compliance Dashboard and Scope Drift Monitor closest to done
- Each solution handled as standalone phase — One at a time for thorough validation
- Defer ARCH-04 (awesome-pages) to v3 — Risk of breaking pedagogical nav structure
- Defer ARCH-05 (SQLite) indefinitely — JSON sufficient for 209 URLs
- Use INFO admonition for playbook links — Provides visual hierarchy
- yaml.safe_load() for security — Prevents arbitrary code execution
- Human verification gate — Automated validation + human checkpoint for production release
- Office 365 Management API over Graph API — Graph auditLogs moved to beta
- Unpacked solution format — Enables version control and pac CLI packaging

**Issues Resolved:**
- ConvertTo-SecureString security vulnerability eliminated
- Missing error handling in production scripts fixed
- Playbook discoverability improved with INFO admonitions
- Monitoring config hardcoding eliminated
- Compliance Dashboard brought to production status
- Scope Drift Monitor brought to production status

**Issues Deferred:**
- Power BI template requires manual GUI creation (documented in spec)
- Runtime testing requires Power Platform environment and E5 license
- Navigation auto-generation (ARCH-04) deferred to v3
- SQLite state file (ARCH-05) deferred indefinitely

**Technical Debt Incurred:**
- Power BI template creation remains manual (GUI-only operation)
- pac CLI packaging requires manual execution

---

_Archived: 2026-02-05 as part of v2 milestone completion_
_For current project status, see .planning/PROJECT.md_
