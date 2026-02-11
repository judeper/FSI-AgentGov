# Research: Phase 4 — Evidence Export & Framework Integration (CAA v10)

**Researched:** 2026-02-10
**Confidence:** HIGH (eighth iteration of proven Tier 2 pattern; Phase 1–3 complete; established patterns from v4 ACV, v5 SSC, v8 FUS, v9 cross-solution integration)

## Phase Goal

CA policy compliance evidence is exportable for regulatory examinations and the solution is fully integrated into the FSI-AgentGov framework documentation and Compliance Dashboard.

## Must-Haves

| # | Must-Have | Requirement | Source |
|---|----------|-------------|--------|
| 1 | SHA-256 integrity-hashed evidence export for CA policy configs, validation results, drift history | EFR-01 | SC-1 |
| 2 | Control 1.11 tip admonition linking to CAA solution | EFR-02 | SC-2 |
| 3 | solutions-index.md entry updated from Work In Progress → Completed | EFR-03 | SC-3 |
| 4 | Documentation suite in companion repo (prerequisites, schema, deployment, troubleshooting, CHANGELOG) | EFR-04 | SC-4 |
| 5 | Compliance Dashboard receives Control 1.11 assessment scores via v9 integration feed pattern | EFR-05 | SC-5 |

---

## Prior Art: Established Patterns for Each Deliverable

### Deliverable 1: SHA-256 Evidence Export (EFR-01)

**Source pattern:** ACV Phase 4 plan at `.planning/phases/04-evidence-export-framework-integration/04-01-PLAN.md`

The ACV established the canonical evidence export pattern with three scripts:
1. **Export-AuditValidationEvidence.ps1** — Main export producing JSON with metadata/summary/validations sections + SHA-256 companion
2. **Get-ValidationResults.ps1** (private helper) — Dataverse OData query with pagination, scope/date/RunId filtering
3. **Test-EvidenceIntegrity.ps1** — Hash verification utility returning boolean

**JSON evidence schema (canonical):**
```json
{
  "metadata": {
    "exportedAt": "ISO8601",
    "scope": "Tenant|Environment",
    "fromDate": "ISO8601",
    "toDate": "ISO8601",
    "runId": "GUID or null",
    "exportVersion": "1.0.0",
    "recordCount": "integer",
    "organizationUrl": "DataverseUrl"
  },
  "summary": {
    "overallStatus": "worst severity across results",
    "validationsRun": "count",
    "validationsPassed": "count",
    "validationsFailed": "count",
    "validationsWarning": "count"
  },
  "validations": [ "array of result objects" ]
}
```

**Critical implementation rules (from 04-RESEARCH.md anti-patterns):**
- `ConvertTo-Json -Depth 10` (NOT default depth 2 — truncates nested objects)
- `Out-File -Encoding utf8` (explicit for cross-platform compatibility)
- SHA-256 companion file format: `"{hash}  {filename}"` (two spaces, compatible with `sha256sum -c`)
- Overall status computation: Error > Failed > GracePeriod > Warning > Passed priority

**CAA adaptation:**
- Script name: `Export-CAAComplianceEvidence.ps1` (follows `Export-{Solution}Evidence` naming)
- Queries: `fsi_CAPolicyValidationHistory` (immutable), `fsi_CAPolicyViolation`, `fsi_CAPolicyBaseline`
- Scope: Unlike ACV which has Tenant/Environment scope, CAA is always tenant-level (CA policies are tenant-scoped)
- Additional JSON sections: `violations` (drift items), `baselines` (current policy baselines) — richer than ACV's validations-only format
- Reuses existing private helper pattern — dot-source `Connect-GraphSession.ps1` and new `Get-CAAValidationResults.ps1`

**Files to create (companion repo):**

| File | Purpose |
|------|---------|
| `C:/dev/FSI-AgentGov-Solutions/conditional-access-automation/scripts/Export-CAAComplianceEvidence.ps1` | Main evidence export with SHA-256 |
| `C:/dev/FSI-AgentGov-Solutions/conditional-access-automation/scripts/private/Get-CAAValidationResults.ps1` | Dataverse query helper for validation history |
| `C:/dev/FSI-AgentGov-Solutions/conditional-access-automation/scripts/Test-EvidenceIntegrity.ps1` | SHA-256 hash verification |

