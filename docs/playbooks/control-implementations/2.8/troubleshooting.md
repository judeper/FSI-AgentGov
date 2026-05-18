# Troubleshooting: Control 2.8 — Access Control and Segregation of Duties

**Last Updated:** April 2026
**Audience:** M365 administrators in US financial services

---

## Quick Reference

| Issue | Likely cause | First-line resolution |
|---|---|---|
| `New-MgGroup` returns `Insufficient privileges to complete the operation` when creating role-assignable group | Caller is not Privileged Role Admin or Global Admin | Sign in with **Entra Privileged Role Admin** (role-assignable group creation requires this role) |
| PIM activation fails with `RoleAssignmentRequestPolicyValidationFailed` | Required justification, ticket field, or approver workflow not satisfied | Re-submit with all required fields; verify approver group has at least one online, non-conflicting member |
| SoD detector reports overlap that operationally must exist | Sandbox / non-production exception | Document in SoD exception register with expiry; suppress only by environment scope, never globally |
| Power Automate SoD flow not triggering on publish | Trigger context is the maker's personal environment, not the production-aligned environment | Move flow to a shared service-account-owned environment; redeploy via solution |
| Access Review never closes | Reviewer left the organisation; no fallback reviewer set | Set Identity Governance Admin as fallback reviewer; configure **If reviewer doesn't respond → Remove access** for privileged reviews |
| Dataverse role assignment "succeeds" but user still can't see records | Role bound to user directly instead of via group team | Re-bind via **Group team** so membership tracks the SG-Agent-* group |
| `Get-MgGroupTransitiveMember` returns 0 for a group that clearly has members | Delegated scope `Group.Read.All` not consented, or app-only context lacks `GroupMember.Read.All` | Re-run `Connect-MgGraph` with the correct scopes; for app-only, grant admin consent |

---

## Detailed Issues

### Issue: Cannot create a role-assignable group

**Symptoms:** Portal greys out the **Microsoft Entra roles can be assigned to the group** toggle, or PowerShell returns `Authorization_RequestDenied`.

**Diagnosis:**

1. Confirm the signed-in caller holds **Privileged Role Administrator** or **Global Administrator**. Group Administrator is **not** sufficient.
2. Confirm the tenant has **Microsoft Entra ID P1 or P2** licensing (role-assignable groups require P1 minimum).

**Resolution:**

- Activate Privileged Role Admin via PIM, then retry.
- The role-assignable flag **cannot be changed after creation**; if the group already exists without the flag, create a new role-assignable group and migrate membership.

---

### Issue: SoD detector reports a violation that the business says is acceptable

**Symptoms:** A user appears in two conflicting groups (e.g., Developer + Approver) but the business owner argues they are the only qualified person.

**Resolution path (do not silently exempt):**

1. Open a SoD exception ticket. Required fields: user UPN, conflicting groups, business justification, compensating control, expiry date (max 90 days), Compliance Officer approval.
2. Add the user to a tracked exception group (e.g., `SG-Agent-SoD-Exceptions`) and update the SoD detector script's allow-list to exclude **only** the (UserId, GroupA, GroupB) triple — not blanket the user.
3. Schedule a quarterly review of every exception. Expired exceptions auto-fail the next detector run.
4. Where the exception is required because no second qualified individual exists, treat the underlying staffing gap as the **root cause** and track remediation.

> Never exempt by removing the conflict pair from the matrix — that hides the issue from examiners.

---

### Issue: PIM activation fails for `SG-Agent-Approvers` or `SG-Agent-ReleaseManagers`

**Symptoms:** User attempts to activate via PIM for Groups; activation errors with `RoleAssignmentScheduleRequest_ApprovalRequired_NoApprovers`.

**Diagnosis:**

- The configured approver list resolves to zero eligible-and-available approvers (e.g., everyone in the approver group is the requester themselves, or all approvers are out of office and no fallback is configured).

**Resolution:**

1. Configure at least **two** approvers per privileged group, drawn from a pool that does not overlap with typical requesters.
2. Add a **fallback approver** in PIM settings (Compliance Officer is a good default).
3. For after-hours coverage, document the break-glass identity path in your IR runbook — do not work around PIM by adding standing Active assignments.

