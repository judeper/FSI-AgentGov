# Control 1.14 — Troubleshooting: Data Minimization and Agent Scope Control

**Control:** [1.14 Data Minimization and Agent Scope Control](../../../controls/pillar-1-security/1.14-data-minimization-and-agent-scope-control.md)
**Pillar:** 1 — Security
**Last UI Verified:** May 2026

> **READ §1 FIRST** if you are responding to a live event. Do **not** mutate configuration before evidence capture (§1.3). Re-scoping a knowledge source, removing a connector, or rotating an agent credential will destroy the access-pattern record that regulators will request.

---

## §1 — FSI Incident Handling — READ FIRST

Control 1.14 sits directly on **GLBA 501(b)** customer-NPI minimization, **SEC Regulation S-P §248.30** safeguards and customer-notification, **FINRA Rules 3110 / 4511 / 4530** supervision and recordkeeping, **FINRA RN 24-09 / Rule 3110** (existing rules apply to AI), and **CCPA §1798.100** purpose-limitation. A scope-drift event in which a Zone 3 customer-facing agent grounds against an undeclared SharePoint site that contains customer NPI is a textbook trigger for the **NY DFS 23 NYCRR 500.17(a)** 72-hour determination clock and the **SEC Reg S-P §248.30(a)(4)** customer-notification analysis. Treat scope-control failures as incidents, not "just admin bugs."

> **Determination vs. detection.** The NY DFS 500.17(a) 72-hour clock starts at the firm's **determination** that a reportable cybersecurity event occurred — not at first alert. Document the determination decision (who, when, on what evidence). That timestamp is the one regulators will examine.
>
> **FINRA Gen AI guidance reminder (RN 24-09, June 2024).** There is no separate "AI rule." Supervisory failures (Rule 3110), recordkeeping gaps (Rule 4511), and reportable events (Rule 4530) involving AI agents are evaluated under the *existing* rules; RN 24-09 applies these on a technology-neutral basis.

### §1.1 Incident severity matrix (Zone-aware)

| Severity | Zone 1 (Personal) | Zone 2 (Team) | Zone 3 (Enterprise / customer-facing / regulated) | Initial response |

| **SEV-1** | Tenant-wide scope-control failure across > 10 agents AND active over-broad access observed | Zone 2 customer-data agent with confirmed access to undeclared NPI source; over-privileged service account discovered with tenant-wide Graph application permissions | **ANY** confirmed surfacing of customer NPI via Copilot/agent due to over-broad scope; **ANY** scope-drift on a customer-facing agent grounding against an undeclared site containing regulated data; loss of scope-drift telemetry across Zone 3 agents; cross-tenant or guest agent observed accessing Zone 3 grounding sources | Page L3 within 30 min; CISO + Compliance + Legal + Privacy joined within 60 min |
| **SEV-2** | Single-agent scope drift with sensitive (non-NPI) data; file/image upload bypassing zone policy on Zone 1 agent | Quarterly access review > 30 days overdue on a Zone 2 agent; DLP-for-Copilot rule not blocking labeled content; connector classification drift; scope-expansion approved without documented justification; DSPM for AI not surfacing agent activity | Any Zone-2 condition occurring on a Zone 3 agent; UAL `AppPermissionGranted` event on Zone 3 agent identity with no change-management ticket; public web grounding still active on a Zone 3 NPI agent; DLP-for-Copilot rule observed in TestWithNotifications when policy of record is Block | L1 within 1 h; L2 paged; AI Governance Lead notified within 2 h |
| **SEV-3** | Configuration drift detected by automated check (scope-drift monitor); knowledge source still scoped to entire site rather than folder/library | Single agent missing data-access justification; OAuth scope wider than declared; quarterly-review backlog growing; Entra ID Governance Access Review not generated for a non-customer-facing agent | Drift on a Zone 3 agent corrected within SLA without NPI exposure; documented and reviewed at next governance cadence | L1 same business day |
| **SEV-4** | Documentation / UI mismatch; cosmetic | Cosmetic | Cosmetic | Backlog |

> **Severity-escalation rule.** If during triage you uncover **either** (a) evidence that customer NPI was processed by an agent during the drift window, **or** (b) a books-and-records gap (UAL events for `AppPermissionGranted`, `SharePointFileOperation`, or `CopilotInteraction` missing for the period) on a Zone 2/3 surface — escalate one severity level immediately and re-page accordingly.

### §1.2 Reportability decision tree (walk top-down; first YES controls)

> Reportability is a Compliance and Legal determination. Use this tree to escalate, not to decide.

1. **NPI / Reg S-P trigger — was customer NPI accessed, viewed, or transmitted by an unauthorized party (or a party not authorized for that scope) as a result of over-broad scope?**
   - **YES →** SEC Regulation S-P §248.30(a)(4) customer-notification analysis begins. Engage Legal within 4 h. Affected-customer notification window under the May 2024 amendments runs from determination (currently codified as as soon as practicable, but no later than 30 days). NY DFS 23 NYCRR 500.17(a) 72-hour notification clock starts at *determination* for Part-500-covered entities. GLBA 501(b) safeguards review triggered. State-AG notice (e.g., NY GBL §899-aa, MA 201 CMR 17.00, CA Civil Code §1798.82) may also apply — Privacy + Legal own the determination. Document the determination decision (who, when, evidence).
   - **NO →** continue.
2. **FINRA 4530 reportable — is this a "specified event" under FINRA Rule 4530(b) (customer harm, regulatory violation, or litigation)? Examples: customer complaint involving compensatory damages ≥ $15,000 caused by AI-surfaced data; internal review concluding a registered person violated a rule; written customer complaint of theft, misappropriation, or forgery related to AI output.**
   - **YES →** FINRA Rule 4530(b) written report due within 30 calendar days of firm conclusion. CCO drafts; Legal reviews. Pair with FINRA RN 24-09 / Rule 3110: AI-mediated misconduct is evaluated under existing 3110/4530, not a separate AI rule.
   - **NO →** continue.
3. **SEC 17a-4 books-and-records implication — is there a recordkeeping gap that prevents reconstruction of an agent's data-access decision subject to FINRA Rule 4511 or SEC Rule 17a-3 / 17a-4?**
   - **YES →** Supervision deficiency under FINRA Rule 3110; recordkeeping gap under SEC 17a-4(f). **Preserve all evidence on WORM** (Purview retention labels with Regulatory Record disposition + immutable Azure Storage with legal hold). Document gap, corrective action, and supervisory review in WSPs. **Do not** rely on Power Platform admin telemetry as the books-and-records source — it is operational, not WORM (Controls 1.7, 1.9, 1.19 cover the WORM side).
   - **NO →** continue.
4. **OCC Bulletin 2026-13 (formerly OCC 2011-12) / Fed SR 26-2 (formerly SR 11-7) model-risk impact — did the over-broad scope materially affect a credit, suitability, supervisory, fraud, or AML decision produced by the agent?**
   - **YES →** Model Risk Management committee notification required; document in model inventory; trigger out-of-cycle "effective challenge" review; assess re-validation need.
   - **NO →** continue.
