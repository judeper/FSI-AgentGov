# Requirements: Deny Event Correlation Report (v10)

**Defined:** 2026-02-10
**Core Value:** Documentation and solutions that US FSI customers trust.

## v10 Requirements

Complete the Deny Event Correlation Report solution from WIP (v1.1.0) to production-ready (v2.0.0). The existing solution has basic extraction scripts and KQL queries but outputs to CSV/blob storage with deprecated x-api-key authentication. The v2.0.0 upgrade adds Entra ID authentication (replacing x-api-key before March 31, 2026 deadline), Dataverse persistence for deny event records and correlation results, Power Automate daily orchestration, Teams alerting for high-severity deny patterns, zone-based analysis, SHA-256 evidence export, and Compliance Dashboard integration via v9 infrastructure.

**Goal:** Transform DEC from a standalone CSV-export pipeline into a fully integrated governance solution with persistent state, automated orchestration, compliance evidence, and dashboard visibility — matching the production quality of v4-v8 Tier 2 solutions.

### Authentication & Script Modernization (AUTH)

- [ ] **AUTH-01**: Migrate `Export-RaiTelemetry.ps1` from deprecated x-api-key to Entra ID (bearer token) authentication using `Connect-AzAccount` + `Get-AzAccessToken` before the March 31, 2026 deadline
- [ ] **AUTH-02**: Create `DECClient.psm1` shared module with Entra ID authentication helpers, connection management, and reusable extraction functions for all three data sources (Purview Audit, DLP, App Insights)
- [ ] **AUTH-03**: Update all extraction scripts to use `#Requires` statements and consistent credential handling via Azure Key Vault (matching v4-v8 security patterns)

### Dataverse Infrastructure (DVS)

- [ ] **DVS-01**: Design and document Dataverse schema with tables for deny event records (`fsi_denyevent`), daily correlation summaries (`fsi_denycorrelation`), and alert history (`fsi_denyalert`), reusing ACV option sets (`fsi_acv_zone`, `fsi_acv_severity`)
- [ ] **DVS-02**: Implement deny event ingestion — extraction scripts write normalized deny events to `fsi_denyevent` with source type, agent ID, deny reason, zone, severity, and timestamp
- [ ] **DVS-03**: Implement correlation logic that groups deny events by agent, zone, and time window, producing daily correlation summaries with event counts, severity distribution, and trend indicators
- [ ] **DVS-04**: Zone-based retention rules: Zone 1 = 90 days, Zone 2 = 365 days, Zone 3 = 730 days (SEC 17a-4 compliance)

### Orchestration & Alerting (ORC)

- [ ] **ORC-01**: Power Automate flow `DEC-DailyOrchestrator` that triggers daily to run all three extraction scripts via Azure Automation, write results to Dataverse, and generate correlation summaries
- [ ] **ORC-02**: Teams adaptive card alerting for high-severity deny patterns: volume anomalies (>2σ from 7-day baseline), new agent deny events (first-time denials), and Zone 3 critical blocks
- [ ] **ORC-03**: Alert severity classification matching cross-solution standard: Critical (Zone 3 jailbreak/XPIA), High (volume anomaly or Zone 2 policy block), Warning (Zone 1 RAI filter), Info (routine DLP match)

### Evidence Export & Dashboard Integration (EVI)

- [ ] **EVI-01**: SHA-256 integrity-hashed evidence export script `Export-DenyEventEvidence.ps1` producing timestamped examination packages with deny events, correlation summaries, and trend analysis
- [ ] **EVI-02**: Evidence package includes regulatory alignment mapping (which deny events satisfy which FINRA/SEC requirements) for examiner self-service
- [ ] **EVI-03**: Register DEC evidence packages with unified evidence export (v9 `Export-UnifiedComplianceEvidence.ps1`) via IntegrationConfig extension
- [ ] **EVI-04**: Extend v9 `IntegrationConfig.psm1` with DEC solution mapping: DEC → Controls 1.5 (Defender), 1.7 (Audit Logging), 3.4 (Deny Event Reporting)
- [ ] **EVI-05**: Extend `Sync-SolutionAssessments.ps1` to query `fsi_denycorrelation` daily summaries and translate to Compliance Dashboard assessment records per mapped control

### Documentation & Framework (DOC)

- [ ] **DOC-01**: Add tip admonitions to Controls 1.5, 1.7, 1.8, and 3.4 referencing the DEC v2.0.0 solution with deployment links
- [ ] **DOC-02**: Update `solutions-index.md` status from "Work In Progress" to "Completed" with v2.0.0 version, updated component list, and regulatory alignment section
- [ ] **DOC-03**: Complete DEC solution documentation suite in FSI-AgentGov-Solutions (README, PREREQUISITES, SCHEMA, EVIDENCE_EXPORT, FLOW_SETUP, TROUBLESHOOTING, CHANGELOG)
- [ ] **DOC-04**: Update framework playbook `docs/playbooks/advanced-implementations/deny-event-correlation-report/index.md` to reflect v2.0.0 architecture with Dataverse persistence and Power Automate orchestration

## Future Requirements

- Real-time deny event streaming via Event Hub for sub-minute detection
- Auto-escalation to compliance officer when deny pattern matches known regulatory scenario
- Cross-solution correlation: deny events + file upload violations + moderation blocks = compound risk score
- Power BI Premium real-time dataset for sub-hourly refresh (currently 8x/day with Pro license)
- Defender CloudAppEvents UPIA/XPIA integration as fourth data source

## Out of Scope

| Feature | Reason |
|---------|--------|
| Auto-remediation | Cannot auto-block agents based on deny patterns without human review |
| Real-time streaming | Daily batch cadence sufficient for governance monitoring |
| New controls | v10 enhances existing controls, not creating new ones |
| Power BI .pbit template | Existing TMDL import path is functional workaround |
| Defender CloudAppEvents source | Optional fourth source; deferred to future enhancement |
| Non-US regulatory mappings | US FSI scope only |

## Traceability

| Requirement | Phase | Status |
|-------------|-------|--------|
| AUTH-01 | Phase 1 | Pending |
| AUTH-02 | Phase 1 | Pending |
| AUTH-03 | Phase 1 | Pending |
| DVS-01 | Phase 2 | Pending |
| DVS-02 | Phase 2 | Pending |
| DVS-03 | Phase 2 | Pending |
| DVS-04 | Phase 2 | Pending |
| ORC-01 | Phase 3 | Pending |
| ORC-02 | Phase 3 | Pending |
| ORC-03 | Phase 3 | Pending |
| EVI-01 | Phase 4 | Pending |
| EVI-02 | Phase 4 | Pending |
| EVI-03 | Phase 4 | Pending |
| EVI-04 | Phase 4 | Pending |
| EVI-05 | Phase 4 | Pending |
| DOC-01 | Phase 5 | Pending |
| DOC-02 | Phase 5 | Pending |
| DOC-03 | Phase 5 | Pending |
| DOC-04 | Phase 5 | Pending |

**Coverage:**
- v10 requirements: 19 total
- Mapped to phases: 19
- Unmapped: 0

---
*Requirements defined: 2026-02-10*
*Previous REQUIREMENTS.md archived with v9 milestone*
