# Verification & Testing — Control 3.4: Incident Reporting and Root Cause Analysis

> **Examiner-defensible evidence package** for Control 3.4. This playbook produces, signs, and retains the artifacts required to demonstrate to FINRA, the SEC, NYDFS, the FFIEC member agencies (OCC, FDIC, Federal Reserve), the FTC, state attorneys general, and the firm's Audit Committee that AI-agent-related incidents are detected, classified, escalated, root-caused, and notified to every applicable regulator on every applicable clock — and that the resulting books-and-records survive examiner scrutiny under SEC Rules 17a-3 / 17a-4 and FINRA Rule 4511.
>
> **Scope:** Microsoft 365 Commercial tenants. Where Microsoft Sentinel, Microsoft Defender XDR, Microsoft Purview Insider Risk Management, Microsoft Purview eDiscovery (Premium), or Microsoft Agent 365 surfaces are in preview or not yet available, this playbook notes the limitation; see TC-19 for the annual SOX 404 self-assessment.
>
> **Companion controls:** This control sits at the centre of the firm's AI-agent incident response chain. Detection feeds come from [1.7 Comprehensive Audit Logging](../../../controls/pillar-1-security/1.7-comprehensive-audit-logging-and-compliance.md), [1.8 Runtime Protection](../../../controls/pillar-1-security/1.8-runtime-protection-and-external-threat-detection.md), [1.11 Conditional Access and Phishing-Resistant MFA](../../../controls/pillar-1-security/1.11-conditional-access-and-phishing-resistant-mfa.md), [1.12 Insider Risk Detection and Response](../../../controls/pillar-1-security/1.12-insider-risk-detection-and-response.md), and [3.9 Microsoft Sentinel Integration](../../../controls/pillar-3-reporting/3.9-microsoft-sentinel-integration.md). Books-and-records retention lands in [1.9 Data Retention and Deletion Policies](../../../controls/pillar-1-security/1.9-data-retention-and-deletion-policies.md). Material model-behavior incidents trigger MRM re-validation under [2.6 Model Risk Management](../../../controls/pillar-2-management/2.6-model-risk-management-sr-26-2.md). Supervisory-relevant incidents feed [2.12 Supervision and Oversight (FINRA Rule 3110)](../../../controls/pillar-2-management/2.12-supervision-and-oversight-finra-rule-3110.md). Inventory metadata for triage comes from [2.25 Agent 365 Admin Center Governance Console](../../../controls/pillar-2-management/2.25-agent-365-admin-center-governance-console.md). Identity-incident cascades feed [3.6 Orphaned Agent Detection and Remediation](../../../controls/pillar-3-reporting/3.6-orphaned-agent-detection-and-remediation.md).
>
> **Last UI verified:** April 2026 against Microsoft 365 admin center build 2026.04.x, Microsoft Defender portal (`security.microsoft.com`), Microsoft Sentinel (Azure portal), Microsoft Purview portal (`purview.microsoft.com`), and Microsoft Agent 365 Admin Center build 2026.04.x. Re-verify each cycle before relying on automated paths.

---

!!! warning "Non-Substitution — Tooling Supports, It Does Not Replace"
    The Microsoft Sentinel analytics rules, Microsoft Defender XDR incidents, Microsoft Purview Insider Risk Management cases, Microsoft Purview eDiscovery (Premium) holds, SharePoint case-management lists, Power Automate notification flows, and Microsoft Agent 365 Admin Center inventory queries referenced in this playbook are **detection, triage, and evidence-collection surfaces**. They **do not** replace, and must not be presented to an examiner as a substitute for:

    - The firm's **written Incident Response Program** required by SEC Regulation S-P 17 CFR 248.30(a)(3), the FFIEC IT Examination Handbook (Information Security booklet), and (for NYDFS covered entities) 23 NYCRR 500.16.
    - **Registered-principal supervisory review** under FINRA Rule 3110 of the underlying business activity (see Control 2.12). A clean run of this playbook helps meet — does not replace — the registered-principal designation, the written supervisory procedures (WSPs), or the principal's contemporaneous review evidence.
    - **Legal hold and litigation-readiness** processes invoked when an incident becomes reasonably anticipated litigation. Legal hold is a Purview eDiscovery (Premium) plus outside-counsel workflow, not a SOC workflow.
    - **Regulator notification itself.** Notifications to NYDFS, the SEC (EDGAR / 8-K Item 1.05), FINRA (Firm Gateway 4530), the firm's primary federal banking regulator, the FTC, state attorneys general, NCUA, CISA (when CIRCIA is effective), and affected customers are filings made by the firm's Compliance and Legal functions on the firm's letterhead. The IR tooling produces the evidence that supports those filings; it does not file them.
    - **Books-and-records retention** under SEC Rule 17a-4 / FINRA Rule 4511. Microsoft Sentinel and Microsoft Defender operational retention windows are **not** WORM-compliant for 17a-4(f) purposes; long-term incident records must land in Microsoft Purview retention or an approved 17a-4(f) vendor (see Controls 1.7 and 1.9, and TC-17 and TC-21 in this playbook).

    A clean PASS across TC-1 through TC-21 produces an examiner-defensible evidence package. It does not by itself ensure compliance with any single regulation. Implementation requires organization-specific risk assessment, legal review, and ongoing recalibration as Microsoft surfaces, and the regulatory landscape change.


---

## Document Conventions

| Convention | Value |
|---|---|
| PowerShell baseline | PowerShell 7.4+ Core; `#Requires -Version 7.4` at the top of every executable script. See [`../../_shared/powershell-baseline.md`](../../_shared/powershell-baseline.md). |
| Test framework | Pester 5.5+. All assertions use `Should` with `-Because` clauses to make examiner traceability explicit. |
| Output discipline | No `Write-Host` in evidence-emitting scripts. All evidence written as structured `[pscustomobject]` instances via `Write-Output`, then serialized with `ConvertTo-Json -Depth 10` to evidence files. |
| Hedged regulatory language | This playbook **supports compliance with** and **helps meet** the cited regulations. It does not "ensure," "guarantee," or "prevent." |
| KQL query hashes | Every KQL snippet that produces an evidence record is fingerprinted with `Get-FileHash -Algorithm SHA256` over the canonical query text, and the hash is captured in the evidence record (`query_sha256`) so that a regulator can reproduce the query verbatim three years later. |
| Evidence retention | Six (6) years on WORM-equivalent storage for the full signed evidence pack — aligning to FINRA Rule 4511 / SEC Rule 17a-4(f). State breach-notification statutes and litigation holds may extend this. |
| Run identifier | Every test run is tagged `AGT34-yyyyMMdd-HHmmss-<8charGuid>` and embedded in every evidence record and artifact filename. |
| Canonical role names | Per [`docs/reference/role-catalog.md`](../../../reference/role-catalog.md). Use `Entra Global Admin`, `Purview Compliance Admin`, `Power Platform Admin`, `Exchange Online Admin`, `AI Administrator`, `AI Governance Lead`, `Compliance Officer`, `Privacy Officer`, `Chief Compliance Officer (CCO)`, `Chief Information Security Officer (CISO)`, `General Counsel (GC)`, `Internal Audit`. No title substitution. |
| Cadence | TC-1, TC-2, TC-9, TC-12, TC-19, TC-19 are scheduled; TC-3 through TC-18 are exercised at least annually as table-tops, and again per actual incident. TC-20 is exercised quarterly. TC-21 is exercised annually as part of the books-and-records sample audit. |
| Audience | Chief Information Security Officer (CISO), Chief Compliance Officer (CCO), General Counsel (GC), AI Governance Lead, Internal Audit, examiner-facing Compliance Officer producing annual + per-incident evidence packages. |

---

## §0 Pre-Test Prerequisites

### 0.1 Operator role prerequisites

Incident-response verification reads from identity, directory, Sentinel workspace, Defender XDR, Purview Audit (Premium), Purview IRM, Purview eDiscovery (Premium), Power Platform admin, SharePoint, and the Microsoft Agent 365 Admin Center, and writes to the firm's incident register, evidence archive, and (in tabletop mode) to the regulator-notification template store. Read/write separation is enforced: every Pester suite below is **read-only with respect to production data**; tabletop synthetic incidents are tagged `synthetic=true` and written to the dedicated tabletop site collection so they cannot pollute live regulator-clock counters.

| Role (canonical) | Required for | PIM activation window |
|---|---|---|
| AI Governance Lead | Owns the incident program; counter-signs every TC evidence record; chairs the quarterly tabletop battery (TC-20) and the annual SOX 404 self-assessment (TC-19). | Standing with quarterly recertification per Control 2.8 |
| Chief Information Security Officer (CISO) | Incident commander; co-signs critical-severity evidence in TC-14; signs the annual Rule 3120-style SLA-test evidence in TC-1. | Standing |
| Chief Compliance Officer (CCO) | Owns FINRA Rule 4530(a) / 4530(d) filings (TC-8, TC-9); co-signs every regulator-clock tabletop. | Standing |
| General Counsel (GC) / Outside Counsel liaison | Owns legal hold (TC-16); owns SEC 8-K Item 1.05 materiality determinations (TC-5); reviews every customer-notice template (TC-7, TC-10, TC-11). | Standing |
| Privacy Officer | Owns Reg S-P customer notice (TC-7); GLBA / FTC Safeguards Rule 30-day notice (TC-10); state-residency map and per-state templates (TC-11). | Standing |
| Disclosure Committee Secretary | Convenes the Disclosure Committee on materiality determinations under SEC 8-K Item 1.05 (TC-5); preserves Disclosure Committee minutes. | Standing |
| Designated Series 24 / Series 66 Principal | Documents supervisory-system implications under FINRA Rule 3110 for incidents that touch supervised activity (cross-reference TC-15 and Control 2.12). | Standing |
| Entra Global Reader | Read-only Entra and service-principal evidence reads; witness role for dual-control attestation in §0.6. | 4 hours, standing permissible |
| Sentinel Reader | Read-only Sentinel workspace queries and incident enumeration. | 4 hours, just-in-time |
| Microsoft Sentinel Responder | Read of Sentinel incidents, automation rules, playbook run history. Writes only to tabletop synthetic incidents. | 4 hours, just-in-time |
| Security Reader (Defender XDR) | Read-only Defender XDR incidents, advanced hunting, AIR run history. | 4 hours |
| Purview Compliance Admin | Reads Purview Audit (Premium), retention-label configuration, IRM cases (subject to RBAC), eDiscovery (Premium) cases and holds. | 4 hours |
| Insider Risk Management Investigator | Read-only IRM case content (pseudonymized) for evidence in TC-15. | 4 hours, just-in-time |
| eDiscovery Manager | Reads eDiscovery (Premium) holds and custodian acknowledgements for TC-16. | 4 hours, just-in-time |
| Power Platform Admin | Reads Power Platform admin activity events for AI-agent telemetry that backs RCAs (TC-15) and the runaway-agent and orphaned-agent scenarios (TC-20). | 4 hours |
| AI Administrator | Reads Microsoft Agent 365 Admin Center inventory for incident triage enrichment in TC-14, TC-15, and TC-20. | 4 hours |
| M365 Service Health Reader | Reads Microsoft 365 Service Health (Microsoft-side correlation) for TC-18. | Standing, read-only |
| Internal Audit | Independent reviewer; signs the §14 evidence pack and the TC-19 SOX 404 self-assessment. Does not co-sign as a producer. | Standing, read-only |
| Compliance Officer (examiner-facing) | Assembles the per-examination evidence package; signs the TC-21 retention sample audit. | Standing |

