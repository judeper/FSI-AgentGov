# Control 1.5 — Troubleshooting: DLP for Microsoft 365 Copilot, Sensitivity Labels, and Power Platform Data Policies

**Control:** [1.5 Data Loss Prevention (DLP) and Sensitivity Labels](../../../controls/pillar-1-security/1.5-data-loss-prevention-dlp-and-sensitivity-labels.md)
**Last UI Verified:** April 2026

---

## §1 — FSI Incident Handling — READ FIRST

Control 1.5 is the **DLP enforcement plane** for AI-surfaced data flows. A failure in this plane (false-allow, missing location coverage, disabled rule, label not honored) is not a UI nuisance — it is a **safeguards failure** under GLBA 501(b), a **books-and-records integrity event** under SEC 17a-4(f) when the underlying record was customer NPI surfaced to an AI surface, and a potential **supervisory-system gap** under FINRA 3110 when DLP was the supervisory control of record. Treat any change to a Copilot DLP rule as an evidence-bearing event; preserve **before** you remediate.

### Severity matrix

| Severity | Trigger (DLP-specific) | Response window | Escalation |
|---|---|---|---|
| **SEV-1** | Confirmed leak of customer NPI / PII / MNPI through Copilot, Copilot Chat, or a published Copilot Studio agent; rule was off / mis-scoped / never enforced; or a Block-by-label rule failed open on Highly Confidential content | Immediate | CISO + Compliance + Legal + Privacy within 1 h |
| **SEV-2** | False-allow during enforcement window (rule fires in test, not in enforce); Copilot location absent from a policy that was supposed to cover it; AU-scoped admin created a Copilot rule that silently never applied; Power Platform DLP regressed allowing a blocked connector | 4 h | Compliance Admin → AI Governance Lead within 4 h |
| **SEV-3** | False-block disrupting a documented business workflow (overbroad SIT, label-condition mis-scope, citation-link friction); single-user / single-site coverage gap; propagation lag exceeded the documented 4-hour window | 1 business day | Compliance Admin |
| **SEV-4** | Cosmetic policy-tip text drift; UI label naming inconsistency; preview-feature regression that does not affect enforcement | Best effort | Track in known-issues log |

### Reportability decision tree

> This is an **escalation aid**, not a legal determination. Every external notification decision must be made by Legal / Compliance. Use this matrix to surface the question to the right desk inside the response window.

| Trigger | Escalate to | Possible obligation (verify with counsel) |
|---|---|---|
| Customer NPI disclosed via Copilot/agent without enforcement | Privacy + Legal | **GLBA 501(b)** safeguards; **SEC Reg S-P** §248.30(a)(4) customer-notification timeline (post-2024 amendments) |
| Books-and-records gap — DLP audit rows missing for Copilot interactions that touched regulated content | Compliance + Legal | **SEC 17a-3 / 17a-4(f)** record integrity; **FINRA 4511** |
| Loss of supervisory visibility on AI-surfaced communications (DLP + CommComp dual control) | Compliance | **FINRA Rule 3110** supervisory-system obligation |
| Cybersecurity event materially affecting normal operations | CISO + Legal | **23 NYCRR 500** (NYDFS) — 72-hour determination |
| AI/model-related operational risk event tied to DLP failure | Model Risk + Compliance | **OCC Bulletin 2011-12** / **Fed SR 11-7** model risk management |
| Records-related event for a covered swap / trading activity surfaced through Copilot | Compliance | **CFTC Rule 1.31** recordkeeping |
| Insider misconduct involving deliberate DLP bypass via Copilot | HR + Legal + Compliance | **FINRA Rule 4530** reporting |
| Unauthorized access to / disclosure of personal information of CA / NY residents | Privacy + Legal | **CA AB 1950** reasonable security; **NY SHIELD Act**; state breach notification statutes |
| Third-party AI / connector vendor failure that contributed to the leak | Vendor mgmt + Compliance | **Interagency Guidance on Third-Party Relationships** (OCC/FRB/FDIC 2023) |

### Evidence preservation **before** remediation

