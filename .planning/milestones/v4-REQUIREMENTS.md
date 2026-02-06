# Requirements Archive: v4 Audit Configuration Validator

**Archived:** 2026-02-06
**Status:** ✅ SHIPPED

This is the archived requirements specification for v4.
For current requirements, see `.planning/REQUIREMENTS.md` (created for next milestone).

---

## v4 Requirements

Requirements for Audit Configuration Validator solution. Each maps to roadmap phases.

### Tenant Audit Validation

- [x] **TVAL-01**: Validator checks M365 Unified Audit Log is enabled via Get-AdminAuditLogConfig ✓
- [x] **TVAL-02**: Validator checks mailbox audit on-by-default status via Get-OrganizationConfig ✓
- [x] **TVAL-03**: Validator checks admin audit log enablement ✓
- [x] **TVAL-04**: Validator uses dual validation strategy (cmdlet + canary event) to avoid false positives ✓

### Environment Audit Validation

- [x] **EVAL-01**: Validator checks per-environment audit enablement via Dataverse Web API ✓
- [x] **EVAL-02**: Validator validates per-environment audit retention period against zone requirements ✓
- [x] **EVAL-03**: Validator applies zone-specific retention rules (Zone 1: 180d, Zone 2: 365d, Zone 3: 730d) ✓
- [x] **EVAL-04**: Validator filters out Trial/Developer environments from validation and alerting ✓
- [x] **EVAL-05**: Validator handles 24-hour audit lag with grace period for recently-enabled environments ✓

### Purview Retention Validation

- [x] **PVAL-01**: Validator checks Purview audit retention policies via Get-UnifiedAuditLogRetentionPolicy ✓
- [x] **PVAL-02**: Validator validates retention periods meet FSI regulatory requirements (minimum 730 days for Zone 3) ✓
- [x] **PVAL-03**: Validator identifies gaps in record type coverage (CopilotInteraction, PowerPlatformAdmin) ✓

### Automation & Alerting

- [x] **AUTO-01**: Daily validation runs via Power Automate scheduled flow ✓
- [x] **AUTO-02**: Configuration drift detection by comparing current state against last known good baseline ✓
- [x] **AUTO-03**: Teams adaptive card alerts for validation failures (Critical/High severity) ✓
- [x] **AUTO-04**: Email alerts to compliance team distribution list for all failures ✓

### Compliance Evidence

- [x] **EVID-01**: Evidence export in JSON format with full validation results ✓
- [x] **EVID-02**: SHA-256 integrity hashing for all exported evidence files ✓
- [x] **EVID-03**: Immutable validation history stored in Dataverse (organization-owned, no update/delete) ✓
- [x] **EVID-04**: Evidence includes timestamp, validation type, overall status, per-environment details ✓

### Solution Infrastructure

- [x] **INFR-01**: Solution follows established Tier 2 pattern (README, CHANGELOG, docs/, scripts/, src/) ✓
- [x] **INFR-02**: Dataverse schema uses fsi_ publisher prefix for all tables and columns ✓
- [x] **INFR-03**: Connection references use fsi_cr_* naming convention ✓
- [x] **INFR-04**: Environment variables use fsi_ACV_* naming convention ✓
- [x] **INFR-05**: PowerShell scripts use #Requires with minimum module versions ✓

### Documentation

- [x] **DOCS-01**: Control 1.7 updated with "Automated Validation" section referencing solution ✓
- [x] **DOCS-02**: Solution added to solutions-index.md with controls covered ✓
- [x] **DOCS-03**: Solution README with prerequisites, quick start, zone requirements ✓
- [x] **DOCS-04**: Deployment guide with step-by-step setup instructions ✓

## Out of Scope

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

| Requirement | Phase | Status |
|-------------|-------|--------|
| TVAL-01 | Phase 1 | Complete |
| TVAL-02 | Phase 1 | Complete |
| TVAL-03 | Phase 1 | Complete |
| TVAL-04 | Phase 1 | Complete |
| EVAL-01 | Phase 2 | Complete |
| EVAL-02 | Phase 2 | Complete |
| EVAL-03 | Phase 2 | Complete |
| EVAL-04 | Phase 2 | Complete |
| EVAL-05 | Phase 2 | Complete |
| PVAL-01 | Phase 1 | Complete |
| PVAL-02 | Phase 1 | Complete |
| PVAL-03 | Phase 1 | Complete |
| AUTO-01 | Phase 3 | Complete |
| AUTO-02 | Phase 3 | Complete |
| AUTO-03 | Phase 3 | Complete |
| AUTO-04 | Phase 3 | Complete |
| EVID-01 | Phase 4 | Complete |
| EVID-02 | Phase 4 | Complete |
| EVID-03 | Phase 2 | Complete |
| EVID-04 | Phase 4 | Complete |
| INFR-01 | Phase 2 | Complete |
| INFR-02 | Phase 2 | Complete |
| INFR-03 | Phase 2 | Complete |
| INFR-04 | Phase 2 | Complete |
| INFR-05 | Phase 1 | Complete |
| DOCS-01 | Phase 4 | Complete |
| DOCS-02 | Phase 4 | Complete |
| DOCS-03 | Phase 4 | Complete |
| DOCS-04 | Phase 4 | Complete |

**Coverage:**
- v4 requirements: 28 total
- Shipped: 28 (100%)
- Adjusted: 0
- Dropped: 0

---

## Milestone Summary

**Shipped:** 28 of 28 requirements
**Adjusted:** None — all requirements delivered as originally specified
**Dropped:** None

---
*Archived: 2026-02-06 as part of v4 milestone completion*
