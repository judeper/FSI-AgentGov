# Control 2.10: Patch Management and System Updates — Troubleshooting

> Troubleshooting companion to [Control 2.10: Patch Management and System Updates](../../../controls/pillar-2-management/2.10-patch-management-and-system-updates.md).
>
> **Audience:** Power Platform Admins, AI Administrators, and AI Governance Leads operating in US financial services tenants.

---

## Quick Reference

| Symptom | Likely Cause | Section |
|---------|--------------|---------|
| No Message Center email digests | Preferences not configured or mailbox filtering | §1 |
| Service Health alert never fires | Alert scope or action group misconfigured | §2 |
| `Get-MgServiceAnnouncementMessage` returns 0 results | Sovereign-cloud endpoint mismatch or scope not consented | §3 |
| Release channel reports `Unknown` from PowerShell | Module version or property path drift | §4 |
| Microsoft applied a change without prior Message Center notice | Change classified as "Stay informed" or routed to Roadmap only | §5 |
| Connector deprecated mid-validation | Connector lifecycle independent of release wave | §6 |
| Rollback impossible — change is platform-side | Customer cannot revert vendor-driven changes | §7 |
| Graph throttling (HTTP 429) on Message Center polling | High call volume or shared app-only credential | §8 |
| Power Apps Admin cmdlets return empty in PowerShell 7 | Module is Desktop (5.1) only | §9 |
| Validation env behavior differs from production after change | Channel mismatch is **expected**; treat as feature not bug | §10 |

---

## §1 — Not Receiving Message Center Email Digests

**Symptoms:** The change-intake distribution list has not received an email in 14+ days.

**Diagnosis:**

1. In Microsoft 365 Admin Center > **Health > Message center > Preferences > Email**, confirm:
    - Email recipients include the distribution list.
    - At least one of the AI-relevant services is checked under **Choose services**.
    - "Send me a weekly digest" or "major updates" is enabled.
2. Check the distribution list's mailbox rules — Message Center digests sometimes route to a **Other** or focused-inbox tab.
3. Check Exchange Online transport rules for any rule that blocks `*.microsoft.com` notification senders.
4. In the Microsoft 365 Admin Center, open a recent Message Center post and select **Share > Email** to send a test message to confirm the routing path works at all.

**Resolution:**

- Re-add the distribution list and save.
- Add the Microsoft notification senders (`o365mc@microsoft.com` and the Service Communications API tenant addresses) to safe senders.
- If the issue persists, fall back to programmatic polling via the [PowerShell Setup](powershell-setup.md) Script 1, which does not depend on email delivery.

---

## §2 — Service Health Alert Never Fires

**Symptoms:** No alert delivered despite a known Microsoft service incident.

**Diagnosis:**

1. In the Azure Portal, open **Service Health > Health alerts** and confirm the rule is **Enabled**.
2. Open the rule and confirm:
    - **Subscription** scope includes the affected subscription.
    - **Region** scope includes the region of the impacted service.
    - **Service** scope includes `Microsoft.PowerPlatform` (or the relevant resource provider).
    - **Event type** includes the relevant category (Service issue, Planned maintenance, Security advisory).
3. Open the action group and confirm at least one action is **Enabled**.
4. In **Monitor > Alerts**, filter by the action group and the time window of the known incident.

**Resolution:**

- Action groups are evaluated independently — disable a misconfigured action (e.g., a webhook to a decommissioned URL) so it does not block the rest.
- For SMS, confirm the carrier-delivery status in the action group test panel; SMS is best-effort and not auditable. Do not rely on it as the primary channel.
- If a known Microsoft incident did not produce an alert, open a Microsoft support case referencing the Service Health tracking ID — the alert pipeline itself can have gaps that must be reported.

---

## §3 — `Get-MgServiceAnnouncementMessage` Returns Zero Results

**Symptoms:** The PowerShell script reports `Total messages in window: 0` even though the Message Center UI shows posts.

**Likely cause #1: Sovereign-cloud endpoint mismatch.** Running `Connect-MgGraph` without `-Environment` against a GCC, GCC High, or DoD tenant connects to commercial endpoints, succeeds, and returns zero data. This is the **#1 source of false-clean evidence** in this control.

**Resolution:**

```powershell
# Use the helper from powershell-setup.md, not bare Connect-MgGraph
. .\Connect-FsiTenant.ps1
Connect-FsiTenant -Cloud GCCHigh -Scopes 'ServiceMessage.Read.All'
```

