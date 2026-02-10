# Requirements: File Upload Security Configurator (v8)

**Defined:** 2026-02-10
**Core Value:** Documentation and solutions that US FSI customers trust.

## v8 Requirements

Automated validation and enforcement of file upload security settings for Copilot Studio agents per governance zone. The solution detects agents with file upload capabilities enabled beyond their zone's security posture requirements, provides drift detection for configuration changes, and exports compliance evidence with SHA-256 integrity hashing for regulatory examinations.

**Target control:** 1.14 (Data Minimization and Agent Scope Control) — file uploads expand agent data intake beyond declared operational scope.

### File Upload Validation (FUS)

- [ ] **FUS-01**: PowerShell script enumerates all Copilot Studio agents across Power Platform environments and retrieves file upload enabled/disabled status from Dataverse bot table metadata
- [ ] **FUS-02**: Zone classification logic determines expected file upload policy per environment (Zone 1: Allowed, Zone 2: Restricted with approval, Zone 3: Disabled by default)
- [ ] **FUS-03**: Compliance comparison evaluates each agent's file upload status against zone baseline with severity classification (Critical/High/Medium/Warning)
- [ ] **FUS-04**: Orchestrator script combines enumeration, comparison, and reporting in a single execution with dry-run mode, environment filtering, and multiple output formats (Table/Json/Object)
- [ ] **FUS-05**: Content moderation cross-check validates that agents with file uploads enabled have minimum content moderation levels (Zone 2: High, Zone 3: Highest) to protect against malicious file content

### Drift Detection & Alerting (DDA)

- [ ] **DDA-01**: Dataverse tables store file upload baselines, validation results, and violations with organization-owned security for immutable history
- [ ] **DDA-02**: Python deployment scripts create Dataverse schema, environment variables (fsi_FUS_ prefix), and connection references following proven Tier 2 pattern
- [ ] **DDA-03**: PowerShell baseline capture script records current file upload settings per agent as the compliance reference point
- [ ] **DDA-04**: Power Automate daily validation flow orchestrates file upload compliance checks with configurable schedule
- [ ] **DDA-05**: Teams adaptive card alerts notify administrators of file upload policy violations with zone context and remediation guidance
- [ ] **DDA-06**: Azure Automation runbook wrapper enables scheduled unattended validation with credential management

### Compliance & Evidence (CEV)

- [ ] **CEV-01**: Evidence export script generates JSON compliance evidence with SHA-256 integrity hash companion files for SEC 17a-4(f) support
- [ ] **CEV-02**: Control 1.14 updated with tip admonition linking to File Upload Security Configurator solution and solutions-index.md catalog entry added
- [ ] **CEV-03**: Complete documentation suite — README, PREREQUISITES, SCHEMA, EVIDENCE_EXPORT, FLOW_SETUP, TROUBLESHOOTING, CHANGELOG

### Infrastructure (INF)

- [ ] **INF-01**: Solution follows Tier 2 pattern reusing proven helpers (Get-ZoneClassification, Connect-EnvironmentDataverse, Test-ParameterValidation) with FUS-specific client module (FUSClient.psm1)
- [ ] **INF-02**: Dataverse schema reuses existing ACV option sets (fsi_acv_zone, fsi_acv_severity) for consistency across solutions
- [ ] **INF-03**: Test-EvidenceIntegrity.ps1 reused from proven pattern for SHA-256 hash verification

## Future Requirements

- Auto-remediation of non-compliant file upload settings (deferred — requires approval workflow per SOX/FINRA change control)
- File type allowlist enforcement when Copilot Studio exposes per-agent file type configuration API
- Integration with Environment Lifecycle Management for new environment provisioning (deferred to v9)
- Compliance Dashboard feed integration (deferred to v9)

## Out of Scope

| Feature | Reason |
|---------|--------|
| Auto-remediation | Too risky without approval workflow; validation-only meets regulatory requirements |
| Per-agent file type restriction | Copilot Studio does not expose per-agent file type configuration — platform-level only |
| v9 Integration | Separate milestone for cross-solution wiring |
| New controls | Enhance existing Control 1.14, not create new control |

## Traceability

| Requirement | Phase | Status |
|-------------|-------|--------|
| FUS-01 | Phase 1 | Pending |
| FUS-02 | Phase 1 | Pending |
| FUS-03 | Phase 1 | Pending |
| FUS-04 | Phase 1 | Pending |
| FUS-05 | Phase 1 | Pending |
| DDA-01 | Phase 2 | Pending |
| DDA-02 | Phase 2 | Pending |
| DDA-03 | Phase 2 | Pending |
| DDA-04 | Phase 3 | Pending |
| DDA-05 | Phase 3 | Pending |
| DDA-06 | Phase 3 | Pending |
| CEV-01 | Phase 4 | Pending |
| CEV-02 | Phase 4 | Pending |
| CEV-03 | Phase 4 | Pending |
| INF-01 | Phase 1 | Pending |
| INF-02 | Phase 2 | Pending |
| INF-03 | Phase 4 | Pending |

**Coverage:**
- v8 requirements: 17 total
- Mapped to phases: 17
- Unmapped: 0

---
*Requirements defined: 2026-02-10*
*Previous REQUIREMENTS.md archived with v7.1 milestone*