5. **CFTC 1.31 record-keeping — does the firm conduct CFTC-regulated activity (swap dealer, FCM, IB, MSP) AND did the failure cause a recordkeeping gap on futures / swaps records?**
   - **YES →** CFTC Regulation 1.31 retention-gap analysis; pair with WORM evidence preservation per §1.3.
   - **NO →** continue.
6. **CCPA / state privacy notice — was California-resident or other state-covered consumer personal information (non-GLBA) collected or used beyond declared purpose?**
   - **YES →** Privacy team engaged for purpose-limitation analysis; update privacy notice / data inventory; consider CCPA §1798.100(c) "reasonably necessary" recordkeeping; evaluate state breach-notification statutes (CCPA §1798.82, CO Rev Stat §5-1-716, IL 815 ILCS 530, TX Bus. & Comm. Code §521.053, VA / VCDPA, CT CTDPA, WA MHMDA where applicable).
   - **NO →** Internal incident only. Document, remediate, review at next governance cadence.

### §1.3 Evidence preservation — capture **before** remediation (≥ 13 items)

Capture, do **not** mutate first. Every artifact below must carry an SHA-256 hash recorded in the manifest (§1.3 closing note). Preserve under **WORM** (see retention spec below).

1. **Agent-to-data-source inventory snapshot** at time of detection — CSV / JSON export of all agents and bound data sources from the scope-drift monitor (Control 1.2 registry join).
2. **Knowledge-source configuration snapshot** for the affected agent — Microsoft Copilot Studio admin API export OR screenshot of the `Knowledge` page showing scope (folder vs library vs site vs tenant-wide), public web grounding state, and file/image upload toggles.
3. **DLP policy snapshot** — `Get-DlpPolicy` (Power Platform DLP via PPAC) plus `Get-DlpCompliancePolicy` and `Get-DlpComplianceRule` (Purview, including DLP-for-M365-Copilot location). Record connector classifications, environment scope, rule mode (Block / TestWithNotifications / Off).
4. **SharePoint permissions snapshot** of the over-broadly-scoped site/library — `Get-SPOSiteGroup`, `Get-SPOUser`, the agent service account's effective permissions (Graph `/sites/{id}/permissions`), and Restricted Content Discovery / Restricted SharePoint Search status from SharePoint Advanced Management (Control 4.6).
5. **Connector OAuth scopes** for every connector bound to the agent — Entra App Registration → API Permissions; for Microsoft Graph, capture the delegated-vs-application split (Control 1.18 boundary).
6. **Service-account / agent-identity snapshot** — Entra user/SP object, group memberships, role assignments (PIM eligible + active), MFA state, last sign-in. Required for the over-privileged-service-account failure mode.
7. **UAL paged export** — `Search-UnifiedAuditLog -RecordType MicrosoftCopilot,SharePointFileOperation,AzureActiveDirectoryApplicationAudit -SessionId <guid> -SessionCommand ReturnLargeSet` for the failure window. Include `AppPermissionGranted`, `Add app role assignment grant to user`, `FileAccessed`, and `CopilotInteraction` rows. Record audit-search Job ID and total row count.
8. **Scope-drift alert payload** — Purview alert JSON, Sentinel incident export, or `scope-drift-monitor` solution run output. Do **not** "ack and clear" before capture.
9. **DSPM for AI Activity Explorer export** for the suspect window — paginated, no truncation. Include any sensitive-info matches surfaced for the affected agent.
10. **Quarterly access review records** for the affected agent — last completion date, reviewer of record, decision, justification on file. If overdue, record the overdue duration and the SoD posture (was the agent owner the only approver?).
11. **Customer-impact analysis** — count of records, sensitivity classification (per Control 1.13 SITs), customer residency, NPI / PII determination. Include sample of returned content (redacted) for the responsible Privacy Officer's review.
13. **Role-group snapshot** — current membership of Power Platform Admin, SharePoint Admin, Purview Compliance Admin, Entra Global Admin, Entra Privileged Role Admin, AI Governance Lead, environment Maker. Captures who could have approved or made the change.

> **SHA-256 manifest spec.** Maintain a single file `INC-<YYYY>-<MMDD>-<seq>/manifest.sha256` at the incident folder root. One line per artifact: `<sha256>  <relative/path/to/artifact>`. Sign the manifest (PGP detached signature `manifest.sha256.asc`, or store under WORM) by SOC lead within 4 h of evidence capture. Any evidence added later requires a new dated manifest line; never edit a prior line.
>
> **WORM retention requirement.** All §1.3 artifacts and the final incident report must be retained under **Purview retention labels** with disposition set to **Regulatory Record** (or organization equivalent) for the longer of: (a) 7 years (FINRA 4511 / SEC 17a-4(b) baseline), (b) the period required by the firm's WSPs, or (c) the period required by an active legal hold. Pair Purview retention with **immutable Azure Storage** (`Set-AzStorageContainerImmutabilityPolicy -Period <days>`) for off-platform copies. Operational telemetry alone (Power Platform admin logs, scope-drift monitor logs at default retention) does **not** satisfy 17a-4(f) — pair every 1.14 incident with the WORM-side evidence anchored in Controls 1.7, 1.9, and 1.19.

### §1.4 Compensating controls during remediation

| Failed surface | Compensating control | Time to deploy |

| Knowledge-source over-broad and cannot be re-scoped immediately (active flows depend on it) | **Quarantine the agent** — set publication off in Copilot Studio until re-scope is complete. Do not "leave it running while we discuss." | 5 min (PPAC publication toggle) |
| DLP connector classification correct but not yet propagated (15-min Power Platform DLP propagation window) | Apply tenant-wide **Block at SharePoint sharing layer** for the affected library; raise Communication Compliance review cadence (Control 1.10) on the agent's interactions | 15 min |
| DLP-for-Copilot rule not enforcing (still in TestWithNotifications) | Switch the rule to **Block**; document the compensating-control change-ticket; notify affected Maker community via Teams broadcast | 30 min |
| Scope-drift monitor degraded or silent | Manual daily UAL search for `AppPermissionGranted` + `MicrosoftCopilot.*` events; freeze new Zone-3 agent publishes (Control 2.1); raise DSPM for AI review cadence (Control 1.6) | 1 h |
| Quarterly access review backlog | Activate **emergency review** with AI Governance Lead + an independent reviewer (NOT the agent owner — see SoD note) | 24 h |
| Over-privileged service account on agent identity | Rotate credential; remove offending role / API permission assignments; re-bind agent to a least-privilege identity (Control 1.18); document the gap window for books-and-records | 2 h |
| Audit gap for `AppPermissionGranted` / `CopilotInteraction` (Control 1.7 ingestion broken) | Pause Zone-3 agent activations; cross-reference SharePoint audit, Graph sign-in logs, and Entra audit as fallback evidence sources | 30 min |
| Public web grounding still active on Zone 3 NPI agent | Disable in Copilot Studio per-agent setting; if propagation lags, set Maker / environment policy to disable web grounding tenant-wide for Zone 3 environments | 15 min |
| File/image upload bypassing zone policy | Disable file/image upload on the agent; raise DLP-for-Copilot rule severity to Block; restrict by sensitivity label and SIT (Controls 1.13, 1.17) | 30 min |

