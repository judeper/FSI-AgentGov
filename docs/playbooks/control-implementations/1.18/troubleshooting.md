# Troubleshooting: Control 1.18 - Application-Level Authorization and RBAC

**Last Updated:** January 2026

## Common Issues

| Issue | Cause | Resolution |
|-------|-------|------------|
| User has too much access | Direct assignment vs group | Reassign via security group |
| PIM activation failing | Approval not configured | Verify approvers assigned |
| Security role not applying | User not synced | Wait for sync or force refresh |
| Column security not working | Profile not assigned | Assign field security profile |
| Access review stuck | No reviewers | Assign group owners as reviewers |

---

## Detailed Troubleshooting

### Issue: User Has More Access Than Expected

**Symptoms:** User can perform actions their role shouldn't allow

**Diagnostic Steps:**

1. Check direct role assignments
2. Verify security group memberships
3. Look for inherited permissions

**Resolution:**

- Remove direct role assignments
- Assign roles only through security groups
- Review team memberships in Dataverse
- Check for system administrator role assignments

---

### Issue: PIM Role Activation Failing

**Symptoms:** User cannot activate privileged role

**Diagnostic Steps:**

1. Verify PIM is configured for the role
2. Check if approval is required and approvers available
3. Verify user is eligible for the role

**Resolution:**

- Add user to eligible members
- Assign approvers if approval required
- Check for conflicting Conditional Access policies
- Verify MFA is completed if required

---

### Issue: Security Role Not Applying

**Symptoms:** User doesn't have expected permissions despite role assignment

**Diagnostic Steps:**

1. Verify role is assigned to correct security group
2. Check user is member of security group
3. Verify team exists and is linked to group

**Resolution:**

- Force sync of security group membership
- Verify Dataverse team is properly configured
- Clear user's browser cache
- Wait 15-30 minutes for propagation

---

## Escalation Path

1. **Power Platform Admin** - Role and environment configuration
2. **Entra Admin** - Security groups and PIM
3. **Dataverse Admin** - Security role privileges
4. **Microsoft Support** - Platform issues

---

## Known Limitations

| Limitation | Impact | Workaround |
|------------|--------|------------|
| Role sync delay | Up to 15 minutes | Plan ahead for changes |
| PIM max 8 hours | Long sessions need re-activation | Use permanent for service accounts |
| Limited custom roles | Some privileges cannot be separated | Use multiple roles |
| Column security performance | May slow queries | Limit fields covered |

---

[Back to Control 1.18](../../../controls/pillar-1-security/1.18-application-level-authorization-and-role-based-access-control-rbac.md) | [Portal Walkthrough](portal-walkthrough.md) | [PowerShell Setup](powershell-setup.md) | [Verification Testing](verification-testing.md)