Capture the following artifacts **before** disabling, editing, or re-scoping the rule. A common audit finding is "the rule was changed before the evidence was captured, and the firm cannot reconstruct the failed configuration." Do not be that finding.

1. Full screenshots of the failing rule (Purview portal: Solutions > Data Loss Prevention > Policies > [policy] > [rule])
2. PowerShell snapshot:
   - `Get-DlpCompliancePolicy -Identity "<policy>" | Format-List` (from **IPPS** — `Connect-IPPSSession`, **not** EXO)
   - `Get-DlpComplianceRule -Policy "<policy>" | Format-List`
3. Audit rows for the suspect window via `Search-UnifiedAuditLog` from an **EXO** session (`Connect-ExchangeOnline`), `RecordType ComplianceDLPSharePoint`, `ComplianceDLPExchange`, or `DlpEndpoint` as applicable — **not** `RecordType DLP` (invalid; silent zero — see §4 / §5)
4. Prompt content & response (where lawful and where the user population is in scope of CommComp / IRM consent) from DSPM for AI Activity Explorer (Control 1.6) — content viewer role required
5. User identity, UPN, AAD object ID, manager, business unit, license SKU
6. UTC timestamps for: rule creation, last edit, enforcement-mode flip, the failing event, the screenshot capture
7. Sensitivity label state on the affected item: published label list for the user, label applied to the item, container-label inheritance state
8. SIT match details (Control 1.13) — which SIT, what confidence, what minimum count fired
9. Power Platform DLP state if the surface was a Copilot Studio agent: `Get-DlpPolicy` (Power Platform module), connector classification, environment scope
10. SHA-256 manifest sidecar covering every artifact above; store in the Control 1.7 evidence bucket with WORM retention

Only after the evidence pack is sealed should the rule be disabled, re-scoped, or moved out of enforcement.

### Compensating controls during the gap

Apply one or more of the following while the rule is being repaired. Document the compensating control in the incident ticket; do not leave the gap open.

- Temporarily **block** (not warn) at the SharePoint Online site or library level for the affected content (Control 1.3)
- Temporarily elevate **IRM / Adaptive Protection** posture for the affected user population (Control 1.12)
- Temporary **external sharing freeze** on the affected SPO sites (Control 1.3)
- Temporary **block on Copilot Studio publish** to non-Microsoft channels (Direct Line custom, Slack, web) for the affected environment (Control 2.1, 2.16)
- Increase **Communication Compliance** review cadence (Control 1.10) for the affected reviewers; manual review of AI-assisted content
- Manually search the Unified Audit Log daily for `CopilotInteraction` events touching the affected SITs / labels (Control 1.7)
- For Power Platform DLP gap: revoke maker access to the affected environment until rule is restored

### Pre-escalation checklist (≥ 10 items)

1. [ ] Tenant ID and cloud confirmed (Commercial / GCC / GCC High / DoD)
2. [ ] Policy + rule identity captured (`Get-DlpCompliancePolicy`, `Get-DlpComplianceRule` from IPPS)
3. [ ] Mode confirmed: `Enable` vs `TestWithNotifications` vs `TestWithoutNotifications` vs `Disable`
4. [ ] Locations enumerated: confirmed `Microsoft 365 Copilot and Copilot Chat` location is present **and** that the policy was built from the **Custom** template (one-click templates do not expose this location)
5. [ ] Confirmed rule does **not** combine SIT + sensitivity-label conditions in the same rule for the Copilot location (Purview rejects this; if it saved, it is split — verify)
6. [ ] Sensitivity label state captured: published-to scope, applied to item vs container only, container-label inheritance state
7. [ ] SIT readiness validated (Control 1.13): SIT exists, pattern matches the test data, confidence and minimum count not over-tight
8. [ ] Audit ingestion verified from EXO session (`Get-AdminAuditLogConfig` — **not** from IPPS, which returns a stale value)
9. [ ] Audit query used a **valid** RecordType (`ComplianceDLPSharePoint`, `ComplianceDLPExchange`, `DlpEndpoint`, `CopilotInteraction`) — **not** `DLP`
10. [ ] Propagation window honored — ≥ 4 hours since last rule save (Microsoft-documented for the Copilot location); test results within that window are not authoritative
11. [ ] Administrative-unit scope ruled out — the Copilot DLP location does **not** support AUs; an AU-scoped admin's rule silently never applies
12. [ ] Power Platform DLP state captured for any Copilot Studio surface (`Get-DlpPolicy`, environment scope, connector classification)
13. [ ] Sovereign-cloud parity verified — Adaptive Protection, IRM, and some Copilot DLP previews are **not at parity** in GCC High / DoD
14. [ ] Endpoint DLP device-onboarding state verified for any Endpoint surface (Defender for Endpoint or standalone Purview onboarding)
15. [ ] Last known good evidence pack timestamp (Control 1.7) recorded
16. [ ] Compliance + Legal notified per severity matrix; Privacy notified for any NPI-touching SEV-1 / SEV-2

