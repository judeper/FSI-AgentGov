# Requirements: Conditional Access Automation (v10)

**Defined:** 2026-02-10
**Core Value:** Documentation and solutions that US FSI customers trust.

## v10 Requirements

Requirements for the Conditional Access Automation milestone. Enhances existing CA policy deployment scripts with Tier 2 governance infrastructure — Dataverse persistence, Power Automate automation, drift detection, alerting, SHA-256 evidence export, and framework integration for Controls 1.11, 1.23, and 1.18.

**Existing assets (companion repo):** Deploy-CAPolicies.ps1, Register-ServicePrincipal.ps1, Test-PolicyCompliance.ps1, 8 zone-specific policy templates, 5 documentation files. Status: Validated.

### Script Modernization & Core (SMC)

- [ ] **SMC-01**: CAA PowerShell module structure following Tier 2 conventions (`#Requires`, `ErrorAction`, help comments, CAAClient module pattern matching ACV/SSC/AAM)
- [ ] **SMC-02**: Validate and update 8 CA policy templates against current Graph API Conditional Access policy schema (`/policies/conditionalAccessPolicies`)
- [ ] **SMC-03**: Zone lookup integration with ELM Dataverse table or naming convention fallback for zone-appropriate policy deployment
- [ ] **SMC-04**: Dry-run mode for all deployment and compliance operations with preview output showing what would change
- [ ] **SMC-05**: Policy drift detection comparing currently deployed CA policies against template baselines (enabled→disabled, conditions changed, controls weakened)

### Dataverse Infrastructure (INF)

- [ ] **INF-01**: Dataverse tables for CA policy baselines, validation history (immutable), and policy violations reusing `fsi_acv_zone` and `fsi_acv_severity` option sets
- [ ] **INF-02**: Environment variables for zone-specific CA policy configuration (`fsi_CAA_*` prefix) including MFA strength, device compliance, session lifetime thresholds
- [ ] **INF-03**: Connection references for Dataverse, Office 365, Teams, and Microsoft Graph (`fsi_cr_*` naming convention)
- [ ] **INF-04**: Python deployment scripts (idempotent, dry-run support) following ACV/SSC/AAM pattern with schema deployment, environment variables, and connection references

### Automation & Alerting (AUT)

- [ ] **AUT-01**: Power Automate daily compliance scan flow executing Test-PolicyCompliance logic against all tracked environments per zone
- [ ] **AUT-02**: Drift detection identifying unauthorized CA policy modifications outside automation (policy disabled, conditions weakened, grant controls changed)
- [ ] **AUT-03**: Teams adaptive card alerts with severity classification (Zone 3 CRITICAL, Zone 2 HIGH, Zone 1 WARNING) and violation details
- [ ] **AUT-04**: ELM provisioning hook for auto-deploying zone-appropriate CA policies to newly provisioned environments

### Evidence & Framework Integration (EFR)

- [ ] **EFR-01**: SHA-256 integrity-hashed compliance evidence export for CA policy configurations, validation results, and drift detection history
- [ ] **EFR-02**: Control 1.11 framework integration (tip admonition linking to Conditional Access Automation solution with deployment and compliance monitoring guidance)
- [ ] **EFR-03**: solutions-index.md catalog entry update (Work In Progress → Completed) with version, description, related controls (1.11, 1.23, 1.18)
- [ ] **EFR-04**: Documentation suite completion in companion repo (prerequisites, Dataverse schema, deployment guide, troubleshooting, CHANGELOG)
- [ ] **EFR-05**: Compliance Dashboard feed integration for Control 1.11 automated assessment scoring via v9 integration pattern

## Future Requirements

Deferred to post-v10.

### Post-MVP Enhancements

- **SMC-06**: Agentic User / Entra Agent ID CA policy templates for agent identity authentication (preview feature — pending GA)
- **AUT-05**: PIM-triggered CA policy activation for Zone 3 role elevation scenarios
- **AUT-06**: Auto-remediation of drift violations with approval workflow (Zone 1/2 only)
- **EFR-06**: Power BI compliance dashboard for CA policy coverage visualization
- **INF-05**: Multi-tenant support for MSP scenarios with tenant-isolated baselines

## Out of Scope

| Feature | Reason |
|---------|--------|
| Auto-remediation of Zone 3 policies | Too risky for FSI; detect-only meets regulatory requirements |
| Named location management | Separate infrastructure concern; CA Automation focuses on policy lifecycle |
| Legacy authentication management beyond AI apps | Broader tenant security, not agent-specific |
| Real-time policy change detection | Batch/daily cadence sufficient for governance monitoring |
| Non-Microsoft IdP integration | Microsoft-native stack only per project constraints |

## Traceability

| Requirement | Phase | Status |
|-------------|-------|--------|
| SMC-01 | Phase 1 | Pending |
| SMC-02 | Phase 1 | Pending |
| SMC-03 | Phase 1 | Pending |
| SMC-04 | Phase 1 | Pending |
| SMC-05 | Phase 1 | Pending |
| INF-01 | Phase 2 | Pending |
| INF-02 | Phase 2 | Pending |
| INF-03 | Phase 2 | Pending |
| INF-04 | Phase 2 | Pending |
| AUT-01 | Phase 3 | Pending |
| AUT-02 | Phase 3 | Pending |
| AUT-03 | Phase 3 | Pending |
| AUT-04 | Phase 3 | Pending |
| EFR-01 | Phase 4 | Pending |
| EFR-02 | Phase 4 | Pending |
| EFR-03 | Phase 4 | Pending |
| EFR-04 | Phase 4 | Pending |
| EFR-05 | Phase 4 | Pending |

**Coverage:**
- v10 requirements: 18 total
- Mapped to phases: 18
- Unmapped: 0

---
*Requirements defined: 2026-02-10*
*Previous REQUIREMENTS.md archived as v9-REQUIREMENTS.md*
