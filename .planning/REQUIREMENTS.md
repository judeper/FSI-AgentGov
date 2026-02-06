# Requirements: FSI-AgentGov v4 — Audit Configuration Validator

**Defined:** 2026-02-06
**Core Value:** Documentation and solutions that US FSI customers trust.

## v4 Requirements

Requirements for Audit Configuration Validator solution. Each maps to roadmap phases.

### Tenant Audit Validation

- [ ] **TVAL-01**: Validator checks M365 Unified Audit Log is enabled via Get-AdminAuditLogConfig
- [ ] **TVAL-02**: Validator checks mailbox audit on-by-default status via Get-OrganizationConfig
- [ ] **TVAL-03**: Validator checks admin audit log enablement
- [ ] **TVAL-04**: Validator uses dual validation strategy (cmdlet + canary event) to avoid false positives

### Environment Audit Validation

- [ ] **EVAL-01**: Validator checks per-environment audit enablement via Dataverse Web API
- [ ] **EVAL-02**: Validator validates per-environment audit retention period against zone requirements
- [ ] **EVAL-03**: Validator applies zone-specific retention rules (Zone 1: 180d, Zone 2: 365d, Zone 3: 730d)
- [ ] **EVAL-04**: Validator filters out Trial/Developer environments from validation and alerting
- [ ] **EVAL-05**: Validator handles 24-hour audit lag with grace period for recently-enabled environments

### Purview Retention Validation

- [ ] **PVAL-01**: Validator checks Purview audit retention policies via Get-UnifiedAuditLogRetentionPolicy
- [ ] **PVAL-02**: Validator validates retention periods meet FSI regulatory requirements (minimum 730 days for Zone 3)
- [ ] **PVAL-03**: Validator identifies gaps in record type coverage (CopilotInteraction, PowerPlatformAdmin)

### Automation & Alerting

- [ ] **AUTO-01**: Daily validation runs via Power Automate scheduled flow
- [ ] **AUTO-02**: Configuration drift detection by comparing current state against last known good baseline
- [ ] **AUTO-03**: Teams adaptive card alerts for validation failures (Critical/High severity)
- [ ] **AUTO-04**: Email alerts to compliance team distribution list for all failures

### Compliance Evidence

- [ ] **EVID-01**: Evidence export in JSON format with full validation results
- [ ] **EVID-02**: SHA-256 integrity hashing for all exported evidence files
- [ ] **EVID-03**: Immutable validation history stored in Dataverse (organization-owned, no update/delete)
- [ ] **EVID-04**: Evidence includes timestamp, validation type, overall status, per-environment details

### Solution Infrastructure

- [ ] **INFR-01**: Solution follows established Tier 2 pattern (README, CHANGELOG, docs/, scripts/, src/)
- [ ] **INFR-02**: Dataverse schema uses fsi_ publisher prefix for all tables and columns
- [ ] **INFR-03**: Connection references use fsi_cr_* naming convention
- [ ] **INFR-04**: Environment variables use fsi_ACV_* naming convention
- [ ] **INFR-05**: PowerShell scripts use #Requires with minimum module versions

### Documentation

- [ ] **DOCS-01**: Control 1.7 updated with "Automated Validation" section referencing solution
- [ ] **DOCS-02**: Solution added to solutions-index.md with controls covered
- [ ] **DOCS-03**: Solution README with prerequisites, quick start, zone requirements
- [ ] **DOCS-04**: Deployment guide with step-by-step setup instructions

## Future Requirements

Deferred to future milestones. Tracked but not in current roadmap.

### Auto-Remediation (v4.1+)

- **RMED-01**: Auto-enable audit logging with Power Automate approval workflow
- **RMED-02**: Exclude Default environment from auto-remediation
- **RMED-03**: Read-before-write for retention policies (preserve existing policies)
- **RMED-04**: Rollback capability for remediation actions

### Advanced Validation (v4.1+)

- **ADVL-01**: SEC 17a-4(f) automatic verification compliance report
- **ADVL-02**: FINRA 2026 compliance evidence format
- **ADVL-03**: Audit event type coverage validation (CopilotInteraction, AgentPublished)
- **ADVL-04**: WORM storage verification for broker-dealers
- **ADVL-05**: Per-agent audit trail validation

### Integration (v9)

- **INTG-01**: ELM post-provisioning audit validation hook
- **INTG-02**: Compliance Dashboard control status feed
- **INTG-03**: Deny Event Correlation prerequisite check

## Out of Scope

Explicitly excluded. Documented to prevent scope creep.

| Feature | Reason |
|---------|--------|
| Audit log content analysis | Deny Event Correlation Report handles this |
| Audit log search interface | Duplicates Purview Audit portal |
| Historical audit log storage | Azure/M365 handles this natively |
| Real-time audit event streaming | SIEM's job (Sentinel integration) |
| User activity monitoring dashboard | Control 3.2 (Usage Analytics) covers this |
| Compliance score calculation | Compliance Dashboard handles this |
| Cross-tenant comparison | High complexity, limited use case |
| Auto-remediation in v4 | Risk without approval workflow; validation-only meets SEC 17a-4(f) |

## Traceability

Which phases cover which requirements. Updated during roadmap creation.

| Requirement | Phase | Status |
|-------------|-------|--------|
| TVAL-01 | TBD | Pending |
| TVAL-02 | TBD | Pending |
| TVAL-03 | TBD | Pending |
| TVAL-04 | TBD | Pending |
| EVAL-01 | TBD | Pending |
| EVAL-02 | TBD | Pending |
| EVAL-03 | TBD | Pending |
| EVAL-04 | TBD | Pending |
| EVAL-05 | TBD | Pending |
| PVAL-01 | TBD | Pending |
| PVAL-02 | TBD | Pending |
| PVAL-03 | TBD | Pending |
| AUTO-01 | TBD | Pending |
| AUTO-02 | TBD | Pending |
| AUTO-03 | TBD | Pending |
| AUTO-04 | TBD | Pending |
| EVID-01 | TBD | Pending |
| EVID-02 | TBD | Pending |
| EVID-03 | TBD | Pending |
| EVID-04 | TBD | Pending |
| INFR-01 | TBD | Pending |
| INFR-02 | TBD | Pending |
| INFR-03 | TBD | Pending |
| INFR-04 | TBD | Pending |
| INFR-05 | TBD | Pending |
| DOCS-01 | TBD | Pending |
| DOCS-02 | TBD | Pending |
| DOCS-03 | TBD | Pending |
| DOCS-04 | TBD | Pending |

**Coverage:**
- v4 requirements: 28 total
- Mapped to phases: 0
- Unmapped: 28 (pending roadmap creation)

---
*Requirements defined: 2026-02-06*
*Last updated: 2026-02-06 after initial definition*
