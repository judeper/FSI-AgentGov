# Phase 4: Evidence Export & Framework Integration - SSC Research

**Researched:** 2026-02-09
**Milestone:** v5 — Session Security Configurator
**Domain:** PowerShell evidence export, SHA-256 integrity hashing, Control 1.23 integration
**Confidence:** HIGH

## Summary

Phase 4 requires implementing compliance evidence export with SHA-256 integrity hashing for session security validation results, integrating the Session Security Configurator into FSI-AgentGov framework documentation (Control 1.23 + solutions-index.md), and creating a complete documentation suite.

The SSC Phase 4 directly adapts the ACV Phase 4 pattern (Export-AuditValidationEvidence.ps1), modified for SSC's fsi_ValidationHistory table and session-security-specific JSON schema.

**Primary recommendation:** Create Export-SessionSecurityEvidence.ps1 following ACV's established pattern, add tip admonition to Control 1.23, and develop comprehensive documentation in session-security-configurator/docs/.

---

## Research Task Results

### 1. SSC Solution Location

**FSI-AgentGov-Solutions repository path:**
```
FSI-AgentGov-Solutions/session-security-configurator/
├── CHANGELOG.md
├── docs/
│   └── FLOW_SETUP.md
├── scripts/
│   ├── Deploy-AuthContexts.ps1
│   ├── Deploy-StepUpPolicies.ps1
│   ├── Test-SessionCompliance.ps1
│   ├── Start-SessionValidationRunbook.ps1
│   ├── Invoke-BaselineCapture.ps1
│   ├── create_dataverse_schema.py
│   ├── create_environment_variables.py
│   ├── create_connection_references.py
│   ├── deploy.py
│   ├── ssc_client.py
│   ├── requirements.txt
│   └── private/
│       ├── Compare-SessionBaseline.ps1
│       ├── Connect-GraphSession.ps1
│       ├── Get-DataverseThreshold.ps1
│       └── Test-BreakGlassExclusion.ps1
├── src/
│   ├── adaptive-card-session-alert.json
│   └── session-validation-flow.json
└── templates/
    ├── auth-contexts/
    ├── session-baselines/
    └── step-up/
```

---

### 2. Phase 1-3 Scripts Analysis

#### Phase 1: PowerShell Core

| Script | Lines | Purpose |
|--------|-------|---------|
| Deploy-AuthContexts.ps1 | 386 | Authentication context deployment (c1-c5) with conflict detection |
| Deploy-StepUpPolicies.ps1 | 686 | Zone-specific CA policy deployment with 72h bake period |
| Test-SessionCompliance.ps1 | 852 | 5-dimension validation orchestrator |
| **Private helpers:** | | |
| Compare-SessionBaseline.ps1 | ~150 | Baseline comparison with minute normalization |
| Connect-GraphSession.ps1 | ~120 | Graph authentication with tenant reuse |
| Test-BreakGlassExclusion.ps1 | ~180 | Break-glass account exclusion validation |

**Phase 1 Total:** ~2,374 lines of PowerShell

#### Phase 2: Dataverse Infrastructure

| Script | Lines | Purpose |
|--------|-------|---------|
| ssc_client.py | ~400 | Dataverse Web API client with MSAL auth |
| create_dataverse_schema.py | ~300 | 3-table schema deployment |
| create_environment_variables.py | ~150 | Zone threshold env vars |
| create_connection_references.py | ~100 | Dataverse/O365/Teams connection refs |
| deploy.py | ~200 | Orchestrator with selective deployment flags |
| requirements.txt | 3 | msal, requests dependencies |
| Get-DataverseThreshold.ps1 | 223 | Dataverse threshold query (Phase 2, Plan 3) |

**Phase 2 Total:** ~1,376 lines (Python + PowerShell)

#### Phase 3: Automation and Alerting

| Script/Artifact | Lines | Purpose |
|-----------------|-------|---------|
| Start-SessionValidationRunbook.ps1 | 351 | Azure Automation runbook wrapper with drift detection |
| Invoke-BaselineCapture.ps1 | 409 | Operator baseline snapshot to Dataverse |
| adaptive-card-session-alert.json | 140 | Teams adaptive card with 12 placeholders |
| session-validation-flow.json | 545 | Power Automate daily validation flow |
| FLOW_SETUP.md | 364 | Flow deployment guide |

**Phase 3 Total:** ~1,809 lines