### Deliverable 2: Control 1.11 Tip Admonition (EFR-02)

**Source pattern:** Control 1.7's Audit Configuration Validator tip in `04-RESEARCH.md` lines 429–448

**Current state of Control 1.11:** The control at `docs/controls/pillar-1-security/1.11-conditional-access-and-phishing-resistant-mfa.md` already contains:
- An existing `!!! tip "Agent 365 Architecture Update"` admonition at the top
- A `!!! warning "Service Principal Security Group Bypass"` admonition in Key Configuration Points
- A reference to `conditional-access-automation` solution within the Service Principal warning (line 66)
- No dedicated "Deployable Solution" tip admonition

**Insertion point:** After the "Related Controls" section (line ~161), before "Implementation Playbooks" section (line ~169), following the exact pattern established by ACV in Control 1.7.

**Template:**
```markdown
!!! tip "Automated Compliance: Conditional Access Automation"
    For automated CA policy deployment, daily compliance scanning, and drift detection for AI workloads, see the **Conditional Access Automation** solution.

    **Capabilities:**
    - 8 zone-specific CA policy templates for Copilot Studio, Agent Builder, M365 Copilot
    - Daily compliance scanning with break-glass exclusion verification
    - Multi-dimensional drift detection (policy disabled, conditions weakened, controls changed)
    - Teams adaptive card alerts with zone-based severity classification
    - Evidence export with SHA-256 integrity hashing for FINRA/SEC examination support

    **Deployable Solution:** [conditional-access-automation](https://github.com/judeper/FSI-AgentGov-Solutions/tree/main/conditional-access-automation) provides PowerShell deployment scripts, Azure Automation runbook wrappers, and Power Automate flow definitions.
```

