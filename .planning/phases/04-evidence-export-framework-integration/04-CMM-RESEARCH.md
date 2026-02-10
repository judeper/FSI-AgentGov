# Phase 4: Evidence Export & Framework Integration — CMM Research

**Researched:** 2026-02-10
**Milestone:** v7 — Content Moderation Governance Monitor
**Domain:** PowerShell evidence export, SHA-256 integrity hashing, Control 1.8 integration
**Confidence:** HIGH — fourth iteration of proven Phase 4 pattern (ACV → SSC → AAM → CMM)

## Summary

Phase 4 for the Content Moderation Governance Monitor requires implementing compliance evidence export with SHA-256 integrity hashing, integrating the solution into Control 1.8 and solutions-index.md, and completing the documentation suite (SCHEMA.md, EVIDENCE_EXPORT.md, TROUBLESHOOTING.md — currently stubs). This follows the proven pattern from ACV (v4), SSC (v5), and AAM (v6) Phase 4 implementations.

**Primary recommendation:** Reuse the established evidence export pattern from AAM with CMM-specific adaptations for per-agent Dataverse tables (fsi_moderationbaselines, fsi_moderationvalidationhistory, fsi_moderationviolations) and Control 1.8 integration.

**Key difference from AAM:** Content moderation is configured **per-agent** (not per-environment), so evidence export queries per-agent violation records with agent-level detail (fsi_agent_id, fsi_agent_name, fsi_expected_level, fsi_actual_level) rather than environment-level settings.

---

## 1. Existing CMM Solution File Inventory (Phases 1-3)

### Phase 1: PowerShell Core (Complete — 2026-02-10)

| Plan | File | Lines | Purpose |
|------|------|-------|---------|
| 01-01 | `scripts/private/CMMClient.psm1` | 701 | Dataverse client module (10 exported functions) |
| 01-01 | `scripts/private/Connect-EnvironmentDataverse.ps1` | — | Per-environment Dataverse auth with token caching |
| 01-01 | `scripts/private/Get-ZoneClassification.ps1` | — | ELM → naming convention → Unknown zone lookup |
| 01-01 | `scripts/private/Get-ExpectedModerationLevel.ps1` | — | Zone-to-moderation compliance check with severity |
| 01-01 | `scripts/private/Test-ParameterValidation.ps1` | — | Parameter validators including Test-ModerationLevel |
| 01-01 | `templates/moderation-baseline.json` | — | Zone-to-moderation-level requirements reference |
| 01-02 | `scripts/Get-AgentModerationSettings.ps1` | ~290 | Enumerates agents across environments, extracts moderation levels |
| 01-02 | `scripts/Compare-ModerationCompliance.ps1` | ~170 | Pipeline-enabled compliance comparison with severity |
| 01-03 | `scripts/Test-ContentModerationCompliance.ps1` | 650 | Full orchestrator: query → compare → summarize → persist → output |

### Phase 2: Dataverse Infrastructure (Complete — 2026-02-10)

| Plan | File | Purpose |
|------|------|---------|
| 02-01 | `scripts/cmm_client.py` | CMMClient Python class for Dataverse Web API |
| 02-01 | `scripts/create_dataverse_schema.py` | Three-table schema deployment (518 lines) |
| 02-01 | `scripts/requirements.txt` | Python deps (msal, requests) |
| 02-02 | `scripts/create_environment_variables.py` | 7 `fsi_CMM_*` operational parameters |
| 02-02 | `scripts/create_connection_references.py` | 3 connection references |
| 02-02 | `scripts/deploy.py` | Full deployment orchestrator |

### Phase 3: Automation and Alerting (Complete — 2026-02-10)

| Plan | File | Lines | Purpose |
|------|------|-------|---------|
| 03-01 | `scripts/Start-ModerationValidationRunbook.ps1` | 537 | Azure Automation runbook wrapper (certificate auth, drift detection) |
| 03-01 | `scripts/Invoke-ModerationBaselineCapture.ps1` | 412 | Operator-initiated per-agent baseline capture |
| 03-02 | `src/adaptive-card-moderation-alert.json` | 366 | Teams adaptive card template |
| 03-02 | `src/moderation-validation-flow.json` | — | Power Automate daily validation flow |
| 03-02 | `docs/FLOW_SETUP.md` | 308 | Flow deployment guide |

### Documentation Stubs (Allocated for Phase 4)

