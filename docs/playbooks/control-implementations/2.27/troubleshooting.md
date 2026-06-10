# Troubleshooting — Control 2.27: Consumption-Entitlement Governance

> **Scope.** This playbook covers operational failure modes for the consumption-entitlement program: security-group registry admission gating, agent pathway classification, the switch-on-pathway entitlement contract (including zero-rating resolution), the two policy objects (PAYG vs prepaid credit), per-agent spend caps, the pre-enforcement coverage-gap analysis, and retention / SIEM forwarding. It is the diagnostic companion to the [Control 2.27 specification](../../../controls/pillar-2-management/2.27-consumption-entitlement-governance.md), the [portal walkthrough](./portal-walkthrough.md), the [PowerShell setup pack](./powershell-setup.md), and the [verification-testing pack](./verification-testing.md). The companion **[Copilot Billing Governance](https://judeper.github.io/FSI-AgentGov-Solutions/solutions/copilot-billing-governance/)** 🔎 solution implements the engine referenced throughout.
>
> **Availability hedging (June 2026 rollout).** Microsoft's Copilot Credits consumption-billing model becomes the operative metering path for several agent surfaces from **June 16, 2026** — scheduled per the Microsoft 365 roadmap (feature 559017) and Microsoft Learn ("use-work-iq"), verified June 2026 — the same day the Work IQ API moves to Copilot-Credits consumption billing. Tenant ceilings (PAYG **50** / credit **10**) 🔎, per-feature **credit rates**, **$0.01 per credit**, and the **25,000-credits-per-month** prepaid pack 🔎 are reference values that should be re-verified against Microsoft licensing documentation before they are used as examiner evidence. Whether a public **write API** for credit-policy / per-agent-cap enforcement exists is resolved: as of June 2026 there is **no public write API** (per-agent caps are Power Platform admin-center UI-managed, per Microsoft Learn, "manage-copilot-studio-messages-capacity"), so a cap **degrades to detect-and-alert** rather than a hard-stop; should Microsoft ship one, caps can be upgraded to a hard-stop.
>
> **Regulatory framing.** Procedures here **support compliance with** — they do not by themselves satisfy — SOX §404 (IT general controls over spend authorization), GLBA 501(b) (Safeguards Rule), FINRA Rule 4511 (books and records, six-year retention for member firms), and SEC Rule 17a-4(b)(4) (records preservation), and **contribute to** third-party AI spend oversight informed by OCC Bulletin 2023-17. This control governs the entitlement **decision**; implementation requires control-owner sign-off, and no automated procedure removes the obligation to attest to control effectiveness.
>
> **Model-risk caveat.** OCC Bulletin 2026-13 (formerly OCC 2011-12) and Federal Reserve SR 26-2 (formerly SR 11-7) are model-risk guidance that, in their 2026 restatements, expressly exclude generative and agentic AI; they are **adjacent context only** and are not the primary spend authority for this control.

---

## Table of contents

- [§0. Triage tree — symptom → pillar](#0-triage-tree-symptom-pillar)
- [§1. Diagnostic data collection (`Get-Cbg227*` helpers, queries, evidence floor)](#1-diagnostic-data-collection)
- [§2. Pillar GROUP-REJECTED — mail-enabled / non-security group rejected by the registry](#2-pillar-group-rejected)
- [§3. Pillar PATHWAY-UNMAPPED — agent classified `unmapped` (fail-open anomaly)](#3-pillar-pathway-unmapped)
- [§4. Pillar ZERORATING-FAILCLOSED — licensed Copilot Studio user resolves fail-closed](#4-pillar-zerorating-failclosed)
- [§5. Pillar PAYG-NO-HARDSTOP — budget-alert vs expected hard-stop confusion](#5-pillar-payg-no-hardstop)
- [§6. Pillar CREDIT-CHATONLY — credit policy Chat-only surprise on SharePoint](#6-pillar-credit-chatonly)
- [§7. Pillar COVERAGEGAP-COUNTS — coverage-gap counts look wrong](#7-pillar-coveragegap-counts)
- [§8. Pillar CAP-NOENFORCE — per-agent cap not enforcing (no write API → detect-and-alert)](#8-pillar-cap-noenforce)
- [§9. Pillar SIEM-NO-EVIDENCE — decisions / coverage-gap not landing in SIEM](#9-pillar-siem-no-evidence)
- [§10. Runbook RB-01 — Coverage-gap sign-off requested before enforcement was activated](#10-runbook-rb-01)
- [§11. Runbook RB-02 — Broadly-shared metered agent draws down spend faster than alerts react](#11-runbook-rb-02)
- [§12. Runbook RB-03 — Bulk reclassification after the June 16 2026 Work IQ consumption-billing switch](#12-runbook-rb-03)
- [§X. Recovery and post-incident attestation refresh](#x-recovery-and-post-incident-attestation-refresh)

---

## §0. Triage tree — symptom → pillar

Use this table as the first stop for any reported issue. It maps an observed symptom to the most likely pillar (and to a runbook where the symptom is high-severity or examiner-visible). Move to the matching pillar section for diagnostic queries and resolution patterns.

### 0.1 Symptom → pillar map

| # | Symptom (what the reporter said) | Most likely pillar | Severity floor | Runbook? |
|---|----------------------------------|--------------------|----------------|----------|
| S-01 | "I added a group to the registry but **it was rejected / did not save**." | [§2 GROUP-REJECTED](#2-pillar-group-rejected) | SEV-3 | — |
| S-02 | "The registry check reports **mail-enabled scope groups** even though I picked security groups." | [§2 GROUP-REJECTED](#2-pillar-group-rejected) | SEV-2 | — |
| S-03 | "An agent shows pathway **`unmapped`** in the classification report." | [§3 PATHWAY-UNMAPPED](#3-pillar-pathway-unmapped) | SEV-3 | — |
| S-04 | "Dozens of agents are **`unmapped`** after the latest run." | [§3 PATHWAY-UNMAPPED](#3-pillar-pathway-unmapped) | SEV-2 | [RB-03](#12-runbook-rb-03) |
| S-05 | "A **Copilot-licensed** user is being **blocked / fail-closed** on a Copilot Studio agent." | [§4 ZERORATING-FAILCLOSED](#4-pillar-zerorating-failclosed) | SEV-2 | — |
| S-06 | "After we set `-ZeroRatingResolved:$false`, **most `mcp-cs` users fail-closed**." | [§4 ZERORATING-FAILCLOSED](#4-pillar-zerorating-failclosed) | SEV-2 | — |
| S-07 | "We set a PAYG budget but spend **kept going past it** — it didn't stop." | [§5 PAYG-NO-HARDSTOP](#5-pillar-payg-no-hardstop) | SEV-2 | [RB-02](#11-runbook-rb-02) |
| S-08 | "Finance expected the PAYG policy to **hard-cap** spend; it only alerted." | [§5 PAYG-NO-HARDSTOP](#5-pillar-payg-no-hardstop) | SEV-3 | [RB-02](#11-runbook-rb-02) |
| S-09 | "A **SharePoint-grounded** agent is consuming spend even though we're on the **credit** policy." | [§6 CREDIT-CHATONLY](#6-pillar-credit-chatonly) | SEV-3 | — |
| S-10 | "Our credit policy hard-stop didn't apply to a **SharePoint** agent." | [§6 CREDIT-CHATONLY](#6-pillar-credit-chatonly) | SEV-3 | — |
| S-11 | "The coverage-gap **would-be-blocked count looks wrong** (too high / too low / zero)." | [§7 COVERAGEGAP-COUNTS](#7-pillar-coveragegap-counts) | SEV-2 | — |
| S-12 | "Coverage-gap rows show a **truncated** blocked-UPN list." | [§7 COVERAGEGAP-COUNTS](#7-pillar-coveragegap-counts) | SEV-4 | — |
| S-13 | "We set a per-agent cap but spend **is not being stopped** at the cap." | [§8 CAP-NOENFORCE](#8-pillar-cap-noenforce) | SEV-3 | — |
| S-14 | "An auditor asked which Zone 3 caps are **hard-stops** vs **detect-and-alert**." | [§8 CAP-NOENFORCE](#8-pillar-cap-noenforce) | SEV-3 | — |
| S-15 | "The SIEM dashboard for entitlement decisions shows **zero events for 24+ hours**." | [§9 SIEM-NO-EVIDENCE](#9-pillar-siem-no-evidence) | SEV-2 | — |
| S-16 | "An examiner asked for the coverage-gap evidence and **enforcement was already on**." | [§7 COVERAGEGAP-COUNTS](#7-pillar-coveragegap-counts) | SEV-1 | [RB-01](#10-runbook-rb-01) |

### 0.2 Severity matrix (Control 2.27 specific)

| Severity | Definition (this control) | Examples | Page first |
|----------|---------------------------|----------|-----------|
| **SEV-1** | Enforcement activated without a signed-off coverage gap; or examiner request open with no answer; or in-scope users blocked from production metered agents | S-16; enforcement turned on before sign-off | AI Governance Lead → CISO |
| **SEV-2** | Governance signal lost > 24 h; or > 5 agents / cohorts in a non-compliant or mis-scoped state; uncontrolled spend trend | S-02, S-04, S-05, S-06, S-07, S-11, S-15 | AI Governance Lead |
| **SEV-3** | Single-agent / single-policy issue, control still operating in aggregate | S-01, S-03, S-08, S-09, S-10, S-13, S-14 | AI Administrator |
| **SEV-4** | Cosmetic / sample-truncation / single-user UX | S-12 | Power Platform Admin |

**Aggravating factors that raise severity by one level:**

- The affected agent is **Zone 3 (Enterprise)** — it touches production data or customer records.
- The issue surfaces **during an active examiner engagement** (FINRA, SEC, OCC, FRB) or in the 30 days preceding a scheduled exam.
- The issue affects **more than one business unit's** agents simultaneously (suggests a systemic registry or classification root cause).
- The control has already been cited or self-disclosed in a prior MRA / MRIA.

### 0.3 Pre-escalation checklist (complete before paging on-call)

Complete all eight items before paging the AI Governance Lead or escalating beyond the owning admin. Capture the answers — examiners will ask whether triage was orderly.

1. [ ] Confirmed the issue against the **Last UI Verified** date in `2.27-consumption-entitlement-governance.md`. Consumption-billing surfaces are changing during the June 2026 rollout; the procedure may be stale.
2. [ ] Captured the exact symptom text from the reporter (screenshot, ticket ID, UTC timestamp).
3. [ ] Identified the affected agent(s) by `objectId` and the affected user(s) by UPN.
4. [ ] Checked tenant health and Message Center for "Microsoft Copilot Studio", "Copilot Credits", and "Power Platform pay-as-you-go" advisories.
5. [ ] Ran the **§1.1 baseline diagnostic** (`Get-Cbg227Health`) and saved the JSON output to the incident folder.
6. [ ] Identified which **zone** (1 / 2 / 3) the agent is in and which **pathway** it classified to.
7. [ ] Confirmed the tenant context and operating cloud before applying remediation.
8. [ ] Started the **examiner artifact preservation** procedure (§0.4) if severity is SEV-1 or SEV-2.

### 0.4 Examiner artifact preservation (mandatory for SEV-1 / SEV-2)

Examiners routinely request "the state of the control at the time the incident was discovered." Remediation destroys that state. Preserve it first.

1. Export the current `fsi_cbgentitlementmaterialized` decisions and `fsi_cbgcoveragegap` rows for the affected agent(s) (pre-remediation).
2. Capture the registry state (`fsi_cbgapprovedgrouppolicy`) and a Microsoft Graph property snapshot (`securityEnabled`/`mailEnabled`) for the affected scope groups.
3. Capture the policy inventory (`Get-BillingPolicyInventory.ps1` output) for both policy objects with their ceilings.
4. Capture the input fixtures / signals (`configuredTier`, `createdIn`) that produced the disputed classification.
5. Note the operator initiating remediation, in UTC, in the incident ticket.

These five artifacts together support the SEC 17a-4(b)(4) / FINRA 4511 evidentiary floor for "state at time of detection."

---

## §1. Diagnostic data collection

This section defines the standard diagnostic surface for Control 2.27: a small set of `Get-Cbg227*` helpers, a query catalog, and an evidence floor. Every pillar (§2–§9) and runbook (§10–§12) references items from this section; do not invent ad-hoc queries during an incident — use the catalog so the evidence pack stays comparable across incidents.

### 1.1 Diagnostic helper functions (`Get-Cbg227*`)

Add these to your incident-response module. They wrap the cmdlets in [`./powershell-setup.md`](./powershell-setup.md) with consistent JSON output suitable for evidence preservation. They **read** state; they do not write.

```powershell
# Get-Cbg227Health — top-level snapshot. Run first on every incident.
function Get-Cbg227Health {
    [CmdletBinding()]
    param(
        [string]$IncidentId,
        [string]$EnvironmentUrl,
        [string]$EvidencePath = ".\evidence"
    )
    $inv = Get-BillingPolicyInventory -EnvironmentUrl $EnvironmentUrl -PayAsYouGoCeiling 50 -CreditCeiling 10
    [ordered]@{
        IncidentId        = $IncidentId
        TimestampUtc      = (Get-Date).ToUniversalTime().ToString('o')
        Tenant            = (Get-MgContext).TenantId
        Cloud             = (Get-MgContext).Environment
        PaygPolicyPresent = [bool]$inv.PayAsYouGo
        CreditPolicyPresent = [bool]$inv.Credit
        PaygCeiling       = 50    # verify current value 🔎
        CreditCeiling     = 10    # verify current value 🔎
        ScopeGroupCount   = (Get-Cbg227ScopeGroups).Count
        MailEnabledScopeGroups = (Get-Cbg227ScopeGroups | Where-Object { $_.MailEnabled }).Count
    }
}
```

```powershell
# Get-Cbg227ScopeGroups — registry groups with their Graph security/mail properties.
function Get-Cbg227ScopeGroups {
    [CmdletBinding()] param()
    # Reads fsi_cbgapprovedgrouppolicy, then resolves each group's properties via Graph.
    Get-CbgApprovedGroupPolicy |
        ForEach-Object {
            $g = Get-MgGroup -GroupId $_.GroupId -Property "id,displayName,securityEnabled,mailEnabled,groupTypes" -ErrorAction SilentlyContinue
            [pscustomobject]@{
                GroupId        = $g.Id
                DisplayName    = $g.DisplayName
                GroupLayer     = $_.GroupLayer      # Maker / Audience / Billing
                SecurityEnabled= $g.SecurityEnabled
                MailEnabled    = $g.MailEnabled
                IsUnified      = ($g.GroupTypes -contains 'Unified')
                AdmissionOk    = ($g.SecurityEnabled -and -not $g.MailEnabled)
            }
        }
}
```

```powershell
# Get-Cbg227Decision — replay one (agent,user) decision from the materialized cache.
function Get-Cbg227Decision {
    [CmdletBinding()] param([string]$AgentId, [string]$UserUpn)
    Get-CbgEntitlementMaterialized -AgentId $AgentId -UserUpn $UserUpn |
        Select-Object AgentId, UserUpn, Pathway, Decision, BlockReason, SpendScope,
                      ZeroRatingResolved, SourcePolicy, TtlExpiresAt
}
```

```powershell
# Get-Cbg227CoverageGap — per-agent coverage-gap rows (monitor-only flag included).
function Get-Cbg227CoverageGap {
    [CmdletBinding()] param([string]$AgentId)
    Get-CbgCoverageGap -AgentId $AgentId |
        Select-Object AgentId, Pathway, EligibleUsers, BlockedUsersCount,
                      BlockReasonSummary, SpendScope, GroupSizePartition, MonitorOnly, RetainUntil
}
```

> **Note.** The `Get-Cbg227*` helpers are diagnostic — they read state. Remediation must be done with the `Invoke-EntitlementEvaluation.ps1` engine and the registry / cap record edits in [`./powershell-setup.md`](./powershell-setup.md) (diagnostic and remediation operators are separable for audit).

### 1.2 Query catalog (Graph + Dataverse OData)

| ID | Purpose | Query | Notes |
|----|---------|-------|-------|
| Q-01 | Scope-group property check | `GET /v1.0/groups/{id}?$select=id,displayName,securityEnabled,mailEnabled,groupTypes` | Admission gate requires `securityEnabled = true` **and** `mailEnabled = false` |
| Q-02 | All scope groups in registry | `GET {env}/api/data/v9.2/fsi_cbgapprovedgrouppolicies?$select=fsi_groupid,fsi_grouplayer` | Logical names are all-lowercase, no word underscores |
| Q-03 | Materialized decision for one pair | `GET {env}/api/data/v9.2/fsi_cbgentitlementmaterializeds?$filter=fsi_agentid eq '{id}' and fsi_userupn eq '{upn}'` | Returns pathway, decision, block reason, `fsi_zeroratingresolved` |
| Q-04 | Coverage-gap rows (monitor-only check) | `GET {env}/api/data/v9.2/fsi_cbgcoveragegaps?$select=fsi_agentid,fsi_pathway,fsi_blockeduserscount,fsi_monitoronly` | All rows should show `fsi_monitoronly = true` before enforcement |
| Q-05 | User Copilot license read | `GET /v1.0/users/{upn}/licenseDetails?$select=skuPartNumber` | Match `*COPILOT*` SKU; absence drives **Block – Missing license** on metered pathways |
| Q-06 | Agent pathway classification | `Invoke-EntitlementEvaluation.ps1 -InputPath <inputs.json>` (read the `pathway` field) | `configuredTier` authoritative first; `createdIn` fallback |
| Q-07 | Policy inventory vs ceilings | `Get-BillingPolicyInventory.ps1 -EnvironmentUrl {url} -PayAsYouGoCeiling 50 -CreditCeiling 10` | Confirms both policy objects and the `fsi_spendscope` surfaces |

### 1.3 Evidence-floor for any 2.27 incident (E-01 .. E-07)

| ID | Artifact | Source | Retention |
|----|----------|--------|-----------|
| E-01 | `Get-Cbg227Health` JSON snapshot at detection | §1.1 | 6 years (FINRA 4511) |
| E-02 | `Get-Cbg227ScopeGroups` registry + Graph property snapshot | §1.1 / Q-01 | 6 years |
| E-03 | `Get-Cbg227Decision` for each affected `(agent, user)` | §1.1 / Q-03 | 6 years |
| E-04 | `Get-Cbg227CoverageGap` rows for affected agents (pre-remediation) | §1.1 / Q-04 | 6 years |
| E-05 | `Get-BillingPolicyInventory` output (both policies + ceilings) | Q-07 | 6 years |
| E-06 | Input signals (`configuredTier`, `createdIn`) that produced the classification | Upstream fixtures | 6 years |
| E-07 | Operator identity + UTC timestamp of every remediation step | Incident ticket | 6 years |

---

## §2. Pillar GROUP-REJECTED

**One-line:** a security group added to the admission-gated registry (`fsi_cbgapprovedgrouppolicy`) is rejected — or silently ignored at evaluation time — because it is **not `securityEnabled`** or **is `mailEnabled`**.

### 2.1 Symptom catalog

| Code | Symptom | First responder |
|------|---------|-----------------|
| P2-S1 | Registry add fails validation when saving a group | Entra User Admin |
| P2-S2 | Group saved, but the registry property check reports `mailEnabled` scope groups (VC-2 fails) | AI Administrator |
| P2-S3 | A cohort that "should be in credit scope" is not being granted (users fail-closed) | AI Administrator |
| P2-S4 | Microsoft 365 Group added expecting it to scope entitlement | Entra User Admin |

### 2.2 Root cause matrix (symptom → cause)

| RC | Description | Likelihood | How to confirm |
|----|-------------|-----------|----------------|
| RC-A | Group is a **Microsoft 365 Group** (`groupTypes` contains `Unified`) — these are mail-enabled | High | Q-01: `mailEnabled = true`, `groupTypes` has `Unified` |
| RC-B | Group is a **mail-enabled security group** | High | Q-01: `securityEnabled = true` **and** `mailEnabled = true` |
| RC-C | Group is a distribution list (not security-enabled) | Medium | Q-01: `securityEnabled = false` |
| RC-D | Correct group, but the **wrong object ID** was recorded in the registry | Medium | Q-02 vs Q-01 — registry `fsi_groupid` does not match the intended group |
| RC-E | Group became mail-enabled **after** registration (drift) | Low | Q-01 now shows `mailEnabled = true`; was false at registration |

### 2.3 Diagnostic queries

```powershell
# Which registered groups fail admission (securityEnabled AND NOT mailEnabled)?
Get-Cbg227ScopeGroups | Where-Object { -not $_.AdmissionOk } |
  Format-Table DisplayName, GroupLayer, SecurityEnabled, MailEnabled, IsUnified

# Confirm a single candidate group before registering it
Get-MgGroup -GroupId <objectId> -Property "displayName,securityEnabled,mailEnabled,groupTypes" |
  Select-Object DisplayName, SecurityEnabled, MailEnabled, GroupTypes
```

A group is admissible only when `SecurityEnabled = True` **and** `MailEnabled = False`. A `GroupTypes` value containing `Unified` is a Microsoft 365 Group and is always mail-enabled.

### 2.4 Resolution steps

1. For RC-A / RC-B / RC-C, **create a dedicated security-only group** (Entra → Groups → New group → **Security**, mail-enabled **off**) and move the members into it. You cannot convert a Microsoft 365 Group or a mail-enabled security group into a non-mail-enabled security group in place.
2. Update the registry row (`fsi_cbgapprovedgrouppolicy`) to point at the new group's object ID and the correct **scope role** (credit-scope / api-audience / billing-policy).
3. For RC-D, correct the `fsi_groupid` in the registry row.
4. For RC-E (drift), remove the now-mail-enabled group from the registry and replace it with a security-only group; record the drift in the incident ticket.
5. Re-run the registry property check and confirm **zero** mail-enabled scope groups (VC-2).

### 2.5 Verification

- `Get-Cbg227ScopeGroups | Where-Object { -not $_.AdmissionOk }` returns **zero rows**.
- The verification-testing assertion behind manifest check `2.27.d` (`Get-MgGroup` property check) passes. See [`./verification-testing.md`](./verification-testing.md).

### 2.6 Cross-links

- Portal: [`./portal-walkthrough.md`](./portal-walkthrough.md) §3 — Register the admission-gated security-group registry.
- PowerShell: [`./powershell-setup.md`](./powershell-setup.md) — `Get-MgGroup` property helper and registry add.

---

## §3. Pillar PATHWAY-UNMAPPED

**One-line:** an agent classifies to **`unmapped`** because `configuredTier` and `createdIn` are both missing or contradictory. By design this **fails open with an anomaly** — a detection defect must not deny a user — but each `unmapped` agent must be triaged, not left silent.

!!! warning "Fail-Open Is Intentional — Do Not 'Fix' It by Blocking"
    `unmapped → Fail-open - Anomaly` is the correct designed behavior: the user is permitted and an anomaly is recorded. Do **not** reconfigure the engine to block `unmapped` agents; that would deny users for a classifier defect. The objective is **zero silent denials** plus a triaged anomaly with a follow-up owner.

### 3.1 Symptom catalog

| Code | Symptom | First responder |
|------|---------|-----------------|
| P3-S1 | A single new agent shows pathway `unmapped` | AI Administrator |
| P3-S2 | Many agents flipped to `unmapped` after an input refresh | AI Governance Lead |
| P3-S3 | An agent that was `none`/`mcp-cs` yesterday is now `unmapped` | AI Administrator |
| P3-S4 | `unmapped` agents have no follow-up owner recorded (VC-3 gap) | AI Governance Lead |

### 3.2 Root cause matrix (symptom → cause)

| RC | Description | Likelihood | How to confirm |
|----|-------------|-----------|----------------|
| RC-A | `configuredTier` not yet produced (Work IQ usage detection hasn't run for the agent) | High (new agents) | Input fixture shows empty/blank `configuredTier` |
| RC-B | `createdIn` missing (Azure Resource Graph inventory stale) | High | Input fixture shows empty `createdIn` |
| RC-C | Contradictory signals (e.g., `createdIn` = Copilot Studio but an unrecognized `configuredTier` string) | Medium | Both present but neither maps cleanly |
| RC-D | Upstream sibling solution not catalog-registered yet; engine running on fixtures | Medium | `copilot-agent-inventory` / `work-iq-usage-detection` not deployed |
| RC-E | June 16 2026 consumption-billing switch (scheduled per M365 roadmap 559017 / Learn "use-work-iq") may change the `configuredTier` vocabulary | Situational (around GA) | Cluster of `unmapped` dated near the switch — see [RB-03](#12-runbook-rb-03) |

### 3.3 Diagnostic queries

```powershell
# List unmapped agents from the latest evaluation output
Get-Content .\eval-output.json | ConvertFrom-Json |
  Where-Object { $_.pathway -eq 'unmapped' } |
  Select-Object agentId, configuredTier, createdIn

# Cohort by date — does the unmapped cluster line up with an input refresh or the GA switch?
Get-Content .\eval-output.json | ConvertFrom-Json |
  Where-Object { $_.pathway -eq 'unmapped' } |
  Group-Object { ([datetime]$_.evaluatedAt).ToString('yyyy-MM-dd') } |
  Select-Object Name, Count
```

### 3.4 Resolution steps

1. **Confirm the fail-open decision was recorded** — each affected `(agent, user)` should be `Fail-open - Anomaly`, not a silent allow. Users are not blocked; this is correct.
2. For RC-A / RC-B, re-run the upstream signal producers (`work-iq-usage-detection` for `configuredTier`; `copilot-agent-inventory` for `createdIn`) and re-evaluate. `configuredTier` is authoritative and is evaluated first.
3. For RC-C, inspect the agent configuration and map it manually to the correct pathway; if the `configuredTier` string is a new Microsoft value, extend the classifier mapping (coordinate with the companion solution owner).
4. For every remaining `unmapped`, record a **follow-up owner** (Business Unit Owner or AI Administrator) and a triage due date in the anomaly log — this is the VC-3 evidence (zero silent denials).
5. For RC-E, follow [RB-03](#12-runbook-rb-03) for the GA-switch bulk reclassification.

### 3.5 Verification

- The pathway classification report shows **`unmapped` count zero**, or every `unmapped` agent carries a follow-up owner.
- Manifest check `2.27.a` (entitlement contract / classification) passes. See [`./verification-testing.md`](./verification-testing.md).

### 3.6 Cross-links

- Portal: [`./portal-walkthrough.md`](./portal-walkthrough.md) §4 — Classify each agent's consumption pathway.
- Control: [2.27 §Control Description](../../../controls/pillar-2-management/2.27-consumption-entitlement-governance.md) — decision outcomes.

---

## §4. Pillar ZERORATING-FAILCLOSED

**One-line:** a Copilot-licensed user on a Copilot Studio (`mcp-cs`) agent resolves to **Fail-closed - Zero-rating Unresolved** because the surface zero-rating was not resolved **and** the user is not in credit scope — or because the conservative `-ZeroRatingResolved:$false` posture was deliberately chosen.

### 4.1 Symptom catalog

| Code | Symptom | First responder |
|------|---------|-----------------|
| P4-S1 | A licensed user is fail-closed on a Teams/SharePoint/M365 Copilot agent | AI Administrator |
| P4-S2 | All `mcp-cs` users fail-closed after a config change | AI Governance Lead |
| P4-S3 | A user on a **non-Microsoft-365 surface** fail-closed (expected) | AI Administrator |
| P4-S4 | An **unlicensed** user is blocked (this is **Block – Missing license**, not zero-rating) | AI Administrator |

### 4.2 Root cause matrix (symptom → cause)

| RC | Description | Likelihood | How to confirm |
|----|-------------|-----------|----------------|
| RC-A | `fsi_zeroratingresolved` is `false` for the agent (conservative posture chosen) | High | Q-03: `ZeroRatingResolved = false` |
| RC-B | Surface is **not** a zero-rated Microsoft 365 surface (e.g., a custom / non-M365 channel) | High | Agent channel is not Teams / SharePoint / M365 Copilot under the user's own identity |
| RC-C | User is licensed and on an M365 surface, but `surfaceZeroRated` was not set true | Medium | Engine input shows `surfaceZeroRated = false` for an M365 surface |
| RC-D | User not in any **credit-scope** group (the OR-branch that would otherwise allow) | Medium | Q-02 / Get-Cbg227ScopeGroups — user absent from credit-scope group |
| RC-E | Footnote 6/7 fair-usage / tenant-grounding refinement applies (credit-metered) | Situational | Generative-answer-with-tenant-grounding or beyond-fair-use usage |

> **Distinguish from Missing-License (P4-S4).** An **unlicensed** user on `mcp-cs` / `mcp-agentbuilder` resolves to **Block – Missing license**, not a zero-rating fail-closed. Confirm license state with Q-05 before treating it as a zero-rating issue.

### 4.3 Diagnostic queries

```powershell
# Replay the disputed decision
Get-Cbg227Decision -AgentId <agentId> -UserUpn <upn>
# Inspect: Pathway (mcp-cs), Decision (Fail-closed - Zero-rating Unresolved),
#          ZeroRatingResolved, SpendScope, BlockReason

# Confirm the user's Copilot license (rule out Missing-License)
Get-MgUser -UserId <upn> | ForEach-Object {
  (Get-MgUserLicenseDetail -UserId $_.Id).SkuPartNumber
} | Where-Object { $_ -match 'COPILOT' }
```

### 4.4 Resolution steps

Pick the resolution that matches the **intended posture** — fail-closed can be correct:

1. **If zero-rating should be resolved (footnote 6/7 base case):** confirm the agent surface is Teams / SharePoint / Microsoft 365 Copilot and invoked under the user's own identity, then run the engine with `-ZeroRatingResolved:$true` (the default). The licensed user is then **Allowed** — the license is sufficient, no credit scope required. (Footnotes 6 & 7 and their fair-usage language were verified June 2026 against the Copilot Studio Licensing Guide and corroborated on Microsoft Learn, "billing-licensing".)
2. **If the surface is genuinely not zero-rated (RC-B):** add the user to the appropriate **credit-scope** group (security-only; see §2) so the OR-branch allows them, **or** accept the fail-closed posture as the conservative-by-design outcome and document it.
3. **If the conservative posture was chosen deliberately (RC-A):** this is working as configured. Fail-closed is the intended outcome when `-ZeroRatingResolved:$false`. Document the decision; only revert to `$true` if the footnote-7 base case applies for your tenant.
4. **If unlicensed (P4-S4):** assign a Microsoft 365 Copilot license (this is a Missing-License block, resolved by licensing — not by zero-rating).

!!! note "Do Not Over-Resolve Zero-Rating"
    Setting `-ZeroRatingResolved:$true` globally to clear fail-closed decisions can under-count credit-metered spend for non-M365 surfaces and the tenant-grounding / beyond-fair-use refinements 🔎. Resolve per agent based on the actual surface, not as a blanket override.

### 4.5 Verification

- `Get-Cbg227Decision` now returns **Allow** (resolved case) or a documented, intended **Fail-closed - Zero-rating Unresolved** (conservative case).
- The materialized decision records the `ZeroRatingResolved` posture per agent (VC-4). Manifest check `2.27.a` passes.

### 4.6 Cross-links

- Portal: [`./portal-walkthrough.md`](./portal-walkthrough.md) §5 — Apply the entitlement contract per pathway.
- Control: [2.27 §Control Description — Zero-rating resolution](../../../controls/pillar-2-management/2.27-consumption-entitlement-governance.md).

---

## §5. Pillar PAYG-NO-HARDSTOP

**One-line:** spend continued past a PAYG "budget" because the **PAYG billing policy provides budget alerts only — not a hard-stop**. The policy is alert-only by design; the expectation that it would cap spend is the defect.

!!! danger "PAYG Is Alert-Only by Design"
    The PAYG billing policy meters against an Azure subscription and raises **budget alerts**. It does **not** stop consumption at a threshold. The only standalone hard-stop available today is the prepaid **credit policy** (Chat-only). Do not document or attest a PAYG budget as a spend cap.

### 5.1 Symptom catalog

| Code | Symptom | First responder |
|------|---------|-----------------|
| P5-S1 | PAYG spend exceeded the configured budget; no stop occurred | AI Administrator |
| P5-S2 | Finance expected the budget to hard-cap; it only emailed an alert | Finance / Controller |
| P5-S3 | A broadly-shared metered agent accrued PAYG charges quickly | AI Governance Lead |

### 5.2 Root cause matrix (symptom → cause)

| RC | Description | Likelihood | How to confirm |
|----|-------------|-----------|----------------|
| RC-A | PAYG is alert-only by design — no hard-stop exists for it | Certain | Control 2.27 / portal §2; policy type is PAYG |
| RC-B | The expectation was set from credit-policy behavior (which **does** hard-stop, Chat-only) and mis-applied to PAYG | High | Configuration note conflates the two policy objects |
| RC-C | Per-agent cap on the agent is **detect-and-alert** (no public write-API hard-stop as of June 2026) | High | Q-04 / cap record enforcement mode |
| RC-D | Budget-alert threshold set too high or alert not routed to an owner | Medium | Azure cost management alert config |

### 5.3 Diagnostic queries

```powershell
# Confirm the policy type and that PAYG carries no hard-stop
Get-BillingPolicyInventory -EnvironmentUrl <url> -PayAsYouGoCeiling 50 -CreditCeiling 10 |
  Select-Object PolicyType, Surfaces, SpendControl  # PAYG SpendControl = 'Alerts only'

# Check the agent's per-agent cap enforcement mode
Get-Cbg227CoverageGap -AgentId <agentId> | Select-Object AgentId, SpendScope
```

### 5.4 Resolution steps

1. **Reset expectations:** document that PAYG is **budget-alerts-only**. Route the budget alert to an accountable owner (AI Governance Lead / Finance) with a defined response action.
2. **Where a hard-stop is required and the surface is Chat:** move the agent to the prepaid **credit policy** (standalone hard-stop, Chat-only) — see §6 for the Chat-only constraint.
3. **For SharePoint-grounded agents** (which stay on PAYG), there is no hard-stop today; manage spend via the per-agent cap in **detect-and-alert** mode plus the coverage-gap monitor and Azure cost alerting. Do not represent this as a hard-stop.
4. **For a runaway broadly-shared agent**, follow [RB-02](#11-runbook-rb-02).

### 5.5 Verification

- The configuration note states PAYG = alerts-only and identifies the accountable alert owner.
- For agents requiring a hard-stop on Chat, the credit policy is in use and verified.

### 5.6 Cross-links

- Portal: [`./portal-walkthrough.md`](./portal-walkthrough.md) §2 — Establish the two policy objects.
- Runbook: [RB-02](#11-runbook-rb-02) — runaway metered agent.

---

## §6. Pillar CREDIT-CHATONLY

**One-line:** a SharePoint-grounded agent is consuming spend (or the credit hard-stop didn't apply to it) because the **prepaid credit policy is Chat-only today** — SharePoint-grounded consumption bills against the PAYG policy.

### 6.1 Symptom catalog

| Code | Symptom | First responder |
|------|---------|-----------------|
| P6-S1 | A SharePoint-grounded agent is metering against PAYG, not the credit pack | AI Administrator |
| P6-S2 | The credit policy hard-stop did not apply to a SharePoint agent | AI Administrator |
| P6-S3 | Coverage-gap `fsi_spendscope` shows SharePoint where Chat was expected | Power Platform Admin |

### 6.2 Root cause matrix (symptom → cause)

| RC | Description | Likelihood | How to confirm |
|----|-------------|-----------|----------------|
| RC-A | Credit policy is **Chat-only today**; SharePoint grounding stays on PAYG | Certain (by design) | Control 2.27 / portal §2 |
| RC-B | Configuration is **credit-only** but the agent grounds on SharePoint | High | Q-07 surfaces + agent grounding config |
| RC-C | `fsi_spendscope` mis-set to Chat for a SharePoint agent | Medium | Q-04 spend scope vs agent config |

### 6.3 Diagnostic queries

```powershell
# What surface is the agent actually grounding on, and which policy covers it?
Get-Cbg227CoverageGap -AgentId <agentId> | Select-Object AgentId, SpendScope
Get-BillingPolicyInventory -EnvironmentUrl <url> | Select-Object PolicyType, Surfaces
```

### 6.4 Resolution steps

1. **Confirm the surface:** if the agent grounds on SharePoint, its metered spend belongs on the **PAYG** policy (alerts-only) — the credit policy's hard-stop will not apply to it today.
2. **Choose the right configuration:** for tenants with SharePoint-grounded agents, use **credit + PAYG** (Chat on credit, SharePoint on PAYG) or **PAYG-only**, not credit-only. Update the configuration note (portal §2.3).
3. **Correct `fsi_spendscope`** if it was mis-set (RC-C) so the engine and coverage-gap remain surface-aware.
4. **Set expectations:** there is no credit hard-stop for SharePoint grounding today; manage via PAYG alerts + the per-agent cap (detect-and-alert) + coverage-gap monitoring.

### 6.5 Verification

- `fsi_spendscope` matches the agent's actual surface (Chat vs SharePoint).
- The configuration note reflects credit + PAYG (or PAYG-only) where SharePoint grounding is present.

### 6.6 Cross-links

- Portal: [`./portal-walkthrough.md`](./portal-walkthrough.md) §2 — choose a configuration.
- Pillar: [§5 PAYG-NO-HARDSTOP](#5-pillar-payg-no-hardstop) — the PAYG side of the SharePoint surface.

---

## §7. Pillar COVERAGEGAP-COUNTS

**One-line:** the coverage-gap **would-be-blocked** count looks wrong (unexpectedly high, low, or zero), or the blocked-UPN sample looks truncated — usually a scoping, classification, or sampling-parameter issue rather than an engine fault.

### 7.1 Symptom catalog

| Code | Symptom | First responder |
|------|---------|-----------------|
| P7-S1 | Would-be-blocked count is far higher than expected | AI Governance Lead |
| P7-S2 | Would-be-blocked count is zero where blocks were expected | AI Administrator |
| P7-S3 | Blocked-UPN sample is truncated (fewer UPNs than blocked count) | Power Platform Admin |
| P7-S4 | Coverage-gap row count looks low for a large audience | Power Platform Admin |
| P7-S5 | Examiner asked for the coverage gap but enforcement is already on | AI Governance Lead |

### 7.2 Root cause matrix (symptom → cause)

| RC | Description | Likelihood | How to confirm |
|----|-------------|-----------|----------------|
| RC-A | A cohort that should be in credit scope / eligible cohort is **missing from the registry** (over-counts blocks) | High | §2 — group not registered or rejected |
| RC-B | Pathway mis-classified (e.g., a `metered` agent read as `none`) under-counts blocks | High | §3 — pathway vs expectation |
| RC-C | Blocked-UPN sample is **capped** by `-SampleCap` (default 20) — truncation is by design | Certain | `fsi_blockedsampleupns` is a bounded sample, not the full list |
| RC-D | Per-agent **aggregate** (not per agent × user) — one row per agent is by design | Certain | `fsi_cbgcoveragegap` is one row per agent |
| RC-E | Large audience partitioned by `-GroupSizeThreshold` (default 500) | Medium | `fsi_groupsizepartition` set above threshold |
| RC-F | `ZeroRatingResolved` posture flips many `mcp-cs` decisions (over/under-counts) | Medium | §4 — posture per agent |

!!! note "Bounded by Design — Not a Bug"
    Two behaviors are intentional and should not be 'fixed': the **capped blocked-UPN sample** (`-SampleCap`, default 20) preserves investigability without a 10⁶–10⁷-row blow-up, and the **per-agent aggregate** (one `fsi_cbgcoveragegap` row per agent, not per agent × user) keeps the output bounded. Use the **count** field (`fsi_blockeduserscount`) for totals; the UPN list is a sample.

### 7.3 Diagnostic queries

```powershell
# Inspect counts vs sample size for an agent
Get-Cbg227CoverageGap -AgentId <agentId> |
  Select-Object EligibleUsers, BlockedUsersCount, GroupSizePartition, SpendScope, MonitorOnly

# Re-run with a larger sample cap if you need more example UPNs for triage (still bounded)
Invoke-EntitlementEvaluation.ps1 -InputPath <inputs.json> -OutputPath <out.json> -SampleCap 50
```

### 7.4 Resolution steps

1. **Over-count (P7-S1, RC-A):** register the missing credit-scope / eligible-cohort group (§2), re-evaluate, and confirm the would-be-blocked count drops to the expected level.
2. **Under-count / zero (P7-S2, RC-B):** correct the pathway classification (§3) so `metered` agents are not read as `none`, then re-evaluate.
3. **Truncated sample (P7-S3, RC-C):** this is the bounded sample. Use `fsi_blockeduserscount` for the true total; raise `-SampleCap` only to gather more triage examples — do not materialize the full per-pair list.
4. **Posture-driven swings (RC-F):** confirm the `ZeroRatingResolved` posture per agent (§4) is intended before treating the count as wrong.
5. **Always confirm `fsi_monitoronly = true`** on every row before enforcement (this is the VC-6 / VC-7 gate).

### 7.5 Verification

- Re-run coverage gap; the would-be-blocked count matches the reviewed expectation, and every row shows `fsi_monitoronly = true`.
- Manifest check `2.27.c` (coverage-gap analysis run) passes. See [`./verification-testing.md`](./verification-testing.md).

### 7.6 Cross-links

- Portal: [`./portal-walkthrough.md`](./portal-walkthrough.md) §7 — coverage-gap analysis and sign-off.
- Runbook: [RB-01](#10-runbook-rb-01) — examiner asks for coverage-gap evidence.

---

## §8. Pillar CAP-NOENFORCE

**One-line:** a per-agent cap is "not stopping" spend because **no public write API for cap / credit-policy enforcement exists as of June 2026** (per-agent caps are Power Platform admin-center UI-managed, per Microsoft Learn, "manage-copilot-studio-messages-capacity"), so enforcement **degrades to detect-and-alert** — the cap is recorded and breaches are surfaced, but consumption is not programmatically blocked.

!!! danger "Detect-and-Alert Is Not a Hard-Stop"
    Where the enforcement mode is **detect-and-alert**, the cap **monitors and alerts**; it does not block consumption. This is the designed degradation when a programmatic hard-stop API is unavailable. Do **not** document a detect-and-alert cap as a hard-stop in examiner evidence.

### 8.1 Symptom catalog

| Code | Symptom | First responder |
|------|---------|-----------------|
| P8-S1 | Spend continued past the per-agent cap | AI Administrator |
| P8-S2 | Auditor asks which Zone 3 caps are hard-stops vs detect-and-alert | AI Governance Lead |
| P8-S3 | A cap shows enforcement mode `enforce` but spend still passed it | AI Administrator |

### 8.2 Root cause matrix (symptom → cause)

| RC | Description | Likelihood | How to confirm |
|----|-------------|-----------|----------------|
| RC-A | Cap enforcement mode is **detect-and-alert** (no public write-API hard-stop as of June 2026) | High | Cap record `fsi_cbg_enforcementmode` = detect-and-alert |
| RC-B | Cap documented as `enforce` but the underlying hard-stop API is unproven | Medium | No verified hard-stop mechanism behind `enforce` |
| RC-C | The only real hard-stop (credit policy) is Chat-only and the agent grounds on SharePoint | Medium | §6 — surface vs policy |
| RC-D | Alert fired but was not routed / actioned | Medium | Alert routing config |

### 8.3 Diagnostic queries

```powershell
# Enforcement mode for the agent's cap
Get-CbgCapRecord -AgentId <agentId> |
  Select-Object AgentId, MonthlyCreditCap, EnforcementMode, Zone

# Cross-check: is there a verified hard-stop behind any 'enforce' cap?
Get-CbgCapRecord | Where-Object { $_.EnforcementMode -eq 'enforce' } |
  Select-Object AgentId, Zone, EnforcementMode
```

### 8.4 Resolution steps

1. **Re-label honestly (RC-A / RC-B):** set the enforcement mode to **detect-and-alert** unless a verified hard-stop mechanism exists. No Zone 3 agent should be documented as a programmatic hard-stop where the write API is unproven (VC-5).
2. **Route the alert:** confirm the cap-breach alert reaches an accountable owner (AI Governance Lead / Finance) with a defined response.
3. **Where a true hard-stop is required on Chat:** use the prepaid **credit policy** (standalone hard-stop, Chat-only).
4. **For SharePoint-grounded agents:** accept detect-and-alert plus PAYG alerting and coverage-gap monitoring; manage spend appetite via the cap threshold and Finance sign-off.
5. **Re-verify the write-API status** periodically — there is no public hard-stop write API as of June 2026; should Microsoft ship a programmatic hard-stop API, the enforcement mode can be upgraded with verification.

### 8.5 Verification

- Every Zone 3 metered agent has a cap record with an honest enforcement mode; no `enforce` label without a verified hard-stop.
- Manifest check `2.27.b` (per-agent caps configured) passes. See [`./verification-testing.md`](./verification-testing.md).

### 8.6 Cross-links

- Portal: [`./portal-walkthrough.md`](./portal-walkthrough.md) §6 — configure per-agent spend caps.
- Pillar: [§5 PAYG-NO-HARDSTOP](#5-pillar-payg-no-hardstop), [§6 CREDIT-CHATONLY](#6-pillar-credit-chatonly).

---

## §9. Pillar SIEM-NO-EVIDENCE

**One-line:** entitlement decisions and coverage-gap aggregates are not landing in the SIEM, breaking the retention / forwarding evidence (VC-8).

### 9.1 Symptom catalog

| Code | Symptom | First responder |
|------|---------|-----------------|
| P9-S1 | SIEM dashboard shows zero entitlement-decision events for 24+ hours | AI Administrator |
| P9-S2 | Coverage-gap aggregates are not in the SIEM | Power Platform Admin |
| P9-S3 | Retention horizon on decisions is shorter than six years | Compliance Officer |

### 9.2 Root cause matrix (symptom → cause)

| RC | Description | Likelihood | How to confirm |
|----|-------------|-----------|----------------|
| RC-A | Export / forwarding flow disabled or failing | High | Flow run history shows failures or no runs |
| RC-B | Retention horizon (`fsi_retainuntil` / Dataverse policy) set below six years | Medium | Q-04 / retention config |
| RC-C | SIEM connector credential expired (managed identity / app) | Medium | Connector auth error |
| RC-D | Ingestion lag mistaken for a gap | Low | Event arrives after the expected lag |

### 9.3 Diagnostic queries

```powershell
# Confirm decisions and coverage-gap rows exist in Dataverse (source side)
Get-Cbg227Decision -AgentId <agentId> -UserUpn <upn>
Get-Cbg227CoverageGap -AgentId <agentId> | Select-Object MonitorOnly, RetainUntil
```

### 9.4 Resolution steps

1. Re-enable / re-run the export-forwarding flow; confirm a known test decision reaches the SIEM within the expected lag.
2. Correct the retention horizon to align to **FINRA 4511 (six-year minimum)** for Zone 3 (Zone 2 minimum 1 year); coordinate with the Compliance Officer.
3. Refresh the SIEM connector credential (prefer managed identity over client secret).
4. Confirm end-to-end ingestion and record the confirmation as VC-8 evidence.

### 9.5 Verification

- A test decision is visible in the SIEM; the retention configuration is documented and six-year-aligned for Zone 3.

### 9.6 Cross-links

- Portal: [`./portal-walkthrough.md`](./portal-walkthrough.md) §8 — retain decisions and forward evidence.

---

## §10. Runbook RB-01

**Title:** Coverage-gap sign-off requested (or enforcement found active) before the would-be-blocked population was signed off.

**Trigger:** S-16 — an examiner or internal audit asks for the pre-enforcement coverage-gap evidence, and either it was never signed off or enforcement is already active.

**Severity:** SEV-1 (examiner-visible; potential control-design gap).

**Steps:**

1. **Preserve state** (§0.4) before any change — export current `fsi_cbgcoveragegap` rows and `fsi_cbgentitlementmaterialized` decisions for the affected agents.
2. **Confirm the gate status:** check `fsi_monitoronly` on the coverage-gap rows. If enforcement was activated without a documented sign-off, record the finding honestly — do not back-date the sign-off.
3. **Produce the coverage gap now in monitor-only mode** for all in-scope metered agents (portal §7 / `Invoke-EntitlementEvaluation.ps1`), including the would-be-blocked count and the capped UPN sample.
4. **Convene the review** (AI Governance Lead + Business Unit Owner + Finance / Controller) and obtain the sign-off, dated as of today (current). State the remediation timeline for any agents where enforcement preceded sign-off.
5. **Produce the spend estimate** from the per-feature credit rates 🔎 and reconcile against the M365 admin center / Azure cost reporting (estimate caveat stated).
6. **Document the corrective action** for the examiner: the gate is now enforced (no enforcement without signed-off coverage gap) and the verification check (`2.27.c`) is in place.

**Exit criteria:** signed-off coverage gap on file; all rows traceable; corrective-action note recorded.

---

## §11. Runbook RB-02

**Title:** Broadly-shared metered agent draws down spend faster than budget alerts react.

**Trigger:** S-07 / S-03 — a single broadly-shared metered agent accrues PAYG charges (or draws down the prepaid credit pack) quickly; budget alerting lags the spend.

**Severity:** SEV-2 (uncontrolled spend; raises to SEV-1 if Zone 3 / production).

**Steps:**

1. **Identify the agent and surface** (Chat vs SharePoint) and the backing policy (PAYG alerts-only vs credit hard-stop). Recall **PAYG does not hard-stop**.
2. **Tighten entitlement scope immediately:** for a metered or `api-direct` pathway, reduce the eligible-cohort / API-audience group membership (§2) so fewer users are entitled — this is the fastest lever that does not depend on a write-API hard-stop.
3. **For a Chat-surface agent requiring a hard-cap:** move it to the prepaid **credit policy** (standalone hard-stop, Chat-only).
4. **For a SharePoint-grounded agent:** there is no hard-stop today; reduce entitled cohorts, lower the per-agent cap (detect-and-alert), and route the PAYG budget alert to an owner with a defined response.
5. **Re-run coverage gap** to confirm the reduced eligible-user count and the expected would-be-blocked change; keep `fsi_monitoronly = true` until any new enforcement is signed off.
6. **Brief Finance / Controller** on the spend appetite and document the cap-threshold approval (SOX 404 ITGC).

**Exit criteria:** entitlement scope reduced; spend trend stabilized; alert routed; coverage gap re-run.

---

## §12. Runbook RB-03

**Title:** Bulk reclassification after the June 16 2026 Work IQ consumption-billing switch.

**Trigger:** S-04 — a cluster of agents flips to `unmapped` (or changes pathway) around the **June 16, 2026** (scheduled per M365 roadmap 559017 / Microsoft Learn "use-work-iq") Work IQ GA / consumption-billing switch, when `configuredTier` vocabulary or metering behavior changes.

**Severity:** SEV-2 (governance signal disruption across many agents).

**Steps:**

1. **Confirm the cluster correlates with the switch date** (§3.3 cohort-by-date query). If the `unmapped` cluster is dated near June 16 2026, treat it as a vocabulary / metering change, not a per-agent defect.
2. **Refresh the upstream signals:** re-run `work-iq-usage-detection` (`configuredTier`) and `copilot-agent-inventory` (`createdIn`) so the classifier reads post-switch values.
3. **Extend the classifier mapping** for any new `configuredTier` strings Microsoft introduced at GA (coordinate with the companion-solution owner). `configuredTier` remains authoritative and is evaluated first.
4. **Re-evaluate** the in-scope population and confirm the `unmapped` count returns to zero (or each remaining `unmapped` has a follow-up owner).
5. **Re-run coverage gap in monitor-only** and re-confirm sign-off before re-activating any enforcement — the switch may change the metered population and the spend estimate.
6. **Re-verify the remaining 🔎 reference values** (ceilings 50/10, credit rates, $0.01/credit, 25,000-credit pack) against the post-switch Microsoft documentation. (Footnotes 6 & 7 were verified June 2026.)

**Exit criteria:** post-switch classification stable; coverage gap re-run and re-signed-off; reference values re-verified.

---

## §X. Recovery and post-incident attestation refresh

After resolving any SEV-1 / SEV-2 incident, refresh the control attestation so the evidence set reflects the corrected state.

1. **Re-run the verification pack** ([`./verification-testing.md`](./verification-testing.md)) and confirm all four manifest checks pass for the affected zone:
   - `2.27.a` entitlement contract evaluated (zones 2, 3)
   - `2.27.b` per-agent caps configured (zone 3)
   - `2.27.c` coverage-gap analysis run (zones 2, 3)
   - `2.27.d` policy scope groups registered — `securityEnabled`, not `mailEnabled` (zones 2, 3)
2. **Regenerate the examiner evidence** (E-01 .. E-07) for the corrected state and retain it under the six-year-aligned policy (FINRA 4511 / SEC 17a-4(b)(4)).
3. **Confirm the coverage-gap sign-off** is current and that no enforcement is active without a signed-off would-be-blocked population.
4. **Update the configuration note** (credit-only / credit + PAYG / PAYG-only), the ceilings (PAYG 50 / credit 10) 🔎, and the per-agent cap enforcement modes (enforce vs detect-and-alert).
5. **Record the incident and corrective action** in the governance log; brief the AI Governance Lead and, where examiner-visible, the Compliance Officer.

!!! warning "Honest Attestation After Incidents"
    Do not back-date sign-offs, re-label a detect-and-alert cap as a hard-stop, or assert zero-rating where the surface is not zero-rated. The control governs the entitlement **decision** and **supports compliance with** the cited regulations; it does not by itself satisfy any of them. Organizations should verify the corrected configuration meets their specific obligations.

---

## Related Documentation

- [Control 2.27 — Consumption-Entitlement Governance](../../../controls/pillar-2-management/2.27-consumption-entitlement-governance.md) — the control specification (source of truth)
- [`./portal-walkthrough.md`](./portal-walkthrough.md) — click-path through the eight Key Configuration Points
- [`./powershell-setup.md`](./powershell-setup.md) — PowerShell and Microsoft Graph automation
- [`./verification-testing.md`](./verification-testing.md) — test procedures and the manifest-check cross-walk (`2.27.a`–`2.27.d`)
- [Copilot Billing Governance — companion solution](https://judeper.github.io/FSI-AgentGov-Solutions/solutions/copilot-billing-governance/) 🔎

*This troubleshooting guide supports compliance with the cited regulations; it does not, on its own, satisfy any of them. The June 16 2026 Work IQ switch, Licensing Guide footnotes 6 & 7, and the absence of a public cap-enforcement write API were verified June 2026; still verify the remaining 🔎-flagged figures (per-feature credit rates, $0.01/credit, 25,000-credits-per-month, tenant ceilings 50/10) against current Microsoft documentation before treating any procedure as examiner evidence.*
