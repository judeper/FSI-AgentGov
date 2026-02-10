# Phase 4: Evidence Export & Framework Integration - AAM Research

**Researched:** 2025-07-17
**Domain:** PowerShell JSON evidence export, SHA-256 integrity hashing, Control 3.8 integration
**Confidence:** HIGH
**Solution:** Agent Access Governance Monitor (v6)

## Summary

Phase 4 for the Agent Access Governance Monitor requires implementing compliance evidence export with SHA-256 integrity hashing, integrating the solution into Control 3.8 and solutions-index.md, and completing the documentation suite (SCHEMA.md, EVIDENCE_EXPORT.md, TROUBLESHOOTING.md). This follows the proven pattern from ACV (v4) and SSC (v5) Phase 4 implementations.

**Primary recommendation:** Reuse established evidence export patterns from ACV/SSC with AAM-specific adaptations for Dataverse table names and Control 3.8 integration.

---

## Existing Patterns (ACV/SSC Reference)

Phase 4 has been executed twice before with identical architecture:

| Component | ACV (v4) | SSC (v5) | AAM (v6 — this) |
|-----------|----------|----------|------------------|
| Export script | Export-AuditValidationEvidence.ps1 | Export-SessionSecurityEvidence.ps1 | Export-AgentAccessEvidence.ps1 |
| Query helper | Get-ValidationResults.ps1 | Get-SSCValidationResults.ps1 | Get-AAMValidationResults.ps1 |
| Hash verifier | Test-EvidenceIntegrity.ps1 | Test-EvidenceIntegrity.ps1 | Test-EvidenceIntegrity.ps1 |
| Target control | Control 1.7 | Control 1.23 | Control 3.8 |
| Validation history table | fsi_auditvalidationhistories | fsi_ValidationHistory | fsi_accessvalidationhistory |
| Violations table | (inline in history) | fsi_DriftViolation | fsi_accessviolations |
| Baselines table | N/A | fsi_SessionBaseline | fsi_accessbaselines |

### Key Differences for AAM

1. **Two export sources**: Both `fsi_accessvalidationhistory` (summary records) and `fsi_accessviolations` (per-environment violations) should be exportable
2. **Zone-centric filtering**: Export by zone (1/2/3) in addition to date range and RunId
3. **Baseline export**: Option to include active baselines in evidence package for comparison
4. **No scope parameter**: AAM doesn't distinguish Tenant vs Environment scope — all validations are environment-level
5. **Control 3.8 has NO existing tip admonitions**: This will be the first solution callout

---

## AAM Dataverse Schema (Relevant Tables)

### fsi_accessvalidationhistory
| Column | Type | Purpose |
|--------|------|---------|
| fsi_name | String | Status-timestamp display name |
| fsi_run_id | String | GUID correlating scan records |
| fsi_validation_time | DateTime | UTC scan timestamp |
| fsi_total_environments | Integer | Environments scanned |
| fsi_compliant_count | Integer | Environments passing |
| fsi_violation_count | Integer | Environments with violations |
| fsi_overall_status | String | Computed worst status |
| fsi_summary_json | String | Full validation JSON |

### fsi_accessviolations
| Column | Type | Purpose |
|--------|------|---------|
| fsi_name | String | Zone-ViolationType-date |
| fsi_environment_guid | String | Environment identifier |
| fsi_environment_name | String | Display name |
| fsi_zone | Integer | Zone classification |
| fsi_violation_type | String | Setting that was violated |
| fsi_expected_value | String | Zone-required value |
| fsi_actual_value | String | Current value |
| fsi_severity | String | Critical/High/Warning/Info |
| fsi_regulatory_context | String | FINRA/SOX reference |
| fsi_detected_at | DateTime | Detection timestamp |
| fsi_run_id | String | Correlating run ID |

### fsi_accessbaselines
| Column | Type | Purpose |
|--------|------|---------|
| fsi_environment_guid | String | Environment identifier |
| fsi_environment_name | String | Display name |
| fsi_zone | Integer | Zone classification |
| fsi_bot_limit_sharing_mode | String | Sharing mode setting |
| fsi_bot_authoring_sharing_disabled | Boolean | Authoring restriction |
| fsi_bot_published_limit_sharing_mode | String | Published bot sharing |
| fsi_captured_by | String | Operator identity |
| fsi_captured_at | DateTime | Capture timestamp |
| fsi_is_active | Boolean | Active baseline flag |