---

## §2 — DSPM-for-AI vs Purview Audit vs DLP enforcement plane (decision matrix)

This control owns the **DLP enforcement plane** column. The other two columns reference Control 1.6 (DSPM for AI — detection plane) and Control 1.7 (Audit — evidence plane). Pick the right tool for the question you are answering; the wrong tool returns a misleading answer.

| Question you are answering | DSPM for AI (Control 1.6) | Purview Audit (Control 1.7) | **DLP enforcement plane (Control 1.5)** |
|---|---|---|---|
| What sensitive content was *processed* by Copilot recently? | ✅ Activity Explorer with content viewer role + content capture | ⚠️ Partial via `CopilotInteraction.AuditData.CopilotEventData` | ❌ DLP only logs *matches against rules*, not the full interaction |
| Did my DLP rule actually fire / block / warn? | ❌ | ⚠️ Audit row exists, but lacks rule-evaluation detail | ✅ DLP Alerts dashboard + `Get-DlpDetailReport` + audit `ComplianceDLP*` rows |
| Long-horizon (> 180 d) books-and-records evidence | ❌ (≈30-day UI window, not WORM) | ✅ Audit Premium + retention policy | ⚠️ DLP alerts retention is shorter than Audit Premium; export to evidence store |
| Should I add / tune / split this rule? | ⚠️ Use as input | ⚠️ Use as input | ✅ Authoritative — this is the enforcement plane |
| Per-prompt risk / category / topic of the AI interaction | ✅ DSPM (preview categories) | ⚠️ Limited fields | ❌ |
| Per-rule false-positive / false-negative rate over time | ❌ | ⚠️ Manual via audit query | ✅ DLP Alerts + Activity Explorer (DLP) + tuning loop in this control |
| Did a Power Platform connector get blocked at design time? | ❌ | ⚠️ Power Platform admin activity in audit | ✅ Power Platform data-policy enforcement + PPAC analytics |
| Did Copilot bypass DLP because the file was uploaded directly into the prompt? | ✅ Visible as interaction | ✅ `CopilotInteraction` row exists | ❌ Direct uploads to a Copilot prompt are **not scanned** by the Copilot DLP location — known limitation; design around it |

> Rule of thumb: **DSPM tells you what happened. Audit proves it. DLP changes what happens next.** Confusing the planes is the most common reason an investigation goes in circles.

---

## §3 — Anti-patterns (do not do)