**Combined Phase 1-3:** ~5,559 lines of scripts and templates

---

### 3. Dataverse Tables Created

| Table | Ownership | Purpose |
|-------|-----------|---------|
| **fsi_SessionBaseline** | UserOwned | Zone-specific session security baselines (SignInFrequencyMinutes, AuthStrength, RequireCompliantDevice, PIM settings) |
| **fsi_ValidationHistory** | OrganizationOwned | Immutable audit log of all validation runs (tamper-proof regulatory requirement) |
| **fsi_DriftViolation** | UserOwned | Threshold violations requiring operator attention (acknowledge workflow) |

**Shared Option Sets (reused from ACV):**
- fsi_acv_zone: Unclassified (0), Zone 1 (100000001), Zone 2 (100000002), Zone 3 (100000003)
- fsi_acv_severity: Passed (1), Warning (2), GracePeriod (3), Failed (4), Error (5)

**SSC-Specific Option Set:**
- fsi_ssc_validationtype: SessionControls, AuthStrength, PIMSettings, BreakGlass, ConflictAudit, Orchestrator

---

### 4. ACV Evidence Export Pattern (v4 Reference)

**Files to adapt:**

| ACV File | Lines | Adaptation for SSC |
|----------|-------|-------------------|
| Export-AuditValidationEvidence.ps1 | 433 | → Export-SessionSecurityEvidence.ps1 |
| private/Get-ValidationResults.ps1 | 216 | → private/Get-SSCValidationResults.ps1 (query fsi_ValidationHistory) |
| Test-EvidenceIntegrity.ps1 | 162 | Reusable as-is (hash verification is generic) |

**Key patterns from ACV:**

```powershell
# 1. JSON serialization with full depth (prevents truncation)
$jsonContent = $evidence | ConvertTo-Json -Depth 10

# 2. SHA-256 hash generation
$hashResult = Get-FileHash -Path $evidenceFilePath -Algorithm SHA256

# 3. Standard companion file format (two spaces)
"$($hashResult.Hash)  $fileName" | Out-File -FilePath $hashFilePath -Encoding utf8

# 4. JSON evidence structure
@{
    metadata = @{
        exportedAt     = (Get-Date).ToUniversalTime().ToString("yyyy-MM-ddTHH:mm:ssZ")
        scope          = "SessionSecurity"
        zone           = $Zone
        fromDate       = $FromDate.ToUniversalTime().ToString("yyyy-MM-ddTHH:mm:ssZ")
        toDate         = $ToDate.ToUniversalTime().ToString("yyyy-MM-ddTHH:mm:ssZ")
        exportVersion  = "1.0.0"
        recordCount    = $results.Count
        organizationUrl = $DataverseUrl
    }
    summary = @{
        overallStatus      = "Passed|Warning|Failed|Error"
        validationsRun     = 5
        validationsPassed  = 4
        validationsFailed  = 1
    }
    validations = @(...)  # Array of validation result objects
}
```

**ACV Dataverse query pattern:**
```powershell
# OData query with pagination handling
$query = "fsi_auditvalidationhistories?`$filter=$filterString&`$orderby=fsi_timestamp desc"
# Handle @odata.nextLink for pagination
while ($result.'@odata.nextLink') { ... }
```

**SSC adaptation notes:**
- Query `fsi_validationhistories` (SSC table) instead of `fsi_auditvalidationhistories` (ACV table)
- Include SSC-specific fields: SessionControls, AuthStrength, PIMSettings, BreakGlass, ConflictAudit
- Map fsi_ssc_validationtype option set values to readable strings
- Include zone-specific thresholds in metadata for context

---

### 5. Control 1.23 Current Structure

**File:** `docs/controls/pillar-1-security/1.23-step-up-authentication-for-agent-operations.md`

**Current structure (key sections):**

```
Line 1-9: Header metadata (Control ID, Pillar, Regulatory Reference, etc.)
Lines 10-17: Objective
Lines 19-26: Why This Matters for FSI
Lines 28-47: Control Description
Lines 49-82: Key Configuration Points (including PIM Integration table)
Lines 84-93: Zone-Specific Requirements table
Lines 95-103: Roles & Responsibilities table
Lines 105-113: Related Controls table
Lines 115-128: Implementation Playbooks section
Lines 130-141: Verification Criteria
Lines 143-151: Additional Resources
Lines 153: Footer metadata
```

