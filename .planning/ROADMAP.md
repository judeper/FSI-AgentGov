# Roadmap: Agent Usage & Performance Workbook (v15)

## Overview

Builds a deployable Azure Monitor Workbook template for Copilot Studio agent usage, performance, and error visibility — solving the ALM separation-of-duties gap for FSI organizations where production Analytics tab access is restricted (Control 2.8).

**Source:** Deferred v13 todo (refined as v15 with 12 requirements). Prior v13 research (01-workbook-template-kql/01-RESEARCH.md) provides validated telemetry schema, KQL patterns, and workbook JSON structure.

**Execution model:** 4 phases, linear dependency chain. Within each phase, plans target non-overlapping file sets for parallel execution.

## Phases

- [x] **Phase 1: Telemetry Research & KQL Query Library** — Confirm Application Insights telemetry schema from Copilot Studio, design parameterized KQL queries for all 3 workbook tabs ✅
- [x] **Phase 2: Workbook Template Development** — Build the 3-tab Azure Monitor Workbook JSON template (Usage/Business Value, Performance/Errors, Operational Health) with zone-aware thresholds ✅
- [x] **Phase 3: Deployment & Customization** — RBAC configuration guide, ARM/manual deployment playbook, customization guide for extending workbook with custom telemetry ✅
- [x] **Phase 4: Framework Integration & Validation** — Update Controls 3.2, 3.9, 2.9 with workbook references, add solutions-index.md entry, run build and language validation ✅

## Phase Details

### Phase 1: Telemetry Research & KQL Query Library
**Goal:** Document the native Copilot Studio Application Insights telemetry schema and build the complete KQL query library that powers all 3 workbook tabs
**Depends on:** Nothing (foundational — telemetry understanding informs all downstream phases)
**Requirements:** TEL-01, TEL-02
**Success Criteria:**
  1. Application Insights telemetry schema documented — customEvents event types (BotMessageReceived, BotMessageSend, TopicStart, etc.), customDimensions properties, channel identifiers (SharePoint vs Teams), session_Id usage
  2. KQL query library covers all 3 tabs: Usage/Business Value (~8 queries), Performance/Errors (~8 queries), Operational Health (~7 queries) — parameterized by time range, agent ID, and channel
  3. Queries validated against known Copilot Studio telemetry schema (tables: customEvents, dependencies, exceptions)
**Plans:** 2 (A = TEL-01 telemetry schema documentation, B = TEL-02 KQL query library design for all tabs)

### Phase 2: Workbook Template Development
**Goal:** Build the deployable Azure Monitor Workbook JSON template with 3 tabs, global parameters, and zone-aware thresholds
**Depends on:** Phase 1 (KQL queries required to populate workbook visualizations)
**Requirements:** WBK-01, WBK-02, WBK-03, WBK-04
**Success Criteria:**
  1. Usage & Business Value tab: session counts, DAU/MAU, conversation trends, channel breakdown, resolution rates, assisted hours, business value estimation
  2. Performance & Errors tab: response latency (p50/p95/p99), error rates by type, connector success rates, RAI content filtering rates
  3. Operational Health tab: anomaly detection, uptime trends, dependency health, DLP event visibility (with telemetry limitation notes), agent health summary
  4. Single deployable JSON file (`src/agent-usage-workbook.json`) with parameterized Application Insights resource ID and zone-aware thresholds
**Plans:** 2 (A = WBK-01 + WBK-02 Usage and Performance tabs with workbook shell, B = WBK-03 + WBK-04 Operational Health tab and template finalization)

### Phase 3: Deployment & Customization
**Goal:** Create deployment artifacts and customization documentation enabling enterprise teams to import, configure, and extend the workbook
**Depends on:** Phase 2 (workbook template must exist for deployment and customization guidance)
**Requirements:** DEP-01, DEP-02, FRM-03
**Success Criteria:**
  1. RBAC configuration documented: Application Insights Reader role assignment for workbook consumers, solving the ALM/separation-of-duties gap
  2. Deployment playbook with ARM template or manual import instructions, prerequisites list (Application Insights resource, Copilot Studio telemetry configuration), and validation checklist
  3. Customization guide: how to add custom telemetry panels, adjust thresholds per zone, integrate organization-specific KPIs
**Plans:** 2 (A = DEP-01 + DEP-02 RBAC guide and deployment playbook, B = FRM-03 customization guide)

