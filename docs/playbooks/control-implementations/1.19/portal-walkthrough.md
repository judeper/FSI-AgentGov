# Portal Walkthrough: Control 1.19 - eDiscovery for Agent Interactions

**Last Updated:** January 2026
**Portal:** Microsoft Purview
**Estimated Time:** 2-3 hours

## Prerequisites

- [ ] Purview eDiscovery Admin or eDiscovery Manager role
- [ ] Legal or compliance approval for case creation
- [ ] Agent content locations documented

---

## Step-by-Step Configuration

### Step 1: Configure eDiscovery Permissions

1. Open [Microsoft Purview](https://compliance.microsoft.com)
2. Navigate to **Roles & scopes** > **Permissions**
3. Assign eDiscovery Manager role to legal/compliance team

### Step 2: Document Agent Content Locations

Create inventory of agent content locations:

| Content Type | Location | Description |
|-------------|----------|-------------|
| Teams conversations | Exchange Online | Agent chat history |
| SharePoint documents | SharePoint Online | Knowledge source content |
| Audit logs | Purview Audit | Agent activity records |
| Dataverse records | Dataverse | Agent configurations |

### Step 3: Create eDiscovery Case

1. Navigate to **eDiscovery** > **Standard** or **Premium**
2. Click **Create case**
3. Configure:
   - Name: `FSI-Agent-Discovery-[Date]`
   - Description: Purpose and regulatory reference
   - Members: Assigned legal/compliance team

### Step 4: Create Content Search

1. In the case, create new search
2. Configure KeyQL query for agent content:
   ```
   kind:microsoftteams AND (from:"Copilot" OR subject:"Agent")
   ```
3. Select locations:
   - Exchange: All or specific mailboxes
   - SharePoint: Agent knowledge source sites
4. Run search and preview results

### Step 5: Configure Legal Hold

1. In case, create new hold
2. Name: `Hold-Agent-Content-[Matter]`
3. Select locations with agent content
4. Configure query if needed (or hold all content)
5. Activate hold

---

## Configuration by Governance Level

| Setting | Baseline (Tier 1) | Recommended (Tier 2) | Regulated (Tier 3) |
|---------|-------------------|----------------------|-------------------|
| **Case Creation** | As needed | Documented process | Approval workflow |
| **Legal Hold** | As needed | Case-by-case | Standing holds |
| **Export** | Standard | Tracked | Approval required |
| **Retention** | Standard | 6 years | 6+ years |
| **Drills** | None | Annual | Quarterly |

---

## FSI Example Configuration

```yaml
eDiscovery Case: FSI-FINRA-Inquiry-2026

Purpose: FINRA examination response
Regulatory Reference: FINRA Rule 4511

Searches:
  - Name: Agent-Trading-Conversations
    Query: kind:microsoftteams AND (from:"TradingBot" OR from:"Copilot")
    DateRange: 2025-01-01 to 2025-12-31

  - Name: Agent-Knowledge-Documents
    Location: /sites/TradingPolicies
    Query: sensitivitylabel:"Confidential"

Holds:
  - Name: Hold-TradingBot-Content
    Locations: Trading team mailboxes, TradingBot SharePoint
    Duration: Until case closed
```

---

## Validation

After completing these steps, verify:

- [ ] eDiscovery roles assigned appropriately
- [ ] Agent content locations documented
- [ ] Test search returns expected results
- [ ] Legal hold preserves content correctly
- [ ] Export produces usable evidence package

---

[Back to Control 1.19](../../../controls/pillar-1-security/1.19-ediscovery-for-agent-interactions.md) | [PowerShell Setup](powershell-setup.md) | [Verification Testing](verification-testing.md) | [Troubleshooting](troubleshooting.md)