> **Segregation of duties (SoD) — critical.** The agent owner / Maker MUST NOT be the sole approver for Zone 3 scope expansion or quarterly access review sign-off. This is a structural SoD violation under FINRA 3110 supervision principles and the OCC Bulletin 2026-13 (formerly OCC 2011-12) / Fed SR 26-2 (formerly SR 11-7) "effective challenge" requirement. Required reviewer set: AI Governance Lead **plus** a business-line compliance officer (Zone 3) or manager (Zone 2). If your current review process allows owner-only sign-off, treat that as a control deficiency and document compensating review in the incident record.

### §1.5 Pre-escalation checklist (≥ 16 items)

- [ ] §1.1 severity assigned (and re-evaluated against the NPI / books-and-records escalation rule)
- [ ] §1.2 reportability tree walked top-down; first YES recorded with timestamp + decision-maker name
- [ ] §1.3 items 1–13 captured to incident folder; SHA-256 manifest signed
- [ ] **Tenant ID** recorded
- [ ] **Knowledge-source scope** captured (folder / library / site / tenant-wide)
- [ ] **DLP policy state** captured for both Power Platform DLP and Purview DLP-for-Copilot; environment in scope confirmed; rule mode recorded
- [ ] **Public web grounding** state captured (per-agent toggle + environment-level policy)
- [ ] **File / image upload** state captured (per-agent toggle + DLP rule conditions)
- [ ] **Service-account permissions** enumerated (delegated vs application; PIM active vs eligible; tenant-wide app roles)
- [ ] **UAL paged export** completed with `-SessionId` + `-SessionCommand ReturnLargeSet`; `AppPermissionGranted`, `MicrosoftCopilot.*`, and `SharePointFileOperation` rows included; row count and Job ID recorded
- [ ] **DSPM for AI Activity Explorer** queried with deterministic filter; result count recorded
- [ ] **Quarterly access review status** captured; overdue duration and SoD posture recorded
- [ ] **Scope-drift alert payload** preserved (do not "ack and clear" before capture)
- [ ] **Customer-impact analysis** completed (count, residency, NPI determination)
- [ ] **Compensating control** deployed if remediation > SLA (§1.4)
- [ ] **SoD verified** — reviewer set excludes agent owner for Zone 3
- [ ] **Cross-references triggered** — Controls 1.2, 1.4, 1.10, 1.13, 1.17, 1.18, 1.19, 4.6 owners notified as applicable
- [ ] **Communication tree activated** (§1.6) — CISO, AI Governance Lead, Compliance Officer, Legal, Privacy Officer notified per severity matrix; Microsoft Premier Support engaged if §4 L4 criteria met
- [ ] **Communications draft** prepared if reportability tree returned YES at any step

### §1.6 Communication tree

| Severity / trigger | Notify | Channel | Within |

| SEV-1; or §1.2 step 1 (NPI / Reg S-P) YES | **CISO**, **Compliance Officer**, **Legal**, **Privacy Officer**, **AI Governance Lead** | Phone bridge + secure email; create incident war-room channel | 60 min of detection |
| SEV-1; cross-tenant / guest access; or known platform fault | **Microsoft Premier / Unified Support** (case open, severity A) with §5 evidence pack | Premier portal | 4 h of triage |
| SEV-1; §1.2 step 4 (model-risk) YES | **Model Risk Management Committee chair** | Secure email + governance ticket | 24 h of determination |
| SEV-1 with NY DFS-covered entity scope | **Board / Senior Governing Body designee** per 23 NYCRR 500.17(b) annual reporting framework; **NY DFS** notification within 72 h of determination | DFS portal | 72 h of determination |
| SEV-2 | **AI Governance Lead**, **Compliance Officer**, **Power Platform Admin lead** | Secure email | 4 h |
| §1.2 step 2 (FINRA 4530) YES | **CCO**, **Legal** | Secure email | 24 h of conclusion; written report 30 days |
| §1.2 step 3 (17a-4) YES | **CCO**, **Records Officer**, **Legal** | Secure email | 24 h |
| §1.2 step 6 (CCPA / state privacy) YES | **Privacy Officer**, **Legal**, **Marketing/HR data owner** as applicable | Secure email | 24 h |

### §1.7 Worked example — Customer NPI surfaced via Copilot due to over-broad knowledge-source scope

**Scenario.** Scope-drift monitor alerts at 14:08 that a Zone 3 customer-service agent has been grounding against `https://contoso.sharepoint.com/sites/Wealth-Operations` — an undeclared site that contains a customer-account spreadsheet with NPI. End-user reports that Copilot returned a customer's account number and SSN-last-4 in a chat response.

**Step 1 — severity (§1.1).** Zone 3 + customer NPI surfaced + customer-facing → **SEV-1**. Page L3 within 30 min. SOC + Compliance + Legal + Privacy joined at 14:38.

**Step 2 — reportability (§1.2).** Step 1 = YES (customer NPI disclosed to a party outside their authorized scope). Engage SEC Reg S-P §248.30(a)(4) customer-notification analysis; start NY DFS 500.17(a) determination clock; trigger GLBA 501(b) safeguards review. Decision recorded: Compliance Officer, 15:02, signed.

**Step 3 — evidence (§1.3).** Capture items 1–13 to `INC-2026-0418-0007/`. Critical: snapshot the SharePoint library permissions, the agent's knowledge-source config, the public-web-grounding toggle, and the UAL `AppPermissionGranted` + `SharePointFileOperation` + `CopilotInteraction` rows for the prior 90 days **before** changing the scope. SHA-256 manifest signed by SOC lead at 15:31. Purview retention label (`Regulatory Record`, 7 y) applied to the incident folder; immutable storage container created.

**Step 4 — compensating control (§1.4).** Quarantine the agent (publication off) at 14:46. Raise Communication Compliance cadence on the affected reviewer pool (Control 1.10). Do **not** delete the agent or the SharePoint library — preserve.

**Step 5 — root cause.** Knowledge source was scoped to the entire site at agent creation (Maker chose "all of organization" default in Copilot Studio); quarterly access review was overdue by 47 days; agent owner was the only approver on file. Three failure modes intersect: §2.2 (entire-site scope), §2.7 (scope-drift detector silent), and the §1.4 SoD note (owner-only approval).

**Step 6 — remediation.** Re-scope knowledge source to the specific approved folder (Control 4.6 Restricted Content Discovery exclusion); add the under-scoped library to the Connector DLP block list (Control 1.4); deploy a SIT-based DLP-for-Copilot rule to detect customer-account-number patterns (Controls 1.13, 1.5); rotate the agent owner's environment-Maker assignment; require an independent reviewer for the next quarterly review.

**Step 7 — regulator notifications.** SEC Reg S-P §248.30(a)(4) customer-notification draft prepared by Privacy + Legal; NY DFS 500.17 72 h clock measured from determination at 15:02 → DFS notification due by 15:02 on day-3. FINRA 4530(b) evaluation: not yet a "specified event" but flagged for re-evaluation if a customer complaint files.

**Step 8 — governance.** Logged in monthly AI governance review; policy change: tenant-wide ban on "all of organization" knowledge-source scope at agent creation in Zone 2/3 environments (Maker policy + DLP-for-Copilot rule); add scope to the standard quarterly review template; require SoD reviewer for all Zone 3 reviews. Lessons learned captured per §7.

