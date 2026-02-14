## VERIFICATION RESULTS: PROHIBITED REGULATORY LANGUAGE SCAN
**Scan Date:** 2026-02-14 15:44:51
**Scope:** C:\dev\FSI-AgentGov\docs\
**Status:** VIOLATIONS FOUND

---

## SUMMARY

- **"prevents" (regulatory claims):** 26 violations
- **"preventing" (regulatory claims):** 10 violations  
- **"eliminates":** 3 violations
- **"will prevent":** 0 violations ✓
- **"ensures compliance":** 0 violations ✓
- **"guarantees":** 0 violations ✓

**Total Violations to Fix:** 39

---

## DETAILED FINDINGS

### Category 1: "prevents" as regulatory claim (26 violations)

These are absolute regulatory claims that need hedging language like "helps prevent" or "supports prevention of".

#### PILLAR 1 - SECURITY CONTROLS

**File:** controls\pillar-1-security\1.1-restrict-agent-publishing-by-authorization.md
- **Line 57:** Table cell text
- **Current:** "Prevents unauthorized agent distribution"
- **Fix to:** "Helps prevent unauthorized agent distribution"
- **Context:** Table describing governance impact of Publish action

**File:** controls\pillar-1-security\1.16-information-rights-management-irm-for-documents.md
- **Line 23:** Regulatory mapping bullet
- **Current:** "Prevents unauthorized document distribution through internal controls"
- **Fix to:** "Helps prevent unauthorized document distribution through internal controls"
- **Context:** SOX 404 regulatory mapping

**File:** controls\pillar-1-security\1.17-endpoint-data-loss-prevention-endpoint-dlp.md
- **Line 21:** Regulatory mapping bullet
- **Current:** "Prevents unauthorized removal of books and records"
- **Fix to:** "Helps prevent unauthorized removal of books and records"
- **Context:** FINRA 4511 regulatory mapping

**File:** controls\pillar-1-security\1.21-adversarial-input-logging.md
- **Line 105:** Prose description
- **Current:** "Zone 3 blocking prevents execution of detected attack"
- **Fix to:** "Zone 3 blocking helps prevent execution of detected attacks"
- **Context:** Control description of Zone 3 enforcement

**File:** controls\pillar-1-security\1.22-information-barriers.md
- **Line 21:** Regulatory mapping bullet
- **Current:** "Prevents trading on research information through segment barriers"
- **Fix to:** "Helps prevent trading on research information through segment barriers"
- **Context:** SEC Regulation SHO regulatory mapping

**File:** controls\pillar-1-security\1.25-mime-type-restrictions.md
- **Line 36:** Prose description
- **Current:** "A deny list of file extensions (e.g., .exe, .bat, .ps1, .dll) that prevents uploads regardless of MIME type header"
- **Fix to:** "A deny list of file extensions (e.g., .exe, .bat, .ps1, .dll) that blocks uploads regardless of MIME type header"
- **Context:** Technical feature description - use "blocks" instead of "prevents" for technical enforcement

**File:** controls\pillar-1-security\1.27-ai-agent-content-moderation-enforcement.md
- **Line 75:** Table cell text (Zone 3 requirements)
- **Current:** "blocking downgrades to Low prevents inappropriate responses in high-stakes interactions"
- **Fix to:** "blocking downgrades to Low helps prevent inappropriate responses in high-stakes interactions"
- **Context:** Zone-specific requirements table

**File:** controls\pillar-1-security\1.28-policy-based-agent-publishing-restrictions.md
- **Line 13:** Objective prose
- **Current:** "policy-based publishing enforcement model that prevents agents from reaching production"
- **Fix to:** "policy-based publishing enforcement model that helps prevent agents from reaching production"
- **Context:** Control objective statement

**File:** controls\pillar-1-security\1.28-policy-based-agent-publishing-restrictions.md
- **Line 32:** Control description
- **Current:** "enforcement model that prevents Copilot Studio agents from being published"
- **Fix to:** "enforcement model that helps prevent Copilot Studio agents from being published"
- **Context:** Control description opening

