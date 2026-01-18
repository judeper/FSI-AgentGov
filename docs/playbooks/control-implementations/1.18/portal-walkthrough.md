# Portal Walkthrough: Control 1.18 - Application-Level Authorization and RBAC

**Last Updated:** January 2026
**Portal:** Power Platform Admin Center, Microsoft Entra Admin Center
**Estimated Time:** 3-5 hours

## Prerequisites

- [ ] Power Platform Admin role
- [ ] Entra Global Admin or Privileged Role Admin
- [ ] Dataverse System Administrator for security role creation

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

1. Open [Power Platform Admin Center](https://admin.powerplatform.microsoft.com)
2. Select environment > **Settings** > **Users + permissions** > **Security roles**
3. Create custom roles:

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

1. Open [Microsoft Entra Admin Center](https://entra.microsoft.com)
2. Navigate to **Identity governance** > **Privileged Identity Management**
3. Select **Azure AD roles** > **Roles**
4. Configure PIM for Power Platform Admin:
   - Maximum activation duration: 4 hours
   - Require approval: Yes (CISO/Security Lead)
   - Require MFA on activation: Yes

### Step 5: Configure Column-Level Security

1. In Power Platform Admin Center > Environment > Settings
2. Navigate to **Data management** > **Field security profiles**
3. Create profile: `FSI-SensitiveFields`
4. Add sensitive columns (SSN, Account Balance, Credit Score)
5. Assign allowed roles/users

### Step 6: Set Up Access Reviews

1. Open Microsoft Entra Admin Center
2. Navigate to **Identity governance** > **Access reviews**
3. Create review for each security group:
   - Frequency: Quarterly (Zone 2/3), Annual (Zone 1)
   - Reviewers: Group owners
   - Auto-remove on non-response: Yes

---

## Configuration by Governance Level

| Setting | Baseline (Tier 1) | Recommended (Tier 2) | Regulated (Tier 3) |
|---------|-------------------|----------------------|-------------------|
| **Role Assignment** | Standard roles | Group-based custom | Least-privilege custom |
| **Access Review** | Annual | Semi-annual | Quarterly |
| **PIM** | Not required | Admin roles | All privileged roles |
| **Approval** | Self-service | Manager | Multi-level |
| **Column Security** | None | Sensitive fields | All PII/NPI fields |

---

## Validation

After completing these steps, verify:

- [ ] Security groups created and populated
- [ ] Custom security roles assigned to groups
- [ ] PIM configured for admin roles
- [ ] Access reviews scheduled
- [ ] Column-level security enforced

---

[Back to Control 1.18](../../../controls/pillar-1-security/1.18-application-level-authorization-and-role-based-access-control-rbac.md) | [PowerShell Setup](powershell-setup.md) | [Verification Testing](verification-testing.md) | [Troubleshooting](troubleshooting.md)
