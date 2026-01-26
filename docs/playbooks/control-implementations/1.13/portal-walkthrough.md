# Control 1.13: Sensitive Information Types (SITs) - Portal Walkthrough

> This playbook provides portal configuration guidance for [Control 1.13](../../../controls/pillar-1-security/1.13-sensitive-information-types-sits-and-pattern-recognition.md).

---

## Prerequisites

- Microsoft 365 E5 or E5 Compliance (full functionality)
- Purview Compliance Admin or Purview Info Protection Admin role
- Inventory of sensitive data types handled by organization
- Sample data patterns for custom SITs (sanitized)
- Test environment for SIT validation

---

## Step 1: Review Built-in Financial SITs

**Portal Path:** Microsoft Purview > Data classification > Classifiers > Sensitive info types

1. Navigate to [Microsoft Purview](https://purview.microsoft.com)
2. Go to **Data classification** > **Classifiers** > **Sensitive info types**
3. Filter by category: **Financial**
4. Review essential financial SITs:

| SIT Name | Use Case |
|----------|----------|
| U.S. Social Security Number (SSN) | Customer identification |
| U.S. Bank Account Number | Payment/transfer monitoring |
| Credit Card Number | PCI-DSS compliance |
| ABA Routing Number | Wire transfer protection |
| U.S. Individual Taxpayer ID (ITIN) | Tax document protection |
| CUSIP | Trading/portfolio data |

---

## Step 2: Create Custom FSI SITs

**Portal Path:** Data classification > Classifiers > Sensitive info types > + Create sensitive info type

### Custom SIT 1: Internal Account Number

1. Click **+ Create sensitive info type**
2. Configure:
   - **Name:** `FSI-Internal-Account-Number`
   - **Description:** "Detects internal customer account numbers"
3. Click **Next** > **Create pattern**
4. Add primary element:
   - **Type:** Regular expression
   - **Pattern:** `\b[A-Z]{3}-\d{6}-[A-Z0-9]{2}\b`
   - **Confidence level:** High (85)
5. Add supporting element:
   - **Keywords:** "account", "acct", "customer number"
   - **Within:** 300 characters
6. Click **Create**

### Custom SIT 2: FINRA CRD Number

1. Click **+ Create sensitive info type**
2. Configure:
   - **Name:** `FSI-FINRA-CRD-Number`
   - **Description:** "Detects FINRA Central Registration Depository numbers"
3. Add pattern:
   - **Type:** Regular expression
   - **Pattern:** `\b(?:CRD\s*#?\s*)?([1-9]\d{4,7})\b`
   - **Confidence level:** Medium (75)
4. Add supporting keywords: "CRD", "registered representative", "broker"
5. Click **Create**

### Custom SIT 3: MNPI Indicators

1. Click **+ Create sensitive info type**
2. Configure:
   - **Name:** `FSI-MNPI-Indicators`
   - **Description:** "Detects potential material non-public information"
3. Add pattern using keywords:
   - **Type:** Keyword dictionary
   - **Keywords:** "earnings announcement", "merger", "acquisition target", "quarterly results", "guidance revision", "SEC filing", "insider", "material information"
   - **Confidence level:** Medium (65)
4. Click **Create**

### Custom SIT 4: Trade Details

1. Click **+ Create sensitive info type**
2. Configure:
   - **Name:** `FSI-Trade-Details`
   - **Description:** "Detects trading activity patterns"
3. Add pattern:
   - **Type:** Regular expression
   - **Pattern:** `\b(BUY|SELL|HOLD)\s+\d+(?:,\d{3})*\s+(?:shares?|units?|contracts?)\s+(?:of\s+)?[A-Z]{1,5}\b`
4. Add supporting keywords: "execute", "trade", "order", "position"
5. Click **Create**

---

## Step 3: Create Keyword Dictionaries

**Portal Path:** Data classification > Classifiers > EDM classifiers > Keyword dictionaries

1. Click **Create keyword dictionary**
2. Configure:
   - **Name:** `FSI-Competitor-Names`
   - **Description:** "List of competitor companies for MNPI monitoring"
3. Enter keywords (one per line)
4. Click **Create**

---

## Step 4: Configure Exact Data Match (EDM)

**Portal Path:** Data classification > Classifiers > EDM classifiers

1. Click **+ Create EDM classifier**
2. Define schema:
   - **Name:** `FSI-Customer-Data-EDM`
   - **Description:** "Exact match for customer account data"
3. Add columns:
   - CustomerAccountNumber (searchable)
   - SSN (searchable)
   - CustomerName (supporting)
4. Configure matching rules
5. Upload hashed data source (see PowerShell playbook)

---

## Step 5: Test SIT Detection

**Portal Path:** Data classification > Content explorer

1. Create test document with sample sensitive data
2. Upload to SharePoint
3. Wait 24 hours for classification
4. Navigate to **Content explorer**
5. Filter by sensitive information type
6. Verify test data correctly identified
7. Check for true/false positives

---

## Step 6: Tune SIT Accuracy

### Reduce False Positives

1. Edit the SIT > Patterns
2. Add exclusions for common false positive formats
3. Add keyword requirements for context
4. Increase confidence threshold

### Reduce False Negatives

1. Edit the SIT > Patterns
2. Add pattern variations
3. Lower confidence threshold (carefully)
4. Add alternative keyword groups

---

[Back to Control 1.13](../../../controls/pillar-1-security/1.13-sensitive-information-types-sits-and-pattern-recognition.md) | [PowerShell Setup](powershell-setup.md) | [Verification Testing](verification-testing.md) | [Troubleshooting](troubleshooting.md)

---

*Updated: January 2026 | Version: v1.2*