**File:** controls\pillar-1-security\1.28-policy-based-agent-publishing-restrictions.md
- **Line 73:** Table cell (Zone 1 requirements)
- **Current:** "DLP enforcement prevents data exfiltration while allowing experimentation"
- **Fix to:** "DLP enforcement helps prevent data exfiltration while allowing experimentation"
- **Context:** Zone-specific requirements justification

**File:** controls\pillar-1-security\1.28-policy-based-agent-publishing-restrictions.md
- **Line 75:** Table cell (Zone 3 requirements)
- **Current:** "environment separation prevents untested agents from reaching production"
- **Fix to:** "environment separation helps prevent untested agents from reaching production"
- **Context:** Zone-specific requirements justification

**File:** controls\pillar-1-security\1.4-advanced-connector-policies-acp.md
- **Line 23:** Regulatory mapping bullet
- **Current:** "Prevents unauthorized data transmission to non-secure external systems"
- **Fix to:** "Helps prevent unauthorized data transmission to non-secure external systems"
- **Context:** GLBA Safeguards Rule regulatory mapping

**File:** controls\pillar-1-security\1.5-data-loss-prevention-dlp-and-sensitivity-labels.md
- **Line 227:** Prose description
- **Current:** "Prevents sensitive data (SSN, account numbers, etc.) from being submitted in AI prompts"
- **Fix to:** "Helps prevent sensitive data (SSN, account numbers, etc.) from being submitted in AI prompts"
- **Context:** Feature capability description

#### PILLAR 2 - MANAGEMENT CONTROLS

**File:** controls\pillar-2-management\2.2-environment-groups-and-tier-classification.md
- **Line 56:** Table cell
- **Current:** "Prevents unauthorized agent distribution"
- **Fix to:** "Helps prevent unauthorized agent distribution"
- **Context:** Agent sharing policy rationale

**File:** controls\pillar-2-management\2.2-environment-groups-and-tier-classification.md
- **Line 59:** Table cell
- **Current:** "Prevents unvetted model usage in regulated environments"
- **Fix to:** "Helps prevent unvetted model usage in regulated environments"
- **Context:** External AI models policy rationale

**File:** controls\pillar-2-management\2.21-ai-marketing-claims-and-substantiation.md
- **Line 14:** Objective statement
- **Current:** "prevents misleading statements about AI functionality"
- **Fix to:** "helps prevent misleading statements about AI functionality"
- **Context:** Control objective

#### PILLAR 3 - REPORTING CONTROLS

**File:** controls\pillar-3-reporting\3.10-hallucination-feedback-loop.md
- **Line 60:** Table cell
- **Current:** "Prevents fabrication in compliance-sensitive contexts"
- **Fix to:** "Helps prevent fabrication in compliance-sensitive contexts"
- **Context:** Explicit fallbacks feature benefit

#### PILLAR 4 - SHAREPOINT CONTROLS

**File:** controls\pillar-4-sharepoint\4.6-grounding-scope-governance.md
- **Line 22:** Regulatory mapping bullet
- **Current:** "Prevents agents from citing draft or unverified documents in responses"
- **Fix to:** "Helps prevent agents from citing draft or unverified documents in responses"
- **Context:** FINRA 4511 regulatory mapping

#### FRAMEWORK DOCUMENTS

**File:** framework\solutions-integration.md
- **Line 207:** Prose description
- **Current:** "Identifies and prevents SoD violations in agent development workflows"
- **Fix to:** "Identifies and helps prevent SoD violations in agent development workflows"
- **Context:** Solution capability description

#### REFERENCE DOCUMENTS

**File:** reference\glossary.md
- **Line 94:** DLP definition
- **Current:** "Policy that prevents unauthorized sharing of sensitive data"
- **Fix to:** "Policy that helps prevent unauthorized sharing of sensitive data"
- **Context:** Glossary term definition

**File:** reference\glossary.md
- **Line 125:** Environment routing definition
- **Current:** "Prevents shadow AI creation in the default environment"
- **Fix to:** "Helps prevent shadow AI creation in the default environment"
- **Context:** Glossary term definition

**File:** reference\glossary.md
- **Line 323:** Shadow AI definition
- **Current:** "Environment routing prevents shadow AI by directing makers to governed environments"
- **Fix to:** "Environment routing helps prevent shadow AI by directing makers to governed environments"
- **Context:** Glossary term definition