**Total time from alert to remediation deployed:** 6 h 18 min. Determination per NY DFS 500.17(a) recorded at 15:02 — clock running.

---

## §2 — Failure-mode runbooks

Each runbook follows: **Symptoms / Root cause / Diagnostic queries / Remediation / Validation / Evidence**.

### §2.1 Power Platform DLP policy not enforced on agent

**Symptoms.** A connector classified as Blocked (or in the Non-Business group while the agent uses only Business connectors) is observed bound to the agent and operating successfully. Maker can still add the connector. Audit shows no DLP block event.

**Root cause.** Most common: the policy's **environment scope** does not include the environment hosting the agent. Less common: policy created at "All environments" but with an explicit exclusion; policy in `Pending` status (15-minute propagation not yet complete); the connector is classified per-environment differently than at tenant; the Maker has the **Environment Admin** role and used a connector exception; or the connector is a **custom connector** not yet classified (custom connectors default to Non-Business unless classified).

**Diagnostic queries.**

```powershell
# Power Platform DLP — verify environment scope
Connect-PowerAppsAccount
Get-DlpPolicy | Where-Object { $_.displayName -eq '<PolicyName>' } |
  Select-Object displayName, environmentType, environments,
    @{n='BusinessCount';e={$_.connectorGroups.Where({$_.classification -eq 'Confidential'}).connectors.Count}},
    @{n='NonBusinessCount';e={$_.connectorGroups.Where({$_.classification -eq 'General'}).connectors.Count}},
    @{n='BlockedCount';e={$_.connectorGroups.Where({$_.classification -eq 'Blocked'}).connectors.Count}}

# Confirm the agent's environment is bound
$envId = (Get-AdminPowerAppEnvironment | Where-Object DisplayName -eq '<EnvDisplayName>').EnvironmentName
Get-DlpPolicy | ForEach-Object {
  [pscustomobject]@{ Policy = $_.displayName; Includes = $_.environments.name -contains $envId }
}
```

```kusto
// Audit (CloudAppEvents / Microsoft 365 audit) — observe connector usage despite Block
CloudAppEvents
| where Timestamp > ago(24h)
| where ActionType in ("PowerPlatformConnectorAdded","PowerPlatformConnectionCreated")
| where AccountObjectId == "<MakerObjectId>"
| project Timestamp, ActionType, ObjectName, RawEventData
```

**Remediation.** Add the missing environment to the policy; if the connector is custom, classify it explicitly. Wait the documented Power Platform DLP propagation window before re-testing; do not assume immediate enforcement. If the Maker exploited an Environment-Admin path, raise the role assignment to PIM-eligible only (Control 1.18) and re-evaluate Maker policy.

**Validation.** Repeat the diagnostic query; expect environment now in `environments` list. Reproduce the Maker action; expect Block event in the Power Platform admin activity log and corresponding Purview audit `DlpRuleMatch` row (where DLP-for-Copilot rule is paired).

**Evidence.** §1.3 items 3, 5, 7, 13. Add the policy diff (before / after) to the incident folder.

### §2.2 Knowledge source scoped too broadly (entire site vs library / folder)

**Symptoms.** Copilot Studio agent's `Knowledge` page shows a SharePoint source as `https://contoso.sharepoint.com/sites/<Name>` (site root) rather than `/sites/<Name>/<Library>/<Folder>`. Agent retrieves content from libraries the Maker did not declare. SIT scan (Control 1.13) of agent transcripts finds matches outside the declared scope.

**Root cause.** Maker selected the site URL rather than drilling to a library / folder. Copilot Studio currently uses **library / folder** as the floor for SharePoint sources — there is no public file-level scope. "All of organization" is the default option in some Copilot Studio templates and is a known anti-pattern for Zone 2/3.

**Diagnostic queries.**

```powershell
# Inspect knowledge sources via the Copilot Studio admin surface (preview at time of writing)
# Confirm the agent's knowledge config
Connect-MgGraph -Scopes "AppCatalog.Read.All","Sites.Read.All"
# Use the supported Copilot Studio admin export from PPAC > Copilot Studio Agents > Export
# Inspect the JSON for knowledgeSources[*].sharePoint.url
```

```kusto
// SharePoint audit — files accessed by the agent service principal beyond declared library
SharePointFileOperation
| where Timestamp > ago(7d)
| where UserId == "<AgentServicePrincipalUPN>"
| where ObjectId !startswith "https://contoso.sharepoint.com/sites/<Name>/<DeclaredLibrary>/"
| summarize Count = count(), distinct_paths = make_set(ObjectId, 100) by bin(Timestamp, 1h)
```

**Remediation.** Re-scope the knowledge source to the declared library or folder (capture evidence first per §1.3). If the library cannot be sub-scoped to a folder due to content layout, **restructure the library** rather than leaving the source site-wide and "trusting DLP." Apply Restricted Content Discovery (RCD) on the parent site per Control 4.6. Update Maker policy (PPAC environment policy) to disallow site-root selection for Zone 2/3 environments.

**Validation.** Repeat the diagnostic; expect zero out-of-scope file access events. Run the verification-testing harness (`verification-testing.md` §scope-drift) to confirm.

**Evidence.** §1.3 items 1, 2, 4, 7. Capture the Copilot Studio knowledge JSON before and after.

### §2.3 Public web grounding still active on Zone 3 NPI agent

**Symptoms.** Zone 3 agent's response includes content with `[Web]` citations or Bing-sourced URLs. Per-agent public-web-grounding toggle in Copilot Studio is observed `On` despite Zone 3 policy of `Off`.

**Root cause.** Maker enabled web grounding at agent creation; environment-level policy does not yet enforce the toggle off; or the toggle was inherited from a parent template. Public web grounding is **not** an audit-visible control change in all clouds — silent regressions are possible.

**Diagnostic queries.**

```powershell
# Read agent settings via supported Copilot Studio admin export
# Look for "publicWebGrounding": true in the agent JSON
$agentJson = Get-Content '<exported-agent>.json' | ConvertFrom-Json
$agentJson | Select-Object name, @{n='WebGrounding';e={$_.settings.publicWebGrounding}},
  @{n='FileUpload';e={$_.settings.allowFileUpload}}, @{n='ImageUpload';e={$_.settings.allowImageUpload}}
```

**Remediation.** Disable public web grounding on the agent. Update environment-level Maker policy to disallow web grounding for Zone 3. Where the cloud surface does not expose the toggle, document the compensating control (DLP-for-Copilot rule scoped to block all web grounding for the agent service principal).

**Validation.** Re-export the agent JSON; expect `publicWebGrounding: false`. Issue a test prompt requesting current events; expect the agent to refuse or to ground only on declared sources.

**Evidence.** §1.3 items 2, 9. Add a redacted prompt/response capture if a web citation was observed.

### §2.4 File / image upload bypassing zone policy

**Symptoms.** Users upload files (PDFs, spreadsheets, images) to a Zone 2/3 agent that is governed to accept only declared sources. SIT scan flags an uploaded file as carrying NPI; no DLP-for-Copilot Block fires.

