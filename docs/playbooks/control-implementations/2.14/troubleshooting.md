# Troubleshooting: Control 2.14 — Training and Awareness Program

**Last Updated:** April 2026

This playbook lists the issues most commonly encountered when operating Control 2.14, with diagnostic steps that respect FSI evidence requirements (no silent fixes; capture before/after state).

---

## Quick Reference

| Issue | Likely Cause | First Action |
|---|---|---|
| Training content not visible in Viva Learning | Source not enabled, ingestion pending, or permissions wrong | Confirm source enabled; wait 24 h; verify M365 Group / Security Group permissions |
| User missing from roster (Script 1) | User holds the role indirectly via group; or holds a non-listed role | Inspect role membership; add the role to `$inScopeRoles` if appropriate |
| User present in roster but flagged Not Completed | Mail mismatch between Entra and LMS; LMS export filter wrong | Reconcile on UPN as well as Mail; check `RequiredCourseId` filter |
| Compliance script returns 0% | LMS export has wrong column names or non-ISO dates | Validate header row; parse `CompletionDateUtc` with `InvariantCulture` |
| Reminder script sends 0 mails despite users in CSV | Run with `-WhatIf` (intentional); or sender lacks `Mail.Send` consent | Re-run without `-WhatIf` after sender consent confirmed |
| Approval workflow not blocking non-compliant makers | Lookup step missing or wired to wrong list | Inspect the Power Automate run history; verify the LMS lookup step |
| Retention policy not applied to training evidence | Policy scope omitted the SharePoint site / mailbox | Extend retention policy scope; trigger a re-evaluation |

---

## Detailed Issues

### Issue 1 — Training Content Not Visible to Users

**Symptoms:** A pilot user opens Viva Learning and cannot find the firm's content.

**Diagnostics:**

1. Confirm the SharePoint source is enabled in **Teams admin center > Viva > Viva Learning > Content sources**.
2. Confirm the SharePoint site uses **Microsoft 365 Group** or **Security Group** permissions. Viva Learning ingestion ignores user-direct permissions.
3. Confirm time elapsed since upload exceeds **24 hours** (basic license). Premium accelerates the cycle but is not instant.
4. Confirm the file count on the source library does not exceed the basic-license ceiling (~1,000 files).
5. Confirm supported file types — `.docx`, `.pptx`, `.xlsx`, `.pdf`, `.mp4`, `.mov`, `.avi`, `.m4a`, `.mp3`. Other types are skipped silently.

**Resolution:**

- Re-permission the SharePoint library using a group, then wait 24 h.
- For files exceeding the ceiling, segment into multiple sources or move to premium licensing.
- For unsupported types, host on SharePoint as URL-linked content or convert to a supported type.

---

### Issue 2 — Users Missing from the In-Scope Roster

**Symptoms:** Script 1 returns fewer users than expected; a user known to be a Power Platform admin does not appear.

**Diagnostics:**

1. In the Entra admin center, open the missing user and check **Assigned roles**.
2. If the user holds the role via **PIM-eligible** (not active) assignment, `Get-MgDirectoryRoleMember` returns only **active** members. Use `Get-MgRoleManagementDirectoryRoleEligibilityScheduleInstance` to enumerate eligible holders if your firm's policy treats eligible holders as in scope for training.
3. If the user holds the role via group membership, `Get-MgDirectoryRoleMember` returns the **group** as the member, not the underlying user. Recursively expand groups when building the roster.

**Resolution:**

- Decide explicitly whether PIM-eligible-only users are in scope; document the decision.
- Extend Script 1 to expand groups (`Get-MgGroupMember`) where role assignment is via group.

---

### Issue 3 — Compliance Script Reports 0% or Wrong Numbers

**Symptoms:** Script 2 runs but reports either 0% compliant or numbers that do not match the LMS dashboard.

**Diagnostics:**

1. Confirm the LMS export has the columns the script expects: `Mail`, `CourseId`, `CompletionDateUtc`. Column-name drift between LMS releases is a frequent cause.
2. Confirm `-RequiredCourseId` matches the LMS course code exactly (case-sensitive in some LMS exports).
3. Open the export in a text editor (not Excel — Excel reformats dates) and confirm `CompletionDateUtc` is in ISO-8601 (`2026-04-15T14:30:00Z`).
4. Confirm join key. The script joins on `Mail`, falling back to UPN. If your LMS uses employee ID, extend the script with a join table.

**Resolution:**

