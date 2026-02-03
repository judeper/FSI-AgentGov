# ROADMAP: FSI-AgentGov Enhancement

**Project:** FSI-AgentGov Comprehensive Audit & Enhancement
**Core Value:** Documentation and solutions that US FSI customers trust — every control accurate, every solution working, ongoing maintenance sustainable.
**Created:** 2026-02-02
**Depth:** Comprehensive (8 phases, 5-10 plans each)

## Overview

This roadmap delivers a comprehensive audit and enhancement of the FSI Agent Governance Framework across two repositories (FSI-AgentGov documentation and FSI-AgentGov-Solutions). The work spans 8 phases that address time-sensitive technical fixes, foundational documentation accuracy, strategic architecture updates, feature enhancements, regulatory validation, solution audits, functional testing, and monitoring improvements.

The phases are ordered to prioritize the February 2026 pipeline deadline, establish documentation accuracy as a foundation, document Microsoft's strategic Agent 365 direction, then systematically enhance controls, validate regulations, audit solutions, test implementations, and optimize monitoring systems.

---

## Phase 1: Critical Technical Remediation

**Goal:** Users have accurate documentation for time-sensitive compliance deadlines and API deprecations.

**Dependencies:** None (starting phase)

**Requirements:** TECH-01, TECH-02, TECH-08

**Plans:** 2 plans

Plans:
- [ ] 01-01-PLAN.md — FSI-AgentGov-Solutions x-api-key deprecation warnings
- [ ] 01-02-PLAN.md — Pipeline deadline cross-references and build validation

**Success Criteria:**
1. February 2026 pipeline deadline is prominently documented in Control 2.1 with licensing implications and required actions
2. All API deprecation warnings include specific dates (x-api-key March 31 2026, EWS, SharePoint Add-Ins, Key Vault)
3. Affected playbooks contain x-api-key deprecation warnings with migration guidance
4. Documentation clearly states urgency and impact for FSI organizations

---

## Phase 2: Documentation Audit Foundation — COMPLETE (2026-02-03)

**Goal:** Users can trust that all 62 controls reflect current Microsoft capabilities with accurate citations and consistent formatting.

**Dependencies:** Phase 1 (technical fixes complete)

**Requirements:** AUDIT-01, AUDIT-02, AUDIT-03, AUDIT-04, AUDIT-05

**Plans:** 9/9 complete

Plans:
- [x] 02-01-PLAN.md — Audit Pillar 1 Security (24 controls, 96 playbooks)
- [x] 02-02-PLAN.md — Audit Pillar 2 Management (21 controls, 84 playbooks)
- [x] 02-03-PLAN.md — Audit Pillar 3 Reporting (10 controls, 40 playbooks)
- [x] 02-04-PLAN.md — Audit Pillar 4 SharePoint (7 controls, 28 playbooks)
- [x] 02-05-PLAN.md — User review checkpoint for all audit reports
- [x] 02-06-PLAN.md — Apply corrections to Pillar 1
- [x] 02-07-PLAN.md — Apply corrections to Pillar 2
- [x] 02-08-PLAN.md — Apply corrections to Pillar 3
- [x] 02-09-PLAN.md — Apply corrections to Pillar 4 and final validation

**Success Criteria:**
1. All 62 controls verified against current Microsoft Learn documentation with discrepancies resolved
2. 10-section control template structure validated across all controls with consistent ordering
3. All regulatory citations verified for accuracy with corrections applied where needed
4. Formatting consistency achieved across all controls (headings, tables, admonitions, code blocks)
5. Cross-references between controls and Microsoft Learn documentation validated

---

## Phase 3: Agent 365 Strategic Architecture — COMPLETE (2026-02-03)

**Goal:** Users understand Microsoft's unified agent governance direction and can plan migration from per-platform governance.

**Dependencies:** Phase 2 (documentation accuracy validated)

**Requirements:** FEAT-01, FEAT-02

**Plans:** 3/3 complete

Plans:
- [x] 03-01-PLAN.md — Create Agent 365 unified governance architecture framework document
- [x] 03-02-PLAN.md — Update Controls 1.2, 1.11, 2.12 with Agent 365 cross-references
- [x] 03-03-PLAN.md — Validation and cross-reference verification

