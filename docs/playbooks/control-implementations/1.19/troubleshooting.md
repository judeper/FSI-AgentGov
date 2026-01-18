# Troubleshooting: Control 1.19 - eDiscovery for Agent Interactions

**Last Updated:** January 2026

## Common Issues

| Issue | Cause | Resolution |
|-------|-------|------------|
| Search returns no results | Query syntax error | Validate KeyQL syntax |
| Cannot create case | Missing permissions | Assign eDiscovery Manager role |
| Export failing | Large result set | Split search or increase timeout |
| Hold not preserving | Location not specified | Add correct locations to hold |
| Audit events missing | Audit not enabled | Enable unified audit logging |

---

## Detailed Troubleshooting

### Issue: Search Returns No Results

**Symptoms:** Content search completes but shows zero items

**Diagnostic Steps:**

1. Verify query syntax is valid KeyQL
2. Check date range includes content period
3. Verify locations are correctly specified

**Resolution:**

- Test with broader query first
- Remove date filters to test
- Verify agent content exists in specified locations
- Check for retention policy deletions

---

### Issue: Cannot Create eDiscovery Case

**Symptoms:** Error when attempting to create case

**Resolution:**

- Verify eDiscovery Manager role assignment
- Check for Conditional Access blocking compliance portals
- Verify E5 or appropriate license
- Wait 24 hours after role assignment

---

## Escalation Path

1. **Purview eDiscovery Admin** - Case and search configuration
2. **Legal/Compliance** - Hold requirements
3. **Microsoft Support** - Platform issues

---

## Known Limitations

| Limitation | Impact | Workaround |
|------------|--------|------------|
| Search limit 1000 items preview | Large searches need export | Use export for full results |
| Export can take hours | Delays for large datasets | Plan ahead |
| Some agent content locations | Not all Dataverse content searchable | Document limitations |

---

[Back to Control 1.19](../../../controls/pillar-1-security/1.19-ediscovery-for-agent-interactions.md) | [Portal Walkthrough](portal-walkthrough.md) | [PowerShell Setup](powershell-setup.md) | [Verification Testing](verification-testing.md)
