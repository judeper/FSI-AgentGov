# Control 1.7 — Verification & Testing Playbook (Audit Capture, Preservation, and Content Plane Integrity)

**Control:** 1.7 — Comprehensive Audit Logging and Compliance
**Pillar:** 1 — Security
**Audience:** Purview Audit Admin, Purview Compliance Admin, Exchange Online Admin (Organization Configuration role), AI Administrator, Power Platform Admin, Entra Security Admin, SOC Analyst, Compliance Officer, AI Governance Lead, Internal Audit, Azure Storage Account Owner / Contributor, Records Management Officer, Designated Executive Officer (DEO) or Designated Third Party (DTP) liaison
**Sovereign-cloud scope:** Microsoft 365 Commercial, GCC, GCC High, DoD. 21Vianet is **out of scope** for this playbook.
**Last UI verified:** April 2026

---

## Regulatory hedging notice

This playbook is intended to help support FSI organizations in meeting expectations from FINRA Rule 4511 (books and records), FINRA Rule 3110 (supervision), FINRA Regulatory Notice 25-07 (request for comment on workplace modernization, including AI-generated communications recordkeeping — not final guidance), SEC Rule 17a-3 (record creation), SEC Rule 17a-4(a) (financial records 6-year retention), SEC Rule 17a-4(b)(4) (communications 3-year retention with first 2 in an easily accessible place), SEC Rule 17a-4(f) (electronic recordkeeping system requirements, including the October 2022 amendments / 3 May 2023 compliance date introducing the audit-trail alternative), SOX §§302/404, GLBA 501(b), OCC Bulletin 2011-12, Federal Reserve SR 11-7, CFTC Regulation 1.31 (5-year retention for FCMs, swap dealers, CPOs), NYDFS 23 NYCRR Part 500.06 (audit trail), NIST AI RMF 1.0, and ISO/IEC 42001:2023 where applicable.

A clean run of this playbook **does not guarantee legal or regulatory compliance**, does not by itself constitute a 17a-4(f) attestation, does not replace the firm's written supervisory procedures, does not substitute for the Cohasset (or equivalent) attestation that an electronic recordkeeping system is non-rewriteable / non-erasable, does not replace the independent records-management assessment required under the audit-trail alternative, and does not prove the absence of unaudited Copilot or agent activity in surfaces this playbook did not enumerate. Implementation requires organization-specific risk assessment, legal review, and integration with the firm's broader compliance program. Organizations should verify current Microsoft Learn documentation, sovereign-cloud feature parity, tenant-specific entitlements, and admin-surface availability at each cycle. Numeric thresholds, latency ceilings, sample sizes, and rotation cadences in this playbook are **calibrated to the tenant baseline captured in PRE-04**; they are not portable between tenants without recalibration.

This playbook is **three-tier verification**: it confirms that audit telemetry is **captured** (capture tier), that the books-and-records record set is **preserved** in a 17a-4(f)-defensible manner where applicable (preservation tier), and that prompt and response **content** is retrievable through Substrate / DSPM for AI / eDiscovery (content tier). Control 1.7 is the foundation control for the **observability and recordkeeping plane** for Microsoft 365 Copilot and Copilot Studio agents; if any of the three tiers fails, every downstream supervisory, examination, and incident-response control loses the evidence it depends on.

---

## Why this playbook is foundational

Microsoft 365 Audit (Standard, Premium, the 10-Year Audit Log Retention add-on, and the Pay-As-You-Go billing model for non-Microsoft AI app interactions) is **record-capture operational telemetry**. It is not, by itself, a SEC Rule 17a-4(f)–compliant electronic recordkeeping system for the books-and-records record set. The playbook treats the three tiers as separate verification problems with separate failure modes:

1. **Capture-tier failures** — audit ingestion is off, a Copilot RecordType is not flowing, a Dataverse environment has audit disabled, a per-user license is missing so a Zone 3 retention policy silently downgrades to 180 days, an Audit Premium-only feature (e.g., `MailItemsAccessed`) is not firing, or an invalid `-RecordType` value is producing false-clean evidence.
2. **Preservation-tier failures** — for broker-dealers, FCMs, swap dealers, or CPOs, no 17a-4(f)-compliant preservation pipeline exists for the Copilot / agent communications record set; or one exists but the time-based retention policy is unlocked, or the third-party archive's attestation has lapsed, or the audit-trail alternative is in use without the Designated Executive Officer (DEO) representation / Designated Third Party (DTP) undertaking and independent records-management assessment.
3. **Content-tier failures** — prompt and response body cannot be retrieved through DSPM for AI, eDiscovery (Premium), or Communication Compliance for a `CopilotInteraction` event identified in the audit log, breaking the join from audit metadata to communication content that an examiner expects.

The playbook treats **silent capture incompleteness** (a Copilot RecordType returning zero rows because of a license gap, a missing custom retention policy, a PAYG enablement that was never performed, or a propagation lag mistaken for steady-state) as more severe than visible misconfiguration, because it cannot be detected by any control downstream of capture. **Preservation absence** in a regulated firm is a cycle-stopping FAIL recorded in PRES-00 — there is no compensating control sufficient to substitute for the 17a-4(f) preservation tier.

---

## Audience and how to use this playbook

| Role | What you do here |
|---|---|
| **Purview Audit Admin** | Owns capture-tier verification (CAP-01 through CAP-08). Confirms unified audit ingestion is on, license entitlement reconciles, RecordType coverage is complete, custom retention policies are in place, and Audit Premium / PAYG features (`MailItemsAccessed`, `AIAppInteraction`) are firing. |
| **Purview Compliance Admin** | Owns content-tier verification (CONT-01 through CONT-04). Runs eDiscovery (Premium) collections, confirms DSPM for AI surfaces transcripts, verifies Communication Compliance review of AI-generated content. |
| **Exchange Online Admin (Organization Configuration role)** | Authors and modifies audit retention policies (Microsoft Learn: `Compliance Admin` alone is **not** sufficient for retention policy create/modify operations). |
| **Power Platform Admin** | Verifies per-environment Dataverse audit and per-table audit on the Copilot Studio entities (CAP-05). |
| **AI Administrator** | Confirms agent-side configuration: `AgentId` propagation into audit, declarative vs custom-engine prefix integrity, Copilot Studio publication events flowing as `MicrosoftCopilotStudio`. |
| **Entra Security Admin** | Verifies `agentSignIn` log type is enabled and forwarded; confirms the live filter affordance on the Sign-in logs page (the prior `Is Agent = Yes` chip was renamed across recent UI revisions — verify the current label rather than asserting it). Confirms `MicrosoftServicePrincipalSignInLogs` diagnostic stream where required. |
| **SOC Analyst** | Owns SIEM-side verification (CAP-08, TAMP-01, JOIN-01). Confirms Sentinel ingestion lag is within the empirically measured ceiling, the disable-audit alert is wired (Control 3.9), and the cross-source join produces a single end-to-end record. |
| **Azure Storage Account Owner / Contributor** | Owns the WORM preservation path (PRES-A). Confirms the immutable blob container has a **locked** time-based retention policy at or above the regulatory floor and that the export pipeline writes to it. |
| **Records Management Officer** | Owns the third-party archive preservation path (PRES-B) and the audit-trail alternative path (PRES-C). Maintains the 17a-4(f) attestation evidence file (Cohasset attestation for the storage path, vendor 17a-4-attested SLA documentation for the archive path, DEO representation / DTP undertaking for the alternative path). |
| **Designated Executive Officer (DEO) or Designated Third Party (DTP) liaison** | Required only for firms relying on the audit-trail alternative under the October 2022 17a-4(f) amendments. Confirms the DEO representation or DTP undertaking is on file and current. |
| **Compliance Officer** | Reviews the cycle evidence pack from a supervisory and regulatory-readiness perspective. Signs as **Compliance** in the three-signature attestation chain. |
| **AI Governance Lead** | Reviews cycle outputs against governance policy, arbitrates failure escalations, owns the per-cycle exception register. |
| **Internal Audit** | Uses the evidence pack and three-signature chain as the testable artifact for SOX-style and FINRA-supervision walkthroughs and runs the quarterly examiner-style reconstruction (CONT-04 / JOIN-01). |

Run order each cycle: **Section 4 PRE gates → Section 5 CAP-* tests → PRES-* tests → CONT-* tests → SOV-* tests → TAMP-01 → JOIN-01 → Section 6 evidence pack assembly → Section 7 attestation chain**. Any PRE-* failure, any CAP-01 / CAP-02 / CAP-03 FAIL, or any PRES-00 FAIL halts the cycle.

---

## Cross-links

This playbook depends on, and is depended on by, the following framework controls and playbooks. Operators should open these alongside this document during a cycle:

