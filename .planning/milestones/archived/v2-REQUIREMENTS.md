# Requirements Archive: v1 + v2 Tech Debt, Architecture & Solution Completion

**Archived:** 2026-02-05
**Status:** SHIPPED

This is the archived requirements specification combining v1 and v2 milestones.
For current requirements, see `.planning/REQUIREMENTS.md` (created for next milestone).

---

# Requirements: FSI-AgentGov Enhancement

**Defined:** 2026-02-02
**Core Value:** Documentation and solutions that US FSI customers trust — every control accurate, every solution working, ongoing maintenance sustainable.

## v1 Requirements

Requirements for this project cycle. Each maps to roadmap phases.

### Documentation Audit

- [x] **AUDIT-01**: Verify all 62 controls for accuracy against current Microsoft capabilities
- [x] **AUDIT-02**: Check formatting consistency across all controls (10-section template)
- [x] **AUDIT-03**: Validate all regulatory citations are accurate and current
- [x] **AUDIT-04**: Review section ordering and structure for optimal flow
- [x] **AUDIT-05**: Cross-reference controls with latest Microsoft Learn documentation

### New Feature Documentation

- [x] **FEAT-01**: Document Microsoft Agent 365 architecture (unified control plane)
- [x] **FEAT-02**: Document Microsoft Entra Agent ID (agent identity with sponsorship)
- [x] **FEAT-03**: Update Control 1.5 with virtual connectors for Copilot Studio
- [x] **FEAT-04**: Update Control 1.6 with enhanced DSPM capabilities
- [x] **FEAT-05**: Update Control 3.8 with AI feature access control
- [x] **FEAT-06**: Verify all Defender for Power Platform capabilities documented (including preview)
- [x] **FEAT-07**: Update role catalog with AI Administrator and Defender XDR Administrator roles

### Solutions Validation

- [x] **SOL-01**: Audit all 13 solutions in FSI-AgentGov-Solutions for completeness
- [x] **SOL-02**: Ensure all solutions align with corresponding documentation
- [x] **SOL-03**: Mark incomplete solutions clearly as WIP with status indicators
- [x] **SOL-04**: Validate solutions work as documented (functional testing)
- [x] **SOL-05**: Document solution dependencies and prerequisites

### Monitoring Systems

- [x] **MON-01**: Review Learn Monitor implementation for simplicity and effectiveness
- [x] **MON-02**: Review Regulatory Monitor implementation for effectiveness
- [x] **MON-03**: Assess if monitoring approach is optimal or if better methods exist
- [x] **MON-04**: Improve change visibility (show WHAT changed, not just THAT something changed)
- [x] **MON-05**: Document monitoring architecture and maintenance procedures

### Regulatory Coverage

- [x] **REG-01**: Verify all US FSI regulations are mapped (FINRA, SEC, SOX, GLBA, OCC, Fed, CFTC)
- [x] **REG-02**: Check for 2025-2026 regulatory updates and incorporate changes
- [x] **REG-03**: Validate retention period classifications (3-year vs 6-year)
- [x] **REG-04**: Add FINRA 2026 Report findings to relevant controls
- [x] **REG-05**: Review state AI laws applicability (Colorado, NYC, Texas)

### Technical Remediation

- [x] **TECH-01**: Document February 2026 pipeline deadline and licensing implications (CRITICAL)
- [x] **TECH-02**: Update all API deprecation warnings with dates (EWS, SharePoint Add-Ins, Key Vault, x-api-key)
- [x] **TECH-03**: Address PAYG vs premium licensing misconceptions in Control 2.1
- [x] **TECH-04**: Document Service Principal security group bypass risk
- [x] **TECH-05**: Clarify DLP enforcement mode confusion (Soft-Enabled vs Enabled)
- [x] **TECH-06**: Update Defender two-portal configuration requirements
- [x] **TECH-07**: Document Information Barriers channel agent limitation
- [x] **TECH-08**: Add x-api-key deprecation warning (March 31, 2026) to affected playbooks

## v2 Requirements

Active requirements for v2 milestone: Tech Debt, Architecture & Solution Completion.

### Tech Debt Resolution

- [x] **DEBT-01**: Fix Register-ServicePrincipal.ps1 secret exposure — replace `ConvertTo-SecureString -AsPlainText -Force` with SecretManagement module pattern (CRITICAL)
- [x] **DEBT-02**: Add error handling to Test-PolicyCompliance.ps1 — wrap unprotected code paths in try/catch with structured error logging (HIGH)
- [x] **DEBT-03**: Add `#Requires` statements to 11 PowerShell scripts missing module dependency declarations (MEDIUM)
- [x] **DEBT-04**: Remove unused dependencies in ELM and FINRA `requirements.txt` files (MEDIUM)

### Architecture Improvements

- [x] **ARCH-01**: Enable breadcrumb navigation (`navigation.path`) in MkDocs Material
- [x] **ARCH-02**: Add playbook discoverability with INFO admonition boxes linking to 4 playbooks per control
- [x] **ARCH-03**: Externalize Learn Monitor classification patterns to YAML configuration

### Solution Completion

- [x] **SOL-01**: Complete Compliance Dashboard (beta → production) — Power Automate flows, Power BI template, validated sample data
- [x] **SOL-02**: Complete Scope Drift Monitor (WIP → production) — access log aggregation, drift detection engine, alert workflow

### Deferred to v3

- **ARCH-04**: Navigation auto-generation with Awesome Pages plugin — deferred per research (risk of breaking pedagogical structure)
- **ARCH-05**: SQLite state file for Learn Monitor — deferred (JSON sufficient for 209 URLs)
- **FUT-01**: Document SharePoint Restricted Search (when released Q2-Q3 2026)
- **FUT-02**: MCP server for governance framework
- **FUT-03**: Copilot Studio agent for governance Q&A
- **FUT-04**: Complete Planned solutions (RAG Validator, COI Testing, Hallucination Tracker, DR Testing)

## Out of Scope

Explicitly excluded. Documented to prevent scope creep.

| Feature | Reason |
|---------|--------|
| Non-US regulations | Framework specifically targets US financial sector |
| Building entirely new solutions | Focus is completing existing WIP solutions |
| Real-time monitoring | Batch/scheduled monitoring sufficient for compliance |
| Mobile interface | GitHub Pages is the delivery mechanism |
| Major architecture overhaul | Current 3-layer structure is sound per research |
| Merging repositories | Separation of docs vs code is intentional |

## Traceability

### v1 (Complete)

All 33 v1 requirements satisfied. See v1-MILESTONE-AUDIT.md for full verification.

### v2 (Complete)

| Requirement | Phase | Status |
|-------------|-------|--------|
| DEBT-01 | Phase 1 | Complete |
| DEBT-02 | Phase 1 | Complete |
| DEBT-03 | Phase 1 | Complete |
| DEBT-04 | Phase 1 | Complete |
| ARCH-01 | Phase 2 | Complete |
| ARCH-02 | Phase 2 | Complete |
| ARCH-03 | Phase 3 | Complete |
| SOL-01 | Phase 4 | Complete |
| SOL-02 | Phase 5 | Complete |

**Coverage:**
- v2 requirements: 9 total
- Mapped to phases: 9
- Satisfied: 9

---

## Milestone Summary

**Shipped:** 9 of 9 v2 requirements

**Adjusted:** None

**Dropped:** None

---

*Archived: 2026-02-05 as part of v2 milestone completion*
