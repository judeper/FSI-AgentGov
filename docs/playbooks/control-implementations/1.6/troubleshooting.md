# Control 1.6 — Troubleshooting: DSPM for AI

**Control:** [1.6 Microsoft Purview DSPM for AI](../../../controls/pillar-1-security/1.6-microsoft-purview-dspm-for-ai.md)
**Last UI Verified:** April 2026

---

## §1 — FSI Incident Handling — READ FIRST

DSPM for AI is the **detection plane** for Copilot / agent / third-party-AI risk. A loss or degradation of DSPM telemetry on a Zone 3 workload is a **supervisory-system gap** under FINRA 3110 and a **books-and-records integrity event** under FINRA 4511 / SEC 17a-4(f). Treat as an incident; do **not** "just fix the UI."

### Severity matrix

| Severity | Trigger | Response window | Escalation |
|---|---|---|---|
| SEV-1 | DSPM telemetry blackout on a Zone 3 workload affecting M365 Copilot or named regulated agents; sensitive-info exposure visible without policy enforcement; unauthorized access to DSPM Content Viewer | Immediate | CISO + Compliance + Legal within 1 h |
| SEV-2 | Degraded coverage (one Get Started step regressed; one-click template not enforcing); Adaptive Protection inactive; missing PAYG coverage of in-scope third-party AI | 4 h | Compliance Admin → AI Governance Lead within 4 h |
| SEV-3 | Single-user / single-site coverage gap; assessment delayed > documented Learn window | 1 business day | Compliance Admin |
| SEV-4 | Cosmetic / UI drift; preview feature regression | Best effort | Track in known-issues log |

### Reportability decision tree

> Reportability is a Compliance/Legal determination. Use this tree to escalate, not to decide.

| Trigger | Escalate to | Possible obligation |
|---|---|---|
| Loss of supervisory visibility on AI-surfaced communications | Compliance | FINRA 3110 supervisory-system obligation |
| Books-and-records gap (CopilotInteraction events lost / not retained) | Compliance + Legal | FINRA 4511 / SEC 17a-4(f) |
| NPI / customer info disclosed via Copilot/agent without enforcement | Privacy + Legal | GLBA 501(b); SEC Reg S-P §248.30(a)(4) customer-notification timeline |
| Cybersecurity event materially affecting normal operations | CISO + Legal | NY DFS 23 NYCRR 500 — 72-hour determination |
| AI/model-related operational risk event | Model Risk + Compliance | OCC 2011-12 / Fed SR 11-7 |
| Third-party AI vendor failure | Vendor mgmt + Compliance | Interagency Guidance on Third-Party Relationships |
| Records-related event for a covered swap/trading activity | Compliance | CFTC Rule 1.31 |
| Insider misconduct involving AI surface | HR + Legal + Compliance | FINRA 4530 |

### Evidence preservation **before** remediation

Capture, do **not** mutate first:

1. Screenshots of the failure state (DSPM Overview, the failing page, error toast)
2. `Get-AdminAuditLogConfig` output from `Connect-ExchangeOnline` (correct shell)
3. One-click policy inventory snapshot (`Get-DlpCompliancePolicy`, `Get-RetentionCompliancePolicy`)
4. Last successful evidence pack timestamp
5. Tenant ID, cloud, affected user/site list, UTC window, role used
6. Browser-extension and device-onboarding state
7. Activity Explorer export for the suspect window (paginated; no truncation)
8. Adaptive Protection / IRM policy snapshot
9. SHA-256 sidecar for every artifact

### Compensating controls during the gap

- Increase Communication Compliance review cadence (Control 1.10) on in-scope reviewers
- Tighten DLP for Copilot location (Control 1.5) to Block where previously TestWithNotifications
- Freeze new Zone 3 agent activations / new Copilot Studio publishes (Control 2.1, 2.16)
- Manually search Unified Audit Log daily for `CopilotInteraction` events (Control 1.7)
- Increase manual supervisory review of AI-assisted content for in-scope user populations

### Pre-escalation checklist (≥ 12 items)

