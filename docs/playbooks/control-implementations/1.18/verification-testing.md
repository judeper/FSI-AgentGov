# Verification & Testing: Control 1.18 — Application-Level Authorization and RBAC

**Last Updated:** May 2026
**Estimated Time:** 2–3 hours per environment (Zone 3); 30–60 minutes (Zone 1/2)
**Cadence:** Quarterly (Zone 3), semi-annual (Zone 2), annual (Zone 1), plus ad-hoc on role-change events

---

## Purpose

This playbook is the auditor-facing verification procedure for Control 1.18. It is structured for FINRA Rule 4511 / 3110 supervisory review, SEC 17a-4 examination evidence, and SOX 404 ICFR walkthroughs. Every test produces an artifact that can be filed in the control evidence repository.

> **Pair with the bootstrap script.** The PowerShell `Validate-Control-1.18.ps1` script confirms the bootstrap (groups + PIM eligibility). The portal-based tests in this playbook confirm the runtime enforcement of Dataverse roles, column security, agent action consent, and connected-agent restrictions, which the bootstrap script cannot verify.

---

## Verification Checklist (Auditor Quick Reference)

| # | Check | Pass criteria | Evidence artifact |
|---|-------|---------------|-------------------|
| C1 | Custom Dataverse roles exist (`FSI - Agent Publisher` / `Viewer` / `Tester`) | All three roles present in target environment with documented privileges | Screenshot + role privilege export |
| C2 | Roles assigned via groups (not direct user assignment) | Direct user-role assignments = 0 outside break-glass list | Dataverse `systemuserroles_association` export |
| C3 | Viewer role is read-only | Viewer cannot create/modify/delete agents (negative test) | Test-account screen recording or screenshots |
| C4 | PIM-for-Groups configured on admin group | Eligible assignments > 0; active assignments minimised | Entra > PIM > Groups export |
| C5 | PIM activation requires approval + MFA + justification | Test activation produces approval request and audit entry | Audit log entry + approval-workflow screenshot |
| C6 | Column-level security enforces NPI/PII restrictions | Unauthorised user sees masked or hidden values | Side-by-side test screenshots |
| C7 | Access reviews are scheduled and within cadence | Last review ≤ cadence window; next review scheduled | Entra > Identity Governance export |
| C8 | Agent action consent enabled on all published agents | Every tool on every published Zone 2/3 agent has "Ask the user before running this action" enabled | Per-agent screenshot or PPAC compliance report |
| C9 | Connected agents disabled by default | Inventory of agents with "Let other agents connect" enabled matches approved-exception list | Per-agent screenshot of Settings > Connected Agents panel, supplemented where available by per-agent metadata export via Power Platform CLI / Copilot Studio API. Microsoft does not yet publish a first-class tenant-wide connected-agent inventory report; the evidence-gathering method should be recorded explicitly in the attestation. |
| C10 | Environment admin count below threshold | < 10 environment-level System Administrators per Zone 3 environment (FSI-imposed numeric threshold; Microsoft publishes "minimize privileged admins" without a published number) | PPAC user-list export with role filter |
| C11 | Service principals not assigned admin roles | No service principal in `System Administrator` or `Environment Admin` | Filtered user-list export (Principal Type = Application) |
| C12 | Service principal credential rotation | Last credential rotation ≤ 90 days for every SPN with Power Platform access (Zone 3) | Entra app-credential export |
| C13 | Role-change events forwarded to SIEM (Zone 3) | Sentinel/SIEM contains entries for last 30 days of role assignments and PIM activations | SIEM query result export |

---

## Manual Verification Steps

### Test 1 — Viewer role is read-only (negative test)

