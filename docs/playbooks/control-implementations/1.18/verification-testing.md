# Verification & Testing: Control 1.18 - Application-Level Authorization and RBAC

**Last Updated:** January 2026

## Manual Verification Steps

### Test 1: Verify Viewer Role Restrictions

1. Log in as user with FSI - Agent Viewer role
2. Navigate to Copilot Studio
3. Attempt to create new agent
4. **EXPECTED:** Create option disabled or error on attempt

### Test 2: Verify PIM Activation Required

1. Log in as Power Platform Admin (without PIM activation)
2. Attempt admin action (e.g., modify environment)
3. **EXPECTED:** Access denied until PIM role activated

### Test 3: Verify Column-Level Security

1. Log in as user without sensitive field access
2. Open record with sensitive fields (SSN, Account Balance)
3. **EXPECTED:** Sensitive fields hidden or show asterisks

### Test 4: Verify Access Review Process

1. Navigate to Entra > Access Reviews
2. Locate review for security group
3. **EXPECTED:** Review scheduled and reviewers assigned

### Test 5: Export Role Assignments

1. Run Export-SecurityRoles.ps1 script
2. Review exported data
3. **EXPECTED:** All assignments documented with no orphaned accounts

---

## Test Cases

| Test ID | Scenario | Expected Result | Pass/Fail |
|---------|----------|-----------------|-----------|
| TC-1.18-01 | Viewer cannot create agent | Action blocked | |
| TC-1.18-02 | Admin requires PIM | Must activate role | |
| TC-1.18-03 | Sensitive fields hidden | Field security enforced | |
| TC-1.18-04 | Service principal rotation | Credentials rotated | |
| TC-1.18-05 | Access review scheduled | Review active | |
| TC-1.18-06 | Role assignment export | Complete export | |

---

## Evidence Collection Checklist

- [ ] Export: Security role assignments (CSV)
- [ ] Screenshot: Custom security role configuration
- [ ] Screenshot: PIM settings for admin roles
- [ ] Screenshot: Access review configuration
- [ ] Document: Role-to-group mapping

---

## Attestation Statement Template

```markdown
## Control 1.18 Attestation - RBAC

**Organization:** [Organization Name]
**Control Owner:** [Name/Role]
**Date:** [Date]

I attest that:

1. Custom security roles are implemented with least-privilege access
2. Role assignments are made to security groups (not individuals)
3. PIM is configured for privileged roles:
   - Max activation: [Duration]
   - Approval required: [Yes/No]
4. Access reviews are scheduled:
   - Zone 1: [Annual]
   - Zone 2: [Semi-annual]
   - Zone 3: [Quarterly]
5. Column-level security protects sensitive fields

**Last Access Review:** [Date]
**Next Access Review:** [Date]

**Signature:** _______________________
**Date:** _______________________
```

---

[Back to Control 1.18](../../../controls/pillar-1-security/1.18-application-level-authorization-and-role-based-access-control-rbac.md) | [Portal Walkthrough](portal-walkthrough.md) | [PowerShell Setup](powershell-setup.md) | [Troubleshooting](troubleshooting.md)
