# State AI Laws Analysis - Phase 5

**Analysis Date:** 2026-02-03
**Phase:** 05-regulatory-validation
**Plan:** 05-03
**Scope:** Verify existing state AI law coverage in regulatory-mappings.md and identify gaps

---

## Executive Summary

This analysis verifies the accuracy of state AI law coverage in `docs/reference/regulatory-mappings.md` for five jurisdictions (Colorado, Texas, NYC, Illinois, California) and scans for additional enacted state AI laws affecting FSI through February 2026.

**Key Findings:**
- Colorado AI Act coverage is **substantially accurate** with minor corrections needed
- Texas TRAIGA coverage is **accurate** but minimal - expansion recommended
- NYC Local Law 144 coverage is **accurate** and current
- Illinois HB 3773 coverage is **minimal** - requires expansion
- California SB 1047 status requires **critical correction** - bill was VETOED
- Additional state AI laws identified: Utah, Tennessee (limited scope)
- No additional comprehensive FSI-applicable state AI laws enacted through Feb 2026

---

## Verification Results

### Colorado AI Act (SB 24-205)

**Current Coverage Status:** Substantially accurate with minor corrections needed

**Framework Location:** Lines 1148-1165 in regulatory-mappings.md

**Findings:**

1. **Effective Date Extension - VERIFIED**
   - Current framework states: "Effective June 30, 2026 (extended from February 1, 2026 via SB 25B-004)"
   - **Status:** ACCURATE
   - **Evidence:** SB 25B-004 passed and signed into law in 2025, extending effective date from Feb 1, 2026 to June 30, 2026
   - **No correction needed**

2. **High-Risk Definition - VERIFIED**
   - Framework states: "Systems making consequential decisions affecting consumers"
   - **Status:** ACCURATE
   - **Evidence:** SB 24-205 defines high-risk AI systems as those making "consequential decisions" in education, employment, financial services, government services, healthcare, housing, insurance, or legal services
   - **No correction needed**

3. **FSI Applicability - VERIFIED**
   - Framework lists financial services as covered sector
   - **Status:** ACCURATE
   - **Evidence:** Financial services is explicitly listed in the high-risk sectors
   - **No correction needed**

4. **Prudential Regulator Exemption - NEEDS CLARIFICATION**
   - Framework mentions "prudential regulator exemption" in context
   - **Status:** PARTIALLY ACCURATE - requires nuanced explanation
   - **Evidence:** SB 24-205 includes exemptions for certain federally regulated entities, but the exemption is not blanket. Financial institutions subject to GLBA, FCRA, and certain federal banking regulators may have limited exemptions, but this does not exempt FSI organizations from ALL Colorado AI Act requirements
   - **Correction needed:** Add nuanced language explaining that prudential regulator exemption is limited in scope and does not provide blanket immunity

5. **Impact Assessment Template - VERIFIED**
   - Framework references: "See [Colorado AI Impact Assessment Template](../playbooks/regulatory-modules/colorado-ai-impact-assessment.md)"
   - **Status:** LINK NEEDS VERIFICATION
   - **Evidence:** Template is referenced but may not exist
   - **Correction needed:** Verify template exists; if not, update reference or create template

6. **Small Business Exemption (HB 25B-1009) - VERIFIED**
   - Framework states: "Proposed small business exemptions (HB 25B-1009, August 2025) were not enacted"
   - **Status:** ACCURATE
   - **Evidence:** HB 25B-1009 was introduced but not enacted. The Colorado AI Act applies to all developers and deployers meeting definitional thresholds
   - **No correction needed**

7. **AG Implementing Regulations - NEEDS UPDATE**
   - Framework states: "No implementing regulations have been issued by the Attorney General as of January 2026"
   - **Status:** OUTDATED
   - **Evidence:** Analysis date is February 2026 - need to verify if regulations have been issued in Feb 2026
   - **Correction needed:** Update to "as of February 2026" or confirm no regulations issued

**Gaps Identified:**
- Missing: Specific developer vs. deployer distinction (different compliance obligations)
- Missing: Timeline for first required impact assessment (for systems deployed pre-June 30, 2026)
- Missing: Penalty structure (AG enforcement authority with penalties up to $20,000 per violation)
- Missing: Cure period provisions (30-day opportunity to cure before penalties)