- [Control 1.7 — Comprehensive Audit Logging and Compliance (control specification)](../../../controls/pillar-1-security/1.7-comprehensive-audit-logging-and-compliance.md)
- [Control 1.5 — Data Loss Prevention for Generative AI](../../../controls/pillar-1-security/1.5-data-loss-prevention-dlp-and-sensitivity-labels.md) — DLP override justification events that must reach audit
- [Control 1.6 — Microsoft Purview DSPM for AI](../../../controls/pillar-1-security/1.6-microsoft-purview-dspm-for-ai.md) — content-tier transcript surfacing
- [Control 1.10 — Communication Compliance](../../../controls/pillar-1-security/1.10-communication-compliance-monitoring.md) — supervisory review of AI-generated content
- [Control 1.19 — eDiscovery for Agent Interactions](../../../controls/pillar-1-security/1.19-ediscovery-for-agent-interactions.md) — content-tier collection and legal hold
- [Control 2.6 — Lifecycle Management of Agents](../../../controls/pillar-2-management/2.6-model-risk-management-alignment-with-occ-2011-12-sr-11-7.md) — publication / decommission events that must surface in audit
- [Control 2.12 — Change Management for AI Agents](../../../controls/pillar-2-management/2.12-supervision-and-oversight-finra-rule-3110.md) — change events whose audit trail this control preserves
- [Control 3.4 — Regulatory Reporting Automation](../../../controls/pillar-3-reporting/3.4-incident-reporting-and-root-cause-analysis.md) — downstream consumer of the evidence pack
- [Control 3.9 — Microsoft Sentinel Integration](../../../controls/pillar-3-reporting/3.9-microsoft-sentinel-integration.md) — SIEM ingestion path and tamper-resistance alerting
- [PowerShell Setup playbook](powershell-setup.md) — source of all helper functions referenced in this document
- [Portal Walkthrough playbook](portal-walkthrough.md)
- [Troubleshooting playbook](troubleshooting.md)

---

## What this playbook catches

This playbook is designed to detect defects in the **audit, preservation, and content recovery program** for Microsoft 365 Copilot and Copilot Studio agents. It is built to surface:

1. **Unified audit ingestion off** — the tenant-level switch is `False`, or a `Get-AdminAuditLogConfig` call from the wrong session (Security & Compliance PowerShell) is producing a false `False`.
2. **Copilot RecordType silent gaps** — `CopilotInteraction`, `ConnectedAIAppInteraction` (mixed Microsoft built-in + PAYG scope), `AIAppInteraction` (PAYG-only), or `MicrosoftCopilotStudio` returning zero rows for a window in which user activity is known to have occurred.
3. **PAYG enablement omissions** — non-Microsoft AI app interactions and the PAYG portion of Connected AI App scope captured in audit only after explicit enablement; firms assuming default coverage produce false-clean evidence.
4. **License-induced silent retention downgrades** — a Zone 3 user holds a Copilot license without the 10-Year Audit Log Retention add-on, so their records drop at 180 days regardless of the custom retention policy duration.
5. **Custom retention policy gaps** — the platform default Audit (Premium) policy excludes Copilot record types, so any RecordType not covered by an enabled custom policy falls back to 180 days.
6. **Dataverse audit gaps** — environment-level audit disabled, retention below the zone floor, or per-table audit not enabled on the six Copilot Studio entities (`bot`, `botcomponent`, `botcomponentcollection`, `botpublishstatus`, and the current additions per the Microsoft Learn Power Platform table reference at the time of test).
7. **Entra agent sign-in invisibility** — the `agentSignIn` log type is not forwarded to Log Analytics / SIEM, the sign-in log filter affordance for agent identities is misnamed in tenant runbooks (the prior `Is Agent = Yes` label has shifted across UI revisions — verify the live label), or `AppOwnerTenantId` / `ResourceOwnerTenantId` / `SessionId` / `SourceAppClientID` / `ASN` are missing from the SIEM ingestion schema.
8. **DLP override justification not reaching audit** — a Control 1.5 policy-tip override is acted on but the justification text is not surfaced in the audit log.
9. **`MailItemsAccessed` not firing** — the Audit Premium event for regulated mailboxes is not present, breaking the breach-investigation reconstruction path.
10. **Preservation tier missing** — for broker-dealer / FCM / swap dealer / CPO firms, no 17a-4(f)-defensible preservation pipeline exists for the Copilot / agent communications record set; this is a **PRES-00 FAIL** and a cycle-stopping condition with no compensating control.
11. **Preservation tier present but defective** — Azure immutable blob container exists but the time-based retention policy is `Unlocked` (still mutable), or the third-party archive's 17a-4-attested SLA documentation has lapsed, or the audit-trail alternative is in use without the DEO representation / DTP undertaking and the independent records-management assessment.
12. **Content-tier retrieval failure** — a `CopilotInteraction` event identified in the audit log cannot be joined to its prompt/response body via DSPM for AI, eDiscovery (Premium), or Communication Compliance, breaking the audit-to-content reconstruction expected by examiners.
13. **Sovereign-cloud feature drift** — Audit Premium availability, PAYG availability, or IRM-dependent audit features assumed to exist in GCC / GCC High / DoD that in fact have parity gaps requiring documented compensating-control records.
14. **Tamper-evidence absence** — disabling unified audit on a non-prod tenant does not produce a corresponding `Set-AdminAuditLogConfig` event in the tenant audit log and does not raise a Sentinel alert.
15. **Cross-source join breakage** — the `Messages[].ID` join key does not connect a single Copilot interaction across CopilotInteraction → Substrate body → DLP event → Sentinel ingestion, breaking the canonical examiner reconstruction path.

---

## What this playbook does NOT claim

This playbook **does not** prove the absence of audit gaps in surfaces it did not enumerate, **does not** independently certify that the firm's electronic recordkeeping system is non-rewriteable / non-erasable in the SEC Rule 17a-4(f)(2)(i) sense (that certification is the role of an independent third party such as Cohasset Associates), **does not** substitute for the firm's written supervisory procedures, **does not** validate the substantive content of any AI-generated communication, **does not** replace the independent records-management assessment required under the audit-trail alternative, **does not** assume universal sovereign-cloud feature parity, and **does not** commit Microsoft to a published audit ingestion SLA. Microsoft does not publish a hard ingestion SLA for unified audit; the playbook records the empirically measured ceiling for the tenant and flags deviations against that empirical baseline rather than against a fabricated number. A clean cycle is a defensible attestation that the audit / preservation / content program operated against the policy in force on the cycle start date; it is not a statement about the firm's complete recordkeeping posture.

---

## Section 1 — The 3-Signature Attestation Chain

Every audit verification cycle terminates in a **three-signature attestation chain** with cryptographic integrity. This is the cycle's primary deliverable and the artifact handed to internal audit and external examiners.

### 1.1 Signature roles

| Signature | Role (canonical) | What this signature attests |
|---|---|---|
| **Capture Owner** | Purview Audit Admin | "I executed CAP-01 through CAP-08; unified audit ingestion is enabled and verified from an Exchange Online PowerShell session; license entitlement is reconciled; every Copilot RecordType in scope is covered by an explicit enabled custom retention policy at the documented horizon; per-environment Dataverse audit and per-table audit on the Copilot Studio entities are enabled; agent sign-in events are flowing; DLP override justification reaches audit; `MailItemsAccessed` is firing for regulated mailboxes." |
| **Preservation Owner** | Records Management Officer | "I executed PRES-00 through PRES-C as applicable to the firm's regulatory profile; for the broker-dealer / FCM / swap dealer / CPO scope, a 17a-4(f)-defensible preservation pipeline exists for the Copilot / agent communications record set, and the path used (A = Azure immutable blob, B = third-party 17a-4-attested archive, C = audit-trail alternative) is documented in the cycle evidence pack with its supporting attestation, vendor SLA, or DEO/DTP and independent records-management assessment artifacts." |
| **Compliance** | Compliance Officer | "I reviewed the evidence pack including capture-tier, preservation-tier, content-tier, sovereign-cloud, tamper-resistance, and cross-source join evidence from a supervisory and regulatory-readiness perspective; the residual gaps documented in this cycle are acceptable for the firm's current risk posture or are tracked to a dated remediation plan; the evidence is suitable for inclusion in the firm's books-and-records repository under the applicable retention period." |

The three signatures **must** be three distinct natural persons. Role collision is a cycle-stopping FAIL recorded in PRE-02. A documented temporary exception is allowed only with a co-signed expiry and a return-to-three-person review on the next cycle.

### 1.2 Hash chain across snapshots

Each cycle's evidence pack contains a `manifest.sha256` file listing one SHA-256 per artifact. The cycle attestation file (`attestation.json`) records:

- `cycleId` — stable identifier (e.g., `1.7-2026-Q2-COMM`)
- `previousCycleId` — the immediately preceding cycle for the same scope and cloud
- `previousManifestHash` — SHA-256 of the previous cycle's `manifest.sha256`
- `manifestHash` — SHA-256 of the current cycle's `manifest.sha256`
- `chainHash` — SHA-256 of `previousManifestHash || manifestHash || cycleId`
- `signatures[]` — three signature objects (Capture Owner, Preservation Owner, Compliance) each with role, identity (UPN), timestamp (UTC ISO-8601), signature method, and signed digest

A break in the chain is itself an audit finding and triggers the failure path described in Section 7.

