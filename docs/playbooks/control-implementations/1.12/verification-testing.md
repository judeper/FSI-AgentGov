# Control 1.12 — Verification & Testing: Insider Risk Detection and Response

> Examiner-defensible verification catalog for [Control 1.12 — Insider Risk Detection and Response](../../../controls/pillar-1-security/1.12-insider-risk-detection-and-response.md). Each test below maps a deterministic Setup, Steps, Expected outcome, Evidence Capture, and Remediation to a specific FSI regulatory expectation. Run on the cadence in §1, retain evidence per §3, and complete the annual + per-incident sign-off in §4.
>
> **Audience.** Chief Information Security Officer (CISO), Chief Compliance Officer (CCO), General Counsel (GC), Privacy Officer, AI Governance Lead, Internal Audit, IRM role-group holders (Admins / Analysts / Investigators / Auditors / Approvers), and the examiner-facing Compliance Officer who assembles the annual program self-assessment and per-incident evidence packages.
>
> **Sovereign clouds in scope.** Microsoft 365 Commercial · GCC · GCC High · DoD. 21Vianet is out of scope. Sovereign-cloud parity for Insider Risk Management — and especially **Adaptive Protection**, **Risky AI usage**, **Risky Agents**, **Forensic Evidence**, and the **Triage Agent** — is not equivalent to commercial. Each TC below specifies sovereign behavior or routes to TC-20 compensating-control evidence.
>
> **Cross-links.** [Portal Walkthrough](portal-walkthrough.md) · [PowerShell Setup](powershell-setup.md) · [Troubleshooting](troubleshooting.md) · [PowerShell Authoring Baseline](../../_shared/powershell-baseline.md).
>
> **Last UI Verified:** April 2026 against Microsoft Purview portal build 2026.04.x and Insider Risk Management Wave 1 release.

---

!!! warning "Non-Substitution"
    This playbook **supports compliance with**, but does **not by itself ensure compliance with**, FINRA Rule 3110 (Supervision), FINRA Rule 4511 (Books and Records), FINRA Regulatory Notice 21-18 (data-stewardship guidance for cloud-hosted books and records), FINRA Regulatory Notice 25-07 (Generative AI / Large Language Models — RFC; cited contextually only and not yet binding), SEC Rules 17a-3 / 17a-4 (Recordkeeping and Retention), Regulation S-P amendments (effective compliance dates 2024–2025; 30-day customer-notice and 72-hour incident-notice expectations as adopted), GLBA §501(b) (Safeguards Rule), SOX §404 (Internal Control over Financial Reporting), OCC Bulletin 2011-12 (Sound Practices for Model Risk Management) / Federal Reserve SR 11-7, CFTC Regulation 1.31, NYDFS 23 NYCRR 500 §§500.06 / 500.16 / 500.17, and the FFIEC IT Examination Handbook.

    A clean execution of every TC in this catalog is **necessary but not sufficient**:

    - It does **not replace** the firm's Written Supervisory Procedures (WSP).
    - It does **not replace** the registered-principal supervisory review obligation under FINRA Rule 3110, nor the supervisory designation expectations restated in FINRA 25-07 for AI-generated communications and AI-assisted supervisory tooling.
    - It does **not constitute** the firm's records-retention plane. IRM (and Forensic Evidence in particular) is an investigative surface; durable books-and-records retention is implemented separately under [Control 1.9](../../../controls/pillar-1-security/1.9-data-retention-and-deletion-policies.md) and [Control 1.7](../../../controls/pillar-1-security/1.7-comprehensive-audit-logging-and-compliance.md).
    - It does **not constitute** legal advice on state employee-monitoring statutes — see TC-13.
    - It does **not** assert sovereign-cloud feature parity. Confirm each capability against current Microsoft Learn at the start of every cycle.

!!! warning "Sovereign Cloud Availability"
    Microsoft Insider Risk Management has documented gaps in US Government cloud programs. As of the **April 2026** verification cycle:

    | Capability | Commercial | GCC | GCC High | DoD |
    |---|---|---|---|---|
    | IRM core (policies, alerts, cases) | GA | GA (subset) | Limited | Limited |
    | Risky Agents (default-applied) | GA | Verify Learn | Verify Learn | Verify Learn |
    | Risky AI usage (template) | GA | Limited / N/A | Limited / N/A | Limited / N/A |
    | Risky browser usage | Preview / GA | N/A | N/A | N/A |
    | Adaptive Protection | GA | **N/A** | **N/A** | **N/A** |
    | Forensic Evidence | GA (PAYG) | Verify Learn | Verify Learn | Verify Learn |
    | Triage Agent (Security Copilot) | GA (SCU + PAYG) | Limited | Limited | Limited |

    Where a capability is N/A or not yet at parity in the target cloud, mark the corresponding TC `NotApplicable — Sovereign Exception #____` and execute **TC-20 (Sovereign Compensating Control Exercise)** for that quarter. Do **not** report a "PASS" or "FAIL" against a capability that does not exist in the tenant — that is a defensible-evidence defect under FINRA 4511.

---

## Document Conventions

| Convention | Value |
|---|---|
| PowerShell baseline | PowerShell 7.4+ Core. `#Requires -Version 7.4` at the top of every executable script. See [`../../_shared/powershell-baseline.md`](../../_shared/powershell-baseline.md). |
| Regulatory hedging | "Supports compliance with" / "helps meet" / "required for" / "recommended to" / "aids in." Never overclaiming language. |
| UTC timestamping | All evidence carries `Get-Date -AsUTC -Format 'yyyy-MM-ddTHH:mm:ssZ'`. Local-time evidence is rejected at audit. |
| Hashing | SHA-256 over canonical JSON; SHA-256 sidecar `.sha256` file per evidence artifact. |
| Sovereign detection | Every Pester / KQL run records `(Get-MgContext).Environment` mapped to `Commercial / GCC / GCCH / DoD` and tags the evidence record. |
| Evidence retention | Two-tier: **operational** (per change ticket / 1–2 year working window) and **records-scope** (≥6 years on WORM, broker-dealer ≥7 years per FINRA 4511 / SEC 17a-4(f)). The records-scope tier is enforced via Purview retention labels with `deletionLocked = true`. |
| Run identifier | `IRM112-yyyyMMdd-HHmmss-<8charGuid>` embedded in every evidence record and filename. |
| Canonical role names | Per [`docs/reference/role-catalog.md`](../../../reference/role-catalog.md). No title substitution — "Global Administrator" is **not** a substitute for "Entra Global Admin"; "Compliance Administrator" is **not** a substitute for "Purview Compliance Admin". |
| KQL anchor | KQL snippets target Microsoft Sentinel workspaces enriched with M365 Defender + Purview + Entra ID Protection connectors. See [Control 3.9 — Microsoft Sentinel Integration](../../../controls/pillar-3-reporting/3.9-microsoft-sentinel-integration.md). |

---

## §1 Re-verification cadence

IRM signals are **non-static**. Microsoft ships analytics-model updates, indicator catalogs evolve, Adaptive Protection thresholds are tunable, and Forensic Evidence's 120-day clip-deletion ceiling creates a ticking-clock evidence horizon. The cadence below reflects OCC 2011-12 / Federal Reserve SR 11-7 ongoing-monitoring expectations for model-driven supervisory systems and the firm's Written Supervisory Procedures.

| TC | Frequency | Primary owner (canonical) | Counter-signer | Records-scope retention | Regulatory driver |
|---|---|---|---|---|---|
| TC-1 UAL + audit retention | Weekly + on-change | Purview Compliance Admin | Internal Audit | 7 years | FINRA 4511, SEC 17a-4(f), [Control 1.7](../../../controls/pillar-1-security/1.7-comprehensive-audit-logging-and-compliance.md) |
| TC-2 IRM role groups + SoD | Quarterly + on-change | Purview Compliance Admin | Internal Audit, GC | 7 years | FINRA 3110, SOX 404, NYDFS 500.07 |
| TC-3 Indicator baseline attestation | Quarterly | Purview Compliance Admin | AI Governance Lead, CCO | 7 years | FINRA 3110, OCC 2011-12 |
| TC-4 Risky Agents default policy | Monthly | Purview Compliance Admin | AI Governance Lead | 7 years | FINRA 25-07 (RFC), OCC 2011-12 |
| TC-5 Risky AI usage + Intune extension | Monthly | Purview Compliance Admin + Intune Admin | AI Governance Lead | 7 years | FINRA 25-07 (RFC), GLBA 501(b) |
| TC-6 Departing-user data theft | Monthly | Purview Compliance Admin + HR liaison | CCO | 7 years | FINRA 3110, Reg S-P (2024) |
| TC-7 Priority-user data leaks | Monthly | Purview Compliance Admin | CCO, GC | 7 years | FINRA 3110, GLBA 501(b), Reg S-P |
| TC-8 Security policy violations (MDE) | Monthly | Purview Compliance Admin + MDE Admin | CISO | 7 years | FFIEC, NYDFS 500.06 |
| TC-9 Risky browser usage | Monthly | Purview Compliance Admin | AI Governance Lead | 7 years | FINRA 3110, GLBA 501(b) |
| TC-10 Defender for Cloud Apps correlation | Quarterly | Defender for Cloud Apps Admin | CISO | 7 years | FINRA 4511, GLBA 501(b) |
| TC-11 Entra ID Protection signal correlation | Quarterly | Entra Security Reader + IRM Analyst | CISO | 7 years | NYDFS 500.06, FFIEC |
| TC-12 Forensic Evidence dual-auth | Quarterly + per-capture | IRM Investigator + IRM Approver | Privacy Officer, GC | Per legal hold (else records-scope ≥7y) | SEC 17a-4(b), FINRA 4511 |
| TC-13 State monitoring-law check | Annually + on enablement | Privacy Officer + GC | CCO | 7 years | State law (CT/DE/NY); GLBA 501(b) |
| TC-14 Triage Agent readiness | Quarterly + 90-day refresh | AI Governance Lead + CISO | CCO | 7 years | OCC 2011-12 / SR 11-7, FINRA 25-07 (RFC) |
| TC-15 Adaptive Protection wiring | Quarterly | Purview Compliance Admin + Conditional Access Admin | CISO | 7 years | OCC 2011-12, GLBA 501(b) |
| TC-16 Communication Compliance correlation | Quarterly | Purview Compliance Admin | CCO | 7 years | FINRA 3110, [Control 1.10](../../../controls/pillar-1-security/1.10-communication-compliance-monitoring.md), [Control 2.12](../../../controls/pillar-2-management/2.12-supervision-and-oversight-finra-rule-3110.md) |
| TC-17 Escalation chain | Quarterly + per-high-severity | IRM Analyst + CCO | CISO, GC | 7 years | FINRA 3110, NYDFS 500.17 (72h), Reg S-P (72h) |
| TC-18 Pseudonymization → unmask gate | Quarterly | Privacy Officer + IRM Auditor | GC, CCO | 7 years | GLBA 501(b), Reg S-P, state monitoring law |
| TC-19 Sentinel UEBA correlation | Quarterly | SOC Analyst (Sentinel) + IRM Analyst | CISO | 7 years | NYDFS 500.06, [Control 2.26](../../../controls/pillar-2-management/2.26-entra-agent-id-identity-governance.md), [Control 3.9](../../../controls/pillar-3-reporting/3.9-microsoft-sentinel-integration.md) |
| TC-20 Sovereign compensating-control | Quarterly (GCC/GCCH/DoD only) | CISO + CCO | GC, AI Governance Lead | 7 years | FINRA 4511, OCC 2011-12, sovereign-cloud exception register |
| TC-21 SOX 404 IRM self-assessment | Annually | CCO + Internal Audit | CISO, GC, Audit Committee | 7 years | SOX §§302/404, OCC 2011-12 |
| TC-22 Examination evidence-pack pull-test | Annually + on-examiner-request | CCO | Internal Audit, GC | 7 years | FINRA 4511, SEC 17a-4(f), Reg S-P |

> **Firm-defined SLAs.** Microsoft Learn does not publish IRM alert latency, triage SLA, or investigation duration ceilings. Any SLA cited below is **firm-defined per WSP**, not Microsoft-published. The only Microsoft-published processing windows cited are the **analytics scan up to 48 hours** and **Forensic Evidence clip retention of 120 days**.

---

## §0 Pre-Test Prerequisites

### §0.1 Operator role assignments (canonical)

| Operator role (canonical) | Entra / Purview role(s) | Used in TCs |
|---|---|---|
| Entra Global Admin | `Global Administrator` (break-glass only) | TC-2 (read-only enumeration) |
| Purview Compliance Admin | `Compliance Administrator` + IRM role-group `Insider Risk Management Admins` | TC-1 → TC-19 |
| AI Administrator | `AI Administrator` (Entra) | TC-4, TC-5, TC-9, TC-14 |
| AI Governance Lead | Custom RBAC (read on Purview, AI Admin Center, AgentDLP) | TC-3, TC-4, TC-5, TC-14, TC-21 |
| Compliance Officer / CCO | `Compliance Administrator` (read) + IRM `Insider Risk Management Auditors` | TC-2, TC-3, TC-21, TC-22 |
| Privacy Officer | IRM `Insider Risk Management Auditors` + Purview Audit Reader | TC-12, TC-13, TC-18 |
| General Counsel (GC) | IRM `Insider Risk Management Auditors` + eDiscovery Reviewer | TC-12, TC-13, TC-17, TC-21 |
| IRM Admin | `Insider Risk Management Admins` | TC-1 → TC-11, TC-15, TC-16 |
| IRM Analyst | `Insider Risk Management Analysts` | TC-3, TC-4, TC-5, TC-6, TC-7, TC-9, TC-10, TC-11, TC-17, TC-19 |
| IRM Investigator | `Insider Risk Management Investigators` | TC-12, TC-18 |
| IRM Approver | `Insider Risk Management Approvers` | TC-12, TC-18 (must NOT overlap Investigator membership — SoD gate) |
| IRM Auditor | `Insider Risk Management Auditors` | TC-1, TC-12, TC-13, TC-18, TC-21, TC-22 |
| Conditional Access Admin | `Conditional Access Administrator` | TC-15 |
| Defender for Cloud Apps Admin | `Defender for Cloud Apps Administrator` (or `Cloud App Security Admin` legacy) | TC-10 |
| MDE Admin | `Security Administrator` (Defender XDR) | TC-8 |
| Intune Admin | `Intune Administrator` | TC-5, TC-9 |
| SOC Analyst (Sentinel) | `Microsoft Sentinel Reader` (+ `Responder` for incident actions) | TC-19, TC-20 |
| Internal Audit | Read-only across IRM + Audit + Sentinel; no `Insider Risk Management` (the catch-all role group is **prohibited** in regulated FSI tenants) | TC-2, TC-21, TC-22 |