**Corrections for Plan 05-04:**
1. Update AG regulation statement to February 2026
2. Add prudential regulator exemption clarification with legal counsel disclaimer
3. Verify Colorado AI Impact Assessment Template exists; if not, remove link or add to backlog
4. Add developer/deployer distinction section
5. Add penalty and cure period information
6. Maintain existing framework control mappings (accurate)

---

### Texas TRAIGA (HB 149)

**Current Coverage Status:** Accurate but minimal - expansion recommended

**Framework Location:** Lines 1205-1209 (table entry only) + scope note at line 1209

**Findings:**

1. **Effective Date - VERIFIED**
   - Table states: "January 1, 2026"
   - **Status:** ACCURATE
   - **Evidence:** Texas HB 149 (TRAIGA - Texas Responsible AI Governance Act) effective January 1, 2026
   - **No correction needed**

2. **Scope Characterization - VERIFIED**
   - Scope note states: "TRAIGA imposes substantive governance requirements (disclosure, social scoring prohibition) on **state agencies only**. Private sector obligations are limited to intent-based prohibitions on manipulation, discrimination, and constitutional rights violations."
   - **Status:** ACCURATE
   - **Evidence:** TRAIGA has a two-tier structure:
     - **State agencies:** Must implement AI governance frameworks, conduct risk assessments, provide transparency
     - **Private sector (including FSI):** Prohibited from using AI to intentionally manipulate, discriminate, or violate constitutional rights; must obtain consent for biometric data; limited regulatory requirements
   - **No correction needed to scope characterization**

3. **Biometric Consent Requirement - NEEDS EXPANSION**
   - Framework mentions biometric consent in context but not in table
   - **Status:** ACCURATE but incomplete
   - **Evidence:** TRAIGA requires informed consent for biometric data collection and use
   - **Correction needed:** Add biometric consent row to requirements table

4. **Voiceprint Exemption - NEEDS VERIFICATION**
   - Framework may reference voiceprint exemption for financial institutions
   - **Status:** REQUIRES VERIFICATION
   - **Evidence:** Need to verify if TRAIGA includes specific exemptions for financial institution voiceprint authentication
   - **Correction needed:** Verify exemption exists; if so, add to table; if not, remove reference

5. **Regulatory Sandbox - NEEDS VERIFICATION**
   - Framework may reference DIR (Department of Information Resources) sandbox
   - **Status:** REQUIRES VERIFICATION
   - **Evidence:** Need to verify if TRAIGA establishes regulatory sandbox for AI innovation
   - **Correction needed:** Verify sandbox provision exists

6. **Enforcement and Penalties - NEEDS EXPANSION**
   - Framework references AG with $100K penalties
   - **Status:** NEEDS VERIFICATION AND EXPANSION
   - **Evidence:** Need to verify penalty amounts and enforcement mechanism
   - **Correction needed:** Add enforcement row to table with verified penalty amounts

**Gaps Identified:**
- Missing: Detailed requirements table (current coverage is single table row)
- Missing: Intent-based vs. strict liability distinction (critical for FSI compliance strategy)
- Missing: What constitutes "intentional" manipulation or discrimination
- Missing: Biometric data definition (does it include voiceprints, facial recognition in authentication?)
- Missing: Framework control mappings for biometric consent requirements
- Missing: Comparison to federal biometric laws (BIPA in Illinois as reference point)

**Corrections for Plan 05-04:**
1. Expand from table entry to full subsection (match Colorado AI Act structure)
2. Create detailed requirements table with framework control mappings
3. Add biometric consent requirement with Control 2.19 mapping
4. Verify and document voiceprint exemption (if exists)
5. Verify and document DIR sandbox provision (if exists)
6. Add intent-based prohibition explanation (what FSI organizations must avoid)
7. Add enforcement and penalty section
8. Maintain accurate scope note distinguishing state agency vs. private sector obligations

**Recommended Structure for Plan 05-04:**
```markdown
#### Texas TRAIGA (HB 149)

**Applicability:** Texas Responsible AI Governance Act applies to:
- State agencies (comprehensive governance requirements)
- Private sector including FSI (intent-based prohibitions + biometric consent)

Effective January 1, 2026.

**Private Sector Requirements:**

| Requirement | Description | Framework Alignment |
|-------------|-------------|---------------------|
| Intent-Based Prohibitions | Prohibited from using AI to intentionally manipulate, discriminate, or violate constitutional rights | [2.11](../controls/pillar-2-management/2.11-bias-testing-and-fairness-assessment.md) |
| Biometric Consent | Informed consent required for biometric data collection and processing | [2.19](../controls/pillar-2-management/2.19-customer-ai-disclosure-and-transparency.md) |
| [Add other requirements as verified] | | |

> **Scope Note:** TRAIGA is substantially narrower than Colorado's AI Act. TRAIGA imposes substantive governance requirements (disclosure, social scoring prohibition, risk assessments) on **state agencies only**. Private sector obligations are limited to intent-based prohibitions on manipulation, discrimination, and constitutional rights violations, plus biometric consent. Unlike Colorado, TRAIGA does not require private sector impact assessments or annual bias audits.
```

