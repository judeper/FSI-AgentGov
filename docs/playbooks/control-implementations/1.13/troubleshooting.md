# Troubleshooting: Control 1.13 - Sensitive Information Types (SITs)

**Last Updated:** January 2026

## Common Issues

| Issue | Cause | Resolution |
|-------|-------|------------|
| SIT not detecting content | Pattern or keyword mismatch | Review regex; test in Content Explorer |
| High false positive rate | Confidence threshold too low | Increase confidence level; add context |
| Custom SIT not appearing | Publishing delay or permission | Wait 24 hours; verify admin role |
| EDM not matching | Schema mismatch or stale data | Verify schema; refresh hash table |
| DLP policy not triggering | SIT not included in policy | Add SIT to policy conditions |

---

## Detailed Troubleshooting

### Issue: SIT Not Detecting Expected Content

**Symptoms:** Documents with sensitive data not flagged in Content Explorer

**Diagnostic Steps:**

1. Verify SIT is published and active:
   ```
   Microsoft Purview > Data classification > Sensitive info types
   Check status is "Active"
   ```

2. Test SIT pattern manually:
   - Use Content Explorer to search for known sensitive content
   - Verify pattern matches expected format

3. Check confidence levels:
   - High confidence may require multiple evidence types
   - Lower confidence for testing, raise for production

**Resolution:**

- Adjust regex pattern to match actual data format
- Add supporting keywords to improve accuracy
- Lower confidence threshold for initial testing
- Wait 24-48 hours for classification to complete

---

### Issue: High False Positive Rate

**Symptoms:** SIT flags content that isn't actually sensitive

**Diagnostic Steps:**

1. Review flagged content in Content Explorer
2. Identify common false positive patterns
3. Check if supporting evidence is too broad

**Resolution:**

- Increase confidence threshold (65 → 75 → 85)
- Add negative keywords to exclude false positives
- Require multiple evidence types (primary + corroborative)
- Use proximity rules to require context

---

### Issue: Custom SIT Not Appearing

**Symptoms:** Created SIT not available in DLP policy configuration

**Diagnostic Steps:**

1. Check publishing status in Purview portal
2. Verify you have correct permissions
3. Check for validation errors in SIT definition

**Resolution:**

- Wait 24-48 hours for propagation
- Verify Purview Information Protection Admin role
- Review SIT definition for syntax errors
- Re-publish the SIT

---

### Issue: EDM Classifier Not Matching

**Symptoms:** Exact Data Match not detecting known customer data

**Diagnostic Steps:**

1. Verify EDM schema matches source data format
2. Check hash table upload status
3. Confirm data source is current

**Resolution:**

- Regenerate hash table from current data
- Verify column mappings match schema
- Check for data format changes (dates, phone numbers)
- Re-upload hash table after corrections

---

## How to Confirm Configuration is Active

### SIT Status

1. Navigate to Microsoft Purview compliance portal
2. Go to Data classification > Sensitive info types
3. Verify SIT shows "Active" status
4. Check "Last modified" date is current

### Detection Testing

1. Upload test document with known sensitive content
2. Wait 24-48 hours for classification
3. Search in Content Explorer for the SIT
4. Verify document appears in results

### DLP Integration

1. Create test DLP policy using the SIT
2. Set policy to "Test with notifications"
3. Test with sample content
4. Verify policy match in Activity Explorer

---

## Escalation Path

If issues persist after troubleshooting:

1. **Purview Info Protection Admin** - SIT configuration
2. **Purview Compliance Admin** - Policy configuration
3. **Microsoft Support** - Platform issues
4. **Legal/Compliance** - Classification requirements

---

## Known Limitations

| Limitation | Impact | Workaround |
|------------|--------|------------|
| 24-48 hour classification delay | Testing requires patience | Use Content Explorer preview |
| Regex complexity limits | Some patterns may not work | Simplify or split into multiple SITs |
| EDM 10M row limit | Large datasets need partitioning | Segment by business unit or region |
| Keyword dictionary 100K limit | Large dictionaries need splitting | Create multiple keyword lists |
| No real-time testing | Must wait for indexing | Use PowerShell for pattern testing |

---

[Back to Control 1.13](../../../controls/pillar-1-security/1.13-sensitive-information-types-sits-and-pattern-recognition.md) | [Portal Walkthrough](portal-walkthrough.md) | [PowerShell Setup](powershell-setup.md) | [Verification Testing](verification-testing.md)