> **SoD gate.** The catch-all `Insider Risk Management` role group bundles all permissions and is **forbidden** in FSI tenants per [Control 1.5 §RBAC](../../../controls/pillar-1-security/1.5-data-loss-prevention-dlp-and-sensitivity-labels.md). TC-2 fails any environment in which it is populated.

### §0.2 Module baseline (pin to known-good versions)

```powershell
#Requires -Version 7.4
#Requires -Modules @{ModuleName='Pester'; ModuleVersion='5.5.0'}
#Requires -Modules @{ModuleName='ExchangeOnlineManagement'; ModuleVersion='3.5.1'}
#Requires -Modules @{ModuleName='Microsoft.Graph.Authentication'; ModuleVersion='2.19.0'}
#Requires -Modules @{ModuleName='Microsoft.Graph.Security'; ModuleVersion='2.19.0'}
#Requires -Modules @{ModuleName='Microsoft.Graph.Identity.SignIns'; ModuleVersion='2.19.0'}
#Requires -Modules @{ModuleName='Microsoft.Graph.Reports'; ModuleVersion='2.19.0'}
#Requires -Modules @{ModuleName='MicrosoftTeams'; ModuleVersion='6.1.0'}
#Requires -Modules @{ModuleName='Az.Accounts'; ModuleVersion='3.0.0'}
#Requires -Modules @{ModuleName='Az.OperationalInsights'; ModuleVersion='3.6.6'}
```

> Exact module versions are **firm-pinned**, not Microsoft-mandated. Any version drift invalidates the evidence cycle and forces re-execution.

### §0.3 PRE gates (executed once per cycle, before any TC runs)

| Gate | Assertion | Owner | On-fail |
|---|---|---|---|
| PRE-1 | PowerShell 7.4+ Core, Pester 5.5+ pinned per §0.2 | Purview Compliance Admin | Halt cycle; remediate workstation. |
| PRE-2 | Tenant licensing includes Microsoft 365 E5 + Microsoft 365 E5 Compliance (or equivalent). Forensic Evidence add-on enabled (PAYG bill-meter active). | Entra Global Admin (read) | Open ticket; record TC-1 evidence with `LicenseShortfall=true`. |
| PRE-3 | `(Get-MgContext).Environment` returns one of `Global / USGov / USGovDoD`. Tagged in every evidence record. | Purview Compliance Admin | Halt cycle if `Unknown`. |
| PRE-4 | UTC clock skew vs. `time.windows.com` < 2s (`w32tm /stripchart`). | Workstation owner | Re-sync NTP; rerun. |
| PRE-5 | Evidence root path resolves to immutable / WORM-backed share with retention label `IRM-EvidenceLock-7y` (or firm equivalent). | Purview Compliance Admin | Halt cycle. |
| PRE-6 | Pseudonymization is **enabled** in IRM settings (default: on). | Privacy Officer | Halt cycle; record incident under TC-18. |
| PRE-7 | `UnifiedAuditLogIngestionEnabled = $true` for the tenant. | Exchange Online Admin | Halt cycle (TC-1 cannot pass). |
| PRE-8 | Run identifier generated and bound to the cycle. | Test runner | Auto-generate. |

### §0.4 Sovereign bootstrap helper

The helper below is referenced by every TC. It is read-only and emits a sovereign tag without mutating tenant state.

```powershell
function Test-Agt112SovereignTenant {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory)] [string] $RunId
    )
    $ctx = Get-MgContext
    $env = if ($ctx) { $ctx.Environment } else { 'Unknown' }
    $cloud = switch ($env) {
        'Global'    { 'Commercial' }
        'USGov'     { 'GCC-or-GCCH' }   # Graph does not split GCC vs. GCCH at this layer
        'USGovDoD'  { 'DoD' }
        default     { 'Unknown' }
    }
    [pscustomobject]@{
        RunId           = $RunId
        UtcTimestamp    = (Get-Date -AsUTC -Format 'yyyy-MM-ddTHH:mm:ssZ')
        GraphEnvironment= $env
        SovereignCloud  = $cloud
        IsSovereign     = ($cloud -in 'GCC-or-GCCH','DoD')
        AdaptiveProtectionInScope   = ($cloud -eq 'Commercial')
        ForensicEvidenceInScope     = $true   # verify on Microsoft Learn each cycle
        TriageAgentInScope          = ($cloud -eq 'Commercial')
        RiskyBrowserUsageInScope    = ($cloud -eq 'Commercial')
    }
}
```

> If `SovereignCloud = 'Unknown'`, every downstream TC is invalidated. Do **not** continue.

---

## §2 Test Catalog

Each TC follows a fixed schema:

```
TC-N · <Title>  ·  Frequency  ·  Owner / Counter-signer
  Setup
  Steps
  Expected
  Evidence Capture
  Remediation
  Regulatory tie-in
```

Mutation operations (policy creation, role-group membership change, license assignment) are **not** performed in this playbook — they live in [`powershell-setup.md`](powershell-setup.md). Verification asserts read-only state.

---

### TC-1 · Unified Audit Log + audit retention attestation
**Frequency:** Weekly + on-change · **Owner:** Purview Compliance Admin · **Counter-signer:** Internal Audit · **Legacy alias:** `1.12-UAL-01`

#### Setup

- PRE-1 → PRE-8 PASS.
- Operator: Purview Compliance Admin with `View-Only Audit Logs` + `Audit Logs` Exchange roles.
- Time window: previous 7 UTC days.

#### Steps

```powershell
$RunId = "IRM112-$(Get-Date -AsUTC -Format 'yyyyMMdd-HHmmss')-$([Guid]::NewGuid().ToString('N').Substring(0,8))"
$sov = Test-Agt112SovereignTenant -RunId $RunId

# 1. Confirm UAL ingestion is enabled
$cfg = Get-AdminAuditLogConfig
$ualOn = $cfg.UnifiedAuditLogIngestionEnabled

# 2. Confirm IRM-class operations are emitting
$ops = @(
  'InsiderRiskMgmtAlertUpdated','InsiderRiskMgmtCaseCreated','InsiderRiskMgmtCaseResolved',
  'InsiderRiskMgmtPolicyCreated','InsiderRiskMgmtPolicyUpdated','InsiderRiskMgmtPolicyDeleted',
  'InsiderRiskMgmtForensicEvidenceCaptureRequested','InsiderRiskMgmtForensicEvidenceCaptureApproved',
  'InsiderRiskMgmtForensicEvidenceCaptureDenied','InsiderRiskMgmtUserUnmasked'
)
$start = (Get-Date).AddDays(-7).ToUniversalTime()
$end   = (Get-Date).ToUniversalTime()
$hits = Search-UnifiedAuditLog -StartDate $start -EndDate $end -Operations $ops -ResultSize 5000 |
  Group-Object Operations | Select-Object Name,Count
```

#### Expected

- `UnifiedAuditLogIngestionEnabled = $true`.
- At minimum the *Policy* operations emit in any 7-day window where IRM is in steady-state operation (Created/Updated/Deleted ≥ 0 is acceptable; absence of *all* IRM operations across 7 days is a finding because it indicates either no IRM activity or, more likely, a connector failure).
- Audit retention label `Audit-10y-WORM` (or firm equivalent) is applied to the IRM operation set.

#### Evidence Capture

- `tc01-ual-state.json` — `{ RunId, Sovereign, UnifiedAuditLogIngestionEnabled, OperationsObserved[] }` + `.sha256`.
- Screenshot: Purview portal → Audit → Search → filter `InsiderRiskMgmt*` over 7 days → result count and CSV export header captured.
- Retention: 7 years (records-scope) per FINRA 4511 / SEC 17a-4(f).

#### Remediation

- If `UnifiedAuditLogIngestionEnabled = $false`: invoke `Set-AdminAuditLogConfig -UnifiedAuditLogIngestionEnabled $true` per [`powershell-setup.md` §2.1](powershell-setup.md). Re-run after ≥ 24h.
- If IRM operations never appear: open Sev-2; verify Purview connector health and IRM policy activation.

#### Regulatory tie-in

FINRA 4511 · SEC 17a-4(f) · NYDFS 500.06 · [Control 1.7](../../../controls/pillar-1-security/1.7-comprehensive-audit-logging-and-compliance.md).

---

### TC-2 · IRM role groups + Separation-of-Duties
**Frequency:** Quarterly + on-change · **Owner:** Purview Compliance Admin · **Counter-signer:** Internal Audit, General Counsel · **Legacy alias:** `1.12-ROLE-01`

#### Setup

- Operator: Purview Compliance Admin (read).
- Reference list of IRM role groups: `Insider Risk Management`, `Insider Risk Management Admins`, `Insider Risk Management Analysts`, `Insider Risk Management Investigators`, `Insider Risk Management Auditors`, `Insider Risk Management Approvers`.

#### Steps

```powershell
Connect-IPPSSession
$groups = 'Insider Risk Management','Insider Risk Management Admins','Insider Risk Management Analysts',
          'Insider Risk Management Investigators','Insider Risk Management Auditors','Insider Risk Management Approvers'

$state = foreach ($g in $groups) {
    $rg = Get-RoleGroup -Identity $g -ErrorAction SilentlyContinue
    if ($rg) {
        $members = (Get-RoleGroupMember -Identity $g).Name
        [pscustomobject]@{ Group=$g; Exists=$true; MemberCount=$members.Count; Members=$members }
    } else {
        [pscustomobject]@{ Group=$g; Exists=$false; MemberCount=0; Members=@() }
    }
}

# SoD: Investigator ∩ Approver MUST be empty
$inv = ($state | Where-Object Group -eq 'Insider Risk Management Investigators').Members
$apv = ($state | Where-Object Group -eq 'Insider Risk Management Approvers').Members
$overlap = $inv | Where-Object { $apv -contains $_ }

# Catch-all role group: MUST be empty in FSI
$catchall = ($state | Where-Object Group -eq 'Insider Risk Management').MemberCount
```

#### Expected

- All five scoped role groups exist (Admins, Analysts, Investigators, Auditors, Approvers).
- `$overlap.Count -eq 0` (Investigator ↔ Approver SoD).
- `$catchall -eq 0` (catch-all role group must be empty in regulated FSI tenants).
- Each scoped role group has a documented owner and a dual-control change procedure (PIM-eligible, not permanent).

#### Evidence Capture

- `tc02-roles.json` — full member rosters with hashed UPNs.
- `tc02-sod.json` — overlap set and catch-all population.
- Quarterly attestation memo signed by CCO + GC.
- Retention: 7 years.

#### Remediation

- Overlap detected → IRM Approver demotes from `Insider Risk Management Investigators` (or vice-versa) per [`powershell-setup.md` §3](powershell-setup.md); re-run within 24h.
- Catch-all populated → empty membership immediately; document remediation in change ticket; treat any prior alerts/cases handled by catch-all members as **uncertified evidence** subject to GC review.

#### Regulatory tie-in

FINRA 3110 (supervisory designation) · SOX 404 (segregation of duties) · NYDFS 500.07 · OCC 2011-12 (model governance) · [Control 1.5](../../../controls/pillar-1-security/1.5-data-loss-prevention-dlp-and-sensitivity-labels.md).

---

### TC-3 · Indicator baseline attestation
**Frequency:** Quarterly · **Owner:** Purview Compliance Admin · **Counter-signer:** AI Governance Lead, CCO

#### Setup

- Operator: Purview Compliance Admin + IRM Analyst (read).
- Baseline indicator catalog versioned in source control under `governance/irm-indicators/baseline.yaml`.

#### Steps

1. Purview portal → Insider Risk Management → **Settings → Policy indicators**.
2. Export the enabled indicator set (UI export → CSV).
3. Diff the export against `baseline.yaml`. Categories of interest:
   - Office indicators (downloads, prints, sync, copy to USB, copy to network share, copy to clipboard from sensitive files).
   - Device indicators (file activity by device, browser-based exfil).
   - Microsoft Defender for Endpoint indicators (security violations, AV detections, AppLocker / WDAC blocks).
   - Healthcare / pharma indicators — **disabled in FSI** unless mapped to a regulated workload.
   - Risky AI usage indicators (Copilot / agent prompt categories).
   - Risky browser usage indicators.
   - Risky Agents indicators (default-applied — see TC-4).
4. Attest indicator weights and time-bound thresholds align with the firm's WSP and the latest OCC 2011-12 / SR 11-7 model-tuning memo.

#### Expected

- Diff result `0` against the locked baseline OR a pre-approved RFC reference is included in the evidence package.
- Healthcare / pharma indicators are off (or, if on, an explicit FSI mapping memo is attached).
- All AI- and agent-class indicators (Risky AI usage, Risky Agents, Risky browser usage) are reviewed and signed by the AI Governance Lead.

#### Evidence Capture

