# Troubleshooting: Control 1.18 — Application-Level Authorization and RBAC

**Last Updated:** May 2026

This playbook covers operational issues commonly encountered when implementing or operating Control 1.18 (Application-Level Authorization and RBAC). Issues are grouped by symptom area; each entry includes diagnostic steps, root cause guidance, and resolution actions appropriate for an FSI environment.

---

## Quick-Reference Issue Matrix

| Symptom area | Likely root causes |
|--------------|--------------------|
| User has more access than expected | Direct role assignment bypassing groups; cumulative role membership; legacy security role |
| User has less access than expected | Group-to-team sync delay; missing field-security profile; missing Dataverse user record |
| PIM activation fails | Missing P2 license; no approver assigned; conflicting Conditional Access; MFA registration gap |
| Column-level security not enforced | Column security not enabled on the column; profile not assigned; cached UI |
| Access reviews stalled | Owners not configured; reviewer scope misaligned with group membership |
| Service principal denied | SPN missing application user record in Dataverse; rotated credential not propagated |
| Connected agent unexpectedly invocable | Connected agents preview re-enabled by maker; environment-level setting overrides agent-level |

---

## Issue Group 1 — Permission Drift

### User has more access than expected

**Symptoms:** A user with an `FSI - Agent Viewer` role is able to publish or modify agents, or sees configuration surfaces that should be hidden.

**Diagnostic steps**

1. In PPAC > Environments > [env] > Settings > Users + permissions > **Users**, locate the user and review **all** assigned roles (not just the FSI role).
2. Run the bootstrap validation export (`Export-SecurityRoles.ps1`) and inspect for **direct user assignments** (PrincipalType = User assigned to admin or maker roles outside the FSI naming convention).
3. Check Entra group membership in case the user is in `SG-PowerPlatform-Admins-Prod` as well as `SG-CopilotStudio-Viewers-Prod`.
4. Inspect Dataverse team memberships (Settings > Teams) for legacy team assignments such as `Default Team` with elevated privileges.

**Resolution**

- Remove direct role assignments; replace with the appropriate FSI security group.
- Remove the user from any group whose role exceeds their need-to-know.
- Disable the legacy team or remove its over-privileged role.
- File a role-change event in the audit trail and trigger an off-cycle access review for the impacted environment.

### User cannot perform actions their role should allow

**Symptoms:** A newly added member of `SG-CopilotStudio-Makers-Prod` cannot create an agent.

**Diagnostic steps**

1. Confirm the user has signed out and back in since being added to the group. Microsoft Entra access tokens have an approximate 60–90 minute default lifetime; group-membership changes are not reflected until a new access token is issued. Forced sign-out / sign-in (or `Revoke-MgUserSignInSession`) refreshes the membership claim immediately.
2. In Entra, confirm group membership is **active** (PIM-for-Groups eligible-not-active = no permissions).
3. In PPAC, confirm the **Dataverse team** linked to the group exists and has the FSI custom role assigned. Group-only assignment without a linked Dataverse team is the most common cause.
4. Confirm the user has a Dataverse **application user / system user** record. Users added to an Entra group but not provisioned into the Dataverse environment will not appear (or will appear as Disabled) in the PPAC Users list for that environment. Force provisioning via PPAC > Settings > Users > **+ Add users**.

**Resolution**

- Re-link the group to a Dataverse team via PPAC > Settings > Teams > **+ Create team** (Type = Microsoft 365 group or Microsoft Entra ID security group).
- Assign the FSI custom role to the team (not to individual users).
- Force token refresh: have the user sign out, clear browser cache, sign back in.
- For Dataverse user provisioning, run the standard "Users" sync from PPAC > Settings > Users > **+ Add users**.

### Role appears assigned but takes effect inconsistently

**Symptoms:** Permission changes propagate for some users but not others.

**Diagnostic steps**

1. Check the Entra group writeback / sync status for the affected directory.
2. Confirm the group is **assigned**, not **dynamic**. Dynamic groups recompute membership asynchronously after attribute changes; processing is typically complete within minutes, but Microsoft does not commit to a hard SLA. Document the local-tenant 95th-percentile observation in the operator runbook rather than asserting a fixed window.
3. Inspect Dataverse cache by viewing the user's effective permissions in PPAC.

**Resolution**

- For dynamic groups, wait or trigger a `Update-MgGroup` membership refresh.
- For PIM-for-Groups assignments, confirm activation is current (not just eligible).
- Allow up to 60 minutes for cross-service propagation; document the propagation delay in the operator runbook.

---

## Issue Group 2 — PIM Activation Failures

### PIM activation request returns "Not eligible"

**Symptoms:** User attempts to activate a privileged role and receives "You are not eligible for this role".

**Diagnostic steps**

