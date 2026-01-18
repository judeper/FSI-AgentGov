# Troubleshooting: Control 1.14 - Data Minimization and Agent Scope Control

**Last Updated:** January 2026

## Common Issues

| Issue | Cause | Resolution |
|-------|-------|------------|
| DLP policy not blocking connector | Policy not applied to environment | Verify environment scope in policy |
| Agent accessing unauthorized data | Knowledge source too broad | Narrow to specific folder |
| Scope change not alerting | Alert policy misconfigured | Verify audit log and alert settings |
| Access review incomplete | No clear ownership | Assign reviewer responsibility |
| Cannot restrict existing connector | Active flows using connector | Migrate flows before blocking |

---

## Detailed Troubleshooting

### Issue: DLP Policy Not Blocking Connector

**Symptoms:** User can add blocked connector despite DLP policy

**Diagnostic Steps:**

1. Verify policy applies to the environment:
   ```
   PPAC > Policies > Data policies
   Check environment is in policy scope
   ```

2. Check connector classification:
   - Verify connector is in "Blocked" category
   - Check for policy exceptions

3. Verify policy is active (not in test mode)

**Resolution:**

- Add environment to policy scope
- Move connector to Blocked category
- Remove any exceptions allowing the connector
- Wait 15 minutes for policy propagation

---

### Issue: Agent Accessing Data Outside Approved Scope

**Symptoms:** Agent retrieves content from unauthorized locations

**Diagnostic Steps:**

1. Review knowledge source configuration:
   ```
   Copilot Studio > Agent > Knowledge
   List all configured sources
   ```

2. Check SharePoint permissions:
   - Agent service account may have broader access
   - Inherited permissions may grant unintended access

3. Review connector permissions (OAuth scopes)

**Resolution:**

- Narrow knowledge source to specific folder path
- Create dedicated SharePoint group with limited permissions
- Remove agent from groups with broader access
- Review and reduce OAuth scopes

---

### Issue: Scope Change Alert Not Firing

**Symptoms:** Changes to agent data sources not generating alerts

**Diagnostic Steps:**

1. Verify audit logging is enabled:
   ```
   Purview > Audit > Audit log search
   Search for recent connector changes
   ```

2. Check alert policy configuration:
   - Correct activities selected
   - Correct users/service accounts included
   - Notification recipients configured

3. Test alert with manual trigger

**Resolution:**

- Enable audit logging if disabled
- Update alert policy with correct activities
- Add service accounts to alert scope
- Verify email delivery for notifications

---

### Issue: Cannot Complete Access Review

**Symptoms:** Access review process stalled or incomplete

**Diagnostic Steps:**

1. Identify review owner and deadline
2. Check if inventory is current
3. Verify reviewer has authority to make decisions

**Resolution:**

- Assign clear ownership for each agent
- Provide reviewer with current inventory
- Establish escalation for stalled reviews
- Document review decisions even if "no change"

---

## How to Confirm Configuration is Active

### DLP Policy

1. Navigate to PPAC > Policies > Data policies
2. Open policy and verify environment is included
3. Confirm connector classifications are correct
4. Test by attempting to add blocked connector

### Knowledge Source Scoping

1. Open Copilot Studio > Agent > Knowledge
2. Verify each source shows specific path
3. Test agent cannot access content outside scope

### Scope Change Monitoring

1. Make a test change (add connector)
2. Verify audit event appears in Purview
3. Confirm alert notification received

---

## Escalation Path

If issues persist after troubleshooting:

1. **Power Platform Admin** - DLP and connector configuration
2. **SharePoint Admin** - Site permissions and access groups
3. **Purview Compliance Admin** - Audit logging and alerts
4. **AI Governance Lead** - Policy decisions and access review

---

## Known Limitations

| Limitation | Impact | Workaround |
|------------|--------|------------|
| DLP 15-minute propagation | Policy changes not immediate | Plan ahead for changes |
| No granular knowledge permissions | Folder-level only, not file-level | Organize content appropriately |
| Connector audit limited | Some connector activities not logged | Supplement with manual review |
| No automated access review | Manual process required | Create calendar reminders |
| OAuth scope visibility | Scopes may not be clearly displayed | Review connector documentation |

---

[Back to Control 1.14](../../../controls/pillar-1-security/1.14-data-minimization-and-agent-scope-control.md) | [Portal Walkthrough](portal-walkthrough.md) | [PowerShell Setup](powershell-setup.md) | [Verification Testing](verification-testing.md)