- `tc03-indicators-export.csv` (UI export).
- `tc03-indicators-diff.json` (diff vs. baseline).
- `tc03-attestation.pdf` (signed by Purview Compliance Admin + AI Governance Lead + CCO).
- Retention: 7 years.

#### Remediation

- Drift detected → revert via [`powershell-setup.md` §4](powershell-setup.md) **only after** the change is rejected by RFC, or update the baseline.yaml under change control.

#### Regulatory tie-in

FINRA 3110 · OCC 2011-12 / SR 11-7 (model risk: indicator drift = parameter drift) · [Control 2.6](../../../controls/pillar-2-management/2.6-model-risk-management-alignment-with-occ-2011-12-sr-11-7.md).

---

### TC-4 · Risky Agents default policy verification
**Frequency:** Monthly · **Owner:** Purview Compliance Admin · **Counter-signer:** AI Governance Lead

#### Setup

- Operator: Purview Compliance Admin + IRM Analyst.
- Reference: Risky Agents is a **default-applied** policy template in IRM and covers Microsoft 365 Copilot agents, Copilot Studio agents, and Azure AI Foundry agents registered to the tenant.

#### Steps

1. Purview portal → Insider Risk Management → **Policies** → confirm a policy of template "Risky AI agent activity" (or current Microsoft-published name) exists and is **Active**.
2. Confirm it scopes to `All users and groups` for agent-attributable activity (per default).
3. Cross-check the agent inventory against [Control 3.1 — Agent inventory](../../../controls/pillar-3-reporting/3.1-agent-inventory-and-metadata-management.md) so that every registered agent is in scope.
4. Pull the last 30-day alert volume by agent identity (Entra Agent ID) — see [Control 2.26](../../../controls/pillar-2-management/2.26-entra-agent-id-identity-governance.md).

```powershell
# Read-only: list IRM policies via IPPS
Connect-IPPSSession
Get-InsiderRiskPolicy | Where-Object { $_.Name -like '*Agent*' -or $_.TemplateName -like '*Agent*' } |
  Select-Object Name,TemplateName,Mode,Enabled,WhenChangedUTC
```

#### Expected

- Risky Agents policy exists, `Enabled = $true`, and scope includes **all** registered Copilot / Copilot Studio / Foundry agents reconciled against [Control 3.1](../../../controls/pillar-3-reporting/3.1-agent-inventory-and-metadata-management.md).
- Reconciliation gap (agents in inventory but not in IRM scope) = `0`.
- Pseudonymization on (re-asserted from PRE-6).

#### Evidence Capture

- `tc04-risky-agents-policy.json`.
- `tc04-agent-reconciliation.csv` (Entra Agent ID × IRM scope).
- Retention: 7 years.

#### Remediation

- Reconciliation gap > 0 → register missing agent in inventory or scope into IRM per [`powershell-setup.md` §5](powershell-setup.md).

#### Regulatory tie-in

FINRA 25-07 (RFC; AI/LLM supervision) · OCC 2011-12 / SR 11-7 (agent = model surface) · [Control 1.6](../../../controls/pillar-1-security/1.6-microsoft-purview-dspm-for-ai.md) · [Control 2.26](../../../controls/pillar-2-management/2.26-entra-agent-id-identity-governance.md) · [Control 3.1](../../../controls/pillar-3-reporting/3.1-agent-inventory-and-metadata-management.md).

> **Sovereign note.** Verify Risky Agents availability against current Microsoft Learn for the target sovereign cloud each cycle. Where the template is `NotApplicable`, route to TC-20.

---


### TC-5 · Risky AI usage policy + Intune-deployed extension
**Frequency:** Monthly · **Owner:** Purview Compliance Admin + Intune Admin · **Counter-signer:** AI Governance Lead

#### Setup

- Risky AI usage requires the **Microsoft Insider risk extension** (Edge) or **Microsoft Purview extension** (Chrome). Both are **Windows-only** as of the April 2026 cycle. macOS / Linux / iOS / Android cannot contribute browser-side AI signal.
- Operator: Purview Compliance Admin (IRM policy state) + Intune Admin (extension assignment state).

#### Steps

1. Purview portal → Insider Risk Management → **Policies**: confirm template "Risky AI usage" is **Active** and scoped to `Priority users — AI workforce` (firm-defined dynamic group).
2. Intune admin centre → **Apps** → confirm:
   - Edge configuration profile: `ExtensionInstallForcelist` includes the Microsoft Insider risk extension ID.
   - Chrome ADMX policy (if Chrome is in scope): `ExtensionInstallForcelist` includes the Microsoft Purview extension ID.
3. From a target Windows endpoint enrolled in Intune, validate the extension is installed and enabled (not user-removable).
4. Validate signal flow: walk through the `tc05-walkthrough.md` simulated prompt set (firm-curated, non-PII, e.g., financial-summary requests against a sandbox tenant). Wait up to 48h for the analytics scan.
5. Confirm an alert appears under the Risky AI usage policy with pseudonymized user reference.

```powershell
# Read-only Intune assignment check via Microsoft Graph
Connect-MgGraph -Scopes 'DeviceManagementConfiguration.Read.All','DeviceManagementApps.Read.All' -NoWelcome
$profiles = Get-MgDeviceManagementDeviceConfiguration -All
$edgeForce = $profiles | Where-Object { $_.AdditionalProperties.omaSettings -match 'ExtensionInstallForcelist' }
```

#### Expected

- Risky AI usage policy `Enabled = $true`, scope = AI-workforce dynamic group.
- Extension force-installed on 100% of in-scope Windows endpoints (record gap %).
- Walkthrough alert lands within 48h with pseudonymized user reference.
- macOS / non-Windows endpoints flagged in evidence as **out of browser-signal scope** with documented compensating control (e.g., DLP + Purview audit).

#### Evidence Capture

- `tc05-policy.json`, `tc05-extension-coverage.csv`, `tc05-walkthrough-alert.json`, screenshot of alert detail (pseudonymized user visible).
- Retention: 7 years.

#### Remediation

- Coverage gap → push Intune assignment to remediation group; re-run within 7 days.
- Alert never appears → escalate via [`troubleshooting.md` §6 — Risky AI signal absence](troubleshooting.md).

#### Regulatory tie-in

FINRA 25-07 (RFC; AI-generated communications) · GLBA 501(b) (data-leak channel) · [Control 1.6](../../../controls/pillar-1-security/1.6-microsoft-purview-dspm-for-ai.md) · [Control 1.13](../../../controls/pillar-1-security/1.13-sensitive-information-types-sits-and-pattern-recognition.md).

---

### TC-6 · Departing-user data-theft policy
**Frequency:** Monthly · **Owner:** Purview Compliance Admin + HR liaison · **Counter-signer:** CCO · **Legacy alias:** `1.12-DEPART-01`

#### Setup

- HR connector pre-loads `EmployeeID`, `ResignationDate`, `LastWorkingDate` for any user with a resignation event in the last 90 days.
- Operator: Purview Compliance Admin + HR system custodian (read-only attestation).

#### Steps

1. Purview portal → IRM → **Settings → HR data**: confirm connector status `Healthy`, last sync ≤ 24h.
2. Confirm "Data theft by departing users" policy is `Active`, lookback 90 days, look-ahead 30 days post-`LastWorkingDate`.
3. Diff HR-source resignation roster (CSV) against IRM in-scope user count: drift = `0`.
4. Spot-check three randomly-sampled users in scope (pseudonymized in IRM UI).

```powershell
# HR connector health (read-only)
Connect-IPPSSession
$conn = Get-DataInsightsImportSchedule | Where-Object { $_.SourceType -eq 'HR' }
$conn | Select-Object Name,Status,LastImportTime,RecordsProcessed
```

#### Expected

- HR connector `Status = Healthy`, drift = 0.
- Policy `Active`, lookback/look-ahead windows match WSP.
- Pseudonymization is on (PRE-6 holds).

#### Evidence Capture

- `tc06-hr-connector.json`, `tc06-hr-vs-irm-drift.csv`, sampled screenshots of pseudonymized scope.
- Retention: 7 years.

#### Remediation

- Drift > 0 → re-run HR connector via [`powershell-setup.md` §6](powershell-setup.md); investigate field-mapping for missing `EmployeeID` / `LastWorkingDate`.

#### Regulatory tie-in

FINRA 3110 · Reg S-P 2024 (customer-information handling at offboarding) · GLBA 501(b) · [Control 1.9](../../../controls/pillar-1-security/1.9-data-retention-and-deletion-policies.md).

---

### TC-7 · Priority-user data-leaks policy (FSI roles)
**Frequency:** Monthly · **Owner:** Purview Compliance Admin · **Counter-signer:** CCO, GC

#### Setup

- Priority user groups (FSI canonical): traders, investment bankers, research analysts, wealth advisors, branch supervisors, loan officers, client service representatives, privileged administrators.
- Operator: Purview Compliance Admin.

#### Steps

1. Purview IRM → **Priority user groups**: confirm each FSI canonical group exists and is bound to an Entra dynamic group whose membership rule is documented and version-controlled.
2. Confirm the "Data leaks by priority users" policy is `Active` and references the canonical groups.
3. Pull a 30-day alert summary by priority group; confirm at least one alert path (or documented explanation if zero — small populations are normal).

#### Expected

- All eight canonical priority groups present and bound.
- Policy `Active`, scope = canonical priority groups.
- Pseudonymization on.

#### Evidence Capture

- `tc07-priority-groups.json`, `tc07-priority-policy.json`, 30-day alert summary CSV.
- Retention: 7 years.

#### Remediation

- Missing group → recreate via [`powershell-setup.md` §7](powershell-setup.md). Re-attest within 7 days.

#### Regulatory tie-in

FINRA 3110 (heightened supervision of registered persons) · GLBA 501(b) · Reg S-P · [Control 1.5](../../../controls/pillar-1-security/1.5-data-loss-prevention-dlp-and-sensitivity-labels.md).

---

### TC-8 · Security policy violations (Defender for Endpoint integration)
**Frequency:** Monthly · **Owner:** Purview Compliance Admin + MDE Admin · **Counter-signer:** CISO

#### Setup

- Microsoft Defender for Endpoint (MDE) onboarded ≥ 95% of Windows / macOS endpoints (record exact %).
- Operator: Purview Compliance Admin + Security Administrator (Defender XDR).

#### Steps

1. Confirm IRM "Security policy violations" template is `Active`.
2. Confirm MDE → IRM connector is `Healthy` (Settings → Insider Risk Management).
3. Pull 30-day correlation between MDE incidents and IRM alerts.

#### Expected

- Connector `Healthy`.
- Endpoint coverage ≥ 95% (firm threshold; not Microsoft-mandated).
- Correlation rate documented.

#### Evidence Capture

- `tc08-mde-connector.json`, coverage CSV, correlation summary.
- Retention: 7 years.

#### Remediation

- Coverage < 95% → escalate to MDE Admin per [`troubleshooting.md` §8](troubleshooting.md).

#### Regulatory tie-in

FFIEC IT Handbook · NYDFS 500.06 · OCC heightened standards.

---

### TC-9 · Risky browser usage (Edge / Chrome extension)
**Frequency:** Monthly · **Owner:** Purview Compliance Admin · **Counter-signer:** AI Governance Lead

#### Setup

- Same extension prerequisites as TC-5 (Windows-only).
- Operator: Purview Compliance Admin + Intune Admin.

#### Steps

1. Purview IRM → confirm "Risky browser usage" policy is `Active` and scoped per WSP (priority groups + departing users at minimum).
2. Re-validate extension force-install coverage (may share evidence with TC-5).
3. Walkthrough: from a sandbox user, navigate to a curated risky-category URL set; confirm signal arrives within 48h.

#### Expected

- Policy `Active`.
- Extension coverage ≥ firm-defined threshold.
- Walkthrough event lands.

#### Evidence Capture

- `tc09-policy.json`, `tc09-walkthrough.json`, extension-coverage CSV.
- Retention: 7 years.

#### Remediation

- Walkthrough fails → see [`troubleshooting.md` §9](troubleshooting.md).

#### Regulatory tie-in

FINRA 3110 · GLBA 501(b) · Reg S-P.

> **Sovereign note.** Risky browser usage is **N/A** in GCC / GCC High / DoD as of the April 2026 cycle. Route to TC-20 in those clouds.

---

### TC-10 · Defender for Cloud Apps signal correlation (June 2025 dynamic threat detection)
**Frequency:** Quarterly · **Owner:** Defender for Cloud Apps Admin · **Counter-signer:** CISO

#### Setup

- Defender for Cloud Apps (MDA) "Dynamic threat detection" model (June 2025 release, commercial cloud) provides anomaly-driven signals consumable by IRM.
- Operator: Defender for Cloud Apps Admin + IRM Analyst.

#### Steps

1. MDA portal → Settings → confirm dynamic threat detection model is enabled and connected to IRM.
2. Pull 90-day MDA-originated IRM alerts; confirm at least one of: anomalous-download, mass-export, impossible-travel-coupled-with-data-access.
3. Cross-reference each MDA-originated alert with a corresponding IRM case or analyst-triage record.

#### Expected

- Model enabled, connector healthy.
- Cross-reference ratio = 100% (every MDA-originated alert acknowledged in IRM).
- Pseudonymization preserved end-to-end.

#### Evidence Capture

- `tc10-mda-irm-correlation.csv`, `tc10-model-state.json`.
- Retention: 7 years.

#### Remediation

- Cross-reference < 100% → analyst SLA breach; review in [`troubleshooting.md` §10](troubleshooting.md).

#### Regulatory tie-in

FINRA 4511 · GLBA 501(b) · NYDFS 500.06.

> **Sovereign note.** Verify dynamic threat detection availability in the target sovereign cloud. Where unavailable, route to TC-20.

---

