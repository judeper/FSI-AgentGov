# Troubleshooting: Control 2.23 - User Consent and AI Disclosure Enforcement

**Last Updated:** April 2026

This playbook addresses the most common failure modes encountered when implementing or operating Control 2.23. Each issue lists symptoms, likely root causes, and resolution steps that admins can execute without escalation. Escalation paths are at the bottom.

---

## Issue 1 — `Copilot AI disclaimer` setting is not visible in the admin center

**Symptoms**
- The path **Copilot → Settings → View all** does not show a `Copilot AI disclaimer` row.
- The signed-in admin sees other Copilot settings but not this one.

**Likely root causes**
1. Signed-in admin lacks the **AI Administrator** role (older Global Admin sessions sometimes cache without the new scope).
2. Tenant has not yet received the rollout (verify against Message Center).
3. Tenant has no Microsoft 365 Copilot or Copilot Chat licenses.

**Resolution**
1. Confirm role assignment:
   ```powershell
   Connect-MgGraph -Scopes 'RoleManagement.Read.Directory','User.Read.All' -NoWelcome
   $me = Get-MgUser -UserId (Get-MgContext).Account
   Get-MgUserMemberOf -UserId $me.Id |
       Where-Object { $_.AdditionalProperties.'@odata.type' -eq '#microsoft.graph.directoryRole' } |
       Select-Object @{n='Role';e={$_.AdditionalProperties.displayName}}
   ```
   Verify `AI Administrator` is present. If not, request assignment (preferred over reusing Global Admin).
2. Pull rollout evidence: run `Get-AIDisclaimerRolloutEvidence.ps1` from the PowerShell Setup playbook.
3. If the rollout has reached your region but the row is still missing, raise a Microsoft 365 admin support ticket and attach the Message Center IDs.

---

## Issue 2 — Custom disclosure URL tooltip does not appear

**Symptoms**
- Disclaimer text renders but the info icon shows no tooltip, or the tooltip shows only the default Microsoft text.

**Likely root causes**
1. Custom URL field saved with leading/trailing whitespace or without `https://`.
2. Browser cached the previous (no-URL) policy state.
3. URL points to a host that returns a non-2xx status.

**Resolution**
1. Re-open the policy and re-paste the URL — the field accepts only well-formed absolute URLs starting with `https://`.
2. Validate reachability:
   ```powershell
   Invoke-WebRequest -Uri 'https://contoso.com/policies/ai-transparency' -UseBasicParsing |
       Select-Object StatusCode, StatusDescription
   ```
3. Clear browser cache for `*.cloud.microsoft` and `*.office.com`, then re-test in InPrivate.

---

## Issue 3 — Agent does not display the disclosure on conversation start

**Symptoms**
- The Conversation Start topic was edited and saved, but live conversations show no disclosure.

**Likely root causes**
1. Agent was saved but not **published**.
2. The maker is testing inside the unpublished Test pane while end-users are hitting the published version.
3. A custom topic with a `Conversation start` trigger is overriding the system topic.

**Resolution**
1. Click **Publish** in the agent canvas. Wait 30–120 seconds, then test in a fresh client (Teams desktop or web).
2. In **Topics → System**, confirm `Conversation Start` is enabled. In **Custom**, search for any topic with a `Conversation start` trigger and reconcile (typically by disabling the custom one).
3. Verify the channel binding in **Channels** matches where you are testing.

---

## Issue 4 — Consent rows not appearing in `fsi_aiconsents`

**Symptoms**
- Users acknowledge consent (`Yes`) but no Dataverse rows are created, or rows appear sporadically.

**Likely root causes**
1. The `Log-AIConsent` flow is failing silently (Microsoft Copilot Studio swallows action errors unless the topic is configured to react).
2. The flow's connection uses a personal account that has lost permission to the table.
3. Service principal lacks `Create` on `fsi_aiconsents` (typo in the security role).
4. Required column missing a value (Dataverse rejects writes when a required column is null).

**Resolution**
1. Open the flow's run history (Power Automate → My flows → `Log-AIConsent` → 28-day run history) and inspect the most recent failure. Common errors:
   - `401 Unauthorized` → re-authenticate or rotate the service principal credential.
   - `403 Forbidden` → security role missing or application user disabled.
   - `400 Bad Request: A required field is missing` → check the column mapping; required columns must always receive a non-empty value.
   - `404 Not Found` → wrong table name or environment.
