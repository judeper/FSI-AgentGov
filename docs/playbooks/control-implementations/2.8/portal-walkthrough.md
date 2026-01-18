# Portal Walkthrough: Control 2.8 - Access Control and Segregation of Duties

**Last Updated:** January 2026
**Portal:** Entra Admin Center, Power Platform Admin Center
**Estimated Time:** 2-3 hours

## Prerequisites

- [ ] Entra Global Admin or Privileged Role Admin
- [ ] Power Platform Admin role
- [ ] Entra ID P2 license (for PIM and Access Reviews)
- [ ] Role definitions documented per SOX SoD requirements

---

## Step-by-Step Configuration

### Step 1: Create Security Groups for Agent Governance Roles

1. Open [Entra Admin Center](https://entra.microsoft.com)
2. Navigate to **Groups** > **All groups**
3. Create security groups for each governance role:

| Group Name | Description | Type |
|------------|-------------|------|
| `SG-Agent-Developers` | Can create and edit agents | Security |
| `SG-Agent-Reviewers` | Can review agent submissions | Security |
| `SG-Agent-Approvers` | Can approve agent deployments | Security |
| `SG-Agent-ReleaseManagers` | Can deploy agents to production | Security |
| `SG-Agent-PlatformAdmins` | Can configure platform settings | Security |

### Step 2: Configure Power Platform Security Roles

1. Open [Power Platform Admin Center](https://admin.powerplatform.microsoft.com)
2. Navigate to **Environments** > select target environment
3. Go to **Settings** > **Users + permissions** > **Security roles**
4. Create or modify roles:

| Role Name | Privileges | Assigned To |
|-----------|-----------|-------------|
| Agent Developer | Create, Read, Write (own) | SG-Agent-Developers |
| Agent Reviewer | Read (all), Append | SG-Agent-Reviewers |
| Agent Approver | Approve (workflow only) | SG-Agent-Approvers |
| Release Manager | Deploy, Publish | SG-Agent-ReleaseManagers |

### Step 3: Configure Privileged Identity Management (PIM)

1. In Entra Admin Center, go to **Identity Governance** > **Privileged Identity Management**
2. Select **Microsoft Entra roles** or **Azure resources**
3. For Zone 3 admin roles, configure:
   - **Activation maximum duration:** 8 hours
   - **Require justification:** Yes
   - **Require approval:** Yes for Platform Admin role
   - **Approvers:** AI Governance Lead or Compliance Officer
4. Add eligible members from appropriate security groups

### Step 4: Configure Access Reviews

1. Navigate to **Identity Governance** > **Access reviews**
2. Click **+ New access review**
3. Configure quarterly review:
   - **Review name:** Agent Governance Role Access Review
   - **Start date:** First day of quarter
   - **Frequency:** Quarterly
   - **Duration:** 14 days
   - **Scope:** Security groups (SG-Agent-*)
   - **Reviewers:** Group owners + AI Governance Lead
   - **Auto-apply results:** Yes

### Step 5: Build Approval Workflow with SoD Enforcement

1. Open [Power Automate](https://make.powerautomate.com)
2. Create flow: **Agent Deployment Approval**
3. Add conditions:
   - If `RequestorEmail` = `ApproverEmail` → Reject (SoD violation)
   - Require approval from SG-Agent-Approvers group
   - Send to Release Manager only after approval

### Step 6: Configure Continuous Access Evaluation

1. In Entra Admin Center, go to **Protection** > **Conditional Access**
2. Enable **Continuous access evaluation** for Power Platform apps
3. Configure policy to immediately revoke access on:
   - User disabled
   - Password changed
   - Location change for sensitive operations

---

## Configuration by Governance Level

| Setting | Baseline (Tier 1) | Recommended (Tier 2) | Regulated (Tier 3) |
|---------|-------------------|----------------------|-------------------|
| **Role Separation** | Self-service | Creator ≠ Approver | Full 4-role separation |
| **PIM** | Optional | Recommended | Required |
| **Access Reviews** | Annual | Quarterly | Monthly |
| **SoD Validation** | Manual | Automated check | Real-time enforcement |
| **JIT Access** | None | Recommended | Required |

---

## FSI Example Configuration

```yaml
Access Control: Segregation of Duties Configuration

Security Groups:
  Developers: SG-Agent-Developers (15 members)
  Reviewers: SG-Agent-Reviewers (5 members)
  Approvers: SG-Agent-Approvers (3 members)
  Release Managers: SG-Agent-ReleaseManagers (2 members)

PIM Configuration:
  Platform Admin:
    Eligible: SG-Agent-PlatformAdmins
    Activation: 8 hours, requires approval
    Approvers: AI Governance Lead

Access Reviews:
  Frequency: Quarterly
  Duration: 14 days
  Auto-apply: Enabled

SoD Rules:
  - Creator cannot approve own work
  - Approver cannot deploy
  - No single person end-to-end
```

---

## Validation

After completing these steps, verify:

- [ ] All security groups created and populated
- [ ] Power Platform security roles configured
- [ ] PIM activated for Zone 3 admin roles
- [ ] Access reviews scheduled
- [ ] Approval workflow enforces SoD
- [ ] Continuous access evaluation enabled

---

[Back to Control 2.8](../../../controls/pillar-2-management/2.8-access-control-and-segregation-of-duties.md) | [PowerShell Setup](powershell-setup.md) | [Verification Testing](verification-testing.md) | [Troubleshooting](troubleshooting.md)