1. Confirm the user has an **Entra ID P2** license assigned (PIM eligibility requires P2 per assigned user).
2. In Entra > PIM > Groups (or Roles) > **Assignments** > **Eligible**, confirm the user appears.
3. Confirm eligibility is via direct assignment to the role-assignable group; nested-group eligibility is not consistently supported by PIM-for-Groups and may be the cause of the "Not eligible" response.

**Resolution**

- Assign Entra ID P2 to the user.
- Add the user to the eligible-assignment list with the documented justification and expiration.
- Wait 5–10 minutes for the eligibility cache to refresh, then retry activation.

### PIM activation hangs at "Awaiting approval"

**Symptoms:** Activation request is stuck pending approval.

**Diagnostic steps**

1. In PIM > Approve requests, confirm the configured approvers exist and are active accounts (not soft-deleted).
2. Check whether the approval notification reached the approvers (Outlook, Teams).
3. Inspect the role/group **Settings** for an "Approval required" misconfiguration that targets an empty group.

**Resolution**

- Reassign approvers to a security group that contains at least two named individuals (avoid single points of failure).
- For Zone 3, configure **at least two approvers** to support the FINRA 3110 supervisory pattern and prevent single-approver bottlenecks.
- If the original approval is stuck, the requester can cancel and resubmit after the approver list is corrected.

### PIM activation succeeds but Power Platform still denies

**Symptoms:** PIM shows the role as **Active**, but PPAC actions still fail.

**Diagnostic steps**

1. Confirm the activation is for the correct directory role (Power Platform Admin, AI Administrator) **and**/or the correct group used for environment access.
2. Check Conditional Access policies that may be blocking the session token (e.g., a CA policy requiring a compliant device that the activation device does not meet).
3. Inspect the Entra sign-in log for the user and look for `Conditional Access Result = Failure`.

**Resolution**

- Adjust Conditional Access exclusions for break-glass scenarios per Control 1.11, **never by removing the policy**.
- Have the user sign out and re-authenticate to refresh the session token containing the activated role claim.
- For environment-scope access, confirm PIM-for-Groups (not PIM for directory roles) is the activation path.

### PIM activation requires MFA but user has no method registered

**Symptoms:** Activation prompts for MFA, user cannot complete the challenge.

**Diagnostic steps**

1. In Entra > Users > [user] > **Authentication methods**, confirm at least one phishing-resistant method is registered.
2. Check tenant Authentication Methods policy for required strengths.

**Resolution**

