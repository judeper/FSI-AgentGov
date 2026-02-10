# Requirements: Framework Currency Reviews (v7.1)

**Defined:** 2026-02-10
**Core Value:** Documentation and solutions that US FSI customers trust.

## v7.1 Requirements

Maintenance milestone to address 4 pending todos: critical Dataverse audit deprecation, Agent 365 GA readiness review, evaluation framework enhancements, and multi-source governance agent investigation.

### Dataverse Audit Deprecation (Critical — May 2026 deadline)

- [ ] **FCR-01**: Control 1.7 updated with deprecation warning admonition for Dataverse Purview audit event changes (before-and-after field values removed May 2026), including guidance to use Dataverse APIs as alternative
- [ ] **FCR-02**: regulatory-mappings.md updated with Dataverse API alternative approach for SEC 17a-4 / FINRA 4511 recordkeeping requirements affected by the deprecation
- [ ] **FCR-03**: Controls 1.10 and 2.1 reviewed and updated if Dataverse audit deprecation affects their guidance (retention completeness, release channel impact)

### Agent 365 GA Readiness Review

- [ ] **FCR-04**: agent-365-architecture.md updated to reflect meeting notes (GA readiness, deployment limitations for declarative agents, shadow AI discovery roadmap, licensing caveats)
- [ ] **FCR-05**: Controls 1.11, 2.12, 3.8 updated with Agent 365 meeting findings (agent registry visibility, admin deployment constraints, observability integration status)
- [ ] **FCR-06**: role-catalog.md updated with Agent 365 admin role limitations (Global Admin + AI Admin only, no fine-grained roles at GA, feedback status)
- [ ] **FCR-07**: Controls referencing Defender integration (1.5, 1.6, 1.8) reviewed against meeting notes on blocked prompt visibility gaps and security event inconsistencies
- [ ] **FCR-08**: Preview/Frontier program admonitions across affected controls updated to reflect current GA timeline signals

### AI Agent Evaluation Framework Enhancements

- [ ] **FCR-09**: Control 2.18 (Agent Testing) enhanced with reference to Copilot Studio's built-in 8-step evaluation framework and grader types
- [ ] **FCR-10**: Control 2.8 (Change Management) enhanced with regression detection via sequential evaluation comparisons
- [ ] **FCR-11**: Control 3.1 (Operational Monitoring) enhanced with comparative monitoring pattern for tracking agent quality over time
- [ ] **FCR-12**: Verification-testing playbook for 2.18 enhanced with evaluation methodology guidance

### Multi-Source Governance Agent Investigation

- [ ] **FCR-13**: Investigation report produced with clear build/don't-build/defer recommendation for multi-source citation agent architecture (Options A/B/C evaluated)
- [ ] **FCR-14**: If recommendation is "build" or "defer," estimated effort, maintenance cost, and recommended approach documented for inclusion in v10+ planning

### Validation

- [ ] **FCR-15**: All documentation changes pass `mkdocs build --strict` and `python scripts/verify_controls.py`
- [ ] **FCR-16**: All updated controls follow FSI language rules (no "ensures compliance", "guarantees", etc.)
- [ ] **FCR-17**: All 4 pending todo files moved to `.planning/todos/done/` upon completion

## File Conflict Analysis

Zero file overlaps between the 4 todos — all can execute in parallel:

| Todo | Write Targets |
|------|--------------|
| Dataverse deprecation | control-1.7, 1.10, 2.1, regulatory-mappings.md, monitoring-config.yaml |
| Agent 365 review | agent-365-architecture.md, control-1.11, 2.12, 3.8, role-catalog.md, 1.5, 1.6, 1.8 |
| Evaluation blog | control-2.18, 2.8, 3.1, playbook verification-testing/2.18 |
| Multi-source agent | Investigation output only (.planning/ artifact) |

## Out of Scope

| Feature | Reason |
|---------|--------|
| New controls | v7.1 is a currency review, not a control addition milestone |
| Solution code changes | No solution artifacts modified; docs-only milestone |
| v8 File Upload Security Configurator | Separate solution milestone (follows v7.1) |
| Implementation of multi-source agent | v7.1 only investigates; build deferred to v10+ |

---
*Requirements defined: 2026-02-10*
*Previous REQUIREMENTS.md archived with v7 milestone*

## Traceability

| Requirement | Phase | Status |
|-------------|-------|--------|
| FCR-01 | Phase 1 | Pending |
| FCR-02 | Phase 1 | Pending |
| FCR-03 | Phase 1 | Pending |
| FCR-04 | Phase 1 | Pending |
| FCR-05 | Phase 1 | Pending |
| FCR-06 | Phase 1 | Pending |
| FCR-07 | Phase 1 | Pending |
| FCR-08 | Phase 1 | Pending |
| FCR-09 | Phase 1 | Pending |
| FCR-10 | Phase 1 | Pending |
| FCR-11 | Phase 1 | Pending |
| FCR-12 | Phase 1 | Pending |
| FCR-13 | Phase 1 | Pending |
| FCR-14 | Phase 1 | Pending |
| FCR-15 | Phase 2 | Pending |
| FCR-16 | Phase 2 | Pending |
| FCR-17 | Phase 2 | Pending |

**Coverage:**
- v7.1 requirements: 17 total
- Mapped to phases: 17
- Unmapped: 0

---
*Traceability updated: 2026-02-10*
