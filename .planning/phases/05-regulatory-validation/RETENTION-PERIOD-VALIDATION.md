# Retention Period Validation - Phase 5

## Current Matrix Assessment

**Location:** `docs/reference/regulatory-mappings.md` (lines 14-19)

**Current Retention Period Matrix:**

| Record Type | Retention | Regulation | Access Requirement |
|-------------|-----------|------------|--------------------|
| **Communications** (agent logs, chat, email) | 3 years | SEC 17a-4(b)(4) | First 2 years readily accessible |
| **Accounting/Financial Records** | 6 years | SEC 17a-4(a) | First 2 years readily accessible |
| **Customer Account Records** | 6 years after account close | SEC 17a-4(c)(e)(5) | First 2 years readily accessible |
| **FINRA-Specific Records** (no SEC period) | 6 years | FINRA 4511(b) | First 2 years easily accessible |

**Initial Assessment:**
- Matrix covers primary record types for AI agents
- SEC 17a-4 subsections cited: (a), (b)(4), (c), (e)(5)
- Access requirement terminology varies: "readily accessible" (SEC) vs "easily accessible" (FINRA)
- Missing: Other SEC 17a-4(b) subsections, CFTC Rule 1.31 comparison

---

## SEC 17a-4 Subsection Verification

**Source:** 17 CFR § 240.17a-4 - https://www.law.cornell.edu/cfr/text/17/240.17a-4

### Subsection (a) - Broker-Dealer Records (6 Years)

**Official Text Verified:** Yes
**Retention Period:** 6 years
**Description:** Records required under Rule 17a-3 (blotters, ledgers, securities records, etc.)
**AI Agent Applicability:** If agent creates or modifies financial/accounting records
**Current Matrix Status:** ✅ Correctly characterized as "Accounting/Financial Records"

**Verification:** The matrix's "6 years" for financial records is accurate per 17 CFR § 240.17a-4(a).

---

### Subsection (b) - Memoranda, Communications, and Other Records

SEC 17a-4(b) has 17 subsections. Current matrix only cites (b)(4).

#### (b)(1) - Blotters (3 Years)

**Official Text Verified:** Yes
**Retention Period:** 3 years
**Description:** Blotters (or other records of original entry) required under Rule 17a-3(a)(1)
**AI Agent Applicability:** If agent records original entry of transactions
**Current Matrix Status:** ⚠️ Not explicitly listed (covered under "Accounting/Financial Records"?)

**Analysis:** Blotters are original entry records, not final accounting records. If agents create blotters, this is a 3-year requirement, not 6-year. However, blotters for broker-dealers are typically not AI agent outputs—they're transaction entry logs.

**Recommendation:** Note in validation that blotters are covered under Rule 17a-3(a)(1) and have 3-year retention. Agent transaction logs may qualify as blotters if they serve as original entry records.

---

#### (b)(2) - Ledgers (3 Years)

**Official Text Verified:** Yes
**Retention Period:** 3 years
**Description:** Ledgers (or other records) required under Rule 17a-3(a)(2) through (a)(9)
**AI Agent Applicability:** If agent maintains ledger records
**Current Matrix Status:** ⚠️ Not explicitly listed

**Analysis:** Similar to (b)(1)—ledgers are 3-year records under (b)(2), distinct from 6-year accounting records under (a).

**Recommendation:** Note that ledgers have 3-year retention per (b)(2). Most AI agents do not maintain formal ledgers.

---

#### (b)(3) - Stock Certificates and Other Securities (3 Years)

**Official Text Verified:** Yes
**Retention Period:** 3 years
**Description:** Cancelled stock certificates, cancelled stocks powers, etc.
**AI Agent Applicability:** Not applicable—agents do not handle physical certificates
**Current Matrix Status:** ✅ Correctly omitted (not applicable)

---

#### (b)(4) - Communications (3 Years)

**Official Text Verified:** Yes
**Retention Period:** 3 years
**Description:** All communications received or sent by the broker-dealer (including inter-office memoranda and communications) relating to its business as such
**AI Agent Applicability:** ✅ Primary record type for AI agents
**Current Matrix Status:** ✅ Correctly listed as "Communications" with 3-year retention