| Anti-pattern | Why it's wrong | What to do instead |
|---|---|---|
| Disabling a rule to "fix" a false positive without documenting a compensating control | Leaves the regulated surface unprotected during the fix window; auditor cannot reconstruct the gap | Apply a §1 compensating control; document in the incident ticket; preserve the failing-state evidence first |
| Building the Copilot DLP rule from the **Standard** template (or any one-click template) | The `Microsoft 365 Copilot and Copilot Chat` location is exposed **only when you create a Custom policy**; one-click templates silently omit it | Always use **Custom** template for Copilot DLP; verify the location is checked before saving |
| Combining a SIT condition and a sensitivity-label condition in the **same rule** for the Copilot location | Purview UI rejects the save for the Copilot location; if you forced it via PowerShell the behavior is unsupported | **Split** into Rule A (SITs) and Rule B (label conditions) within the same policy |
| Treating a **container** label (site / Team / group) as if it were a **file** label | DLP rules that test "content has label X" evaluate the label on the **item**, not the container; container-label inheritance must be turned on, and it labels containers, not files | Apply file labels via auto-labeling or manual labeling; verify `Get-Label` / item label, not just the container |
| Querying audit with `Search-UnifiedAuditLog -RecordType DLP` | `DLP` is **not** a valid RecordType — it returns zero rows silently (no error). Investigators conclude "no events" when events exist | Use `ComplianceDLPSharePoint`, `ComplianceDLPExchange`, `DlpEndpoint`, or `CopilotInteraction` |
| Reading a Power Platform connector classification value from the API as if it were a UI label, without normalization | API returns `confidential` / `general` / `blocked` (Business / Non-Business / Blocked in UI) — string mismatch breaks reporting and audit reconciliation | Normalize via the documented mapping table; assert on the API value, not the UI label |
| Writing an auto-labeling policy that targets "AI interactions" as a location | **No such location exists** for auto-labeling. AI interactions are governed via the DLP for Copilot location and DSPM for AI, not via auto-labeling | Auto-label the underlying SPO / OneDrive / Exchange items; let the Copilot DLP rule act on the labeled items |
| Validating a new Copilot DLP rule by testing immediately after save | Documented propagation is **up to 4 hours** for the Copilot location; "it didn't fire" within that window is not a finding | Wait the documented window; record the rule-save UTC timestamp; test after the window |
| Scoping a Copilot DLP rule to a Restricted Administrative Unit (or having an AU-restricted admin author it) | Copilot DLP location does **not** support AUs — the rule silently never applies. Most insidious failure mode in this control | Author with a tenant-scoped Compliance Admin; do not use AU scoping for the Copilot location |
| Assuming **Adaptive Protection** is at parity in **GCC High / DoD** | IRM and Adaptive Protection are not at parity in GCC High / DoD; DLP rules conditioned on Adaptive Protection signals do nothing in those clouds | Document the sovereign-cloud exception; use static DLP conditions in GCC High / DoD |
| Trusting the citation list as evidence the file was "blocked" | The `Prevent Copilot from processing content` action stops summarization, but the item **still appears in citations with a link** — users can still click through | Combine with site-level / library-level access controls (Control 1.3); do not rely on the DLP action alone for click-through prevention |
| Using `Get-AdminAuditLogConfig` from `Connect-IPPSSession` to verify audit ingestion | IPPS returns a cached / stale value; the authoritative read is from `Connect-ExchangeOnline` | Always run `Get-AdminAuditLogConfig` from an EXO session |

---

## §4 — Symptom-driven diagnostics

> Format: **Symptom → Likely cause → Diagnostic → Fix → Reference**. Sovereign-cloud variants are called out inline.

### Symptom 1: "I created a Copilot DLP rule but it never fires"

| Likely cause | Diagnostic | Fix |
|---|---|---|
| Policy was built from a one-click / Standard template; Copilot location not present | Purview > DLP > Policies > [policy] > Locations — `Microsoft 365 Copilot and Copilot Chat` checkbox state | Recreate from **Custom** template; check the Copilot location |
| Rule combines SIT + label conditions (silently mis-saved) | `Get-DlpComplianceRule -Policy "<p>" \| Select Name, ContentContainsSensitiveInformation, ContentMatchesLabel` | Split into two rules per §3 |
| Rule still in `TestWithoutNotifications` mode | `Get-DlpCompliancePolicy -Identity "<p>" \| Select Mode` | Move to `TestWithNotifications` → `Enable` after the propagation window |
| < 4 hours since last save | UTC timestamp of last `Set-DlpCompliancePolicy` / `Set-DlpComplianceRule` | Wait the documented propagation window (up to 4 h) before testing |
| Author was a Restricted-AU admin | Confirm author identity and AU scope | Re-author with a tenant-scoped Compliance Admin (Copilot DLP location does not support AUs) |

**Reference:** Control 1.5 §"Custom template required; admin-unit limitations".

### Symptom 2: "I cannot find the Microsoft 365 Copilot and Copilot Chat location in the policy template"