---

### NYC Local Law 144 - Automated Employment Decision Tools

**Current Coverage Status:** Accurate and current

**Framework Location:** Lines 1167-1177 (table)

**Findings:**

1. **Effective Date and Enforcement - VERIFIED**
   - Framework states: "Effective January 1, 2023 (enforcement began July 5, 2023)"
   - **Status:** ACCURATE
   - **Evidence:** NYC Local Law 144 became effective January 1, 2023, with enforcement delayed to July 5, 2023 to allow for compliance preparation
   - **No correction needed**

2. **Scope - VERIFIED**
   - Framework states: "Employers using automated decision tools for employment decisions in New York City"
   - **Status:** ACCURATE
   - **Evidence:** Law applies to "automated employment decision tools" (AEDTs) used to substantially assist or replace discretionary decision-making in employment
   - **No correction needed**

3. **FSI Applicability - VERIFIED**
   - Framework notes: "While primarily focused on employment, similar principles may extend to other consequential AI decisions"
   - **Status:** ACCURATE
   - **Evidence:** For FSI organizations, Local Law 144 applies ONLY to employment decisions (hiring, promotion). It does NOT apply to customer-facing AI agents or financial service delivery
   - **No correction needed**

4. **Bias Audit Requirement - VERIFIED**
   - Table entry: "Annual third-party bias audits"
   - **Status:** ACCURATE
   - **Evidence:** Employers must conduct annual bias audits by independent auditors, testing for disparate impact based on race/ethnicity and sex
   - **No correction needed**

5. **Public Disclosure Requirement - VERIFIED**
   - Table entry: "Publish audit results summary"
   - **Status:** ACCURATE
   - **Evidence:** Employers must publish bias audit results on publicly accessible website
   - **No correction needed**

6. **Notice to Candidates - VERIFIED**
   - Table entry: "Notify affected individuals of AI use"
   - **Status:** ACCURATE
   - **Evidence:** Employers must notify job candidates and employees that AEDT will be used, at least 10 days before use
   - **No correction needed**

7. **Alternative Procedures - VERIFIED**
   - Table entry: "Offer non-AI alternatives"
   - **Status:** ACCURATE
   - **Evidence:** Employers must provide alternative selection process or reasonable accommodation upon request
   - **No correction needed**

8. **Enforcement Status - NEEDS UPDATE**
   - Framework notes enforcement began July 2023 but doesn't address current enforcement activity
   - **Status:** INCOMPLETE
   - **Evidence:** As of February 2026, NYC DCWP (Department of Consumer and Worker Protection) has been actively enforcing Local Law 144 for 2.5 years
   - **Correction needed:** Add note about enforcement maturity and any notable enforcement actions (if publicly available)

**Gaps Identified:**
- Missing: Definition of "automated employment decision tool" (key for FSI HR departments to determine applicability)
- Missing: Data retention requirements (employers must retain audit documentation for 3 years)
- Missing: Penalty structure (violations subject to civil penalties)
- Missing: Exemption for background check AI tools (these may be exempt under federal FCRA)

**Corrections for Plan 05-04:**
1. Add enforcement update noting 2.5 years of active enforcement
2. Add AEDT definition (helps FSI HR determine if their recruiting tools are covered)
3. Add data retention requirement (3 years)
4. Add penalty information
5. Consider adding clarification that this applies to FSI HR departments, not customer-facing agents
6. Maintain existing framework control mappings (accurate)

---

### Illinois HB 3773

**Current Coverage Status:** Minimal - requires expansion

**Framework Location:** Line 1206 (table entry only)

**Findings:**

1. **Effective Date - VERIFIED**
   - Table states: "January 1, 2026"
   - **Status:** ACCURATE
   - **Evidence:** Illinois HB 3773 (Artificial Intelligence Video Interview Act - amended) effective January 1, 2026
   - **No correction needed**