```json
{
  "cycleId": "1.7-2026-Q2-COMM",
  "previousCycleId": "1.7-2026-Q1-COMM",
  "previousManifestHash": "9c0f...e1a7",
  "manifestHash": "1ad4...77b2",
  "chainHash": "8b22...904c",
  "scope": { "zone": "Z3", "cloud": "Commercial", "regulatedProfile": "broker-dealer", "preservationPath": "A" },
  "signatures": [
    { "role": "CaptureOwner",      "upn": "audit@contoso.com",      "tsUtc": "2026-04-15T14:02:11Z", "method": "Entra-bound key", "digest": "..." },
    { "role": "PreservationOwner", "upn": "records@contoso.com",    "tsUtc": "2026-04-15T14:09:48Z", "method": "Hardware token",  "digest": "..." },
    { "role": "Compliance",        "upn": "compliance@contoso.com", "tsUtc": "2026-04-15T15:31:02Z", "method": "S/MIME",          "digest": "..." }
  ]
}
```

### 1.3 Attestation note language

The Capture Owner attestation should include the literal language: *"This cycle was executed against the audit surfaces and tenant entitlements available as of the cycle start date in the declared sovereign cloud. A clean cycle does not by itself ensure regulatory compliance, does not constitute a 17a-4(f) attestation that the firm's electronic recordkeeping system is non-rewriteable / non-erasable, and does not substitute for the firm's written supervisory procedures."*

The Preservation Owner attestation should include the literal language: *"The preservation path identified in `scope.preservationPath` is the path on which the firm relies to satisfy SEC Rule 17a-4(f) for the Copilot / agent communications record set, and the supporting attestation / SLA / DEO representation / DTP undertaking / independent records-management assessment artifacts referenced in this cycle's manifest are current as of the cycle start date."*

### 1.4 Signature method requirements

| Zone | Minimum signature method | Stronger-method recommendation |
|---|---|---|
| Zone 1 | Entra Verified ID-attested signature or equivalent | Entra-bound device-bound key |
| Zone 2 | Entra-bound device-bound key on a managed device | Hardware-token-protected key |
| Zone 3 | Hardware-token-protected key (FIPS 140-2 or 140-3 validated) | HSM-resident signing key with dual-control activation |

---

## Section 2 — Sovereign Cloud parity matrix

The audit and preservation surfaces this playbook depends on do **not** have uniform feature parity across Microsoft 365 sovereign clouds as of April 2026. Cells marked *Verify* should be re-checked against the tenant Message Center and Microsoft Learn at cycle start; the cycle should record what was observed, not what was assumed.

| Capability | Commercial | GCC | GCC High | DoD | Cycle implication if unavailable |
|---|---|---|---|---|---|
| Unified audit log (Audit Standard) | GA | GA | GA | GA | Required everywhere; absence is a hard blocker |
| Audit (Premium) including `MailItemsAccessed` | GA | GA | GA / verify | GA / verify | Required for breach-investigation reconstruction; record SOV-01 compensating control if unavailable |
| 10-Year Audit Log Retention add-on | GA | GA / verify | Verify | Verify | Required for Zone 3 retention; without it, records drop at 180 days |
| Audit Pay-As-You-Go billing model | GA | Verify | Verify | Verify | Required to capture `AIAppInteraction` and the PAYG portion of `ConnectedAIAppInteraction`; record SOV-02 if unavailable |
| `CopilotInteraction` RecordType | GA | GA | GA / verify | GA / verify | Hard blocker if absent |
| `ConnectedAIAppInteraction` RecordType (Microsoft built-in scope) | GA | GA | Verify | Verify | Hard blocker if absent for in-scope agents |
| `ConnectedAIAppInteraction` RecordType (PAYG scope) | GA / opt-in | Verify | Verify | Verify | Required for non-Microsoft AI app coverage; record SOV-02 |
| `AIAppInteraction` RecordType (PAYG-only) | GA / opt-in | Verify | Verify | Verify | Required for non-Microsoft AI app coverage |
| `MicrosoftCopilotStudio` RecordType | GA | GA | Verify | Verify | Required for agent lifecycle audit |
| Dataverse environment + per-table audit | GA | GA | GA | GA | Required everywhere |
| `agentSignIn` log type (preview) | Preview | Preview / verify | Verify | Verify | Use Entra sign-in logs (service principal type) as fallback; record SOV-04 |
| `MicrosoftServicePrincipalSignInLogs` diagnostic stream (preview) | Preview | Verify | Verify | Verify | Optional; document non-availability as gap, not failure |
| DSPM for AI transcript surfacing | GA | GA / verify | Verify | Verify | Required for content-tier verification (CONT-02) |
| eDiscovery (Premium) | GA | GA | GA | GA | Required for content-tier verification (CONT-01) |
| Communication Compliance | GA | GA | GA / verify | GA / verify | Required for content-tier verification (CONT-03) |
| Microsoft Sentinel | GA | GA | GA | GA | Required for tamper-resistance alerting (TAMP-01) and cross-source join (JOIN-01) |
| IRM-dependent audit features | GA | **Not available** | **Not available** | **Not available** | Document as compensating-control gap in **all** US Gov clouds — none of GCC / GCC High / DoD support IRM-dependent audit features as of April 2026 |
| Azure immutable blob storage with locked time-based retention (Cohasset-attested) | GA | GA (Azure Government) | GA (Azure Government) | GA (Azure Government Secret / Top Secret separately) | Required for PRES-A path; absence forces PRES-B or PRES-C |

---

## Section 3 — Re-verification cadence

Audit configuration is not static — license assignments, retention policies, RecordType coverage, per-environment Dataverse settings, archive vendor SLAs, and 17a-4(f) attestations all change continuously. Run each test on its own cadence; do not rely on a single annual binder refresh.

| Trigger | Tests |
|---|---|
| **Daily** (automated) | CAP-01 (audit ingestion enabled), CAP-03 (Copilot RecordType smoke test — non-zero or documented zero) |
| **Weekly** | CAP-08 (Sentinel ingestion lag against empirical ceiling), PRES-A retrieval test (random object pull from immutable blob), PRES-B retrieval test (random retrieval from third-party archive) |
| **Monthly** | CAP-02 (license entitlement reconciliation), CAP-04 (custom retention policy coverage map), CAP-05 (Dataverse environment + per-table audit), CAP-06 (DLP override justification in audit), CAP-07 (`MailItemsAccessed` for regulated mailboxes), preservation pipeline end-to-end test (write → seal → retrieve), TAMP-01 (tamper-evidence rehearsal on non-prod) |
| **Quarterly** | CONT-01 (eDiscovery Premium retrieval drill), CONT-02 (DSPM for AI transcript drill), CONT-03 (Communication Compliance review drill), CONT-04 (worked examiner reconstruction example), JOIN-01 (cross-source join), 17a-4(f) attestation review (Cohasset attestation currency or vendor SLA currency or DEO representation / DTP undertaking currency), SOV-* parity matrix re-check |
| **Annual** | Independent records-management assessment (firms relying on PRES-C audit-trail alternative — required by the October 2022 17a-4(f) amendments) |
| **On-change** | After any retention policy create/modify, license SKU change, environment add/remove, RecordType enablement (PAYG opt-in), archive vendor change, immutable retention policy change, or sovereign-cloud feature rollout: re-run the affected CAP-* / PRES-* / SOV-* tests within 24 hours and capture evidence |
| **License event** | When a Copilot user is added/removed or 10-year add-on assignment changes: re-run CAP-02 within 24 hours |

---

## Section 4 — Pre-flight gates

| Gate | Description | Pass condition |
|---|---|---|
| **PRE-01** | Cycle scope and zone declared | `cycleId`, `scope.zone`, `scope.cloud`, `scope.regulatedProfile`, `scope.preservationPath` recorded |
| **PRE-02** | Three distinct signers identified | Capture Owner, Preservation Owner, Compliance — three different UPNs |
| **PRE-03** | Module versions pinned | `ExchangeOnlineManagement` v3.x and `Microsoft.Graph` v2.x at CAB-approved versions |
| **PRE-04** | Tenant baseline current | Empirical Sentinel ingestion ceiling (CAP-08) measured within the last 30 days |
| **PRE-05** | Previous-cycle hash present | `previousManifestHash` populated and matches the prior cycle's `manifestHash` |
| **PRE-06** | Connection asserted to Exchange Online | `Test-UnifiedAuditEnabled` returns a `SessionUri` matching `outlook.office365.(com|us)` — defends against the Security & Compliance PowerShell trap that always returns `False` for `UnifiedAuditLogIngestionEnabled` |
| **PRE-07** | RecordType enum hydrated | `[Enum]::GetNames([Microsoft.Office.CompliancePolicy.PSCmdlets.AuditRecordType])` enumerable, OR module-version warning recorded — defends against silent zero-row return for invalid `-RecordType` values |

Any PRE-* failure halts the cycle.

---

## Section 5 — Verification tests