| Likely cause | Fix |
|---|---|
| Started from a one-click template (Standard, Financial, Custom-but-from-template) | Start from **Custom policy** > Custom template; the location appears only here |
| License floor not met (per-user Copilot license + Purview prerequisites) | Verify per-user M365 Copilot license assignment via Graph (`Get-MgUserLicenseDetail`); verify Purview SKU |
| Sovereign cloud parity gap | Confirm cloud (Commercial / GCC / GCC High / DoD); Copilot DLP location availability lags in sovereign clouds — verify against current Microsoft Learn matrix |

**Reference:** Microsoft Learn — *Learn about the DLP policy for Microsoft 365 Copilot*.

### Symptom 3: "Save fails when I add SIT and label conditions to one rule"

- **Cause:** Documented limitation. The Copilot location does not allow `Content contains > Sensitive info types` and `Content contains > Sensitivity labels` in the same rule.
- **Fix:** Split into two rules within the same policy. Both can target the same Copilot location.
- **Reference:** Control 1.5 §"Do not combine SIT and sensitivity-label conditions in one rule for the Copilot location".

### Symptom 4: "Block-by-label works in SharePoint Online but not in email"

| Likely cause | Diagnostic | Fix |
|---|---|---|
| The label-based block action is scoped to SPO/OneDrive locations, not Exchange | Inspect rule's `Locations` and `BlockAccess` setting per location | Add Exchange location with a parallel rule using `BlockAccess = $true`; verify per-location settings |
| Email message did not inherit the label from the attachment | Check label on message vs attachment; verify `Outlook` MIP client version | Update MIP client; configure auto-labeling on the message based on attachment label |
| Rule order — an earlier allow rule short-circuits the block | `Get-DlpComplianceRule -Policy "<p>" \| Sort Priority` | Re-order priorities; ensure no upstream allow rule |

### Symptom 5: "User uploads a file directly into a Copilot prompt and it bypasses my DLP rule"

- **Cause:** Documented limitation — **files uploaded directly into a Copilot prompt are not scanned by the Copilot DLP location.** This is by design at the time of writing.
- **Fix (defense in depth):**
  - Add Endpoint DLP rule to detect / block the upload action at the device (Control 1.5 endpoint surface)
  - Apply a **sensitivity label** to the file at rest in SPO/OneDrive — the label travels with the file; downstream processing can act on the label
  - Use **Adaptive Protection** (Commercial only — Control 1.12) to elevate posture for risky users
  - Educate users via policy tip; treat as a known limitation in the risk register
- **Reference:** Control 1.5 §"DLP for Microsoft 365 Copilot and Copilot Chat" — file-upload limitation.

### Symptom 6: "Audit search returns zero rows"

| Likely cause | Diagnostic | Fix |
|---|---|---|
| Used `RecordType DLP` (invalid; silent zero) | Inspect script | Use `ComplianceDLPSharePoint`, `ComplianceDLPExchange`, `DlpEndpoint`, `CopilotInteraction` |
| Audit ingestion off | `Get-AdminAuditLogConfig` from **EXO** (not IPPS) | Re-enable: `Set-AdminAuditLogConfig -UnifiedAuditLogIngestionEnabled $true` from EXO |
| Single-shot pagination truncated | Inspect for missing `-SessionId` / `-SessionCommand ReturnLargeSet` | Implement do-while pagination; cap 50,000 per session |
| Wrong cloud endpoint (sovereign) | Verify `Connect-ExchangeOnline -ExchangeEnvironmentName` matches tenant cloud | Use `O365USGovGCCHigh` / `O365USGovDoD` as appropriate |
| Time window includes propagation lag (audit ingestion is not real-time) | Widen window to ≥ T+30 min | Re-run with widened window |

**Reference:** Control 1.7 (Audit) troubleshooting; Control 1.6 §"Wrong-shell trap".

### Symptom 7: "Power Platform DLP report shows different connector grouping than the UI"