> **Least privilege.** No operator should hold **Entra Global Admin** persistently for incident-response purposes. The cycle-stopping FAIL is: any operator who is both **Preparer** and **Validator** on the same evidence record (see §0.6 dual-control rule). Standing privileged-role overlap between Preparer / Validator / Compliance signatories voids the run.

### 0.2 Module baseline

Pin to specific module versions so evidence packs are reproducible across machines and across time. Re-validate against newer module versions before promoting them to the standing schedule.

```powershell
#Requires -Version 7.4
#Requires -Modules @{ ModuleName='Microsoft.Graph.Authentication';                ModuleVersion='2.25.0' }
#Requires -Modules @{ ModuleName='Microsoft.Graph.Users';                         ModuleVersion='2.25.0' }
#Requires -Modules @{ ModuleName='Microsoft.Graph.Identity.DirectoryManagement';  ModuleVersion='2.25.0' }
#Requires -Modules @{ ModuleName='Microsoft.Graph.Security';                      ModuleVersion='2.25.0' }
#Requires -Modules @{ ModuleName='Microsoft.Graph.Beta.Security';                 ModuleVersion='2.25.0' }
#Requires -Modules @{ ModuleName='Microsoft.Graph.Compliance';                    ModuleVersion='2.25.0' }
#Requires -Modules @{ ModuleName='Az.Accounts';                                   ModuleVersion='3.0.0'  }
#Requires -Modules @{ ModuleName='Az.SecurityInsights';                           ModuleVersion='4.5.0'  }
#Requires -Modules @{ ModuleName='Az.OperationalInsights';                        ModuleVersion='3.2.0'  }
#Requires -Modules @{ ModuleName='Az.Monitor';                                    ModuleVersion='5.2.0'  }
#Requires -Modules @{ ModuleName='ExchangeOnlineManagement';                      ModuleVersion='3.5.0'  }
#Requires -Modules @{ ModuleName='Microsoft.PowerApps.Administration.PowerShell'; ModuleVersion='2.0.200' }
#Requires -Modules @{ ModuleName='PnP.PowerShell';                                ModuleVersion='2.5.0'  }
#Requires -Modules @{ ModuleName='Pester';                                        ModuleVersion='5.5.0'  }

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'
$ProgressPreference    = 'SilentlyContinue'
```

### 0.3 PRE gates (must all pass before any TC executes)

`Invoke-Agt34PreFlight.ps1` runs ten pre-flight gates. Any `FAIL` halts the run and emits a single `preflight-FAILED-<runId>.json`. A `SKIPPED` on PRE-06, PRE-07, or PRE-08 routes the run to the SOV namespace (TC-19).

| Gate | ID | Purpose | Failure behavior |
|---|---|---|---|
| Module presence | PRE-01 | Confirms modules loaded at the pinned versions in §0.2 | HALT |
| Graph context | PRE-02 | Confirms `Connect-MgGraph` with read scopes `SecurityEvents.Read.All`, `SecurityIncident.Read.All`, `SecurityActions.Read.All`, `IdentityRiskEvent.Read.All`, `Directory.Read.All`, `User.Read.All`, `AuditLog.Read.All`, `eDiscovery.Read.All`, `InsiderRiskManagement.Read.All` | HALT |
| Tenant identification | PRE-03 | Captures `tenantId`, `displayName`, `verifiedDomains[0].name` for every evidence record | HALT |
| Cloud detection | PRE-04 | Reads `(Get-MgContext).Environment`; confirms `Global` (Commercial) | HALT |
| Sentinel workspace reachability | PRE-05 | Confirms the Sentinel workspace ID, region, and that an `AzSentinel` connection succeeds | HALT for IR-pillar tests |
| Defender XDR reachability | PRE-06 | Probes `/security/incidents?$top=1` on Graph Security | 4xx/5xx → HALT |
| Purview Audit (Premium) reachability | PRE-07 | Confirms a `Search-UnifiedAuditLog` returns within tenant SLA over a 1-hour window | HALT — without UAL, no books-and-records evidence chain |
| Purview eDiscovery (Premium) reachability | PRE-08 | Confirms an eDiscovery (Premium) case-list call succeeds | HALT — without eDiscovery, TC-16 cannot run |
| Clock skew gate | PRE-09 | Compares local UTC to Graph `Date` header; aborts on > 60s drift | HALT — skew invalidates timestamp evidence under FINRA 4511 / SEC 17a-4 |
| Evidence root writeable | PRE-10 | Confirms `$env:AGT34_EVIDENCE_ROOT` exists, is writeable, resolves to WORM-eligible storage with a verified retention label | HALT |


### 0.5 Run identifier and evidence root

```powershell
function New-Agt34RunId {
    $ts   = (Get-Date).ToUniversalTime().ToString('yyyyMMdd-HHmmss')
    $guid = ([guid]::NewGuid().ToString('N')).Substring(0,8)
    "AGT34-$ts-$guid"
}

$global:Agt34RunId = New-Agt34RunId
$global:Agt34Root  = Join-Path $env:AGT34_EVIDENCE_ROOT $global:Agt34RunId
New-Item -ItemType Directory -Path $global:Agt34Root -Force | Out-Null
```

### 0.6 Dual-control evidence rule

Every evidence record in this playbook carries three signature blocks: **Preparer** (the operator who ran the test), **Validator** (an independent operator with read-only privileges who replays the assertion), and **Compliance Signatory** (AI Governance Lead, CCO, or Internal Audit, depending on the TC). No two of these may be the same individual. The `Test-Agt34DualControl` helper enforces this at evidence-pack assembly time and refuses to seal a pack with a violation.

### 0.7 KQL query hash convention

