# Troubleshooting: Control 2.21 — AI Marketing Claims and Substantiation

**Last Updated:** April 2026
**Primary Owners:** Compliance Officer (process), SharePoint Admin (list/library), Power Platform Admin (flows)
**Escalation Path:** Functional admin → AI Governance Lead → Compliance Officer → Legal Counsel

---

## Diagnostic order of operations

When a claim or workflow is not behaving as expected, work through the diagnostics in this order — each step rules out a class of cause:

1. **Item state** — confirm the list item exists and `Status` is what you expect.
2. **Flow run history** — confirm the flow triggered and check the last failed action.
3. **Approval record** — confirm an approval was created and routed to a real, active user.
4. **Permissions** — confirm the actor has the required SharePoint and Power Automate permissions.
5. **Connections** — confirm the SharePoint, Outlook, and Approvals connections in the flow are still authorized.

---

## Issue 1 — Approval workflow does not trigger

**Symptoms**

- Submitter saves a claim and changes Status to `Under Review`, but no approval is generated.
- Power Automate run history shows no recent runs, or runs marked **Skipped**.
- Approvers receive nothing.

**Diagnosis**

1. **Power Automate → My flows** — confirm the flow is **On**. Flows automatically turn off after repeated failures or after 90 days without a successful run.
2. Open the flow → **Run history** — if the trigger fires but the run is **Skipped**, the trigger condition (`Status eq 'Under Review'`) likely did not evaluate true. Common cause: the submitter saved with `Status = Draft` and never moved to Under Review.
3. Open the flow in edit view — check the trigger card for a **Trigger condition** filter and confirm the column internal name matches `ClaimStatus` (not the display name).
4. Check the SharePoint connection — re-authenticate if the connection icon shows a warning.
5. If the flow runs but no approval is generated, inspect the **Start and wait for an approval** action: the dynamic `Compliance Reviewer` field may be empty, in which case Power Automate cannot route the approval.

**Resolution**

- Set the trigger to **When an item is created or modified** with a trigger condition `@equals(triggerOutputs()?['body/ClaimStatus/Value'], 'Under Review')`.
- Provide a fallback recipient (Compliance shared mailbox or distribution group) when the per-item reviewer is empty.
- Re-authenticate connections; re-enable the flow.

---

## Issue 2 — Substantiation hyperlink returns 404 or "Access denied"

**Symptoms**

- The Substantiation File link is present but clicking returns a SharePoint not-found page or an access-denied page.

**Diagnosis**

1. Confirm the document still exists at the expected location (it may have been moved or renamed, which breaks the stored URL — SharePoint stored hyperlinks are not auto-updated).
2. Confirm the URL is fully qualified (`https://<tenant>.sharepoint.com/...`), not relative.
3. Confirm the user opening the link has at least Read access to the substantiation library. Submitters typically need Contribute to the inventory list and Read on the library — verify both.

**Resolution**

- Re-link by copying the URL from the document's **... → Copy link** dialog (use a "people in your organization can view" or scoped link consistent with firm policy).
- Where documents move frequently, consider replacing the hyperlink column with a managed metadata or lookup column tied to a stable identifier.

---

## Issue 3 — Quarterly reminders are not delivered

**Symptoms**

- Approved claims pass their Next Review Date with no reminder email.
- Scheduled flow shows no recent runs, or runs return zero items.

**Diagnosis**

1. Open the scheduled flow → **Run history**. If runs do not appear, check the recurrence schedule and confirm the flow is **On**.
2. Open the **Get items** action's run output — if the array is empty, the OData filter is too restrictive or the field internal names are wrong.
3. Confirm the OData filter uses the internal field names: `ClaimStatus eq 'Approved' and NextReviewDate le '@{addDays(utcNow(),14)}'`.
4. Confirm the **Compliance Reviewer** field is populated on the affected claims; if empty, the email recipient is null and the **Send an email** action fails silently.

**Resolution**

- Correct the OData filter and field references.
- Add a fallback recipient (Compliance group mailbox) for claims with an empty Compliance Reviewer.
- Add a top-level **Scope** with a **Configure run after** on a final notification step so failures are surfaced to the flow owner.

---

## Issue 4 — Claim stuck in "Under Review"

**Symptoms**

- Claim shows `Under Review` for days; flow run shows **Running**; no progress.

**Diagnosis**

1. Open the run → identify which **Start and wait for an approval** action is pending.
2. Confirm the assigned approver is active in the directory (not disabled, not departed).
3. The approver should check **Power Automate → Action items → Approvals**, the Microsoft 365 approval email, and the **Approvals** app in Microsoft Teams. Approvals can be claimed from any of these surfaces.
4. Power Automate approvals time out after 30 days by default; longer waits may be the result of a missed reassignment.

**Resolution**

- Reassign the approval (approval owners can reassign from the Approvals UI).
- If the approver has departed, cancel the run, set `Status = Draft`, repopulate the **Compliance Reviewer** field with a current approver, and resubmit.
- Add a periodic reminder action (e.g., **Send an email** after a Delay of 3 days inside the approval scope) to reduce missed approvals.

---