**Success Criteria:**
1. New framework document explains Agent 365 unified control plane concept and comparison with current per-platform governance
2. Microsoft Entra Agent ID architecture documented with sponsorship model and FINRA 3110 alignment
3. FSI organizations have clear guidance on early adoption benefits and migration roadmap
4. Cross-references established between Agent 365 architecture and existing controls (1.2, 1.11, 2.12)

---

## Phase 4: Feature Enhancement Updates — COMPLETE (2026-02-03)

**Goal:** Users have documentation for all GA and preview governance features released in 2025-2026.

**Dependencies:** Phase 3 (strategic architecture established)

**Requirements:** FEAT-03, FEAT-04, FEAT-05, FEAT-06, FEAT-07

**Plans:** 5/5 complete

Plans:
- [x] 04-01-PLAN.md — Control 1.5 virtual connectors DLP enhancement + playbooks
- [x] 04-02-PLAN.md — Control 1.6 DSPM weekly assessments, observability, remediation + playbooks
- [x] 04-03-PLAN.md — Control 3.8 AI Feature Access Control + role catalog updates (AI Administrator, Defender XDR Admin)
- [x] 04-04-PLAN.md — Defender for Cloud Apps verification and cross-control consistency
- [x] 04-05-PLAN.md — Validation, cross-reference verification, and researcher package regeneration

**Success Criteria:**
1. Control 1.5 updated with virtual connectors table for Copilot Studio feature-level DLP
2. Control 1.6 enhanced with weekly risk assessments and AI observability capabilities
3. Control 3.8 updated with AI Feature Access Control for user-level feature restrictions
4. All Defender for Power Platform capabilities documented including preview features
5. Role catalog updated with AI Administrator and Defender XDR Administrator roles

---

## Phase 5: Regulatory Validation

**Goal:** Users can verify that all US FSI regulatory requirements are accurately mapped and current.

**Dependencies:** Phase 2 (documentation audit complete)

**Requirements:** REG-01, REG-02, REG-03, REG-04, REG-05

**Plans:** 4 plans

Plans:
- [ ] 05-01-PLAN.md — Federal regulatory citation verification audit (7 bodies, 62 controls)
- [ ] 05-02-PLAN.md — FINRA 2026 Report AI/agent analysis + retention period validation
- [ ] 05-03-PLAN.md — State AI laws verification and expansion (CO, TX, NYC, IL, CA)
- [ ] 05-04-PLAN.md — Corrections pass: apply all findings, integrate FINRA Report, validate build

**Success Criteria:**
1. All US FSI regulation mappings verified (FINRA, SEC, SOX, GLBA, OCC, Fed SR 11-7, CFTC)
2. 2025-2026 regulatory updates incorporated with specific changes documented
3. Retention period classifications validated (3-year vs 6-year) with accurate citations
4. FINRA 2026 Report findings added to relevant controls with specific guidance
5. State AI laws applicability reviewed (Colorado, NYC, Texas) with FSI impact assessment

---

## Phase 6: Solutions Audit

**Goal:** Users know which solutions are complete, which are WIP, and how solutions align with framework controls.

**Dependencies:** Phase 2 (documentation accuracy validated)

**Requirements:** SOL-01, SOL-02, SOL-03, SOL-05, TECH-03, TECH-04, TECH-05, TECH-06, TECH-07

**Success Criteria:**
1. All 13 solutions audited with completeness status clearly marked (Complete, WIP, Beta)
2. Solution-to-control mappings validated with bidirectional cross-references updated
3. Incomplete solutions flagged with status indicators and missing components documented
4. Solution prerequisites and dependencies documented for each implementation
5. Technical accuracy issues resolved (PAYG licensing, Service Principal bypass, DLP enforcement modes, Defender configuration, Information Barriers limitation)

---

## Phase 7: Solutions Functional Testing

**Goal:** Users can deploy solutions with confidence that they work as documented.

**Dependencies:** Phase 6 (solutions audit complete)

**Requirements:** SOL-04

**Success Criteria:**
1. Each solution validated through functional testing in representative environment
2. Installation and configuration procedures verified to work as documented
3. Test results documented with any corrections applied to documentation
4. Known limitations or environment-specific issues documented in solution README files

---

## Phase 8: Monitoring Systems Review

**Goal:** Users benefit from simplified, effective monitoring that shows WHAT changed in Microsoft documentation and regulations.

**Dependencies:** None (can run in parallel)

**Requirements:** MON-01, MON-02, MON-03, MON-04, MON-05

