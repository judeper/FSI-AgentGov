# Portal Walkthrough: Control 1.1 - Restrict Agent Publishing by Authorization

**Last Updated:** January 2026
**Portal:** Power Platform Admin Center, Microsoft Entra Admin Center
**Estimated Time:** 15-30 minutes

## Prerequisites

- [ ] Power Platform Admin role assigned
- [ ] Access to [Power Platform Admin Center](https://admin.powerplatform.microsoft.com)
- [ ] Access to [Microsoft Entra Admin Center](https://entra.microsoft.com)
- [ ] Security groups configured in Microsoft Entra ID for maker management
- [ ] [Control 2.1: Managed Environments](../../../controls/pillar-2-management/2.1-managed-environments.md) enabled (recommended)

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

### Step 3: Restrict Copilot Studio Access

1. In Power Platform Admin Center, select the environment
2. Navigate to **Settings** > **Features**
3. Configure the following:
   - **Who can create and edit Copilots**: Select **Only specific security groups**
   - Add the FSI-Agent-Makers security group(s)
4. Select **Save**

**Hardening notes:**

- Apply this setting in **each** environment where Copilot Studio is enabled.
- In PROD, prefer restricting creation/editing to `FSI-Agent-Publishers-Prod` (or a dedicated production maker group) rather than broad maker groups.

### Step 4: Configure Maker Sharing Restrictions (Team/Enterprise)

1. In Power Platform Admin Center, navigate to **Manage** > **Environments**
2. Select your environment > **...** (ellipsis) > **Enable Managed Environments** (if not already)
3. Configure **Limit sharing**:
   - For team collaboration: **Exclude Sharing to Security Groups**
   - For enterprise managed: **Do not allow sharing** (strictest)
4. This prevents unauthorized distribution of agents

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

## Validation

After completing these steps, verify:

- [ ] Security groups created in Entra ID with correct membership
- [ ] Environment Maker role restricted to authorized groups only
- [ ] Copilot Studio access restricted to specific security groups
- [ ] Managed Environment enabled with sharing limits configured
- [ ] Unauthorized users cannot create/publish agents (test with non-member account)

---

[Back to Control 1.1](../../../controls/pillar-1-security/1.1-restrict-agent-publishing-by-authorization.md) | [PowerShell Setup](powershell-setup.md) | [Verification Testing](verification-testing.md) | [Troubleshooting](troubleshooting.md)