**Key characteristics (from established pattern):**
- Uses "Automated Compliance" heading (not "Deployable Solution" — that's the closing line)
- Placed after Related Controls, before Implementation Playbooks
- 5–6 capability bullet points
- Single-line deployable solution reference with artifacts list
- No more than 10 lines total to avoid control file bloat

**File to modify:**
- `docs/controls/pillar-1-security/1.11-conditional-access-and-phishing-resistant-mfa.md`

### Deliverable 3: solutions-index.md Update (EFR-03)

**Current state:** The CAA entry in `docs/reference/solutions-index.md` shows:

Table row (line ~31):
```
| [Conditional Access Automation](#conditional-access-automation) | v1.0.0 | Work In Progress | CA policy deployment and compliance monitoring for AI workloads | 1.11, 1.23, 1.18 |
```

Detail section (lines ~219–242) already exists with:
- Components list (8 CA policy templates, PowerShell scripts, zone-based requirements, break-glass, ELM integration)
- Security alignment (NIST, Zero Trust, SOX, GLBA)
- Related controls (1.11, 1.23)
- Repository link

**Changes required:**
1. **Table row:** Change `Work In Progress` → `Completed`, update version to `v1.1.0` (major functionality added in v10)
2. **Detail section:** Add components for v10 deliverables (Azure Automation, Power Automate flows, Dataverse tables, evidence export, drift detection)
3. **Version history table:** Update version to `v1.1.0`

**Pattern from existing Completed solutions (Scope Drift Monitor, Session Security Configurator):**
- Status badge: `Completed`
- `!!! success "Production Ready"` admonition (optional, used by CD and SDM)
- Comprehensive components list including all Tier 2 infrastructure
- Regulatory Alignment section with 4+ regulations

**File to modify:**
- `docs/reference/solutions-index.md`

### Deliverable 4: Documentation Suite (EFR-04)

**Source pattern:** SSC and ACV companion repo directory structures (from ARCHITECTURE.md lines 390–420)

**Current CAA companion repo structure (existing assets):**
```
conditional-access-automation/
├── README.md                    # Existing (needs update)
├── CHANGELOG.md                 # Existing (needs update)
├── docs/
│   ├── zone-requirements.md     # Existing
│   ├── compliance-monitoring.md # Existing
│   ├── deployment-guide.md      # Existing
│   ├── troubleshooting.md       # Existing
│   └── architecture.md          # Existing (possibly)
├── scripts/
│   ├── Deploy-CAPolicies.ps1            # Existing (Phase 1 modernized)
│   ├── Test-PolicyCompliance.ps1        # Existing (Phase 1 modernized)
│   ├── Watch-PolicyDrift.ps1            # Phase 1 new
│   ├── Export-PolicyBaseline.ps1        # Phase 1 new
│   ├── Register-ServicePrincipal.ps1    # Existing (Phase 1 modernized)
│   ├── Start-CAAValidationRunbook.ps1   # Phase 3 new
│   ├── caa_client.py                    # Phase 2 new
│   ├── create_dataverse_schema.py       # Phase 2 new
│   ├── create_environment_variables.py  # Phase 2 new
│   ├── create_connection_references.py  # Phase 2 new
│   ├── deploy.py                        # Phase 2 new
│   ├── conditional-access-automation.psd1 # Phase 1 module manifest
│   ├── CAAClient.psm1                  # Phase 2 module
│   └── private/
│       ├── Connect-GraphSession.ps1     # Phase 1
│       ├── Get-ZoneClassification.ps1   # Phase 1
│       ├── Test-ParameterValidation.ps1 # Phase 1
│       ├── Get-PolicyBaseline.ps1       # Phase 3
│       └── Compare-PolicyBaseline.ps1   # Phase 3
├── templates/                   # 8 zone-specific CA policy JSON templates
└── src/
    ├── adaptive-card-caa-alert.json       # Phase 3
    ├── caa-daily-compliance-flow.json      # Phase 3
    └── caa-provisioning-hook-flow.json     # Phase 3
```

**Docs to create/update for Phase 4:**

| File | Action | Content |
|------|--------|---------|
| `docs/PREREQUISITES.md` | Create | Permissions, modules, Entra ID setup, Azure Automation requirements |
| `docs/SCHEMA.md` | Create | Dataverse table and column reference (3 tables, option sets, env vars, connection refs) |
| `docs/EVIDENCE_EXPORT.md` | Create | Evidence export usage guide for auditors |
| `docs/TROUBLESHOOTING.md` | Update | Add evidence export troubleshooting section |
| `CHANGELOG.md` | Update | Add v1.1.0 entries for all v10 deliverables |
| `README.md` | Update | Add Phase 3/4 components, update status to Completed |

**Documentation pattern from SSC/ACV:**
- PREREQUISITES.md: PowerShell version, Graph module, Azure subscription, Entra app registration steps, required permissions table
- SCHEMA.md: Table definitions with column type/description, option set values, environment variable defaults
- EVIDENCE_EXPORT.md: Export command examples, JSON schema explanation, hash verification steps, recommended frequency
- TROUBLESHOOTING.md: Common issues (auth failures, missing permissions, hash mismatches) with causes and resolutions

### Deliverable 5: Compliance Dashboard Feed (EFR-05)

**Source pattern:** v9 Cross-Solution Integration, Phase 2 (Dashboard Feed Layer)

The v9 integration established the `Sync-SolutionAssessments.ps1` script and `cd-solution-feed-collector.json` flow that:
1. Queries each Tier 2 solution's validation history table daily
2. Translates `overall_status` → CD `fsi_status` (1=Compliant, 2=Partial, 3=Non-Compliant)
3. Upserts `fsi_controlassessment` records using `IntegrationConfig.psm1` mappings
4. Auto-registers evidence in `fsi_complianceevidence` with SHA-256 hashes

**Current v9 solution-to-control mapping (from 02-01-SUMMARY.md):**
- ACV → Control 1.7
- SSC → Controls 1.23, 1.11
- AAM → Control 3.8
- CMM → Control 1.8
- FUS → Control 1.14

**CAA integration requirement:** SSC already feeds Control 1.11, but CAA provides more specific CA policy compliance data. Two options:

**Option A: Extend Sync-SolutionAssessments.ps1** (RECOMMENDED)
- Add CAA as 6th solution in the sync pipeline
- CAA → Control 1.11 (primary), Control 1.23 (secondary — CA session controls), Control 1.18 (secondary — RBAC complement)
- SSC's 1.11 feed covers session security; CAA's 1.11 feed covers CA policy compliance — these are complementary signals
- IntegrationConfig.psm1 needs a new entry for CAA table names and control mappings
- `Sync-SolutionAssessments.ps1` needs CAA query block added

**Option B: Standalone feed script**
- Create `Write-CAAComplianceFeed.ps1` in CAA scripts directory
- Self-contained, doesn't modify v9 code
- Duplicates pattern, harder to maintain

**Recommendation: Option A** — Extend the existing integration infrastructure. This is the pattern used by all 5 current solutions. Adding CAA as the 6th solution maintains consistency and centralized management.

**Files to modify (companion repo — cross-solution-integration):**

| File | Change |
|------|--------|
| `cross-solution-integration/scripts/powershell/IntegrationConfig.psm1` | Add CAA table names, control mappings (1.11, 1.23, 1.18) |
| `cross-solution-integration/scripts/powershell/Sync-SolutionAssessments.ps1` | Add CAA query/translate/upsert block |
| `cross-solution-integration/flows/cd-solution-feed-collector.json` | Add CAA sync step in flow |
| `cross-solution-integration/docs/STATUS_MAPPING.md` | Document CAA status translation logic |

**CAA status translation logic:**
```
CAA overall_status → CD fsi_status:
  Passed (severity 1) → 1 (Compliant)
  Warning (severity 2) → 2 (Partial)
  GracePeriod (severity 3) → 2 (Partial)
  Failed (severity 4) → 3 (Non-Compliant)
  Error (severity 5) → 3 (Non-Compliant)
```

**CAA Dataverse tables to query:**
- `fsi_CAPolicyValidationHistory` — latest run results, immutable
- `fsi_CAPolicyViolation` — active violations for compliance calculation

---

## Technical Approach by Plan

### Recommended Plan Structure (5 plans, 2 waves)

#### Wave 1 (independent, parallel)

| Plan | Title | Requirements | Files Created/Modified |
|------|-------|-------------|----------------------|
| 04-01 | Evidence Export Scripts | EFR-01 | 3 PS scripts in companion repo |
| 04-02 | Control 1.11 Tip + solutions-index.md | EFR-02, EFR-03 | 2 docs in FSI-AgentGov |

#### Wave 2 (depends on Wave 1)

| Plan | Title | Requirements | Files Created/Modified |
|------|-------|-------------|----------------------|
| 04-03 | Documentation Suite | EFR-04 | 3 new docs, 2 updated docs in companion repo |
| 04-04 | Compliance Dashboard Feed | EFR-05 | 4 files in cross-solution-integration |
| 04-05 | Build Validation & Verification | All | Verification checklist |

**Rationale for plan split:**
- EFR-02 and EFR-03 are both framework doc edits (same repo, same `mkdocs build --strict` validation) — combine into one plan
- EFR-01 (evidence scripts) and EFR-04 (docs) are both in companion repo but independent — Wave 1 vs Wave 2
- EFR-05 (CD feed) depends on understanding CAA's Dataverse schema and evidence output from EFR-01

### Alternative: 3-plan structure (aggressive)

| Plan | Title | Requirements |
|------|-------|-------------|
| 04-01 | Evidence Export Scripts + CD Feed | EFR-01, EFR-05 |
| 04-02 | Framework Documentation (Control 1.11 + solutions-index) | EFR-02, EFR-03 |
| 04-03 | Companion Repo Docs + CHANGELOG | EFR-04 |

This is faster but combines evidence export and CD feed, which have different target repos and risk profiles.

---

## Specific Files To Create or Modify

### Creates (Companion Repo — FSI-AgentGov-Solutions/conditional-access-automation/)

| File | Purpose | Template Source |
|------|---------|---------------|
| `scripts/Export-CAAComplianceEvidence.ps1` | Main evidence export | ACV's Export-AuditValidationEvidence.ps1 |
| `scripts/private/Get-CAAValidationResults.ps1` | Dataverse query helper | ACV's Get-ValidationResults.ps1 |
| `scripts/Test-EvidenceIntegrity.ps1` | Hash verification | ACV's Test-EvidenceIntegrity.ps1 |
| `docs/PREREQUISITES.md` | Prerequisites guide | SSC docs/prerequisites.md pattern |
| `docs/SCHEMA.md` | Dataverse schema reference | SSC docs/dataverse-schema.md pattern |
| `docs/EVIDENCE_EXPORT.md` | Evidence export guide | ACV docs/evidence-export-guide.md |

### Modifies (Companion Repo — FSI-AgentGov-Solutions/conditional-access-automation/)

| File | Change |
|------|--------|
| `README.md` | Add Phase 3/4 components, update status |
| `CHANGELOG.md` | Add v1.1.0 entries |
| `docs/TROUBLESHOOTING.md` | Add evidence export troubleshooting section |

### Modifies (FSI-AgentGov Framework Repo)

| File | Change |
|------|--------|
| `docs/controls/pillar-1-security/1.11-conditional-access-and-phishing-resistant-mfa.md` | Add tip admonition after Related Controls |
| `docs/reference/solutions-index.md` | Update table entry (WIP→Completed), update detail section, update version history |

### Modifies (Companion Repo — FSI-AgentGov-Solutions/cross-solution-integration/)

| File | Change |
|------|--------|
| `scripts/powershell/IntegrationConfig.psm1` | Add CAA solution entry |
| `scripts/powershell/Sync-SolutionAssessments.ps1` | Add CAA query block |
| `flows/cd-solution-feed-collector.json` | Add CAA sync step |
| `docs/STATUS_MAPPING.md` | Add CAA status translation |

---

## Differences from Prior Phase 4 Implementations

| Aspect | v4 ACV Phase 4 | v8 FUS Phase 4 | v10 CAA Phase 4 |
|--------|----------------|----------------|-----------------|
| **Evidence scope** | Tenant + Environment | Per-environment + per-agent | Tenant-level only (CA policies are tenant-scoped) |
| **Evidence sections** | metadata/summary/validations | metadata/summary/validations/violations/baselines | metadata/summary/validations/violations/baselines (follows FUS enrichment) |
| **Control integration** | Control 1.7 | Control 1.14 | Control 1.11 |
| **CD feed** | Not applicable (pre-v9) | Not applicable (pre-v9) | Extends v9 Sync-SolutionAssessments.ps1 |
| **Target control count** | 1 (1.7) | 1 (1.14) | 3 (1.11 primary, 1.23 and 1.18 secondary) |
| **Plan count** | 2 plans | 3 plans | 4-5 plans (evidence, framework docs, companion docs, CD feed) |

---

## Risks and Dependencies

| Risk | Severity | Mitigation |
|------|----------|------------|
| **Cross-repo edit coordination** — Changes span 3 directories (FSI-AgentGov, CAA companion, cross-solution-integration) | MEDIUM | Wave structure isolates repo boundaries; validate each repo independently |
| **CD feed conflict with SSC** — SSC already feeds Control 1.11 | LOW | SSC covers session security dimension; CAA covers CA policy compliance dimension; both valid signals; document coexistence in STATUS_MAPPING.md |
| **IntegrationConfig.psm1 backwards compatibility** — Adding CAA must not break existing 5-solution sync | MEDIUM | New entry follows identical structure; DryRun mode tests before upsert |
| **Evidence schema divergence** — CAA's tenant-only scope differs from ACV/FUS's mixed scope | LOW | Document that CAA evidence always has `"scope": "Tenant"`; no Environment scope needed |
| **mkdocs build validation** — Control 1.11 and solutions-index.md changes must pass strict build | LOW | Run `mkdocs build --strict` after each framework doc change |
| **Companion repo not in same worktree** — FSI-AgentGov-Solutions is at `C:/dev/FSI-AgentGov-Solutions/` | LOW | Document cd to companion repo before git commits; separate commit per repo |

---

## Dependencies

### External Dependencies
- Phase 1 complete: CAAClient module, Test-PolicyCompliance.ps1 with Dataverse persistence
- Phase 2 complete: Dataverse tables (fsi_CAPolicyBaseline, fsi_CAPolicyValidationHistory, fsi_CAPolicyViolation), environment variables, connection references
- Phase 3 complete: Start-CAAValidationRunbook.ps1, adaptive card, daily compliance flow, ELM provisioning hook
- v9 complete: IntegrationConfig.psm1, Sync-SolutionAssessments.ps1, CD-SolutionFeedCollector flow

### Internal Dependencies (within Phase 4)
- Wave 2 plans depend on Wave 1 completion
- CD feed (EFR-05) depends on understanding evidence output schema from EFR-01
- Documentation suite (EFR-04) references evidence export commands from EFR-01

---

## Dataverse Query Patterns for Evidence Export

### CAA Validation History Query (for Get-CAAValidationResults.ps1)

```powershell
# OData query pattern for fsi_CAPolicyValidationHistory
$filter = @(
    "fsi_timestamp ge $($FromDate.ToString('yyyy-MM-ddTHH:mm:ssZ'))"
    "fsi_timestamp le $($ToDate.ToString('yyyy-MM-ddTHH:mm:ssZ'))"
)
if ($RunId) { $filter += "fsi_runid eq '$RunId'" }

$query = "fsi_capolicyvalidationhistories?" +
    "`$filter=$($filter -join ' and ')" +
    "&`$orderby=fsi_timestamp desc" +
    "&`$select=fsi_name,fsi_runid,fsi_scope,fsi_zone,fsi_severity," +
    "fsi_validationtype,fsi_rawvalue,fsi_reason,fsi_timestamp"
```

### CAA Violation Query

```powershell
# Active violations for evidence context
$query = "fsi_capolicyviolations?" +
    "`$filter=fsi_detectedat ge $($FromDate.ToString('yyyy-MM-ddTHH:mm:ssZ'))" +
    "&`$orderby=fsi_detectedat desc" +
    "&`$select=fsi_name,fsi_policyid,fsi_policyname,fsi_violationtype," +
    "fsi_zone,fsi_severity,fsi_previousvalue,fsi_currentvalue," +
    "fsi_detectedat,fsi_status"
```

### CAA Baseline Query

```powershell
# Current baselines for evidence snapshot
$query = "fsi_capolicybaselines?" +
    "`$filter=fsi_isactive eq true" +
    "&`$orderby=fsi_policyname asc" +
    "&`$select=fsi_policyid,fsi_policyname,fsi_zone,fsi_state," +
    "fsi_conditions,fsi_grantcontrols,fsi_sessioncontrols,fsi_createdon"
```

---

## CAA Evidence JSON Schema (Extended)

```json
{
  "metadata": {
    "exportedAt": "2026-02-10T14:00:00Z",
    "scope": "Tenant",
    "tenantId": "contoso.onmicrosoft.com",
    "fromDate": "2026-01-11T00:00:00Z",
    "toDate": "2026-02-10T14:00:00Z",
    "runId": null,
    "exportVersion": "1.0.0",
    "solutionVersion": "1.1.0",
    "recordCount": 48,
    "violationCount": 2,
    "baselineCount": 8
  },
  "summary": {
    "overallStatus": "Warning",
    "validationsRun": 48,
    "validationsPassed": 44,
    "validationsFailed": 2,
    "validationsWarning": 2,
    "zoneBreakdown": {
      "zone1": { "passed": 16, "total": 16 },
      "zone2": { "passed": 15, "total": 16 },
      "zone3": { "passed": 13, "total": 16 }
    }
  },
  "validations": [],
  "violations": [],
  "baselines": []
}
```

---

## CD Feed Integration Constants (for IntegrationConfig.psm1)

```powershell
# New entry for IntegrationConfig.psm1 solution registry
@{
    SolutionId   = 'CAA'
    DisplayName  = 'Conditional Access Automation'
    TablePrefix  = 'fsi_CAPolicyValidationHistory'
    ViolationTable = 'fsi_CAPolicyViolation'
    BaselineTable  = 'fsi_CAPolicyBaseline'
    Controls     = @(
        @{ ControlId = '1.11'; Role = 'Primary'; Description = 'CA policy compliance for AI workloads' }
        @{ ControlId = '1.23'; Role = 'Secondary'; Description = 'CA session controls for step-up auth' }
        @{ ControlId = '1.18'; Role = 'Secondary'; Description = 'CA policy RBAC complement' }
    )
    StatusMapping = @{
        1 = 1   # Passed → Compliant
        2 = 2   # Warning → Partial
        3 = 2   # GracePeriod → Partial
        4 = 3   # Failed → Non-Compliant
        5 = 3   # Error → Non-Compliant
    }
}
```

---

## Build Validation Requirements

All framework repo changes must pass:
```bash
mkdocs build --strict
python scripts/verify_controls.py
```

Companion repo changes validated by:
- PowerShell syntax check: `pwsh -NoProfile -Command "& { Get-Content Export-CAAComplianceEvidence.ps1 | Out-Null }"`
- JSON syntax check: `python -c "import json; json.load(open('file.json'))"`

---

## Milestone References

| Milestone | Phase | Relevant Pattern |
|-----------|-------|-----------------|
| v4 (ACV) | Phase 4 | Evidence export scripts, Control 1.7 tip, solutions-index update |
| v5 (SSC) | Phase 4 | Evidence export + CD evidence push to `fsi_complianceevidence` |
| v8 (FUS) | Phase 4 | 3-plan structure (evidence, control tip + solutions-index, docs) |
| v9 (Integration) | Phase 2 | Sync-SolutionAssessments.ps1, IntegrationConfig.psm1, CD feed pattern |
| v9 (Integration) | Phase 4 | Export-UnifiedComplianceEvidence.ps1 master evidence pattern |

---

## Open Questions

1. **CAA version bump:** Should CAA update from v1.0.0 → v1.1.0 (minor — Tier 2 infrastructure added) or v2.0.0 (major — fundamentally different from original validated scripts)?
   - **Recommendation:** v1.1.0 — the original Deploy/Test/Register scripts are unchanged in API contract; new scripts are additive
   
2. **Dual CD feed for Control 1.11:** Both SSC and CAA will feed Control 1.11. Should SSC remain or should CAA replace it?
   - **Recommendation:** Both co-exist — SSC covers session security dimension, CAA covers CA policy compliance. Sync-SolutionAssessments.ps1 should use worst-of-two status for 1.11 overall score. Document in STATUS_MAPPING.md.

3. **Evidence export default date range:** 30 days (ACV default) or broader?
   - **Recommendation:** 30 days default matches ACV pattern. Quarterly evidence rolls up via v9's Export-UnifiedComplianceEvidence.ps1 which calls per-solution exports with custom date ranges.

---

## Sources

### Primary (HIGH confidence)
- `.planning/phases/04-evidence-export-framework-integration/04-01-PLAN.md` — ACV evidence export plan (canonical pattern)
- `.planning/phases/04-evidence-export-framework-integration/04-RESEARCH.md` — ACV evidence export research (anti-patterns, pitfalls)
- `.planning/phases/04-evidence-integration-v8/04-FUS-01-PLAN.md` — FUS evidence export plan
- `.planning/phases/04-evidence-integration-v8/04-FUS-02-PLAN.md` — FUS control tip + solutions-index plan
- `.planning/phases/04-evidence-integration-v8/04-FUS-03-PLAN.md` — FUS documentation suite plan
- `.planning/milestones/v9-ROADMAP.md` — v9 cross-solution integration roadmap
- `.planning/milestones/v9-REQUIREMENTS.md` — v9 CDF requirements (CDF-01 through CDF-05)
- `.planning/phases/02-dashboard-feed-layer/02-01-SUMMARY.md` — v9 Phase 2 summary (Sync-SolutionAssessments.ps1)
- `docs/controls/pillar-1-security/1.11-conditional-access-and-phishing-resistant-mfa.md` — Current control content
- `docs/reference/solutions-index.md` — Current CAA entry and format
- `.planning/phases/03-automation-alerting-caa/03-VERIFICATION.md` — Phase 3 verification results

### Secondary (MEDIUM confidence)
- `.planning/research/ARCHITECTURE.md` — Cross-solution integration architecture
- `.planning/phases/01-schema-normalization/01-03-PLAN.md` — cross-solution-integration scaffold

---

## Metadata

**Confidence breakdown:**
- Evidence export scripts: HIGH — 7th iteration of identical pattern (ACV, SSC, AAM, CMM, FUS, SDM, now CAA)
- Control 1.11 tip: HIGH — Pattern verified from Control 1.7 ACV tip, Control 1.14 FUS tip
- solutions-index.md: HIGH — Direct pattern from 6 completed solution entries
- Documentation suite: HIGH — 7 prior companion repo doc suites as templates
- CD feed integration: HIGH — v9 Sync-SolutionAssessments.ps1 is production-verified with 5 solutions

**Research date:** 2026-02-10
**Valid until:** 60 days (stable PowerShell patterns, established documentation conventions)