| Likely cause | Fix |
|---|---|
| API returns `confidential` / `general` / `blocked`; UI shows Business / Non-Business / Blocked | Normalize via the documented mapping in Control 1.5 before joining datasets |
| Connector has multiple aliases / variants (e.g., `HTTP Webhook` vs `HTTP with Microsoft Entra ID`) | Inventory all variants; classify each explicitly |
| Tenant connector catalog is dynamic — new connectors appear without notice | Run a scheduled connector inventory; alert on any unclassified new connector |
| Environment scope mismatch — policy `All environments except…` does not behave as expected | Re-scope to explicit environment list; avoid `except` patterns for Zone 3 |

### Symptom 8: "Sensitivity label not visible to user"

| Likely cause | Fix |
|---|---|
| Label not published to the user's group | Purview > Information Protection > Label policies > Publish to the user's group; allow propagation (up to 24 h for client) |
| MIP client out of date | Update Office / built-in labeling client to a supported version |
| Label scope excludes the workload (Files & emails vs Groups & sites vs Schematized data assets) | Edit label > Scope; republish |
| User license does not include MIP client labeling | Verify SKU (E3/E5/Purview) |

### Symptom 9: "Auto-labeling policy not finding 'AI interactions' as a location"

- **Cause:** **No such location exists.** Auto-labeling targets files (SPO/OneDrive), email (Exchange), and schematized data assets — not AI interactions.
- **Fix:** Auto-label the underlying SPO/OneDrive items; let the Copilot DLP rule (Control 1.5) act on the label. For the AI interaction itself, use DSPM for AI (Control 1.6) for detection and the Copilot DLP location for enforcement.
- **Anti-pattern check:** Do not invent the location via PowerShell — it will not exist.

### Symptom 10: "Adaptive Protection rule does nothing in GCC High"

- **Cause:** Insider Risk Management and Adaptive Protection are **not at parity** in GCC High / DoD at the time of writing. A DLP rule conditioned on Adaptive Protection signals will evaluate to false in those clouds.
- **Fix:** In GCC High / DoD, use static DLP conditions (SIT + label + group membership). Document the sovereign-cloud exception. Revisit on each Microsoft Learn refresh.
- **Reference:** Microsoft Learn — service description matrices for US Government clouds.

### Symptom 11: "Endpoint DLP rule not enforcing on a managed device"

| Likely cause | Diagnostic | Fix |
|---|---|---|
| Device not onboarded | Defender for Endpoint device list, or standalone Purview onboarding state | Onboard via Intune script or DfE auto-onboarding |
| Endpoint DLP not licensed for the user | `Get-MgUserLicenseDetail` | Assign E5 Compliance / Purview Suite |
| Browser extension missing (for browser-uploaded content) | Intune extension deployment report | Push the Purview browser extension via Intune |
| Rule does not include the Devices location | Rule > Locations | Add `Devices` location; re-save; honor propagation window |
| Affected app not in the monitored-app list | Endpoint DLP settings > Restricted apps | Add app; re-test |

### Symptom 12: "Wrong-shell error: command not found in EXO session"

- **Cause:** `Get-DlpCompliancePolicy` / `Get-DlpComplianceRule` / `Get-Label` are exposed via **`Connect-IPPSSession`** (Security & Compliance PowerShell), **not** `Connect-ExchangeOnline`. Conversely, `Get-AdminAuditLogConfig` is authoritative from **EXO**, not IPPS.
- **Fix:** Open two sessions. Use IPPS for DLP / label cmdlets; use EXO for audit-config and `Search-UnifiedAuditLog`.
- **Reference:** Control 1.6 §"Wrong-shell trap".

### Symptom 13: "Sovereign cloud connection fails — wrong endpoint"

| Cloud | Connect-IPPSSession parameter | Connect-ExchangeOnline parameter |
|---|---|---|
| Commercial | (default) | (default) |
| GCC | `-ConnectionUri https://ps.compliance.protection.outlook.com/powershell-liveid/` | `-ExchangeEnvironmentName O365USGovGCC` |
| GCC High | `-ConnectionUri https://ps.compliance.protection.office365.us/powershell-liveid/ -AzureADAuthorizationEndpointUri https://login.microsoftonline.us/common` | `-ExchangeEnvironmentName O365USGovGCCHigh` |
| DoD | `-ConnectionUri https://l5.ps.compliance.protection.office365.us/powershell-liveid/ -AzureADAuthorizationEndpointUri https://login.microsoftonline.us/common` | `-ExchangeEnvironmentName O365USGovDoD` |

