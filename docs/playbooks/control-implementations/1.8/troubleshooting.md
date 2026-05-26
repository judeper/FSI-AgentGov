# Control 1.8 Troubleshooting: Runtime Protection and External Threat Detection

**Control:** 1.8 — Runtime Protection and External Threat Detection
**Pillar:** 1 — Security
**Audience:** Power Platform Admin, Microsoft Defender XDR System Administrator, AI Governance Lead, SOC Analyst
**Last UI Verified:** May 2026

> **Scope.** This playbook diagnoses runtime-protection failures across the four enforcement surfaces of Control 1.8: (1) native Defender for Cloud Apps **AI Agent Protection** (real-time evaluation through the Microsoft 365 App Connector), (2) **Additional Threat Detection** webhook callout from Microsoft Copilot Studio to an external security provider, (3) **Prompt Shields** for jailbreak/indirect-injection defense, and (4) **agent-level content moderation slider** (5 positions: Lowest / Low / Medium / High / Highest). It also covers the **AI Security Posture Management (AISPM)** dashboard surface and per-agent **Responsible AI (RAI) App Insights** telemetry. Classic (non-generative) Copilot Studio agents are out of scope for Defender AI Agent Protection — see §4 for details. The separate **per-prompt** moderation slider (3 positions: Low / Moderate / High, managed GPT models only) inside the prompt builder is governed by Control 1.27, not this playbook.

> **Two-portal architecture.** Control 1.8 is enforced through **two portals that must be configured in handshake**: Microsoft Defender XDR portal (`security.microsoft.com`) for the Defender side, and Power Platform Admin Center (`admin.powerplatform.microsoft.com`) for the Copilot Studio side. A toggle in one portal without the matching toggle in the other produces silent failure — see §2 row 1 and §6.1.

> **READ §1 FIRST if you are responding to a live event.** Sections 2–7 are diagnostic; §1 governs incident handling, regulatory clocks, and evidence preservation. Skipping §1 in a regulated incident risks a missed FINRA Rule 4530(b) report or a NY DFS 23 NYCRR 500.17(a) 72-hour clock.

---

## 1. FSI Incident Handling — READ FIRST

This section governs how a runtime-protection failure becomes an *incident*, who decides whether it is *reportable*, and how evidence must be preserved before any remediation that could overwrite logs. Use it before touching configuration in §2–§7.

### 1.1 Incident severity matrix (Zone-aware)

Severity is the product of **blast radius** (which agents and which data are at risk) and **regulatory exposure** (which books-and-records, customer-NPI, or supervision rules are implicated). Zone 3 (regulated, customer-facing) incidents are scored one severity higher than the same technical fault in Zone 1.

| Severity | Zone 1 (Personal) | Zone 2 (Team) | Zone 3 (Regulated / customer-facing) | Initial response |
|---|---|---|---|---|
| **SEV-1** (critical) | Tenant-wide loss of runtime protection across >10 agents AND active exploitation observed | Same as Zone 1, OR a Zone 2 customer-NPI agent with confirmed prompt-injection success | ANY confirmed bypass of content moderation, Prompt Shields, or webhook block on a customer-facing agent; ANY exfiltration of customer NPI via an agent | Page L3 within 30 min; SOC opens incident bridge; Legal + Compliance joined within 60 min |
| **SEV-2** (high) | Single-agent runtime-protection failure on Zone 1 with sensitive data | Defender AI Agent Protection toggle drift; AISPM alerts not flowing >4 hours; webhook 5xx storm with errorBehavior=Allow | Any of the Zone 2 conditions on a Zone 3 agent; UAL `RAI:ContentFiltered` events spike >3σ | L1 within 1 hour; L2 paged; AI Governance Lead notified within 2 hours |
| **SEV-3** (moderate) | Configuration drift detected by automated check; no exploitation evidence | Single agent missing per-agent App Insights; FIC binding misconfigured but errorBehavior=Block | Drift on a Zone 3 agent corrected within SLA; documented and reviewed at next governance cadence | L1 same business day; logged in change-management system |
| **SEV-4** (low) | Documentation/UI mismatch; cosmetic | Cosmetic | Cosmetic | Tracked in backlog |

> **Severity-escalation rule.** If during triage you uncover **either** (a) evidence that customer NPI was processed by an agent during the failure window, **or** (b) a books-and-records gap (UAL or RAI logs missing for periods covered by FINRA Rule 4511 / SEC Rule 17a-4), escalate the incident one severity level immediately and re-page accordingly.

### 1.2 Reportability decision tree

Runtime-protection failures are **not automatically reportable**. The decision is governed by the regulators below. Walk this tree top-down; the first **YES** controls reporting.

1. **Customer NPI (non-public personal information) accessed, viewed, or transmitted by an unauthorized party as a result of the failure?**
   - **YES →** SEC Regulation S-P §248.30(a)(4) customer-notification analysis begins; engage Legal within 4 hours. NY DFS-regulated entities also evaluate 23 NYCRR 500.17(a) (72-hour notice to Superintendent from *determination* of a cybersecurity event, not first alert). GLBA 501(b) safeguards review is triggered.
   - **NO →** continue to step 2.
2. **A "specified event" under FINRA Rule 4530(b) occurred (e.g., violation of securities laws, customer complaint involving compensatory damages ≥ \$15,000, internal review concluding rule violation)?**
   - **YES →** FINRA Rule 4530(b) written report due within 30 calendar days of firm conclusion that a reportable event occurred. CCO drafts; Legal reviews.
   - **NO →** continue to step 3.
3. **Books-and-records gap that prevents reconstruction of an agent interaction subject to FINRA Rule 4511 or SEC Rule 17a-3/17a-4?**
   - **YES →** This is a supervision deficiency under FINRA Rule 3110 and a recordkeeping gap under SEC Rule 17a-4. Document the gap, the corrective action, and the supervisory review in the firm's WSPs. **Do not** rely on Defender XDR / CloudAppEvents alerts as the books-and-records source — those are operational telemetry, not WORM-preserved customer communications. See Control 1.7 for the audit trail, Control 1.10 for supervisory review, and 1.9 for retention enforcement.
   - **NO →** continue to step 4.
4. **Model-risk control failure under OCC Bulletin 2026-13 (formerly OCC Bulletin 2011-12) / Federal Reserve SR 26-2 (formerly SR 11-7) (e.g., generative AI model produced uncontrolled output that materially affected a customer or a credit decision)?**
   - **YES →** Model Risk Management is engaged; document in the model inventory and trigger an out-of-cycle effective-challenge review.
   - **NO →** continue to step 5.
5. **CFTC-regulated activity (swap dealer, FCM, IB) involved and the failure caused a recordkeeping gap under CFTC Regulation 1.31?**
   - **YES →** CFTC 1.31 retention gap analysis; document remediation.
   - **NO →** Internal incident only. Document, remediate, review at governance cadence. No external regulatory report.

> **RN 24-09 reminder.** FINRA RN 24-09 (June 2024) reiterates that existing FINRA rules apply to generative-AI tools used by member firms. There is no separate "AI rule" that triggers a new report — but supervisory failures and recordkeeping gaps that involve AI are evaluated under existing Rules 3110, 4511, and 4530. FINRA RN 25-07 (April 2025) addresses workplace modernization recordkeeping and is cited contextually only; it is not the AI supervisory authority.

> **Determination vs. detection.** NY DFS 23 NYCRR 500.17(a) 72-hour clock starts from **determination** that a reportable cybersecurity event has occurred, not from the first alert. Document the determination decision (who, when, what evidence) — this is the timestamp regulators will examine.

