# Control 1.13: Sensitive Information Types (SITs) - Verification & Testing

> This playbook provides verification and testing guidance for [Control 1.13](../../../controls/pillar-1-security/1.13-sensitive-information-types-sits-and-pattern-recognition.md).

---

## Verification Steps

| Step | Action | Expected Result |
|------|--------|-----------------|
| 1 | Confirm built-in SITs available | Core financial SITs listed |
| 2 | Test SIT detection | Test data correctly identified |
| 3 | Verify custom SITs | All custom SITs created and active |
| 4 | Test DLP policy integration | Policy fires on SIT detection |
| 5 | Validate EDM classifier | Exact match detected |

---

## Test Cases

### Test 1: Built-in SIT Detection

1. Create test document with:
   - Test SSN: 123-45-6789
   - Test Credit Card: 4111-1111-1111-1111
2. Upload to SharePoint
3. Wait 24 hours for indexing
4. Check Content Explorer
5. **Expected:** SSN and credit card detected with high confidence

### Test 2: Custom SIT Detection

1. Create test document with custom patterns:
   - Internal account: ABC-123456-XY
   - CRD number: CRD# 1234567
2. Upload to monitored location
3. Wait for classification
4. **Expected:** Custom SITs detect test patterns

### Test 3: Keyword Dictionary

1. Create document mentioning competitor names
2. Verify keyword dictionary matches
3. **Expected:** Matches found for dictionary terms

### Test 4: DLP Policy Integration

1. Create test DLP policy using custom SIT
2. Trigger policy with test content
3. **Expected:** Policy fires on SIT detection
4. Verify alert/action occurs

### Test 5: EDM Exact Match

1. Upload test record to EDM data source
2. Create content matching exact data
3. **Expected:** EDM classifier matches exact data

---

## Evidence Artifacts

- [ ] Screenshot: Built-in financial SITs list
- [ ] Export: Custom SIT definitions (XML)
- [ ] Documentation: SIT pattern definitions and rationale
- [ ] Screenshot: Content Explorer showing detections
- [ ] Test results: True/false positive rates
- [ ] Documentation: EDM schema and refresh schedule

---

## Zone-Specific Testing

### Zone 1 (Personal Productivity)

- SITs Used: Basic built-in SITs
- Detection Mode: Alert only
- Confidence Threshold: High (85+)

### Zone 2 (Team Collaboration)

- SITs Used: Built-in + basic custom
- Detection Mode: Alert + educate
- Confidence Threshold: Medium-High (75-85)

### Zone 3 (Enterprise Managed)

- SITs Used: Full library + EDM
- Detection Mode: Block on high confidence
- Confidence Threshold: Medium (65+)

---

## SIT Accuracy Testing

| Test Type | Method | Target |
|-----------|--------|--------|
| True Positive | Test with known sensitive data | > 95% detection |
| False Positive | Test with non-sensitive lookalikes | < 5% false alerts |
| False Negative | Test with format variations | < 5% missed |

---

## Confirmation Checklist

- [ ] Built-in financial SITs reviewed
- [ ] Custom SITs created for org-specific patterns
- [ ] Keyword dictionaries configured
- [ ] EDM classifier configured (if needed)
- [ ] SIT detection tested with sample data
- [ ] Accuracy tuning completed
- [ ] Evidence artifacts collected

---

*Updated: January 2026 | Version: v1.2*
