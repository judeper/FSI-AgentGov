# Roadmap: Agent Usage & Performance Workbook (v13)

## Overview

Builds a deployable Azure Monitor Workbook (JSON template) for Copilot Studio agent monitoring in enterprise ALM environments where separation of duties prevents production Analytics tab access. Integrates with existing framework controls and adds deployment/customization documentation.

**Source:** Pending todo — Agent Usage & Performance Workbook for Enterprise ALM (2026-02-11).

**Execution model:** 3 phases. Phase 1 builds the core workbook artifact. Phases 2 and 3 depend on Phase 1 but are independent of each other and can run in parallel.

## Phases

- [ ] **Phase 1: Workbook Template & KQL** — Build Azure Monitor Workbook JSON with 3 tabs (Usage/Business Value, Performance/Errors, Operational Health) and validate KQL queries
- [ ] **Phase 2: Framework Integration** — Update Controls 3.2, 3.9, 2.9 with workbook references and add solutions catalog entry
- [ ] **Phase 3: Documentation & Deployment** — Create deployment guide, customization guide, and ALM separation-of-duties scenario documentation

## Phase Details

### Phase 1: Workbook Template & KQL
**Goal:** Build the core Azure Monitor Workbook JSON template with validated KQL queries sourced from Application Insights telemetry
**Depends on:** Nothing (core deliverable)
**Requirements:** WBK-01 through WBK-04
**Success Criteria:**
  1. Workbook JSON template exists with Usage/Business Value tab (sessions, DAU/MAU, channels, resolution rates, assisted hours, business value)
  2. Workbook JSON template includes Performance/Errors tab (latency percentiles, error types, connector success rates, RAI trigger rates)
  3. Workbook JSON template includes Operational Health tab (anomaly indicators, uptime trends, grounding issues, DLP events)
  4. All KQL queries validated against Application Insights schema (customEvents, exceptions, dependencies)
**Plans:** 2 (A = Usage + Performance tabs, B = Operational Health tab + full template validation)

### Phase 2: Framework Integration
**Goal:** Update framework controls to reference the workbook and add solutions catalog entry
**Depends on:** Phase 1 (needs workbook artifact to reference)
**Requirements:** FWK-01 through FWK-04
**Success Criteria:**
  1. Control 3.2 references workbook and documents ALM separation-of-duties scenario
  2. Control 3.9 references deployable workbook JSON template
  3. Control 2.9 references workbook as out-of-box performance KPI implementation
  4. solutions-index.md contains Agent Usage & Performance Workbook entry with status, controls, and prerequisites
  5. `mkdocs build --strict` passes
**Plans:** 2 (A = Control file updates [3.2, 3.9, 2.9], B = Solutions catalog + related reference docs)

### Phase 3: Documentation & Deployment
**Goal:** Create deployment, customization, and scenario documentation so admins can deploy and extend the workbook
**Depends on:** Phase 1 (references workbook structure and KQL queries)
**Requirements:** DOC-01 through DOC-03
**Success Criteria:**
  1. Deployment guide exists with prerequisites (App Insights, telemetry config, RBAC), deployment script, and post-deployment validation
  2. Customization guide covers adding KQL queries, modifying thresholds, extending tabs
  3. ALM separation-of-duties scenario document explains why workbooks solve the production visibility gap
  4. `mkdocs build --strict` passes
**Plans:** 2 (A = Deployment guide + script, B = Customization guide + ALM scenario doc)

## Progress

| Phase | Plans Complete | Status |
|-------|---------------|--------|
| 1. Workbook Template & KQL | 0/2 | Not started |
| 2. Framework Integration | 0/2 | Not started |
| 3. Documentation & Deployment | 0/2 | Not started |

## Parallel Execution Guide

Phases 2 and 3 have **no file overlap** and can run in parallel after Phase 1 completes:

| Phase | Plan A Files | Plan B Files |
|-------|-------------|-------------|
| 1 | Workbook JSON (usage + performance tabs) | Workbook JSON (ops health tab) + validation |
| 2 | docs/controls/pillar-3-reporting/3.2-*.md, docs/controls/pillar-3-reporting/3.9-*.md, docs/controls/pillar-2-management/2.9-*.md | docs/reference/solutions-index.md |
| 3 | Deployment guide + deployment script | Customization guide + ALM scenario doc |

## Coverage

| Requirement | Phase | Plan | Description |
|-------------|-------|------|-------------|
| WBK-01 | 1 | 01-01 | Usage / Business Value tab |
| WBK-02 | 1 | 01-01 | Performance / Errors tab |
| WBK-03 | 1 | 01-02 | Operational Health tab |
| WBK-04 | 1 | 01-02 | KQL query validation |
| FWK-01 | 2 | 02-01 | Control 3.2 workbook reference + ALM scenario |
| FWK-02 | 2 | 02-01 | Control 3.9 deployable template reference |
| FWK-03 | 2 | 02-01 | Control 2.9 workbook template reference |
| FWK-04 | 2 | 02-02 | Solutions catalog entry |
| DOC-01 | 3 | 03-01 | Deployment guide + script |
| DOC-02 | 3 | 03-02 | Customization guide |
| DOC-03 | 3 | 03-02 | ALM separation-of-duties scenario |

**Total: 11/11 requirements mapped. No orphans.**

---
*Roadmap created: 2026-02-11*
*Depth: comprehensive*
*Phases: 3 (workbook template -> framework integration + documentation)*
