# Control 1.5 — Troubleshooting: DLP for Microsoft 365 Copilot, Sensitivity Labels, and Power Platform Data Policies

**Control:** [1.5 Data Loss Prevention (DLP) and Sensitivity Labels](../../../controls/pillar-1-security/1.5-data-loss-prevention-dlp-and-sensitivity-labels.md)
**Pillar:** Pillar 1 — Security
**Audience:** Purview Compliance Admin, Purview Info Protection Admin, Power Platform Admin, AI Administrator, Purview Data Security AI Admin, Entra Security Admin, AI Governance Lead, FSI Compliance Officer
**Companion playbooks:**
[Portal walkthrough](./portal-walkthrough.md) ·
[PowerShell setup](./powershell-setup.md) ·
[Verification & testing](./verification-testing.md)

> **Scope.** This playbook covers the two DLP control planes governed by Control 1.5 — (1) **Microsoft Purview DLP** for Microsoft 365 Copilot and Copilot Chat, sensitivity-label enforcement, Endpoint DLP, Network DLP / Edge for Business unmanaged-AI rules, and (2) **Power Platform data policies** for Copilot Studio agents and connector classification. It also covers the cross-cutting evidence dependencies on Purview Audit (Control 1.7), DSPM for AI (Control 1.6), Sensitive Information Types (Control 1.13), and Insider Risk Management / Adaptive Protection (Control 1.12).
>
> Use this playbook when a DLP rule has produced an unexpected allow, an unexpected block, a missing audit row, a sovereign-cloud capability gap, or an examiner observation. For day-2 verification, use [verification-testing.md](./verification-testing.md). For first-time setup, use [portal-walkthrough.md](./portal-walkthrough.md) and [powershell-setup.md](./powershell-setup.md).

---

## Table of Contents