### Phase 4: Framework Integration & Validation
**Goal:** Integrate workbook into framework controls and reference catalogs, validate all changes pass build and language rules
**Depends on:** Phases 1-3 (all content must be finalized before framework cross-references and validation)
**Requirements:** FRM-01, FRM-02, VAL-01
**Success Criteria:**
  1. Controls 3.2, 3.9, 2.9 updated with tip admonitions linking to workbook solution; ALM scenario cross-referenced in relevant playbooks
  2. solutions-index.md includes Agent Usage & Performance Workbook entry with status, control mappings, and component list
  3. `mkdocs build --strict` passes, `verify_controls.py` 62/62, `verify_language_rules.py` 0 violations across all modified files
**Plans:** 2 (A = FRM-01 + FRM-02 control updates and solutions catalog, B = VAL-01 build and language validation)

## Progress

| Phase | Plans Complete | Status |
|-------|---------------|--------|
| 1. Telemetry Research & KQL Query Library | 2/2 | Complete ✅ |
| 2. Workbook Template Development | 2/2 | Complete ✅ |
| 3. Deployment & Customization | 2/2 | Complete ✅ |
| 4. Framework Integration & Validation | 2/2 | Complete ✅ |

## Parallel Execution Guide

Phases have a **linear dependency chain** (1 → 2 → 3 → 4). Within each phase, plans target non-overlapping file sets:

| Phase | Plan A Files | Plan B Files |
|-------|-------------|-------------|
| 1 | docs/ telemetry schema reference doc | KQL query files or inline queries (research artifacts) |
| 2 | src/agent-usage-workbook.json (tabs 1-2 + shell) | src/agent-usage-workbook.json (tab 3 + finalization) |
| 3 | docs/playbooks/ deployment playbook | docs/playbooks/ customization guide |
| 4 | docs/controls/pillar-3-reporting/, docs/controls/pillar-2-management/, docs/reference/solutions-index.md | Validation scripts (read-only) |

**Phase 2 Plan A/B overlap:** Both plans modify `src/agent-usage-workbook.json` — execute sequentially (A→B) within Phase 2.
**Phase 3 Plan A/B:** No file overlap — can run in parallel.
**Phase 4 Plan A/B:** No file overlap — can run in parallel (Plan B is read-only validation).

## Prior Research

The deferred v13 milestone produced extensive research that remains applicable:

| Artifact | Location | Relevance |
|----------|----------|-----------|
| Telemetry schema analysis | `.planning/phases/01-workbook-template-kql/01-RESEARCH.md` | Full Copilot Studio customEvents schema, JSON structure patterns, tab designs |
| Workbook JSON patterns | `.planning/phases/01-workbook-template-kql/01-01-PLAN.md` | Detailed visualization specs for Usage + Performance tabs |
| Operational Health design | `.planning/phases/01-workbook-template-kql/01-02-PLAN.md` | Tab 3 visualization specs with anomaly detection approach |
| Existing KQL patterns | v3 Agent Observability Foundation | 14+ KQL queries (conceptual) — need adaptation from Agent 365 SDK to native Copilot Studio schema |

## Coverage

| Requirement | Phase | Plan | Description |
|-------------|-------|------|-------------|
| TEL-01 | 1 | 01-01 | Application Insights telemetry schema documentation |
| TEL-02 | 1 | 01-02 | KQL query library for all 3 workbook tabs |
| WBK-01 | 2 | 02-01 | Usage & Business Value tab |
| WBK-02 | 2 | 02-01 | Performance & Errors tab |
| WBK-03 | 2 | 02-02 | Operational Health tab |
| WBK-04 | 2 | 02-02 | Deployable workbook JSON template finalization |
| DEP-01 | 3 | 03-01 | RBAC configuration for read-only access |
| DEP-02 | 3 | 03-01 | Deployment playbook (ARM template or manual import) |
| FRM-03 | 3 | 03-02 | Customization guide |
| FRM-01 | 4 | 04-01 | Update Controls 3.2, 3.9, 2.9 with workbook references |
| FRM-02 | 4 | 04-01 | Add workbook to solutions-index.md |
| VAL-01 | 4 | 04-02 | Build and language validation |

**Total: 12/12 requirements mapped. No orphans.**

---
*Roadmap created: 2026-02-11*
*Depth: comprehensive*
*Phases: 4 (telemetry research → workbook template → deployment/customization → framework integration/validation)*