### 1.3 Evidence preservation (do this before remediation)

Runtime-protection remediation often involves toggling Defender or PPAC settings, restarting webhook providers, or reconfiguring federated identity credentials (FICs). Each of these can overwrite or invalidate the evidence trail. Capture the items below **before** any change.

**Mandatory evidence capture (≥12 items):**

1. **PPAC toggle state** — screenshot of `Power Platform Admin Center → Security → AI security posture management` showing the **AI Agent Protection** toggle state (On / Off) and the **Additional Threat Detection** configuration block (provider URL, FIC binding, errorBehavior). Export via `Get-AdminPowerPlatformAISettings` (or equivalent admin API) to JSON.
2. **Defender XDR toggle state** — screenshot of `Defender XDR → Settings → Cloud apps → AI Agent Protection` showing preview opt-in and Connector binding. Capture the M365 App Connector status (Connected / Disconnected / Error).
3. **M365 App Connector health** — `Defender XDR → Settings → Cloud apps → App Connectors → Microsoft 365` last-sync timestamp and any error string.
4. **FIC (federated identity credential) configuration** — for each agent that calls an external webhook, capture the FIC subject, issuer, and audience values from the App Registration (`Entra ID → App registrations → <app> → Certificates & secrets → Federated credentials`). Mismatched FIC produces 401 from the webhook but the agent may still respond — see §6.5.
5. **Content moderation level snapshot** — for each affected agent, the configured agent-level slider position (Lowest / Low / Medium / High / Highest) for hate, sexual, violence, self-harm. Export via Copilot Studio admin API or screenshot from the agent's `Settings → Generative AI → Content moderation`.
6. **App Insights connection string per agent** — RAI telemetry binding for each affected agent. Without per-agent App Insights, `RAI:ContentFiltered`, `RAI:JailbreakDetected`, and `RAI:GroundingFailed` events are not retrievable for that agent. Capture the resource ID and the connection string redacted (last-4 only) for evidence.
7. **AISPM dashboard screenshot** — current alert list, suppressed alerts, and the timestamp of the last AISPM refresh (note the up-to-15-minute latency disclaimer).
8. **CloudAppEvents export (Defender)** — Advanced hunting export covering the failure window plus 24 hours before/after. Use the Learn-documented `CloudAppEvents` schema; this is operational telemetry, **not** a books-and-records source — see disclaimer below.
9. **Unified Audit Log (UAL) paged export** — `Search-UnifiedAuditLog -RecordType CopilotInteraction -SessionId <guid> -SessionCommand ReturnLargeSet` for the failure window. **Do not use `-RecordType CopilotStudio`** (that record type does not exist) and **do not use a single-shot query** without `-SessionId` (truncates at 5,000 rows). See §6.7.
10. **RAI:ContentFiltered / JailbreakDetected export** — KQL against the per-agent App Insights resource for the failure window. Required for any incident involving content moderation, Prompt Shields, or jailbreak claims.
11. **Role-group snapshot** — current membership of: Microsoft Defender XDR System Administrator, Power Platform Admin, Application Administrator, AI Security Operator, and any custom AISPM viewer roles. Captures who could have changed the toggle.
12. **Sovereign cloud confirmation** — explicit record of the cloud (Commercial / GCC / GCC High / DoD), because Defender for Cloud Apps AI Agent Protection has Commercial-only parity as of Q1 2026 (see §4). The cloud determines which evidence sources are available.
13. **SHA-256 manifest** — produce a manifest file listing every evidence file captured above with its SHA-256. Sign the manifest (or store in a WORM location) so its integrity can be demonstrated to a regulator. This is the chain-of-custody anchor; without it, every other artifact is challengeable.

> **Defender XDR / CloudAppEvents retention disclaimer.** Defender XDR alerts and the `CloudAppEvents` Advanced Hunting table are **operational telemetry**, retained for 30 days (default) in Advanced Hunting. They are **not** WORM, **not** a books-and-records source under SEC Rule 17a-4, and **not** sufficient on their own to satisfy FINRA Rule 4511. Cross-link Control 1.7 (Comprehensive Audit Logging and Compliance) for the audit trail, Control 1.10 (Communication Compliance Monitoring) for supervisory review, and Control 1.9 (Data Retention and Deletion Policies) for retention enforcement. If your incident involves a books-and-records claim, capture the WORM-side evidence in addition to the Defender-side telemetry.

### 1.4 Compensating controls during remediation

If a runtime-protection surface is degraded and cannot be restored within the SLA (Zone 3 SEV-1: 4 hours), apply compensating controls before resuming agent traffic.

| Failed surface | Compensating control | Time to deploy |
|---|---|---|
| Native Defender AI Agent Protection (M365 Connector down) | Quarantine the affected generative agents (set publication off) until connector is restored. **Do not** rely on Additional Threat Detection alone — they evaluate different signals. | 15 min (PPAC publication toggle) |
| Additional Threat Detection webhook (5xx from provider) | If `errorBehavior=Block` is configured (required for Zone 2/3), the agent will already block on webhook failure — confirm. If `errorBehavior=Allow`, immediately switch to Block (or quarantine the agent) — **Allow during a provider outage means the agent runs unprotected**. See §3 anti-pattern A4. | 5 min |
| Prompt Shields (Azure Content Safety regional outage) | Increase content moderation to High for the duration; re-evaluate agent grounding sources for indirect-injection vectors; quarantine high-risk agents (those with web search or external connector grounding). | 30 min |
| Content moderation (configured Low on Zone 2/3 in violation of policy) | Raise to Medium (Zone 2) or High (Zone 3) immediately. Audit `RAI:ContentFiltered` for the prior 30 days to assess what may have been allowed through. | 10 min |
| AISPM dashboard not refreshing | Continue to rely on direct Defender XDR alerts and KQL until refresh resumes. AISPM is a *visualization* layer, not the enforcement surface — enforcement continues. | n/a |
| Per-agent App Insights missing | Bind App Insights immediately; backfill is **not possible** — the gap from agent creation to App Insights binding is permanently unrecoverable. Document the gap as a books-and-records issue if the agent is Zone 2/3. | 10 min binding; gap is permanent |

### 1.5 Pre-escalation checklist (≥12 items)

Run this checklist before paging L2 or L3. Items failed → capture in the escalation payload (§7).

- [ ] **§1.1** Severity assigned (and re-evaluated against the severity-escalation rule for NPI / books-and-records).
- [ ] **§1.2** Reportability tree walked top-down; first YES recorded with timestamp and decision-maker.
- [ ] **§1.3.1–§1.3.13** All thirteen evidence items captured to the incident folder with the SHA-256 manifest signed.
- [ ] **PPAC + Defender XDR toggles** — both portals' toggle states confirmed and screenshot captured (handshake state recorded explicitly).
- [ ] **M365 App Connector** status confirmed Connected; last-sync within 60 min.
- [ ] **errorBehavior** value confirmed (Allow / Block) for every affected agent; Zone 2/3 agents confirmed Block.
- [ ] **FIC binding** validated for every agent calling an external webhook (subject + audience match).
- [ ] **Content moderation level** captured per agent and compared to the Zone policy minimum.
- [ ] **Per-agent App Insights** binding verified for every Zone 2/3 agent.
- [ ] **AISPM latency** noted (last-refresh timestamp captured; 15-min delay accounted for).
- [ ] **Sovereign cloud** explicitly recorded; §4 fallbacks reviewed if not Commercial.
- [ ] **UAL paged export** completed with `-SessionId` + `-SessionCommand ReturnLargeSet`; row count recorded; truncation at 5K confirmed not applicable.
- [ ] **Compensating control** in place if runtime protection cannot be restored within SLA (§1.4).
- [ ] **Customer-impact analysis** completed and recorded (count of impacted customers, NPI exposure assessment, customer-facing agent list).
- [ ] **Communications draft** prepared if reportability tree returned YES at any step.

