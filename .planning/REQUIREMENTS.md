# Requirements: Session Security Configurator (v5)

**Defined:** 2026-02-06
**Core Value:** Documentation and solutions that US FSI customers trust.

## v5 Requirements

Requirements for the Session Security Configurator milestone. Automates Conditional Access session control enforcement per governance zone for Control 1.23.

### Session Control Management

- [x] **SCM-01**: Deploy authentication contexts (c1-c5) for step-up operations with conflict detection for pre-existing contexts
- [x] **SCM-02**: Deploy step-up CA policies with zone-specific session controls (Zone 1: 8h, Zone 2: 4h/30min, Zone 3: 1h/15min)
- [x] **SCM-03**: Validate deployed CA policies match zone-specific session requirements with pass/fail/warning status per zone
- [x] **SCM-04**: All deployment operations support dry-run mode previewing changes before applying
- [x] **SCM-05**: Create/validate authentication strength policies (phishing-resistant MFA for Zone 3, passwordless for Zone 2)
- [x] **SCM-06**: Validate PIM settings for AI admin roles match Control 1.23 requirements (activation windows, approval, auth context)
- [x] **SCM-07**: Report-only mode enforcement with minimum 72-hour bake period before enforcement transition

### Drift Detection & Alerting

- [ ] **DDA-01**: Detect session control drift (sign-in frequency weakened, auth strength downgraded, policy disabled, exclusions added)
- [ ] **DDA-02**: Teams adaptive card alerts with severity classification for detected drift
- [ ] **DDA-03**: Dataverse immutable validation history for all drift scan results
- [ ] **DDA-04**: Baseline capture and comparison with zone-parameterized thresholds from environment variables

### Compliance & Evidence

- [ ] **CEV-01**: SHA-256 integrity-hashed compliance evidence export for session security configuration
- [ ] **CEV-02**: Control 1.23 framework integration (tip admonition on control page + solutions-index.md catalog entry)
- [ ] **CEV-03**: Documentation suite (prerequisites, schema, configuration, troubleshooting)

### Infrastructure

- [ ] **INF-01**: Dataverse tables for session baselines, validation history, and drift violations (reuse ACV option sets)
- [ ] **INF-02**: Environment variables for zone-specific session thresholds (fsi_SSC_* prefix)
- [ ] **INF-03**: Connection references for Dataverse, Office 365, Teams (fsi_cr_* naming)
- [ ] **INF-04**: Power Automate scheduled daily drift scan flow
- [ ] **INF-05**: Python deployment scripts (idempotent, dry-run support) following ACV pattern

## Future Requirements

Deferred to post-v5 or v9 integration milestone.

### Post-MVP Enhancements

- **SCM-08**: Authentication context-to-operation mapping validation (verify step-ups actually trigger in production)
- **DDA-05**: Step-up session activity dashboard data (metrics for Power BI/Compliance Dashboard)
- **CEV-04**: Continuous Access Evaluation (CAE) configuration validation
- **CEV-05**: Token protection validation for Zone 3 sessions
- **DDA-06**: Auto-remediation opt-in for Zone 1/Zone 2 drift (with approval workflow)

## Out of Scope

| Feature | Reason |
|---------|--------|
| General CA policy deployment engine | Conditional Access Automation solution handles policy lifecycle |
| Auto-remediation of Zone 3 policies | Too risky for FSI; detect-only meets regulatory requirements |
| MFA method registration management | IAM operational concern, outside session configuration scope |
| Application-level auth context integration | Agent development team responsibility, not infrastructure |
| Real-time policy enforcement agent | Microsoft Entra ID enforces CA policies; this solution validates configuration |
| Context-to-operation mapping | Requires production usage data; cannot validate without deployed agents |
| Dashboard activity metrics | Defer to v9 integration milestone with Compliance Dashboard |

## Traceability

| Requirement | Phase | Status |
|-------------|-------|--------|
| SCM-01 | Phase 1 | Complete |
| SCM-02 | Phase 1 | Complete |
| SCM-03 | Phase 1 | Complete |
| SCM-04 | Phase 1 | Complete |
| SCM-05 | Phase 1 | Complete |
| SCM-06 | Phase 1 | Complete |
| SCM-07 | Phase 1 | Complete |
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
- v5 requirements: 19 total
- Mapped to phases: 19
- Unmapped: 0

---
*Requirements defined: 2026-02-06*
*Last updated: 2026-02-07 after Phase 1 execution*
