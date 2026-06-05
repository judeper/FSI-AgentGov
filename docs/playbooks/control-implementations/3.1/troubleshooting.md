# Control 3.1 — Agent Inventory and Metadata Management: Troubleshooting Playbook

> **Scope.** Failure modes, diagnostics, and FSI-aligned incident handling for Control 3.1 (Agent Inventory and Metadata Management). Use this playbook when the consolidated agent inventory is incomplete, drifted, tampered with, or mis-classified across Microsoft 365 Copilot Hub, Power Platform Admin Center (PPAC), Microsoft Graph, Microsoft Purview, and the governance register.
>
> **Audience.** AI Governance Lead, Power Platform Admin, Purview Compliance Admin, Entra Global Admin, Information Security, Compliance Operations, Internal Audit.
>
> **Use this with.** [Control 3.1 — Agent Inventory and Metadata Management](../../../controls/pillar-3-reporting/3.1-agent-inventory-and-metadata-management.md) · [Portal Walkthrough](portal-walkthrough.md) · [PowerShell Setup](powershell-setup.md) · [Verification & Testing](verification-testing.md) · [AI Incident Response Playbook](../../incident-and-risk/ai-incident-response-playbook.md).
>
> **Regulatory note.** Reportability decisions in this playbook are escalation aids, not final determinations. Compliance, Legal, and the BSA/AML/Privacy Officer (where applicable) make the final call on regulator notifications. Use the decision tree in §1.2 to escalate quickly, not to decide unilaterally.

---

## §1 — FSI Incident Handling (READ FIRST)

A missing, drifted, or tampered agent inventory is rarely "just" an inventory bug. In a regulated US financial services tenant, the consolidated inventory is the **system of record** that supervisory, books-and-records, model-risk, and privacy obligations rely on. Any meaningful gap is presumptively in scope for FINRA Rule 3110 (supervision), FINRA Rule 4511 / SEC Rule 17a-4(b)(4) (recordkeeping), SEC Reg S-P §248.30, NYDFS 23 NYCRR §500.16/§500.17, OCC Bulletin 2026-13 (formerly OCC Bulletin 2011-12) / Federal Reserve SR 26-2 (formerly SR 11-7) (model risk management), and CFTC Rule 1.31 until proven otherwise. Treat this section as the **first thing you read** when an inventory anomaly is detected; the seven pillars (§2) and eight runbooks (§3) operate inside the framing it sets.

### §1.1 Severity Matrix

The severity rating drives the response clock, the escalation ladder (L1–L5, §1.6), the evidence floor (§1.3), and the reportability tree (§1.2). When in doubt, rate **up** — downgrading later is cheap; missing a 72-hour or 4-business-day clock is not.

| Severity | Inventory-specific trigger | Initial response | Communication | Examples |
|---|---|---|---|---|
| **SEV-1** | A regulated-zone (Zone 3) production agent is in active use but absent from the consolidated inventory; OR inventory tampering with intent suspected; OR inventory unavailable during an active examiner / audit pull | Immediate (≤15 min triage); SIRT engaged; Compliance & Legal paged | Executive sponsor, CISO, Chief Compliance Officer, General Counsel within 1 hour | Z3 RM Copilot agent in usage logs but not in PPAC, Hub, Graph, or register; Active supervisory agent silently moved to "Decommissioned" |
| **SEV-2** | Material lifecycle-state corruption; >50 orphaned (departed-owner) agents; metadata fields critical to supervision or DLP scoping (zone, owner, business unit, regulated-data flag) missing or stale at scale; reconciliation between Hub/PPAC/Graph/register diverges by >5% | ≤1 hour triage; AI Governance Lead + Purview Compliance Admin engaged | Pillar 3 stakeholders + Compliance Operations notified within 4 hours | DLP policy orphan affecting Z3 agents; Purview audit log gap >24h preventing reconciliation |
| **SEV-3** | Single-source inventory failure with another source still authoritative (e.g., Hub list fails to render but PPAC + Graph + register agree); slow reconciliation drift <5%; metadata enrichment job failure with no regulated-zone impact | ≤4 hour triage; standard ticket | Owner + AI Governance Lead | Hub UI 500 error during refresh; nightly enrichment Logic App fails with retry |
| **SEV-4** | Cosmetic/UX issue, single-agent metadata typo, advisory drift in non-regulated (Zone 1 personal) scope | Next business day | Ticket queue | One Z1 agent's display name mis-cased |

**Inventory-specific aggravating factors that bump severity up one level:**

- The affected agent or agent population processes customer NPI (GLBA-regulated), PHI, or material non-public information (MNPI).
- The affected agent is classified as a "model" under Fed SR 26-2 (formerly SR 11-7) / OCC Bulletin 2026-13 (formerly OCC 2011-12) (decisioning, valuation, risk scoring, surveillance).
- The anomaly occurred during an active regulatory exam, audit, internal investigation, litigation hold, or LegalOps preservation request.
- The inventory drift is correlated with personnel changes (departing privileged user, reorganization, M&A integration).

**Severity bumps must be documented**, including the operator who applied the bump, the trigger, and the time. This is examiner-grade evidence.

### §1.2 Reportability Decision Tree (Q1–Q10)

> **Disclaimer.** Reportability is a Compliance / Legal determination. Use this tree to **escalate**, not to **decide**. Every "Yes" or "Maybe" answer triggers an escalation to Compliance with the supporting evidence package; Compliance owns the final notification decision and timing.

Walk every SEV-1 and SEV-2 inventory incident through Q1–Q10 within the first 60 minutes. Document the answer to every question, even "No," in the incident record. The set of "Yes / Maybe" answers determines the escalation path, the regulator(s) potentially in scope, and the clock(s) that may have started.

| # | Rule / authority | Question to ask | If Yes / Maybe → |
|---|---|---|---|
| **Q1** | FINRA Rule 3110 (Supervision) | Did the inventory gap remove a supervisor's, principal's, or compliance officer's ability to see, monitor, or supervise an agent that produces or assists with communications, advice, recommendations, or trading activity? | Escalate to CCO; document the supervisory blind window (start time, end time); preserve all interactions in the window. |
| **Q2** | FINRA Rule 4511 / SEC Rule 17a-4(b)(4)/(f) | Could the gap have caused a record required to be made or preserved (including agent metadata, configuration, prompts, outputs, or audit trails) to be lost, altered, deleted, or rendered non-WORM? | Escalate to CCO + Records Management; trigger 17a-4(f) WORM preservation review; preserve under retention hold. |
| **Q3** | FINRA Rule 4530 | Is there evidence of insider misconduct, intentional concealment, or a registered representative attempting to evade supervision via the agent? | Escalate to CCO + HR + Legal; preserve all evidence under privilege; consider 4530(a)/(b)/(d) reporting paths. |
| **Q4** | FINRA RN 24-09 / Rule 3110 (AI obligations) | Did the gap involve an AI tool used in a member-firm capacity (research, advice, communications, surveillance) such that supervisory and recordkeeping obligations under existing rules apply with AI-specific considerations? | Escalate to CCO; document the AI-specific control gap; align response with existing 3110/4511 obligations. |
| **Q5** | SEC Reg S-P §248.30(a)(3) | Did the agent have access to, or could the gap have caused unauthorized exposure of, customer non-public personal information (NPI)? | Escalate to CCO + Privacy Officer + Legal; trigger Reg S-P incident-response procedures; assess customer notification. |
| **Q6** | SEC Form 8-K Item 1.05 (registrant) | Has a "material" cybersecurity incident likely occurred (qualitative / quantitative materiality)? | Escalate to CCO + General Counsel + Disclosure Committee; **4-business-day clock starts upon materiality determination**. |
| **Q7** | NYDFS 23 NYCRR §500.17(a) | Has a cybersecurity event materially affecting normal operations or requiring notice to a government / SRO occurred? | Escalate to CISO + General Counsel; **72-hour determination/notification clock starts upon discovery**. |
| **Q8** | OCC Bulletin 2026-13 (formerly OCC Bulletin 2011-12) / Federal Reserve SR 26-2 (formerly SR 11-7) | Is the affected agent a "model" (drives decisions, valuations, risk scoring, surveillance), and did the gap impair model inventory, performance monitoring, change control, or validation evidence? | Escalate to MRM (Model Risk Management) + CCO; record an MRM finding and remediation plan. |
| **Q9** | GLBA / FTC Safeguards Rule (16 CFR §314) | Did the gap impair the ability to safeguard customer information, or could it amount to a Safeguards Rule control failure? | Escalate to Privacy Officer + CISO; document Safeguards control failure & remediation. |
| **Q10** | CFTC Rule 1.31 / NFA recordkeeping | For swap dealers, FCMs, IBs, CPOs, CTAs: did the gap affect records required to be kept under CFTC Part 1, Part 23, or NFA rules (including AI-assisted trading or surveillance records)? | Escalate to CCO + CFTC-registered entity Compliance; preserve under CFTC-aligned retention. |