### TC-11 · Entra ID Protection signal correlation
**Frequency:** Quarterly · **Owner:** Entra Security Reader + IRM Analyst · **Counter-signer:** CISO

#### Setup

- Entra ID Protection (P2) emits user / sign-in risk signals consumable by IRM and Conditional Access.
- Operator: Entra Security Reader + IRM Analyst.

#### Steps

1. Entra portal → Protection → confirm risk policies (sign-in risk, user risk) are `On` with documented thresholds.
2. Pull 90-day high-risk users; confirm each high-risk user has either:
   - An IRM case or alert, **or**
   - A Conditional Access remediation record (MFA / password reset), **or**
   - A documented benign-rationale memo signed by the SOC.
3. Confirm Entra Agent ID risk telemetry (where applicable) flows to IRM — see [Control 2.26](../../../controls/pillar-2-management/2.26-entra-agent-id-identity-governance.md).

```powershell
Connect-MgGraph -Scopes 'IdentityRiskyUser.Read.All','IdentityRiskEvent.Read.All' -NoWelcome
$risky = Get-MgRiskyUser -Filter "riskLevel eq 'high'" -All
```

#### Expected

- Risk policies `On`.
- 100% of high-risk users have a corresponding IRM / CA / SOC record.

#### Evidence Capture

- `tc11-risky-users.json`, `tc11-correlation.csv`.
- Retention: 7 years.

#### Remediation

- Coverage gap → analyst follow-up within 5 business days; document in incident log.

#### Regulatory tie-in

NYDFS 500.06 / 500.12 · FFIEC · [Control 2.26](../../../controls/pillar-2-management/2.26-entra-agent-id-identity-governance.md).

---


### TC-12 · Forensic Evidence dual-authorization
**Frequency:** Quarterly + per-capture · **Owner:** IRM Investigator + IRM Approver · **Counter-signer:** Privacy Officer, GC · **Legacy alias:** `1.12-FE-01`

!!! info "Forensic Evidence ≠ books-and-records retention"
    Forensic Evidence captures **screen-recording clips** for IRM investigations under a strict **120-day clip-deletion ceiling** and is billed **PAYG** per minute. It is an **investigative surface** designed to satisfy investigative discovery, dual-authorization, and right-to-be-forgotten constraints — **not** a durable books-and-records store.

    Records-tier retention for the **substance** of an alert / case / investigation outcome (analyst notes, decisions, exfiltrated-content fingerprints, regulatory submissions) is implemented separately under [Control 1.9 — Data retention and deletion](../../../controls/pillar-1-security/1.9-data-retention-and-deletion-policies.md), [Control 1.7 — Audit logging](../../../controls/pillar-1-security/1.7-comprehensive-audit-logging-and-compliance.md), [Control 1.19 — eDiscovery for agent interactions](../../../controls/pillar-1-security/1.19-ediscovery-for-agent-interactions.md), and the firm's records-management plane.

    A clip that has aged past 120 days is **gone** unless it has been (a) exported under a documented legal hold per the firm's eDiscovery procedure, or (b) preserved as part of an in-progress IRM case where the export-to-evidence step has been completed. **Every Forensic Evidence capture has an evidentiary half-life — the per-capture playbook below treats that half-life as a clock that starts the moment the Approver approves the capture.**

#### Setup

- Forensic Evidence add-on enabled (PAYG meter active per PRE-2).
- Two distinct individuals occupying `Insider Risk Management Investigators` and `Insider Risk Management Approvers` (TC-2 SoD gate must hold).
- State-law check (TC-13) completed for every jurisdiction in scope.
- Operator: IRM Investigator (capture requestor) + IRM Approver (independent approver).

#### Steps

1. **Quarterly attestation walkthrough** (no real user impacted):
   - IRM Investigator requests a sandbox-user capture via Purview portal → IRM → Forensic Evidence capture request.
   - IRM Approver receives the request, reviews business justification, and approves OR denies.
   - Confirm UAL emits both `InsiderRiskMgmtForensicEvidenceCaptureRequested` and `InsiderRiskMgmtForensicEvidenceCaptureApproved` (or `…Denied`) within 1 hour.
2. **Per-capture playbook** (real captures):
   - Investigator opens a request bound to a specific case ID with documented justification (regulatory tie-in, applicable indicators, target jurisdiction).
   - Approver verifies (a) state-law notice obligations are satisfied, (b) target user is on-notice via the firm's monitoring-disclosure programme, (c) capture window is minimised.
   - On approval, the capture begins. Clip metadata (RunId, case ID, target hash, jurisdiction, approval reference) recorded immediately.
   - **Within 100 days** of the approval timestamp (i.e., 20 days before clip auto-deletion), Investigator decides: extend hold via export-to-evidence (records-tier), preserve under legal hold, or allow auto-deletion. Decision logged in the case timeline.

```powershell
# Read-only audit confirmation
Connect-ExchangeOnline
$ops = 'InsiderRiskMgmtForensicEvidenceCaptureRequested','InsiderRiskMgmtForensicEvidenceCaptureApproved','InsiderRiskMgmtForensicEvidenceCaptureDenied'
$start = (Get-Date).AddDays(-90).ToUniversalTime()
$end   = (Get-Date).ToUniversalTime()
$fe = Search-UnifiedAuditLog -StartDate $start -EndDate $end -Operations $ops -ResultSize 5000
$fe | Group-Object Operations | Select-Object Name,Count
```

#### Expected

- SoD: zero overlap between Investigator and Approver memberships (re-asserts TC-2).
- UAL operations emit on every capture event.
- Every approved capture has a documented 100-day decision record (extend / hold / auto-delete).
- No capture proceeds in a jurisdiction lacking a current TC-13 attestation.

#### Evidence Capture

- `tc12-fe-quarterly.json` (sandbox walkthrough).
- `tc12-fe-per-capture-{caseId}.json` (per-capture record + approver identity hash + jurisdiction reference).
- `tc12-fe-decision-{caseId}.json` (100-day decision artifact).
- Retention: per legal hold; otherwise records-tier ≥ 7 years for the **decision metadata** (the clip itself is governed by the 120-day Microsoft ceiling unless exported).

#### Remediation

- SoD overlap → halt all in-flight captures; demote per TC-2 remediation; re-attest within 24h; treat any in-flight captures as unverified pending GC review.
- Missed 100-day decision → record as a finding; document any clip aged-out; report to CCO; review process design.
- Capture initiated without TC-13 attestation → halt immediately; notify Privacy Officer and GC; trigger incident-response per [Control 1.10](../../../controls/pillar-1-security/1.10-communication-compliance-monitoring.md) and the firm's privacy-incident playbook.

#### Regulatory tie-in

SEC 17a-4(b) (preservation of records when captured) · FINRA 4511 · GLBA 501(b) · State employee-monitoring statutes · [Control 1.19](../../../controls/pillar-1-security/1.19-ediscovery-for-agent-interactions.md).

---

### TC-13 · State employee-monitoring law check
**Frequency:** Annually + on every Forensic Evidence enablement / scope change · **Owner:** Privacy Officer + General Counsel · **Counter-signer:** CCO

!!! danger "State employee-monitoring laws"
    Connecticut, Delaware, and New York each impose **statutory written-notice obligations** on employers that engage in electronic monitoring of employees, including but not limited to screen recording, keystroke logging, and content monitoring. As of the April 2026 cycle:

    - **Connecticut General Statutes §31-48d** — written notice of types of monitoring that may occur.
    - **Delaware Code Title 19 §705** — daily electronic notice or one-time written acknowledgement.
    - **New York Civil Rights Law §52-bis** — written notice on hire and conspicuous workplace posting.

    Other states (e.g., California under the CCPA/CPRA, and various state wiretap statutes) may impose related obligations depending on the **substance** of what is captured (e.g., communications content versus user-action telemetry). Multistate, hybrid, and cross-border workforces may trigger overlapping obligations.

    **This playbook does not constitute legal advice.** No Forensic Evidence capture, Risky AI / Risky browser walkthrough on a real user, or pseudonymization-unmask action shall proceed in any jurisdiction unless the Privacy Officer and General Counsel have signed the current TC-13 attestation for that jurisdiction. The Privacy Officer maintains the canonical jurisdiction × in-scope-feature matrix; GC owns the legal interpretation.

#### Setup

- Privacy Officer maintains `governance/state-monitoring-matrix.yaml` enumerating each jurisdiction × in-scope IRM feature × notice mechanism × on-hire / annual / on-change cadence.
- Operator: Privacy Officer + GC.

#### Steps

1. Compare current employee residency / work-location data (HR source of truth) against `state-monitoring-matrix.yaml`. New jurisdictions appearing in the workforce must be added before any monitoring-feature scope expansion.
2. For each jurisdiction with active monitoring features, confirm:
   - Written notice issued to all in-scope employees (acknowledgement record exists).
   - Workplace posting (where required, e.g., NY) is current.
   - Daily-electronic-notice mechanism (where required, e.g., DE) is operating.
3. For Forensic Evidence specifically, GC sign-off attests jurisdictional notice satisfies the substance of the capture (screen-recording clips).
4. Annual re-attestation memo signed by Privacy Officer + GC + CCO.

#### Expected

- Matrix is current; no jurisdiction has active monitoring without satisfied notice.
- Attestation memo signed and stored at records-tier.
- TC-12 captures honor TC-13 jurisdiction status (no capture in a jurisdiction without current attestation).

#### Evidence Capture

- `tc13-jurisdiction-matrix.yaml` (versioned).
- `tc13-attestation-{year}.pdf` (signed).
- HR-source vs. matrix diff CSV.
- Retention: 7 years.

#### Remediation

- Notice gap detected → suspend all monitoring features in the affected jurisdiction immediately; notify CCO and CISO; rectify notice; re-attest before reactivating.

#### Regulatory tie-in

State employee-monitoring statutes (CT §31-48d, DE Title 19 §705, NY Civil Rights Law §52-bis) · GLBA 501(b) (privacy implementation) · NYDFS 500.06 (where overlapping).

---

### TC-14 · Triage Agent (Security Copilot) readiness
**Frequency:** Quarterly + 90-day saved-auth/config refresh · **Owner:** AI Governance Lead + CISO · **Counter-signer:** CCO

#### Setup

- Triage Agent depends on Microsoft Security Copilot, Security Compute Units (SCU), and a PAYG meter.
- The Triage Agent's saved authentication and configuration **expire on a 90-day cycle** — refresh is a hard prerequisite to continued operation.
- Operator: AI Governance Lead + CISO.

#### Steps

1. Security Copilot portal → confirm SCU allocation ≥ firm-defined floor (record exact allocation; not Microsoft-mandated).
2. IRM → Triage Agent → confirm `Status = Healthy`, `LastConfigRefreshUtc` ≤ 90 days ago, `LastAuthRefreshUtc` ≤ 90 days ago.
3. Pull a 30-day sample of agent-triaged alerts; confirm each agent-recommendation has a corresponding analyst review-and-disposition record (the agent is **decision-support**, not the supervisory decision-maker — see FINRA 25-07 RFC).
4. Sample 5% of agent recommendations for analyst-level fidelity review (false-positive / false-negative scoring) per OCC 2011-12 / SR 11-7 ongoing model monitoring.

#### Expected

- SCU allocation ≥ floor.
- Saved auth + config refreshed within 90 days.
- 100% of agent-triaged alerts have an analyst review-and-disposition record.
- Fidelity review documented and signed by AI Governance Lead.

#### Evidence Capture

- `tc14-triage-state.json`, `tc14-fidelity-sample.csv`, `tc14-attestation.pdf`.
- Retention: 7 years.

#### Remediation

- Refresh expiring → schedule via change ticket per [`powershell-setup.md` §10](powershell-setup.md).
- Fidelity drift → escalate to AI Governance Lead; potentially retune indicator weights (TC-3) under model-risk RFC.

#### Regulatory tie-in

OCC 2011-12 / SR 11-7 (model risk; Triage Agent is a decision-support model surface) · FINRA 25-07 (RFC) · [Control 2.6](../../../controls/pillar-2-management/2.6-model-risk-management-alignment-with-occ-2011-12-sr-11-7.md).

> **Sovereign note.** Triage Agent / Security Copilot has limited sovereign availability. Where unavailable, route to TC-20.

---

### TC-15 · Adaptive Protection wiring (sovereign-aware)
**Frequency:** Quarterly · **Owner:** Purview Compliance Admin + Conditional Access Admin · **Counter-signer:** CISO

#### Setup

- Adaptive Protection links IRM risk levels (Minor / Moderate / Elevated) to dynamic enforcement in DLP, Conditional Access, and Data Lifecycle Management.
- **Adaptive Protection is `NotApplicable` in GCC, GCC High, and DoD** as of the April 2026 cycle (verify Microsoft Learn each cycle).
- Operator: Purview Compliance Admin + Conditional Access Admin.

#### Steps

**Commercial cloud:**

1. Purview IRM → Adaptive Protection → confirm risk-level → policy bindings exist for Minor / Moderate / Elevated and reference firm-approved DLP and Conditional Access policies.
2. Pull a 30-day sample of users who entered each risk band; confirm enforcement applied.
3. Confirm de-escalation (risk band drop) removes enforcement after the documented cool-down window.

**Sovereign clouds (GCC / GCCH / DoD):**

- Mark this TC `NotApplicable — Sovereign Exception #15` and execute TC-20 with the **Adaptive Protection compensating-control** scenario:
  - Static Conditional Access policy targeting documented priority-user risk groups.
  - Manual analyst-driven escalation procedure (documented SLA).
  - Quarterly review of escalation outcomes.

#### Expected (commercial)

- Bindings present for all three bands.
- Enforcement applied + de-escalated cleanly in samples.

#### Evidence Capture

- `tc15-adaptive-bindings.json`, sample-set CSV, sovereign-exception record where applicable.
- Retention: 7 years.