---

### Issue: Power Automate SoD flow does not fire on agent publish

**Symptoms:** Maker publishes an agent; the production deploy occurs without the approval task appearing.

**Diagnosis checklist:**

1. Is the flow's trigger bound to the **production-aligned environment**, not the maker's default environment? Triggers in the maker environment will never see production-publish events.
2. Is the flow **enabled**? Check **Power Automate → My flows → Production-Aligned environment**.
3. Is the flow's connection owned by a **service account**? Maker-owned connections can break when the maker's session expires or when the maker is offboarded.
4. Did the publish path bypass the flow? Some pipeline tools (e.g., direct ALM Accelerator deployment) require explicit gate configuration.

**Resolution:**

- Move the flow to the production-aligned environment and add it to a managed solution.
- Convert connections to **service-account-owned** (or, where supported, **service-principal-owned**).
- Add a Defender for Cloud Apps / Sentinel detection for any production deploy event that did not have a corresponding `agent_sod_decisions` row created within ±5 minutes.

---

### Issue: Continuous Access Evaluation does not revoke tokens promptly

**Symptoms:** A disabled user retains Power Platform access for &gt; 60 minutes.

**Diagnosis:**

1. Confirm the affected app supports CAE (Power Platform admin app, Microsoft Graph, Microsoft Copilot Studio do; some third-party apps proxied through the tenant may not).
2. Confirm the Conditional Access policy is **not** in **Report-only** mode.
3. Confirm the user signed in via a CAE-aware client (modern auth + Continuous access evaluation enabled clients).

**Resolution:**

- Switch CA policy from Report-only to **On**.
- For non-CAE-aware integrations, set short token lifetimes via Conditional Access **Sign-in frequency**.
- Where instant revocation is mandatory, use **Disable user → Revoke sessions** (`Revoke-MgUserSignInSession`) in the offboarding runbook in addition to CAE.

---

## Escalation Path

1. **Entra Admin / Privileged Role Admin** — group creation, PIM configuration, role-assignable flag, CAE policy
2. **Power Platform Admin** — Dataverse security roles, environment-level permissions, group team bindings
3. **Identity Governance Admin** — Access Reviews, PIM for Groups onboarding, exception register tooling
4. **AI Governance Lead** — SoD policy interpretation, exception decisions
5. **Compliance Officer** — Exception sign-off, regulator-facing evidence, attestation independence
6. **Microsoft Support** — Premier / Unified support for product-level issues; reference the Microsoft Learn doc URLs in the parent control

---

## Known Limitations (April 2026)

| Limitation | Impact | Mitigation |
|---|---|---|
| PIM and Access Reviews require Microsoft Entra ID P2 per user | JIT and recertification unavailable for unlicensed users | Restrict privileged groups to P2-licensed users; use Conditional Access + group-based monitoring as a fallback |
| Dataverse System Administrator sits outside the Entra group model | A user with Dataverse System Administrator can grant themselves any privilege within the environment | PIM-gate the role via PIM for Groups onto a role-assignable group team; alert on any standing assignment |
| Service principals are not subject to PIM or Access Reviews | Automated identities can bypass user-centric SoD | Quarterly service-principal inventory + Application Permissions review (Control 1.x); least-privilege application roles |
| Access Review duration capped at ~30 days | Large reviews may not complete | Split into multiple smaller reviews scoped per zone or per business unit |
| Self-approval reject in Power Automate is workflow-side, not platform-side | A maker with environment-admin rights can deploy without the flow | Combine with Dataverse System Administrator PIM gating and Power Platform DLP on the deploy connector |
| Copilot Studio author / admin separation is policy-enforced, not platform-enforced | Tenant admins can override role assignments | Detect with the SoD script and alert; treat any drift as a Sev-2 control incident |

---

[Back to Control 2.8](../../../controls/pillar-2-management/2.8-access-control-and-segregation-of-duties.md) | [Portal Walkthrough](portal-walkthrough.md) | [PowerShell Setup](powershell-setup.md) | [Verification & Testing](verification-testing.md)
---

*Updated: May 2026 | Version: v1.6.2 | UI Verification Status: Current*
