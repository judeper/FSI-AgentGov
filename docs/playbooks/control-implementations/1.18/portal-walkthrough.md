# Portal Walkthrough: Control 1.18 - Application-Level Authorization and RBAC

**Last Updated:** April 2026
**Portal:** Power Platform Admin Center, Microsoft Entra Admin Center
**Estimated Time:** 3-5 hours

## Prerequisites

- [ ] Power Platform Admin role
- [ ] Entra Global Admin or Entra Privileged Role Admin
- [ ] Dataverse System Admin for security role creation

---

## Step-by-Step Configuration

### Step 1: Create Security Groups

1. Open [Microsoft Entra Admin Center](https://entra.microsoft.com)
2. Navigate to **Groups** > **All groups**
3. Create security groups:
   - `SG-PowerPlatform-Admins-Prod`
   - `SG-CopilotStudio-Makers-Prod`
   - `SG-CopilotStudio-Viewers-Prod`
   - `SG-CopilotStudio-Testers-Prod`

### Step 2: Create Custom Dataverse Security Roles

> **Dataverse-only.** Steps 2–3 apply to Dataverse-backed environments (all Copilot Studio environments). For non-Dataverse environments, use environment-level role assignments via PPAC > Environments > Settings > Users + permissions.

1. Open [Power Platform Admin Center](https://admin.powerplatform.microsoft.com)
2. Select environment > **Settings** > **Users + permissions** > **Security roles**
3. For each role below: select **+ New role**, set the **Business unit** to the root BU, name the role per the convention, then on the **Core records** / **Custom entities** tabs grant only the privileges listed.

**FSI - Agent Publisher:**
- Bot: Create, Read, Write, Delete, Append, Append To
- Bot Component: Create, Read, Write, Delete
- Environment: Read

**FSI - Agent Viewer:**
- Bot: Read
- Bot Component: Read
- Environment: Read

**FSI - Agent Tester:**
- Bot: Read, Write
- Bot Component: Read
- Environment: Read

### Step 3: Assign Roles to Security Groups

1. In Power Platform Admin Center
2. Select environment > **Settings** > **Users + permissions** > **Teams**
3. Create teams linked to security groups
4. Assign security roles to teams

### Step 4: Configure Privileged Identity Management

> **Licensing prerequisite:** PIM and PIM-for-Groups require **Microsoft Entra ID P2** for every assigned and eligible user. Without P2, eligibility-based assignments will not appear.

1. Open [Microsoft Entra Admin Center](https://entra.microsoft.com)
2. Navigate to **Identity governance** > **Privileged Identity Management**
3. **For directory roles** (Power Platform Admin, AI Administrator): select **Microsoft Entra roles** > **Roles** > target role > **Settings**
4. **For environment / Dataverse access** (recommended pattern): select **Groups** > add `SG-PowerPlatform-Admins-Prod` > **Settings** > **Member** role
5. Configure activation settings:
   - Maximum activation duration: **4 hours** (Zone 3) / 8 hours (Zone 2)
   - Require approval to activate: **Yes** (Zone 3 — minimum 2 approvers from CISO/Security Lead)
   - Require MFA on activation: **Yes** (all zones)
   - Require justification on activation: **Yes**
   - Require ticket information on activation: **Yes** (Zone 3)
   - Notification on activation: route to Sentinel/SIEM via Entra audit log forwarding

### Step 5: Configure Column-Level Security

> **Path note (April 2026):** "Field security profiles" is also accessible via the modern Power Apps maker portal at **make.powerapps.com** > Solutions > Default Solution > **Security** > **Field security profiles**. The classic path below remains supported.

1. In Power Platform Admin Center > Environment > **Settings**
2. Navigate to **Users + permissions** > **Column security profiles** (formerly "Field security profiles")
3. Create profile: `FSI-SensitiveFields-Prod`
4. Add sensitive columns by enabling **Column security** on the column definition first (Solutions > target table > column > Advanced options > **Enable column security: On**) — this is required before the column appears in the profile
5. Common FSI columns to protect: SSN/Tax ID, account number, account balance, credit score, date of birth, government ID
6. Assign the profile to the security groups (or Dataverse teams) that require access; **all other users default to no access**

### Step 6: Set Up Access Reviews

1. Open Microsoft Entra Admin Center
2. Navigate to **Identity governance** > **Access reviews**
3. Create review for each security group:
   - Frequency: Quarterly (Zone 2/3), Annual (Zone 1)
   - Reviewers: Group owners
   - Auto-remove on non-response: Yes

---

## Configuration by Governance Level

| Setting | Baseline (Zone 1) | Recommended (Zone 2) | Regulated (Zone 3) |
|---------|-------------------|----------------------|-------------------|
| **Role Assignment** | Standard roles | Group-based custom | Least-privilege custom |
| **Access Review** | Annual | Semi-annual | Quarterly |
| **PIM** | Not required | Admin roles | All privileged roles |
| **Approval** | Self-service | Manager | Multi-level |
| **Column Security** | None | Sensitive fields | All PII/NPI fields |

---

### Step 7: Configure Agent Action Consent

1. Open **Copilot Studio** ([https://copilotstudio.microsoft.com](https://copilotstudio.microsoft.com))
2. Navigate to **Agents** and select each agent
3. Go to **Tools** and locate each configured tool
4. For every action, enable **"Ask the user before running this action"**
5. Where available, set "How do you want to ask the user?" to **"You create the message"** and configure a clear, human-written description of what the action will do
6. Repeat for all agents in Zone 2 and Zone 3 environments

### Step 8: Configure Connected Agent Governance

1. In Copilot Studio, select each agent
2. Navigate to **Settings** > under **Connected Agents** (Preview)
3. Locate the toggle **"Let other agents connect to and use this one"**
4. Set to **Disabled** by default
5. Enable only with:
   - Documented business justification
   - Cross-agent data handling review
   - Compliance officer sign-off
6. Document all approved inter-agent connections and review quarterly

### Step 9: Review Environment Admin Roles

1. Sign in to **Power Platform Admin Center** ([https://admin.powerplatform.microsoft.com](https://admin.powerplatform.microsoft.com))
2. Navigate to **Environments** > select the target environment > **Settings** > **Users + Permissions** > **Users**
3. Review all users with **System Administrator** role
4. For any assignment that is not justified, select the user > **Manage Roles** > remove System Administrator
5. Ensure fewer than 10 administrators per environment
6. Document all admin role assignments with business justification

---

## Validation

After completing these steps, verify:

- [ ] Security groups created and populated
- [ ] Custom security roles assigned to groups
- [ ] PIM configured for admin roles
- [ ] Access reviews scheduled
- [ ] Column-level security enforced
- [ ] All agent actions have "Ask the user before running this action" enabled (Copilot Studio > Agent > Tools)
- [ ] Connected agent access disabled for all agents unless explicitly approved (Copilot Studio > Agent > Settings > Connected Agents)
- [ ] Admin count is below 10 per environment (PPAC > Environment > Users + Permissions)

---

[Back to Control 1.18](../../../controls/pillar-1-security/1.18-application-level-authorization-and-role-based-access-control-rbac.md) | [PowerShell Setup](powershell-setup.md) | [Verification Testing](verification-testing.md) | [Troubleshooting](troubleshooting.md)

---

*Updated: May 2026 | Version: v1.6.2 | UI Verification Status: Current*