All scripts below assume the helpers from [`powershell-setup.md`](powershell-setup.md) are in scope: `Connect-AuditExchangeOnline`, `Test-UnifiedAuditEnabled`, `Get-UserAuditEntitlement`, `Search-AuditLogPaged`, `Save-AuditEvidence`. Each test produces a structured `[pscustomobject]` with a `collectorField` value suitable for ingestion into the v1.4 assessment manifest.

### CAP — Capture-tier tests

#### CAP-01 — Unified audit ingestion enabled

**Expected:** `UnifiedAuditLogIngestionEnabled : True` from an Exchange Online PowerShell session, with `SessionUri` matching `outlook.office365.(com|us)`.

```powershell
. .\Connect-AuditExchangeOnline.ps1
Connect-AuditExchangeOnline -Cloud Commercial -UserPrincipalName 'auditor@contoso.com'

$cap01 = Test-UnifiedAuditEnabled
$result = [pscustomobject]@{
    testId          = 'CAP-01'
    collectorField  = 'audit.unifiedAuditLogIngestionEnabled'
    expected        = $true
    observed        = $cap01.UnifiedAuditLogIngestionEnabled
    sessionUri      = $cap01.SessionUri
    status          = if ($cap01.UnifiedAuditLogIngestionEnabled -eq $true -and $cap01.SessionUri -match 'outlook\.office365\.(com|us)') { 'PASS' } else { 'FAIL' }
    capturedAtUtc   = (Get-Date).ToUniversalTime().ToString('o')
}
$result | Save-AuditEvidence -Name 'CAP-01_AuditConfig'
$result
```

- `[PASS]` only if `UnifiedAuditLogIngestionEnabled = True` **AND** `SessionUri` matches the expected EXO URI pattern.
- `[FAIL]` if either is wrong, or if the connection is unverified.

#### CAP-02 — Per-user license entitlement reconciliation (Audit Standard / Premium / 10-Year add-on / PAYG)

**Expected:** every Copilot-licensed user has Audit Premium; every Zone 3 Copilot user additionally has the 10-Year Audit Log Retention add-on; tenants in scope for non-Microsoft AI app coverage have PAYG enrollment recorded.

```powershell
$report = Get-MgUser -All -Property Id,UserPrincipalName,AssignedLicenses |
    ForEach-Object { Get-UserAuditEntitlement -UserId $_.Id }

$gaps = $report | Where-Object {
    $_.HasCopilot -and (-not $_.HasAuditPremium -or -not $_.Has10YearRetention)
}

# Optional: PAYG enrollment check (verify against the current Purview billing surface)
$paygEnrolled = $null  # populate from Purview portal evidence; record explicitly even if False

$cap02 = [pscustomobject]@{
    testId          = 'CAP-02'
    collectorField  = 'audit.licenseEntitlement'
    copilotUserCount = ($report | Where-Object HasCopilot).Count
    gapCount        = $gaps.Count
    paygEnrolled    = $paygEnrolled
    regulatedScope  = 'broker-dealer'  # echo from PRE-01
    status          = if ($gaps.Count -eq 0) { 'PASS' } else { 'FAIL' }
    capturedAtUtc   = (Get-Date).ToUniversalTime().ToString('o')
}
$report | Save-AuditEvidence -Name 'CAP-02_LicenseEntitlement'
$cap02 | Save-AuditEvidence -Name 'CAP-02_Summary'
$cap02
```

- `[PASS]` if `gapCount -eq 0` and PAYG enrollment matches the firm's regulated-data scope.
- `[FAIL]` if any user has Copilot without Audit Premium, any Zone 3 Copilot user lacks the 10-year add-on (records will silently drop at 180 days), or the firm is in scope for non-Microsoft AI app coverage and PAYG is not enrolled.

#### CAP-03 — Copilot RecordType coverage smoke test

**Expected:** every Copilot RecordType in scope returns either non-zero rows for the prior 24 hours, or a documented expected-zero (e.g., a tenant with no `AIAppInteraction` PAYG enablement should always return 0 for that type, and the absence itself is the evidence).

```powershell
$copilotRecordTypes = @(
    @{ Name = 'CopilotInteraction';        Scope = 'Microsoft built-in'; Required = $true  },
    @{ Name = 'ConnectedAIAppInteraction'; Scope = 'Mixed (Microsoft built-in + PAYG)'; Required = $true  },
    @{ Name = 'AIAppInteraction';          Scope = 'PAYG-only';          Required = $false },
    @{ Name = 'MicrosoftCopilotStudio';    Scope = 'Microsoft built-in'; Required = $true  }
)

$cap03 = foreach ($rt in $copilotRecordTypes) {
    $rows = Search-AuditLogPaged -StartDate (Get-Date).AddDays(-1) -EndDate (Get-Date) -RecordTypes @($rt.Name)
    [pscustomobject]@{
        testId          = 'CAP-03'
        collectorField  = "audit.recordType.$($rt.Name).rowCount24h"
        recordType      = $rt.Name
        scope           = $rt.Scope
        rowCount        = $rows.Count
        required        = $rt.Required
        status          = if ($rows.Count -gt 0) { 'PASS' } elseif (-not $rt.Required) { 'PASS-DOCUMENTED-ZERO' } else { 'FAIL' }
        capturedAtUtc   = (Get-Date).ToUniversalTime().ToString('o')
    }
}
$cap03 | Save-AuditEvidence -Name 'CAP-03_RecordTypeSmoke'
$cap03 | Format-Table testId,recordType,rowCount,status
```

- `[PASS]` if every required RecordType is non-zero **OR** every non-required RecordType returns the documented expected-zero.
- `[FAIL]` if any required RecordType is zero with no documented expected-zero rationale.

Verify the live `ConnectedAIAppInteraction` scope split (Microsoft built-in vs PAYG portion) at cycle start; the split has shifted across recent Microsoft Learn revisions.

#### CAP-04 — Custom retention policy coverage map and horizon

**Expected:** every Copilot RecordType in scope is covered by an explicit, enabled custom retention policy with `RetentionDuration` matching the documented zone horizon.

```powershell
$expected = @(
    @{ Zone = 'Zone 1'; Duration = 'SixMonths';    LicenseFloor = 'Any commercial M365 enterprise SKU' },
    @{ Zone = 'Zone 2'; Duration = 'TwelveMonths'; LicenseFloor = 'Audit Premium' },
    @{ Zone = 'Zone 3'; Duration = 'TenYears';     LicenseFloor = 'Audit Premium + 10-Year Audit Log Retention add-on' }
)

$policies = Get-UnifiedAuditLogRetentionPolicy
$copilotRecordTypes = @('CopilotInteraction','ConnectedAIAppInteraction','AIAppInteraction','MicrosoftCopilotStudio')

$cap04 = foreach ($rt in $copilotRecordTypes) {
    $covered = $policies | Where-Object { $_.RecordTypes -contains $rt -and $_.Enabled }
    [pscustomobject]@{
        testId          = 'CAP-04'
        collectorField  = "audit.retentionPolicy.$rt.coveredBy"
        recordType      = $rt
        coveredByPolicy = ($covered.Name -join '; ')
        retentionDuration = ($covered.RetentionDuration -join '; ')
        status          = if ($covered) { 'PASS' } else { 'FAIL' }
        capturedAtUtc   = (Get-Date).ToUniversalTime().ToString('o')
    }
}
$cap04 | Save-AuditEvidence -Name 'CAP-04_RetentionCoverage'
$cap04 | Format-Table testId,recordType,coveredByPolicy,retentionDuration,status
```

- `[PASS]` if every required RecordType is covered by an enabled custom policy at the documented horizon.
- `[FAIL]` if any RecordType is uncovered — the platform default Audit (Premium) retention policy includes only AAD / Exchange / OneDrive / SharePoint, so Copilot record types fall back to 180 days regardless of E5 license.

#### CAP-05 — Dataverse environment audit and per-table audit on Copilot Studio entities

**Expected:** every Copilot Studio environment has environment-level audit enabled with retention ≥ the zone floor (180 / 365 / 730 days), and per-table audit is enabled on the six Copilot Studio entities documented in Microsoft Learn at the cycle start.

The current canonical entity set is `bot`, `botcomponent`, `botcomponentcollection`, `botpublishstatus`, plus the additions present in the live Power Platform table reference at the time of test. Verify against the Microsoft Learn Power Platform table reference rather than asserting the prior set; the entity list has been extended over time.

