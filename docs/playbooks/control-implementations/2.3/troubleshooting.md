# Control 2.3: Change Management and Release Planning - Troubleshooting

> This playbook provides troubleshooting guidance for [Control 2.3](../../../controls/pillar-2-management/2.3-change-management-and-release-planning.md).

---

## Common Issues and Solutions

| Issue | Symptoms | Root Cause | Solution |
|-------|----------|------------|----------|
| Pipeline deployment fails | "Access denied" error during import | Missing permissions on target environment | Verify user has Dataverse System Admin or Environment Admin role on target |
| Solution import conflicts | "Component already exists" warning | Unmanaged customizations in target | Enable "Overwrite Unmanaged Customizations" in import settings |
| Approval stuck in pending | Deployment blocked, no timeout | Approver hasn't received notification | Check Power Automate flow runs, verify approver email, check spam folder |
| Version mismatch after deploy | Deployed version differs from expected | Multiple solutions with same name | Use unique solution publisher prefix, verify solution uniquename |
| Rollback fails | Cannot restore previous version | Previous version not retained | Implement backup strategy, export before each deployment |

---

## Detailed Troubleshooting Steps

### Issue: Pipeline not visible in Power Apps

**Symptoms:** Users cannot see or access configured pipelines in the Power Apps maker portal.

**Steps to resolve:**

1. Verify user is assigned to the pipeline in host environment
2. Check that source environment is added to pipeline stages
3. Confirm user has minimum "Basic User" security role
4. Refresh the Power Apps browser session
5. Verify pipeline host environment is accessible

---

### Issue: Solution export fails with missing dependencies

**Symptoms:** Export operation fails with dependency error messages.

**Steps to resolve:**

1. Run Solution Checker on the solution before export
2. Identify missing dependencies in the error message
3. Add required dependent solutions to the target first
4. Use "Export including required components" option
5. Review solution component dependencies in maker portal

---

### Issue: Managed solution cannot be modified in target

**Symptoms:** Unable to edit components after importing managed solution.

**Explanation:** This is expected behavior for managed solutions (governance protection).

**Resolution:**

1. All changes must be made in the unmanaged source environment
2. Re-export and import the updated managed solution
3. For emergency fixes, use holding solutions (not recommended for production)

---

### Issue: Environment routing conflicts with pipeline targets

**Symptoms:** Agents or solutions deploy to unexpected environments.

**Steps to resolve:**

1. Verify Environment Routing rules don't override pipeline destinations
2. Check that pipeline target matches governance zone assignment
3. Review environment group membership and routing priorities
4. Consult with Platform Admin to align routing and pipeline configurations

---

### Issue: Approval workflow not triggering

**Symptoms:** Pipeline proceeds without expected approval gates.

**Steps to resolve:**

1. Verify approval gates are configured in pipeline settings
2. Check Power Automate flow is active and connected
3. Verify approver has appropriate license
4. Check connection status in Power Automate
5. Review flow run history for errors

---

### Issue: Solution checker errors blocking deployment

**Symptoms:** Pipeline fails at solution checker stage.

**Steps to resolve:**

1. Review solution checker results in maker portal
2. Address critical and high severity issues
3. Document accepted risks for medium/low issues if appropriate
4. Re-run solution checker to verify fixes
5. Consider excluding non-critical rules if justified

---

### Issue: Cross-region deployment failures

**Symptoms:** Deployment fails when source and target are in different regions.

**Steps to resolve:**

1. Verify "Solution deployments across regions" is enabled in PPAC Deployment Settings
2. Check network connectivity between regions
3. Verify data residency requirements allow cross-region deployment
4. Consider using export/import instead of pipeline for cross-region

---

### Issue: Version number not incrementing

**Symptoms:** Multiple deployments show same version number.

**Steps to resolve:**

1. Verify version is updated in source environment before export
2. Check solution version management scripts are running
3. Manually update version if automation failed
4. Review version numbering convention compliance

---

## Rollback-Specific Issues

### Issue: Cannot find previous solution version

**Symptoms:** Need to rollback but backup is missing.

**Steps to resolve:**

1. Check backup storage location per zone requirements
2. Search for solution export files with timestamps
3. Check if solution history is available in Dataverse
4. Contact IT Operations for backup recovery

---

### Issue: Rollback causes data conflicts

**Symptoms:** Previous solution version conflicts with current data state.

**Steps to resolve:**

1. Assess data changes made since original deployment
2. Create data export before rollback
3. Plan data migration strategy post-rollback
4. Consider forward-fix instead of rollback if data impact is high

---

## Escalation Path

If issues cannot be resolved using this guide:

1. **Level 1:** Power Platform Admin - Technical configuration issues
2. **Level 2:** AI Governance Lead - Process and workflow issues
3. **Level 3:** Compliance Officer - Regulatory impact assessment
4. **Level 4:** Microsoft Support - Product-level issues

---

## Related Playbooks

- [Portal Walkthrough](./portal-walkthrough.md) - Step-by-step portal configuration
- [PowerShell Setup](./powershell-setup.md) - Automation scripts
- [Verification & Testing](./verification-testing.md) - Test procedures

---

*Updated: January 2026 | Version: v1.2*