| File | Status | Lines |
|------|--------|-------|
| `docs/PREREQUISITES.md` | Populated | ~78 |
| `docs/SCHEMA.md` | Stub | ~22 |
| `docs/EVIDENCE_EXPORT.md` | Stub | ~14 |
| `docs/TROUBLESHOOTING.md` | Stub | ~28 |

### Other Files

| File | Lines | Purpose |
|------|-------|---------|
| `README.md` | ~105 | Solution overview, quick start, zone requirements |
| `CHANGELOG.md` | 84 | v0.1.0 → v0.2.0 → v0.3.0 changelog |
| `flows/.gitkeep` | — | Placeholder for exported flow files |
| `src/dataverse/` | — | Dataverse schema definitions subdirectories |

### Full Directory Tree (Post Phase 3)

```
content-moderation-monitor/
├── CHANGELOG.md
├── README.md
├── docs/
│   ├── EVIDENCE_EXPORT.md          (stub)
│   ├── FLOW_SETUP.md              (populated — Phase 3)
│   ├── PREREQUISITES.md           (populated)
│   ├── SCHEMA.md                  (stub)
│   └── TROUBLESHOOTING.md         (stub)
├── flows/
│   └── .gitkeep
├── scripts/
│   ├── cmm_client.py
│   ├── Compare-ModerationCompliance.ps1
│   ├── create_connection_references.py
│   ├── create_dataverse_schema.py
│   ├── create_environment_variables.py
│   ├── deploy.py
│   ├── Get-AgentModerationSettings.ps1
│   ├── Invoke-ModerationBaselineCapture.ps1
│   ├── requirements.txt
│   ├── Start-ModerationValidationRunbook.ps1
│   ├── Test-ContentModerationCompliance.ps1
│   └── private/
│       ├── CMMClient.psm1
│       ├── Connect-EnvironmentDataverse.ps1
│       ├── Get-ExpectedModerationLevel.ps1
│       ├── Get-ZoneClassification.ps1
│       └── Test-ParameterValidation.ps1
├── src/
│   ├── adaptive-card-moderation-alert.json
│   ├── dataverse/
│   │   ├── connection-references/
│   │   ├── environment-variables/
│   │   └── tables/
│   └── moderation-validation-flow.json
└── templates/
    └── moderation-baseline.json
```

---

## 2. CMM Dataverse Tables and Key Columns

### fsi_moderationbaselines (UserOwned)

EntitySetName: `fsi_moderationbaselines`

| Column | Type | Required | Description |
|--------|------|----------|-------------|
| `fsi_moderationbaselineid` | GUID | PK | Primary key |
| `fsi_name` | String(200) | Yes | Baseline display name (auto: `{AgentName}-{Zone}-{timestamp}`) |
| `fsi_environment_guid` | String(100) | Yes | Power Platform environment GUID |
| `fsi_environment_name` | String(500) | Yes | Environment display name |
| `fsi_zone` | OptionSet | Yes | Zone classification (fsi_acv_zone: 0/1/2/3) |
| `fsi_agent_id` | String(100) | Yes | Copilot Studio bot GUID |
| `fsi_agent_name` | String(500) | Yes | Agent display name |
| `fsi_moderation_level` | String(50) | Yes | Captured level: Low/Medium/High |
| `fsi_is_active` | Boolean | Yes | Current active baseline flag (default: true) |
| `fsi_captured_at` | DateTime | Yes | When baseline was captured |
| `fsi_captured_by` | String(200) | No | UPN of capturing operator |
| `fsi_raw_json` | Memo(100K) | No | Full JSON snapshot of moderation settings |

### fsi_moderationvalidationhistory (OrganizationOwned — Immutable)

EntitySetName: `fsi_moderationvalidationhistory` (explicit, avoids auto-plural)

| Column | Type | Required | Description |
|--------|------|----------|-------------|
| `fsi_moderationvalidationhistoryid` | GUID | PK | Primary key |
| `fsi_name` | String(200) | Yes | Status-timestamp display name |
| `fsi_run_id` | String(36) | Yes | GUID correlating all records in one scan run |
| `fsi_validation_time` | DateTime | Yes | When scan executed (UTC) |
| `fsi_total_agents` | Integer | Yes | Total agents scanned |
| `fsi_compliant_count` | Integer | Yes | Agents passing moderation checks |
| `fsi_violation_count` | Integer | Yes | Agents with violations |
| `fsi_overall_status` | String(50) | Yes | Passed/Failed/Warning/Critical |
| `fsi_environments_scanned` | String(2000) | No | Comma-separated environments covered |
| `fsi_summary_json` | Memo(100K) | No | Full JSON summary blob |

