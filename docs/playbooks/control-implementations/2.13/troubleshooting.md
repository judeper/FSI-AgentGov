# Troubleshooting: Control 2.13 - Documentation and Record Keeping

**Last Updated:** January 2026

## Common Issues

| Issue | Cause | Resolution |
|-------|-------|------------|
| Retention label not applying | Auto-labeling not configured | Enable auto-labeling policy |
| WORM deletion blocked | Working as intended | Use legal hold exception if needed |
| Metadata not populated | Content type not applied | Apply correct content type |
| Search not finding records | Indexing delay | Wait for search crawl |

---

## Detailed Troubleshooting

### Issue: Retention Labels Not Auto-Applying

**Symptoms:** Documents uploaded without retention label

**Resolution:**

1. Verify auto-labeling policy exists
2. Check policy conditions match content
3. Verify policy is enabled
4. Wait for policy processing (can take 24-48 hours)

---

### Issue: Cannot Find Records for Examination

**Symptoms:** Search not returning expected results

**Resolution:**

1. Verify documents are in indexed locations
2. Check metadata is populated correctly
3. Use advanced search with metadata filters
4. Wait for search index to update

---

## Escalation Path

1. **SharePoint Admin** - Site and library configuration
2. **Purview Records Manager** - Retention policies
3. **Compliance Officer** - Regulatory requirements
4. **Legal** - Examination response

---

## Known Limitations

| Limitation | Impact | Workaround |
|------------|--------|------------|
| Auto-labeling delay | May take 24-48 hours | Apply labels manually for urgent |
| WORM is irreversible | Cannot shorten retention | Plan carefully before enabling |
| Search indexing delay | New docs not immediately searchable | Wait for crawl |
| Cross-site search complex | Hard to search across libraries | Use eDiscovery for comprehensive search |

---

[Back to Control 2.13](../../../controls/pillar-2-management/2.13-documentation-and-record-keeping.md) | [Portal Walkthrough](portal-walkthrough.md) | [PowerShell Setup](powershell-setup.md) | [Verification Testing](verification-testing.md)
