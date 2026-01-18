# Troubleshooting: Control 2.8 - Access Control and Segregation of Duties

**Last Updated:** January 2026

## Common Issues

| Issue | Cause | Resolution |
|-------|-------|------------|
| PIM activation fails | User not eligible | Add user as eligible member |
| SoD check shows violations | User in conflicting groups | Remove from one group |
| Access review not completing | Reviewers not responding | Send reminder, extend deadline |
| Approval workflow not triggering | Flow disabled or misconfigured | Check Power Automate flow status |

---

## Detailed Troubleshooting

### Issue: User Cannot Activate PIM Role

**Symptoms:** User sees "not eligible" error when activating role

**Resolution:**

1. Verify user is added as **eligible** (not active) member
2. Check PIM policy allows activation duration requested
3. Verify any required approvers are available
4. Check if user's activation request is pending approval

---

### Issue: SoD Violation Detected

**Symptoms:** User appears in multiple conflicting role groups

**Resolution:**

1. Identify which roles are in conflict
2. Determine user's primary function
3. Remove user from the group not aligned with their role
4. Document exception if business justification exists (requires Compliance Officer approval)

---

### Issue: Access Review Stalled

**Symptoms:** Access review shows low completion rate

**Resolution:**

1. Send reminder notifications to pending reviewers
2. Check if reviewers have left the organization
3. Extend review deadline if needed
4. Configure auto-deny for non-responses (if appropriate)

---

## Escalation Path

1. **Entra Admin** - Group membership, PIM configuration
2. **Power Platform Admin** - Security role configuration
3. **AI Governance Lead** - SoD policy decisions
4. **Compliance Officer** - Exception approvals

---

## Known Limitations

| Limitation | Impact | Workaround |
|------------|--------|------------|
| PIM requires P2 license | Cannot use JIT access without license | Use standard group membership with monitoring |
| No cross-platform SoD | Entra groups separate from Power Platform roles | Document mapping, manual validation |
| Access review max 14 days | May not complete for large groups | Run multiple smaller reviews |
| Manual SoD check | Script must be run periodically | Schedule as automation or weekly task |

---

[Back to Control 2.8](../../../controls/pillar-2-management/2.8-access-control-and-segregation-of-duties.md) | [Portal Walkthrough](portal-walkthrough.md) | [PowerShell Setup](powershell-setup.md) | [Verification Testing](verification-testing.md)