**File:** reference\solutions-index.md
- **Line 273:** Solution description
- **Current:** "Identifies and prevents segregation of duties violations"
- **Fix to:** "Identifies and helps prevent segregation of duties violations"
- **Context:** Solution capability description

**File:** reference\solutions-index.md
- **Line 817:** Solution description
- **Current:** "Continuous detection and proactive restriction...prevents public internet links"
- **Fix to:** "Continuous detection and proactive restriction...helps prevent public internet links"
- **Context:** Solution capability description

#### SKIPPED (Technical/Non-Regulatory)

The following were reviewed and DO NOT require changes:

- **1.18-application-level-authorization-and-role-based-access-control-rbac.md:57** - Technical instruction "This prevents agents from performing..."
- **1.9-data-retention-and-deletion-policies.md:131** - Technical fact "Legal hold prevents deletion when applied"
- **2.1-managed-environments.md:114** - Technical outcome "This prevents uncontrolled environment sprawl"
- **2.12-supervision-and-oversight-finra-rule-3110.md:208** - Table: "Built-in role restriction prevents sponsor..."
- **zones-and-tiers.md:412** - Table: "Required (prevents bypass)"
- **Various playbook files** - Implementation/testing instructions (not regulatory claims)
- **Various troubleshooting files** - Issue descriptions
- **EXPECTED.md files** - Test expectations

---

### Category 2: "preventing" as regulatory claim (10 violations)

**File:** controls\pillar-1-security\1.25-mime-type-restrictions.md
- **Line 17:** Objective statement
- **Current:** "preventing the introduction of malicious or high-risk file types"
- **Fix to:** "helping prevent the introduction of malicious or high-risk file types"
- **Context:** Control objective

**File:** controls\pillar-1-security\1.25-mime-type-restrictions.md
- **Line 26:** Regulatory mapping bullet
- **Current:** "aids in operational risk management by preventing executable or high-risk attachments"
- **Fix to:** "aids in operational risk management by helping prevent executable or high-risk attachments"
- **Context:** OCC 2011-12 regulatory mapping

**File:** controls\pillar-1-security\1.26-agent-file-upload-and-file-analysis-restrictions.md
- **Line 25:** Regulatory mapping bullet
- **Current:** "supports operational risk management by preventing agents from processing unvetted file content"
- **Fix to:** "supports operational risk management by helping prevent agents from processing unvetted file content"
- **Context:** OCC 2011-12 regulatory mapping

**File:** controls\pillar-1-security\1.27-ai-agent-content-moderation-enforcement.md
- **Line 24:** Regulatory mapping bullet
- **Current:** "supports recordkeeping compliance by preventing AI agents from generating responses"
- **Fix to:** "supports recordkeeping compliance by helping prevent AI agents from generating responses"
- **Context:** SEC 17a-3/4 regulatory mapping

**File:** controls\pillar-1-security\1.28-policy-based-agent-publishing-restrictions.md
- **Line 23:** Regulatory mapping bullet
- **Current:** "help meet internal control requirements by...preventing unauthorized deployment"
- **Fix to:** "help meet internal control requirements by...helping prevent unauthorized deployment"
- **Context:** SOX 302/404 regulatory mapping

**File:** controls\pillar-1-security\1.5-data-loss-prevention-dlp-and-sensitivity-labels.md
- **Line 109:** Table cell
- **Current:** "Enable self-service agent development while preventing external data sharing"
- **Fix to:** "Enable self-service agent development while helping prevent external data sharing"
- **Context:** Zone 1 DLP strategy

**File:** controls\pillar-1-security\1.5-data-loss-prevention-dlp-and-sensitivity-labels.md
- **Line 138:** Regulatory mapping prose
- **Current:** "helps support FINRA 4511 (preventing unauthorized data sharing via external API calls)"
- **Fix to:** "helps support FINRA 4511 (helping prevent unauthorized data sharing via external API calls)"
- **Context:** HTTP connector DLP filtering