#### Remediation

- Binding missing → re-bind per [`powershell-setup.md` §11](powershell-setup.md).
- Sovereign cloud → TC-20 compensating-control execution.

#### Regulatory tie-in

OCC 2011-12 (dynamic risk response) · GLBA 501(b) · NYDFS 500.06.

---

### TC-16 · Communication Compliance correlation (supervisory tie-in)
**Frequency:** Quarterly · **Owner:** Purview Compliance Admin · **Counter-signer:** CCO

#### Setup

- Communication Compliance (CC) supervises communications under FINRA 3110 and the firm's WSP.
- Operator: Purview Compliance Admin.

#### Steps

1. Confirm CC policies covering FINRA 3110 supervisory scope are `Active` per [Control 1.10](../../../controls/pillar-1-security/1.10-communication-compliance-monitoring.md).
2. Pull a 90-day cross-reference: CC alerts where the **same user** also produced an IRM alert in the same window.
3. Confirm any cross-referenced pair is jointly triaged in the supervisory-review record per [Control 2.12](../../../controls/pillar-2-management/2.12-supervision-and-oversight-finra-rule-3110.md).

#### Expected

- CC policies `Active`.
- 100% of cross-referenced pairs jointly triaged.

#### Evidence Capture

- `tc16-cc-irm-correlation.csv`, `tc16-supervisory-tieout.csv`.
- Retention: 7 years.

#### Remediation

- Cross-reference gap → analyst follow-up; review supervisory-review handoff.

#### Regulatory tie-in

FINRA 3110 · FINRA 4511 · [Control 1.10](../../../controls/pillar-1-security/1.10-communication-compliance-monitoring.md) · [Control 2.12](../../../controls/pillar-2-management/2.12-supervision-and-oversight-finra-rule-3110.md).

---

### TC-17 · Escalation chain (72-hour regulatory clocks)
**Frequency:** Quarterly + per-high-severity incident · **Owner:** IRM Analyst + CCO · **Counter-signer:** CISO, GC

#### Setup

- Two regulatory clocks govern escalation:
  - **NYDFS 23 NYCRR 500.17(a)** — 72-hour cybersecurity event notification.
  - **Reg S-P (2024)** — 30-day customer notification + 72-hour incident clock per the adopted amendments.
- Operator: IRM Analyst + CCO.

#### Steps

1. Pull a 90-day sample of high-severity IRM alerts. For each:
   - Confirm escalation-to-CCO timestamp ≤ firm-defined SLA (firm WSP-defined; not Microsoft-published).
   - Confirm CCO disposition: in-scope of 72-hour clock vs. out-of-scope, with documented rationale.
   - Where in-scope: confirm regulator-notification draft drafted within 48 hours and submitted within 72 hours.
2. Run a quarterly tabletop exercise (1 simulated incident) end-to-end: detection → analyst → CCO → GC → CISO → regulator-notification draft → close.

#### Expected

- 100% of high-severity alerts have CCO-disposition record.
- 100% of in-scope incidents meet the 72-hour clock.
- Tabletop exercise completed with after-action memo.

#### Evidence Capture

- `tc17-escalation-sample.csv`, `tc17-tabletop-{quarter}.pdf`.
- Retention: 7 years.

#### Remediation

- Clock breach → root-cause analysis within 7 business days; CCO + GC + CISO sign-off; report to Audit Committee.

#### Regulatory tie-in

NYDFS 500.17(a) · Reg S-P 2024 · FINRA 3110 · GLBA 501(b).

---

### TC-18 · Pseudonymization → unmask gate
**Frequency:** Quarterly · **Owner:** Privacy Officer + IRM Auditor · **Counter-signer:** GC, CCO

#### Setup

- Pseudonymization is **default-on** in IRM. Unmask is restricted to `Insider Risk Management Investigators` and is fully audited.
- Operator: Privacy Officer + IRM Auditor.

#### Steps

1. Reconfirm PRE-6 (pseudonymization on).
2. Pull 90-day audit of `InsiderRiskMgmtUserUnmasked` operations:

```powershell
Connect-ExchangeOnline
$start = (Get-Date).AddDays(-90).ToUniversalTime()
$end   = (Get-Date).ToUniversalTime()
$unmask = Search-UnifiedAuditLog -StartDate $start -EndDate $end -Operations 'InsiderRiskMgmtUserUnmasked' -ResultSize 5000
$unmask | ForEach-Object {
    $d = $_.AuditData | ConvertFrom-Json
    [pscustomobject]@{
        UtcWhen     = $_.CreationDate
        Investigator= $d.UserId
        CaseId      = $d.CaseId
        TargetHash  = (Get-FileHash -Algorithm SHA256 -InputObject ([IO.MemoryStream]::new([Text.Encoding]::UTF8.GetBytes($d.TargetUser)))).Hash
        Justification= $d.Justification
    }
}
```

3. Confirm each unmask event has a documented justification, ties to a specific case, and was performed by a member of `Insider Risk Management Investigators` (not catch-all).
4. Confirm jurisdictional pre-conditions (TC-13) for each unmask target.

#### Expected

- 100% of unmask events have justification + case binding + Investigator role + jurisdictional clearance.
- Pseudonymization remains default-on.

#### Evidence Capture

- `tc18-unmask-audit.csv` (with hashed target IDs), summary memo.
- Retention: 7 years.

#### Remediation

- Unmask without justification → halt; immediate Privacy Officer + GC review; report to CCO.

#### Regulatory tie-in

GLBA 501(b) · Reg S-P · State monitoring statutes · [Control 1.7](../../../controls/pillar-1-security/1.7-comprehensive-audit-logging-and-compliance.md).

---


### TC-19 · Sentinel UEBA correlation (KQL)
**Frequency:** Quarterly · **Owner:** SOC Analyst (Sentinel) + IRM Analyst · **Counter-signer:** CISO

#### Setup

- Microsoft Sentinel workspace ingests M365 Defender + Purview + Entra ID Protection connectors per [Control 3.9](../../../controls/pillar-3-reporting/3.9-microsoft-sentinel-integration.md).
- Operator: SOC Analyst (Sentinel Reader) + IRM Analyst.

#### Steps

1. Run the canonical correlation queries below over a 30-day window. Tag results with `(Get-MgContext).Environment` mapping.
2. For every IRM alert in the window, confirm at least one of: a corresponding Sentinel incident, a Sentinel hunting-query hit, or a documented benign-rationale memo.
3. For Entra Agent ID activity, confirm Sentinel UEBA enrichment is present per [Control 2.26](../../../controls/pillar-2-management/2.26-entra-agent-id-identity-governance.md).

```kql
// TC-19.A — IRM operations volume by day (last 30d)
OfficeActivity
| where TimeGenerated > ago(30d)
| where Operation startswith "InsiderRiskMgmt"
| summarize Events = count() by bin(TimeGenerated, 1d), Operation
| order by TimeGenerated desc
```

```kql
// TC-19.B — Forensic Evidence dual-auth chain (request → approval/denial)
OfficeActivity
| where TimeGenerated > ago(90d)
| where Operation in ("InsiderRiskMgmtForensicEvidenceCaptureRequested",
                      "InsiderRiskMgmtForensicEvidenceCaptureApproved",
                      "InsiderRiskMgmtForensicEvidenceCaptureDenied")
| extend CaseId = tostring(parse_json(AuditData).CaseId)
| summarize Events = make_set(Operation), Actors = make_set(UserId), When = make_set(TimeGenerated)
        by CaseId
| extend HasRequest  = set_has_element(Events, "InsiderRiskMgmtForensicEvidenceCaptureRequested")
| extend HasDecision = set_has_element(Events, "InsiderRiskMgmtForensicEvidenceCaptureApproved")
                   or set_has_element(Events, "InsiderRiskMgmtForensicEvidenceCaptureDenied")
| where HasRequest and HasDecision
| extend SoDOk = array_length(Actors) >= 2
| project CaseId, SoDOk, Actors, When
```

```kql
// TC-19.C — IRM ↔ Entra ID Protection user-risk join
let highRisk =
    SigninLogs
    | where TimeGenerated > ago(30d)
    | where RiskLevelDuringSignIn == "high" or RiskLevelAggregated == "high"
    | summarize by tolower(UserPrincipalName);
OfficeActivity
| where TimeGenerated > ago(30d)
| where Operation startswith "InsiderRiskMgmt"
| extend Upn = tolower(tostring(parse_json(AuditData).UserId))
| join kind=inner (highRisk) on $left.Upn == $right.UserPrincipalName
| summarize IRMEvents = count() by Upn, bin(TimeGenerated, 1d)
```

```kql
// TC-19.D — Entra Agent ID activity not yet correlated to an IRM alert (90d)
let agentSignals =
    AADNonInteractiveUserSignInLogs
    | where TimeGenerated > ago(90d)
    | where ServicePrincipalType == "AgentIdentity"   // adjust to the published field for your tenant
    | summarize by AgentId = tostring(ServicePrincipalId);
let irmAgents =
    OfficeActivity
    | where TimeGenerated > ago(90d)
    | where Operation startswith "InsiderRiskMgmt"
    | extend AgentRef = tostring(parse_json(AuditData).AgentId)
    | where isnotempty(AgentRef)
    | summarize by AgentRef;
agentSignals
| join kind=leftanti (irmAgents) on $left.AgentId == $right.AgentRef
| project AgentId
```

```kql
// TC-19.E — Pseudonymization unmask audit-rate
OfficeActivity
| where TimeGenerated > ago(90d)
| where Operation == "InsiderRiskMgmtUserUnmasked"
| summarize Unmasks = count(),
            UniqueInvestigators = dcount(UserId),
            Cases = dcount(tostring(parse_json(AuditData).CaseId))
| extend AvgUnmasksPerCase = todouble(Unmasks) / todouble(Cases)
```

#### Expected

- Every IRM alert in window has a corresponding Sentinel artefact OR documented benign rationale.
- TC-19.B returns SoD `true` for every Forensic Evidence case.
- TC-19.D returns an empty set OR a documented exception.

#### Evidence Capture

- `tc19-{query}.csv` per query, plus the JSON evidence record with the workspace ID + run ID.
- Retention: 7 years.

#### Remediation

- Sentinel artefact missing → SOC follow-up; potentially add a hunting query / detection rule per [`troubleshooting.md` §19](troubleshooting.md).
- TC-19.B SoD `false` → halt all Forensic Evidence captures; investigate role-group integrity.

#### Regulatory tie-in

NYDFS 500.06 / 500.16 · FFIEC · [Control 2.26](../../../controls/pillar-2-management/2.26-entra-agent-id-identity-governance.md) · [Control 3.9](../../../controls/pillar-3-reporting/3.9-microsoft-sentinel-integration.md).

---

### TC-20 · Sovereign compensating-control exercise
**Frequency:** Quarterly (GCC / GCC High / DoD only) · **Owner:** CISO + CCO · **Counter-signer:** GC, AI Governance Lead

#### Setup

- Required for any TC marked `NotApplicable — Sovereign Exception #N` in the current cycle.
- Operator: CISO + CCO + GC + AI Governance Lead.

#### Steps

For each sovereign exception, document and exercise the compensating control. Canonical mapping:

| Sovereign exception | Compensating control |
|---|---|
| Adaptive Protection (TC-15) N/A | Static Conditional Access policy bound to documented priority-user risk groups + manual analyst escalation procedure with documented SLA + quarterly outcome review. |
| Risky AI usage (TC-5) limited / N/A | DLP + Purview audit + manual sample-based prompt review by AI Governance Lead (sandbox-only). |
| Risky browser usage (TC-9) N/A | DLP + endpoint AV / EDR controls + browser ADMX hardening + analyst sample review. |
| Triage Agent (TC-14) limited | Manual analyst triage SLA documented in WSP; OCC 2011-12 model-monitoring evidence assembled by hand each cycle. |
| Forensic Evidence (TC-12) limited | Documented sovereign-friendly evidence procedure (e.g., MDE Live Response with dual-auth + WORM evidence store). |
| Defender for Cloud Apps dynamic threat detection (TC-10) N/A | Static MDA policies + manual anomaly review on quarterly cadence. |

For each entry, the exercise:

1. Documents the sovereign-exception register entry (cloud, capability, Microsoft Learn link, date verified).
2. Exercises the compensating control end-to-end (test alert / test policy / sample review) and produces a structured evidence record.
3. Files the exercise outcome with CCO + CISO sign-off.

#### Expected

- Every active sovereign exception has a current (≤ 90-day) compensating-control exercise on file.
- Exception register matches Microsoft Learn current state (re-verified each cycle).

#### Evidence Capture

- `tc20-exception-register.yaml` (versioned).
- `tc20-exercise-{exception}.json` per exception.
- `tc20-attestation-{quarter}.pdf` (signed by CISO + CCO + GC + AI Governance Lead).
- Retention: 7 years.

#### Remediation

- Stale exception (> 90 days without exercise) → freeze the affected workload (scope-out IRM-dependent operations) until the exercise completes.
- Microsoft Learn now reports parity → close the exception via change ticket; restore the corresponding TC to in-scope status.

#### Regulatory tie-in

FINRA 4511 (defensible evidence) · OCC 2011-12 (compensating-control documentation) · sovereign-cloud exception register.

---

### TC-21 · SOX 404 IRM self-assessment
**Frequency:** Annually · **Owner:** CCO + Internal Audit · **Counter-signer:** CISO, GC, Audit Committee

#### Setup

- Annual self-assessment supports SOX §§302 / 404 internal-control over financial reporting (ICFR) where IRM is part of the firm's anti-fraud / data-handling control set.
- Operator: CCO + Internal Audit + control owners (Purview Compliance Admin, AI Governance Lead, Privacy Officer, GC).

#### Steps

