# Phase 4 Research: Evidence Export & Dashboard Integration

**Researched:** 2026-02-10
**Phase:** 4 of 5 — Evidence Export & Dashboard Integration
**Domain:** SHA-256 evidence export, IntegrationConfig extension, Compliance Dashboard sync
**Confidence:** HIGH

---

## 1. Evidence Export Pattern Analysis (v4–v8)

### 1.1 Common File Structure

Every Tier 2 solution's evidence export follows a 3-script pattern:

| Script | Naming Convention | Purpose |
|--------|-------------------|---------|
| `Export-{Solution}Evidence.ps1` | Main export | JSON evidence + SHA-256 companion |
| `Get-{PREFIX}ValidationResults.ps1` | Private helper | Dataverse OData query with pagination |
| `Test-EvidenceIntegrity.ps1` | Verification utility | SHA-256 hash comparison |

Confirmed across ACV (v4), SSC (v5), AAM (v6), CMM (v7), FUS (v8).

### 1.2 SHA-256 Hashing Pattern

All solutions use identical hashing:

```powershell
$hash = Get-FileHash -Path $filePath -Algorithm SHA256
"$($hash.Hash)  $fileName" | Out-File -FilePath "$filePath.sha256" -Encoding utf8 -Force
```

Format: `{HASH}  {filename}` (two spaces) — compatible with `sha256sum -c` on Linux/macOS.

### 1.3 JSON Evidence Schema (5-Section Format)

```json
{
  "metadata": {
    "exportedAt": "ISO8601",
    "solution": "SolutionName",
    "solutionVersion": "2.0.0",
    "fromDate": "ISO8601",
    "toDate": "ISO8601",
    "zoneFilter": "All|1|2|3",
    "exportVersion": "1.0.0",
    "recordCount": 42,
    "organizationUrl": "https://org.crm.dynamics.com"
  },
  "summary": { "overallStatus": "Passed|Warning|Failed|Error", ... },
  "validations": [...],
  "violations": [...],
  "baselines": [...]
}
```

### 1.4 Evidence File Naming

Pattern: `{prefix}-evidence-{zone}-{yyyyMMdd-HHmmss}.json`

**DEC:** `dec-evidence-{zone}-{yyyyMMdd-HHmmss}.json`

### 1.5 Common Function Signature

```powershell
function Export-{Solution}Evidence {
    param(
        [Parameter(Mandatory)] [string]$DataverseUrl,
        [Parameter(Mandatory)] [string]$TenantId,
        [Parameter(Mandatory)] [string]$OutputDirectory,
        [ValidateSet('All','1','2','3')] [string]$Zone = 'All',
        [datetime]$FromDate = (Get-Date).AddDays(-30),
        [datetime]$ToDate = (Get-Date),
        [string]$RunId,
        [switch]$IncludeBaseline,
        [switch]$Interactive,
        [string]$CertificateThumbprint,
        [string]$ClientId
    )
}
```

Returns: `[PSCustomObject]@{ EvidenceFile; HashFile; SHA256; RecordCount; ViolationCount; GeneratedAt }`

### 1.6 Authentication Pattern

Dual auth: Interactive (MSAL.PS) or Certificate-based SP (Azure Automation). Imports solution-specific `*Client.psm1` for Dataverse connection.

---

## 2. v9 Integration Infrastructure Analysis

### 2.1 IntegrationConfig.psm1

**8 exported functions:**

| Function | Purpose |
|----------|---------|
| `Get-SolutionControlMapping` | Solution name → array of control IDs |
| `Get-SolutionTableConfig` | Table schema, key columns, query patterns per solution |
| `ConvertTo-DashboardStatus` | Solution status → CD status (1=Compliant, 2=Partial, 3=Non-Compliant, 4=Not Assessed) |
| `Get-CanonicalZoneValue` | Normalizes zone values |
| `Get-EvidenceTypeId` | Returns evidence type choice value (5 = Test Result) |
| `Get-EvidenceExportScripts` | Per-solution evidence export script paths |
| `Get-SolutionDirectories` | Solution directory paths |
| `Get-DashboardTableConfig` | CD target table schema (`fsi_controlassessments`) |

**Current mappings (5 solutions):** ACV→1.7, SSC→1.23/1.11, AAM→3.8, CMM→1.8, FUS→1.14

**DEC extension:** `DEC → [1.5, 1.7, 3.4]` — Control 1.7 will have TWO solutions (ACV + DEC), requiring worst-case status aggregation.

### 2.2 Export-UnifiedComplianceEvidence.ps1

Discovers solutions via `Get-EvidenceExportScripts`, iterates and invokes each export script, creates unified package with SHA-256 hash chain and manifest. **No changes needed** — DEC registration in IntegrationConfig automatically integrates.

### 2.3 Sync-SolutionAssessments.ps1

Flow: authenticate → get mappings → per-solution OData query → group by zone → translate status → upsert to `fsi_controlassessments`.