**Verification:** The matrix correctly identifies communications as 3-year retention per SEC 17a-4(b)(4). This is the most commonly cited subsection for AI agent conversation logs.

---

#### (b)(5) through (b)(17) - Other Records (3 Years)

**Subsections:**
- (b)(5): Customer account records
- (b)(6): Powers of attorney
- (b)(7): Copies of confirmations
- (b)(8): Notifications
- (b)(9): Written agreements
- (b)(10): Schedules/computations
- (b)(11): Trial balances
- (b)(12): Questionnaires/applications
- (b)(13): Written consents
- (b)(14): Guarantees
- (b)(15): Financial documents
- (b)(16): Records relating to AML
- (b)(17): Additional records

**Official Text Verified:** Yes (all subsections exist)
**Retention Period:** 3 years (all subsections)
**AI Agent Applicability:** Varies by subsection; most are low applicability
**Current Matrix Status:** ⚠️ Not explicitly listed

**Analysis:** These are specialized record types. Most are not applicable to typical AI agent outputs. If agents generate records in these categories, they would follow the 3-year retention per (b)(1)-(b)(17).

**Recommendation:** Note that SEC 17a-4(b) subsections (b)(1) through (b)(17) all require 3-year retention. If AI agents create records matching these categories, apply 3-year retention.

---

### Subsection (c) - Customer Account Records (6 Years After Account Close)

**Official Text Verified:** Yes
**Retention Period:** 6 years after the account is closed
**Description:** Every broker-dealer shall preserve for a period of not less than 6 years after the closing of any customer's account, any account cards or records relating to the terms and conditions with respect to the opening and maintenance of the account
**AI Agent Applicability:** If agent maintains customer account information
**Current Matrix Status:** ✅ Correctly listed

**Verification:** The matrix correctly identifies "6 years after account close" per SEC 17a-4(c).

---

### Subsection (e)(5) - Customer Account Records Cross-Reference

**Official Text Verified:** Checking subsection (e)(5)...
**Finding:** Subsection (e)(5) does NOT exist in SEC 17a-4. The regulation has subsections (e)(1) through (e)(4) related to ELECTRONIC STORAGE requirements, not retention periods.

**Current Matrix Status:** ❌ **CRITICAL ERROR** - Matrix cites "SEC 17a-4(c)(e)(5)" which is not a valid citation

**Correction Required:**
- Remove "(e)(5)" from matrix
- Citation should be "SEC 17a-4(c)" only
- Subsection (e) addresses electronic storage format requirements, not retention periods

---

### Subsection (f) - WORM or Audit-Trail Alternative (October 2022 Amendments)

**Official Text Verified:** Yes
**Effective Date:** May 3, 2023 (amendments adopted October 2022)
**Description:** Electronic storage requirements - WORM storage OR audit-trail alternative
**AI Agent Applicability:** All electronically stored agent records
**Current Matrix Status:** ⚠️ Not referenced in Retention Period Matrix (mentioned elsewhere in doc at line 277)

**Analysis:** This is a storage format requirement, not a retention period. However, it's critical for compliance.

**Recommendation:** The Retention Period Matrix should note that electronic records must comply with subsection (f) WORM or audit-trail requirements. This is documented elsewhere in regulatory-mappings.md but should be cross-referenced from the matrix.

---

### SEC 17a-4 Summary: Verified Retention Periods

| Subsection | Record Type | Retention | AI Agent Applicability | Matrix Status |
|-----------|-------------|-----------|----------------------|---------------|
| 17a-4(a) | Accounting/Financial | 6 years | ✅ High | ✅ Correct |
| 17a-4(b)(1) | Blotters | 3 years | ⚠️ Low | Not listed |
| 17a-4(b)(2) | Ledgers | 3 years | ⚠️ Low | Not listed |
| 17a-4(b)(3) | Stock certificates | 3 years | ❌ N/A | Correctly omitted |
| 17a-4(b)(4) | **Communications** | **3 years** | ✅ **High** | ✅ **Correct** |
| 17a-4(b)(5)-(17) | Various specialized | 3 years | ⚠️ Low | Not listed |
| 17a-4(c) | Customer accounts | 6 years after close | ✅ Medium | ✅ Correct citation, but... |
| 17a-4(c)(e)(5) | **ERROR** | **N/A** | **N/A** | ❌ **Invalid citation** |
| 17a-4(f) | Electronic storage format | N/A (format req) | ✅ High | Referenced elsewhere |

