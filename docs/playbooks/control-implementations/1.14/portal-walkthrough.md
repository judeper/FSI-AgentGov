# Portal Walkthrough: Control 1.14 - Data Minimization and Agent Scope Control

**Last Updated:** January 2026
**Portal:** Power Platform Admin Center, Copilot Studio, Microsoft Purview
**Estimated Time:** 2-4 hours initial setup, ongoing maintenance

## Prerequisites

- [ ] Power Platform Admin or Environment Admin role
- [ ] SharePoint Admin access for site permissions
- [ ] Purview Compliance Admin for audit alerts
- [ ] Agent inventory completed (Control 1.2)

---

## Step-by-Step Configuration

### Step 1: Create Agent Data Access Inventory

Document all data sources accessed by each agent:

1. Open [Power Platform Admin Center](https://admin.powerplatform.microsoft.com)
2. Navigate to **Environments** > Select environment
3. Select **Resources** > **Copilot Studio agents**
4. For each agent, document:

| Agent Name | Data Source | Data Type | Classification | Justification |
|------------|-------------|-----------|----------------|---------------|
| [Agent] | SharePoint | Documents | Confidential | [Business need] |
| [Agent] | Dataverse | Customer records | Restricted | [Business need] |

### Step 2: Configure Connector Restrictions

1. Navigate to **Policies** > **Data policies**
2. Create or edit DLP policy for the environment
3. Classify connectors:
   - **Business** - Approved data sources
   - **Non-business** - Personal/consumer services
   - **Blocked** - Prohibited connectors

4. Apply connector restrictions:
   ```
   Business: SharePoint, Dataverse, SQL Server
   Non-business: Twitter, Facebook
   Blocked: Dropbox, Google Drive (consumer)
   ```

### Step 3: Scope Knowledge Sources

1. Open [Copilot Studio](https://copilotstudio.microsoft.com)
2. Select agent > **Knowledge**
3. Review each knowledge source:
   - Verify scope is specific folder, not entire site
   - Remove unnecessary sources
   - Document justification for each source

**Best Practice:**
```
✅ Good: /sites/HR/Policies/Benefits
❌ Bad: /sites/HR (entire site)
```

### Step 4: Create Agent Access SharePoint Groups

1. Open [SharePoint Admin Center](https://admin.microsoft.com/sharepoint)
2. Navigate to the site used as knowledge source
3. Create dedicated group: `SG-AgentAccess-[AgentName]`
4. Assign minimum permissions (typically Read)
5. Add agent service account to group

### Step 5: Configure Scope Change Alerts

1. Open [Microsoft Purview](https://compliance.microsoft.com)
2. Navigate to **Audit** > **Audit log search**
3. Create alert policy:
   - Name: "Agent Scope Change Alert"
   - Activity: ConnectorAdded, KnowledgeSourceAdded
   - Users: Agent service accounts
   - Notification: AI Governance Lead

---

## Configuration by Governance Level

| Setting | Baseline (Tier 1) | Recommended (Tier 2) | Regulated (Tier 3) |
|---------|-------------------|----------------------|-------------------|
| **Access Review** | Annual | Quarterly | Monthly |
| **DLP Policy** | Standard | Enhanced | Strict allowlist |
| **Scope Changes** | Self-service | Manager approval | CISO approval |
| **Monitoring** | Periodic audit | Alert on changes | Real-time |
| **Documentation** | Basic inventory | Full justification | Formal approval chain |

---

## FSI Example Configuration

```yaml
Agent: Investment Advisory Bot
Environment: FSI-Production-Zone3

Data Sources:
  - Source: SharePoint - /sites/InvestmentResearch/Approved
    Classification: Confidential
    Justification: Market research for client recommendations
    Approved By: Investment Committee
    Review Date: 2026-04-01

  - Source: Dataverse - CustomerProfiles (read-only)
    Classification: Restricted
    Justification: Customer suitability assessment
    Approved By: CISO
    Review Date: 2026-04-01

Connector Policy:
  Allowed: SharePoint, Dataverse
  Blocked: All others

Access Review:
  Frequency: Monthly
  Reviewer: Investment Operations Manager
  Escalation: CISO
```

---

## Validation

After completing these steps, verify:

- [ ] Agent data access inventory is complete and documented
- [ ] Connector restrictions are applied via DLP policy
- [ ] Knowledge sources are scoped to specific folders
- [ ] Agent access groups have minimum permissions
- [ ] Scope change alerts are configured and tested

---

[Back to Control 1.14](../../../controls/pillar-1-security/1.14-data-minimization-and-agent-scope-control.md) | [PowerShell Setup](powershell-setup.md) | [Verification Testing](verification-testing.md) | [Troubleshooting](troubleshooting.md)