### 1.6 Worked example — UPIA blocked on a Zone 3 customer-facing agent

**Scenario.** AISPM dashboard shows an "Unauthorized Prompt Injection Attempt (UPIA)" alert at 09:42 against a Zone 3 customer-facing wealth-management agent. The webhook returned `block` and the agent refused. SOC analyst paged.

**Step 1 — severity (per §1.1).** Zone 3 + confirmed bypass attempt + customer-facing → SEV-2 baseline. No evidence of NPI exfiltration in the response stream → not yet SEV-1. Re-evaluate after evidence review.

**Step 2 — reportability (per §1.2).** No NPI exposed (block succeeded) → step 1 NO. No FINRA 4530(b) specified event → step 2 NO. UAL and RAI logs intact for the interaction → no books-and-records gap → step 3 NO. Model behaved as configured → step 4 NO. → **Internal incident only**, no external regulatory report. Decision recorded: Compliance Officer, 10:18, signed.

**Step 3 — evidence preservation (per §1.3).** Captured items 1–13 to incident folder `INC-2026-0214-0042/`. SHA-256 manifest signed by SOC lead at 10:34.

**Step 4 — root-cause investigation.** Was this a real attack or a false positive? KQL against `RAI:JailbreakDetected` plus the webhook-provider's own log shows the prompt was an indirect-injection probe embedded in a SharePoint document the agent grounded against. Block was correct.

**Step 5 — remediation.** No remediation needed for the runtime layer (it worked). Refer the SharePoint grounding source to Control 1.5 (Data Loss Prevention (DLP) and Sensitivity Labels) and 4.x (SharePoint AI governance) for content review. File a ticket against the SharePoint owner.

**Step 6 — governance cadence.** Logged in monthly AI governance review; no policy change.

**Total time from alert to closure:** 4 hours 12 minutes. Determination decision (per NY DFS 500.17(a)) recorded as "not a reportable cybersecurity event" at 10:18 — clock stopped at determination, no external notice required.

---
## 2. Decision matrix — symptom → cause → action → owner

Use this table as a triage entry point. Each row is a recurring failure mode in Control 1.8. The "Detail" column points to the §6 deep-dive for diagnostic snippets and Microsoft Learn references.

| # | Symptom | Probable cause | Action | Owner | Detail |
|---|---|---|---|---|---|
| 1 | AISPM dashboard shows agents but no alerts ever fire; Defender XDR shows AI Agent Protection On but PPAC shows AI Agent Protection Off (or vice versa) | **Two-portal handshake broken** — the toggle exists in both portals and *both* must be On for native protection to evaluate. PPAC On + Defender Off = no Defender evaluation; Defender On + PPAC Off = Defender ignores the tenant's agents. | Open both portals, confirm both toggles On. Capture screenshots for evidence (§1.3 item 1 and 2). Trigger a known-bad prompt against a test agent and confirm `CloudAppEvents` in Defender within 15 min. | Power Platform Admin + Microsoft Defender XDR System Administrator (joint) | §6.1 |
| 2 | Defender XDR portal shows banner "Microsoft 365 App Connector error" or "not connected"; AISPM agent inventory empty or stale | **M365 App Connector authentication failure** — connector uses tenant-level OAuth; admin consent expired, conditional access blocked the service principal, or tenant-restriction policy is filtering the connector traffic. | Defender XDR → Settings → Cloud apps → App Connectors → Microsoft 365 → Reconnect. If conditional access is blocking, exclude the connector service principal. Validate connector last-sync timestamp returns to <60 min. | Microsoft Defender XDR System Administrator | §6.2 |
| 3 | Defender XDR Settings → Cloud apps does not show **AI Agent Protection** anywhere; documentation says it should be there | **Preview opt-in not completed** OR tenant is not eligible (sovereign cloud — see §4) OR Defender for Cloud Apps license is missing. | Confirm tenant in Commercial cloud (§4); confirm Defender for Cloud Apps license assigned; opt in to the AI Agent Protection preview from the Defender XDR Settings → Cloud apps page. Allow up to 60 min for UI to surface. | Microsoft Defender XDR System Administrator | §6.3 |
| 4 | AI Agent Protection toggle is greyed out in PPAC; tooltip says "Managed Environments required" | **Managed Environments not enabled** for the environment containing the agent. AI Agent Protection enforcement requires the environment to be a Managed Environment. | PPAC → Environments → select environment → Edit Managed Environments → Enable. Confirm license capacity for Managed Environments. Re-check the AI Agent Protection toggle. | Power Platform Admin | §6.4 |
| 5 | Webhook provider returns 5xx for >1 min; agent continues responding to users normally; no `block` events appear | **errorBehavior=Allow** is configured (anti-pattern A4 below). On webhook failure or timeout, the agent allows the response. For Zone 2/3 this is a policy violation. | Switch errorBehavior to **Block** immediately. PPAC → Security → AI security posture management → Additional Threat Detection → edit. Audit the failure window in UAL and `CloudAppEvents` for any responses returned during the outage that would have been blocked. | Power Platform Admin (config) + AI Governance Lead (policy) | §6.4, §6.5 |
| 6 | Webhook provider logs show 401 Unauthorized on every Copilot Studio callout; agent responses still flow (or block, depending on errorBehavior) | **FIC binding wrong** — the federated identity credential subject, issuer, or audience does not match what Copilot Studio sends. The webhook is invoked but cannot validate the token, so the provider returns 401. Copilot Studio treats the 401 as a provider failure and falls back to errorBehavior. | Compare the FIC subject/issuer/audience to the values documented in `learn.microsoft.com/microsoft-copilot-studio/external-security-provider`. Re-bind the FIC. Validate with a test prompt; confirm webhook returns 200 (allow) or 200 (block) — not 401. | Application Administrator + Power Platform Admin | §6.5 |
| 7 | KQL query against `PowerPlatformAdminActivity` returns zero rows for known admin actions you saw in the portal | **Schema gotcha** — the `PowerPlatformAdminActivity` table uses **`EventOriginalType`**, not `Operation`. Queries written against `Operation` silently return empty. | Rewrite the query: `PowerPlatformAdminActivity \| where EventOriginalType == "<event-name>"`. Cross-reference the table schema at `learn.microsoft.com/azure/azure-monitor/reference/tables/powerplatformadminactivity`. | SOC Analyst / AI Governance Lead | §6.6 |
| 8 | `Search-UnifiedAuditLog -RecordType CopilotStudio` returns zero rows; you know agents were used | **Wrong RecordType** — Copilot Studio interactions are logged under `CopilotInteraction`, not `CopilotStudio`. The latter is not a valid RecordType and silently returns empty. | Re-run with `-RecordType CopilotInteraction`. Reference `learn.microsoft.com/powershell/module/exchange/search-unifiedauditlog`. | SOC Analyst | §6.7 |
| 9 | UAL query for a busy agent returns exactly 5,000 rows even though you expect more; subsequent rows missing | **Single-shot UAL truncation at 5,000 rows.** A `Search-UnifiedAuditLog` call without session paging hard-caps at 5K. | Re-run with `-SessionId <new-guid> -SessionCommand ReturnLargeSet` and loop until the cmdlet returns fewer than 5K rows. Save the full set; preserve the SessionId in evidence. | SOC Analyst | §6.7 |
| 10 | A Zone 2/3 agent has content moderation set to **Low**; `RAI:ContentFiltered` rates appear unusually low; user complaints about inappropriate output | **Policy violation** — Zone 2/3 minimum is **Medium**; Zone 3 customer-facing minimum is typically **High**. Low allows hate/sexual/violence content the policy intends to block. | Raise to Medium (Zone 2) or High (Zone 3). Audit prior 30-day output for what was allowed through. Document for governance review. | AI Governance Lead + agent owner | §6.8 |
| 11 | `RAI:ContentFiltered`, `RAI:JailbreakDetected`, `RAI:GroundingFailed` events not retrievable for a specific agent; KQL returns nothing for that agent's resourceId | **Per-agent App Insights binding missing.** Each agent needs its own App Insights connection string for RAI telemetry. Without binding, the events are emitted but not collected. **Backfill is not possible.** | Bind App Insights immediately. Document the gap window (agent-creation timestamp → binding timestamp) as a books-and-records issue if Zone 2/3. | Power Platform Admin + agent owner | §6.9 |
| 12 | Agent uses a customer-supplied connector; runtime protection alerts include "connection consent revoked" or the agent fails calls to the provider | **End-customer revoked OAuth consent** for the connection. Agent calls fail; runtime protection cannot evaluate the response stream because the upstream call never returned. | Coordinate with the customer to re-consent. Until restored, route customers to the fallback (non-agent) channel. This is **not** a runtime-protection failure — it is a connection-consent failure — but AISPM may surface it under the same alert family. | Agent owner + Power Platform Admin | §6.5 (related) |