**File:** controls\pillar-1-security\1.5-data-loss-prevention-dlp-and-sensitivity-labels.md
- **Line 208:** Regulatory mapping prose
- **Current:** "help support FINRA 4511 (preventing unauthorized data sharing by controlling...)"
- **Fix to:** "help support FINRA 4511 (helping prevent unauthorized data sharing by controlling...)"
- **Context:** Virtual connector governance

**File:** controls\pillar-1-security\1.5-data-loss-prevention-dlp-and-sensitivity-labels.md
- **Line 244:** Feature description
- **Current:** "preventing users from pasting account numbers, SSNs, or other regulated data"
- **Fix to:** "helping prevent users from pasting account numbers, SSNs, or other regulated data"
- **Context:** Block SITs in Copilot prompts feature

**File:** controls\pillar-2-management\2.15-environment-routing.md
- **Line 14:** Objective statement
- **Current:** "preventing the creation of ungoverned 'shadow AI' in the default environment"
- **Fix to:** "helping prevent the creation of ungoverned 'shadow AI' in the default environment"
- **Context:** Control objective

#### SKIPPED (Technical/Non-Regulatory)

The following were reviewed and DO NOT require changes:

- **2.24-agent-feature-enablement-and-restriction-governance.md:20,23** - Already hedged with "supports...by preventing"
- **controls\pillar-4-sharepoint\index.md:10** - Pillar overview "critical for preventing" - acceptable in high-level context
- **3.6-orphaned-agent-detection-and-remediation.md:284** - "For preventing orphaned environments" - section header
- **3.8-copilot-hub-and-governance-dashboard.md:255** - "controls preventing agent creators" - technical feature
- **Various playbook/troubleshooting files** - Implementation guidance
- **reference\glossary.md:122** - Technical definition "preventing configuration drift"

---

### Category 3: "eliminates" (3 violations - LOW PRIORITY)

These use "eliminates" in technical/benefit descriptions rather than regulatory claims. Consider whether to change:

**File:** framework\agent-identity-architecture.md
- **Line 905:** Table comparison
- **Current:** "Agent 365 unified registry eliminates manual consolidation"
- **Suggested:** "Agent 365 unified registry removes the need for manual consolidation"
- **Context:** Agent 365 vs. manual approach comparison (technical benefit, not regulatory)
- **PRIORITY:** Low - This is a technical benefit claim, not a regulatory compliance claim

**File:** playbooks\advanced-implementations\environment-lifecycle-management\implementation-provisioning.md
- **Line 483:** Technical explanation
- **Current:** "This eliminates the exposure window"
- **Suggested:** "This removes the exposure window"
- **Context:** Technical explanation of Environment Group DLP behavior
- **PRIORITY:** Low - This is a technical fact, not a regulatory claim

**File:** playbooks\advanced-implementations\environment-lifecycle-management\index.md
- **Line 106:** Feature benefit
- **Current:** "Eliminates configuration drift"
- **Suggested:** "Helps eliminate configuration drift" or "Reduces configuration drift"
- **Context:** Environment groups benefit description
- **PRIORITY:** Low - Technical benefit, but could be softened

---

## RECOMMENDED FIXES

### High Priority (36 violations)
All "prevents" and "preventing" violations in:
- Control files (Pillars 1-4)
- Framework documents
- Reference documents
- Regulatory mappings

### Low Priority (3 violations)
"Eliminates" in technical benefit descriptions (not regulatory claims)

---

## VALIDATION COMMANDS

After fixes are applied, re-run this verification:

```powershell
# Search for remaining violations
cd C:\dev\FSI-AgentGov
Get-ChildItem -Path docs -Filter *.md -Recurse | Select-String -Pattern '\bprevents\b' -Context 0,0 | Where-Object { $_.Line -notmatch 'helps prevent' -and $_.Line -notmatch '```' }
Get-ChildItem -Path docs -Filter *.md -Recurse | Select-String -Pattern '\bpreventing\b' -Context 0,0 | Where-Object { $_.Line -notmatch 'helps prevent' }
Get-ChildItem -Path docs -Filter *.md -Recurse | Select-String -Pattern '\beliminates\b' -Context 0,0
```

---

## BUILD VALIDATION STATUS

**Note:** Build validation should be run after fixes are applied.

```bash
mkdocs build --strict
python scripts/verify_controls.py
```