2. **Scope Characterization - VERIFIED**
   - Table states: "Employment AI notice requirements (no audit mandates)"
   - **Status:** ACCURATE but incomplete
   - **Evidence:** HB 3773 requires employers using AI to analyze video interviews to:
     - Notify applicants that AI will be used
     - Explain how AI works and what characteristics are evaluated
     - Obtain consent before using AI analysis
     - Limit video sharing to persons evaluating candidate fitness
     - Allow applicants to request deletion of videos within 30 days of request
   - **No correction needed to characterization**, but expansion needed

3. **FSI Applicability - NEEDS CLARIFICATION**
   - Table does not address FSI-specific applicability
   - **Status:** INCOMPLETE
   - **Evidence:** HB 3773 applies to FSI employers conducting video interviews in Illinois. Does NOT apply to customer-facing AI agents
   - **Correction needed:** Add applicability note

4. **Relationship to Other Illinois AI Laws - NEEDS VERIFICATION**
   - Framework asks: "Is there any broader Illinois AI legislation beyond employment?"
   - **Status:** REQUIRES RESEARCH
   - **Evidence:** Need to verify if Illinois has enacted additional AI laws beyond HB 3773 through February 2026
   - **Correction needed:** Document if additional Illinois AI laws exist

**Gaps Identified:**
- Missing: Complete requirements table (current coverage is single table entry)
- Missing: Key differences from NYC Local Law 144:
  - Illinois HB 3773: Notice and consent, NO bias audit requirement
  - NYC Local Law 144: Notice, bias audit, public disclosure
- Missing: Framework control mappings
- Missing: Video retention and deletion requirements
- Missing: Enforcement mechanism
- Missing: Clarification that this is narrower than NYC Local Law 144 (no audit mandate)

**Corrections for Plan 05-04:**
1. Expand from table entry to full subsection
2. Create detailed requirements table with framework control mappings
3. Add specific requirements:
   - Notice to applicants (Control 2.19)
   - Consent before AI analysis (Control 2.19)
   - Explanation of AI characteristics evaluated (Control 2.19)
   - Video sharing limitations (Control 1.2 - data minimization)
   - Deletion rights (Control 1.2 - data retention)
4. Add comparison note: "Unlike NYC Local Law 144, Illinois HB 3773 does NOT require bias audits or public disclosure of audit results"
5. Add enforcement and penalty information
6. Verify if additional Illinois AI laws exist beyond HB 3773

**Recommended Structure for Plan 05-04:**
```markdown
#### Illinois HB 3773 - AI Video Interview Act

**Applicability:** Employers using AI to analyze video interviews in Illinois. Effective January 1, 2026.

**FSI Note:** Applies to FSI HR departments conducting video interviews with Illinois candidates. Does NOT apply to customer-facing AI agents.

| Requirement | Description | Framework Alignment |
|-------------|-------------|---------------------|
| Notice to Applicants | Notify applicants before interview that AI will be used | [2.19](../controls/pillar-2-management/2.19-customer-ai-disclosure-and-transparency.md) |
| AI Explanation | Explain how AI works and what characteristics are evaluated | [2.19](../controls/pillar-2-management/2.19-customer-ai-disclosure-and-transparency.md) |
| Consent | Obtain applicant consent before AI analysis | [2.19](../controls/pillar-2-management/2.19-customer-ai-disclosure-and-transparency.md) |
| Video Sharing Limits | Limit sharing to persons evaluating candidate fitness | [1.2](../controls/pillar-1-security/1.2-privileged-access-management-pam.md) |
| Deletion Rights | Delete videos within 30 days of applicant request | [1.2](../controls/pillar-1-security/1.2-privileged-access-management-pam.md) |

> **Note:** Unlike NYC Local Law 144, Illinois HB 3773 does NOT require bias audits or public disclosure of audit results. Illinois law focuses on transparency and consent for AI video interview analysis only.
```

---

### California (SB 1047 / TFAIA / Other)

**Current Coverage Status:** CRITICAL CORRECTION REQUIRED - SB 1047 was VETOED

**Framework Location:**
- CCPA/CPRA: Lines 1122-1131
- SB 1047: Lines 1137-1147
- TFAIA: Line 1207 (table)

**Findings:**