**Root cause.** Per-agent file/image upload toggle left `On`; DLP-for-Copilot rule conditions do not include the upload surface; rule operating in TestWithNotifications; or the file format is outside the SIT scanner's supported set (e.g., scanned PDFs without OCR).

**Diagnostic queries.**

```powershell
# Purview DLP — inspect DLP-for-Copilot rule conditions and mode
Connect-IPPSSession
Get-DlpCompliancePolicy | Where-Object { $_.Mode -ne 'Enable' -and $_.CopilotInteractionLocation -eq $true } |
  Select-Object Name, Mode, Enabled, CopilotInteractionLocation
Get-DlpComplianceRule | Where-Object { $_.ParentPolicyName -eq '<PolicyName>' } |
  Select-Object Name, Mode, BlockAccess, NotifyUser, ContentContainsSensitiveInformation
```

**Remediation.** Disable upload at the per-agent setting where Zone policy requires; switch the DLP-for-Copilot rule to `Block`; expand SIT coverage (Control 1.13) to include the unsupported format via OCR-enabled SITs or pre-upload Purview scan. Update Maker policy to disallow upload on new Zone 2/3 agents.

**Validation.** Attempt an upload of a file matching a SIT; expect Block + DSPM activity row + audit `DlpRuleMatch`.

**Evidence.** §1.3 items 2, 3, 7, 9.

### §2.5 Purview DSPM for AI not surfacing agent activity

**Symptoms.** DSPM for AI Activity Explorer shows zero rows for the affected agent over the suspect window despite known prompt activity. One-click policy templates show "Recommendation Not Updating."

**Root cause.** Most common: `UnifiedAuditLogIngestionEnabled = False` (must be checked from `Connect-ExchangeOnline`, not `Connect-IPPSSession` — wrong-shell trap). Less common: M365 Copilot license missing on the affected user; Restricted Administrative Unit admin running the query (DSPM does not currently support AU); content-capture not enabled on the collection policy; or Activity Explorer queried with the wrong RecordType filter.

**Diagnostic queries.**

```powershell
# Correct shell — EXO, not IPPS
Connect-ExchangeOnline
Get-AdminAuditLogConfig | Select-Object UnifiedAuditLogIngestionEnabled

# Verify Copilot license for the affected user
Connect-MgGraph -Scopes "User.Read.All"
Get-MgUserLicenseDetail -UserId '<affected-upn>' |
  Select-Object SkuPartNumber, ServicePlans
```

```powershell
# Mirror via Search-UnifiedAuditLog — paginated
$sid = [guid]::NewGuid().ToString()
$all = @()
do {
  $batch = Search-UnifiedAuditLog -StartDate (Get-Date).AddDays(-7) -EndDate (Get-Date) `
    -RecordType MicrosoftCopilot -ResultSize 5000 `
    -SessionId $sid -SessionCommand ReturnLargeSet
  $all += $batch
} while ($batch.Count -gt 0)
$all.Count
```

**Remediation.** Enable audit ingestion from the EXO session; assign the M365 Copilot license; remove the AU restriction or re-run from a tenant-scoped admin account; enable content-capture on the DSPM collection policy. Re-test after the documented propagation window.

**Validation.** Repeat the paged audit query; expect a non-zero deterministic row count for a known prompt.

**Evidence.** §1.3 items 7, 9. Record audit-search Job ID + total row count.

### §2.6 DLP-for-Copilot rule not blocking labeled content

**Symptoms.** Sensitivity-labeled (e.g., `Highly Confidential / Customer NPI`) content surfaces in agent responses. The DLP-for-Copilot rule of record claims to block on that label.

**Root cause.** Endpoint MIP client out of date on the user device; label not published to the affected user / group; auto-labeling scope excludes the file; container-label inheritance off; rule mixes a SIT condition and a label condition in the same rule (DLP-for-Copilot location historically requires separate rules per condition class — verify on current Learn); or rule mode is TestWithNotifications.

**Diagnostic queries.**

```powershell
Connect-IPPSSession
Get-Label | Where-Object DisplayName -eq '<LabelName>' |
  Select-Object Name, DisplayName, ContentType, IsValid, Disabled
Get-LabelPolicy |
  Select-Object Name, Labels, ScopedLabels,
    @{n='UsersIncluded';e={$_.ExchangeLocation, $_.ModernGroupLocation, $_.SharePointLocation}}

Get-DlpComplianceRule -Identity '<RuleName>' |
  Select-Object Name, Mode, BlockAccess, NotifyUser,
    ContentContainsSensitiveInformation, ContentContainsSensitivityLabel
```

**Remediation.** Update endpoint MIP client; publish the label to the affected user / group; enable container-label inheritance per Microsoft Learn (`sensitivity-labels-teams-groups-sites`); split combined SIT + label rules where the location requires it; switch rule from TestWithNotifications to Block. Pair with Control 1.5 (DLP for Microsoft 365 Copilot) and Control 1.13 (SITs) for end-to-end coverage.

**Validation.** Reproduce with a labeled test document; expect Block + audit `DlpRuleMatch` + DSPM Activity Explorer entry.

**Evidence.** §1.3 items 3, 9, 11.

### §2.7 Scope-drift detector silent (no baseline / record-type mismatch / missing -Endpoint)

**Symptoms.** The `scope-drift-monitor` solution (or equivalent SIEM correlation) returns zero alerts despite known scope changes. `Get-AgentRegistry` baseline appears empty; correlation rules in Sentinel show zero hits.

**Root cause.** Three common failure modes:
1. **Baseline never seeded** — the inventory snapshot from Control 1.2 was not loaded as the comparison baseline.
2. **Record-type mismatch** — the correlation queries `AIPDiscover` or another deprecated record type instead of `MicrosoftCopilot` and `SharePointFileOperation`. (FYI: there is **no native** `AgentScopeExpansion` audit event — the signal is derived.)
3. **Missing `-Endpoint`** on the Connect call — `Connect-PowerAppsAccount` was issued without `-Endpoint prod`, returning empty data silently.

**Diagnostic queries.**

```powershell
# Baseline check — Agent Registry export must exist and be current
$baseline = Import-Csv 'agent-registry-baseline.csv'
$baseline.Count

# Record-type sanity — are we querying a real schema?
Search-UnifiedAuditLog -StartDate (Get-Date).AddDays(-1) -EndDate (Get-Date) `
  -RecordType MicrosoftCopilot -ResultSize 10 | Measure-Object