---

## AAMClient.psm1 Existing Functions

The module already exports 8 functions:

| Function | Relevance to Phase 4 |
|----------|----------------------|
| Connect-AAMDataverse | Required — establishes Dataverse connection |
| Get-AAMConnection | Useful — verify connection state |
| Get-AAMEnvironmentVariable | Not needed for evidence export |
| Get-AAMActiveBaseline | Useful — include baselines in evidence |
| Write-AAMValidationHistory | Not needed (write path) |
| Write-AAMViolation | Not needed (write path) |
| Save-AAMBaseline | Not needed (write path) |
| Get-AAMLastValidation | Partial — queries validation history but only top N, no date/zone filter |

**Gap:** Get-AAMLastValidation is too limited for evidence export. A dedicated Get-AAMValidationResults.ps1 helper is needed with:
- Date range filtering (FromDate/ToDate)
- Zone filtering
- RunId filtering
- Pagination for large result sets
- Violation record inclusion

---

## Evidence Export JSON Schema

```json
{
  "metadata": {
    "exportedAt": "ISO8601",
    "solution": "Agent Access Governance Monitor",
    "solutionVersion": "1.0.0",
    "fromDate": "ISO8601",
    "toDate": "ISO8601",
    "runId": "GUID or null",
    "zoneFilter": "All|1|2|3",
    "exportVersion": "1.0.0",
    "recordCount": 0,
    "violationCount": 0,
    "organizationUrl": "https://org.crm.dynamics.com"
  },
  "summary": {
    "overallStatus": "Compliant|Violations|Error",
    "totalScans": 0,
    "scansCompliant": 0,
    "scansWithViolations": 0,
    "totalViolations": 0,
    "criticalViolations": 0,
    "highViolations": 0,
    "warningViolations": 0
  },
  "validations": [],
  "violations": [],
  "baselines": []
}
```

---

## Control 3.8 Integration

Control 3.8 (Copilot Hub and Governance Dashboard) currently has:
- No tip admonitions for deployable solutions
- Related Controls section before Implementation Playbooks (line ~292)
- Implementation Playbooks info admonition (line ~296)

The tip admonition should be placed **between Related Controls and Implementation Playbooks** sections, following the pattern used in Control 1.7 and Control 1.23.

---

## Solutions-Index.md Integration

Current pattern (from SSC entry):
1. Table row in Available Solutions table with version, status, description, related controls
2. Solution Details section (`### Agent Access Governance Monitor`) with Components, Regulatory Alignment, Related Control, Repository Link
3. Version History table entry

---

## Documentation Suite

README.md Solution Components tree already references these files:
- `docs/PREREQUISITES.md` — EXISTS (63 lines)
- `docs/SCHEMA.md` — MISSING (needs creation)
- `docs/EVIDENCE_EXPORT.md` — MISSING (needs creation)
- `docs/TROUBLESHOOTING.md` — MISSING (needs creation)
- `docs/FLOW_SETUP.md` — EXISTS (from Phase 3)

---

## Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| OData query differences from ACV/SSC | Low | Low | AAMClient.psm1 patterns are well-established |
| Control 3.8 preview status | Low | Low | Tip admonition is solution-independent |
| Documentation inconsistency | Low | Medium | Follow exact SSC documentation patterns |

---

## Recommendations

1. **Test-EvidenceIntegrity.ps1**: Nearly identical across ACV/SSC — same script works for AAM
2. **Evidence export**: Include violations AND baselines in export (AAM-specific enhancement over ACV which only had validation history)
3. **Control 3.8 tip**: Place after Related Controls, before Implementation Playbooks
4. **Three plans, two waves**: Plans 01 (scripts) and 02 (framework integration) are independent → Wave 1. Plan 03 (documentation) depends on Plan 01 → Wave 2.

---
*Research completed: 2025-07-17*
*Confidence: HIGH — third iteration of proven Phase 4 pattern*