Use `purview.microsoft.us` (not `purview.microsoft.com`) for GCC High / DoD portal access. Hitting `.com` on a `.us` tenant returns the wrong directory scope and can silently authenticate to the wrong tenant.

### Symptom 14: "DLP rule applies but the citation still shows the blocked file"

- **Cause:** Documented behavior. The `Prevent Copilot from processing content` action stops summarization of the labeled item into the response, but the item **still appears in citations with a link**. This is not a rule failure.
- **Fix:** Combine with **site / library-level access controls** (Control 1.3) so the click-through is denied at SPO. The DLP action alone is not sufficient to prevent click-through; that is by design.
- **Reference:** Control 1.5 §"Block by sensitivity label" — citation behavior callout.

---

## §5 — Sovereign cloud differences (summary)

| Capability | Commercial | GCC | GCC High | DoD |
|---|---|---|---|---|
| Copilot DLP location (`Microsoft 365 Copilot and Copilot Chat`) | ✅ GA (block-by-label) | ⚠️ Verify per Learn | ⚠️ Lagging — verify per Learn | ⚠️ Lagging — verify per Learn |
| Adaptive Protection / IRM signals usable as DLP condition | ✅ | ⚠️ Partial | ❌ Not at parity | ❌ Not at parity |
| Power Platform DLP (Copilot Studio enforcement) | ✅ | ✅ | ✅ (verify connector parity) | ✅ (verify connector parity) |
| Endpoint DLP | ✅ | ✅ | ✅ | ✅ |
| Portal hostname | `purview.microsoft.com` | `compliance.microsoft.com` | `purview.microsoft.us` | `purview.apps.mil` (verify current) |

Document any sovereign-cloud exception in the control's deviation register; re-check on each Microsoft Learn refresh.

---

## §6 — Escalation path

1. **L1 — Purview Compliance Admin** (within 1 h SEV-1; 4 h SEV-2): preserve evidence per §1; run pre-escalation checklist
2. **L2 — AI Governance Lead** (within 1 h SEV-1): triage cross-control impact (1.3, 1.6, 1.7, 1.10, 1.12, 1.13, 2.1, 2.16)
3. **L3 — CISO + Compliance Officer + Privacy + Legal** (within 1 h SEV-1): reportability determination per §1 decision tree
4. **L4 — Microsoft support** with: tenant ID, cloud, affected workload, UTC window, evidence pack reference, severity, business impact statement
5. **L5 — Regulator notifications** (FINRA / SEC / NYDFS / state AGs / OCC / Fed / CFTC) as determined by Legal / Compliance

---

## Cross-references

- [Control 1.5 Portal Walkthrough](portal-walkthrough.md)
- [Control 1.5 PowerShell Setup](powershell-setup.md)
- [Control 1.5 Verification & Testing](verification-testing.md)
- [Control 1.3 SharePoint & OneDrive Governance](../1.3/troubleshooting.md) — site-level compensating control
- [Control 1.6 DSPM for AI Troubleshooting](../1.6/troubleshooting.md) — detection plane
- [Control 1.7 Audit Troubleshooting](../1.7/troubleshooting.md) — evidence plane
- [Control 1.10 Communication Compliance](../1.10/troubleshooting.md) — compensating supervisory control
- [Control 1.12 Insider Risk Detection](../1.12/troubleshooting.md) — Adaptive Protection dependency
- [Control 1.13 Sensitive Information Types](../1.13/troubleshooting.md) — SIT readiness for DLP rules
- [Control 2.1 Copilot Studio Governance](../2.1/troubleshooting.md) — Power Platform DLP surface
- [Control 2.16 Agent Publishing Channels](../2.16/troubleshooting.md) — channel-level DLP enforcement

---

*Updated: April 2026 | Version: v1.4 | UI Verification Status: Current*