1. Compile the year's TC-1 through TC-20 evidence packages.
2. Score each control against the firm's ICFR rubric: Designed-effectively / Operating-effectively / Deficient / Material weakness.
3. Run a tabletop test of three FSI scenarios end-to-end:
   - Front-office data theft by a departing wealth advisor.
   - Trader prompt-leak via Copilot agent into an unsanctioned destination.
   - Insider abuse of supervisory tooling (e.g., catch-all role group repopulated).
4. Audit-Committee review and sign-off.

#### Expected

- Self-assessment memo produced, scored, and signed.
- Tabletop scenarios executed with after-action memos.
- Material weaknesses (if any) reported per the firm's escalation policy.

#### Evidence Capture

- `tc21-soa-{year}.pdf` (self-assessment).
- `tc21-tabletop-{year}-{scenario}.pdf`.
- Retention: 7 years.

#### Remediation

- Material weakness identified → remediation plan with target dates; Audit-Committee monitoring cadence.

#### Regulatory tie-in

SOX §§302 / 404 · OCC 2011-12 · NYDFS 500.06 · [Control 2.6](../../../controls/pillar-2-management/2.6-model-risk-management-alignment-with-occ-2011-12-sr-11-7.md).

---

### TC-22 · Examination evidence-pack pull-test
**Frequency:** Annually + on-examiner-request · **Owner:** CCO · **Counter-signer:** Internal Audit, GC

#### Setup

- The pull-test confirms that, on-demand, the firm can assemble the IRM evidence pack a regulator (FINRA / SEC / OCC / Federal Reserve / NYDFS) would request without ad-hoc effort.
- Operator: CCO + Internal Audit + records-management custodian.

#### Steps

1. Pick two random 90-day windows in the prior 12 months.
2. For each window, assemble the canonical evidence pack:
   - TC-1 weekly UAL attestations (≥ 12 records).
   - TC-2 quarterly role-SoD attestation.
   - TC-3 quarterly indicator-baseline attestation.
   - TC-4–TC-11 monthly / quarterly attestations as applicable.
   - TC-12 per-capture records for any Forensic Evidence captures in window.
   - TC-13 jurisdiction matrix in effect during window.
   - TC-17 escalation-sample CSV.
   - TC-18 unmask-audit CSV.
   - TC-19 Sentinel KQL outputs.
   - TC-20 sovereign-exception exercises (if applicable).
3. Verify all artifacts resolve from the WORM store with intact `.sha256` sidecars and integrity check passes.
4. Time the assembly: target ≤ 48h end-to-end (firm-defined SLA).

#### Expected

- 100% of artifacts resolve, sidecars verify, assembly within SLA.
- Any gap is treated as a records-handling deficiency under FINRA 4511 / SEC 17a-4(f) and routed to remediation.

#### Evidence Capture

- `tc22-pulltest-{window}.json` (artefact list + hash verification + assembly elapsed time).
- `tc22-attestation-{year}.pdf` signed by CCO, Internal Audit, GC.
- Retention: 7 years.

#### Remediation

- Missing / corrupt artefact → records-management incident; root-cause within 14 days; report to Audit Committee.
- Assembly time > SLA → process-engineering review.

#### Regulatory tie-in

FINRA 4511 · SEC 17a-4(f) · Reg S-P · OCC examination expectations · NYDFS 500.06.

---

## §3 Evidence Capture canonical mapping

| TC | Artefact filename pattern | Storage tier | Retention | Primary regulation tie-in |
|---|---|---|---|---|
| TC-1 | `tc01-ual-state.json` (+ `.sha256`) | WORM | 7 years | FINRA 4511 · SEC 17a-4(f) |
| TC-2 | `tc02-roles.json`, `tc02-sod.json` | WORM | 7 years | FINRA 3110 · SOX 404 · NYDFS 500.07 |
| TC-3 | `tc03-indicators-export.csv`, `tc03-indicators-diff.json`, `tc03-attestation.pdf` | WORM | 7 years | FINRA 3110 · OCC 2011-12 |
| TC-4 | `tc04-risky-agents-policy.json`, `tc04-agent-reconciliation.csv` | WORM | 7 years | FINRA 25-07 (RFC) · OCC 2011-12 |
| TC-5 | `tc05-policy.json`, `tc05-extension-coverage.csv`, `tc05-walkthrough-alert.json` | WORM | 7 years | FINRA 25-07 (RFC) · GLBA 501(b) |
| TC-6 | `tc06-hr-connector.json`, `tc06-hr-vs-irm-drift.csv` | WORM | 7 years | FINRA 3110 · Reg S-P 2024 · GLBA 501(b) |
| TC-7 | `tc07-priority-groups.json`, `tc07-priority-policy.json` | WORM | 7 years | FINRA 3110 · GLBA 501(b) · Reg S-P |
| TC-8 | `tc08-mde-connector.json` (+ coverage + correlation CSVs) | WORM | 7 years | FFIEC · NYDFS 500.06 |
| TC-9 | `tc09-policy.json`, `tc09-walkthrough.json` | WORM | 7 years | FINRA 3110 · GLBA 501(b) · Reg S-P |
| TC-10 | `tc10-mda-irm-correlation.csv`, `tc10-model-state.json` | WORM | 7 years | FINRA 4511 · GLBA 501(b) |
| TC-11 | `tc11-risky-users.json`, `tc11-correlation.csv` | WORM | 7 years | NYDFS 500.06 / 500.12 |
| TC-12 | `tc12-fe-quarterly.json`, `tc12-fe-per-capture-{caseId}.json`, `tc12-fe-decision-{caseId}.json` | WORM (+ legal-hold preservation where applicable) | Per legal hold; else 7 years for **decision metadata** | SEC 17a-4(b) · FINRA 4511 · GLBA 501(b) · State monitoring statutes |
| TC-13 | `tc13-jurisdiction-matrix.yaml`, `tc13-attestation-{year}.pdf` | WORM | 7 years | State monitoring statutes · GLBA 501(b) |
| TC-14 | `tc14-triage-state.json`, `tc14-fidelity-sample.csv`, `tc14-attestation.pdf` | WORM | 7 years | OCC 2011-12 / SR 11-7 · FINRA 25-07 (RFC) |
| TC-15 | `tc15-adaptive-bindings.json`, sample-set CSV, sovereign-exception record | WORM | 7 years | OCC 2011-12 · GLBA 501(b) |
| TC-16 | `tc16-cc-irm-correlation.csv`, `tc16-supervisory-tieout.csv` | WORM | 7 years | FINRA 3110 · FINRA 4511 |
| TC-17 | `tc17-escalation-sample.csv`, `tc17-tabletop-{quarter}.pdf` | WORM | 7 years | NYDFS 500.17(a) · Reg S-P 2024 · FINRA 3110 |
| TC-18 | `tc18-unmask-audit.csv` (hashed target IDs) | WORM | 7 years | GLBA 501(b) · Reg S-P · State statutes |
| TC-19 | `tc19-{query}.csv` per KQL query | WORM | 7 years | NYDFS 500.06 / 500.16 · FFIEC |
| TC-20 | `tc20-exception-register.yaml`, `tc20-exercise-{exception}.json`, `tc20-attestation-{quarter}.pdf` | WORM | 7 years | FINRA 4511 · OCC 2011-12 |
| TC-21 | `tc21-soa-{year}.pdf`, `tc21-tabletop-{year}-{scenario}.pdf` | WORM | 7 years | SOX §§302 / 404 · OCC 2011-12 |
| TC-22 | `tc22-pulltest-{window}.json`, `tc22-attestation-{year}.pdf` | WORM | 7 years | FINRA 4511 · SEC 17a-4(f) · Reg S-P |

> **Two-tier retention reminder.** The **operational** tier (working window 1–2 years) is for live triage and analyst handoff; the **records-scope** tier above (7 years on WORM with `deletionLocked = true` retention labels) is for examination-ready evidence. **Forensic Evidence clip media** themselves remain on the Microsoft 120-day clip-deletion ceiling unless exported under legal hold — only the **decision metadata** records-tier-retains.

---

## §4 Annual attestation and sign-off

### §4.1 Annual program attestation

The following officers sign the annual IRM program attestation:

| Officer (canonical) | Scope of attestation |
|---|---|
| Chief Compliance Officer (CCO) | Program-level effectiveness; FINRA 3110 / 4511 / Reg S-P / NYDFS 500 readiness; books-and-records integrity for IRM evidence. |
| Chief Information Security Officer (CISO) | Technical control state across TC-1 → TC-20; sovereign-exception register accuracy; Sentinel correlation health (TC-19). |
| Privacy Officer | Pseudonymization integrity (TC-18); state-law jurisdiction matrix (TC-13); employee-notice mechanism operating. |
| General Counsel (GC) | Legal interpretation of state monitoring statutes; Forensic Evidence dual-auth chain (TC-12); legal-hold preservation paths. |
| AI Governance Lead | Risky Agents / Risky AI usage policy posture (TC-4 / TC-5); Triage Agent fidelity (TC-14); model-risk alignment with OCC 2011-12 / SR 11-7. |
| Internal Audit | Independent verification of evidence integrity and SoD; pull-test results (TC-22); SOX 404 self-assessment (TC-21). |
| Audit Committee Chair | Acceptance of self-assessment memo and remediation plan (TC-21). |

### §4.2 Per-incident sign-off

For every high-severity incident touching the 72-hour clocks (NYDFS 500.17(a) / Reg S-P 2024), the per-incident memo records:

1. Detection timestamp (UTC) and the IRM alert / case ID.
2. CCO disposition (in-scope vs. out-of-scope of the 72-hour clock) with rationale.
3. GC review of state-monitoring-law implications (where Forensic Evidence or unmask was invoked).
4. CISO sign-off on technical containment.
5. Regulator-notification draft and submission references (where in-scope).
6. Hash + WORM-storage reference to the assembled TC-22 sub-pack supporting the incident.

### §4.3 Cycle close

- Run identifier `IRM112-yyyyMMdd-HHmmss-<8charGuid>` archived.
- All TC artefacts hash-verified and resolved from WORM.
- Sovereign-exception register reviewed and updated against Microsoft Learn.
- Indicator baseline diff (TC-3) reviewed; any approved drift incorporated into `governance/irm-indicators/baseline.yaml` under change control.
- Next-cycle calendar items scheduled (weekly TC-1, monthly TC-4 → TC-9, quarterly TC-2 / TC-3 / TC-10 → TC-19 / TC-20, annual TC-21 / TC-22).

### §4.4 Cross-references (canonical)

- [Control 1.5 — Data Loss Prevention and Sensitivity Labels](../../../controls/pillar-1-security/1.5-data-loss-prevention-dlp-and-sensitivity-labels.md)
- [Control 1.6 — Microsoft Purview DSPM for AI](../../../controls/pillar-1-security/1.6-microsoft-purview-dspm-for-ai.md)
- [Control 1.7 — Comprehensive Audit Logging and Compliance](../../../controls/pillar-1-security/1.7-comprehensive-audit-logging-and-compliance.md)
- [Control 1.9 — Data Retention and Deletion Policies](../../../controls/pillar-1-security/1.9-data-retention-and-deletion-policies.md)
- [Control 1.10 — Communication Compliance Monitoring](../../../controls/pillar-1-security/1.10-communication-compliance-monitoring.md)
- [Control 1.13 — Sensitive Information Types and Pattern Recognition](../../../controls/pillar-1-security/1.13-sensitive-information-types-sits-and-pattern-recognition.md)
- [Control 1.19 — eDiscovery for Agent Interactions](../../../controls/pillar-1-security/1.19-ediscovery-for-agent-interactions.md)
- [Control 2.6 — Model Risk Management Alignment with OCC 2011-12 / SR 11-7](../../../controls/pillar-2-management/2.6-model-risk-management-alignment-with-occ-2011-12-sr-11-7.md)
- [Control 2.12 — Supervisory Review and Attestation](../../../controls/pillar-2-management/2.12-supervision-and-oversight-finra-rule-3110.md)
- [Control 2.26 — Entra Agent ID Identity Governance](../../../controls/pillar-2-management/2.26-entra-agent-id-identity-governance.md)
- [Control 3.1 — Agent Inventory and Metadata Management](../../../controls/pillar-3-reporting/3.1-agent-inventory-and-metadata-management.md)
- [Control 3.9 — Microsoft Sentinel Integration](../../../controls/pillar-3-reporting/3.9-microsoft-sentinel-integration.md)

### §4.5 Sister playbooks

- [Portal Walkthrough](portal-walkthrough.md)
- [PowerShell Setup](powershell-setup.md)
- [Troubleshooting](troubleshooting.md)
- [PowerShell Authoring Baseline](../../_shared/powershell-baseline.md)

---

---

## §5 Appendices

### §5.1 Appendix A — Canonical evidence schema

Every TC emits a JSON evidence record that conforms to this schema (firm-defined; not Microsoft-published):

```json
{
  "$schema": "urn:fsi-agentgov:irm-evidence:v1",
  "RunId": "IRM112-20260415-093215-3a2f9c8e",
  "ControlId": "1.12",
  "TestCaseId": "TC-12",
  "TestCaseTitle": "Forensic Evidence dual-authorization",
  "Frequency": "QuarterlyAndPerCapture",
  "UtcExecutionStart": "2026-04-15T09:32:15Z",
  "UtcExecutionEnd": "2026-04-15T09:34:02Z",
  "Sovereign": {
    "GraphEnvironment": "Global",
    "Cloud": "Commercial",
    "AdaptiveProtectionInScope": true,
    "ForensicEvidenceInScope": true,
    "TriageAgentInScope": true,
    "RiskyBrowserUsageInScope": true
  },
  "Operator": {
    "PrincipalUpnHash": "sha256:5f1d…",
    "RoleGroups": ["Insider Risk Management Investigators"],
    "WorkstationHostHash": "sha256:0c8a…"
  },
  "Result": "Pass",
  "Findings": [],
  "Artefacts": [
    {
      "Path": "tc12-fe-quarterly.json",
      "Sha256": "f2c8…",
      "Bytes": 4821,
      "RetentionLabel": "IRM-EvidenceLock-7y"
    }
  ],
  "RelatedControls": ["1.5","1.6","1.7","1.9","1.10","1.13","1.19","2.6","2.12","2.26","3.1","3.9"],
  "RegulatoryTieIn": ["FINRA-4511","SEC-17a-4(b)","GLBA-501(b)","StateMonitoringStatutes-CT-DE-NY"],
  "SchemaVersion": "v1"
}
```

