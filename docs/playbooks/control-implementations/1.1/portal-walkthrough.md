# Portal Walkthrough: Control 1.1 - Restrict Agent Publishing by Authorization

**Last Updated:** April 2026
**Portal:** Power Platform Admin Center, Microsoft Entra Admin Center, M365 Admin Center, Copilot Studio
**Estimated Time:** 30-60 minutes

!!! warning "Prerequisites & Licensing"
    This walkthrough requires:

    - **Power Platform Admin** or (preferred) **AI Administrator** role assigned
    - Access to PPAC, Entra, M365 Admin Center, Copilot Studio
    - Security groups already created in Entra ID
    - **Managed Environments** licensed (required for Step 4 sharing limits)
    - **Copilot Studio** licensed at the tenant or per-user
    - **Microsoft Entra ID P1** for any dynamic group membership
    - For sovereign tenants (GCC / GCC-High / DoD), all portal URLs differ — consult Microsoft sovereign-cloud documentation; this walkthrough uses commercial URLs

    See the parent [Control 1.1](../../../controls/pillar-1-security/1.1-restrict-agent-publishing-by-authorization.md) Prerequisites & Licensing block for the full list.

!!! info "Propagation timing"
    Most settings below are **not retroactive** and take **up to ~1 hour** to enforce against existing agents and active sessions. Authentication changes (Step 6) take effect **only after each agent is re-published**. Do not interpret a delayed enforcement window as a broken control.

---

## Step-by-Step Configuration

### Step 0 (Recommended): Establish Release Gates and Separation of Duties

Use environment separation to enforce authorization as a technical control (not just policy):

1. Create at least **DEV/UAT/PROD** environments (all in US regions).
2. Assign roles so that:
   - **Makers** can create/edit only in DEV (and optionally UAT).
   - **Publishers/Release Managers** (small group) can publish to production channels in PROD.
   - **Compliance approvers** cannot publish; they approve via workflow/tickets.
3. Enforce "no direct publish to PROD" by ensuring unauthorized users do **not** have maker/admin rights in PROD.

This release-gate model is what makes "restrict publishing by authorization" auditable.

### Step 1: Create Security Groups for Authorized Makers