2. Verify the Dataverse application user is enabled and bound to the restricted security role:
   - Power Platform admin center → Environment → **Settings → Users + permissions → Application users**.
3. Add an explicit **try / catch** around the Dataverse action so the topic can route the user to the contact path on failure (currently failures often produce a successful-looking conversation with no audit trail).

---

## Issue 5 — Purview unified audit log returns no consent events

**Symptoms**
- `Search-DisclosureAuditEvidence.ps1` returns zero rows even after configuration changes and consent acknowledgments.

**Likely root causes**
1. Unified audit log ingestion is disabled for the tenant.
2. Insufficient time has elapsed for indexing (events can take up to 60 minutes; some Power Platform events up to 24 hours).
3. The signed-in account lacks audit permissions.
4. Search keywords do not match the operation strings present in your tenant.

**Resolution**
1. Confirm ingestion:
   ```powershell
   Connect-ExchangeOnline -ShowBanner:$false
   Get-AdminAuditLogConfig | Select-Object UnifiedAuditLogIngestionEnabled
   ```
   If `False`, enable (requires Exchange Administrator):
   ```powershell
   Set-AdminAuditLogConfig -UnifiedAuditLogIngestionEnabled $true
   ```
2. Wait 60 minutes after a configuration change, then re-run the search with a longer window:
   ```powershell
   Search-UnifiedAuditLog -StartDate (Get-Date).AddDays(-2) -EndDate (Get-Date) -ResultSize 5000 -RecordType PowerAppsApp,PowerAutomateFlow,MicrosoftFlow
   ```
3. Confirm role: **Purview Audit Reader** (or higher) is required for `Search-UnifiedAuditLog`.
4. If you cannot find a tenant-policy change event, fall back to Microsoft 365 admin center **Activity reports** → search for the admin's UPN around the change time.

---

## Issue 6 — Disclaimer missing on Microsoft Teams mobile

**Symptoms**
- Disclaimer renders in Teams desktop and web but not in Teams mobile.

**Likely root causes**
1. Mobile app version is older than the rollout build.
2. Mobile client is signed in to a different tenant profile than the test admin.

**Resolution**
1. Update the Teams mobile app from the App Store (iOS) or Google Play (Android).
2. Sign out and sign back in as the test user.
3. If the disclaimer still does not render, document the gap and use the agent-level disclosure (Conversation Start topic) as the compensating control. Open a Microsoft support ticket referencing the Message Center post for the disclaimer rollout.

> **Do not** instruct users to enable hidden "developer feature flags" on the Teams mobile app — those flags are not a supported configuration surface and must not be relied on for compliance evidence.

---

## Issue 7 — Custom disclosure URL fails for guest users

**Symptoms**
- Internal users can open the AI policy link; guest accounts get a sign-in loop or `Access denied`.

**Likely root causes**
1. The policy lives on a SharePoint site that disallows external sharing.
2. Conditional Access blocks guest access to the host site.

**Resolution**
1. Move the AI policy to a public-facing page (recommended: `https://www.<company>.com/ai-policy`) hosted outside SharePoint, OR
2. Move it to a SharePoint site whose sharing setting is at least **New and existing guests** and grant guests **Read** at the page level. Avoid `Anyone with the link` for FSI tenants — it bypasses Conditional Access.
3. Review the relevant Conditional Access policy:
   ```powershell
   Connect-MgGraph -Scopes 'Policy.Read.All' -NoWelcome
   Get-MgIdentityConditionalAccessPolicy |
       Where-Object { $_.Conditions.Applications.IncludeApplications -contains '00000003-0000-0ff1-ce00-000000000000' } |
       Select-Object DisplayName, State
   ```
   Coordinate with the policy owner before adjusting scope.

---

## Issue 8 — Consent expiration logic does not trigger re-acknowledgment

**Symptoms**
- Consent rows older than 90 days exist for active Zone 3 users, yet those users are never re-prompted.

**Likely root causes**
1. The `Check-AIConsent` flow is returning `consentValid = Yes` regardless of timestamp (logic bug).
2. The agent's Conversation Start topic does not call `Check-AIConsent` before the disclosure decision.
3. The OData filter ignores time zones (always store and compare in UTC).