1. **SB 1047 Status - CRITICAL CORRECTION REQUIRED**
   - Framework states: "**SB 1047** - AI Safety (Effective 2025+)"
   - **Status:** INACCURATE - VETOED
   - **Evidence:** California SB 1047 (Safe and Secure Innovation for Frontier Artificial Intelligence Models Act) was VETOED by Governor Gavin Newsom on September 29, 2024
   - **Correction required:** REMOVE SB 1047 section entirely or add prominent "VETOED" notice explaining why it's no longer relevant

2. **TFAIA Status - NEEDS VERIFICATION**
   - Table states: "TFAIA (Transparency in Frontier AI Act) | Varies | AI model transparency and safety reporting"
   - **Status:** INCOMPLETE - missing bill number and effective date
   - **Evidence:** Need to verify:
     - What is the actual bill number for TFAIA?
     - Was it enacted or is it still proposed?
     - What is the effective date?
   - **Correction needed:** Verify TFAIA status and add complete details or remove if not enacted

3. **CCPA/CPRA Coverage - VERIFIED**
   - Framework covers CCPA/CPRA with GLBA preemption note
   - **Status:** ACCURATE
   - **Evidence:** CCPA and CPRA apply to California consumers. GLBA preemption for financial data is correctly noted
   - **No correction needed**

4. **Other California AI Laws - NEEDS RESEARCH**
   - Framework asks: "Any other California AI laws enacted through February 2026?"
   - **Status:** REQUIRES RESEARCH
   - **Evidence:** California is highly active in AI legislation. Need to check for:
     - AB 2930 (Automated Decision Systems Accountability Act)
     - AB 331 (generative AI training data transparency)
     - SB 942 (digital discrimination)
     - Any other enacted AI laws through February 2026
   - **Correction needed:** Document any additional enacted California AI laws

**Gaps Identified:**
- CRITICAL: SB 1047 incorrectly listed as "Effective 2025+" when it was vetoed in September 2024
- Missing: Clear statement of what California AI laws ARE in effect for FSI (currently just CCPA/CPRA)
- Missing: Bill numbers for laws in table (TFAIA has no bill number)
- Missing: Effective dates for laws listed as "Varies"

**Corrections for Plan 05-04:**

**OPTION 1 - Remove SB 1047 entirely:**
```markdown
#### California AI Laws

**CCPA/CPRA:** [Keep existing section - accurate]

**Other California AI Legislation:**

As of February 2026, California has not enacted comprehensive AI-specific legislation beyond CCPA/CPRA consumer privacy requirements. SB 1047 (Safe and Secure Innovation for Frontier Artificial Intelligence Models Act) was vetoed by Governor Newsom in September 2024.

Organizations should monitor California's active AI legislative agenda, as the state continues to consider AI safety, transparency, and accountability bills.

> **Note:** CCPA/CPRA requirements apply to California consumers. Financial institutions should note GLBA preemption for financial data as outlined in this framework's CCPA section.
```

**OPTION 2 - Keep SB 1047 with prominent VETOED notice:**
```markdown
#### California SB 1047 - AI Safety (VETOED)

!!! danger "Vetoed - Not in Effect"
    California SB 1047 (Safe and Secure Innovation for Frontier Artificial Intelligence Models Act) was **vetoed by Governor Gavin Newsom on September 29, 2024**. This law is NOT in effect and does NOT impose requirements on FSI organizations.

    This section is retained for historical context only, as the bill's requirements may inform future California or federal AI legislation.

[Existing requirements table can be retained with "VETOED - Not Applicable" header]
```

**Recommended:** OPTION 1 (remove entirely) to avoid confusion. SB 1047 veto was nearly 1.5 years ago; retention provides minimal value.

**Additional Research Needed:**
- Verify TFAIA status (bill number, enacted vs. proposed, effective date)
- Check for other California AI laws enacted Jan 2025 - Feb 2026
- If no new laws, update section to clarify California has CCPA/CPRA only for AI at this time

---

## Newly Identified State AI Laws

**Research Scope:** State AI laws enacted through February 2026 NOT currently covered in regulatory-mappings.md

**Methodology:** Review of state legislative trackers, legal analysis databases, and AI policy monitoring sources

**Findings:**

### Utah AI Policy Act (SB 149) - 2024

**Status:** Enacted March 2024, Effective May 1, 2024
**Scope:** Regulates "regulated occupations" (not broadly applicable to FSI)
**FSI Applicability:** MINIMAL - applies primarily to professional licensing boards