Schema rules:

- `RunId` MUST follow `IRM112-yyyyMMdd-HHmmss-<8charGuid>`.
- `UtcExecutionStart` and `UtcExecutionEnd` MUST be ISO 8601 in UTC.
- `Result` ∈ {`Pass`, `Fail`, `NotApplicable`, `Skipped`}; `NotApplicable` and `Skipped` MUST include a `Reason` field referencing the sovereign-exception register entry where applicable.
- `Operator.PrincipalUpnHash` is SHA-256 over the lower-cased UPN to support pseudonymization at the evidence layer.
- `Artefacts[].Sha256` MUST match the `.sha256` sidecar contents (verified at TC-22 pull-test).

### §5.2 Appendix B — Sovereign exception register template

`governance/sovereign-exceptions.yaml`:

```yaml
schemaVersion: v1
controlId: "1.12"
lastReviewedUtc: "2026-04-15T00:00:00Z"
exceptions:
  - id: "SOV-15"
    capability: "Adaptive Protection"
    affectedClouds: ["GCC", "GCC High", "DoD"]
    learnReference: "https://learn.microsoft.com/…/adaptive-protection"
    learnVerifiedUtc: "2026-04-12T00:00:00Z"
    compensatingControlId: "TC-20-AdaptiveProtection-Static-CA"
    lastExerciseUtc: "2026-04-14T00:00:00Z"
    nextExerciseDueUtc: "2026-07-13T00:00:00Z"
    owner: "CISO"
    counterSigner: "CCO"
  - id: "SOV-09"
    capability: "Risky browser usage"
    affectedClouds: ["GCC", "GCC High", "DoD"]
    learnReference: "https://learn.microsoft.com/…/risky-browser-usage"
    learnVerifiedUtc: "2026-04-12T00:00:00Z"
    compensatingControlId: "TC-20-RiskyBrowser-DLP-Hardening"
    lastExerciseUtc: "2026-04-14T00:00:00Z"
    nextExerciseDueUtc: "2026-07-13T00:00:00Z"
    owner: "AI Governance Lead"
    counterSigner: "CISO"
```

The register is **versioned in source control** so that historical examination questions ("what was the sovereign-exception posture in Q3-2025?") can be answered by checkout.

### §5.3 Appendix C — Indicator baseline excerpt (`baseline.yaml`)

```yaml
schemaVersion: v1
controlId: "1.12"
baselineId: "FSI-IRM-Baseline-2026.04"
office:
  downloadFromSensitiveSite: { enabled: true, weight: high }
  printFromSensitiveSite:    { enabled: true, weight: high }
  copyToUsb:                 { enabled: true, weight: high }
  copyToNetworkShare:        { enabled: true, weight: medium }
  copyToClipboardFromSensitive: { enabled: true, weight: medium }
device:
  fileActivityByDevice:      { enabled: true, weight: medium }
  browserExfil:              { enabled: true, weight: high }
mde:
  securityViolation:         { enabled: true, weight: high }
  avDetection:               { enabled: true, weight: medium }
  appLockerOrWdacBlock:      { enabled: true, weight: medium }
ai:
  riskyAiUsage:              { enabled: true, weight: high }
  riskyAgentActivity:        { enabled: true, weight: high }
  riskyBrowserUsage:         { enabled: true, weight: high }
healthcarePharma:
  enabled: false   # FSI tenant — disabled per WSP
priorityUserGroups:
  - "FSI-Traders"
  - "FSI-InvestmentBankers"
  - "FSI-ResearchAnalysts"
  - "FSI-WealthAdvisors"
  - "FSI-BranchSupervisors"
  - "FSI-LoanOfficers"
  - "FSI-ClientService"
  - "FSI-PrivilegedAdmins"
```

### §5.4 Appendix D — Pester scaffolding skeleton

```powershell
#Requires -Version 7.4
#Requires -Modules @{ModuleName='Pester'; ModuleVersion='5.5.0'}

BeforeAll {
    $script:RunId = "IRM112-$(Get-Date -AsUTC -Format 'yyyyMMdd-HHmmss')-$([Guid]::NewGuid().ToString('N').Substring(0,8))"
    $script:Sov   = Test-Agt112SovereignTenant -RunId $script:RunId
}

Describe 'Control 1.12 · Verification (read-only)' {

    Context 'PRE gates' {
        It 'PRE-1 PowerShell baseline'   { $PSVersionTable.PSVersion.Major | Should -BeGreaterOrEqual 7 }
        It 'PRE-3 Sovereign tag known'  { $script:Sov.SovereignCloud | Should -Not -Be 'Unknown' }
        It 'PRE-6 Pseudonymization on'  { (Get-InsiderRiskTenantSettings).PseudonymizationEnabled | Should -BeTrue }
        It 'PRE-7 UAL ingestion on'     { (Get-AdminAuditLogConfig).UnifiedAuditLogIngestionEnabled | Should -BeTrue }
    }

    Context 'TC-2 Role SoD' {
        It 'Catch-all role group is empty' {
            (Get-RoleGroupMember -Identity 'Insider Risk Management').Count | Should -Be 0
        }
        It 'Investigator ↔ Approver overlap is empty' {
            $inv = (Get-RoleGroupMember -Identity 'Insider Risk Management Investigators').Name
            $apv = (Get-RoleGroupMember -Identity 'Insider Risk Management Approvers').Name
            ($inv | Where-Object { $apv -contains $_ }).Count | Should -Be 0
        }
    }

    Context 'TC-12 Forensic Evidence audit chain' {
        It 'Both request and decision operations emit in 90-day window' {
            $start = (Get-Date).AddDays(-90).ToUniversalTime()
            $end   = (Get-Date).ToUniversalTime()
            $ops = 'InsiderRiskMgmtForensicEvidenceCaptureRequested',
                   'InsiderRiskMgmtForensicEvidenceCaptureApproved',
                   'InsiderRiskMgmtForensicEvidenceCaptureDenied'
            $hits = Search-UnifiedAuditLog -StartDate $start -EndDate $end -Operations $ops -ResultSize 5000
            # If any captures occurred, request + decision pairs must be balanced per case
            ($hits | Group-Object { ($_.AuditData | ConvertFrom-Json).CaseId } | ForEach-Object {
                $ops = $_.Group | ForEach-Object { $_.Operations }
                ($ops -contains 'InsiderRiskMgmtForensicEvidenceCaptureRequested') -and
                ((($ops -contains 'InsiderRiskMgmtForensicEvidenceCaptureApproved') -or
                  ($ops -contains 'InsiderRiskMgmtForensicEvidenceCaptureDenied')))
            }) | Should -Not -Contain $false
        }
    }
}

AfterAll {
    # Emit canonical evidence record per Appendix A schema
    # …
}
```

### §5.5 Appendix E — TC-to-regulation matrix

| Regulation | TCs that primarily evidence it |
|---|---|
| FINRA Rule 3110 (Supervision) | TC-2, TC-3, TC-6, TC-7, TC-9, TC-16, TC-17 |
| FINRA Rule 4511 (Books and Records) | TC-1, TC-10, TC-12, TC-16, TC-20, TC-22 |
| FINRA Regulatory Notice 21-18 | TC-1, TC-12, TC-22 (cloud-hosted records stewardship context) |
| FINRA Regulatory Notice 25-07 (RFC) | TC-4, TC-5, TC-14, TC-16 (AI-supervision context; not yet binding) |
| SEC Rule 17a-3 / 17a-4 | TC-1, TC-12, TC-22 |
| SEC Reg S-P (2024 amendments) | TC-6, TC-7, TC-9, TC-17, TC-18, TC-22 |
| GLBA §501(b) (Safeguards Rule) | TC-5, TC-6, TC-7, TC-9, TC-10, TC-13, TC-15, TC-18 |
| SOX §§302 / 404 | TC-2, TC-21 |
| OCC Bulletin 2011-12 / Federal Reserve SR 11-7 | TC-3, TC-4, TC-14, TC-15, TC-20, TC-21 |
| CFTC Regulation 1.31 | TC-1, TC-12, TC-22 (records preservation context) |
| NYDFS 23 NYCRR 500.06 | TC-1, TC-8, TC-10, TC-11, TC-13, TC-19, TC-21, TC-22 |
| NYDFS 23 NYCRR 500.16 | TC-19 |
| NYDFS 23 NYCRR 500.17(a) (72-hour) | TC-17 |
| FFIEC IT Examination Handbook | TC-8, TC-11, TC-19 |
| State employee-monitoring statutes (CT §31-48d, DE Title 19 §705, NY Civil Rights Law §52-bis) | TC-12 (gating), TC-13 (primary), TC-18 (operational) |

### §5.6 Appendix F — Glossary (subset)

| Term | Meaning |
|---|---|
| Adaptive Protection | IRM capability that links risk levels to dynamic enforcement in DLP / Conditional Access / DLM. **N/A in GCC / GCC High / DoD** as of April 2026. |
| Catch-all role group | The default `Insider Risk Management` role group; bundles all permissions and is **prohibited** in regulated FSI tenants. |
| Forensic Evidence | IRM screen-recording capability; PAYG-billed; 120-day clip auto-delete; dual-authorization. **Investigative**, not records-tier. |
| HR connector | Purview connector that ingests `EmployeeID`, `ResignationDate`, `LastWorkingDate` for the departing-user template. |
| IRM Approver | Member of `Insider Risk Management Approvers`; approves Forensic Evidence captures; **must not** overlap with Investigators. |
| IRM Investigator | Member of `Insider Risk Management Investigators`; requests Forensic Evidence captures and performs unmask actions. |
| Pseudonymization | Default-on IRM behaviour that masks user identifiers in alerts and cases; unmask is restricted to Investigators and audited. |
| Priority user group | Firm-defined dynamic group of higher-risk roles (e.g., traders, wealth advisors) with bespoke IRM policies. |
| Risky Agents | Default-applied IRM policy template covering Microsoft 365 Copilot, Copilot Studio, and Foundry agents. |
| Risky AI usage | IRM policy template covering AI prompt categories; depends on Edge / Chrome browser extension; **Windows-only**. |
| Risky browser usage | IRM policy template covering risky browsing categories; same extension dependency. |
| Run identifier | `IRM112-yyyyMMdd-HHmmss-<8charGuid>`; binds all evidence in a verification cycle. |
| Saved-auth refresh (Triage Agent) | 90-day refresh requirement for Security Copilot Triage Agent saved authentication and configuration. |
| Sovereign exception | Documented gap between commercial and a sovereign cloud, with compensating-control evidence (TC-20). |
| Triage Agent | Security Copilot agent that triages IRM alerts; depends on SCU + PAYG; decision-support, not supervisory decision-maker. |
| WORM | Write-Once-Read-Many storage tier supporting `deletionLocked = true` retention labels. |

### §5.7 Appendix G — Examiner-facing crib sheet

For the CCO presenting to a regulator, the answer to "show me your IRM evidence" is the following six-question rubric:

1. **Where are policies authored and who approved them?** → TC-3 baseline + RFC trail.
2. **How do you know IRM is producing a defensible audit trail?** → TC-1 weekly attestation + WORM 7-year retention.
3. **How do you prevent abuse of the IRM tool itself?** → TC-2 SoD + TC-18 unmask gate.
4. **How do you handle Forensic Evidence under state law?** → TC-12 dual-auth + TC-13 jurisdiction matrix.
5. **How do you tie IRM to your supervisory program?** → TC-16 CC correlation + TC-17 escalation chain (72-hour clocks).
6. **How is your AI / agent surface governed?** → TC-4 / TC-5 / TC-14 + Control 2.6 (model-risk) + Control 2.26 (agent identity).

### §5.8 Appendix H — Out-of-scope clarifications

- **Books-and-records retention** is implemented under [Control 1.9](../../../controls/pillar-1-security/1.9-data-retention-and-deletion-policies.md) and [Control 1.7](../../../controls/pillar-1-security/1.7-comprehensive-audit-logging-and-compliance.md), not by IRM or Forensic Evidence.
- **DLP authoring** is implemented under [Control 1.5](../../../controls/pillar-1-security/1.5-data-loss-prevention-dlp-and-sensitivity-labels.md). IRM consumes DLP signals; it does not author DLP.
- **Sensitive Information Type authoring** is implemented under [Control 1.13](../../../controls/pillar-1-security/1.13-sensitive-information-types-sits-and-pattern-recognition.md).
- **eDiscovery preservation paths** for IRM cases routed to legal hold are implemented under [Control 1.19](../../../controls/pillar-1-security/1.19-ediscovery-for-agent-interactions.md).
- **Communication Compliance authoring** is implemented under [Control 1.10](../../../controls/pillar-1-security/1.10-communication-compliance-monitoring.md). TC-16 is the IRM-to-CC correlation, not a CC authoring procedure.
- **Supervisory review attestation** is implemented under [Control 2.12](../../../controls/pillar-2-management/2.12-supervision-and-oversight-finra-rule-3110.md).
- **Model-risk governance** for IRM analytics models, the Triage Agent, and Adaptive Protection is implemented under [Control 2.6](../../../controls/pillar-2-management/2.6-model-risk-management-alignment-with-occ-2011-12-sr-11-7.md).
- **Agent identity, lifecycle, and risk telemetry** are implemented under [Control 2.26](../../../controls/pillar-2-management/2.26-entra-agent-id-identity-governance.md).
- **Agent inventory** is implemented under [Control 3.1](../../../controls/pillar-3-reporting/3.1-agent-inventory-and-metadata-management.md).
- **Sentinel workspace authoring and detection-rule lifecycle** are implemented under [Control 3.9](../../../controls/pillar-3-reporting/3.9-microsoft-sentinel-integration.md). The KQL in TC-19 is read-only verification, not detection-rule authoring.

