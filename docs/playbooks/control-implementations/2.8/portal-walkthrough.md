# Portal Walkthrough: Control 2.8 — Access Control and Segregation of Duties

**Last Updated:** April 2026
**Portals:** Microsoft Entra Admin Center, Microsoft 365 Admin Center, Power Platform Admin Center (PPAC), Copilot Studio, Power Automate
**Estimated Time:** 3–4 hours for the initial Zone 3 build; ~30 min/quarter for ongoing review tasks
**Audience:** M365 administrators in US financial services responsible for AI agent governance

> This playbook configures the **portal-side** scaffolding for Control 2.8. The companion [PowerShell Setup](powershell-setup.md) automates group creation, SoD detection, and evidence export. Portal screenshots should be captured per `docs/images/2.8/EXPECTED.md` and stored under `maintainers-local/tenant-evidence/` (never committed).

---

## Prerequisites

- [ ] **Entra Global Admin** (initial setup only) and **Entra Privileged Role Admin** (ongoing PIM configuration)
- [ ] **Entra Identity Governance Admin** (for Access Reviews and PIM for Groups)
- [ ] **Power Platform Admin** (for Dataverse security roles and environment access)
- [ ] **Microsoft Entra ID P2** licensing for every user who will be PIM-eligible or a reviewer of record
- [ ] Role definitions, exception register, and reviewer-of-record list documented and signed off by AI Governance Lead and Compliance Officer
- [ ] Naming standard published for SG-Agent-* groups (kept in sync with the PowerShell baseline)

> **Canonical role names** — use the short names defined in `docs/reference/role-catalog.md`. Do not substitute display names like "Global Administrator" inside the framework.

---

## Step 1 — Create role-assignable security groups (Entra Admin Center)