```powershell
function Get-Agt34QueryHash {
    [CmdletBinding()]
    [OutputType([string])]
    param([Parameter(Mandatory)][string]$Query)

    # Normalise: strip carriage returns, trim trailing whitespace per line, collapse
    # multiple blank lines, lowercase nothing (KQL is case-sensitive). The normalisation
    # rule itself is part of the records-of-the-business and is documented here so a
    # regulator can reproduce the hash three years later.
    $lines = ($Query -split "`n") | ForEach-Object { $_.TrimEnd() }
    $norm  = ($lines -join "`n").TrimEnd() + "`n"
    $bytes = [System.Text.Encoding]::UTF8.GetBytes($norm)
    $sha   = [System.Security.Cryptography.SHA256]::Create()
    $hash  = $sha.ComputeHash($bytes)
    ($hash | ForEach-Object { $_.ToString('x2') }) -join ''
}
```

Every KQL snippet shown in TC-3 through TC-21 is followed by its `query_sha256`. The hash captured in evidence records is computed over the same canonicalised query text shown in the playbook so an examiner can verify reproducibility independently.

---

## §1 Evidence Schema and Mapping

### 1.1 Canonical evidence record

```jsonc
{
  "schema_version": "agt34.v1.4",
  "run_id": "AGT34-20260415-141523-3a9c1b08",
  "test_case": "TC-3",
  "test_case_title": "NYDFS 72-hour cybersecurity event tabletop",
  "tenant_id": "<guid>",
  "tenant_display_name": "<string>",
  "cloud": "Commercial",
  "executed_at_utc": "2026-04-15T14:15:23Z",
  "result": "PASS | FAIL | SKIPPED",
  "skipped_reason": "string|null",
  "compensating_ref": null,
  "regulator_clocks_exercised": ["NYDFS-72h", "NYDFS-24h-ransom", "..."],
  "artifacts": [
    { "name": "nydfs-portal-template.pdf", "sha256": "...", "size_bytes": 0,
      "retention_tier": "books-scope", "retention_years": 6 }
  ],
  "queries": [
    { "label": "ual-determination-event", "query_sha256": "...", "row_count": 0 }
  ],
  "signatures": {
    "preparer":   { "upn": "...", "role": "Sentinel Reader",     "signed_at_utc": "..." },
    "validator":  { "upn": "...", "role": "Entra Global Reader", "signed_at_utc": "..." },
    "compliance": { "upn": "...", "role": "AI Governance Lead",  "signed_at_utc": "..." }
  },
  "merkle_leaf_sha256": "..."
}
```

### 1.2 Canonical evidence-capture mapping

Every test case writes to one or more retention tiers. The tiers are not interchangeable. The mapping below is reproduced in each TC's "Evidence Capture" section and is the authoritative cross-reference for the per-examination evidence package.

| Tier | Storage | Retention | WORM? | Purpose |
|---|---|---|---|---|
| **Operational** | Microsoft Sentinel workspace, Microsoft Defender XDR incidents store, Microsoft Purview Audit (Premium) (default 1y, optional 10y add-on) | Per Microsoft default; not WORM-equivalent | No (Sentinel/Defender) / Limited (Purview Audit) | Live triage, hunting, pivot. Is **not** the books-and-records record. |
| **Archive** | SharePoint Online site backed by a Purview retention label with `deletionLocked=true`; Azure Storage with immutability policy | 6 years minimum, 10 years for Zone 3 | Yes (Purview retention with locked policy or Azure Storage time-based immutability) | Long-term incident records, RCA documents, tabletop output, materiality memos, customer-notice copies. |
| **Books-scope (17a-4(f))** | SharePoint with Purview retention label `deletionLocked=true`, **or** an SEC-non-objected 17a-4(f) third-party archive (vendor list per the firm's books-and-records program) | 6 years (FINRA 4511 / SEC 17a-4(b)(4)); first 2 years easily accessible | Yes — WORM-equivalent with audit trail | Regulator notification copies, regulator acknowledgments, customer-notice copies, RCA documents that touch supervised activity, FINRA 4530(a) / (d) filings, SEC 8-K materiality memos and EDGAR drafts. |
| **Corporate-records** | Corporate Secretary repository | Permanent | Yes | Disclosure Committee minutes, board materials, Audit Committee SOX 404 packages. |
| **Legal-hold** | Microsoft Purview eDiscovery (Premium) hold; outside counsel duplicate as required | Duration of matter + applicable retention | Yes (preservation hold) | Custodian preservation when an incident becomes reasonably anticipated litigation. |

### 1.3 TC → artifact → tier → regulation map

| TC | Primary artifact | Tier | Regulation tie |
|---|---|---|---|
| TC-1 | Internal SLA matrix v1.4 + annual test report | Archive + Books-scope | FINRA Rule 3120; FFIEC IT Handbook; SOX 404 |
| TC-2 | Regulator Notification Matrix v1.4 + quarterly review minutes | Archive | FINRA 3110; NYDFS 500.16; FFIEC IT Handbook |
| TC-3 | NYDFS portal submission template; clock-trace JSON; tabletop after-action | Books-scope + Archive | NYDFS 23 NYCRR 500.17(a) |
| TC-4 | NYDFS 24h ransom template; OFAC screening worksheet; CFO+GC sign-off; 30-day written explanation | Books-scope + Corporate-records | NYDFS 500.17(c); OFAC 31 CFR 501 / 596 |
| TC-5 | Disclosure Committee minute; materiality memo; outside-counsel sign-off; 8-K Item 1.05 EDGAR draft | Books-scope + Corporate-records | SEC Form 8-K Item 1.05; SEC 17a-4 |
| TC-6 | 36h determination worksheet; primary-federal-regulator submission template; bank-affiliate identification | Books-scope | 12 CFR 53 / 225 / 304 |
| TC-7 | Reg S-P customer-notice template; Privacy Officer + Outside Counsel sign-off; SP-contract clause sample | Books-scope + Archive | SEC Reg S-P 17 CFR 248.30 (2024 amendments) |
| TC-8 | FINRA 4530(a) Firm Gateway draft + AI-agent event mapping memo | Books-scope | FINRA Rule 4530(a) |
| TC-9 | FINRA 4530(d) quarterly statistical with AI-agent-channel rollup | Books-scope | FINRA Rule 4530(d); FINRA RN 24-09 / Rule 3110 |
| TC-10 | FTC Safeguards Rule 30-day notice template; ≥500-consumer trigger evidence | Books-scope | GLBA 501(b); FTC 16 CFR 314.4(j) |
| TC-11 | State-residency map; per-state notification templates; per-state clock-trace JSON | Books-scope + Archive | NY GBL 899-aa; CA CCPA/CPRA breach rules; MA 201 CMR 17; per-state |
| TC-12 | CISA CIRCIA quarterly horizon-check log; Federal Register monitoring evidence | Archive | CISA CIRCIA (rulemaking pending) |
| TC-13 | NCUA 72h applicability determination; verification or N/A justification | Archive or Books-scope | NCUA 12 CFR 748 |
| TC-14 | Critical-severity tabletop; CISO+CCO+GC notification delivery evidence within 1 hour | Books-scope + Archive | NYDFS 500.16; FFIEC; firm WSPs |
| TC-15 | Closed-incident sample (n≥30); 5-Whys + corrective actions + MRM feedback ticket sample | Books-scope | OCC Bulletin 2026-13 (formerly OCC 2011-12); Fed SR 26-2 (formerly SR 11-7); FINRA 3110 |
| TC-16 | Legal-hold notice; custodian acknowledgment sample; Purview eDiscovery (Premium) hold export | Legal-hold + Books-scope | FRCP 37(e); Zubulake-line case law; SEC 17a-4 |
| TC-17 | Sentinel/Defender/IRM extract written to 17a-4(f) storage; chain-of-custody log | Books-scope | SEC 17a-4(f); FINRA 4511 |
| TC-18 | Service Health correlation log per Sev-Critical/High; pre-RCA recorded check | Archive | FFIEC IT Handbook (correlation discipline) |
| TC-19 | Annual SOX 404 incident-program self-assessment; Audit Committee minute | Corporate-records + Books-scope | SOX §§ 302 / 404 |
| TC-20 | Quarterly AI tabletop battery; after-action reports per scenario | Archive + Books-scope | FINRA RN 24-09 + Rule 3110; Fed SR 26-2 (formerly SR 11-7); NYDFS 500.16 |
| TC-21 | Random sample (n≥25) of >6yr records per artifact category; retrievability log | Books-scope | SEC 17a-4(b)(4); FINRA 4511 |

---

## §2 Test Cases

The 21 test cases below verify Control 3.4 implementation across regulator-clock conformance, internal-SLA conformance, RCA gating, and evidence chain. Each case lists Setup / Steps / Expected / Evidence Capture / Remediation. Test cases are designed to be reproducible by an independent operator and auditable by an examiner.

> **Operator note.** Run each TC under the Run-ID generated in §0. Sign all evidence records using the Preparer / Validator / Compliance Signatory triple — no two roles may resolve to the same individual (dual-control rule, §0.6).

---

### TC-1 — Internal SLA matrix conformance

**Objective.** Confirm the internal incident-response SLA matrix (Critical / High / Medium / Low) is loaded into the SharePoint list "AI Agent Incidents" and into the Power Automate notification flow, and that triage decisions resolve to the matrix recommended in Control 3.4.

**Regulatory anchor.** FINRA Rule 3120 (annual supervisory-system test); Fed SR 26-2 (formerly SR 11-7) (model-risk operating discipline); NIST SP 800-61 r2 (incident-response lifecycle).

**Setup.**

- Roles: AI Governance Lead (preparer); Compliance Officer (validator); Chief Compliance Officer or delegate (signatory).
- Modules: PRE-01..PRE-10 must be GREEN (PRE-06 SKIPPED routes to TC-19).
- Inputs: current copy of `Get-IncidentSlaMatrix` output from `powershell-setup.md`; the parent-control SLA table (Critical 15min/1h/24h, High 1h/4h/72h, Medium 4h/24h/7d, Low 24h/7d/30d).

**Steps.**

1. Export the live SLA configuration: `Get-IncidentSlaMatrix -ListName 'AI Agent Incidents' | Export-Csv "$EvidenceRoot\TC-01\sla-live.csv" -NoTypeInformation`.
2. Compare to the canonical matrix in `..\..\..\controls\pillar-3-reporting\3.4-incident-reporting-and-root-cause-analysis.md` (lines 144-149). Any drift is a finding.
3. Trigger a synthetic incident at each severity using `New-AgentIncident -Severity Critical|High|Medium|Low -Synthetic -RunId $RunId`. Record the four resulting incident IDs.
4. For each, capture (a) the acknowledgement timestamp, (b) the containment timestamp, (c) the resolution timestamp, (d) the notification recipients list as written by the flow.
5. Compute observed-vs-target deltas for each clock; flag any negative margin.

**Expected.**

- Live SLA matrix matches canonical matrix exactly (no extra severities; no relaxed clocks).
- Synthetic Critical incident reaches CISO + CCO + GC notification list within 1 hour, observed.
- All four synthetic incidents close within their respective resolution windows or, if intentionally left open, are tagged `synthetic-do-not-close` and excluded from regulator-clock metrics.

**Evidence Capture.**

- `sla-live.csv`, `sla-canonical.csv`, `sla-diff.csv` (must be empty for PASS).
- `synthetic-incidents.json` (4 incident IDs + timestamps).
- Signed evidence record `agt34.v1.4` with `tc_id="TC-01"`.

**Remediation.**

- If drift detected: open a corrective-action ticket against the SharePoint list owner; do **not** silently update production. Drift indicates either out-of-band change or stale documentation; root-cause both before re-baselining.
- If notification recipients list is missing CCO or GC for a Critical incident: this supports a 2.6-class finding (notification taxonomy gap) and must be escalated to the AI Governance Lead within 1 business day.

---

### TC-2 — Regulator notification matrix quarterly review

**Objective.** Confirm that the regulator notification matrix (NYDFS, SEC, FRB/OCC/FDIC, FINRA, GLBA/FTC, state AGs, CISA, NCUA) reflected in the parent control is reviewed quarterly by the Disclosure Committee Secretary and signed by the General Counsel.

**Regulatory anchor.** Aggregate — supports compliance with NYDFS 23 NYCRR 500.17, SEC Reg S-K Item 1.05, 12 CFR 53/225/304, FINRA 4530, GLBA Safeguards Rule, state breach-notification statutes.

**Setup.**

- Roles: Disclosure Committee Secretary (preparer); General Counsel (validator); Chief Compliance Officer (signatory).
- Inputs: current quarter's Disclosure Committee minute set; live regulator matrix from parent control lines 89-108.

**Steps.**

1. Pull the most-recent quarterly Disclosure Committee minute referencing the AI-agent incident-reporting matrix; confirm date is ≤ 92 days prior to test date.
2. For each row in the matrix, confirm: (a) regulator citation, (b) trigger condition, (c) clock, (d) form/channel, (e) responsible role are unchanged or, if changed, there is a corresponding change-control record.
3. Confirm any pending rule changes (CISA CIRCIA final rule horizon, Reg S-P 2024 amendments compliance dates by tier) are tracked in a horizon log and not yet treated as in-force unless effective.
4. Capture General Counsel attestation in writing (email or signed PDF) referencing the run-id.

**Expected.**

- Most recent review ≤ 92 days old; matrix unchanged or all changes traceable; horizon log distinguishes in-force from pending.

**Evidence Capture.**

- `disclosure-committee-minute.pdf`, `regulator-matrix-q{n}.csv`, `gc-attestation.pdf`, `horizon-log.csv`.
- Signed evidence record `agt34.v1.4` with `tc_id="TC-02"`.

**Remediation.**

- If review is overdue: schedule the Disclosure Committee within 10 business days; do not advance any regulator-clock TC until the matrix is re-attested.
- If a new federal or state rule has crossed effective date without matrix update: this is a **High** internal severity and must trigger a same-day review by GC + CCO.

---

### TC-3 — NYDFS 23 NYCRR 500.17(a) 72-hour notification tabletop

**Objective.** Demonstrate that an AI-agent cybersecurity event meeting the NYDFS reportable-event definition can be characterized, escalated, and electronically filed via the DFS Cybersecurity Portal within 72 hours of determination.

**Regulatory anchor.** 23 NYCRR Part 500.17(a). The clock starts at *determination* of a reportable event, not at first detection — operators must record both timestamps and the reasoning bridging them.

**Setup.**

- Roles: Microsoft Sentinel Responder (preparer for detection-side artifacts); Chief Information Security Officer (validator); General Counsel (signatory for the regulator-facing filing).
- Scenario: a Microsoft 365 Copilot agent within scope of the firm's NYDFS covered-entity boundary exfiltrates customer NPI to an unauthorized SharePoint site, detected by Defender XDR alert `M365A_AI_Exfil_HighRisk`.

**Steps.**

1. Open the Sentinel incident derived from the Defender alert; confirm correlation to the AI-agent identity (service principal or user-context agent).
2. Run the determination KQL below. Capture the query text and its SHA-256 (`Get-KqlHash`) into the evidence record.

```kusto
// kql.id: agt34-tc03-determination
let lookback = 72h;
let agentScope = dynamic(["AIAgent","Copilot","DeclarativeAgent"]);
SecurityAlert
| where TimeGenerated > ago(lookback)
| where ProductName in~ ("Microsoft 365 Defender","Microsoft Sentinel")
| where Entities has_any (agentScope) or AlertName has "AI"
| extend determined = iff(Severity in ("High","Informational") and Status == "New", true, false)
| where determined == true
| project TimeGenerated, AlertName, Severity, SystemAlertId, Entities
```

3. Convene the Disclosure Committee in tabletop mode; record the *determination timestamp* (T0) when the committee concludes the event meets 500.17(a) criteria.
4. Generate the DFS notification draft using the firm's standard template; include event description, scope, indicators, and remediation status.
5. Stage the filing in the DFS Cybersecurity Portal staging environment (or, if no staging exists, walk through the production form to the final review screen and screenshot — do not submit).
6. Stop the clock at T1 (staged-ready timestamp). Confirm T1 − T0 ≤ 72 hours.

**Expected.**

- T1 − T0 ≤ 72h with at least 24h of operational margin (firm-internal target).
- KQL hash captured and reproducible.
- Disclosure Committee minute records both T0 reasoning and the determination vote.

**Evidence Capture.**

- `sentinel-incident-export.json`, `kql-determination.kql`, `kql-determination.sha256`, `disclosure-committee-tabletop-minute.pdf`, `dfs-portal-staged.png`, `dfs-notification-draft.pdf`.
- Signed evidence record `agt34.v1.4` with `tc_id="TC-03"`, fields `t0_determination`, `t1_staged`, `delta_hours`.

**Remediation.**

- If T1 − T0 > 60h (within window but tight): file an internal-process finding to compress the determination-to-staging path; common drivers are Disclosure Committee scheduling latency and unclear determination-authority delegation.
- If T1 − T0 > 72h: the tabletop has surfaced a **Critical** readiness gap; suspend new AI-agent deployments in the Zone-3 environment until the gap is closed and re-tested.

---
!!! danger "OFAC sanctions screening — required before any ransom payment consideration"
    Before the firm even deliberates a ransomware payment, the Chief Financial Officer and General Counsel must confirm screening of the threat actor, payment intermediary, and ultimate recipient against the OFAC Specially Designated Nationals (SDN) list and sectoral sanctions identifications under 31 CFR Parts 501 and 596. A payment to a sanctioned person can constitute a strict-liability OFAC violation independent of any cybersecurity reporting obligation. NYDFS 23 NYCRR 500.17(c) requires written explanation within 30 days of payment; OFAC and FinCEN advisories (most recently the September 2021 updated advisory) make clear that the *fact of payment*, not merely its disclosure, is the regulated act. **No ransom payment may be authorized without documented OFAC clearance and dual sign-off by CFO and General Counsel.** This admonition must be read aloud at the start of any TC-4 tabletop.

### TC-4 — NYDFS 500.17(c) 24-hour ransom-payment notification + 30-day written explanation

**Objective.** Demonstrate that, in the event of an extortion payment connected to an AI-agent-related cybersecurity event, the firm can (a) clear OFAC, (b) notify DFS within 24 hours of payment, and (c) submit the written explanation required under 23 NYCRR 500.17(c) within 30 days.

**Regulatory anchor.** 23 NYCRR 500.17(c). Related: 31 CFR 501/596 (OFAC), FinCEN 2021 advisory on ransomware payments, CISA / Treasury joint guidance.

**Setup.**

- Roles: Chief Information Security Officer (preparer); General Counsel (validator); Chief Compliance Officer + Chief Financial Officer (joint signatories — dual-control on payment authorization is non-negotiable).
- Scenario: a Zone-3 declarative agent's underlying SharePoint repository is encrypted by a ransomware actor that demands payment in cryptocurrency. The firm's Disclosure Committee is convened to consider payment. **No actual payment is made in this tabletop** — all financial steps are dry-run.

**Steps.**

1. Convene the Disclosure Committee + CFO + GC. Read the OFAC danger admonition above into the meeting record.
2. Run OFAC screening against (a) the threat-actor handle, (b) any cryptocurrency wallet address provided, (c) any payment intermediary (typically a digital-forensics-and-incident-response firm or specialized broker). Record the screening tool, version, and result. If any hit returns, **stop the test and escalate**; the playbook is not designed to walk past an OFAC hit.
3. Document the business-justification analysis: why payment is being considered, alternatives evaluated, expected operational impact of non-payment, FinCEN-advisory factors considered.
4. Mark T0 as the (simulated) payment-authorization timestamp.
5. Generate the DFS 24-hour notification draft via the firm's standard template; stage in the DFS Cybersecurity Portal (do not submit). Mark T1 as the staged-ready timestamp. Confirm T1 − T0 ≤ 24h.
6. Generate the 30-day written explanation draft addressing: reasons payment was necessary; alternatives considered; sanctions diligence; controls planned to prevent recurrence. Mark T2 as the draft-completion timestamp; confirm T2 − T0 ≤ 30 days (in tabletop mode, simulate the 30-day window using the run-id timestamp arithmetic).
7. Capture the joint CFO + GC dry-run authorization on a signed PDF that explicitly states "tabletop — no funds transferred."

**Expected.**

- OFAC screening completed and documented with no SDN hit (in the synthetic scenario).
- T1 − T0 ≤ 24h with operational margin.
- 30-day written explanation draft addresses all four FinCEN advisory factors.
- CFO + GC joint signature present on dry-run authorization.

**Evidence Capture.**

- `ofac-screening-result.pdf`, `business-justification-analysis.pdf`, `dfs-24h-notification-draft.pdf`, `dfs-portal-staged.png`, `30-day-written-explanation-draft.pdf`, `cfo-gc-dryrun-auth.pdf`, `disclosure-committee-minute.pdf`.
- Signed evidence record `agt34.v1.4` with `tc_id="TC-04"`, fields `ofac_clear=true`, `t0_payment_auth_simulated`, `t1_dfs_staged`, `t2_explanation_drafted`.

**Remediation.**

- If OFAC screening process is not documented or relies on a single individual: this is a **Critical** finding under both NYDFS 500.17(c) and 31 CFR 501. Suspend any incident-response runbook that contemplates payment until dual-control OFAC clearance is in place.
- If 24h DFS notification path requires more than 4 hours of preparation: optimize the template and pre-stage the portal session; the operational margin must accommodate weekend / holiday determination timing.

---

### TC-5 — SEC Form 8-K Item 1.05 materiality determination and 4-business-day filing

**Objective.** Demonstrate that an AI-agent-related cybersecurity incident that the registrant determines to be material can be characterized, deliberated by the Disclosure Committee, cleared by outside counsel, and filed on Form 8-K Item 1.05 within four business days of the materiality determination.

**Regulatory anchor.** SEC Reg S-K Item 1.05 (effective December 2023 for large accelerated filers; June 2024 for smaller reporting companies). Materiality determination must be made "without unreasonable delay." The 4-business-day clock starts at materiality determination, not at incident detection.

**Setup.**

- Roles: Disclosure Committee Secretary (preparer); General Counsel + outside securities counsel (validators); Chief Executive Officer or designated principal financial officer (signatory for the 8-K filing).
- Applicability check: only registrants with SEC-reporting obligations must run this TC. Private firms log "N/A — non-registrant" with CCO sign-off and skip.
- Scenario: a Zone-3 enterprise agent supporting a customer-facing trading workflow is compromised; preliminary scoping suggests material impact to a reportable segment.

**Steps.**

1. Open a materiality-assessment workbook capturing: nature/scope/timing of the incident, impact on operations and financial condition, qualitative materiality factors per Staff Accounting Bulletin 99, and reasonable-investor framing.
2. Convene the Disclosure Committee. Mark T0 as the materiality-determination timestamp recorded in the minute.
3. Engage outside securities counsel for a written sign-off on the materiality conclusion and on the proposed 8-K language.
4. Draft Item 1.05 narrative addressing: material aspects of the nature, scope, and timing of the incident; material impact or reasonably likely material impact on the registrant including financial condition and results of operations. **Avoid technical detail that would impede response or provide a roadmap for further attack** (per SEC adopting release).
5. Stage the EDGAR filing through the firm's filer agent; do not transmit. Mark T1 as the staged-ready timestamp.
6. Confirm T1 − T0 ≤ 4 business days, computed using the firm's published business-day calendar (NYSE/Nasdaq trading days for most issuers).
7. If material, evaluate whether amendment under Item 1.05(c) will be needed once additional facts are determined; record the planned amendment cadence.

**Expected.**

- Materiality determination supported by documented analysis, not unreasonably delayed.
- Outside-counsel written sign-off received before staging.
- 4-business-day clock observed with operational margin.

**Evidence Capture.**

- `materiality-assessment-workbook.xlsx`, `disclosure-committee-minute.pdf`, `outside-counsel-signoff.pdf`, `item-1-05-narrative-draft.pdf`, `edgar-staged-screenshot.png`, `business-day-calc.xlsx`, `amendment-plan.pdf`.
- Signed evidence record `agt34.v1.4` with `tc_id="TC-05"`, fields `t0_materiality`, `t1_edgar_staged`, `business_days_used`.

**Remediation.**

- If materiality determination has no documented analysis: this fails the "without unreasonable delay" standard on its face. Re-run with a complete workbook before filing any future 8-K.
- If outside counsel cannot sign off within the 4-business-day window: pre-engage counsel on retainer with defined response SLAs; this is a Disclosure Committee charter item and not a one-time fix.

---

### TC-6 — Federal banking 36-hour notification (12 CFR 53 / 225 / 304)

**Objective.** Demonstrate that a banking-organization-affiliated firm can, upon determining a "computer-security incident" that rises to a "notification incident," notify its primary federal banking regulator within 36 hours.

**Regulatory anchor.** 12 CFR Part 53 (OCC), Part 225 Subpart N (FRB), Part 304 (FDIC). Definitions of "notification incident" turn on actual or reasonably likely material disruption or degradation; the 36-hour clock starts at determination.

**Setup.**

- Roles: Chief Information Security Officer (preparer); Chief Risk Officer (validator); Chief Compliance Officer + bank-holding-company General Counsel (joint signatories).
- Applicability check: only firms or affiliates that are insured depository institutions, bank holding companies, or US operations of foreign banking organizations run this TC. Others log "N/A — non-bank-affiliate" and skip.
- Scenario: an AI agent supporting a bank-affiliate's loan-origination back-office workflow degrades materially due to a model-data poisoning event that disrupts processing across multiple branches.

**Steps.**

1. Convene the firm's bank-affiliate incident-management triad (CISO, CRO, GC). Score the event against the "notification incident" definition: actual or reasonably likely impact to (a) ability to deliver banking products/services, (b) business lines that would result in material loss, or (c) operations that threaten financial stability.
2. Mark T0 as the determination timestamp recorded in the triad minute.
3. Identify the primary federal regulator (OCC for national banks/federal savings; FRB for state-member and BHCs; FDIC for state-nonmember insured banks). Confirm the contact channel published in the regulator's most recent guidance (typically a designated email address or supervisory point of contact).
4. Draft the 36-hour notification using the regulator's format expectation (often a brief factual summary; the rule does not prescribe a form). Stage transmission; do not send.
5. Mark T1 as the staged-ready timestamp; confirm T1 − T0 ≤ 36h.

**Expected.**

- Determination supported by mapping to the rule's three-prong notification-incident definition.
- Correct primary regulator identified; contact channel current.
- 36-hour clock observed with operational margin.

**Evidence Capture.**

- `notification-incident-scoring.pdf`, `triad-minute.pdf`, `regulator-channel-confirmation.pdf`, `36h-notification-draft.pdf`, `staged-evidence.png`.
- Signed evidence record `agt34.v1.4` with `tc_id="TC-06"`, fields `regulator`, `t0_determination`, `t1_staged`.

**Remediation.**

- If the firm cannot confidently identify its primary federal regulator for this purpose within minutes: the CCO must publish a single-page reference card to the incident-response runbook within 5 business days.
- If contact channel has not been verified within 92 days: add a quarterly verification step to TC-2.

---

### TC-7 — Reg S-P 30-day customer notification + 72-hour service-provider notification (2024 amendments)

**Objective.** Demonstrate readiness under the SEC's amended Regulation S-P (adopted May 2024) for (a) customer notification within 30 days of determining unauthorized access to or use of customer information, and (b) service-provider notification within 72 hours under contractual flow-down.

**Regulatory anchor.** 17 CFR Part 248 (Reg S-P, as amended 2024). Compliance dates phased: large entities December 3, 2025; smaller entities June 3, 2026.

**Setup.**

- Roles: Chief Compliance Officer (preparer); Privacy Officer (validator); General Counsel (signatory).
- Inputs: firm's standard service-provider data-processing addendum containing the 72-hour incident-flow-down clause; standard customer-notification template.
- Scenario: an AI agent processing customer account data in a Zone-3 environment is found to have transmitted customer NPI to a misconfigured third-party logging endpoint operated by a vendor.

**Steps.**

1. Confirm the firm's compliance tier and the corresponding effective date; confirm the test is being run on or after that date (or, if before, log as readiness-only).
2. Determine that unauthorized access or use of customer information has occurred or is reasonably likely. Mark T0.
3. Identify affected customers; confirm scope using the firm's customer-data-mapping inventory (Control 2.10 cross-reference).
4. Generate the customer-notification draft. Confirm content addresses: incident description, type of information involved, steps customer can take, firm contact information, and any free credit-monitoring offer required by state law overlay.
5. Generate the 72-hour service-provider notification under the data-processing addendum, addressed to the upstream broker-dealer or investment adviser as applicable.
6. Stage both notifications; do not send. Mark T1 (SP staged) and T2 (customer staged). Confirm T1 − T0 ≤ 72h and T2 − T0 ≤ 30 days.
7. Pull a sample of three current vendor contracts and confirm the 72-hour flow-down clause is present and binding.

**Expected.**

- Customer-notification draft includes all required elements; 30-day window observed.
- Service-provider 72-hour clause present in sampled vendor contracts.
- Both clocks observed with operational margin.

**Evidence Capture.**

- `compliance-tier-confirmation.pdf`, `customer-notification-draft.pdf`, `sp-72h-notification-draft.pdf`, `vendor-contract-clause-sample.pdf` (3 contracts, redacted), `data-mapping-extract.csv`.
- Signed evidence record `agt34.v1.4` with `tc_id="TC-07"`, fields `t0_determination`, `t1_sp_staged`, `t2_customer_staged`.

**Remediation.**

- If any sampled vendor contract lacks the 72-hour flow-down: open a Procurement / GC remediation ticket; track to closure under Control 2.10 (third-party AI-component governance).
- If customer-notification template lacks any required Reg S-P element: update the template and re-test before next quarter.

---
### TC-8 — FINRA Rule 4530(a) 30-day reporting for AI-agent-related events

**Objective.** Demonstrate that an AI-agent-related event meeting any FINRA Rule 4530(a) trigger (e.g., associated person involvement in a covered violation, certain customer-complaint dispositions, written customer complaints involving theft or misappropriation) is reported within 30 calendar days via the FINRA Firm Gateway.

**Regulatory anchor.** FINRA Rule 4530(a). The 30-day clock starts on the date the firm has concluded, or reasonably should have concluded, that the reportable event has occurred.

**Setup.**

- Roles: Designated Series 24 Principal (preparer); Compliance Officer (validator); Chief Compliance Officer (signatory).
- Inputs: current 4530(a) decision-tree job aid; access to FINRA Firm Gateway (staging or production with submit gate disabled).
- Scenario: an AI agent generated a customer-facing communication that misrepresented a security's risk profile, the customer filed a written complaint alleging misrepresentation, and the firm has settled the complaint for an amount exceeding the de minimis threshold.

**Steps.**

1. Walk the event through the 4530(a) decision tree; identify the specific subsection that applies (here, typically (a)(1)(B) — written customer complaint alleging certain types of misconduct, or (a)(1)(G) — settlement-related disclosure threshold).
2. Confirm the AI-agent attribution: which agent, which session(s), which model version, which knowledge source. Map to the agent inventory (Control 1.1).
3. Mark T0 as the firm's conclusion timestamp recorded in the principal's review note.
4. Draft the 4530(a) submission via the Firm Gateway interface; complete all mandatory fields. Stage; do not submit. Mark T1.
5. Confirm T1 − T0 ≤ 30 calendar days with operational margin.

**Expected.**

- Decision-tree application is documented and signed by the designated principal.
- AI-agent attribution is unambiguous and ties to inventory.
- 30-day window observed.

**Evidence Capture.**

- `4530a-decision-tree.pdf`, `principal-review-note.pdf`, `agent-attribution-extract.csv`, `firm-gateway-staged.png`, `4530a-draft.pdf`.
- Signed evidence record `agt34.v1.4` with `tc_id="TC-08"`, fields `subsection`, `t0_conclusion`, `t1_staged`.

**Remediation.**

- If agent attribution cannot be reconstructed within hours: this is a Control 1.1 (inventory) and Control 3.1 (logging) finding — escalate cross-control.
- If the principal's review note is missing or unsigned: the 4530(a) decision is procedurally defective regardless of substantive correctness.

---

### TC-9 — FINRA Rule 4530(d) quarterly statistical reporting with AI-channel rollup

**Objective.** Demonstrate that the firm's quarterly 4530(d) statistical report of written customer complaints includes an AI-channel rollup distinguishing complaints arising from interactions with AI agents from other channels.

**Regulatory anchor.** FINRA Rule 4530(d); FINRA RN 24-09 / Rule 3110 (AI-related supervisory expectations).

**Setup.**

- Roles: Compliance Officer (preparer); Designated Series 24 Principal (validator); Chief Compliance Officer (signatory).
- Inputs: prior-quarter complaint store extract; AI-agent session correlation table.

**Steps.**

1. Pull all written customer complaints received during the most recently closed calendar quarter from the firm's complaint system.
2. Run the KQL below against the unified audit log (UAL) plus the agent-session correlation table to identify complaints whose root interaction touches an AI agent. Capture the query and its SHA-256.

```kusto
// kql.id: agt34-tc09-ai-channel-rollup
let qStart = startofquarter(ago(90d));
let qEnd = endofquarter(ago(90d));
let agentSessions =
    AIAgentSessions_CL
    | where TimeGenerated between (qStart .. qEnd)
    | project SessionId, UserUpn, AgentId, AgentClass, TimeGenerated;