1. [ ] Tenant ID and cloud confirmed (Commercial / GCC / GCC High / DoD)
2. [ ] All four Get Started steps re-checked with screenshots
3. [ ] License floor verified via Graph (`Get-MgSubscribedSku`)
4. [ ] Per-user Copilot license verified for sample of affected users
5. [ ] PAYG billing state verified (where third-party AI in scope)
6. [ ] Audit ingestion verified from **EXO** session, not IPPS
7. [ ] One-click policy inventory captured with mode + content-capture state
8. [ ] Activity Explorer queried with deterministic filter; result count recorded
9. [ ] Mirror query run via `Search-UnifiedAuditLog -RecordType CopilotInteraction` (paginated)
10. [ ] Browser extension / Edge configuration policy state verified per device class
11. [ ] Device onboarding state verified (Defender for Endpoint / standalone)
12. [ ] Adaptive Protection / IRM policy state captured
13. [ ] Sovereign cloud parity confirmed (IRM/Adaptive Protection NOT at parity in GCC High/DoD)
14. [ ] Administrative-unit restriction ruled out
15. [ ] Last known good evidence pack timestamp recorded
16. [ ] Compliance + Legal notified per severity matrix

---

## §2 — Symptom-driven diagnostics

### Symptom: DSPM Activity Explorer shows zero AI interactions

| Cause | Diagnostic | Fix |
|---|---|---|
| Audit ingestion off | `Get-AdminAuditLogConfig` from EXO session | Re-enable in EXO; do not trust IPPS value |
| Wrong RecordType used in PowerShell mirror query | Inspect script for `AIPDiscover` etc. | Use `CopilotInteraction` |
| Single-shot pagination truncated | Inspect for missing `-SessionId` / `-SessionCommand ReturnLargeSet` | Implement do-while pagination, cap 50,000 per session |
| Affected users unlicensed for M365 Copilot | `Get-MgUserLicenseDetail` | Assign Copilot license; document gap |
| Content capture not enabled on collection policy | DSPM > Policies > template > content capture state | Enable; allow up to 24 h to surface |
| Browser extension / Edge config policy missing on managed device | Intune device compliance report | Push policy / extension; reconcile coverage |
| Affected user without Exchange Online mailbox | Graph user lookup | Prompt/response text won't display per Learn |
| Restricted-AU admin opening the page | Confirm user's AU scope | Use a tenant-scoped reviewer; AU not supported |

### Symptom: One-click policy template not visible / "Recommendation Not Updating"

| Cause | Fix |
|---|---|
| Missing role group (e.g., IRM role group for Risky AI usage) | Assign per template's underlying solution |
| License floor unmet (E5 / E5 Compliance / Purview Suite) | Assign SKU; reload page after propagation |
| Recommendation completed/dismissed/`PendingDeletion` | Check status; do **not** "manually mark complete" without evidence — that suppresses oversight |
| Restricted-AU admin (DSPM does not support AU) | Use tenant-scoped admin |
| GCC High/DoD parity gap | Document exception; use commercial-only feature only where the workload allows |

### Symptom: DSPM Get Started never completes / "Activate Audit" step stuck

- Validate `UnifiedAuditLogIngestionEnabled = True` from EXO session
- If `True` but UI cached `False`, sign out / refresh token; allow propagation
- Confirm an Exchange role group holder is performing the step (Compliance Admin alone cannot)
- "Extend your insights" requires IRM / Communication Compliance pre-reqs — incomplete pre-reqs leave the step "Completed" with degraded observability

### Symptom: Adaptive Protection score does not change

| Requirement | Verification |
|---|---|
| IRM policy created and active | `Get-InsiderRiskPolicy` (where exposed) / portal |
| Minimum baseline window observed | ≥ 7 days per Learn |
| Risk-level thresholds configured in IRM | Insider Risk > Settings |
| User in scope of IRM policy | IRM policy scope |
| Tenant cloud supports IRM/Adaptive Protection | Skip in GCC High/DoD; document |

### Symptom: Sensitivity label not propagated to Copilot response