**Insertion point for tip admonition:**

Insert after Related Controls section (line 113), before Implementation Playbooks (line 115). This matches the ACV pattern where the "Automated Validation" tip appears after Related Controls.

**Recommended tip format:**

```markdown
!!! tip "Automated Validation: Session Security Configurator"
    For automated deployment, validation, and drift detection of session security controls per governance zone, see the **Session Security Configurator** solution.

    **Capabilities:**

    - Authentication context deployment (c1-c5) with conflict detection
    - Zone-specific CA policy deployment with 72-hour bake period enforcement
    - 5-dimension session security validation (session controls, auth strength, PIM, break-glass, conflict audit)
    - Daily drift detection with Teams adaptive card alerts
    - Compliance evidence export with SHA-256 integrity hashing

    **Deployable Solution:** [session-security-configurator](https://github.com/judeper/FSI-AgentGov-Solutions/tree/main/session-security-configurator) provides PowerShell validation scripts, Dataverse infrastructure, and Power Automate flows.
```

---

### 6. solutions-index.md Entry Format

**Current format pattern (from ACV entry):**

**Table row (line 23 area):**
```markdown
| [Session Security Configurator](#session-security-configurator) | v1.0.0 | Work In Progress | Automated session security validation per governance zone with drift detection and compliance evidence export | 1.23, 1.11 |
```

**Solution Details section:**
```markdown
### Session Security Configurator

Automates Conditional Access session control enforcement per governance zone for Control 1.23. Provides deployment automation, compliance validation, drift detection, and evidence export for FINRA/SEC examination support.

**Components:**
- PowerShell scripts for auth context and CA policy deployment
- 5-dimension validation orchestrator (session controls, auth strength, PIM, break-glass, conflict audit)
- Dataverse tables for session baselines, validation history, and drift violations
- Power Automate daily validation flow with Teams alerting
- Evidence export with SHA-256 integrity hashing

**Regulatory Alignment:**
- GLBA 501(b) (User Identity Verification at Transaction Time)
- FINRA 4511 (Authorized Access to Financial Records)
- SOX 302/404 (Transaction-Level Authentication Controls)
- NIST SP 800-63B (AAL2/AAL3 Authentication Strength)

**Related Controls:**
- [1.23 - Step-Up Authentication](../controls/pillar-1-security/1.23-step-up-authentication-for-agent-operations.md)
- [1.11 - Conditional Access and MFA](../controls/pillar-1-security/1.11-conditional-access-and-phishing-resistant-mfa.md)

**Repository Link:** [session-security-configurator](https://github.com/judeper/FSI-AgentGov-Solutions/tree/main/session-security-configurator)
```

**Version History entry:**
```markdown
| Session Security Configurator | v1.0.0 | February 2026 |
```

---

### 7. Recommended Approach for Each Success Criterion

#### CEV-01: SHA-256 Compliance Evidence Export

**Plan:** Create Export-SessionSecurityEvidence.ps1 adapting ACV pattern

**Tasks:**
1. Create `private/Get-SSCValidationResults.ps1` helper
   - Query `fsi_validationhistories` via Dataverse Web API
   - OData filtering by zone, date range, RunId
   - Pagination handling via @odata.nextLink
   - Map option set values to readable strings

2. Create `Export-SessionSecurityEvidence.ps1` main script
   - Structured JSON with metadata/summary/validations
   - ConvertTo-Json -Depth 10 (prevent truncation)
   - SHA-256 via Get-FileHash
   - Companion .sha256 file with standard format
   - Support both interactive and service principal auth
   - Parameters: DataverseUrl, TenantId, Zone, OutputDirectory, FromDate, ToDate, RunId

3. Copy `Test-EvidenceIntegrity.ps1` from ACV (reusable)

**Estimated effort:** 1 plan, ~600 lines

#### CEV-02: Control 1.23 Framework Integration

**Plan:** Update Control 1.23 and solutions-index.md

**Tasks:**
1. Add tip admonition to Control 1.23
   - Insert after Related Controls section (line 113)
   - 5 capability bullets matching SSC features
   - Deployable Solution link to GitHub repo

2. Add solutions-index.md catalog entry
   - Table row with v1.0.0, Work In Progress status, Controls 1.23/1.11
   - Solution Details section with all required elements
   - Version History entry (February 2026)

**Estimated effort:** 1 plan, documentation-only