> **Decision-matrix discipline.** Always confirm both portals' toggle states before declaring a "Defender problem" or a "Copilot Studio problem". The two-portal handshake (row 1) is the single most common cause of "no alerts firing despite everything looking on" tickets.

---

## 3. Anti-pattern catalog

These ten anti-patterns produce silent or under-detected failures. Each is observed in real FSI deployments. Audit your environment against this list quarterly.

1. **Toggling AI Agent Protection in PPAC only (or Defender XDR only).** Both portals must be On. Single-side On = silent no-op for the unbound side. Mitigation: include both portal screenshots in every change-management ticket touching this control.
2. **Treating Defender XDR alerts / `CloudAppEvents` as books-and-records.** They are operational telemetry, 30-day default retention, not WORM. SEC Rule 17a-4 and FINRA Rule 4511 require the recordkeeping and supervision controls in 1.7, 1.9, and 1.10. Mitigation: never cite CloudAppEvents alone as the recordkeeping source in a regulatory response.
3. **Configuring Additional Threat Detection without binding a per-agent App Insights resource.** The webhook callout is logged in the provider's logs but the *Copilot Studio side* of the interaction (RAI events, grounding failures) is lost without App Insights. Mitigation: bind App Insights *before* enabling Additional Threat Detection on a Zone 2/3 agent.
4. **Setting `errorBehavior=Allow` on Zone 2/3 agents.** When the webhook times out (1-second hard limit) or the provider returns 5xx, Allow lets the response through unprotected. For Zone 2/3 the only acceptable value is Block. Mitigation: enforce Block via tenant policy and audit every agent quarterly.
5. **Relying on AISPM dashboard freshness for live incident triage.** AISPM has up to 15-minute latency. During an active incident, query Defender XDR Advanced Hunting (`CloudAppEvents`) and the per-agent App Insights resource directly. Mitigation: train SOC on direct KQL, not dashboard polling.
6. **Setting content moderation to Low on a Zone 2/3 agent.** Low allows substantial hate/sexual/violence content. Zone 2 minimum is Medium; Zone 3 is typically High. Mitigation: encode the per-zone minimums in a tenant-wide DLP-style policy and audit.
7. **Configuring the FIC binding from documentation written for a different cloud.** Audience values differ between Commercial / GCC / GCC High / DoD. A FIC bound with the Commercial audience in a GCC High tenant produces 401s. Mitigation: cite the Learn URL for *your specific cloud* in the FIC change ticket; cross-check audience against `external-security-provider` Learn page.
8. **Querying `PowerPlatformAdminActivity` with `Operation` instead of `EventOriginalType`.** Returns empty silently. Mitigation: code-review every KQL query that touches this table; reject reviews that use `Operation`.
9. **Querying UAL with `-RecordType CopilotStudio` (does not exist) or single-shot without `-SessionId`.** Both return incomplete data silently. The first returns nothing; the second hard-caps at 5,000 rows. Mitigation: every UAL Copilot query must use `-RecordType CopilotInteraction` AND `-SessionId` + `-SessionCommand ReturnLargeSet`. Add this to the SOC runbook template.
10. **Treating a successful `block` event as proof the threat was external.** Indirect prompt-injection often originates inside the tenant — in a SharePoint document, an internal chat message, or a connector-fetched data source. A `block` confirms the response layer worked but does not absolve the *grounding source* — refer the source to the relevant upstream-governance control (for example, Control 1.5 for DLP / labels, Control 1.10 for communication monitoring, or 4.x for SharePoint governance).

---

## 4. Sovereign cloud variants

Defender for Cloud Apps **AI Agent Protection** is a Microsoft Defender preview that is **Commercial-only** as of Q1 2026. Other Control 1.8 surfaces have varying parity. Confirm your cloud (§1.3 item 12) before applying any guidance below.

| Capability | Commercial | GCC | GCC High | DoD | Notes |
|---|---|---|---|---|---|
| Defender for Cloud Apps **AI Agent Protection** (native) | ✅ Available (preview) | ❌ Not available | ❌ Not available | ❌ Not available | Use Additional Threat Detection webhook + AISPM + per-agent App Insights as the primary defense in non-Commercial clouds. |
| **Additional Threat Detection** webhook (Copilot Studio) | ✅ | ✅ | ✅ (with sovereign provider) | ✅ (with sovereign provider) | The webhook provider must reside in a compliant cloud boundary. For GCC High / DoD, validate the provider's authorization (e.g., FedRAMP High, DoD IL5). |
| **Prompt Shields** (Azure Content Safety) | ✅ | ✅ | Limited regional availability | Limited | Confirm the Content Safety region binding for your tenant; some regions are not available in GCC High / DoD. |
| **Content moderation** Low/Med/High | ✅ | ✅ | ✅ | ✅ | Same enforcement model across clouds. |
| **AISPM dashboard** | ✅ | Limited (telemetry partial) | ❌ Not surfaced | ❌ Not surfaced | In GCC High / DoD, the equivalent visibility comes from Defender XDR's hunting tables and per-agent App Insights, not an AISPM-branded dashboard. |
| **Per-agent App Insights** | ✅ | ✅ | ✅ (Azure Government) | ✅ (Azure Government Secret/Top Secret as applicable) | Use the corresponding sovereign Azure Monitor instance. Connection strings differ by cloud. |
| Admin portal URL | `admin.powerplatform.microsoft.com` | `gcc.admin.powerplatform.microsoft.us` | `admin.powerplatform.appsplatform.us` | `admin.apps.mil` | Bookmark the correct URL for your cloud. |
| Defender portal URL | `security.microsoft.com` | `security.microsoft.com` (GCC tenant) | `security.microsoft.us` | `security.apps.mil` | |
| Copilot Studio licensing reference | Standard licensing | See Learn `requirements-licensing-gcc` | See Learn `requirements-licensing-gcc` (GCC High section) | See Learn `requirements-licensing-gcc` (DoD section) | Some preview features are excluded from sovereign clouds — confirm before designing controls around them. |