```powershell
# Pseudocode — Power Platform Admin Center / Power Platform admin PowerShell module (Microsoft.PowerApps.Administration.PowerShell)
$envs = Get-AdminPowerAppEnvironment | Where-Object { $_.EnvironmentType -ne 'Default' }
$expectedTables = @('bot','botcomponent','botcomponentcollection','botpublishstatus')  # Verify live

$cap05 = foreach ($env in $envs) {
    $envAudit = Get-AdminPowerAppEnvironmentAuditSettings -EnvironmentName $env.EnvironmentName  # if exposed
    $tableAudit = foreach ($t in $expectedTables) {
        # Use Dataverse Web API or PAC CLI to query entity AuditEnabled metadata
        [pscustomobject]@{ Table = $t; AuditEnabled = (Get-DataverseTableAuditEnabled -Env $env.EnvironmentName -Table $t) }
    }
    [pscustomobject]@{
        testId          = 'CAP-05'
        collectorField  = "audit.dataverse.$($env.EnvironmentName).perTableCoverage"
        environment     = $env.DisplayName
        envAuditEnabled = $envAudit.IsAuditEnabled
        envRetention    = $envAudit.RetentionPeriodDays
        perTableAll     = ($tableAudit | Where-Object { -not $_.AuditEnabled } | Measure-Object).Count -eq 0
        status          = if ($envAudit.IsAuditEnabled -and ($tableAudit | Where-Object { -not $_.AuditEnabled } | Measure-Object).Count -eq 0) { 'PASS' } else { 'FAIL' }
        capturedAtUtc   = (Get-Date).ToUniversalTime().ToString('o')
    }
}
$cap05 | Save-AuditEvidence -Name 'CAP-05_DataverseAudit'
$cap05
```

Without per-table audit on the Copilot Studio entities, agent admin events do not surface in `MicrosoftCopilotStudio` and downstream `ConnectedAIAppInteraction` correlation may be incomplete.

#### CAP-06 — DLP override justification reaches audit (Control 1.5 cross-link)

**Expected:** when a user overrides a Control 1.5 Generative AI DLP policy tip with a justification, the justification text is captured in the audit log and joinable to the originating `CopilotInteraction` event.

```powershell
# Trigger: from a test account, send a Copilot prompt that should hit a DLP policy with override-with-justification.
# Override the tip with a deterministic marker string, e.g.:
$marker = "FSI-1.7-DLP-override-test-$([guid]::NewGuid())"
# (Operator action in the Copilot client; record marker in the test log.)

Start-Sleep -Seconds 5400   # empirical audit propagation window — see CAP-08

$dlpRows = Search-AuditLogPaged `
    -StartDate (Get-Date).AddHours(-3) -EndDate (Get-Date) `
    -RecordTypes @('DLPEndpoint','ComplianceDLPSharePoint','ComplianceDLPExchange') `
    | Where-Object { $_.AuditData -match $marker }

$cap06 = [pscustomobject]@{
    testId          = 'CAP-06'
    collectorField  = 'audit.dlp.overrideJustificationCaptured'
    marker          = $marker
    rowsFound       = $dlpRows.Count
    status          = if ($dlpRows.Count -gt 0) { 'PASS' } else { 'FAIL' }
    capturedAtUtc   = (Get-Date).ToUniversalTime().ToString('o')
}
$cap06 | Save-AuditEvidence -Name 'CAP-06_DLPOverrideJustification'
$cap06
```

#### CAP-07 — `MailItemsAccessed` firing for regulated mailboxes (Audit Premium)

**Expected:** the Audit Premium `MailItemsAccessed` event is firing for the regulated mailbox population and is queryable in the prior 24 hours.

```powershell
$regulatedMailboxes = Get-Content '.\inputs\regulated-mailboxes.txt'

$cap07 = foreach ($upn in $regulatedMailboxes) {
    $rows = Search-AuditLogPaged `
        -StartDate (Get-Date).AddDays(-1) -EndDate (Get-Date) `
        -RecordTypes @('ExchangeItemAggregated') `
        -Operations @('MailItemsAccessed') `
        -UserIds $upn
    [pscustomobject]@{
        testId          = 'CAP-07'
        collectorField  = "audit.mailItemsAccessed.$upn.rowCount24h"
        upn             = $upn
        rowCount        = $rows.Count
        status          = if ($rows.Count -gt 0) { 'PASS' } else { 'FAIL' }
        capturedAtUtc   = (Get-Date).ToUniversalTime().ToString('o')
    }
}
$cap07 | Save-AuditEvidence -Name 'CAP-07_MailItemsAccessed'
$cap07 | Format-Table testId,upn,rowCount,status
```

A persistent zero on a known-active regulated mailbox typically indicates Audit Premium is not licensed for that user, the policy throttling has activated, or the user's mailbox is in a tenant where the feature is not available — investigate before stamping `[PASS]` on the cycle.

#### CAP-08 — Sentinel ingestion lag against empirical ceiling (Control 3.9 cross-link)

**Expected:** end-to-end latency from event emission to Sentinel availability is within the documented operational ceiling for the tenant (PRE-04 baseline). **Do not assert against a fabricated "15 min" or "24 h" SLA — Microsoft does not publish a hard audit availability SLA.**

```powershell
$marker = "FSI-1.7-ingest-test-$([guid]::NewGuid())"
$emitTs = (Get-Date).ToUniversalTime()
# (Trigger an action that emits a known RecordType, e.g., open a Copilot session in a test account
# with the marker embedded in the prompt.)

Start-Sleep -Seconds 5400   # 90 min — adjust to the tenant's empirical ceiling

$auditFound = Search-AuditLogPaged `
    -StartDate (Get-Date).AddHours(-3) -EndDate (Get-Date) `
    -RecordTypes @('CopilotInteraction') | Where-Object { $_.AuditData -match $marker }

$auditTs = if ($auditFound) { ($auditFound | Select-Object -First 1).CreationDate } else { $null }

# Sentinel-side query (run in the SIEM with the same marker)
# OfficeActivity | where TimeGenerated > ago(3h) | where Operation == 'CopilotInteraction' and AuditData contains 'marker'
# Record the SentinelTs by hand or via Az.SecurityInsights.

