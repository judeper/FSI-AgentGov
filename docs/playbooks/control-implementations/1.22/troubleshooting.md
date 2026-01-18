# Troubleshooting: Control 1.22 - Information Barriers

**Last Updated:** January 2026

## Common Issues

| Issue | Cause | Resolution |
|-------|-------|------------|
| User not in segment | Department attribute missing | Populate Entra ID attribute |
| Policy not applying | Application not started | Run Start-InformationBarrierPoliciesApplication |
| Barrier not enforcing | User without segment | Ensure all users have segments |
| SharePoint access despite barrier | Site permissions override | Align SharePoint permissions |

---

## Detailed Troubleshooting

### Issue: User Not Assigned to Segment

**Symptoms:** User can access content they shouldn't

**Resolution:**

1. Verify user's Department attribute in Entra ID
2. Check segment filter matches attribute value
3. Run policy application after fixing
4. Wait for propagation (can take hours)

---

### Issue: Policy Application Stuck

**Symptoms:** Status shows "InProgress" for extended period

**Resolution:**

1. Check for conflicting policies
2. Verify all segments have valid filters
3. Contact Microsoft Support if stuck > 24 hours

---

## Escalation Path

1. **Purview Compliance Admin** - Segment and policy configuration
2. **SharePoint Admin** - Site permission alignment
3. **Entra Admin** - User attribute population
4. **Microsoft Support** - Policy application issues

---

## Known Limitations

| Limitation | Impact | Workaround |
|------------|--------|------------|
| Application can take hours | Delays after changes | Plan ahead |
| Users without segments bypass | Security gap | Ensure 100% coverage |
| Complex hierarchies | Difficult to model | Simplify segment structure |
| Teams/SharePoint sync delay | May see temporary access | Wait for full propagation |

---

[Back to Control 1.22](../../../controls/pillar-1-security/1.22-information-barriers.md) | [Portal Walkthrough](portal-walkthrough.md) | [PowerShell Setup](powershell-setup.md) | [Verification Testing](verification-testing.md)