1. Open the [Microsoft Entra Admin Center](https://entra.microsoft.com).
2. Browse to **Identity → Groups → All groups → New group**.
3. Create the five governance groups below. For any group that will hold or be granted a **directory role**, set **Microsoft Entra roles can be assigned to the group** to **Yes** at creation (this cannot be changed later).

| Group name | Description | Type | Membership | Role-assignable | Owner |
|---|---|---|---|---|---|
| `SG-Agent-Developers` | Authoring identities (makers) for Copilot Studio agents | Security | Assigned | No | AI Governance Lead |
| `SG-Agent-Reviewers` | Independent reviewers of agent submissions | Security | Assigned | No | AI Governance Lead |
| `SG-Agent-Approvers` | Approvers for production publish/share | Security | Assigned | **Yes** (PIM-managed) | Compliance Officer |
| `SG-Agent-ReleaseManagers` | Identities authorised to deploy to Zone 3 production environments | Security | Assigned | **Yes** (PIM-managed) | Compliance Officer |
| `SG-Agent-PlatformAdmins` | Holders of Power Platform Admin / Environment Admin (PIM-eligible only) | Security | Assigned | **Yes** | Entra Privileged Role Admin |

> The Approvers, Release Managers, and Platform Admins groups should be **role-assignable** so that PIM for Groups can manage them and so that they cannot be modified by Group Administrators outside the privileged-access path.

---

## Step 2 — Configure Dataverse / Power Platform security roles (PPAC)

1. Open the [Power Platform Admin Center](https://admin.powerplatform.microsoft.com).
2. **Environments** → select the target Zone 2 or Zone 3 environment → **Settings** → **Users + permissions** → **Security roles**.
3. Either clone an existing role (recommended starting points: **Environment Maker**, **Basic User**, **System Customizer**) or create custom roles. Apply least-privilege table and column privileges.

| Dataverse role | Privileges | Mapped Entra group | Notes |
|---|---|---|---|
| Agent Author (custom, cloned from Environment Maker) | Read/Write on agent assets owned by user; Read on shared environment metadata | `SG-Agent-Developers` | Do **not** grant Append-To across all tables; scope to agent-related tables only |
| Agent Reviewer (custom) | Read on all agent assets; Append (annotate) | `SG-Agent-Reviewers` | Read-all is required for independent review |
| Agent Approver (custom) | Read on all agent assets; Approve workflow steps | `SG-Agent-Approvers` | No Write/Deploy privileges — approval is a workflow signal |
| Release Manager (custom) | Publish/Deploy on agent assets; Read on solutions | `SG-Agent-ReleaseManagers` | Reserve for production-aligned environments |
| **Dataverse System Administrator** | All | (no standing assignment) | **Break-glass only** — assign via PIM for Groups, time-boxed |

4. Assign each role to its Entra group via **Users + permissions → Teams → New team → Microsoft Entra ID security group team** (Group team) and attach the security role to the team. This keeps Dataverse role membership in sync with Entra group membership.

> **April 2026 path note** — PPAC moved the security-role list under **Settings → Users + permissions → Security roles** in the post-March 2026 navigation refresh. The legacy **Settings → Security roles** path still resolves but is deprecated.

---

## Step 3 — Separate Copilot Studio authoring from administration

1. Open [Copilot Studio](https://copilotstudio.microsoft.com).
2. Confirm that members of `SG-Agent-Developers` hold **Copilot Studio author** (Environment Maker + the relevant Dataverse role) **only** — they should **not** appear in `SG-Agent-PlatformAdmins`.
3. In PPAC, verify that no identity is simultaneously a member of `SG-Agent-Developers` **and** holds **Power Platform Admin** or **Environment Admin** in a Zone 3 environment. The PowerShell SoD check enforces this; the portal step is a visual cross-check during the change window.
4. If your tenant has the **March 2026 enhanced admin controls** enabled, set **Approved authentication providers** at the environment-group level so that makers cannot introduce identity paths that reviewers cannot independently validate.

---

## Step 4 — Configure PIM for Roles (Entra Admin Center)

1. **Identity governance → Privileged Identity Management → Microsoft Entra roles → Roles**.
2. For each of the following roles, open **Settings** and apply the Zone 3 configuration:

| Role | Max activation | MFA | Justification | Approval | Approvers |
|---|---|---|---|---|---|
| Power Platform Admin | 4 hours | Required | Required (ticket #) | **Yes** | `SG-Agent-Approvers` (excluding the activator) |
| AI Administrator | 4 hours | Required | Required | **Yes** | `SG-Agent-Approvers` |
| Entra Global Admin | 1 hour | Required | Required | **Yes** | Compliance Officer + Entra Privileged Role Admin |
| Privileged Role Administrator | 1 hour | Required | Required | **Yes** | Compliance Officer |

3. **Assignments → Add assignments** → assign **Eligible** (not Active) members from `SG-Agent-PlatformAdmins`.
4. Confirm the **Audit history** tab is populating (this feed is consumed by Control 3.x reporting).

---

## Step 5 — Configure PIM for Groups (Entra Admin Center)

1. **Identity governance → Privileged Identity Management → Groups → Discover groups** → onboard `SG-Agent-Approvers`, `SG-Agent-ReleaseManagers`, and `SG-Agent-PlatformAdmins`.
2. For each onboarded group, open **Settings → Member** and set:
   - Activation max: **4 hours** (Approvers, Release Managers); **1 hour** (Platform Admins)
   - MFA on activation: **Required**
   - Justification: **Required**
   - Approval to activate: **Required** (Zone 3); approver = a different group than the requester's home team
3. Move standing members to **Eligible** assignments. The only Active members should be break-glass identities documented in your incident-response runbook.

> PIM for Groups is the recommended Zone 3 control because it brings just-in-time enforcement to Dataverse-bound identities (group-team assignments) that PIM for Roles alone cannot reach.

---

## Step 6 — Configure Access Reviews (Entra Identity Governance)

1. **Identity governance → Access reviews → New access review**.
2. Configure a **per-zone** review schedule:

| Review name | Scope | Frequency | Duration | Reviewers | Auto-apply | If reviewer doesn't respond |
|---|---|---|---|---|---|---|
| Agent Governance — Zone 3 Privileged Roles | PIM-eligible assignments for Power Platform Admin, AI Administrator, Dataverse System Administrator | **Monthly** | 7 days | Group owners + AI Governance Lead (multi-stage) | Yes | **Remove access** |
| Agent Governance — Zone 3 Approver/Release groups | `SG-Agent-Approvers`, `SG-Agent-ReleaseManagers` | **Quarterly** | 14 days | Compliance Officer + Group owner | Yes | **Remove access** |
| Agent Governance — Zone 2 maker groups | `SG-Agent-Developers`, `SG-Agent-Reviewers` | **Quarterly** | 14 days | Group owner | Yes | Take recommendations |
| Agent Governance — Zone 1 broad makers | All Power Platform makers (Environment Maker) | **Annually** | 21 days | Manager (M365 manager attribute) | Yes | Take recommendations |

3. Enable **Justification required** and **Show recommendations** (recommendations are based on sign-in activity).
4. Save and confirm the first instance is scheduled.

---

## Step 7 — Build the SoD-enforcing approval workflow (Power Automate)

1. Open [Power Automate](https://make.powerautomate.com) in the **shared production-aligned environment** (not the maker's personal environment).
2. Create a flow **Agent Production Publish — SoD Approval** with trigger **When a Copilot Studio agent is submitted for publish** (or an HTTP request from your release pipeline).
3. Add the following branching:
   - **Initialize variable** `RequestorUPN` = trigger output.
   - **Get group members (V3)** for `SG-Agent-Approvers`, store UPNs.
   - **Condition**: if `RequestorUPN` is in the Approvers list **OR** if `RequestorUPN` is in `SG-Agent-Developers` for the agent's solution → **Terminate** with status `Failed` and reason `SoD: requestor cannot approve own work`.
   - Otherwise → **Start and wait for an approval** (Approval type: **First to respond**, Assigned to: `SG-Agent-Approvers` minus `RequestorUPN`).
   - On Approve → call the deployment endpoint (only `SG-Agent-ReleaseManagers` should hold the deployment service-principal credentials).
   - Always → write an audit row to a Dataverse table `agent_sod_decisions` (Requestor, Approver, Decision, Timestamp, Justification, AgentSolutionId).
4. Set the flow owner to a **service account** (not the maker) and grant `SG-Agent-PlatformAdmins` co-owner via PIM for Groups.

---

## Step 8 — Conditional Access and CAE for the privileged path

1. **Entra Admin Center → Protection → Conditional Access → Policies → New policy**.
2. Create policy **CA-Agent-Privileged-Path**:
   - **Users**: `SG-Agent-Approvers`, `SG-Agent-ReleaseManagers`, `SG-Agent-PlatformAdmins`
   - **Target resources**: Microsoft Admin Portals, Power Platform admin app (`a8f7a65c-f5ba-4859-b2d6-df772c264e9d`), Microsoft Graph PowerShell, Copilot Studio
   - **Conditions**: Sign-in risk = **Medium and above**; client apps = browser + modern auth
   - **Grant**: Require **phishing-resistant MFA**, require **compliant device**
   - **Session**: Sign-in frequency 4 hours; persistent browser = Never
3. **Protection → Continuous access evaluation**: confirm **Migrate** is set to **Enabled** for the tenant. CAE will revoke tokens on disabled-user, password-change, and high-risk events for the policies above.

---

## Configuration by Governance Level

| Setting | Baseline (Zone 1) | Recommended (Zone 2) | Regulated (Zone 3) |
|---|---|---|---|
| Role separation | Self-service | Creator ≠ Approver | Creator ≠ Reviewer ≠ Approver ≠ Release Manager |
| PIM for Roles | Optional | Recommended for Power Platform Admin | Required for all admin roles |
| PIM for Groups | Not required | Recommended for Approvers | Required for Approvers, Release Managers, Platform Admins |
| Access Reviews | Annual | Quarterly | Monthly (privileged) + Quarterly (operational) |
| Approval workflow | Optional | Required for shared agents | Required with mechanical SoD reject |
| Conditional Access | Baseline tenant policy | Risk-based MFA | Phishing-resistant MFA + compliant device + CAE |
| Break-glass procedure | Not required | Documented | Documented, tested annually, monitored alert |

---

## Validation (Portal-Side)

After completing the walkthrough, verify in the portal:

- [ ] All 5 SG-Agent-* groups exist with named owners and the privileged three are role-assignable.
- [ ] Each Dataverse environment in Zone 2/3 shows the four custom security roles bound to the group teams.
- [ ] PIM for Roles shows zero Active assignments for Power Platform Admin, AI Administrator, and Entra Global Admin.
- [ ] PIM for Groups shows the three privileged groups onboarded and configured.
- [ ] Access Reviews shows the four review series scheduled with the correct cadence and auto-apply enabled.
- [ ] Power Automate shows the Agent Production Publish — SoD Approval flow as **On** and owned by the service account.
- [ ] Conditional Access policy CA-Agent-Privileged-Path is **On** for the three privileged groups.

Now run the [PowerShell Setup](powershell-setup.md) to lock the same state in code and emit evidence; then run [Verification & Testing](verification-testing.md).

---

[Back to Control 2.8](../../../controls/pillar-2-management/2.8-access-control-and-segregation-of-duties.md) | [PowerShell Setup](powershell-setup.md) | [Verification & Testing](verification-testing.md) | [Troubleshooting](troubleshooting.md)
