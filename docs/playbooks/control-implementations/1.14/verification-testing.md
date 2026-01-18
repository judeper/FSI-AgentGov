# Verification & Testing: Control 1.14 - Data Minimization and Agent Scope Control

**Last Updated:** January 2026

## Manual Verification Steps

### Test 1: Verify Data Access Inventory Exists

1. Request agent data access inventory document
2. Confirm all production agents are listed
3. Verify each data source has documented justification
4. **EXPECTED:** Complete inventory with business justifications

### Test 2: Verify Connector Restrictions

1. Open Power Platform Admin Center
2. Navigate to Policies > Data policies
3. Verify DLP policy covers the environment
4. Confirm blocked/restricted connectors are enforced
5. **EXPECTED:** DLP policy active with appropriate restrictions

### Test 3: Verify Knowledge Source Scoping

1. Open Copilot Studio
2. Select Zone 3 agent > Knowledge
3. Review each knowledge source path
4. **EXPECTED:** Sources scoped to specific folders, not entire sites

### Test 4: Test Blocked Connector

1. Attempt to add a blocked connector to test agent
2. **EXPECTED:** Action blocked by DLP policy with error message

### Test 5: Verify Access Review Process

1. Request documentation of last access review
2. Confirm review completed within required timeframe
3. Verify reviewer has appropriate authority
4. **EXPECTED:** Documented review with decisions and approvals

---

## Test Cases

| Test ID | Scenario | Expected Result | Pass/Fail |
|---------|----------|-----------------|-----------|
| TC-1.14-01 | Agent inventory exists | All agents documented | |
| TC-1.14-02 | Data sources have justification | Business need documented | |
| TC-1.14-03 | DLP policy enforced | Blocked connectors rejected | |
| TC-1.14-04 | Knowledge sources scoped | Folder-level, not site-level | |
| TC-1.14-05 | Scope change alert fires | Alert received on change | |
| TC-1.14-06 | Access review completed | Within required timeframe | |
| TC-1.14-07 | Unauthorized connector blocked | DLP prevents addition | |

---

## Evidence Collection Checklist

### Data Access Inventory

- [ ] Document: Agent data access inventory (spreadsheet)
- [ ] Screenshot: DLP policy configuration
- [ ] Screenshot: Connector classification settings

### Knowledge Source Configuration

- [ ] Screenshot: Knowledge source settings per agent
- [ ] Document: Justification for each data source
- [ ] Screenshot: SharePoint permissions for agent groups

### Access Review Evidence

- [ ] Document: Access review schedule
- [ ] Document: Last review findings and decisions
- [ ] Screenshot: Approval workflow configuration

### Monitoring

- [ ] Screenshot: Scope change alert configuration
- [ ] Export: Recent scope change audit events

---

## Evidence Artifact Naming Convention

```
Control-1.14_[ArtifactType]_[YYYYMMDD].[ext]

Examples:
- Control-1.14_DataAccessInventory_20260115.xlsx
- Control-1.14_DLPPolicyConfig_20260115.png
- Control-1.14_AccessReviewLog_20260115.pdf
- Control-1.14_ScopeChangeAlert_20260115.png
```

---

## Attestation Statement Template

```markdown
## Control 1.14 Attestation - Data Minimization

**Organization:** [Organization Name]
**Control Owner:** [Name/Role]
**Date:** [Date]

I attest that:

1. Agent data access inventory is maintained and current
2. All data sources have documented business justification
3. DLP connector restrictions are enforced for all environments
4. Knowledge sources are scoped to minimum necessary
5. Scope change alerts are configured and monitored
6. Access reviews completed per schedule:
   - Zone 1: Annual
   - Zone 2: Quarterly
   - Zone 3: Monthly

**Last Review Date:** [Date]
**Next Review Date:** [Date]
**Agents Reviewed:** [Count]

**Signature:** _______________________
**Date:** _______________________
```

---

[Back to Control 1.14](../../../controls/pillar-1-security/1.14-data-minimization-and-agent-scope-control.md) | [Portal Walkthrough](portal-walkthrough.md) | [PowerShell Setup](powershell-setup.md) | [Troubleshooting](troubleshooting.md)