**DEC-specific considerations:**
- Query source: `fsi_denycorrelations` (not validation history)
- Status derived from alerts, not pass/fail
- Three controls mapped → up to 9 assessment records per sync run (3 zones × 3 controls)

### 2.4 CD Assessment Record Structure

Target: `fsi_controlassessments` — columns: `fsi_controlid`, `fsi_zone`, `fsi_status`, `fsi_assessmentdate`, `fsi_notes`, `fsi_evidenceid`.

---

## 3. Phase 1-3 Artifact Summary

### DECClient.psm1 Functions (15 total)

| Function | Category | Available for Phase 4 |
|----------|----------|----------------------|
| `Connect-DECDataverse` | Connection | Yes — Dataverse auth |
| `Read-DECDenyEvents` | Dataverse read | Yes — query fsi_denyevents |
| `Read-DECCorrelations` | Dataverse read | Yes — query fsi_denycorrelations |
| `Read-DECAlerts` | Dataverse read | Yes — query fsi_denyalerts |
| `Connect-DECServices` | Connection (master) | Yes |

### Dataverse Tables (Phase 2)

| Table | Entity Set | Key Columns |
|-------|-----------|-------------|
| `fsi_denyevent` | `fsi_denyevents` | source_type, agent_id, zone, severity, timestamp |
| `fsi_denycorrelation` | `fsi_denycorrelations` | correlation_date, agent_id, zone, event_count, severity_distribution_json, trend_7day_json |
| `fsi_denyalert` | `fsi_denyalerts` | alert_timestamp, severity, alert_type |
| `fsi_denyvalidationhistory` | `fsi_denyvalidationhistories` | validation_date |

---

## 4. DEC Solution Current State

Existing scripts after Phase 1-3: 7 PS1 scripts, 5 Python scripts, DECClient.psm1 (2097 lines), 3 templates, KQL queries, 3 docs.

**What needs to be created for Phase 4:**

| File | Requirement | Location |
|------|-------------|----------|
| `Export-DenyEventEvidence.ps1` | EVI-01, EVI-02 | `scripts/` |
| `Get-DECValidationResults.ps1` | EVI-01 (helper) | `scripts/private/` |
| `Test-EvidenceIntegrity.ps1` | EVI-01 (verification) | `scripts/` |

**Files to modify (in companion repo via IntegrationConfig):**

| File | Requirement | Changes |
|------|-------------|---------|
| `IntegrationConfig.psm1` | EVI-03, EVI-04 | 5 functions updated |
| `Sync-SolutionAssessments.ps1` | EVI-05 | DEC query block added |

---

## 5. Risks and Dependencies

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| Control 1.7 dual-solution mapping | Certain | Medium | Use worst-case status when ACV + DEC both report |
| DEC has no simple pass/fail | Certain | Medium | Derive status from alert severity distribution |
| Regulatory alignment is novel | Medium | Low | Static mapping table embedded in export script |
| Cross-repo dependency | Certain | Low | Follow established pattern: stage locally |

---

## 6. Recommended Technical Approach

### EVI-01/EVI-02: Export-DenyEventEvidence.ps1

- Use DECClient functions (`Read-DECDenyEvents`, `Read-DECCorrelations`, `Read-DECAlerts`) — already handle OData pagination and retry
- 6-section JSON: metadata, summary, regulatoryAlignment, correlations, alerts, denyEvents (raw events gated on `-IncludeRawEvents`)
- Regulatory alignment as static mapping table (FINRA 4511/3110/25-07, SEC 17a-3/4, SOX 302/404, GLBA 501(b))
- Overall status derived from alert severity: Critical/High → Failed, Warning → Warning, else → Passed

### EVI-03/EVI-04: IntegrationConfig Extension

- Add DEC to 5 functions: `Get-SolutionControlMapping`, `Get-SolutionTableConfig`, `ConvertTo-DashboardStatus`, `Get-EvidenceExportScripts`, `Get-SolutionDirectories`
- DEC status translation: alert-severity-based (Critical/High → 3, Warning → 2, else → 1)

### EVI-05: Sync-SolutionAssessments Extension

- Query `fsi_denycorrelations` for today's summaries + `fsi_denyalerts` for today's alerts
- Group by zone, derive status per zone from alert distribution
- Upsert 3 controls (1.5, 1.7, 3.4) × zones = up to 9 assessment records
- Handle 1.7 overlap with ACV via worst-case aggregation

### Wave Structure

| Plan | Wave | Requirements | Dependencies |
|------|------|-------------|--------------|
| 04-01 | 1 | EVI-01, EVI-02 | Phase 2-3 complete (DECClient) |
| 04-02 | 2 | EVI-03, EVI-04 | 04-01 (evidence script path) |
| 04-03 | 2 | EVI-05 | 04-01 (status translation logic) |

---

*Research completed: 2026-02-10*