**Fallback patterns by cloud:**

- **GCC tenants** — When AI Agent Protection (Defender preview) is unavailable, the primary runtime defense is Additional Threat Detection webhook with errorBehavior=Block and a sovereign-cloud-resident provider. Compensate the missing AISPM dashboard with scheduled KQL against per-agent App Insights and `PowerPlatformAdminActivity`.
- **GCC High tenants** — Same as GCC, plus: validate the Content Safety region; if Prompt Shields are unavailable in your region, raise content moderation to High and harden grounding sources (no public web search; vetted SharePoint only). Document the compensating control in the agent's design record.
- **DoD tenants** — Same as GCC High, plus: every external dependency (webhook provider, Azure Monitor, Content Safety) must be in DoD IL-appropriate boundaries. Confirm the Copilot Studio service availability for your specific DoD impact level — some Copilot Studio features (especially generative actions) are not available in all DoD environments.

> **Sovereign cloud anti-pattern.** Reading Commercial-cloud Learn documentation and assuming the same UI / capability exists in GCC High. The toggles, URLs, and feature parity differ. Always cross-check with `requirements-licensing-gcc` and the cloud-specific portal URLs above.

---
## 5. Escalation matrix (L1 → L4)

This matrix is **runtime-protection-specific**. It distinguishes platform issues (Microsoft service degradation), configuration issues (toggles, FIC, errorBehavior), and threat events (active or attempted bypass). Do not use a generic SOC matrix here — the criteria for escalating an AI runtime issue differ from a classic identity or endpoint incident.

| Level | Owner | Triggers | MTTR target | Required evidence at handoff | Transition criteria to next level |
|---|---|---|---|---|---|
| **L1** | Power Platform Admin (with Microsoft Defender XDR System Administrator on watch) | All SEV-3 and SEV-4; initial triage of all SEV-1/2 | 1 business hour for SEV-3; 30 min for SEV-1/2 | §1.5 pre-escalation checklist completed; both portals' toggle screenshots; UAL paged export started | Decision matrix §2 row exhausted with no fix; OR SEV-1/2 confirmed; OR books-and-records gap identified |
| **L2** | AI Governance Lead + SOC Analyst | All SEV-2; SEV-1 within 60 min of detection; any incident where reportability tree §1.2 returns YES at step 2, 3, 4, or 5 | 4 hours for SEV-2; 1 hour for SEV-1 | All §1.3 evidence items 1–13; §1.2 reportability decision recorded with timestamp; AISPM screenshot; CloudAppEvents export covering window ±24 h | Customer NPI exposure suspected (§1.2 step 1 YES); OR SEV-1 confirmed; OR Microsoft platform-side fault suspected |
| **L3** | CISO + Compliance Officer + Legal | SEV-1; any §1.2 step 1 YES (NPI / Reg S-P); any §1.2 step 2 YES (FINRA 4530(b)); NY DFS 23 NYCRR 500.17(a) determination | Determination decision within 24 h of SEV-1 declaration; 72-hour DFS clock from determination | Full §1.3 evidence package with signed SHA-256 manifest; reportability decision documented; customer-impact analysis; communications draft | Microsoft Support engagement required (platform fault, suspected service-side bug, or vendor-managed component failure) |
| **L4** | Microsoft Support (via Premier / Unified) | Suspected platform fault (Defender service degradation, Copilot Studio runtime fault, AISPM ingestion outage, M365 Connector inability to authenticate not attributable to tenant config) | Per support contract SLA | §7 escalation payload (template below) | n/a (terminal escalation) |

**L1 → L2 specific triggers for runtime protection:**

- §2 decision matrix row 1, 2, 3, or 4 confirmed but no fix in <1 hour.
- Webhook provider outage exceeds the SLA documented with the provider.
- AISPM dashboard not refreshing for >2 hours (suspect ingestion fault — could be configuration or service-side).
- Any UAL or RAI gap detected on a Zone 2/3 agent (books-and-records implication).
- A customer (external party) reports anomalous output from a Zone 3 agent.

**L2 → L3 specific triggers:**

- Reportability tree returns YES at any step.
- Severity escalates from SEV-2 to SEV-1 mid-incident.
- The incident touches multiple regulated business lines (e.g., wealth management + lending) — broader scope requires CISO/Compliance scope.
- A regulator inquiry arrives mid-incident.

**L3 → L4 (Microsoft Support) specific triggers:**

- Platform component is suspected at fault, not tenant configuration.
- Sovereign cloud feature parity question (e.g., is AI Agent Protection now available in GCC?).
- Microsoft-managed component (M365 App Connector, AISPM ingestion, Defender preview) is degraded with no admin remediation path.

> **Distinguish platform vs. config vs. threat.** Before escalating to Microsoft Support, eliminate configuration. Microsoft Support will close a case as "not a Microsoft fault" if you cannot show that toggles, FIC, errorBehavior, App Insights binding, and licensing are all correct. Use §6 deep-dives to confirm before paying the support engagement.

---

## 6. Detailed failure modes — diagnostics

Each subsection covers one of the nine major failure modes. Format: **Symptom → Root cause → Diagnostic snippet → Microsoft Learn → Fix.**

### 6.1 Two-portal handshake broken (PPAC ↔ Defender XDR)

**Symptom.** AISPM dashboard lists agents but shows no alerts. Defender XDR Settings shows AI Agent Protection On; PPAC shows AI Agent Protection Off (or vice versa). A known-bad prompt produces no `CloudAppEvents` row.

**Root cause.** AI Agent Protection is enforced when **both** portals' toggles are On. This is a defense-in-depth handshake: PPAC enables the data-plane export from Power Platform; Defender XDR enables the consumption and evaluation of that data. One side without the other is a silent no-op.

**Diagnostic.**

```powershell
# Capture PPAC side via REST (replace tenant + auth):
$token = (Get-AzAccessToken -ResourceUrl "https://api.powerplatform.com").Token
$headers = @{ Authorization = "Bearer $token" }
Invoke-RestMethod -Uri "https://api.powerplatform.com/governance/aisecurity/v1/aiagentprotection?api-version=2024-10-01" -Headers $headers |
    Select-Object enabled, lastUpdated, lastUpdatedBy
```

```kusto
// Defender XDR Advanced Hunting — confirm AI Agent Protection is emitting events at all
CloudAppEvents
| where Application == "Microsoft Copilot Studio"
| where Timestamp > ago(24h)
| summarize Events = count() by ActionType, bin(Timestamp, 1h)
| order by Timestamp desc
```

If the KQL returns zero rows for the last 24 hours despite known agent activity, the handshake is broken on the Defender side.

**Microsoft Learn.**

- `learn.microsoft.com/defender-cloud-apps/ai-agent-protection`
- `learn.microsoft.com/defender-cloud-apps/real-time-agent-protection-during-runtime`
- `learn.microsoft.com/en-us/power-platform/guidance/adoption/threat-detection`

**Fix.** Toggle both portals On. Capture screenshots for evidence. Trigger a test prompt against a sandbox Zone 1 agent and confirm a `CloudAppEvents` row appears within 15 min. Document the joint toggle decision in change management — both Power Platform Admin and Microsoft Defender XDR System Administrator sign off.

### 6.2 Microsoft 365 App Connector authentication failure

**Symptom.** Defender XDR portal banner: "Microsoft 365 connector error" or last-sync timestamp >2 hours old. AISPM agent inventory empty or stale. New agents created in Copilot Studio do not appear in Defender.

