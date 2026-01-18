# Portal Walkthrough: Control 2.15 - Environment Routing and Auto-Provisioning

**Last Updated:** January 2026
**Portal:** Power Platform Admin Center
**Estimated Time:** 30-60 minutes

## Prerequisites

- [ ] Power Platform Administrator role assigned
- [ ] Access to [Power Platform Admin Center](https://admin.powerplatform.microsoft.com)
- [ ] Environment groups defined and created
- [ ] Routing rules documented and approved
- [ ] Default environment governance strategy determined

---

## Step-by-Step Configuration

### Step 1: Access Environment Groups

1. Open [Power Platform Admin Center](https://admin.powerplatform.microsoft.com)
2. Navigate to **Environments** > **Environment groups**
3. Review existing groups or create new ones

### Step 2: Create Environment Group

1. Click **+ New group**
2. Enter group details:
   - **Name:** e.g., "FSI-Production-US"
   - **Description:** Purpose and governance tier
3. Click **Save**

### Step 3: Add Environments to Group

1. Open the environment group
2. Click **Add environments**
3. Select environments to include:
   - Only add environments in the same governance tier
   - Ensure all are Managed Environments (Control 2.1)
4. Click **Add**

### Step 4: Configure Environment Routing Rules

1. In the environment group, select **Rules**
2. Click **+ New rule**
3. Configure rule conditions:

**Rule Types:**

| Rule Type | Use Case |
|-----------|----------|
| Security group | Route users by AD group membership |
| Domain | Route by email domain |
| Geographic | Route by user location |
| Custom | Advanced conditions |

4. Set rule priority (lower number = higher priority)
5. Click **Save**

### Step 5: Configure Routing Priority

1. Review all rules in the group
2. Drag to reorder by priority
3. Ensure most specific rules are highest priority
4. Verify fallback behavior (default environment)

### Step 6: Test Routing Configuration

1. Sign in as a test user matching a routing rule
2. Navigate to [Power Apps](https://make.powerapps.com) or [Copilot Studio](https://copilotstudio.microsoft.com)
3. Create a new app/agent
4. Verify routed to expected environment

---

## Configuration by Governance Level

| Setting | Baseline (Tier 1) | Recommended (Tier 2) | Regulated (Tier 3) |
|---------|-------------------|----------------------|--------------------|
| **Environment Groups** | Optional | Recommended | **Required** |
| **Routing Rules** | Basic (domain) | Security group based | **Role-based + approvals** |
| **Default Environment** | Developer | Sandbox | **No direct access** |
| **Rule Documentation** | Optional | Recommended | **Mandatory with audit** |
| **Change Control** | Informal | Documented | **Formal approval** |

---

## FSI Example Configuration

```yaml
Environment Group: FSI-Regulated-Production
Description: "Enterprise-managed production environments for regulated agents"

Environments:
  - FSI-Wealth-Management-Prod
  - FSI-Client-Services-Prod
  - FSI-Compliance-Prod

Routing Rules:
  1. Rule: "Wealth Management Team"
     Type: Security Group
     Group: sg-wealth-management-makers
     Target: FSI-Wealth-Management-Prod
     Priority: 1

  2. Rule: "Client Services Team"
     Type: Security Group
     Group: sg-client-services-makers
     Target: FSI-Client-Services-Prod
     Priority: 2

  3. Rule: "Compliance Analysts"
     Type: Security Group
     Group: sg-compliance-makers
     Target: FSI-Compliance-Prod
     Priority: 3

Default Behavior: Route to sandbox if no rule matches
Warning: Users in no group are redirected to non-production
```

---

## Important Warning: Default Environment Fallback

> **CRITICAL:** Users who don't match any routing rule will be directed to the default environment. Ensure your default environment has appropriate governance controls or consider blocking unrouted users.

**FSI Recommendation:** Configure the default environment as a sandbox with strict DLP policies, or implement a "deny by default" approach where users must be explicitly granted access.

---

## Validation

After completing these steps, verify:

- [ ] Environment group is created with correct environments
- [ ] Routing rules target appropriate environments
- [ ] Rule priorities are correctly ordered
- [ ] Test users are routed as expected
- [ ] Default fallback behavior is acceptable
- [ ] Documentation is complete and approved

---

[Back to Control 2.15](../../../controls/pillar-2-management/2.15-environment-routing.md) | [PowerShell Setup](powershell-setup.md) | [Verification Testing](verification-testing.md) | [Troubleshooting](troubleshooting.md)