### fsi_moderationviolations (UserOwned)

EntitySetName: `fsi_moderationviolations` (auto-generated)

| Column | Type | Required | Description |
|--------|------|----------|-------------|
| `fsi_moderationviolationid` | GUID | PK | Primary key |
| `fsi_name` | String(200) | Yes | Auto: `{AgentName}-{Zone}-{date}` |
| `fsi_environment_guid` | String(100) | Yes | Power Platform environment GUID |
| `fsi_environment_name` | String(500) | Yes | Environment display name |
| `fsi_agent_id` | String(100) | Yes | Violating agent's bot GUID |
| `fsi_agent_name` | String(500) | Yes | Agent display name |
| `fsi_zone` | OptionSet | Yes | Zone classification (fsi_acv_zone) |
| `fsi_expected_level` | String(50) | Yes | Zone-required moderation level |
| `fsi_actual_level` | String(50) | Yes | Agent's current moderation level |
| `fsi_severity` | OptionSet | Yes | Violation severity (fsi_acv_severity) |
| `fsi_regulatory_context` | String(2000) | No | FINRA/SOX/GLBA regulatory impact context |
| `fsi_detected_at` | DateTime | Yes | When violation was detected (UTC) |
| `fsi_run_id` | String(36) | No | Correlating scan GUID |

### Shared Option Sets (Reused from ACV)

| Option Set | Description | Values |
|------------|-------------|--------|
| `fsi_acv_zone` | Zone classification | 0=Unclassified, 1=Zone 1, 2=Zone 2, 3=Zone 3 |
| `fsi_acv_severity` | Severity levels | 1=Passed, 2=Warning, 3=GracePeriod, 4=Failed, 5=Error |

### Environment Variables (7 fsi_CMM_* variables)

| Variable | Type | Default | Purpose |
|----------|------|---------|---------|
| `fsi_CMM_ScanFrequencyHours` | Integer | 24 | Informational for flow schedule |
| `fsi_CMM_GracePeriodHours` | Integer | 48 | Environment age filter |
| `fsi_CMM_IncludeSandbox` | Boolean | true | Include sandbox environments |
| `fsi_CMM_IncludeDrafts` | Boolean | false | Include draft (unpublished) agents |
| `fsi_CMM_BaselineAgeThresholdDays` | Integer | 90 | Baseline staleness alerting |
| `fsi_CMM_TeamsGroupId` | String | (empty) | Teams channel targeting |
| `fsi_CMM_TeamsChannelId` | String | (empty) | Teams channel targeting |

### Connection References

| Reference | Connector | Purpose |
|-----------|-----------|---------|
| `fsi_cr_dataverse_moderationmonitor` | Dataverse | Validation history writes |
| `fsi_cr_office365_moderationmonitor` | Office 365 | Email alerts |
| `fsi_cr_teams_moderationmonitor` | Teams | Adaptive card posting |

### CMMClient.psm1 Exported Functions (10 total)

| Function | Phase 4 Relevance |
|----------|-------------------|
| `Connect-CMMDataverse` | **Required** — establishes Dataverse connection |
| `Get-CMMConnection` | Useful — verify connection state |
| `Get-CMMEnvironmentVariable` | Not needed for evidence export |
| `Get-ModerationBaseline` | **Required** — include active baselines in evidence (has -ActiveOnly param) |
| `Write-ModerationValidationHistory` | Not needed (write path) |
| `Write-ModerationViolation` | Not needed (write path) |
| `Get-AgentBots` | Not needed for evidence export |
| `Get-BotModerationLevel` | Not needed for evidence export |
| `Save-CMMBaseline` | Not needed (write path) |
| `Get-CMMLastValidation` | Partial — queries history but only top N, no date/zone filter |

**Gap:** `Get-CMMLastValidation` only retrieves top N records without date range, zone, or RunId filtering. A dedicated `Get-CMMValidationResults.ps1` private helper is needed for evidence export.

---

## 3. Proven Evidence Export Pattern (ACV → SSC → AAM)

### Cross-Solution Comparison

