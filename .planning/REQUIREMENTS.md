# Requirements: Content Moderation Governance Monitor (v7)

**Defined:** 2026-02-09
**Core Value:** Documentation and solutions that US FSI customers trust.

## v7 Requirements

Requirements for the Content Moderation Governance Monitor milestone. Automates validation and drift detection of Copilot Studio agent content moderation levels per governance zone for Control 1.8.

### Content Moderation Validation

- [ ] **CMV-01**: Enumerate all Copilot Studio agents across Power Platform environments and retrieve generative AI configuration including content moderation level (Low/Medium/High)
- [ ] **CMV-02**: Validate content moderation levels against zone-specific requirements (Zone 1: Medium minimum, Zone 2: High, Zone 3: High)
- [ ] **CMV-03**: Classify violations by severity (Zone 3 agent with Low = CRITICAL, Zone 3 with Medium = HIGH, Zone 2 with Low = HIGH, Zone 2 with Medium = MEDIUM, Zone 1 with Low = HIGH) with regulatory impact context
- [ ] **CMV-04**: All validation operations support dry-run mode previewing violations before persisting
- [ ] **CMV-05**: Filter agents by status (published/draft) and exclude sandbox/trial environments from validation
- [ ] **CMV-06**: Zone lookup via ELM Dataverse table with naming convention fallback (matching ACV/SSC/AAM pattern)

### Drift Detection & Alerting

- [ ] **DDA-01**: Detect content moderation setting drift (level weakened from baseline — e.g., High to Medium or Low)
- [ ] **DDA-02**: Teams adaptive card alerts with severity classification matching zone and moderation violation type
- [ ] **DDA-03**: Dataverse immutable validation history for all scan results and violated agents
- [ ] **DDA-04**: Baseline capture and comparison with per-agent moderation level snapshots and active baseline tracking

### Compliance & Evidence

- [ ] **CEV-01**: SHA-256 integrity-hashed compliance evidence export for content moderation configuration validation
- [ ] **CEV-02**: Control 1.8 framework integration (tip admonition on control page + solutions-index.md catalog entry)
- [ ] **CEV-03**: Documentation suite (prerequisites, schema, configuration, troubleshooting)

### Infrastructure

- [ ] **INF-01**: Dataverse tables for moderation baselines, validation history, and violations (reuse ACV option sets)
- [ ] **INF-02**: Environment variables for zone-specific moderation thresholds (fsi_CMM_* prefix)
- [ ] **INF-03**: Connection references for Dataverse, Office 365, Teams (fsi_cr_* naming)
- [ ] **INF-04**: Power Automate scheduled daily moderation scan flow
- [ ] **INF-05**: Python deployment scripts (idempotent, dry-run support) following ACV/SSC/AAM pattern

## Future Requirements

Deferred to post-v7 or v9 integration milestone.

### Post-MVP Enhancements

- **CMV-07**: Application Insights RAI telemetry correlation (ContentFiltered events tied to agent moderation level)
- **DDA-05**: Per-agent moderation change history timeline
- **CEV-04**: Multi-tenant support for MSP/hosting scenarios
- **CMV-08**: Content moderation effectiveness scoring (filter trigger rate vs. moderation level)
- **DDA-06**: Dashboard integration for aggregated moderation compliance metrics

## Out of Scope

| Feature | Reason |
|---------|--------|
| Auto-remediation of moderation levels | Too risky for FSI; detect-only meets regulatory requirements |
| Real-time moderation event capture | Batch/scheduled detection sufficient for governance |
| Third-party content safety integration | Separate concern covered by webhook threat detection in Control 1.8 |
| Custom content filter category tuning | Beyond governance scope; Copilot Studio feature management |
| Agent-level Application Insights setup | Covered by existing Control 1.8 documentation; not solution scope |

## Traceability

| Requirement | Phase | Status |
|-------------|-------|--------|
| CMV-01 | Phase 1 | Pending |
| CMV-02 | Phase 1 | Pending |
| CMV-03 | Phase 1 | Pending |
| CMV-04 | Phase 1 | Pending |
| CMV-05 | Phase 1 | Pending |
| CMV-06 | Phase 1 | Pending |
| DDA-01 | Phase 3 | Pending |
| DDA-02 | Phase 3 | Pending |
| DDA-03 | Phase 3 | Pending |
| DDA-04 | Phase 3 | Pending |
| CEV-01 | Phase 4 | Pending |
| CEV-02 | Phase 4 | Pending |
| CEV-03 | Phase 4 | Pending |
| INF-01 | Phase 2 | Pending |
| INF-02 | Phase 2 | Pending |
| INF-03 | Phase 2 | Pending |
| INF-04 | Phase 3 | Pending |
| INF-05 | Phase 2 | Pending |

**Coverage:**
- v7 requirements: 18 total
- Mapped to phases: 18
- Unmapped: 0

---
*Requirements defined: 2026-02-09*