# Commercial endpoint verification
$ctx = Get-PowerAppsAccount
$ctx | Select-Object Account, Environment, TenantId
```

**Remediation.** Seed the baseline from the latest Control 1.2 registry export; replace deprecated record types with `MicrosoftCopilot` + `SharePointFileOperation` + `AzureActiveDirectoryApplicationAudit`. Add a synthetic-test agent that performs a known scope expansion daily; alert if no detection within 24 h (silent-zero-row guard).

**Validation.** Trigger a controlled scope expansion (test agent + test library); expect alert within the documented detection window.

**Evidence.** §1.3 items 1, 8. Capture the `scope-drift-monitor` run log (JSON).

### §2.8 Entra ID Governance Access Review not generated

**Symptoms.** Quarterly access review for the agent identity (Entra Agent ID) or a connector connection is not present in My Access; reviewer never receives the email.

**Root cause.** Most common: the Entra ID Governance license (P2 or Governance SKU) is not assigned to the reviewer; the review's resource scope does not include the agent's app / group; the review schedule is set to "One time" rather than recurring; the reviewer is a guest and guest-reviewer support is not configured. Less common: the access-review policy is in `Pending` and never activated; admin who created it lacks `Identity Governance Administrator`.

**Diagnostic queries.**

```powershell
Connect-MgGraph -Scopes "AccessReview.ReadWrite.All","Group.Read.All"
Get-MgIdentityGovernanceAccessReviewDefinition |
  Select-Object Id, DisplayName, Status, CreatedDateTime,
    @{n='Recurrence';e={$_.Settings.RecurrenceSettings}},
    @{n='Reviewers';e={$_.Reviewers.Query}},
    @{n='Scope';e={$_.Scope.Query}}
```

**Remediation.** Assign Entra ID Governance license to reviewers; add the agent's app / Entra security group to the review scope; set recurrence to quarterly (or zone cadence); switch the reviewer to a tenant member or configure guest-reviewer support; activate `Pending` reviews. Where the cloud does not support the feature in full, use a manual quarterly review tracked in the AI governance backlog with the same SoD requirement.

**Validation.** Confirm review appears in My Access for the reviewer; confirm decision is logged on the agent.

**Evidence.** §1.3 items 6, 10, 13.

### §2.9 Cross-tenant or guest agent access unmanaged

**Symptoms.** Audit shows `AppPermissionGranted` for a service principal whose Entra app registration lives in a foreign tenant; or a B2B guest user is the agent owner / Maker; or Copilot is grounding against a SharePoint site shared with `Everyone Except External Users` that nonetheless surfaces guest-shared files.

**Root cause.** External Identities cross-tenant access settings allow inbound application access from the foreign tenant; B2B guest invitation policy allows guests as Makers in Zone 2/3 environments; SharePoint external sharing policy allows site-level guest access on a Zone 3 source.

**Diagnostic queries.**

```powershell
Connect-MgGraph -Scopes "Policy.Read.All","CrossTenantInformation.ReadBasic.All"
Get-MgPolicyCrossTenantAccessPolicyPartner |
  Select-Object TenantId,
    @{n='B2BInbound';e={$_.B2BCollaborationInbound.UsersAndGroups.AccessType}},
    @{n='B2BAppsInbound';e={$_.B2BCollaborationInbound.Applications.AccessType}}