**Root cause.** The M365 App Connector uses a tenant-scoped service principal with Graph permissions. Common failure modes: admin consent expired or revoked; conditional access policy applied to "all cloud apps" caught the connector service principal; tenant restriction policy is blocking egress; recent Entra password rotation invalidated cached credentials.

**Diagnostic.**

```powershell
# Confirm the connector's service principal and recent sign-ins
Connect-MgGraph -Scopes "AuditLog.Read.All","Application.Read.All"
$sp = Get-MgServicePrincipal -Filter "displayName eq 'Microsoft 365'" -All |
    Where-Object { $_.AppId -eq '<connector-app-id>' }
Get-MgAuditLogSignIn -Filter "appId eq '$($sp.AppId)' and createdDateTime ge $(Get-Date).AddHours(-24).ToString('o')" |
    Select-Object createdDateTime, status, conditionalAccessStatus, ipAddress |
    Sort-Object createdDateTime -Descending
```

**Microsoft Learn.**

- `learn.microsoft.com/defender-cloud-apps/ai-agent-protection`
- `learn.microsoft.com/microsoft-365/security/defender/advanced-hunting-cloudappevents-table`

**Fix.** Defender XDR → Settings → Cloud apps → App Connectors → Microsoft 365 → Reconnect. If conditional access is the cause, exclude the connector service principal (or add an explicit allow rule). After reconnect, validate that `CloudAppEvents` resumes for the Copilot Studio application within 30 min.

### 6.3 Defender preview opt-in missing

**Symptom.** Defender XDR Settings → Cloud apps shows no **AI Agent Protection** node. PPAC may show the protection toggle but Defender side is invisible.

**Root cause.** AI Agent Protection in Defender for Cloud Apps is gated behind a **preview opt-in** on the Defender XDR Settings page (as of Q1 2026). Without opt-in, the feature is hidden from the UI. Eligibility also requires the tenant to be in the **Commercial cloud** and to have an active Defender for Cloud Apps license.

**Diagnostic.** Check Defender XDR → Settings → Cloud apps → Preview features. Confirm tenant cloud (`Get-MgOrganization | Select-Object DisplayName, TenantType, AdditionalProperties`). Confirm Defender for Cloud Apps license assigned at the tenant.

**Microsoft Learn.**

- `learn.microsoft.com/defender-cloud-apps/ai-agent-inventory`
- `learn.microsoft.com/defender-cloud-apps/ai-agent-protection`

**Fix.** Opt in to the preview. Allow up to 60 min for the UI to surface the AI Agent Protection node. If the tenant is sovereign (GCC / GCC High / DoD), the preview is **not available** — see §4 and use the fallback pattern.

### 6.4 Managed Environments not enabled / errorBehavior misconfigured

**Symptom (Managed Environments).** PPAC shows the AI Agent Protection toggle greyed out with a tooltip "Managed Environments required."

**Symptom (errorBehavior).** Webhook provider returns 5xx for >1 minute or exceeds the 1-second timeout; users continue to receive agent responses; no `block` events appear.

**Root cause.** Two related but distinct configuration issues. AI Agent Protection enforcement requires the Power Platform environment to be enrolled in Managed Environments. Separately, Additional Threat Detection's `errorBehavior` field controls what happens when the webhook fails — `Allow` lets the response through; `Block` rejects it. Zone 2/3 policy mandates `Block`.

**Diagnostic.**

```powershell
# Enumerate environments and their Managed Environments status
$token = (Get-AzAccessToken -ResourceUrl "https://api.bap.microsoft.com").Token
$headers = @{ Authorization = "Bearer $token" }
Invoke-RestMethod -Uri "https://api.bap.microsoft.com/providers/Microsoft.BusinessAppPlatform/scopes/admin/environments?api-version=2020-10-01" -Headers $headers |
    Select-Object -ExpandProperty value |
    Select-Object @{n='Name';e={$_.properties.displayName}}, @{n='Managed';e={$_.properties.governanceConfiguration.protectionLevel}}
```

For errorBehavior, inspect the Additional Threat Detection configuration in PPAC → Security → AI security posture management. There is no documented public REST surface for this field at GA; for change-management evidence, screenshot the configured value.

**Microsoft Learn.**

- `learn.microsoft.com/microsoft-copilot-studio/external-security-provider`
- `learn.microsoft.com/en-us/power-platform/guidance/adoption/threat-detection`
- `learn.microsoft.com/en-us/microsoft-copilot-studio/knowledge-copilot-studio#content-moderation`

**Fix.** Enable Managed Environments for the affected environment; confirm the toggle is no longer greyed out. For errorBehavior, switch to `Block` for any Zone 2/3 agent immediately. Audit `CloudAppEvents` and the webhook provider's logs for the outage window to assess whether responses were allowed through that should have been blocked.

### 6.5 FIC binding wrong (401 from external security provider)

**Symptom.** Webhook provider logs show `401 Unauthorized` on every Copilot Studio callout. The agent continues to respond (if `errorBehavior=Allow`) or always blocks (if `errorBehavior=Block`) — both are wrong because the webhook never actually evaluates the prompt.

**Root cause.** Copilot Studio authenticates to the external security provider using a **federated identity credential (FIC)** on an App Registration. The FIC must specify an `issuer` (Microsoft Entra issuer URL for the tenant + `copilotstudio` audience), a `subject` (Copilot Studio identifier for the bound agent or environment), and an `audience` (the value the webhook expects). A mismatch on any of these — most commonly `audience` when copy-pasted from the wrong cloud's Learn doc — results in a token the provider cannot validate, returning 401.

**Diagnostic.**

```powershell
# List FIC bindings on the App Registration used by the security provider
Connect-MgGraph -Scopes "Application.Read.All"
$app = Get-MgApplication -Filter "displayName eq '<security-provider-app>'"
Get-MgApplicationFederatedIdentityCredential -ApplicationId $app.Id |
    Select-Object Name, Issuer, Subject, Audiences
```

Compare `Issuer`, `Subject`, and `Audiences` to the values documented at `learn.microsoft.com/microsoft-copilot-studio/external-security-provider` for your specific cloud.

**Microsoft Learn.**

- `learn.microsoft.com/microsoft-copilot-studio/external-security-provider`
- `learn.microsoft.com/microsoft-copilot-studio/admin-logging-copilot-studio`

**Fix.** Re-bind the FIC with the correct values. Trigger a test prompt; confirm the provider returns 200 (allow or block — both are correct outcomes; 401 is not). Update the change-management ticket with before/after FIC values and the test result.

### 6.6 KQL `Operation` vs `EventOriginalType` (PowerPlatformAdminActivity)

**Symptom.** Hunting query against `PowerPlatformAdminActivity` returns zero rows for admin actions you can see in the PPAC audit log UI.

**Root cause.** The Azure Monitor table `PowerPlatformAdminActivity` does **not** have a column named `Operation`. The equivalent column is `EventOriginalType`. KQL silently returns empty for non-existent columns referenced in a `where` clause that evaluates to false (because no row has the column).

**Diagnostic / fix.**

```kusto
// WRONG — silently returns zero rows
PowerPlatformAdminActivity
| where Operation == "EnableAIAgentProtection"

// RIGHT
PowerPlatformAdminActivity
| where EventOriginalType == "EnableAIAgentProtection"
| project TimeGenerated, EventOriginalType, EventOriginalUid, Identity, ResultType
| order by TimeGenerated desc
```

**Microsoft Learn.**

- `learn.microsoft.com/azure/azure-monitor/reference/tables/powerplatformadminactivity`

### 6.7 UAL `-RecordType` and 5,000-row truncation