ComplaintStore_CL
| where ComplaintReceivedDate between (qStart .. qEnd)
| join kind=leftouter (agentSessions) on $left.LinkedSessionId == $right.SessionId
| extend AiChannel = iif(isnotempty(SessionId), "AI", "Non-AI")
| summarize ComplaintCount = count() by AiChannel, ProductLine, AllegationCategory
```

3. Produce the quarterly 4530(d) submission worksheet with separate AI-channel columns; reconcile to the complaint-store totals.
4. Stage the submission via Firm Gateway; do not submit. Confirm filing falls within 15 calendar days after quarter-end (FINRA expectation).

**Expected.**

- AI-channel rollup reconciles to complaint store with zero variance.
- Submission staged within the 15-day window.
- KQL hash captured.

**Evidence Capture.**

- `complaint-store-extract.csv`, `kql-ai-channel.kql`, `kql-ai-channel.sha256`, `4530d-worksheet.xlsx`, `firm-gateway-staged.png`, `reconciliation-summary.pdf`.
- Signed evidence record `agt34.v1.4` with `tc_id="TC-09"`, fields `quarter`, `ai_complaint_count`, `non_ai_complaint_count`.

**Remediation.**

- If reconciliation variance > 0: investigate session-correlation gaps. Variance reflects either incomplete UAL coverage (Control 3.1) or incomplete complaint-store linkage (Control 3.5).
- If AI-channel rollup is not produced at all: this is a direct FINRA RN 24-09 / Rule 3110 finding; escalate to AI Governance Lead.

---

### TC-10 — GLBA Safeguards Rule 30-day FTC notification (≥500 consumers)

**Objective.** Demonstrate readiness to notify the FTC within 30 days of discovery of a notification event involving the unauthorized acquisition of unencrypted customer information of 500 or more consumers.

**Regulatory anchor.** 16 CFR Part 314 as amended (effective May 2024); FTC Safeguards Rule notification requirement.

**Setup.**

- Roles: Privacy Officer (preparer); Chief Compliance Officer (validator); General Counsel (signatory).
- Applicability: firms that are "financial institutions" under GLBA and not otherwise excepted; broker-dealers and investment advisers with consumer-customer relationships.
- Scenario: an AI agent's debug logs containing unencrypted customer NPI for ≥500 consumers were inadvertently exposed to an unauthorized internal audience.

**Steps.**

1. Confirm the event meets the "notification event" definition (unauthorized acquisition of unencrypted customer information of ≥500 consumers).
2. Mark T0 as the discovery timestamp.
3. Compose the FTC notification per the rule's content requirements (firm name and contact, notification event description, type of information involved, dates of event and discovery, number of consumers affected, law-enforcement-delay status if applicable).
4. Stage the FTC online submission; do not submit. Mark T1; confirm T1 − T0 ≤ 30 days.

**Expected.**

- Discovery timestamp documented; consumer count substantiated by data-mapping extract.
- All required content elements present.
- 30-day window observed.

**Evidence Capture.**

- `notification-event-determination.pdf`, `consumer-count-substantiation.csv`, `ftc-notification-draft.pdf`, `ftc-staged-screenshot.png`.
- Signed evidence record `agt34.v1.4` with `tc_id="TC-10"`, fields `consumer_count`, `t0_discovery`, `t1_staged`.

**Remediation.**

- If consumer count cannot be substantiated within 5 business days: this is a Control 2.10 (data-mapping) finding.
- If the consumer count is uncertain at T0+30d: the rule does not allow waiting; notify with best estimate and amend.

---

### TC-11 — State breach-notification readiness (top-10 residency states)

**Objective.** Demonstrate that the firm's state breach-notification matrix is current for at least the top 10 states by customer residency, and that a single AI-agent-related incident can be characterized against each state's threshold and timing rule.

**Regulatory anchor.** State breach-notification statutes (e.g., NY GBL 899-aa, CA Civ. Code 1798.82, MA 201 CMR 17, IL 815 ILCS 530, TX Bus. & Com. 521, FL 501.171, NJ 56:8-163, PA 73 P.S. 2301, OH 1349.19, WA 19.255 — list to be confirmed against current customer-residency distribution).

**Setup.**

- Roles: Privacy Officer (preparer); state-counsel network (validator); General Counsel (signatory).
- Inputs: current customer-residency distribution extract; the state matrix as maintained in the Control 3.4 reference set.

**Steps.**

1. Pull customer-residency distribution from the firm's CRM; identify the top 10 states by count.
2. For each, capture: statute citation, breach definition, notification trigger, timing rule, AG-notification trigger, content requirements, encryption safe-harbor language.
3. Walk the synthetic incident from TC-10 through each state's matrix; produce 10 mini-determinations.
4. Confirm the firm has in-state counsel or counsel-of-record relationships for each.

**Expected.**

- Matrix current for all 10 states (last updated ≤ 180 days).
- Mini-determinations completed; counsel-of-record list current.

**Evidence Capture.**

- `residency-distribution.csv`, `state-matrix-top10.xlsx`, `mini-determinations.pdf`, `counsel-of-record.csv`.
- Signed evidence record `agt34.v1.4` with `tc_id="TC-11"`.

**Remediation.**

- If any of the top 10 state entries is older than 180 days: refresh within 30 days; this is a recurring quarterly task.
- If no counsel-of-record exists in a top-3 state: this is a Critical readiness gap.

---

### TC-12 — CISA CIRCIA quarterly horizon check

**Objective.** Confirm the firm tracks the CIRCIA final-rule horizon, identifies expected covered-entity status, and stages a 72-hour covered-cyber-incident report channel readiness pending effective date.

**Regulatory anchor.** Cyber Incident Reporting for Critical Infrastructure Act of 2022 (CIRCIA); CISA Notice of Proposed Rulemaking (April 2024). **Final rule not yet effective at time of this playbook revision** — TC-12 is a horizon-tracking exercise, not a live-clock test.

**Setup.**

- Roles: AI Governance Lead (preparer); Chief Information Security Officer (validator); Chief Compliance Officer (signatory).

**Steps.**

1. Pull current CISA rulemaking status from the federal register and CISA's CIRCIA program page.
2. Assess the firm's expected covered-entity status under the proposed rule's sector-and-size criteria.
3. Confirm the firm has identified an internal owner for the 72-hour covered-cyber-incident report and 24-hour ransom-payment report; confirm channel-of-record placeholder.
4. Log status to the horizon log referenced in TC-2.

**Expected.**

- Status documented; owner identified; channel placeholder in place.

**Evidence Capture.**

- `circia-status-snapshot.pdf`, `covered-entity-assessment.pdf`, `horizon-log-update.csv`.
- Signed evidence record `agt34.v1.4` with `tc_id="TC-12"`, fields `effective_date_known=false|true`.

**Remediation.**

- When effective date publishes: convert TC-12 from horizon check to live clock test (72h CCI report + 24h ransom-payment report) and re-baseline.

---

### TC-13 — NCUA 72-hour notification (applicability check)

**Objective.** Confirm applicability to the firm; if applicable, demonstrate readiness to notify NCUA within 72 hours of a reportable cyber incident.

**Regulatory anchor.** 12 CFR Part 748 Appendix B (NCUA cyber-incident notification, effective September 2023). Applies to federally insured credit unions.

**Setup.**

- Roles: Chief Compliance Officer (preparer); General Counsel (validator); Chief Compliance Officer (signatory).

**Steps.**

1. Confirm whether the firm or any affiliate is a federally insured credit union.
2. If **N/A**: log "N/A — not a federally insured credit union" with CCO sign-off; skip remaining steps.
3. If applicable: walk through the NCUA notification path analogous to TC-3 (Sentinel-derived determination, 72h staging via the NCUA designated channel).

**Expected.**

- Applicability conclusion is recorded and current (≤ 365 days).
- If applicable: 72h staging path is current and tested.

**Evidence Capture.**

- `applicability-determination.pdf`, optional `ncua-staged-evidence.png`.
- Signed evidence record `agt34.v1.4` with `tc_id="TC-13"`, fields `applicable=true|false`.

**Remediation.**

- If applicability changes (e.g., acquisition of a credit-union charter): elevate this TC to live status within 30 days.

---
### TC-14 — Critical-severity end-to-end with CISO + CCO + GC notification within 1 hour

**Objective.** Demonstrate that a Sev-Critical AI-agent incident routes notification to CISO + CCO + GC within 1 hour with delivery evidence (read receipt or acknowledged page).

**Regulatory anchor.** Internal SLA matrix from parent control; supports compliance with FINRA 3110 supervisory expectations and NYDFS 500.16 incident-response-plan requirements.

**Setup.**

- Roles: AI Administrator (preparer); Chief Information Security Officer (validator — also a notification target); Chief Compliance Officer (signatory — also a notification target).
- Inputs: synthetic Sev-Critical incident generator (`New-AgentIncident -Severity Critical -Synthetic`); the firm's paging / on-call platform.

**Steps.**

1. Pre-confirm the on-call schedule and acknowledge that CISO, CCO, and GC (or designated alternates) are reachable.
2. Trigger `New-AgentIncident -Severity Critical -Synthetic -RunId $RunId`. Mark T0 as the incident-creation timestamp.
3. Capture the Power Automate run history showing fan-out to the three notification targets; capture timestamps of message acceptance by the paging platform.
4. Capture acknowledgement timestamps from each target (page-ack, email read receipt, or chat-channel reaction).
5. Compute T_ack − T0 per target; confirm all three ≤ 1 hour.

**Expected.**

- All three notification targets acknowledged within 1 hour.
- Power Automate run completed without retries (or with retries that still met the 1h target).

**Evidence Capture.**

- `power-automate-run-history.json`, `paging-platform-export.csv`, `acks-summary.csv`, `notification-recipients.csv`.
- Signed evidence record `agt34.v1.4` with `tc_id="TC-14"`, fields `ciso_ack`, `cco_ack`, `gc_ack`, `t0_creation`.

**Remediation.**

- If any of the three failed to acknowledge within 1h: investigate (a) on-call coverage, (b) paging-platform routing, (c) notification flow logic. Re-test within 5 business days.
- If alternates were not designated: this is a Disclosure Committee charter gap.

---

### TC-15 — RCA gating with 5-Whys + corrective actions + MRM feedback ticket (Control 2.6)

**Objective.** Demonstrate that closed incidents pass a root-cause-analysis gate requiring (a) 5-Whys analysis, (b) defined corrective actions with owners and dates, and (c) for incidents flagged `AIAgentClass=DataQuality-ModelRisk`, a feedback ticket opened against Control 2.6 (model risk management).

**Regulatory anchor.** OCC Bulletin 2026-13 (formerly OCC Bulletin 2011-12) (model-risk management); Fed SR 26-2 (formerly SR 11-7) (interagency model-risk-management guidance); FINRA Rule 3110 (supervisory system).

**Setup.**

- Roles: AI Governance Lead (preparer); Compliance Officer (validator); Chief Compliance Officer (signatory).
- Inputs: closed-incident sample (n ≥ 30) drawn from the most recent 90 days.

**Steps.**

1. Pull the closed-incident sample using the KQL below; capture query and SHA-256.

```kusto
// kql.id: agt34-tc15-closed-incidents
let lookback = 90d;
AIAgentIncidents_CL
| where Status == "Closed" and ClosedTime > ago(lookback)
| extend AgentClass = tostring(parse_json(Tags).AIAgentClass)
| project IncidentId, OpenedTime, ClosedTime, Severity, AgentClass, RcaUri, CorrectiveActions, MrmFeedbackTicket
| sample 30
```

2. For each sampled incident, confirm: (a) `RcaUri` resolves to a 5-Whys document, (b) `CorrectiveActions` lists ≥1 action with owner and date, (c) if `AgentClass == "DataQuality-ModelRisk"`, `MrmFeedbackTicket` is populated and resolves to an open or closed Control 2.6 ticket.
3. Spot-check three RCA documents for analytical quality (not a rubber-stamp 5-Whys).

**Expected.**

- 100% of sampled incidents pass (a) and (b).
- 100% of `DataQuality-ModelRisk` incidents pass (c).
- Spot-check finds analysis substantive in all three.

**Evidence Capture.**

- `kql-closed-incidents.kql`, `kql-closed-incidents.sha256`, `sample-incidents.csv`, `rca-spotcheck-notes.pdf`, `mrm-feedback-tickets.csv`.
- Signed evidence record `agt34.v1.4` with `tc_id="TC-15"`, fields `sample_size`, `pass_count`, `pass_rate`.

**Remediation.**

- If pass rate < 100%: open a corrective-action ticket per failure; the AI Governance Lead reviews failure pattern monthly.
- If MRM feedback ticket missing for any DataQuality-ModelRisk incident: this is a Critical Control 2.6 integration finding; escalate to the Model Risk Officer.

---

### TC-16 — Legal hold via Purview eDiscovery (Premium) with custodian acknowledgments

**Objective.** Demonstrate that a legal hold can be placed within 1 business day of a regulator-notification trigger, custodians acknowledged within 5 business days, and hold scope verified via Purview eDiscovery (Premium) hold export.

**Regulatory anchor.** FRCP 37(e); Zubulake-line case law; SEC Rule 17a-4 (preservation duty).

**Setup.**

- Roles: eDiscovery Manager (preparer); General Counsel (validator); Chief Compliance Officer (signatory).
- Inputs: a synthetic regulator-notification trigger from any of TC-3..TC-13.

**Steps.**

1. Open a Purview eDiscovery (Premium) case linked to the run-id.
2. Place hold on identified custodians (the AI agent's owner principal, the agent's service principal mailbox if applicable, the RCA author, the Disclosure Committee Secretary). Mark T_hold as hold-effective timestamp.
3. Confirm hold scope includes Exchange, SharePoint, OneDrive, Teams chat, and Loop components.
4. Generate custodian-notification emails via the eDiscovery (Premium) acknowledgment workflow; capture send timestamps.
5. Track acknowledgments; confirm 100% within 5 business days.
6. Export hold report; confirm scope is unchanged.

**Expected.**

- T_hold within 1 business day of trigger.
- 100% custodian acknowledgment within 5 business days.
- Hold report shows expected custodians and locations.

**Evidence Capture.**

- `ediscovery-case-export.json`, `hold-report.csv`, `custodian-notifications-sent.csv`, `custodian-ack-log.csv`.
- Signed evidence record `agt34.v1.4` with `tc_id="TC-16"`, fields `t_hold`, `ack_rate`.

**Remediation.**

- If hold scope is missing a workload: confirm appropriate eDiscovery (Premium) license and re-issue hold; missing-workload holds are a spoliation risk.
- If a custodian fails to acknowledge by day 5: GC sends a follow-up; if no response by day 10, escalate to direct supervisor.

---

!!! info "Books-and-records vs operational retention"
    Microsoft Sentinel and Microsoft Defender XDR retain telemetry under their respective platform retention windows (Sentinel: typically 90 days hot + extended in Log Analytics or archive; Defender: typically 30-180 days depending on data type). **These retention surfaces are operational; they are not WORM-compliant under SEC Rule 17a-4(f).** When a Sentinel or Defender extract becomes part of a books-and-records package — for example, the determination KQL output that supports a 4530(a) decision, or the alert correlation that supports a 500.17(a) determination — the **extract** must be written to 17a-4(f)-compliant storage (with the audit trail and serialization documented), not relied upon in place. Operators must avoid implying that platform retention substitutes for books-and-records retention. TC-17 verifies the extract path; the operational platform is auxiliary.

### TC-17 — Books-and-records evidence chain to 17a-4(f) storage

**Objective.** Demonstrate that operational extracts (Sentinel queries, Defender alert exports, IRM case exports) supporting any books-and-records-scoped incident are written to 17a-4(f)-compliant storage with a documented chain of custody.

**Regulatory anchor.** SEC Rule 17a-4(f); FINRA Rule 4511. See the books-and-records admonition above.

**Setup.**

- Roles: Compliance Officer (preparer); eDiscovery Manager (validator); Chief Compliance Officer (signatory).
- Inputs: the firm's designated 17a-4(f)-compliant storage target (typically a third-party WORM service or an Azure Storage immutable-blob container with a vendor attestation supporting 17a-4(f) operation); chain-of-custody log template.

**Steps.**

1. Select three recent books-and-records-scoped incidents (any TC-3..TC-13 evidence record marked `tier="books-scope"`).
2. For each, run the extract KQL below to retrieve the supporting operational evidence; capture the query and SHA-256.

```kusto
// kql.id: agt34-tc17-books-extract
let runIds = dynamic(["AGT34-XXXXXXXX-XXXXXX-XXXXXXXX"]); // replace with actual run-ids
union SecurityAlert, SigninLogs, OfficeActivity, AIAgentSessions_CL
| where TimeGenerated > ago(180d)
| where tostring(AdditionalFields) has_any (runIds)
| project TimeGenerated, Source = $table, RunId = extract("AGT34-[A-Za-z0-9-]+", 0, tostring(AdditionalFields)), _ResourceId
```

3. Write each extract to the 17a-4(f) storage target with serialization metadata (date-time stamped, original media identifier, capture officer name).
4. Compute SHA-256 of each extract file; record in chain-of-custody log alongside ingestion receipt.
5. Confirm the storage target's WORM lock has engaged (immutability policy with retention ≥ 6 years for books-scope, or ≥ 7 years for compliance-records-scope).

**Expected.**

- All three extracts written and locked.
- Chain-of-custody log complete with SHA-256, capture officer, target URL.
- Vendor attestation supporting 17a-4(f) operation on file.

**Evidence Capture.**

- `kql-books-extract.kql`, `kql-books-extract.sha256`, `extract-files-manifest.csv`, `chain-of-custody-log.pdf`, `worm-lock-confirmation.png`, `vendor-attestation.pdf`.
- Signed evidence record `agt34.v1.4` with `tc_id="TC-17"`, fields `extract_count`, `worm_locked=true`.

**Remediation.**

- If WORM lock did not engage: do not rely on the storage target; revert to the prior validated path and escalate to the storage-platform owner.
- If vendor attestation is more than 24 months old: request refresh; older attestations may not reflect current 17a-4(f) interpretive guidance.

---

### TC-18 — Service Health correlation per Sev-Critical/High before firm-side RCA declared

**Objective.** Demonstrate that, for any Sev-Critical or Sev-High AI-agent incident, the M365 Service Health Reader has confirmed whether a coincident Microsoft service-side incident exists, and that this correlation check is recorded before the firm-side RCA is declared final.

**Regulatory anchor.** FFIEC IT Handbook (Operations) — correlation-discipline expectation in incident management.

**Setup.**

- Roles: M365 Service Health Reader (preparer); AI Governance Lead (validator); Chief Compliance Officer (signatory).
- Inputs: a recent Sev-Critical or Sev-High closed incident.

**Steps.**

1. For the selected incident, pull the Microsoft 365 Service Health advisory list covering the incident time window ± 12 hours.
2. Pull the Azure Status history for the same window.
3. Pull the Azure OpenAI / Foundry service status if the agent's underlying model traffic is involved.
4. Record correlation conclusion: (a) coincident Microsoft incident exists and is causally related, (b) coincident incident exists but is not causally related, (c) no coincident incident.
5. Confirm this conclusion is referenced in the firm-side RCA before final-RCA declaration timestamp.

**Expected.**

- Correlation check documented for 100% of Sev-Critical and Sev-High incidents.
- RCA declaration timestamp is after correlation-check timestamp.

**Evidence Capture.**

- `m365-service-health.json`, `azure-status-history.json`, `model-service-status.json`, `correlation-conclusion.pdf`.
- Signed evidence record `agt34.v1.4` with `tc_id="TC-18"`, fields `correlation_outcome`, `t_correlation`, `t_rca_final`.

**Remediation.**

- If correlation check is missing: the RCA must be re-opened and amended; an RCA without correlation discipline is examiner-defective.
- If a causally-related Microsoft incident is identified: ensure the firm-side RCA narrative reflects that the firm's controls operated as designed and the upstream cause was vendor-side.


### TC-19 — Annual SOX 404 incident-program self-assessment to Audit Committee

**Objective.** Demonstrate that, on at least an annual basis, the AI-agent incident-reporting program is subject to a SOX 404 self-assessment whose results are reported to the Audit Committee.

**Regulatory anchor.** Sarbanes-Oxley §§ 302 and 404; PCAOB AS 2201 (audit of internal control over financial reporting).

**Setup.**

- Roles: Internal Audit (preparer); Chief Financial Officer (validator); Chief Compliance Officer + Audit Committee Chair (signatories).
- Applicability: SEC-reporting issuers.

**Steps.**

1. Internal Audit performs design-and-operating-effectiveness testing of the incident-reporting program; samples ≥ 25 incidents from the year for procedural conformance.
2. Test results documented in a SOX workpaper package referencing TC-1 through TC-19.
3. Findings, if any, classified by severity and remediated or accepted.
4. Audit Committee minute reflects program presentation, findings, remediation, and Committee acknowledgment.

**Expected.**

- Self-assessment completed within the firm's SOX cycle.
- Audit Committee minute on file with date.

**Evidence Capture.**

- `sox-workpaper-package.pdf`, `incident-sample.csv`, `findings-log.csv`, `audit-committee-minute.pdf`.
- Signed evidence record `agt34.v1.4` with `tc_id="TC-19"`, fields `cycle_year`, `finding_count`.

**Remediation.**

- If material weaknesses are identified: convert to public disclosure under SOX §302/404 with outside-counsel guidance.
- If the self-assessment was not performed in the cycle: the program lacks SOX 404 attestation; the CFO and CCO must address before next 10-K filing.

---

### TC-20 — Quarterly AI tabletop battery (4 scenarios)

**Objective.** Demonstrate that, each quarter, the firm runs the four AI-specific tabletop scenarios required by the parent control: prompt-injection exfiltration; hallucinated customer communication; runaway agent on stale context; orphaned-agent cascade.

**Regulatory anchor.** FINRA RN 24-09 / Rule 3110; Fed SR 26-2 (formerly SR 11-7); NYDFS 23 NYCRR 500.16 (incident-response-plan testing).

**Setup.**

- Roles: AI Governance Lead (preparer); Chief Information Security Officer + Chief Compliance Officer (validators); General Counsel (signatory).
- Inputs: scenario decks for each of the four scenarios (maintained in `docs/playbooks/scenarios/` or equivalent).

**Steps.**

1. **Prompt-injection exfiltration.** A Zone-3 agent with retrieval over a confidential SharePoint site is prompted via a malicious user-supplied document to exfiltrate restricted content into a chat response. Walk the detection path (Defender XDR alert), the determination path (TC-3 KQL), and the notification path (TC-3 + TC-7).
2. **Hallucinated customer communication.** An agent generates a customer-facing email containing a fabricated material fact about a security. Walk the supervisory-review failure (Control 3.5), the complaint receipt, and the FINRA 4530(a) path (TC-8).
3. **Runaway agent on stale context.** An agent automation re-issues the same erroneous trade instruction repeatedly due to caching of stale model context. Walk the kill-switch (Control 1.6), Service Health correlation (TC-18), and the bank-affiliate or registrant notification path (TC-5 / TC-6).
4. **Orphaned-agent cascade.** An agent owner leaves the firm; an orphaned agent continues to execute and triggers anomalous activity. Walk the joiner-mover-leaver gap (Control 1.5), the determination path (TC-3), and the books-and-records evidence path (TC-17).
5. Each scenario produces an after-action report with: timeline, decisions made, gaps identified, owners and dates for remediation.

**Expected.**

- All four scenarios run within the quarter.
- After-action reports filed within 10 business days of each tabletop.
- Cross-control referrals (1.5, 1.6, 2.6, 3.1, 3.5) opened where applicable.

**Evidence Capture.**

- `tabletop-scenario-{n}-aar.pdf` × 4, `tabletop-attendance.csv` × 4, `cross-control-referrals.csv`.
- Signed evidence record `agt34.v1.4` with `tc_id="TC-20"`, fields `quarter`, `scenarios_completed`, `cross_referrals_opened`.

**Remediation.**

- If any scenario is skipped in a quarter: this is a FINRA RN 24-09 / Rule 3110 readiness gap; reschedule within the following 30 days and report to the Audit Committee.
- If after-action reports are perfunctory: the AI Governance Lead reviews and may require re-run with an independent facilitator.

---

### TC-21 — Evidence-retention sample audit (>6yr records, WORM, retrievability)

**Objective.** Demonstrate that a random sample (n ≥ 25) of incident-evidence records older than six years can be retrieved within a reasonable window from the books-and-records storage target, with WORM lock intact and chain-of-custody verifiable.

**Regulatory anchor.** SEC Rule 17a-4(b)(4) (six-year preservation for the first two in an easily accessible place); FINRA Rule 4511.

**Setup.**

- Roles: Compliance Officer (preparer); Internal Audit (validator); Chief Compliance Officer (signatory).
- Applicability: firms in operation ≥ 6 years with books-and-records-scoped evidence in storage.

**Steps.**

1. Pull a random sample (n ≥ 25) of evidence records with `created_at` > 6 years from the 17a-4(f) storage index.
2. For each, attempt retrieval; record retrieval latency.
3. Verify SHA-256 of retrieved file against the chain-of-custody log.
4. Verify WORM lock status on each record.
5. Confirm records remain associated with their TC-ID, run-id, and signature triple.

**Expected.**

- Retrieval succeeds for 100% of sampled records.
- SHA-256 matches for 100%.
- WORM lock intact for 100%.

**Evidence Capture.**

- `sample-records.csv`, `retrieval-latency.csv`, `sha-verification.csv`, `worm-lock-status.csv`.
- Signed evidence record `agt34.v1.4` with `tc_id="TC-21"`, fields `sample_size`, `retrieval_pass`, `sha_pass`, `worm_pass`.

**Remediation.**

- If any retrieval fails: this is a Critical 17a-4 finding; engage the storage vendor immediately and notify GC.
- If any SHA-256 mismatch: investigate possible tampering or migration corruption; a mismatch invalidates the evidentiary chain for that record.

---

## §3 Evidence-Pack Assembly

After all 22 TCs complete (or are recorded as N/A with sign-off), assemble the quarterly evidence pack:

1. Collect all signed evidence records from `$EvidenceRoot` for the run-id range covered.
2. Generate the pack manifest with TC-ID, run-id, preparer, validator, signatory, retention tier, and SHA-256 of each artifact bundle.
3. Sign the manifest using the Chief Compliance Officer's certificate; write to 17a-4(f) storage with retention metadata appropriate to the highest-tier artifact in the pack.
4. Register the pack in the AI Governance evidence index; cross-link to the parent-control file and to any related-control evidence packs (Control 1.5, 1.6, 2.6, 3.1, 3.5, 3.6).

The pack is the single examiner-facing artifact for Control 3.4 in any given quarter; it should stand on its own without requiring access to live tenants.

---

## §4 Examiner Walkthrough — Reading the Evidence Pack

Examiners reviewing a Control 3.4 evidence pack will typically follow this reading order. The pack is structured to support that order without requiring sequential live-system access.

1. **Manifest first.** The pack manifest lists every TC executed in the quarter, the run-id, the preparer / validator / signatory triple, and the SHA-256 of each artifact bundle. Examiners verify the manifest signature before opening any artifact.
2. **Regulator-clock conformance (TC-3 through TC-13).** Examiners typically open these in the order the firm's regulators appear on the firm's organizational chart — NYDFS for New York covered entities, then SEC, then the firm's primary federal banking regulator, then FINRA, then GLBA / state. Each TC is self-contained: determination timestamp, staging timestamp, delta, and the operational margin.
3. **Internal-SLA conformance (TC-1, TC-14).** Internal clocks are evaluated against the parent control's matrix; deltas are reported with the same numerical precision as the regulator clocks.
4. **RCA discipline (TC-15, TC-18).** Examiners look for evidence that the firm distinguished operational symptoms from root cause and that vendor-side correlation was performed before declaring root cause.
5. **Evidence chain (TC-16, TC-17, TC-21).** Examiners spot-check legal-hold currency, books-and-records 17a-4(f) lock status, and long-tail retrievability. A strong pack demonstrates that the firm's storage decisions match its preservation duty.
6. **Annual and quarterly cadence (TC-2, TC-19, TC-20).** These TCs anchor the program in the firm's governance calendar and connect to Audit Committee oversight.

A pack that survives this walkthrough without follow-up requests is the operational definition of "examiner-defensible" for Control 3.4.

---

## §5 Cross-Control Referrals Generated by This Playbook

The 22 TCs are designed to surface findings that, by their nature, must be opened against other controls. This is intentional: Control 3.4 is the connective tissue between detection (Pillar 1), management (Pillar 2), and reporting (Pillar 3). When a TC fails, the corrective action is often owned by another control's owner. The table below is a quick reference for the AI Governance Lead.

| Failing TC | Likely Cross-Control | Rationale |
|---|---|---|
| TC-1 (SLA drift) | 2.25 (governance console) | Notification-recipient mapping lives in inventory |
| TC-3 / TC-6 (determination latency) | 1.7, 1.8, 3.9 (logging, runtime protection, Sentinel) | Detection-side telemetry gaps |
| TC-4 (OFAC clearance) | 2.10 (third-party governance) | Vendor / DFIR broker due diligence |
| TC-7 (vendor 72h clause) | 2.10 (third-party governance) | Contract flow-down |
| TC-8 (4530(a) attribution) | 1.1 (inventory), 3.1 (logging) | Agent attribution unreconstructible |
| TC-9 (4530(d) reconciliation) | 3.5 (complaint handling) | Complaint-store linkage |
| TC-15 (RCA gating) | 2.6 (model risk management) | Model-class incidents missing MRM feedback |
| TC-16 (legal hold scope) | 1.9 (retention) | Workload coverage gap |
| TC-17 / TC-21 (WORM, retrievability) | 1.9 (retention) | Storage-target compliance |
| TC-18 (correlation discipline) | 3.6 (orphaned-agent), 1.6 (kill switch) | Vendor-side cause attribution |
| TC-20 (tabletop scenario gap) | 1.5 (joiner-mover-leaver), 1.6 (kill switch), 3.5 (supervision) | Scenario-specific control owners |

The AI Governance Lead reviews this table monthly and confirms that any open cross-control referrals are tracked in the firm's GRC system with owner, date, and target closure.

---

## §6 Negative Tests and Anti-Patterns

A complete verification program tests not only that controls operate when invoked but also that they refuse to operate in inappropriate ways. The following negative tests are run alongside the 22 positive TCs at least annually.

- **N-1 — Unilateral closure rejected.** Confirm that an attempt to close a Sev-Critical incident with only a single signature (no validator, no signatory) is rejected by the SharePoint list / Power Automate flow. Evidence: rejection log entry; no closed-state transition.
- **N-2 — Out-of-scope notification suppressed.** Confirm that an attempt to file a NYDFS notification from a tenant outside the NYDFS covered-entity boundary is flagged for review by GC, not auto-routed. Evidence: GC review entry.
- **N-3 — Books-and-records substitution rejected.** Confirm that Sentinel-only retention cannot be cited as 17a-4(f) coverage in the evidence-pack manifest builder. Evidence: builder error and corrective-pointer to TC-17.
- **N-4 — Same-individual triple rejected.** Confirm that the evidence-record signer cannot resolve preparer = validator = signatory to the same UPN. Evidence: dual-control-violation entry.
- **N-5 — Stale OFAC screening rejected.** Confirm that a TC-4 evidence record older than 24 hours from the staged-payment authorization timestamp is rejected for use. Evidence: screening-stale entry.

Negative-test results are filed alongside the positive-test pack and signed by the same triple.

---
[Back to Control 3.4](../../../controls/pillar-3-reporting/3.4-incident-reporting-and-root-cause-analysis.md) | [Portal Walkthrough](portal-walkthrough.md) | [PowerShell Setup](powershell-setup.md) | [Troubleshooting](troubleshooting.md)

*Updated: May 2026 | Version: v1.6.2 | UI Verification Status: Current*
