# Roadmap: Framework Currency Reviews (v7.1)

## Overview

A maintenance milestone that addresses 4 pending todos to keep the FSI Agent Governance Framework current. Unlike solution milestones (v4–v9), this is a docs-only milestone with no cross-repo work. The key architectural insight is that all 4 work streams target non-overlapping files, enabling full subagent parallelism — 4 plans execute simultaneously in a single wave.

**Critical item:** Dataverse Purview audit event deprecation (May 2026) requires immediate Control 1.7 update with alternative guidance.

## Phases

**Phase Numbering:**
- Integer phases (1, 2): Planned milestone work

- [ ] **Phase 1: Parallel Documentation Updates** — 4 subagents execute simultaneously: Dataverse deprecation warnings, Agent 365 GA updates, evaluation framework enhancements, and multi-source agent investigation
- [ ] **Phase 2: Validation and Cleanup** — Build validation, FSI language compliance, and todo closure

## Phase Details

### Phase 1: Parallel Documentation Updates
**Goal**: All 4 pending todos resolved with documentation updates applied to the framework — Dataverse audit deprecation warning on Control 1.7, Agent 365 architecture and controls updated for GA readiness, evaluation framework references added to testing/monitoring controls, and multi-source agent investigation recommendation produced
**Depends on**: Nothing (first phase)
**Requirements**: FCR-01 through FCR-14
**Success Criteria** (what must be TRUE):
  1. Control 1.7 contains a deprecation warning admonition about Dataverse Purview audit event changes (May 2026) with guidance to use Dataverse APIs as alternative, and regulatory-mappings.md reflects the change for SEC 17a-4 / FINRA 4511
  2. agent-365-architecture.md reflects Agent 365 meeting notes including GA readiness status, declarative agent deployment limitations, shadow AI discovery roadmap, and licensing caveats
  3. Controls 1.11, 2.12, 3.8 are updated with Agent 365 findings; role-catalog.md reflects AI Admin limitations; Defender-referencing controls (1.5, 1.6, 1.8) note security event inconsistencies; preview admonitions reflect GA timeline
  4. Controls 2.18, 2.8, 3.1 reference Copilot Studio's evaluation framework capabilities; verification-testing playbook for 2.18 includes evaluation methodology guidance
  5. Investigation report exists with clear build/don't-build/defer recommendation for multi-source governance agent architecture, with estimated effort if applicable
**Plans**: 4 plans (Wave 1 — all parallel, zero file conflicts)

Plans:
- [ ] 01-01-PLAN.md — Dataverse Purview audit deprecation: Control 1.7 warning, 1.10/2.1 review, regulatory-mappings.md update (FCR-01, FCR-02, FCR-03)
- [ ] 01-02-PLAN.md — Agent 365 GA readiness: architecture doc, controls 1.11/2.12/3.8/1.5/1.6/1.8, role-catalog, preview admonitions (FCR-04, FCR-05, FCR-06, FCR-07, FCR-08)
- [ ] 01-03-PLAN.md — Evaluation framework enhancements: controls 2.18/2.8/3.1, verification-testing playbook (FCR-09, FCR-10, FCR-11, FCR-12)
- [ ] 01-04-PLAN.md — Multi-source governance agent investigation: Options A/B/C analysis, recommendation report (FCR-13, FCR-14)

### Phase 2: Validation and Cleanup
**Goal**: All Phase 1 changes validated (build passes, language rules followed), all 4 todo files moved to done
**Depends on**: Phase 1
**Requirements**: FCR-15, FCR-16, FCR-17
**Success Criteria** (what must be TRUE):
  1. `mkdocs build --strict` passes with zero errors
  2. `python scripts/verify_controls.py` passes with zero errors
  3. All updated controls use FSI-safe language (no "ensures compliance", "guarantees", "will prevent", "eliminates risk")
  4. All 4 todo files moved from `.planning/todos/pending/` to `.planning/todos/done/`
  5. STATE.md and ROADMAP.md updated with completion status
**Plans**: 1 plan

Plans:
- [ ] 02-01-PLAN.md — Build validation, language audit, todo closure, state update (FCR-15, FCR-16, FCR-17)

## Progress

**Execution Order:**
Phases execute in numeric order: 1 → 2

| Phase | Plans Complete | Status | Completed |
|-------|---------------|--------|-----------|
| 1. Parallel Documentation Updates | 0/4 | Planned | — |
| 2. Validation and Cleanup | 0/1 | Planned | — |

## Coverage

| Requirement | Phase | Plan | Description |
|-------------|-------|------|-------------|
| FCR-01 | Phase 1 | 01-01 | Control 1.7 Dataverse deprecation warning |
| FCR-02 | Phase 1 | 01-01 | regulatory-mappings.md Dataverse API alternative |
| FCR-03 | Phase 1 | 01-01 | Controls 1.10, 2.1 review for deprecation impact |
| FCR-04 | Phase 1 | 01-02 | agent-365-architecture.md GA update |
| FCR-05 | Phase 1 | 01-02 | Controls 1.11, 2.12, 3.8 Agent 365 updates |
| FCR-06 | Phase 1 | 01-02 | role-catalog.md AI Admin limitations |
| FCR-07 | Phase 1 | 01-02 | Defender controls (1.5, 1.6, 1.8) review |
| FCR-08 | Phase 1 | 01-02 | Preview/Frontier admonition updates |
| FCR-09 | Phase 1 | 01-03 | Control 2.18 evaluation framework reference |
| FCR-10 | Phase 1 | 01-03 | Control 2.8 regression detection enhancement |
| FCR-11 | Phase 1 | 01-03 | Control 3.1 comparative monitoring enhancement |
| FCR-12 | Phase 1 | 01-03 | Playbook 2.18 evaluation methodology |
| FCR-13 | Phase 1 | 01-04 | Multi-source agent investigation report |
| FCR-14 | Phase 1 | 01-04 | Effort estimate and approach recommendation |
| FCR-15 | Phase 2 | 02-01 | Build validation (mkdocs + verify_controls) |
| FCR-16 | Phase 2 | 02-01 | FSI language rules compliance |
| FCR-17 | Phase 2 | 02-01 | Todo files moved to done |

**Total: 17/17 requirements mapped. No orphans.**

---
*Roadmap created: 2026-02-10*
*Depth: comprehensive*
*Phases: 2 (parallel documentation + validation)*

