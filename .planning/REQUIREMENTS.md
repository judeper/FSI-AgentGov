# Requirements: Cross-Solution Integration (v9)

**Defined:** 2026-02-10
**Core Value:** Documentation and solutions that US FSI customers trust.

## v9 Requirements

Cross-solution integration wiring that connects the 5 Tier 2 governance solutions (ACV, SSC, AAM, CMM, FUS) into the Compliance Dashboard for unified compliance visibility, adds ELM provisioning hooks for automatic downstream solution initialization, and provides a unified compliance evidence export for regulatory examinations.

**Goal:** Transition from standalone solutions to an integrated governance platform where environment provisioning cascades to solution initialization, daily validations feed the compliance dashboard, and quarterly evidence rolls up into a single regulatory package.

### Schema Normalization (SCH)

- [ ] **SCH-01**: Document canonical option set contract specifying that `fsi_acv_zone` uses values 1=Zone 1, 2=Zone 2, 3=Zone 3 (matching ELM/CD convention) and `fsi_acv_severity` uses values 1=Passed, 2=Warning, 3=GracePeriod, 4=Failed, 5=Error as the cross-solution standard
- [ ] **SCH-02**: Create solution status mapping reference defining how each Tier 2 solution's `overall_status` translates to Compliance Dashboard `fsi_status` (1=Compliant, 2=Partial, 3=Non-Compliant) with documented logic per solution
- [ ] **SCH-03**: Create shared integration constants module (`IntegrationConfig.psm1`) with canonical mappings, table names, control-to-solution assignments, and evidence type definitions

### Compliance Dashboard Feed (CDF)

- [ ] **CDF-01**: Power Automate flow definition `CD-SolutionFeedCollector` that queries each Tier 2 solution's validation history table daily, maps results to `fsi_controlassessment` records, and upserts compliance scores
- [ ] **CDF-02**: Solution-to-control mapping table documenting which controls each solution feeds (ACV→1.7, SSC→1.23/1.11, AAM→3.8, CMM→1.8, FUS→1.14) with assessment logic per mapping
- [ ] **CDF-03**: PowerShell script `Sync-SolutionAssessments.ps1` that can run standalone or from Azure Automation to pull latest validation results from all Tier 2 solutions and create/update CD assessments
- [ ] **CDF-04**: Evidence auto-registration in `fsi_complianceevidence` when Tier 2 solutions produce SHA-256 evidence packages, with evidence type set to "Test Result" and hash preserved
- [ ] **CDF-05**: Update CD-ScoreCalculator flow to recognize automated assessments (source=solution) vs manual assessments (source=assessor) with appropriate weighting

### ELM Provisioning Hooks (ELM)

- [ ] **ELM-01**: Power Automate child flow `ELM-SolutionInitializer` triggered by ProvisioningCompleted log entry that cascades to downstream solution registration
- [ ] **ELM-02**: ACV environment auto-registration — creates `fsi_environmentregistry` record with zone from ELM request when new environment is provisioned
- [ ] **ELM-03**: Integration configuration specifying which downstream solutions receive provisioning events and what data is passed (environment ID, name, zone, URL, security group)

### Unified Evidence Export (UEV)

- [ ] **UEV-01**: PowerShell script `Export-UnifiedComplianceEvidence.ps1` that orchestrates evidence collection from all Tier 2 solutions and produces a master evidence package with manifest
- [ ] **UEV-02**: Master evidence manifest JSON with solution inventory, per-solution SHA-256 hashes, collection timestamps, and overall compliance summary
- [ ] **UEV-03**: Evidence chain validation script `Test-UnifiedEvidenceIntegrity.ps1` that verifies all solution evidence packages and the master manifest hash chain

### Documentation & Framework (DOC)

- [ ] **DOC-01**: Integration architecture document in framework docs describing cross-solution data flow, feed mechanisms, and evidence aggregation
- [ ] **DOC-02**: Updated solutions-index.md reflecting integration status for all connected solutions with "Dashboard Feed" and "ELM Hook" badges
- [ ] **DOC-03**: Updated Compliance Dashboard README with Tier 2 solution feed documentation, mapping table, and setup instructions
- [ ] **DOC-04**: Complete integration solution documentation suite (README, PREREQUISITES, CONFIGURATION, TROUBLESHOOTING, CHANGELOG) in FSI-AgentGov-Solutions

## Future Requirements

- Real-time event-driven feeds via Dataverse webhooks (currently batch/daily)
- Auto-remediation orchestration across solutions when dashboard score drops below threshold
- Cross-solution correlation analysis (e.g., file upload enabled + low moderation = compound risk)
- Power BI unified cross-solution workbook with drill-through to solution-specific details

## Out of Scope

| Feature | Reason |
|---------|--------|
| Auto-remediation | Too risky without approval workflow; deferred per SOX/FINRA change control |
| Real-time streaming | Batch/daily cadence is sufficient for governance monitoring |
| New controls | v9 wires existing controls, not creating new ones |
| Power BI template | Existing TMDL import path is functional workaround |
| Non-Tier 2 solution feeds | SDM, FINRA, and others can be added in future increments |

## Traceability

| Requirement | Phase | Status |
|-------------|-------|--------|
| SCH-01 | Phase 1 | Pending |
| SCH-02 | Phase 1 | Pending |
| SCH-03 | Phase 1 | Pending |
| CDF-01 | Phase 2 | Pending |
| CDF-02 | Phase 2 | Pending |
| CDF-03 | Phase 2 | Pending |
| CDF-04 | Phase 2 | Pending |
| CDF-05 | Phase 2 | Pending |
| ELM-01 | Phase 3 | Pending |
| ELM-02 | Phase 3 | Pending |
| ELM-03 | Phase 3 | Pending |
| UEV-01 | Phase 4 | Pending |
| UEV-02 | Phase 4 | Pending |
| UEV-03 | Phase 4 | Pending |
| DOC-01 | Phase 5 | Pending |
| DOC-02 | Phase 5 | Pending |
| DOC-03 | Phase 5 | Pending |
| DOC-04 | Phase 5 | Pending |

**Coverage:**
- v9 requirements: 18 total
- Mapped to phases: 18
- Unmapped: 0

---
*Requirements defined: 2026-02-10*
*Previous REQUIREMENTS.md archived with v8 milestone*