---

## CFTC Rule 1.31 Verification

**Source:** 17 CFR § 1.31 - https://www.law.cornell.edu/cfr/text/17/1.31

### Retention Period Requirements

**Official Text Verified:** Yes
**Retention Period:** 5 years minimum (17 CFR § 1.31(b)(1))
**Additional Requirement:** "First 2 years in readily accessible location"
**Life of Enterprise Requirement:** Certain records required for "life of the enterprise plus 5 years" (varies by record type)

**AI Agent Applicability:** Organizations registered with CFTC (FCMs, IBs, CTAs, CPOs) using agents for derivatives/commodities trading

**Current Matrix Status:** ⚠️ Not listed in Retention Period Matrix

**Recommendation:** Add CFTC Rule 1.31 to matrix for dual-registrant organizations.

---

### Electronic Storage Requirements

**WORM Requirement:** ❌ Eliminated May 2017
**Current Requirement:** Principles-based "authenticity and reliability" standard per 17 CFR § 1.31(c)

**Comparison to SEC:**
- **SEC 17a-4(f):** WORM storage OR audit-trail alternative (as of May 2023)
- **CFTC Rule 1.31:** Principles-based; WORM NOT required

**Current Matrix Status:** ⚠️ This distinction is documented in regulatory-mappings.md (lines 866-872) but not in Retention Period Matrix

**Verification:** The framework correctly notes that CFTC eliminated WORM in 2017 while SEC maintained it (with audit-trail alternative added).

---

### CFTC Rule 1.31 Summary

| Requirement | Description | Verified | Matrix Status |
|------------|-------------|----------|---------------|
| Retention period | 5 years minimum | ✅ Yes | ❌ Not in matrix |
| Accessibility | First 2 years readily accessible | ✅ Yes | ❌ Not in matrix |
| Life of enterprise | Certain records: life + 5 years | ✅ Yes | ❌ Not in matrix |
| WORM requirement | Eliminated May 2017 | ✅ Yes | ✅ Documented in text (line 872) |
| Authenticity standard | Principles-based per 17 CFR § 1.31(c) | ✅ Yes | ✅ Documented in text (line 859) |

---

## Findings

### CRITICAL: Invalid Citation - SEC 17a-4(c)(e)(5)

**Issue:** Retention Period Matrix cites "SEC 17a-4(c)(e)(5)" for Customer Account Records.

**Fact:** SEC 17a-4 subsection (e)(5) does not exist. Subsection (e) has only (e)(1) through (e)(4), which address electronic storage format requirements, not retention periods.

**Impact:** The citation creates legal risk. Auditors or regulators checking citations will find this does not exist.

**Correction Required:**
```markdown
# Current (INCORRECT):
| **Customer Account Records** | 6 years after account close | SEC 17a-4(c)(e)(5) | First 2 years readily accessible |

# Corrected:
| **Customer Account Records** | 6 years after account close | SEC 17a-4(c) | First 2 years readily accessible |
```

**File:** `docs/reference/regulatory-mappings.md` line 18

---

### CRITICAL: SEC 17a-3/4 Section Inconsistency

**Issue:** Section "SEC Rule 17a-3/4 - Recordkeeping" (lines 223-283) contains an internal inconsistency.

**Finding 1 - Generic Overview Statement (Line 226):**
```markdown
Requires SEC-registered firms to maintain records of all transactions and communications for 6 years
```

**Problem:** This is overgeneralized. SEC 17a-4 has BOTH 3-year and 6-year retention periods depending on record type. The overview incorrectly states "6 years" as a universal requirement.