1. Sign in as a test user assigned **only** to `SG-CopilotStudio-Viewers-Prod`.
2. Open Copilot Studio at [https://copilotstudio.microsoft.com](https://copilotstudio.microsoft.com).
3. Attempt the following actions:
   - Create a new agent → **Expected:** "+ New agent" button hidden or returns "You don't have permission" error.
   - Open an existing agent and modify a topic → **Expected:** Save / publish controls disabled.
   - Delete an agent → **Expected:** Delete option absent or denied.
4. **Evidence:** Screenshot of denied action; record test-account UPN and timestamp.

### Test 2 — PIM activation gate

1. Sign in as a test admin who is **eligible** (not active) for `SG-PowerPlatform-Admins-Prod`.
2. Without activating PIM, navigate to PPAC > Environments > [Zone 3 environment] > Settings.
3. Attempt to modify the environment (e.g., change DLP policy assignment).
4. **Expected:** Action denied or settings hidden because the eligible role is not active.
5. Activate PIM via the Entra portal: provide MFA, justification, and ticket reference.
6. **Expected:** Approval request appears for the configured approver(s); on approval, role becomes active for ≤ 4 hours.
7. **Evidence:** Approval workflow screenshot, MFA challenge timestamp, Entra audit log entry showing the PIM activation event ("Add member to role completed (PIM activation)" for directory roles, or the analogous PIM-for-Groups membership-add event) with the activator UPN, justification, and ticket reference recorded.

### Test 3 — Column-level security on PII

1. Identify a Dataverse table with a column-secured PII field (e.g., `account.creditscore`).
2. Sign in as **User A** who has the field-security profile assigned.
3. Open a record → **Expected:** PII value visible.
4. Sign in as **User B** who does **not** have the profile.
5. Open the same record → **Expected:** Field hidden, masked (`***`), or shows "No access".
6. **Evidence:** Side-by-side screenshots with timestamps and test-account UPNs.

### Test 4 — Access review cadence

1. Open Entra Admin Center > **Identity governance** > **Access reviews**.
2. Locate reviews for each FSI security group.
3. Confirm:
   - **Frequency** matches Zone requirement (Zone 3: quarterly; Zone 2: semi-annual; Zone 1: annual).
   - **Reviewers** are the group owners or designated compliance reviewers.
   - **On non-response** = "Remove access" for Zone 3 (or "Take recommendations" with documented review of recommendations).
   - **Last completed review** date is within the cadence window.
4. **Evidence:** Export the access-review series to CSV or capture a full-page screenshot showing the schedule and last completion date.

### Test 5 — Service principal admin scrub

1. In PPAC > Environments > [target] > Settings > **Users + permissions** > **Users**.
2. Filter or sort by principal type so that application users (service principals) are isolated from interactive users (the PPAC Users list exposes a principal-type column; the exact filter label may vary between releases).
3. Cross-reference any returned principals against the **System Administrator** and **Environment Admin** role membership.
4. **Expected:** Zero application principals in admin roles. Application principals should hold only purpose-built custom roles (e.g., `FSI - Service - DataReader`).
5. **Evidence:** Filtered user export (CSV) annotated with the approved SPN list.

### Test 6 — Agent action consent enforcement

1. In Copilot Studio, open each **published** agent in Zone 2/3 environments.
2. Open **Tools** and inspect each tool's "Ask the user before running this action" setting.
3. **Expected:** Setting is **Enabled** for every tool. For tools where consent is intentionally suppressed, an approved exception should exist in the agent governance log.
4. **Evidence:** Per-agent screenshot of the Tools list with consent status visible. For large estates, use the agent-inventory PowerShell export and confirm the consent flag.

### Test 7 — Connected-agent inventory

1. In Copilot Studio, open each agent in a Zone 2/3 environment.
2. Navigate to **Settings** > **Connected agents** (the multi-agent collaboration surface; verify the literal menu label at apply-time — some tenants surface this as **'Agents'** depending on UI release ring. The A2A protocol underpinning cross-agent invocation reached GA in April 2026, but the per-agent connectivity toggle may still surface a Preview label in some tenants — https://learn.microsoft.com/en-us/microsoft-copilot-studio/authoring-add-other-agents).
3. Inspect the toggle "Let other agents connect to and use this one".
4. **Expected:** Connected-agent toggle for the agent is **Disabled** unless the agent appears on the FSI-maintained approved cross-agent connectivity list (filed with the AI Governance Lead). Microsoft Copilot Studio does not surface this exception list natively; the FSI repository is the source of truth.
5. **Evidence:** Settings screenshot per agent + the current approved-exception list with sign-off dates.

---

## Audit Test Cases

| Test ID | Scenario | Expected result | Pass / Fail | Notes |
|---------|----------|-----------------|-------------|-------|
| TC-1.18-01 | Viewer cannot create agent | Action blocked | | |
| TC-1.18-02 | Eligible admin cannot perform privileged action without PIM activation | Denied until activated | | |
| TC-1.18-03 | PIM activation enforces approver + MFA + justification | Workflow + audit entry produced | | |
| TC-1.18-04 | User without column-security profile cannot read PII column | Value hidden / masked | | |
| TC-1.18-05 | Quarterly access review completed within cadence (Zone 3) | Last completion ≤ 90 days | | |
| TC-1.18-06 | No service principals in System Administrator role | Count = 0 | | |
| TC-1.18-07 | Environment admin count < 10 (Zone 3) | Count < 10 per environment | | |
| TC-1.18-08 | Agent action consent enabled on all published agents | All tools = enabled | | |
| TC-1.18-09 | Connected agents disabled or on approved list | Inventory matches approved list | | |
| TC-1.18-10 | SPN credential rotation ≤ 90 days (Zone 3) | All SPNs within window | | |
| TC-1.18-11 | Role-change events present in SIEM (Zone 3) | Last 30 days of events queryable | | |
| TC-1.18-12 | Bootstrap PowerShell `Validate-Control-1.18.ps1` exits 0 | Validation passes | | |

---

## Evidence Collection Checklist

For each evidence artifact: capture at original resolution, embed timestamp, hash with SHA-256, and store in the control evidence repository under `1.18/<YYYY-Q#>/`.

- [ ] Custom Dataverse role privilege export (one per role: Publisher, Viewer, Tester)
- [ ] Group-based role assignment matrix (`systemuser` joined to `systemuserroles_association`)
- [ ] PIM-for-Groups configuration screenshot (activation duration, approver list, MFA setting)
- [ ] PIM activation audit log sample (last quarter)
- [ ] Column security profile configuration + assignment list
- [ ] Negative-test screenshot pack (Viewer role; missing column-security profile)
- [ ] Access review schedule + last completion proof per group
- [ ] PPAC environment user export with role and principal-type columns
- [ ] Service principal credential age report
- [ ] Agent action consent inventory (per-agent or PPAC compliance report)
- [ ] Connected-agent enablement inventory + approved-exception list
- [ ] Sentinel/SIEM KQL query proof from the `AuditLogs` table filtered to `Category == "AdministrativeUnit"` (administrative-unit lifecycle and membership events) and `Category == "RoleManagement"` for PIM role-assignment activities such as `"Add member to role completed (PIM activation)"` (Zone 3) — verify the current activity-name strings against the [Entra audit activities reference](https://learn.microsoft.com/en-us/entra/identity/monitoring-health/reference-audit-activities) at apply-time, as Microsoft updates this taxonomy periodically
- [ ] Signed attestation (template below)

---

## Auditor Evidence Pack — Regulatory Mapping

When packaging evidence for an examination or internal audit, label artifacts with the regulation each one supports:

| Regulation / standard | Artifact(s) supporting the assertion |
|-----------------------|--------------------------------------|
| **FINRA 4511** — books and records integrity | Group-based role assignment matrix; access review completion proof; PIM activation audit log |
| **FINRA 3110** — supervisory procedures | Approved-exception list (connected agents); attestation; access review reviewer list |
| **FINRA RN 24-09 / Rule 3110** (guidance document — verify exact published title against finra.org; do not present as a Rule) — AI system access controls | Custom role privilege exports; agent action consent inventory; connected-agent inventory |
| **SEC 17a-3/4** — access documentation | PPAC user export; SPN credential age report; SIEM query proof |
| **SOX 302/404** — ICFR / segregation of duties | Negative-test screenshot pack; PIM approval workflow; service-principal admin scrub |
| **GLBA 501(b)** — Safeguards | Column security configuration + assignment; field-level negative test |
| **NIST SP 800-53 AC-2/AC-3/AC-5/AC-6** | Bootstrap validation script output; PIM eligibility export; access review schedule |

---

## Attestation Statement Template

```markdown
## Control 1.18 Attestation — Application-Level Authorization and RBAC

**Organization:** [Organization Name]
**Environment(s) in scope:** [PROD-NAME (Zone 3), TEAM-NAME (Zone 2)]
**Control Owner:** [Name / Role]
**Reviewer:** [Independent reviewer — must differ from operator]
**Reporting period:** [YYYY Q#]
**Attestation date:** [YYYY-MM-DD]

I attest that, for the reporting period above:

1. Custom Dataverse security roles (Agent Publisher, Viewer, Tester) are implemented with documented least-privilege scope.
2. All role assignments are made through Entra security groups; direct user-role assignments are limited to the documented break-glass account list.
3. Privileged Identity Management for Groups is enforced on the Power Platform admin group with:
   - Maximum activation: [Duration]
   - Approval required: [Yes/No, approver list]
   - MFA on activation: [Yes/No]
4. Column-level security is enforced on the documented set of NPI/PII columns; negative test (Test 3) was completed on [Date].
5. Access reviews completed on schedule for the period:
   - Zone 1: [Last completion date]
   - Zone 2: [Last completion date]
   - Zone 3: [Last completion date]
6. Agent action consent is enabled on every published agent in Zone 2/3 (or documented exceptions are filed).
7. Connected-agent enablement matches the approved-exception list as of the attestation date.
8. Service principal credentials with Power Platform access were rotated within 90 days (Zone 3).
9. Role-change events have been forwarded to [SIEM name] for the entire reporting period (Zone 3).

**Evidence pack reference:** [Repository path / SharePoint link]
**Bootstrap validation script result:** PASS / FAIL — [link to log]

**Operator signature:** _______________________  **Date:** ___________
**Reviewer signature:** _______________________  **Date:** ___________
```

---

## SSPM Configuration Verification

!!! abstract "Security Posture Assessment Test Cases"

    The following test cases validate configuration points flagged by security posture assessments. Each test maps to a specific setting in the [Configuration Hardening Baseline](../../advanced-implementations/configuration-hardening-baseline/index.md).

| Test ID | Configuration Point | Expected Result | Portal Path | Evidence |
|---------|--------------------|-----------------|-------------|----------|
| SSPM-1.18-01 | Agent tool consent | Enabled for all published agents | Copilot Studio > Agent > Tools > "Ask the user before running this action" | Per-agent screenshot |
| SSPM-1.18-02 | Connected agents | Disabled or restricted to approved list | Copilot Studio > Agent > Settings > Connected agents (verify the literal menu label at apply-time — may surface as 'Agents' depending on UI release ring; A2A reached GA in April 2026 but per-agent toggle may still show Preview — [Learn](https://learn.microsoft.com/en-us/microsoft-copilot-studio/authoring-add-other-agents)) | Per-agent screenshot |
| SSPM-1.18-03 | Admin count | < 10 environment-level admins per environment | PPAC > Environments > [env] > Settings > Users + permissions > Security roles > System Administrator | Filtered user export |
| SSPM-1.18-04 | RPA / SPN admin roles | No service principals in admin roles | PPAC > Environments > [env] > Settings > Users + permissions > Users (filter Type = Application) | Filtered user export |

### Test procedures

**SSPM-1.18-01 — Agent action consent**

1. Open Copilot Studio > select agent > **Tools**.
2. For each tool, confirm "Ask the user before running this action" = **Enabled**.
3. **Pass criteria:** Every tool on every published Zone 2/3 agent has the consent prompt enabled.
4. **Evidence:** Screenshot of the Tools list with the consent toggle visible.

**SSPM-1.18-02 — Connected agents**

1. Open Copilot Studio > select agent > **Settings** > **Connected agents** (the multi-agent collaboration surface; verify the literal menu label at apply-time — some tenants surface this as **'Agents'** depending on UI release ring. The A2A protocol underpinning cross-agent invocation reached GA in April 2026, but the per-agent connectivity toggle may still surface a Preview label in some tenants — https://learn.microsoft.com/en-us/microsoft-copilot-studio/authoring-add-other-agents).
2. Confirm "Let other agents connect to and use this one" = **Disabled**, or that the agent is on the documented approved-exception list.
3. **Pass criteria:** Connected-agent enablement matches the approved-exception list.
4. **Evidence:** Settings screenshot + approved-exception list reference.

**SSPM-1.18-03 — Admin count**

1. Navigate to PPAC > Environments > [env] > Settings > **Users + permissions** > **Security roles** > **System Administrator**.
2. Count assigned users.
3. **Pass criteria:** < 10 named admins per Zone 3 environment.
4. **Evidence:** Screenshot or CSV export with member count.

**SSPM-1.18-04 — RPA / SPN admin scrub**

1. Navigate to PPAC > Environments > [env] > Settings > **Users + permissions** > **Users**.
2. Filter or sort by **Type** = Application.
3. Cross-reference returned principals against the System Administrator and Environment Admin role members.
4. **Pass criteria:** Zero application principals in admin roles.
5. **Evidence:** Filtered CSV export annotated against the approved SPN list.

---

[Back to Control 1.18](../../../controls/pillar-1-security/1.18-application-level-authorization-and-role-based-access-control-rbac.md) | [Portal Walkthrough](portal-walkthrough.md) | [PowerShell Setup](powershell-setup.md) | [Troubleshooting](troubleshooting.md)
---

*Updated: May 2026 | Version: v1.6.2 | UI Verification Status: Current*