### §5.9 Appendix I — Change-log discipline

Any modification to this verification catalogue requires:

1. Pull-request with two reviewers (Purview Compliance Admin + CCO at minimum).
2. `mkdocs build --strict` clean build.
3. `python scripts/verify_controls.py` clean.
4. Cross-reference integrity (every `../../../controls/pillar-N-…` link resolves).
5. Footer version bump (e.g., v1.4 → v1.5) with `Updated:` date.
6. Re-run of TC-22 pull-test against the updated catalogue with archived evidence to confirm assembly continues to meet SLA.

---

### §5.10 Appendix J — Extended KQL hunting library

The queries below extend TC-19 with additional hunting patterns the SOC may schedule independently. They are **hunting-tier** (not detection rules) and are referenced by the TC-19 evidence record where the SOC Analyst includes them in the cycle.

```kql
// J.1 — IRM cases opened but not advanced beyond Triage in 14 days
let triaged =
    OfficeActivity
    | where TimeGenerated > ago(60d)
    | where Operation == "InsiderRiskMgmtCaseCreated"
    | extend CaseId = tostring(parse_json(AuditData).CaseId)
    | summarize Created = min(TimeGenerated) by CaseId;
let advanced =
    OfficeActivity
    | where TimeGenerated > ago(60d)
    | where Operation in ("InsiderRiskMgmtCaseResolved","InsiderRiskMgmtCaseEscalated")
    | extend CaseId = tostring(parse_json(AuditData).CaseId)
    | summarize Advanced = min(TimeGenerated) by CaseId;
triaged
| join kind=leftouter (advanced) on CaseId
| extend AgeDays = datetime_diff('day', coalesce(Advanced, now()), Created)
| where isnull(Advanced) and AgeDays >= 14
| project CaseId, Created, AgeDays
```

```kql
// J.2 — Investigator unmask velocity (per-investigator daily rate)
OfficeActivity
| where TimeGenerated > ago(90d)
| where Operation == "InsiderRiskMgmtUserUnmasked"
| extend Investigator = tostring(parse_json(AuditData).UserId)
| summarize Unmasks = count() by Investigator, bin(TimeGenerated, 1d)
| summarize MaxDailyUnmasks = max(Unmasks), AvgDailyUnmasks = avg(Unmasks) by Investigator
| order by MaxDailyUnmasks desc
```

```kql
// J.3 — Forensic Evidence captures approved without a recent TC-13 jurisdiction reference (90d)
// Requires the firm-published `TC13Jurisdictions_CL` custom log table populated by the
// Privacy Officer's pipeline. Returns approvals lacking a jurisdiction reference within 365d.
let approvals =
    OfficeActivity
    | where TimeGenerated > ago(90d)
    | where Operation == "InsiderRiskMgmtForensicEvidenceCaptureApproved"
    | extend CaseId = tostring(parse_json(AuditData).CaseId),
             Jurisdiction = tostring(parse_json(AuditData).Jurisdiction);
let jurisdictions =
    TC13Jurisdictions_CL
    | where TimeGenerated > ago(365d)
    | summarize LastRef = max(TimeGenerated) by Jurisdiction = JurisdictionCode_s;
approvals
| join kind=leftouter (jurisdictions) on Jurisdiction
| where isnull(LastRef)
| project CaseId, Jurisdiction
```

```kql
// J.4 — Risky Agents alert volume by Entra Agent ID (90d) — agent-level fairness/false-positive lens
OfficeActivity
| where TimeGenerated > ago(90d)
| where Operation startswith "InsiderRiskMgmt"
| extend AgentId = tostring(parse_json(AuditData).AgentId), AlertId = tostring(parse_json(AuditData).AlertId)
| where isnotempty(AgentId)
| summarize Alerts = dcount(AlertId) by AgentId
| order by Alerts desc
```

```kql
// J.5 — Adaptive Protection band-transition cardinality (commercial only)
// Read-only count of users transitioning into Elevated within 30d
OfficeActivity
| where TimeGenerated > ago(30d)
| where Operation == "InsiderRiskMgmtAdaptiveProtectionBandChanged"
| extend NewBand = tostring(parse_json(AuditData).NewBand),
         User = tostring(parse_json(AuditData).UserId)
| where NewBand == "Elevated"
| summarize Users = dcount(User), Transitions = count()
```

```kql
// J.6 — Triage Agent agreement-rate vs. analyst final disposition (sample)
let agentRecs =
    OfficeActivity
    | where TimeGenerated > ago(30d)
    | where Operation == "InsiderRiskMgmtTriageAgentRecommendation"
    | extend AlertId = tostring(parse_json(AuditData).AlertId),
             AgentRec = tostring(parse_json(AuditData).Recommendation);
let analystDisp =
    OfficeActivity
    | where TimeGenerated > ago(30d)
    | where Operation == "InsiderRiskMgmtAlertUpdated"
    | extend AlertId = tostring(parse_json(AuditData).AlertId),
             Disposition = tostring(parse_json(AuditData).Disposition);
agentRecs
| join kind=inner (analystDisp) on AlertId
| extend Agreement = iff(AgentRec == Disposition, 1, 0)
| summarize Total = count(), Agree = sum(Agreement), AgreementRate = todouble(sum(Agreement)) / todouble(count())
```

> **Hunting-tier note.** Operation names in the above queries reflect commercial-cloud OfficeActivity emissions as observed in the April 2026 cycle. Sovereign cloud emission names may differ; verify against your tenant's Sentinel ingestion before scheduling.

### §5.11 Appendix K — Operational dashboards reference

The firm publishes the following IRM dashboards (Power BI / Sentinel Workbooks). They are **operational-tier** (consumption views), not records-tier evidence:

| Dashboard | Audience | Refresh | Source |
|---|---|---|---|
| IRM Health (UAL ingest, connector state, policy state) | CISO, Purview Compliance Admin | Hourly | Sentinel + Purview |
| IRM Alert / Case Volumetrics | CCO, IRM Analyst | Daily | Sentinel |
| Forensic Evidence Capture Ledger | GC, Privacy Officer, IRM Approver | On-event | Sentinel |
| Sovereign Exception Posture | CISO, CCO | Daily | `governance/sovereign-exceptions.yaml` + Sentinel |
| AI / Agent Surface (Risky Agents, Risky AI usage, Triage Agent) | AI Governance Lead, CCO | Daily | Sentinel + Purview DSPM for AI |
| Supervisory Tie-out (CC ↔ IRM) | CCO | Weekly | Sentinel |

Dashboards are **not** a substitute for the TC artefacts in §3 — they are derived views, not WORM-stored evidence.

### §5.12 Appendix L — On-change triggers

The following events MUST trigger off-cycle re-execution of the indicated TCs:

| Trigger | TCs to re-run | SLA |
|---|---|---|
| New IRM policy created or modified | TC-3, TC-4, TC-5, TC-6, TC-7, TC-9 (any affected) | Same business day |
| IRM role-group membership change | TC-2, TC-12 (re-assert SoD) | Within 24h |
| Forensic Evidence enabled in a new jurisdiction | TC-13, TC-12 | Before first capture |
| Sovereign-exception register updated | TC-20 (affected exception only) | Within 7 days |
| Tenant migration (commercial → sovereign or vice-versa) | All TCs (full cycle) | Within 30 days post-migration |
| Microsoft Learn change to a referenced capability (Adaptive Protection, Risky Agents, Forensic Evidence, Triage Agent) | TC-3 (indicator implications), TC-4 / TC-5 / TC-9 / TC-12 / TC-14 / TC-15 / TC-20 (as applicable) | Within 30 days of Microsoft change |
| Indicator baseline change (RFC approved) | TC-3 | Same business day |
| Intune extension force-install policy change | TC-5, TC-9 | Within 7 days |
| HR connector schema change (added / removed field) | TC-6 | Same business day |
| Defender for Cloud Apps model update | TC-10 | Within 14 days |
| Conditional Access policy bound to Adaptive Protection changed | TC-15 | Within 7 days |
| Communication Compliance policy scope change | TC-16 | Within 7 days |
| Sentinel connector health change | TC-19 | Within 24h |
| State employee-monitoring statute change (legislative or regulatory) | TC-13 | Within 30 days; suspend affected captures pending GC review |

### §5.13 Appendix M — Firm-defined SLA register (illustrative)

> Microsoft does **not** publish IRM alert latency, triage SLA, or investigation duration ceilings. The values below are **firm-defined per WSP** and serve as defaults; tune via your governance process.

| SLA | Default | Owner |
|---|---|---|
| High-severity alert → Analyst acknowledgement | 4 business hours | IRM Analyst |
| High-severity alert → CCO disposition | 24 business hours | CCO |
| In-scope incident → Regulator-notification draft | 48 hours | CCO + GC |
| In-scope incident → Regulator-notification submission | 72 hours (NYDFS / Reg S-P) | CCO + GC |
| Forensic Evidence capture request → Approver decision | 4 business hours | IRM Approver |
| Forensic Evidence approval → 100-day decision (extend / hold / auto-delete) | 100 days from approval | IRM Investigator |
| Triage Agent saved-auth/config refresh | 90 days | AI Governance Lead |
| TC-22 pull-test assembly | 48 hours | CCO + records-management custodian |
| Sovereign-exception compensating-control exercise | 90 days | Per exception owner |
| Indicator baseline RFC review | 14 calendar days | Purview Compliance Admin + AI Governance Lead |

### §5.14 Appendix N — Failure-mode catalogue (selected)

| Failure mode | Detected by | Immediate action | Long-term action |
|---|---|---|---|
| UAL ingestion silently disabled | TC-1 (PRE-7 + 7-day operations check) | Re-enable; halt evidence cycle | Add Sentinel detection rule on `UnifiedAuditLogIngestionEnabled = false`; alert CISO |
| Catch-all role group repopulated | TC-2 | Empty membership; quarantine in-flight cases | Add Sentinel detection rule on role-group membership changes |
| Investigator ↔ Approver overlap | TC-2, TC-12 | Halt all FE captures; demote per SoD | Make role-group changes PIM-eligible only; require dual-approver |
| Pseudonymization disabled | PRE-6, TC-18 | Re-enable; halt evidence cycle | Add Sentinel detection rule on `PseudonymizationEnabled = false` |
| Risky Agents policy missing or scope-incomplete | TC-4 | Recreate policy; reconcile inventory | Wire Control 3.1 inventory to a scheduled Risky Agents reconciliation job |
| Risky AI extension coverage gap | TC-5 | Push Intune assignment | Add coverage SLO to operational dashboard |
| HR connector stale > 24h | TC-6 | Manual sync; investigate field mapping | Add health-monitor alert on connector last-sync age |
| MDA dynamic threat detection disabled or unhealthy | TC-10 | Re-enable; SOC sample review | Add connector-health detection rule |
| Sentinel KQL hits but no IRM artefact | TC-19 | Analyst follow-up; document benign rationale | Tune detection rule or IRM policy as appropriate |
| Sovereign capability changes parity (Microsoft Learn) | TC-15 / TC-20 quarterly verification | Update `governance/sovereign-exceptions.yaml`; rerun TC | Add Microsoft Learn change-watch process to AI Governance Lead's intake |
| Forensic Evidence clip auto-delete imminent (≤ 20 days) without 100-day decision | TC-12 (per-capture) | Investigator decides extend / hold / auto-delete | Add automated reminder at 80-day mark |
| State statute change | TC-13 | Suspend captures in jurisdiction; GC review | Subscribe to legislative-tracking service |
| Triage Agent saved-auth expiring | TC-14 | Refresh under change ticket | Add 14-day pre-expiry alert |
| Adaptive Protection binding drift (commercial) | TC-15 | Re-bind under change ticket | Add binding-state detection rule |
| 72-hour clock breach | TC-17 | RCA within 7 business days | Process-engineering review; tabletop reset |
| TC-22 artefact missing or sidecar mismatch | TC-22 | Records-management incident | Audit Committee escalation |

### §5.15 Appendix O — Microsoft Learn watch-list (re-verify each cycle)

Each cycle, the AI Governance Lead re-verifies the following Microsoft Learn topics and records `learnVerifiedUtc` against the sovereign-exception register and the indicator baseline:

- Insider Risk Management — overview and policy templates.
- Insider Risk Management — Forensic Evidence (PAYG, 120-day clip retention).
- Insider Risk Management — Adaptive Protection (sovereign availability).
- Insider Risk Management — Risky AI usage (extension prerequisites).
- Insider Risk Management — Risky Agents (default-applied policy; agent-class indicators).
- Insider Risk Management — Risky browser usage.
- Insider Risk Management — Communication Compliance integration.
- Insider Risk Management — Defender for Cloud Apps integration.
- Insider Risk Management — Triage Agent (Security Copilot) requirements.
- Insider Risk Management — sovereign cloud parity matrix.
- Microsoft Sentinel — OfficeActivity table for `InsiderRiskMgmt*` operations.
- Microsoft Purview — pseudonymization and unmask audit operations.

A delta against the prior cycle's watch-list is recorded in the cycle's evidence package.

---

*Updated: April 2026 | Version: v1.4 | UI Verification Status: Current*