#### CEV-03: Documentation Suite

**Plan:** Create comprehensive docs in session-security-configurator/docs/

**Target structure:**
```
session-security-configurator/docs/
├── README-DEPLOYMENT.md (or add to root README.md)
├── PREREQUISITES.md
├── DATAVERSE-SCHEMA.md
├── CONFIGURATION.md
├── TROUBLESHOOTING.md
└── EVIDENCE-EXPORT-GUIDE.md
```

**Required content per document:**

| Document | Content |
|----------|---------|
| PREREQUISITES.md | Licensing (M365 E5, Power Platform), roles (Entra Security Admin, Power Platform Admin), PowerShell modules, Python requirements |
| DATAVERSE-SCHEMA.md | Table definitions, option sets, relationships, sample data |
| CONFIGURATION.md | Environment variables, config.json template, zone thresholds, auth context mapping |
| EVIDENCE-EXPORT-GUIDE.md | Evidence export usage (interactive + SP modes), verification steps, recommended schedule |
| TROUBLESHOOTING.md | Common issues, error codes, remediation steps, support escalation |

**Alternative approach:** Update solution README.md with all sections (matching ACV pattern) rather than separate files.

**Estimated effort:** 1 plan, ~500 lines of documentation

---

## Recommended Phase 4 Plan Structure

Based on ACV Phase 4 pattern (3 plans):

| Plan | Focus | Deliverables |
|------|-------|--------------|
| 04-01 | Evidence export scripts | Export-SessionSecurityEvidence.ps1, Get-SSCValidationResults.ps1, copy Test-EvidenceIntegrity.ps1 |
| 04-02 | Framework integration | Control 1.23 tip admonition, solutions-index.md entry |
| 04-03 | Documentation suite | README updates, deployment guide, evidence export guide |

---

## Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Different Dataverse schema than ACV | Low | Medium | SSC uses fsi_ValidationHistory (singular) vs ACV's fsi_validationhistories — verify table name in create_dataverse_schema.py |
| Option set value differences | Low | Low | Verify option set mappings match between SSC schema and export script |
| Control 1.23 already has solution tip | Medium | Low | Check for existing Conditional Access Automation tip — may need to coordinate placement |

---

## Open Questions

1. **Evidence export scope:** Should export support all zones in single run, or zone-by-zone exports?
   - **Recommendation:** Support -Zone parameter (1, 2, 3, or "All"), default to "All"

2. **Baseline inclusion:** Should evidence export include current baseline settings alongside validation history?
   - **Recommendation:** Yes — include current baseline in metadata for context

3. **Existing CAA tip:** Control 1.23 Related Controls section mentions Conditional Access Automation solution. Does SSC evidence export complement or overlap?
   - **Recommendation:** SSC and CAA are complementary. SSC focuses on session controls; CAA focuses on policy lifecycle. Both can appear in Related Controls.

---

## Sources

### Primary (HIGH confidence)

- ACV Phase 4 Implementation: .planning/phases/04-evidence-export-framework-integration/04-01-SUMMARY.md
- ACV Export Script: FSI-AgentGov-Solutions/audit-configuration-validator/scripts/Export-AuditValidationEvidence.ps1 (433 lines)
- SSC Phase 2 Schema: .planning/phases/02-dataverse-infrastructure/02-01-SUMMARY.md
- SSC Phase 3 Scripts: .planning/phases/03-automation-and-alerting/03-01-SUMMARY.md, 03-02-SUMMARY.md, 03-03-SUMMARY.md
- Control 1.23: docs/controls/pillar-1-security/1.23-step-up-authentication-for-agent-operations.md
- solutions-index.md: docs/reference/solutions-index.md (383 lines with existing patterns)

### Secondary (MEDIUM confidence)

- REQUIREMENTS.md: .planning/REQUIREMENTS.md (CEV-01, CEV-02, CEV-03 definitions)
- ROADMAP.md: .planning/ROADMAP.md (Phase 4 success criteria)

---

## Metadata

**Confidence breakdown:**
- Solution location: HIGH — verified via list_dir
- Script inventory: HIGH — verified via Phase summaries + list_dir
- ACV pattern: HIGH — full script read (433 lines)
- Control 1.23 structure: HIGH — full file read
- solutions-index.md format: HIGH — full file read + pattern analysis

**Research date:** 2026-02-09
**Valid until:** Phase 4 execution