**Resolution**
1. Open `Check-AIConsent`, inspect the **List rows** filter and the post-query expression. The age check should be:
   ```
   div(sub(ticks(utcNow()), ticks(outputs('List_rows')?['body/value'][0]?['fsi_consenttimestamp'])), 864000000000)
   ```
   (returns whole days). Compare against `90`.
2. Confirm the agent's Conversation Start topic calls `Check-AIConsent` first and only renders the consent question when `consentValid = No`.
3. Backdate a record (per Verification Test 7) and re-run end-to-end.

---

## Issue 9 — Zone 3 disclosure language fails compliance review

**Symptoms**
- Compliance flags missing elements (data location, retention period, contact paths, etc.) during review.

**Required Zone 3 elements (checklist)**
1. Explicit AI identification ("I'm an AI assistant…")
2. Statement that AI responses must be reviewed before action
3. Retention period and supervisory-review notice (FINRA 3110, SEC 17a-4)
4. Privacy contact for data access / deletion requests (GLBA 501(b))
5. Compliance contact for AI-usage concerns
6. Link to the full AI policy with a current `Last Updated` date
7. Explicit acknowledgment question

**Resolution**
1. Use the Zone 3 template from Portal Walkthrough Step 6 verbatim, then customize the bracketed tokens.
2. Route through the standing approval workflow: Legal → Compliance → AI Governance Lead. Record the approval decision and the resulting `DisclosureVersion` in the governance documentation system.
3. After publishing, run Verification Test 3 to confirm the rendered text matches the approved version exactly.

---

## Issue 10 — Beta Graph endpoint for tenant disclaimer policy does not behave as documented

**Symptoms**
- Scripts that target `https://graph.microsoft.com/beta/admin/copilot/settings` return `404`, `401`, or unstable shapes.

**Likely root causes**
1. The endpoint is in private preview and not enabled for your tenant.
2. The shape changes between preview revisions.

**Resolution**
1. Do **not** rely on this endpoint for production governance evidence. Treat the admin-center UI as authoritative until a GA endpoint ships.
2. Use the Message Center evidence script (`Get-AIDisclaimerRolloutEvidence.ps1`) to demonstrate awareness of rollout state, and the audit log evidence script for change history.
3. Track the GA announcement on the [Microsoft 365 Roadmap](https://www.microsoft.com/en-us/microsoft-365/roadmap) and the [Microsoft Graph changelog](https://learn.microsoft.com/en-us/graph/whats-new-overview).

---

## Escalation Paths

| Issue type | Escalate to | Evidence to attach |
|---|---|---|
| Tenant policy missing or rolled-back unexpectedly | Microsoft 365 admin support (Sev B) | Message Center IDs, screenshots, admin role list |
| Power Automate flow systemic failure | Power Platform admin → Microsoft Power Platform support | Flow run IDs, request/response payloads, environment ID |
| Audit log gap exceeding 24 h | Purview Compliance Admin → Microsoft Purview support | `Get-AdminAuditLogConfig` output, search query, date range |
| Regulatory question | AI Governance Lead → Chief Compliance Officer | Disclosure version, approval record, evidence bundle |

---

## Additional Resources

- [Microsoft Learn: Turn on AI Disclaimers in Microsoft 365 Copilot](https://learn.microsoft.com/en-us/microsoft-365/copilot/microsoft-365-ai-disclaimers)
- [Microsoft Learn: Manage Microsoft 365 Copilot Scenarios](https://learn.microsoft.com/en-us/microsoft-365/copilot/microsoft-365-copilot-page)
- [Microsoft Learn: Search the audit log in the Microsoft Purview portal](https://learn.microsoft.com/en-us/purview/audit-search)
- [Microsoft Learn: Power Automate run-history troubleshooting](https://learn.microsoft.com/en-us/power-automate/fix-flow-failures)
- [Microsoft 365 Roadmap](https://www.microsoft.com/en-us/microsoft-365/roadmap)

---

[Back to Control 2.23](../../../controls/pillar-2-management/2.23-user-consent-and-ai-disclosure-enforcement.md) | [Portal Walkthrough](portal-walkthrough.md) | [PowerShell Setup](powershell-setup.md) | [Verification Testing](verification-testing.md)
---

*Updated: May 2026 | Version: v1.6.2 | UI Verification Status: Current*
