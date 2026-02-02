# Requirements: FSI-AgentGov Enhancement

**Defined:** 2026-02-02
**Core Value:** Documentation and solutions that US FSI customers trust — every control accurate, every solution working, ongoing maintenance sustainable.

## v1 Requirements

Requirements for this project cycle. Each maps to roadmap phases.

### Documentation Audit

- [ ] **AUDIT-01**: Verify all 62 controls for accuracy against current Microsoft capabilities
- [ ] **AUDIT-02**: Check formatting consistency across all controls (10-section template)
- [ ] **AUDIT-03**: Validate all regulatory citations are accurate and current
- [ ] **AUDIT-04**: Review section ordering and structure for optimal flow
- [ ] **AUDIT-05**: Cross-reference controls with latest Microsoft Learn documentation

### New Feature Documentation

- [ ] **FEAT-01**: Document Microsoft Agent 365 architecture (unified control plane)
- [ ] **FEAT-02**: Document Microsoft Entra Agent ID (agent identity with sponsorship)
- [ ] **FEAT-03**: Update Control 1.5 with virtual connectors for Copilot Studio
- [ ] **FEAT-04**: Update Control 1.6 with enhanced DSPM capabilities
- [ ] **FEAT-05**: Update Control 3.8 with AI feature access control
- [ ] **FEAT-06**: Verify all Defender for Power Platform capabilities documented (including preview)
- [ ] **FEAT-07**: Update role catalog with AI Administrator and Defender XDR Administrator roles

### Solutions Validation

- [ ] **SOL-01**: Audit all 13 solutions in FSI-AgentGov-Solutions for completeness
- [ ] **SOL-02**: Ensure all solutions align with corresponding documentation
- [ ] **SOL-03**: Mark incomplete solutions clearly as WIP with status indicators
- [ ] **SOL-04**: Validate solutions work as documented (functional testing)
- [ ] **SOL-05**: Document solution dependencies and prerequisites

### Monitoring Systems

- [ ] **MON-01**: Review Learn Monitor implementation for simplicity and effectiveness
- [ ] **MON-02**: Review Regulatory Monitor implementation for effectiveness
- [ ] **MON-03**: Assess if monitoring approach is optimal or if better methods exist
- [ ] **MON-04**: Improve change visibility (show WHAT changed, not just THAT something changed)
- [ ] **MON-05**: Document monitoring architecture and maintenance procedures

### Regulatory Coverage

- [ ] **REG-01**: Verify all US FSI regulations are mapped (FINRA, SEC, SOX, GLBA, OCC, Fed, CFTC)
- [ ] **REG-02**: Check for 2025-2026 regulatory updates and incorporate changes
- [ ] **REG-03**: Validate retention period classifications (3-year vs 6-year)
- [ ] **REG-04**: Add FINRA 2026 Report findings to relevant controls
- [ ] **REG-05**: Review state AI laws applicability (Colorado, NYC, Texas)

### Technical Remediation

- [ ] **TECH-01**: Document February 2026 pipeline deadline and licensing implications (CRITICAL)
- [ ] **TECH-02**: Update all API deprecation warnings with dates (EWS, SharePoint Add-Ins, Key Vault, x-api-key)
- [ ] **TECH-03**: Address PAYG vs premium licensing misconceptions in Control 2.1
- [ ] **TECH-04**: Document Service Principal security group bypass risk
- [ ] **TECH-05**: Clarify DLP enforcement mode confusion (Soft-Enabled vs Enabled)
- [ ] **TECH-06**: Update Defender two-portal configuration requirements
- [ ] **TECH-07**: Document Information Barriers channel agent limitation
- [ ] **TECH-08**: Add x-api-key deprecation warning (March 31, 2026) to affected playbooks

## v2 Requirements

Deferred to future release. Tracked but not in current roadmap.

### Architecture Improvements

- **ARCH-01**: Implement breadcrumb navigation enhancement
- **ARCH-02**: Add playbook discoverability with admonition boxes in controls
- **ARCH-03**: Externalize Learn Monitor patterns to YAML configuration
- **ARCH-04**: Implement navigation auto-generation with Awesome Pages plugin
- **ARCH-05**: SQLite state file for Learn Monitor (if performance issues emerge)

### Future Features

- **FUT-01**: Document SharePoint Restricted Search (when released Q2-Q3 2026)
- **FUT-02**: Complete WIP solutions (after audit determines scope)
- **FUT-03**: Automated compliance checks
- **FUT-04**: Cross-repo documentation parity improvements

## Out of Scope

Explicitly excluded. Documented to prevent scope creep.

| Feature | Reason |
|---------|--------|
| Non-US regulations | Framework specifically targets US financial sector |
| Building new solutions from scratch | Focus is audit and completion of existing WIP |
| Real-time monitoring | Batch/scheduled monitoring sufficient for compliance |
| Mobile interface | GitHub Pages is the delivery mechanism |
| Major architecture overhaul | Current 3-layer structure is sound per research |
| Merging repositories | Separation of docs vs code is intentional |

## Traceability

Which phases cover which requirements. Updated during roadmap creation.

| Requirement | Phase | Status |
|-------------|-------|--------|
| AUDIT-01 | TBD | Pending |
| AUDIT-02 | TBD | Pending |
| AUDIT-03 | TBD | Pending |
| AUDIT-04 | TBD | Pending |
| AUDIT-05 | TBD | Pending |
| FEAT-01 | TBD | Pending |
| FEAT-02 | TBD | Pending |
| FEAT-03 | TBD | Pending |
| FEAT-04 | TBD | Pending |
| FEAT-05 | TBD | Pending |
| FEAT-06 | TBD | Pending |
| FEAT-07 | TBD | Pending |
| SOL-01 | TBD | Pending |
| SOL-02 | TBD | Pending |
| SOL-03 | TBD | Pending |
| SOL-04 | TBD | Pending |
| SOL-05 | TBD | Pending |
| MON-01 | TBD | Pending |
| MON-02 | TBD | Pending |
| MON-03 | TBD | Pending |
| MON-04 | TBD | Pending |
| MON-05 | TBD | Pending |
| REG-01 | TBD | Pending |
| REG-02 | TBD | Pending |
| REG-03 | TBD | Pending |
| REG-04 | TBD | Pending |
| REG-05 | TBD | Pending |
| TECH-01 | TBD | Pending |
| TECH-02 | TBD | Pending |
| TECH-03 | TBD | Pending |
| TECH-04 | TBD | Pending |
| TECH-05 | TBD | Pending |
| TECH-06 | TBD | Pending |
| TECH-07 | TBD | Pending |
| TECH-08 | TBD | Pending |

**Coverage:**
- v1 requirements: 33 total
- Mapped to phases: 0
- Unmapped: 33 ⚠️

---
*Requirements defined: 2026-02-02*
*Last updated: 2026-02-02 after initial definition*