- Realign the LMS export schema with the script (or vice versa) and document the canonical schema in Control 2.13.
- Standardize on UTC ISO-8601 dates in the export pipeline.

---

### Issue 4 — Reminders Send to the Wrong People (or Don't Send)

**Symptoms:** Script 3 either sends to users who are compliant, or sends nothing.

**Diagnostics:**

1. Confirm the input CSV is **filtered** to `Status -ne 'Compliant'` before passing to Script 3. The script does not re-filter.
2. Confirm `-WhatIf` is **not** present on the production run.
3. Confirm the sender mailbox (`-SenderUpn`) is licensed for Exchange Online and the calling identity has consented `Mail.Send` (delegated or application).
4. Inspect the reminder log CSV produced by the script — every recipient appears with `Sent`, `WhatIf`, or `Error: ...`.

**Resolution:**

- Pre-filter the CSV in PowerShell before passing it in.
- For application-permission `Mail.Send`, scope the application to a single mailbox using an Exchange Online application access policy to limit blast radius.

---

### Issue 5 — Approval Workflow Does Not Block Non-Compliant Makers

**Symptoms:** Makers without a current training completion can still publish in Zone 3.

**Diagnostics:**

1. There is **no native PPAC or Copilot Studio toggle** for "require training to publish." This is process-only — implemented in your approval Power Automate flow. Confirm the flow exists and is wired to the right environments.
2. Inspect the most recent approval run history. The flow should have a step that queries the LMS (or the latest `training-compliance-*.json`) and short-circuits the approval if the maker is `Expired` or `NotCompleted`.
3. Confirm the data the flow reads from is fresh. A daily refresh is typical; longer staleness creates audit findings.

**Resolution:**

- If the flow is missing, build it. Reference the cross-link from Control 2.4 / 2.12.
- If the flow exists but the lookup is broken, fix and add a unit-test step that submits a known non-compliant test user.

---

### Issue 6 — Retention Policy Did Not Apply to Training Evidence

**Symptoms:** A Purview content search shows training evidence but retention status reads "no policy applied."

**Diagnostics:**

1. In the Microsoft Purview portal, open **Data Lifecycle Management > Policies** and select the relevant retention policy.
2. Confirm the policy scope **includes** the SharePoint site hosting the learning content and any mailbox receiving LMS-generated notifications.
3. Confirm the policy is **on** (not in simulation / test mode).
4. For SEC 17a-4(f) WORM, confirm a **records label** with **mark items as records (regulatory)** is applied — a retention policy alone does not provide WORM lock.

**Resolution:**

- Extend the retention policy scope; allow up to 7 days for full propagation.
- Add or apply the records label to the relevant locations.
- Document the scope and label in Control 2.13 evidence.

---

## Known Limitations (As of April 2026)

| Limitation | Impact | Workaround |
|---|---|---|
| No native "training-required" gate in PPAC or Copilot Studio | Cannot enforce in-platform; relies on approval-flow process | Implement check in the Power Automate approval flow |
| Viva Learning ingestion delay (~24 h basic) | New content not immediately visible | Plan releases ahead of training assignment |
| SharePoint source file ceiling on basic licensing | Very large catalogs require segmentation | Multiple SharePoint sources, or upgrade to premium |
| Viva Learning Graph APIs are beta | Not audit-defensible as system of record | Use LMS export as system of record, countersigned by LMS owner |
| `Get-MgDirectoryRoleMember` does not recurse groups or list eligible PIM holders | Roster may miss users | Extend script to expand groups and query PIM eligibility |
| LMS connector data sync 24–48 h | Dashboards can lag actual completions | Set examiner-facing reports against the LMS, not Viva Learning |

---

## Escalation Path

1. **AI Administrator** — Curriculum scope, M365 Copilot / agent governance alignment
2. **Knowledge Admin** — Viva Learning content sources and ingestion
3. **Power Platform Admin** — Approval workflow and environment configuration
4. **Purview Compliance Admin** — Retention, records labels, examination evidence
5. **LMS owner / vendor support** — LMS-side data quality, connector failures
6. **Compliance / Legal** — Interpretation of FINRA / SEC obligations and curriculum sufficiency

---

[Back to Control 2.14](../../../controls/pillar-2-management/2.14-training-and-awareness-program.md) | [Portal Walkthrough](portal-walkthrough.md) | [PowerShell Setup](powershell-setup.md) | [Verification & Testing](verification-testing.md)
---

*Updated: May 2026 | Version: v1.6.2 | UI Verification Status: Current*