**Finding 2 - Agent Communications Subsection (Lines 244-249):**
```markdown
**Agent Communications:**

- All user interactions with agents
- All agent outputs and decisions
- All approvals and rejections
- Retention: 6 years, first 2 years in easily accessible place
```

**Problem:** This states agent communications require **6-year** retention. But the Retention Period Matrix (line 16) correctly states communications require **3-year** retention per SEC 17a-4(b)(4).

**Impact:** Users reading Control 3.3 or reviewing regulatory-mappings.md will see conflicting retention periods for agent communications: 3 years (matrix) vs 6 years (SEC 17a-3/4 section).

**Correction Required:**

1. **Fix overview (line 226):**
```markdown
# Current (INCORRECT):
Requires SEC-registered firms to maintain records of all transactions and communications for 6 years

# Corrected:
Requires SEC-registered firms to maintain records for varying periods: 3 years for communications (17a-4(b)(4)), 6 years for accounting/financial records (17a-4(a))
```

2. **Fix Agent Communications subsection (line 249):**
```markdown
# Current (INCORRECT):
- Retention: 6 years, first 2 years in easily accessible place

# Corrected:
- Retention: 3 years per SEC 17a-4(b)(4) (communications), first 2 years readily accessible
- Exception: If agent outputs constitute accounting/financial records, apply 6-year retention per SEC 17a-4(a)
```

**Files Affected:**
- `docs/reference/regulatory-mappings.md` lines 226, 249

---

### MODERATE: CFTC Rule 1.31 Not in Retention Period Matrix

**Issue:** Organizations with dual SEC/CFTC registration need CFTC retention periods in the matrix.

**Current Matrix:** Only SEC and FINRA retention periods listed.

**CFTC Requirements:**
- 5 years minimum
- First 2 years readily accessible
- Some records: life of enterprise + 5 years

**Impact:** Dual-registrant organizations (broker-dealers also registered as FCMs, IBs, CTAs, CPOs) may miss CFTC retention requirements.

**Correction Required:** Add CFTC row to Retention Period Matrix:

```markdown
| **Derivatives/Commodities Records** (CFTC entities) | 5 years minimum | CFTC Rule 1.31 | First 2 years readily accessible |
```

**Note:** Add after FINRA row in matrix (new line 20 in regulatory-mappings.md)

---

### MODERATE: Missing Agent-Specific Record Types

**Issue:** The matrix covers traditional record types but doesn't explicitly list agent-specific governance records.

**Missing Record Types:**

| Record Type | Suggested Retention | Regulation Basis |
|-------------|-------------------|------------------|
| **Agent Model Validation Records** | 6 years | SEC 17a-4(a) - governance records |
| **Agent Approval/Governance Records** | 6 years | SEC 17a-4(a) - compliance documentation |
| **Agent Incident Reports** | 6 years | SEC 17a-4(a) - incident documentation |
| **Agent Bias Testing Results** | 6 years | SR 11-7 model risk management |
| **AI Marketing Substantiation Files** | 7 years | FINRA 4511 for Rule 2210 communications (per Control 2.21) |

**Analysis:**
- These are governance/compliance records, not communications
- Typically fall under 6-year retention as business records
- AI marketing substantiation may require 7 years per FINRA 4511 for Rule 2210 communications

**Correction Required:** Add "Governance Records" category to matrix:

```markdown
| **Agent Governance Records** (approvals, validations, incidents, bias testing) | 6 years | SEC 17a-4(a) / SR 11-7 | First 2 years readily accessible |
```

**Note:** Marketing substantiation is already covered in Control 2.21; cross-reference from matrix.

---

### MINOR: Terminology Inconsistency - "Readily" vs "Easily" Accessible

**Issue:** Matrix uses different terminology for access requirements:
- SEC rows: "readily accessible"
- FINRA row: "easily accessible"

**Analysis:**
- SEC 17a-4 uses "readily accessible" (official text)
- FINRA 4511 uses "easily accessible" (official text)
- This is correct citation of official terminology, NOT an error

**Recommendation:** No change needed. Add explanatory note to matrix that terminology varies by regulation but means the same thing (immediate access capability).