## Issue 5 — PowerShell export fails or returns an empty file

**Symptoms**

- `Export-AIClaimsReport.ps1` raises an authentication error, returns no rows, or returns rows with empty fields.

**Diagnosis**

1. Confirm PowerShell edition is **7.2 or later** — PnP.PowerShell v2 will not load on Windows PowerShell 5.1.
2. Confirm the module is loaded at the CAB-pinned version: `Get-Module PnP.PowerShell | Format-List Name, Version`.
3. Confirm the executing account has at least **Read** on the AI Governance site.
4. Confirm the executing account has at least **Read** on the AI Governance site.
5. For a list with more than 5,000 items, ensure `-PageSize 500` is set and that you are not hitting a list-view threshold caused by an unindexed filter.

**Resolution**

- Re-run with the correct PowerShell edition, pinned module version, and `-AzureEnvironment` value.
- Re-authenticate: `Disconnect-PnPOnline; Connect-PnPOnline -Url $SiteUrl -Interactive -AzureEnvironment <env>`.
- Add an index on `NextReviewDate` and `ClaimStatus` if you frequently query large historical datasets.

---

## Issue 6 — Duplicate claims

**Symptoms**

- The same claim text appears multiple times; the workflow may have triggered more than once.

**Diagnosis**

1. Sort the list by `Submission Date` and `Claim Text` to identify duplicates.
2. Inspect flow run history for duplicate triggers (a "When an item is created or modified" trigger fires on every save, which is expected — the trigger condition on `Status` should suppress duplicates).
3. Confirm the trigger condition on `Status = 'Under Review'` is in place; without it, every edit re-runs the approval flow.

**Resolution**

- Add or correct the trigger condition.
- Resolve in-flight duplicates by setting the duplicates to `Status = Withdrawn` and noting the authoritative claim ID in `Review Comments` (do **not** delete — preserve the audit trail per books-and-records expectations).
- Consider adding a Power Apps form for submission with simple duplicate detection (search the inventory by claim text on submit).

---

## Issue 7 — Retention label not applied to new uploads

**Symptoms**

- Documents uploaded to the substantiation library show no retention label in the **Details** pane, even though a Purview policy targets the library.

**Diagnosis**

1. Confirm the Purview retention label **policy** is **Published** and that its location includes the AI Governance site or specifically the substantiation library.
2. Policy propagation can take up to 24 hours after publication; check the policy's **Status** and **Last refresh** times.
3. Confirm the library has a **default retention label** set (Library settings → Apply label to items in this list or library).
4. Confirm the executing user has at least **Edit** permission on the library — readers cannot apply labels.

**Resolution**

- Set the default label on the library so new items inherit it automatically.
- Wait for policy propagation (up to 24 hours) before declaring failure.
- For pre-existing items, run a **Bulk apply label** action from the library command bar.

---

## Escalation matrix

| Issue type | First responder | Escalation 1 | Escalation 2 |
|---|---|---|---|
| Flow failure | Power Platform Admin | AI Governance Lead | Microsoft Support |
| List / library / retention | SharePoint Admin | Purview Compliance Admin | Microsoft Support |
| Permission issues | SharePoint Admin | Entra Security Admin | IT Director |
| Disputed claim content | Compliance Officer | Legal Counsel | Chief Compliance Officer |
| Regulatory interpretation | Legal Counsel | External Counsel | Applicable regulator |
| Urgent claim blocking marketing | Compliance Officer | Legal Counsel | CCO + General Counsel |

---

## Known limitations

| Limitation | Workaround | Status |
|---|---|---|
| Power Automate approval default timeout (30 days) | Add periodic reminder inside approval scope; reassign on time-out | By design |
| SharePoint hyperlink columns do not track moved/renamed files | Use Library command bar **Copy link** when relinking; consider managed metadata | By design |
| Out-of-the-box list does not enforce duplicate detection | Add a Power Apps submission form with pre-submit lookup | Future enhancement |
| Retention label policy propagation can take up to 24 hours | Schedule label changes outside change-window cutoffs | By design |
| Mobile experience for the Approvals app may differ from desktop | Use the Approvals app in Teams on supported devices | Microsoft platform behavior |

---

## Support contacts (template)

| Role | Responsibility | Contact |
|---|---|---|
| Compliance Officer | Claim review, regulatory questions | _compliance@example.com_ |
| AI Governance Lead | Technical accuracy validation | _ai-governance@example.com_ |
| SharePoint Admin | List, library, retention configuration | _sharepoint-support@example.com_ |
| Power Platform Admin | Flow configuration and run-history triage | _powerplatform@example.com_ |
| Purview Compliance Admin | Retention labels and policies | _purview-support@example.com_ |
| Legal Counsel | Regulatory interpretation; high-risk claims | _legal@example.com_ |

---

[Back to Control 2.21](../../../controls/pillar-2-management/2.21-ai-marketing-claims-and-substantiation.md) | [Portal Walkthrough](portal-walkthrough.md) | [PowerShell Setup](powershell-setup.md) | [Verification & Testing](verification-testing.md)
---

*Updated: May 2026 | Version: v1.6.2 | UI Verification Status: Current*