- [§1 FSI Incident Handling — read first](#1-fsi-incident-handling-read-first)
- [§2 Plane decision matrix — DSPM vs Audit vs DLP enforcement](#2-plane-decision-matrix-dspm-vs-audit-vs-dlp-enforcement)
- [§3 Anti-patterns (do not do)](#3-anti-patterns-do-not-do)
- [§4 Symptom-driven scenarios (FSI critical 13)](#4-symptom-driven-scenarios-fsi-critical-13)
  - [Scenario 1 — DLP policy didn't fire on Copilot prompt or response](#scenario-1-dlp-policy-didnt-fire-on-copilot-prompt-or-response)
  - [Scenario 2 — Endpoint DLP not enforcing on macOS device](#scenario-2-endpoint-dlp-not-enforcing-on-macos-device)
  - [Scenario 3 — Unmanaged-AI rule (Edge for Business / Network DLP) not blocking](#scenario-3-unmanaged-ai-rule-edge-for-business-network-dlp-not-blocking)
  - [Scenario 4 — Power Platform connector still allowed in environment despite tenant DLP](#scenario-4-power-platform-connector-still-allowed-in-environment-despite-tenant-dlp)
  - [Scenario 5 — Sensitivity label not applied to SharePoint grounding source — Copilot returned restricted content](#scenario-5-sensitivity-label-not-applied-to-sharepoint-grounding-source-copilot-returned-restricted-content)
  - [Scenario 6 — Adaptive Protection unavailable in GCC / GCC High / DoD](#scenario-6-adaptive-protection-unavailable-in-gcc-gcc-high-dod)
  - [Scenario 7 — DLP override justification not captured in audit](#scenario-7-dlp-override-justification-not-captured-in-audit)
  - [Scenario 8 — EDM detection not matching real customer account numbers](#scenario-8-edm-detection-not-matching-real-customer-account-numbers)
  - [Scenario 9 — DKE-protected file unreadable in Copilot](#scenario-9-dke-protected-file-unreadable-in-copilot)
  - [Scenario 10 — Simulation produced no hits but Turn-it-on caused floods](#scenario-10-simulation-produced-no-hits-but-turn-it-on-caused-floods)
  - [Scenario 11 — Audit shows DLP event but Sentinel didn't ingest](#scenario-11-audit-shows-dlp-event-but-sentinel-didnt-ingest)
  - [Scenario 12 — FSI false-positive flood from a generic SIT](#scenario-12-fsi-false-positive-flood-from-a-generic-sit)
  - [Scenario 13 — DLP coverage gap surfaced during exam](#scenario-13-dlp-coverage-gap-surfaced-during-exam)
- [§5 Sovereign-cloud differences (summary)](#5-sovereign-cloud-differences-summary)
- [§6 Escalation path](#6-escalation-path)
- [§7 Cross-references](#7-cross-references)

---

## §1 FSI Incident Handling — read first

Control 1.5 is the **DLP enforcement plane** for AI-surfaced data flows. A failure here (false-allow, missing location coverage, disabled rule, label not honored) is not a UI nuisance — it is a potential **safeguards failure** under GLBA 501(b), a **books-and-records integrity event** under SEC 17a-4(f) when the underlying record was customer NPI surfaced to an AI surface, and a potential **supervisory-system gap** under FINRA 3110 when DLP was the supervisory control of record. Treat any change to a Copilot DLP rule as an evidence-bearing event; preserve **before** you remediate.

> **Hedging note.** This framework helps meet, and is recommended to support compliance with, the regulations cited below. It does not by itself satisfy any reporting obligation. Implementation requires legal review, and organizations should verify each obligation against current rule text and the firm's Written Supervisory Procedures (WSPs) before relying on the timing or scope guidance here.

### 1.1 Severity matrix

| Severity | Trigger (DLP-specific) | Response window | Escalation |
|---|---|---|---|
| **SEV-1** | Confirmed leak of customer NPI / PII / MNPI through Copilot, Copilot Chat, or a published Copilot Studio agent; rule was off / mis-scoped / never enforced; or a Block-by-label rule failed open on Highly Confidential content | Immediate; bridge within 15 min | CISO + Compliance + Legal + Privacy within 1 h |
| **SEV-2** | False-allow during enforcement window (rule fires in Test, not in Enforce); Copilot location absent from a policy that was supposed to cover it; AU-scoped admin created a Copilot rule that silently never applied; Power Platform DLP regressed allowing a blocked connector | 4 h to first containment | Compliance Admin → AI Governance Lead within 4 h |
| **SEV-3** | False-block disrupting a documented business workflow (overbroad SIT, label-condition mis-scope, citation-link friction); single-user / single-site coverage gap; propagation lag exceeded the documented 4-hour window | 1 business day | Compliance Admin |
| **SEV-4** | Cosmetic policy-tip text drift; UI label naming inconsistency; preview-feature regression that does not affect enforcement | 5 business days | Track in known-issues log |

### 1.2 Reportability decision tree

> Escalation aid only — every external notification decision must be made by Legal and Compliance.

| Trigger | Escalate to | Possible obligation (verify with counsel) |
|---|---|---|
| Customer NPI disclosed via Copilot / agent without enforcement | Privacy + Legal | **GLBA 501(b)** safeguards; **SEC Reg S-P** §248.30(a)(3)–(4) — 30-day customer-notification clock from determination of unauthorized access (post-2024 amendments); 72-hour service-provider written notice |
| Books-and-records gap — DLP audit rows missing for Copilot interactions touching regulated content | Compliance + Legal | **SEC 17a-3 / 17a-4(f)** record integrity; **FINRA 4511** |
| Loss of supervisory visibility on AI-surfaced communications | Compliance | **FINRA Rule 3110** supervisory system; **FINRA Notice 25-07** AI-related supervisory expectations |
| Cybersecurity event materially affecting normal operations | CISO + Legal | **23 NYCRR 500.17** (NYDFS) — 72-hour determination |
| Material cybersecurity incident at SEC registrant | CISO + Legal + Disclosure Committee | **SEC Form 8-K Item 1.05** — 4 business days from materiality determination |
| AI / model-related operational risk event tied to DLP failure | Model Risk + Compliance | **OCC Bulletin 2011-12** / **Fed SR 11-7** model risk management; effective-challenge process |
| Records event for a covered swap / trading activity surfaced through Copilot | Compliance | **CFTC Rule 1.31** recordkeeping |
| Insider misconduct involving deliberate DLP bypass via Copilot | HR + Legal + Compliance | **FINRA Rule 4530** reporting |
| State-resident PII disclosed | Privacy + Legal | State breach-notification statutes (NY GBL 899-aa, MA 201 CMR 17, CCPA/CPRA, SHIELD Act) |
| Third-party AI / connector vendor failure that contributed to the leak | Vendor mgmt + Compliance | **Interagency Guidance on Third-Party Relationships** (OCC / FRB / FDIC, June 2023) — refer Control 2.7 |

### 1.3 Evidence preservation **before** remediation

Capture the following artifacts **before** disabling, editing, or re-scoping the rule. A common audit finding is "the rule was changed before evidence was captured, and the firm cannot reconstruct the failed configuration."

1. Full screenshots of the failing rule — Purview portal: **Solutions → Data Loss Prevention → Policies → [policy] → [rule]** (timestamp visible)
2. PowerShell snapshot from an **IPPS** session (`Connect-IPPSSession`):
   ```powershell
   Get-DlpCompliancePolicy -Identity '<policy>' | ConvertTo-Json -Depth 10 |
       Out-File ".\evidence\1.5\policy_$((Get-Date).ToString('yyyyMMddTHHmmssZ')).json"
   Get-DlpComplianceRule -Policy '<policy>'    | ConvertTo-Json -Depth 10 |
       Out-File ".\evidence\1.5\rules_$((Get-Date).ToString('yyyyMMddTHHmmssZ')).json"
   ```
3. Audit rows for the suspect window — from an **EXO** session (`Connect-ExchangeOnline`), using a **valid** `RecordType` (`ComplianceDLPSharePoint`, `ComplianceDLPExchange`, `DlpEndpoint`, `CopilotInteraction`). `RecordType DLP` is invalid and returns silent zero — see Scenario 11 and §3.
4. Prompt content and response from **DSPM for AI Activity Explorer** (Control 1.6) — content-viewer role required, lawful and in-scope of CommComp / IRM consent
5. User identity (UPN, AAD object ID, manager, business unit, license SKU)
6. UTC timestamps for: rule creation, last edit, enforcement-mode flip, the failing event, and the evidence capture
7. Sensitivity-label state on the affected item — published label list for the user, label applied to the item, container-label inheritance state
8. SIT match details (Control 1.13) — which SIT, what confidence threshold, what minimum count fired
9. Power Platform DLP state if the surface was a Copilot Studio agent — `Get-DlpPolicy`, environment scope, connector classification
10. SHA-256 manifest sidecar covering every artifact above; store in the Control 1.7 evidence bucket with WORM retention

Only after the evidence pack is sealed should the rule be disabled, re-scoped, or moved out of enforcement.

### 1.4 Compensating controls during the gap

Apply one or more while the rule is being repaired. Document in the incident ticket; do not leave the gap open.

- Temporarily **block** (not warn) at the SharePoint site or library level for the affected content ... Control 1.3
- Temporarily elevate **IRM / Adaptive Protection** posture for the affected user population ... Control 1.12 (Commercial only)
- Temporary **external sharing freeze** on the affected SPO sites ... Control 1.3
- Temporary **block on Copilot Studio publish** to non-Microsoft channels (Direct Line custom, Slack, web) for the affected environment ... Controls 2.1, 2.16
- Increase **Communication Compliance** review cadence for affected reviewers ... Control 1.10
- Manually search the Unified Audit Log daily for `CopilotInteraction` events touching the affected SITs / labels ... Control 1.7
- For a Power Platform DLP gap: revoke maker access to the affected environment until the rule is restored

### 1.5 Pre-escalation checklist (≥ 15 items)

1. [ ] Tenant ID and cloud confirmed (Commercial / GCC / GCC High / DoD)
2. [ ] Policy + rule identity captured (`Get-DlpCompliancePolicy`, `Get-DlpComplianceRule` from IPPS)
3. [ ] Mode confirmed — `Enable` vs `TestWithNotifications` vs `TestWithoutNotifications` vs `Disable`
4. [ ] Locations enumerated — `Microsoft 365 Copilot and Copilot Chat` location is present and the policy was built from the **Custom** template (one-click templates omit it)
5. [ ] Confirmed the rule does **not** combine SIT + sensitivity-label conditions in the same rule for the Copilot location (Purview rejects this; if it saved, verify the split)
6. [ ] Sensitivity-label state captured — published-to scope, applied to item vs container only, container-inheritance state
7. [ ] SIT readiness validated (Control 1.13) — SIT exists, pattern matches the test data, confidence and minimum count not over-tight
8. [ ] Audit ingestion verified from an **EXO** session (`Get-AdminAuditLogConfig`) — not from IPPS, which can return a stale value
9. [ ] Audit query used a valid `RecordType` (`ComplianceDLPSharePoint`, `ComplianceDLPExchange`, `DlpEndpoint`, `CopilotInteraction`) — not `DLP`
10. [ ] Propagation window honored — ≥ 4 hours since the last rule save (Microsoft-documented for the Copilot location)
11. [ ] Administrative-unit scope ruled out — the Copilot DLP location does not support AUs; an AU-scoped admin's rule silently never applies
12. [ ] Power Platform DLP state captured for any Copilot Studio surface (`Get-DlpPolicy`, environment scope, connector classification)
13. [ ] Sovereign-cloud parity verified — Adaptive Protection, IRM, and some Copilot DLP previews are not at parity in GCC / GCC High / DoD
14. [ ] Endpoint DLP device-onboarding state verified for any Endpoint surface (Defender for Endpoint or standalone Purview onboarding)
15. [ ] Last known-good evidence pack timestamp (Control 1.7) recorded
16. [ ] Compliance + Legal notified per severity matrix; Privacy notified for any NPI-touching SEV-1 / SEV-2

---

## §2 Plane decision matrix — DSPM vs Audit vs DLP enforcement

Control 1.5 owns the **DLP enforcement plane**. The other two columns reference Control 1.6 (DSPM for AI — detection plane) and Control 1.7 (Audit — evidence plane). Pick the right tool for the question; the wrong tool returns a misleading answer.

| Question | DSPM for AI (Control 1.6) | Purview Audit (Control 1.7) | **DLP enforcement (Control 1.5)** |
|---|---|---|---|
| What sensitive content was *processed* by Copilot recently? | ✅ Activity Explorer with content viewer role | ⚠️ Partial via `CopilotInteraction.AuditData.CopilotEventData` | ❌ DLP only logs *matches against rules* |
| Did my DLP rule actually fire / block / warn? | ❌ | ⚠️ Audit row exists, but no rule-evaluation detail | ✅ DLP Alerts dashboard + `Get-DlpDetailReport` + audit `ComplianceDLP*` rows |
| Long-horizon (> 180 d) books-and-records evidence | ❌ (≈30-day UI window, not WORM) | ✅ Audit Premium + retention policy | ⚠️ DLP alerts retention is shorter than Audit Premium; export to evidence store |
| Per-prompt risk / category / topic | ✅ DSPM categories | ⚠️ Limited fields | ❌ |
| Per-rule false-positive / false-negative rate over time | ❌ | ⚠️ Manual via audit query | ✅ DLP Alerts + Activity Explorer (DLP) tuning loop |
| Did a Power Platform connector get blocked at design time? | ❌ | ⚠️ Power Platform admin activity | ✅ Power Platform data-policy enforcement + PPAC analytics |
| Did Copilot bypass DLP because the file was uploaded directly into the prompt? | ✅ Visible as interaction | ✅ `CopilotInteraction` row exists | ❌ Direct uploads to a Copilot prompt are **not scanned** by the Copilot DLP location — known limitation |

> Rule of thumb: **DSPM tells you what happened. Audit proves it. DLP changes what happens next.**

---

## §3 Anti-patterns (do not do)

| Anti-pattern | Why it is wrong | What to do instead |
|---|---|---|
| Disabling a rule to "fix" a false positive without a documented compensating control | Leaves the regulated surface unprotected; auditor cannot reconstruct the gap | Apply a §1.4 compensating control; document in the incident ticket; preserve evidence first |
| Building the Copilot DLP rule from the **Standard** template (or any one-click template) | The `Microsoft 365 Copilot and Copilot Chat` location is exposed **only on a Custom policy** | Always use the **Custom** template; verify the location checkbox before saving |
| Combining a SIT condition and a sensitivity-label condition in the **same rule** for the Copilot location | Purview UI rejects the save; if it persisted via PowerShell the behavior is unsupported | **Split** into Rule A (SITs) and Rule B (label) within the same policy |
| Treating a **container** label (site / Team / group) as if it were a **file** label | DLP rules that test "content has label X" evaluate the label on the **item**, not the container | Apply file labels via auto-labeling or manual labeling; verify item label, not container |
| Querying audit with `Search-UnifiedAuditLog -RecordType DLP` | `DLP` is not a valid `RecordType` and returns zero rows silently | Use `ComplianceDLPSharePoint`, `ComplianceDLPExchange`, `DlpEndpoint`, or `CopilotInteraction` |
| Reading a Power Platform connector classification from the API as if it were a UI label without normalization | API returns `confidential` / `general` / `blocked`; UI shows Business / Non-Business / Blocked | Normalize via the documented mapping; assert on the API value |
| Writing an auto-labeling policy that targets "AI interactions" as a location | No such location exists for auto-labeling | Auto-label the underlying SPO / OneDrive / Exchange items; let the Copilot DLP rule act on the labeled items |
| Validating a new Copilot DLP rule by testing immediately after save | Documented propagation is **up to 4 hours** | Wait the documented window; record the rule-save UTC timestamp |
| Scoping a Copilot DLP rule to a Restricted Administrative Unit | Copilot DLP location does not support AUs — the rule silently never applies | Author with a tenant-scoped Compliance Admin |
| Assuming **Adaptive Protection** is at parity in GCC / GCC High / DoD | IRM is not available in any US Government cloud per Microsoft Learn | Document the sovereign-cloud exception; use static role-based DLP — see Scenario 6 |
| Trusting the citation list as evidence the file was "blocked" | The Prevent-Copilot-from-processing-content action stops summarization, but the item still appears in citations with a click-through link | Combine with site / library access controls (Control 1.3); do not rely on the DLP action alone |
| Using `Get-AdminAuditLogConfig` from `Connect-IPPSSession` to verify audit ingestion | IPPS can return a cached / stale value | Always run from `Connect-ExchangeOnline` |

---

## §4 Symptom-driven scenarios (FSI critical 13)

> Format: **Symptom → Likely cause → Diagnostic (PowerShell + portal path) → Resolution → What good looks like (exit criteria)**.
>
> All snippets below assume connection helpers from [`powershell-setup.md`](./powershell-setup.md) — specifically `Connect-Purview-IPPS`, `Connect-Purview-EXO`, `Connect-PowerPlatform`, and `Get-EvidenceStamp`. Do not redefine them inline. Sovereign-cloud parameters are in the baseline at [`docs/playbooks/_shared/powershell-baseline.md`](../../_shared/powershell-baseline.md).

---

### Scenario 1 — DLP policy didn't fire on Copilot prompt or response

A user pasted (or Copilot summarized) regulated content; an audit row exists for the interaction but no DLP match. The rule appears correctly authored.

**Likely causes**

1. Policy was built from a one-click / Standard template and the **Microsoft 365 Copilot and Copilot Chat** location was never added.
2. The triggering rule references a label or SIT that is not actually applied on the source item.
3. The policy is in `TestWithoutNotifications` / `TestWithNotifications` ("Test / Simulation"), not `Enable` ("Turn it on").
4. Less than ~4 hours have elapsed since the last rule save (Microsoft Learn documents propagation as **up to 4 hours** for the Copilot location).
5. Author was a Restricted-Administrative-Unit-scoped admin (the Copilot location does not support AUs; the rule silently never applies).
6. Audit query used an invalid `RecordType` and the rule did fire — see Scenario 11.

**Diagnostic — PowerShell**

```powershell
Connect-Purview-IPPS                                      # helper from powershell-setup.md
$pol  = Get-DlpCompliancePolicy -Identity '<policy>'
$rule = Get-DlpComplianceRule  -Policy   '<policy>'

# (a) Custom template + Copilot location present?
$pol  | Select-Object Name, Mode, Workload, CreatedBy,
                     @{N='HasCopilotLocation';E={ $_.Workload -match 'Copilot' }}

# (b) Rule mode flip — when was the policy last saved / enabled?
$pol  | Select-Object Name, Mode, WhenChangedUTC, LastModifiedTime

# (c) Conditions — SIT and label must be in *separate* rules
$rule | Select-Object Name, Disabled, Priority,
                     ContentContainsSensitiveInformation, ContentMatchesLabel,
                     BlockAccess, NotifyUser

# (d) Author identity — Restricted-AU admin?
Get-RoleGroupMember -Identity 'Compliance Administrator' |
    Where-Object Name -eq $pol.CreatedBy
```

**Diagnostic — portal**

- Purview → **Solutions → Data Loss Prevention → Policies → [policy] → Edit policy → Locations** — confirm `Microsoft 365 Copilot and Copilot Chat` is checked.
- Same wizard → **Policy mode** — confirm "Turn it on" (not "Run in simulation mode" or "Keep it off").
- Purview → **DLP → Alerts** — filter by policy name and the failing UTC window.
- Purview → **Audit** → search `ComplianceDLPSharePoint`, `ComplianceDLPExchange`, or `CopilotInteraction` for the test event.

**Resolution**

- If the location is missing, recreate the policy from the **Custom** template and re-add the location. Standard / one-click templates do not surface the Copilot location ([Learn — DLP for Microsoft 365 Copilot location](https://learn.microsoft.com/en-us/purview/dlp-microsoft365-copilot-location-learn-about)).
- If the SIT/label is not applied on the source, fix the upstream labeling (Scenario 5) or tune the SIT (Scenario 12).
- If still in Test mode, advance through **TestWithNotifications → Enable** and wait the propagation window before testing.
- If authored by an AU-scoped admin, re-author with a tenant-scoped Compliance Admin.

**What good looks like**

- `Get-DlpCompliancePolicy` returns `Mode = Enable` and the workload string contains the Copilot location.
- A deterministic activation test (named test user, known prompt, UTC-stamped, run **after** T+4h from the last save) produces a `ComplianceDLPSharePoint` / `CopilotInteraction` audit row with `PolicyMatched = true` and the expected rule name.
- Verification evidence is sealed per Control 1.7 with a SHA-256 manifest.

... see Verification Criterion 6 of the Control 1.5 doc for the exit gate.

---

### Scenario 2 — Endpoint DLP not enforcing on macOS device

An Endpoint DLP rule for clipboard, print, or upload-to-cloud is enforcing on Windows 10/11 but a macOS endpoint shows no enforcement.

**Likely causes**

1. The macOS device is not onboarded to Microsoft Defender for Endpoint (or to standalone Purview onboarding).
2. The macOS version is older than the **last 3** Microsoft-supported releases.
3. The user is not in scope of the policy (group membership, license).
4. macOS-specific feature parity gap — clipboard / print, browser support, and a subset of restricted-app behavior do not match Windows.

**Diagnostic — PowerShell**

```powershell
Connect-MgGraph -Scopes 'DeviceManagementManagedDevices.Read.All','User.Read.All'

# (a) Onboarding state via Defender / Intune
Get-MgDeviceManagementManagedDevice -Filter "operatingSystem eq 'macOS'" |
    Select-Object DeviceName, OSVersion, ComplianceState, LastSyncDateTime, UserPrincipalName

# (b) User in scope?
Connect-Purview-IPPS
$rule = Get-DlpComplianceRule -Policy '<endpoint-policy>'
$rule | Select-Object Name, IncludedUserGroups, ExcludedUserGroups

# (c) Endpoint-DLP licensing on the user
Get-MgUserLicenseDetail -UserId '<upn>' |
    Select-Object SkuPartNumber, ServicePlans
```

**Diagnostic — portal**

- Microsoft Defender → **Assets → Devices** — confirm the macOS device shows **Onboarded** and a recent **Last seen**.
- Purview → **DLP → Endpoint DLP settings → Devices** — confirm device count and platform breakdown include macOS.
- Purview → DLP policy → **Locations → Devices** — confirm the location is checked and includes macOS-supported actions.

**Resolution**

- Onboard via Intune macOS configuration profile or DfE auto-onboarding script.
- Upgrade the device to one of the last 3 Microsoft-supported macOS versions; document the supported-version policy in the firm's mobile-device standard.
- Add the user to the policy scope group and re-test after the 4-hour propagation window.
- Where macOS parity is missing for a specific action (e.g., a particular browser block), document the gap in Written Supervisory Procedures and apply a compensating control (Conditional Access app control, MDE attack surface reduction, or restricted browser deployment).

**What good looks like**

- The macOS device is **Onboarded** in Defender, in scope of the policy, and on a supported OS version.
- A deterministic clipboard / upload test on the macOS endpoint produces a `DlpEndpoint` audit row with `Platform = macOS` and the expected rule.
- Any documented parity gap is recorded in WSPs with a named compensating control.

... see Control 1.5 §"Endpoint DLP — Win 10/11, Win Server 2019/2022, last 3 macOS versions".

---

### Scenario 3 — Unmanaged-AI rule (Edge for Business / Network DLP) not blocking

A rule intended to block paste-into-ChatGPT / Gemini / DeepSeek / consumer-Copilot does not enforce when the user navigates to the unmanaged AI site.

**Likely causes**

1. The user is signed into Edge with a personal account, not **Edge for Business**.
2. The preview-feature enablement flag for Network DLP / unmanaged-AI is not turned on at the tenant level.
3. The rule scope does not include the relevant unmanaged-AI category or domain.
4. Web-content-collection (browser-side telemetry) is not configured, so the rule has nothing to evaluate.

**Diagnostic — portal**

- Purview → **Settings → Endpoint DLP settings → Browser and domain restrictions to sensitive data** — confirm the unmanaged-AI category is enabled and the target domains appear.
- Purview → **DLP → Policies → [policy] → Locations → Devices → Network and web activities** — confirm the rule includes the relevant browser activity.
- Edge → `edge://management` on the endpoint — confirm the profile shows **Managed by your organization** and is signed in with the corporate account.
- Purview → **DSPM for AI → Activity Explorer** (Control 1.6) — filter by **Unmanaged AI app** to confirm the platform is collecting events at all.

**Diagnostic — PowerShell**

```powershell
Connect-Purview-IPPS
Get-PolicyConfig | Select-Object EndpointDlpBrowserRestrictionList,
                                  EndpointDlpUnallowedBrowsers,
                                  WebContentCollectionEnabled
```

**Resolution**

- Force Edge for Business sign-in via Conditional Access (require compliant device + corporate identity for AI domains).
- Enable the unmanaged-AI / Network DLP preview flag at the tenant level (verify against Microsoft Learn and Message Center; preview features can change without notice).
- Add the missing domains or categories to the rule scope.
- Enable **Web content collection** for the in-scope device groups so the rule has telemetry to act on.
- Wait the 4-hour propagation window and re-test with a non-corporate-data string first to validate the path before testing with sensitive data.

**What good looks like**

- A test paste of a benign canary string into the unmanaged-AI site is blocked (or warned) and produces a `DlpEndpoint` audit row with `BrowserName = Edge` and the unmanaged-AI category.
- The DSPM for AI Activity Explorer shows the same event under **Unmanaged AI app**.

... see Control 1.5 §"Edge for Business — unmanaged AI (preview)" and Control 1.6 detection plane.

---

### Scenario 4 — Power Platform connector still allowed in environment despite tenant DLP

A tenant-level Power Platform data policy classifies the **HTTP Webhook** connector as `Blocked`, but a maker in a specific environment is still able to add it to a Copilot Studio agent.

**Likely causes**

1. **Tenant vs environment DLP precedence** — environment-scope policies and tenant policies stack; an environment-scope policy with `Business / Non-Business` classification can still allow the connector if no policy actually places it in `Blocked` for that environment.
2. The tenant policy uses `All environments except…` and the affected environment is in the `except` list.
3. The environment is a **managed environment** with a separate policy that overrides the tenant default.
4. The default-environment behavior — `Add-PowerAppsAccount`-scoped policies and the Default environment have specific override rules; verify against [Power Platform DLP precedence](https://learn.microsoft.com/en-us/power-platform/admin/wp-data-loss-prevention).

**Diagnostic — PowerShell**

```powershell
Connect-PowerPlatform                                # PS 5.1 helper from powershell-setup.md

# (a) All policies and their environment scope
Get-DlpPolicy | Select-Object DisplayName, EnvironmentType, CreatedTime,
                              @{N='Envs';E={($_.Environments.name) -join ','}}

# (b) Connector classification per policy
foreach ($p in Get-DlpPolicy) {
    $p.ConnectorGroups | ForEach-Object {
        [pscustomobject]@{
            Policy        = $p.DisplayName
            Classification= $_.classification          # confidential|general|blocked
            Connectors    = ($_.connectors.name) -join ','
        }
    }
}
```

**Diagnostic — portal**

- PPAC → **Policies → Data policies** — list every policy that targets the affected environment; note `Environments`, `Type`, and `Last modified`.
- For each policy → **Connectors** tab — confirm where `HTTP Webhook` is classified.
- PPAC → **Environments → [env] → Settings → Features** — confirm whether the environment is a Managed Environment.

**Resolution**

- Move the `HTTP Webhook` connector to **Blocked** in **every** policy that targets the affected environment.
- Replace `All environments except…` patterns with explicit environment lists in Zone 3 — see Control 2.1.
- For Managed Environments, configure the environment-scope policy explicitly; do not rely on tenant defaults.
- Re-test maker experience: in Copilot Studio in the affected environment, attempt to add `HTTP Webhook` and confirm the connector is greyed out with the policy name shown.

**What good looks like**

- `Get-DlpPolicy` shows `HTTP Webhook` as `blocked` in every policy whose environment scope includes the affected environment.
- A Copilot Studio maker test in that environment cannot add the connector and the UI surfaces the blocking policy name.
- Power Platform admin-activity audit shows the policy-evaluation event referencing the blocking policy.

... see Control 2.1 — Copilot Studio governance and connector classification precedence.

---

### Scenario 5 — Sensitivity label not applied to SharePoint grounding source — Copilot returned restricted content

A Highly Confidential document was returned (or summarized) by Copilot. Investigation shows the file in SharePoint had **no file-level label** even though the site / Team has a container label.

**Likely causes**

1. **Label scope mismatch** — the label is published with scope **Groups & sites** but not **Files & emails**, so it can be applied to the container but not to the file.
2. Auto-labeling not configured for the SPO location, or the auto-labeling policy is in **Simulation** mode.
3. Container-label inheritance does not propagate the label to files; container labels govern container settings (privacy, sharing, device access), not item content.
4. Copilot respects file labels and label-encryption (IRM) inheritance — without a file label, the block-by-label DLP rule has nothing to match.
5. The file pre-dates the label policy and was never re-labeled.
6. The IRM scope on the label excludes the user's group, so encryption is not enforced even where the label is present.

**Diagnostic — PowerShell**

```powershell
Connect-Purview-IPPS

# (a) Label scope — Files/Email vs Sites/Groups
Get-Label | Select-Object DisplayName, ContentType, IsValid,
                          @{N='Scope';E={ $_.LabelActions.Name -join ',' }}

# (b) Label policies and their published-to scope
Get-LabelPolicy | Select-Object Name, Mode, Labels, ScopedLabels,
                                ModernGroupLocation, SharePointLocation

# (c) Auto-labeling policies and mode
Get-AutoSensitivityLabelPolicy | Select-Object Name, Mode, ApplySensitivityLabel,
                                               SharePointLocation, OneDriveLocation,
                                               ExchangeLocation
```

**Diagnostic — portal**

- Purview → **Information Protection → Labels → [label] → Edit → Scope** — confirm both **Files & emails** and **Groups & sites** are checked if both are needed.
- Purview → **Information Protection → Auto-labeling** — confirm at least one policy targets the SPO site and is in `Enable` (not `TestWithoutNotifications`).
- SharePoint → **Site contents → [file] → Sensitivity** column — confirm the file label.

**Resolution**

- Republish the label with **Files & emails** scope; allow client propagation (up to 24 h).
- Move the auto-labeling policy from Simulation to Enable after the propagation window.
- Backfill labels on pre-existing files via auto-labeling on existing items (one-time scan) or manual labeling.
- Where IRM (encryption) is required, configure the label's **Encryption** action and verify the user's group is in scope.
- Document **Reg S-P implications and notification clocks** — if customer NPI was returned to Copilot through this path, escalate to Privacy + Legal under the §1.2 decision tree (30-day customer notification clock from determination of unauthorized access; refer Control 3.4).

**What good looks like**

- The affected file shows the expected sensitivity label in SPO (`File → Sensitivity` column).
- A Copilot prompt that previously returned the content now returns "Some content was withheld due to organizational policy" (or equivalent) and a `ComplianceDLPSharePoint` audit row records the block.
- Auto-labeling coverage report shows the SPO site at ≥ 95% labeled.
- Reg S-P notification analysis is complete and recorded in the incident ticket regardless of outcome.

... see Control 3.4 — Incident reporting and Reg S-P 2024 notification clocks.

---

### Scenario 6 — Adaptive Protection unavailable in GCC / GCC High / DoD

A DLP rule conditioned on Adaptive Protection risk tier (low / moderate / elevated) does nothing in a US Government cloud tenant.

**This is not a defect.** Microsoft Learn documents that **Insider Risk Management is not available in any US Government cloud (GCC, GCC High, or DoD)** ([Adaptive Protection in Microsoft Purview](https://learn.microsoft.com/en-us/purview/insider-risk-management-adaptive-protection)). Adaptive Protection depends on IRM; therefore the dependency cannot be satisfied in those clouds.

**Diagnostic — PowerShell**

```powershell
Connect-Purview-IPPS

# Confirm cloud + IRM cmdlet absence
$env:USERDOMAIN
(Get-OrganizationConfig).Identity                   # tenant identity hint
Get-Command Get-InsiderRiskPolicy -ErrorAction SilentlyContinue   # null in US Gov clouds

# Confirm the DLP rule references the IRM-derived condition
$rule = Get-DlpComplianceRule -Policy '<policy>'
$rule | Where-Object { $_.RawContent -match 'AdaptiveProtection|InsiderRisk' } |
        Select-Object Name, RawContent
```

**Diagnostic — portal**

- Purview → **Insider Risk Management** — in a US Government tenant, this solution does not appear in the left navigation (or is greyed out).

**Resolution (compensating control)**

- Use **static, role-based DLP** in GCC / GCC High / DoD: scope by group membership (e.g., front-office, M&A, research), by Azure AD role, by sensitivity label, and by SIT — not by risk tier.
- Document the parity gap in Written Supervisory Procedures **and** in the firm's deviation register, citing the Microsoft Learn link above.
- Increase **Communication Compliance** review cadence (Control 1.10) for high-risk populations as a behavioral compensating layer.
- Re-check on each Microsoft Learn refresh; if Microsoft adds IRM to the relevant cloud, schedule a review.

**What good looks like**

- All DLP rules in the US Gov tenant use static conditions only (no `AdaptiveProtection*` references).
- The deviation register entry cites the Microsoft Learn parity statement and lists the named compensating control (static DLP + elevated CommComp cadence).
- The WSP section on AI supervision references the deviation register entry.

... see Control 1.5 §"Sovereign Cloud Availability" and the deviation register pattern from Control 2.6.

---

### Scenario 7 — DLP override justification not captured in audit

A user clicked "Override" on a DLP policy tip but the audit row contains no justification text, breaking the supervisory-review chain.

**Likely causes**

1. The rule was authored with `NotifyAllowOverride 'WithoutJustification'` (or override was not enabled).
2. Audit logging is not at Purview Audit **Standard** / **Premium** for the relevant `RecordType`.
3. Forwarding to Sentinel is mis-scoped and the row exists in Audit but not in Sentinel — see Scenario 11.

**Diagnostic — PowerShell**

```powershell
Connect-Purview-IPPS

Get-DlpComplianceRule -Policy '<policy>' |
    Select-Object Name,
                  NotifyUser, NotifyAllowOverride,
                  @{N='OverrideRequiresJustification';E={
                       $_.NotifyAllowOverride -contains 'WithJustification' }},
                  IncidentReportContent

# Confirm audit ingestion (run from EXO, not IPPS)
Connect-Purview-EXO
Get-AdminAuditLogConfig | Select-Object UnifiedAuditLogIngestionEnabled,
                                        AdminAuditLogEnabled
```

**Diagnostic — portal**

- Purview → DLP → policy → rule → **User notifications → Allow overrides** — confirm `Require a business justification to override` is checked.
- Purview → **Audit** — search for `ComplianceDLPSharePoint` / `ComplianceDLPExchange` in the suspect window; expand the event JSON and locate `UserJustification` / `OverrideReasons`.

**Resolution**

- Update the rule: `Set-DlpComplianceRule -Identity '<rule>' -NotifyAllowOverride 'WithJustification'`. Re-save and wait the propagation window.
- Confirm `UnifiedAuditLogIngestionEnabled = True` from an **EXO** session (IPPS can return a stale value — see §3 anti-pattern).
- Confirm the Sentinel Office 365 connector includes the relevant workload — refer Control 3.9.

**What good looks like**

- `Get-DlpComplianceRule` shows `NotifyAllowOverride` containing `WithJustification`.
- A test override produces an audit event with non-empty `UserJustification`.
- The same event appears in Sentinel within the connector's documented latency window.

... see Control 3.9 — Sentinel forwarding and analytics.

---

### Scenario 8 — EDM detection not matching real customer account numbers

An Exact Data Match (EDM) SIT built from the firm's customer-master file is not matching real account numbers in test prompts.

**Likely causes**

1. **Schema mismatch** — the EDM schema column names or order differ from the uploaded CSV.
2. **Data refresh cadence** — the sensitive-data-store upload completed, but indexing has not finished, or the upload is stale relative to the test data.
3. Sensitive-data-store upload errors (silent partial uploads).
4. **Case sensitivity** — the EDM schema is configured case-sensitive but the test data differs in casing.
5. **Field type** — numeric vs string mismatch in the schema.
6. The SIT lacks a proximity dictionary, and the test prompt does not include a corroborating keyword to meet the configured confidence floor.

**Diagnostic — PowerShell**

```powershell
Connect-Purview-IPPS

# (a) EDM schema and data store state
Get-DlpEdmSchema    | Select-Object Name, State, CreationTime, LastModifiedTime
Get-DlpSensitiveInformationTypeRulePackage |
    Where-Object { $_.Name -match 'EDM' } |
    Select-Object Name, Identity, LastModifiedTime

# (b) Confidence threshold and minimum count on the EDM SIT reference
$rule = Get-DlpComplianceRule -Policy '<policy>'
$rule | Select-Object Name, ContentContainsSensitiveInformation
```

**Diagnostic — portal**

- Purview → **Data classification → Exact data matches → [schema]** — confirm `State = Indexed` and `Last refreshed` is recent.
- Purview → **Data classification → Sensitive info types → [EDM SIT]** — verify the SIT references the indexed store.
- Use **Test** (Purview → Data classification → Sensitive info types → Test) with a known-good account number from the source file.

**Resolution**

- Re-upload the sensitive data store, verifying the schema column order and casing match the CSV header exactly. Wait for indexing to complete before testing.
- Where false negatives persist, lower the confidence threshold incrementally **only** with documented evidence that false-positive rate stays acceptable.
- Add a proximity dictionary (e.g., "Account", "Acct #", "Customer ID") to lift confidence when the surrounding context is present.
- Where the schema cannot be fixed quickly, fall back to a regex SIT with high specificity as an interim and record the gap in WSPs.

**What good looks like**

- Purview EDM portal shows `State = Indexed` and a `Last refreshed` timestamp inside the agreed refresh SLA.
- The Purview SIT **Test** view returns a hit on a known-good account number from the source file.
- A controlled DLP test prompt produces a `ComplianceDLP*` audit row referencing the EDM SIT with the expected confidence value.

... see Control 1.13 — Sensitive Information Types and pattern recognition.

---

### Scenario 9 — DKE-protected file unreadable in Copilot

Copilot returns "I couldn't access this content" or omits a Double Key Encryption (DKE)-protected file from grounding even though the user has access in SPO.

**This is expected behavior.** DKE applies a customer-held second key in addition to the Microsoft-managed key; **Microsoft (and therefore Copilot) cannot decrypt the content.** The trade-off is intentional.

**Diagnostic**

- Confirm the file's label uses the **Double Key Encryption** action (not standard Microsoft-managed encryption) — Purview → Information Protection → **Labels → [label] → Encryption**.
- Confirm the user can open the file in Office desktop while connected to the DKE service.
- Confirm Copilot's behavior is consistent across users and prompts; intermittent access points to a different cause (label scope, sharing, conditional access).

**Resolution / decision framework**

- DKE is a **deliberate** trade-off: it provides the strongest customer-controlled confidentiality but blocks every cloud service (Copilot, eDiscovery, server-side auto-labeling, server-side DLP scanning).
- Before applying DKE to a content set, document the trade-off against:
  - **NYDFS 23 NYCRR 500.15** encryption-of-NPI expectations (DKE meets the spirit but at the cost of cloud productivity)
  - State regulator expectations (e.g., where the regulator expects the firm to be able to retrieve and produce records)
  - **SEC Rule 17a-4(f)** — DKE-encrypted records must still be reproducible to the SEC; verify your DKE deployment supports controlled decryption-for-production
- Where Copilot productivity is required on the same content set, use **standard Microsoft-managed encryption** with sensitivity labels; reserve DKE for the highest-sensitivity tier (board materials, M&A deal rooms) and accept that those tiers are not Copilot-eligible.

**What good looks like**

- DKE deployment scope, decryption-for-production runbook, and Copilot-incompatibility statement are documented in Control 1.15 evidence.
- The firm's WSPs explicitly identify which content tiers are DKE-protected and therefore not Copilot-eligible.
- No DLP incident is opened for "Copilot couldn't read DKE content" — it is logged as expected behavior.

... see Control 1.15 — Encryption key custody and DKE.

---

### Scenario 10 — Simulation produced no hits but Turn-it-on caused floods

A new policy was run in `TestWithoutNotifications` for two weeks with zero hits; on flipping to `Enable` it produced thousands of matches in the first hour.

**Likely causes**

1. Simulation did not cover all locations / scopes — for example, simulated SPO only, then enforced added Exchange + Endpoint.
2. SIT confidence-level threshold was set higher in the simulation rule and lowered for enforcement.
3. **Trainable-classifier training drift** — the classifier was retrained between simulation and enforcement and now matches more broadly.
4. The user / group scope expanded between simulation and enforcement.
5. Simulation results were not actually reviewed — the count was zero because no hits made it past an upstream allow rule.

**Diagnostic — PowerShell**

```powershell
Connect-Purview-IPPS

# (a) Compare current rule to the simulation snapshot (kept in evidence per §1.3)
$current = Get-DlpComplianceRule -Policy '<policy>'
$snapshot = Get-Content '.\evidence\1.5\rules_<sim-timestamp>.json' | ConvertFrom-Json

Compare-Object $current $snapshot -Property Name, Disabled, Priority,
              ContentContainsSensitiveInformation, ContentMatchesLabel,
              IncludedUserGroups, ExcludedUserGroups, BlockAccess

# (b) DLP detail report for the first hour of enforcement
Get-DlpDetailReport -StartDate (Get-Date).AddHours(-1) -EndDate (Get-Date) |
    Group-Object Action, RuleName | Sort-Object Count -Descending
```

**Diagnostic — portal**

- Purview → **DLP → Reports → DLP policy matches** — compare the simulation window vs the enforcement window.
- Purview → **Trainable classifiers → [classifier] → Versions** — confirm whether the classifier was retrained between the two windows.

**Resolution**

- Always re-run simulation **after** any rule change (location, condition, classifier version) and **before** advancing to enforcement.
- Use **incremental enablement**: enforce on a pilot group first (1–5% of users), monitor for 72 hours, then expand in 10–25% rings.
- Pin classifier versions where possible; record the version in the rule's evidence pack.
- Document the simulation-to-enforcement comparison method as a standing pre-flight check in the change record.

**What good looks like**

- A diff between simulation snapshot and enforcement-time rule shows zero unintended changes.
- The pilot ring produces a hit volume within 1–2× the simulation projection; a flood (≥ 10×) blocks promotion to the next ring.
- The change ticket attaches both snapshots and the diff.

... see Control 2.3 — Change management and release planning.

---

### Scenario 11 — Audit shows DLP event but Sentinel didn't ingest

A `ComplianceDLPSharePoint` event is visible in the Purview Audit search but the corresponding Sentinel analytics rule never fired.

**Likely causes**

1. The Sentinel **Office 365** connector scope does not include the relevant workload (SharePoint / Exchange / Teams) or does not include `Audit.General`, where some DLP records land.
2. **UEBA mapping** — UEBA enrichment expects fields that the DLP record schema does not populate; the analytics rule's `where` clause filters the event out.
3. The analytics rule conditions reference a `RecordType` enum value that does not match the ingested string (case, hyphenation).
4. Latency — the connector ingestion latency window was shorter than the test interval. Verify against the connector's documented SLA.

**Diagnostic — KQL (Sentinel)**

```kql
OfficeActivity
| where TimeGenerated between (ago(2h) .. now())
| where RecordType in ("ComplianceDLPSharePoint","ComplianceDLPExchange","DlpEndpoint")
| summarize count() by RecordType, Operation, bin(TimeGenerated, 5m)
```

If the query returns zero with rows present in Purview Audit, the gap is at the connector. If it returns rows but the analytics rule did not trigger, the gap is in the rule logic.

**Diagnostic — Sentinel portal**

- Sentinel → **Data connectors → Office 365** — confirm the connector status is **Connected** and SharePoint / Exchange / Teams are toggled on.
- Sentinel → **Analytics → [rule] → Edit → Query** — re-run the query in the Logs blade against the test event window.

**Resolution**

- Add the missing workload to the Office 365 connector and wait the documented backfill window (typically minutes to hours; verify against Microsoft Learn for the current SLA).
- Adjust the analytics rule to match the actual `RecordType` string emitted by the connector.
- Where UEBA enrichment is required, confirm the upstream identity records are also being ingested.
- Validate end-to-end with a controlled test event and document the latency.

**What good looks like**

- A controlled DLP test event appears in `OfficeActivity` within the connector's documented latency window.
- The analytics rule fires on the test event and produces an incident with the expected severity and entities.
- The end-to-end latency (Purview Audit → Sentinel → incident) is recorded in the connector's runbook.

... see Control 3.9 — Sentinel forwarding, analytics, and SOAR.

---

### Scenario 12 — FSI false-positive flood from a generic SIT

A rule using the built-in **U.S. Bank Account Number** SIT (or another generic 9-digit numeric SIT) is producing thousands of false positives on internal documents containing order numbers, ticket numbers, or part numbers.

**Likely causes**

1. The built-in SIT uses a permissive regex with low confidence; without a proximity dictionary it matches any 9-digit run.
2. The confidence threshold on the rule is set too low.
3. The SIT lacks a corroborating keyword list relevant to the firm's actual data (e.g., "account", "acct #", "customer", "routing").

**Diagnostic — PowerShell**

```powershell
Connect-Purview-IPPS

$rule = Get-DlpComplianceRule -Policy '<policy>'
$rule | Select-Object Name,
       @{N='SITs';E={ ($_.ContentContainsSensitiveInformation | ConvertTo-Json -Compress) }}

# (b) Top false-positive sources from DLP detail report
Get-DlpDetailReport -StartDate (Get-Date).AddDays(-7) -EndDate (Get-Date) |
    Where-Object { $_.RuleName -eq '<rule>' } |
    Group-Object Source, Title | Sort-Object Count -Descending | Select-Object -First 25
```

**Resolution**

- Replace the generic SIT with an **EDM SIT** built from the firm's real customer-account list (Scenario 8 covers EDM mechanics; refer Control 1.13).
- Raise the confidence threshold on the existing SIT (e.g., from `Low` to `High`) and require a corroborating keyword via a proximity dictionary.
- Combine SIT with a sensitivity-label condition in a **separate rule** (remember: Copilot location does not allow SIT + label in the same rule — see §3) so that only files already labeled Confidential are scanned for the SIT.
- Re-validate via simulation before advancing to enforcement (Scenario 10).

**What good looks like**

- Weekly false-positive count drops by ≥ 90% compared to the baseline week.
- True-positive recall remains within tolerance (validated via a labeled test corpus).
- The SIT change is recorded in Control 1.13's tuning log with a SHA-256 evidence stamp.

... see Control 1.13 — SIT tuning and EDM lifecycle.

---

### Scenario 13 — DLP coverage gap surfaced during exam

A FINRA, SEC, OCC, Fed, NYDFS, or state examiner identifies that a specific surface (e.g., Exchange Online for an associated-person population) is uninstrumented for a regulated content type, and asks the firm to remediate.

**This is an escalation, not a debug.** The diagnostic question is not "what's broken" — the surface was simply not instrumented. The remediation path is procedural.

**Procedure**

1. **Document the gap** in the firm's deviation register and incident ticket with: surface, content type, regulatory reference, date of examiner observation, and named owner.
2. **Apply a compensating control immediately** from §1.4 (e.g., site-level block at SPO, external sharing freeze, elevated CommComp review cadence).
3. **Define the remediation timeline** with concrete milestones: gap-closure design (T+5 business days), pilot enablement (T+15), full enforcement (T+30 or earlier per examiner expectation).
4. **Update Written Supervisory Procedures** to reflect both the new control and the compensating control during the gap.
5. **Log the gap closure under the firm's effective-challenge process** per **SR 11-7** / OCC 2011-12 — the AI Governance Lead and Model Risk function must independently challenge the closure design before sign-off. Refer Control 2.6.
6. **Provide examiner evidence**: the deviation register entry, the change ticket, the dated screenshots of policy state pre- and post-remediation, the SHA-256-stamped PowerShell exports, and the Sentinel ingestion proof for the new surface.

**What good looks like**

- The deviation register entry exists with a clear close-by date and named owner.
- A documented compensating control is in place from the moment the gap was identified through the moment full enforcement is verified.
- The remediation passes effective-challenge per SR 11-7 and is signed off by Model Risk + AI Governance + Compliance.
- The examiner closes the observation against documented evidence.

... see Control 2.6 — Effective challenge and SR 11-7 alignment, and Control 3.4 — Incident reporting and RCA.

---

## §5 Sovereign-cloud differences (summary)

| Capability | Commercial | GCC | GCC High | DoD |
|---|---|---|---|---|
| Purview DLP for Microsoft 365 Copilot and Copilot Chat (block by label) | ✅ GA | ⚠️ Verify Roadmap / MC | ⚠️ Verify — staged | ⚠️ Verify — staged |
| Purview DLP for Copilot prompts (SIT) | Preview | Verify | Verify | Verify |
| Power Platform data policies | ✅ GA | ✅ GA | ✅ GA (verify connector parity) | ✅ GA (verify connector parity) |
| Connector endpoint filtering | Preview | Verify | Verify | Verify |
| Sensitivity labels (file / email) | ✅ GA | ✅ GA | ✅ GA | ✅ GA |
| Auto-labeling (SPO / ODB / Exchange) | ✅ GA | ✅ GA | ✅ GA (verify model parity) | ✅ GA (verify model parity) |
| Endpoint DLP (Win + macOS) | ✅ | ✅ | ✅ | ✅ |
| Insider Risk Management + Adaptive Protection | ✅ GA | ❌ Not available | ❌ Not available | ❌ Not available |
| DSPM for AI | Staged | Verify | Verify | Verify |

**Portal endpoints**

- Commercial: `https://purview.microsoft.com` and `https://admin.powerplatform.microsoft.com`
- GCC: `https://compliance.microsoft.com` (transitioning to `purview.microsoft.com`); PPAC `admin.powerplatform.microsoft.us`
- GCC High / DoD: `https://purview.microsoft.us` and `https://admin.powerplatform.microsoft.us`

Document any sovereign-cloud exception in the control's deviation register; re-check on each Microsoft Learn refresh.

---

## §6 Escalation path

1. **L1 — Purview Compliance Admin** (within 1 h SEV-1; 4 h SEV-2): preserve evidence per §1.3; run §1.5 pre-escalation checklist.
2. **L2 — AI Governance Lead** (within 1 h SEV-1): triage cross-control impact (1.3, 1.6, 1.7, 1.10, 1.12, 1.13, 2.1, 2.16, 3.4, 3.9).
3. **L3 — CISO + Compliance Officer + Privacy + Legal** (within 1 h SEV-1): reportability determination per §1.2 decision tree.
4. **L4 — Microsoft support**: tenant ID, cloud, affected workload, UTC window, evidence pack reference, severity, business impact.
5. **L5 — Regulator notifications** (FINRA / SEC / NYDFS / state AGs / OCC / Fed / CFTC) as determined by Legal and Compliance.

---

## §7 Cross-references

- [Control 1.5 Portal Walkthrough](portal-walkthrough.md)
- [Control 1.5 PowerShell Setup](powershell-setup.md)
- [Control 1.5 Verification & Testing](verification-testing.md)
- [Control 1.3 — SharePoint & OneDrive Governance](../1.3/troubleshooting.md) ... site-level compensating control
- [Control 1.6 — DSPM for AI Troubleshooting](../1.6/troubleshooting.md) ... detection plane
- [Control 1.7 — Audit Troubleshooting](../1.7/troubleshooting.md) ... evidence plane
- [Control 1.10 — Communication Compliance](../1.10/troubleshooting.md) ... compensating supervisory control
- [Control 1.12 — Insider Risk Detection](../1.12/troubleshooting.md) ... Adaptive Protection dependency (Commercial only)
- [Control 1.13 — Sensitive Information Types](../1.13/troubleshooting.md) ... SIT and EDM readiness for DLP rules
- [Control 1.15 — Encryption Key Custody](../1.15/troubleshooting.md) ... DKE trade-offs vs Copilot
- [Control 2.1 — Copilot Studio Governance](../2.1/troubleshooting.md) ... Power Platform DLP precedence
- [Control 2.3 — Change Management and Release Planning](../2.3/troubleshooting.md) ... incremental enablement gates
- [Control 2.6 — Records Management and Effective Challenge (SR 11-7)](../2.6/troubleshooting.md) ... exam-driven gap closure
- [Control 2.16 — Agent Publishing Channels](../2.16/troubleshooting.md) ... channel-level DLP enforcement
- [Control 3.4 — Incident Reporting and RCA](../3.4/troubleshooting.md) ... Reg S-P 2024 notification clocks
- [Control 3.9 — Sentinel Forwarding and Analytics](../3.9/troubleshooting.md) ... DLP → Sentinel ingestion

---

*Updated: April 2026 | Version: v1.6.2 | UI Verification Status: Current*