A single "Yes" on Q6 or Q7 means a regulatory clock has likely started — log the **clock-start time in UTC** and the operator who logged it.

### §1.3 Evidence Floor (E-01 through E-15)

The evidence floor below is the **minimum** preservation set for every SEV-1 and SEV-2 inventory incident. It is designed for FINRA / SEC / OCC / NYDFS examiner reproducibility. Capture in the order listed (volatile UI surfaces first, durable APIs second, audit & posture last). Land everything in WORM-compliant storage (Purview Records Management or equivalent). Retention floor is the longer of: 7 years, the firm's WSP, or the FINRA / SEC / NFA / state rule that applies to the affected record type.

| ID | Evidence artifact | Source | Capture mechanism | Notes |
|---|---|---|---|---|
| **E-01** | Surface screenshots: Copilot Hub agent list view, PPAC Copilot agents view, Agent 365 (where licensed), governance register UI | Hub / PPAC / Agent 365 / register | Full-page screenshots with visible URL bar, timestamp, operator UPN | Capture **before** any remediation; refresh once and recapture to detect propagation lag. |
| **E-02** | PPAC + Dataverse `bot` table snapshot | Power Platform Admin PowerShell (`Get-AdminPowerApp` for canvas apps; Dataverse Web API for bots) | `Get-AdminPowerApp -EnvironmentName <env>` (canvas only); `GET {orgUrl}/api/data/v9.2/bots` for Microsoft Copilot Studio | **Critical**: `Get-AdminPowerApp` does NOT return Copilot Studio agents. Query Dataverse `bot` and `botcomponent` tables directly. |
| **E-03** | Microsoft Graph snapshot | `graph.microsoft.com` | `GET /applications`, `GET /servicePrincipals` (with appRoleAssignments), `GET /copilot/agents` (preview), `GET /agents` (preview) | Page through all results; capture `@odata.nextLink` chain; record API version. |
| **E-04** | Governance register state | Register store (SharePoint list, Dataverse table, Sentinel watchlist, etc.) | API export with timestamp + operator UPN | Capture register version/etag if available. |
| **E-05** | Purview audit log paginated export | Purview compliance portal / `Search-UnifiedAuditLog` | Export filtered for agent operations across the incident window ±24h | Account for ~60–90 min surfacing latency; do NOT close the search until latency window has elapsed. |
| **E-06** | Microsoft Purview DSPM for AI — Activity Explorer | Purview portal → DSPM for AI | Export filtered to affected agent(s) and zone(s) | Cross-reference to Control 1.6 evidence package. |
| **E-07** | DLP policy inventory snapshot | Purview DLP | `Get-DlpCompliancePolicy`, `Get-DlpComplianceRule` | Confirms whether the affected agent was in/out of scope of expected DLP policy. |
| **E-08** | Retention policy inventory snapshot | Purview Data Lifecycle Management | `Get-RetentionCompliancePolicy`, `Get-RetentionComplianceRule` | Confirms whether the affected agent's outputs were under retention. |
| **E-09** | Sensitivity label state | Purview Information Protection | `Get-Label`, `Get-LabelPolicy`; agent-specific label assignment via Graph | Confirms label-inheritance state at incident time. |
| **E-10** | Entra owner / group state for the agent | Entra ID | `Get-MgApplication`, `Get-MgServicePrincipal`, owner & group memberships | Capture owners' employment status and last sign-in. |
| **E-11** | PIM activation log | Entra PIM | PIM audit export for the incident window | Identifies who held privileged roles when the anomaly occurred. |
| **E-12** | Sign-in logs / Defender for Cloud Apps | Entra sign-in logs + MDA | Export filtered to agent-related sign-ins and admin operations | Helps detect tampering, unusual locations, anomalous service-principal activity. |
| **E-13** | Operator context manifest | Operator workstation | Plaintext file: operator UPN, tenant ID, UTC timestamp, Entra role, PIM activation reference | Required for examiner-grade chain of custody. |
| **E-14** | Module / SDK / API version manifest | Operator workstation | `Get-Module Microsoft.PowerApps.Administration.PowerShell, Microsoft.Graph, ExchangeOnlineManagement \| Format-Table Name, Version`; record API version for any REST calls | Required for reproducibility of the evidence years later. |
| **E-15** | SHA-256 manifest of all artifacts | Operator workstation | `Get-FileHash -Algorithm SHA256` on every E-01..E-14 artifact; sign manifest and land in WORM | Establishes integrity for examiner reproducibility. |

### §1.4 Compensating Controls (while the inventory is degraded)

While inventory is being restored, the following compensating controls help preserve the supervision and recordkeeping perimeter and reduce the likelihood that the gap turns into a reportable books-and-records failure.

- **Freeze new Z3 agent provisioning** in PPAC (DLP Block + maker-restriction) until inventory parity is restored. Document the freeze decision, scope, and ETA.
- **Engage Purview eDiscovery hold** on mailboxes / Teams / SharePoint sites likely to contain agent interactions in the incident window.
- **Increase Purview audit log retention** for the affected workloads to the longer of 1 year or the firm's WSP retention period for the duration of the investigation.
- **Re-baseline the consolidated inventory daily** (instead of the steady-state cadence) using the verification-testing procedures in `verification-testing.md`.
- **Notify supervisors** of the affected business unit(s) of the supervisory blind window so manual supervision compensates.
- **Tighten DLP scope** to "all Copilot Studio agents in environment X" rather than agent-specific scoping, to avoid orphan windows.
- **Disable Power Platform self-service environment creation** if the root cause involves rogue environments.

### §1.5 Pre-Escalation Checklist (≥15 items)

Before escalating to L4 or L5 (Compliance / Legal / Executive), the on-call AI Governance Lead must complete this checklist. The checklist is itself preserved as evidence (it shows reasonable diligence).

1. [ ] Severity rated per §1.1; aggravating-factor bumps documented.
2. [ ] Initial reportability tree (§1.2 Q1–Q10) walked; answers recorded with evidence references.
3. [ ] Operator context manifest (E-13) captured.
4. [ ] Module / SDK / API version manifest (E-14) captured.
5. [ ] Surface screenshots (E-01) captured **before** any remediation.
6. [ ] PPAC + Dataverse `bot` snapshot (E-02) captured for the affected environment(s).
7. [ ] Microsoft Graph snapshot (E-03) captured (paginated, `@odata.nextLink` chain preserved).
8. [ ] Governance register snapshot (E-04) captured.
9. [ ] Purview audit log search (E-05) initiated; surfacing-latency window noted.
10. [ ] DLP / retention / sensitivity-label / Entra-owner snapshots (E-07/08/09/10) captured.
11. [ ] PIM activation log (E-11) reviewed for unusual privileged activations during the window.
12. [ ] SHA-256 manifest (E-15) generated and landed in WORM.
13. [ ] PPAC steady-state refresh window (~15 min) and Purview audit surfacing window (~60–90 min) accounted for; the team has not over-attributed normal latency to a real incident.
14. [ ] `Get-AdminPowerApp` / `Get-AdminPowerAppEnvironmentRoleAssignment` known-gotchas (canvas-only return; empty-no-error return on Dataverse-backed environments) accounted for in the diagnostic conclusion.
15. [ ] Cross-source reconciliation (Hub vs PPAC vs Graph vs register) re-run after waiting for documented latency windows; any remaining drift quantified (count, %).
16. [ ] Compensating controls (§1.4) applied where appropriate; freeze decisions documented.
17. [ ] Communication ladder (§1.6) prepared — recipients, draft summary, attachment list.

### §1.6 Communication Ladder (L1–L5)

| Level | Audience | Trigger | Owner | Channel & cadence |
|---|---|---|---|---|
| **L1** | Owning team (agent owner, business unit governance partner) | Any SEV-3+ | AI Governance Lead | Teams DM / ticket; 1× at incident open + at resolution |
| **L2** | Pillar 3 stakeholders (Reporting & Analytics workstream); AI Governance steering group | SEV-2+ | AI Governance Lead | Teams channel + email; at open, at status changes, at resolution |
| **L3** | Compliance Operations, Information Security on-call, Records Management | SEV-2 with regulated-zone impact, or any "Yes" on Q1/Q2/Q4/Q8 | Purview Compliance Admin | Email + Compliance ticket; within 4h of open |
| **L4** | Chief Compliance Officer, General Counsel, CISO, Privacy Officer | Any SEV-1, or any "Yes" on Q3/Q5/Q6/Q7/Q9/Q10 | CCO delegate (AI Governance Lead) | Page + email + secure call; within 1h of materiality determination |
| **L5** | CEO, Board Risk Committee, Disclosure Committee, external counsel | Confirmed material cyber incident (Q6 / Q7 fired); confirmed customer-NPI exposure; confirmed records loss requiring 17a-4(f) reconciliation | CCO + General Counsel jointly | In-person / secure call + privileged memo; within disclosure clock requirements |