# Find guest users that are environment Makers
Connect-PowerAppsAccount
Get-AdminPowerAppEnvironment | ForEach-Object {
  $envId = $_.EnvironmentName
  Get-AdminPowerAppEnvironmentRoleAssignment -EnvironmentName $envId |
    Where-Object { $_.PrincipalType -eq 'User' -and $_.PrincipalDisplayName -like '*#EXT#*' } |
    Select-Object @{n='Env';e={$envId}}, RoleName, PrincipalDisplayName
}
```

**Remediation.** Constrain cross-tenant access settings to the named partner tenants; deny inbound application access from unspecified tenants; remove guest users from Maker / Environment-Admin roles in Zone 2/3 environments (Control 1.18); restrict external sharing on Zone 3 SharePoint sources; coordinate with Control 4.6 to apply Restricted Content Discovery on guest-accessible sites.

**Validation.** Reproduce: foreign-tenant app cannot acquire token for the agent identity; guest user cannot create / publish an agent in Zone 2/3.

**Evidence.** §1.3 items 4, 5, 6, 13.

---

## §3 — Anti-patterns (do not do)

| # | Anti-pattern | How to detect | Correction |

| 1 | Approving scope expansion without documented justification (e.g., "per Slack thread") | Audit change-management tickets quarterly; sample 5% of Zone 3 scope changes; confirm justification field has substantive narrative tied to a business need | Reject; require the Maker to amend with named business owner + business need + data-classification statement; record FINRA 4511 anchor |
| 2 | Scoping knowledge source to entire SharePoint site (or "all of organization") instead of a specific folder / library | Inspect `knowledgeSources[*].sharePoint.url`; flag any URL ending at site root | Re-scope; tighten Maker policy to disallow site-root selection in Zone 2/3 |
| 3 | Ignoring or auto-acknowledging scope-drift alerts ("noisy") | Sentinel rule: count of alerts cleared within 60 s by the same operator; investigate top-quartile clearers | Require a change-ticket reference or a §1.2 reportability decision in every clear |
| 4 | Treating the agent owner / Maker as the sole approver for Zone 3 scope changes or quarterly reviews | Quarterly review export; flag agents where reviewer = owner | Add a required SoD reviewer (AI Governance Lead + business-line Compliance) before close-out |
| 5 | Mutating the configuration (re-scoping, removing connector, rotating credential) before capturing evidence | Compare incident timestamp series against §1.3 manifest timestamps | Halt; restore from snapshot if possible; capture before further mutation |
| 6 | Treating Power Platform admin activity logs / scope-drift monitor logs as books-and-records | Inventory the firm's WORM record list; absence of UAL / Purview retention pairing for AI activity flags this | Pair every 1.14 incident with Controls 1.7 + 1.9 + 1.19 WORM evidence |
| 7 | Configuring a DLP policy without including the environment in scope ("no environments" no-op) | `Get-DlpPolicy` and inspect `environments` list per policy | Add the environment; re-test |
| 8 | Granting Microsoft Graph application (vs delegated) permissions to an agent identity when delegated would suffice | `Get-MgServicePrincipalAppRoleAssignment` for the agent SP; flag tenant-wide app-role grants like `Sites.FullControl.All`, `Files.ReadWrite.All`, `Mail.Read` | Replace with `Sites.Selected` + per-site grant, or delegated scopes; rotate credential; document gap window |
| 9 | Running the audit query from `Connect-IPPSSession` instead of `Connect-ExchangeOnline` (wrong-shell trap) | Operator runbook review; CI lint on internal scripts | Re-run from the EXO session; mirror via DSPM Activity Explorer |
| 10 | `Search-UnifiedAuditLog` single-shot (no `-SessionId`) for a multi-day Copilot investigation | Inspect script for missing `-SessionId` / `-SessionCommand ReturnLargeSet` | Implement do-while pagination; cap 50,000 per session |
| 12 | Citing a quarterly review as "complete" against an inventory > 90 days stale | Compare review completion date to Control 1.2 registry export date | Re-run the review against a refreshed inventory; document the gap window |

---


## §4 — Escalation paths (L1 → L4)

| Level | Owner | Triggers | MTTR target | Required evidence at handoff | Transition to next level |

| **L1 — Help desk / Power Platform Admin** (with SharePoint Admin on watch) | Power Platform Admin lead | All SEV-3/4; initial triage of all SEV-1/2; first-touch on scope-drift alerts | 30 min SEV-1/2 acknowledge; 1 business hour SEV-3 | §1.5 pre-escalation checklist items 1–10; agent-to-data-source snapshot; UAL paged export started | §2 runbook exhausted with no fix; OR SEV-1/2 confirmed; OR books-and-records gap identified |
| **L2 — Power Platform / Purview operations** (AI Governance Lead + Purview Compliance Admin) | AI Governance Lead | All SEV-2; SEV-1 within 60 min; any incident where reportability tree §1.2 returns YES at step 2, 3, 4, 5, or 6 | 4 h SEV-2; 1 h SEV-1 | All §1.3 evidence items 1–13; §1.2 reportability decision recorded; customer-impact analysis | Customer NPI exposure suspected (§1.2 step 1 YES); OR SEV-1 confirmed; OR Microsoft platform-side fault suspected |
| **L3 — SME + Microsoft Support** (CISO + Compliance Officer + Legal + Privacy Officer; Microsoft case open) | CISO | SEV-1; any §1.2 step 1 YES (NPI / Reg S-P / GLBA / DFS); any §1.2 step 2 YES (FINRA 4530); NY DFS 500.17 determination in scope | Determination within 24 h of SEV-1; 72 h DFS clock from determination | Full §1.3 package with signed SHA-256 manifest under WORM; reportability decision; customer-impact analysis; communications draft; Microsoft case ID | Microsoft Premier engagement required (platform fault, vendor-managed component failure) |
| **L4 — Microsoft Premier Support + CISO** | Microsoft Premier engineer (engineering bridge) + CISO | Suspected platform fault (Copilot Studio knowledge-source scoping fault, Purview audit ingestion outage, DLP propagation > 60 min, DSPM for AI blackout); cross-tenant fault| Per Premier contract SLA (Sev A: 1 h response) | §5 Microsoft Support pack | (terminal) — escalate to Microsoft account team for product-roadmap items; Compliance reports out to Board / regulator per §1.6 |

---

## §5 — Microsoft Support pack

Mandatory data to gather **before** filing the case. Do not file without items 1–9; cases without these are routinely closed as "insufficient information" and the clock continues to run on the firm's reportability obligations.

1. **Tenant ID** (`Get-MgContext | Select TenantId`)
2. **Affected agent ID(s)** — Copilot Studio agent ID + environment ID + Maker UPN
3. **Connection / connector IDs** for every connector bound to the agent (Power Platform admin export)
4. **Audit-search Job IDs** for every `Search-UnifiedAuditLog` paged query (record the GUID `-SessionId` used)
5. **Screenshots** of each failing portal page with UTC timestamp visible (Copilot Studio Knowledge page, PPAC DLP page, Purview DSPM Activity Explorer, Purview DLP rule page, Entra access-review)
6. **Run output JSON** from the `scope-drift-monitor` solution (or equivalent) covering the failure window, paginated, no truncation
7. **Configuration-baseline diff** for the last 14 days touching DLP policies, knowledge sources, connector classifications, service-account permissions, environment Maker membership
8. **UAL paged export** (`MicrosoftCopilot`, `SharePointFileOperation`, `AzureActiveDirectoryApplicationAudit` record types) for the failure window
9. **SHA-256 manifest** (§1.3 closing note) covering all attached artifacts; signed by SOC lead
10. **Business impact statement** — Zone, customer-facing or internal, NPI determination, severity, in-scope regulators, reportability decision (if made)
11. **Reproducer** — minimal steps with a test agent + test prompt + test grounding source; do not file without a reproducer for SEV-2 and below

**When NOT to file with Microsoft.** Single-user complaint with no reproducer; request to change default product behavior (product feedback channel). Filing these wastes the case slot and dilutes urgency on the genuine platform faults.

**While waiting for Microsoft.** Maintain the §1.4 compensating control; continue capturing evidence; re-walk §1.2 if severity escalates; do **not** change configuration mid-case unless Microsoft requests it in writing on the case.

---

## §6 — Cross-references

### §6.1 Related controls

| Control | Why it matters here |

| [1.2 — Agent Registry and Integrated Apps Management](../../../controls/pillar-1-security/1.2-agent-registry-and-integrated-apps-management.md) | Source of truth for agent-to-data-source pairs; baseline for the scope-drift detector (§2.7) |
| [1.4 — Advanced Connector Policies (ACP)](../../../controls/pillar-1-security/1.4-advanced-connector-policies-acp.md) | Connector-layer enforcement of the scope this control defines at the agent layer; every "connector added without DLP review" failure (§2.1) traces here |
| [1.10 — Communication Compliance Monitoring](../../../controls/pillar-1-security/1.10-communication-compliance-monitoring.md) | Compensating control during 1.14 gap (§1.4); surfaces policy violations in agent input/output |
| [1.13 — Sensitive Information Types and Pattern Recognition](../../../controls/pillar-1-security/1.13-sensitive-information-types-sits-and-pattern-recognition.md) | Detection layer for "customer NPI surfaced via Copilot" (§2.4); SIT-based DLP on agent transcripts is the runtime detection pattern |
| [1.17 — Endpoint Data Loss Prevention (Endpoint DLP)](../../../controls/pillar-1-security/1.17-endpoint-data-loss-prevention-endpoint-dlp.md) | Endpoint-side enforcement for upload (§2.4); pairs with DLP-for-Copilot at the cloud surface |
| [1.18 — Application-Level Authorization and RBAC](../../../controls/pillar-1-security/1.18-application-level-authorization-and-role-based-access-control-rbac.md) | Identity-layer least privilege; companion for the over-privileged-service-account remediation (§2.1, §2.9) |
| [1.19 — eDiscovery for Agent Interactions](../../../controls/pillar-1-security/1.19-ediscovery-for-agent-interactions.md) | WORM evidence preservation surface for §1.3 artifacts; books-and-records anchor |
| [4.6 — Grounding Scope Governance](../../../controls/pillar-4-sharepoint/4.6-grounding-scope-governance.md) | SharePoint-side governance of the grounding sources 1.14 minimizes; re-scoping per §2.2 is co-owned by SharePoint Admin |
| [AI Incident Response Playbook](../../incident-and-risk/ai-incident-response-playbook.md) | General AI-incident framework; 1.14 §1 specializes the data-exposure / privacy sub-flow |

### §6.2 Sibling 1.14 playbooks

- [PowerShell setup](powershell-setup.md) — wrong-shell trap, paginated audit query, baseline export
- [Verification & testing](verification-testing.md) — detects the conditions this playbook handles

### §6.3 Microsoft Learn anchors

- `learn.microsoft.com/microsoft-copilot-studio/knowledge-add-sharepoint`
- `learn.microsoft.com/microsoft-copilot-studio/security-and-governance`
- `learn.microsoft.com/en-us/microsoft-copilot-studio/knowledge-copilot-studio#content-moderation`
- `learn.microsoft.com/microsoft-copilot-studio/admin-logging-copilot-studio`
- `learn.microsoft.com/power-platform/admin/wp-data-loss-prevention`
- `learn.microsoft.com/power-platform/admin/dlp-connector-classification`
- `learn.microsoft.com/purview/dspm-for-ai`
- `learn.microsoft.com/purview/dlp-microsoft365-copilot-location-learn-about`
- `learn.microsoft.com/purview/audit-log-search`
- `learn.microsoft.com/purview/audit-log-activities`
- `learn.microsoft.com/purview/alert-policies`
- `learn.microsoft.com/purview/sit-learn-about-sensitive-information-types`
- `learn.microsoft.com/sharepoint/modern-experience-sharing-permissions`
- `learn.microsoft.com/sharepoint/restricted-content-discovery`
- `learn.microsoft.com/sharepoint/advanced-management`
- `learn.microsoft.com/graph/permissions-reference`
- `learn.microsoft.com/entra/identity-platform/permissions-consent-overview`
- `learn.microsoft.com/entra/id-governance/access-reviews-overview`
- `learn.microsoft.com/powershell/module/exchange/search-unifiedauditlog`