**Likely cause #2: Scope not consented.** Application permission `ServiceMessage.Read.All` requires Entra Global Admin consent. Delegated permission requires the signed-in user to hold a role that includes Service Health read (e.g., **Service Support Administrator**, **Global Reader**, or **Global Administrator**).

**Resolution:** In Microsoft Entra admin center > **Applications > Enterprise applications > [your app]**, confirm `ServiceMessage.Read.All` is granted with admin consent.

**Likely cause #3: Filter is too restrictive.** A `lastModifiedDateTime` window that is too short returns nothing.

**Resolution:** Widen `-Days` to 60 and re-run.

---

## §4 — Release Channel Reports `Unknown`

**Symptoms:** `Get-EnvironmentReleaseChannels.ps1` returns `ReleaseChannel = Unknown` for some or all environments.

**Cause:** The JSON property exposing release channel through the Power Apps Admin module has changed across module versions and is not always surfaced in the cmdlet output. The PPAC UI is authoritative.

**Resolution:**

1. Treat the PPAC UI value as authoritative for evidence — capture a screenshot of **Settings > Product > Behavior** for each environment.
2. Document the module version mismatch in the validation evidence so it is not flagged as a finding.
3. If you require a programmatic source, query the Dataverse `organization` entity directly for the environment using the Web API (cmdlet support is inconsistent across versions). This is an advanced workaround; record any custom query in your runbook.

> **Note:** The cmdlet may stabilize on this in a future module version. Re-test with each pinned-version upgrade.

---

## §5 — Microsoft Applied a Change Without Prior Message Center Notice

**Symptoms:** A behavior change appears in production but no Message Center post predates it.

**Cause:** Some changes are tracked only on the Microsoft 365 Roadmap or in Power Platform release notes, not Message Center. Common categories:

- "Stay informed" posts that are advisory only and may not be sent as digests
- Bug fixes in Microsoft-managed services that do not require customer action
- Changes in preview features that are not announced through Message Center until GA

**Resolution:**