- Have the user complete authentication-method registration via [https://aka.ms/mfasetup](https://aka.ms/mfasetup) using a non-privileged session.
- For Zone 3, require phishing-resistant methods (FIDO2 / Windows Hello for Business / certificate-based) per Control 1.11.

---

## Issue Group 3 — Column-Level Security

### Column security profile created but values still visible to all users

**Symptoms:** A field-security profile is configured, yet users without the profile still see PII values.

**Diagnostic steps**

1. Confirm the **column-level security flag** is set on the column itself (Solutions > target table > column > Advanced options > **Enable column security: On**). Without this flag the profile assignment has no effect.
2. Confirm the profile is **assigned** to a user/team, not just created.
3. Verify the user is **not** in `System Administrator` (admins bypass column security).
4. Clear cached form views (close and reopen the model-driven app or refresh the form).

**Resolution**

- Enable column security on the column, then publish customizations.
- Assign the field-security profile to the appropriate Dataverse team (preferred) or individual user.
- Remove unnecessary System Administrator memberships that are masking the test result.

### Column security degrades query performance

**Symptoms:** Views and reports referencing column-secured fields are slow.

**Diagnostic steps**

1. Identify how many columns are secured on the table.
2. Check whether secured columns appear in default views, charts, or aggregate queries.

**Resolution**

- Limit column security to the highest-sensitivity fields only (SSN/Tax ID, account number, balance, credit score, government ID).
- Remove secured columns from default views; expose them only on detail forms.
- Where masking is sufficient, prefer a calculated/formatted column rather than full column security.

---

## Issue Group 4 — Access Reviews

### Access review created but no reviewers assigned

**Symptoms:** Review is scheduled but no reviewer receives notifications.

**Diagnostic steps**

1. In Entra > Identity governance > Access reviews > [review] > **Settings**, confirm the **Reviewers** field is populated.
2. Confirm group owners exist on the target group; "Group owners" as reviewer fails silently when no owner is set.

**Resolution**

- Assign group owners to every governed group (minimum two for Zone 3).
- For Zone 3, prefer named reviewers (not "Group owners") to maintain auditable supervisory accountability per FINRA 3110.

### Access review auto-completes with "No response" → unintended removals

**Symptoms:** Users were removed from groups after a review they did not see.

**Diagnostic steps**

1. Confirm reviewer received the notification (check spam, Teams notifications).
2. Inspect the review configuration for **"If reviewers don't respond"** setting.

**Resolution**

- For Zone 1/2, consider setting the non-response action to "Take recommendations" rather than "Remove access" until a notification baseline is established.
- For Zone 3, retain "Remove access" but ensure reviewers are paged through monitored channels and reviews include a 2-week response window.
- Implement a back-out runbook for restoring removed users (audit-friendly, not silent re-add).

---

## Issue Group 5 — Service Principal and Connected-Agent Issues

### Service principal denied even after credential rotation

**Symptoms:** Automation that worked before credential rotation now returns 401/403.

**Diagnostic steps**

1. Confirm the new credential (certificate or secret) is registered on the **same** application object the SPN authenticates against.
2. In Dataverse, confirm the **Application User** record for the SPN exists in the target environment and is assigned the correct custom role.
3. Check expiration of the prior credential — ensure it has not been removed before the new one was added (overlap window).

**Resolution**

- Maintain a **credential overlap window** (minimum 7 days) when rotating SPN credentials in Zone 3.
- Re-create the Dataverse Application User record if the environment was restored or copied without it.
- Verify the SPN holds only purpose-built custom roles, not `System Administrator`.

### Connected agent unexpectedly invocable from another agent

**Symptoms:** Agent A can invoke Agent B even though Agent B's "Let other agents connect" toggle is disabled.

**Diagnostic steps**

1. Confirm the connection was not established before the toggle was disabled (existing connections may persist).
2. Check Copilot Studio tenant-level and environment-level connected-agent settings (where exposed); verify the precise toggle name against the current Power Platform admin center UI at apply-time, since the surface has been changing through the A2A GA cycle (April 2026).
3. Review the agent-to-agent invocation audit log (Power Platform admin analytics).

**Resolution**

- Remove the existing connection from Agent A's tools list.
- Set environment-level connected agents to **Disabled** as the baseline; enable per-agent only via documented exception.
- Add the offending agent connection to the connected-agent inventory (Verification & Testing Test 7) and trigger an off-cycle review.

---

## Escalation Path

1. **Power Platform Admin** — environment users, Dataverse role assignments, application users
2. **Entra Identity Governance Admin** — PIM-for-Groups, access reviews, eligibility
3. **Entra Global Admin** — security group lifecycle, conditional access policy adjustments, P2 licensing
4. **AI Governance Lead / Compliance Officer** — exception approval, attestation sign-off, examination response
5. **Microsoft Support** — platform defects, Dataverse cmdlet behaviour on Dataverse-backed environments, PIM platform issues

---

## Known Limitations

| Limitation | Impact | Workaround |
|------------|--------|------------|
| Group-to-Dataverse-team sync may take up to 60 minutes after Entra changes | New makers cannot work immediately after group assignment | Document the SLA in onboarding; pre-stage assignments before user start date |
| `Get/Set/Remove-AdminPowerAppEnvironmentRoleAssignment` cmdlets do not function on Dataverse-backed environments | PowerShell cannot directly assign Dataverse roles | Use PPAC for Dataverse role assignment; use the Dataverse Web API for read-only inventory |
| PIM-for-Groups requires Entra ID P2 per assigned user | Without P2, eligibility-based admin access is not available | License the small admin population with P2; do not attempt to substitute group-only RBAC |
| PIM activation maximum is bounded by tenant policy (default 8 hours, recommended ≤ 4 for Zone 3) | Long admin sessions require re-activation | Schedule maintenance windows that fit within the activation window |
| Column-level security adds per-record authorization checks at read time | Slow lists and reports when secured columns appear in default views, charts, or aggregate queries | Microsoft recommends limiting secured columns to the highest-sensitivity fields and avoiding their use in default views, charts, and aggregate queries; mask via formatting where possible |
| Dataverse security roles grant privileges at table granularity (Create / Read / Write / Delete / Append / Append To / Assign / Share) with depth scoping (User / Business Unit / Parent:Child BU / Organization) | Pure security-role configuration cannot enforce row-level, field-by-field discrimination | Layer column security profiles (column granularity) or business-process flow restrictions; use multiple roles assigned via different groups for finer separation |
| Connected-agent connectivity can be re-enabled at the agent level by an authorized maker; tenant- or environment-level override behavior has been changing through the A2A GA cycle (April 2026) | Risk of cross-agent data flow re-emerging | Quarterly inventory (Test 7); verify tenant- and environment-level controls against current Copilot Studio governance documentation at apply-time; audit changes via SIEM |

---

[Back to Control 1.18](../../../controls/pillar-1-security/1.18-application-level-authorization-and-role-based-access-control-rbac.md) | [Portal Walkthrough](portal-walkthrough.md) | [PowerShell Setup](powershell-setup.md) | [Verification Testing](verification-testing.md)

---

*Updated: May 2026 | Version: v1.6.2 | UI Verification Status: Current*