**Symptom (wrong RecordType).** `Search-UnifiedAuditLog -RecordType CopilotStudio` returns zero rows.

**Symptom (truncation).** A query for a busy agent returns exactly 5,000 rows; subsequent rows missing without warning.

**Root cause.** Copilot Studio interactions are written to UAL under `RecordType=CopilotInteraction` (not `CopilotStudio`, which is not a valid record type). Additionally, `Search-UnifiedAuditLog` without session paging hard-caps at 5,000 rows per call. For any non-trivial export, session paging is required.

**Diagnostic / fix.**

```powershell
# Correct paged query for a Copilot Studio investigation window
$session = [guid]::NewGuid().ToString()
$start = (Get-Date).AddHours(-48)
$end   = Get-Date
$all = @()
do {
    $batch = Search-UnifiedAuditLog -StartDate $start -EndDate $end `
        -RecordType CopilotInteraction `
        -SessionId $session -SessionCommand ReturnLargeSet -ResultSize 5000
    $all += $batch
} while ($batch.Count -ge 5000)
"Retrieved $($all.Count) records under SessionId $session"
$all | Export-Csv -Path "ual-copilot-$session.csv" -NoTypeInformation
```

**Microsoft Learn.**

- `learn.microsoft.com/powershell/module/exchange/search-unifiedauditlog`

**Preserve evidence.** Save the SessionId in the incident folder; it is the identifier the regulator can use to verify the export was complete.

### 6.8 Content moderation level too low for Zone

**Symptom.** A Zone 2/3 agent has content moderation set to **Low**; rate of `RAI:ContentFiltered` events is unusually low for the agent's traffic; user complaints surface inappropriate output.

**Root cause.** Low allows substantial categories of harmful output the policy intends to block. The control's Zone-Specific Requirements table (in the control doc) specifies Medium minimum for Zone 2 and typically High for Zone 3 customer-facing agents.

**Diagnostic.** Inspect the agent's `Settings → Generative AI → Content moderation` page. For RAI telemetry, query the per-agent App Insights resource:

```kusto
// In the per-agent App Insights workspace
customEvents
| where name == "RAI:ContentFiltered"
| where timestamp > ago(30d)
| summarize Filtered = count() by tostring(customDimensions.category), bin(timestamp, 1d)
| order by timestamp desc
```

**Microsoft Learn.**

- `learn.microsoft.com/en-us/microsoft-copilot-studio/knowledge-copilot-studio#content-moderation`
- `learn.microsoft.com/azure/ai-services/content-safety/concepts/harm-categories`

**Fix.** Raise to Medium (Zone 2) or High (Zone 3). Audit the prior 30-day output for what was allowed through; coordinate with Communication Compliance (Control 1.10) to review for policy violations. Document for governance review.

### 6.9 Per-agent App Insights binding missing (RAI telemetry gap)

**Symptom.** KQL for `RAI:ContentFiltered`, `RAI:JailbreakDetected`, or `RAI:GroundingFailed` against a specific agent's App Insights resource returns nothing, even for periods of known agent use.

**Root cause.** Each Copilot Studio agent must be individually bound to an App Insights resource via its connection string. Without binding, RAI events are emitted but not collected. **There is no backfill** — the gap from agent creation to App Insights binding is permanently unrecoverable.

**Diagnostic.** In Copilot Studio → agent → Settings → Advanced → Application Insights, confirm the connection string is present. For a tenant-wide audit, list all agents and their App Insights binding state via the Power Platform admin API (where available); for agents lacking a binding, generate a remediation ticket.

**Microsoft Learn.**

- `learn.microsoft.com/microsoft-copilot-studio/admin-logging-copilot-studio`
- `learn.microsoft.com/en-us/microsoft-copilot-studio/knowledge-copilot-studio#content-moderation`

**Fix.** Bind App Insights immediately. Document the gap window in the agent's design record. If the agent is Zone 2/3 and was active during the gap, raise as a books-and-records issue (FINRA 4511 / SEC 17a-4 implication) and walk the §1.2 reportability tree.

---
## 7. Microsoft Support escalation (L4)

Use this template when escalating to Microsoft Support (Premier or Unified) for a Control 1.8 issue. Microsoft will close cases as "not a Microsoft fault" if the payload does not demonstrate that tenant configuration has been eliminated as a cause.

### 7.1 When to file

File a Microsoft Support case when **all** of the following are true:

1. §6 deep-dives have eliminated configuration causes (toggles, FIC, errorBehavior, content moderation level, App Insights binding, Managed Environments, license).
2. The fault behavior reproduces after a known-good configuration is in place.
3. The fault affects production traffic (not a one-off test) OR a regulated agent (Zone 2/3).
4. CISO or AI Governance Lead has approved the engagement (because Premier/Unified tickets carry a cost and a vendor-disclosure consideration).

Do **not** file a Microsoft case for: a single user complaint with no reproducer; a fault that resolves on retry; a documentation/UI inconsistency; a sovereign-cloud feature-gap question (raise that to your account team, not support).

### 7.2 Required evidence in the case payload

Attach the full §1.3 evidence package, plus:

- **Reproducer.** A minimal test agent and prompt that reproduces the fault, with the expected vs. actual behavior described.
- **Screen recording.** A short recording (≤2 min) of the reproduction in both portals, with timestamps.
- **Tenant ID and environment ID.** Both required.
- **Sovereign cloud explicitly named.** Commercial / GCC / GCC High / DoD.
- **Configuration baseline diff.** A before/after of any recent config changes (last 14 days) that touched any of: AI Agent Protection toggle, Additional Threat Detection, errorBehavior, FIC binding, App Insights binding, content moderation level, Managed Environments, conditional access affecting the M365 Connector service principal.
- **Defender hunting query** that demonstrates the fault — typically a `CloudAppEvents` query showing missing or unexpected events.
- **App Insights query** for the affected agent showing missing or unexpected RAI events.
- **UAL paged export** (`-RecordType CopilotInteraction` with `-SessionId`) for the failure window.

### 7.3 Escalation payload template

Copy this template into the support case description:

```
Subject: Copilot Studio Control 1.8 (Runtime Protection) — <symptom> — Tenant <id>

Tenant ID: <guid>
Environment ID: <guid>
Sovereign cloud: Commercial | GCC | GCC High | DoD
Severity (per FSI Control 1.8 §1.1): SEV-1 | SEV-2 | SEV-3
Regulated workload: yes | no  (Zone <1|2|3>; regulations: <FINRA / SEC / NY DFS / OCC / CFTC>)
Customer-facing: yes | no
Customer NPI exposure analysis (per §1.2 step 1): completed — result <yes/no>

Symptom (one paragraph):
<what the user / monitor sees>

Expected behavior:
<what should happen, with reference to Microsoft Learn URL>

Actual behavior:
<what is observed, with timestamps>

Reproducer:
- Agent: <name / id>
- Prompt: <text or attached file>
- Steps: <1, 2, 3>
- Frequency: <every time | intermittent — N of M>

Configuration confirmed correct (per FSI Control 1.8 §6 troubleshooting):
- [x] PPAC AI Agent Protection toggle ON (screenshot attached)
- [x] Defender XDR AI Agent Protection toggle ON (screenshot attached)
- [x] M365 App Connector status Connected, last-sync <timestamp>
- [x] Managed Environments enabled for environment <id>
- [x] Defender for Cloud Apps preview opt-in completed
- [x] Defender for Cloud Apps license assigned
- [x] errorBehavior = Block for affected agent(s)
- [x] FIC binding validated (subject/issuer/audience match Learn doc for <cloud>)
- [x] Per-agent App Insights connection string present
- [x] Content moderation level confirmed (Lowest|Low|Medium|High|Highest) and matches Zone policy

Recent configuration changes (last 14 days):
- <date> — <change> — <change ticket id>
- <date> — <change> — <change ticket id>

Diagnostic queries (attached as files):
- CloudAppEvents-export.csv  (Defender Advanced Hunting; timeframe <start>–<end>)
- AppInsights-RAI-export.csv (per-agent App Insights; timeframe <start>–<end>)
- UAL-CopilotInteraction-<sessionid>.csv (paged export; <N> rows)
- PowerPlatformAdminActivity-export.csv (Azure Monitor)

Evidence package SHA-256 manifest: attached, signed by <SOC lead>

Compensating control currently in place (if any):
<description; reference §1.4>

Business impact:
<count of affected users / transactions / customer-facing interactions; revenue or supervision implication>

Requested support outcome:
- Confirm whether the symptom is a known platform issue (provide tracking id)
- Provide remediation steps OR a workaround OR an ETA for a service-side fix
- Confirm whether any tenant data needs to be re-evaluated post-fix
```