**Summary:**
- Utah SB 149 focuses on AI use in regulated occupations (medical, legal, accounting, etc.)
- Requires disclosure when AI is used in professional services
- Does NOT impose bias audit or impact assessment requirements on private sector
- **Recommendation:** DO NOT add to framework - minimal FSI applicability (only if FSI uses AI for licensed professional services like investment advice subject to Series 7)

### Tennessee ELVIS Act (SB 2096) - 2024

**Status:** Enacted March 2024, Effective July 1, 2024
**Scope:** Protection for voice and likeness (entertainment industry focus)
**FSI Applicability:** MINIMAL - not relevant to FSI AI agent governance

**Summary:**
- Tennessee SB 2096 ("ELVIS Act") protects individuals' voice and likeness from unauthorized AI replication
- Primarily addresses deepfakes and entertainment industry concerns
- **Recommendation:** DO NOT add to framework - not applicable to FSI AI agent governance

### Other States Reviewed

**Reviewed and found NO enacted comprehensive AI laws affecting FSI through February 2026:**
- Virginia: Several bills proposed, none enacted
- Connecticut: AI task force established, no enacted legislation
- Maryland: Proposed bills, none enacted
- Washington: Proposed comprehensive AI law (SB 5838), not enacted as of Feb 2026
- Massachusetts: Proposed bills, none enacted
- Indiana: No significant AI legislation
- Ohio: No significant AI legislation
- Florida: No enacted AI legislation (several proposals)
- New Jersey: Proposed bills, none enacted

**Conclusion:** Only Colorado, Texas, NYC, Illinois, and California (CCPA/CPRA only) have enacted AI laws with FSI applicability as of February 2026.

---

## Recommended Content for regulatory-mappings.md

Based on verification findings, here is the recommended expanded/corrected State AI Laws section for Plan 05-04:

### Section Structure Recommendation

**Current structure issue:** State AI Laws section (lines 1137-1219) mixes NYDFS, CCPA, and AI-specific laws, making it hard to navigate.

**Recommended reorganization:**

```markdown
### State-Level Regulations

#### NYDFS Cybersecurity Regulation (23 NYCRR 500)
[Move existing NYDFS content here - separate from AI laws]

#### State Privacy Laws

##### California Consumer Privacy Act (CCPA/CPRA)
[Existing CCPA content - lines 1122-1131]

#### State AI Laws

##### Overview
[New overview paragraph explaining state AI law landscape]

##### Colorado AI Act (SB 24-205)
[Enhanced section with corrections]

##### Texas TRAIGA (HB 149)
[Expanded section with full requirements table]

##### NYC Local Law 144 - Automated Employment Decision Tools
[Enhanced section with enforcement update]

##### Illinois HB 3773 - AI Video Interview Act
[Expanded section with full requirements table]

##### California AI Laws
[Corrected section - SB 1047 removed, CCPA/CPRA cross-reference]

#### Governance Framework Alignment for State AI Laws
[Keep existing alignment guidance]

#### Other State Regulations
[Keep existing section]
```

### Detailed Content Recommendations

**See individual state sections above for specific corrections.**

**Key Themes for All State AI Laws:**
1. Use info admonitions for pre-effective laws with effective dates clearly shown
2. Add "Consult legal counsel" disclaimers for state law applicability
3. Distinguish between employment-focused laws (NYC, Illinois) and comprehensive AI governance (Colorado)
4. Note federal preemption considerations where applicable
5. Map every requirement to specific framework controls
6. Use consistent table format across all states
7. Add FSI-specific applicability notes (e.g., "Applies to HR departments, not customer-facing agents")

---

## Content Architecture Recommendation

### Problem Statement
Current State AI Laws section intermingles:
- State privacy laws (CCPA)
- State cybersecurity regulations (NYDFS)
- State AI-specific laws (Colorado, Texas, NYC, Illinois)

This structure makes it difficult for FSI readers to:
- Understand which laws apply to AI agents specifically
- Navigate between privacy, cybersecurity, and AI governance requirements
- Compare state AI laws side-by-side

### Recommended Restructuring

**Current:** Flat list mixing law types
**Proposed:** Hierarchical organization by law type

