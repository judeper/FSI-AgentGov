# Control 4.7 — Microsoft 365 Copilot Data Governance: Troubleshooting

This playbook is the FSI-grade incident response and troubleshooting guide for **Control 4.7 — Microsoft 365 Copilot Data Governance**. It assumes you have already implemented the control per the [portal walkthrough](portal-walkthrough.md), [PowerShell setup](powershell-setup.md), and [verification testing](verification-testing.md) playbooks, and that something has either failed an internal verification check or surfaced as a real-world incident.

> **Audience:** SharePoint Admin, Purview Compliance Admin, AI Governance Lead, Compliance Officer, Privacy Officer, Records Officer, Model Risk Officer, Incident Commander, CISO, General Counsel, FINRA Designated Supervisor.
>
> **Scope:** Microsoft 365 Copilot (BizChat, Copilot in Word/Excel/PowerPoint/Outlook/Teams), Copilot Pages, Copilot Notebooks, Restricted Content Discovery (RCD), Restricted SharePoint Search (RSS), DLP for Copilot, Endpoint DLP for Copilot, Microsoft Purview Audit (UAL), and the SEC 17a-4(f) recordkeeping perimeter that surrounds these workloads.
>
> **What this playbook does NOT cover:** General SharePoint sharing controls (see Control 4.1), tenant-wide DLP baselines (see Controls 1.10/1.11), retention policy authoring (see Control 3.4), Copilot Studio agent governance (see Pillar 2 controls), or general Microsoft 365 incident response (see Control 1.6).

---

## Table of Contents