| Component | ACV (v4) | SSC (v5) | AAM (v6) | CMM (v7 — this) |
|-----------|----------|----------|----------|------------------|
| Export script | Export-AuditValidationEvidence.ps1 | Export-SessionSecurityEvidence.ps1 | Export-AgentAccessEvidence.ps1 (528 lines) | Export-ContentModerationEvidence.ps1 |
| Query helper | Get-ValidationResults.ps1 | Get-SSCValidationResults.ps1 | Get-AAMValidationResults.ps1 | Get-CMMValidationResults.ps1 |
| Hash verifier | Test-EvidenceIntegrity.ps1 | Test-EvidenceIntegrity.ps1 | Test-EvidenceIntegrity.ps1 (162 lines) | Test-EvidenceIntegrity.ps1 |
| Target control | 1.7 (Audit Logging) | 1.23 (Step-Up Auth) | 3.8 (Copilot Hub) | **1.8 (Runtime Protection)** |
| History table | fsi_auditvalidationhistories | fsi_validationhistories | fsi_accessvalidationhistory | **fsi_moderationvalidationhistory** |
| Violations table | (inline) | fsi_DriftViolation | fsi_accessviolations | **fsi_moderationviolations** |
| Baselines table | N/A | fsi_SessionBaseline | fsi_accessbaselines | **fsi_moderationbaselines** |
| Evidence JSON sections | metadata, summary, validations | metadata, summary, validations | metadata, summary, validations, violations, baselines | metadata, summary, validations, violations, baselines |
| Evidence filename prefix | `acv-evidence-` | `session-security-evidence-` | `aam-evidence-` | `cmm-evidence-` |

### Export Script Architecture (Proven Pattern)

```
Export-{Solution}Evidence.ps1
├── Import-Module CMMClient.psm1
├── Dot-source Get-CMMValidationResults.ps1
├── Authenticate (Interactive or Certificate-based)
├── Connect-CMMDataverse
├── Query validation results (Get-CMMValidationResults)
├── Optional: Query active baselines (Get-ModerationBaseline -ActiveOnly)
├── Build JSON evidence object
│   ├── metadata: exportedAt, solution, solutionVersion, fromDate, toDate, runId, zoneFilter, recordCount, violationCount, organizationUrl
│   ├── summary: overallStatus, totalScans, compliant/violated counts, severity breakdown
│   ├── validations: array of history records
│   ├── violations: array of violation records
│   └── baselines: array of active baseline records (optional)
├── ConvertTo-Json -Depth 10 | Out-File -Encoding utf8
├── Get-FileHash -Algorithm SHA256
├── Write companion .sha256 file: "{hash}  {filename}"
└── Return PSCustomObject summary
```

### Key Code Patterns

```powershell
# SHA-256 generation
$hashResult = Get-FileHash -Path $evidenceFilePath -Algorithm SHA256
"$($hashResult.Hash)  $(Split-Path -Leaf $evidenceFilePath)" | Out-File -FilePath "$evidenceFilePath.sha256" -Encoding utf8

# JSON depth (CRITICAL — prevents nested object truncation)
$jsonContent = $evidence | ConvertTo-Json -Depth 10

# Evidence filename convention
$fileName = "cmm-evidence-$Zone-$(Get-Date -Format 'yyyyMMdd-HHmmss').json"

# OData query with pagination (from AAMClient pattern)
$allRecords = @()
$nextLink = $uri
while ($nextLink) {
    $response = Invoke-RestMethod -Uri $nextLink -Headers $headers -Method Get
    $allRecords += $response.value
    $nextLink = $response.'@odata.nextLink'
}
```

### CMM-Specific Adaptations Required