L4 and L5 communications must be drafted with privilege markings and routed through Legal before distribution.

### §1.7 Worked SEV-1 Example — "Project Atlantis"

A regulated relationship-manager (RM) Copilot Studio agent named "Atlantis Advisor" appears in Purview DSPM for AI usage logs at 14:03 ET on a Tuesday. It is making approximately 40 interactions per hour with high-net-worth client data. It is **not** in the Copilot Hub agent list, **not** in the PPAC Copilot agents view, **not** returned by `GET /copilot/agents` in Microsoft Graph, and **not** in the governance register. The triggering signal is a Sentinel detection wired to Control 3.9 that compares Purview Activity Explorer "agent name" cardinality to the consolidated inventory and alerts on net-new entries.

**T+0 (14:03 ET).** Sentinel alert fires; on-call AI Governance Lead acknowledges within 4 minutes. Initial severity rated **SEV-2** pending evidence (regulated zone suspected from the "RM" naming). Operator context manifest (E-13) captured.

**T+0:08.** Surface screenshots (E-01) captured of all four inventory surfaces showing the agent absent. PPAC + Dataverse `bot` snapshot (E-02) launched against the suspected environment ("Wealth-Prod-East"). Initial Dataverse query returns the bot record (`botid`, `name`, `owner`, `createdon`, `modifiedon`, `solutionid`, `componentstate`). Severity bumped to **SEV-1** because (a) the agent is in active production use against client data, (b) it is invisible to four of five inventory sources, (c) the owner field on the Dataverse record points to a user whose Entra account was disabled the prior Friday (departing-employee cascade hint).

**T+0:15.** L3 + L4 paged. Compliance Operations, CCO delegate, CISO on-call joined the bridge. Reportability tree walk (§1.2) initiated. Initial answers: Q1 **Yes** (RM agent → supervisory perimeter); Q2 **Maybe** (records preservation depends on Purview retention scope, which is unconfirmed); Q4 **Yes** (AI tool, member-firm capacity); Q5 **Maybe** (HNW client data → likely NPI in scope); Q6 **TBD** (materiality assessment to be made by Disclosure Committee); Q7 **Maybe** (NYDFS-regulated entity; 72h clock provisionally starts at 14:03 ET); Q8 **No** (advisory, not a "model" under Fed SR 26-2 (formerly SR 11-7)); Q9 **Yes** (Safeguards control failure on customer information); Q10 **N/A** (not a CFTC-registered entity).

**T+0:30.** Compensating controls applied: maker-restriction freeze on net-new Copilot Studio agents in Wealth-Prod-East; Purview eDiscovery hold on the prior owner's mailbox + Teams + OneDrive; supervisory blind-window notification sent to Wealth Management Compliance. Microsoft Graph snapshot (E-03) completed; the agent **is** returned by `GET /copilot/agents` (preview) but with `displayName` differing from the Dataverse record by a single character — explaining why the Hub / PPAC fuzzy joins didn't match.

**T+1:00.** Root cause identified: the agent was created from a Copilot Studio template by the prior owner, then renamed via the Copilot Studio UI in a way that updated the Dataverse `name` but not the Hub-cached `displayName`. PPAC `Get-AdminPowerApp` did not return it because that cmdlet returns canvas apps, not bots. The DLP policy in scope was scoped by `displayName`-prefix and missed it. Purview audit log search (E-05) shows the rename event ~16 hours ago.

**T+2:00.** Eradication plan: re-baseline the agent in the governance register with full canonical metadata; reapply zone classification (Z3); migrate ownership to a service account managed by Wealth Management Operations; widen the DLP scope from `displayName`-prefix to "all bots in Wealth-Prod-East". Recovery plan: re-run consolidated inventory build; verify all four surfaces show the agent within 4 hours (accounting for PPAC ~15-min and Purview ~60–90-min latency).

**T+4:00.** Inventory parity verified across Hub, PPAC, Graph, register. Purview audit log re-search confirms no further drift. Evidence package E-01 through E-15 finalized; SHA-256 manifest signed; landed in WORM with retention hold.