### 7.4 Expected response and what to do while waiting

Microsoft Support typical first response is per the contracted SLA (Premier: severity-based; Unified: severity-based). While waiting:

- Maintain the compensating control (§1.4).
- Continue to capture evidence on the running incident — every additional reproducer strengthens the case.
- If the incident escalates (severity climbs, NPI exposure surfaces), update the support case AND walk §1.2 again — a previously "internal-only" incident can become reportable.
- Do **not** make additional configuration changes during the support engagement unless explicitly requested by Microsoft — changes obscure the root cause.

---

## 8. Cross-references

### 8.1 Related controls

| Control | Why it matters here |
|---|---|
| [1.5 — Data Loss Prevention (DLP) and Sensitivity Labels](../../../controls/pillar-1-security/1.5-data-loss-prevention-dlp-and-sensitivity-labels.md) | Constrains what data agents can ground against and emit. DLP and labels reduce the attack surface that 1.8 must defend at runtime; sensitivity labels also feed the policy decisions that runtime protection enforces. |
| [1.6 — Microsoft Purview DSPM for AI](../../../controls/pillar-1-security/1.6-microsoft-purview-dspm-for-ai.md) | Posture-management visibility for AI workloads. DSPM-for-AI surfaces drift and risky agent behaviors that may precede a runtime-protection incident. The §1 incident-handling pattern in this playbook mirrors Control 1.6's. |
| [1.7 — Comprehensive Audit Logging and Compliance](../../../controls/pillar-1-security/1.7-comprehensive-audit-logging-and-compliance.md) | Books-and-records source for agent interactions (UAL `CopilotInteraction`). Defender XDR / `CloudAppEvents` are operational telemetry — not WORM. Always cross-reference 1.7 for the recordkeeping side of any 1.8 incident. |
| [1.9 — Data Retention and Deletion Policies](../../../controls/pillar-1-security/1.9-data-retention-and-deletion-policies.md) | Enforces SEC Rule 17a-4 / FINRA 4511 retention on the records that 1.7 captures. A books-and-records gap discovered during a 1.8 investigation usually triggers a 1.9 retention review. |
| [1.10 — Communication Compliance Monitoring](../../../controls/pillar-1-security/1.10-communication-compliance-monitoring.md) | Surfaces policy violations in agent input/output for supervisory review. Runtime protection (1.8) blocks; Communication Compliance (1.10) supervises and routes to a reviewer. Together they help satisfy supervision under FINRA Rule 3110. |
| [1.21 — Adversarial Input Logging](../../../controls/pillar-1-security/1.21-adversarial-input-logging.md) | Captures jailbreak / prompt-injection attempts for forensic review. Companion to 1.8 — runtime protection blocks; 1.21 ensures the attempt is preserved for analysis and trend-detection. |
| [1.24 — Defender AI Security Posture Management](../../../controls/pillar-1-security/1.24-defender-ai-security-posture-management.md) | The AISPM dashboard and posture surface referenced throughout §1.3, §1.5, and §6 of this playbook. 1.24 governs the dashboard configuration; 1.8 governs the runtime enforcement that feeds it. |
| [1.27 — AI Agent Content Moderation Enforcement](../../../controls/pillar-1-security/1.27-ai-agent-content-moderation-enforcement.md) | Governs the **per-prompt** moderation slider (3 positions: Low / Moderate / High) inside the prompt builder for managed GPT models. Complementary to the **agent-level** slider (5 positions: Lowest / Low / Medium / High / Highest) enforced at runtime by 1.8. §6.8 of this playbook references the 1.27 zone-minimum policy where it overlaps. |

### 8.2 Sibling 1.8 playbooks

- [Portal walkthrough](portal-walkthrough.md) — step-by-step UI configuration of the four runtime surfaces.
- [PowerShell setup](powershell-setup.md) — automation for the configuration captured in the portal walkthrough.
- [Verification & testing](verification-testing.md) — proves the runtime protection actually evaluates and blocks; covers test prompts, expected `CloudAppEvents`, and RAI telemetry signatures.

### 8.3 Microsoft Learn anchors used in this playbook

- `learn.microsoft.com/defender-cloud-apps/ai-agent-protection`
- `learn.microsoft.com/defender-cloud-apps/ai-agent-inventory`
- `learn.microsoft.com/defender-cloud-apps/real-time-agent-protection-during-runtime`
- `learn.microsoft.com/microsoft-copilot-studio/external-security-provider`
- `learn.microsoft.com/microsoft-copilot-studio/admin-logging-copilot-studio`
- `learn.microsoft.com/en-us/microsoft-copilot-studio/knowledge-copilot-studio#content-moderation`
- `learn.microsoft.com/microsoft-copilot-studio/requirements-licensing-gcc`
- `learn.microsoft.com/azure/ai-services/content-safety/concepts/harm-categories`
- `learn.microsoft.com/microsoft-365/security/defender/advanced-hunting-cloudappevents-table`
- `learn.microsoft.com/azure/azure-monitor/reference/tables/powerplatformadminactivity`
- `learn.microsoft.com/powershell/module/exchange/search-unifiedauditlog`
- `learn.microsoft.com/en-us/power-platform/guidance/adoption/threat-detection`

### 8.4 Regulatory anchors used in §1

- **NY DFS 23 NYCRR 500.17(a)** — 72-hour cybersecurity-event notification clock from determination.
- **SEC Regulation S-P §248.30(a)(4)** — customer-notification analysis on unauthorized NPI access.
- **FINRA Rule 4530(b)** — written reports of specified events within 30 days.
- **FINRA Rule 3110** — supervision; written supervisory procedures (WSPs) cover AI agents.
- **FINRA Rule 4511** — books-and-records retention applicable to communications produced by agents.
- **FINRA RN 24-09 (June 2024)** — existing rules apply to generative-AI tools; no separate AI rule. (RN 25-07 (April 2025) workplace modernization is contextual only.)
- **SEC Rule 17a-3 / 17a-4** — broker-dealer recordkeeping including WORM preservation.
- **GLBA 501(b)** — safeguards rule; customer-information protection.
- **OCC Bulletin 2026-13 (formerly OCC Bulletin 2011-12) / Federal Reserve SR 26-2 (formerly SR 11-7)** — model risk management for AI/ML.
- **CFTC Regulation 1.31** — recordkeeping for CFTC-regulated activity.

---

*Updated: May 2026 | Version: v1.6.2 | UI Verification Status: Current*