**Success Criteria:**
1. Learn Monitor implementation reviewed with simplification opportunities identified
2. Regulatory Monitor implementation assessed for effectiveness with improvement recommendations
3. Change visibility enhanced to show specific content changes, not just detection flags
4. Monitoring architecture documented with maintenance procedures and troubleshooting guidance
5. Alternative approaches evaluated with decision rationale documented

---

## Progress

| Phase | Requirements | Status | Progress |
|-------|--------------|--------|----------|
| 1 - Critical Technical Remediation | 3 | ✓ Complete | ██████████ 100% |
| 2 - Documentation Audit Foundation | 5 | ✓ Complete | ██████████ 100% |
| 3 - Agent 365 Strategic Architecture | 2 | ✓ Complete | ██████████ 100% |
| 4 - Feature Enhancement Updates | 5 | ✓ Complete | ██████████ 100% |
| 5 - Regulatory Validation | 5 | Planned | ░░░░░░░░░░ 0% |
| 6 - Solutions Audit | 9 | Pending | ░░░░░░░░░░ 0% |
| 7 - Solutions Functional Testing | 1 | Pending | ░░░░░░░░░░ 0% |
| 8 - Monitoring Systems Review | 5 | Pending | ░░░░░░░░░░ 0% |

**Total:** 33/33 requirements mapped (100% coverage)

---

## Coverage Validation

All 33 v1 requirements mapped to phases:

**Phase 1 (3 requirements):**
- TECH-01: February 2026 pipeline deadline
- TECH-02: API deprecation warnings
- TECH-08: x-api-key deprecation in playbooks

**Phase 2 (5 requirements):**
- AUDIT-01: Verify all 62 controls
- AUDIT-02: Check formatting consistency
- AUDIT-03: Validate regulatory citations
- AUDIT-04: Review section ordering
- AUDIT-05: Cross-reference Microsoft Learn

**Phase 3 (2 requirements):**
- FEAT-01: Document Agent 365 architecture
- FEAT-02: Document Entra Agent ID

**Phase 4 (5 requirements):**
- FEAT-03: Update Control 1.5 virtual connectors
- FEAT-04: Update Control 1.6 DSPM
- FEAT-05: Update Control 3.8 AI feature access
- FEAT-06: Verify Defender capabilities
- FEAT-07: Update role catalog

**Phase 5 (5 requirements):**
- REG-01: Verify regulation mappings
- REG-02: Check regulatory updates
- REG-03: Validate retention periods
- REG-04: Add FINRA 2026 Report
- REG-05: Review state AI laws

**Phase 6 (9 requirements):**
- SOL-01: Audit all 13 solutions
- SOL-02: Ensure solution-documentation alignment
- SOL-03: Mark incomplete solutions
- SOL-05: Document dependencies
- TECH-03: PAYG licensing clarification
- TECH-04: Service Principal bypass risk
- TECH-05: DLP enforcement mode confusion
- TECH-06: Defender two-portal configuration
- TECH-07: Information Barriers limitation

**Phase 7 (1 requirement):**
- SOL-04: Validate solutions work

**Phase 8 (5 requirements):**
- MON-01: Review Learn Monitor
- MON-02: Review Regulatory Monitor
- MON-03: Assess monitoring approach
- MON-04: Improve change visibility
- MON-05: Document monitoring architecture

**Orphans:** None (100% coverage achieved)

---

## Notes

**Phase ordering rationale:**
- Phase 1 addresses February 2026 compliance deadline (time-sensitive)
- Phase 2 establishes documentation accuracy foundation for all other work
- Phase 3 documents strategic architecture before feature details
- Phase 4 adds feature enhancements after strategic context is clear
- Phase 5 validates regulations after documentation accuracy is confirmed
- Phase 6-7 audit and test solutions after documentation is accurate
- Phase 8 runs in parallel optimizing monitoring systems

**Research integration:**
- Phase 3 implements Milestone 1 from research (Agent 365 Foundation)
- Phase 4 implements Milestone 2 from research (Enhance Existing Controls)
- SharePoint Restricted Search (Milestone 3) deferred to v2 (not yet released)

**Depth calibration:**
- Comprehensive depth (8 phases) reflects natural requirement clustering
- Each phase delivers coherent, verifiable capability
- No artificial splits or padding applied

---

*Roadmap version: 1.3*
*Last updated: 2026-02-03*