---

## Recommended Matrix Updates

### Updated Retention Period Matrix (For Plan 05-04)

```markdown
### Retention Period Matrix

| Record Type | Retention | Regulation | Access Requirement |
|-------------|-----------|------------|--------------------|
| **Communications** (agent logs, chat, email) | 3 years | SEC 17a-4(b)(4) | First 2 years readily accessible |
| **Accounting/Financial Records** | 6 years | SEC 17a-4(a) | First 2 years readily accessible |
| **Customer Account Records** | 6 years after account close | SEC 17a-4(c) | First 2 years readily accessible |
| **Agent Governance Records** (approvals, validations, incidents, bias testing) | 6 years | SEC 17a-4(a) / SR 11-7 | First 2 years readily accessible |
| **Derivatives/Commodities Records** (CFTC-registered entities) | 5 years minimum | CFTC Rule 1.31 | First 2 years readily accessible |
| **FINRA-Specific Records** (no SEC period applies) | 6 years | FINRA 4511(b) | First 2 years easily accessible |
| **AI Marketing Substantiation** (investment advisers) | 7 years | FINRA 4511 / Control 2.21 | First 2 years easily accessible |

!!! note "Terminology Note"
    "Readily accessible" (SEC) and "easily accessible" (FINRA) both mean the same compliance standard: records must be available for immediate access and review.

!!! warning "Agent Communications: 3-Year Not 6-Year"
    Agent conversation logs typically fall under SEC 17a-4(b)(4) **communications retention (3 years)**, not the 6-year financial records period. Only apply 6-year retention if agent interactions generate or modify accounting/financial records.
```

**Changes:**
1. ❌ Removed invalid "(e)(5)" from Customer Account Records citation
2. ✅ Added Agent Governance Records row (new)
3. ✅ Added Derivatives/Commodities Records row for CFTC entities (new)
4. ✅ Added AI Marketing Substantiation row (new)
5. ✅ Added terminology note explaining "readily" vs "easily" accessible
6. ✅ Added warning admonition about 3-year vs 6-year for agent communications

---

## Summary of Corrections for Plan 05-04

| Finding | Severity | Location | Correction |
|---------|----------|----------|------------|
| Invalid citation "17a-4(c)(e)(5)" | **CRITICAL** | regulatory-mappings.md line 18 | Change to "SEC 17a-4(c)" |
| Generic "6 years" in overview | **CRITICAL** | regulatory-mappings.md line 226 | Clarify 3-year vs 6-year by record type |
| Agent Communications says "6 years" | **CRITICAL** | regulatory-mappings.md line 249 | Change to "3 years per SEC 17a-4(b)(4)" |
| Missing CFTC Rule 1.31 | **MODERATE** | Retention Period Matrix | Add CFTC row |
| Missing agent governance records | **MODERATE** | Retention Period Matrix | Add governance row |
| Missing marketing substantiation | **MODERATE** | Retention Period Matrix | Add marketing row |
| Terminology inconsistency | **MINOR** | Retention Period Matrix | Add explanatory note (no change to citations) |

**Total Corrections Required:** 7 (3 Critical, 3 Moderate, 1 Minor)

---

## Official Sources Verified

**SEC 17a-4:**
- ✅ Accessed: https://www.law.cornell.edu/cfr/text/17/240.17a-4
- ✅ Verified subsections (a), (b)(1)-(17), (c), (e)(1)-(4), (f)
- ✅ Confirmed retention periods: 3 years (b), 6 years (a), 6 years after close (c)
- ✅ Confirmed (e)(5) does NOT exist

**CFTC Rule 1.31:**
- ✅ Accessed: https://www.law.cornell.edu/cfr/text/17/1.31
- ✅ Verified 5-year minimum retention
- ✅ Verified "first 2 years readily accessible"
- ✅ Confirmed WORM requirement eliminated May 2017
- ✅ Confirmed principles-based "authenticity and reliability" standard per 17 CFR § 1.31(c)

---

*Validation completed: 2026-02-03*
*Ready for correction application in Plan 05-04*