1. **Per-agent violation detail**: CMM violations include `fsi_agent_id`, `fsi_agent_name`, `fsi_expected_level`, `fsi_actual_level` (vs AAM's `fsi_violation_type`, `fsi_expected_value`, `fsi_actual_value`)
2. **History columns**: CMM uses `fsi_total_agents` (not `fsi_total_environments`), `fsi_environments_scanned`
3. **Zone filtering on violations**: Filter `fsi_moderationviolations` by `fsi_zone` for zone-specific evidence
4. **Agent-level baselines**: Get-ModerationBaseline returns per-agent records (agent_id + agent_name + moderation_level), not per-environment records
5. **Agent filtering**: Consider adding an `-AgentId` parameter for agent-specific evidence export

---

## 4. Control 1.8 Current State

**File:** `docs/controls/pillar-1-security/1.8-runtime-protection-and-external-threat-detection.md` (363 lines)

### Structure Analysis

| Section | Line Range | Notes |
|---------|------------|-------|
| Header metadata | 1-9 | Control ID, Pillar, Regulatory Reference |
| !!! info "Agent 365 Architecture Update" | ~12-14 | Existing info admonition |
| Objective | ~16-18 | One paragraph |
| Why This Matters for FSI | ~21-27 | Regulatory bullet points |
| Control Description | ~30-100 | Comprehensive, includes Defender and threat detection |
| Content Moderation Level Configuration | ~220-240 | Per-agent moderation levels, zone table |
| Key Configuration Points | ~242-255 | Bulleted config items |
| Zone-Specific Requirements | ~258-265 | Zone table |
| Roles & Responsibilities | ~268-275 | Admin roles table |
| Related Controls | ~278-290 | Cross-reference table |
| RAI Telemetry Capture | ~293-340 | App Insights telemetry section |
| Implementation Playbooks | ~342-349 | !!! info admonition with 4 links |
| Verification Criteria | ~352-362 | 11 numbered checks |
| Additional Resources | ~365+ | Microsoft Learn links |
| Footer metadata | ~363 | Version v1.3 |

### Existing Admonitions in Control 1.8

1. `!!! info "Agent 365 Architecture Update"` — after header, before Objective
2. `!!! success "Generally Available - February 2026"` — in Defender integration section
3. `!!! warning "Licensing Consideration"` — after Defender section
4. `!!! info "Additional Threat Detection vs. Native Defender"` — in threat detection section
5. `!!! info "Security Webhooks API vs. Additional Threat Detection"` — in webhooks section
6. `!!! warning "Third-Party Provider Assessment"` — vendor assessment note
7. `!!! warning "FSI Recommendation: Set Content Moderation to High"` — in moderation section
8. `!!! info "Prompt Injection Detection Locations"` — in RAI section
9. `!!! warning "Per-Agent Configuration"` — App Insights per-agent note
10. `!!! info "Step-by-Step Implementation"` — Implementation Playbooks section

**No existing `!!! tip` admonitions for deployable solutions.** This will be the first.

### Tip Admonition Insertion Point

Place the tip admonition **between Related Controls and the RAI Telemetry section** (or alternatively between Related Controls and Implementation Playbooks). The most logical placement is just before the Implementation Playbooks section (after the `---` separator following Verification Criteria, or after Related Controls before RAI Telemetry).

Recommended: After the **Related Controls** section and before the **RAI Telemetry Capture** section (approximately line 290). This follows the AAM pattern where the tip goes between Related Controls and Implementation Playbooks, and places it near the content moderation configuration section for discoverability.

### Content Moderation Relevance

Control 1.8 explicitly covers content moderation:
- "Content Moderation Level Configuration" subsection (lines ~220-240)
- Zone-specific moderation levels documented (Zone 1: Medium min, Zone 2/3: High)
- Verification criteria #10: "Content moderation level is set to High for all Zone 2/3 agents"
- Verification criteria #11: "No agents have content moderation set below Medium without documented risk acceptance"

This makes Control 1.8 the natural framework home for the CMM solution (which automates exactly these checks).

---

## 5. Solutions-Index.md Current State

**File:** `docs/reference/solutions-index.md` (~500 lines)

### Available Solutions Table (16 entries)

Currently includes 16 solutions. The CMM entry should be added. Key existing entries for reference:

| Solution | Status | Related Controls |
|----------|--------|------------------|
| Agent Access Governance Monitor | Work In Progress | 3.8 |
| Audit Configuration Validator | Work In Progress | 1.7 |
| Session Security Configurator | Completed | 1.23, 1.11 |
| Scope Drift Monitor | Completed | 1.14, 1.4, 1.5 |

**CMM is NOT yet listed** — needs adding.

### Solution Details Section Format

Each solution has a `### {Solution Name}` section with:
1. One-paragraph description
2. **Components:** bullet list
3. **Regulatory Alignment:** regulatory reference bullets
4. **Related Control(s):** link(s) to control doc(s)
5. **Repository Link:** GitHub link to solution folder

### Version History Table

Table with Solution, Current Version, Last Updated columns. CMM needs a v1.0.0 entry.

---

## 6. Documentation Suite Pattern (From AAM)

### AAM Documentation Suite (Reference Implementation)

| File | Lines | Content Sections |
|------|-------|------------------|
| `docs/PREREQUISITES.md` | ~78 | Licensing, Roles, PowerShell Modules, Python Requirements, Network, Dataverse |
| `docs/SCHEMA.md` | ~136 | 3 Tables with columns, Option Sets, Environment Variables, Connection References, ERD |
| `docs/EVIDENCE_EXPORT.md` | ~158 | Overview, Prerequisites, Interactive/SP/Zone/Baseline examples, Parameters Reference, Output Files, JSON Structure, Verify, Batch Verify, Cross-platform, Recommended Schedule, Troubleshooting |
| `docs/TROUBLESHOOTING.md` | ~95 | Deployment Issues, Authentication Issues, Validation Issues, Drift Detection Issues, Evidence Export Issues, Power Automate Flow Issues, Related Documentation |
| `docs/FLOW_SETUP.md` | — | Already exists for CMM (308 lines) |

### CMM Doc Task Breakdown

For CMM Phase 4:
- `docs/SCHEMA.md`: Replace stub with full content (3 CMM tables, option sets, env vars, connection refs, ERD)
- `docs/EVIDENCE_EXPORT.md`: Replace stub with full content (per-agent export examples, agent-level JSON schema)
- `docs/TROUBLESHOOTING.md`: Replace stub with full content (6 issue categories including per-agent specifics)
- `docs/PREREQUISITES.md`: Already populated — minor updates to mention evidence export module (MSAL.PS)
- `README.md`: Add evidence export to features, quick start steps 5-6, solution components tree
- `CHANGELOG.md`: Add `[1.0.0]` release entry

---

## 7. Recommended Approach for Each Plan

### Plan 04-CMM-01: Evidence Export Scripts (Wave 1)

**Scripts to create:**

| File | Target Location | Lines (est.) | Reference |
|------|-----------------|-------------|-----------|
| Export-ContentModerationEvidence.ps1 | `scripts/` | ~530 | AAM Export-AgentAccessEvidence.ps1 |
| Get-CMMValidationResults.ps1 | `scripts/private/` | ~220 | AAM Get-AAMValidationResults.ps1 |
| Test-EvidenceIntegrity.ps1 | `scripts/` | ~162 | AAM Test-EvidenceIntegrity.ps1 (copy with header update) |

**Key CMM adaptations for Export-ContentModerationEvidence.ps1:**

1. Import `CMMClient.psm1` (not AAMClient.psm1)
2. Query `fsi_moderationvalidationhistory` for scan summaries
3. Query `fsi_moderationviolations` for per-agent violations
4. Use `Get-ModerationBaseline -ActiveOnly` for baseline inclusion
5. JSON metadata.solution = "Content Moderation Governance Monitor"
6. Evidence filename prefix: `cmm-evidence-`
7. Summary includes agent-level metrics: `totalAgents`, `agentsCompliant`, `agentsViolated`
8. Violation severity breakdown: `criticalViolations`, `highViolations`, `mediumViolations`, `warningViolations`

**Key CMM adaptations for Get-CMMValidationResults.ps1:**

1. Query `fsi_moderationvalidationhistory` (not `fsi_accessvalidationhistory`)
2. Date filter on `fsi_validation_time` field
3. Select columns: `fsi_name,fsi_run_id,fsi_validation_time,fsi_total_agents,fsi_compliant_count,fsi_violation_count,fsi_overall_status,fsi_environments_scanned,fsi_summary_json`
4. Violations query uses agent-level columns: `fsi_agent_id,fsi_agent_name,fsi_expected_level,fsi_actual_level`
5. Zone filter applies to violations table `fsi_zone` column (not to history — history is aggregate)

**Parameters for Export-ContentModerationEvidence.ps1:**
- `-DataverseUrl` (Mandatory)
- `-TenantId` (Mandatory)
- `-OutputDirectory` (Mandatory)
- `-Zone` (Optional, ValidateSet 'All','1','2','3', default 'All')
- `-RunId` (Optional)
- `-FromDate` (Optional, default: 30 days ago)
- `-ToDate` (Optional, default: now)
- `-IncludeBaselines` (switch)
- `-Interactive` (switch)
- `-CertificateThumbprint` (Optional)
- `-ClientId` (Optional)

**CMM Evidence JSON Schema:**

```json
{
  "metadata": {
    "exportedAt": "ISO8601",
    "solution": "Content Moderation Governance Monitor",
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
    "overallStatus": "Compliant|NonCompliant|Warning|Critical",
    "totalScans": 0,
    "scansCompliant": 0,
    "scansWithViolations": 0,
    "totalAgents": 0,
    "totalViolations": 0,
    "criticalViolations": 0,
    "highViolations": 0,
    "mediumViolations": 0,
    "warningViolations": 0
  },
  "validations": [
    {
      "name": "string",
      "runId": "GUID",
      "validationTime": "ISO8601",
      "totalAgents": 0,
      "compliantCount": 0,
      "violationCount": 0,
      "overallStatus": "string",
      "environmentsScanned": "string",
      "summaryJson": "string"
    }
  ],
  "violations": [
    {
      "name": "string",
      "environmentGuid": "string",
      "environmentName": "string",
      "agentId": "string",
      "agentName": "string",
      "zone": 0,
      "expectedLevel": "High",
      "actualLevel": "Low",
      "severity": "Critical",
      "regulatoryContext": "FINRA 3110",
      "detectedAt": "ISO8601",
      "runId": "GUID"
    }
  ],
  "baselines": [
    {
      "baselineId": "GUID",
      "name": "string",
      "environmentGuid": "string",
      "environmentName": "string",
      "zone": 0,
      "agentId": "string",
      "agentName": "string",
      "moderationLevel": "High",
      "capturedBy": "user@org.com",
      "capturedAt": "ISO8601",
      "isActive": true
    }
  ]
}
```

### Plan 04-CMM-02: Control 1.8 Tip Admonition and Solutions-Index.md (Wave 1)

**Two files to modify in FSI-AgentGov repo:**

#### Control 1.8 Tip Admonition

Insert after the **Related Controls** section (around line 290) and before the **RAI Telemetry Capture** section:

```markdown
!!! tip "Automated Validation: Content Moderation Governance Monitor"
    For automated detection of non-compliant content moderation settings on Copilot Studio agents per governance zone, see the **Content Moderation Governance Monitor** solution.

    **Capabilities:**

    - Per-agent content moderation level validation (Low/Medium/High vs zone requirements)
    - Zone-based compliance checking (Zone 1: Medium minimum, Zone 2/3: High)
    - Drift detection with baseline comparison for configuration change tracking
    - Teams adaptive card alerts with severity classification and regulatory context
    - SHA-256 integrity-hashed evidence export for examination support

    **Deployable Solution:** [content-moderation-monitor](https://github.com/judeper/FSI-AgentGov-Solutions/tree/main/content-moderation-monitor) provides PowerShell validation scripts, Power Automate flow definitions, and Dataverse schema for persistent governance state.
```

#### Solutions-Index.md Additions

1. **Table row** (Available Solutions table):
```
| [Content Moderation Governance Monitor](#content-moderation-governance-monitor) | v1.0.0 | Work In Progress | Automated per-agent content moderation level validation against zone-specific governance requirements | 1.8, 1.14 |
```

2. **Solution Details section** (`### Content Moderation Governance Monitor`):
   - Description: per-agent content moderation validation
   - Components: PowerShell scripts, drift detection, Teams alerting, Dataverse tables, evidence export
   - Regulatory Alignment: FINRA 3110, SOX 404, GLBA 501(b), SEC AI Priorities
   - Related Controls: 1.8 (Primary), 1.14 (Data Minimization / Content Moderation), 2.1 (Managed Environments)
   - Repository Link: content-moderation-monitor

3. **Version History row**:
```
| Content Moderation Governance Monitor | v1.0.0 | February 2026 |
```

### Plan 04-CMM-03: Documentation Suite (Wave 2, depends on CMM-01)

**Files to create/update in FSI-AgentGov-Solutions repo:**

| File | Action | Target Lines | Content |
|------|--------|-------------|---------|
| `docs/SCHEMA.md` | Replace stub | ~130 | 3 tables, option sets, env vars, connection refs, ERD |
| `docs/EVIDENCE_EXPORT.md` | Replace stub | ~150 | Export guide adapted from AAM with per-agent examples |
| `docs/TROUBLESHOOTING.md` | Replace stub | ~110 | 6 issue categories with agent-specific troubleshooting |
| `docs/PREREQUISITES.md` | Update | ~85 | Add MSAL.PS requirement for evidence export |
| `README.md` | Update | ~135 | Add evidence export features, quick start steps, solution components |
| `CHANGELOG.md` | Update | ~120 | Add [1.0.0] release entry with Phase 4 additions |

**Key CMM-specific documentation differences from AAM:**

- SCHEMA.md documents per-agent columns (fsi_agent_id, fsi_agent_name, fsi_moderation_level, fsi_expected_level, fsi_actual_level) instead of per-environment settings
- EVIDENCE_EXPORT.md examples show per-agent JSON and agent-level filtering
- TROUBLESHOOTING.md includes "Unknown moderation level" issue (bot configuration parsing), agent enumeration failures, and per-agent vs per-environment distinction
- README.md emphasizes per-agent validation as the key differentiator

---

## 8. Risks and Dependencies

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| OData query differences for per-agent tables | Low | Low | CMMClient.psm1 patterns well-established; same Dataverse Web API |
| Control 1.8 is long (363 lines) — insertion point ambiguity | Low | Low | Research confirms Related Controls → RAI Telemetry boundary |
| Doc stubs may have been modified since Phase 1 | Low | Low | Stubs checked — still placeholders, safe to replace |
| Solutions-index.md merge conflicts | Low | Medium | CMM entry is short; no overlapping entries |
| PREREQUISITES.md already populated — risk of overwrite | Low | Medium | Only append MSAL.PS requirement; do not replace existing content |
| CMMClient.psm1 missing evidence-export functions | Medium | Low | Dedicated Get-CMMValidationResults.ps1 helper fills the gap |

### Dependencies

| Dependency | Required By | Status |
|------------|-------------|--------|
| CMMClient.psm1 | Plan CMM-01 | ✅ Available (v0.3.0, 10 functions) |
| fsi_moderationvalidationhistory table | Plan CMM-01 | ✅ Deployed (Phase 2) |
| fsi_moderationviolations table | Plan CMM-01 | ✅ Deployed (Phase 2) |
| fsi_moderationbaselines table | Plan CMM-01 | ✅ Deployed (Phase 2) |
| Phase 3 completion | Plan CMM-01 | ✅ Complete (2026-02-10) |
| Evidence export scripts | Plan CMM-03 | ⏳ CMM-01 delivers these |
| Solution catalog entry | Plan CMM-03 | ⏳ CMM-02 delivers this |
| mkdocs build --strict | Plan CMM-02 | ✅ Framework repo builds clean |

---

## 9. File Manifests Per Plan

### Plan 04-CMM-01: Evidence Export Scripts

| File | Action | Repository | Est. Lines |
|------|--------|------------|-----------|
| `content-moderation-monitor/scripts/Export-ContentModerationEvidence.ps1` | CREATE | FSI-AgentGov-Solutions | ~530 |
| `content-moderation-monitor/scripts/private/Get-CMMValidationResults.ps1` | CREATE | FSI-AgentGov-Solutions | ~220 |
| `content-moderation-monitor/scripts/Test-EvidenceIntegrity.ps1` | CREATE | FSI-AgentGov-Solutions | ~162 |

### Plan 04-CMM-02: Framework Integration

| File | Action | Repository | Est. Lines Changed |
|------|--------|------------|-------------------|
| `docs/controls/pillar-1-security/1.8-runtime-protection-and-external-threat-detection.md` | MODIFY | FSI-AgentGov | +13 (tip admonition) |
| `docs/reference/solutions-index.md` | MODIFY | FSI-AgentGov | +28 (table row + details section + version entry) |

### Plan 04-CMM-03: Documentation Suite

| File | Action | Repository | Est. Lines |
|------|--------|------------|-----------|
| `content-moderation-monitor/docs/SCHEMA.md` | REPLACE | FSI-AgentGov-Solutions | ~130 |
| `content-moderation-monitor/docs/EVIDENCE_EXPORT.md` | REPLACE | FSI-AgentGov-Solutions | ~150 |
| `content-moderation-monitor/docs/TROUBLESHOOTING.md` | REPLACE | FSI-AgentGov-Solutions | ~110 |
| `content-moderation-monitor/docs/PREREQUISITES.md` | MODIFY | FSI-AgentGov-Solutions | +5 |
| `content-moderation-monitor/README.md` | MODIFY | FSI-AgentGov-Solutions | +30 |
| `content-moderation-monitor/CHANGELOG.md` | MODIFY | FSI-AgentGov-Solutions | +25 |

---

## 10. Wave Structure and Execution Order

| Wave | Plans | Rationale |
|------|-------|-----------|
| Wave 1 | 04-CMM-01, 04-CMM-02 | Independent — scripts (Solutions repo) and framework integration (AgentGov repo) have no interdependency |
| Wave 2 | 04-CMM-03 | Depends on CMM-01 (documentation references export script names), and on CMM-02 (README references Control 1.8 and solutions-index) |

---

*Research completed: 2026-02-10*
*Confidence: HIGH — fourth iteration of proven Phase 4 pattern*
*Estimated total new code: ~912 lines PowerShell + ~445 lines documentation*