| Cause | Fix |
|---|---|
| Endpoint MIP client out of date | Update to supported client version |
| Label not published to user | Publish via Sensitivity labels > Publish |
| Auto-labeling scope excludes the file | Review scope conditions |
| Container-label inheritance off | Enable per Learn `sensitivity-labels-teams-groups-sites` |
| DLP for Copilot location does not allow SIT + label in same rule | Split into separate rules per Learn |

### Symptom: Third-party AI (ChatGPT Enterprise / Gemini) shows no events

| Cause | Fix |
|---|---|
| PAYG billing not enabled | Enable Purview pay-as-you-go in Azure subscription |
| Browser extension missing on Windows + Chrome/Firefox | Push via Intune |
| Edge configuration policy missing | Push via Intune (NOT extension) |
| Device not onboarded | Defender for Endpoint or standalone Purview onboarding |
| Extended insights step not complete (requires IRM pre-reqs) | Complete Get Started step 4 |

---

## §3 — DSPM vs Audit decision matrix

| Question | Use DSPM Activity Explorer | Use Search-UnifiedAuditLog (Control 1.7) |
|---|---|---|
| What was the prompt content / response category? | ✅ (with content viewer role + content capture on) | ⚠️ Partial via `CopilotInteraction.AuditData.CopilotEventData` |
| Books-and-records evidence for FINRA 4511 / SEC 17a-4(f) | ❌ (UI tool, ~30-day window, not WORM) | ✅ (paired with Audit Premium retention) |
| Third-party AI app interaction (ChatGPT / Gemini) | ✅ (browser extension + PAYG) | ❌ (not captured in UAL) |
| Long-horizon (> 180 d) lookback | ❌ | ✅ (Audit Premium + retention policy) |
| Per-agent risk score | ✅ (preview) | ❌ |

---

## §4 — Anti-patterns (do not do)

| Anti-pattern | Why it's wrong |
|---|---|
| "Manually mark recommendation as complete" without evidence | Suppresses oversight without proving the underlying control is effective |
| Treating Activity Explorer empty table as PASS | Silent-zero-row trap (N3.2) — assert deterministic event |
| Filtering audit search with `AIPDiscover` etc. for Copilot evidence | AIP record types ≠ DSPM-for-AI events |
| Calling `Set-AdminAuditLogConfig` from `Connect-IPPSSession` | Wrong-shell trap (N3.1) |
| Asserting `RiskScore` / `AccessPattern` fields on `CopilotInteraction.AuditData` | Not in published schema |
| Using commercial portal URL on a GCC High tenant | `purview.microsoft.com` on a `.us` tenant returns wrong scope |
| Assuming Adaptive Protection works in GCC High / DoD | IRM not at parity |
| Restricted-AU admin attempting one-click policy creation | AU not supported by DSPM |

---

## §5 — Escalation path

1. **L1 — Compliance Admin** (within 1 h for SEV-1; 4 h for SEV-2): preserve evidence, run pre-escalation checklist
2. **L2 — AI Governance Lead** (within 1 h for SEV-1): triage cross-control impact (1.5 / 1.7 / 1.10 / 1.12 / 2.1)
3. **L3 — CISO + Compliance Officer + Legal** (within 1 h for SEV-1): reportability determination
4. **L4 — Microsoft support** with: tenant ID, cloud, affected workload, UTC window, evidence pack reference, severity, business impact statement
5. **L5 — Regulator notifications** as determined by Legal / Compliance

---

## Cross-references

- [Control 1.6 Verification & Testing](verification-testing.md) — detects the conditions this playbook handles
- [Control 1.6 Portal Walkthrough](portal-walkthrough.md) — sovereign cloud table, role-by-step matrix
- [Control 1.6 PowerShell Setup](powershell-setup.md) — wrong-shell trap, paginated audit query
- [Control 1.7 Troubleshooting](../1.7/troubleshooting.md) — durable evidence backbone
- [Control 1.10 Communication Compliance](../1.10/troubleshooting.md) — compensating control during DSPM gap
- [Control 1.12 Insider Risk Detection](../1.12/troubleshooting.md) — Adaptive Protection dependency

---

*Updated: April 2026 | Version: v1.4 | UI Verification Status: Current*