1. Subscribe to the [Microsoft 365 Roadmap RSS feed](https://www.microsoft.com/microsoft-365/roadmap) filtered to AI services.
2. Subscribe to the [Power Platform Release Plan](https://learn.microsoft.com/en-us/power-platform/release-plan/) RSS for the current wave.
3. Add a periodic review (monthly) of the [Copilot Studio "What's new"](https://learn.microsoft.com/en-us/microsoft-copilot-studio/whats-new) page to the AI Administrator's runbook.
4. If the change has produced a regression, open a Microsoft support case and reference the lack of prior notice as a finding.

---

## §6 — Connector Deprecated Mid-Validation

**Symptoms:** A connector used by an agent is marked deprecated during the validation window.

**Cause:** Connector lifecycle is **independent** of Power Platform release waves. Connector deprecations follow the connector publisher's own schedule and are announced in connector documentation, not always in Message Center.

**Resolution:**

1. Check the connector's reference page for the published deprecation date and recommended replacement.
2. If the replacement is a different connector, treat it as a Major change per [Control 2.3](../../../controls/pillar-2-management/2.3-change-management-and-release-planning.md) — it requires CAB review.
3. If the deprecation predates your evidence window, document the gap and the planned replacement in the change ticket.
4. Subscribe to the connector publisher's change feed where available (Microsoft connectors are tracked in the [connector reference](https://learn.microsoft.com/en-us/connectors/connector-reference/)).

---

## §7 — Cannot Roll Back a Platform-Side Change

**Symptoms:** A platform change has degraded agent behavior, but the documented rollback plan does not work because the change is server-side.

**Cause:** Some changes (Copilot Studio platform behavior, Microsoft 365 Copilot model updates, connector authentication changes initiated by Microsoft) cannot be reverted by the customer. The customer can only **mitigate**.

**Resolution:**

1. Update the agent's rollback plan to distinguish **revertible** vs. **mitigation-only** changes.
2. For mitigation-only changes, document the available mitigations:
    - Disable the affected topic or knowledge source.
    - Route users to a fallback agent or human channel.
    - Apply a workaround in the agent's prompt or instructions.
3. Open a Microsoft support case with severity aligned to the business impact.
4. Record the constraint in the change ticket so future audits do not flag the inability to roll back as a control failure — it is a vendor-platform reality that the FSI control framework explicitly recognizes.

> **Important:** Do not claim a rollback capability in attestations that the platform does not support. Examiners test for accuracy.

---

## §8 — Graph Throttling on Message Center Polling

**Symptoms:** Script 1 from the [PowerShell Setup](powershell-setup.md) playbook returns HTTP 429 errors.

**Cause:** Microsoft Graph applies tenant-wide and app-wide throttling. High-frequency polling, especially with a shared service principal across many automations, can trip throttling.

**Resolution:**

1. Reduce polling frequency to once per day off-peak.
2. Honor the `Retry-After` header — `Microsoft.Graph` SDK does this automatically; if you build a raw HTTP client, implement exponential backoff.
3. Use a **dedicated** service principal for Message Center polling so it is not contending with other Graph clients.
4. For Zone 3, use the [Message Center Monitor](https://github.com/judeper/FSI-AgentGov-Solutions/tree/main/message-center-monitor) solution which polls once per day and persists to Dataverse, removing the need for ad hoc PowerShell pulls.

---

## §9 — Power Apps Admin Cmdlets Return Empty in PowerShell 7

**Symptoms:** `Get-AdminPowerAppEnvironment` runs without error in PowerShell 7 but returns no environments.

**Cause:** The `Microsoft.PowerApps.Administration.PowerShell` module is **Desktop edition only** (Windows PowerShell 5.1). In PowerShell 7 (Core), the cmdlet authenticates and silently returns empty, producing **false-clean evidence**.

**Resolution:**

```powershell
# Run from Windows PowerShell 5.1, not PowerShell 7
if ($PSVersionTable.PSEdition -ne 'Desktop') {
    throw "Run this from Windows PowerShell 5.1. Detected: $($PSVersionTable.PSEdition) $($PSVersionTable.PSVersion)."
}
```

The validation script in the [PowerShell Setup](powershell-setup.md) playbook includes this guard. Do not run release-channel checks from PowerShell 7 hosts.

---

## §10 — Validation Environment Behaves Differently From Production

**Symptoms:** Test results in the Monthly-channel validation environment do not match production behavior.

**Cause:** This is **expected**. The Monthly channel receives features 4–8 weeks before the Semi-annual channel by design. The point of the validation environment is to surface these differences before they reach production users.

**Resolution:** This is not a defect. Capture the behavior difference in the validation evidence and decide whether to:

- Wait for Semi-annual roll-out and confirm parity at that time.
- Apply a workaround to the agent if the change will be breaking when it reaches Semi-annual.
- Open a Microsoft support case if the change is unintended.

If the divergence is excessive (entire features missing rather than minor behavior differences), confirm that production has not been switched to Monthly accidentally.

---

## Escalation Path

| Tier | Owner | When to Engage |
|------|-------|----------------|
| **Tier 1** | Power Platform Admin | Configuration issues with Message Center, Service Health, release channels |
| **Tier 2** | AI Administrator | Copilot Studio / Microsoft 365 Copilot platform-update impact |
| **Tier 3** | AI Governance Lead | Change-management process exceptions, CAB escalation, attestation gaps |
| **Tier 4** | Microsoft Support | Platform incidents, missing Message Center notice, throttling beyond documented limits |
| **Tier 5** | Microsoft Account Team / FastTrack | Pre-wave architecture risk reviews, advance notice of breaking changes |

For severe issues, parallel-engage Microsoft Support and the Microsoft account team — support handles the technical incident, the account team escalates internally if the change appears to violate Microsoft's published change-notice commitments.

---

## Known Limitations

| Limitation | Impact | Mitigation |
|------------|--------|------------|
| Microsoft owns platform release cadence | Customer cannot defer or opt out indefinitely | Use validation environment + Monthly channel for early detection |
| Some changes are not announced through Message Center | Surprise behavior changes possible | Subscribe to Roadmap, Release Plan, and "What's new" pages |
| Connector lifecycle is independent of release waves | Deprecation can occur outside wave windows | Monitor connector reference pages monthly |
| Some changes are non-revertible by the customer | Rollback may be mitigation-only | Document realistic rollback vs. mitigation options |
| Power Apps Admin cmdlets are Desktop-only | Cannot consolidate all checks in PowerShell 7 | Run release-channel checks from a 5.1 host |
| Sovereign-cloud endpoint mismatches return false-clean | Evidence may understate exposure | Always pass `-Environment` / `-Endpoint` parameters |
| `releaseChannel` property path drifts across module versions | PowerShell may report `Unknown` | Treat PPAC UI as authoritative; capture screenshot |

---

[Back to Control 2.10](../../../controls/pillar-2-management/2.10-patch-management-and-system-updates.md) | [Portal Walkthrough](portal-walkthrough.md) | [PowerShell Setup](powershell-setup.md) | [Verification Testing](verification-testing.md)

---

*Updated: April 2026 | Version: v1.6.2*
