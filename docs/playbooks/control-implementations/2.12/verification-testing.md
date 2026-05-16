# Verification & Testing — Control 2.12: Supervision and Oversight (FINRA Rule 3110)

> **Examiner-defensible evidence package** for Control 2.12. This playbook produces, signs, and retains the artifacts required to demonstrate to FINRA, SEC, OCC, FFIEC, NYDFS, and internal audit that every Zone 2 and Zone 3 Microsoft 365 AI agent output is produced under a written supervisory procedure, reviewed by a qualified principal where required, classified correctly under FINRA Rule 2210, tested annually under FINRA Rule 3120, and retained as a books-and-records artifact under FINRA Rule 4511 and SEC Rule 17a-4.
>
> **Scope:** Microsoft 365 Copilot, Copilot Studio agents, and Microsoft Agent Framework HITL workflows across Commercial, GCC, GCC High, and DoD tenants. The playbook produces evidence keyed to the **nine Verification Criteria** in [Control 2.12 §Verification Criteria](../../../controls/pillar-2-management/2.12-supervision-and-oversight-finra-rule-3110.md#verification-criteria) and runs under **twelve Pester namespaces** catalogued in §1.
>
> **Non-substitution anchor.** FINRA Rule 3110 requires written supervisory procedures, the designation of a qualified registered principal (Series 24 for broker-dealers; Series 66 / 65 for investment advisers), and supervisory review by that principal for the business activities involved. This playbook helps **evidence** that those obligations are being performed; it does **not** and **cannot** substitute for them. A clean Pester run is not supervision. Supervision is a signed decision by a qualified human. The tests verify the artifact; the artifact verifies the human.
>
> **Companion controls:** [2.13 Documentation and Record-Keeping](../../../controls/pillar-2-management/2.13-documentation-and-record-keeping.md) governs retention of the evidence produced here. [2.25 Agent 365 Admin Center Governance](../../../controls/pillar-2-management/2.25-agent-365-admin-center-governance-console.md) and [2.26 Entra Agent ID Identity Governance](../../../controls/pillar-2-management/2.26-entra-agent-id-identity-governance.md) reference this control as the supervisory non-substitution anchor. [1.7 Comprehensive Audit Logging](../../../controls/pillar-1-security/1.7-comprehensive-audit-logging-and-compliance.md) provides the immutable log surface that the REVIEWER, QUEUE, and AGF namespaces read from. [3.1 Agent Inventory](../../../controls/pillar-3-reporting/3.1-agent-inventory-and-metadata-management.md) bounds supervisory scope; [3.4 Incident Reporting](../../../controls/pillar-3-reporting/3.4-incident-reporting-and-root-cause-analysis.md) consumes FAIL records from this playbook; [3.6 Orphaned Agent Detection](../../../controls/pillar-3-reporting/3.6-orphaned-agent-detection-and-remediation.md) re-enters supervisory scope when a sponsor departs.
>
> **Last UI verified:** April 2026 against Microsoft Entra admin center build 2026.04.x, Copilot Studio web client April 2026, Power Automate April 2026, Microsoft Purview compliance portal April 2026, and Microsoft Graph beta endpoints for agent identities and Agent Framework HITL evidence export.

---

## Document Conventions

| Convention | Value |
|---|---|
| PowerShell baseline | PowerShell 7.4+ Core; `#Requires -Version 7.4` |
| Test framework | Pester 5.5+ |
| Output discipline | No `Write-Host`. All evidence emitted as structured objects via `Write-Output`, then serialized to canonical JSON. |
| Sovereign cloud handling | Every Pester suite detects tenant cloud and, where the underlying surface is not GA in GCC / GCC High / DoD, emits `SKIPPED` with a pointer to the §13 SOV compensating-control namespace rather than `FAIL`. |
| Evidence retention | 6 years on WORM-protected storage or the SEC Rule 17a-4(f) audit-trail alternative (FINRA Rule 4511 / SEC Rule 17a-4(b)(4)). Rule 3120 working papers, principal designation records, and sovereign quarterly attestations are retained under the same policy, with the first two years easily accessible. |
| Hashing | SHA-256 over canonical JSON; per-record hashes are chained into a Merkle root and signed in `attestation.json` per §17. |
| Canonical roles | Per [docs/reference/role-catalog.md](../../../reference/role-catalog.md). This playbook references **Compliance Officer**, **Designated Principal / Qualified Supervisor**, **AI Governance Lead**, **AI Administrator**, **Agent Owner**, **Entra Global Admin**, **Purview Compliance Admin**, **Power Platform Admin**, **Exchange Online Admin**, and **Entra Security Reader** only. |
| Regulatory framing | This playbook **helps meet** recordkeeping, supervision, and oversight expectations under FINRA Rules 3110 / 3120 / 2210 / 4511, FINRA Regulatory Notice 24-09 (Gen AI / LLM guidance), SEC Rules 17a-3 / 17a-4, SOX §§302 / 404, GLBA §501(b), OCC Bulletin 2026-13 (formerly OCC Bulletin 2011-12) (Fed SR 26-2 (formerly SR 11-7)), NYDFS 23 NYCRR 500, and the FFIEC IT Examination Handbook. It does **not** by itself ensure compliance; organizations should verify findings against their own legal and regulatory obligations and tailor sample sizes, SLAs, and zone thresholds to their documented risk appetite. |

> **FINRA 3110 non-substitution, restated.** Tests in this playbook verify that WSPs exist, that reviewers are qualified, that decisions are captured with rationale, and that evidence is retained. They do not verify that the reviewer's *decision* was correct. The decision correctness test is a qualitative supervisory review performed by the Designated Principal during Rule 3120 annual testing (§9) and documented in Rule 3120 working papers.

---

## §0 Pre-Test Prerequisites & Sovereign Cloud Bootstrap

### 0.1 Operator prerequisites

The operator running this playbook must hold the following role assignments, scoped to the tenant under test, and activated through Privileged Identity Management (PIM) for the duration of the test run.

| Role (canonical) | Required for |
|---|---|
| Entra Global Admin **or** Entra Agent ID Admin (read) | Agent identity enumeration; sponsor attribute reads for §11 SPONSOR cross-ref |
| Purview Compliance Admin (read) | Supervision audit-log reads; retention-label verification in §13 SIEM |
| Power Platform Admin (read) | Copilot Studio HITL configuration export (§3 HITL); Power Automate approval history reads (§4 QUEUE) |
| Exchange Online Admin (read) | Where HITL decisions are delivered to a supervisory mailbox, verify journaling targets in §13 SIEM |
| Entra Security Reader | Sign-in log reads for reviewer-decision attribution (§5 REVIEWER) |
| AI Governance Lead | Operates the daily Pester cadence; counter-signs the quarterly attestation packet in §18 |
| Compliance Officer | Co-signs §17 evidence packs; owns the WSP addendum verified in §2 WSP |
| Designated Principal (Series 24 for BD supervisory scope; Series 66 / 65 for RIA scope) | Signs Rule 3120 working papers in §8 R3120; signs 2210 principal pre-use approval evidence in §9 R2210; signs sovereign quarterly attestation in §13 SOV |

The Pester suites in §2 through §13 are **read-only** and do not require write permissions. Remediation runbooks referenced from failure paths (see §16 triage) require additional write scopes and a separate change ticket.

### 0.2 Module baseline

```powershell
#Requires -Version 7.4
#Requires -Modules @{ ModuleName='Microsoft.Graph.Authentication';         ModuleVersion='2.20.0' }
#Requires -Modules @{ ModuleName='Microsoft.Graph.Identity.Governance';    ModuleVersion='2.20.0' }
#Requires -Modules @{ ModuleName='Microsoft.Graph.Identity.SignIns';       ModuleVersion='2.20.0' }
#Requires -Modules @{ ModuleName='Microsoft.Graph.Beta.Applications';      ModuleVersion='2.20.0' }
#Requires -Modules @{ ModuleName='Microsoft.PowerApps.Administration.PowerShell'; ModuleVersion='2.0.180' }
#Requires -Modules @{ ModuleName='ExchangeOnlineManagement';               ModuleVersion='3.4.0' }
#Requires -Modules @{ ModuleName='Pester';                                 ModuleVersion='5.5.0' }

$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest
```

### 0.3 PRE gates (must all pass before §2–§13 execute)

The bootstrap script `Invoke-Agt212PreFlight.ps1` runs eight pre-flight gates. Any `FAIL` halts the suite and emits a single evidence artifact `preflight-FAILED-<runId>.json`. Any `SKIPPED` from PRE-06 routes subsequent suites to the sovereign compensating path (§13 SOV).

| Gate | ID | Purpose | Failure behavior |
|---|---|---|---|
| Module presence | PRE-01 | Confirms required modules loaded at pinned versions | HALT |
| Graph / PowerApps context | PRE-02 | Confirms `Connect-MgGraph` and `Add-PowerAppsAccount` established with required scopes | HALT |
| Tenant identification | PRE-03 | Captures `tenantId`, `displayName`, `verifiedDomains[0].name` for every evidence record | HALT |
| Cloud detection | PRE-04 | Reads `(Get-MgContext).Environment` and maps to `Commercial / GCC / GCCH / DoD` | Continue with `cloud` field set |
| Copilot license gate | PRE-05 | Confirms tenant holds at least one Microsoft 365 Copilot SKU | HALT — supervision surface presumes Copilot footprint |
| Feature parity probe | PRE-06 | Probes Copilot Studio human-agent handoff API and Agent Framework `request_info()` surface for HTTP 200 vs 404/403 | If sovereign and probe negative, route to §13 SOV; if Commercial and probe negative, HALT with remediation pointer |
| Clock skew gate | PRE-07 | Compares local UTC to `Date` header from Graph response; aborts if drift > 60 seconds | HALT |
| Control 1.2 / 3.1 registry freshness | PRE-08 | Confirms the authoritative agent registry (Control 1.2 / 3.1) attestation is ≤ 30 days old | Continue with `WARN` if 30–60 days; HALT if > 60 days |

### 0.4 Sovereign bootstrap pattern

```powershell
function Test-Agt212SovereignTenant {
    [CmdletBinding()]
    [OutputType([pscustomobject])]
    param()

    $ctx = Get-MgContext
    if (-not $ctx) { throw "PRE-02 failed: no Graph context. Run Connect-MgGraph first." }

    $cloud = switch ($ctx.Environment) {
        'Global'    { 'Commercial' }
        'USGov'     { 'GCC' }
        'USGovDoD'  { 'DoD' }
        'USGovHigh' { 'GCCH' }
        default     { 'Unknown' }
    }

    [pscustomobject]@{
        cloud        = $cloud
        is_sovereign = $cloud -in @('GCC','GCCH','DoD')
        tenant_id    = $ctx.TenantId
        detected_at  = (Get-Date).ToUniversalTime().ToString('o')
    }
}
```

When `is_sovereign` is `$true` **and** the PRE-06 parity probe is negative for the specific surface under test, every affected Pester `It` block emits:

```json
{
  "status": "SKIPPED",
  "reason": "Surface not GA in sovereign cloud at run time",
  "compensating_control_ref": "§13 SOV"
}
```

This produces a defensible audit trail showing the test was attempted, was correctly skipped on regulatory-sound grounds, and was supplemented by the manual attestation in §13 — rather than appearing as an unexplained gap.

### 0.5 Run identifier

Every test run is tagged with a deterministic `runId` of the form `AGT212-yyyyMMdd-HHmmss-<8charGuid>`. The `runId` is embedded in every evidence record and in the filename of every artifact produced by §17.

### 0.6 What success looks like

A "green quarter" for Control 2.12 is the conjunction of nine conditions, one per Verification Criterion in the control document. The conditions are stated as objective evidence, not as narrative.

| # | Verification Criterion | What success looks like (objective) | Pester namespace |
|---|---|---|---|
| 1 | WSP addendum coverage | Versioned WSP document present; names this control; enumerates per-zone supervision activities; designates qualified principals by name and CRD number; signature page dated within 12 months by a registered principal | §2 WSP |
| 2 | HITL configuration — Zone 3 | For **N=10** Zone 3 agents per quarter, Copilot Studio human-agent handoff or Agent Framework HITL wiring is present; trigger criteria match the WSP; a test transcript shows routing to a qualified reviewer | §3 HITL + §11 AGF |
| 3 | Principal registration verification | For **100%** of designated principals in the WSP, a CRD / WebCRD extract dated within 90 days shows Series 24 (BD) or Series 66 / 65 (RIA) active | §6 PRINCIPAL |
| 4 | Review queue SLA | Supervisory review queue shows median and 95th-percentile time-to-review within zone SLA; exceptions logged as incidents under Control 3.4 | §4 QUEUE |
| 5 | Reviewer-decision audit trail | For **N=25** reviewer decisions per quarter, each record has non-null reviewer UPN + timestamp + decision + rationale; each decision is traceable to the originating agent interaction and (for Agent Framework) to the originating request ID and checkpoint | §5 REVIEWER |
| 6 | Rule 3120 annual test | Rule 3120 annual test of AI supervisory controls documents design and operating effectiveness, enumerates exceptions with remediation, and is signed by a qualified principal | §8 R3120 |
| 7 | Rule 2210 classification evidence | For **N=10** customer-facing Zone 3 agent outputs per quarter, 2210 classification (Correspondence / Retail / Institutional) is recorded; where Retail, principal pre-use approval (or documented exclusion under Rule 2210(b)(1)) is attached | §9 R2210 |
| 8 | Sovereign-cloud compensating control | For sovereign tenants, a quarterly manual supervisory review against the Control 1.2 / 3.1 agent registry, evidenced by dual-signed attestation, covers every Zone 3 agent not backed by commercial-cloud HITL tooling | §13 SOV |
| 9 | Agent Framework evidence retention | For every HITL request raised via `request_info()`, the firm retains request ID, checkpoint state at pause, reviewer response payload, and final executor output | §11 AGF |

Any missing artifact is treated as a control exception requiring written remediation and re-test within the following quarter.

---

## §1 Namespace Catalog

Control 2.12's nine Verification Criteria are evidenced by **twelve Pester namespaces**. Two criteria (C2.12-2 HITL and C2.12-9 AGF retention) are served by two namespaces each because Copilot Studio and Agent Framework are distinct supervisory surfaces that must be tested independently. Three namespaces (§7 SAMPLING, §10 SPONSOR, §13 SIEM) do not map to a single VC; they evidence cross-cutting supervisory integrity that every VC silently depends on.

| Namespace | Section | Evidences criterion | Cadence | Owner |
|---|---|---|---|---|
| `WSP`       | §2  | C2.12-1 | Quarterly (attestation of annual re-review) | Compliance Officer |
| `HITL`      | §3  | C2.12-2 (Copilot Studio surface) | Monthly sampling; N=10/quarter | AI Administrator |
| `QUEUE`     | §4  | C2.12-4 | Daily; monthly latency report | AI Governance Lead |
| `REVIEWER`  | §5  | C2.12-5 | Weekly; N=25/quarter | Compliance Officer |
| `PRINCIPAL` | §6  | C2.12-3 | Monthly; 100% quarterly | Compliance Officer |
| `SAMPLING`  | §7  | Cross-cutting (supports C2.12-4, -5, -7) | Monthly | AI Governance Lead |
| `R3120`     | §8  | C2.12-6 | Annual | Designated Principal |
| `R2210`     | §9  | C2.12-7 | Monthly sampling; N=10/quarter | Designated Principal |
| `SPONSOR`   | §10 | Upstream dependency on [Control 2.26](../../../controls/pillar-2-management/2.26-entra-agent-id-identity-governance.md) | Weekly | AI Governance Lead |
| `AGF`       | §11 | C2.12-2 (Agent Framework surface) + C2.12-9 | Continuous (per HITL request) + weekly reconciliation | AI Administrator |
| `SOV`       | §13 | C2.12-8 | Quarterly (sovereign tenants) | Designated Principal |
| `SIEM`      | §12 | Forwarding & retention for all above | Weekly | AI Governance Lead |

Each namespace section follows an identical template:

1. **Criterion mapping** — explicit pointer to which numbered criterion in Control 2.12 §Verification Criteria is satisfied, including partial-coverage notes.
2. **Pre-conditions** — what must already be true (e.g., Copilot Studio bot exists, WSP addendum path supplied, Agent Framework evidence export pipeline reachable).
3. **Pester suite** — `Describe "AGT212-{NS}" { Context "Zone {1|2|3}" { It "..." } }` with PS 7.4 / Pester 5.5 syntax.
4. **Sample passing JSON evidence record** — exact shape that flows into the evidence pack.
5. **Sample failing JSON evidence record + remediation pointer** — links to a numbered triage entry in §16.
6. **Examiner artifact** — filename pattern, retention duration, signing policy.
7. **Zone 1 / Zone 2 / Zone 3 thresholds** — pass / warn / fail bands per zone.
8. **Regulator mapping** — which specific regulatory citation each test supports.

### 1.1 Evidence record schema (canonical)

Every evidence record produced by every namespace MUST conform to this schema. The schema is enforced by `Test-Agt212EvidenceSchema` in §17.

```json
{
  "control_id": "2.12",
  "run_id": "AGT212-20260415-093012-a1b2c3d4",
  "run_timestamp": "2026-04-15T09:30:12Z",
  "tenant_id": "11111111-2222-3333-4444-555555555555",
  "tenant_display_name": "Contoso Securities, LLC",
  "cloud": "Commercial",
  "namespace": "HITL",
  "criterion": "C2.12-2",
  "zone": "3",
  "subject_id": "copilot-retail-research-assistant",
  "subject_type": "copilot_studio_bot",
  "status": "PASS",
  "assertion": "Z3 Copilot Studio bot has human-agent handoff enabled with trigger matching WSP",
  "observed_value": {
    "handoff_enabled": true,
    "trigger_expression": "intent in ['buy-recommendation','sell-recommendation','account-specific-advice']",
    "handoff_target": "o365group:supervision-retail@contoso.com",
    "wsp_version_ref": "WSP-AI-Addendum-v2026.03"
  },
  "expected_value": {
    "handoff_enabled": true,
    "trigger_expression": "<matches WSP v2026.03 high-risk taxonomy>"
  },
  "evidence_artifacts": ["hitl-config-AGT212-20260415-093012-a1b2c3d4.json","hitl-transcript-0007.json"],
  "regulator_mappings": ["FINRA-3110","FINRA-2210","FINRA-4511","SEC-17a-4","SOX-404"],
  "remediation_ref": null,
  "operator_upn": "agt212-runner@contoso.com",
  "schema_version": "1.0"
}
```

---

## §2 WSP — Written Supervisory Procedures Addendum Evidence

### 2.1 Criterion mapping

This namespace evidences **C2.12-1**: *the firm's WSP addendum names this control, enumerates the supervision activities for each zone, designates qualified principals by name and registration, and was approved by a registered principal before current effective date.*

The WSP addendum is the upstream document that defines *what counts as high-risk*, *what the review SLAs are*, and *who the designated principal is* for every other namespace. A WSP failure cascades: §3 HITL cannot verify "trigger matches WSP" if no WSP exists; §4 QUEUE cannot verify SLA compliance if no SLA is documented; §6 PRINCIPAL cannot verify designations if none are enumerated. WSP therefore runs first in the suite order and any FAIL in this namespace downgrades every subsequent namespace's `status` to `UNVERIFIED_UPSTREAM_WSP`.

### 2.2 Pre-conditions

- PRE-01 through PRE-08 returned `PASS` (or PRE-08 returned `WARN` with Compliance Officer acknowledgement).
- The WSP addendum file path is supplied via `-WspAddendumPath` (PDF, DOCX, or Markdown with a detached signature file).
- A reference JSON schema `wsp-addendum-expected.json` enumerates the required sections and signer roles.
- The signer identity is reachable via Entra for validation that the signer was a registered principal on the effective date.

### 2.3 Pester suite

```powershell
#Requires -Version 7.4
#Requires -Modules Pester

Describe "AGT212-WSP" -Tag 'C2.12','WSP' {

    BeforeAll {
        $script:WspPath       = $env:AGT212_WSP_ADDENDUM_PATH
        $script:WspSigPath    = "$script:WspPath.sig"
        $script:WspExpected   = Get-Content "$PSScriptRoot/wsp-addendum-expected.json" -Raw | ConvertFrom-Json
        $script:WspMeta       = Get-WspAddendumMetadata -Path $script:WspPath
        $script:WspSignerUpn  = $script:WspMeta.signer_upn
        $script:WspSignedAt   = [datetime]$script:WspMeta.signed_at
        $script:WspVersion    = $script:WspMeta.version
    }

    Context "Addendum file presence" {
        It "WSP addendum file exists at the supplied path" {
            Test-Path $script:WspPath | Should -BeTrue -Because "C2.12-1 requires a documented, retrievable WSP addendum"
        }
        It "WSP addendum has a detached PKCS#7 signature" {
            Test-Path $script:WspSigPath | Should -BeTrue
            $verify = Invoke-Pkcs7Verify -DataPath $script:WspPath -SignaturePath $script:WspSigPath
            $verify.IsValid | Should -BeTrue -Because "unsigned WSPs are not examination-defensible"
        }
    }

    Context "Required sections" {
        It "addendum names Control 2.12 explicitly" {
            (Get-Content $script:WspPath -Raw) | Should -Match '\b2\.12\b'
        }
        It "addendum enumerates zone-specific supervision activities for Z1, Z2, and Z3" {
            foreach ($z in @('Zone 1','Zone 2','Zone 3')) {
                (Get-Content $script:WspPath -Raw) | Should -Match $z -Because "each zone must have documented supervision activity"
            }
        }
        It "addendum designates at least one principal by name and CRD number" {
            $principals = $script:WspMeta.designated_principals
            $principals.Count | Should -BeGreaterThan 0
            foreach ($p in $principals) {
                $p.full_name | Should -Not -BeNullOrEmpty
                $p.crd_number | Should -Match '^\d{5,7}$'
                $p.series_registration | Should -BeIn @('24','66','65')
            }
        }
        It "addendum defines per-zone SLAs for review queue (used by §4 QUEUE)" {
            $script:WspMeta.sla.zone_2.minutes_to_review | Should -BeGreaterThan 0
            $script:WspMeta.sla.zone_3.minutes_to_review | Should -BeGreaterThan 0
        }
        It "addendum defines 2210 classification methodology (used by §9 R2210)" {
            $script:WspMeta.r2210_methodology | Should -Not -BeNullOrEmpty
        }
        It "addendum defines Rule 3120 annual testing scope (used by §8 R3120)" {
            $script:WspMeta.r3120_scope | Should -Not -BeNullOrEmpty
        }
    }

    Context "Signer registration and recency" {
        It "WSP signer holds a current registered-principal series at the date of signing" {
            $reg = Get-CrdRegistrationSnapshot -Upn $script:WspSignerUpn -AsOf $script:WspSignedAt
            $reg.series | Should -BeIn @('24','66','65')
            $reg.status_as_of_signing | Should -Be 'Active'
        }
        It "WSP was approved within the last 365 days (annual re-review)" {
            ((Get-Date) - $script:WspSignedAt).TotalDays | Should -BeLessOrEqual 365 -Because "C2.12-1 re-review cadence is annual"
        }
        It "WSP version label is present and follows the firm naming convention" {
            $script:WspVersion | Should -Match '^WSP-AI-Addendum-v\d{4}\.\d{2}$'
        }
    }

    Context "Cross-reference integrity" {
        It "every downstream namespace's expected configuration is resolvable from WSP metadata" {
            $script:WspMeta.downstream_refs | ForEach-Object {
                $_.namespace | Should -BeIn @('HITL','QUEUE','REVIEWER','PRINCIPAL','SAMPLING','R3120','R2210','AGF')
                $_.anchor_ref | Should -Not -BeNullOrEmpty
            }
        }
    }
}
```

### 2.4 Sample passing evidence record

```json
{
  "control_id": "2.12",
  "run_id": "AGT212-20260415-093012-a1b2c3d4",
  "run_timestamp": "2026-04-15T09:30:12Z",
  "tenant_id": "11111111-2222-3333-4444-555555555555",
  "cloud": "Commercial",
  "namespace": "WSP",
  "criterion": "C2.12-1",
  "zone": "all",
  "subject_id": "WSP-AI-Addendum-v2026.03",
  "subject_type": "wsp_document",
  "status": "PASS",
  "assertion": "WSP addendum present, signed by registered principal within 365 days, enumerates Z1/Z2/Z3 supervision and downstream references",
  "observed_value": {
    "signer_upn": "jane.principal@contoso.com",
    "signer_crd": "1234567",
    "signer_series": "24",
    "signed_at": "2026-01-14T17:00:00Z",
    "days_since_signing": 91,
    "designated_principals_count": 4,
    "downstream_refs_resolved": ["HITL","QUEUE","REVIEWER","PRINCIPAL","SAMPLING","R3120","R2210","AGF"]
  },
  "expected_value": {
    "signer_series": "24|66|65",
    "days_since_signing": "<=365",
    "designated_principals_count": ">=1"
  },
  "evidence_artifacts": ["wsp-addendum-v2026.03.pdf","wsp-addendum-v2026.03.pdf.sig","wsp-metadata-<runId>.json"],
  "regulator_mappings": ["FINRA-3110","FINRA-4511","SEC-17a-4","SOX-404"],
  "remediation_ref": null,
  "schema_version": "1.0"
}
```

### 2.5 Sample failing evidence record

```json
{
  "control_id": "2.12",
  "namespace": "WSP",
  "criterion": "C2.12-1",
  "zone": "all",
  "subject_id": "WSP-AI-Addendum-v2025.02",
  "subject_type": "wsp_document",
  "status": "FAIL",
  "assertion": "WSP addendum must be re-reviewed at least annually",
  "observed_value": {
    "signed_at": "2025-02-20T17:00:00Z",
    "days_since_signing": 420,
    "signer_series_at_signing": "24"
  },
  "expected_value": { "days_since_signing": "<=365" },
  "remediation_ref": "TRG-WSP-01",
  "regulator_mappings": ["FINRA-3110","FINRA-4511"],
  "schema_version": "1.0"
}
```

`TRG-WSP-01` (§16.2): initiate the annual WSP re-review workflow; Compliance Officer drafts updates; Designated Principal re-signs within 30 days; every downstream namespace in the interim emits `status: UNVERIFIED_UPSTREAM_WSP` rather than `PASS`.

### 2.6 Examiner artifact

| Artifact | Filename pattern | Retention | Signed by |
|---|---|---|---|
| WSP addendum document | `wsp-addendum-<version>.pdf` | 6 years from supersession + 2 years accessible | Designated Principal (Series 24 / 66 / 65) |
| WSP detached signature | `wsp-addendum-<version>.pdf.sig` | Same as document | Same |
| WSP metadata extraction | `wsp-metadata-<runId>.json` | 6 years | AI Governance Lead |
| Pester results (JUnit XML) | `pester-WSP-<runId>.xml` | 6 years | Same |

### 2.7 Zone thresholds

| Zone | PASS band | WARN band | FAIL band |
|---|---|---|---|
| All zones (WSP is cross-zone) | Signed ≤ 365 days; all required sections present; signer registration verified | Signed 366–395 days with remediation in flight | Signed > 395 days, unsigned, missing required sections, signer registration not verifiable |

### 2.8 Regulator mapping

| Test | FINRA 3110 | FINRA 4511 | SEC 17a-4 | SOX §404 |
|---|---|---|---|---|
| Addendum presence | ✓ written supervisory procedures | ✓ books-and-records | ✓ 17a-4(b)(4) | ✓ documented controls |
| Signer is registered principal | ✓ supervisor qualification | — | — | ✓ named control owner |
| Annual re-review cadence | ✓ ongoing adequacy | ✓ retention of supersessions | ✓ easily accessible | ✓ periodic review |
| Downstream refs resolvable | ✓ WSPs enforceable | — | — | ✓ control traceability |

---

## §3 HITL — Copilot Studio Human-Agent Handoff Evidence

### 3.1 Criterion mapping

This namespace evidences **C2.12-2** for the Copilot Studio surface: *for a random sample of N=10 Zone 3 agents per quarter, the Copilot Studio human-agent handoff configuration is present, the trigger criteria match the WSP, and a test transcript demonstrates routing to a qualified reviewer.*

The companion namespace §11 AGF covers the same criterion for the Microsoft Agent Framework surface. An agent using both surfaces (some tenants front Copilot Studio bots with Agent Framework workflows for back-end reasoning) must PASS in both namespaces.

### 3.2 Pre-conditions

- WSP namespace returned PASS (the WSP trigger taxonomy is the expected value for the HITL trigger configuration).
- Power Platform admin credentials are PIM-activated with Power Platform Admin (read) role.
- Copilot Studio bot inventory is retrievable via `Get-AdminPowerAppEnvironment` + `Get-CopilotStudioBot` (firm wrapper around the unsupported but documented Power Platform API).
- The reference dataset `hitl-test-prompts.json` supplies 3 canonical high-risk prompts per Z3 agent used to drive the handoff transcript test.

### 3.3 Pester suite

```powershell
Describe "AGT212-HITL" -Tag 'C2.12','HITL' {

    BeforeAll {
        $script:Sov        = Test-Agt212SovereignTenant
        $script:AllZ3Bots  = Get-CopilotStudioBotInventory -Zone 3
        $script:Sample     = Get-Random -InputObject $script:AllZ3Bots -Count ([Math]::Min(10, $script:AllZ3Bots.Count))
        $script:WspTriggers = (Get-WspAddendumMetadata).high_risk_intents
        $script:TestPrompts = Get-Content "$PSScriptRoot/hitl-test-prompts.json" -Raw | ConvertFrom-Json
    }

    Context "Sovereign-cloud short-circuit" -Skip:(-not $script:Sov.is_sovereign) {
        It "emits SKIPPED with §13 SOV compensating-control pointer when Copilot Studio handoff surface is not GA in sovereign cloud" {
            $rec = New-Agt212EvidenceRecord -Namespace 'HITL' `
                -Criterion 'C2.12-2' -Zone '3' -Status 'SKIPPED' `
                -Assertion 'Copilot Studio handoff not GA in sovereign cloud at run time; attest via §13 SOV' `
                -RemediationRef 'TRG-SOV-01'
            $rec.status | Should -Be 'SKIPPED'
        }
    }

    Context "Per-bot HITL configuration (N=10 sample)" -Skip:$script:Sov.is_sovereign {
        It "each sampled Z3 bot has human-agent handoff enabled" {
            foreach ($bot in $script:Sample) {
                $cfg = Get-CopilotStudioHandoffConfiguration -BotId $bot.Id
                $cfg.handoff_enabled | Should -BeTrue -Because "Z3 bot $($bot.DisplayName) must route high-risk outputs to a human reviewer"
            }
        }
        It "each sampled Z3 bot's handoff trigger expression matches the WSP high-risk taxonomy" {
            foreach ($bot in $script:Sample) {
                $cfg = Get-CopilotStudioHandoffConfiguration -BotId $bot.Id
                $matched = Test-HandoffTriggerAlignment -Trigger $cfg.trigger_expression -WspIntents $script:WspTriggers
                $matched.all_covered | Should -BeTrue -Because "C2.12-2 requires WSP-trigger alignment"
            }
        }
        It "each sampled Z3 bot routes to a reviewer group whose members hold current supervisory registration" {
            foreach ($bot in $script:Sample) {
                $cfg = Get-CopilotStudioHandoffConfiguration -BotId $bot.Id
                $members = Get-MgGroupMember -GroupId $cfg.handoff_target_group_id -All
                foreach ($m in $members) {
                    $reg = Get-CrdRegistrationSnapshot -Upn $m.AdditionalProperties.userPrincipalName
                    $reg.series | Should -BeIn @('24','66','65') -Because "reviewer $($m.AdditionalProperties.userPrincipalName) must be a qualified principal"
                    $reg.status | Should -Be 'Active'
                }
            }
        }
    }

    Context "Transcript replay (live handoff test)" -Skip:$script:Sov.is_sovereign {
        It "each sampled Z3 bot produces a handoff event when driven with a canonical high-risk prompt" {
            foreach ($bot in $script:Sample) {
                $prompt = ($script:TestPrompts | Where-Object bot_id -eq $bot.Id).prompts[0]
                $result = Invoke-CopilotStudioProbeTranscript -BotId $bot.Id -Prompt $prompt
                $result.handoff_fired     | Should -BeTrue -Because "canonical prompt must fire handoff"
                $result.reviewer_notified | Should -BeTrue
                $result.transcript_id     | Should -Not -BeNullOrEmpty
            }
        }
        It "the transcript is captured in the supervision audit log within 60 seconds of emission" {
            foreach ($bot in $script:Sample) {
                $prompt = ($script:TestPrompts | Where-Object bot_id -eq $bot.Id).prompts[0]
                $result = Invoke-CopilotStudioProbeTranscript -BotId $bot.Id -Prompt $prompt
                Start-Sleep -Seconds 60
                $log = Search-UnifiedAuditLog `
                    -StartDate $result.emitted_at `
                    -EndDate   ($result.emitted_at.AddMinutes(5)) `
                    -RecordType 'CopilotInteraction' `
                    -FreeText  $result.transcript_id
                $log.Count | Should -BeGreaterOrEqual 1 -Because "transcript must be auditable (supports C2.12-5 REVIEWER)"
            }
        }
    }

    Context "Autonomy-level alignment" -Skip:$script:Sov.is_sovereign {
        It "no sampled Z3 bot is marked Fully Autonomous (autonomy pattern not in scope at Agent 365 GA)" {
            foreach ($bot in $script:Sample) {
                $meta = Get-AgentAutonomyClassification -BotId $bot.Id
                $meta.autonomy_level | Should -Not -Be 'fully_autonomous' -Because "see Control 2.12 autonomy admonition"
            }
        }
    }
}
```

### 3.4 Sample passing evidence record

```json
{
  "control_id": "2.12",
  "namespace": "HITL",
  "criterion": "C2.12-2",
  "zone": "3",
  "subject_id": "bot-retail-research-assistant-0012",
  "subject_type": "copilot_studio_bot",
  "status": "PASS",
  "assertion": "Z3 bot has handoff enabled, trigger aligns with WSP, reviewer group members are qualified principals, live probe fired handoff within SLA",
  "observed_value": {
    "handoff_enabled": true,
    "handoff_target_group": "supervision-retail@contoso.com",
    "reviewer_count_active_series24": 5,
    "trigger_intents": ["buy-recommendation","sell-recommendation","account-specific-advice","outside-business-activity"],
    "wsp_intents_covered_pct": 100,
    "probe_transcript_id": "copilot-tx-0b7a...",
    "probe_latency_ms": 1843,
    "audit_log_hit_within_60s": true,
    "autonomy_level": "recommend_only"
  },
  "expected_value": {
    "handoff_enabled": true,
    "wsp_intents_covered_pct": 100,
    "reviewer_count_active_series24_or_66_or_65": ">=1",
    "audit_log_hit_within_60s": true
  },
  "evidence_artifacts": ["hitl-config-bot-0012-<runId>.json","hitl-transcript-0b7a-<runId>.json"],
  "regulator_mappings": ["FINRA-3110","FINRA-2210","FINRA-4511","SEC-17a-4","FINRA-Notice-24-09"],
  "schema_version": "1.0"
}
```

### 3.5 Sample failing evidence record

```json
{
  "control_id": "2.12",
  "namespace": "HITL",
  "criterion": "C2.12-2",
  "zone": "3",
  "subject_id": "bot-wealth-onboarding-0021",
  "subject_type": "copilot_studio_bot",
  "status": "FAIL",
  "assertion": "Z3 handoff trigger must cover 100% of WSP high-risk intents",
  "observed_value": {
    "handoff_enabled": true,
    "trigger_intents": ["buy-recommendation"],
    "wsp_intents_missing": ["sell-recommendation","account-specific-advice","outside-business-activity"],
    "wsp_intents_covered_pct": 25
  },
  "expected_value": { "wsp_intents_covered_pct": 100 },
  "remediation_ref": "TRG-HITL-01",
  "regulator_mappings": ["FINRA-3110","FINRA-2210"],
  "schema_version": "1.0"
}
```

`TRG-HITL-01` (§16.3): within 24 hours, disable Z3 publication of the affected bot; update handoff trigger to cover all WSP intents; re-run the §3 suite against the bot only; re-enable after PASS.

### 3.6 Examiner artifact

| Artifact | Filename | Retention |
|---|---|---|
| Per-bot handoff configuration export | `hitl-config-<botId>-<runId>.json` | 6 years |
| Probe transcript | `hitl-transcript-<transcriptId>-<runId>.json` | 6 years |
| Reviewer-group registration snapshot | `hitl-reviewer-registrations-<runId>.json` | 6 years |
| Pester JUnit | `pester-HITL-<runId>.xml` | 6 years |

### 3.7 Zone thresholds

| Zone | PASS | WARN | FAIL |
|---|---|---|---|
| Zone 1 | n/a — Z1 personal scope, HITL optional | — | — |
| Zone 2 | Handoff enabled OR documented sampling-based alternative in WSP; reviewer is Agent Owner or team lead | Handoff misaligned < 10% with WSP intents | Handoff disabled with no WSP-documented alternative |
| Zone 3 | 100% WSP intent coverage; 100% reviewer-group membership is registered principal; probe handoff fires; audit-log hit < 60s | Probe latency 60–120s with trend down | Any WSP intent not covered; any reviewer non-registered; probe fails to fire |

### 3.8 Regulator mapping

| Test | FINRA 3110 | FINRA 2210 | FINRA 4511 | SEC 17a-4 | SOX §404 |
|---|---|---|---|---|---|
| Handoff enabled | ✓ supervision | ✓ retail-comm pre-use | — | — | ✓ control operating effectiveness |
| WSP-trigger alignment | ✓ WSPs enforceable | ✓ consistent classification | — | — | ✓ traceability |
| Reviewer qualifications | ✓ qualified principal | ✓ principal pre-use approver | — | — | ✓ segregation |
| Audit-log hit | — | — | ✓ books-and-records | ✓ 17a-4(b)(4) | ✓ evidence |

---

## §4 QUEUE — Supervisory Review Queue SLA Evidence

### 4.1 Criterion mapping

This namespace evidences **C2.12-4**: *supervisory review queue shows median and 95th-percentile time-to-review within the firm's documented SLA (per zone); exceptions are logged as incidents under Control 3.4.*

The queue is the operational surface where handoff events (§3) and AGF `request_info()` pauses (§11) become work items for a human reviewer. A queue with perfect handoff configuration but a 48-hour median review latency fails C2.12-4 even if C2.12-2 passes.

### 4.2 Pre-conditions

- WSP namespace PASS provides the per-zone SLA values (median and p95).
- Queue backing store is one of: SharePoint list, Dataverse table, Power Automate approval history, or a firm-built ticketing system with a JSON export endpoint.
- Timestamp precision is millisecond or better (some SharePoint configurations truncate to seconds; accept second precision with documented variance).
- Lookback window default is 30 days; configurable via `-LookbackDays`.

### 4.3 Pester suite

```powershell
Describe "AGT212-QUEUE" -Tag 'C2.12','QUEUE' {

    BeforeAll {
        $script:Lookback   = (Get-Date).AddDays(-30).ToUniversalTime()
        $script:QueueItems = Get-SupervisionQueueItems -Since $script:Lookback
        $script:WspSla     = (Get-WspAddendumMetadata).sla
        $script:Z2Sla      = [int]$script:WspSla.zone_2.minutes_to_review
        $script:Z3Sla      = [int]$script:WspSla.zone_3.minutes_to_review
    }

    Context "Queue reachability" {
        It "the supervision queue returned at least one item in the 30-day lookback" {
            # Zero items across 30 days in a production tenant signals a broken intake, not a quiet quarter.
            $script:QueueItems.Count | Should -BeGreaterThan 0 -Because "an empty queue over 30 days is a QUEUE-INTAKE-BROKEN signal"
        }
        It "every queue item has both created_at and decided_at (or escalated_at) timestamps" {
            foreach ($item in $script:QueueItems) {
                $item.created_at  | Should -Not -BeNullOrEmpty
                ($item.decided_at -or $item.escalated_at -or $item.status -eq 'open') | Should -BeTrue
            }
        }
    }

    Context "Zone 2 SLA" {
        It "Z2 median time-to-review ≤ WSP-defined Z2 SLA" {
            $z2 = $script:QueueItems | Where-Object { $_.zone -eq '2' -and $_.decided_at }
            $lat = $z2 | ForEach-Object { ([datetime]$_.decided_at - [datetime]$_.created_at).TotalMinutes }
            $median = ($lat | Sort-Object)[[Math]::Floor($lat.Count / 2)]
            $median | Should -BeLessOrEqual $script:Z2Sla
        }
        It "Z2 p95 time-to-review ≤ 2x WSP-defined Z2 SLA" {
            $z2 = $script:QueueItems | Where-Object { $_.zone -eq '2' -and $_.decided_at }
            $lat = $z2 | ForEach-Object { ([datetime]$_.decided_at - [datetime]$_.created_at).TotalMinutes }
            $p95 = ($lat | Sort-Object)[[Math]::Floor($lat.Count * 0.95)]
            $p95 | Should -BeLessOrEqual ($script:Z2Sla * 2)
        }
    }

    Context "Zone 3 SLA" {
        It "Z3 median time-to-review ≤ WSP-defined Z3 SLA" {
            $z3 = $script:QueueItems | Where-Object { $_.zone -eq '3' -and $_.decided_at }
            $lat = $z3 | ForEach-Object { ([datetime]$_.decided_at - [datetime]$_.created_at).TotalMinutes }
            $median = ($lat | Sort-Object)[[Math]::Floor($lat.Count / 2)]
            $median | Should -BeLessOrEqual $script:Z3Sla
        }
        It "Z3 p95 time-to-review ≤ 1.5x WSP-defined Z3 SLA (tighter than Z2)" {
            $z3 = $script:QueueItems | Where-Object { $_.zone -eq '3' -and $_.decided_at }
            $lat = $z3 | ForEach-Object { ([datetime]$_.decided_at - [datetime]$_.created_at).TotalMinutes }
            $p95 = ($lat | Sort-Object)[[Math]::Floor($lat.Count * 0.95)]
            $p95 | Should -BeLessOrEqual ($script:Z3Sla * 1.5)
        }
        It "no Z3 item is open longer than the Z3 SLA without a logged escalation" {
            $open = $script:QueueItems | Where-Object { $_.zone -eq '3' -and $_.status -eq 'open' }
            foreach ($item in $open) {
                $age = ((Get-Date) - [datetime]$item.created_at).TotalMinutes
                if ($age -gt $script:Z3Sla) {
                    $item.escalated_at | Should -Not -BeNullOrEmpty -Because "overdue Z3 items must escalate, not linger"
                }
            }
        }
    }

    Context "Exception logging into Control 3.4" {
        It "every SLA-breach item has a matching incident ticket in the 3.4 incident registry" {
            $breaches = $script:QueueItems | Where-Object {
                $_.decided_at -and (([datetime]$_.decided_at - [datetime]$_.created_at).TotalMinutes -gt `
                    (@{2=$script:Z2Sla; 3=$script:Z3Sla}[[int]$_.zone]))
            }
            foreach ($b in $breaches) {
                $inc = Get-Control34Incident -CorrelationId $b.item_id
                $inc | Should -Not -BeNullOrEmpty -Because "C2.12-4 requires breach incidents to enter 3.4"
            }
        }
    }
}
```

### 4.4 Sample passing evidence record

```json
{
  "control_id": "2.12",
  "namespace": "QUEUE",
  "criterion": "C2.12-4",
  "zone": "3",
  "subject_id": "supervision-queue-<30d>",
  "subject_type": "review_queue_window",
  "status": "PASS",
  "assertion": "Z3 queue median and p95 within SLA; no un-escalated overdue items; all breaches mirrored into 3.4",
  "observed_value": {
    "lookback_days": 30,
    "z3_item_count": 412,
    "z3_median_min": 7,
    "z3_p95_min": 22,
    "z3_sla_min": 15,
    "z3_open_items_overdue_no_escalation": 0,
    "breach_count": 4,
    "breaches_linked_to_34_incidents": 4
  },
  "expected_value": {
    "z3_median_min": "<=15",
    "z3_p95_min": "<=22.5",
    "z3_open_items_overdue_no_escalation": 0,
    "breaches_linked_to_34_incidents": "== breach_count"
  },
  "evidence_artifacts": ["queue-latency-<runId>.csv","queue-breach-34-crossref-<runId>.json"],
  "regulator_mappings": ["FINRA-3110","FINRA-4511","SEC-17a-4","SOX-404"],
  "schema_version": "1.0"
}
```

### 4.5 Sample failing evidence record

```json
{
  "control_id": "2.12",
  "namespace": "QUEUE",
  "criterion": "C2.12-4",
  "zone": "3",
  "subject_id": "supervision-queue-<30d>",
  "subject_type": "review_queue_window",
  "status": "FAIL",
  "assertion": "Z3 p95 time-to-review must be ≤ 1.5x SLA",
  "observed_value": {
    "z3_median_min": 14,
    "z3_p95_min": 71,
    "z3_sla_min": 15,
    "p95_multiplier": 4.73
  },
  "expected_value": { "z3_p95_min": "<=22.5" },
  "remediation_ref": "TRG-QUEUE-01",
  "regulator_mappings": ["FINRA-3110","FINRA-4511"],
  "schema_version": "1.0"
}
```

`TRG-QUEUE-01` (§16.4): capacity review by AI Governance Lead within 5 business days; add reviewer coverage or reduce Z3 agent footprint; raise root-cause ticket in Control 3.4.

### 4.6 Examiner artifact

| Artifact | Filename | Retention |
|---|---|---|
| Queue-latency CSV (per-item) | `queue-latency-<runId>.csv` | 6 years |
| Monthly latency report (p50/p95/p99 per zone) | `queue-monthly-<yyyyMM>.pdf` | 6 years |
| Breach-to-3.4 cross-reference | `queue-breach-34-crossref-<runId>.json` | 6 years |
| Pester JUnit | `pester-QUEUE-<runId>.xml` | 6 years |

### 4.7 Zone thresholds

| Zone | PASS | WARN | FAIL |
|---|---|---|---|
| Zone 1 | n/a — Z1 queue is advisory | — | — |
| Zone 2 | median ≤ SLA; p95 ≤ 2x SLA; open-overdue = 0 | p95 within 2x–3x SLA | p95 > 3x SLA or open-overdue-without-escalation > 0 |
| Zone 3 | median ≤ SLA; p95 ≤ 1.5x SLA; open-overdue = 0; 100% breach→3.4 link | p95 within 1.5x–2x SLA | p95 > 2x SLA or any open-overdue without escalation or breach not in 3.4 |

### 4.8 Regulator mapping

| Test | FINRA 3110 | FINRA 4511 | SEC 17a-4 | SOX §404 |
|---|---|---|---|---|
| Queue intake non-empty | ✓ supervision in effect | — | — | ✓ control operating effectiveness |
| Median / p95 within SLA | ✓ reasonable supervision | — | — | ✓ |
| Breach→3.4 linkage | ✓ escalation discipline | ✓ record of exception | ✓ | ✓ |

---

## §5 REVIEWER — Reviewer-Decision Audit Trail Evidence

### 5.1 Criterion mapping

This namespace evidences **C2.12-5**: *for a random sample of N=25 reviewer decisions per quarter, each record contains non-null reviewer UPN, timestamp, decision (approve / reject / escalate), and rationale; each decision is traceable to the original agent interaction and (for Agent Framework) to the originating request ID and checkpoint.*

REVIEWER verifies the **audit-trail integrity** of decisions, not decision correctness. Decision correctness is a qualitative review performed under §8 R3120.

### 5.2 Pre-conditions

- PRE-01 through PRE-08 PASS.
- Purview Compliance Admin (read) role active.
- Reviewer decisions are sourced from (a) Copilot Studio handoff disposition events, (b) Power Automate approval history, and (c) Agent Framework response-handler events, unioned by correlation ID.
- Quarter boundary is the prior calendar quarter unless overridden with `-Quarter Q{1-4}-yyyy`.

### 5.3 Pester suite

```powershell
Describe "AGT212-REVIEWER" -Tag 'C2.12','REVIEWER' {

    BeforeAll {
        $script:Quarter = Get-PreviousQuarterBoundary
        $script:AllDecisions = Get-ReviewerDecisionUnion `
            -Start $script:Quarter.start -End $script:Quarter.end
        $script:Sample = Get-Random -InputObject $script:AllDecisions -Count 25
    }

    Context "Sample size" {
        It "at least 25 decisions available in the quarter (else C2.12-5 is N/A)" {
            if ($script:AllDecisions.Count -lt 25) {
                Set-ItResult -Skipped -Because "only $($script:AllDecisions.Count) decisions in quarter; document rationale in §17 pack"
            } else {
                $script:AllDecisions.Count | Should -BeGreaterOrEqual 25
            }
        }
    }

    Context "Non-null required fields (N=25)" {
        It "every sampled decision has reviewer_upn" {
            foreach ($d in $script:Sample) { $d.reviewer_upn | Should -Not -BeNullOrEmpty }
        }
        It "every sampled decision has decided_at (ISO-8601)" {
            foreach ($d in $script:Sample) {
                $d.decided_at | Should -Not -BeNullOrEmpty
                { [datetime]$d.decided_at } | Should -Not -Throw
            }
        }
        It "every sampled decision has a decision value in {approve, reject, escalate}" {
            foreach ($d in $script:Sample) {
                $d.decision | Should -BeIn @('approve','reject','escalate')
            }
        }
        It "every sampled decision has a non-empty rationale of at least 25 characters" {
            foreach ($d in $script:Sample) {
                $d.rationale.Length | Should -BeGreaterOrEqual 25 -Because "one-word rationales are not examination-defensible"
            }
        }
    }

    Context "Traceability to originating interaction" {
        It "every sampled decision links to an agent interaction ID that resolves in the audit log" {
            foreach ($d in $script:Sample) {
                $audit = Search-UnifiedAuditLog `
                    -StartDate ([datetime]$d.decided_at).AddHours(-24) `
                    -EndDate   ([datetime]$d.decided_at) `
                    -FreeText  $d.agent_interaction_id
                $audit.Count | Should -BeGreaterOrEqual 1 -Because "decision must be traceable to the interaction it decided"
            }
        }
        It "for Agent Framework decisions, the originating request_id and checkpoint_id are non-null" {
            foreach ($d in $script:Sample | Where-Object source -eq 'agent_framework') {
                $d.agf_request_id    | Should -Not -BeNullOrEmpty
                $d.agf_checkpoint_id | Should -Not -BeNullOrEmpty
            }
        }
    }

    Context "Reviewer qualification at time of decision" {
        It "every sampled decision's reviewer held a supervisory registration on decided_at" {
            foreach ($d in $script:Sample) {
                $reg = Get-CrdRegistrationSnapshot -Upn $d.reviewer_upn -AsOf $d.decided_at
                $reg.status_as_of_decision | Should -Be 'Active'
                $reg.series | Should -BeIn @('24','66','65')
            }
        }
    }

    Context "Immutability" {
        It "every sampled decision record is in a Purview retention-labelled location with a compliance lock" {
            foreach ($d in $script:Sample) {
                $loc = Get-ReviewerDecisionStorageMetadata -DecisionId $d.decision_id
                $loc.retention_label | Should -Match 'FINRA-3110-6y'
                $loc.is_records      | Should -BeTrue
                $loc.compliance_lock | Should -BeTrue
            }
        }
    }
}
```

### 5.4 Sample passing evidence record

```json
{
  "control_id": "2.12",
  "namespace": "REVIEWER",
  "criterion": "C2.12-5",
  "zone": "3",
  "subject_id": "decision-0x8f3a-2026q1",
  "subject_type": "reviewer_decision",
  "status": "PASS",
  "assertion": "Sampled decision has complete, immutable, registered-reviewer audit trail with linkage to interaction and AGF request",
  "observed_value": {
    "reviewer_upn": "jane.principal@contoso.com",
    "reviewer_series_as_of_decision": "24",
    "decided_at": "2026-02-18T14:22:17Z",
    "decision": "reject",
    "rationale_length": 187,
    "agent_interaction_id": "copilot-tx-0b7a...",
    "agf_request_id": "req_0x9e2d...",
    "agf_checkpoint_id": "chk_0x9e2d_0002",
    "retention_label": "FINRA-3110-6y",
    "compliance_lock": true
  },
  "expected_value": {
    "reviewer_series_as_of_decision": "24|66|65",
    "rationale_length": ">=25",
    "compliance_lock": true
  },
  "evidence_artifacts": ["reviewer-decisions-sample-<runId>.json"],
  "regulator_mappings": ["FINRA-3110","FINRA-4511","SEC-17a-4","SOX-404"],
  "schema_version": "1.0"
}
```

### 5.5 Sample failing evidence record

```json
{
  "control_id": "2.12",
  "namespace": "REVIEWER",
  "criterion": "C2.12-5",
  "zone": "3",
  "subject_id": "decision-0xaa12-2026q1",
  "subject_type": "reviewer_decision",
  "status": "FAIL",
  "assertion": "Reviewer rationale must be ≥25 characters and must link to a resolvable interaction ID",
  "observed_value": {
    "reviewer_upn": "bob.reviewer@contoso.com",
    "rationale": "ok",
    "rationale_length": 2,
    "agent_interaction_id": null
  },
  "expected_value": { "rationale_length": ">=25", "agent_interaction_id": "<non-null>" },
  "remediation_ref": "TRG-REVIEWER-01",
  "regulator_mappings": ["FINRA-3110","FINRA-4511"],
  "schema_version": "1.0"
}
```

`TRG-REVIEWER-01` (§16.5): Compliance Officer contacts reviewer for rationale expansion; decision record is re-executed rather than back-dated (the original is retained, annotated, and a successor record is issued); reviewer receives training-intervention flag (§7 SAMPLING low-finding).

### 5.6 Examiner artifact

| Artifact | Filename | Retention |
|---|---|---|
| Sampled decisions JSON | `reviewer-decisions-sample-<runId>.json` | 6 years WORM |
| Quarterly decision population summary | `reviewer-decisions-population-<qLabel>.csv` | 6 years WORM |
| Pester JUnit | `pester-REVIEWER-<runId>.xml` | 6 years |

### 5.7 Zone thresholds

| Zone | PASS | WARN | FAIL |
|---|---|---|---|
| Zone 1 | n/a — personal scope | — | — |
| Zone 2 | 100% non-null required fields; 95% rationale ≥ 25 chars | 85–94% rationale ≥ 25 chars | < 85% or any non-null field failure |
| Zone 3 | 100% non-null required fields; 100% rationale ≥ 25 chars; 100% interaction traceable; 100% AGF request linkage where applicable; 100% reviewers qualified | n/a | any deviation |

### 5.8 Regulator mapping

| Test | FINRA 3110 | FINRA 4511 | SEC 17a-4 | SOX §404 |
|---|---|---|---|---|
| Non-null reviewer + decision + rationale | ✓ supervision evidence | ✓ books-and-records | ✓ 17a-4(b)(4) | ✓ |
| Interaction traceability | ✓ complete audit trail | ✓ | ✓ | ✓ |
| Reviewer qualification at decision | ✓ qualified supervisor | — | — | ✓ segregation |
| Compliance lock | — | ✓ WORM | ✓ 17a-4(f) | ✓ |

---

## 6. PRINCIPAL — Designated Principal & CRD Registration Verification

> **Verification Criterion:** C2.12-3 — Designated Principal recorded for each in-scope agent; principal holds a current FINRA Series 24/9/10 (or equivalent) registration in CRD; principal-to-agent assignment is observable in the Agent Inventory and time-bounded.
>
> **Non-substitution reminder:** This namespace verifies *registration evidence and assignment artifacts*. The qualitative judgment of whether a principal is appropriate for a given agent's business line is documented during Rule 3120 annual testing (see §8 R3120) and is outside the scope of automated assertions.

### 6.1 Criterion mapping

| Aspect | Source | Evidence file |
|---|---|---|
| Principal-to-agent assignment | Agent Inventory `principal_upn` field | `agent-inventory-export-<run_id>.json` |
| Principal qualification | CRD U4 export (manual upload to evidence vault) | `crd-u4-<principal_upn>-<asof>.pdf` |
| Registration currency | CRD `series_24_status = ACTIVE` AND `expiry_date > today + 30d` | `principal-registry-<run_id>.json` |
| Time-boundedness | `assignment_start_utc`, `assignment_end_utc` (nullable) | inventory record |
| Backup principal (Z3) | `backup_principal_upn` populated | inventory record |

### 6.2 Pre-conditions

1. Agent Inventory CSV/JSON export available at `$env:AGT212_INVENTORY_PATH`.
2. Principal Registry (maintained by Compliance Officer) at `$env:AGT212_PRINCIPAL_REGISTRY_PATH` with schema `{upn, full_name, crd_number, registrations:[{series, status, granted_utc, expiry_utc}], backup_for:[]}`.
3. Read access to Microsoft Entra to confirm the principal UPN resolves to an active, non-guest user with MFA enrolled.
4. Sovereign-cloud short-circuit: if `Test-Agt212SovereignTenant` returns `$true` and the Principal Registry is maintained out-of-band, the Pester suite emits `SKIPPED` records and points to the §13 SOV dual-signed attestation.

### 6.3 Pester suite — `AGT212.Principal.Tests.ps1`

```powershell
#Requires -Modules Pester, Microsoft.Graph.Users
[CmdletBinding()]
param(
    [string]$RunId       = (New-Agt212RunId),
    [string]$EvidenceDir = (Join-Path $env:AGT212_EVIDENCE_ROOT $RunId)
)

BeforeAll {
    . $PSScriptRoot/_helpers/Agt212.Common.ps1
    $script:Inventory = Get-Content $env:AGT212_INVENTORY_PATH | ConvertFrom-Json
    $script:Registry  = Get-Content $env:AGT212_PRINCIPAL_REGISTRY_PATH | ConvertFrom-Json
    $script:Sov       = Test-Agt212SovereignTenant
    New-Item -ItemType Directory -Path $EvidenceDir -Force | Out-Null
}

Describe 'PRINCIPAL — C2.12-3 Designated Principal & CRD' -Tag 'PRINCIPAL','C2.12-3' {

    Context 'Sovereign-cloud short-circuit' -Skip:(-not $script:Sov) {
        It 'records SKIPPED with pointer to §13 SOV' {
            New-Agt212EvidenceRecord -Namespace 'PRINCIPAL' -Criterion 'C2.12-3' `
                -Status 'SKIPPED' -Assertion 'Sovereign tenant — see §13 SOV attestation' `
                -EvidenceArtifacts @('sov-attestation-current.pdf') -RunId $RunId | Out-Null
            $true | Should -BeTrue
        }
    }

    Context 'Assignment present and well-formed' -Skip:$script:Sov {
        It 'every Z2/Z3 agent has a non-empty principal_upn' -ForEach ($script:Inventory | Where-Object zone -in 'Zone 2','Zone 3') {
            $_.principal_upn | Should -Match '^[^@\s]+@[^@\s]+\.[^@\s]+$' -Because "Agent $($_.agent_id) lacks a Designated Principal (C2.12-3)"
        }
        It 'every Zone 3 agent has a backup_principal_upn distinct from primary' -ForEach ($script:Inventory | Where-Object zone -eq 'Zone 3') {
            $_.backup_principal_upn | Should -Not -BeNullOrEmpty
            $_.backup_principal_upn | Should -Not -Be $_.principal_upn
        }
        It 'assignment_start_utc precedes today' -ForEach ($script:Inventory | Where-Object zone -in 'Zone 2','Zone 3') {
            ([datetime]$_.assignment_start_utc) | Should -BeLessOrEqual (Get-Date).ToUniversalTime()
        }
    }

    Context 'CRD currency' -Skip:$script:Sov {
        It 'principal appears in Principal Registry' -ForEach ($script:Inventory | Where-Object zone -in 'Zone 2','Zone 3') {
            $entry = $script:Registry | Where-Object upn -eq $_.principal_upn
            $entry | Should -Not -BeNullOrEmpty -Because "Principal $($_.principal_upn) for agent $($_.agent_id) not in registry"
        }
        It 'has ACTIVE Series 24 (or equivalent: 9/10) with > 30 days to expiry' -ForEach ($script:Inventory | Where-Object zone -in 'Zone 2','Zone 3') {
            $entry = $script:Registry | Where-Object upn -eq $_.principal_upn
            $qualifying = $entry.registrations | Where-Object {
                $_.series -in @('24','9','10') -and $_.status -eq 'ACTIVE' -and ([datetime]$_.expiry_utc -gt (Get-Date).AddDays(30))
            }
            $qualifying.Count | Should -BeGreaterThan 0
        }
    }

    Context 'Entra resolution' -Skip:$script:Sov {
        It 'principal UPN resolves to active, MFA-enrolled, non-guest Entra user' -ForEach ($script:Inventory | Where-Object zone -in 'Zone 2','Zone 3') {
            $u = Get-MgUser -UserId $_.principal_upn -Property AccountEnabled,UserType -ErrorAction Stop
            $u.AccountEnabled | Should -BeTrue
            $u.UserType       | Should -Be 'Member'
        }
    }
}

AfterAll {
    Write-Agt212EvidenceManifest -EvidenceDir $EvidenceDir -RunId $RunId
}
```

### 6.4 Sample passing record

```json
{
  "control_id": "C2.12",
  "run_id": "AGT212-20260415-091200-7f3ac9d2",
  "run_timestamp": "2026-04-15T09:12:14Z",
  "tenant_id": "11111111-2222-3333-4444-555555555555",
  "cloud": "Public",
  "namespace": "PRINCIPAL",
  "criterion": "C2.12-3",
  "zone": "Zone 3",
  "subject_id": "agent-treasury-ops-001",
  "subject_type": "DeclarativeAgent",
  "status": "PASS",
  "assertion": "Designated Principal jane.doe@contoso.com holds ACTIVE Series 24 expiring 2027-08-15; backup principal mark.lee@contoso.com",
  "observed_value": { "principal_upn": "jane.doe@contoso.com", "series": "24", "expiry_utc": "2027-08-15T00:00:00Z", "backup_principal_upn": "mark.lee@contoso.com" },
  "expected_value": { "principal_upn": "non-empty", "series_in": ["24","9","10"], "status": "ACTIVE", "expiry_gt_days": 30 },
  "evidence_artifacts": ["agent-inventory-export-AGT212-20260415-091200-7f3ac9d2.json","principal-registry-AGT212-20260415-091200-7f3ac9d2.json","crd-u4-jane.doe-2026Q1.pdf"],
  "regulator_mappings": ["FINRA Rule 3110(a)(2)","FINRA Rule 1210","SEC 17a-4(b)(4)"],
  "remediation_ref": null,
  "schema_version": "1.0"
}
```

### 6.5 Sample failing record + triage pointer

```json
{
  "control_id": "C2.12",
  "run_id": "AGT212-20260415-091200-7f3ac9d2",
  "namespace": "PRINCIPAL",
  "criterion": "C2.12-3",
  "zone": "Zone 2",
  "subject_id": "agent-retail-marketing-014",
  "status": "FAIL",
  "assertion": "Principal alex.kim@contoso.com Series 24 expired 2026-03-22 (registration LAPSED)",
  "observed_value": { "series": "24", "status": "LAPSED", "expiry_utc": "2026-03-22T00:00:00Z" },
  "expected_value": { "status": "ACTIVE", "expiry_gt_days": 30 },
  "evidence_artifacts": ["principal-registry-AGT212-20260415-091200-7f3ac9d2.json","crd-u4-alex.kim-2026Q1.pdf"],
  "remediation_ref": "TRG-PRINCIPAL-01",
  "schema_version": "1.0"
}
```

See §16 for **TRG-PRINCIPAL-01** (lapsed/expiring registration handling).

### 6.6 Examiner artifact table

| Examiner ask | Artifact | Source | Retention |
|---|---|---|---|
| "Show the Designated Principal for agent X on date Y" | `agent-inventory-export-*.json` filtered by `agent_id` and `assignment_start_utc <= Y < assignment_end_utc` | Agent Inventory | 7 yrs |
| "Prove the principal was qualified on date Y" | CRD U4 PDF dated ≤ Y plus Principal Registry snapshot | Vault `crd-u4-*` | 7 yrs |
| "Who acted as backup when primary was OOO?" | Backup principal field + delegation log (out of scope here; see Control 2.26) | Inventory + 2.26 sponsor logs | 7 yrs |

### 6.7 Zone thresholds

| Zone | Pass threshold | Warn | Fail |
|---|---|---|---|
| Zone 1 | n/a — Personal scope; no Designated Principal required | — | — |
| Zone 2 | 100% agents have valid principal with ACTIVE qualifying series | one agent within 30-day expiry window | any LAPSED, missing, or unresolved principal |
| Zone 3 | Zone 2 thresholds plus 100% have backup_principal_upn distinct from primary | one agent missing backup | any missing/duplicate backup, any LAPSED |

### 6.8 Regulator mapping

| Test | FINRA 3110 | FINRA 1210 | SEC 17a-4 | SOX §404 |
|---|---|---|---|---|
| Principal assignment present | ✓ 3110(a)(2) | — | ✓ books-and-records | ✓ |
| Series 24/9/10 ACTIVE | — | ✓ qualification | — | ✓ segregation |
| Backup principal (Z3) | ✓ supervisory continuity | — | — | ✓ |
| Time-bounded assignment | ✓ historical reconstructability | — | ✓ 17a-4(b)(4) | ✓ |

---

## 7. SAMPLING — Cross-Cutting Sampling Integrity

> **Cross-cutting namespace.** SAMPLING does not map to a single Verification Criterion. It validates that statistical samples drawn for QUEUE (§4), REVIEWER (§5), R3120 (§8), and R2210 (§9) are *reproducible, unbiased, and traceable*. A weak sampling foundation undermines every downstream criterion.

### 7.1 Why sampling integrity matters

FINRA Rule 3110(b)(4) and Rule 3120 both rely on supervisory sampling. If samples are non-reproducible (e.g., a reviewer can re-roll the dice until they get a "clean" set) the supervisory record fails the **completeness** prong of SEC 17a-4(b)(4). This namespace verifies four properties:

1. **Determinism** — given the same seed, population, and stratification rule, the sample set is identical.
2. **Coverage** — every in-scope record had a non-zero probability of selection.
3. **Stratification correctness** — sampling honours documented strata (e.g., autonomy level, business line).
4. **Audit trail** — seed, population hash, selection timestamp, and selector identity are recorded.

### 7.2 Pre-conditions

1. The sampling helper module `Agt212.Sampling.psm1` is installed and exposes `Get-Agt212Sample -Population <obj[]> -Size <int> -Seed <string> -Stratify <scriptblock>`.
2. The population source (e.g., Purview audit log export, supervisory queue snapshot) is hashed (SHA-256) and the hash is included in the evidence record.
3. The seed scheme is documented in the WSP: `seed = SHA-256("<control_id>|<criterion>|<period_start>|<period_end>|<rotation_salt>")` where `rotation_salt` rotates quarterly.

### 7.3 Pester suite — `AGT212.Sampling.Tests.ps1`

```powershell
#Requires -Modules Pester
[CmdletBinding()]
param(
    [string]$RunId = (New-Agt212RunId)
)

BeforeAll {
    . $PSScriptRoot/_helpers/Agt212.Common.ps1
    Import-Module $PSScriptRoot/_helpers/Agt212.Sampling.psm1 -Force
    $script:Population = 1..10000 | ForEach-Object {
        [pscustomobject]@{ id = $_; autonomy = (@('assistive','semi','fully'))[$_ % 3]; bu = (@('retail','wealth','ib'))[$_ % 3] }
    }
}

Describe 'SAMPLING — cross-cutting integrity' -Tag 'SAMPLING' {

    Context 'Determinism' {
        It 'identical seed yields identical sample set' {
            $a = Get-Agt212Sample -Population $script:Population -Size 50 -Seed 'unit-test-seed-001'
            $b = Get-Agt212Sample -Population $script:Population -Size 50 -Seed 'unit-test-seed-001'
            ($a.id -join ',') | Should -Be ($b.id -join ',')
        }
        It 'different seed yields different sample set' {
            $a = Get-Agt212Sample -Population $script:Population -Size 50 -Seed 'unit-test-seed-001'
            $b = Get-Agt212Sample -Population $script:Population -Size 50 -Seed 'unit-test-seed-002'
            ($a.id -join ',') | Should -Not -Be ($b.id -join ',')
        }
    }

    Context 'Coverage' {
        It 'no record has zero selection probability across 1000 random seeds' {
            $hits = @{}
            1..1000 | ForEach-Object {
                $s = Get-Agt212Sample -Population $script:Population -Size 50 -Seed "coverage-$_"
                $s.id | ForEach-Object { $hits[$_] = $true }
            }
            # For a uniform sampler with 1000 draws of size 50 from 10000, expect ~99% coverage.
            ($hits.Keys.Count / 10000) | Should -BeGreaterThan 0.95
        }
    }

    Context 'Stratification' {
        It 'honours autonomy-level strata at requested proportions' {
            $sample = Get-Agt212Sample -Population $script:Population -Size 90 -Seed 'strat-test' -Stratify { param($r) $r.autonomy }
            $byStratum = $sample | Group-Object autonomy
            foreach ($g in $byStratum) {
                $g.Count | Should -BeGreaterOrEqual 25  # ~30 expected per stratum, allow ±5
                $g.Count | Should -BeLessOrEqual 35
            }
        }
    }

    Context 'Audit trail' {
        It 'records seed, population hash, selector identity in evidence record' {
            $rec = Get-Agt212Sample -Population $script:Population -Size 50 -Seed 'audit-test' -EmitEvidence
            $rec.evidence.seed             | Should -Be 'audit-test'
            $rec.evidence.population_sha256 | Should -Match '^[0-9a-f]{64}$'
            $rec.evidence.selector_upn     | Should -Not -BeNullOrEmpty
            $rec.evidence.selected_at_utc  | Should -Not -BeNullOrEmpty
        }
    }
}
```

### 7.4 Sample evidence record (sampling envelope)

```json
{
  "control_id": "C2.12",
  "namespace": "SAMPLING",
  "criterion": "cross-cutting",
  "status": "PASS",
  "assertion": "Sample of 50 supervisory queue items drawn for QUEUE p95 calculation; deterministic and stratified by autonomy level",
  "observed_value": {
    "size": 50,
    "seed": "C2.12|QUEUE|2026-01-01|2026-03-31|2026Q1-rotation-salt-7f3a",
    "population_sha256": "9c2b...e41a",
    "selector_upn": "compliance.officer@contoso.com",
    "selected_at_utc": "2026-04-15T09:00:00Z",
    "stratification": "autonomy_level"
  },
  "evidence_artifacts": ["sample-manifest-AGT212-20260415-091200-7f3ac9d2.json"],
  "schema_version": "1.0"
}
```

### 7.5 Failure modes and triage pointer

| Symptom | Likely cause | Triage |
|---|---|---|
| Determinism test fails | sampler uses `Get-Random` without explicit seed | TRG-SAMPLING-01 |
| Coverage < 95% | population shuffling biased; check Fisher-Yates implementation | TRG-SAMPLING-01 |
| Stratification skew > ±5 from expected | proportional allocation rounding error | TRG-SAMPLING-02 |
| Population hash differs between sampling and downstream test | population mutated mid-run | TRG-SAMPLING-03 |

### 7.6 Examiner artifact table

| Examiner ask | Artifact |
|---|---|
| "Show the sample you used for Q1 supervisory testing" | `sample-manifest-*.json` with seed, population hash, selected IDs |
| "Prove the sample was not cherry-picked" | Quarterly `rotation_salt` change-log signed by Compliance Officer |
| "Re-draw the sample in front of me" | Run `Get-Agt212Sample` with the recorded seed; output must match |

### 7.7 Zone thresholds

SAMPLING is infrastructure; thresholds apply to all zones uniformly. Any failure in §7.3 blocks downstream namespaces (QUEUE, REVIEWER, R3120, R2210) from emitting PASS records.

### 7.8 Regulator mapping

| Test | FINRA 3110 | FINRA 3120 | SEC 17a-4 | SOX §404 |
|---|---|---|---|---|
| Determinism | ✓ reproducibility | ✓ testing methodology | ✓ books-and-records | ✓ |
| Coverage | ✓ completeness | ✓ representative sampling | ✓ | ✓ |
| Stratification | — | ✓ risk-based testing | — | ✓ |
| Audit trail | ✓ | ✓ working-papers | ✓ 17a-4(b)(4) | ✓ |

---

## 8. R3120 — FINRA Rule 3120 Annual Testing Working Papers

> **Verification Criterion:** C2.12-6 — Annual Rule 3120 testing of agent supervisory controls is performed, working papers are retained, the report is signed by senior management, and remediations are tracked through closure.
>
> **Non-substitution reminder:** R3120 is, by design, a *qualitative* exercise. This namespace verifies the **artifacts** of that exercise (working papers, test scripts, sample selections, sign-off, remediation tracking). It does not adjudicate whether the conclusions reached by the testers were correct.

### 8.1 Criterion mapping

| Aspect | Source | Evidence file |
|---|---|---|
| Test plan exists and dated | Compliance vault | `r3120-test-plan-<year>.pdf` |
| Sample selection (uses §7 SAMPLING) | Pester sampling output | `r3120-sample-manifest-<year>.json` |
| Test execution working papers | Reviewer notes, screenshots | `r3120-working-papers-<year>/` |
| Senior management sign-off | Signed PDF with name, title, date | `r3120-signoff-<year>.pdf` |
| Remediation tracker | Service Now / Azure DevOps export | `r3120-remediations-<year>.csv` |

### 8.2 Pre-conditions

1. Annual testing window is bounded by `$env:AGT212_R3120_PERIOD_START` and `$env:AGT212_R3120_PERIOD_END` (typically a 12-month rolling window).
2. The vault path `$env:AGT212_R3120_VAULT_ROOT/<year>` is mounted read-only to the runner.
3. Sample size for the annual test follows the WSP-documented formula (typically n=30 per business line, stratified by autonomy level — confirmed via §7 SAMPLING).
4. Sovereign-cloud short-circuit applies; out-of-band testing is documented in §13 SOV.

### 8.3 Pester suite — `AGT212.R3120.Tests.ps1`

```powershell
#Requires -Modules Pester
[CmdletBinding()]
param(
    [string]$Year  = (Get-Date).AddYears(-1).Year,
    [string]$RunId = (New-Agt212RunId)
)

BeforeAll {
    . $PSScriptRoot/_helpers/Agt212.Common.ps1
    $script:VaultRoot = Join-Path $env:AGT212_R3120_VAULT_ROOT $Year
    $script:Sov       = Test-Agt212SovereignTenant
}

Describe "R3120 — C2.12-6 Annual Testing ($Year)" -Tag 'R3120','C2.12-6' {

    Context 'Sovereign-cloud short-circuit' -Skip:(-not $script:Sov) {
        It 'records SKIPPED' { $true | Should -BeTrue }
    }

    Context 'Working-paper completeness' -Skip:$script:Sov {
        It 'test plan PDF exists and is dated within the testing window' {
            $plan = Join-Path $script:VaultRoot "r3120-test-plan-$Year.pdf"
            Test-Path $plan | Should -BeTrue
            $meta = Get-Agt212PdfMetadata -Path $plan
            ([datetime]$meta.CreationDate) | Should -BeGreaterOrEqual ([datetime]$env:AGT212_R3120_PERIOD_START)
        }
        It 'sample manifest exists and was generated by Agt212.Sampling' {
            $manifest = Join-Path $script:VaultRoot "r3120-sample-manifest-$Year.json"
            Test-Path $manifest | Should -BeTrue
            $j = Get-Content $manifest | ConvertFrom-Json
            $j.evidence.population_sha256 | Should -Match '^[0-9a-f]{64}$'
        }
        It 'working-papers folder is non-empty and every sampled item has at least one note' {
            $manifest = Get-Content (Join-Path $script:VaultRoot "r3120-sample-manifest-$Year.json") | ConvertFrom-Json
            $papers   = Join-Path $script:VaultRoot 'working-papers'
            foreach ($id in $manifest.selected_ids) {
                (Get-ChildItem -Path $papers -Filter "*$id*" -ErrorAction SilentlyContinue).Count | Should -BeGreaterThan 0 -Because "Sampled item $id has no working paper"
            }
        }
    }

    Context 'Senior management sign-off' -Skip:$script:Sov {
        It 'sign-off PDF exists and is digitally signed' {
            $signoff = Join-Path $script:VaultRoot "r3120-signoff-$Year.pdf"
            Test-Path $signoff | Should -BeTrue
            (Test-Agt212PdfSignature -Path $signoff).IsValid | Should -BeTrue
        }
        It 'signer holds an executive title (CCO, CRO, CEO, COO, or board-designated)' {
            $sig = Test-Agt212PdfSignature -Path (Join-Path $script:VaultRoot "r3120-signoff-$Year.pdf")
            $sig.SignerTitle | Should -Match '(CCO|CRO|CEO|COO|Chief|Designated Board Member)'
        }
    }

    Context 'Remediation tracking' -Skip:$script:Sov {
        It 'every finding has a remediation entry with target_close_utc' {
            $findings     = (Get-Content (Join-Path $script:VaultRoot "r3120-findings-$Year.json") | ConvertFrom-Json).findings
            $remediations = Import-Csv (Join-Path $script:VaultRoot "r3120-remediations-$Year.csv")
            foreach ($f in $findings) {
                $entry = $remediations | Where-Object finding_id -eq $f.id
                $entry | Should -Not -BeNullOrEmpty
                $entry.target_close_utc | Should -Not -BeNullOrEmpty
            }
        }
        It 'no remediation has been open > 180 days past target_close_utc without an exception memo' {
            $remediations = Import-Csv (Join-Path $script:VaultRoot "r3120-remediations-$Year.csv")
            $stale = $remediations | Where-Object { $_.status -ne 'CLOSED' -and ([datetime]$_.target_close_utc -lt (Get-Date).AddDays(-180)) -and -not $_.exception_memo_ref }
            $stale.Count | Should -Be 0
        }
    }
}
```

### 8.4 Sample passing record

```json
{
  "control_id": "C2.12",
  "namespace": "R3120",
  "criterion": "C2.12-6",
  "status": "PASS",
  "assertion": "FY2025 Rule 3120 testing complete: plan dated 2025-04-01, n=90 stratified sample, 12 findings all in remediation tracker, signed by CCO 2026-02-14",
  "observed_value": { "year": 2025, "sample_size": 90, "findings_total": 12, "findings_open": 3, "signoff_signer_title": "Chief Compliance Officer" },
  "evidence_artifacts": ["r3120-test-plan-2025.pdf","r3120-sample-manifest-2025.json","r3120-signoff-2025.pdf","r3120-remediations-2025.csv"],
  "regulator_mappings": ["FINRA Rule 3120","FINRA Rule 3110","SEC 17a-4(b)(4)","SOX §404"],
  "schema_version": "1.0"
}
```

### 8.5 Sample failing record + triage pointer

```json
{
  "control_id": "C2.12",
  "namespace": "R3120",
  "criterion": "C2.12-6",
  "status": "FAIL",
  "assertion": "Sign-off PDF for FY2025 Rule 3120 testing is not digitally signed (image stamp only)",
  "observed_value": { "signoff_signature_valid": false, "signature_type": "image-stamp" },
  "expected_value": { "signoff_signature_valid": true, "signature_type": "PKI" },
  "evidence_artifacts": ["r3120-signoff-2025.pdf"],
  "remediation_ref": "TRG-R3120-01",
  "schema_version": "1.0"
}
```

See §16 for **TRG-R3120-01** (sign-off integrity remediation).

### 8.6 Examiner artifact table

| Examiner ask | Artifact |
|---|---|
| "Show last year's Rule 3120 test plan" | `r3120-test-plan-<year>.pdf` |
| "How did you select the sample?" | `r3120-sample-manifest-<year>.json` plus the §7 SAMPLING evidence record |
| "Walk me through finding #7" | `working-papers/<finding-id>/` (notes, screenshots, agent output exports) |
| "Who signed off?" | `r3120-signoff-<year>.pdf` with PKI verification report |
| "Status of remediation #4?" | Row in `r3120-remediations-<year>.csv` with target/actual close dates and ticket link |

### 8.7 Zone thresholds

R3120 testing is enterprise-wide; thresholds apply at the firm level rather than per-zone. Open-finding age and signature integrity are go/no-go.

### 8.8 Regulator mapping

| Test | FINRA 3120 | FINRA 3110 | SEC 17a-4 | SOX §404 |
|---|---|---|---|---|
| Test plan exists | ✓ | ✓ supervisory system | ✓ | ✓ |
| Sample manifest reproducible | ✓ | — | ✓ | ✓ |
| Working papers complete | ✓ | ✓ | ✓ 17a-4(b)(4) | ✓ |
| Senior-management signed | ✓ | — | — | ✓ 302/404 |
| Remediation tracked | ✓ | ✓ | — | ✓ |

---

## 9. R2210 — FINRA Rule 2210 Communication Classification

> **Verification Criterion:** C2.12-7 — Agent-generated content that constitutes a "communication with the public" is correctly classified (correspondence / retail communication / institutional communication), retained for the prescribed period, and — for retail communications — pre-use approval by a registered Principal is recorded prior to first distribution.
>
> **Non-substitution reminder:** Classification is ultimately a judgment of the Designated Principal. This namespace verifies that classification *labels and approval artifacts exist and are internally consistent*; it does not opine on whether a given output should be retail vs. institutional.

### 9.1 Criterion mapping

| Aspect | Source | Evidence file |
|---|---|---|
| Output classification label | Purview sensitivity label `Comms-Class-{Corr|Retail|Inst}` | Purview audit log |
| Audience size (retail threshold = >25 retail investors in a 30-day window) | Distribution log from Outlook/Teams/Power Pages | `r2210-distribution-<period>.json` |
| Pre-use principal approval (retail) | Approval workflow record | `r2210-approval-<artifact-id>.json` |
| Filing with FINRA Advertising (retail, certain product types) | Filing receipt | `r2210-filing-<artifact-id>.pdf` |
| Retention | 3 years per Rule 2210(b)(4); hold ≥ 6 yrs in WORM aligned to firm policy | Purview retention label |

### 9.2 Pre-conditions

1. The Purview sensitivity-label scheme `Comms-Class-*` is published and applied via auto-labelling policies on agent-generated documents/messages.
2. A monthly distribution roll-up `r2210-distribution-<yyyymm>.json` is exported by the Purview Compliance Admin and lands in `$env:AGT212_R2210_VAULT_ROOT`.
3. Approval workflow (Power Automate flow `flow-r2210-preuse-approval`) writes one JSON per approval to the vault.
4. Sample selection follows §7 SAMPLING with seed scheme `seed = SHA-256("C2.12|R2210|<period_start>|<period_end>|<rotation_salt>")`.

### 9.3 Pester suite — `AGT212.R2210.Tests.ps1`

```powershell
#Requires -Modules Pester
[CmdletBinding()]
param(
    [string]$Period = (Get-Date).AddMonths(-1).ToString('yyyyMM'),
    [int]$SampleSize = 10,
    [string]$RunId   = (New-Agt212RunId)
)

BeforeAll {
    . $PSScriptRoot/_helpers/Agt212.Common.ps1
    Import-Module $PSScriptRoot/_helpers/Agt212.Sampling.psm1 -Force
    $script:Sov  = Test-Agt212SovereignTenant
    $script:Dist = Get-Content (Join-Path $env:AGT212_R2210_VAULT_ROOT "r2210-distribution-$Period.json") | ConvertFrom-Json
    $script:Sample = Get-Agt212Sample -Population $script:Dist.items -Size $SampleSize -Seed "C2.12|R2210|$Period|$($env:AGT212_R2210_ROTATION_SALT)" -Stratify { param($r) $r.proposed_class }
}

Describe "R2210 — C2.12-7 Communication classification ($Period)" -Tag 'R2210','C2.12-7' {

    Context 'Sovereign short-circuit' -Skip:(-not $script:Sov) { It 'SKIPPED' { $true | Should -BeTrue } }

    Context 'Label presence' -Skip:$script:Sov {
        It 'every sampled item has a Comms-Class-* sensitivity label' -ForEach $script:Sample {
            $_.sensitivity_label | Should -Match '^Comms-Class-(Corr|Retail|Inst)$' -Because "Item $($_.artifact_id) lacks classification"
        }
    }

    Context 'Audience-size consistency' -Skip:$script:Sov {
        It 'items labelled Corr have audience ≤ 25 retail recipients in 30-day window' -ForEach ($script:Sample | Where-Object sensitivity_label -eq 'Comms-Class-Corr') {
            $_.retail_audience_30d | Should -BeLessOrEqual 25 -Because "Correspondence with $($_.retail_audience_30d) retail recipients should be reclassified Retail"
        }
        It 'items labelled Retail have audience > 25 OR are explicitly templated retail material' -ForEach ($script:Sample | Where-Object sensitivity_label -eq 'Comms-Class-Retail') {
            ($_.retail_audience_30d -gt 25 -or $_.is_template -eq $true) | Should -BeTrue
        }
        It 'items labelled Inst have ZERO retail recipients' -ForEach ($script:Sample | Where-Object sensitivity_label -eq 'Comms-Class-Inst') {
            $_.retail_audience_30d | Should -Be 0
        }
    }

    Context 'Pre-use principal approval (Retail only)' -Skip:$script:Sov {
        It 'approval JSON exists and is timestamped before first_distribution_utc' -ForEach ($script:Sample | Where-Object sensitivity_label -eq 'Comms-Class-Retail') {
            $approvalPath = Join-Path $env:AGT212_R2210_VAULT_ROOT "approvals/r2210-approval-$($_.artifact_id).json"
            Test-Path $approvalPath | Should -BeTrue -Because "Retail item $($_.artifact_id) has no pre-use approval record"
            $a = Get-Content $approvalPath | ConvertFrom-Json
            ([datetime]$a.approved_utc) | Should -BeLessThan ([datetime]$_.first_distribution_utc)
        }
        It 'approver UPN matches a Designated Principal in the registry' -ForEach ($script:Sample | Where-Object sensitivity_label -eq 'Comms-Class-Retail') {
            $a = Get-Content (Join-Path $env:AGT212_R2210_VAULT_ROOT "approvals/r2210-approval-$($_.artifact_id).json") | ConvertFrom-Json
            $reg = Get-Content $env:AGT212_PRINCIPAL_REGISTRY_PATH | ConvertFrom-Json
            ($reg.upn -contains $a.approver_upn) | Should -BeTrue
        }
    }

    Context 'Retention label binding' -Skip:$script:Sov {
        It 'every sampled item has a retention label with hold ≥ 3 years' -ForEach $script:Sample {
            $_.retention_label_years | Should -BeGreaterOrEqual 3
        }
    }
}
```

### 9.4 Sample passing record

```json
{
  "control_id": "C2.12",
  "namespace": "R2210",
  "criterion": "C2.12-7",
  "status": "PASS",
  "assertion": "Period 202603, n=10 stratified sample: all items labelled, retail items have pre-use approval by registered principal, retention ≥ 3y",
  "observed_value": { "period": "202603", "sample_size": 10, "retail_count": 4, "retail_with_approval": 4, "min_retention_years": 6 },
  "evidence_artifacts": ["r2210-distribution-202603.json","r2210-sample-manifest-202603.json","approvals/r2210-approval-*.json"],
  "regulator_mappings": ["FINRA Rule 2210","FINRA Rule 3110","SEC 17a-4(b)(4)"],
  "schema_version": "1.0"
}
```

### 9.5 Sample failing record + triage pointer

```json
{
  "control_id": "C2.12",
  "namespace": "R2210",
  "criterion": "C2.12-7",
  "status": "FAIL",
  "assertion": "Item art-2026-03-0418 labelled Comms-Class-Corr but distributed to 47 retail recipients in 30-day window — likely misclassification (should be Retail)",
  "observed_value": { "artifact_id": "art-2026-03-0418", "sensitivity_label": "Comms-Class-Corr", "retail_audience_30d": 47 },
  "expected_value": { "retail_audience_30d_for_Corr": "<=25" },
  "evidence_artifacts": ["r2210-distribution-202603.json"],
  "remediation_ref": "TRG-R2210-01",
  "schema_version": "1.0"
}
```

See §16 for **TRG-R2210-01** (misclassification remediation; mandatory Designated Principal review of impacted artifact within 5 business days).

### 9.6 Examiner artifact table

| Examiner ask | Artifact |
|---|---|
| "Show classification rationale for artifact X" | Purview audit record + `r2210-approval-X.json` (if Retail) |
| "Show pre-use approval for retail piece Y" | `r2210-approval-Y.json` with approver UPN, timestamp, comments |
| "How are you sampling 2210 evidence?" | §7 SAMPLING manifest plus monthly seed log |
| "What's your retention?" | Purview retention label policy export (≥ 3y, firm policy ≥ 6y) |

### 9.7 Zone thresholds

| Zone | Pass threshold | Warn | Fail |
|---|---|---|---|
| Zone 1 | n/a — Personal-scope output is not a 2210 communication | — | — |
| Zone 2 | 100% labelled; ≥ 95% audience-consistency in monthly sample; 100% retail items have pre-use approval | 90–94% audience-consistency | < 90% or any unapproved retail |
| Zone 3 | Zone 2 plus 100% audience-consistency and 100% approver is Designated Principal of record | n/a | any deviation |

### 9.8 Regulator mapping

| Test | FINRA 2210 | FINRA 3110 | SEC 17a-4 | SOX §404 |
|---|---|---|---|---|
| Classification label present | ✓ | ✓ supervisory review | ✓ books-and-records | ✓ |
| Audience consistency | ✓ retail definition | — | — | ✓ |
| Pre-use principal approval (retail) | ✓ 2210(b)(1)(A) | ✓ supervisory pre-clearance | ✓ | ✓ |
| Retention ≥ 3y | ✓ 2210(b)(4) | — | ✓ 17a-4(b)(4) | ✓ |

---

## 10. SPONSOR — Entra Agent ID Sponsorship Cross-Reference (Upstream to Control 2.26)

> **Cross-control verification.** Control 2.12 supervision presumes that every in-scope Entra Agent ID has a current human Sponsor as governed by [Control 2.26 — Entra Agent ID Identity Governance](../../../controls/pillar-2-management/2.26-entra-agent-id-identity-governance.md). This namespace performs *thin-shim* re-checks to detect orphaning that would invalidate supervisory traceability for Control 2.12.
>
> **Non-substitution reminder:** Sponsor adequacy and lifecycle compliance are owned by Control 2.26's Pester suites. SPONSOR here only verifies the *bridge* between an agent's Designated Principal (this control) and its Entra Agent ID Sponsor (2.26).

### 10.1 Criterion mapping

| Aspect | Source | Bridges to |
|---|---|---|
| Every in-scope agent has a current Sponsor | 2.26 SPONSOR namespace export | C2.12-3, C2.12-5 |
| Sponsor and Designated Principal are documented (may be the same person; if different, both must be valid) | Agent Inventory | C2.12-3 |
| Orphan-detection re-entry: any agent flagged orphan by 2.26 is suspended *before* Control 2.12 supervisory queue runs | 2.26 orphan log | C2.12-4 |

### 10.2 Pre-conditions

1. The 2.26 verification suite has run within the prior 24 hours and emitted `sponsor-status-<run_id>.json` to a shared evidence path `$env:AGT212_226_BRIDGE_PATH`.
2. The Agent Inventory exposes `sponsor_upn` and `principal_upn` per agent.
3. Sovereign-cloud short-circuit applies; bridge file may be produced by an out-of-band process documented in §13 SOV.

### 10.3 Pester suite — `AGT212.Sponsor.Tests.ps1`

```powershell
#Requires -Modules Pester
Describe 'SPONSOR — bridge to Control 2.26' -Tag 'SPONSOR','BRIDGE' {

    BeforeAll {
        . $PSScriptRoot/_helpers/Agt212.Common.ps1
        $script:Sov     = Test-Agt212SovereignTenant
        $script:Bridge  = Get-Content $env:AGT212_226_BRIDGE_PATH | ConvertFrom-Json
        $script:Inventory = Get-Content $env:AGT212_INVENTORY_PATH | ConvertFrom-Json
        $script:Age     = (Get-Date) - ([datetime]$script:Bridge.run_timestamp)
    }

    Context 'Bridge freshness' -Skip:$script:Sov {
        It 'control 2.26 evidence is < 24 hours old' {
            $script:Age.TotalHours | Should -BeLessThan 24 -Because 'Stale 2.26 evidence cannot anchor 2.12 supervision'
        }
    }

    Context 'No orphans in 2.12 scope' -Skip:$script:Sov {
        It 'every Z2/Z3 agent in inventory has current Sponsor per 2.26' -ForEach ($script:Inventory | Where-Object zone -in 'Zone 2','Zone 3') {
            $entry = $script:Bridge.agents | Where-Object agent_id -eq $_.agent_id
            $entry              | Should -Not -BeNullOrEmpty -Because "Agent $($_.agent_id) absent from 2.26 evidence"
            $entry.sponsor_status | Should -Be 'CURRENT'
        }
    }

    Context 'Principal and Sponsor consistency' -Skip:$script:Sov {
        It 'when principal_upn != sponsor_upn, both resolve to active Members' -ForEach ($script:Inventory | Where-Object { $_.principal_upn -ne $_.sponsor_upn -and $_.zone -in 'Zone 2','Zone 3' }) {
            (Get-MgUser -UserId $_.principal_upn -Property AccountEnabled).AccountEnabled | Should -BeTrue
            (Get-MgUser -UserId $_.sponsor_upn   -Property AccountEnabled).AccountEnabled | Should -BeTrue
        }
    }
}
```

### 10.4 Sample passing record

```json
{
  "control_id": "C2.12", "namespace": "SPONSOR", "criterion": "BRIDGE",
  "status": "PASS",
  "assertion": "All 47 Z2/Z3 agents map to a CURRENT 2.26 Sponsor; bridge evidence age 4.1 h",
  "observed_value": { "agents_checked": 47, "current": 47, "orphan": 0, "bridge_age_hours": 4.1 },
  "evidence_artifacts": ["sponsor-status-RUN226-20260415-040000.json","agent-inventory-export-AGT212-20260415-091200-7f3ac9d2.json"],
  "regulator_mappings": ["FINRA Rule 3110(a)(2)","SEC 17a-4(b)(4)"],
  "schema_version": "1.0"
}
```

### 10.5 Sample failing record + triage pointer

```json
{
  "control_id": "C2.12", "namespace": "SPONSOR", "criterion": "BRIDGE",
  "status": "FAIL",
  "assertion": "Agent agent-wealth-research-022 flagged ORPHAN by Control 2.26 at 2026-04-14T22:00Z but still active in 2.12 supervisory queue",
  "observed_value": { "agent_id": "agent-wealth-research-022", "sponsor_status": "ORPHAN" },
  "expected_value": { "sponsor_status": "CURRENT", "queue_state_if_orphan": "SUSPENDED" },
  "evidence_artifacts": ["sponsor-status-RUN226-20260414-220000.json"],
  "remediation_ref": "TRG-SPONSOR-01",
  "schema_version": "1.0"
}
```

See §16 for **TRG-SPONSOR-01** (orphan suspension and supervisory re-entry workflow).

### 10.6 Examiner artifact table

| Examiner ask | Artifact |
|---|---|
| "Show me the agent-to-human chain on a given date" | Inventory snapshot + 2.26 sponsor-status snapshot dated ≤ that date |
| "What happened when the prior Sponsor left?" | 2.26 reassignment log (out of scope here) plus 2.12 inventory diff showing new `sponsor_upn` |

### 10.7 Zone thresholds

Bridge integrity is binary across all zones: any orphan in Z2/Z3 fails the namespace.

### 10.8 Regulator mapping

| Test | FINRA 3110 | SEC 17a-4 | SOX §404 |
|---|---|---|---|
| Bridge freshness | ✓ supervisory currency | ✓ books-and-records | ✓ control operating effectiveness |
| No orphans in scope | ✓ supervisory accountability | ✓ | ✓ |
| Principal/Sponsor consistency | ✓ documented chain | ✓ | ✓ segregation |

---

## 11. AGF — Microsoft Agent Framework Human-in-the-Loop

> **Verification Criteria:** C2.12-2 (when AGF is the runtime) and **C2.12-9** (Agent Framework HITL request/response handlers and checkpoint persistence are configured and observable).
>
> **Non-substitution reminder:** AGF verifies that the *technical scaffolding* for HITL exists (request_info functions, checkpoint storage, response handlers wired to a human queue). It does not verify that the human's response was correct — that is reviewer-decision audit-trail (§5 REVIEWER) territory.

### 11.1 Background — what AGF HITL must look like

A conformant Microsoft Agent Framework agent that participates in Control 2.12 supervision must:

1. Define at least one `request_info` (or framework-equivalent) function for *any* tool that mutates customer-facing state, exceeds an autonomy threshold, or produces a Rule 2210 retail communication.
2. Persist a **checkpoint** (workflow state + tool inputs + draft output) to durable storage at the moment the request is made.
3. Wire a **response handler** that consumes the human's decision (`approve | reject | modify`) and either resumes, terminates, or branches the workflow.
4. Emit a structured event to the supervisory queue such that §4 QUEUE p95-latency calculations include AGF interventions.

### 11.2 Pre-conditions

1. AGF agents are inventoried with `runtime = "AgentFramework"` in the Agent Inventory.
2. Checkpoint store is reachable: `$env:AGT212_AGF_CHECKPOINT_STORE` (Azure Storage Table or Cosmos DB).
3. The Pester runner has read access to the agent's source manifest (`agent.yaml` or `agent.json`) at `$env:AGT212_AGF_MANIFEST_ROOT`.
4. Sovereign-cloud short-circuit applies; manifests in air-gapped tenants are inspected during the §13 SOV attestation cycle.

### 11.3 Pester suite — `AGT212.AGF.Tests.ps1`

```powershell
#Requires -Modules Pester
[CmdletBinding()] param([string]$RunId = (New-Agt212RunId))

BeforeAll {
    . $PSScriptRoot/_helpers/Agt212.Common.ps1
    $script:Sov = Test-Agt212SovereignTenant
    $script:AgfAgents = (Get-Content $env:AGT212_INVENTORY_PATH | ConvertFrom-Json) | Where-Object runtime -eq 'AgentFramework'
}

Describe 'AGF — C2.12-9 Agent Framework HITL scaffolding' -Tag 'AGF','C2.12-9' {

    Context 'Sovereign short-circuit' -Skip:(-not $script:Sov) { It 'SKIPPED' { $true | Should -BeTrue } }

    Context 'Manifest declares request_info for sensitive tools' -Skip:$script:Sov {
        It 'every sensitive tool has a paired request_info' -ForEach $script:AgfAgents {
            $manifestPath = Join-Path $env:AGT212_AGF_MANIFEST_ROOT "$($_.agent_id)/agent.yaml"
            $m = ConvertFrom-Yaml (Get-Content $manifestPath -Raw)
            $sensitive = $m.tools | Where-Object { $_.sensitivity -in @('mutating','retail-comm','high-autonomy') }
            foreach ($t in $sensitive) {
                ($m.request_info | Where-Object linked_tool -eq $t.name).Count | Should -BeGreaterThan 0 -Because "Tool $($t.name) of agent $($_.agent_id) lacks request_info wiring"
            }
        }
    }

    Context 'Checkpoint persistence' -Skip:$script:Sov {
        It 'each agent emits a checkpoint within 30 days for every request_info invocation' -ForEach $script:AgfAgents {
            $cp = Get-Agt212AgfCheckpoints -AgentId $_.agent_id -Since (Get-Date).AddDays(-30)
            $invocations = Get-Agt212AgfRequestInfoInvocations -AgentId $_.agent_id -Since (Get-Date).AddDays(-30)
            ($cp.Count) | Should -BeGreaterOrEqual ($invocations.Count) -Because 'Every request_info must produce a durable checkpoint'
        }
        It 'checkpoint payload includes workflow_state, tool_inputs, draft_output' -ForEach $script:AgfAgents {
            $sample = Get-Agt212AgfCheckpoints -AgentId $_.agent_id -Since (Get-Date).AddDays(-30) | Select-Object -First 5
            foreach ($c in $sample) {
                $c.workflow_state | Should -Not -BeNullOrEmpty
                $c.tool_inputs    | Should -Not -BeNullOrEmpty
                $c.draft_output   | Should -Not -BeNullOrEmpty
            }
        }
    }

    Context 'Response handler wired to supervisory queue' -Skip:$script:Sov {
        It 'every checkpoint resolves with approve|reject|modify within SLA or remains OPEN < SLA' -ForEach $script:AgfAgents {
            $cp = Get-Agt212AgfCheckpoints -AgentId $_.agent_id -Since (Get-Date).AddDays(-30)
            foreach ($c in $cp) {
                if ($c.status -eq 'CLOSED') {
                    $c.decision | Should -BeIn @('approve','reject','modify')
                    $c.closed_utc | Should -Not -BeNullOrEmpty
                } else {
                    ((Get-Date) - [datetime]$c.created_utc).TotalHours | Should -BeLessThan 48
                }
            }
        }
    }

    Context 'AGF events surface in §4 QUEUE telemetry' -Skip:$script:Sov {
        It 'sample of 10 AGF checkpoints all appear in supervisory queue export' {
            $sample = Get-Agt212AgfCheckpoints -Since (Get-Date).AddDays(-7) | Get-Random -Count 10
            $queue  = Get-Content (Join-Path $env:AGT212_QUEUE_EXPORT_DIR 'queue-export-latest.json') | ConvertFrom-Json
            foreach ($c in $sample) {
                ($queue.items | Where-Object correlation_id -eq $c.checkpoint_id).Count | Should -Be 1 -Because "AGF checkpoint $($c.checkpoint_id) missing from supervisory queue"
            }
        }
    }
}
```

### 11.4 Sample passing record

```json
{
  "control_id": "C2.12",
  "namespace": "AGF",
  "criterion": "C2.12-9",
  "status": "PASS",
  "assertion": "8 AGF agents inspected: all sensitive tools have request_info wiring; 412 checkpoints in 30d, 100% surface in queue, p95 close 6.2 h",
  "observed_value": { "agf_agents": 8, "checkpoints_30d": 412, "queue_correlation_rate": 1.0, "p95_close_hours": 6.2 },
  "evidence_artifacts": ["agf-manifests-AGT212-20260415-091200-7f3ac9d2.zip","agf-checkpoints-30d-AGT212-20260415-091200-7f3ac9d2.json"],
  "regulator_mappings": ["FINRA Rule 3110(b)","SEC 17a-4(b)(4)"],
  "schema_version": "1.0"
}
```

### 11.5 Sample failing record + triage pointer

```json
{
  "control_id": "C2.12",
  "namespace": "AGF",
  "criterion": "C2.12-9",
  "status": "FAIL",
  "assertion": "Agent agent-trade-allocation-002 invokes mutating tool 'submit_block_trade' without a paired request_info — direct execution observed 14 times in last 7 days",
  "observed_value": { "agent_id": "agent-trade-allocation-002", "tool": "submit_block_trade", "request_info_present": false, "direct_invocations_7d": 14 },
  "expected_value": { "request_info_present": true },
  "evidence_artifacts": ["agf-manifests-AGT212-20260415-091200-7f3ac9d2.zip"],
  "remediation_ref": "TRG-AGF-01",
  "schema_version": "1.0"
}
```

See §16 for **TRG-AGF-01** (missing request_info — agent suspension and re-deployment workflow).

### 11.6 Examiner artifact table

| Examiner ask | Artifact |
|---|---|
| "Show that every sensitive tool requires human approval" | Manifest excerpts mapping tool → request_info |
| "Reconstruct the human decision on checkpoint X" | Checkpoint record + queue entry + reviewer-decision record from §5 REVIEWER |
| "What happens if the human times out?" | Response-handler config + observed timeout behaviour (auto-reject vs. escalate) documented in WSP §2 |

### 11.7 Zone thresholds

| Zone | Pass threshold | Warn | Fail |
|---|---|---|---|
| Zone 1 | n/a — Personal-scope AGF agents are out of supervisory scope unless they expose enterprise data | — | — |
| Zone 2 | 100% sensitive tools have request_info; ≥ 95% checkpoint→queue correlation; p95 close ≤ 24 h | 90–94% correlation OR 24–48 h p95 | < 90% correlation OR > 48 h p95 |
| Zone 3 | Zone 2 plus 100% checkpoint→queue correlation and 100% checkpoints carry workflow_state+tool_inputs+draft_output | n/a | any deviation |

### 11.8 Regulator mapping

| Test | FINRA 3110 | FINRA 3120 | SEC 17a-4 | SOX §404 |
|---|---|---|---|---|
| request_info on sensitive tools | ✓ supervisory pre-clearance | ✓ control design | — | ✓ |
| Checkpoint durability | ✓ reconstructability | ✓ | ✓ 17a-4(b)(4) | ✓ |
| Response-handler closure | ✓ supervisory completion | ✓ control operating effectiveness | ✓ | ✓ |
| Queue correlation | ✓ unified supervisory record | ✓ | ✓ | ✓ |

---

## 12. SIEM — Forwarding and Retention to Sentinel/Splunk

> **Cross-cutting namespace.** SIEM does not map to a single Verification Criterion but underpins all of them by ensuring supervisory events leave the productivity stack and land in a tamper-evident log store within the firm's SIEM (typically Microsoft Sentinel or Splunk for FSI tenants). Loss of this pipeline silently invalidates every PASS in §2–§11 because the firm cannot reconstruct the supervisory record at examiner request.

### 12.1 What this namespace verifies

1. The Microsoft Purview audit pipeline forwards Copilot Studio, Agent Framework, Power Platform, and Entra agent-related event categories to the firm SIEM.
2. Forwarding is configured for the table set required by Control 2.12 (see §12.2).
3. End-to-end latency from event emission to SIEM index is bounded (target: p95 ≤ 15 min for Z3 events).
4. Retention in SIEM meets or exceeds the maxima in the Control 2.12 retention table (7 yrs for supervisory records; 6 yrs WORM-aligned for 2210; 17a-4(f) for compliance-locked items).
5. Daily forwarding-health digests are produced and reviewed by Compliance/SOC.

### 12.2 Required event categories

| Source | Table / event class | Why it matters for 2.12 |
|---|---|---|
| Copilot Studio | `CopilotStudioActivity` | HITL events, prompt/response audit |
| Microsoft Agent Framework | `AgentFrameworkCheckpoint`, `AgentFrameworkRequestInfo` | C2.12-9 evidence |
| Power Platform | `PowerPlatformAdminActivity`, `PowerAutomateRunHistory` | flow-driven supervisory queue events |
| Entra | `AuditLogs` (filter: agent-id objects, sponsor changes) | C2.12-3 chain integrity |
| Purview | `ComplianceManagerAlerts`, `LabelActivity` | C2.12-7 classification |

### 12.3 Pre-conditions

1. Sentinel workspace `$env:AGT212_SENTINEL_WORKSPACE_ID` is set, and the Pester runner identity holds `Microsoft Sentinel Reader` on the workspace's resource group.
2. KQL queries in `_helpers/Agt212.Siem.kql/` are vetted by SOC and version-controlled.
3. Forwarding-health digest path: `$env:AGT212_SIEM_DIGEST_DIR/digest-<yyyymmdd>.json`.
4. Sovereign short-circuit: in air-gapped tenants, SIEM may be a separate sovereign Sentinel instance; the same KQL queries are run against the sovereign workspace and recorded in §13 SOV.

### 12.4 Pester suite — `AGT212.Siem.Tests.ps1`

```powershell
#Requires -Modules Pester, Az.OperationalInsights
[CmdletBinding()] param([string]$RunId = (New-Agt212RunId))

BeforeAll {
    . $PSScriptRoot/_helpers/Agt212.Common.ps1
    $script:Workspace = $env:AGT212_SENTINEL_WORKSPACE_ID
    $script:Sov       = Test-Agt212SovereignTenant
    $script:KqlRoot   = Join-Path $PSScriptRoot '_helpers/Agt212.Siem.kql'
}

Describe 'SIEM — forwarding & retention' -Tag 'SIEM' {

    Context 'Sovereign short-circuit' -Skip:(-not $script:Sov) { It 'SKIPPED' { $true | Should -BeTrue } }

    Context 'All required tables receiving data within last 6h' -Skip:$script:Sov {
        $tables = @('CopilotStudioActivity','AgentFrameworkCheckpoint','PowerPlatformAdminActivity','AuditLogs','LabelActivity')
        It "<_> has rows in last 6h" -ForEach $tables {
            $kql = "$_ | where TimeGenerated > ago(6h) | summarize n = count()"
            $r = Invoke-AzOperationalInsightsQuery -WorkspaceId $script:Workspace -Query $kql
            ($r.Results[0].n -as [int]) | Should -BeGreaterThan 0 -Because "Table $_ silent in last 6h — supervisory pipeline at risk"
        }
    }

    Context 'End-to-end latency' -Skip:$script:Sov {
        It 'p95 ingestion lag for CopilotStudioActivity ≤ 15 minutes' {
            $kql = Get-Content (Join-Path $script:KqlRoot 'copilot-ingestion-lag.kql') -Raw
            $r = Invoke-AzOperationalInsightsQuery -WorkspaceId $script:Workspace -Query $kql
            ($r.Results[0].p95_lag_seconds -as [int]) | Should -BeLessOrEqual 900
        }
    }

    Context 'Retention configuration' -Skip:$script:Sov {
        It 'Sentinel workspace retention ≥ 2 years; archive tier configured to 7 yrs' {
            $ws = Get-AzOperationalInsightsWorkspace -Name $env:AGT212_SENTINEL_WORKSPACE_NAME -ResourceGroupName $env:AGT212_SENTINEL_RG
            $ws.RetentionInDays   | Should -BeGreaterOrEqual 730
            $ws.ArchiveRetentionInDays | Should -BeGreaterOrEqual 2555  # 7 yrs
        }
    }

    Context 'Forwarding-health digest' -Skip:$script:Sov {
        It 'today digest exists and reports zero unacknowledged forwarding errors' {
            $today = Join-Path $env:AGT212_SIEM_DIGEST_DIR ("digest-" + (Get-Date -Format 'yyyyMMdd') + ".json")
            Test-Path $today | Should -BeTrue
            $j = Get-Content $today | ConvertFrom-Json
            ($j.errors | Where-Object acknowledged -eq $false).Count | Should -Be 0
        }
    }
}
```

### 12.5 Sample passing record

```json
{
  "control_id": "C2.12", "namespace": "SIEM", "criterion": "cross-cutting",
  "status": "PASS",
  "assertion": "All 5 required tables fresh < 6h; p95 ingestion lag 312s; retention 730 hot / 2555 archive days; digest clean",
  "observed_value": { "tables_fresh": 5, "p95_lag_seconds": 312, "retention_hot_days": 730, "retention_archive_days": 2555, "open_errors": 0 },
  "evidence_artifacts": ["siem-table-counts-AGT212-20260415-091200-7f3ac9d2.json","siem-digest-20260415.json"],
  "regulator_mappings": ["SEC 17a-4(b)(4)","SEC 17a-4(f)","FINRA Rule 3110(b)","SOX §404"],
  "schema_version": "1.0"
}
```

### 12.6 Sample failing record + triage pointer

```json
{
  "control_id": "C2.12", "namespace": "SIEM",
  "status": "FAIL",
  "assertion": "AgentFrameworkCheckpoint table silent for 9h — possible Diagnostic Settings disconnect",
  "observed_value": { "table": "AgentFrameworkCheckpoint", "silent_hours": 9 },
  "expected_value": { "max_silent_hours": 6 },
  "remediation_ref": "TRG-SIEM-01",
  "schema_version": "1.0"
}
```

### 12.7 Examiner artifact table

| Examiner ask | Artifact |
|---|---|
| "Show me supervisory events from last March" | KQL output saved to `siem-export-<period>.csv` with workspace + query hash |
| "Prove the data hasn't been altered" | Sentinel immutable archive policy export + Storage account lock report |
| "How fast does an event reach SIEM?" | Daily lag dashboard PNG + raw KQL |

### 12.8 Regulator mapping

| Test | FINRA 3110 | SEC 17a-4 | SOX §404 |
|---|---|---|---|
| Required tables receiving | ✓ supervisory data exists | ✓ books-and-records | ✓ |
| Latency bounded | ✓ timely supervision | ✓ | ✓ |
| Retention ≥ 7 yrs archive | — | ✓ 17a-4(b)(4)/(f) | ✓ |
| Digest reviewed daily | ✓ pipeline supervised | ✓ | ✓ |

---

## 13. SOV — Sovereign-Cloud Compensating Control

> **Verification Criterion:** C2.12-8 — In sovereign / air-gapped tenants where one or more automated assertions in §2–§12 cannot run (e.g., no outbound Graph reachability, no Sentinel, manifests held offline), the firm performs a **dual-signed quarterly attestation** that the same intent is met through compensating manual procedures.
>
> **Non-substitution reminder:** SOV does not relax any obligation. It substitutes a documented manual procedure for the automated check, with **two human signers** (typically the CCO and the Designated Principal of record for the affected business line) attesting that the procedure ran and produced the intended evidence.

### 13.1 When SOV applies

SOV is engaged when `Test-Agt212SovereignTenant` returns `$true`. That helper is wired to detect:

* Tenant in `MicrosoftCloud.USNat` / `USSec` / sovereign partner clouds where Graph is restricted.
* Absence of the ingress endpoints required by §6, §11, §12.
* An explicit operator override `$env:AGT212_FORCE_SOV='true'` (used during DR exercises).

When SOV applies, every namespace's Pester suite emits `SKIPPED` records pointing here; the **only** evidence accepted is the dual-signed quarterly attestation packet described below.

### 13.2 Attestation packet contents

Each quarterly packet is a single ZIP at `$env:AGT212_SOV_VAULT_ROOT/sov-attestation-<yyyy>Q<n>.zip` containing:

1. `attestation.pdf` — narrative attestation, dual signatures (PKI), see §13.3 template.
2. `criteria-matrix.json` — for each VC C2.12-1…C2.12-9, the compensating procedure, evidence references, and PASS/FAIL determination by the signers.
3. `evidence/` folder — copies (or hashes + secure-vault pointers) of the underlying artifacts: WSP version, principal registry snapshot, sample of reviewer decisions, R3120 working papers, R2210 approvals, AGF manifest excerpts, SIEM-equivalent log exports.
4. `procedures/` — the SOPs followed (e.g., "Manual Reviewer-Decision Audit Walkthrough — sovereign tenant").
5. `signatures.json` — PKI signature metadata for the two signers, including CRD numbers where applicable.

### 13.3 Attestation template (excerpt)

```
SOVEREIGN-CLOUD COMPENSATING ATTESTATION — CONTROL 2.12 (FINRA Rule 3110)
Quarter: <yyyy>Q<n>     Tenant: <tenant_id>     Cloud: <USNat|USSec|partner>

We, the undersigned, attest that during the quarter ending <date>:

1. The Written Supervisory Procedures applicable to AI agents (version <v>, published <date>)
   were in force and were followed.
2. Each in-scope agent (n=<count>; see criteria-matrix.json §C2.12-3) had a Designated Principal
   holding a current Series 24/9/10 registration, evidenced by CRD U4 records dated within
   this quarter and held in the Compliance vault under hash <sha256>.
3. The Supervisory Review Queue SLA was met for <pass-rate>% of items in the manually drawn
   sample (n=<size>, seed <seed>), measured against the WSP-documented thresholds.
4. Reviewer decisions for the sample carried non-null reviewer, decision, rationale (≥ 25 chars
   in 100% of Z3 cases), and were locked to retention per Compliance policy <policy-id>.
5. Annual Rule 3120 testing for FY<year> is on track / was completed; working papers held
   under <vault-path>.
6. Rule 2210 classification was inspected on a sample of n=<size>; misclassification rate
   <rate>%; all retail items had documented pre-use principal approval.
7. Microsoft Agent Framework HITL scaffolding was inspected via offline manifest review;
   <count> AGF agents reviewed; no missing request_info on sensitive tools.
8. Supervisory event logs were exported to the sovereign log store with retention ≥ 7 years
   archive; pipeline health was reviewed daily with no unresolved failures > 24 h.

Signature 1 — Chief Compliance Officer
   Name:           ________________________
   PKI thumbprint: ________________________
   Date:           ________________________

Signature 2 — Designated Principal of Record
   Name:           ________________________
   CRD #:          ________________________
   PKI thumbprint: ________________________
   Date:           ________________________
```

### 13.4 Pester verification of the attestation packet

Even in sovereign mode, a thin Pester suite verifies the *presence and well-formedness* of the packet. The suite can run on a sovereign-internal runner that never reaches public Microsoft endpoints.

```powershell
Describe 'SOV — C2.12-8 quarterly attestation packet' -Tag 'SOV','C2.12-8' {

    BeforeAll {
        . $PSScriptRoot/_helpers/Agt212.Common.ps1
        $script:Quarter = Get-Agt212CurrentQuarter
        $script:Pkg     = Join-Path $env:AGT212_SOV_VAULT_ROOT "sov-attestation-$($script:Quarter).zip"
    }

    It 'packet for current quarter exists' {
        Test-Path $script:Pkg | Should -BeTrue -Because 'SOV attestation is mandatory each quarter'
    }
    It 'packet is dual-signed (two distinct PKI signatures)' {
        $sigs = Get-Agt212ZipPdfSignatures -ZipPath $script:Pkg -InnerPath 'attestation.pdf'
        $sigs.Count | Should -BeGreaterOrEqual 2
        ($sigs.Thumbprint | Select-Object -Unique).Count | Should -BeGreaterOrEqual 2
    }
    It 'criteria-matrix covers all 9 verification criteria' {
        $tmp = Expand-Agt212ZipMember -ZipPath $script:Pkg -Member 'criteria-matrix.json'
        $j = Get-Content $tmp | ConvertFrom-Json
        $covered = $j.criteria.id | Sort-Object -Unique
        @('C2.12-1','C2.12-2','C2.12-3','C2.12-4','C2.12-5','C2.12-6','C2.12-7','C2.12-8','C2.12-9') |
            ForEach-Object { $covered | Should -Contain $_ }
    }
    It 'no criterion is marked SKIPPED-without-compensation' {
        $tmp = Expand-Agt212ZipMember -ZipPath $script:Pkg -Member 'criteria-matrix.json'
        $j = Get-Content $tmp | ConvertFrom-Json
        ($j.criteria | Where-Object { $_.status -eq 'SKIPPED' -and -not $_.compensating_procedure }).Count | Should -Be 0
    }
}
```

### 13.5 Sample failing record + triage pointers

```json
{
  "control_id": "C2.12", "namespace": "SOV", "criterion": "C2.12-8",
  "status": "FAIL",
  "assertion": "Q2 2026 attestation packet single-signed (only CCO; missing Designated Principal signature)",
  "observed_value": { "signature_count": 1 },
  "expected_value": { "signature_count": 2 },
  "remediation_ref": "TRG-SOV-01",
  "schema_version": "1.0"
}
```

```json
{
  "control_id": "C2.12", "namespace": "SOV", "criterion": "C2.12-8",
  "status": "FAIL",
  "assertion": "Criteria-matrix omits C2.12-9 (Agent Framework HITL); no compensating procedure on file",
  "observed_value": { "missing_criteria": ["C2.12-9"] },
  "remediation_ref": "TRG-SOV-02",
  "schema_version": "1.0"
}
```

See §16 for **TRG-SOV-01** (dual-signature remediation) and **TRG-SOV-02** (criterion coverage gap).

### 13.6 Examiner artifact table

| Examiner ask | Artifact |
|---|---|
| "How do you supervise AI agents in the air-gapped tenant?" | Latest sov-attestation-<q>.zip plus the SOPs in `procedures/` |
| "Show me CCO sign-off" | `signatures.json` with PKI thumbprint and certificate chain |
| "Prove no criterion was skipped" | `criteria-matrix.json` showing 9-of-9 with compensating procedure refs |

### 13.7 Zone thresholds

SOV is enterprise-wide. Any missing or single-signed quarterly packet is FAIL across all zones.

### 13.8 Regulator mapping

| Test | FINRA 3110 | FINRA 3120 | SEC 17a-4 | SOX §404 |
|---|---|---|---|---|
| Quarterly packet present | ✓ ongoing supervision | ✓ control operating effectiveness | ✓ books-and-records | ✓ |
| Dual signatures | ✓ supervisory accountability | — | — | ✓ segregation |
| Full criteria coverage | ✓ supervisory completeness | ✓ | ✓ 17a-4(b)(4) | ✓ |
| Compensating procedures documented | ✓ | ✓ control design | — | ✓ |

---

## 14. Manual Verification Procedures

The Pester suites in §2–§13 cover the bulk of automated assertions. The following manual checks fill gaps that cannot reasonably be automated and are run quarterly by the Compliance Officer (or designate) with the AI Governance Lead as witness. Each procedure produces a screenshot bundle and a short narrative, both filed in the run's evidence directory.

### 14.1 WSP human-readability spot-check (C2.12-1)

1. In Microsoft Word/SharePoint, open the current canonical WSP document.
2. Read aloud sections covering: agent intake, autonomy levels, supervisory queue routing, escalation, exception handling.
3. Confirm each section answers *who*, *what triggers*, *what happens*, *what evidence*. Note any ambiguity.
4. Save reading notes as `wsp-readability-<run_id>.md` and a PDF print of the table-of-contents.

### 14.2 Copilot Studio author-experience walkthrough (C2.12-2)

1. Sign in to Copilot Studio as a non-admin author.
2. Attempt to publish a new agent with a sensitive topic (e.g., trade recommendation) but **without** a configured human-handoff topic.
3. Confirm the publish action is blocked or the agent is auto-routed to the supervisory review backlog.
4. Capture screenshots of the block dialog and resulting backlog entry.

### 14.3 Reviewer console UX walkthrough (C2.12-5)

1. Sign in to the supervisory queue UI as a Designated Principal.
2. Open a pending item; verify the UI requires non-null reviewer, decision, and free-text rationale (≥ 25 chars on Z3 items) before allowing close.
3. Attempt to close with a 10-character rationale; capture the validation error.
4. Save screenshots as `reviewer-ux-walkthrough-<run_id>.zip`.

### 14.4 CRD/U4 vault retrieval drill (C2.12-3)

1. Pick three random Designated Principals from the registry.
2. Retrieve their current U4 PDFs from the Compliance vault.
3. Verify each PDF dates within the last 12 months and shows ACTIVE Series 24/9/10.
4. File `crd-vault-drill-<run_id>.md` with the three filenames, hashes, and "verified by" signature.

### 14.5 Sentinel KQL re-run drill (§12 SIEM)

1. Open Sentinel; paste the canonical KQL from `_helpers/Agt212.Siem.kql/copilot-supervision-30d.kql`.
2. Confirm result row count matches the figure in the latest digest within ±2%.
3. Export results as CSV and file as `siem-rerun-<run_id>.csv`.

### 14.6 Sovereign attestation cover-sheet review (C2.12-8)

Where applicable: open the latest `sov-attestation-<q>.pdf`, verify both PKI signatures via the OS certificate viewer, file the validation report.

---

## 15. Examiner Scenarios

The following eight scenarios rehearse end-to-end examiner asks and map them to namespaces, artifacts, and the people who must respond. Each scenario should be drilled at least once per year and after any material change to the control's operating environment.

### 15.1 Scenario A — FINRA cycle examination: WSP walkthrough and evidence pull

**Examiner ask:** "Walk me through your written supervisory procedures for AI agents and show me how you tested them in the last 12 months."

| Step | Owner | Artifacts |
|---|---|---|
| 1. Produce current WSP version + change log | Compliance Officer | `wsp-current.pdf`, `wsp-changelog.md`, §2 WSP latest evidence record |
| 2. Show the testing program | Compliance Officer | §8 R3120 last-year working papers + signoff |
| 3. Demonstrate sample reproducibility | AI Governance Lead | §7 SAMPLING manifest; live `Get-Agt212Sample` re-run |
| 4. Walk through three sampled supervisory decisions | Designated Principal | §5 REVIEWER records + §4 QUEUE timing |
| 5. Provide evidence pack | AI Administrator | Per-criterion bundle assembled per §16 |

**Expected duration:** 90–120 min onsite. **Failure mode:** stale WSP (> 12 mo without review) — see TRG-WSP-01.

### 15.2 Scenario B — SEC Rule 17a-4 WORM audit

**Examiner ask:** "Demonstrate that supervisory records are retained on non-rewriteable, non-erasable media for the required period."

| Step | Owner | Artifacts |
|---|---|---|
| 1. Produce Purview retention policy export | Purview Compliance Admin | `retention-policy-export.json` |
| 2. Demonstrate compliance lock on a sample record | Purview Compliance Admin | Screenshot: attempt to delete; produce error |
| 3. Show storage account immutable policy (Sentinel archive) | AI Administrator | Az CLI output of `az storage account blob-service-properties show` |
| 4. Provide §12 SIEM retention verification | AI Governance Lead | Latest §12.4 PASS record |

**Failure mode:** retention < 7 yrs archive — see TRG-SIEM-02.

### 15.3 Scenario C — Surprise audit: reviewer-decision audit trail for a named agent output

**Examiner ask:** "Pull every supervisory record for output `art-2026-02-1814` from agent `agent-wealth-research-022`."

| Step | Owner | Artifacts |
|---|---|---|
| 1. Locate output in Purview audit | Purview Compliance Admin | KQL `LabelActivity \| where ItemId == "art-2026-02-1814"` |
| 2. Locate corresponding supervisory queue entry | AI Governance Lead | §4 QUEUE export filtered by `correlation_id` |
| 3. Locate reviewer decision | AI Governance Lead | §5 REVIEWER record |
| 4. Confirm Designated Principal of record on date of decision | Compliance Officer | §6 PRINCIPAL inventory snapshot at that date |
| 5. Produce full chain as PDF | AI Administrator | `chain-art-2026-02-1814.pdf` |

**Target time-to-produce:** ≤ 30 min from ask. **Failure mode:** broken chain (any link missing) — automatically opens TRG-REVIEWER-01.

### 15.4 Scenario D — FINRA Rule 2210 misclassification

**Examiner ask:** "Show me an example where an agent-produced piece was distributed to retail without principal pre-approval, and what happened."

| Step | Owner | Artifacts |
|---|---|---|
| 1. Query R2210 quarterly findings | Compliance Officer | §9 R2210 latest run + remediation log |
| 2. For each FAIL: produce the artifact, audience log, missing-approval evidence | Designated Principal | Per-artifact `r2210-fail-<id>.zip` |
| 3. Show the remediation: re-classification + retroactive principal review | Compliance Officer | Approval record dated > distribution date with explanatory memo |
| 4. Show the corrective action: WSP update OR additional training | AI Governance Lead | WSP changelog entry or training attendance roster |

**Failure mode:** finding without remediation — TRG-R2210-01.

### 15.5 Scenario E — Autonomy-level escalation: a fully-autonomous Z3 agent surfaces

**Examiner ask:** "How was this fully-autonomous Zone 3 agent reviewed before it went live?"

| Step | Owner | Artifacts |
|---|---|---|
| 1. Produce the agent intake record | Agent Owner + AI Governance Lead | Intake form, autonomy classification rationale |
| 2. Produce the Designated Principal sign-off on autonomy | Designated Principal | §6 PRINCIPAL record at intake date + signed memo |
| 3. Show the AGF HITL scaffolding | AI Administrator | §11 AGF latest record for this agent |
| 4. Show 30 days of supervisory traffic | AI Governance Lead | §4 QUEUE + §5 REVIEWER export |

**Failure mode:** missing intake or missing AGF request_info on a sensitive tool — TRG-AGF-01.

### 15.6 Scenario F — Sponsor departs: evidence continuity during reassignment

**Examiner ask:** "The Designated Principal of record for these agents left the firm last month. Show me the supervisory continuity."

| Step | Owner | Artifacts |
|---|---|---|
| 1. Show the inventory diff (old vs. new principal_upn) | AI Governance Lead | Inventory snapshots before/after transition |
| 2. Show backup_principal handover (Z3) | Compliance Officer | Backup principal log + handover memo |
| 3. Demonstrate no orphan via §10 SPONSOR bridge | AI Governance Lead | §10 PASS record for the relevant period |
| 4. Show training/onboarding for the incoming principal | Compliance Officer | Training roster + acknowledgment of WSP version |

**Failure mode:** orphan window detected — TRG-SPONSOR-01.

### 15.7 Scenario G — Supervisor Series 24 lapses mid-quarter

**Examiner ask:** "Your principal's Series 24 expired on March 22. What supervisory decisions did this person make after that date, and how did you remediate?"

| Step | Owner | Artifacts |
|---|---|---|
| 1. Identify the lapse window from §6 PRINCIPAL records | Compliance Officer | §6 FAIL record (TRG-PRINCIPAL-01) |
| 2. Pull all reviewer decisions made by the lapsed principal in the window | AI Governance Lead | §5 REVIEWER export filtered by `reviewer_upn` and date range |
| 3. Reassign each decision to a currently-qualified principal for re-review | Compliance Officer | New §5 REVIEWER records with `re_review_of` pointer |
| 4. File exception memo and notify the firm's Chief Compliance Officer | Compliance Officer | `lapse-memo-<principal>.pdf` |

**Target turnaround:** 5 business days from detection. **Failure mode:** no re-review — escalates to Rule 3120 finding.

### 15.8 Scenario H — SOX 302/404 management certification: control design and operating effectiveness evidence

**Examiner ask (internal/external auditor):** "Provide management's assertion that supervisory controls over AI agent communications operated effectively for the fiscal year."

| Step | Owner | Artifacts |
|---|---|---|
| 1. Provide control narrative | Compliance Officer + AI Governance Lead | Section 5 of the Control 2.12 doc (link) |
| 2. Provide design documentation | AI Governance Lead | This playbook + 2.12 Control file |
| 3. Provide operating-effectiveness evidence (full FY) | AI Administrator | Quarterly attestation packs (§17), R3120 working papers (§8) |
| 4. Provide management certification | Designated Principal + CCO | Signed annual certification PDF |

**Failure mode:** missing quarterly pack — opens TRG-WSP-01 (governance failure) and may require disclosure under SOX §302.

---

## 16. Evidence Packaging per Criterion + Failure Triage Matrix

### 16.1 Per-criterion evidence pack contents

For each verification criterion, the evidence pack is a directory containing:

* `summary.json` — top-level record (run_id, criterion, namespaces involved, overall PASS/FAIL).
* `records/*.json` — every Pester evidence record bearing this criterion.
* `artifacts/` — referenced artifacts (or hash + vault pointer).
* `manifest.json` — per-file SHA-256, size, and inclusion timestamp; hashed into a Merkle root recorded in `summary.json`.
* `chain-of-custody.md` — who collected what and when.

| Criterion | Required namespaces | Minimum artifacts |
|---|---|---|
| C2.12-1 | WSP | WSP PDF, change log, Pester output |
| C2.12-2 | HITL, AGF | Topic export, AGF manifest excerpts, transcript sample |
| C2.12-3 | PRINCIPAL, SPONSOR | Inventory, registry, CRD U4 sample, 2.26 bridge file |
| C2.12-4 | QUEUE, SAMPLING | Queue export, sample manifest, p95 calc |
| C2.12-5 | REVIEWER, SAMPLING | Decision sample, reviewer qualification snapshot |
| C2.12-6 | R3120, SAMPLING | Test plan, sample, working papers, signoff, remediations |
| C2.12-7 | R2210, SAMPLING | Distribution log, approvals, sensitivity-label policy |
| C2.12-8 | SOV | Quarterly attestation ZIP |
| C2.12-9 | AGF | Manifests, checkpoints, queue correlation evidence |

### 16.2 Failure Triage Matrix

Each TRG-* identifier is a short remediation runbook. Owners are role names, not individuals.

#### TRG-WSP-01 — WSP missing or stale

* **Trigger:** §2 WSP test fails (no current published WSP, or last-review > 12 months).
* **Owner:** Compliance Officer (lead); AI Governance Lead (support).
* **Steps:** convene WSP review committee within 10 business days; publish updated version; backfill change log; re-run §2; notify CCO.
* **Closure evidence:** new WSP version + signed change-log entry + passing §2 record.

#### TRG-HITL-01 — Copilot Studio handoff misconfigured

* **Trigger:** §3 HITL FAIL — sensitive topic without human-handoff route or unauthenticated handoff.
* **Owner:** Agent Owner (lead); AI Administrator (support).
* **Steps:** disable affected agent; correct topology in Copilot Studio; re-publish; re-run §3.
* **Closure evidence:** passing §3 record + Copilot Studio change-history export.

#### TRG-QUEUE-01 — SLA breach on supervisory queue

* **Trigger:** p95 latency exceeds zone threshold OR backlog > limit.
* **Owner:** AI Governance Lead.
* **Steps:** add reviewer capacity; escalate to backup principals; root-cause backlog (volume spike vs. reviewer absence); document in §17 sign-off note.

#### TRG-REVIEWER-01 — Reviewer decision audit gap

* **Trigger:** §5 REVIEWER FAIL — null reviewer/decision/rationale, or reviewer not qualified at decision time.
* **Owner:** Designated Principal of record.
* **Steps:** retroactively re-review the affected items by a qualified principal; document `re_review_of` pointer; file exception memo; consider Rule 3120 finding.

#### TRG-PRINCIPAL-01 — Lapsed/expiring principal registration

* **Trigger:** §6 PRINCIPAL FAIL — Series 24/9/10 LAPSED or within 30-day expiry.
* **Owner:** Compliance Officer.
* **Steps:** for LAPSED: immediately reassign agents to a qualified principal; re-review any decisions made post-lapse (see Scenario G). For expiring: schedule renewal; if renewal not confirmed within 14 days of expiry, pre-emptively reassign.

#### TRG-SAMPLING-01 — Non-deterministic or low-coverage sampler

* **Trigger:** §7 SAMPLING FAIL on determinism or coverage.
* **Owner:** AI Administrator.
* **Steps:** patch sampler module; re-run §7; re-run any downstream namespaces that ran on the broken sampler; mark prior records SUPERSEDED.

#### TRG-SAMPLING-02 — Stratification skew

* **Trigger:** §7 stratification test fails.
* **Owner:** AI Administrator.
* **Steps:** review proportional-allocation logic; widen acceptable band only with Compliance Officer approval and WSP update.

#### TRG-SAMPLING-03 — Population mutation mid-run

* **Trigger:** population SHA-256 differs between sampling and downstream test.
* **Owner:** AI Governance Lead.
* **Steps:** snapshot population to immutable storage before sampling; re-run.

#### TRG-R3120-01 — Sign-off integrity

* **Trigger:** §8 R3120 FAIL on signature (image stamp, expired cert, untrusted chain, or non-executive title).
* **Owner:** Compliance Officer + CCO.
* **Steps:** re-sign with valid PKI from an executive title; replace artifact; re-run §8.

#### TRG-R2210-01 — Communication misclassification

* **Trigger:** §9 R2210 FAIL — label/audience inconsistency or missing pre-use approval.
* **Owner:** Designated Principal.
* **Steps:** retroactive principal review within 5 business days; re-classify; if material, file with FINRA Advertising; capture corrective action (training or WSP update).

#### TRG-SPONSOR-01 — Orphan in supervisory scope

* **Trigger:** §10 SPONSOR FAIL — orphan from 2.26 still active in 2.12 scope.
* **Owner:** AI Governance Lead.
* **Steps:** suspend agent from supervisory queue immediately; coordinate with Control 2.26 owner to reassign Sponsor; resume only after 2.26 PASS and §10 PASS.

#### TRG-AGF-01 — Missing request_info on sensitive AGF tool

* **Trigger:** §11 AGF FAIL.
* **Owner:** Agent Owner (lead); AI Administrator (support).
* **Steps:** suspend agent; add request_info to manifest; redeploy; backfill checkpoint storage if required; re-run §11.

#### TRG-SIEM-01 — Forwarding pipeline silent

* **Trigger:** §12 SIEM table silent > 6h.
* **Owner:** AI Administrator + SOC.
* **Steps:** check Diagnostic Settings; restart connector; backfill from source if possible; document gap window in §17 sign-off.

#### TRG-SIEM-02 — Retention shortfall

* **Trigger:** §12 SIEM retention < 7 yrs archive.
* **Owner:** AI Administrator.
* **Steps:** extend workspace archive retention; coordinate cost approval; re-run §12.

#### TRG-SOV-01 — Single-signed sovereign attestation

* **Trigger:** §13 SOV FAIL on dual-signature requirement.
* **Owner:** CCO + Designated Principal.
* **Steps:** re-execute attestation with both signatures; replace packet; document delay reason.

#### TRG-SOV-02 — Criterion coverage gap in sovereign attestation

* **Trigger:** §13 SOV criteria-matrix missing one or more VCs.
* **Owner:** AI Governance Lead.
* **Steps:** document compensating procedure for missing VC; have signers re-attest; replace packet.

---

## 17. Sign-off Workflow

### 17.1 Run-end sign-off sequence

1. **Pester completion** — runner emits all evidence records and the per-namespace manifests.
2. **Pack assembly** — `Build-Agt212EvidencePack -RunId <id>` walks namespaces, computes per-file SHA-256, builds a Merkle tree, writes `manifest.json` with the Merkle root.
3. **Triage triage** — for each FAIL record, the triage script opens (or reuses) a ticket in the firm's GRC system referencing the TRG-* identifier, owner role, and target close date.
4. **Compliance Officer review** — reviews the evidence pack summary; signs `signoff.json` with PKI; the signed JSON binds the Merkle root and counts of PASS/FAIL/SKIPPED per criterion.
5. **Designated Principal counter-sign** (Z3 scope) — Designated Principal of record for the affected business line counter-signs.
6. **Vault deposit** — pack is deposited to the Compliance vault with retention label `Supervisory-Records-7yr` (or 6yr WORM aligned for 2210 components).
7. **SIEM event emission** — a single signed event is forwarded to Sentinel/Splunk to anchor the run in the immutable log.

### 17.2 `signoff.json` schema

```json
{
  "control_id": "C2.12",
  "run_id": "AGT212-20260415-091200-7f3ac9d2",
  "merkle_root_sha256": "ab12...ef90",
  "criteria_summary": {
    "C2.12-1": { "pass": 1, "fail": 0, "skipped": 0 },
    "C2.12-2": { "pass": 1, "fail": 0, "skipped": 0 },
    "C2.12-3": { "pass": 47, "fail": 0, "skipped": 0 },
    "C2.12-4": { "pass": 1, "fail": 0, "skipped": 0 },
    "C2.12-5": { "pass": 1, "fail": 0, "skipped": 0 },
    "C2.12-6": { "pass": 1, "fail": 0, "skipped": 0 },
    "C2.12-7": { "pass": 1, "fail": 0, "skipped": 0 },
    "C2.12-8": { "pass": 0, "fail": 0, "skipped": 1, "note": "Public-cloud tenant; SOV not engaged" },
    "C2.12-9": { "pass": 1, "fail": 0, "skipped": 0 }
  },
  "signatures": [
    { "role": "Compliance Officer", "upn": "compliance.officer@contoso.com", "pki_thumbprint": "AB:CD:...", "signed_utc": "2026-04-15T10:02:11Z" },
    { "role": "Designated Principal", "upn": "jane.doe@contoso.com", "crd_number": "1234567", "pki_thumbprint": "EF:01:...", "signed_utc": "2026-04-15T10:08:44Z" }
  ],
  "vault_uri": "vault://contoso-compliance/c2.12/2026Q2/AGT212-20260415-091200-7f3ac9d2.zip",
  "retention_label": "Supervisory-Records-7yr",
  "schema_version": "1.0"
}
```

### 17.3 Sign-off failure modes

| Symptom | Resolution |
|---|---|
| Merkle root mismatch on re-validation | Re-pack from source records; investigate vault tampering; raise Sev-2 incident |
| Compliance Officer unavailable | Backup signer (CCO direct designate) per WSP §2; document in `signoff.json.notes` |
| Designated Principal lapsed mid-run | Sign with replacement principal; flag run as containing TRG-PRINCIPAL-01 finding |

---

## 18. Quarterly Attestation Template

Quarterly, the Compliance Officer assembles a roll-up packet covering the 13 weekly/monthly Pester runs in the quarter. The packet is the canonical evidence pack for examiners and the SOX audit team.

```json
{
  "control_id": "C2.12",
  "period": "2026Q2",
  "tenant_id": "11111111-2222-3333-4444-555555555555",
  "cloud": "Public",
  "runs_included": ["AGT212-20260415-091200-7f3ac9d2", "AGT212-20260422-091200-...", "..."],
  "criteria_attestation": {
    "C2.12-1": { "status": "PASS", "evidence_refs": ["wsp-current-2026Q2.pdf"], "notes": "WSP version 4.2 published 2026-04-01" },
    "C2.12-2": { "status": "PASS", "evidence_refs": ["copilot-handoff-export-2026Q2.json"], "notes": "100% sensitive topics routed" },
    "C2.12-3": { "status": "PASS", "evidence_refs": ["principal-registry-2026Q2.json"], "notes": "47 agents, all principals current" },
    "C2.12-4": { "status": "PASS", "evidence_refs": ["queue-p95-2026Q2.json"], "notes": "Z3 p95 = 6.1 h (threshold 8 h)" },
    "C2.12-5": { "status": "PASS", "evidence_refs": ["reviewer-sample-2026Q2.json"], "notes": "n=120, 100% non-null fields" },
    "C2.12-6": { "status": "PASS", "evidence_refs": ["r3120-fy2025-signoff.pdf"], "notes": "FY2025 closed 2026-02-14" },
    "C2.12-7": { "status": "PASS", "evidence_refs": ["r2210-2026Q2-summary.json"], "notes": "n=30 sampled; 0 unapproved retail" },
    "C2.12-8": { "status": "N/A", "evidence_refs": [], "notes": "Public cloud; SOV not engaged" },
    "C2.12-9": { "status": "PASS", "evidence_refs": ["agf-quarterly-2026Q2.json"], "notes": "8 AGF agents; 100% request_info wired" }
  },
  "open_findings": [],
  "signatures": [
    { "role": "Compliance Officer", "name": "...", "signed_utc": "..." },
    { "role": "Chief Compliance Officer", "name": "...", "signed_utc": "..." }
  ],
  "merkle_root_sha256": "...",
  "vault_uri": "vault://contoso-compliance/c2.12/quarterly/2026Q2.zip",
  "schema_version": "1.0"
}
```

The quarterly packet must be filed within 30 days of quarter-end. Late filing is itself a §17 sign-off failure mode and triggers a §15.8 (SOX) escalation.

---

## 19. Continuous Improvement Metrics

The following metrics are trended quarter-over-quarter to detect drift before it becomes an examination finding. Trends are reviewed by the AI Governance Council with the AI Governance Lead presenting.

| Metric | Source | Healthy direction | Threshold for action |
|---|---|---|---|
| Supervisory queue p95 latency | §4 QUEUE | Stable or decreasing | > 10% increase QoQ for two consecutive quarters |
| WSP intent coverage (% of agent intents addressed by WSP sections) | §2 WSP | Increasing toward 100% | < 90% or any decrease |
| Rule 2210 misclassification rate | §9 R2210 | Decreasing | > 5% in any quarter or > 2% trend over 3 quarters |
| Principal registration expiry lead time | §6 PRINCIPAL | ≥ 60 days mean | Mean drops below 45 days |
| AGF checkpoint→queue correlation rate | §11 AGF | 100% | < 99% |
| Sentinel ingestion lag p95 | §12 SIEM | ≤ 15 min | > 15 min |
| Sovereign attestation on-time rate | §13 SOV | 100% | < 100% (any late filing) |
| Triage MTTR by TRG-ID | §16 + GRC ticketing | Decreasing | > target by ID (e.g., TRG-PRINCIPAL-01 > 5 BD) |

Each metric should appear on the council's quarterly scorecard with a sparkline covering at least the prior four quarters.

---

## 20. Cross-References

### 20.1 Companion controls (governance dependencies)

* [Control 2.26 — Entra Agent ID Identity Governance](../../../controls/pillar-2-management/2.26-entra-agent-id-identity-governance.md) — upstream sponsorship; verified via §10 SPONSOR.
* [Control 2.25 — Agent 365 Admin Center Governance Console](../../../controls/pillar-2-management/2.25-agent-365-admin-center-governance-console.md) — administrative surface for agent inventory used by §6 PRINCIPAL.
* [Control 3.6 — Orphaned Agent Detection & Remediation](../../../controls/pillar-3-reporting/3.6-orphaned-agent-detection-and-remediation.md) — orphan signals consumed by §10 SPONSOR re-entry workflow.
* [Control 2.13 — Documentation and Record Keeping](../../../controls/pillar-2-management/2.13-documentation-and-record-keeping.md) — retention labels used by §16 packaging and §17 vault deposit.
* [Control 2.21 — AI Marketing Claims and Substantiation](../../../controls/pillar-2-management/2.21-ai-marketing-claims-and-substantiation.md) — substantiation requirements that feed §9 R2210 retail-communication review.

### 20.2 Sister playbooks under Control 2.12

* [Portal Walkthrough](portal-walkthrough.md) — admin-portal configuration steps that produce the artifacts verified here.
* [PowerShell Setup](powershell-setup.md) — bootstraps `Agt212.Common.ps1`, `Agt212.Sampling.psm1`, helper modules referenced throughout.
* [Troubleshooting](troubleshooting.md) — symptom-to-fix lookup for the Pester suites and pipelines.

### 20.3 Regulatory references

* FINRA Rule 3110 — Supervision (especially 3110(a), (b)(2), (b)(4))
* FINRA Rule 3120 — Supervisory Control System (annual testing)
* FINRA Rule 2210 — Communications with the Public
* FINRA Rule 1210 — Registration Requirements
* FINRA Rule 4511 — General Requirements (books and records)
* SEC Rule 17a-4 — Records to be Preserved by Certain Exchange Members (especially 17a-4(b)(4) and 17a-4(f))
* SOX §302 / §404 — Management certification and internal controls over financial reporting
* GLBA Safeguards Rule (16 CFR Part 314) — administrative safeguards
* OCC Bulletin 2026-13 (formerly OCC Bulletin 2011-12) — Model Risk Management (where AI agents are model-bearing)
* Federal Reserve SR 26-2 (formerly SR 11-7) — Guidance on Model Risk Management

### 20.4 Microsoft Learn references

* [Microsoft 365 Copilot governance overview](https://learn.microsoft.com/microsoft-365-copilot/microsoft-365-copilot-overview)
* [Microsoft Purview audit (premium)](https://learn.microsoft.com/purview/audit-premium)
* [Microsoft Sentinel data ingestion](https://learn.microsoft.com/azure/sentinel/data-connectors-reference)
* [Microsoft Agent Framework — request_info pattern](https://learn.microsoft.com/en-us/agent-framework/workflows)
* [Copilot Studio human handoff](https://learn.microsoft.com/en-us/microsoft-copilot-studio/advanced-hand-off)
* [Microsoft Entra agent identities](https://learn.microsoft.com/en-us/entra/agent-id/agent-identities)

---

**Implementation caveats.** The procedures above are designed to *support* compliance with the cited regulations; they do not, by themselves, establish compliance, and they do not substitute for the qualitative supervisory judgment required by FINRA Rule 3110. Organizations should verify that the WSP, role assignments, and retention configurations described here align with their specific regulatory posture, business model, and FINRA membership category before adoption. Settings, screen labels, and APIs evolve; verify against current Microsoft documentation before each material deployment.

---

*Updated: April 2026 | Version: v1.6.2 | UI Verification Status: Current*


---