1. Sign in to the **Microsoft Entra Admin Center** ([https://entra.microsoft.com](https://entra.microsoft.com))
2. Navigate to **Identity** > **Groups** > **All groups**
3. Select **New group**
4. Configure the group:
   - **Group type**: Security
   - **Group name**: `FSI-Agent-Makers-Team` or `FSI-Agent-Makers-Enterprise`
   - **Group description**: `Authorized makers for team/enterprise agent development`
   - **Membership type**: Assigned (for strict control) or Dynamic (for automation)
5. Add authorized users as members
6. Select **Create**

Create additional security groups to support segregation of duties and release gates:

- `FSI-Agent-Publishers-Prod` (small, named individuals only)
- `FSI-Agent-Approvers-Compliance` (approvers only; no maker rights required)
- `FSI-Agent-Admins-Platform` (Power Platform/Dataverse admins)

### Step 2: Configure Environment Security Roles

1. Sign in to the **Power Platform Admin Center** ([https://admin.powerplatform.microsoft.com](https://admin.powerplatform.microsoft.com))
2. Navigate to **Manage** > **Environments**
3. Select the target environment
4. Select **Settings** > **Users + permissions** > **Security roles**
5. Review and configure roles:
   - **Environment Maker**: Can create apps and flows (assign to authorized makers only)
   - **Basic User**: Can run apps but not create (for end users)
   - **Dataverse System Admin**: Full control (limit to admins only)
6. Remove Environment Maker role from unauthorized users

**Recommended minimum assignments by environment:**

| Environment | FSI-Agent-Makers-* | FSI-Agent-Publishers-Prod | FSI-Agent-Admins-Platform | All Other Users |
|-------------|-------------------|---------------------------|---------------------------|-----------------|
| DEV | Environment Maker | - | Dataverse System Admin | - |
| UAT | (optional) Environment Maker | - | Dataverse System Admin | - |
| PROD | - | Environment Maker | Dataverse System Admin | Basic User only |

### Step 3: Restrict Copilot Studio Authoring (Two Layers)

There are **two enforcement layers** for who can author / edit Copilot Studio agents. Configure **both**; they apply to different scopes.

**Layer A — Tenant-wide author gate (Power Platform Admin Center)**

1. Sign in to [Power Platform Admin Center](https://admin.powerplatform.microsoft.com)
2. Navigate to **Manage** > **Tenant settings**
3. Locate **Copilot Studio authors** *(may appear as "preview" depending on tenant rollout)*
4. Set to **Specific security groups**, then add `FSI-Agent-Makers-*` (and `FSI-Agent-Publishers-Prod` for PROD-eligible authors)
5. **Save**

> **Caveat (Microsoft-documented):** Users who already hold a Copilot Studio license at the time this setting is enforced **retain authoring access** until their license is removed. Pair this control with a license-cleanup pass for any user not in the approved groups.

**Layer B — Per-environment Dataverse Security Roles**

Copilot Studio agents in Dataverse-backed environments require Dataverse security roles, not the legacy "Environment Maker" PowerShell role assignment:

1. PPAC > **Manage** > **Environments** > select environment
2. **Settings** > **Users + permissions** > **Security roles**
3. Locate and assign the following Dataverse roles to your security groups:
   - **Environment Maker** (Dataverse role) — for agent creation
   - **Copilot Author** *(or the equivalent Dataverse role enabling Copilot Studio authoring in your environment — name has shifted across releases; verify in your tenant)*
4. Remove these roles from any "Everyone in tenant" / "All users" group assignment
5. **Save**

> **Why both layers?** Layer A is the tenant-wide gate that controls who Microsoft will *let* into Copilot Studio at all. Layer B is the per-environment Dataverse permission needed to *do* anything once they are in. Either alone leaves a gap.

> **Future direction:** Microsoft is consolidating these into the **Copilot hub** in PPAC (left nav > Copilot > Settings, per MC1162460). Verify the current state in your tenant before relying on the legacy paths.

### Step 4: Configure Managed Environment Agent-Sharing Limits

> **Important:** The *agent* sharing limits below are different from the *canvas-app* sharing limits historically configured under "Limit sharing". Make sure you are configuring the agent rules — the canvas-app rules will not restrict Copilot Studio agent sharing.

1. PPAC > **Manage** > **Environments** > select environment > **...** > **Enable Managed Environments** (if not already)
2. Open the environment > **Settings** > **Product** > **Sharing limits** *(verify exact label in your tenant — the Microsoft Learn page is `managed-environment-sharing-limits`)*
3. Configure the **agent** sharing rules for governance level:

| Setting | Recommended (Team) | Regulated (Enterprise) |
|---|---|---|
| **Let people grant Editor permissions when agents are shared** | Restricted to specific groups | **Off** for non-author users |
| **Let people grant Viewer permissions when agents are shared** | Restricted to specific groups | Restricted to named groups |
| **Only share with individuals (no security groups)** | **On** for non-Publishers groups | **On** |
| **Limit number of viewers who can access each agent** | Optional cap (e.g., 200) | **On** with strict cap |

4. **Save**

> **Propagation:** Settings are **not retroactive** to existing agent shares and take **up to ~1 hour** to enforce against new sharing actions. Verify with a test share from a non-author account after the wait window.

### Step 5: Implement Approval Workflow (Team/Enterprise)

For collaborative and enterprise-managed environments, implement a formal approval process:

1. **Create Approval SharePoint List**:
   - Columns: Agent Name, Creator, Environment, Governance Tier, Approval Status, Approver, Date
   - Configure permissions for Compliance team review

2. **Create Power Automate Approval Flow** (optional automation):
   - Trigger: When agent is ready for production
   - Action: Send approval to designated approvers
   - Outcome: Update registry and notify creator

3. **Document Approval Requirements**:
   - Team collaboration: Manager + Compliance acknowledgment
   - Enterprise managed: Governance Committee + Legal review + Change Advisory Board

**Release Gates (evidence-grade):**

| Gate | Purpose | Artifacts |
|------|---------|-----------|
| Gate A | Design & Data Review | Agent purpose, data classification, connectors list |
| Gate B | Security Review | DLP/connector policy confirmation, least-privilege review |
| Gate C | Testing/UAT | Functional testing evidence, user acceptance sign-off |
| Gate D | Production Publish | Approval record + change ticket ID |

---

## Configuration by Governance Level

| Setting | Baseline (Personal) | Recommended (Team) | Regulated (Enterprise) |
|---------|-------------------|----------------------|--------------------|
| **Security groups** | Optional | Required | Required + approval |
| **Environment Maker role** | Default access | Restricted to group | Restricted + logged |
| **Copilot Studio access** | All users | Authorized groups | Authorized + reviewed |
| **Sharing restrictions** | None | Exclude sharing to groups | No sharing allowed |
| **Approval workflow** | None | Manager approval | Governance committee |
| **Publishing audit** | Basic | Enhanced | Complete with retention |

---

## Microsoft 365 Integrated Surfaces

If your organization exposes Copilot Studio agents through Microsoft 365 integrated surfaces (Microsoft Teams or Microsoft 365 publish targets):

1. Only allow publishing to broad channels from the **PROD** environment.
2. Restrict PROD maker/publishing rights to `FSI-Agent-Publishers-Prod`.
3. If Teams distribution is used, ensure only designated administrators can manage org-wide availability.
4. Require a change ticket/approval record for any publish that makes an agent broadly discoverable.

**Evidence expectation:** An auditor should be able to trace a publish event in audit logs back to an approved change record and to a user's membership in `FSI-Agent-Publishers-Prod` at the time of publish.

---

## Agent and Tenant Configuration

### Step 6: Configure Agent-Level Authentication (Copilot Studio)

For each Copilot Studio agent, configure authentication settings to prevent unauthorized or anonymous interactions:

1. Open **Copilot Studio** ([https://copilotstudio.microsoft.com](https://copilotstudio.microsoft.com))
2. Navigate to **Agents** and select the target agent
3. Go to **Settings** (right side of the agent header) > **Security**
4. Configure authentication:
   - Change authentication from "No Authentication" to **"Authenticate with Microsoft"** (recommended for internal agents) or **"Authenticate Manually"** (for OAuth-based scenarios)
   - If using "Authenticate Manually," enable **"Require users to sign in"** to prevent anonymous interactions
   - For "Authenticate with Microsoft," users are already authenticated through Teams and Microsoft 365
5. Select **Save**
6. **Re-publish the agent.** Authentication setting changes take effect **only after the next publish** of each affected agent (per Microsoft Learn). Until then, existing sessions continue under the prior authentication mode.

**Repeat for every agent in Zone 2 and Zone 3 environments.**

### Step 7: Restrict Agent Sharing Scope (Copilot Studio)

!!! tip "Automated Detection: Unrestricted Agent Sharing Detector"

    For continuous automated detection of agents with overly permissive sharing configurations, deploy the [Unrestricted Agent Sharing Detector (UASD)](../../advanced-implementations/unrestricted-agent-sharing-detector/index.md). UASD scans all agents for organization-wide sharing, public internet links, unapproved groups, excessive individual shares, and cross-tenant access — with automated remediation and exception management.

1. In Copilot Studio, select the target agent
2. Select the three dots (**…**) > **Share** to review who can chat with or collaborate on the agent
3. Verify the agent is **not** shared with:
   - "Anyone" (public access)
   - "Any (multi-tenant)" (cross-tenant access)
4. Restrict sharing to:
   - **Copilot Readers** (for limited general access to low-risk agents)
   - **Specific Security Groups** (for restricted access based on role)
5. Enforce broader sharing restrictions through Managed Environment sharing rules in Power Platform Admin Center
6. Document exceptions for any agents intentionally shared broadly (requires risk acceptance)

### Step 8: Control Generative-AI Agent Publishing (Tenant Level)

1. Sign in to [Power Platform Admin Center](https://admin.powerplatform.microsoft.com)
2. Navigate to **Manage** > **Tenant settings**
3. Locate the AI / generative-AI publishing setting *(label has changed across releases — recent rollouts surface this as **"AI features"**, **"Generative AI features"**, or **"Copilot AI features for makers"**; verify the current label in your tenant)*
4. Set to **Off** (or restrict to specific environments) until governance review confirms AI-feature controls are in place
5. **Save**

> Document any exception in writing with a dated approval; revisit at the next governance cadence.

### Step 9: Block Unapproved Agents (M365 Admin Center)

The current GA flow is **instance-scoped**, not agent-scoped — you must drill into a specific instance to block:

1. Sign in to [M365 Admin Center](https://admin.microsoft.com)
2. **Copilot** > **Agents & connectors** > **Agents** *(label may also appear as "Agents" alone)*
3. Select **All agents**
4. Click into the unapproved agent to open its **Overview**
5. Open **Instance availability** > **See details**
6. Select the specific instance (e.g., a tenant-wide deployment, a Teams channel, a SharePoint site)
7. Select **Block** for that instance
8. Repeat for each instance where the agent is exposed
9. Document the block decision (date, who authorized, reason) and notify the agent owner

> **Important:** Selecting "Block" at the agent level without drilling into instances will not have the expected effect in the current UI. Block must be set at the instance level for each surface.

---

## Validation

After completing these steps, verify:

- [ ] Security groups created in Entra ID with correct membership
- [ ] Environment Maker role restricted to authorized groups only
- [ ] Copilot Studio access restricted to specific security groups
- [ ] Managed Environment enabled with sharing limits configured
- [ ] Unauthorized users cannot create/publish agents (test with non-member account)
- [ ] All agents have authentication enabled (not "No Authentication")
- [ ] Agents using manual authentication have "Require users to sign in" enabled
- [ ] No agents are shared with unrestricted access ("Anyone" or "Any multi-tenant")
- [ ] Generative AI agent publishing is disabled at tenant level
- [ ] Unapproved agents are blocked in M365 Admin Center

---

[Back to Control 1.1](../../../controls/pillar-1-security/1.1-restrict-agent-publishing-by-authorization.md) | [PowerShell Setup](powershell-setup.md) | [Verification Testing](verification-testing.md) | [Troubleshooting](troubleshooting.md)

---

*Updated: April 2026 | Version: v1.3.3 | Classification: Portal Walkthrough*