$sentinelTs = $null  # populate from Sentinel query result
$cap08 = [pscustomobject]@{
    testId             = 'CAP-08'
    collectorField     = 'audit.sentinel.endToEndLatencySec'
    marker             = $marker
    emitTsUtc          = $emitTs.ToString('o')
    auditTsUtc         = if ($auditTs) { $auditTs.ToString('o') } else { $null }
    sentinelTsUtc      = if ($sentinelTs) { $sentinelTs.ToString('o') } else { $null }
    auditLatencySec    = if ($auditTs) { ($auditTs - $emitTs).TotalSeconds } else { $null }
    sentinelLatencySec = if ($sentinelTs) { ($sentinelTs - $emitTs).TotalSeconds } else { $null }
    empiricalCeilingSec = 5400   # PRE-04 baseline; recalibrate per tenant
    status             = if ($sentinelTs -and ($sentinelTs - $emitTs).TotalSeconds -le 5400) { 'PASS' } else { 'FAIL' }
    capturedAtUtc      = (Get-Date).ToUniversalTime().ToString('o')
}
$cap08 | Save-AuditEvidence -Name 'CAP-08_SentinelIngestionLag'
$cap08
```

### PRES — Preservation-tier tests (the central FSI test)

#### PRES-00 — Preservation pipeline existence (cycle-stopping)

**Expected — broker-dealer / FCM / swap dealer / CPO scope:** the firm operates at least one of PRES-A, PRES-B, or PRES-C as its 17a-4(f) preservation pipeline for the Copilot / agent communications record set, and the path is recorded in `scope.preservationPath`.

```powershell
$pres00 = [pscustomobject]@{
    testId           = 'PRES-00'
    collectorField   = 'preservation.pathDeclared'
    regulatedProfile = 'broker-dealer'   # echo from PRE-01
    pathDeclared     = 'A'               # one of A / B / C
    status           = if ($pres00PathDeclared -in @('A','B','C')) { 'PASS' } else { 'FAIL-CYCLE-STOPPING' }
    capturedAtUtc    = (Get-Date).ToUniversalTime().ToString('o')
}
$pres00 | Save-AuditEvidence -Name 'PRES-00_PathDeclared'
```

**Explicit fail rule.** If the firm is broker-dealer, FCM, swap dealer, or CPO **and** no preservation tier is declared, the verification cycle FAILS at PRES-00. There is no compensating control. The Microsoft 365 Audit retention horizon (including the 10-Year Audit Log Retention add-on) is operational telemetry retention, not 17a-4(f) preservation, and cannot be substituted for the preservation tier.

#### PRES-A — Azure immutable blob storage path

**Expected:** an Azure Blob container exists with a **locked** time-based retention policy whose period meets or exceeds the regulatory floor for the record set (3 years for SEC 17a-4(b)(4) communications, 5 years for CFTC 1.31, 6 years for SEC 17a-4(a) financial records); an export pipeline writes the Copilot / agent communications record set to the container; Cohasset Associates attestation evidence (or equivalent independent attestation) for SEC 17a-4(f) / CFTC 1.31 / FINRA 4511 is on file and current.

```powershell
$presA = foreach ($container in (Get-Content '.\inputs\preservation-containers.txt')) {
    $parts = $container -split '/'
    $rg, $sa, $c = $parts[0], $parts[1], $parts[2]
    $pol = Get-AzStorageContainerImmutabilityPolicy `
        -ResourceGroupName $rg -StorageAccountName $sa -ContainerName $c -ErrorAction SilentlyContinue

    [pscustomobject]@{
        testId            = 'PRES-A'
        collectorField    = "preservation.azure.$sa.$c.policyState"
        container         = "$sa/$c"
        policyState       = $pol.State                                  # 'Locked' or 'Unlocked'
        retentionDays     = $pol.ImmutabilityPeriodSinceCreationInDays
        regulatoryFloorDays = 1095                                       # 3 years; raise per record set
        cohassetAttestationOnFile = $true                                # echo from records evidence
        cohassetAttestationDate   = '2025-09-12'                         # echo from records evidence
        status            = if ($pol.State -eq 'Locked' -and $pol.ImmutabilityPeriodSinceCreationInDays -ge 1095) { 'PASS' } else { 'FAIL' }
        capturedAtUtc     = (Get-Date).ToUniversalTime().ToString('o')
    }
}
$presA | Save-AuditEvidence -Name 'PRES-A_ImmutabilityPolicy'
$presA | Format-Table testId,container,policyState,retentionDays,status
```

- `[PASS]` only if `policyState = Locked`, retention meets the regulatory floor for the record set, the export pipeline is verified to write to the container (separate retrieval evidence in the weekly cadence), and a current Cohasset (or equivalent) attestation is on file.
- `[FAIL]` if `policyState = Unlocked` (still mutable), retention is below the floor, the pipeline is not verified, or the attestation is absent or stale.

#### PRES-B — Third-party 17a-4-attested archive path

**Expected:** for firms relying on Smarsh Enterprise Archive, Global Relay Archive, Proofpoint Enterprise Archive, Mimecast Cloud Archive, Bloomberg Vault, or Veritas Enterprise Vault.cloud, the journaling / connector path is configured and active; the vendor's 17a-4-attested SLA documentation is on file and current; and a retrieval test was completed in the prior quarter.

```powershell
$presB = [pscustomobject]@{
    testId                       = 'PRES-B'
    collectorField               = 'preservation.thirdPartyArchive.vendor'
    vendor                       = 'Smarsh Enterprise Archive'   # one of the six listed
    journalConnectorConfigured   = $true
    journalConnectorActive       = $true                          # verified by test message round-trip in last 24 h
    attestedSlaOnFile            = $true
    attestedSlaDate              = '2025-11-04'
    lastRetrievalTestUtc         = '2026-02-18T15:42:00Z'
    retrievalTestPassed          = $true
    status                       = if ($journalConnectorActive -and $attestedSlaOnFile -and $retrievalTestPassed) { 'PASS' } else { 'FAIL' }
    capturedAtUtc                = (Get-Date).ToUniversalTime().ToString('o')
}
$presB | Save-AuditEvidence -Name 'PRES-B_ThirdPartyArchive'
$presB
```

- `[PASS]` if the journal/connector is verified active, the vendor's 17a-4-attested SLA documentation is current, and a retrieval test was completed in the last quarter.
- `[FAIL]` if the connector is inactive, attestation is missing/stale, or the retrieval test is overdue.

#### PRES-C — Audit-trail alternative path (post-October 2022 amendment, 3 May 2023 compliance)

**Expected — firms relying on the 17a-4(f) audit-trail alternative:** the system preserves original records and a complete time-stamped audit trail of all modifications and deletions, **plus** a Designated Executive Officer (DEO) representation **or** a Designated Third Party (DTP) undertaking is on file, **plus** an independent records-management assessment has been performed within the last 12 months.

```powershell
$presC = [pscustomobject]@{
    testId                       = 'PRES-C'
    collectorField               = 'preservation.auditTrailAlternative'
    deoRepresentationOnFile      = $true   # OR
    dtpUndertakingOnFile         = $false
    deoOrDtpDate                 = '2025-08-21'
    independentAssessmentOnFile  = $true
    independentAssessmentDate    = '2025-09-30'
    independentAssessmentFirm    = 'Cohasset Associates'   # or equivalent independent assessor
    completeAuditTrailVerified   = $true                    # round-trip modify/delete test in the cycle
    status                       = if (($deoRepresentationOnFile -or $dtpUndertakingOnFile) -and $independentAssessmentOnFile -and $completeAuditTrailVerified) { 'PASS' } else { 'FAIL' }
    capturedAtUtc                = (Get-Date).ToUniversalTime().ToString('o')
}
$presC | Save-AuditEvidence -Name 'PRES-C_AuditTrailAlternative'
$presC
```

The independent records-management assessment is required by the October 2022 amendments to Rule 17a-4(f) and is **annual**. A lapsed assessment is a `[FAIL]` even if the DEO representation / DTP undertaking is current.

### CONT — Content-tier tests

#### CONT-01 — eDiscovery (Premium) prompt + response body retrievable (Control 1.19 cross-link)

**Expected:** an eDiscovery (Premium) search across a test custodian for `CopilotInteraction` events returns reviewable items whose body contains the prompt text and response text — not only audit metadata.

Run from the Microsoft Purview portal → eDiscovery → Premium → create a test case → add a test custodian known to have used Copilot in the prior 7 days → collect against the Copilot interaction location → review one item.

```powershell
$cont01 = [pscustomobject]@{
    testId                = 'CONT-01'
    collectorField        = 'content.eDiscoveryPremium.bodyRetrievable'
    custodian             = 'jane.doe@contoso.com'
    casesId               = '<eDiscovery case GUID>'
    itemsCollected        = 14
    bodyRetrievableSample = $true   # operator confirms prompt + response body present in reviewed item
    status                = if ($bodyRetrievableSample -and $itemsCollected -gt 0) { 'PASS' } else { 'FAIL' }
    capturedAtUtc         = (Get-Date).ToUniversalTime().ToString('o')
}
$cont01 | Save-AuditEvidence -Name 'CONT-01_eDiscoveryRetrieval'
$cont01
```

#### CONT-02 — DSPM for AI surfaces transcripts for `CopilotInteraction` events (Control 1.6 cross-link)

**Expected:** in the Microsoft Purview portal → DSPM for AI experience, a compliance manager can view chat transcripts directly for a `CopilotInteraction` event identified in the audit log.

Pick one `CopilotInteraction` event from CAP-03 output, navigate to DSPM for AI → Activity explorer → filter to the user and time window, open the corresponding transcript view, and confirm prompt + response body is visible.

```powershell
$cont02 = [pscustomobject]@{
    testId                  = 'CONT-02'
    collectorField          = 'content.dspmForAi.transcriptVisible'
    sourceCopilotInteractionId = '<Messages[].ID from CAP-03 row>'
    transcriptVisible       = $true
    status                  = if ($transcriptVisible) { 'PASS' } else { 'FAIL' }
    capturedAtUtc           = (Get-Date).ToUniversalTime().ToString('o')
}
$cont02 | Save-AuditEvidence -Name 'CONT-02_DSPMTranscript'
$cont02
```

#### CONT-03 — Communication Compliance can review AI-generated messages (Control 1.10 cross-link)

**Expected:** an active Communication Compliance policy with AI-generated message scope returns reviewable items in the policy's queue, and the reviewer can take a supervisory action (acknowledge, escalate, resolve).

```powershell
$cont03 = [pscustomobject]@{
    testId             = 'CONT-03'
    collectorField     = 'content.communicationCompliance.queueActive'
    policyName         = 'CC-AI-Generated-Communications'
    queueDepth         = 47
    reviewerActionTaken = $true   # operator acknowledges one item in the cycle
    status             = if ($queueDepth -ge 0 -and $reviewerActionTaken) { 'PASS' } else { 'FAIL' }
    capturedAtUtc      = (Get-Date).ToUniversalTime().ToString('o')
}
$cont03 | Save-AuditEvidence -Name 'CONT-03_CommComplianceReview'
$cont03
```

#### CONT-04 — Worked examiner reconstruction example

**Expected:** the canonical FINRA / SEC examiner question — *"Show me the audit trail and the underlying communication content for AI-generated communications to customer X between dates Y and Z"* — produces a complete reconstruction filed in the cycle evidence pack.

1. Pick one AI agent and one date range (rotate quarterly).
2. Run a complete reconstruction: `Search-AuditLogPaged` against `CopilotInteraction` + `ConnectedAIAppInteraction` for the agent, the user(s), and the date range.
3. Resolve each `Messages[].ID` from the audit results to its body via eDiscovery (Premium) or DSPM for AI.
4. Cross-reference any DLP override events (Control 1.5) by joining on user, time window, and `Messages[].ID`.
5. Export results, SHA-256 hash, copy to immutable storage (PRES-A) or third-party archive (PRES-B).
6. File the search query, exported records, hash, and a chain-of-custody note in the audit binder.
7. Brief the compliance team on retrieval time.

```powershell
$cont04 = [pscustomobject]@{
    testId             = 'CONT-04'
    collectorField     = 'content.examinerReconstruction.completedQuarter'
    cycle              = '2026-Q2'
    agentId            = 'CopilotStudio.Declarative.<guid>'
    dateRange          = '2026-01-15..2026-02-28'
    auditRowsRetrieved = 312
    bodyRowsResolved   = 312
    completionMinutes  = 47
    status             = if ($auditRowsRetrieved -gt 0 -and $bodyRowsResolved -eq $auditRowsRetrieved) { 'PASS' } else { 'FAIL' }
    capturedAtUtc      = (Get-Date).ToUniversalTime().ToString('o')
}
$cont04 | Save-AuditEvidence -Name 'CONT-04_ExaminerReconstruction'
$cont04
```

### SOV — Sovereign cloud tests

#### SOV-01 — Audit Premium availability per current Microsoft Learn

**Expected:** for tenants in GCC / GCC High / DoD, Audit Premium availability (including `MailItemsAccessed`) is verified against the current Microsoft Learn sovereign-cloud parity documentation at cycle start. Document the observed state, not the assumed state.

#### SOV-02 — PAYG availability per current Microsoft Learn

**Expected:** PAYG billing model availability for `AIAppInteraction` and the PAYG portion of `ConnectedAIAppInteraction` is verified for the sovereign cloud at cycle start.

#### SOV-03 — Sign-in agent identity filter live UI affordance

**Expected:** the live Entra Sign-in logs UI filter affordance for agent identities is verified in the sovereign cloud's Entra admin center. Do not assume the prior `Is Agent = Yes` chip; the UI exposes four sign-in *types* (Interactive user / Non-interactive user / Service principal / Managed identity) plus a separate Agent activity log entry on the Monitoring & health page in current revisions, and the chip naming has changed across releases.

#### SOV-04 — IRM-dependent audit features documented as compensating-control gap

**Expected:** IRM-dependent audit features (which are **not available** in any US Gov cloud as of April 2026 — GCC, GCC High, DoD) are documented as a compensating-control gap with a corresponding Sentinel rule, Communication Compliance policy, or DLP rule that supplies the substitute coverage.

```powershell
$sov = [pscustomobject]@{
    testId                = 'SOV'
    collectorField        = 'audit.sovereignParity'
    cloud                 = 'GCCHigh'
    auditPremiumAvailable = $true   # verify against Learn at cycle start
    paygAvailable         = $false  # verify; record as gap if false
    signInFilterLabel     = 'Sign-in type: Service principal'   # observed live label
    irmDependentAuditGapDocumented = $true
    compensatingControlRefs = @('Sentinel rule SR-1.7-IRM-substitute','CC policy CC-AI-IRM-substitute')
    status                = if ($auditPremiumAvailable -and $irmDependentAuditGapDocumented) { 'PASS' } else { 'FAIL' }
    capturedAtUtc         = (Get-Date).ToUniversalTime().ToString('o')
}
$sov | Save-AuditEvidence -Name 'SOV_ParityVariant'
$sov
```

### TAMP — Tamper-resistance test

#### TAMP-01 — Disable-audit attempt produces tamper-evidence and Sentinel alert (Control 3.9 cross-link)

**Expected — execute on a non-prod tenant only:** an attempt to disable unified audit ingestion (`Set-AdminAuditLogConfig -UnifiedAuditLogIngestionEnabled $false`) produces a corresponding event in the tenant audit log and raises a Sentinel alert within the empirical ingestion ceiling.

!!! danger "Non-prod only"
    Never execute the disable command in production. Use a CAB-approved non-prod tenant. Re-enable immediately after the test and confirm CAP-01 returns to `PASS`.

```powershell
# Non-prod tenant only.
Connect-AuditExchangeOnline -Cloud Commercial -UserPrincipalName 'auditor@nonprod.contoso.com'

$preState = Test-UnifiedAuditEnabled
Set-AdminAuditLogConfig -UnifiedAuditLogIngestionEnabled $false -Confirm:$false
$disableTs = (Get-Date).ToUniversalTime()

# Re-enable immediately
Set-AdminAuditLogConfig -UnifiedAuditLogIngestionEnabled $true -Confirm:$false

Start-Sleep -Seconds 5400

$disableEvent = Search-AuditLogPaged `
    -StartDate $disableTs.AddMinutes(-5) -EndDate $disableTs.AddHours(3) `
    -RecordTypes @('ExchangeAdmin') `
    -Operations @('Set-AdminAuditLogConfig')

# Sentinel-side: verify the alert rule defined under Control 3.9 fired against the disable event.
$sentinelAlertFired = $null   # populate from Sentinel incident query

$tamp01 = [pscustomobject]@{
    testId             = 'TAMP-01'
    collectorField     = 'audit.tamper.disableEventCaptured'
    nonProdTenant      = 'nonprod.contoso.com'
    disableEventCount  = $disableEvent.Count
    sentinelAlertFired = $sentinelAlertFired
    status             = if ($disableEvent.Count -gt 0 -and $sentinelAlertFired) { 'PASS' } else { 'FAIL' }
    capturedAtUtc      = (Get-Date).ToUniversalTime().ToString('o')
}
$tamp01 | Save-AuditEvidence -Name 'TAMP-01_DisableAuditTamperEvidence'
$tamp01
```

### JOIN — Cross-source join test

#### JOIN-01 — Single Copilot interaction joinable across all four sources

**Expected:** for a single Copilot interaction picked at random, the same `Messages[].ID` connects:

1. The `CopilotInteraction` audit record (capture tier).
2. The Substrate-stored prompt/response body retrieved via DSPM for AI or eDiscovery (Premium) (content tier).
3. The DLP event in the audit log if any override was triggered (Control 1.5).
4. The Sentinel ingestion record for the same interaction (Control 3.9).

```powershell
# Pick one CopilotInteraction event from CAP-03
$pick = (Search-AuditLogPaged -StartDate (Get-Date).AddDays(-1) -EndDate (Get-Date) -RecordTypes @('CopilotInteraction') | Get-Random -Count 1)
$auditData = $pick.AuditData | ConvertFrom-Json
$messageId = $auditData.Messages[0].ID

# 1. Audit row
$auditRow = $pick

# 2. Substrate body — operator confirms the same MessageId resolves in DSPM for AI Activity explorer / eDiscovery review
$bodyResolved = $true   # operator-confirmed flag

# 3. DLP event — search for the same MessageId in DLP RecordTypes
$dlpRow = Search-AuditLogPaged -StartDate $pick.CreationDate.AddMinutes(-5) -EndDate $pick.CreationDate.AddMinutes(5) `
    -RecordTypes @('DLPEndpoint','ComplianceDLPSharePoint','ComplianceDLPExchange') `
    | Where-Object { $_.AuditData -match $messageId }

# 4. Sentinel — operator runs the corresponding KQL in the SIEM and confirms presence
$sentinelRowPresent = $true   # operator-confirmed flag

$join01 = [pscustomobject]@{
    testId             = 'JOIN-01'
    collectorField     = 'audit.crossSourceJoin.messagesId'
    joinKey            = 'Messages[].ID'
    messageId          = $messageId
    auditRowFound      = [bool]$auditRow
    substrateBodyResolved = $bodyResolved
    dlpRowFound        = [bool]$dlpRow         # may be 0 — record explicitly
    sentinelRowFound   = $sentinelRowPresent
    status             = if ($auditRow -and $bodyResolved -and $sentinelRowPresent) { 'PASS' } else { 'FAIL' }
    capturedAtUtc      = (Get-Date).ToUniversalTime().ToString('o')
}
$join01 | Save-AuditEvidence -Name 'JOIN-01_CrossSourceJoin'
$join01
```

A `dlpRowFound` of `false` is **not** a join failure (the interaction may not have triggered DLP). A `false` on `auditRowFound`, `substrateBodyResolved`, or `sentinelRowFound` is a join failure and a cycle finding.

### Negative tests (run with the cycle)

Each must produce the documented "deny" outcome and surface in the audit log:

| Negative test | Expected outcome | Audit signal |
|---|---|---|
| Account without `Audit Logs` role attempts `Search-UnifiedAuditLog` | Access denied | Sign-in + role-check failure |
| Audit log disable attempt by unauthorized account | Access denied | `Set-AdminAuditLogConfig` denied + alert |
| Audit retention policy delete attempt by `Compliance Admin` only | Access denied (requires Organization Configuration) | Failure event |
| Search a date range older than the policy retention horizon | Returns zero rows / not-found | (No false-positive expected) |
| Tamper with an exported evidence file (modify a byte) | SHA-256 sidecar mismatches at re-hash | (Detection during integrity check) |
| Attempt to delete or shorten a `Locked` immutable retention policy | Operation denied by Azure Storage | Storage diagnostic event |

---

## Section 6 — Evidence Pack

Every cycle, produce and archive these artifacts under naming convention `Control-1.7_{Tenant}_{Artifact}_{YYYYMMDD-HHmm-UTC}.{ext}` with a `.sha256` sidecar for each:

| # | Artifact | Source |
|---|---|---|
| 1 | `CAP-01_AuditConfig.json` | `Test-UnifiedAuditEnabled` |
| 2 | `CAP-02_LicenseEntitlement.csv` + `CAP-02_Summary.json` | `Get-UserAuditEntitlement` loop |
| 3 | `CAP-03_RecordTypeSmoke.json` | RecordType smoke loop |
| 4 | `CAP-04_RetentionCoverage.json` | `Get-UnifiedAuditLogRetentionPolicy` coverage map |
| 5 | `CAP-05_DataverseAudit_{EnvId}.json` | Per environment |
| 6 | `CAP-06_DLPOverrideJustification.json` | Marker round-trip |
| 7 | `CAP-07_MailItemsAccessed.json` | Per regulated mailbox |
| 8 | `CAP-08_SentinelIngestionLag.json` | Marker + dual timestamp |
| 9 | `PRES-00_PathDeclared.json` | Cycle scope echo |
| 10 | `PRES-A_ImmutabilityPolicy.json` (if path A) | `Get-AzStorageContainerImmutabilityPolicy` |
| 11 | `PRES-B_ThirdPartyArchive.json` (if path B) | Vendor SLA + retrieval test record |
| 12 | `PRES-C_AuditTrailAlternative.json` (if path C) | DEO representation / DTP undertaking + independent assessment record |
| 13 | `CONT-01_eDiscoveryRetrieval.json` | eDiscovery (Premium) drill |
| 14 | `CONT-02_DSPMTranscript.json` | DSPM for AI drill |
| 15 | `CONT-03_CommComplianceReview.json` | Communication Compliance drill |
| 16 | `CONT-04_ExaminerReconstruction.csv` + `.json` | Worked example |
| 17 | `SOV_ParityVariant.json` (if applicable) | Sovereign cloud variant |
| 18 | `TAMP-01_DisableAuditTamperEvidence.json` | Non-prod disable rehearsal |
| 19 | `JOIN-01_CrossSourceJoin.json` | Single-interaction trace |
| 20 | `NegativeTests.json` | Negative test matrix results |
| 21 | `Transcript.txt` | `Start-Transcript` from the verification run |
| 22 | `manifest.sha256` | One SHA-256 line per artifact |
| 23 | `attestation.json` | Three-signature attestation chain (Section 1) |

All files are copied to immutable storage at capture time. The attestation references each artifact's SHA-256.

---

## Section 7 — Failure escalation matrix

| Finding | Severity | Escalation |
|---|---|---|
| PRE-* failure | Cycle-stopping | Halt cycle; remediate gate; restart |
| CAP-01 FAIL (audit ingestion off) | P1 | Page Purview Audit Admin; remediate within 4 hours; re-run after 60 min propagation; document gap window |
| CAP-02 FAIL (license entitlement gap) | P2 | Notify license admin; assign 10-year add-on; document silent-downgrade exposure window |
| CAP-03 FAIL (required RecordType zero) | P1 | Open Microsoft support case; document expected vs observed; check PAYG enablement |
| CAP-04 FAIL (retention coverage gap) | P2 | Author missing custom retention policy; verify coverage on next daily run |
| CAP-05 FAIL (Dataverse audit gap) | P2 | Notify Power Platform Admin; remediate per environment |
| CAP-06 / CAP-07 FAIL | P3 | Investigate per playbook §Troubleshooting |
| CAP-08 FAIL (Sentinel lag exceeds ceiling) | P2 | Notify SOC; recalibrate PRE-04 baseline if structural; do not stamp `[PASS]` against a fabricated SLA |
| **PRES-00 FAIL (no preservation tier, broker-dealer / FCM / swap dealer / CPO scope)** | **Cycle-stopping** | **Halt cycle. Notify CCO and DEO. No compensating control exists. Reconstitute preservation pipeline (PRES-A, PRES-B, or PRES-C) before resuming.** |
| PRES-A FAIL (Unlocked policy or sub-floor retention) | P1 | Notify Azure Storage Account Owner; lock policy; re-verify |
| PRES-B FAIL (vendor SLA stale or retrieval test missed) | P1 | Records Management Officer engages vendor; refresh SLA; run retrieval test |
| PRES-C FAIL (assessment lapsed) | P1 | Engage independent records-management assessor; refresh assessment within 30 days |
| CONT-01 / CONT-02 / CONT-03 FAIL | P2 | Investigate content-tier surface; involve Purview Compliance Admin |
| CONT-04 FAIL (reconstruction incomplete) | P1 | Notify Compliance Officer; root-cause and re-run; this is the canonical examiner question |
| SOV-* FAIL | P2 | Document parity gap; ensure compensating controls are in place; re-verify at next quarterly cadence |
| TAMP-01 FAIL (disable not alerted) | P1 | Notify SOC; verify Sentinel rule (Control 3.9); re-rehearse |
| JOIN-01 FAIL | P1 | Trace which tier broke; cross-reference CAP / CONT / Sentinel; do not close until end-to-end join is reproducible |
| Hash chain break (manifest mismatch) | Cycle-stopping | Treat as potential evidence tampering; engage Internal Audit |

---

## Section 8 — Attestation Statement (Template)

```text
Control 1.7 — Comprehensive Audit Logging and Compliance
Tenant: {tenantId}
Cycle: {YYYY-Qn}
Cloud: {Commercial | GCC | GCCHigh | DoD}
Regulated profile: {broker-dealer | FCM | swap dealer | CPO | other}
Preservation path: {A | B | C}
Verification window: {start UTC} – {end UTC}

Verified by:   Capture Owner       — {role: Purview Audit Admin}
Reviewed by:   Preservation Owner  — {role: Records Management Officer}
Approved by:   Compliance          — {role: Compliance Officer / CCO designee}

Statements (capture tier):
1. Unified audit logging is enabled and verified from an Exchange Online PowerShell session
   (sha256 {CAP-01}); the SessionUri matches the expected EXO endpoint.
2. {N} users hold a Copilot license; license entitlement is reconciled (sha256 {CAP-02});
   the gap report lists {0 or actual} users with retention shortfall risk; PAYG enrollment
   is {confirmed | not applicable | gap documented}.
3. Each Copilot RecordType in scope returned non-zero rows, or a documented expected-zero,
   in the smoke test (sha256 {CAP-03}).
4. Custom audit retention policies are in place for every Copilot record type in scope at
   the documented zone horizon (sha256 {CAP-04}).
5. Per-environment Dataverse audit and per-table audit on the Copilot Studio entities
   are enabled for all {N} environments (sha256 {CAP-05}).
6. DLP override justification is captured in the audit log (sha256 {CAP-06}).
7. MailItemsAccessed is firing for the regulated mailbox population (sha256 {CAP-07}).
8. Sentinel end-to-end ingestion latency is within the empirical ceiling of
   {ceilingSec} sec measured for this tenant (sha256 {CAP-08}).

Statements (preservation tier):
9. The firm relies on preservation path {A | B | C} for the Copilot / agent communications
   record set (sha256 {PRES-00}); supporting attestation, vendor SLA, or DEO/DTP and
   independent records-management assessment artifacts are referenced by sha256 in
   {PRES-A | PRES-B | PRES-C}; the path is currently in a passing state.

Statements (content tier):
10. eDiscovery (Premium) collection on a test custodian retrieves prompt and response body
    for CopilotInteraction events (sha256 {CONT-01}).
11. DSPM for AI surfaces transcripts for the sampled CopilotInteraction event
    (sha256 {CONT-02}).
12. Communication Compliance review of AI-generated communications is active and
    reviewer action is observable (sha256 {CONT-03}).
13. The worked examiner reconstruction example for this cycle is filed (sha256 {CONT-04})
    and completed in {N} minutes.

Statements (sovereign / tamper / join):
14. Sovereign cloud parity variant (if applicable) is verified (sha256 {SOV});
    IRM-dependent audit features are documented as compensating-control gaps in any
    US Gov cloud.
15. Tamper-resistance rehearsal on the non-prod tenant produced an audit event for the
    disable attempt and a Sentinel alert (sha256 {TAMP-01}).
16. Cross-source join across CopilotInteraction → Substrate body → DLP (if any) →
    Sentinel resolves on the Messages[].ID join key for the sampled interaction
    (sha256 {JOIN-01}).

This attestation is intended to support — but does not by itself ensure — compliance with
FINRA 4511, FINRA 3110, FINRA 25-07 (RFC), SEC 17a-3, SEC 17a-4 (including 17a-4(f)
October 2022 amendments and 3 May 2023 compliance date), SOX 302/404, GLBA 501(b),
OCC 2011-12, Federal Reserve SR 11-7, and CFTC 1.31. This attestation does not by itself
constitute the 17a-4(f) attestation that the firm's electronic recordkeeping system is
non-rewriteable / non-erasable; that attestation is the role of an independent third party
(e.g., Cohasset Associates) and is referenced in this cycle's preservation evidence rather
than substituted by it. Continued effectiveness requires the operational controls in
Controls 1.5, 1.6, 1.10, 1.19, 2.6, 2.12, 3.4, 3.9 and the cadence in Section 3.

Signatures:
  {CaptureOwner UPN} — {tsUtc} — {method} — {digest}
  {PreservationOwner UPN} — {tsUtc} — {method} — {digest}
  {Compliance UPN} — {tsUtc} — {method} — {digest}
```

---

[Back to Control 1.7](../../../controls/pillar-1-security/1.7-comprehensive-audit-logging-and-compliance.md) | [Portal Walkthrough](portal-walkthrough.md) | [PowerShell Setup](powershell-setup.md) | [Troubleshooting](troubleshooting.md)

---

*Updated: April 2026 | Version: v1.4 | UI Verification Status: Current*