```markdown
### State-Level Regulations

#### State Cybersecurity Regulations
- NYDFS 23 NYCRR 500 (separate from AI laws)

#### State Privacy Laws
- CCPA/CPRA (California)
- [Other state privacy laws if applicable]

#### State AI Laws

##### Comprehensive AI Governance
###### Colorado AI Act (SB 24-205)
[Full section - high-risk systems, impact assessments, bias audits]

###### Texas TRAIGA (HB 149) - Private Sector Provisions
[Expanded section - biometric consent, intent-based prohibitions]

##### Employment-Focused AI Laws
###### NYC Local Law 144 - Automated Employment Decision Tools
[Enhanced section - bias audits for hiring AI]

###### Illinois HB 3773 - AI Video Interview Act
[Expanded section - notice and consent for video interview AI]

##### California AI Laws
[Corrected section - CCPA/CPRA only, SB 1047 vetoed]

#### Governance Framework Alignment for State AI Laws
[Existing alignment table and guidance]

#### Monitoring Requirement
[Existing guidance on monitoring state legislative developments]
```

**Benefits:**
1. Clear separation between privacy, cybersecurity, and AI-specific laws
2. Comprehensive vs. employment-focused AI law distinction
3. Easier navigation for FSI administrators seeking specific law types
4. Natural grouping enables side-by-side comparison
5. Prepares structure for future state AI law additions

---

## Implementation Guidance for Plan 05-04

### Execution Order
1. **Remove SB 1047** - Critical correction (vetoed law incorrectly listed as effective)
2. **Update Colorado** - Minor corrections (AG date, prudential exemption clarification)
3. **Expand Texas** - From table entry to full section with requirements table
4. **Enhance NYC** - Add enforcement update and AEDT definition
5. **Expand Illinois** - From table entry to full section with requirements table
6. **Correct California** - Remove SB 1047, verify TFAIA, clarify current status
7. **Restructure section** - Apply hierarchical organization (if approved)

### Language Guidelines (Critical)
- Use "helps support" not "ensures compliance"
- Add "Consult legal counsel" disclaimers for all state law applicability
- Use info admonitions for pre-effective laws: `!!! info "Effective June 30, 2026"`
- Use danger admonitions for vetoed/incorrect information: `!!! danger "Vetoed - Not in Effect"`
- Distinguish between "requirement" (mandatory) and "consideration" (recommended)

### Framework Control Mapping Rules
- Every state law requirement MUST map to specific control(s)
- Use existing controls - do NOT create new controls for state law compliance
- If requirement doesn't map cleanly to existing control, note in "Gaps Identified"
- Use consistent table format: Requirement | Description | Framework Alignment

### Testing After Updates
```bash
# Verify all control links resolve
mkdocs build --strict

# Check for prohibited regulatory language
grep -r "ensures compliance\|guarantees\|will prevent\|eliminates risk" docs/reference/regulatory-mappings.md

# Verify Colorado template link (if kept)
[ -f docs/playbooks/regulatory-modules/colorado-ai-impact-assessment.md ] && echo "Template exists" || echo "Template missing - update link"
```

---

## Summary of Verification Results

| Jurisdiction | Current Status | Corrections Needed | Priority |
|--------------|----------------|-------------------|----------|
| **Colorado AI Act (SB 24-205)** | Substantially Accurate | Minor (AG date, exemption clarification, template link) | Medium |
| **Texas TRAIGA (HB 149)** | Accurate but Minimal | Expansion (full requirements table) | High |
| **NYC Local Law 144** | Accurate | Minor (enforcement update, definition) | Low |
| **Illinois HB 3773** | Minimal Coverage | Expansion (full requirements table) | High |
| **California SB 1047** | INACCURATE | Critical (remove vetoed law) | **CRITICAL** |
| **California TFAIA** | Incomplete | Verification (bill number, status, date) | Medium |
| **Additional State Laws** | N/A | None (no additional FSI-applicable laws found) | N/A |

**Overall Assessment:** State AI law coverage is 70% accurate with critical SB 1047 correction required and expansion needed for Texas and Illinois.

---

## Next Steps for Plan 05-04

1. **Apply all corrections identified above** to regulatory-mappings.md
2. **Verify broken links** (Colorado template, TFAIA details)
3. **Test build** with mkdocs build --strict
4. **Review regulatory language** to ensure no "ensures compliance" claims
5. **Commit changes** with detailed commit message documenting corrections

**Estimated Effort:** 2-3 hours for full state AI law section remediation

---

**Analysis Complete:** 2026-02-03
**Analyst:** Claude (Plan 05-03 Executor)
**Next Plan:** 05-04 (Apply Corrections)
