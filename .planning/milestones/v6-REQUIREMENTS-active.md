# Requirements: Agent Access Governance Monitor (v6) — Active Tracking Copy

**Defined:** 2026-02-09
**Core Value:** Documentation and solutions that US FSI customers trust.
**Note:** This is the active tracking copy with completion status. The companion file `v6-REQUIREMENTS.md` preserves the original baseline with all items pending.

## v6 Requirements

Requirements for the Agent Access Governance Monitor milestone. Automates detection of unrestricted agent access configurations per governance zone for Control 3.8.

### Access Configuration Validation

- [x] **ACV-01**: Query Power Platform environment agent access settings (`bot-limitSharingMode`, `bot-authoringSharingDisabled`, `bot-publishedBotLimitSharingMode`) for all environments
- [x] **ACV-02**: Validate agent access settings against zone-specific requirements with zone lookup via ELM Dataverse or naming convention fallback
- [x] **ACV-03**: Classify violations by severity (Zone 3 CRITICAL, Zone 2 HIGH, Zone 1 INFO) with regulatory impact context
- [x] **ACV-04**: All validation operations support dry-run mode previewing violations before persisting
- [x] **ACV-05**: Query environment groups for group-level agent access rules and correlate with member environments
- [x] **ACV-06**: Exclude sandbox/trial environments and apply 48-hour grace period for newly provisioned environments

### Drift Detection & Alerting

- [ ] **DDA-01**: Detect agent access setting drift (sharing mode changed, authoring sharing enabled, settings weakened)
- [ ] **DDA-02**: Teams adaptive card alerts with severity classification matching zone and violation type
- [ ] **DDA-03**: Dataverse immutable validation history for all scan results and violated environments
- [ ] **DDA-04**: Baseline capture and comparison with environment-level snapshots and active baseline tracking

### Compliance & Evidence

- [ ] **CEV-01**: SHA-256 integrity-hashed compliance evidence export for agent access configuration validation
- [ ] **CEV-02**: Control 3.8 framework integration (tip admonition on control page + solutions-index.md catalog entry)
- [ ] **CEV-03**: Documentation suite (prerequisites, schema, configuration, troubleshooting)

### Infrastructure

- [ ] **INF-01**: Dataverse tables for access baselines, validation history, and violations (reuse ACV option sets)
- [ ] **INF-02**: Environment variables for zone-specific access thresholds (fsi_AAM_* prefix)
- [ ] **INF-03**: Connection references for Dataverse, Office 365, Teams (fsi_cr_* naming)
- [ ] **INF-04**: Power Automate scheduled daily access validation flow
- [ ] **INF-05**: Python deployment scripts (idempotent, dry-run support) following ACV/SSC pattern

## Future Requirements

Deferred to post-v6 or v9 integration milestone.

### Post-MVP Enhancements

- **ACV-07**: M365 Admin Center agent settings validation (manual baseline + drift detection workflow)
- **DDA-05**: Environment group-level alerting aggregation (single alert per group vs per environment)
- **CEV-04**: Multi-tenant support for MSP/hosting scenarios
- **ACV-08**: Auto-remediation opt-in for Zone 1/Zone 2 violations (with approval workflow)
- **DDA-06**: Dashboard integration for aggregated access compliance metrics

## Out of Scope

| Feature | Reason |
|---------|--------|
| Auto-remediation of Zone 3 settings | Too risky for FSI; detect-only meets regulatory requirements |
| M365 Admin agent type API (portal-only) | No Graph API available; manual baseline workaround in CEV-04 |
| SharePoint agent access controls | Different control domain (Pillar 4), separate solution |
| Real-time setting change detection | Batch/scheduled detection sufficient for governance |
| Agent-level permission validation | Covered by Control 1.1 and registry, not access configuration |

## Traceability

| Requirement | Phase | Status |
|-------------|-------|--------|
| ACV-01 | Phase 1 | Complete |
| ACV-02 | Phase 1 | Complete |
| ACV-03 | Phase 1 | Complete |
| ACV-04 | Phase 1 | Complete |
| ACV-05 | Phase 1 | Complete |
| ACV-06 | Phase 1 | Complete |
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
- v6 requirements: 18 total
- Mapped to phases: 18
- Complete: 6

---
*Requirements defined: 2026-02-09*
*Phase 1 complete: 2026-02-09*
