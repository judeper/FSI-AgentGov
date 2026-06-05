# Control 3.6 — Verification & Testing Playbook (Orphaned Agent Detection and Remediation)

**Control:** 3.6 — Orphaned Agent Detection and Remediation
**Pillar:** 3 — Reporting
**Audience:** AI Governance Lead, Compliance Officer, AI Administrator, Power Platform Admin, Entra Agent ID Admin, Entra Identity Governance Admin, Entra Global Reader, Purview Compliance Admin, HR / People Operations liaison, Internal Audit
**Cloud scope:** Microsoft 365 Commercial (Global) cloud. This framework targets the commercial Microsoft 365 deployment surface for US financial-services customers.
**Last UI verified:** April 2026

---

## Document Conventions

This playbook is the verification-and-testing artifact for [Control 3.6 — Orphaned Agent Detection and Remediation](../../../controls/pillar-3-reporting/3.6-orphaned-agent-detection-and-remediation.md). It is authored against framework version v1.4 and cites Microsoft UI and API surfaces as last verified in April 2026.

- **Hedged regulatory language.** This playbook supports compliance with FINRA Rule 3110 (Supervision), FINRA Rule 4511 (Books and Records), FINRA RN 24-09 / Rule 3110 (Generative-AI Supervision), SEC Rules 17a-3 / 17a-4 (Records and Retention), SOX Sections 302 / 404 (Internal Control over Financial Reporting), GLBA §501(b), OCC Bulletin 2026-13 (formerly OCC Bulletin 2011-12), Federal Reserve SR 26-2 (formerly SR 11-7) (Model Risk Management), CFTC Regulation 1.31, and NYDFS 23 NYCRR Part 500. A clean execution **does not guarantee** compliance, **does not replace** written supervisory procedures, and **supports — does not replace — registered-principal supervisory review under FINRA Rule 3110**. Implementation requires organization-specific risk assessment and legal review. Organizations should verify current Microsoft Learn documentation and tenant entitlements at each cycle.
- **Canonical role names.** AI Administrator, Power Platform Admin, Entra Agent ID Admin, Entra Identity Governance Admin, Entra Global Reader, AI Governance Lead, Compliance Officer, Purview Compliance Admin, HR / People Operations. No title substitution (for example, "Global Administrator" is not a substitute for "Entra Global Admin").
- **Terminology.** The framework term is **orphaned agent** (five loss-of-accountability categories — see the control document); Microsoft surface terminology is **ownerless agent** (narrow definition — owner principal unset). Every ownerless agent is an orphaned agent; not every orphaned agent is ownerless.
- **Backtick rule.** Code identifiers are fenced with backticks in body text but not inside headings.
- **PowerShell 7.4 + Pester 5.5.** All automated assertions use Pester 5.5 `Describe/Context/It` blocks; all code is executable against PowerShell 7.4. Module versions are pinned in §0.2.
- **Evidence schema.** Every test emits a JSON evidence record conforming to §1.3. The §14 pack assembler refuses to publish packs containing records that fail schema validation.
- **What this playbook does NOT claim.** It does not prove the absence of undiscovered shadow agents; it does not replace the registered-principal supervisory review required by FINRA Rule 3110 where that rule applies; it does not guarantee commercial-cloud feature availability; and it does not substitute for the firm's written supervisory procedures or books-and-records program.

---

## §0 Pre-Test Prerequisites

### 0.1 Operator role prerequisites

Orphan detection, reconciliation, and remediation read from identity, directory, Power Platform, SharePoint, Purview, and HR-connector surfaces, and write to the orphan register and to remediation ticketing. Read/write separation is enforced: every Pester suite in §2–§12 is **read-only**; any remediation cited from a FAIL routes to the sister [PowerShell Setup](./powershell-setup.md) or [Portal Walkthrough](./portal-walkthrough.md) under its own change ticket and its own write scopes.

| Role (canonical) | Required for | PIM activation window |
|---|---|---|
| AI Administrator | Reads Agent 365 Ownerless Agents card, agent inventory, inline Assign-Owner evidence; signs DETECT and RECONCILE evidence | 4 hours, just-in-time |
| Power Platform Admin | Reads PPAC agent / environment / maker metadata; exports `Get-AdminPowerApp`, `Get-AdminPowerAppEnvironment`; reads Dataverse maker tables | 4 hours, just-in-time |
| Entra Agent ID Admin | Reads Microsoft Entra Agent ID sponsor tasks, lifecycle-workflow run history, service-principal state | 4 hours, just-in-time |
| Entra Identity Governance Admin | Reads HR connector attribute mapping (`employeeLeaveDateTime`), lifecycle-workflow definitions | 4 hours, just-in-time |
| Entra Global Reader | Read-only Entra user / service-principal / sign-in evidence; witness-role for dual-control attestation in §14 | 4 hours, standing permissible |
| Purview Compliance Admin | Reads retention-label configuration bound to the orphan register and snapshots; reads UAL evidence for SIEM forwarding | 4 hours |
| AI Governance Lead | Owns the orphan register; counter-signs REASSIGN, TERMINAL, and quarterly attestation evidence | Standing with quarterly recertification per Control 2.8 |
| Compliance Officer | Counter-signs TERMINAL delete decisions; counter-signs quarterly attestation | Standing |
| HR / People Operations liaison | Confirms HR connector feed integrity (leaver / mover / joiner with `employeeLeaveDateTime`) that drives SPONSOR and HR namespaces | Standing, read-only |

> **Least privilege.** No operator should hold **Entra Global Admin** persistently. This playbook does not require Global Admin; if a tenant insists on it for Agent 365 blade reads, activate through Entra PIM time-bound, never standing. Standing privileged role overlap between Preparer / Validator / Compliance signatories is a cycle-stopping FAIL (see §14).

### 0.2 Module baseline

Pin to specific module versions so evidence packs are reproducible across machines and across time. Re-validate against newer module versions before promoting them to the standing schedule.

```powershell
#Requires -Version 7.4
#Requires -Modules @{ ModuleName='Microsoft.Graph.Authentication';             ModuleVersion='2.25.0' }
#Requires -Modules @{ ModuleName='Microsoft.Graph.Users';                      ModuleVersion='2.25.0' }
#Requires -Modules @{ ModuleName='Microsoft.Graph.Identity.DirectoryManagement'; ModuleVersion='2.25.0' }
#Requires -Modules @{ ModuleName='Microsoft.Graph.Identity.Governance';        ModuleVersion='2.25.0' }
#Requires -Modules @{ ModuleName='Microsoft.Graph.Beta.Applications';          ModuleVersion='2.25.0' }
#Requires -Modules @{ ModuleName='Microsoft.PowerApps.Administration.PowerShell'; ModuleVersion='2.0.200' }
#Requires -Modules @{ ModuleName='MicrosoftTeams';                             ModuleVersion='6.5.0'  }
#Requires -Modules @{ ModuleName='ExchangeOnlineManagement';                   ModuleVersion='3.5.0'  }
#Requires -Modules @{ ModuleName='Pester';                                     ModuleVersion='5.5.0'  }

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'
$ProgressPreference    = 'SilentlyContinue'
```

> **Note on Agent 365 Graph endpoints.** The `/beta/agentGovernance` Graph branch exposes the Ownerless Agents card data as of the verification date. Noun names and module distribution are still stabilising across 2026 Wave 1. Wrapper functions (`Get-Agt36OwnerlessCard`, `Get-Agt36AgentInventory`, `Get-Agt36SponsorTask`) are defined in the sister [PowerShell Setup](./powershell-setup.md). Re-verify module / noun availability after each Microsoft release wave.

### 0.3 PRE gates (must all pass before §2–§12 execute)

`Invoke-Agt36PreFlight.ps1` runs nine pre-flight gates. Any `FAIL` halts the suite and emits a single `preflight-FAILED-<runId>.json`. 

| Gate | ID | Purpose | Failure behavior |
|---|---|---|---|
| Module presence | PRE-01 | Confirms modules loaded at the pinned versions in §0.2 | HALT |
| Graph context | PRE-02 | Confirms `Connect-MgGraph` with scopes `AgentGovernance.Read.All`, `Directory.Read.All`, `User.Read.All`, `Application.Read.All`, `LifecycleWorkflows.Read.All`, `AuditLog.Read.All`, `Reports.Read.All` | HALT |
| Tenant identification | PRE-03 | Captures `tenantId`, `displayName`, `verifiedDomains[0].name` for every evidence record | HALT |
| Cloud detection | PRE-04 | Reads `(Get-MgContext).Environment`; confirms `Commercial` | HALT if not commercial |
| HR connector health | PRE-05 | Confirms at least one Entra HR provisioning connector with status `Healthy` in the last 24h and last-sync within tenant SLA | HALT — without HR feed, SPONSOR and HR namespaces cannot attest |
| Agent 365 Ownerless card reachability | PRE-06 | Probes `/beta/agentGovernance/ownerlessAgents?$top=1`; any error → HALT | HALT |
| Orphan register endpoint | PRE-07 | Confirms the SharePoint or Dataverse orphan register is reachable, has versioning enabled, and is bound to a `≥6-year` Purview retention label with `deletionLocked=true` | HALT — without the system of record, no evidence can be assembled |
| Clock skew gate | PRE-08 | Compares local UTC to Graph `Date` header; aborts on > 60s drift | HALT — skew invalidates timestamp evidence under FINRA 4511 / SEC 17a-4 |
| Evidence root writeable | PRE-09 | Confirms `$env:AGT36_EVIDENCE_ROOT` exists, is writeable, resolves to WORM-eligible storage | HALT |

### 0.4 Run identifier and evidence root

```powershell
function New-Agt36RunId {
    $ts   = (Get-Date).ToUniversalTime().ToString('yyyyMMdd-HHmmss')
    $guid = ([guid]::NewGuid().ToString('N')).Substring(0,8)
    "AGT36-$ts-$guid"
}

$script:RunId        = New-Agt36RunId
$script:RunTimestamp = (Get-Date).ToUniversalTime().ToString('o')
$script:EvidenceRoot = Join-Path $env:AGT36_EVIDENCE_ROOT $script:RunId
New-Item -Path $script:EvidenceRoot -ItemType Directory -Force | Out-Null
```

Every evidence record written in §2–§12 is stored under `$script:EvidenceRoot` and the `runId` is embedded in each artifact filename that is assembled into the §14 evidence pack.

---

## §1 Namespace Catalog