1. [§1 — FSI Incident Handling — READ FIRST](#1-fsi-incident-handling-read-first)
2. [§2 — Nine Failure-Mode Runbooks](#2-nine-failure-mode-runbooks)
3. [§3 — Reportability Decision Tree (Reference)](#3-reportability-decision-tree-reference)
4. [§4 — Evidence Preservation](#4-evidence-preservation)
5. [§5 — Communication and Escalation](#5-communication-and-escalation)
6. [§6 — Recovery Procedures](#6-recovery-procedures)
7. [§7 — Post-Incident Review](#7-post-incident-review)
8. [§8 — Anti-Patterns](#8-anti-patterns)

---
## §1 — FSI Incident Handling — READ FIRST

> **STOP.** Before you change a single label, DLP rule, RCD assignment, or RSS allowlist entry, read this section in full. The actions you take in the first 60 minutes of a Copilot data-governance incident determine (a) whether you have defensible SEC 17a-4(f) evidence, (b) whether you trigger or miss SEC Reg S-P, SEC Form 8-K Item 1.05, NYDFS §500.17, FINRA Rule 4530, or FTC Safeguards reporting clocks, and (c) whether your remediation destroys the very telemetry you need to prove the scope of the incident.

This section establishes the non-negotiable incident-handling perimeter. Every runbook in §2 references back here.

### §1.1 — Severity Classification

Classify the incident immediately on detection. Severity drives Incident Commander selection, communication tree (§5), evidence floor (§4), and reportability evaluation (§3). When in doubt, classify UP one level — downgrades are easier to defend than missed escalations.

| Severity | 4.7-Specific Triggers | Initial Owner | Maximum Time to IC Assignment |
|---|---|---|---|
| **SEV-1** | (a) Confirmed exfiltration of customer NPI, MNPI, or regulated content via Copilot grounding to an unauthorized user; (b) Copilot grounding crossed a Multi-Geo data-residency boundary in violation of customer contract or local law; (c) Copilot Pages or Notebooks containing regulated communications were created and proven not preserved per SEC 17a-4(f); (d) any incident with potential customer notice obligation under SEC Reg S-P §248.30 or NYDFS §500.17. | CISO + General Counsel | 30 minutes |
| **SEV-2** | (a) DLP for Copilot policy failed to block a configured sensitive-content match in a controlled test; (b) RSS allowlist drift (sites outside the approved list returned grounding results); (c) Endpoint DLP bypass via non-Edge browser by privileged user; (d) labeled-and-encrypted content surfaced in Copilot output to a user without decryption rights; (e) RCD silent no-op (no Copilot license assigned) discovered post-go-live. | AI Governance Lead + Purview Compliance Admin | 2 hours |
| **SEV-3** | (a) Single-user oversharing complaint with no confirmed exfiltration; (b) DLP false-positive blocking legitimate business use at scale (>50 users/day); (c) RSS allowlist add/remove drift not matching change-control record; (d) Copilot Notebook stored in a Loop container outside the recordkeeping scope discovered during periodic review. | Purview Compliance Admin | 1 business day |
| **SEV-4** | (a) Documentation drift between control 4.7 and tenant configuration; (b) per-user RCD anomalies during periodic license-tally check; (c) audit-log query latency exceeding SLA. | SharePoint Admin or AI Governance Lead | 5 business days |

> **Calibration note for FSI:** Any incident touching a brokerage book of business, MNPI, M&A workspace, customer NPI, or a regulated communications channel (subject to FINRA Rule 4511 / SEC 17a-4) defaults to SEV-1 until the Compliance Officer downgrades in writing.

### §1.2 — Reportability Decision Tree (Q1–Q7)

Run this tree in parallel with §1.1 classification — do **not** sequence it after triage. The clocks below start from the moment of *materiality determination* (Q2/Q3) or *discovery* (Q1/Q4/Q5), not from when the IC is appointed. Refer to §3 for full annotated rule text.

| # | Question | If YES → | Owner | Clock |
|---|---|---|---|---|
| **Q1** | Did the incident expose customer NPI (non-public personal information of a "customer" as defined in Reg S-P §248.3)? | SEC Regulation S-P §248.30(a)(3) — provide notice to affected customers no later than **30 days** after discovery, unless a federal or state law-enforcement request justifies delay. Large entities effective Dec 3, 2025; smaller entities Jun 3, 2026. | Privacy Officer + General Counsel | 30 days from discovery |
| **Q2** | Is the incident *material* to a reasonable investor in the registrant or its parent? | SEC Form 8-K Item 1.05 — file within **4 business days** of materiality determination. Note: materiality determination itself must be made "without unreasonable delay." | General Counsel + CFO | 4 business days from materiality determination |
| **Q3** | Does the registrant operate in New York and is the incident a "Cybersecurity Event" requiring notice to the NYDFS Superintendent? | NYDFS 23 NYCRR §500.17(a) — notice within **72 hours** of determination that the event meets reporting thresholds. | CISO + General Counsel | 72 hours from determination |
| **Q4** | Does the incident require disclosure to FINRA under Rule 4530 (regulatory action, written customer complaint, or specified events)? Note: FINRA Notice 25-07 specifically calls out AI-related risks in member supervision. | FINRA Rule 4530(a) — report within **30 calendar days** after the firm knows or should have known of the qualifying event. | Compliance Officer + FINRA Designated Supervisor | 30 calendar days from knew-or-should-have-known |
| **Q5** | Were ≥500 consumers affected and is the firm subject to the FTC Safeguards Rule (16 CFR Part 314)? | FTC Safeguards §314.4(j) — notify FTC within **30 days** of discovery of a notification event. Effective May 13, 2024. | Privacy Officer + General Counsel | 30 days from discovery |
| **Q6** | Does the incident involve a model-risk failure (Copilot generating inaccurate, biased, or unexplainable output that informed a regulated decision)? | Federal Reserve SR 11-7 / OCC Bulletin 2011-12 — document model-risk event in the model inventory; no external clock, but failure to document is itself an examination finding. | Model Risk Officer + Compliance Officer | No external clock; document immediately |
| **Q7** | Did the incident involve credential compromise, AAL step-down, or trigger a state breach-notification statute (e.g., CCPA §1798.82, NY Shield Act, MA 201 CMR 17.00)? | NIST SP 800-63B AAL re-binding required; consult state-by-state matrix — most states require notice "in the most expedient time possible and without unreasonable delay" with hard caps ranging from 30 to 90 days. | Privacy Officer + CISO | Varies by state; assume 30 days unless legal advises otherwise |

> **Critical rule:** If ANY of Q1–Q5 evaluates YES, the incident is automatically SEV-1, regardless of §1.1 classification. The reverse is also true for Q1–Q3: a SEV-1 classification triggers a written legal evaluation of Q1–Q3 within 4 hours.

### §1.3 — Evidence Floor (E-01 through E-13)

The following 13 artifacts MUST be captured **before** any remediation action that mutates state. The Incident Commander signs the evidence manifest at incident close. The manifest is written to SEC 17a-4(f)-compliant WORM storage (Microsoft Purview Records Management with regulatory record locks, OR an attested D3P storage location per SEC Release 34-96034).

| ID | Artifact | Source | Capture Method | Retention |
|---|---|---|---|---|
| **E-01** | Unified Audit Log export covering the incident window ±48 hours | Microsoft Purview Audit (Premium) | `Search-UnifiedAuditLog` with `RecordType` filter for `CopilotInteraction`, `SharePointFileOperation`, `MipLabel`, `DLPEndpoint` | 10 years (SEC 17a-4(f)) |
| **E-02** | Copilot interaction transcripts (prompt + grounding sources + response) | Purview Audit `CopilotInteraction` records, OR Purview eDiscovery (Premium) hold | Export to immutable JSON; SHA-256 hash each file | 10 years |
| **E-03** | RCD assignment snapshot (per-user license tally + assignment scope) | `Get-MgUser` + `Get-MgUserLicenseDetail` + RCD policy export | PowerShell transcript + CSV with row-level SHA-256 | 7 years |
| **E-04** | RSS allowlist export at time of incident | SharePoint Online Management Shell: `Get-SPOTenantRestrictedSearchApplicableSites` and `Get-SPOSite \| Where-Object RestrictContentOrgWideSearch -eq $true` | CSV + PowerShell transcript | 7 years |
| **E-05** | DLP for Copilot policy export (rules, conditions, actions, scope) | Purview Compliance Portal export OR `Get-DlpCompliancePolicy` / `Get-DlpComplianceRule` | XML + JSON; signed by Purview Compliance Admin | 7 years |
| **E-06** | Sensitivity label policy and rights-protection settings export | `Get-Label`, `Get-LabelPolicy`, `Get-LabelPolicyRule` | XML + JSON | 7 years |
| **E-07** | Endpoint DLP policy + Microsoft Purview browser extension inventory | `Get-DlpComplianceRule` (Endpoint workload) + Intune device-config export | JSON | 7 years |
| **E-08** | Affected user account state (group memberships, license, MFA/AAL, recent sign-ins) | Microsoft Graph: `/users/{id}`, `/users/{id}/memberOf`, `/users/{id}/signInActivity`, `/auditLogs/signIns` | JSON | 7 years |
| **E-09** | Copilot Pages and Notebooks inventory created/modified during the incident window | Graph `/me/drive/root/search` for Pages (.fluid in OneDrive); Loop workspace API for Notebooks | JSON manifest with file IDs, owners, sharing state | 10 years (recordkeeping artifact) |
| **E-10** | Multi-Geo configuration snapshot (preferred data location per affected user) | `Get-SPOGeoStorageQuota`, Graph `/users/{id}?$select=preferredDataLocation` | JSON | 7 years |
| **E-11** | Service health and known-issue evidence (Microsoft 365 Service Health Dashboard, Message Center) | Admin center export + `Get-ServiceHealth` (Graph) | PDF + JSON | 7 years |
| **E-12** | Communication artifacts (Teams, email, ticket-system threads from triage through close) | eDiscovery (Premium) hold across IC, Comms Officer, Counsel mailboxes | PST/JSON via Purview eDiscovery export | 10 years |
| **E-13** | Signed evidence manifest with SHA-256 hashes of E-01 through E-12, attested by Incident Commander, countersigned by Compliance Officer | Generated at incident close | JSON + PDF; written to SEC 17a-4(f) WORM target | 10 years |

> **Manifest format (E-13 reference):**
> ```json
> {
>   "incident_id": "INC-2026-0407-001",
>   "control": "4.7",
>   "severity": "SEV-1",
>   "incident_commander": "<UPN>",
>   "compliance_officer": "<UPN>",
>   "captured_at_utc": "2026-04-07T14:32:00Z",
>   "artifacts": [
>     {"id": "E-01", "filename": "ual-2026-04-05_to_2026-04-09.json", "sha256": "..."},
>     {"id": "E-02", "filename": "copilot-transcripts.json", "sha256": "..."}
>   ],
>   "worm_target": "purview-records-mgmt://policy/sec17a4-incidents",
>   "signatures": {
>     "ic": "<digital signature>",
>     "co": "<digital signature>"
>   }
> }
> ```

### §1.4 — Compensating Controls During the Gap

If the failed control cannot be remediated immediately (e.g., RSS allowlist requires change-control approval, DLP policy needs author review), put compensating controls in place to bound exposure during the gap. **Do not leave the tenant in the failed state without a compensating measure documented and time-bounded.**

| Failed Control | Compensating Action | Maximum Gap Duration | Owner |
|---|---|---|---|
| RCD not assigned | Suspend Copilot license assignment for affected user(s) via Entra group membership change | 24 hours | Entra Global Admin |
| RSS allowlist drift (extra sites) | Apply per-site `Set-SPOSite -RestrictContentOrgWideSearch $true` to the drifting sites pending allowlist correction | 72 hours | SharePoint Admin |
| DLP for Copilot policy not blocking | Add the affected SIT/label to the tenant-wide DLP policy in BLOCK mode targeting the Copilot workload | 7 days | Purview Compliance Admin |
| Endpoint DLP non-Edge bypass | Apply Conditional Access app-control policy forcing Edge for affected user/group | 14 days | Entra Global Admin |
| Copilot Pages outside retention | Apply hold on author's OneDrive via Purview eDiscovery (Premium) | 30 days | Records Officer |
| Loop Notebook not preserved | Apply Loop workspace retention via Purview retention policy targeting the Loop workload | 30 days | Records Officer |
| Multi-Geo cross-region grounding | Restrict affected user via `Set-MgUser -PreferredDataLocation` and force re-provisioning OR temporarily revoke Copilot license | 24 hours | SharePoint Admin |

### §1.5 — Pre-Escalation Checklist (Minimum 17 items)

Before paging the Incident Commander, the on-call responder MUST work through this checklist and capture answers in the incident ticket. If you cannot answer an item, mark it UNKNOWN and proceed — do not delay escalation to investigate.

1. **Incident ID assigned?** (Format: `INC-YYYY-MMDD-NNN`)
2. **Detection time** captured in UTC?
3. **Detection source** identified? (UAL alert, user report, control verification, partner notification, regulator inquiry, third-party security report)
4. **Affected user count** estimated? (Exact, range, or UNKNOWN)
5. **Affected data classification** identified? (Public / Internal / Confidential / Highly Confidential / NPI / MNPI / regulated communication)
6. **Affected workload(s)** identified? (BizChat, Copilot in app, Copilot Pages, Copilot Notebook, Copilot Studio agent, search experience)
7. **Geographic scope** identified? (Single region, multi-region, cross-border)
8. **Customer impact** assessed? (Yes / No / UNKNOWN — if Yes, Q1 of §1.2 applies)
9. **MNPI involvement** assessed? (Yes / No / UNKNOWN — if Yes, Wall Crossing protocol initiated)
10. **External actor involvement** assessed? (Yes / No / UNKNOWN — if Yes, contact CISO before any further action)
11. **Service Health Dashboard** checked for related Microsoft incident?
12. **Message Center** checked for advisories or pending changes affecting Copilot/RCD/RSS/DLP in the past 30 days?
13. **Recent change records** reviewed for Copilot, Purview, SharePoint, Entra, Intune in past 14 days?
14. **Q1–Q7 reportability tree** evaluated and documented in ticket?
15. **Severity classification** assigned per §1.1?
16. **Evidence floor (§1.3)** capture initiated? (At minimum E-01 UAL pull triggered)
17. **Compensating control (§1.4)** applied if remediation will exceed 1 hour?
18. **Wall Crossing list** consulted if MNPI involved?
19. **Communication tree (§5)** initiated at the appropriate L-level?

### §1.6 — Communication Tree — Initial Notification

| Level | Who | When | Channel |
|---|---|---|---|
| **L1** | On-call responder → Incident Commander | At classification | Primary on-call paging system |
| **L2** | IC → AI Governance Lead, Purview Compliance Admin, SharePoint Admin | At IC assignment | Dedicated incident Teams channel (eDiscovery hold pre-applied) |
| **L3** | IC → Compliance Officer, Privacy Officer, General Counsel | If Q1–Q5 of §1.2 evaluates YES, OR SEV-1 classification | Phone call followed by written summary |
| **L4** | IC → CISO, CFO, CEO, Board Audit Committee chair | If 8-K Item 1.05 materiality discussion warranted, OR Q3 NYDFS clock starting | Phone call; do not use email until Counsel approves messaging |

Full L-level details in §5.

### §1.7 — Worked SEV-1 Example: M&A "Project Atlas" Plugin-Bypassing-RCD

**Scenario.** During M&A due diligence ("Project Atlas"), a deal-team analyst uses Copilot to summarize the target's confidential financial projections. The analyst's Copilot returns content from the M&A workspace AND surfaces three documents from an unrelated business unit's SharePoint site that contain MNPI about a pending earnings restatement. Investigation reveals: (a) the unrelated site was added to RSS allowlist by mistake during a recent change, (b) RCD was correctly assigned but only constrains BizChat grounding to the user's permission scope, not the allowlist scope, and (c) a Copilot Studio agent built by the FP&A team had bypassed the M&A workspace label-based DLP because the agent's connection used a service account that was not in the DLP policy scope.

**Incident Commander actions, hour-by-hour:**

- **T+0 to T+15 min.** Page IC. IC declares SEV-1 (MNPI involvement → Q4 FINRA, Q2 8-K materiality assessment). Open incident channel. Apply eDiscovery hold to analyst, agent author, and three site owners.
- **T+15 to T+45 min.** Capture E-01 (UAL pull for analyst's CopilotInteraction records ±48 hours), E-02 (transcripts), E-04 (RSS snapshot), E-05 (DLP policy export). Suspend the Copilot Studio agent. Suspend Copilot license for analyst pending review.
- **T+45 min to T+2 hr.** Wall Crossing list updated by Compliance Officer. General Counsel evaluates Q2 (8-K materiality). NYDFS 72-hour clock (Q3) started — written notice prepared in parallel.
- **T+2 to T+6 hr.** Apply compensating control: per-site `Set-SPOSite -RestrictContentOrgWideSearch $true` on the three drifting sites. Identify all users who may have queried the analyst's prompt patterns via UAL `CopilotInteraction` filter. Confirm no further exposure.
- **T+6 to T+24 hr.** Q4 FINRA Rule 4530 evaluation completed. CISO + GC + CFO meeting on 8-K materiality. Customer-facing impact assessment for Q1 Reg S-P (concluded: no customer NPI exposed in this scenario, Q1 NO).
- **T+24 to T+72 hr.** NYDFS notice filed. Internal communications drafted. PIR scheduled per §7.

**Key lesson:** RCD constrains *grounding to user-scoped content*, but RSS controls *which sites Copilot can index in the first place*. They are complementary, not redundant. DLP for Copilot must be scoped to all identities that can invoke Copilot — including service accounts used by Copilot Studio agents.

### §1.8 — Diagnostic Query Reference

The following queries are referenced repeatedly in §2 runbooks. Save them in your incident-response playbook tooling (Sentinel, Splunk, custom dashboards).

**KQL (Microsoft Sentinel / Log Analytics):**

```kusto
// Q-D1: All Copilot interactions for a user in a window
OfficeActivity
| where TimeGenerated between (datetime(2026-04-05) .. datetime(2026-04-09))
| where Operation in ("CopilotInteraction", "CopilotChat")
| where UserId =~ "<UPN>"
| project TimeGenerated, UserId, Operation, AppHost, ResultStatus, AccessedResources

// Q-D2: DLP for Copilot policy hits in window
OfficeActivity
| where Operation startswith "DLPRuleMatch"
| where Workload == "Copilot"
| summarize Count=count() by PolicyName, RuleName, ActionType, bin(TimeGenerated, 1h)

// Q-D3: Sites returning grounding results outside RSS allowlist
OfficeActivity
| where Operation == "CopilotGrounding"
| extend Site = tostring(parse_json(AccessedResources)[0].Site)
| join kind=leftanti (
    externaldata(Site:string) ["https://<your-allowlist-csv>"] with (format="csv", ignoreFirstRecord=true)
) on Site
| project TimeGenerated, UserId, Site, Operation
```

**PowerShell:**

```powershell
# Q-D4: RSS effective allowlist
Connect-SPOService -Url https://<tenant>-admin.sharepoint.com
Get-SPOTenantRestrictedSearchApplicableSites
# Cross-check sites that have per-site restriction:
Get-SPOSite -Limit All -IncludePersonalSite:$false |
    Where-Object { $_.RestrictContentOrgWideSearch -eq $true } |
    Select-Object Url, Title, Owner |
    Export-Csv .\rss-per-site-snapshot.csv -NoTypeInformation

# Q-D5: RCD per-user license tally (should be exactly 1 Copilot license per RCD-targeted user)
Connect-MgGraph -Scopes "User.Read.All","Directory.Read.All"
$copilotSku = (Get-MgSubscribedSku | Where-Object { $_.SkuPartNumber -like "Microsoft_365_Copilot*" }).SkuId
Get-MgUser -All -Property Id,UserPrincipalName,AssignedLicenses |
    Where-Object { ($_.AssignedLicenses.SkuId -contains $copilotSku) } |
    Select-Object UserPrincipalName, @{N="CopilotLicenses";E={($_.AssignedLicenses | Where-Object {$_.SkuId -eq $copilotSku}).Count}} |
    Where-Object { $_.CopilotLicenses -ne 1 }

# Q-D6: Copilot connectors / Graph external connections (sources of grounding outside Microsoft 365)
Connect-MgGraph -Scopes "ExternalConnection.Read.All"
Get-MgExternalConnection | Select-Object Id, Name, Description, State

# Q-D7: DLP for Copilot policies (full export for evidence)
Connect-IPPSSession
Get-DlpCompliancePolicy | Where-Object { $_.Workload -like "*Copilot*" } |
    Export-Clixml .\dlp-copilot-policies.xml
Get-DlpComplianceRule | Where-Object { $_.Workload -like "*Copilot*" } |
    Export-Clixml .\dlp-copilot-rules.xml
```

---
## §2 — Nine Failure-Mode Runbooks

Each runbook follows the same six-block structure: **Symptoms → Root cause → Diagnostic → Remediation → Validation → Evidence + Reportability mapping**. Use them in conjunction with §1 — never run a remediation step without first capturing the evidence floor.

### §2.1 — Sensitive Content Surfaced via Copilot Grounding (Oversharing)

**Symptoms.**
- A user reports that Copilot returned a document, email, chat, or list item that they were not aware they could access.
- A periodic verification (per [verification testing](verification-testing.md)) shows Copilot returning grounding citations from sites or files that should have been excluded.
- Auditors or business stakeholders surface MNPI, customer NPI, HR, or M&A content in unrelated user prompts.

**Root cause (most common, in order of probability).**
1. Site-level NTFS-style permission inheritance left a sensitive container shared "Everyone except external users" or "All Company" — a long-standing SharePoint oversharing pattern that Copilot now amplifies.
2. RCD was not assigned to the user, so Copilot grounded on the user's full access scope (which was broader than expected).
3. RSS allowlist was set tenant-wide but the offending site was added to the allowlist incorrectly during a change.
4. A SharePoint group nested inside a Microsoft 365 group expanded the user's effective access scope without the user's awareness.
5. Sensitivity labels were not applied (or were applied only as headers/footers without rights-protection), so DLP for Copilot had nothing to match on.

**Diagnostic.**
1. Capture E-01 (UAL pull for the affected user, ±48 hours).
2. Capture E-02 (Copilot transcripts) — extract the full grounding-citation list.
3. For each cited document, run effective-permissions check: `Get-SPOUser -Site <site> -LoginName <UPN>` and the SharePoint admin "Check user permissions" portal action.
4. Run **Q-D5** to confirm RCD assignment for the user.
5. Run **Q-D4** to confirm the cited site(s) are within the RSS allowlist scope.
6. Pull sensitivity-label state for each cited document via Graph `/sites/{id}/drive/items/{id}?$select=sensitivityLabel`.

**Remediation.**
1. **Immediate (within 1 hour):** If the cited content is MNPI or customer NPI, escalate to SEV-1 and apply compensating control: revoke the user's site-level access via `Remove-SPOUser` AND apply a per-site restriction via `Set-SPOSite -RestrictContentOrgWideSearch $true`.
2. **Short term (within 24 hours):** Re-evaluate the site's sharing posture. Remove "Everyone except external users" / "All Company" assignments at the site, library, and item level. Apply sensitivity labels with rights-protection to the cited documents.
3. **Medium term (within 7 days):** Add the affected site to the SharePoint Advanced Management (SAM) Data Access Governance (DAG) recurring report. Schedule a Site Access Review (SAM feature) for the site owner.
4. **Long term (within 30 days):** Use SAM "Restricted Access Control Policy" (RAC) to enforce membership restriction on sites containing MNPI or customer NPI. Document policy in change-control.

**Validation.**
1. Re-run the original user prompt and confirm Copilot does not return the previously cited content.
2. Run a per-site DAG report and confirm "Everyone" assignments are zero.
3. Re-run **Q-D2** to confirm DLP for Copilot now matches on the labeled content.
4. Confirm the user's effective permissions to the site are removed.

**Evidence + Reportability.**
- Capture E-01, E-02, E-03, E-04, E-06, E-08, E-09 (Pages/Notebooks if Copilot generated derivatives), and E-13.
- Q1 (Reg S-P): YES if any cited content was customer NPI.
- Q2 (8-K): Materiality assessment required if MNPI or customer NPI ≥10,000 records.
- Q3 (NYDFS 72-hour): YES if NY-licensed registrant and event is "material."
- Q4 (FINRA 4530): YES if event involved a customer complaint or regulated supervision lapse.

### §2.2 — DLP for Copilot Policy Not Blocking Expected Content

**Symptoms.**
- A controlled test (per verification playbook) creates a document with a configured Sensitive Information Type (SIT) match, attaches a configured sensitivity label, and prompts Copilot. Copilot returns the content instead of the configured block message.
- Audit query **Q-D2** shows zero `DLPRuleMatch` events for Copilot workload despite known label/SIT-bearing content in the tenant.

**Root cause (most common).**
1. Policy targeting mismatch: the DLP policy was scoped to "All users" but the test user is in an excluded group, OR the policy was scoped to a security group the test user is not in.
2. Label-based vs. condition-based confusion: the policy targets a sensitivity label, but the test content has the SIT only (no label). DLP for Copilot supports both label-based and condition (SIT) targeting — verify which mode the policy uses.
3. Service-account / agent-author identity gap: the prompt was issued via a Copilot Studio agent whose connection identity is not in the policy scope.
4. Policy mode is "Test with notifications" or "Test without notifications" instead of "Turn on the policy."
5. Workload mismatch: the policy targets the "Microsoft 365 Copilot" workload but the test was performed in a workload not yet covered (e.g., a Copilot agent in Teams that uses a different workload classifier).

**Diagnostic.**
1. Capture E-05 (DLP policy export via **Q-D7**).
2. Capture E-06 (sensitivity-label export).
3. Confirm policy mode: `(Get-DlpCompliancePolicy -Identity "<name>").Mode` should return `Enable`.
4. Confirm scope: `(Get-DlpCompliancePolicy -Identity "<name>") | Select-Object IncludedUserGroups, ExcludedUserGroups`.
5. For each rule: `Get-DlpComplianceRule -Policy "<name>" | Select-Object Name, ContentContainsSensitiveInformation, Workload, BlockAccess, NotifyUser`.
6. For Copilot Studio agents: identify the connection identity (`Get-AdminPowerAppConnection`) and confirm membership in policy scope.

**Remediation.**
1. Correct the scoping mismatch (add user/group to IncludedUserGroups, remove from ExcludedUserGroups).
2. Switch mode to `Enable` if currently in test mode.
3. Add a parallel rule in the same policy that targets the SIT directly (in addition to label-based targeting) to cover content that lacks a label.
4. For agent-driven prompts, ensure the agent's connection identity is in scope. Where the agent uses a service account, add that account to the policy scope.
5. If workload coverage gap is suspected, verify the Microsoft Learn DLP workload reference for the latest Copilot workload identifiers.

**Validation.**
1. Re-run the controlled test (per verification playbook). Confirm Copilot returns the configured block message and **Q-D2** shows the rule match.
2. Run an aggregation: `OfficeActivity | where Workload == "Copilot" and Operation startswith "DLPRuleMatch" | summarize by RuleName, ActionType` and confirm match count is non-zero for the affected rule.
3. Run a parallel test as a Copilot Studio agent identity to confirm coverage.

**Evidence + Reportability.**
- Capture E-01, E-05, E-06, E-08, E-13.
- Q1–Q5 generally NO unless the content actually surfaced to an external party — this is most often a control-effectiveness finding (SOX 404, FINRA 3110 supervision) rather than an external reporting trigger.
- However: a *systemic* DLP failure spanning weeks may itself be a material control deficiency requiring SOX disclosure.

### §2.3 — Restricted SharePoint Search Not Enforced After Enable

**Symptoms.**
- Tenant-wide RSS was enabled (per [PowerShell setup](powershell-setup.md)) but Copilot continues to return grounding citations from sites outside the allowlist.
- `Get-SPOTenantRestrictedSearchApplicableSites` returns an empty list despite an intended allowlist population.

**Root cause (most common).**
1. The RSS allowlist defaults empty. Enabling tenant-wide RSS without populating the allowlist results in *no sites being included in Copilot grounding scope at all*. Conversely, the per-site flag `RestrictContentOrgWideSearch` excludes specific sites from Copilot grounding — these are two different mechanisms.
2. Confusion between the two RSS modes: tenant-wide RSS (org-level allowlist) vs. per-site `RestrictContentOrgWideSearch` (per-site exclusion).
3. The `ApplicableToAllSites=$true` parameter was omitted on `Set-SPOTenant -RestrictedSearchApplicability` so the allowlist did not actually take effect.
4. Replication latency: RSS configuration changes can take up to 24 hours to fully propagate.

**Diagnostic.**
1. Capture E-04 (RSS snapshot via **Q-D4**).
2. Confirm tenant-wide RSS state: `Get-SPOTenant | Select-Object RestrictedSearchApplicability`.
3. Cross-reference the actual allowlist (`Get-SPOTenantRestrictedSearchApplicableSites`) against the intended allowlist (from your change-control record).
4. List per-site exclusions (`Get-SPOSite ... | Where RestrictContentOrgWideSearch -eq $true`) and verify they match intent.
5. Check Service Health Dashboard for SharePoint search advisory in past 48 hours.

**Remediation.**
1. If allowlist is empty and intent was to populate it: load the intended sites via `Add-SPOTenantRestrictedSearchAllowedList -SitesListFileUrl <CSV>`.
2. If `ApplicableToAllSites=$true` was omitted: re-run `Set-SPOTenant -RestrictedSearchApplicability ApplicableToAllSites=$true`.
3. If a specific site needs immediate exclusion regardless of allowlist: `Set-SPOSite -Identity <url> -RestrictContentOrgWideSearch $true`.
4. Document all changes in change-control with timestamp, operator, and approver.

**Validation.**
1. Wait at least 4 hours after change for replication. Re-run **Q-D4** and confirm allowlist matches intent.
2. As a test user, run a Copilot prompt that previously returned an out-of-scope citation and confirm the citation no longer appears.
3. Run **Q-D3** (KQL) and confirm zero out-of-scope grounding events post-change.

**Evidence + Reportability.**
- Capture E-01, E-04, E-13.
- Q1–Q5 generally NO unless out-of-scope citations actually exposed customer NPI/MNPI to unauthorized users.
- This is typically a SOX 404 / FINRA 3110 control-effectiveness finding.

### §2.4 — Endpoint DLP Bypass via Non-Edge Browser

**Symptoms.**
- A user copies content from a Copilot response in Chrome, Firefox, or Safari, and the configured Endpoint DLP egress action (block / warn / audit) does not fire.
- The same content in Microsoft Edge correctly triggers the egress action.

**Root cause.**
1. Endpoint DLP for non-Edge browsers requires the **Microsoft Purview browser extension** to be installed and enrolled in the device's Purview agent. Edge has *native* enforcement built in. This is not a policy bug — it is an architectural distinction.
2. The Purview browser extension is not deployed via Intune to the affected device.
3. The user is using an unsupported browser entirely (e.g., Brave, Vivaldi) — the Purview extension supports a defined set of browsers (currently Chrome and Firefox; verify current Microsoft Learn list).
4. The device is not Intune-enrolled or not onboarded to Microsoft Defender for Endpoint, so the Purview agent has no enforcement context.

**Diagnostic.**
1. Capture E-07 (Endpoint DLP policy + extension inventory).
2. Confirm device onboarding state: Microsoft Defender XDR → Devices → onboarding status.
3. Confirm Purview browser extension installed via Intune device-config report.
4. Identify the user's browser usage pattern via UAL `BrowserUsageReport` if available.

**Remediation.**
1. **Immediate compensating control:** Apply a Conditional Access app-control policy that forces the user (or group) to access Microsoft 365 only via Edge for the duration of the gap.
2. **Short term:** Deploy Microsoft Purview browser extension to all in-scope devices via Intune. Document the Intune configuration profile in change-control.
3. **Medium term:** Update acceptable-use policy to require Edge or a supported Purview-extension browser for accessing Copilot. Communicate via the standard end-user policy update channel.
4. **Block the gap permanently:** Where the user role does not require non-Edge browsers, apply Conditional Access to enforce Edge only for Copilot.

**Validation.**
1. On the affected device, install Purview browser extension. Re-test the egress action in Chrome and confirm enforcement fires.
2. Pull Intune compliance report to confirm extension deployment to all in-scope devices.
3. Re-run UAL audit for Endpoint DLP events in the affected device's browser.

**Evidence + Reportability.**
- Capture E-01, E-07, E-08, E-13.
- Q1 NO unless content actually exited the device boundary to an unauthorized destination.
- Q2 / Q4 evaluation if a systemic gap is discovered.

### §2.5 — Copilot Pages Stored Outside Retention Scope (Recordkeeping Gap)

**Symptoms.**
- Periodic recordkeeping verification reveals that Copilot Pages created by users are not under any active retention policy.
- A regulated communication (e.g., research-related summary, customer-correspondence draft) was created in Copilot Pages and was deleted by the author with no retention enforcement.

**Root cause.**
- **Copilot Pages are .fluid files stored in the author's OneDrive — NOT in SharePoint.** Therefore SharePoint-scoped retention policies do not cover them. OneDrive retention policies do, but many tenants apply OneDrive retention only to leavers, not to all users.
- This is an architectural recordkeeping gap. SEC 17a-4(f) requires all "communications relating to the broker-dealer's business" to be preserved in WORM-equivalent format. A Copilot Page that drafts customer correspondence or summarizes regulated content qualifies.

**Diagnostic.**
1. Capture E-09 (Pages inventory via Graph `/me/drive/root/search` filtered to `.fluid` extension across all in-scope users).
2. Confirm OneDrive retention policy scope: `Get-RetentionCompliancePolicy | Where-Object { $_.OneDriveLocation -ne $null }`.
3. Cross-reference Pages owners against retention-scope membership.
4. Sample a representative set of Pages and assess content sensitivity.

**Remediation.**
1. **Immediate:** Apply Purview eDiscovery (Premium) hold on all Pages authors' OneDrive accounts pending policy expansion. This freezes deletes without disrupting active work.
2. **Short term:** Expand OneDrive retention policy to cover all licensed users, not just leavers, with a retention period that meets SEC 17a-4(f) (≥6 years for broker-dealer records, with the first 2 years in immediately accessible form).
3. **Medium term:** Implement a Copilot Pages governance policy: define which user roles may use Pages for which content categories. Train users that Pages are subject to recordkeeping.
4. **Long term:** Where Copilot Pages produces output that must be preserved as a formal business record, require export to a SharePoint document library under retention scope before sharing.

**Validation.**
1. Confirm OneDrive retention policy scope expansion via `Get-RetentionCompliancePolicy ... | Get-RetentionComplianceRule`.
2. Sample a Pages file, attempt to delete it as the author, and confirm the deletion is intercepted by retention.
3. Verify the Pages file appears in Purview Content Search with `IsRecord:true` filter.

**Evidence + Reportability.**
- Capture E-01, E-09, E-13.
- This is a SEC 17a-4(f) recordkeeping finding *even if no confidentiality breach occurred*. It must be documented and reported through internal compliance channels and is examination-discoverable.
- Q1–Q5 generally NO. Q4 (FINRA 4530) MAY apply if the firm previously certified completeness of supervision controls and this gap contradicts that certification.

### §2.6 — Copilot Notebook in Loop Container Not Preserved (Recordkeeping Gap)

**Symptoms.**
- Periodic recordkeeping verification reveals Copilot Notebooks created in a Loop workspace are not preserved by any retention policy.
- A Notebook used to track research positions or compliance reviews was deleted with no retention enforcement.

**Root cause.**
- **Copilot Notebooks live in Microsoft Loop containers, which are a separate workload from SharePoint and OneDrive.** Retention policies must explicitly target the Loop workload (`Set-RetentionCompliancePolicy -ModernGroupLocation` or the Loop-specific scope when available — verify current Microsoft Learn guidance).
- Loop workspaces also have their own storage location (often Loop SharePoint Embedded containers), which may not be visible in SharePoint Admin Center.

**Diagnostic.**
1. Capture E-09 (Notebook inventory) — list Loop workspaces via Loop workspace API or the M365 admin Loop reporting view.
2. Confirm retention policy scope: `Get-RetentionCompliancePolicy | Select-Object Name, *Location*` and verify Loop workload coverage.
3. Cross-reference Notebook owners against Wall Crossing list, MNPI access list, or other regulated-content rosters.

**Remediation.**
1. **Immediate:** Apply eDiscovery (Premium) hold on identified Loop workspaces.
2. **Short term:** Configure retention policy that targets the Loop workload with a retention period matching SEC 17a-4(f) requirements.
3. **Medium term:** Define a Loop and Notebooks governance posture: which user roles may create Loop workspaces, what content classifications are permitted, what naming conventions for Notebooks identify regulated content.
4. **Long term:** Periodic review of Loop workspace inventory by Records Officer.

**Validation.**
1. Sample a Notebook, attempt to delete, confirm retention intercepts.
2. Verify Notebook appears in eDiscovery search results.

**Evidence + Reportability.**
- Capture E-09, E-13.
- Same SEC 17a-4(f) examination posture as §2.5.

### §2.7 — Multi-Geo Cross-Region Grounding Violation

**Symptoms.**
- A user in EU PreferredDataLocation prompts Copilot, and the response includes grounding citations from US-region SharePoint sites containing customer data subject to EU data-residency contractual commitments.
- A periodic Multi-Geo verification reports cross-region grounding events.

**Root cause.**
1. RSS allowlist includes sites in regions outside the user's PreferredDataLocation.
2. The user's PreferredDataLocation was changed but the user's existing OneDrive and Teams home was not re-provisioned to the new region.
3. A document was shared cross-region prior to Copilot enablement and is now grounding-eligible.
4. The Microsoft 365 Copilot service architecture, while EU Data Boundary-compliant for in-scope EU users, may surface non-EU grounding sources if the *content itself* is hosted outside the EU. The Data Boundary commitment covers Microsoft's processing of customer data; it does not change which content is accessible to a user.

**Diagnostic.**
1. Capture E-10 (Multi-Geo configuration snapshot).
2. Capture E-04 (RSS allowlist).
3. Capture E-02 (Copilot transcripts) — extract citation regions from each grounded URL.
4. Cross-reference user PreferredDataLocation against grounded site PreferredDataLocation.

**Remediation.**
1. **Immediate:** Suspend Copilot license for affected users pending policy correction.
2. **Short term:** Restrict RSS allowlist to the user's PreferredDataLocation regions. Where multi-region access is a business requirement, document the contractual basis (customer consent, data-processing agreement).
3. **Medium term:** Implement per-region Copilot policies if the tenant has multiple regulatory regimes.
4. **Long term:** Establish a Multi-Geo governance posture documenting which content categories may cross which boundaries, with sign-off from Privacy Officer and General Counsel.

**Validation.**
1. Re-test affected user prompts and confirm no cross-region citations.
2. Pull a Multi-Geo cross-region grounding KQL query and confirm zero events.

**Evidence + Reportability.**
- Capture E-01, E-02, E-04, E-08, E-10, E-13.
- If the cross-region content was customer NPI: Q1 (Reg S-P) YES. Note: Reg S-P does not specifically address data-residency, but a cross-border NPI exposure is a "covered incident."
- GDPR (where applicable): Article 33 — supervisory-authority notification within 72 hours of awareness for personal-data breaches likely to result in risk.
- Customer contractual notice may be required if data-residency commitments were broken.

### §2.8 — Encrypted/Labeled Content Decrypted Incorrectly by Copilot

**Symptoms.**
- A document protected with a sensitivity label that includes rights protection (e.g., "Highly Confidential — Restricted Decryption to Owners Only") is grounded by Copilot for a user who lacks decryption rights, AND the response contains the protected content in clear text.
- Conversely (false positive): a user *with* decryption rights cannot get Copilot to summarize a document they can open in Word.

**Root cause (clear-text exposure scenario).**
1. The document was labeled but the rights-protection ("encrypted") setting was not applied — it has only a header/footer/visual marker.
2. Co-authoring with rights-protected files in Office for the web has specific requirements; if these are not met the document may temporarily fall back to plaintext rendering pathways that bypass label rights-protection at grounding time.
3. The user obtained decryption rights via a Group membership change that was not yet propagated when policy was authored.

**Root cause (false-positive scenario).**
1. The user has decryption rights in Word but the Copilot service principal performing the grounding does not have the equivalent decryption rights (requires correct Azure Information Protection unified labeling configuration).
2. The label policy excludes the user's UPN from the policy scope.

**Diagnostic.**
1. Capture E-06 (label policy export).
2. Confirm label rights-protection: `Get-Label -Identity "<name>" | Select-Object EncryptionEnabled, EncryptionRightsDefinitions`.
3. For the affected document, check current label state via Graph `/sites/{id}/drive/items/{id}?$select=sensitivityLabel` and `Get-AIPFileStatus`.
4. Confirm Copilot service-principal rights via tenant configuration (refer to Microsoft Learn Copilot + Purview integration reference for current required configuration).

**Remediation (clear-text exposure).**
1. **Immediate:** Apply correct rights-protection to the label and re-label the affected document(s).
2. Apply eDiscovery hold on the user(s) who received the clear-text response.
3. Suspend Copilot license for affected user pending review.
4. **Short term:** Audit all sensitivity labels to confirm rights-protection is applied where the label policy intent requires it.

**Remediation (false positive).**
1. Confirm Copilot tenant configuration matches current Microsoft Learn guidance for label decryption integration.
2. Re-test after Copilot tenant configuration update.

**Validation.**
1. Re-test labeled-content prompt as both authorized and unauthorized users; confirm correct behavior in each case.
2. Run a verification suite covering all label policies in the tenant.

**Evidence + Reportability.**
- Capture E-01, E-02, E-06, E-08, E-13.
- If protected content surfaced in clear text to an unauthorized user: Q1 / Q2 / Q3 / Q4 evaluation as in §2.1.

### §2.9 — Recovery from Broad Oversharing Incident

**Symptoms.**
- The incident scope expands beyond a single user/site to a tenant-wide pattern (e.g., a broad "Everyone" share, a misconfigured Microsoft 365 group, a tenant-wide DLP policy that was inadvertently disabled).
- Multiple SEV-1 incidents are merged into a single recovery operation.

**Root cause.** Compound — typically a combination of: deferred SharePoint hygiene (legacy "Everyone" assignments), a recent change to RCD/RSS/DLP that introduced a regression, and gaps in the verification cadence that allowed the regression to persist undetected.

**Diagnostic.**
1. Convene the Recovery Team: Incident Commander, CISO, AI Governance Lead, SharePoint Admin, Purview Compliance Admin, Compliance Officer, Privacy Officer, General Counsel.
2. Capture full evidence floor (E-01 through E-13) for the broadest defensible time window.
3. Run SharePoint Advanced Management Data Access Governance reports tenant-wide.
4. Run **Q-D5** to identify all RCD anomalies.
5. Run **Q-D4** to confirm RSS state.
6. Run **Q-D7** to confirm all DLP for Copilot policies are enabled and correctly scoped.

**Remediation.**
1. **Immediate (within 1 hour):** Suspend Copilot for the affected user population (entire tenant, geo, or business unit) via Entra group-based license assignment change.
2. **Short term (within 24 hours):** Apply tenant-wide compensating controls per §1.4. Communicate to affected users via approved Communications channel (see §5).
3. **Medium term (within 7 days):** Remediate root causes per §2.1–§2.8 in priority order.
4. **Long term (within 30 days):** Re-baseline the verification cadence. Implement automation (Sentinel analytic rules, Power Automate flows, Logic Apps) for continuous detection of the failure pattern.
5. **PIR:** Conduct full §7 PIR with Board Audit Committee briefing if SEV-1.

**Validation.**
1. Re-enable Copilot incrementally — start with a pilot population of 10 users for 48 hours, expand to 100 for 1 week, then full population.
2. Run the verification suite after each expansion.
3. Confirm no new SEV-1 or SEV-2 incidents during incremental re-enablement.

**Evidence + Reportability.**
- Capture full E-01 through E-13.
- Multi-question reportability evaluation: typically Q1, Q2, Q3, Q4 all require evaluation.
- 8-K materiality determination is a Board-level conversation.

---
## §3 — Reportability Decision Tree (Reference)

This section expands §1.2 with annotated rule text and decision-procedure detail. Use it when General Counsel and Compliance Officer evaluate the formal reportability questions. The §1.2 table is the operational quick-reference; this section is the substantive support.

### §3.1 — Q1: SEC Regulation S-P §248.30(a)(3) — Customer Notification

**Rule.** SEC Regulation S-P, §248.30 (revised July 2024), requires covered institutions to provide notice to affected individuals as soon as practicable but in no event later than **30 days** after the firm becomes aware that unauthorized access to or use of customer information has occurred or is reasonably likely to have occurred.

**Effective dates.** Large entities (registrant ≥$1.5B in assets, ≥1,000 customers): December 3, 2025. Smaller entities: June 3, 2026.

**Definition of "customer information."** Includes any record containing nonpublic personal information about a customer.

**Decision procedure.**
1. Was customer NPI involved? If NO → Q1 = NO.
2. Has unauthorized access or use occurred OR is it reasonably likely to have occurred? If "reasonably likely" → Q1 = YES.
3. Is there a federal or state law-enforcement request to delay notice? If YES → Q1 = YES with delay documented.
4. Document the date of awareness — this starts the 30-day clock.
5. Notice content: nature of incident, dates of incident, types of information involved, contact for inquiries, recommended steps for individuals.

**Owner.** Privacy Officer + General Counsel jointly.

### §3.2 — Q2: SEC Form 8-K Item 1.05 — Material Cybersecurity Incident

**Rule.** Item 1.05 of Form 8-K (in effect since Dec 18, 2023 for large filers; Jun 15, 2024 for smaller reporting companies) requires registrants to disclose a material cybersecurity incident within **4 business days** of determining that the incident is material.

**Definition of "material."** A matter is material if there is a substantial likelihood that a reasonable shareholder would consider it important. The SEC has indicated qualitative as well as quantitative materiality applies.

**Decision procedure.**
1. Did the incident impair the firm's operations, customer relationships, financial condition, or expose data of consequence? If NO → likely Q2 = NO.
2. Materiality determination must be made "without unreasonable delay" — track the date.
3. The 4-business-day clock starts at the date of materiality determination, not at the date of discovery.
4. Disclosure should describe nature, scope, timing, and material impact OR reasonably likely material impact.
5. Permitted delay: U.S. Attorney General determination that immediate disclosure poses substantial risk to national security or public safety.

**Owner.** General Counsel + Chief Financial Officer + Disclosure Committee.

### §3.3 — Q3: NYDFS 23 NYCRR §500.17(a) — Cybersecurity Event Notice

**Rule.** Within **72 hours** of determining that a "Cybersecurity Event" has occurred, NY-licensed Covered Entities must notify the NYDFS Superintendent if the event meets specified thresholds (e.g., notice required to a government body, self-regulatory agency, or supervisory body; OR a reasonable likelihood of materially harming any material part of the normal operations).

**Decision procedure.**
1. Is the firm NYDFS-regulated? If NO → Q3 = NO.
2. Does the event meet a §500.17(a)(1) or §500.17(a)(2) threshold? If YES → Q3 = YES.
3. The 72-hour clock starts at determination, not discovery. Document the determination memo.
4. Notification is via NYDFS Cybersecurity Portal.
5. Subsequent notice: filing of Cybersecurity Event Compliance Notice (annual) and follow-up information as it becomes available.

**Owner.** CISO + General Counsel jointly.

### §3.4 — Q4: FINRA Rule 4530 — Reporting Requirements

**Rule.** FINRA Rule 4530(a) requires member firms to report specified events within **30 calendar days** after the firm knows or should have known of the existence of any of the conditions listed in 4530(a)(1)–(8). FINRA Notice 25-07 specifically addresses AI-related supervision considerations.

**Decision procedure.**
1. Does the incident involve a customer complaint, regulatory action, criminal/civil action, or other 4530(a)-listed event? If YES → Q4 = YES.
2. The 30-day clock starts at "knew or should have known" — document the date.
3. Reporting via FINRA Gateway.
4. Quarterly reporting under 4530(d) covers customer complaints separately.

**Owner.** Compliance Officer + FINRA Designated Supervisor.

### §3.5 — Q5: FTC Safeguards Rule §314.4(j) — Notification to FTC

**Rule.** Effective May 13, 2024. Financial institutions subject to the Safeguards Rule must notify the FTC within **30 days** of discovering a "notification event" — defined as unauthorized acquisition of unencrypted customer information of **500 or more consumers**.

**Decision procedure.**
1. Is the firm subject to the FTC Safeguards Rule? (Most broker-dealers are dual-regulated; both SEC Reg S-P and FTC Safeguards may apply.)
2. Were ≥500 consumers affected by unauthorized acquisition of unencrypted customer information? If YES → Q5 = YES.
3. Notification via FTC online portal.

**Owner.** Privacy Officer + General Counsel.

### §3.6 — Q6: Federal Reserve SR 11-7 / OCC Bulletin 2011-12 — Model Risk Management

**Rule.** SR 11-7 and OCC 2011-12 establish supervisory expectations for model risk management at banking organizations. Generative AI used in regulated decision-making qualifies as a model. Material model failures must be documented and reported through the firm's model-risk governance.

**Decision procedure.**
1. Did Copilot output inform a regulated decision (credit, market risk, customer suitability, AML, BSA)? If NO → Q6 = NO for the supervisory model-risk dimension (but still document under general AI governance).
2. Was the output inaccurate, biased, or unexplainable in a way that affected the decision?
3. Is the output traceable in the model inventory?

No external clock, but failure to document in the model inventory is examination-discoverable.

**Owner.** Model Risk Officer + Compliance Officer.

### §3.7 — Q7: AAL Step-Down + State Privacy

**Rule.** NIST SP 800-63B requires re-binding of authentication when AAL is stepped down or credentials are compromised. State privacy and breach-notification statutes apply to incidents involving consumer personal information (CCPA/CPRA in California, Shield Act in NY, 201 CMR 17.00 in MA, and equivalent in 50 states).

**Decision procedure.**
1. Was credential material exposed or AAL stepped down? If YES → re-bind authentication, force MFA re-registration.
2. Were consumers in any state affected? If YES → consult state-by-state matrix maintained by Privacy Officer.
3. Most states require notice "in the most expedient time possible and without unreasonable delay" with hard caps ranging from 30 to 90 days.

**Owner.** Privacy Officer + CISO.

---

## §4 — Evidence Preservation

This section codifies the evidence floor introduced in §1.3 with capture procedures and retention specifications.

### §4.1 — Capture Order

The mnemonic **"UAL first, mutate last"** governs the capture order. Many remediation actions reduce or alter telemetry that the evidence floor depends on.

1. **E-01 (UAL).** Trigger first. Use the broadest defensible time window (incident detection ±48 hours minimum; expand to ±7 days for confirmed SEV-1).
2. **E-02 (Copilot transcripts).** Apply Purview eDiscovery (Premium) hold immediately to lock the affected user mailboxes and Copilot interaction history.
3. **E-03 (RCD), E-04 (RSS), E-05 (DLP), E-06 (labels), E-07 (Endpoint DLP).** Capture in parallel — these are configuration snapshots and do not change quickly.
4. **E-08 (account state), E-09 (Pages/Notebooks), E-10 (Multi-Geo).** Capture before any user-account changes.
5. **E-11 (service health), E-12 (communication artifacts).** Capture continuously throughout incident.
6. **E-13 (manifest).** Generate at incident close; signed by IC and Compliance Officer.

### §4.2 — SHA-256 Manifest Generation

```powershell
# Generate manifest for an evidence directory
$evidenceDir = "C:\Evidence\INC-2026-0407-001"
$manifest = @{
    incident_id = "INC-2026-0407-001"
    control = "4.7"
    severity = "SEV-1"
    incident_commander = "ic@contoso.com"
    compliance_officer = "co@contoso.com"
    captured_at_utc = (Get-Date).ToUniversalTime().ToString("o")
    artifacts = @()
}
Get-ChildItem -Path $evidenceDir -File -Recurse | ForEach-Object {
    $hash = (Get-FileHash -Path $_.FullName -Algorithm SHA256).Hash
    $manifest.artifacts += @{
        id = $_.Name.Split('-')[0]
        filename = $_.Name
        sha256 = $hash
        size_bytes = $_.Length
    }
}
$manifest | ConvertTo-Json -Depth 10 | Out-File "$evidenceDir\E-13-manifest.json" -Encoding UTF8
```

### §4.3 — WORM Storage Targets

SEC Rule 17a-4(f) requires preservation in a non-rewriteable, non-erasable format. Two acceptable patterns:

1. **Microsoft Purview Records Management with regulatory record locks.** Apply a retention label marked as "Regulatory record" and lock the policy. Once locked, neither Purview Compliance Admin nor any other role can shorten the retention or remove the record.
2. **Designated Third Party (D3P) attested storage.** Per SEC Release 34-96034 (October 2022), an alternative to traditional WORM is a D3P that holds the firm's records and can produce them on regulator request even if the broker-dealer cannot. Examples include cloud-based WORM-equivalent services with D3P attestation letter on file.

The evidence pack (E-01 through E-13) must be written to one of these patterns within 72 hours of incident close.

### §4.4 — Retention Periods

| Artifact | Retention | Citation |
|---|---|---|
| E-01 UAL | 10 years | SEC 17a-4(b)(4); SEC 17a-4(f) for storage format |
| E-02 Copilot transcripts | 10 years | SEC 17a-4(b)(4) — "communications relating to broker-dealer business" |
| E-03 through E-08, E-10 | 7 years | SEC 17a-3 records of original entry; 17a-4 retention rule |
| E-09 Pages/Notebooks inventory | 10 years | SEC 17a-4(b)(4); recordkeeping artifact for examination |
| E-11 service health | 7 years | Internal control evidence (SOX 404) |
| E-12 communications | 10 years | SEC 17a-4(b)(4); attorney-client privilege handled separately |
| E-13 manifest | 10 years | Tied to evidence pack |

### §4.5 — Audit-Log Retention Configuration Verification

```powershell
# Confirm UAL retention policy is in place for the relevant record types
Connect-IPPSSession
Get-UnifiedAuditLogRetentionPolicy | Select-Object Name, RecordTypes, RetentionDuration, Priority
```

If `RecordTypes` does not include `CopilotInteraction`, `SharePointFileOperation`, `MipLabel`, `DLPEndpoint`, `DLPRuleMatch`, the policy must be updated to ensure the 10-year retention applies to these record types.

---

## §5 — Communication and Escalation

### §5.1 — L1–L4 Escalation Ladder

| Level | Trigger | Audience | Channel | Maximum Time to Notify |
|---|---|---|---|---|
| **L1** | Incident classified per §1.1 | Incident Commander | Primary on-call paging | At classification |
| **L2** | IC assigned | AI Governance Lead, Purview Compliance Admin, SharePoint Admin, Records Officer | Dedicated incident Teams channel (eDiscovery hold pre-applied) | 30 min after IC assignment |
| **L3** | SEV-1 OR Q1–Q5 evaluates YES | Compliance Officer, Privacy Officer, General Counsel, Model Risk Officer (if Q6 YES) | Phone call followed by written summary | 1 hour after L3 trigger |
| **L4** | 8-K materiality assessment, NYDFS clock starting, Board-level reportable event | CISO, CFO, CEO, Board Audit Committee chair, FINRA Designated Supervisor | Phone call; written summary only after Counsel approval | 2 hours after L4 trigger |

### §5.2 — Microsoft Support Engagement Pack

When the incident requires Microsoft engagement (e.g., suspected service-side issue, request for additional telemetry), prepare the following before opening the case:

| Item | Source |
|---|---|
| Tenant ID | Entra admin center → Overview |
| Affected workload(s) | E-01, E-02 |
| UAL excerpt covering the incident window | E-01 |
| Configuration exports (RCD, RSS, DLP, labels) | E-03 through E-07 |
| Service Health Dashboard correlation IDs | E-11 |
| Reproducible test case (where applicable) | Verification playbook |
| Severity (Microsoft severity, not internal severity) | Microsoft Support documentation |
| Business impact statement (single paragraph) | IC + Compliance Officer |

Open the case via Microsoft 365 admin center → Support. For SEV-A (Microsoft severity) cases, follow up with Premier or Unified support TAM/CSAM by phone.

### §5.3 — Internal Stakeholder Communication Templates

**Template 1 — L3 Notification to Compliance and Counsel:**

```
Subject: [INC-YYYY-MMDD-NNN] SEV-1 Copilot Data Governance — Initial Notification

Incident Commander: <name>
Detection time (UTC): <ts>
Severity: SEV-1
Affected workload: <Copilot in BizChat / Pages / Notebook / agent>
Affected users (estimated): <count or range>
Affected data classification: <Public/Internal/Confidential/HC/NPI/MNPI/regulated comm>

Reportability tree (initial assessment):
  Q1 (Reg S-P): YES/NO/UNKNOWN
  Q2 (8-K materiality): YES/NO/UNKNOWN
  Q3 (NYDFS 72hr): YES/NO/UNKNOWN
  Q4 (FINRA 4530): YES/NO/UNKNOWN
  Q5 (FTC Safeguards): YES/NO/UNKNOWN
  Q6 (SR 11-7): YES/NO/UNKNOWN
  Q7 (state privacy): YES/NO/UNKNOWN

Compensating controls applied: <list>
Evidence floor capture: INITIATED / IN-PROGRESS / COMPLETE

Next briefing: <ts>
```

**Template 2 — L4 Notification (Board-Level):**

To be drafted by General Counsel using Counsel's privileged-communication template. Do not freelance. Do not send via email until Counsel approves.

### §5.4 — External Communication Holds

No external communication (customer notice, press, regulator) without:
1. General Counsel written approval, AND
2. CISO written approval, AND
3. (For 8-K) CFO and Disclosure Committee approval.

Premature external communication can prejudice law-enforcement coordination and create securities-law disclosure timing issues.

---
## §6 — Recovery Procedures

### §6.1 — Sensitivity Label Rollback

If a sensitivity-label change is the root cause (incorrect label scope, wrong rights-protection setting), roll back via:

1. Identify the previous label policy version. Purview retains label policy version history — `Get-LabelPolicy -Identity <name> | Select-Object DistributionStatus, ModifiedTime`.
2. Re-author the label policy to the previous configuration.
3. Re-publish to the same scope.
4. Confirm policy distribution: `Get-LabelPolicy | Select-Object DistributionStatus`.
5. For documents that were re-labeled during the gap, re-apply the original label via Purview Information Protection scanner or PowerShell `Set-AIPFileLabel` for sample sets.

### §6.2 — DLP Policy Rollback

1. Capture the current DLP state (E-05) before rollback.
2. Identify the prior policy version. Where Purview does not retain detailed version history, your change-control system should hold the prior export.
3. Disable the new policy: `Set-DlpCompliancePolicy -Identity <name> -Mode Disable`.
4. Re-import the prior policy via `New-DlpCompliancePolicy` and `New-DlpComplianceRule`.
5. Confirm rule effectiveness via **Q-D2** within 4 hours.

### §6.3 — RSS Allowlist Rollback

1. Capture current state via **Q-D4**.
2. Identify the prior allowlist via change-control system.
3. Replace allowlist: `Add-SPOTenantRestrictedSearchAllowedList` with the prior CSV (or use `Remove-` and re-`Add-` operations to converge).
4. Confirm: `Get-SPOTenantRestrictedSearchApplicableSites` matches the intended state.
5. Wait at least 4 hours for replication.

### §6.4 — Endpoint DLP Rollback

1. Capture current state (E-07).
2. Disable the new policy via `Set-DlpCompliancePolicy -Identity <name> -Mode Disable`.
3. Re-enable the prior policy from the prior export.
4. For Intune-deployed Purview browser extension changes, roll back the Intune configuration profile via the Intune admin center.

### §6.5 — Pages and Notebooks Containment

For incidents where Pages or Notebooks contain regulated content discovered after the fact:

1. Apply Purview eDiscovery (Premium) hold on the Pages/Notebook authors' OneDrive (for Pages) and Loop workspaces (for Notebooks). This freezes deletes.
2. Snapshot the file list (E-09) and hash each file via **§4.2**.
3. Where business-record status is confirmed by Records Officer, export the file to a SharePoint document library under retention scope.
4. Where the content should never have existed in Pages/Notebooks per governance policy, work with the user to formalize the content into the appropriate system of record (CRM, document management system, regulated-communications archive).

### §6.6 — Broad Oversharing Recovery

For tenant-wide oversharing scope, the recovery follows §2.9 with these additions:

1. **Phase 1 — Containment.** Suspend Copilot license via Entra group change for the affected population. This is reversible and does not destroy evidence.
2. **Phase 2 — Surface area reduction.** Apply per-site `RestrictContentOrgWideSearch` to all sites containing high-classification content as a temporary belt-and-suspenders measure.
3. **Phase 3 — Root-cause remediation.** Per §2.1–§2.8.
4. **Phase 4 — Incremental re-enablement.** Pilot 10 users for 48 hours, expand to 100 for 1 week, then full population. Run verification suite at each expansion.
5. **Phase 5 — Sustained verification.** Implement automated continuous detection (Sentinel analytic rules) for the failure pattern.

---

## §7 — Post-Incident Review

A Post-Incident Review (PIR) is mandatory for SEV-1 and SEV-2; recommended for SEV-3; optional for SEV-4. The PIR is led by the Incident Commander, attended by all L2 and (for SEV-1) L3 stakeholders, with output written to the incident-management knowledge base and (for SEV-1) presented to the Board Audit Committee.

### §7.1 — RCA Template

```
Incident: INC-YYYY-MMDD-NNN
Severity (final): SEV-X
Detection time (UTC): <ts>
Containment time (UTC): <ts>
Resolution time (UTC): <ts>
Total duration: <hh:mm>
Reportability outcome: <list of Q's evaluated YES and notice filed>

What happened:
  <2-3 paragraph narrative>

Why it happened (5 Whys):
  Why 1: ...
  Why 2: ...
  Why 3: ...
  Why 4: ...
  Why 5: ...

What we did well:
  - ...

What did not go well:
  - ...

What we learned:
  - ...

Action items:
  - [Owner] [Due date] [Description]
  - ...

Action items rolled to next quarter:
  - ...
```

### §7.2 — Standing PIR Questions (10)

1. Was the incident detected by an automated control or by user report? If user report, what was the gap in automated detection?
2. Was severity classification correct on first triage? If revised, why?
3. Did the reportability tree (§3) produce the correct Q1–Q7 outcomes? Any missed clocks?
4. Was the evidence floor (§4) captured in full and within the "UAL first, mutate last" order? Any gaps?
5. Were compensating controls (§1.4) applied within the maximum gap duration?
6. Was the L3/L4 communication ladder (§5) initiated at the correct trigger?
7. Did Microsoft Support engagement (§5.2) provide value commensurate with the time invested?
8. Was the recovery (§6) executed without introducing new failure modes?
9. Were users impacted by the remediation given clear, accurate, and timely communication?
10. What automation can prevent the next occurrence? Specify Sentinel rule, Power Automate flow, KQL alert, or process change.

### §7.3 — Action-Item Tracking

PIR action items are tracked in the standard incident-management system with:
- Owner (named individual, not team)
- Due date (specific calendar date, not "Q3")
- Acceptance criteria (measurable)
- Re-review at 30 / 60 / 90 days

### §7.4 — Board Audit Committee Briefing (SEV-1 Only)

Briefing materials prepared by Incident Commander, reviewed by General Counsel, presented by CISO and Compliance Officer. Include:
- Incident summary (single page)
- Reportability decisions and external notices filed
- Root cause and remediation summary
- Action items and ownership
- Implications for the firm's broader cybersecurity and AI governance program

---

## §8 — Anti-Patterns

The following 20 anti-patterns are recurring causes of Control 4.7 incidents in FSI tenants. Avoid them in design, implementation, and incident response.

### §8.1 — Enabling Tenant-Wide RSS Without Populating the Allowlist

**Pattern.** SharePoint Admin enables tenant-wide RSS to "lock things down." Allowlist defaults empty. No site is in scope for Copilot grounding.

**Why it fails.** Either (a) Copilot returns no useful results and users circumvent via Pages/Notebooks/external tools, or (b) the admin then disables RSS to "fix" it, creating a worse posture than before.

**Fix.** Populate the allowlist before or simultaneously with enabling RSS. Use change-control to track allowlist composition.

### §8.2 — Treating RCD as a Substitute for SharePoint Permission Hygiene

**Pattern.** Team treats RCD as a magic constraint that "solves oversharing." Defers SharePoint permission cleanup indefinitely.

**Why it fails.** RCD constrains *grounding to user-scoped content*. If the user's permission scope is overbroad, RCD does not narrow it. Pre-existing oversharing surfaces in Copilot output.

**Fix.** Implement RCD AND SharePoint Advanced Management Data Access Governance reviews in parallel. Treat RCD as one layer in defense-in-depth.

### §8.3 — Confusing Tenant-Wide RSS With Per-Site `RestrictContentOrgWideSearch`

**Pattern.** Admin uses both mechanisms inconsistently, creating a tenant state where some sites are "allowlisted" tenant-wide but per-site flagged as restricted, or vice versa.

**Why it fails.** The two mechanisms are orthogonal. Per-site `RestrictContentOrgWideSearch` excludes a site from Copilot grounding regardless of allowlist status; tenant-wide RSS allowlist includes only listed sites in grounding. A site can be in both sets, leading to non-obvious behavior.

**Fix.** Document which mechanism is the primary control. Pick a default model (typically tenant-wide allowlist + per-site exclusion for sensitive sites) and reconcile state quarterly.

### §8.4 — Assuming Edge Endpoint DLP Behavior in Chrome/Firefox

**Pattern.** Endpoint DLP is configured. Verification is performed only in Edge. Non-Edge browsers are assumed to behave the same.

**Why it fails.** Edge has *native* enforcement; Chrome and Firefox require the Microsoft Purview browser extension. Without the extension, egress actions do not fire.

**Fix.** Verify Endpoint DLP in every supported browser. Where the extension is not deployed, restrict access via Conditional Access app-control.

### §8.5 — Ignoring Copilot Pages in Recordkeeping

**Pattern.** Retention policies cover SharePoint and Exchange. Copilot Pages are forgotten because they are "just drafts."

**Why it fails.** Pages live in OneDrive (.fluid files) and may contain regulated content (drafts of customer correspondence, summaries of MNPI). SEC 17a-4(f) does not distinguish drafts from final. Authors deleting Pages without retention coverage is a recordkeeping violation.

**Fix.** Apply OneDrive retention policy to all licensed users. Train users that Pages are subject to recordkeeping. Where output is the system of record, formalize via SharePoint export.

### §8.6 — Ignoring Copilot Notebooks in Loop Containers

**Pattern.** Same as §8.5 but for Notebooks living in Loop workspaces.

**Why it fails.** Loop is a separate workload from SharePoint and OneDrive. Retention policies must explicitly target the Loop workload. Failure to do so leaves Notebooks unpreserved.

**Fix.** Configure Loop-targeted retention. Inventory Loop workspaces quarterly.

### §8.7 — Allowing Copilot Studio Agents to Bypass DLP via Service Account

**Pattern.** A Copilot Studio agent uses a connection backed by a service account. The service account is not in DLP for Copilot policy scope. The agent's prompts to Copilot are not subject to DLP enforcement.

**Why it fails.** DLP scoping by user identity does not cover non-user identities. Agents become the easiest exfiltration path in the tenant.

**Fix.** Include all service accounts that back Copilot Studio agent connections in DLP scope. Periodically inventory agent connections and reconcile against DLP scope.

### §8.8 — Trusting "Test with Notifications" as Production State

**Pattern.** DLP policy is created in Test mode for staged rollout. Months later, the policy is still in Test mode and is treated as enforcing.

**Why it fails.** Test mode does not block; it only logs and notifies. Users continue to access content the policy was intended to restrict.

**Fix.** Track all policies' Mode field. Quarterly review. Policies in Test mode for >90 days require justification or transition to Enable.

### §8.9 — Skipping the License Tally Before RCD Go-Live

**Pattern.** RCD is configured. License tally check (per **Q-D5**) is not run. Some users targeted for RCD have zero or multiple Copilot licenses.

**Why it fails.** RCD has a hard prerequisite of exactly one assigned Copilot license. Without it, RCD is silently a no-op for the user. Users assume they are constrained when they are not.

**Fix.** Run **Q-D5** before, immediately after, and quarterly after RCD go-live. Alert on anomalies.

### §8.10 — Using "All Company" or "Everyone Except External Users" as a Sharing Default

**Pattern.** SharePoint sites and OneDrive folders are shared with "Everyone except external users" by default to "make collaboration easy."

**Why it fails.** Copilot grounding inherits these permissions. The "everyone" pattern is the single largest source of Copilot oversharing in FSI tenants.

**Fix.** Disable "All Company" / "Everyone except external users" as a sharing option at the tenant level. Use Microsoft 365 group membership for collaboration scope.

### §8.11 — Treating Sensitivity Labels as Visual Markers Only

**Pattern.** Labels are deployed with header/footer text only — no rights-protection (encryption).

**Why it fails.** DLP for Copilot can match on labels even without encryption, but without rights-protection the underlying content is not encrypted at rest. If a user obtains the file by another path (download, share), the content is in clear text. Defense-in-depth is broken.

**Fix.** For Highly Confidential and equivalent classifications, configure rights-protection (encryption) on the label. Test the encrypted-content scenario in §2.8.

### §8.12 — Assuming EU Data Boundary Covers All Cross-Region Risk

**Pattern.** EU customers are reassured that the EU Data Boundary ensures EU residency. No further controls applied.

**Why it fails.** The EU Data Boundary commitment covers Microsoft's processing of customer data. It does not change which content is accessible to a user. If a user in the EU has access to a US-region SharePoint site, Copilot can ground on that content. Anthropic was added as a Microsoft subprocessor on January 7, 2026, and is outside the EU Data Boundary — verify whether Copilot scenarios in your tenant invoke Anthropic-routed processing.

**Fix.** Layer Multi-Geo, RSS allowlist by region, and explicit content-residency policies on top of the EU Data Boundary. Document the subprocessor map.

### §8.13 — Assuming Copilot Is Available in GCC-H or DoD

**Pattern.** Sovereign-cloud customer assumes Microsoft 365 Copilot is generally available in GCC-H or DoD.

**Why it fails.** As of April 2026, Microsoft 365 Copilot in GCC-H is in limited preview. DoD availability is even more constrained. Customers assuming general availability deploy controls expecting full feature parity that does not exist.

**Fix.** Verify current Copilot availability in your sovereign cloud via Microsoft Learn and your account team. Document the feature-parity gap and adjust controls accordingly.

### §8.14 — Skipping the Q1–Q7 Reportability Tree Until Day 25

**Pattern.** Incident detected Day 1. Compliance Officer not involved until Day 25 of the 30-day Reg S-P clock.

**Why it fails.** Q1 evaluation is not just notification timing — it determines investigation scope, customer-list assembly, and notice content. Late evaluation creates a fire drill that often misses the clock.

**Fix.** Q1–Q7 evaluated by IC and Compliance Officer within 4 hours of SEV-1 declaration. Documented in incident ticket regardless of Y/N outcome.

### §8.15 — Using Email for L4 Communications

**Pattern.** L4 (board-level) initial notification sent via email.

**Why it fails.** Email creates a written record before Counsel has approved messaging. Securities-law and litigation-discovery exposure follows.

**Fix.** L4 phone-call first. Written summary only after Counsel approval.

### §8.16 — Mutating State Before Capturing UAL

**Pattern.** Responder revokes user license, suspends agent, removes site permission BEFORE pulling UAL.

**Why it fails.** Many state changes alter what is queryable in UAL. Some service operations show only the post-change state. Investigators lose the ability to prove pre-incident scope.

**Fix.** "UAL first, mutate last." E-01 capture is the first action after evidence-floor initiation.

### §8.17 — Treating PIR as Optional for SEV-2

**Pattern.** PIR is held for SEV-1 only. SEV-2 incidents are closed with a brief ticket comment.

**Why it fails.** SEV-2 incidents are the leading indicator of SEV-1. Skipping PIR loses the learning that prevents the next SEV-1.

**Fix.** PIR mandatory for SEV-2. Use a streamlined template if needed (single page) but capture root cause and action items.

### §8.18 — Allowing Copilot Studio Agents Without Inventory

**Pattern.** Copilot Studio is enabled. Agents are created freely. No inventory of agents, owners, connections, or grounding sources.

**Why it fails.** Each agent is a potential bypass of the controls in this playbook. Without inventory, the surface area for incidents grows monotonically.

**Fix.** Maintain an agent inventory. Periodic review of connections, scopes, and decommissioning of orphan agents. See Pillar 2 controls for full agent governance.

### §8.19 — Ignoring Service Health Dashboard During Triage

**Pattern.** Responder assumes the failure is policy-side and skips Service Health Dashboard check.

**Why it fails.** Microsoft service issues affect Copilot grounding, DLP enforcement, and label propagation. Ignoring the SHD wastes triage time and may lead to "remediating" a problem that was not on the customer side.

**Fix.** §1.5 item 11. Always check SHD and Message Center during pre-escalation.

### §8.20 — Failing to Reconcile Configuration Drift Quarterly

**Pattern.** RCD, RSS, DLP, and label configurations are set up once. Quarterly verification (per [verification testing](verification-testing.md)) is skipped because "nothing has changed."

**Why it fails.** Configuration drift is constant — through Microsoft service updates, admin changes, group membership shifts, and tenant license changes. Drift compounds. Eventually a control that was correct in Q1 is materially failed in Q4.

**Fix.** Mandatory quarterly verification using the cadence in the verification playbook. Report results to Compliance Officer. Use SAM Site Lifecycle Management and Data Access Governance for continuous reporting.

---

## Related Resources

- Microsoft Learn: [Microsoft 365 Copilot data protection](https://learn.microsoft.com/microsoft-365-copilot/microsoft-365-copilot-privacy)
- Microsoft Learn: [Restricted SharePoint Search](https://learn.microsoft.com/sharepoint/restricted-sharepoint-search)
- Microsoft Learn: [DLP for Microsoft 365 Copilot](https://learn.microsoft.com/en-us/purview/dlp-microsoft365-copilot-location-learn-about)
- Microsoft Learn: [Microsoft Purview Audit (Premium)](https://learn.microsoft.com/purview/audit-premium)

---

[Back to Control 4.7](../../../controls/pillar-4-sharepoint/4.7-microsoft-365-copilot-data-governance.md) | [Portal Walkthrough](portal-walkthrough.md) | [PowerShell Setup](powershell-setup.md) | [Verification Testing](verification-testing.md)

---

*Updated: April 2026 | Version: v1.6.2 | UI Verification Status: Current*