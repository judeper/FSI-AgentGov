# Control 2.4: Business Continuity and Disaster Recovery - Troubleshooting

> This playbook provides troubleshooting guidance for [Control 2.4](../../../controls/pillar-2-management/2.4-business-continuity-and-disaster-recovery.md).

---

## Common Issues and Solutions

| Issue | Symptoms | Root Cause | Solution |
|-------|----------|------------|----------|
| DR environment out of sync | DR agents don't match production version | Sync pipeline failure | Check pipeline logs, verify permissions, manually sync |
| Connection failures in DR | Agents can't connect to data sources | DR connection references not configured | Update connection references for DR region |
| Backup pipeline failures | Scheduled backups not completing | Service connection expired | Renew credentials, test manual backup |
| RTO target not met | DR activation exceeds time target | Manual steps too slow | Automate runbook, increase DR env tier |

---

## Detailed Troubleshooting

### Issue 1: DR Environment Out of Sync

**Symptoms:** DR agents don't match production version

**Resolution:**

1. Check sync pipeline execution logs
2. Verify service connection permissions
3. Manually import latest solution:
   ```powershell
   # Export from production
   pac solution export --name "AgentSolution" --path ".\backup.zip" --managed true

   # Import to DR
   pac auth create --environment "https://org-dr.crm.dynamics.com"
   pac solution import --path ".\backup.zip"
   ```
4. Adjust sync schedule if needed
5. Enable alerting for sync failures

---

### Issue 2: Connection Failures in DR

**Symptoms:** Agents can't connect to data sources in DR

**Resolution:**

1. **Verify connection references updated for DR:**
   - Navigate to DR environment in Power Apps
   - Check Settings > Connection References
   - Update each reference to use DR-region connection

2. **Check service account permissions:**
   - Verify service accounts exist in DR region
   - Confirm appropriate roles assigned
   - Test individual connector authentication

3. **Validate network connectivity:**
   - Confirm DR environment can reach data sources
   - Check firewall rules for DR IP ranges
   - Verify VPN/ExpressRoute configuration

4. **Update OAuth tokens if expired:**
   - Re-authenticate connections in DR environment
   - Configure token refresh automation

5. **Test individual connectors:**
   - Create test flow to validate each connector
   - Document working configurations

---

### Issue 3: Backup Pipeline Failures

**Symptoms:** Scheduled backups not completing

**Resolution:**

1. **Review pipeline error logs:**
   - Check Azure DevOps pipeline run history
   - Identify specific task that failed
   - Review error messages

2. **Check service connection expiration:**
   - Navigate to Project Settings > Service connections
   - Verify Power Platform connection is valid
   - Renew credentials if expired

3. **Verify storage account accessibility:**
   - Confirm storage account exists and is accessible
   - Check container permissions
   - Verify network access rules

4. **Validate solution export permissions:**
   - Confirm service principal has System Administrator role
   - Check solution is not locked or in use

5. **Test manual backup:**
   ```powershell
   pac auth create --environment "https://org.crm.dynamics.com"
   pac solution export --name "AgentSolution" --path ".\test-backup.zip"
   ```

---

### Issue 4: RTO Target Not Met

**Symptoms:** DR activation exceeds time target

**Resolution:**

1. **Review and streamline runbook:**
   - Identify slow steps
   - Remove unnecessary approvals
   - Parallelize where possible

2. **Pre-stage more configuration in DR:**
   - Keep DR environment current (daily sync)
   - Pre-configure connection references
   - Maintain warm standby state

3. **Automate manual steps:**
   - Script DNS/routing changes
   - Automate notification distribution
   - Create one-click activation workflow

4. **Increase DR environment tier:**
   - Upgrade from sandbox to production
   - Increase compute capacity
   - Enable premium features

5. **Conduct additional training:**
   - Regular tabletop exercises
   - Document lessons learned
   - Update runbook with shortcuts

---

### Issue 5: Data Integrity Problems After Restore

**Symptoms:** Restored agent has missing or corrupted data

**Resolution:**

1. **Verify backup integrity:**
   - Check backup file size matches expected
   - Validate ZIP file is not corrupted
   - Compare solution component counts

2. **Check dependent data:**
   - Verify Dataverse tables restored
   - Check environment variable values
   - Confirm configuration data intact

3. **Restore from alternate backup:**
   - Identify last known good backup
   - Restore to test environment first
   - Validate before production restore

---

### Issue 6: Failback Data Conflicts

**Symptoms:** Changes made in DR conflict with primary data

**Resolution:**

1. **Document DR operation period:**
   - Note start/end times
   - Identify transactions processed in DR
   - Catalog configuration changes

2. **Export DR state before failback:**
   - Solution export from DR
   - Data export if applicable
   - Screenshot key configurations

3. **Merge changes carefully:**
   - Import DR changes to primary
   - Resolve conflicts manually
   - Test merged state thoroughly

4. **Consider forward-sync approach:**
   - Keep DR as new primary if changes significant
   - Update DNS permanently
   - Rebuild old primary as new DR

---

## Escalation Path

If issues cannot be resolved using this guide:

1. **Level 1:** IT Operations - Technical issues, pipeline failures
2. **Level 2:** Power Platform Admin - Environment configuration
3. **Level 3:** AI Governance Lead - Process and compliance issues
4. **Level 4:** Microsoft Support - Product-level issues

---

## Related Playbooks

- [Portal Walkthrough](./portal-walkthrough.md) - Step-by-step portal configuration
- [PowerShell Setup](./powershell-setup.md) - Automation scripts
- [Verification & Testing](./verification-testing.md) - Test procedures

---

*Updated: January 2026 | Version: v1.1*