**T+24:00.** Post-Incident Review (§8) convened. Compliance + Legal review the reportability tree walk. NYDFS 72h determination: **non-reportable** (no unauthorized disclosure of NPI confirmed via DSPM + DLP review of the agent's interactions; the 72h clock is closed with documented rationale). Reg S-P customer-notification: **no** (no unauthorized acquisition occurred). Form 8-K Item 1.05 materiality: **immaterial** per Disclosure Committee. FINRA Rule 3110 supervisory-blind-window log preserved; manual supervision review of the agent's interactions completed and logged. MRM finding **not** raised (not a "model"). Lessons-learned items feed §3 runbooks 1, 4, 5, and 6.

### §1.8 Diagnostic Query Reference

A short index of the highest-yield diagnostic queries used throughout this playbook. Full versions are inlined in `powershell-setup.md` and the relevant §3 runbooks.

| Code | Purpose | Source |
|---|---|---|
| **DQ-1** | List Copilot Studio bots in an environment (canonical inventory of the surface that PPAC / Hub depend on) | Dataverse Web API: `GET {orgUrl}/api/data/v9.2/bots?$select=botid,name,createdon,modifiedon,_ownerid_value,componentstate,statecode` |
| **DQ-2** | List declarative agents and Copilot extensions registered to the tenant | Microsoft Graph: `GET /copilot/agents` (preview); `GET /applications?$filter=tags/any(t:t eq 'M365Copilot')` |
| **DQ-3** | Audit recent agent operations (create/update/delete/rename/share) | Purview: `Search-UnifiedAuditLog -Operations 'BotCreated','BotUpdated','BotDeleted','SharePointAppCreated' -StartDate ... -EndDate ...` |
| **DQ-4** | Identify orphaned agents (owner disabled, owner left, owner missing) | Cross-join Dataverse `bot._ownerid_value` ↔ Entra `users.accountEnabled / employeeLeaveDateTime` |
| **DQ-5** | Identify zone / regulated-data classification mismatch | Cross-join governance register `zone` ↔ DSPM Activity Explorer "data classifications observed" |
| **DQ-6** | Identify DLP scope vs. agent population drift | Cross-join `Get-DlpComplianceRule` scope ↔ Dataverse `bot` list per environment |
| **DQ-7** | Identify retention scope vs. agent population drift | Cross-join `Get-RetentionComplianceRule` scope ↔ Dataverse `bot` outputs / Teams sites |

---

## §2 — Seven Troubleshooting Pillars

The seven pillars below are organized by **inventory source** (Pillars 1–4) and **cross-cutting failure mode** (Pillars 5–8). For any incident, walk the relevant pillar first before opening a runbook in §3 — the pillar narrows the failure surface and tells you which evidence to capture.

### §2.1 Pillar 1 — Microsoft 365 Copilot Hub Inventory Failures

**Scope.** Failures of the Copilot Hub admin experience (`https://admin.cloud.microsoft/copilot`) to render, refresh, or export the agent list, including the "Agents" view, the connector inventory, and the per-agent detail blade.

**Common symptoms.**

- The Hub agent list renders but shows fewer agents than expected (compared with PPAC / Graph / register).
- The Hub agent list shows a stale snapshot for >30 min after a known create / rename / delete.
- The Hub UI returns a 500 / "Something went wrong" error on the agents view.
- Per-agent detail blade displays empty owner, environment, or sensitivity-label fields when those exist in source.
- Agent count display is capped (e.g., paged at 500 per environment view).

**Diagnostics.**

1. Confirm the steady-state refresh interval: PPAC and Hub propagate inventory changes within approximately 15 minutes (per Microsoft Learn). If <15 min has elapsed since a write, the symptom is **expected propagation delay**, not a failure. Document and wait.
2. Compare Hub against the canonical Dataverse `bot` table query (DQ-1) for the same environment. A drift of >1 bot after the propagation window is in-scope.
    3. Inspect the Hub URL bar for the `tenantId`. A mis-routed admin session can present as missing agents.
4. Check Service Health for "Microsoft 365 Copilot" and "Power Platform" advisories. Hub-render failures are commonly upstream service incidents.
5. Capture E-01 (Hub screenshot with URL + timestamp + operator UPN).

**Anti-patterns.**

- Treating <15 min propagation delay as an incident.
- Using the Hub agent count as the system-of-record number for examiner responses; the system of record is the consolidated inventory derived from Dataverse + Graph + register.
- Assuming the 500-agent display ceiling in some Hub views is the true ceiling on agents in the environment — it is a UI cap, not a data cap.

**Cross-links.** Pillar 5 (reconciliation), Runbook 1 (inventory drift), Control 3.8 (Copilot Hub dashboard).

### §2.2 Pillar 2 — PPAC Copilot Agent List Failures

**Scope.** Failures of the Power Platform Admin Center Copilot agents view (`https://admin.powerplatform.microsoft.com` → Copilot → Agents) and of the underlying Power Platform Admin PowerShell module.

**Common symptoms.**

- PPAC Copilot agents view returns no rows for an environment that demonstrably contains bots.
- `Get-AdminPowerApp -EnvironmentName <env>` returns an empty result; the operator concludes "no agents" and is wrong.
- `Get-AdminPowerAppEnvironmentRoleAssignment` returns an empty result with no error.
- PPAC paged display caps at 500 rows per environment.

**Diagnostics.**

1. **Critical gotcha.** `Get-AdminPowerApp` returns **canvas Power Apps**, not Copilot Studio agents (bots). For agents, query the Dataverse `bot` table directly (DQ-1). Document this in every PPAC-related ticket so the next operator does not fall into the same trap.
2. **Critical gotcha.** `Get-AdminPowerAppEnvironmentRoleAssignment` returns an empty array **with no error** for Dataverse-backed environments because environment-level role assignments are stored in Dataverse `systemuser` / `roleassignment`, not in the Power Platform admin role store. Use the Dataverse Web API or the Power Platform CLI (`pac admin list-app-users`) instead.
3. Verify that the operator session has the Power Platform Admin role (or Dynamics 365 Service Admin) and that PIM has been activated. Missing scope presents as empty results, not "access denied".
4. Verify the module version (E-14): `Microsoft.PowerApps.Administration.PowerShell` should be at the current published version; older versions silently fail on newer environment types.

**Anti-patterns.**

- Concluding "no agents" from `Get-AdminPowerApp` or `Get-AdminPowerAppEnvironmentRoleAssignment` empty results.
- Sharing a screenshot of a PPAC empty list as evidence without the Dataverse `bot` corroboration.

**Cross-links.** Pillar 3 (Graph), Pillar 5 (reconciliation), Runbook 1, Runbook 2 (departed-owner cascade), Control 3.11 (centralized inventory enforcement).

### §2.3 Pillar 3 — Microsoft Graph Inventory Query Failures

**Scope.** Failures of Microsoft Graph endpoints used to enumerate agents, declarative Copilot extensions, app registrations, and service principals.

**Common symptoms.**

- `GET /copilot/agents` returns 404 or an empty page in a tenant where agents demonstrably exist.
- `GET /applications` does not include declarative agents added via Copilot Studio publishing flow.
- Pagination is not followed; a single page is treated as "all".
- Throttling (HTTP 429) drops results silently in poorly written enumeration scripts.

**Diagnostics.**

1. Confirm the correct Graph host: `graph.microsoft.com`. A misconfigured connection can return **404 with no error context** that suggests a routing problem.
2. Confirm the API version. `/copilot/agents` and `/agents` endpoints are preview; pin and record the version in E-14.
3. Always page through `@odata.nextLink` until null; never rely on a single page. Capture the full page chain in E-03.
4. Confirm the application or delegated permission scope (e.g., `Application.Read.All`, `CopilotSettings.Read.All` where required). Missing consent surfaces as 403 or as filtered (silently empty) results.
5. Honor `Retry-After` on 429s. Throttling-induced gaps look identical to "missing agents" if not retried.
6. Compare Graph against Dataverse `bot` (DQ-1) for the same environment; the Graph and Dataverse views have different shapes (Graph is tenant-wide; Dataverse is per-environment) and require careful join keys.

**Anti-patterns.**

- Single-page enumeration treated as authoritative.
- Using preview endpoints in production evidence packages without recording the API version in E-14.

**Cross-links.** Pillar 5 (reconciliation), Runbook 9 (examiner audit-pull).

### §2.4 Pillar 4 — Agent 365 / Agent Registry Failures

**Scope.** Failures of the Agent 365 admin center (where licensed) and the firm's internal agent registry / inventory store (SharePoint list, Dataverse table, Sentinel watchlist).

**Common symptoms.**

- Agent 365 inventory differs from Hub / PPAC / Graph.
- Agent 365 analytics show usage for an agent that is not enrolled in Agent 365.
- The internal registry's nightly enrichment job runs successfully but produces stale outputs.
- Registry ETag / version drift between read and write produces lost updates.

**Diagnostics.**

1. Confirm Agent 365 license / entitlement scope; some agents may legitimately be out of scope of Agent 365 even though they are in scope of Hub / PPAC.
2. Verify the registry enrichment job's log; "succeeded" without error does not equal "produced fresh data".
3. Verify registry write concurrency control (ETag, optimistic locking). Lost updates present as silent staleness.
4. Verify identity context for the enrichment job (managed identity, app registration). A token-refresh failure can leave the job running but unable to write.

**Anti-patterns.**

- Trusting the registry as the sole system of record without periodic round-trip verification against Hub / PPAC / Graph / Dataverse.
- Running enrichment as a user identity that may rotate or leave.

**Cross-links.** Pillar 5, Pillar 6, Control 3.13 (Agent 365 admin center analytics), Control 3.14 (Agent 365 observability SDK).

### §2.5 Pillar 5 — Cross-Source Reconciliation Failures

**Scope.** Failures of the consolidated inventory build that joins Hub + PPAC/Dataverse + Graph + Agent 365 + register into a single reconciled view.

**Common symptoms.**

- Reconciliation reports persistent drift > 5% between sources after the documented latency windows.
- Join key collisions: two agents with identical `displayName` across environments collapse into one row.
- "Ghost" agents appear in the consolidated view (deleted in source, still in register).
- Reconciliation is run before Purview audit surfacing latency (~60–90 min) elapses, producing false-positive drift.

**Diagnostics.**

1. Use **stable join keys** in this order of preference: (a) Dataverse `botid` (GUID), (b) Graph `id` (object ID), (c) Hub `agentId`. Avoid `displayName` as a join key; it is mutable and non-unique.
2. Wait for the longer of the documented latency windows before declaring drift: PPAC ~15 min, Purview audit surfacing ~60–90 min, Graph propagation typically <5 min.
3. Capture the "as-of" UTC timestamp for each source snapshot in the consolidated build; do not allow snapshots taken hours apart to be treated as a coherent view.
4. Run reconciliation in **append-only** mode against a WORM-backed history table; a snapshot lineage allows examiner reproducibility and avoids "we changed it and lost the prior state" gaps.
5. Maintain an explicit **expected-difference catalog**: agents legitimately in one source and not in another (e.g., Hub-only declarative agents not yet provisioned to Dataverse). Drift outside the catalog is investigated.

**Anti-patterns.**

- Joining on `displayName`.
- Treating sub-15-min drift as a real incident.
- Failing to record source-snapshot timestamps.

**Cross-links.** All §3 runbooks; Control 3.11 (centralized enforcement).

### §2.6 Pillar 6 — Metadata Enrichment Failures

**Scope.** Failures of the metadata-enrichment pipeline that adds canonical fields (zone classification, business unit, regulated-data flag, MRM scope, supervisory ownership, retention class, sensitivity label) to inventory records.

**Common symptoms.**

- Newly discovered agents appear in the inventory with empty enrichment fields.
- Enrichment runs to completion but applies stale taxonomy (business unit codes that have changed, owner mappings out of date).
- Enrichment overwrites a manually corrected field with an incorrect automated value.
- Z3 agents are enriched as Z1 because the heuristic fails on a renamed agent.

**Diagnostics.**

1. Treat enrichment as a **suggestion engine**, not an authority. A field marked "human-reviewed" must never be overwritten by automation; the enrichment pipeline must respect a `lockedBy` attribute.
2. Version the enrichment taxonomy and emit the taxonomy version on every write so historical records can be re-explained.
3. Sample-audit the enrichment output weekly: 25 agents per zone, by Compliance Operations, with results landed in WORM.
4. Where enrichment uses ML / heuristic classification, log the model / rule version and confidence; surface low-confidence rows for human review rather than silent acceptance.

**Anti-patterns.**

- Letting enrichment overwrite human-reviewed fields.
- Running enrichment without a versioned taxonomy.
- Treating low-confidence ML outputs as authoritative for zone assignment.

**Cross-links.** Pillar 5, Runbook 4 (regulatory misclassification), Runbook 6 (sensitivity label inheritance), Control 3.10 (hallucination feedback loop) for enrichment-quality feedback.

### §2.7 Pillar 7 — Lifecycle State Transition Failures

**Scope.** Failures of the lifecycle state machine for agents: Draft → In Review → Approved → Active → Deprecated → Decommissioned. Failures include incorrect transitions, missing transitions, and silent regressions.

**Common symptoms.**

- An agent is marked "Decommissioned" in the register but is still active in PPAC / Dataverse and producing interactions.
- An agent is marked "Active" in the register but the underlying bot has been deleted from Dataverse (lifecycle-state corruption).
- Approval workflow completes without recording the approver's identity or timestamp.
- Lifecycle transitions occur outside the workflow (manual register edit) without an associated change-control record.

**Diagnostics.**

1. Reconcile lifecycle state against Dataverse `bot.statecode` / `componentstate` and against the most recent Purview audit `BotDeleted` events.
2. Require a **change-control reference** (ticket ID, approver UPN, UTC timestamp) for every lifecycle transition; reject transitions without one at the register write layer.
3. For Decommissioned transitions, retain the agent record (do not delete) and apply a long-term retention label aligned to FINRA 4511 / SEC 17a-4(b)(4) record-class retention.
4. Where the bot is deleted from Dataverse but still appears Active in the register, treat as **lifecycle-state corruption**; open Runbook 7.

**Anti-patterns.**

- Allowing manual register edits to bypass the lifecycle state machine.
- Deleting Decommissioned agents from the register before the retention floor elapses.
- Treating Decommissioned as "we can stop preserving evidence".

**Cross-links.** Runbook 7 (lifecycle state corruption), Control 3.6 (orphaned-agent detection), Control 3.12 (governance exception & override).


## §3 — Eight Failure-Mode Runbooks

> **Disclaimer.** Reportability columns are escalation aids. Compliance / Legal makes the final notification call.

Each runbook follows the eight-block shape: **Severity & triggers → Immediate actions (T+0 → T+30) → Investigation → Containment → Eradication → Recovery → Lessons learned → Reporting decision tree**.

### §3.1 Runbook 1 — Inventory Drift Discovered (Production Agent Not in Inventory)

**Severity & triggers.** SEV-1 if regulated-zone (Z3) production agent missing from any inventory source AND active in usage logs. SEV-2 if Z2 agent missing. SEV-3 if Z1 agent missing or if agent is in build/test environment.

**Immediate actions (T+0 → T+30).**

1. Acknowledge alert; capture E-01 (surface screenshots), E-13 (operator manifest), E-14 (module/SDK manifest).
2. Identify the affected environment(s); run DQ-1 (Dataverse `bot` query) to confirm the agent exists in source.
3. Run DQ-2 (Graph) and PPAC PowerShell against the same environment .
4. Wait the longer of 15 min (PPAC propagation) or 90 min (Purview audit surfacing) **before** concluding the gap is real, unless usage-log evidence makes the gap operationally undeniable.
5. Walk Q1–Q10 (§1.2); record answers.

**Investigation.**

- Identify when the agent was created (Dataverse `createdon`); cross-reference with Purview audit (DQ-3) to find the create event.
- Identify the creator's Entra account state; capture E-10 (Entra owner state) and E-11 (PIM activation log).
- Determine why each inventory source missed the agent (was Hub display name divergent? was DLP scope wrong? was Graph paging incomplete?).
- Sample 50 of the agent's interactions (DSPM Activity Explorer, E-06) to assess data-class exposure.

**Containment.**

- Apply maker-restriction freeze on the affected environment.
- Apply Purview eDiscovery hold to the agent owner's mailbox / Teams / OneDrive.
- Notify the supervisory chain of the affected business unit of the supervisory blind window.

**Eradication.**

- Re-baseline the agent in the governance register with full canonical metadata (zone, owner, business unit, regulated-data flag, lifecycle state, sensitivity label).
- Widen the DLP scope rule that missed the agent; deploy and verify scope.
- Fix the join-key issue in the consolidated inventory build that hid the agent (if `displayName`-based, migrate to `botid`).

**Recovery.**

- Re-run consolidated inventory build; verify all four surfaces show the agent within the documented latency windows.
- Run a 7-day re-baseline at daily (not steady-state) cadence to confirm no recurrence.

**Lessons learned.** Feed into Pillar 5 (reconciliation) and Pillar 6 (enrichment) controls. Update verification-testing test cases.

**Reporting decision tree.** Q1, Q2, Q4, Q5, Q9 are the typical "Yes" answers. Q6 / Q7 depend on materiality and unauthorized-disclosure findings. CCO + Legal own the final call.

### §3.2 Runbook 2 — Departed-Owner Cascade (>50 Orphaned Agents)

**Severity & triggers.** SEV-2 baseline; SEV-1 if any orphaned agent is Z3 with regulated data, OR if the departed user held privileged Power Platform admin roles.

**Immediate actions (T+0 → T+30).**

1. Run DQ-4 (orphaned-agent identification): cross-join Dataverse `bot._ownerid_value` with Entra users where `accountEnabled = false` or `employeeLeaveDateTime < now()`.
2. Bucket the orphan list by zone, by environment, and by regulated-data flag.
3. For Z3 orphans, capture E-01 through E-15 immediately; for Z2 / Z1, capture the inventory snapshots and proceed to investigation.
4. Walk Q1–Q10; Q1 (supervisory) and Q3 (insider misconduct) require special attention if the departure was involuntary or under investigation.

**Investigation.**

- For each departed owner, retrieve from HR the departure date/time, departure reason, and any active investigation flag (privilege-protected; route through Legal).
- Run Purview audit (DQ-3) for the 30 days before departure; identify any anomalous bot creation, sharing, or export operations.
- Identify whether the departed owner held PIM-eligible Power Platform / Dataverse admin roles; if so, capture PIM activation history (E-11).

**Containment.**

- Reassign ownership of all orphaned agents to a service account managed by the relevant business unit (do **not** reassign to a single individual).
- For Z3 orphans, place under maker-restriction freeze pending validation.
- Apply Purview eDiscovery hold on the departed owner's mailbox / Teams / OneDrive if not already held.

**Eradication.**

- Establish or refresh the joiner-mover-leaver (JML) integration that fires owner-reassignment within 24 h of departure.
- For each orphan, decide: Decommission (if no business owner can be found) or Re-home (with new owner approval).

**Recovery.**

- Re-run consolidated inventory; verify zero orphans within 24 h.
- Schedule a quarterly orphan-detection sweep (Control 3.6).

**Lessons learned.** Update onboarding/offboarding runbooks; ensure Power Platform Admin role is in PIM with reasonable activation duration; ensure agents created by departing users are flagged at offboarding intake.

**Reporting decision tree.** Q1 likely **Yes** for any Z3 orphan; Q2 **Yes** if any orphan held records subject to 17a-4; Q3 **Maybe** if any departure was for-cause; Q5/Q9 **Maybe** if any orphan accessed customer NPI.

### §3.3 Runbook 3 — Inventory Tampering Detected

**Severity & triggers.** SEV-1 in all cases. Tampering means: an agent was deleted, hidden, renamed, or had its metadata altered in a manner suggesting evasion of supervision or recordkeeping. Triggers include: Purview audit shows a `BotDeleted` event without a corresponding change-control ticket; register row was directly edited bypassing the workflow; lifecycle state regressed from Active to Draft / Decommissioned outside policy; mass `displayName` rename event correlated with departing-employee or under-investigation user.

**Immediate actions (T+0 → T+30).**

1. **Engage Legal immediately** under privilege; do not discuss findings outside the privileged channel.
2. Capture E-01 through E-15 immediately, including E-05 (Purview audit log) and E-11 (PIM activations) for the suspected actor.
3. Place a litigation hold on the suspected actor's mailbox / Teams / OneDrive / OneDrive Recycle Bin.
4. Walk Q1–Q10; Q3 (FINRA 4530 insider misconduct) and Q2 (records integrity) are nearly always **Yes**.
5. Do **not** revert the tampered records before evidence preservation is complete; the tampered state is itself evidence.

**Investigation.**

- Reconstruct the timeline from Purview audit (DQ-3), Entra sign-in logs, and PIM activations.
- Cross-reference with Defender for Cloud Apps anomaly detections and Microsoft Sentinel alerts (Control 3.9).
- If the actor used a service principal, identify how the actor obtained credentials (consent grant, certificate / secret).
- Determine the scope of records affected (count, business units, regulated-data exposure).

**Containment.**

- Suspend the suspected actor's privileged role assignments (PIM, eligible & active).
- Rotate any service-principal credentials the actor may have accessed.
- Freeze all maker / approver actions in the affected environment(s) pending investigation.

**Eradication.**

- Restore the tampered records from the consolidated inventory history table (Pillar 5 append-only WORM lineage).
- Re-validate every restored record against source (Dataverse / Graph) before returning to operational use.
- Implement compensating controls: require dual-control for Decommission transitions; deny direct register edits outside the workflow.

**Recovery.**

- Run a full consolidated inventory rebuild; reconcile against the pre-tampering snapshot.
- Compliance + Internal Audit review of the restored state.

**Lessons learned.** Tighten audit alerting on the specific tampering signatures observed; add a Sentinel detection (Control 3.9) for the pattern; update WSP and JML procedures.

**Reporting decision tree.** Q1, Q2, Q3, Q4 are typical **Yes**. Q6 / Q7 highly likely if the tampering scope is material. Q5 / Q9 if customer-NPI-related. Q10 for CFTC-registered entities.

### §3.4 Runbook 4 — Regulatory Misclassification (FINRA Communications Agent Miscategorized as Zone 1)

**Severity & triggers.** SEV-2 baseline; SEV-1 if the misclassification persisted for >7 days or affected >25 communications interactions with customers.

**Immediate actions (T+0 → T+30).**

1. Confirm the misclassification by walking the agent through the firm's zone-classification taxonomy (regulated-data flag, supervisory scope, member-firm-capacity test).
2. Capture E-01 through E-09 (DLP / retention / sensitivity-label scope at the time of misclassification).
3. Identify the population of interactions produced under the wrong classification; export from DSPM Activity Explorer (E-06).
4. Walk Q1–Q10; Q1, Q2, Q4 are typical **Yes**.

**Investigation.**

- Determine the classification error mode: enrichment heuristic miss (Pillar 6), human reviewer error, Z1 default applied to a Z3 agent at creation, or zone-bypass via governance exception (Control 3.12).
- Reconstruct what supervision / DLP / retention controls **should** have been in scope and **were** in scope during the misclassification window.
- Identify whether any communications produced under the wrong classification require principal review under FINRA 3110 / 2210.

**Containment.**

- Reclassify to the correct zone (typically Z3 for FINRA Comms agents); reapply DLP / retention / sensitivity-label scope.
- Apply Purview retention hold to the back-population of interactions to prevent expiration before principal review completes.

**Eradication.**

- Update the enrichment heuristic / taxonomy to prevent the same miss class.
- Add a Sentinel detection for "Z1 agent producing high-volume customer-domain interactions" as an early warning.

**Recovery.**

- Compliance / supervisory principals review the back-population of interactions; document review per FINRA 3110.
- Re-run reconciliation to confirm no other agents share the same misclassification pattern.

**Lessons learned.** Strengthen Pillar 6 enrichment quality controls; require Compliance sign-off before zone-downgrade transitions; require a "regulated-communications" gate at agent creation that cannot be bypassed silently.

**Reporting decision tree.** Q1 **Yes**, Q2 **Yes** (potential records-integrity gap on retention scope at creation), Q4 **Yes**. Q5/Q9 if customer NPI was processed. Q6/Q7 if material.

### §3.5 Runbook 5 — DLP Policy Orphan (Zone 3 Agent Without DLP Scope)

**Severity & triggers.** SEV-1 if the orphan is a Z3 agent with regulated-data access for >24 h. SEV-2 if Z3 with no observed regulated-data interaction yet. SEV-3 if Z2.

**Immediate actions (T+0 → T+30).**

1. Identify the orphan via DQ-6 (DLP scope vs. agent-population cross-join).
2. Capture E-07 (DLP policy inventory at incident time).
3. Walk Q1–Q10; Q5, Q9 are typical attention areas; Q2 if records went outside DLP-controlled paths.

**Investigation.**

- Identify why the agent fell outside scope: scope rule used `displayName` prefix that didn't match a renamed agent; environment was newer than the rule's environment list; agent was created by a maker outside the rule's user-scope; rule was scoped by location/group that excluded the agent's site.
- Sample DSPM Activity Explorer (E-06) for the orphan window to determine whether any regulated-data interactions occurred.

**Containment.**

- Widen the DLP scope to cover the agent (and its environment-cohort) immediately.
- If a regulated-data interaction is suspected, route through DLP incident-response (Control 1.6 / 1.7).

**Eradication.**

- Migrate DLP scope rules from `displayName`-prefix patterns to **environment-wide + bot-type** scoping.
- Add a daily reconciliation that flags any Z3 agent not covered by an expected DLP policy.

**Recovery.**

- Confirm the orphan and its peers are now in scope; verify with a synthetic policy-test interaction.
- Re-run reconciliation for 7 days to confirm no recurrence.

**Lessons learned.** Update Control 1.6 / 1.7 implementation; add Sentinel detection for newly created Z3 agents not yet in DLP scope.

**Reporting decision tree.** Q5/Q9 if NPI exposed; Q2 if records-integrity affected.

### §3.6 Runbook 6 — Sensitivity Label Inheritance Failure

**Severity & triggers.** SEV-2 baseline; SEV-1 if a Z3 agent's outputs are unlabeled and were shared externally or to broad internal audiences.

**Immediate actions (T+0 → T+30).**

1. Identify the failure via DSPM Activity Explorer + Purview Information Protection logs (E-06, E-09).
2. Capture the agent's expected label policy and the actual label state on its outputs.
3. Walk Q1–Q10; Q5/Q9 attention if NPI-bearing outputs were unlabeled; Q2 if labels drive retention.

**Investigation.**

- Determine the inheritance failure mode: container label not applied to host site / Team; agent output channel (chat vs. file vs. message) outside label policy; auto-labeling rule not triggered due to content / location filters; Purview label cache stale.
- Identify the population of unlabeled outputs and their disclosure scope (private chat, channel, externally shared file).

**Containment.**

- Apply correct labels via Purview bulk relabel where possible; revoke external sharing on unlabeled files pending review.
- For documents that left the tenant, route through the data-disclosure incident-response process.

**Eradication.**

- Fix the container-label inheritance for the host Team / site.
- Add auto-labeling rules covering the agent's output paths.

**Recovery.**

- Re-validate label state on a sample of new outputs after fix.
- 30-day surveillance via DSPM to detect any further unlabeled outputs.

**Lessons learned.** Strengthen the Pillar 6 enrichment to require a sensitivity-label assignment at agent registration; require label-inheritance verification as part of approval workflow.

**Reporting decision tree.** Q5/Q9 likely **Yes** if NPI-bearing outputs were exposed. Q6/Q7 if material.

### §3.7 Runbook 7 — Lifecycle State Corruption (Active but Deleted)

**Severity & triggers.** SEV-2 baseline; SEV-1 if the corrupted record affects supervisory ownership of an active customer-facing agent.

**Immediate actions (T+0 → T+30).**

1. Identify the corruption via Pillar 7 reconciliation: register `lifecycleState = Active` while Dataverse `bot.statecode = Inactive` or bot record absent.
2. Capture E-04 (register state) and DQ-1 (Dataverse `bot` snapshot, including `componentstate`).
3. Walk Q1–Q10; Q1 / Q2 typical attention.

**Investigation.**

- Reconstruct the deletion: who deleted the bot, when, with what change-control reference (DQ-3 Purview audit).
- Determine whether the deletion was authorized (legitimate decommission that failed to flip the register) or unauthorized (Runbook 3 territory — escalate to tampering if unauthorized).

**Containment.**

- If unauthorized, escalate to Runbook 3 (tampering).
- If authorized but mis-recorded, place the register record under hold pending correction.

**Eradication.**

- Apply correct lifecycle state in the register with the proper change-control reference and approver UPN.
- For Decommissioned records, apply long-term retention label per FINRA 4511 / SEC 17a-4(b)(4).

**Recovery.**

- Re-run lifecycle-state reconciliation across the inventory.
- Add a daily check: register Active records that lack a corresponding Dataverse bot.

**Lessons learned.** Tighten lifecycle state machine: deny direct register edits outside the workflow; require Dataverse-side validation before Active transition.

**Reporting decision tree.** Q1 **Yes** if supervision was affected; Q2 **Yes** if records were lost; Q3 **Maybe** if unauthorized.

### §3.8 Runbook 8 — Examiner Audit-Pull (FINRA / OCC / Fed Snapshot As-Of-Date)

**Severity & triggers.** Operational, not an incident in the SEV-1..SEV-4 sense, but **handle with SEV-1-equivalent care**. Triggers include: FINRA Rule 8210 request; SEC examination request; OCC / Federal Reserve examination request; NYDFS examination request; CFTC / NFA request; internal audit; litigation discovery.

**Immediate actions (T+0 → T+30).**

1. Engage Legal and Compliance immediately. All audit-pull responses route through Legal; do not respond directly to the examiner.
2. Capture the request scope: as-of date(s), agent population (all / regulated-zone only / specific business unit / specific agents), metadata fields requested, retention horizon.
3. Identify the closest snapshot in the consolidated inventory history table (Pillar 5 WORM lineage) for each as-of date.

**Investigation / preparation.**

- Validate the snapshot's chain of custody: source-snapshot timestamps, SHA-256 manifest, operator context (E-13), module / SDK / API version (E-14).
- Re-execute the inventory build on the as-of date if necessary using the documented rebuild procedure; produce a fresh manifest.
- For each requested metadata field, confirm the field's definition, taxonomy version at the as-of date, and known data-quality caveats.

**Production.**

- Produce the response in WORM-acceptable formats (typically PDF or CSV with SHA-256 manifest).
- Include a methodology cover note: which sources were joined, on what keys, with what latency-windows, and with what known caveats (PPAC ~15 min, Purview ~60–90 min, `Get-AdminPowerApp` canvas-only return, `Get-AdminPowerAppEnvironmentRoleAssignment` empty-no-error return on Dataverse-backed environments).
- Land the response in WORM with retention hold for the longer of 7 years, the WSP, or the rule-specific record-class retention.

**Recovery.**

- Decommission any temporary access granted for the audit pull.
- Hot-wash the audit-pull experience with Legal + Compliance + Internal Audit; capture process improvements.

**Lessons learned.** Update the documented audit-pull SLA; identify any field for which response was delayed and remediate via Pillar 5 / Pillar 6 improvements.

**Reporting decision tree.** N/A — the audit pull **is** the regulatory interaction. Internal escalation per the ladder ensures appropriate executive awareness.

---

## §4 — Reportability Per-Rule Reference

This section restates and expands the §1.2 reportability tree with rule-specific detail. **Compliance / Legal owns the final notification call.** This reference is a triage aid.

### §4.1 FINRA Rule 3110 — Supervision

Loss of supervisory visibility into an agent that produces or assists with communications, advice, recommendations, or trading is presumptively in scope. The "blind window" (start time → end time) must be documented with UTC precision. Manual supervision compensating procedures must be initiated for the duration of the blind window. Document principal review of any communications / recommendations issued during the window. Retention floor: WSP retention for supervisory records, typically the longer of 3 years or 6 years per record class.

### §4.2 FINRA Rule 4511 / SEC Rule 17a-4(b)(4) and 17a-4(f) — Books and Records

Inventory metadata, agent configuration, prompts, outputs, and audit trails are records when they relate to the firm's business. Loss, alteration, deletion, or non-WORM storage is presumptively a 4511 / 17a-4 issue. 17a-4(f) WORM media requirements apply to the storage of these records. Reconciliation against backups and the WORM-backed history table (Pillar 5) is the first-line response. Notification to FINRA via the firm's supervisory chain may be required if material records are unrecoverable.

### §4.3 FINRA Rule 4530 — Insider / Reportable Events

If an inventory anomaly is correlated with insider misconduct (intentional concealment, attempts to evade supervision, unauthorized agent creation by a registered representative), 4530(a) / (b) / (d) reporting paths may be triggered. Engage HR and Legal under privilege immediately.

### §4.4 FINRA RN 24-09 / Rule 3110 — AI-Specific Obligations

Existing supervisory and recordkeeping obligations apply to AI tools used in member-firm capacity. AI-specific considerations include: model versioning, prompt versioning, output traceability, third-party model dependencies. An inventory gap on an AI tool is a control gap on these obligations.

### §4.5 SEC Reg S-P §248.30(a)(3) — Customer NPI Incident Response

If an inventory gap permitted unauthorized access to or disclosure of customer non-public personal information (NPI), Reg S-P incident-response procedures (assessment, containment, customer notification) are triggered. Privacy Officer + General Counsel own the determination.

### §4.6 SEC Form 8-K Item 1.05 — Material Cybersecurity Incident

Public-registrant firms must disclose material cybersecurity incidents on Form 8-K within 4 business days of materiality determination. The materiality clock starts upon **determination**, not upon **discovery**, but firms must determine without unreasonable delay. The Disclosure Committee owns materiality.

### §4.7 NYDFS 23 NYCRR §500.17(a) — Cybersecurity Event Notification

Covered entities must notify the Department of Financial Services within 72 hours of determining that a cybersecurity event has occurred that meets the §500.17(a)(1) or (2) criteria. The 72-hour clock starts upon **determination**. The CISO + General Counsel own the determination.

### §4.8 OCC Bulletin 2026-13 / Federal Reserve SR 26-2 — Model Risk Management

For agents that meet the firm's "model" definition (decisioning, valuation, risk scoring, surveillance), inventory gaps impair model-risk controls (model inventory, performance monitoring, change control, validation evidence). MRM raises a finding and tracks remediation. The Chief Risk Officer + Model Risk Manager own the response.

### §4.9 GLBA / FTC Safeguards Rule (16 CFR §314)

Inventory gaps that impair safeguarding of customer information are Safeguards Rule control failures. The firm's Information Security Program (qualified individual) owns documentation and remediation.

### §4.10 CFTC Rule 1.31 / NFA Recordkeeping

For CFTC-registered entities (swap dealers, FCMs, IBs, CPOs, CTAs), inventory gaps affecting records under CFTC Part 1, Part 23, or NFA rules trigger CFTC-aligned preservation and potential notification. Compliance for the CFTC-registered entity owns the response.

### §4.11 State Privacy Laws (CCPA/CPRA, others)

Customer-data exposure from inventory gaps may trigger state-level breach notification obligations (varying definitions and clocks). Privacy Officer owns the multi-state assessment.

---

## §5 — Evidence Preservation

### §5.1 Capture Order

1. **Volatile UI surfaces first** (E-01 surface screenshots) — these change as caches refresh and as remediation occurs.
2. **Durable APIs second** (E-02 PPAC + Dataverse `bot`, E-03 Graph, E-04 register, E-09 sensitivity-label state, E-10 Entra owner state).
3. **Audit and posture last** (E-05 Purview audit log — wait for surfacing latency before closing the search; E-06 DSPM Activity Explorer; E-07 DLP inventory; E-08 retention inventory; E-11 PIM; E-12 sign-in / Defender for Cloud Apps).
4. **Operator context** (E-13 manifest) and **module/SDK/API version** (E-14) captured at the **start** of the response and updated if the operator or modules change mid-response.
5. **Integrity** (E-15 SHA-256 manifest) generated **last**, signed, and landed in WORM.

### §5.2 Storage and Retention

- Land all evidence in WORM-compliant storage (Microsoft Purview Records Management, immutable storage container, or equivalent).
- Apply a retention label aligned to the longer of: 7 years, WSP retention, the rule-specific record-class retention (FINRA 4511 / SEC 17a-4 / NFA / state).
- Apply a litigation hold if any aspect of the incident triggers a hold (Q3, Q5, Q6, Q7).
- Maintain a versioned chain of custody: who captured, when (UTC), with what tooling (E-14), in what cloud (E-13).

### §5.3 Reproducibility

Examiner-grade evidence requires that the response be **reproducible** years later by a different operator. The E-13 + E-14 + E-15 triad is the minimum reproducibility set. Where a query relied on a preview API, the API version must be recorded; where a query relied on a specific endpoint, the endpoint must be recorded.

### §5.4 Integrity Validation

The SHA-256 manifest (E-15) must be re-validated at retrieval time. Any mismatch is itself a reportable event (records integrity, FINRA 4511 / SEC 17a-4(f)).

---

## §6 — Communication and Escalation

### §6.1 Internal Communication

Use the L1–L5 ladder (§1.6). Each communication includes:

- Incident ID, severity, current status.
- Affected agent population (count, zones, business units).
- Reportability tree status (Q1–Q10 answers as of the message time).
- Compensating controls in effect.
- Next checkpoint time.
- Owner and bridge.

L4 / L5 communications are drafted with privilege markings and routed through Legal.

### §6.2 External Communication

External communication (regulators, customers, vendors) is owned exclusively by Legal + Compliance. The technical team supports by producing accurate, timestamped facts and evidence references; the technical team does **not** initiate external communication.

### §6.3 Microsoft Support Engagement

For incidents involving Microsoft 365, Power Platform, or Microsoft Graph service-side issues:

- Open a Premier / Unified support ticket with severity matching the firm's internal severity.
- Include in the support ticket: tenant ID, affected environments, time window, Purview audit operations of interest, Graph endpoints called, error codes / correlation IDs, module / SDK / API versions (E-14).
- Do **not** send customer NPI or examination-sensitive information to Microsoft Support without Legal approval.

### §6.4 Regulator Communication

- All regulator communication is routed through Legal + Compliance.
- The technical team produces evidence packages on request, in WORM-acceptable formats with SHA-256 manifests and methodology cover notes.
- Document every regulator-facing artifact with operator UPN, UTC capture time, and chain-of-custody references.

---

## §7 — Recovery Procedures

### §7.1 Verification of Inventory Parity

After remediation, verify parity across the four canonical sources within the documented latency windows:

1. Hub agent list (after PPAC propagation, ≥15 min).
2. PPAC Copilot agents view + Dataverse `bot` (DQ-1) (within propagation window).
3. Microsoft Graph (DQ-2) (within propagation window).
4. Governance register (after enrichment job completes).

Parity is measured on stable join keys (`botid`, Graph `id`), **not** `displayName`. Capture parity status in the consolidated inventory history table (Pillar 5).

### §7.2 Daily Re-Baselining

For 7 days after a SEV-1 or SEV-2 incident, run the consolidated inventory build at **daily** cadence (instead of steady-state) and produce a delta report. Any drift is investigated immediately rather than queued.

### §7.3 Monitoring Strengthening

Add or tighten Sentinel detections (Control 3.9) for the specific failure pattern observed:

- For Runbook 1: net-new agent in usage logs without inventory entry.
- For Runbook 2: orphaned agent detection at >25 / >50 thresholds.
- For Runbook 3: lifecycle state regressions; mass-rename events; deletion without change-control reference.
- For Runbook 4: Z1 agent producing high-volume customer-domain interactions.
- For Runbook 5: Z3 agent not in expected DLP scope.
- For Runbook 6: Z3 agent producing unlabeled outputs.
- For Runbook 7: register `Active` without Dataverse `bot`.
- For Runbook 8: cross-cloud reference patterns.

### §7.4 Closing the Incident

The incident closes when:

- All parity checks pass for 7 consecutive days.
- The reportability tree (§1.2) is closed by Compliance / Legal with documented determinations.
- The evidence package is landed in WORM with SHA-256 manifest validated.
- The Post-Incident Review (§8) is scheduled or completed.
- All compensating controls are either lifted (with documented sign-off) or promoted to permanent controls.

---

## §8 — Post-Incident Review (PIR)

### §8.1 Scope and Cadence

PIR is mandatory for every SEV-1 and SEV-2 inventory incident, and convened within 5 business days of incident closure. Attendees include: AI Governance Lead, Power Platform Admin, Purview Compliance Admin, Compliance Operations, Information Security, Internal Audit (observer), and the affected business-unit governance partner. Legal attends if any reportability tree question fired "Yes".

### §8.2 PIR Agenda

1. Timeline walkthrough (T+0 → closure), with evidence references.
2. Reportability tree (§1.2) walk with determinations and Compliance / Legal sign-off.
3. Root-cause analysis (per Pillar that owned the failure surface).
4. Compensating controls applied; promoted to permanent or lifted.
5. Sentinel detection / monitoring strengthening (§7.3).
6. WSP / runbook / playbook updates.
7. Action items with owners and due dates.

### §8.3 Outputs

- PIR memorandum landed in WORM with the incident evidence package.
- Action-item ledger entries in the AI Governance backlog (linked to controls 3.1, 3.6, 3.8, 3.9, 3.11, 3.12, 3.13).
- Updates to this troubleshooting playbook where the incident exposed a gap.

### §8.4 Lessons-Learned Feedback

Lessons feed:

- Pillar 5 (reconciliation) and Pillar 6 (enrichment) controls.
- Verification & testing scenarios (`verification-testing.md`).
- The companion control's verification criteria.
- Sentinel detections (Control 3.9).
- Onboarding / offboarding (JML) procedures (Runbook 2).

---

## §9 — Anti-Patterns

The behaviors below are repeated failure modes observed in FSI Copilot inventory operations. Any of them, if observed in your incident response, is itself a finding.

| # | Anti-pattern | Why it fails | Correct pattern |
|---|---|---|---|
| 1 | Treating `Get-AdminPowerApp` empty result as "no agents" | The cmdlet returns canvas Power Apps, not Copilot Studio bots | Query Dataverse `bot` table directly (DQ-1) |
| 2 | Treating `Get-AdminPowerAppEnvironmentRoleAssignment` empty result as "no role assignments" | Returns empty with no error on Dataverse-backed environments | Use Dataverse Web API or `pac admin list-app-users` |
| 3 | Joining inventory sources on `displayName` | `displayName` is mutable and non-unique across environments | Join on stable keys: Dataverse `botid`, Graph `id` |
| 4 | Treating sub-15-minute Hub / PPAC drift as a real incident | Documented steady-state propagation is ~15 min | Wait the documented latency window before declaring drift |
| 5 | Treating sub-90-minute Purview audit gap as a real incident | Audit surfacing latency is ~60–90 min | Wait the documented surfacing window before concluding |
| 6 | Single-page Graph enumeration treated as authoritative | Pagination missed | Always page through `@odata.nextLink` until null |
| 7 | Reverting a tampered record before evidence capture | Destroys evidence | Capture E-01–E-15 first; then remediate under Legal direction |
| 8 | Allowing manual register edits to bypass the lifecycle state machine | No change-control reference; opens audit findings | Reject writes without change-control reference at the register layer |
| 9 | Letting enrichment overwrite human-reviewed metadata fields | Loses high-confidence corrections to low-confidence automation | Respect a `lockedBy` attribute on enrichment writes |
| 10 | Using the Hub agent count as the system-of-record for examiner responses | Hub is a UI surface, not the system of record | Use the consolidated inventory derived from Dataverse + Graph + register |
| 11 | Sharing customer NPI or examination-sensitive data with Microsoft Support without Legal approval | Privacy / privilege exposure | Route Microsoft Support engagement through Legal-approved redaction |
| 12 | Closing an incident before the reportability tree is closed by Compliance / Legal | Risks missing a 4-business-day or 72-hour clock | Compliance / Legal sign-off is part of incident closure |
| 13 | Waiting 24–48 hours before triaging an inventory anomaly | The 72-hour NYDFS clock and 4-business-day SEC clock can elapse | Triage within the response clock for the rated severity |
| 14 | Treating Decommissioned as "we can stop preserving evidence" | Records retention obligations persist after decommission | Apply long-term retention label aligned to FINRA 4511 / SEC 17a-4(b)(4) |

---

## Cross-References

**Companion control.** [Control 3.1 — Agent Inventory and Metadata Management](../../../controls/pillar-3-reporting/3.1-agent-inventory-and-metadata-management.md)

**Sibling playbooks (Control 3.1).** [Portal Walkthrough](portal-walkthrough.md) · [PowerShell Setup](powershell-setup.md) · [Verification & Testing](verification-testing.md)

**Pillar 3 siblings.** [3.6 Orphaned Agent Detection](../../../controls/pillar-3-reporting/3.6-orphaned-agent-detection-and-remediation.md) · [3.8 Copilot Hub & Governance Dashboard](../../../controls/pillar-3-reporting/3.8-copilot-hub-and-governance-dashboard.md) · [3.9 Microsoft Sentinel Integration](../../../controls/pillar-3-reporting/3.9-microsoft-sentinel-integration.md) · [3.11 Centralized Agent Inventory Enforcement](../../../controls/pillar-3-reporting/3.11-centralized-agent-inventory-enforcement.md) · [3.12 Governance Exception & Override](../../../controls/pillar-3-reporting/3.12-agent-governance-exception-and-override-management.md) · [3.13 Agent 365 Admin Center Analytics](../../../controls/pillar-3-reporting/3.13-agent-365-admin-center-analytics.md) · [3.14 Agent 365 Observability SDK](../../../controls/pillar-3-reporting/3.14-agent-365-observability-sdk.md)

**Pillar 1 dependencies.** [1.6 Microsoft Purview DSPM for AI](../../../controls/pillar-1-security/1.6-microsoft-purview-dspm-for-ai.md) · [1.7 Comprehensive Audit Logging & Compliance](../../../controls/pillar-1-security/1.7-comprehensive-audit-logging-and-compliance.md)

**Related troubleshooting playbooks.** [1.6 Troubleshooting](../1.6/troubleshooting.md) · [2.5 Troubleshooting](../2.5/troubleshooting.md) · [4.7 Troubleshooting](../4.7/troubleshooting.md)

**Incident response framework.** [AI Incident Response Playbook](../../incident-and-risk/ai-incident-response-playbook.md) · [AI Risk Assessment Template](../../incident-and-risk/ai-risk-assessment-template.md) · [Remediation Tracking](../../incident-and-risk/remediation-tracking.md)

---

*Updated: May 2026 | Version: v1.6.2 | UI Verification Status: Current*