### §6.4 Regulatory anchors

- **NY DFS 23 NYCRR 500.17(a)** — 72 h cybersecurity-event notification from determination — `dfs.ny.gov/industry_guidance/cybersecurity`
- **SEC Regulation S-P §248.30** — safeguards rule and customer-notification (amended May 2024) — `ecfr.gov/current/title-17/chapter-II/part-248/section-248.30`
- **SEC Rule 17a-3 / 17a-4** — broker-dealer recordkeeping — `ecfr.gov/current/title-17/chapter-II/part-240/section-240.17a-4`
- **GLBA Safeguards Rule (16 CFR Part 314)** — `ecfr.gov/current/title-16/chapter-I/subchapter-C/part-314`
- **FINRA Rule 3110** — supervision — `finra.org/rules-guidance/rulebooks/finra-rules/3110`
- **FINRA Rule 4511** — books-and-records general requirements — `finra.org/rules-guidance/rulebooks/finra-rules/4511`
- **FINRA Rule 4530** — reporting requirements — `finra.org/rules-guidance/rulebooks/finra-rules/4530`
- **FINRA RN 24-09 (June 2024) / Rule 3110** — generative-AI supervision expectations — `finra.org/rules-guidance/notices/24-09`
- **OCC Bulletin 2026-13 / Federal Reserve SR 26-2** (formerly OCC Bulletin 2011-12 / SR 11-7) — model risk management — `occ.gov/news-issuances/bulletins/2026/bulletin-2026-13.html` / `federalreserve.gov/supervisionreg/srletters/SR2602.htm`
- **CFTC Regulation 1.31** — recordkeeping — `ecfr.gov/current/title-17/chapter-I/part-1/subpart-A/section-1.31`
- **CCPA §1798.100** — collection-and-use minimization (purpose limitation) — `leginfo.legislature.ca.gov/faces/codes_displaySection.xhtml?sectionNum=1798.100.&lawCode=CIV`

---

## §7 — Lessons learned & post-incident review template

Run a post-incident review (PIR) within 10 business days of incident closure for every SEV-1 and SEV-2. Capture findings under the template below; circulate to the AI Governance Forum monthly; include in the firm's annual 23 NYCRR 500.17(b) Senior-Governing-Body report where in scope.

### §7.1 PIR template

```text
INCIDENT: INC-<YYYY>-<MMDD>-<seq>
SEVERITY: SEV-<n>             ZONE: <13>
DETECTION TIMESTAMP (UTC):
DETERMINATION TIMESTAMP (UTC):     // §1.2 — what regulators will examine
REMEDIATION DEPLOYED (UTC):
TOTAL ALERT-TO-REMEDIATION:        // hh:mm

REPORTABILITY DECISION (§1.2 result):
  Step 1 (NPI / Reg S-P):       <Y|N>  Decision-maker:  Date:
  Step 2 (FINRA 4530):          <Y|N>  Decision-maker:  Date:
  Step 3 (17a-4 books):         <Y|N>  Decision-maker:  Date:
  Step 4 (OCC 2026-13 / Fed SR 26-2 — formerly OCC 2011-12 / SR 11-7):       <Y|N>  Decision-maker:  Date:
  Step 5 (CFTC 1.31):           <Y|N>  Decision-maker:  Date:
  Step 6 (CCPA / state):        <Y|N>  Decision-maker:  Date:

REGULATOR NOTIFICATIONS FILED:
  - NY DFS:           <Y|N>  Filed:           Within 72h of determination?  <Y|N>
  - SEC Reg S-P:      <Y|N>  Filed:           Notification window:
  - FINRA 4530(b):    <Y|N>  Filed (≤30d):
  - State AG / other: <Y|N>  Filed:

ROOT CAUSE (5 Whys):
  1.
  2.
  3.
  4.
  5.

CONTRIBUTING FAILURE MODES (§2):
  [ ] §2.1 DLP not enforced       [ ] §2.6 DLP-for-Copilot not blocking labels
  [ ] §2.2 Knowledge source over-broad  [ ] §2.7 Scope-drift detector silent
  [ ] §2.3 Public web grounding   [ ] §2.8 Access Review not generated
  [ ] §2.4 Upload bypass          [ ] §2.9 Cross-tenant / guest unmanaged
  [ ] §2.5 DSPM blackout

ANTI-PATTERNS OBSERVED (§3):  // numbered 1–12
  Numbers:

EVIDENCE INDEX:
  Manifest:                          // path + sha256
  WORM retention applied (Y/N):
  Immutable storage container:
  Legal hold:                        // ticket / matter ID

CORRECTIVE ACTIONS (with owners + due dates):
  CA-1:
  CA-2:
  CA-3:

PREVENTIVE ACTIONS (policy / process changes):
  PA-1:
  PA-2:

CONTROL DEFICIENCIES IDENTIFIED:
  - Control 1.x: <description> → <CR / ticket>

EFFECTIVENESS-CHALLENGE NOTES (OCC Bulletin 2026-13 / Fed SR 26-2, where in scope):

SOD POSTURE AT TIME OF INCIDENT (§1.4 SoD note):
  Reviewer of record: <name>     Owner of agent: <name>     Conflict?  <Y|N>
  Corrective action:

LESSONS LEARNED (free text):

DISTRIBUTION:
  AI Governance Forum (monthly):   <date>
  CISO sign-off:                   <name + date>
  CCO sign-off:                    <name + date>
  Records to WSP / annual report:  <Y|N>
```

### §7.2 Standing review questions

1. Did §1.2 reportability tree produce the correct first-YES on the first walkthrough? If not, why — and what training or tooling change closes the gap?
2. Was the §1.4 SoD note honored? If not, what structural change is required (Maker policy, environment role-assignment, governance template)?
3. Did any §1.3 evidence item rely on a non-WORM source (Power Platform admin telemetry alone)? If yes, raise a Control 1.7 / 1.9 / 1.19 enhancement.
5. Did Microsoft Support engagement (§4 L4) yield a platform-side fix, a feature-gap acknowledgement, or no-action? Track product-roadmap requests through the Microsoft account team, not Premier cases.

### §7.3 Trend-watch (rolling 12 months)

Maintain a rolling 12-month dashboard for the AI Governance Forum:
- SEV-1 incident count by Zone
- §1.2 first-YES distribution (which regulator triggered most often)
- Mean time from detection to determination
- Mean time from determination to remediation deployed
- §2 failure-mode frequency (which runbook fired most)
- Anti-pattern recurrence (a recurring anti-pattern is a process / training gap, not an operator failure)

---

*Updated: May 2026 | Version: v1.6.2 | UI Verification Status: Current*