The eight Verification Criteria from [Control 3.6 §Verification Criteria](../../../controls/pillar-3-reporting/3.6-orphaned-agent-detection-and-remediation.md#verification-criteria) — hereafter "VC-1 … VC-8" — are evidenced by the eight test namespaces below. Each namespace produces independent evidence records that combine into a single signed pack (§14).

| Namespace | Section | Evidences | Cadence | Owner |
|---|---|---|---|---|
| `DETECT` | §2 | VC-1 — Detection-run completeness (all 10 signal sources, all zones) | Weekly (Z3 sample 100%); ≥4 weeks/quarter (Z2, Z1) | AI Administrator |
| `RECONCILE` | §3 | VC-2 — Agent 365 Ownerless card count vs orphan register category-1 count (zero variance unsubstantiated) | Per cycle × 4/quarter | AI Governance Lead |
| `TERMINAL` | §4 | VC-3 — Per-category, per-zone SLA adherence (≥95% Z3); **and** VC-5 — Archive/delete approval evidence (Z3 dual approval, ITSM ref, retention-label state) | Weekly | AI Governance Lead |
| `REASSIGN` | §5 | VC-4 — Reassignment integrity: sample 10/quarter, new-owner prerequisites, permission/metadata transfer | Quarterly (sample) | Power Platform Admin |
| `HR` | §6 | Supporting — HR leaver / mover / `employeeLeaveDateTime` feed integrity that powers sponsor / owner / maker-departure detection | Weekly | Entra Identity Governance Admin |
| `SPONSOR` | §7 | Supporting — Entra Agent ID sponsor-departure cascade (one sponsor → many agents); feeds DETECT category #2 | Per cycle | Entra Agent ID Admin |
| `BULK` | §8 | Supporting — Bulk-reassign safety (dry-run, exclusion of distribution-list-owned agents, false-positive rate) | Per bulk run | Power Platform Admin |
| `SIEM` | §9 | Supporting — Detection-run logs, remediation tickets, and approval artifacts forwarded to SIEM; 6-year retention enforced | Weekly | Purview Compliance Admin |
| `RETAIN` | §10 | VC-6 — Purview retention-label enforcement on orphan register, snapshots, and approvals (`≥6-year`, deletion locked) | Monthly | Purview Compliance Admin |
| `PREVENT` | §11 | VC-7 — Pre-orphan prevention rate (orphans-avoided ÷ agents-created) with YoY trend | Quarterly | AI Governance Lead |

Each namespace section follows an identical 8-part structure, mirroring the sibling [Control 2.25](../2.25/verification-testing.md) and [Control 2.26](../2.26/verification-testing.md) verification playbooks:

1. **Criterion mapping** — explicit pointer to the numbered VC in Control 3.6.
2. **Pre-conditions** — PRE gates passed; reference data present; Graph scopes granted; zone scope declared.
3. **Pester suite** — `Describe "AGT36-{NS}" { Context "Zone {1|2|3}" { It "…" } }` in Pester 5.5 on PowerShell 7.4.
4. **Sample PASS evidence record** — the exact JSON shape assembled into the evidence pack.
5. **Sample FAIL evidence record** — with a pointer to §15 triage.
6. **Examiner artifact** — filename pattern, retention duration, signing policy.
7. **Zone thresholds** — PASS / WARN / FAIL bands per zone.
8. **Regulator mapping** — which specific regulatory citation each test supports.

### 1.1 Evidence record schema (canonical)

Every evidence record MUST conform to this schema. `Test-Agt36EvidenceSchema` in §14.5 enforces it; the pack assembler refuses to publish a pack containing any record that fails validation.

```json
{
  "control_id": "3.6",
  "run_id": "AGT36-20260415-093012-a1b2c3d4",
  "run_timestamp": "2026-04-15T09:30:12Z",
  "tenant_id": "11111111-2222-3333-4444-555555555555",
  "tenant_display_name": "Contoso Bank, N.A.",
  "cloud": "Commercial",
  "zone": "3",
  "namespace": "DETECT",
  "criterion": "VC-1",
  "subject_id": "detection-cycle-2026W15",
  "subject_type": "detection_run",
  "status": "PASS",
  "assertion": "Weekly detection cycle exercised all 10 signal sources with non-null counts and a signed run-log bundle.",
  "observed_value": {
    "signal_sources_exercised": 10,
    "run_bundle_sha256": "f3a1…",
    "start": "2026-04-14T02:00:00Z",
    "end":   "2026-04-14T02:06:41Z",
    "counts_by_category": { "1":3, "2":1, "3":0, "4":0, "5":0, "6":0, "7":2, "8":0, "9":1, "10":0 }
  },
  "expected_value": {
    "signal_sources_exercised": 10,
    "run_bundle_sha256": "<non-null>",
    "counts_by_category": "<object with keys 1..10>"
  },
  "evidence_artifacts": ["detect-run-AGT36-20260415-093012-a1b2c3d4.json"],
  "regulator_mappings": ["FINRA-4511","FINRA-25-07","SEC-17a-4","SOX-404","NYDFS-500"],
  "remediation_ref": null,
  "operator_upn": "ai.administrator@contoso.com",
  "schema_version": "1.0"
}
```

Field semantics (abbreviated where identical to peer controls):

| Field | Type | Notes |
|---|---|---|
| `control_id` | string | Always `"3.6"` for this playbook. |
| `run_id` | string | Output of `New-Agt36RunId`; identical across every record in a run. |
| `cloud` | enum | `Commercial`. |
| `zone` | enum | `1 / 2 / 3 / all`. |
| `namespace` | enum | One of `DETECT / RECONCILE / TERMINAL / REASSIGN / HR / SPONSOR / BULK / SIEM / RETAIN / PREVENT`. |
| `criterion` | enum | `VC-1` … `VC-8`, `supporting`, or `VC-1..8 (compensating)` for SOV. |
| `subject_id` | string | Agent ID, cycle ID, template ID, policy ID, or workflow ID. |
| `subject_type` | enum | `agent / detection_run / reconciliation / remediation_ticket / reassignment / sponsor_task / hr_feed / retention_label / attestation / manual_attestation`. |
| `status` | enum | `PASS / WARN / FAIL / SKIPPED / ERROR`. |
| `remediation_ref` | string or null | `TRG-{NS}-NN` pointer into §15 when `status != 'PASS'`. |

### 1.2 Regulator mapping vocabulary

| Token | Citation |
|---|---|
| `FINRA-3110` | FINRA Rule 3110 (Supervision) |
| `FINRA-4511` | FINRA Rule 4511 (Books and Records) |
| `FINRA-25-07` | FINRA RN 24-09 / Rule 3110 (Generative-AI Supervision) |
| `SEC-17a-3` | SEC Rule 17a-3 (Records to be Made) |
| `SEC-17a-4` | SEC Rule 17a-4 (Records Retention; WORM requirement) |
| `SOX-302` | Sarbanes-Oxley §302 (Management Certification) |
| `SOX-404` | Sarbanes-Oxley §404 (Internal Control over Financial Reporting) |
| `GLBA-501b` | Gramm-Leach-Bliley Act §501(b) (Safeguards) |
| `OCC-2011-12` | OCC Bulletin 2026-13 (formerly OCC Bulletin 2011-12) (Third-Party / Technology Risk) |
| `FED-SR-11-7` | Federal Reserve SR 26-2 (formerly SR 11-7) (Model Risk Management) |
| `CFTC-1.31` | CFTC Regulation 1.31 (Recordkeeping) |
| `NYDFS-500` | NYDFS 23 NYCRR Part 500 (Cybersecurity) |
| `FFIEC-MGMT` | FFIEC IT Examination Handbook — Management booklet |

> **No FINRA Rule 3110 substitution.** Wherever `FINRA-3110` appears, it indicates that the control element **supports** — does not replace — registered-principal supervisory review of AI-enabled business activity. The firm's written supervisory procedures remain the authoritative supervisory document; this playbook's evidence supports those procedures.

---

## §2 DETECT — Detection-run Completeness (VC-1)

### 2.1 Criterion mapping

This namespace evidences **VC-1** of [Control 3.6 §Verification Criteria](../../../controls/pillar-3-reporting/3.6-orphaned-agent-detection-and-remediation.md#verification-criteria): "Weekly detection cycle exercised all ten signal sources for Zone 3 (100% sample) and at least four cycles per quarter for Zone 2 and Zone 1, with a signed run-log bundle persisted to evidence storage." It is the foundational completeness assertion: every downstream namespace (RECONCILE, TERMINAL, REASSIGN, SPONSOR) presupposes that DETECT ran end-to-end.

### 2.2 Pre-conditions

- PRE-01 through PRE-09 PASS.
- The 10 Detection Signal Sources defined in [Control 3.6 §Detection Signal Sources](../../../controls/pillar-3-reporting/3.6-orphaned-agent-detection-and-remediation.md#detection-signal-sources) are wired into the weekly job: (1) Ownerless agent, (2) Sponsor-departed, (3) Maker-departed, (4) Environment-owner departed, (5) SharePoint agent author disabled, (6) Environment deleted, (7) Inactivity, (8) License expired, (9) Broken connector, (10) Shadow agent.
- Per-zone cadence configured: Z3 weekly 100%; Z2 ≥4 cycles/quarter; Z1 ≥4 cycles/quarter.
- Run-log signing key (X.509 or sigstore) present in the orchestrator key vault; thumbprint pinned in `Agt36Config.psd1`.

### 2.3 Pester suite

```powershell
Describe "AGT36-DETECT" -Tag 'Control3.6','VC-1' {

    BeforeAll {
        $script:Cycles = Get-Agt36DetectionCycle -LookbackDays 100
    }

    Context "Zone 3 — weekly cycles, 100% sample" {

        It "exercises all 10 signal sources in every Z3 cycle" {
            foreach ($c in $script:Cycles | Where-Object Zone -eq 3) {
                $c.SignalSourcesExercised | Should -Be 10 -Because "Z3 cycle $($c.CycleId) must cover all 10 categories"
            }
        }

        It "persists a signed run-log bundle for every Z3 cycle" {
            foreach ($c in $script:Cycles | Where-Object Zone -eq 3) {
                $c.RunLogBundleSha256        | Should -Not -BeNullOrEmpty
                $c.RunLogSignatureValid      | Should -BeTrue
                $c.RunLogSignerThumbprint    | Should -Be (Get-Agt36Config).RunLogSignerThumbprint
            }
        }

        It "completes the cycle within the orchestrator's 60-minute SLA" {
            foreach ($c in $script:Cycles | Where-Object Zone -eq 3) {
                ($c.End - $c.Start).TotalMinutes | Should -BeLessOrEqual 60
            }
        }
    }

    Context "Zone 2 — at least four cycles per quarter" {
        It "has ≥4 completed Z2 cycles in the trailing 92 days" {
            ($script:Cycles | Where-Object Zone -eq 2).Count | Should -BeGreaterOrEqual 4
        }
    }

    Context "Zone 1 — at least four cycles per quarter" {
        It "has ≥4 completed Z1 cycles in the trailing 92 days" {
            ($script:Cycles | Where-Object Zone -eq 1).Count | Should -BeGreaterOrEqual 4
        }
    }

    Context "Cross-zone integrity" {
        It "produces non-null counts_by_category for all 10 categories in every cycle" {
            foreach ($c in $script:Cycles) {
                1..10 | ForEach-Object { $c.CountsByCategory.ContainsKey([string]$_) | Should -BeTrue }
            }
        }
    }
}
```

### 2.4 Sample PASS evidence record

```json
{
  "control_id": "3.6",
  "run_id": "AGT36-20260415-093012-a1b2c3d4",
  "namespace": "DETECT",
  "criterion": "VC-1",
  "zone": "3",
  "subject_id": "detection-cycle-2026W15",
  "subject_type": "detection_run",
  "status": "PASS",
  "assertion": "Z3 weekly cycle exercised all 10 signal sources, signed bundle persisted, SLA met.",
  "observed_value": {
    "signal_sources_exercised": 10,
    "run_bundle_sha256": "f3a1b9c4e7…",
    "run_log_signer_thumbprint": "9F:2A:11:…",
    "duration_minutes": 6.7
  },
  "evidence_artifacts": ["detect-run-2026W15-AGT36-20260415-093012-a1b2c3d4.json","detect-run-2026W15.sig"],
  "regulator_mappings": ["FINRA-4511","FINRA-25-07","SEC-17a-3","SEC-17a-4","SOX-404","NYDFS-500","FED-SR-11-7"]
}
```

### 2.5 Sample FAIL evidence record

```json
{
  "control_id": "3.6",
  "run_id": "AGT36-20260415-093012-a1b2c3d4",
  "namespace": "DETECT",
  "criterion": "VC-1",
  "zone": "3",
  "subject_id": "detection-cycle-2026W14",
  "subject_type": "detection_run",
  "status": "FAIL",
  "assertion": "Z3 cycle exercised only 9 of 10 signal sources; category 9 (broken-connector) skipped due to connector-API throttling.",
  "observed_value": { "signal_sources_exercised": 9, "missing_categories": [9], "throttle_429_count": 47 },
  "remediation_ref": "TRG-DETECT-02",
  "regulator_mappings": ["FINRA-4511","SEC-17a-4","SOX-404"]
}
```

### 2.6 Examiner artifact

| Item | Value |
|---|---|
| Filename pattern | `detect-run-{YYYYWww}-{runId}.json` plus signed bundle `*.sig` |
| Storage | Evidence root → assembled into §14 pack |
| Retention | 6 years WORM, Purview retention label `FSI-Records-6Y-WORM`, deletion locked |
| Signing | X.509 detached signature; signer = orchestrator service principal; counter-signed at pack assembly by AI Governance Lead |

### 2.7 Zone thresholds

| Zone | PASS | WARN | FAIL |
|---|---|---|---|
| 3 | All weekly cycles cover 10/10 sources, signed | One cycle covered 9/10 with documented re-run within 24h | Any uncompensated coverage gap, or missing signature |
| 2 | ≥4 cycles/quarter, ≥9/10 average coverage | 3 cycles/quarter | <3 cycles/quarter |
| 1 | ≥4 cycles/quarter, ≥8/10 average coverage | 3 cycles/quarter | <3 cycles/quarter |

### 2.8 Regulator mapping

| Regulator | Specifically supported by VC-1 |
|---|---|
| FINRA Rule 4511 / SEC 17a-3 | Continuous capture of identity-and-accountability change events for AI-enabled business activity |
| FINRA RN 24-09 / Rule 3110 | Documented periodic monitoring of generative-AI inventory accountability |
| SOX §404 | Operating effectiveness of the detection control over financial-reporting-relevant agents |
| NYDFS Part 500 | Documented monitoring activity on technology assets |
| Federal Reserve SR 26-2 (formerly SR 11-7) | Ongoing model-risk monitoring on identity-bound model assets |

---

## §3 RECONCILE — Card-vs-Register Parity (VC-2)

### 3.1 Criterion mapping

VC-2: "For every reconciliation cycle, the count from the Microsoft 365 Agent 365 Ownerless Agents card equals the count of category-1 (ownerless-narrow) entries in the orphan register; any variance is documented with a substantiation memo and a corrective action."

### 3.2 Pre-conditions

- DETECT cycle for the same window has PASS status.
- AI Administrator can read the Ownerless Agents card via Graph (`/beta/agentGovernance/ownerlessAgents`) or Agent 365 admin center.
- Orphan register query supports filter `category=1 AND status IN ('open','reassigned-pending','terminal-pending')`.

### 3.3 Pester suite

```powershell
Describe "AGT36-RECONCILE" -Tag 'Control3.6','VC-2' {

    BeforeAll {
        $script:Card     = Get-Agt36OwnerlessCard
        $script:Register = Get-Agt36OrphanRegister -Category 1 -Status 'open','reassigned-pending','terminal-pending'
    }

    Context "Snapshot parity at cycle close" {
        It "card count equals register category-1 open-set count" {
            $script:Card.Count | Should -Be $script:Register.Count
        }

        It "every card-listed agent appears in the register with category=1" {
            foreach ($a in $script:Card.Agents) {
                $script:Register.AgentId | Should -Contain $a.AgentId
            }
        }

        It "no register category-1 entry is missing from the card" {
            foreach ($r in $script:Register) {
                $script:Card.Agents.AgentId | Should -Contain $r.AgentId
            }
        }
    }

    Context "Variance substantiation (when present)" {
        It "every documented variance carries a substantiation memo and corrective action" {
            $variances = Get-Agt36ReconciliationVariance -CycleId $script:Card.CycleId
            foreach ($v in $variances) {
                $v.SubstantiationMemoUri | Should -Not -BeNullOrEmpty
                $v.CorrectiveActionTicket | Should -Match '^(SNOW|JIRA|REM)-\d+$'
                $v.SignedBy               | Should -Be 'AI Governance Lead'
            }
        }
    }
}
```

### 3.4 Sample PASS evidence record

```json
{
  "control_id": "3.6", "namespace": "RECONCILE", "criterion": "VC-2", "zone": "3",
  "subject_id": "reconcile-2026W15", "subject_type": "reconciliation",
  "status": "PASS",
  "assertion": "Ownerless card count (12) equals orphan register category-1 open-set count (12); zero variance.",
  "observed_value": { "card_count": 12, "register_count": 12, "variance": 0, "card_snapshot_sha256": "1a2b…", "register_snapshot_sha256": "9f8e…" },
  "evidence_artifacts": ["card-snapshot-2026W15.png","card-snapshot-2026W15.csv","register-snapshot-2026W15.csv","reconcile-2026W15.json"],
  "regulator_mappings": ["FINRA-4511","SEC-17a-4","SOX-302","SOX-404","NYDFS-500"]
}
```

### 3.5 Sample FAIL evidence record

```json
{
  "control_id": "3.6", "namespace": "RECONCILE", "criterion": "VC-2", "zone": "3",
  "subject_id": "reconcile-2026W14", "subject_type": "reconciliation",
  "status": "FAIL",
  "assertion": "Card count (12) and register category-1 count (10) diverge by 2; missing entries: agent-aaaa, agent-bbbb.",
  "observed_value": { "card_count": 12, "register_count": 10, "missing_from_register": ["agent-aaaa","agent-bbbb"] },
  "remediation_ref": "TRG-RECONCILE-01",
  "regulator_mappings": ["FINRA-4511","SEC-17a-4","SOX-404"]
}
```

### 3.6 Examiner artifact

| Item | Value |
|---|---|
| Filename | `reconcile-{YYYYWww}-{runId}.json` plus PNG + CSV snapshots of the card |
| Retention | 6 years WORM (matches the "weekly Ownerless Agents card snapshot" line of [Control 3.6 Evidence and Retention](../../../controls/pillar-3-reporting/3.6-orphaned-agent-detection-and-remediation.md#evidence-and-retention)) |
| Signing | Counter-signed by AI Governance Lead at §14 pack assembly |

### 3.7 Zone thresholds

| Zone | PASS | WARN | FAIL |
|---|---|---|---|
| 3 | Variance = 0; or variance fully substantiated within 24h | Variance > 0 substantiated within 72h | Any uncompensated variance > 24h, or missing snapshot |
| 2 | Variance ≤ 5% substantiated within 7d | Variance ≤ 10% substantiated within 14d | Variance > 10% or unsubstantiated |
| 1 | Variance ≤ 10% substantiated within 14d | Variance ≤ 20% substantiated within 30d | Variance > 20% or unsubstantiated |

### 3.8 Regulator mapping

`FINRA-4511`, `SEC-17a-3`, `SEC-17a-4`, `SOX-302`, `SOX-404`, `NYDFS-500`, `OCC-2011-12`. Reconciliation parity is the inventory-completeness test that examiners use to confirm books-and-records integrity for AI-enabled business activity.

---

## §4 TERMINAL — SLA Adherence & Archive/Delete Approval (VC-3, VC-5)

### 4.1 Criterion mapping

This namespace evidences two Verification Criteria:

- **VC-3 — SLA adherence.** Remediation is completed within the per-category, per-zone SLA defined in [Control 3.6 §Detection Signal Sources](../../../controls/pillar-3-reporting/3.6-orphaned-agent-detection-and-remediation.md#detection-signal-sources). Zone 3 SLA attainment must be ≥95% on a rolling 90-day window.
- **VC-5 — Archive/delete approval.** Every Zone 3 archive or delete action carries dual approval (AI Governance Lead + Compliance Officer for delete), an ITSM reference, and evidence that the retention-label state of the agent's records is preserved (`≥6Y WORM`, deletion locked) before the agent object is removed.

### 4.2 Pre-conditions

- DETECT and RECONCILE have PASS for the cycle under review.
- Orphan register exposes each category's remediation timeline (`firstDetectedAt`, `terminalAt`, `terminalKind`, `approverIds[]`, `itsmRef`).
- Purview retention labels are applied to the orphan's records (Dataverse tables, SharePoint sites, Teams messages) per the firm's records schedule.

### 4.3 Detection Signal Sources — SLA reference

Reproduced from [Control 3.6 §Detection Signal Sources](../../../controls/pillar-3-reporting/3.6-orphaned-agent-detection-and-remediation.md#detection-signal-sources). Dates are the maximum elapsed calendar time from **first-detected** to **terminal state** (reassigned, archived, or deleted).

| # | Category | Z3 SLA | Z2 SLA | Z1 SLA |
|---|---|---|---|---|
| 1 | Ownerless (narrow) | 7d | 14d | 30d |
| 2 | Sponsor-departed | real-time / 24h | 10 bd | 10 bd |
| 3 | Maker-departed | 7d | 14d | 30d |
| 4 | Environment-owner departed | 3d | 7d | 14d |
| 5 | SharePoint agent — author disabled | 7d | 14d | 30d |
| 6 | Environment deleted | 3d | 3d | 7d |
| 7 | Inactivity | 30d | 60d | 90d |
| 8 | License expired | 7d | 14d | 30d |
| 9 | Broken connector | 14d | 30d | 30d |
| 10 | Shadow agent | 7d | 14d | 30d |

### 4.4 Pester suite

```powershell
Describe "AGT36-TERMINAL-SLA" -Tag 'Control3.6','VC-3' {

    BeforeAll {
        $script:Sla     = Get-Agt36SlaTable
        $script:Closed  = Get-Agt36OrphanRegister -Status 'terminal' -LookbackDays 90
    }

    Context "Zone 3 — ≥95% on 90-day rolling window" {
        It "per-category Z3 SLA attainment is ≥95%" {
            foreach ($cat in 1..10) {
                $set = $script:Closed | Where-Object { $_.Zone -eq 3 -and $_.Category -eq $cat }
                if (-not $set) { continue }
                $met = $set | Where-Object { ($_.TerminalAt - $_.FirstDetectedAt) -le $script:Sla["Z3-$cat"] }
                ($met.Count / $set.Count) | Should -BeGreaterOrEqual 0.95 -Because "Z3 category $cat"
            }
        }
    }

    Context "Zone 2 — ≥90% rolling" {
        It "per-category Z2 SLA attainment is ≥90%" {
            foreach ($cat in 1..10) {
                $set = $script:Closed | Where-Object { $_.Zone -eq 2 -and $_.Category -eq $cat }
                if (-not $set) { continue }
                $met = $set | Where-Object { ($_.TerminalAt - $_.FirstDetectedAt) -le $script:Sla["Z2-$cat"] }
                ($met.Count / $set.Count) | Should -BeGreaterOrEqual 0.90
            }
        }
    }

    Context "Zone 1 — ≥80% rolling" {
        It "per-category Z1 SLA attainment is ≥80%" {
            foreach ($cat in 1..10) {
                $set = $script:Closed | Where-Object { $_.Zone -eq 1 -and $_.Category -eq $cat }
                if (-not $set) { continue }
                $met = $set | Where-Object { ($_.TerminalAt - $_.FirstDetectedAt) -le $script:Sla["Z1-$cat"] }
                ($met.Count / $set.Count) | Should -BeGreaterOrEqual 0.80
            }
        }
    }
}

Describe "AGT36-TERMINAL-DELETE" -Tag 'Control3.6','VC-5' {

    BeforeAll {
        $script:Deletes = Get-Agt36OrphanRegister -Status 'terminal' -TerminalKind 'delete' -LookbackDays 90
    }

    Context "Zone 3 delete approvals" {
        It "every Z3 delete carries dual approval from AI Governance Lead AND Compliance Officer" {
            foreach ($d in $script:Deletes | Where-Object Zone -eq 3) {
                $d.Approvers.Role | Should -Contain 'AI Governance Lead'
                $d.Approvers.Role | Should -Contain 'Compliance Officer'
                $d.Approvers.Count | Should -BeGreaterOrEqual 2
                ($d.Approvers | Select-Object -ExpandProperty Upn -Unique).Count | Should -Be $d.Approvers.Count
            }
        }

        It "every Z3 delete references a closed ITSM change ticket" {
            foreach ($d in $script:Deletes | Where-Object Zone -eq 3) {
                $d.ItsmRef           | Should -Match '^(SNOW|JIRA|CHG)-\d+$'
                $d.ItsmTicketState   | Should -BeIn @('Closed','Resolved','Implemented')
            }
        }

        It "retention label on the agent's records is ≥6Y WORM and deletion-locked" {
            foreach ($d in $script:Deletes | Where-Object Zone -eq 3) {
                $d.RetentionLabel.RetentionDurationDays | Should -BeGreaterOrEqual 2190
                $d.RetentionLabel.IsDeletionLocked       | Should -BeTrue
                $d.RetentionLabel.BehaviorDuringRetentionPeriod | Should -BeIn @('retainAsRecord','retainAsRegulatoryRecord')
            }
        }
    }

    Context "Zone 3 archive approvals" {
        It "every Z3 archive carries at least AI Governance Lead approval" {
            foreach ($a in (Get-Agt36OrphanRegister -Status 'terminal' -TerminalKind 'archive' -Zone 3 -LookbackDays 90)) {
                $a.Approvers.Role | Should -Contain 'AI Governance Lead'
                $a.ItsmRef        | Should -Match '^(SNOW|JIRA|CHG)-\d+$'
            }
        }
    }
}
```

### 4.5 Sample PASS evidence record (delete)

```json
{
  "control_id": "3.6", "namespace": "TERMINAL", "criterion": "VC-5", "zone": "3",
  "subject_id": "agent-1e2f3a4b", "subject_type": "remediation_ticket",
  "status": "PASS",
  "assertion": "Z3 delete approved by AI Governance Lead AND Compliance Officer; ITSM CHG-44821 Closed; retention label 10Y WORM deletion-locked.",
  "observed_value": {
    "terminal_kind": "delete",
    "approvers": [
      { "role": "AI Governance Lead", "upn": "jane.doe@contoso.com",  "approved_at": "2026-04-14T16:02:11Z" },
      { "role": "Compliance Officer",  "upn": "carlos.k@contoso.com", "approved_at": "2026-04-14T16:11:44Z" }
    ],
    "itsm_ref": "CHG-44821", "itsm_state": "Closed",
    "retention_label": { "name": "FSI-Records-10Y-WORM", "retention_days": 3650, "deletion_locked": true, "behavior": "retainAsRegulatoryRecord" },
    "category": 1, "first_detected_at": "2026-04-09T02:00:00Z", "terminal_at": "2026-04-14T18:03:00Z", "elapsed_days": 5.7
  },
  "evidence_artifacts": ["terminal-agent-1e2f3a4b.json","approval-CHG-44821.pdf","retention-label-FSI-Records-10Y-WORM.json"],
  "regulator_mappings": ["FINRA-3110","FINRA-4511","SEC-17a-4","SOX-302","SOX-404","GLBA-501b","NYDFS-500"]
}
```

### 4.6 Sample FAIL evidence record

```json
{
  "control_id": "3.6", "namespace": "TERMINAL", "criterion": "VC-5", "zone": "3",
  "subject_id": "agent-9c8d7e6f", "subject_type": "remediation_ticket",
  "status": "FAIL",
  "assertion": "Z3 delete carries only one approver (AI Governance Lead); Compliance Officer approval missing; dual-control violated.",
  "observed_value": { "approvers": [ { "role": "AI Governance Lead", "upn": "jane.doe@contoso.com" } ], "terminal_kind": "delete" },
  "remediation_ref": "TRG-TERMINAL-03",
  "regulator_mappings": ["FINRA-3110","SEC-17a-4","SOX-404"]
}
```

### 4.7 Examiner artifact

| Item | Value |
|---|---|
| Filename | `terminal-{agentId}.json` plus `approval-{itsmRef}.pdf` and retention-label export |
| Retention | 6 years WORM (remediation-ticket and approval-artifact rows of Evidence and Retention) |
| Signing | ITSM approval PDF (system signature) + AI Governance Lead pack counter-signature |

### 4.8 Zone thresholds

| Zone | PASS (VC-3) | PASS (VC-5 delete) |
|---|---|---|
| 3 | ≥95% SLA attainment per category | Dual approval (AI Governance Lead + Compliance Officer), ITSM Closed, retention ≥6Y WORM locked |
| 2 | ≥90% SLA attainment per category | Single approval (AI Governance Lead) + ITSM |
| 1 | ≥80% SLA attainment per category | Single approval + ITSM |

### 4.9 Regulator mapping

`FINRA-3110` (supports registered-principal supervisory review — does not replace it), `FINRA-4511`, `FINRA-25-07`, `SEC-17a-3`, `SEC-17a-4`, `SOX-302`, `SOX-404`, `GLBA-501b`, `OCC-2011-12`, `FED-SR-11-7`, `NYDFS-500`.

---

## §5 REASSIGN — Reassignment Integrity (VC-4)

### 5.1 Criterion mapping

VC-4: "On a sample of at least ten reassignments per quarter, the new owner meets all prerequisites (license, environment membership, maker / admin role) and the full set of agent permissions and metadata transferred atomically before the old accountability was severed." This is the regulator's favourite integrity test because it prevents a permissions-gap window and preserves books-and-records custody.

### 5.2 Pre-conditions

- DETECT, RECONCILE, and TERMINAL (reassign kind) have PASS status for the period.
- Sample frame: all Z3 reassignments in the quarter; if >10, sample 10 at random with reproducible seed; if <10, sample all.
- Pre/post snapshots captured by the orchestrator at `T-0` (before reassign) and `T+1` (after reassign).

### 5.3 Pester suite

```powershell
Describe "AGT36-REASSIGN" -Tag 'Control3.6','VC-4' {

    BeforeAll {
        $script:Sample = Get-Agt36ReassignmentSample -QuarterId (Get-Agt36Quarter) -MinSize 10
    }

    Context "New-owner prerequisites" {
        It "new owner holds the required license" {
            foreach ($r in $script:Sample) {
                $r.NewOwner.Licenses | Should -Contain (Get-Agt36Config).RequiredOwnerLicenseSku
            }
        }
        It "new owner is a member of the agent's Power Platform environment" {
            foreach ($r in $script:Sample) {
                $r.NewOwner.EnvironmentRoles[$r.EnvironmentId] | Should -BeIn @('EnvironmentMaker','EnvironmentAdmin','SystemAdministrator')
            }
        }
        It "new owner is a distinct security principal from the departed owner" {
            foreach ($r in $script:Sample) {
                $r.NewOwner.ObjectId | Should -Not -Be $r.OldOwner.ObjectId
                $r.NewOwner.UserType | Should -Be 'Member'
            }
        }
        It "new owner is not a distribution list or shared mailbox" {
            foreach ($r in $script:Sample) {
                $r.NewOwner.PrincipalType | Should -BeIn @('User','Group:Security','ServicePrincipal:ManagedIdentity')
                if ($r.NewOwner.PrincipalType -eq 'Group:Security') {
                    $r.NewOwner.IsAssignableToRole | Should -BeTrue
                    $r.NewOwner.IsMailEnabled      | Should -BeFalse
                }
            }
        }
    }

    Context "Permission and metadata transfer integrity" {
        It "all agent permissions present at T-0 are present at T+1 on the new owner" {
            foreach ($r in $script:Sample) {
                $missing = Compare-Object $r.Before.PermissionSet $r.After.PermissionSet -PassThru |
                           Where-Object SideIndicator -eq '<='
                $missing | Should -BeNullOrEmpty
            }
        }
        It "agent metadata (display name, description, environment, connection refs) is byte-identical except the owner field" {
            foreach ($r in $script:Sample) {
                $diff = Compare-Agt36AgentMetadata -Before $r.Before.Metadata -After $r.After.Metadata -IgnoreFields 'owner','modifiedBy','modifiedOn'
                $diff | Should -BeNullOrEmpty
            }
        }
        It "old owner accountability is severed only after new owner accepts" {
            foreach ($r in $script:Sample) {
                $r.NewOwner.AcceptedAt | Should -BeLessOrEqual $r.OldOwner.RemovedAt
            }
        }
    }
}
```

### 5.4 Sample PASS evidence record

```json
{
  "control_id": "3.6", "namespace": "REASSIGN", "criterion": "VC-4", "zone": "3",
  "subject_id": "agent-4a5b6c7d", "subject_type": "reassignment",
  "status": "PASS",
  "assertion": "New owner Lin Zhou has license, env-maker role, accepted at 2026-03-12T14:02Z; permission set and metadata identical pre/post.",
  "observed_value": {
    "old_owner_upn": "departed.user@contoso.com",
    "new_owner_upn": "lin.zhou@contoso.com",
    "new_owner_accepted_at": "2026-03-12T14:02:10Z",
    "old_owner_removed_at":  "2026-03-12T14:02:14Z",
    "permission_delta": [],
    "metadata_delta_ignoring_owner": []
  },
  "evidence_artifacts": ["reassign-agent-4a5b6c7d.json","reassign-agent-4a5b6c7d-before.json","reassign-agent-4a5b6c7d-after.json"],
  "regulator_mappings": ["FINRA-3110","FINRA-4511","SEC-17a-4","SOX-404","GLBA-501b","NYDFS-500"]
}
```

### 5.5 Sample FAIL evidence record

```json
{
  "control_id": "3.6", "namespace": "REASSIGN", "criterion": "VC-4", "zone": "3",
  "subject_id": "agent-8e9f0a1b", "subject_type": "reassignment",
  "status": "FAIL",
  "assertion": "New owner lacks required Power Platform per-user license; reassignment committed without prerequisite.",
  "observed_value": { "new_owner_upn":"a.b@contoso.com", "missing_license":"POWERAUTOMATE_ATTENDED_RPA" },
  "remediation_ref": "TRG-REASSIGN-01",
  "regulator_mappings": ["FINRA-4511","SOX-404","NYDFS-500"]
}
```

### 5.6 Examiner artifact

| Item | Value |
|---|---|
| Filename | `reassign-{agentId}.json`, plus `before.json` / `after.json` snapshots |
| Retention | 6 years WORM (sponsor/owner reassignment approval row of Evidence and Retention) |
| Signing | Power Platform Admin performs; AI Governance Lead counter-signs at pack assembly |

### 5.7 Zone thresholds

| Zone | PASS | WARN | FAIL |
|---|---|---|---|
| 3 | 10/10 sample passes all four checks | 9/10 with a documented corrective action | ≤8/10 or any atomicity breach |
| 2 | 8/10 sample passes | 7/10 with corrective action | ≤6/10 |
| 1 | 7/10 sample passes | 6/10 with corrective action | ≤5/10 |

### 5.8 Regulator mapping

`FINRA-3110`, `FINRA-4511`, `FINRA-25-07`, `SEC-17a-4`, `SOX-302`, `SOX-404`, `GLBA-501b`, `OCC-2011-12`, `NYDFS-500`.

---

## §6 HR — HR Connector Feed Integrity (Supporting)

### 6.1 Criterion mapping

Supporting evidence for VC-1 / VC-3: the orphan detector cannot detect sponsor-departed, maker-departed, or environment-owner-departed orphans without a healthy HR connector providing `employeeLeaveDateTime`, `employeeHireDate`, `employeeId`, and termination event signals to Microsoft Entra. A broken or stale HR feed silently breaks four of the ten Detection Signal Sources.

### 6.2 Pre-conditions

- Entra Identity Governance Admin can read `/identityGovernance/workflowsHrSync/connectors`.
- HR connector has been configured per Control 2.26 (Entra Agent ID — Identity Governance for Agents).

### 6.3 Pester suite

```powershell
Describe "AGT36-HR" -Tag 'Control3.6','Supporting' {

    BeforeAll {
        $script:Connectors = Get-Agt36HrConnector
    }

    Context "Connector health and freshness" {
        It "at least one HR connector is in Healthy state" {
            ($script:Connectors | Where-Object Status -eq 'Healthy').Count | Should -BeGreaterOrEqual 1
        }
        It "last successful sync is within the tenant freshness SLA" {
            foreach ($c in $script:Connectors) {
                ((Get-Date).ToUniversalTime() - $c.LastSuccessfulSyncUtc).TotalHours | Should -BeLessOrEqual 24
            }
        }
        It "employeeLeaveDateTime attribute is mapped and populated for ≥98% of leavers in last 30 days" {
            $leavers = Get-Agt36HrLeaver -LookbackDays 30
            $populated = $leavers | Where-Object { $_.EmployeeLeaveDateTime -ne $null }
            ($populated.Count / [math]::Max(1,$leavers.Count)) | Should -BeGreaterOrEqual 0.98
        }
    }

    Context "Cascading impact on Detection Signal Sources" {
        It "every leaver in last 30 days surfaces as a sponsor / maker / owner departure event when applicable" {
            foreach ($l in (Get-Agt36HrLeaver -LookbackDays 30)) {
                $cascade = Get-Agt36DepartureCascade -PrincipalId $l.PrincipalId
                $cascade.Detected | Should -BeTrue -Because "leaver $($l.Upn) must be reflected in detection signals"
            }
        }
    }
}
```

### 6.4 Sample PASS evidence record

```json
{
  "control_id": "3.6", "namespace": "HR", "criterion": "supporting", "zone": "all",
  "subject_id": "hr-connector-workday-prod", "subject_type": "hr_feed",
  "status": "PASS",
  "assertion": "Workday HR connector Healthy, last sync 2h22m ago, 99.4% of last-30-day leavers carry employeeLeaveDateTime.",
  "observed_value": { "status":"Healthy", "last_sync_age_minutes":142, "leavers_with_leave_date_pct":0.994, "leavers_count":491 },
  "evidence_artifacts": ["hr-feed-2026W15.json"],
  "regulator_mappings": ["FINRA-4511","SEC-17a-4","SOX-404","GLBA-501b","NYDFS-500"]
}
```

### 6.5 Sample FAIL evidence record

```json
{
  "control_id":"3.6","namespace":"HR","criterion":"supporting","zone":"all",
  "subject_id":"hr-connector-workday-prod","subject_type":"hr_feed",
  "status":"FAIL",
  "assertion":"HR connector last successful sync is 38h ago — exceeds 24h freshness SLA. Sponsor/maker departure cascade is at risk.",
  "observed_value":{"status":"Degraded","last_sync_age_minutes":2280},
  "remediation_ref":"TRG-HR-01",
  "regulator_mappings":["FINRA-4511","SOX-404","NYDFS-500"]
}
```

### 6.6 Examiner artifact, thresholds, regulators

| Item | Value |
|---|---|
| Retention | 1 year operational + roll-up summary in 6Y attestation pack |
| Z3 PASS | Healthy + ≤24h sync age + ≥98% leave-date populated |
| Z2/Z1 PASS | Healthy + ≤72h sync age + ≥95% leave-date populated |
| Regulators | `FINRA-4511`, `SEC-17a-4`, `SOX-404`, `GLBA-501b`, `NYDFS-500`, `FFIEC-MGMT` |

---

## §7 SPONSOR — Entra Agent ID Sponsor-Departure Cascade

### 7.1 Criterion mapping

Supporting evidence for VC-1 (Detection Signal Source #2) and VC-3 (real-time / 24h Z3 SLA): when a registered sponsor departs, **every** Entra Agent ID for which they were named sponsor must be (a) detected within 24h on Z3, (b) routed to a sponsor-task in the Entra Agent ID surface for re-sponsorship or terminal action, and (c) reflected in the orphan register as category-2.

### 7.2 Pre-conditions

- HR namespace PASS (else cascade evidence is unreliable).
- Entra Agent ID Admin can read `/identityGovernance/agentSponsorships` and `/identityGovernance/agentSponsorTasks`.
- Sponsor-task workflow has SLA timer configured per zone.

### 7.3 Pester suite

```powershell
Describe "AGT36-SPONSOR" -Tag 'Control3.6','Supporting','VC-1','VC-3' {

    BeforeAll {
        $script:Departed = Get-Agt36DepartedSponsor -LookbackDays 30
    }

    Context "Cascade completeness" {
        It "every agent with a departed sponsor surfaces as a category-2 orphan within 24h (Z3)" {
            foreach ($s in $script:Departed) {
                foreach ($agent in $s.SponsoredAgents | Where-Object Zone -eq 3) {
                    $reg = Get-Agt36OrphanRegisterEntry -AgentId $agent.AgentId
                    $reg.Category | Should -Be 2
                    ($reg.FirstDetectedAt - $s.LeaveDateTime).TotalHours | Should -BeLessOrEqual 24
                }
            }
        }

        It "every cascade-detected agent has an Entra Agent ID sponsor-task created" {
            foreach ($s in $script:Departed) {
                foreach ($agent in $s.SponsoredAgents) {
                    $task = Get-Agt36SponsorTask -AgentId $agent.AgentId
                    $task | Should -Not -BeNullOrEmpty
                    $task.State | Should -BeIn @('open','assigned','resolved','escalated')
                }
            }
        }
    }

    Context "Multi-agent cascade integrity" {
        It "no Z3 sponsor-departure leaves a sponsored agent undetected after 24h" {
            $stragglers = Get-Agt36SponsorCascadeStraggler -Zone 3 -OlderThanHours 24
            $stragglers | Should -BeNullOrEmpty
        }
    }
}
```

### 7.4 Sample PASS / FAIL evidence

```json
{
  "control_id":"3.6","namespace":"SPONSOR","criterion":"VC-1+VC-3","zone":"3",
  "subject_id":"sponsor-departure-jdoe","subject_type":"sponsor_task",
  "status":"PASS",
  "assertion":"Sponsor jdoe@contoso.com left 2026-04-09T17:02Z; all 7 Z3-sponsored agents detected and sponsor-tasked within 24h.",
  "observed_value":{"sponsored_agent_count":7,"detected_within_24h":7,"max_detection_lag_hours":3.4},
  "evidence_artifacts":["sponsor-departure-jdoe.json"],
  "regulator_mappings":["FINRA-3110","FINRA-4511","FINRA-25-07","SEC-17a-4","SOX-404","NYDFS-500"]
}
```

```json
{
  "control_id":"3.6","namespace":"SPONSOR","criterion":"VC-1+VC-3","zone":"3",
  "subject_id":"sponsor-departure-msmith","subject_type":"sponsor_task",
  "status":"FAIL",
  "assertion":"3 of 5 Z3-sponsored agents not detected after 26h; cascade integrity broken.",
  "observed_value":{"sponsored_agent_count":5,"detected_within_24h":2,"undetected_after_24h":3},
  "remediation_ref":"TRG-SPONSOR-01",
  "regulator_mappings":["FINRA-3110","SOX-404","NYDFS-500"]
}
```

### 7.5 Thresholds & regulators

Z3: 100% cascade within 24h. Z2: ≥95% within 10 business days. Z1: ≥90% within 10 business days. Regulators: `FINRA-3110` (supports), `FINRA-4511`, `FINRA-25-07`, `SEC-17a-4`, `SOX-302`, `SOX-404`, `NYDFS-500`.

---

## §8 BULK — Bulk-Reassign Safety Gates

### 8.1 Criterion mapping

Supporting — protects the integrity of REASSIGN (§5) when remediations are batched. A poorly-gated bulk reassignment can silently transfer custody of dozens of agents to a single principal who lacks proper licensing, can over-apply to false positives (DL-owned agents that are not in fact orphans), and can race the SLA window.

### 8.2 Pre-conditions

- Bulk-reassign tooling runs in dry-run by default; `-Commit` requires explicit AI Governance Lead approval ticket.
- Exclusion list maintained for non-orphan ownership patterns: distribution-list-owned agents, role-assignable security-group-owned agents, managed-identity-owned agents.

### 8.3 Pester suite

```powershell
Describe "AGT36-BULK" -Tag 'Control3.6','Supporting' {

    BeforeAll {
        $script:Runs = Get-Agt36BulkReassignRun -LookbackDays 90
    }

    Context "Safety gates on every commit" {
        It "every -Commit run has a paired -DryRun within the prior 24h with identical scope hash" {
            foreach ($r in $script:Runs | Where-Object Mode -eq 'Commit') {
                $r.PairedDryRunId            | Should -Not -BeNullOrEmpty
                $r.PairedDryRunScopeSha256   | Should -Be $r.ScopeSha256
                ($r.StartedAt - $r.PairedDryRunStartedAt).TotalHours | Should -BeLessOrEqual 24
            }
        }
        It "every -Commit run cites a closed AI-Governance approval ticket" {
            foreach ($r in $script:Runs | Where-Object Mode -eq 'Commit') {
                $r.ApprovalTicket            | Should -Match '^(SNOW|JIRA|AGV)-\d+$'
                $r.ApprovalTicketState       | Should -BeIn @('Closed','Resolved','Implemented')
            }
        }
        It "exclusion list is applied; no DL-owned, MI-owned, or role-assignable group-owned agent is in the commit scope" {
            foreach ($r in $script:Runs | Where-Object Mode -eq 'Commit') {
                $excluded = $r.ExpandedScope | Where-Object {
                    $_.Owner.PrincipalType -eq 'Group:Distribution' -or
                    $_.Owner.PrincipalType -eq 'ServicePrincipal:ManagedIdentity' -or
                    ($_.Owner.PrincipalType -eq 'Group:Security' -and $_.Owner.IsAssignableToRole)
                }
                $excluded | Should -BeNullOrEmpty
            }
        }
        It "post-run false-positive rate is ≤1%" {
            foreach ($r in $script:Runs | Where-Object Mode -eq 'Commit') {
                ($r.FalsePositives.Count / [math]::Max(1,$r.CommittedCount)) | Should -BeLessOrEqual 0.01
            }
        }
    }
}
```

### 8.4 Sample evidence

```json
{
  "control_id":"3.6","namespace":"BULK","criterion":"supporting","zone":"all",
  "subject_id":"bulk-run-2026Q1-04","subject_type":"reassignment",
  "status":"PASS",
  "assertion":"Bulk reassign 47 agents committed under AGV-1244; dry-run paired; exclusions applied; 0 false positives.",
  "observed_value":{"committed":47,"false_positives":0,"approval_ticket":"AGV-1244","dry_run_id":"bulk-run-2026Q1-04-dry"},
  "evidence_artifacts":["bulk-run-2026Q1-04.json","bulk-run-2026Q1-04-dry.json","approval-AGV-1244.pdf"],
  "regulator_mappings":["FINRA-4511","SEC-17a-4","SOX-404","NYDFS-500","OCC-2011-12"]
}
```

### 8.5 Thresholds & regulators

Z3: false-positive rate ≤1%, dual-control on every commit, dry-run pairing. Z2: ≤2%. Z1: ≤5%. Regulators: `FINRA-4511`, `SEC-17a-4`, `SOX-404`, `OCC-2011-12`, `NYDFS-500`.

---

## §9 SIEM — Detection/Remediation Event Forwarding

### 9.1 Criterion mapping

Supporting — the orphan register and the detection / remediation event streams must forward to the enterprise SIEM with 6-year retention so that examiners can reconstruct any cycle, sponsor departure, or delete decision independently of the Microsoft tenant.

### 9.2 Pester suite

```powershell
Describe "AGT36-SIEM" -Tag 'Control3.6','Supporting' {

    BeforeAll {
        $script:Streams = Get-Agt36SiemStream
    }

    Context "Stream registration and health" {
        It "detection-run and remediation-ticket streams are registered and active" {
            $script:Streams.Name | Should -Contain 'agt36-detection-run'
            $script:Streams.Name | Should -Contain 'agt36-remediation-ticket'
            $script:Streams.Name | Should -Contain 'agt36-approval-artifact'
            foreach ($s in $script:Streams) { $s.State | Should -Be 'Active' }
        }
        It "each stream declares ≥6-year retention" {
            foreach ($s in $script:Streams) { $s.RetentionDays | Should -BeGreaterOrEqual 2190 }
        }
        It "each stream has produced events in the last 7 days" {
            foreach ($s in $script:Streams) { $s.LastEventAgeHours | Should -BeLessOrEqual 168 }
        }
    }

    Context "End-to-end trace" {
        It "a sample detection cycle from the last 30 days is present in SIEM with matching run-bundle hash" {
            $sample = Get-Agt36DetectionCycle -LookbackDays 30 | Get-Random -Count 1
            $siem   = Get-Agt36SiemEvent -Stream 'agt36-detection-run' -CorrelationId $sample.CycleId
            $siem.RunBundleSha256 | Should -Be $sample.RunLogBundleSha256
        }
    }
}
```

### 9.3 Sample evidence

```json
{
  "control_id":"3.6","namespace":"SIEM","criterion":"supporting","zone":"all",
  "subject_id":"siem-streams","subject_type":"detection_run",
  "status":"PASS",
  "assertion":"All three required streams Active, ≥6Y retention, sample cycle hash matches end-to-end.",
  "observed_value":{"streams":["agt36-detection-run","agt36-remediation-ticket","agt36-approval-artifact"],"retention_days":2555,"sample_corr_match":true},
  "regulator_mappings":["FINRA-4511","SEC-17a-4","SOX-404","NYDFS-500"]
}
```

### 9.4 Thresholds & regulators

Z3/Z2/Z1 share the same PASS: all three streams Active, ≥6Y retention, last-event age ≤168h, sample-cycle hash match. Regulators: `FINRA-4511`, `SEC-17a-3`, `SEC-17a-4`, `SOX-404`, `NYDFS-500`, `OCC-2011-12`, `FFIEC-MGMT`.

---

## §10 RETAIN — Purview Retention Enforcement (VC-7)

### 10.1 Criterion mapping

VC-7: "The orphan register, all weekly card snapshots, detection-run bundles, remediation tickets, approval artifacts, quarterly attestation PDFs are bound to a Purview retention label with retention ≥6 years, deletion-locked, and verified each month."

### 10.2 Pester suite

```powershell
Describe "AGT36-RETAIN" -Tag 'Control3.6','VC-7' {

    BeforeAll {
        $script:Labels   = Get-Agt36RetentionLabelBinding
        $script:Artifacts = @(
            'orphan-register','ownerless-card-snapshot','detection-run-log',
            'remediation-ticket','approval-artifact','quarterly-attestation'
        )
    }

    Context "Per-artifact retention binding" {
        foreach ($a in $script:Artifacts) {
            It "$a is bound to a ≥6Y deletion-locked retention label" {
                $b = $script:Labels | Where-Object ArtifactClass -eq $a
                $b | Should -Not -BeNullOrEmpty
                $b.RetentionDays       | Should -BeGreaterOrEqual 2190
                $b.IsDeletionLocked    | Should -BeTrue
                $b.Behavior            | Should -BeIn @('retainAsRecord','retainAsRegulatoryRecord')
            }
        }
    }
}
```

### 10.3 Sample evidence

```json
{
  "control_id":"3.6","namespace":"RETAIN","criterion":"VC-7","zone":"all",
  "subject_id":"purview-binding-2026-04","subject_type":"retention_label",
  "status":"PASS",
  "assertion":"All 7 artifact classes bound to FSI-Records-6Y-WORM; deletion-locked; retainAsRegulatoryRecord.",
  "observed_value":{"artifact_count":7,"retention_days_min":2190,"all_deletion_locked":true},
  "regulator_mappings":["FINRA-4511","SEC-17a-4","SOX-302","SOX-404","CFTC-1.31","NYDFS-500"]
}
```

### 10.4 Thresholds & regulators

Z3/Z2/Z1: all 7 artifact classes bound, ≥6Y, deletion-locked, behaviour `retainAsRecord` or `retainAsRegulatoryRecord`. Any unbound artifact class is a FAIL at any zone. Regulators: `FINRA-4511`, `SEC-17a-3`, `SEC-17a-4`, `SOX-302`, `SOX-404`, `CFTC-1.31`, `NYDFS-500`, `OCC-2011-12`.

---

## §11 PREVENT — Pre-Orphan Prevention Rate (VC-8)

### 11.1 Criterion mapping

VC-8: "Each quarter, measure the *pre-orphan prevention rate* — the proportion of agents created in the quarter whose ownership / sponsorship was kept current (no orphan event in the quarter of creation plus one) — and track year-over-year trend."

### 11.2 Formula

```
pre_orphan_prevention_rate(Q) =
    1 - ( orphan_events_in(Q, Q+1) for agents created in Q
          ÷ agents_created_in(Q) )
```

Computed per zone, reported at quarterly governance review.

### 11.3 Pester suite

```powershell
Describe "AGT36-PREVENT" -Tag 'Control3.6','VC-8' {

    BeforeAll {
        $script:Metrics = Get-Agt36PreventionMetric -QuarterId (Get-Agt36Quarter) -IncludeYoY
    }

    Context "Zone 3 target" {
        It "Z3 pre-orphan prevention rate ≥ 0.95" {
            ($script:Metrics | Where-Object Zone -eq 3).Rate | Should -BeGreaterOrEqual 0.95
        }
        It "Z3 YoY trend is non-regressive (≥ prior year quarter - 0.02)" {
            $m = $script:Metrics | Where-Object Zone -eq 3
            $m.Rate | Should -BeGreaterOrEqual ($m.PriorYearRate - 0.02)
        }
    }
    Context "Zone 2 target" {
        It "Z2 pre-orphan prevention rate ≥ 0.90" {
            ($script:Metrics | Where-Object Zone -eq 2).Rate | Should -BeGreaterOrEqual 0.90
        }
    }
    Context "Zone 1 target" {
        It "Z1 pre-orphan prevention rate ≥ 0.80" {
            ($script:Metrics | Where-Object Zone -eq 1).Rate | Should -BeGreaterOrEqual 0.80
        }
    }
}
```

### 11.4 Sample evidence

```json
{
  "control_id":"3.6","namespace":"PREVENT","criterion":"VC-8","zone":"3",
  "subject_id":"prevention-2026Q1","subject_type":"attestation",
  "status":"PASS",
  "assertion":"Z3 pre-orphan prevention rate 0.972 in 2026Q1 (prior year 0.963); trend non-regressive.",
  "observed_value":{
    "agents_created":358,"orphan_events_same_or_next_quarter":10,"rate":0.972,
    "prior_year_rate":0.963,"yoy_delta":0.009,
    "z2_rate":0.921,"z1_rate":0.831
  },
  "regulator_mappings":["FINRA-25-07","SOX-404","FED-SR-11-7","NYDFS-500","OCC-2011-12"]
}
```

### 11.5 Thresholds & regulators

| Zone | PASS | WARN | FAIL |
|---|---|---|---|
| 3 | ≥0.95 and non-regressive YoY | 0.90–0.95 | <0.90 or regression >0.02 |
| 2 | ≥0.90 | 0.85–0.90 | <0.85 |
| 1 | ≥0.80 | 0.75–0.80 | <0.75 |

Regulators: `FINRA-25-07` (periodic monitoring of generative-AI supervisory program effectiveness), `SOX-404`, `FED-SR-11-7`, `NYDFS-500`, `OCC-2011-12`, `FFIEC-MGMT`.

---

## §12 Manual Verification Procedures

Automation cannot cover every assertion. The following are performed manually each quarter and captured as PDF manual-attestation evidence records.

### 12.1 Supervisory review walkthrough (FINRA 3110)

**Performer:** AI Governance Lead in the presence of a registered principal (for firms to which FINRA 3110 applies).
**Procedure:**

1. Pick three Z3 orphan events closed in the quarter — one category-1, one category-2, one category-7.
2. For each, walk the registered principal through: detection date, cascade path (if any), approvals, reassignment or terminal, retention binding, SIEM trace.
3. Record principal's signed acknowledgement that the evidence supports supervisory review per the firm's written supervisory procedures.
4. This walkthrough **supports — does not replace** the registered-principal supervisory review under FINRA Rule 3110; the firm's WSPs remain authoritative.

### 12.2 Shadow-agent sweep review (category 10)

Shadow-agent detection (Detection Signal Source #10) is the most error-prone source because it relies on pattern-matching naming conventions, connector usage, and Dataverse table heuristics. Each quarter, the AI Governance Lead reviews a 5-agent sample of category-10 detections with the Power Platform Admin to confirm true positives and to capture learnings into detector rules.

### 12.3 Litigation-hold interaction check

Every quarter, confirm with the Purview Compliance Admin that **no** orphan register entry or related record has been moved to a terminal-delete state while under a legal or litigation hold. Any conflict is a cycle-stopping FAIL and routes to legal.

### 12.4 Microsoft Learn parity re-verification

Re-read the current Microsoft Learn documentation for the Agent 365 Ownerless Agents card, Entra Agent ID lifecycle workflows, and Power Platform maker-departure telemetry. Note any new zone availability. Any material change triggers an update to this playbook and to [Control 3.6](../../../controls/pillar-3-reporting/3.6-orphaned-agent-detection-and-remediation.md).

---

## §13 Examiner-Facing Test Scenarios

Each scenario is an end-to-end narrative with expected evidence. Examiners frequently ask for these during SOX walkthroughs, FINRA sweeps, NYDFS audits, and Fed SR 26-2 (formerly SR 11-7) reviews.

### Scenario A — M&A divestiture / mass-RIF orphan wave

**Trigger:** 340 leavers in a single day from a divested business unit.
**Expected evidence:**

1. **HR namespace** shows the leaver batch ingested within 24h with `employeeLeaveDateTime` populated (§6).
2. **SPONSOR namespace** shows cascade tasks generated for every sponsored agent (§7).
3. **DETECT namespace** shows category-2 spike in the weekly cycle (§2).
4. **RECONCILE namespace** shows card-vs-register parity maintained or variance substantiated (§3).
5. **TERMINAL namespace** shows Z3 remediation within SLA for the category-2 wave (§4).
6. **BULK namespace** shows any bulk reassign passed all safety gates (§8).
7. **Quarterly attestation** (§18) includes a narrative note on the M&A event.

### Scenario B — Examiner pulls orphan register during a SIEM outage window

**Trigger:** Examiner asks for every orphan event for calendar week W when the SIEM forwarder had a 12-hour outage.
**Expected evidence:**

1. **Orphan register** itself (Dataverse / SharePoint) is primary source of truth and is WORM.
2. **Detection-run bundles** (§2) are persisted independently of SIEM.
3. **SIEM outage ticket** referenced with remediation — gap window is disclosed, not hidden.
4. **§18 attestation** lines up register events with detection-bundle hashes for the affected window.

### Scenario C — Sponsor-departure cascade (one sponsor, many agents)

**Trigger:** Registered sponsor for 12 Z3 agents departs on a Friday evening.
**Expected evidence:**

1. SPONSOR namespace produces 12 sponsor-tasks within 24h.
2. DETECT surfaces 12 category-2 entries in the next cycle.
3. REASSIGN namespace (sampled) shows new sponsors meet all prerequisites (§5).
4. TERMINAL SLA for category-2 (24h Z3) is attained or substantiated.
5. Registered-principal supervisory walkthrough under §13.1 is performed for at least one of the 12 agents.

### Scenario D — Bulk reassign over-applied to DL-owned false positives

**Trigger:** An over-inclusive bulk reassign attempts to transfer ownership from a distribution-list-owned Teams agent (which is not orphaned).
**Expected evidence:**

1. BULK namespace (§8) shows exclusion list caught the DL-owner; commit was blocked.
2. If any DL-owner slipped through, it is listed in FalsePositives and routed to §15 triage `TRG-BULK-02`.
3. AI Governance Lead approval ticket captures the corrective scope-reduction.

## §14 Failure Triage Matrix

Triage IDs referenced from FAIL evidence records via `remediation_ref`. Each entry includes likely root cause, first-responder role, first actions, and the sibling playbook to consult.

| ID | Namespace | Symptom | Likely cause | First responder | First actions | See |
|---|---|---|---|---|---|---|
| TRG-DETECT-01 | DETECT | Cycle did not run | Orchestrator disabled, expired service-principal credential | AI Administrator | Re-enable schedule, rotate SP credential, rerun cycle, document gap | [powershell-setup.md](./powershell-setup.md) |
| TRG-DETECT-02 | DETECT | Cycle ran but < 10 sources | Connector throttled, Graph 429, missing module | AI Administrator | Back-off+retry, pin module versions, rerun within 24h | [troubleshooting.md](./troubleshooting.md) |
| TRG-DETECT-03 | DETECT | Signature missing or invalid | Key vault access revoked, key rotated without pin update | AI Administrator | Restore access, update thumbprint pin in `Agt36Config.psd1`, re-sign | [powershell-setup.md](./powershell-setup.md) |
| TRG-RECONCILE-01 | RECONCILE | Card count ≠ register count | Category-1 write lag, filter bug, excluded tenant partition | AI Governance Lead | Capture substantiation memo, open corrective ticket, rerun reconcile | [portal-walkthrough.md](./portal-walkthrough.md) |
| TRG-TERMINAL-01 | TERMINAL | SLA attainment below Z3 95% | Approval backlog, stale queue, on-call gap | AI Governance Lead | Escalate backlog, add Compliance Officer approval slot, reassign remediator | [portal-walkthrough.md](./portal-walkthrough.md) |
| TRG-TERMINAL-02 | TERMINAL | Retention label missing on terminal | Label policy drifted, new workload unbound | Purview Compliance Admin | Re-apply label, confirm deletion lock, rerun RETAIN suite | [troubleshooting.md](./troubleshooting.md) |
| TRG-TERMINAL-03 | TERMINAL | Z3 delete with single approver | Dual-control bypassed, role spoof | Compliance Officer | Halt delete, investigate override, escalate per incident-response plan | [Control 2.8](../../../controls/pillar-2-management/2.8-access-control-and-segregation-of-duties.md) |
| TRG-REASSIGN-01 | REASSIGN | New owner lacks license / env role | Pre-check skipped, stale cache | Power Platform Admin | Revert reassign, provision license, rerun | [powershell-setup.md](./powershell-setup.md) |
| TRG-REASSIGN-02 | REASSIGN | Permission delta non-empty | Transfer tool bug, race | Power Platform Admin | Replay transfer from `before.json`, open vendor ticket | [troubleshooting.md](./troubleshooting.md) |
| TRG-HR-01 | HR | Connector stale > 24h | Cert expiry, source-system outage | Entra Identity Governance Admin | Rotate cert, engage HRIS vendor, rerun provisioning | [Control 3.5](../../../controls/pillar-2-management/2.26-entra-agent-id-identity-governance.md) |
| TRG-HR-02 | HR | `employeeLeaveDateTime` missing | Attribute mapping drift | Entra Identity Governance Admin | Fix mapping, backfill, re-run HR suite | [Control 3.5](../../../controls/pillar-2-management/2.26-entra-agent-id-identity-governance.md) |
| TRG-SPONSOR-01 | SPONSOR | Cascade incomplete after 24h Z3 | Workflow disabled, SLA timer drift | Entra Agent ID Admin | Re-enable workflow, recompute cascade, document gap | [powershell-setup.md](./powershell-setup.md) |
| TRG-BULK-01 | BULK | Commit without dry-run pairing | Operator bypass | AI Governance Lead | Halt bulk tooling, require approval ticket, add guardrail in CLI | [Control 2.8](../../../controls/pillar-2-management/2.8-access-control-and-segregation-of-duties.md) |
| TRG-BULK-02 | BULK | DL/MI/role-group owner in scope | Exclusion list drifted | Power Platform Admin | Restore exclusion list, remove false positives, replay | [troubleshooting.md](./troubleshooting.md) |
| TRG-SIEM-01 | SIEM | Stream inactive or retention < 6Y | Forwarder misconfig, policy drift | Purview Compliance Admin | Reconfigure forwarder, rebind retention, open gap ticket | [Control 3.2](../../../controls/pillar-3-reporting/3.9-microsoft-sentinel-integration.md) |
| TRG-RETAIN-01 | RETAIN | Artifact class unbound to label | New artifact class introduced without label | Purview Compliance Admin | Bind label, rerun RETAIN, backfill prior artifacts if possible | [Control 2.3](../../../controls/pillar-1-security/1.9-data-retention-and-deletion-policies.md) |
| TRG-PREVENT-01 | PREVENT | Rate below zone target | Detection/remediation drift causing repeat orphans | AI Governance Lead | Root-cause analysis, update governance playbook, report to steering | [Control 1.2](../../../controls/pillar-1-security/1.2-agent-registry-and-integrated-apps-management.md) |

---

## §15 Evidence Pack Assembly and Signing

### 16.1 Pack contents (mirrors [Control 3.6 §Evidence and Retention](../../../controls/pillar-3-reporting/3.6-orphaned-agent-detection-and-remediation.md#evidence-and-retention))

The quarterly evidence pack for Control 3.6 contains:

1. **Orphan register export** (CSV + PDF) — system of record, all open and closed events in the quarter.
2. **Weekly Ownerless Agents card snapshot** (PNG + CSV) — one per week.
3. **Detection-run bundles** (JSON + detached signatures) — one per cycle, one per zone.
4. **Remediation tickets** (PDF export from ITSM) — one per closed terminal.
5. **Sponsor / owner reassignment approval artifacts** (PDF) — sample-per-quarter, plus all Z3.
6. **Quarterly governance attestation PDF** (§19 template output, dual-signed).
8. **Pack manifest** (`manifest.json`) with SHA-256 for every artifact and a top-level manifest hash.
9. **Pack signature** (`manifest.sig`) — detached X.509 signature by AI Governance Lead; second detached signature by Compliance Officer.

All items carry the Purview retention label `FSI-Records-6Y-WORM` (or the firm's equivalent ≥6Y regulatory-record label), deletion-locked.

### 16.2 Pack assembly procedure

```powershell
function New-Agt36EvidencePack {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory)] [string] $QuarterId,    # e.g. 2026Q1
        [Parameter(Mandatory)] [string] $RunId,
        [Parameter(Mandatory)] [string] $DestinationRoot
    )

    $pack = Join-Path $DestinationRoot "AGT36-$QuarterId-$RunId"
    New-Item -Path $pack -ItemType Directory -Force | Out-Null

    # 1. Validate every evidence record against the canonical schema.
    Get-ChildItem $script:EvidenceRoot -Filter '*.json' | ForEach-Object {
        if (-not (Test-Agt36EvidenceSchema -Path $_.FullName)) {
            throw "Schema validation failed for $($_.Name); pack assembly aborted."
        }
    }

    # 2. Copy artifacts and compute SHA-256 for each.
    $manifest = @()
    foreach ($art in Get-Agt36PackArtifact -QuarterId $QuarterId) {
        Copy-Item $art.Path -Destination $pack
        $manifest += [pscustomobject]@{
            name          = Split-Path $art.Path -Leaf
            kind          = $art.Kind
            sha256        = (Get-FileHash $art.Path -Algorithm SHA256).Hash
            produced_at   = $art.ProducedAt
            namespace     = $art.Namespace
        }
    }

    # 3. Write manifest and compute top-level manifest hash.
    $manifest | ConvertTo-Json -Depth 6 | Set-Content (Join-Path $pack 'manifest.json') -Encoding UTF8
    $topHash = (Get-FileHash (Join-Path $pack 'manifest.json') -Algorithm SHA256).Hash
    Set-Content -Path (Join-Path $pack 'manifest.sha256') -Value $topHash -Encoding ASCII

    # 4. Sign — AI Governance Lead first, Compliance Officer second.
    Invoke-Agt36Sign -PackRoot $pack -Signer 'AI Governance Lead'
    Invoke-Agt36Sign -PackRoot $pack -Signer 'Compliance Officer'

    # 5. Bind retention label on the destination location.
    Set-Agt36PurviewLabel -Path $pack -LabelName 'FSI-Records-6Y-WORM' -DeletionLock

    return $pack
}
```

### 16.3 Schema validation helper

```powershell
function Test-Agt36EvidenceSchema {
    param([Parameter(Mandatory)][string]$Path)
    $r = Get-Content $Path -Raw | ConvertFrom-Json
    $required = 'control_id','run_id','namespace','criterion','zone','subject_id','subject_type','status','assertion','evidence_artifacts','regulator_mappings','schema_version'
    foreach ($k in $required) { if (-not $r.PSObject.Properties.Name.Contains($k)) { return $false } }
    if ($r.control_id -ne '3.6')        { return $false }
    if ($r.status -notin 'PASS','WARN','FAIL','SKIPPED','ERROR') { return $false }
    if ($r.status -ne 'PASS' -and -not $r.remediation_ref) { return $false }
    return $true
}
```

---

## §16 Sign-off Workflow

### 17.1 Three-signature chain

| Signatory | Role | Responsibility |
|---|---|---|
| **Preparer** | AI Administrator or Power Platform Admin (per namespace) | Runs the Pester suites, produces raw evidence records, runs `Test-Agt36EvidenceSchema` on every record. |
| **Validator** | Entra Global Reader (or a second, independent AI Administrator) | Independently re-runs a 10% sample of the suites and confirms evidence records match. Privileged-role separation required — must not share standing roles with Preparer. |
| **Compliance** | Compliance Officer + AI Governance Lead | Counter-sign pack manifest; confirm retention binding; confirm cross-control dependency status; confirm no litigation-hold conflicts. |

### 17.2 Separation of duties

- No single principal may hold Preparer and Validator on the same cycle.
- No single principal may hold Validator and Compliance on the same cycle.
- Standing privileged-role overlap between Preparer / Validator / Compliance is a cycle-stopping FAIL (see §15 → TRG-TERMINAL-03, TRG-BULK-01). Verify via [Control 2.8 Access Governance for Agent Admin Roles](../../../controls/pillar-2-management/2.8-access-control-and-segregation-of-duties.md).

### 17.3 Sign-off artifact

```
signoff-AGT36-<QuarterId>-<RunId>.json
{
  "pack_root": "AGT36-2026Q1-AGT36-20260415-093012-a1b2c3d4",
  "preparer":  { "upn":"ai.administrator@contoso.com", "signed_at":"2026-04-16T14:00:00Z", "sig_sha256":"…" },
  "validator": { "upn":"globalreader@contoso.com",      "signed_at":"2026-04-16T16:12:00Z", "sig_sha256":"…", "sample_pct":0.10, "reruns_passed":true },
  "compliance":[
    { "role":"AI Governance Lead", "upn":"jane.doe@contoso.com",  "signed_at":"2026-04-17T10:04:00Z", "sig_sha256":"…" },
    { "role":"Compliance Officer",  "upn":"carlos.k@contoso.com",  "signed_at":"2026-04-17T11:02:00Z", "sig_sha256":"…" }
  ],
  "regulator_mappings":["FINRA-3110","FINRA-4511","FINRA-25-07","SEC-17a-3","SEC-17a-4","SOX-302","SOX-404","GLBA-501b","OCC-2011-12","FED-SR-11-7","CFTC-1.31","NYDFS-500"]
}
```

---

## §17 Quarterly Attestation Template

The quarterly attestation is the pack's cover document. It restates the hedged language of §Document Conventions, summarises per-namespace status, restates per-zone threshold attainment, discloses every WARN / FAIL with its remediation pointer, and captures the dual signatures that bind the quarter.

```markdown
# Control 3.6 — Quarterly Governance Attestation — {Tenant} — {QuarterId}

**Framework version:** v1.4
**Control:** 3.6 Orphaned Agent Detection and Remediation
**Cloud:** Commercial
**Cycle dates:** {start} – {end}
**Pack root:** AGT36-{QuarterId}-{RunId}
**Pack manifest SHA-256:** {hash}

## Statement

This attestation supports compliance with FINRA 3110, 4511, and RN 24-09, SEC Rules 17a-3 / 17a-4, SOX 302 / 404, GLBA §501(b), OCC Bulletin 2026-13 (formerly OCC Bulletin 2011-12), Fed SR 26-2 (formerly SR 11-7), CFTC 1.31, and NYDFS Part 500. A clean attestation **does not guarantee** compliance, **does not replace** the firm's written supervisory procedures, and **supports — does not replace — registered-principal supervisory review under FINRA Rule 3110**.

## Namespace Summary

| § | Namespace | Criterion | Z3 | Z2 | Z1 | Status | WARN/FAIL refs |
|---|---|---|---|---|---|---|---|
| 2 | DETECT | VC-1 | ✓ | ✓ | ✓ | PASS | — |
| 3 | RECONCILE | VC-2 | ✓ | ✓ | ✓ | PASS | — |
| 4 | TERMINAL | VC-3, VC-5 | ✓ | ✓ | ✓ | PASS | — |
| 5 | REASSIGN | VC-4 | ✓ | ✓ | ✓ | PASS | — |
| 6 | HR | supporting | ✓ | ✓ | ✓ | PASS | — |
| 7 | SPONSOR | supporting | ✓ | ✓ | ✓ | PASS | — |
| 8 | BULK | supporting | ✓ | ✓ | ✓ | PASS | — |

| 10 | SIEM | supporting | ✓ | ✓ | ✓ | PASS | — |
| 11 | RETAIN | VC-7 | ✓ | ✓ | ✓ | PASS | — |
| 12 | PREVENT | VC-8 | ✓ | ✓ | ✓ | PASS | — |

## Metrics

- **Pre-orphan prevention rate** (VC-8): Z3 = 0.972 (YoY Δ +0.009), Z2 = 0.921, Z1 = 0.831.
- **SLA attainment** (VC-3, Z3, 90-day rolling): per-category range 96.8% – 100%.
- **Reconciliation variance** (VC-2): 0 unsubstantiated variances; 2 substantiated and remediated.

## Disclosures

{WARN or FAIL narratives with pointers to §15 triage}

## Cross-control status

- [Control 1.2](../../../controls/pillar-1-security/1.2-agent-registry-and-integrated-apps-management.md): current-cycle inventory attestation: {status}
- [Control 2.3](../../../controls/pillar-1-security/1.9-data-retention-and-deletion-policies.md): records retention alignment: {status}
- [Control 2.8](../../../controls/pillar-2-management/2.8-access-control-and-segregation-of-duties.md): admin-role access review: {status}
- [Control 2.25](../2.25/verification-testing.md) — agent identity lifecycle: {status}
- [Control 2.26](../2.26/verification-testing.md) — sponsor lifecycle: {status}
- [Control 3.1](../../../controls/pillar-3-reporting/3.1-agent-inventory-and-metadata-management.md) — inventory reporting: {status}
- [Control 3.2](../../../controls/pillar-3-reporting/3.9-microsoft-sentinel-integration.md) — SIEM integration: {status}
- [Control 3.5](../../../controls/pillar-2-management/2.26-entra-agent-id-identity-governance.md) — sponsor/maker lifecycle: {status}
- [Control 3.13](../../../controls/pillar-3-reporting/3.13-agent-365-admin-center-analytics.md) — Agent 365 analytics: {status}

## Signatures

| Role | Name | UPN | Signed (UTC) | Sig SHA-256 |
|---|---|---|---|---|
| Preparer (AI Administrator) | | | | |
| Validator (Entra Global Reader) | | | | |
| AI Governance Lead | | | | |
| Compliance Officer | | | | |
```

---

## §18 Continuous-Improvement Metrics

Beyond VC-8 (prevention rate), the program tracks:

| Metric | Formula | Target | Trend |
|---|---|---|---|
| Detection-run availability | successful cycles ÷ scheduled cycles (90d) | ≥99.5% Z3 | monthly |
| Mean time to detect (MTTD) | `firstDetectedAt - triggeringEventAt` median, per category | see Detection Signal Sources table | monthly |
| Mean time to remediate (MTTR) | `terminalAt - firstDetectedAt` median, per category+zone | ≤ SLA × 0.7 | monthly |
| Reassignment success-rate | REASSIGN PASS ÷ REASSIGN sample | ≥0.95 Z3 | quarterly |
| Variance substantiation time | hours from variance to signed memo | ≤24h Z3 | quarterly |
| Shadow-agent false-positive rate | category-10 FPs ÷ category-10 detections | ≤5% | quarterly |
| Pack assembly reproducibility | independent re-run produces identical manifest hash | 100% | per pack |

### 19.1 YoY trend table

| Quarter | Z3 Prevention rate | Z3 SLA attainment | Reconcile variance (uncompensated) | Notes |
|---|---|---|---|---|
| 2025Q1 | 0.954 | 94.1% | 1 | baseline |
| 2025Q2 | 0.961 | 95.3% | 0 | |
| 2025Q3 | 0.958 | 96.0% | 0 | |
| 2025Q4 | 0.963 | 96.4% | 0 | |
| 2026Q1 | 0.972 | 97.2% | 0 | |

---

## §19 Cross-Control Verification Dependencies

Control 3.6 does not stand alone. Evidence from the following controls must be in PASS state for the 3.6 attestation to be defensible:

| Dependency | Why it matters for 3.6 |
|---|---|
| [Control 1.2 Agent Inventory and Classification](../../../controls/pillar-1-security/1.2-agent-registry-and-integrated-apps-management.md) | Defines the universe against which orphans are computed; without 1.2 the denominator is unknown. |
| [Control 2.3 Records Retention and eDiscovery](../../../controls/pillar-1-security/1.9-data-retention-and-deletion-policies.md) | Provides the `FSI-Records-6Y-WORM` retention label used throughout §4, §11, §14. |
| [Control 2.8 Access Governance for Agent Admin Roles](../../../controls/pillar-2-management/2.8-access-control-and-segregation-of-duties.md) | Enforces PIM and dual-control used in §4 TERMINAL-DELETE, §8 BULK, §17 sign-off. |
| [Control 2.25 Agent Identity Lifecycle](../2.25/verification-testing.md) | Provides the identity-object lifecycle signals that feed DETECT sources 1, 3, 4, 8. |
| [Control 2.26 Sponsor Lifecycle](../2.26/verification-testing.md) | Provides sponsor-departure signal for DETECT source 2 and §7 SPONSOR. |
| [Control 3.1 Agent Inventory Reporting](../../../controls/pillar-3-reporting/3.1-agent-inventory-and-metadata-management.md) | Provides the reconciled inventory view used in §3 RECONCILE. |
| [Control 3.2 Audit Logging and SIEM Integration](../../../controls/pillar-3-reporting/3.9-microsoft-sentinel-integration.md) | Provides SIEM forwarding and retention verified in §10. |
| [Control 3.5 Identity Lifecycle for Agent Sponsors and Makers](../../../controls/pillar-2-management/2.26-entra-agent-id-identity-governance.md) | Provides HR connector and mover/leaver signal verified in §6 HR. |
| [Control 3.13 Agent 365 Admin Center Analytics](../../../controls/pillar-3-reporting/3.13-agent-365-admin-center-analytics.md) | Provides the Ownerless Agents card surface reconciled in §3. |

If any dependency is in WARN or FAIL for the quarter, the 3.6 attestation must disclose it on the §18 attestation under "Cross-control status" and reference the owning control's triage.

---

## §20 References

### 21.1 Source control document

- [Control 3.6 — Orphaned Agent Detection and Remediation](../../../controls/pillar-3-reporting/3.6-orphaned-agent-detection-and-remediation.md)
  - [Detection Signal Sources](../../../controls/pillar-3-reporting/3.6-orphaned-agent-detection-and-remediation.md#detection-signal-sources)
  - [Evidence and Retention](../../../controls/pillar-3-reporting/3.6-orphaned-agent-detection-and-remediation.md#evidence-and-retention)
  - [Verification Criteria](../../../controls/pillar-3-reporting/3.6-orphaned-agent-detection-and-remediation.md#verification-criteria)

### 21.2 Sibling playbooks

- [Portal walkthrough](./portal-walkthrough.md)
- [PowerShell setup](./powershell-setup.md)
- [Troubleshooting](./troubleshooting.md)

### 21.3 Peer verification playbooks

- [Control 1.2 verification-testing](../1.2/verification-testing.md)
- [Control 2.25 verification-testing](../2.25/verification-testing.md)
- [Control 2.26 verification-testing](../2.26/verification-testing.md)
- [Control 3.1 verification-testing](../3.1/verification-testing.md)

### 21.4 Regulatory sources

- FINRA Rule 3110 (Supervision) — fi(n)ra.org/rules/3110
- FINRA Rule 4511 (Books and Records) — finra.org/rules/4511
- FINRA RN 24-09 / Rule 3110 (Generative-AI Supervision)
- SEC Rule 17a-3 (Records to be Made)
- SEC Rule 17a-4 (Records Retention; WORM)
- Sarbanes-Oxley Act §302, §404
- Gramm-Leach-Bliley Act §501(b)
- OCC Bulletin 2026-13 (formerly OCC Bulletin 2011-12) (Third-Party / Technology Risk)
- Federal Reserve SR 26-2 (formerly SR 11-7) (Model Risk Management)
- CFTC Regulation 1.31 (Recordkeeping)
- NYDFS 23 NYCRR Part 500 (Cybersecurity)
- FFIEC IT Examination Handbook — Management booklet

### 21.5 Microsoft Learn (re-verify each cycle)

- Microsoft 365 Agent 365 admin center — Ownerless Agents card
- Microsoft Entra Agent ID — sponsor lifecycle workflows
- Microsoft Purview records management — retention labels and regulatory records
- Microsoft Power Platform — environment and maker ownership management
- Microsoft Graph `/beta/agentGovernance` namespace

---

*Updated: May 2026 | Version: v1.6.2 | UI Verification Status: Current*
